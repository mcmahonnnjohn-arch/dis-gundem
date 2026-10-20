"""Store: Supabase'e giden her satır JSON'a uygun olmalı (datetime alanları dahil)."""
import json
from datetime import datetime, timezone

from disgundem.store import Store


class _Q:
    def __init__(self, sink): self.sink = sink
    def upsert(self, rows, on_conflict=None): self.sink.append(json.dumps(rows)); return self
    def insert(self, row): self.sink.append(json.dumps(row)); return self
    def execute(self): return self


class _Client:
    def __init__(self): self.sent = []
    def table(self, name): return _Q(self.sent)


def test_datetimes_serialized_for_upsert_and_cluster_insert():
    st = Store.__new__(Store)
    st.client = _Client()
    now = datetime(2026, 10, 20, 12, 0, tzinfo=timezone.utc)
    st.upsert_articles([{"id": "a", "source_id": "K1", "url": "u", "published_at": now, "fetched_at": now}])
    st.insert_cluster({"id": "c", "first_seen": now, "last_seen": now, "created_at": now})
    st.log_run({"id": "r", "started_at": now, "finished_at": now})
    assert len(st.client.sent) == 3 and all("2026-10-20T12:00:00+00:00" in x for x in st.client.sent)


def test_existing_urls_does_not_put_urls_in_query():
    calls = []

    class Q:
        def __init__(self): self.data = [{"url": "https://a/1"}, {"url": "https://a/9"}]
        def select(self, *a): calls.append(("select", a)); return self
        def eq(self, *a): calls.append(("eq", a)); return self
        def gte(self, *a): calls.append(("gte", a)); return self
        def limit(self, n): return self
        def in_(self, *a): raise AssertionError("URL listesi sorguya konmamalı")
        def execute(self): return self

    st = Store.__new__(Store)
    st.client = type("C", (), {"table": lambda self, n: Q()})()
    long_urls = ["https://a/1", "https://news.google.com/rss/articles/" + "x" * 600]
    assert st.existing_urls("K1", long_urls) == {"https://a/1"}
    assert ("eq", ("source_id", "K1")) in calls


def test_queue_today_counts_tr_in_total_and_filters_origin():
    seen = {}

    class Q:
        data = [{"origin": "server", "country_id": "tr", "n": 3}, {"origin": "server", "country_id": "sy", "n": 2},
                {"origin": "server", "country_id": None, "n": 1}]
        def select(self, *a): return self
        def eq(self, k, v): seen[k] = v; return self
        def execute(self): return self

    st = Store.__new__(Store)
    st.client = type("C", (), {"table": lambda self, n: Q()})()
    per, total = st.queue_today("server")
    assert seen == {"origin": "server"} and per == {"sy": 2} and total == 6
