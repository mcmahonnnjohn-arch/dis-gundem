from datetime import datetime, timedelta, timezone

from disgundem.fetch import Item
from disgundem.funnel import Gates, cluster, prefilter, select_for_queue
from disgundem.terms import Matcher

NOW = datetime(2026, 10, 20, 9, 0, tzinfo=timezone.utc)
A = {"id": "K001", "name": "Enab", "tier": "A", "country_id": "sy"}
B = {"id": "K116", "name": "NYT", "tier": "B", "country_id": "us"}


def it(title, hours_ago=1, src="K001", lang="en"):
    return Item(source_id=src, url=f"https://x/{abs(hash(title))}", title=title,
                published_at=NOW - timedelta(hours=hours_ago), lang=lang)


def test_prefilter_b_scope_needs_turkey_term():
    m, g = Matcher(), Gates()
    items = [it("Senate passes budget bill", src="K116"), it("Erdogan and Trump discuss F-35 sale", src="K116")]
    out = prefilter(items, B, m, g, NOW)
    assert [x.title for x in out] == ["Erdogan and Trump discuss F-35 sale"]


def test_prefilter_a_scope_keeps_domestic_but_drops_old():
    m, g = Matcher(), Gates()
    items = [it("Damascus forms new cabinet"), it("Old story", hours_ago=24 * 5)]
    out = prefilter(items, A, m, g, NOW)
    assert [x.title for x in out] == ["Damascus forms new cabinet"]


def _r(title, imp, c, hours_ago=1):
    return {"item": it(title, hours_ago), "imp": imp, "c": c, "tr": True}


def test_cluster_merges_same_event():
    rows = [
        _r("Turkey and Syria sign energy agreement in Damascus", 4, ["tr", "sy"]),
        _r("Syria, Turkey sign energy agreement during Damascus visit", 4, ["tr", "sy"]),
        _r("Israeli strike hits Gaza hospital", 5, ["il"]),
    ]
    groups = cluster(rows)
    assert sorted(len(g) for g in groups) == [1, 2]


def test_queue_caps_and_fives_pierce():
    g = Gates(store_min=3, queue_min=4, per_country_daily=2, total_daily=3)
    groups = [[_r(f"Syria item {i} unique words alpha{i}", 4, ["sy"])] for i in range(4)]
    groups += [[_r("Iran item unique beta", 4, ["ir"])], [_r("Iran item gamma special", 3, ["ir"])]]
    groups += [[_r("Ceasefire declared across Syria fronts", 5, ["sy"])]]
    queue, pool = select_for_queue(groups, g)
    imps = sorted(max(x["imp"] for x in grp) for grp in queue)
    # 5'lik tavanı deler; 4'lerden ülke tavanı (sy=2) ve toplam tavan (3) uygulanır; 3'lük havuza
    assert 5 in imps
    assert sum(1 for grp in queue if grp[0]["c"] == ["sy"]) <= 3   # 2 normal + 1 delen
    assert len(queue) <= 4
    assert any(max(x["imp"] for x in grp) == 3 for grp in pool)


def test_end_to_end_dry_run(monkeypatch, tmp_path):
    """LLM yok (terim modu): yalnız Türkiye geçen başlıklar saklanır, A iç gündem bu modda düşer."""
    import disgundem.cli as cli
    from disgundem import config
    monkeypatch.setattr(config, "OUT", tmp_path)
    import disgundem.store as store_mod
    monkeypatch.setattr(store_mod, "OUT", tmp_path)

    raw = [it("Erdogan meets Sharaa on reconstruction", src="K001"), it("Damascus bakery prices rise", src="K001"),
           it("Turkish drones spotted near Kobani", src="K001"), it("Football league resumes", src="K001")]

    def fake_fetch(s, matcher, src):
        return src, [x for x in raw] if src["id"] == "K001" else [], None
    monkeypatch.setattr(cli, "_fetch_one", fake_fetch)
    monkeypatch.setenv("DRY_RUN", "1")
    monkeypatch.setenv("LLM_PROVIDER", "none")
    cli.main(["fetch", "--source", "K001"])
    import json
    stats = json.loads((tmp_path / "funnel_last.json").read_text())
    assert stats["raw"] == 4
    assert stats["stored"] == 2          # yalnız Türkiye geçen iki başlık (terim modu)
    lines = (tmp_path / "articles.jsonl").read_text().splitlines()
    assert all(json.loads(l)["importance"] == 3 for l in lines)


def test_economic_analysis_lower_queue_threshold():
    from disgundem.funnel import Gates, select_for_queue
    g = Gates(store_min=3, queue_min=4, econ_queue_min=3, per_country_daily=4, total_daily=30)
    eko3 = [{"imp": 3, "eko": True, "c": ["sy"]}]
    plain3 = [{"imp": 3, "eko": False, "c": ["sy"]}]
    q, p = select_for_queue([eko3, plain3], g)
    assert q == [eko3] and p == [plain3]


def test_economic_analysis_ranks_behind_real_fours():
    from disgundem.funnel import Gates, select_for_queue
    g = Gates(store_min=3, queue_min=4, econ_queue_min=3, per_country_daily=1, total_daily=30)
    eko3 = [{"imp": 3, "eko": True, "c": ["sy"]}]
    news4 = [{"imp": 4, "eko": False, "c": ["sy"]}]
    q, p = select_for_queue([eko3, news4], g)
    assert q == [news4] and p == [eko3]


def test_quota_counts_only_primary_country():
    from disgundem.funnel import Gates, select_for_queue
    g = Gates(store_min=3, queue_min=4, econ_queue_min=3, per_country_daily=1, total_daily=30)
    saudi = [{"imp": 4, "eko": False, "c": ["sa"]}]
    tr_with_sa = [{"imp": 3, "eko": True, "c": ["tr", "sa"]}]     # asıl konu Türkiye; sa ikincil
    iq_with_sy = [{"imp": 3, "eko": True, "c": ["iq", "sy"]}]
    syria = [{"imp": 4, "eko": False, "c": ["sy"]}]
    q, p = select_for_queue([saudi, syria, tr_with_sa, iq_with_sy], g)
    assert p == [] and len(q) == 4


def test_turkey_primary_has_no_country_quota_but_total_cap_applies():
    from disgundem.funnel import Gates, select_for_queue
    g = Gates(store_min=3, queue_min=4, econ_queue_min=3, per_country_daily=1, total_daily=3)
    tr_items = [[{"imp": 4, "eko": False, "c": ["tr", "az"]}] for _ in range(4)]
    q, p = select_for_queue(tr_items, g)
    assert len(q) == 3 and len(p) == 1


def test_prefilter_caps_items_per_source_newest_first():
    from datetime import datetime, timedelta, timezone
    from disgundem.fetch import Item
    from disgundem.funnel import Gates, prefilter
    from disgundem.terms import Matcher
    now = datetime(2026, 10, 20, 12, tzinfo=timezone.utc)
    items = [Item(source_id="K1", url=f"u{i}", title=f"t{i}", published_at=now - timedelta(minutes=i)) for i in range(50)]
    out = prefilter(items, {"tier": "A"}, Matcher(), Gates(max_items_per_source=30), now=now)
    assert len(out) == 30 and out[0].url == "u0" and out[-1].url == "u29"
