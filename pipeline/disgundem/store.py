"""Depolama: Supabase (prod/dev) veya DRY_RUN'da data/out/*.jsonl.

Arayüz bilinçli olarak dar: upsert_sources, upsert_articles, log_run, metrics_window, upsert_metrics.
"""
from __future__ import annotations

import json
import logging
from dataclasses import asdict, is_dataclass
from datetime import date, datetime, timedelta, timezone
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

    @staticmethod
    def _clean(rows: list[dict]) -> list[dict]:
        """datetime/date gibi alanları Supabase'e gitmeden JSON'a uygun hale getirir (DRY_RUN dökümüyle aynı kural)."""
        return json.loads(json.dumps(rows, ensure_ascii=False, default=_json))

    def _upsert(self, table: str, rows: list[dict], on_conflict: str) -> None:
        if not rows:
            return
        if self.client is None:
            self._dump(table, rows)
            return
        for i in range(0, len(rows), 500):
            self.client.table(table).upsert(self._clean(rows[i:i + 500]), on_conflict=on_conflict).execute()

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
    def existing_urls(self, source_id: str, urls: list[str], days: int = 14) -> set[str]:
        """Bu kaynaktan son `days` günde saklanmış URL'ler arasından `urls` içinde olanlar.
        URL'ler sorguya konmaz: Google News yönlendirme adresleri yüzlerce karakter, liste GET sınırını aşıyordu."""
        if self.client is None or not urls:
            return set()
        since = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        r = (self.client.table("articles").select("url").eq("source_id", source_id)
             .gte("fetched_at", since).limit(5000).execute())
        have = {x["url"] for x in r.data}
        return have & set(urls)

    def existing_article_keys(self, source_ids: list[str]) -> set[tuple[str, str]]:
        """(source_id, url) çiftleri zaten saklı olanlar — içe almayı tekrar çalıştırmaya karşı güvenli kılar."""
        if self.client is None or not source_ids:
            return set()
        r = self.client.table("articles").select("source_id,url").in_("source_id", sorted(set(source_ids))).execute()
        return {(x["source_id"], x["url"]) for x in r.data}

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

    def unsummarized(self, limit: int = 200) -> list[dict]:
        """Kuyruktaki ve özeti olmayan kayıtlar; havuzdakiler (önem 3) editör çekince özetlenir."""
        if self.client is None:
            return []
        r = (self.client.table("articles").select("*").eq("status", "queued").is_("summary_tr", "null")
             .order("importance", desc=True).limit(limit).execute())
        return r.data

    def queued_server(self, limit: int = 200) -> list[dict]:
        """Kuyruktaki sunucu kökenli kayıtlar (Chrome oturumu özetleri tam metinden elle yazıldı; dokunulmaz)."""
        if self.client is None:
            return []
        chrome = {r["id"] for r in self.client.table("clusters").select("id").eq("origin", "chrome").execute().data}
        r = (self.client.table("articles").select("*").eq("status", "queued")
             .order("importance", desc=True).limit(limit + len(chrome)).execute())
        return [x for x in r.data if x.get("cluster_id") not in chrome][:limit]

    # --- olay birleştirme (olay.py) ---
    def recent_clusters(self, hours: int = 48) -> tuple[list[dict], list[dict]]:
        """Son `hours` saatte açılmış kuyruk/havuz kümeleri ve üye makaleleri."""
        if self.client is None:
            return [], []
        since = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
        cl = (self.client.table("clusters").select("id,status,origin,importance,first_seen,primary_country,countries,"
                                                  "article_count,title_tr,summary_tr")
              .in_("status", ["queued", "pool"]).gte("created_at", since).execute().data)
        ids = [c["id"] for c in cl]
        arts: list[dict] = []
        for i in range(0, len(ids), 100):
            arts += (self.client.table("articles").select("id,cluster_id,source_id,title,lang,status,summary_tr,"
                                                         "local_view_note,classification,uyarilar,published_at")
                     .in_("cluster_id", ids[i:i + 100]).execute().data)
        return cl, arts

    def merge_clusters(self, target: dict, others: list[dict], members: list[dict]) -> None:
        """`others` kümelerinin makalelerini `target`a taşır; diğerleri 'rejected' + merged_into olur."""
        if self.client is None:
            self._dump("merges", [{"target": target["id"], "others": [o["id"] for o in others]}])
            return
        oids = [o["id"] for o in others]
        upd = {"cluster_id": target["id"]}
        if target["status"] == "queued":
            upd["status"] = "queued"   # kuyruktaki olaya katılan havuz haberi de özetlensin
        self.client.table("articles").update(upd).in_("cluster_id", oids).execute()
        self.client.table("clusters").update({"status": "rejected", "merged_into": target["id"]}).in_("id", oids).execute()
        allc = [target, *others]
        self.client.table("clusters").update({
            "importance": max((c.get("importance") or 0) for c in allc) or None,
            "article_count": len(members),
            "countries": sorted({x for c in allc for x in (c.get("countries") or [])}),
        }).eq("id", target["id"]).execute()

    def update_cluster(self, cid: str, fields: dict) -> None:
        if self.client is None:
            self._dump("cluster_updates", [{"id": cid, **fields}])
            return
        self.client.table("clusters").update(self._clean([fields])[0]).eq("id", cid).execute()

    def set_articles_status(self, ids: list[str], status: str) -> None:
        if self.client is None or not ids:
            return
        self.client.table("articles").update({"status": status}).in_("id", ids).execute()

    def insert_eval_run(self, row: dict) -> None:
        """Test seti ölçüm sonucu (özetler ve puanlar; makale metni yok)."""
        if self.client is None:
            self._dump("eval_runs", [row])
            return
        self.client.table("eval_runs").insert(self._clean([row])[0]).execute()

    def due_sources(self) -> list[dict]:
        """Çekirdek kaynaklardan tarama aralığı dolmuş olanlar (think tank haftalık, diğerleri saatlik)."""
        rows = self.active_sources()
        if self.client is None:
            return rows
        now = datetime.now(timezone.utc)
        out = []
        for r in rows:
            last = r.get("last_fetched_at")
            iv = r.get("scan_interval") or "1 hour"
            hours = 24 * 7 if "week" in str(iv) or "7 day" in str(iv) else 1
            if not last or (now - datetime.fromisoformat(str(last).replace("Z", "+00:00"))).total_seconds() >= hours * 3600 - 300:
                out.append(r)
        return out

    def touch_sources(self, ids: list[str]) -> None:
        if self.client is None or not ids:
            return
        self.client.table("sources").update({"last_fetched_at": datetime.now(timezone.utc).isoformat()}).in_("id", ids).execute()

    # ---- huni
    def seen(self, pairs: list[tuple[str, str, str]]) -> set[tuple[str, str]]:
        """(source_id, url_hash, title_hash) listesinden daha önce görülenleri döndürür.
        Başlık hash'i kaynaklar arası da eşleşir (aynı ajans metni birden çok sitede)."""
        if self.client is None or not pairs:
            return set()
        out: set[tuple[str, str]] = set()
        by_src: dict[str, list[str]] = {}
        for sid, uh, _ in pairs:
            by_src.setdefault(sid, []).append(uh)
        for sid, hashes in by_src.items():
            for i in range(0, len(hashes), 200):
                r = (self.client.table("seen_items").select("source_id,url_hash")
                     .eq("source_id", sid).in_("url_hash", hashes[i:i + 200]).execute())
                out |= {(x["source_id"], x["url_hash"]) for x in r.data}
        th = list({t for _, _, t in pairs})
        seen_titles: set[str] = set()
        for i in range(0, len(th), 200):
            r = self.client.table("seen_items").select("title_hash").in_("title_hash", th[i:i + 200]).execute()
            seen_titles |= {x["title_hash"] for x in r.data}
        out |= {(sid, uh) for sid, uh, t in pairs if t in seen_titles}
        return out

    def mark_seen(self, rows: list[dict]) -> None:
        self._upsert("seen_items", rows, "source_id,url_hash")

    def queue_today(self, origin: str = "server") -> tuple[dict[str, int], int]:
        """Bugün kuyruğa giren küme sayıları — yalnız verilen köken için (server | chrome; ayrı kotalar).
        Ülke kotası 'tr' dışı birincil ülkeleri sayar; toplam, 'tr' dahil tüm kümeleri sayar."""
        if self.client is None:
            return {}, 0
        r = self.client.table("queue_today").select("*").eq("origin", origin).execute()
        per = {x["country_id"]: x["n"] for x in r.data if x["country_id"] and x["country_id"] != "tr"}
        return per, sum(x["n"] for x in r.data)

    def insert_cluster(self, row: dict) -> str:
        if self.client is None:
            self._dump("clusters", [row])
            return row["id"]
        self.client.table("clusters").insert(self._clean([row])[0]).execute()
        return row["id"]

    # ---- harita (0008)
    def upsert_map_dictionaries(self, places: list[dict], actors: list[dict]) -> None:
        self._upsert("places", places, "id")
        self._upsert("actors", actors, "id")

    def map_candidates(self, hours: int = 72, redo: bool = False) -> tuple[list[dict], list[dict]]:
        """Haritaya bağlanmamış (event_type boş) kuyruk/onaylı/yayında kümeler ve üye makaleleri."""
        if self.client is None:
            return [], []
        since = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
        q = (self.client.table("clusters").select("id,status,importance,primary_country,countries,title_tr,summary_tr")
             .in_("status", ["queued", "approved", "published"]).is_("merged_into", "null").gte("created_at", since))
        if not redo:
            q = q.is_("event_type", "null")
        cl = q.execute().data
        ids = [c["id"] for c in cl]
        arts: list[dict] = []
        for i in range(0, len(ids), 100):
            arts += (self.client.table("articles").select("id,cluster_id,title,summary_tr")
                     .in_("cluster_id", ids[i:i + 100]).execute().data)
        return cl, arts

    def set_map_links(self, cid: str, fields: dict, places: list[tuple[str, bool]],
                      actors: list[tuple[str, str | None]]) -> None:
        """Kümenin yer ve aktör bağlarını baştan yazar (yeniden çalıştırmada eski bağlar kalmasın)."""
        if self.client is None:
            self._dump("map_links", [{"id": cid, **fields, "places": places, "actors": actors}])
            return
        self.client.table("cluster_places").delete().eq("cluster_id", cid).execute()
        self.client.table("cluster_actors").delete().eq("cluster_id", cid).execute()
        if places:
            self.client.table("cluster_places").insert(
                [{"cluster_id": cid, "place_id": p, "is_primary": b} for p, b in places]).execute()
        if actors:
            self.client.table("cluster_actors").insert(
                [{"cluster_id": cid, "actor_id": a, "role": r} for a, r in actors]).execute()
        self.update_cluster(cid, fields)

    def note_unresolved(self, names: list[tuple[str, str | None]]) -> None:
        """Sözlükte bulunamayan yer adları; görülme sayısı artar, editör `resolved_to` ile eşler."""
        if not names:
            return
        if self.client is None:
            self._dump("place_unresolved", [{"raw_name": n, "country_id": c} for n, c in names])
            return
        now = datetime.now(timezone.utc).isoformat()
        uniq = {n: c for n, c in names}
        have = {r["raw_name"]: r["seen_count"] for r in self.client.table("place_unresolved")
                .select("raw_name,seen_count").in_("raw_name", list(uniq)).execute().data}
        self._upsert("place_unresolved", [{"raw_name": n, "country_id": c, "seen_count": have.get(n, 0) + 1,
                                           "last_seen": now} for n, c in uniq.items()], "raw_name")

    def map_report_data(self, days: int = 7) -> tuple[list[dict], dict, dict, list[dict]]:
        """Harita ölçüm raporu için: pencere kümeleri, kümenin yerleri, aktörleri, çözülemeyen adlar."""
        if self.client is None:
            return [], {}, {}, []
        since = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        cl = (self.client.table("clusters").select("id,status,primary_country,event_type,turkey_stake,title_tr")
              .in_("status", ["queued", "approved", "published"]).is_("merged_into", "null")
              .gte("created_at", since).execute().data)
        ids = [c["id"] for c in cl]
        pl: dict[str, list] = {}
        ac: dict[str, list] = {}
        for i in range(0, len(ids), 100):
            chunk = ids[i:i + 100]
            for r in self.client.table("cluster_places").select("cluster_id,place_id,is_primary").in_("cluster_id", chunk).execute().data:
                pl.setdefault(r["cluster_id"], []).append((r["place_id"], r["is_primary"]))
            for r in self.client.table("cluster_actors").select("cluster_id,actor_id").in_("cluster_id", chunk).execute().data:
                ac.setdefault(r["cluster_id"], []).append(r["actor_id"])
        un = (self.client.table("place_unresolved").select("raw_name,country_id,seen_count,resolved_to")
              .gte("last_seen", since).execute().data)
        return cl, pl, ac, un

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
