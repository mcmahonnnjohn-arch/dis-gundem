"""disgundem CLI: seed | fetch | premium-import | classify | measure | check-feeds"""
from __future__ import annotations

import argparse
import json
import logging
import sys
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import replace
from datetime import datetime, timezone

from . import config
from .classify import TRIAGE_VERSION, Classifier
from .fetch import Item
from .fetch.article import fetch_text
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
    from . import harita
    pl, ac = harita.places(), harita.actors()
    try:
        store.upsert_map_dictionaries([x.row() for x in pl.values()], [x.row() for x in ac.values()])
    except Exception as e:   # 0008 uygulanmadıysa hat durmasın
        log.warning("harita sözlükleri yüklenemedi (0008_harita.sql uygulandı mı?): %s", str(e)[:200])
    print(f"seed: {len(srcs)} kaynak, {len(dictionaries()['countries'])} ülke, {len(pl)} yer, {len(ac)} aktör")


def _collect(client, matcher, src: dict) -> tuple[list[Item], str]:
    """Kaynağın yöntemine göre topla; dönen ikinci değer kullanılan yol.

    RSS ya da liste sayfası kırıksa (403 vb.) Google News `site:` yedeğine düşülür. Yedek çalışıp sonuç
    döndürmezse bu hata değildir: B kaynaklarında son 7 günde Türkiye geçmemiş olabilir ("gnews-yedek-0").
    Yedeğin kendisi de hata verirse özgün hata yükseltilir."""
    lang = (src.get("langs") or [None])[0]
    site = src.get("local_url") or src["url"]

    def fallback(err: Exception) -> tuple[list[Item], str]:
        try:
            items = fetch_gnews(client, matcher, src["id"], site, lang or "en", turkey_only=(src["tier"] != "A"))
        except Exception:
            raise err
        for i in items:
            i.extra["primary_error"] = f"{type(err).__name__}: {str(err)[:120]}"
        if not items:
            log.info("%s birincil yol kırık (%s: %s), gnews yedeği 0 sonuç", src["id"], type(err).__name__, str(err)[:80])
        return items, "gnews-yedek" if items else "gnews-yedek-0"

    if src["method"] == "rss" and src.get("feed_url"):
        try:
            items = fetch_feed(client, src["id"], src["feed_url"], lang)
            return items, "rss+ua" if any(i.extra.get("browser_ua") for i in items) else "rss"
        except Exception as e:
            return fallback(e)
    if src["method"] == "gnews":
        return fetch_gnews(client, matcher, src["id"], site, lang or "en", turkey_only=(src["tier"] != "A")), "gnews"
    if src["method"] == "scrape":
        try:
            return fetch_listing(client, src["id"], site, lang), "scrape"
        except Exception as e:
            return fallback(e)
    return [], "manual"  # premium: Chrome oturumu + premium-import


