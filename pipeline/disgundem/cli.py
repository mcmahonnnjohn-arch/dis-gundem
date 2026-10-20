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
from .classify import Classifier
from .fetch import Item
from .fetch.rss import fetch_feed, make_client
from .fetch.gnews import fetch_gnews
from .fetch.scrape import fetch_listing
from .funnel import Gates, cluster, prefilter, select_for_queue, title_hash
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


def _fetch_one(s, matcher, src: dict) -> tuple[dict, list[Item], str | None]:
    client = make_client(s)
    lang = (src.get("langs") or [None])[0]
    try:
        if src["method"] == "rss" and src.get("feed_url"):
            items = fetch_feed(client, src["id"], src["feed_url"], lang)
        elif src["method"] == "gnews":
            items = fetch_gnews(client, matcher, src["id"], src.get("local_url") or src["url"], lang or "en",
                                turkey_only=(src["tier"] != "A"))
        elif src["method"] == "scrape":
            items = fetch_listing(client, src["id"], src.get("local_url") or src["url"], lang)
        else:
            return src, [], None  # manual (premium): Chrome oturumu + premium-import
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
            scored.append({"item": it, "src": src, "imp": t["imp"], "tr": t["tr"], "c": t["c"], "model": t["model"]})
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
                              "article_count": len(grp), "countries": countries, "first_seen": min(times),
                              "last_seen": max(times), "status": status, "created_at": now})
        for x in grp:
            it = x["item"]
            rows.append({"id": str(uuid.uuid4()), "source_id": it.source_id, "url": it.url, "title": it.title,
                         "lang": it.lang, "published_at": it.published_at, "excerpt": it.excerpt,
                         "is_turkey_related": x["tr"], "importance": x["imp"], "cluster_id": cid, "status": status,
                         "triage": {"model": x["model"], "prompt": "triage_v1", "countries": x["c"],
                                    "fetch": it.extra or None}})
        stats["queued_clusters" if status == "queued" else "pool"] += 1
    store.upsert_articles(rows)
    stats["stored"] = len(rows)

    print("huni: ham {raw} → tekrar {dup} düştü → ön filtre {prefiltered} düştü → elemeye {triaged} → "
          "saklanan {stored} başlık → kuyruğa {queued_clusters} küme, havuza {pool} küme".format(**stats))
    (config.OUT / "funnel_last.json").write_text(json.dumps(stats), encoding="utf-8")


def cmd_premium_import(s, args):
    """Claude in Chrome premium tarama oturumunun çıktısını (JSON) kuyruğa alır.

    Dosya biçimi: [{"source_id":"K170","url":"...","title":"...","published_at":"2026-10-19",
                   "summary_tr":"kendi cümlelerimizle 2-3 cümle","countries":["sy"],"themes":["enerji"],
                   "dossiers":[], "frame":"notr", "note":"..."}]
    Makale metni, uzun alıntı kabul edilmez: summary_tr 600 karakteri aşarsa kayıt reddedilir.
    """
    from .fetch.premium import load_session
    store = Store(s)
    rows, links, rejected = load_session(args.file)
    store.upsert_articles(rows)
    for aid, c, t, d in links:
        store.set_article_links(aid, c, t, d)
    print(f"premium-import: {len(rows)} kayıt kuyruğa, {len(rejected)} reddedildi")
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
    """Envanterdeki RSS adreslerini ayrıştırıp sonuç tablosu basar (DB gerekmez)."""
    srcs = [x for x in load_sources() if x.feed_url and (not args.core or x.status == "cekirdek")]
    print(f"check-feeds: {len(srcs)} besleme")
    results = []

    def one(x):
        client = make_client(s)
        try:
            items = fetch_feed(client, x.id, x.feed_url, x.langs[0] if x.langs else None)
            newest = max((i.published_at for i in items if i.published_at), default=None)
            return x, len(items), newest, None
        except Exception as e:
            return x, 0, None, f"{type(e).__name__}: {str(e)[:70]}"
        finally:
            client.close()

    with ThreadPoolExecutor(max_workers=s.concurrency) as ex:
        for x, n, newest, err in ex.map(one, srcs):
            results.append({"id": x.id, "name": x.name, "feed": x.feed_url, "items": n,
                            "newest": newest.isoformat() if newest else None, "error": err})
            print(f"  {x.id:5} {x.name[:34]:34} {n:4} kayıt  en yeni={newest.date() if newest else '-'}  {err or ''}")
    p = config.OUT / "feed_check.json"
    p.write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")
    ok = sum(1 for r in results if r["items"] > 0)
    print(f"çalışan: {ok}/{len(results)} → {p}")


def main(argv=None):
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    p = argparse.ArgumentParser(prog="disgundem")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("seed", help="sözlükleri ve kaynak envanterini yükle")
    f = sub.add_parser("fetch", help="çekirdek kaynakları topla")
    f.add_argument("--source", nargs="*", help="yalnız bu ID'ler")
    f.add_argument("--method", choices=["rss", "gnews", "scrape"])
    f.add_argument("--all", action="store_true", help="tarama aralığını yok say, tüm çekirdeği tara")
    g = sub.add_parser("premium-import", help="Claude in Chrome premium tarama çıktısını (JSON) kuyruğa al")
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
    {"seed": cmd_seed, "fetch": cmd_fetch, "premium-import": cmd_premium_import, "classify": cmd_classify,
     "measure": cmd_measure, "check-feeds": cmd_check_feeds}[args.cmd](s, args)


if __name__ == "__main__":
    sys.exit(main())
