"""Chrome oturumu listesi: premium + engelli-RSS kaynakları import'ta kabul edilir, liste dışı reddedilir."""
import json

from disgundem.fetch.premium import CHROME_IDS, PREMIUM_IDS, load_session

BLOCKED = {"K001", "K019", "K020", "K037", "K065", "K068", "K070", "K095",
           "K124", "K129", "K139", "K154", "K230", "K245"}


def test_list_contents():
    assert PREMIUM_IDS == {"K170", "K171", "K172", "K173", "K174", "K175"}
    assert BLOCKED <= CHROME_IDS and len(CHROME_IDS) == 20


def test_import_accepts_blocked_rejects_others(tmp_path):
    recs = [
        {"source_id": "K070", "url": "https://azertag.az/x", "title": "t", "summary_tr": "Kısa özet.", "importance": 4},
        {"source_id": "K002", "url": "https://syria.tv/x", "title": "t", "summary_tr": "Kısa özet.", "importance": 4},
    ]
    p = tmp_path / "s.json"
    p.write_text(json.dumps(recs), encoding="utf-8")
    rows, _, rejected = load_session(p)
    assert [r["source_id"] for r in rows] == ["K070"] and rows[0]["lang"] == "az"
    assert len(rejected) == 1 and "Chrome listesinde değil" in rejected[0]


def test_route_matches_server_funnel():
    from disgundem.fetch.premium import route
    from disgundem.funnel import Gates
    g = Gates(store_min=3, queue_min=4, chrome_per_country_daily=1, chrome_total_daily=30)
    mk = lambda imp, c: {"importance": imp, "classification": {"countries": c}, "status": "queued"}
    rows = [mk(2, ["sy"]), mk(3, ["sy"]), mk(4, ["sy"]), mk(4, ["sy"]), mk(5, ["sy"])]
    kept, below = route(rows, g)
    assert len(below) == 1 and len(kept) == 4
    st = sorted((r["importance"], r["status"]) for r in kept)
    # sy kotası 1: 5 önce sıralanır ve kotayı kullanır (5 tavanı deler); 4'ler kotaya takılıp havuza düşer
    assert st == [(3, "pool"), (4, "pool"), (4, "pool"), (5, "queued")]


def test_importance_required(tmp_path):
    p = tmp_path / "s.json"
    p.write_text(json.dumps([{"source_id": "K001", "url": "https://x/a", "title": "t", "summary_tr": "s"}]),
                 encoding="utf-8")
    rows, _, rejected = load_session(p)
    assert not rows and "importance" in rejected[0]


def test_session_file_routes():
    """Gerçek oturum dosyası: hepsi kabul edilir, eşik altı yok; Enab Baladi alt kümesi 4 kuyruk / 3 havuz."""
    from pathlib import Path
    from disgundem.fetch.premium import route
    from disgundem.funnel import Gates
    f = Path(__file__).resolve().parents[2] / "data" / "premium" / "2026-10-20.json"
    rows, _, rej = load_session(f)
    assert not rej
    g = Gates(store_min=3, queue_min=4, econ_queue_min=3, per_country_daily=4, total_daily=30)
    kept, below = route([r for r in rows if r["source_id"] == "K001"], g)
    assert not below
    assert sum(r["status"] == "queued" for r in kept) == 4 and sum(r["status"] == "pool" for r in kept) == 3


def test_import_skips_existing(monkeypatch, tmp_path, capsys):
    """İkinci çalıştırma zaten saklı (source_id, url) kayıtlarını atlar; yeni küme açmaz."""
    from types import SimpleNamespace
    from disgundem import cli

    class FakeStore:
        def __init__(self, s): self.arts, self.clusters = [], []
        def existing_article_keys(self, ids): return {(a["source_id"], a["url"]) for a in STORE.arts}
        def queue_today(self, origin="server"): return {}, 0
        def insert_cluster(self, row): STORE.clusters.append(row)
        def upsert_articles(self, rows): STORE.arts.extend(rows)
        def set_article_links(self, *a): pass

    STORE = SimpleNamespace(arts=[], clusters=[])
    monkeypatch.setattr(cli, "Store", FakeStore)
    p = tmp_path / "s.json"
    p.write_text(json.dumps([{"source_id": "K070", "url": "https://azertag.az/x", "title": "t",
                              "summary_tr": "s", "importance": 4, "countries": ["az", "tr"]}]), encoding="utf-8")
    from disgundem.fetch.rss import canonical  # noqa: F401  (url kanonikleştirilmiş saklanır)
    cli.cmd_premium_import(None, SimpleNamespace(file=str(p)))
    cli.cmd_premium_import(None, SimpleNamespace(file=str(p)))
    assert len(STORE.arts) == 1 and len(STORE.clusters) == 1
    assert "1 zaten içeride" in capsys.readouterr().out


def test_chrome_uses_own_quota_not_server_quota():
    """Sunucu kotası dolu olsa da Chrome kaydı kendi kotasıyla kuyruğa girer; küme origin='chrome' yazılır."""
    from disgundem.fetch.premium import route
    from disgundem.funnel import Gates
    g = Gates(store_min=3, queue_min=4, per_country_daily=0, total_daily=0,          # sunucu kotası sıfır
              chrome_per_country_daily=2, chrome_total_daily=5)
    rows = [{"importance": 4, "classification": {"countries": ["az", "tr"]}, "status": "queued"}]
    kept, _ = route(rows, g, per_today={}, total_today=0)
    assert kept[0]["status"] == "queued"
