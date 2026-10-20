"""disgundem CLI: seed | fetch | premium-import | classify | measure | check-feeds"""
from __future__ import annotations

import argparse
import json
import logging
import sys
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone

from . import config
from .classify import TRIAGE_VERSION, Classifier
from .fetch import Item
from .fetch.rss import fetch_feed, make_client
from .fetch.gnews import fetch_gnews
from .fetch.scrape import fetch_listing
from .funnel import Gates, cluster, prefilter, primary_country, select_for_queue, title_hash
from .measure import compute_window, prune_report
from .sources import dictionaries, load_sources
from .store import Store
from .terms import Matcher

log = logging.getLogger("disgundem")


def cmd_seed(s, args):
    store = Store(s)
    store.upsert_dictionaries(dictionaries())
    srcs = load_sources()
    store.upsert_sources([x.as_row() for x in srcs])
    print(f"seed: {len(srcs)} kaynak, {len(dictionaries()['countries'])} ülke")


def _collect(client, matcher, src: dict) -> tuple[list[Item], str]:
    """Kaynağın yöntemine göre topla. RSS kırıksa Google News `site:` yedeğine düş; dönen ikinci değer kullanılan yol."""
    lang = (src.get("langs") or [None])[0]
    site = src.get("local_url") or src["url"]
    if src["method"] == "rss" and src.get("feed_url"):
        try:
            items = fetch_feed(client, src["id"], src["feed_url"], lang)
            return items, "rss+ua" if any(i.extra.get("browser_ua") for i in items) else "rss"
        except Exception as e:
            items = fetch_gnews(client, matcher, src["id"], site, lang or "en", turkey_only=(src["tier"] != "A"))
            if items:
                for i in items:
                    i.extra["rss_error"] = f"{type(e).__name__}: {str(e)[:120]}"
                return items, "gnews-yedek"
            raise
    if src["method"] == "gnews":
        return fetch_gnews(client, matcher, src["id"], site, lang or "en", turkey_only=(src["tier"] != "A")), "gnews"
    if src["method"] == "scrape":
        return fetch_listing(client, src["id"], site, lang), "scrape"
    return [], "manual"  # premium: Chrome oturumu + premium-import


def _fetch_one(s, matcher, src: dict) -> tuple[dict, list[Item], str | None]:
    client = make_client(s)
    try:
        items, via = _collect(client, matcher, src)
        if via == "gnews-yedek":
            log.warning("%s RSS kırık, gnews yedeği kullanıldı: %s", src["id"], items[0].extra.get("rss_error"))
        return src, items, None
    except Exception as e:
        return src, [], f"{type(e).__name__}: {e}"
    finally:
        client.close()


