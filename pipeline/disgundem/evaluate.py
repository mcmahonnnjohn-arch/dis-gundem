"""Özet test seti ölçümü (`disgundem eval`).

Test seti: data/test_seti/ozet_test_seti.jsonl — editör onaylı referans özetler, kaynak olguları ve kontrol
maddeleri. Makale metni sette YOKTUR; ölçüm sırasında kaynaktan okunur ve saklanmaz (kılavuz §7).

Her haber için güncel hat (classify + denetim) çalışır, sonra üç katmanda puanlanır:
  1. kurallar  — olmali/olmamali eşleşmeleri, ≤3 cümle, ≤600 kr, süreç cümlesi
  2. hakem     — ayrı LLM çağrısı: kaynak olgularına göre doğruluk (desteksiz/yanlış iddia), kapsam, atıf
  3. özet      — set genelinde oranlar; dil kırılımı
Sonuç `eval_runs` tablosuna (ve DB yoksa out/ altına) yazılır; prompt/model değişiklikleri buna göre kıyaslanır.
"""
from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace

from .classify import AUDIT_VERSION, MAX_SENTENCES, MAX_SUMMARY, PROMPT_VERSION, Classifier, _parse
from .config import PROMPTS, ROOT
from .fetch import Item
from .fetch.article import fetch_text

log = logging.getLogger(__name__)

SET_PATH = ROOT / "data" / "test_seti" / "ozet_test_seti.jsonl"
JUDGE_VERSION = "hakem_v2"   # v2: hakem makale metnini de görür (v1 yalnız kısa olgularla metindeki doğru bilgiyi cezalandırıyordu)
PROCESS = re.compile(r"başlığa göre|başlıktan anlaşıl|lead|ayrıntı verilmiyor|belirtilmiyor|doğrulanam|"
                     r"dikkatle okunmalı|kaynağın aktardığına göre|tam metin", re.I)
SENT_SPLIT = re.compile(r"(?<=[.!?…])\s+(?=[A-ZÇĞİÖŞÜ0-9\"'«“(])")


def tr_lower(s: str) -> str:
    return (s or "").replace("I", "ı").replace("İ", "i").lower()


def _hit(pattern: str, text: str) -> bool:
    t = tr_lower(text)
    return any(tr_lower(alt.strip()) in t for alt in pattern.split("|") if alt.strip())


def load_set(path: Path = SET_PATH, only_approved: bool = False) -> list[dict]:
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    return [r for r in rows if r.get("onay")] if only_approved else rows


def rule_scores(case: dict, summary: str | None) -> dict:
    s = summary or ""
    olmali = case.get("olmali") or []
    olmamali = case.get("olmamali") or []
    eksik = [p for p in olmali if not _hit(p, s)]
    ihlal = [p for p in olmamali if _hit(p, s)]
    sents = [x for x in SENT_SPLIT.split(s.strip()) if x]
    return {
        "olmali_oran": round(1 - len(eksik) / len(olmali), 3) if olmali else 1.0,
        "eksik": eksik, "ihlal": ihlal,
        "cumle": len(sents), "uzunluk": len(s),
        "bicim_ok": bool(s) and len(s) <= MAX_SUMMARY and len(sents) <= MAX_SENTENCES,
        "surec": bool(PROCESS.search(s)),
    }


def judge(clf: Classifier, case: dict, summary: str, text: str | None = None) -> dict:
    system = (PROMPTS / f"{JUDGE_VERSION}.md").read_text(encoding="utf-8")
    src = _sources().get(case.get("source_id"))
    user = json.dumps({"baslik": case["baslik"], "kaynak": getattr(src, "name", case.get("source_id", "")),
                       "metin": text or "", "kaynak_olgulari": case.get("kaynak_olgulari") or [],
                       "referans_ozet": case["referans_ozet"], "aday_ozet": summary}, ensure_ascii=False)
    prev_rol = getattr(clf, "rol", "hat")
    clf.rol = "hakem"   # hakem çağrılarının maliyeti aday modelin (hat) maliyetinden ayrı sayılır
    try:
        # Hakem, aday modelden bağımsız sabit tutulur (JUDGE_MODEL); yoksa özet modeline düşer (eski davranış).
        raw = _parse(clf._call(system, user, model=getattr(clf, "judge_model", clf.summary_model), cache=True))
    except Exception as e:
        return {"hata": str(e)[:200]}
    finally:
        clf.rol = prev_rol
    def _score(k):
        v = raw.get(k)
        return int(v) if isinstance(v, (int, float)) and 1 <= v <= 5 else None
    return {"dogruluk": _score("dogruluk"), "kapsam": _score("kapsam"), "atif": _score("atif"),
            "hatalar": [h for h in raw.get("hatalar") or [] if isinstance(h, str)][:6]}


