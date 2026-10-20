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