def cmd_fetch(s, args):
    """Topla → tekilleştir → ön filtre → toplu eleme → eşik → kümele → tavan → sakla. Bkz. funnel.py."""
    import hashlib
    store = Store(s)
    matcher = Matcher()
    gates = Gates()
    clf = Classifier(s, matcher)
    srcs = store.due_sources() if not args.all else store.active_sources()
    if args.source:
        srcs = [x for x in store.active_sources() if x["id"] in args.source]
    if args.method:
        srcs = [x for x in srcs if x["method"] == args.method]
    by_id = {x["id"]: x for x in srcs}
    print(f"fetch: {len(srcs)} kaynak (eşikler: sakla>={gates.store_min}, kuyruk>={gates.queue_min}, "
          f"ülke/gün={gates.per_country_daily}, toplam/gün={gates.total_daily}; triage={clf.provider})")

    # 1-2: topla, tekilleştir, ön filtre
    stats = dict(raw=0, dup=0, prefiltered=0, triaged=0, stored=0, pool=0, queued_clusters=0)
    candidates: list[tuple[Item, dict]] = []
    seen_rows: list[dict] = []
    with ThreadPoolExecutor(max_workers=s.concurrency) as ex:
        for fut in as_completed([ex.submit(_fetch_one, s, matcher, src) for src in srcs]):
            src, items, err = fut.result()
            stats["raw"] += len(items)
            uh = {i.url: hashlib.md5(i.url.encode()).hexdigest() for i in items}
            seen = store.seen([(src["id"], uh[i.url], title_hash(i.title)) for i in items])
            fresh = [i for i in items if (src["id"], uh[i.url]) not in seen]
            stats["dup"] += len(items) - len(fresh)
            kept = prefilter(fresh, src, matcher, gates)
            stats["prefiltered"] += len(fresh) - len(kept)
            for i in fresh:
                if i not in kept:
                    seen_rows.append({"source_id": src["id"], "url_hash": uh[i.url], "title_hash": title_hash(i.title),
                                      "importance": 0})
            candidates += [(i, src) for i in kept]
            store.log_run({"id": str(uuid.uuid4()), "source_id": src["id"], "started_at": datetime.now(timezone.utc),
                           "finished_at": datetime.now(timezone.utc), "ok": err is None,
                           "fetched": len(items), "new_items": len(kept), "error": err})
    store.touch_sources([x["id"] for x in srcs])

    # 3: toplu eleme
    scored: list[dict] = []
    for k in range(0, len(candidates), gates.batch_size):
        batch = candidates[k:k + gates.batch_size]
        for (it, src), t in zip(batch, clf.triage(batch)):
            scored.append({"item": it, "src": src, "imp": t["imp"], "tr": t["tr"], "eko": t.get("eko", False),
                           "c": t["c"], "model": t["model"]})
    stats["triaged"] = len(scored)

    # 4: saklama eşiği — altı yalnız hash olarak
    keep = []
    for r in scored:
        if r["imp"] >= gates.store_min and (r["src"]["tier"] == "A" or r["tr"]):
            keep.append(r)
        else:
            seen_rows.append({"source_id": r["src"]["id"], "url_hash": hashlib.md5(r["item"].url.encode()).hexdigest(),
                              "title_hash": title_hash(r["item"].title), "importance": r["imp"]})
    store.mark_seen(seen_rows)

    # 5-6: kümele, tavan
    groups = cluster(keep)
    per_today, total_today = store.queue_today()
    queue, pool = select_for_queue(groups, gates, per_today, total_today)
    now = datetime.now(timezone.utc)
    rows = []
    for grp, status in [(g, "queued") for g in queue] + [(g, "pool") for g in pool]:
        cid = str(uuid.uuid4())
        countries = sorted({c for x in grp for c in x["c"]})
        times = [x["item"].published_at for x in grp if x["item"].published_at] or [now]
        store.insert_cluster({"id": cid, "title_tr": None, "importance": max(x["imp"] for x in grp),
                              "article_count": len(grp), "countries": countries, "primary_country": primary_country(grp),
                              "first_seen": min(times),
                              "last_seen": max(times), "status": status, "created_at": now})
        for x in grp:
            it = x["item"]
            rows.append({"id": str(uuid.uuid4()), "source_id": it.source_id, "url": it.url, "title": it.title,
                         "lang": it.lang, "published_at": it.published_at, "excerpt": it.excerpt,
                         "is_turkey_related": x["tr"], "importance": x["imp"], "cluster_id": cid, "status": status,
                         "triage": {"model": x["model"], "prompt": TRIAGE_VERSION, "countries": x["c"], "eko": x["eko"],
                                    "fetch": it.extra or None}})
        stats["queued_clusters" if status == "queued" else "pool"] += 1
    store.upsert_articles(rows)
    stats["stored"] = len(rows)

    print("huni: ham {raw} → tekrar {dup} düştü → ön filtre {prefiltered} düştü → elemeye {triaged} → "
          "saklanan {stored} başlık → kuyruğa {queued_clusters} küme, havuza {pool} küme".format(**stats))
    (config.OUT / "funnel_last.json").write_text(json.dumps(stats), encoding="utf-8")


def cmd_premium_import(s, args):
    """Claude in Chrome oturumunun çıktısını (JSON) sunucudaki huniyle aynı kapılardan geçirir.

    Dosya biçimi: data/premium/README.md. `importance` zorunlu (1-5, docs/KAPSAM_MODELI.md tablosu):
    store_min altı saklanmaz, 3 havuza, ≥ queue_min kuyruğa (ülke/gün tavanı; 5 tavanı deler).
    Makale metni, uzun alıntı kabul edilmez: summary_tr 600 karakteri aşarsa kayıt reddedilir.
    """
    from .fetch.premium import load_session, route
    store = Store(s)
    gates = Gates()
    rows, links, rejected = load_session(args.file)
    per_today, total_today = store.queue_today()
    kept, below = route(rows, gates, per_today, total_today)
    now = datetime.now(timezone.utc)
    for r in kept:
        cid = str(uuid.uuid4())
        t = r["published_at"] or now
        store.insert_cluster({"id": cid, "title_tr": None, "importance": r["importance"], "article_count": 1,
                              "countries": sorted(r["classification"]["countries"]),
                              "primary_country": (r["classification"]["countries"] or ["tr"])[0],
                              "first_seen": t, "last_seen": t,
                              "status": r["status"], "created_at": now})
        r["cluster_id"] = cid
    store.upsert_articles(kept)
    kept_ids = {r["id"] for r in kept}
    for aid, c, t, d in links:
        if aid in kept_ids:
            store.set_article_links(aid, c, t, d)
    q = sum(1 for r in kept if r["status"] == "queued")
    print(f"chrome-import: {q} kuyruğa, {len(kept) - q} havuza, {len(below)} eşik altı, {len(rejected)} reddedildi")
    for r in rejected:
        print("  reddedildi:", r)


