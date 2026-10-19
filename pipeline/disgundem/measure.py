"""Hacim ölçümü ve budama raporu.

PR #1 elle ölçümün sürdürülemez olduğunu gösterdi (269 kaynaktan 1'i). Ölçüm hattın kendisine gömülür:
her çalıştırmada kayan 30 günlük pencere için kaynak başına fetched / turkey_related / domestic_major / published
sayılır, source_metrics'e yazılır; `report` komutu budama önerisi üretir.

Budama kuralı (2 haftalık toplama sonrası):
- Çekirdekte olup pencere içinde 0 Türkiye-ilgili VE (A kapsamı için) 0 önem>=3 iç haber üretmiş → "pasif aday"
- Çekirdekte olup fetch_runs'ta 7 günde >=5 hata ve 0 yeni kayıt → "kırık"
- Yedekte olup Google News taramasında ayda >=8 Türkiye-ilgili başlık → "çekirdek adayı"
Karar editöre aittir; rapor yalnız öneri.
"""
from __future__ import annotations

from datetime import date, timedelta

from .store import Store


def compute_window(store: Store, days: int = 30, end: date | None = None) -> list[dict]:
    end = end or date.today()
    start = end - timedelta(days=days)
    rows = store.window_counts(start, end)
    store.upsert_metrics(rows)
    return rows


def prune_report(store: Store, rows: list[dict], sources: list[dict]) -> str:
    by_id = {r["source_id"]: r for r in rows}
    lines = ["# Budama raporu", "", f"Pencere: {rows[0]['window_start']} → {rows[0]['window_end']}" if rows else "Veri yok", ""]
    passive, broken, promote = [], [], []
    for s in sources:
        m = by_id.get(s["id"], {"fetched": 0, "turkey_related": 0, "domestic_major": 0, "published": 0})
        if s["status"] == "cekirdek":
            if m["turkey_related"] == 0 and (s["tier"] != "A" or m["domestic_major"] == 0):
                passive.append((s, m))
        elif s["status"] == "yedek" and m["turkey_related"] >= 8:
            promote.append((s, m))
    lines.append(f"## Pasif adayı ({len(passive)})")
    lines.append("Çekirdekte, pencere içinde Türkiye-ilgili ve önemli iç haber üretmemiş:")
    for s, m in passive:
        lines.append(f"- {s['id']} {s['name']} ({s['country_id']}, {s['tier']}): fetched={m['fetched']}")
    lines.append("")
    lines.append(f"## Çekirdek adayı ({len(promote)})")
    for s, m in promote:
        lines.append(f"- {s['id']} {s['name']}: turkey_related={m['turkey_related']}")
    lines.append("")
    lines.append("## Kırık kaynaklar")
    lines.append("`source_health` görünümünde errors_7d >= 5 ve new_items_7d = 0 olanlar; SQL: "
                 "`select * from source_health where errors_7d >= 5 and new_items_7d = 0;`")
    return "\n".join(lines)