@dataclass
class CaseResult:
    no: int
    lang: str
    metin: str
    ozet: str | None
    uyarilar: list
    kurallar: dict
    hakem: dict | None

    def as_dict(self) -> dict:
        return self.__dict__


_SRC: dict | None = None


def _sources() -> dict:
    """Kaynak envanteri (ad, ülke, kapsam, eğilim) — sınıflandırma promptu hattakiyle aynı bağlamı alsın."""
    global _SRC
    if _SRC is None:
        from .sources import load_sources
        _SRC = {x.id: x for x in load_sources()}
    return _SRC


def run_case(clf: Classifier, client, s, case: dict, use_judge: bool = True) -> CaseResult:
    item = Item(source_id=case.get("source_id", ""), url=case["url"], title=case["baslik"],
                lang=case.get("lang"), excerpt=case.get("lead") or None)
    src = _sources().get(case.get("source_id")) or SimpleNamespace(
        name=case.get("source_id", ""), country_id="", tier="A", langs=[case.get("lang") or ""], lean_note="")
    text, st = fetch_text(client, case["url"], s.user_agent, case["baslik"]) if (client and case.get("url", "").startswith("http")) \
        else (None, "yok")
    c = clf.classify(item, src, text=text, audit=s.audit)
    summary = c.summary_tr
    verdict = judge(clf, case, summary, text) if (use_judge and summary) else None
    del text   # metin yalnız bu iki çağrıda kullanıldı; sonuca girmez
    return CaseResult(no=case["no"], lang=case.get("lang", ""), metin=st, ozet=summary, uyarilar=c.warnings,
                      kurallar=rule_scores(case, summary), hakem=verdict)


def aggregate(results: list[CaseResult]) -> dict:
    n = len(results) or 1
    def avg(vals):
        vals = [v for v in vals if v is not None]
        return round(sum(vals) / len(vals), 3) if vals else None
    by_lang: dict[str, list[CaseResult]] = {}
    for r in results:
        by_lang.setdefault(r.lang, []).append(r)
    def block(rs):
        return {
            "n": len(rs),
            "olmali_oran": avg([r.kurallar["olmali_oran"] for r in rs]),
            "ihlal_orani": round(sum(bool(r.kurallar["ihlal"]) for r in rs) / (len(rs) or 1), 3),
            "bicim_ok": round(sum(r.kurallar["bicim_ok"] for r in rs) / (len(rs) or 1), 3),
            "surec_orani": round(sum(r.kurallar["surec"] for r in rs) / (len(rs) or 1), 3),
            "dogruluk": avg([(r.hakem or {}).get("dogruluk") for r in rs]),
            "kapsam": avg([(r.hakem or {}).get("kapsam") for r in rs]),
            "atif": avg([(r.hakem or {}).get("atif") for r in rs]),
            "metin_ok": round(sum(r.metin == "ok" for r in rs) / (len(rs) or 1), 3),
            "denetim_orani": round(sum("denetim" in r.uyarilar for r in rs) / (len(rs) or 1), 3),
        }
    out = block(results)
    out["dil"] = {k: block(v) for k, v in sorted(by_lang.items())}
    out["n"] = n if results else 0
    return out


def usage_summary(clf, n_cases: int) -> dict | None:
    """Çalışmanın token ve maliyet özeti. `hat_usd` aday modellerin (eleme/özet/denetim/olay) toplamıdır ve
    haber başına maliyet buradan bölünür; hakem ayrı sayılır. Fiyatı bilinmeyen model varsa o toplam None olur."""
    rep_fn = getattr(clf, "usage_report", None)
    rep = rep_fn() if callable(rep_fn) else None
    if not rep:
        return None

    def total(rol: str) -> float | None:
        costs = [u["maliyet"] for u in (rep.get(rol) or {}).values()]
        return None if not costs or any(c is None for c in costs) else round(sum(costs), 6)

    hat = total("hat")
    return {"hat_usd": hat, "hakem_usd": total("hakem"),
            "hat_usd_haber": round(hat / n_cases, 6) if hat is not None and n_cases else None,
            "tahmini": any(u.get("tahmini") for b in rep.values() for u in b.values()), "ayrinti": rep}


