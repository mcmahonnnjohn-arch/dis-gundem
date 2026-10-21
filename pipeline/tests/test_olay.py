"""olay: gruplama eşlemesi, hedef seçimi, metinsiz kuyruk kümesinin havuza düşmesi, olay özeti."""
import json
from types import SimpleNamespace

from disgundem import cli, olay
from disgundem.config import Settings


class FakeClf:
    provider, model, summary_model = "anthropic", "h", "s"
    def __init__(self, replies): self.replies = list(replies); self.calls = []
    def _call(self, system, user, model=None, cache=False):
        self.calls.append(user); return json.dumps(self.replies.pop(0))
    def audit(self, item, text, summary): return {"gecti": True, "sorunlar": [], "duzeltilmis_ozet": None}


def test_group_items_maps_indices_and_drops_singletons():
    items = [{"k": "a", "t": ["x"]}, {"k": "b", "t": ["y"]}, {"k": "c", "t": ["z"]}]
    g = olay.group_items(FakeClf([{"gruplar": [[0, 2], [1], [0, 1]]}]), items)
    assert g == [["a", "c"]]          # tekli grup atılır, aynı küme iki gruba giremez


def test_pick_target_prefers_queue_then_chrome_then_importance():
    cs = [{"id": "p", "status": "pool", "importance": 5}, {"id": "q", "status": "queued", "importance": 3},
          {"id": "c", "status": "queued", "origin": "chrome", "importance": 3}]
    assert olay.pick_target(cs)["id"] == "c"


def _run_olay(monkeypatch, clusters, arts, replies, drop=True):
    rec = SimpleNamespace(upd=[], st=[])

    class FakeStore:
        def __init__(self, s): pass
        def recent_clusters(self, hours): return clusters, arts
        def update_cluster(self, cid, f): rec.upd.append((cid, f))
        def set_articles_status(self, ids, st): rec.st.append((ids, st))

    monkeypatch.setattr(cli, "Store", FakeStore)
    monkeypatch.setattr(cli, "Classifier", lambda s: FakeClf(replies))
    monkeypatch.setattr(cli, "load_sources", lambda: [])
    cli.cmd_olay(Settings(drop_no_text=drop), SimpleNamespace(saat=48, yeniden=False))
    return rec


def test_no_readable_text_drops_queued_cluster(monkeypatch):
    cl = [{"id": "k1", "status": "queued", "origin": "server"}]
    arts = [{"id": "a1", "cluster_id": "k1", "title": "t", "classification": {"metin": "http-403"}, "summary_tr": "s"}]
    rec = _run_olay(monkeypatch, cl, arts, [])
    assert rec.upd == [("k1", {"status": "pool"})] and rec.st == [(["a1"], "pool")]


def test_one_readable_member_keeps_cluster_and_writes_event(monkeypatch):
    cl = [{"id": "k1", "status": "queued", "origin": "server"}]
    arts = [{"id": "a1", "source_id": "K1", "cluster_id": "k1", "title": "t1", "classification": {"metin": "http-403"}, "summary_tr": "s1"},
            {"id": "a2", "source_id": "K2", "cluster_id": "k1", "title": "t2", "classification": {"metin": "ok"}, "summary_tr": "s2",
             "local_view_note": "Yunan basını yasadışı sayıyor"}]
    rec = _run_olay(monkeypatch, cl, arts, [{"baslik": "Libya meclisi mutabakatı onayladı", "ozet": "Bir. İki.",
                                             "bakis_farki": "Yunan basını yasadışı sayıyor."}])
    assert rec.st == [] and rec.upd[0][1]["bakis_farki"].startswith("Yunan")


def test_legacy_articles_without_metin_flag_are_not_dropped(monkeypatch):
    cl = [{"id": "k1", "status": "queued", "origin": "server"}]
    arts = [{"id": "a1", "cluster_id": "k1", "title": "t", "classification": {"prompt": "classify_v1"}, "summary_tr": "s"}]
    assert _run_olay(monkeypatch, cl, arts, []).st == []


def test_within_window_keeps_old_event_separate():
    t = {"id": "t", "first_seen": "2026-10-10T00:00:00+00:00"}
    near = {"id": "n", "first_seen": "2026-10-11T10:00:00+00:00"}
    far = {"id": "f", "first_seen": "2026-10-15T00:00:00+00:00"}
    nodate = {"id": "d", "first_seen": None}
    inside, outside = olay.within_window(t, [t, near, far, nodate], hours=48)
    assert [c["id"] for c in inside] == ["t", "n", "d"] and [c["id"] for c in outside] == ["f"]


class AuditClf(FakeClf):
    """Başlıktaki yanlış unvanı yakalayıp düzelten denetçi."""
    def audit(self, item, text, summary):
        if "Genelkurmay'ı Munir" in summary:
            return {"gecti": False, "sorunlar": [{"tur": "unvan", "ozet_ifadesi": "Genelkurmay'ı Munir", "aciklama": "x"}],
                    "duzeltilmis_ozet": summary.replace("Genelkurmay'ı Munir", "Genelkurmay Başkanı Munir")}
        return {"gecti": True, "sorunlar": [], "duzeltilmis_ozet": None}


def test_audit_event_fixes_title_and_reports_issue():
    members = [{"kaynak": "K", "baslik": "b", "ozet": "o"}]
    res = olay.audit_event(AuditClf([]), members, {"baslik": "Pakistan Genelkurmay'ı Munir geldi", "ozet": "Temiz özet.", "bakis_farki": None})
    assert res["baslik"] == "Pakistan Genelkurmay Başkanı Munir geldi" and res["ozet"] == "Temiz özet."
    assert res["denetim"] == [{"tur": "unvan", "ozet_ifadesi": "Genelkurmay'ı Munir", "aciklama": "x", "alan": "baslik"}]


def test_audit_error_leaves_event_text_unchanged():
    class Err(FakeClf):
        def audit(self, item, text, summary): return {"gecti": None, "sorunlar": [], "duzeltilmis_ozet": None}
    res = olay.audit_event(Err([]), [], {"baslik": "B", "ozet": "O."})
    assert res["baslik"] == "B" and res["denetim"] == []
