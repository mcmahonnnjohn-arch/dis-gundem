"""cmd_fetch akışı: saklı makale tekrar işlenmez; kaynak tavanı yüzünden bekleyen başlık 'görüldü' sayılmaz."""
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

from disgundem import cli
from disgundem.fetch import Item

NOW = datetime.now(timezone.utc)
SRC = {"id": "K1", "name": "x", "tier": "A", "country_id": "sy", "method": "rss", "feed_url": "f", "url": "u",
       "langs": ["en"]}


def test_fetch_skips_stored_and_keeps_capped_unseen(monkeypatch, tmp_path):
    items = [Item(source_id="K1", url=f"https://x/{i}", title=f"Haber {i} başlık", published_at=NOW - timedelta(minutes=i))
             for i in range(5)]
    rec = SimpleNamespace(seen=[], triaged=[], articles=[])

    class FakeStore:
        def __init__(self, s): pass
        def due_sources(self): return [SRC]
        def active_sources(self): return [SRC]
        def seen(self, triples): return set()
        def existing_urls(self, sid, urls): return {"https://x/0"}          # önceki çalışmada saklanmış
        def touch_sources(self, ids): pass
        def log_run(self, row): pass
        def mark_seen(self, rows): rec.seen.extend(rows)
        def queue_today(self): return {}, 0
        def insert_cluster(self, row): return row["id"]
        def upsert_articles(self, rows): rec.articles.extend(rows)

    class FakeClf:
        provider = "test"
        def __init__(self, s, m): pass
        def triage(self, batch):
            rec.triaged.extend(it.url for it, _ in batch)
            return [{"imp": 1, "tr": False, "eko": False, "c": ["sy"], "model": "t"} for _ in batch]

    monkeypatch.setattr(cli, "Store", FakeStore)
    monkeypatch.setattr(cli, "Classifier", FakeClf)
    monkeypatch.setattr(cli, "_fetch_one", lambda s, m, src: (src, items, None))
    monkeypatch.setenv("MAX_ITEMS_PER_SOURCE", "2")
    monkeypatch.setattr(cli.config, "OUT", tmp_path)
    s = SimpleNamespace(concurrency=1)
    cli.cmd_fetch(s, SimpleNamespace(all=False, source=None, method=None))

    assert "https://x/0" not in rec.triaged                       # saklı makale elemeye gitmedi
    assert rec.triaged == ["https://x/1", "https://x/2"]           # tavan: en yeni 2
    seen_hashes = {r["url_hash"] for r in rec.seen if r["importance"] == 0}
    assert not seen_hashes                                         # tavan dışı (3, 4) 'görüldü' sayılmadı