def usage_md(k: dict) -> list[str]:
    def usd(v):
        return "?" if v is None else f"${v:.4f}"
    lines = ["", "## Kullanım ve maliyet", "",
             f"hat {usd(k['hat_usd'])} (haber başına {usd(k['hat_usd_haber'])}) · hakem {usd(k['hakem_usd'])}"
             + (" · maliyet fiyat tablosundan **tahmini** (OpenRouter dışı)" if k["tahmini"] else ""), "",
             "| rol | model | çağrı | girdi | önbellek | çıktı | maliyet |", "|---|---|---|---|---|---|---|"]
    for rol, models in k["ayrinti"].items():
        for model, u in models.items():
            lines.append(f"| {rol} | {model} | {u['cagri']} | {u['girdi']} | {u['onbellek']} | {u['cikti']} | {usd(u['maliyet'])} |")
    return lines


def report_md(meta: dict, agg: dict, results: list[CaseResult]) -> str:
    lines = [f"# Özet test seti — {meta['prompt']} / {meta['denetim']} / {meta['model']}", "",
             f"n={agg['n']} · olmalı {agg['olmali_oran']} · ihlal {agg['ihlal_orani']} · biçim {agg['bicim_ok']} · "
             f"süreç {agg['surec_orani']} · doğruluk {agg['dogruluk']} · kapsam {agg['kapsam']} · atıf {agg['atif']}",
             "", "| dil | n | olmalı | ihlal | doğruluk | kapsam | atıf | metin |", "|---|---|---|---|---|---|---|---|"]
    for k, b in agg["dil"].items():
        lines.append(f"| {k} | {b['n']} | {b['olmali_oran']} | {b['ihlal_orani']} | {b['dogruluk']} | "
                     f"{b['kapsam']} | {b['atif']} | {b['metin_ok']} |")
    lines += ["", "## Sorunlu örnekler", ""]
    for r in results:
        h = r.hakem or {}
        if r.kurallar["ihlal"] or r.kurallar["eksik"] or (h.get("dogruluk") or 5) <= 3:
            lines.append(f"- **{r.no}** ({r.lang}) eksik={r.kurallar['eksik']} ihlal={r.kurallar['ihlal']} "
                         f"doğruluk={h.get('dogruluk')} · {'; '.join(h.get('hatalar') or [])}")
    if agg.get("kullanim"):
        lines += usage_md(agg["kullanim"])
    return "\n".join(lines)


def olay_testi(clf: Classifier, cases: list[dict]) -> dict:
    """Birleştirme ölçümü: başlıklar olay gruplayıcıya verilir, sonuç editörün `olay` gruplarıyla çift bazında
    karşılaştırılır. `olay_belirsiz` işaretli haberler (aynı olay mı tartışmalı) puanlamaya girmez."""
    from itertools import combinations
    from .olay import group_items
    items = [{"k": str(c["no"]), "t": [c["baslik"][:200]], "u": "", "z": ""} for c in cases]
    pred = group_items(clf, items)
    same_pred = {frozenset(p) for g in pred for p in combinations(g, 2)}
    gold: dict[str, list[str]] = {}
    for c in cases:
        if c.get("olay"):
            gold.setdefault(c["olay"], []).append(str(c["no"]))
    same_gold = {frozenset(p) for g in gold.values() for p in combinations(g, 2)}
    skip = {str(c["no"]) for c in cases if c.get("olay_belirsiz")}
    sp = {p for p in same_pred if not (p & skip)}
    sg = {p for p in same_gold if not (p & skip)}
    hit = sp & sg
    return {"kesinlik": round(len(hit) / len(sp), 3) if sp else None,
            "duyarlilik": round(len(hit) / len(sg), 3) if sg else None,
            "tahmin": [sorted(g, key=int) for g in pred],
            "yanlis_birlesen": [sorted(p, key=int) for p in sp - sg],
            "kacan": [sorted(p, key=int) for p in sg - sp]}


def meta_for(clf: Classifier, s) -> dict:
    meta = {"prompt": PROMPT_VERSION, "denetim": AUDIT_VERSION if s.audit else None, "hakem": JUDGE_VERSION,
            "model": clf.summary_model, "metin": s.article_text}
    if clf.provider == "openrouter":   # model karşılaştırmasında hangi sağlayıcı/eleme/hakem modeli kullanıldı
        meta.update({"saglayici": "openrouter", "eleme_modeli": clf.model,
                     "hakem_modeli": getattr(clf, "judge_model", clf.summary_model),
                     "yedekler": list(s.fallback_models), "zdr": s.openrouter_zdr})
    return meta
