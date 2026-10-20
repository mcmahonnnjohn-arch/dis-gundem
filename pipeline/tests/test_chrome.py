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
    g = Gates(store_min=3, queue_min=4, per_country_daily=1, total_daily=30)
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