def cmd_classify(s, args):
    """Kuyruğa girmiş başlıklara özet, tema, dosya, çerçeve ekler. Elemeyi geçmeyenlere hiç LLM harcanmaz."""
    store = Store(s)
    srcs = {x.id: x for x in load_sources()}
    clf = Classifier(s)
    rows = store.unsummarized(limit=args.limit)
    print(f"classify: kuyrukta özetsiz {len(rows)} kayıt, sağlayıcı={clf.provider} model={clf.model}")
    out = []
    for a in rows:
        src = srcs.get(a["source_id"])
        if not src:
            continue
        item = Item(source_id=a["source_id"], url=a["url"], title=a["title"], lang=a.get("lang"), excerpt=a.get("excerpt"))
        c = clf.classify(item, src)
        out.append({"id": a["id"], "source_id": a["source_id"], "url": a["url"], "title": a["title"],
                    "frame": c.frame, "summary_tr": c.summary_tr, "local_view_note": c.local_view_note,
                    "status": a["status"],
                    "classification": {"model": c.model, "prompt": c.prompt_version, "confidence": c.confidence,
                                       "raw": c.raw, "countries": c.countries, "themes": c.themes, "dossiers": c.dossiers}})
        store.set_article_links(a["id"], c.countries, c.themes, c.dossiers)
    store.upsert_articles(out)
    print(f"özetlenen: {len(out)}")


def cmd_measure(s, args):
    store = Store(s)
    rows = compute_window(store, days=args.days)
    print(f"measure: {len(rows)} kaynak için {args.days} günlük pencere yazıldı")
    if args.report:
        rep = prune_report(store, rows, store.active_sources() + [x.as_row() for x in load_sources() if x.status == "yedek"])
        p = config.OUT / "budama_raporu.md"
        p.write_text(rep, encoding="utf-8")
        print(f"rapor: {p}")


def cmd_check_feeds(s, args):
    """Envanterdeki RSS adreslerini dener; kırıksa tarayıcı başlığı ve gnews yedeğini de dener (DB gerekmez)."""
    srcs = [x for x in load_sources() if x.feed_url and (not args.core or x.status == "cekirdek")]
    matcher = Matcher()
    print(f"check-feeds: {len(srcs)} besleme")
    results = []

    def one(x):
        client = make_client(s)
        row = x.as_row()
        rss_err = None
        try:
            items = fetch_feed(client, x.id, x.feed_url, x.langs[0] if x.langs else None)
            via = "rss+ua" if any(i.extra.get("browser_ua") for i in items) else "rss"
        except Exception as e:
            rss_err = f"{type(e).__name__}: {str(e)[:90]}"
            try:
                items, via = _collect(client, matcher, row)
            except Exception:
                items, via = [], "yok"
        finally:
            client.close()
        newest = max((i.published_at for i in items if i.published_at), default=None)
        return x, len(items), newest, via, rss_err

    with ThreadPoolExecutor(max_workers=s.concurrency) as ex:
        for x, n, newest, via, err in ex.map(one, srcs):
            results.append({"id": x.id, "name": x.name, "feed": x.feed_url, "items": n, "via": via,
                            "newest": newest.isoformat() if newest else None, "rss_error": err})
            print(f"  {x.id:5} {x.name[:30]:30} {n:4} kayıt  {via:11} en yeni={newest.date() if newest else '-'}  {err or ''}")
    p = config.OUT / "feed_check.json"
    p.write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")
    by = {}
    for r in results:
        by[r["via"]] = by.get(r["via"], 0) + 1
    ok = sum(1 for r in results if r["items"] > 0)
    print(f"çalışan: {ok}/{len(results)}  yol dağılımı: {by} → {p}")
    broken = [r for r in results if r["via"] != "rss"]
    if broken:
        print("RSS dışı / kırık:")
        for r in broken:
            print(f"  {r['id']:5} {r['name'][:30]:30} {r['via']:11} {r['items']:4}  {r['rss_error'] or ''}")


def main(argv=None):
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    p = argparse.ArgumentParser(prog="disgundem")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("seed", help="sözlükleri ve kaynak envanterini yükle")
    f = sub.add_parser("fetch", help="çekirdek kaynakları topla")
    f.add_argument("--source", nargs="*", help="yalnız bu ID'ler")
    f.add_argument("--method", choices=["rss", "gnews", "scrape"])
    f.add_argument("--all", action="store_true", help="tarama aralığını yok say, tüm çekirdeği tara")
    g = sub.add_parser("premium-import", aliases=["chrome-import"],
                       help="Claude in Chrome oturumu çıktısını (JSON; premium + engelli-RSS) kuyruğa al")
    g.add_argument("file")
    c = sub.add_parser("classify", help="toplananları sınıflandır, özetle, kuyruğa al")
    c.add_argument("--limit", type=int, default=200)
    m = sub.add_parser("measure", help="kayan pencere hacmi hesapla")
    m.add_argument("--days", type=int, default=30)
    m.add_argument("--report", action="store_true")
    k = sub.add_parser("check-feeds", help="envanterdeki RSS adreslerini dene")
    k.add_argument("--core", action="store_true")
    args = p.parse_args(argv)
    s = config.load()
    {"seed": cmd_seed, "fetch": cmd_fetch, "premium-import": cmd_premium_import, "chrome-import": cmd_premium_import, "classify": cmd_classify,
     "measure": cmd_measure, "check-feeds": cmd_check_feeds}[args.cmd](s, args)


if __name__ == "__main__":
    sys.exit(main())
