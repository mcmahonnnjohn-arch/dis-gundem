"""Depolama: Supabase (prod/dev) veya DRY_RUN'da data/out/*.jsonl.

Arayüz bilinçli olarak dar: upsert_sources, upsert_articles, log_run, metrics_window, upsert_metrics.
"""
from __future__ import annotations

import json
import logging
from dataclasses import asdict, is_dataclass
from datetime import date, datetime
from pathlib import Path

from .config import OUT, Settings

log = logging.getLogger(__name__)


def _json(o):
    if isinstance(o, (datetime, date)):
        return o.isoformat()
    if is_dataclass(o):
        return asdict(o)
    raise TypeError(type(o))


class Store:
    def __init__(self, s: Settings):
        self.s = s
        self.client = None
        if s.has_db:
            from supabase import create_client
            self.client = create_client(s.supabase_url, s.supabase_key)
        else:
            log.info("DRY_RUN: çıktılar %s altına yazılır", OUT)

    # ---- yardımcı
    def _dump(self, name: str, rows: list[dict]) -> None:
        p: Path = OUT / f"{name}.jsonl"
        with open(p, "a", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False, default=_json) + "\n")

    def _upsert(self, table: str, rows: list[dict], on_conflict: str) -> None:
        if not rows:
            return
        if self.client is None:
            self._dump(table, rows)
            return
        for i in range(0, len(rows), 500):
            self.client.table(table).upsert(rows[i:i + 500], on_conflict=on_conflict).execute()

    # ---- sözlükler ve kaynaklar
    def upsert_dictionaries(self, d: dict[str, list[dict]]) -> None:
        self._upsert("regions", d["regions"], "id")
        self._upsert("countries", d["countries"], "id")
        self._upsert("dossiers", d["dossiers"], "id")
        self._upsert("themes", d["themes"], "id")

    def upsert_sources(self, rows: list[dict]) -> None:
        self._upsert("sources", rows, "id")

    def active_sources(self) -> list[dict]:
        if self.client is None:
            from .sources import load_sources
            return [s.as_row() for s in load_sources() if s.status == "cekirdek"]
        r = self.client.table("sources").select("*").in_("status", ["cekirdek"]).execute()
        return r.data

    # ---- içerik
    def existing_urls(self, source_id: str, urls: list[str]) -> set[str]:
        if self.client is None or not urls:
            return set()
        r = self.client.table("articles").select("url").eq("source_id", source_id).in_("url", urls).execute()
        return {x["url"] for x in r.data}

    def upsert_articles(self, rows: list[dict]) -> None:
        self._upsert("articles", rows, "source_id,url")

    def set_article_links(self, article_id: str, countries: list[str], themes: list[str], dossiers: list[str]) -> None:
        if self.client is None:
            return
        if countries:
            self.client.table("article_countries").upsert(
                [{"article_id": article_id, "country_id": c} for c in countries], on_conflict="article_id,country_id").execute()
        if themes:
            self.client.table("article_themes").upsert(
                [{"article_id": article_id, "theme_id": t} for t in themes], on_conflict="article_id,theme_id").execute()
        if dossiers:
            self.client.table("article_dossiers").upsert(
                [{"article_id": article_id, "dossier_id": d} for d in dossiers], on_conflict="article_id,dossier_id").execute()

    def unclassified(self, limit: int = 200) -> list[dict]:
        if self.client is None:
            return []
        r = (self.client.table("articles").select("*").eq("status", "fetched")
             .order("published_at", desc=True).limit(limit).execute())
        return r.data

    def log_run(self, row: dict) -> None:
        self._upsert("fetch_runs", [row], "id")

    # ---- ölçüm
    def window_counts(self, start: date, end: date) -> list[dict]:
        """source_id başına pencere içi sayımlar."""
        if self.client is None:
            return []
        r = (self.client.table("articles")
             .select("source_id,is_turkey_related,importance,status,published_at")
             .gte("published_at", start.isoformat()).lt("published_at", end.isoformat()).execute())
        agg: dict[str, dict] = {}
        for a in r.data:
            m = agg.setdefault(a["source_id"], {"fetched": 0, "turkey_related": 0, "domestic_major": 0, "published": 0})
            m["fetched"] += 1
            m["turkey_related"] += 1 if a.get("is_turkey_related") else 0
            m["domestic_major"] += 1 if (a.get("importance") or 0) >= 3 else 0
            m["published"] += 1 if a.get("status") == "published" else 0
        return [{"source_id": k, "window_start": start, "window_end": end, **v} for k, v in agg.items()]

    def upsert_metrics(self, rows: list[dict]) -> None:
        self._upsert("source_metrics", rows, "source_id,window_start,window_end")
