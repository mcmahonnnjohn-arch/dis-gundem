"""disgundem CLI: seed | fetch | classify | measure | report | check-feeds"""
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
            return src, [], None  # gmail ayrı komutta, manual atlanır
        return src, items, None
    except Exception as e:
        return src, [], f"{type(e).__name__}: {e}"
    finally:
        client.close()


def cmd_fetch(s, args):
    store = Store(s)
    matcher = Matcher()
    srcs = store.active_sources()
    if args.source:
        srcs = [x for x in srcs if x["id"] in args.source]
    if args.method:
        srcs = [x for x in srcs if x["method"] == args.method]
    print(f"fetch: {len(srcs)} kaynak")
    total_new = 0
    with ThreadPoolExecutor(max_workers=s.concurrency) as ex:
        futs = [ex.submit(_fetch_one, s, matcher, src) for src in srcs]
        for fut in as_completed(futs):
            src, items, err = fut.result()
            started = datetime.now(timezone.utc)
            known = store.existing_urls(src["id"], [i.url for i in items])
            new = [i for i in items if i.url not in known]
            rows = [{
                "source_id": i.source_id, "url": i.url, "title": i.title, "lang": i.lang,
                "published_at": i.published_at, "excerpt": i.excerpt, "status": "fetched",
                "classification": {"fetch": i.extra} if i.extra else None,
            } for i in new]
            store.upsert_articles(rows)
            store.log_run({"id": str(uuid.uuid4()), "source_id": src["id"], "started_at": started,
                           "finished_at": datetime.now(timezone.utc), "ok": err is None,
                           "fetched": len(items), "new_items": len(new), "error": err})
            total_new += len(new)
            print(f"  {src['id']:5} {src['name'][:38]:38} {src['method']:6} {len(items):4} kayıt {len(new):4} yeni {('HATA ' + err[:60]) if err else ''}")
    print(f"toplam yeni: {total_new}")


def cmd_gmail(s, args):
    from .fetch.gmail import fetch_gmail
    store = Store(s)
    items = fetch_gmail(s, since_days=args.days)
    rows = [{"source_id": i.source_id, "url": i.url, "title": i.title, "lang": "en", "published_at": i.published_at,
             "status": "fetched", "classification": {"fetch": i.extra}} for i in items]
    store.upsert_articles(rows)
    print(f"gmail: {len(rows)} başlık")


def cmd_classify(s, args):
    store = Store(s)
    srcs = {x.id: x for x in load_sources()}
    clf = Classifier(s)
    rows = store.unclassified(limit=args.limit)
    print(f"classify: {len(rows)} kayıt, sağlayıcı={clf.provider} model={clf.model}")
    out = []
    for a in rows:
        src = srcs.get(a["source_id"])
        if not src:
            continue
        item = Item(source_id=a["source_id"], url=a["url"], title=a["title"], lang=a.get("lang"), excerpt=a.get("excerpt"))
        c = clf.classify(item, src)
        status = "queued" if c.publishable else "rejected"
        out.append({"id": a["id"], "source_id": a["source_id"], "url": a["url"], "title": a["title"],
                    "is_turkey_related": c.turkey_related, "importance": c.importance, "frame": c.frame,
                    "summary_tr": c.summary_tr, "local_view_note": c.local_view_note, "status": status,
                    "classification": {"model": c.model, "prompt": c.prompt_version, "confidence": c.confidence,
                                       "raw": c.raw, "countries": c.countries, "themes": c.themes, "dossiers": c.dossiers}})
        store.set_article_links(a["id"], c.countries, c.themes, c.dossiers)
    store.upsert_articles(out)
    q = sum(1 for r in out if r["status"] == "queued")
    print(f"kuyruğa: {q}, elenen: {len(out) - q}")


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
    g = sub.add_parser("gmail", help="premium bültenlerden başlık topla")
    g.add_argument("--days", type=int, default=2)
    c = sub.add_parser("classify", help="toplananları sınıflandır, özetle, kuyruğa al")
    c.add_argument("--limit", type=int, default=200)
    m = sub.add_parser("measure", help="kayan pencere hacmi hesapla")
    m.add_argument("--days", type=int, default=30)
    m.add_argument("--report", action="store_true")
    k = sub.add_parser("check-feeds", help="envanterdeki RSS adreslerini dene")
    k.add_argument("--core", action="store_true")
    args = p.parse_args(argv)
    s = config.load()
    {"seed": cmd_seed, "fetch": cmd_fetch, "gmail": cmd_gmail, "classify": cmd_classify,
     "measure": cmd_measure, "check-feeds": cmd_check_feeds}[args.cmd](s, args)


if __name__ == "__main__":
    sys.exit(main())
