"""evaluate: kural puanları, Türkçe büyük/küçük harf, toplama, CLI akışı (metin saklanmaz)."""
import json
from types import SimpleNamespace

from disgundem import cli
from disgundem import evaluate as ev
from disgundem.config import Settings

CASE = {"no": 1, "lang": "ar", "source_id": "K012", "url": "https://ex.com/a", "baslik": "t",
        "referans_ozet": "Milli Savunma Bakanı Yaşar Güler, AFP'ye yazılı yanıtında konuştu.",
        "kaynak_olgulari": ["Güler AFP'ye yazılı yanıt verdi."],
        "olmali": ["Güler", "AFP|Fransız haber ajansı", "IRAK"], "olmamali": ["Orgeneral", "başlığa göre"]}


def test_rule_scores_turkish_case_and_alternatives():
    r = ev.rule_scores(CASE, "Milli Savunma Bakanı Güler, Fransız haber ajansına Irak'tan söz etti.")
    assert r["olmali_oran"] == 1.0 and r["ihlal"] == [] and r["bicim_ok"] and not r["surec"]


def test_rule_scores_violation_and_process():
    r = ev.rule_scores(CASE, "Başlığa göre Orgeneral Güler konuştu. İki. Üç. Dört.")
    assert set(r["ihlal"]) == {"Orgeneral", "başlığa göre"} and r["surec"] and not r["bicim_ok"]
    assert r["eksik"] == ["AFP|Fransız haber ajansı", "IRAK"]


def test_aggregate_by_language():
    mk = lambda no, lang, ok, d: ev.CaseResult(no, lang, "ok", "x", [], {"olmali_oran": ok, "ihlal": [], "eksik": [],
                                               "cumle": 1, "uzunluk": 1, "bicim_ok": True, "surec": False},
                                               {"dogruluk": d, "kapsam": 4, "atif": 5})
    agg = ev.aggregate([mk(1, "ar", 1.0, 5), mk(2, "ar", 0.5, 3), mk(3, "el", 1.0, 4)])
    assert agg["n"] == 3 and agg["dil"]["ar"]["dogruluk"] == 4.0 and agg["dil"]["el"]["n"] == 1


def test_cmd_eval_flow_never_stores_text(monkeypatch, tmp_path):
    saved = []
    (tmp_path / "set.jsonl").write_text(json.dumps(CASE, ensure_ascii=False) + "\n", encoding="utf-8")
    monkeypatch.setattr(ev, "SET_PATH", tmp_path / "set.jsonl")
    monkeypatch.setattr(ev, "load_set", lambda only_approved=False: [CASE])

    class FakeClf:
        provider, model, summary_model = "anthropic", "h", "s"
        def __init__(self, s): pass
        def classify(self, item, src, text=None, audit=True):
            assert text == "GİZLİ METİN"
            return SimpleNamespace(summary_tr="Bakan Güler AFP'ye Irak'ı anlattı.", warnings=[])
        def _call(self, system, user, model=None, cache=False):
            if "hakem" in system or "hakemi" in system:
                assert "GİZLİ METİN" in user          # hakem metni görür (yalnız çağrıda)
            return json.dumps({"dogruluk": 5, "kapsam": 4, "atif": 5, "hatalar": []})

    class FakeStore:
        def __init__(self, s): pass
        def insert_eval_run(self, row): saved.append(row)

    monkeypatch.setattr(cli, "Classifier", FakeClf)
    monkeypatch.setattr(cli, "Store", FakeStore)
    monkeypatch.setattr(cli, "make_client", lambda s: SimpleNamespace(close=lambda: None))
    monkeypatch.setattr(ev, "fetch_text", lambda c, u, ua: ("GİZLİ METİN", "ok"))
    monkeypatch.setattr(cli.config, "OUT", tmp_path)
    cli.cmd_eval(Settings(article_text=True), SimpleNamespace(no=None, onayli=False, hakemsiz=False, etiket="t"))
    row = saved[0]
    assert row["ozet"]["dogruluk"] == 5 and row["ozet"]["olmali_oran"] == 1.0
    assert "GİZLİ" not in json.dumps(row, ensure_ascii=False)
