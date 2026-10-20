"""Claude in Chrome oturumu kaynakları: premium (FT, Bloomberg, WSJ, Economist, FA, FP) + RSS'i sunucuya kapalı (403)
kaynaklar. Liste `data/chrome_kaynaklari.csv`.

Premium sunucu tarafında hiç toplanmaz; engelli-RSS kaynakları sunucuda gnews yedeğiyle de izlenir, Chrome oturumu
doğrudan yayıncı sayfasından tamamlar (aynı başlık tekilleştirmede elenir). Editör, Claude in Chrome oturumunda
(kendi tarayıcısı ve abonelikleriyle) günlük/haftalık tarama yapar;
oturumun çıktısı bu modülün beklediği JSON biçiminde `data/premium/YYYY-MM-DD.json` olarak kaydedilir ve
`disgundem premium-import <dosya>` ile kuyruğa girer.

Telif kuralları (docs/HEDEF.md) burada zorlanır:
- makale metni ve uzun alıntı kabul edilmez (summary_tr ≤ 600 karakter, tırnak içi parça ≤ 15 kelime)
- yalnız başlık, tarih, link, kendi cümlelerimizle özet ve etiketler saklanır
"""
from __future__ import annotations

import csv
import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path

from dateutil import parser as dtparse

from .rss import canonical

from ..config import DATA
from ..sources import FRAMES, KNOWN_DOSSIERS, KNOWN_THEMES, clean_countries, clean_ids

CHROME_CSV = DATA / "chrome_kaynaklari.csv"


def chrome_sources(path: Path = CHROME_CSV) -> dict[str, dict]:
    with open(path, encoding="utf-8", newline="") as f:
        return {r["ID"]: r for r in csv.DictReader(f)}


CHROME = chrome_sources()
CHROME_IDS = set(CHROME)
PREMIUM_IDS = {i for i, r in CHROME.items() if r["Katman"] == "premium"}
MAX_SUMMARY = 600
MAX_QUOTE_WORDS = 15
QUOTE = re.compile(r'["“”«»]([^"“”«»]{20,})["“”«»]')


def _check(rec: dict) -> str | None:
    if rec.get("source_id") not in CHROME_IDS:
        return f"source_id Chrome listesinde değil: {rec.get('source_id')}"
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
    imp = rec.get("importance")
    if not isinstance(imp, int) or not 1 <= imp <= 5:
        return "importance 1-5 arası tam sayı olmalı (docs/KAPSAM_MODELI.md tablosu)"
    return None


def route(rows: list[dict], gates, per_today: dict[str, int] | None = None, total_today: int = 0):
    """Sunucudaki huninin aynısı: önem < store_min saklanmaz, 3 havuza, ≥ queue_min kuyruğa (ülke/gün tavanı; 5 deler);
    economic_analysis=true kayıtlar econ_queue_min (varsayılan 3) ile kuyruğa girer.
    Her Chrome kaydı kendi kümesidir. Dönen: (yönlendirilmiş satırlar, eşik altı satırlar)."""
    from ..funnel import select_for_queue
    kept = [r for r in rows if r["importance"] >= gates.store_min]
    below = [r for r in rows if r["importance"] < gates.store_min]
    groups = [[{"imp": r["importance"], "eko": r["classification"].get("eko", False),
                "c": r["classification"]["countries"] or ["tr"], "row": r}] for r in kept]
    queue, pool = select_for_queue(groups, gates.for_chrome(), per_today, total_today)
    for grp, status in [(g, "queued") for g in queue] + [(g, "pool") for g in pool]:
        grp[0]["row"]["status"] = status
    return kept, below


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
            "lang": rec.get("lang") or (CHROME[rec["source_id"]]["Dil"].split("/")[0] or "en"), "published_at": pub, "fetched_at": datetime.now(timezone.utc), "excerpt": None,
            "is_turkey_related": bool(rec.get("turkey_related", True)),
            "importance": rec.get("importance"), "frame": rec.get("frame") if rec.get("frame") in FRAMES else None,
            "summary_tr": rec["summary_tr"].strip(), "local_view_note": rec.get("note"),
            "classification": {"model": "editor-chrome", "prompt": f"chrome-session:{CHROME[rec['source_id']]['Katman']}",
                               "countries": clean_countries(rec.get("countries"), "tr"),
                               "themes": rec.get("themes", []), "dossiers": rec.get("dossiers", []),
                               "eko": bool(rec.get("economic_analysis"))},
            "status": "queued",
        })
        links.append((aid, clean_countries(rec.get("countries"), "tr"), clean_ids(rec.get("themes"), KNOWN_THEMES),
                      clean_ids(rec.get("dossiers"), KNOWN_DOSSIERS)))
    return rows, links, rejected
