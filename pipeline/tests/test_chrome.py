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
        {"source_id": "K070", "url": "https://azertag.az/x", "title": "t", "summary_tr": "Kısa özet."},
        {"source_id": "K002", "url": "https://syria.tv/x", "title": "t", "summary_tr": "Kısa özet."},
    ]
    p = tmp_path / "s.json"
    p.write_text(json.dumps(recs), encoding="utf-8")
    rows, _, rejected = load_session(p)
    assert [r["source_id"] for r in rows] == ["K070"] and rows[0]["lang"] == "az"
    assert len(rejected) == 1 and "Chrome listesinde değil" in rejected[0]
