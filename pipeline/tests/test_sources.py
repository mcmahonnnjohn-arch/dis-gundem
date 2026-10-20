from disgundem.sources import load_sources, dictionaries, COUNTRIES, REGION_BY_NAME


def test_all_countries_mapped():
    srcs = load_sources()
    assert len(srcs) >= 250
    ids = {s.id for s in srcs}
    assert len(ids) == len(srcs), "ID tekrarı"


def test_dictionaries_consistent():
    d = dictionaries()
    region_ids = {r["id"] for r in d["regions"]}
    for c in d["countries"]:
        assert c["region_id"] in region_ids, c
    for s in load_sources():
        assert s.region_id in region_ids
        assert s.country_id in {c["id"] for c in d["countries"]}


def test_core_has_feed_or_fallback():
    for s in load_sources():
        if s.status == "cekirdek":
            assert s.method in ("rss", "gnews", "scrape", "manual"), s.id
            if s.method == "rss":
                assert s.feed_url and s.feed_url.startswith("http"), s.id


def test_clean_countries_drops_unknown_and_keeps_order():
    from disgundem.sources import clean_countries
    assert clean_countries(["JO", "sa", "ye", "tr", "sa"], "sy") == ["sa", "tr"]
    assert clean_countries(["jo", "ye"], "sy") == ["sy"]
    assert clean_countries([], None) == []


def test_clean_ids_filters_to_dictionary():
    from disgundem.sources import KNOWN_THEMES, clean_ids
    assert clean_ids(["Enerji", "uzay", "enerji", "ekonomi"], KNOWN_THEMES) == ["enerji", "ekonomi"]
