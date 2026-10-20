"""Aynı olayın haberlerini tek kartta toplama (editör kararı, 21 Ekim 2026).

İki adım:
  1. `birlestir` (fetch/chrome-import'tan sonra, classify'dan önce): son pencerede kuyruk ve havuzdaki kümelerin
     başlıkları tek LLM çağrısıyla olaylara gruplanır; aynı olaydaki kümeler tek kümede birleşir (diller arası).
     Birleşen kümeler silinmez: status='rejected', merged_into=<hedef>. Hedefin önemi grubun en yükseği olur;
     kuyruktaki bir küme varsa hedef kuyrukta kalır.
  2. `olay_ozeti` (classify'dan sonra): birden çok haberli kümeye, üye özetlerinden olay başlığı ve özeti yazılır;
     kaynaklar olayı belirgin biçimde farklı çerçeveliyorsa `bakis_farki` satırı (kim, nasıl) eklenir.
     Hiçbir üyesinin makale metni okunamamış kuyruk kümesi havuza düşer (editör kararı: metne erişilemiyorsa
     kuyruktan çıkar); kümede tek bir okunabilir haber yeterlidir.
"""
from __future__ import annotations

import json
import logging

from .classify import Classifier, _parse, fit_summary
from .config import PROMPTS

log = logging.getLogger(__name__)

GROUP_VERSION = "olay_grupla_v2"   # v2: doğrudan tepkiler aynı kartta, analizler ayrı (21 Ekim editör kararı)
SUMMARY_VERSION = "olay_ozet_v1"
STATUS_RANK = {"queued": 3, "pool": 2, "classified": 1, "fetched": 0}


def group_items(clf: Classifier, items: list[dict]) -> list[list[str]]:
    """items: [{"k": küme_id, "t": [başlıklar], "u": ülke, "z": tarih}] → aynı olaydaki küme id grupları (≥2)."""
    if len(items) < 2 or clf.provider == "none":
        return []
    system = (PROMPTS / f"{GROUP_VERSION}.md").read_text(encoding="utf-8")
    idx = {str(n): it["k"] for n, it in enumerate(items)}
    lines = [{"i": n, "basliklar": it["t"][:4], "ulke": it.get("u"), "tarih": it.get("z")} for n, it in enumerate(items)]
    try:
        raw = _parse(clf._call(system, json.dumps(lines, ensure_ascii=False), model=clf.summary_model))
    except Exception as e:
        log.warning("olay gruplama hatası: %s", e)
        return []
    out, used = [], set()
    for g in raw.get("gruplar") or []:
        ids = [idx[str(i)] for i in g if str(i) in idx and idx[str(i)] not in used]
        if len(ids) >= 2:
            used.update(ids)
            out.append(ids)
    return out


def pick_target(clusters: list[dict]) -> dict:
    """Birleşmede kalacak küme: kuyrukta olan > Chrome kökenli (tam metinden elle özetli) > önem > en eski."""
    return max(clusters, key=lambda c: (STATUS_RANK.get(c.get("status"), 0), c.get("origin") == "chrome",
                                        c.get("importance") or 0, -(_ts(c.get("first_seen")))))


def _ts(v) -> float:
    from datetime import datetime
    if not v:
        return 0.0
    try:
        return datetime.fromisoformat(str(v).replace("Z", "+00:00")).timestamp()
    except ValueError:
        return 0.0


def summarize_event(clf: Classifier, members: list[dict]) -> dict | None:
    """members: [{"kaynak", "ulke", "dil", "baslik", "ozet", "bakis"}] → {"baslik", "ozet", "bakis_farki"}."""
    if clf.provider == "none":
        return None
    system = (PROMPTS / f"{SUMMARY_VERSION}.md").read_text(encoding="utf-8")
    try:
        from . import glossary
        system = system.replace("{SOZLUK}", glossary.block() or "(boş)")
        raw = _parse(clf._call(system, json.dumps(members, ensure_ascii=False), model=clf.summary_model, cache=True))
    except Exception as e:
        log.warning("olay özeti hatası: %s", e)
        return None
    fark = raw.get("bakis_farki")
    return {"baslik": (raw.get("baslik") or "").strip()[:160] or None,
            "ozet": fit_summary(raw.get("ozet")),
            "bakis_farki": fark.strip()[:400] if isinstance(fark, str) and fark.strip() else None}
