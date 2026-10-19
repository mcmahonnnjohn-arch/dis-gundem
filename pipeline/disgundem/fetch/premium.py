"""Premium kaynaklar (FT, Bloomberg, WSJ, Economist, Foreign Affairs, Foreign Policy).

Sunucu tarafında toplanmaz. Editör, Claude in Chrome oturumunda (kendi abonelikleriyle) günlük/haftalık tarama yapar;
oturumun çıktısı bu modülün beklediği JSON biçiminde `data/premium/YYYY-MM-DD.json` olarak kaydedilir ve
`disgundem premium-import <dosya>` ile kuyruğa girer.

Telif kuralları (docs/HEDEF.md) burada zorlanır:
- makale metni ve uzun alıntı kabul edilmez (summary_tr ≤ 600 karakter, tırnak içi parça ≤ 15 kelime)
- yalnız başlık, tarih, link, kendi cümlelerimizle özet ve etiketler saklanır
"""
from __future__ import annotations

import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path

from dateutil import parser as dtparse

from .rss import canonical

PREMIUM_IDS = {"K170", "K171", "K172", "K173", "K174", "K175"}
MAX_SUMMARY = 600
MAX_QUOTE_WORDS = 15
QUOTE = re.compile(r'["“”«»]([^"“”«»]{20,})["“”«»]')


def _check(rec: dict) -> str | None:
    if rec.get("source_id") not in PREMIUM_IDS:
        return f"source_id premium değil: {rec.get('source_id')}"
    for k in ("url", "title", "summary_tr"):
        if not rec.get(k):
            return f"eksik alan: {k}"
    if len(rec["summary_tr"]) > MAX_SUMMARY:
        return f"özet çok uzun ({len(rec['summary_tr'])} > {MAX_SUMMARY}); makale metni/uzun alıntı olabilir"
    for m in QUOTE.finditer(rec["summary_tr"]):
        if len(m.group(1).split()) > MAX_QUOTE_WORDS:
            return f"alıntı {MAX_QUOTE_WORDS} kelimeyi aşıyor"
    if rec.get("body") or rec.get("text") or rec.get("content"):
        return "makale metni alanı kabul edilmez"
    return None


def load_session(path: str | Path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(data, dict) and "items" in data:
        data = data["items"]
    rows, links, rejected = [], [], []
    for rec in data:
        err = _check(rec)
        if err:
            rejected.append(f"{rec.get('url', '?')}: {err}")
            continue
        try:
            pub = dtparse.parse(rec.get("published_at")) if rec.get("published_at") else None
            if pub and not pub.tzinfo:
                pub = pub.replace(tzinfo=timezone.utc)
        except (ValueError, TypeError):
            pub = None
        aid = str(uuid.uuid4())
        rows.append({
            "id": aid, "source_id": rec["source_id"], "url": canonical(rec["url"]), "title": rec["title"].strip(),
            "lang": "en", "published_at": pub, "fetched_at": datetime.now(timezone.utc), "excerpt": None,
            "is_turkey_related": bool(rec.get("turkey_related", True)),
            "importance": rec.get("importance"), "frame": rec.get("frame"),
            "summary_tr": rec["summary_tr"].strip(), "local_view_note": rec.get("note"),
            "classification": {"model": "editor-chrome", "prompt": "premium-session", "countries": rec.get("countries", []),
                               "themes": rec.get("themes", []), "dossiers": rec.get("dossiers", [])},
            "status": "queued",
        })
        links.append((aid, rec.get("countries", []), rec.get("themes", []), rec.get("dossiers", [])))
    return rows, links, rejected
