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