def _fetch_one(s, matcher, src: dict) -> tuple[dict, list[Item], str | None]:
    client = make_client(s)
    try:
        items, via = _collect(client, matcher, src)
        if via == "gnews-yedek":
            log.warning("%s birincil yol kırık, gnews yedeği kullanıldı: %s", src["id"], items[0].extra.get("primary_error"))
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
            stored = store.existing_urls(src["id"], [i.url for i in items])   # önceki çalışmada saklanmış makaleler
            fresh = [i for i in items if (src["id"], uh[i.url]) not in seen and i.url not in stored]
            stats["dup"] += len(items) - len(fresh)
            # Yaş/Türkiye filtresinden düşen "görüldü" sayılır; kaynak tavanı yüzünden bekleyen sayılmaz (sonra gelir).
            passed = prefilter(fresh, src, matcher, replace(gates, max_items_per_source=10**9))
            kept = passed[:gates.max_items_per_source]
            stats["prefiltered"] += len(fresh) - len(kept)
            for i in fresh:
                if i not in passed:
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
    per_today, total_today = store.queue_today("server")
    queue, pool = select_for_queue(groups, gates, per_today, total_today)
    now = datetime.now(timezone.utc)
    rows = []
    for grp, status in [(g, "queued") for g in queue] + [(g, "pool") for g in pool]:
        cid = str(uuid.uuid4())
        countries = sorted({c for x in grp for c in x["c"]})
        times = [x["item"].published_at for x in grp if x["item"].published_at] or [now]
        store.insert_cluster({"id": cid, "title_tr": None, "importance": max(x["imp"] for x in grp),
                              "article_count": len(grp), "countries": countries, "primary_country": primary_country(grp),
                              "origin": "server",
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
    have = store.existing_article_keys([r["source_id"] for r in rows])
    skipped = [r for r in rows if (r["source_id"], r["url"]) in have]
    rows = [r for r in rows if (r["source_id"], r["url"]) not in have]
    per_today, total_today = store.queue_today("chrome")
    kept, below = route(rows, gates, per_today, total_today)
    now = datetime.now(timezone.utc)
    for r in kept:
        cid = str(uuid.uuid4())
        t = r["published_at"] or now
        store.insert_cluster({"id": cid, "title_tr": None, "importance": r["importance"], "article_count": 1,
                              "countries": sorted(r["classification"]["countries"]),
                              "primary_country": (r["classification"]["countries"] or ["tr"])[0], "origin": "chrome",
                              "first_seen": t, "last_seen": t,
                              "status": r["status"], "created_at": now})
        r["cluster_id"] = cid
    store.upsert_articles(kept)
    kept_ids = {r["id"] for r in kept}
    for aid, c, t, d in links:
        if aid in kept_ids:
            store.set_article_links(aid, c, t, d)
    q = sum(1 for r in kept if r["status"] == "queued")
    print(f"chrome-import: {q} kuyruğa, {len(kept) - q} havuza, {len(below)} eşik altı, "
          f"{len(skipped)} zaten içeride, {len(rejected)} reddedildi")
    for r in rejected:
        print("  reddedildi:", r)


def cmd_classify(s, args):
    """Kuyruğa girmiş başlıklara özet, tema, dosya, çerçeve ekler. Elemeyi geçmeyenlere hiç LLM harcanmaz.

    Makale metni (ARTICLE_TEXT=1) yalnız bu çağrı sırasında bellekte tutulur; DB'ye, dosyaya, loga yazılmaz.
    `--yeniden`: sunucu kökenli kuyruk haberlerini yeni prompt/modelle baştan özetler, eski özeti saklar.
    """
    store = Store(s)
    srcs = {x.id: x for x in load_sources()}
    clf = Classifier(s)
    rows = store.queued_server(limit=args.limit) if args.yeniden else store.unsummarized(limit=args.limit)
    print(f"classify: {len(rows)} kayıt ({'yeniden' if args.yeniden else 'özetsiz'}), sağlayıcı={clf.provider} "
          f"eleme={clf.model} özet={clf.summary_model} metin={'açık' if s.article_text else 'kapalı'} "
          f"denetim={'açık' if s.audit else 'kapalı'}")
    client = make_client(s) if s.article_text and clf.provider != "none" else None
    out, stats = [], {"metin_ok": 0, "metin_yok": 0, "denetim": 0, "duzeltildi": 0, "hata": 0}
    try:
        for a in rows:
            src = srcs.get(a["source_id"])
            if not src:
                continue
            item = Item(source_id=a["source_id"], url=a["url"], title=a["title"], lang=a.get("lang"),
                        excerpt=a.get("excerpt"))
            text, text_status = (fetch_text(client, a["url"], s.user_agent, a["title"]) if client else (None, "kapali"))
            stats["metin_ok" if text else "metin_yok"] += 1
            c = clf.classify(item, src, text=text, audit=s.audit)
            del text   # metin bu noktadan sonra hiçbir yere gitmez
            if "error" in c.raw:   # LLM hatası: mevcut özetin üzerine boş yazılmaz, kayıt sonraki çalışmaya kalır
                stats["hata"] += 1
                if stats["hata"] == 1:
                    print(f"LLM hatası: {c.raw['error'][:300]}")
                continue
            if c.audit and c.audit.get("gecti") is False:
                stats["denetim"] += 1
                stats["duzeltildi"] += bool(c.audit.get("ilk_ozet"))
            meta = {"model": c.model, "prompt": c.prompt_version, "confidence": c.confidence, "raw": c.raw,
                    "countries": c.countries, "themes": c.themes, "dossiers": c.dossiers,
                    "metin": text_status, "uyarilar": c.warnings, "denetim": c.audit}
            if args.yeniden and a.get("summary_tr"):
                prev = a.get("classification") or {}
                # Karşılaştırma ilk (v1) özete karşı yapılır: önceki zaten saklıysa korunur.
                meta["onceki"] = prev.get("onceki") or {"summary_tr": a["summary_tr"], "prompt": prev.get("prompt"),
                                                        "model": prev.get("model")}
            out.append({"id": a["id"], "source_id": a["source_id"], "url": a["url"], "title": a["title"],
                        "frame": c.frame, "summary_tr": c.summary_tr, "local_view_note": c.local_view_note,
                        "status": a["status"], "uyarilar": c.warnings, "classification": meta})
            store.set_article_links(a["id"], c.countries, c.themes, c.dossiers)
    finally:
        if client:
            client.close()
    store.upsert_articles(out)
    print(f"özetlenen: {len(out)} · metin okundu {stats['metin_ok']}, okunamadı {stats['metin_yok']} · "
          f"denetimde sorun {stats['denetim']} (düzeltilen {stats['duzeltildi']}) · LLM hatası {stats['hata']}")
    if rows and stats["hata"] == len(rows):
        sys.exit("classify: tüm LLM çağrıları hata verdi")


def cmd_birlestir(s, args):
    """Aynı olayın kümelerini birleştirir (olay.py). fetch/chrome-import'tan sonra, classify'dan önce çalışır."""
    from . import olay
    store = Store(s)
    clf = Classifier(s)
    clusters, arts = store.recent_clusters(hours=args.saat)
    by_c: dict[str, list[dict]] = {}
    for a in arts:
        by_c.setdefault(a["cluster_id"], []).append(a)
    items = [{"k": c["id"], "t": [a["title"][:200] for a in by_c.get(c["id"], [])],
              "u": c.get("primary_country"), "z": str(c.get("first_seen") or "")[:10]}
             for c in clusters if by_c.get(c["id"])]
    groups = olay.group_items(clf, items)
    cmap = {c["id"]: c for c in clusters}
    merged = 0
    for g in groups:
        cs = [cmap[x] for x in g]
        target = olay.pick_target(cs)
        others = [c for c in cs if c["id"] != target["id"]]
        members = [a for c in cs for a in by_c.get(c["id"], [])]
        store.merge_clusters(target, others, members)
        merged += len(others)
        print(f"  olay: {len(members)} haber → {target['id'][:8]} ({target['status']}) · "
              + " | ".join(a["title"][:50] for a in members[:4]))
    print(f"birlestir: {len(items)} küme, {len(groups)} olay grubu, {merged} küme birleşti")


def cmd_harita(s, args):
    """Özetli kümeleri haritaya bağlar: olay türü, yerler (birincil işaretçi), aktörler, "Türkiye için anlamı".
    `olay` adımından sonra çalışır; yalnız event_type'ı boş kümeler (--yeniden ile hepsi)."""
    from . import harita
    store = Store(s)
    clf = Classifier(s)
    try:
        clusters, arts = store.map_candidates(hours=args.saat, redo=args.yeniden)
    except Exception as e:   # 0008 uygulanmadıysa hat durmasın
        print(f"harita: atlandı, harita sütunları yok (0008_harita.sql uygulandı mı?): {str(e)[:160]}")
        return
    by_c: dict[str, list[dict]] = {}
    for a in arts:
        by_c.setdefault(a["cluster_id"], []).append(a)
    events = []
    for c in clusters:
        members = by_c.get(c["id"], [])
        ozet = c.get("summary_tr") or next((a["summary_tr"] for a in members if a.get("summary_tr")), None)
        if not ozet:
            continue                       # özetsiz küme haritaya düşmez; sonraki çalıştırmada tekrar denenir
        baslik = c.get("title_tr") or (members[0]["title"] if members else None)
        events.append({"k": c["id"], "baslik": baslik, "ozet": ozet, "ulke": c.get("primary_country"),
                       "kaynak_basliklari": [a["title"][:200] for a in members]})
    links = harita.extract(clf, events)
    known_c = {x["id"] for x in dictionaries()["countries"]}
    unresolved: list[tuple[str, str | None]] = []
    noplace = 0
    for cid, L in links.items():
        meta = {"prompt": harita.PROMPT_VERSION, "model": clf.model,
                "cozulemeyen": [n for n, _ in L.unresolved]}
        store.set_map_links(cid, {"event_type": L.event_type, "turkey_stake": L.turkey_stake, "map_meta": meta},
                            L.places, L.actors)
        unresolved += [(n, c if c in known_c else None) for n, c in L.unresolved]
        noplace += not L.places
    store.note_unresolved(unresolved)
    print(f"harita: {len(events)} olay, {len(links)} bağlandı, {noplace} yersiz, "
          f"{len(unresolved)} çözülemeyen yer adı (place_unresolved)")


def cmd_olay(s, args):
    """Çok haberli kümelere olay özeti + bakış farkı yazar; metni hiç okunamamış kuyruk kümelerini havuza düşürür."""
    from . import olay
    store = Store(s)
    clf = Classifier(s)
    clusters, arts = store.recent_clusters(hours=args.saat)
    by_c: dict[str, list[dict]] = {}
    for a in arts:
        by_c.setdefault(a["cluster_id"], []).append(a)
    srcs = {x.id: x for x in load_sources()}
    yazildi = dusen = 0
    for c in clusters:
        members = by_c.get(c["id"], [])
        if not members:
            continue
        # Metin politikası: değerlendirilmiş (classify_v2+) sunucu haberlerinin hiçbiri okunamadıysa kuyruktan çık
        judged = [a for a in members if "metin" in (a.get("classification") or {})]
        readable = [a for a in members if (a.get("classification") or {}).get("metin") == "ok"
                    or (a.get("classification") or {}).get("prompt", "").startswith("chrome")]
        if (s.drop_no_text and c["status"] == "queued" and c.get("origin") != "chrome"
                and judged and len(judged) == len(members) and not readable):
            store.update_cluster(c["id"], {"status": "pool"})
            store.set_articles_status([a["id"] for a in members], "pool")
            dusen += 1
            print(f"  havuza: {members[0]['title'][:70]} (metin okunamadı)")
            continue
        done = [a for a in members if a.get("summary_tr")]
        if len(done) < 2 or (c.get("summary_tr") and not args.yeniden):
            continue
        payload = [{"kaynak": getattr(srcs.get(a["source_id"]), "name", a["source_id"]),
                    "ulke": getattr(srcs.get(a["source_id"]), "country_id", ""), "dil": a.get("lang"),
                    "baslik": a["title"][:200], "ozet": a["summary_tr"], "bakis": a.get("local_view_note")}
                   for a in done]
        res = olay.summarize_event(clf, payload)
        if res and res["ozet"]:
            store.update_cluster(c["id"], {"title_tr": res["baslik"], "summary_tr": res["ozet"],
                                           "bakis_farki": res["bakis_farki"], "article_count": len(members)})
            yazildi += 1
    print(f"olay: {yazildi} olay özeti yazıldı, {dusen} metinsiz küme havuza düştü")


def cmd_eval(s, args):
    """Özet test setini güncel hatla çalıştırır ve puanlar (evaluate.py). Makale metni okunur, saklanmaz."""
    from . import evaluate as ev
    cases = ev.load_set(only_approved=args.onayli)
    if args.no:
        want = {int(x) for x in args.no}
        cases = [c for c in cases if c["no"] in want]
    clf = Classifier(s)
    if clf.provider == "none":
        sys.exit("eval: LLM sağlayıcısı yok (LLM_PROVIDER/anahtar)")
    meta = ev.meta_for(clf, s)
    if getattr(args, "yalniz_olay", False):   # yalnız birleştirme ölçümü: özet üretilmez, tek LLM çağrısı
        res = ev.olay_testi(clf, cases)
        print(f"olay birleştirme: {res}")
        from .olay import GROUP_VERSION
        Store(s).insert_eval_run({"meta": {**meta, "olay": GROUP_VERSION}, "ozet": {"n": len(cases), "olay": res},
                                  "sonuclar": [], "etiket": args.etiket or None})
        return
    print(f"eval: {len(cases)} haber · {meta}")
    client = make_client(s) if s.article_text else None
    results = []
    try:
        for c in cases:
            r = ev.run_case(clf, client, s, c, use_judge=not args.hakemsiz)
            k, h = r.kurallar, r.hakem or {}
            print(f"  {r.no:>2} {r.lang} metin={r.metin:<8} olmalı={k['olmali_oran']:.2f} ihlal={len(k['ihlal'])} "
                  f"doğruluk={h.get('dogruluk')} kapsam={h.get('kapsam')} atıf={h.get('atif')}")
            results.append(r)
    finally:
        if client:
            client.close()
    agg = ev.aggregate(results)
    if not args.no:   # olay birleştirme ölçümü tüm sette anlamlı
        agg["olay"] = ev.olay_testi(clf, cases)
        print(f"olay birleştirme: kesinlik {agg['olay']['kesinlik']} · duyarlılık {agg['olay']['duyarlilik']} · "
              f"yanlış birleşen {agg['olay']['yanlis_birlesen']} · kaçan {agg['olay']['kacan']}")
    md = ev.report_md(meta, agg, results)
    (config.OUT / "eval_raporu.md").write_text(md, encoding="utf-8")
    print(md)
    Store(s).insert_eval_run({"meta": meta, "ozet": agg, "sonuclar": [r.as_dict() for r in results],
                              "etiket": args.etiket or None})


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
    c.add_argument("--yeniden", action="store_true", help="sunucu kökenli kuyruk haberlerini baştan özetle")
    b = sub.add_parser("birlestir", help="aynı olayın kümelerini birleştir (diller arası)")
    b.add_argument("--saat", type=int, default=48)
    o = sub.add_parser("olay", help="çok haberli kümelere olay özeti; metinsiz kuyruk kümesini havuza düşür")
    o.add_argument("--saat", type=int, default=48)
    o.add_argument("--yeniden", action="store_true", help="olay özeti olan kümeleri de yeniden yaz")
    h = sub.add_parser("harita", help="özetli olayları haritaya bağla (tür, yer, aktör, Türkiye için anlamı)")
    h.add_argument("--saat", type=int, default=72)
    h.add_argument("--yeniden", action="store_true", help="bağlı kümeleri de yeniden çıkar")
    e = sub.add_parser("eval", help="özet test setini çalıştır ve puanla")
    e.add_argument("--no", nargs="*", help="yalnız bu test numaraları")
    e.add_argument("--onayli", action="store_true", help="yalnız editör onaylı satırlar")
    e.add_argument("--hakemsiz", action="store_true", help="LLM hakem çağrısını atla (yalnız kurallar)")
    e.add_argument("--etiket", default="", help="çalışmaya not (ör. 'classify_v4 tabanı')")
    e.add_argument("--yalniz-olay", action="store_true", help="yalnız olay birleştirme ölçümü")
    m = sub.add_parser("measure", help="kayan pencere hacmi hesapla")
    m.add_argument("--days", type=int, default=30)
    m.add_argument("--report", action="store_true")
    k = sub.add_parser("check-feeds", help="envanterdeki RSS adreslerini dene")
    k.add_argument("--core", action="store_true")
    args = p.parse_args(argv)
    s = config.load()
    {"seed": cmd_seed, "fetch": cmd_fetch, "premium-import": cmd_premium_import, "chrome-import": cmd_premium_import, "classify": cmd_classify, "eval": cmd_eval,
     "birlestir": cmd_birlestir, "olay": cmd_olay, "harita": cmd_harita,
     "measure": cmd_measure, "check-feeds": cmd_check_feeds}[args.cmd](s, args)


if __name__ == "__main__":
    sys.exit(main())
