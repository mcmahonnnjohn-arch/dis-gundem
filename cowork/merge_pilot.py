"""Coordinator merge for the 30-source pilot (2026-11-15).

Reads the staging outputs in data/out/cowork/, applies the red-team spot-check downgrades, and writes:
  data/source_universe/pilot_30.jsonl, provenance_edges.json, set_findings.json
  data/out/cowork/editorial.jsonl
Never touches data/kaynak_envanteri_v3.csv, Supabase, pipeline/ or secrets. Never fills signoffs.editor.
Run from repo root: python cowork/merge_pilot.py
"""
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from pilot_harness.__main__ import materialize  # noqa: E402
OUT = ROOT / "data/out/cowork"
TODAY = date(2026, 11, 15)
MANDATORY = ["identity", "canonical_url", "activity", "originality", "provenance"]
WEIGHTS = {"evidence": 25, "originality": 20, "signal_noise": 15, "coverage": 15,
           "transparency": 10, "continuity": 10, "timeliness": 5}
BATCH = {}
for i, ids in enumerate([
    "K001 K003 K004 K007 K020 K029 K031 K039 K047 K051",
    "K065 K070 K077 K080 K083 K086 K225 K105 K112 K238",
    "K123 K244 K132 K138 K153 K154 K159 K168 N001 N002"]):
    for sid in ids.split():
        BATCH[sid] = "ABC"[i]

# Red-team driven downgrades: (source, check) -> reason. PASS becomes UNKNOWN until an editor/verifier re-checks.
DOWNGRADE = {
    ("K080", "originality"): "RT-024/spot-check partial: örnek kısmen özgün",
    ("K031", "provenance"): "RT-005/spot-check no: açıklayıcı metin kaynak göstermiyor",
    ("K225", "activity"): "spot-check partial; RT-017: örnek başka kurumun brifinden türetilmiş",
    ("K244", "activity"): "RT-013/spot-check partial: fdd.org sayfaları açılamadı, tarih URL'den",
    ("K244", "originality"): "RT-013/spot-check partial",
    ("K244", "canonical_url"): "RT-013: fdd.org/about ve brief sayfası açılmadı; keşif BLOCKED dedi",
    ("K123", "activity"): "spot-check partial: yalnız ayna PDF; congress.gov robots engelli",
    ("K065", "provenance"): "RT-018/spot-check partial: paywall; içerik kısmen AFP/Axios aktarımı",
    ("K153", "canonical_url"): "RT-011: ana sayfa eski (2024) içerik; yalnız alan adı kimliği",
    ("K154", "canonical_url"): "RT-012: ana sayfa alan adı/tarih içermiyor; makale açılmadı",
    ("K105", "provenance"): "RT-005: hiçbir kalem incelenmemiş",
    ("K123", "provenance"): "RT-005: yukarı akış izlenmedi",
    ("K007", "provenance"): "RT-005: yukarı akış izlenmedi",
    ("K007", "originality"): "RT-016: özgünlük kanıtı 166 gün eski (>45)",
    ("K244", "provenance"): "RT-005: yukarı akış izlenmedi",
    ("K086", "originality"): "RT-007: tek örnek Glasnaya'dan yeniden yayım; özgün röportaj yalnız keşifte, bağımsız teyit yok",
}


OFFICIAL_ROLE_IDS = {"K003", "K047", "K070", "K083", "K105", "K132", "K159"}  # editor decision 2026-11-15


def jl(name):
    return [json.loads(x) for x in (OUT / name).read_text(encoding="utf-8").splitlines() if x.strip()]


def main():
    ver = {r["source_id"]: r for r in jl("verification.jsonl")}
    disc = {r["source_id"]: r for r in jl("discovery.jsonl")}
    round2 = {}
    if (OUT / "verification_round2.jsonl").exists():  # clean-room re-verification with real per-fetch `date -u` timestamps
        round2 = {r["source_id"]: r for r in jl("verification_round2.jsonl")}
        ver.update(round2)
    rt = jl("red_team.jsonl")
    fam = json.loads((OUT / "provenance_families.json").read_text(encoding="utf-8"))
    edges = jl("provenance.jsonl")
    pilot = [json.loads(x) for x in (ROOT / "data/source_universe/pilot_30.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
    mat = {r["id"]: r for r in materialize()}
    editorial = []
    for rec in pilot:
        sid = rec["id"]
        m = mat[sid]
        v, d = ver[sid], disc[sid]
        reviewer = "cowork-verifier-D" if sid in round2 else f"cowork-verifier-{BATCH[sid]}"
        precision = "per_fetch_date_u" if sid in round2 else "batch_write_time"
        rec["discoverer"] = f"cowork-discovery-{BATCH[sid]}"
        checks, evidence, notes = {}, [], {}
        for name, c in v["checks"].items():
            status = c["status"]
            if (sid, name) in DOWNGRADE and status == "PASS":
                notes[name] = f"PASS→UNKNOWN (kırmızı takım): {DOWNGRADE[(sid, name)]}"
                status = "UNKNOWN"
            if status == "BLOCKED":
                notes.setdefault(name, "BLOCKED (araç/robots/paywall engeli); kaynak kötü demek değildir")
                status = "UNKNOWN"
            checks[name] = status
            if status == "PASS":
                evidence.append({"check": name, "url": c["evidence_url"], "observed_at": c["observed_at"],
                                 "reviewer": reviewer, "observation": c["observation"],
                                 "observed_at_precision": precision,
                                 "limitations": c.get("limitations", "")})
            elif status == "FAIL":
                notes[name] = f"FAIL: {c['observation']}"
        rec["checks"], rec["evidence"], rec["verification_notes"] = checks, evidence, notes
        examples = [e for e in v.get("original_work_examples", []) if e.get("url", "").startswith("https://") and e.get("published_at")]
        if checks["originality"] == "PASS":
            rec["original_work_examples"] = [{"url": e["url"], "published_at": e["published_at"], "why_original": e.get("why_original", "")} for e in examples]
            rec["original_work_examples_unverified"] = []
        else:
            rec["original_work_examples"] = []
            rec["original_work_examples_unverified"] = [{"url": e["url"], "published_at": e["published_at"]} for e in examples] + \
                [{"url": e["url"], "published_at": e.get("published_at"), "source": "discovery"} for e in d.get("original_work_candidates", []) if e.get("url", "").startswith("https://")]
        f = fam[sid]["provenance_family"]
        rec["provenance_family"] = f if checks["provenance"] == "PASS" else ("UNKNOWN" + ("" if f.upper().startswith("UNKNOWN") else f" (öneri, doğrulanmadı: {f})"))
        rec["signoffs"] = {"verifier": reviewer, "red_team": "cowork-redteam-01", "editor": None}
        rec["assigned_tier"] = None
        if sid in OFFICIAL_ROLE_IDS:
            rec["monitoring_role"] = "official_position_monitor"
            rec["attribution_only"] = True
        rec["status"] = "CANDIDATE"
        rec["red_team_findings"] = [{"finding_id": r["finding_id"], "severity": r["severity"], "resolved": False,
                                     "reason": r["issue"][:400], "evidence_urls": r.get("evidence_urls", [])}
                                    for r in rt if r["source_id"] == sid]
        rec["risk_flags"] = d.get("risk_flags", []) if isinstance(d.get("risk_flags"), list) else [str(d.get("risk_flags"))]
        rec["unknowns"] = [k for k, val in checks.items() if val == "UNKNOWN"] and \
            [f"{k}: {notes.get(k, 'kanıt toplanamadı/yetersiz')}" for k, val in checks.items() if val == "UNKNOWN"] \
            or ["yok"]
        if sid == "K003":
            rec["x_handles"] = ["@Sana__gov"]
            rec["x_handle_proof"] = "https://sana.sy (keşif görevi; bağımsız teyit yok)"
        # ---- evidence-based provisional scoring (unknown = 0) ----
        n_pass = sum(checks[m] == "PASS" for m in MANDATORY)
        nex = len(rec["original_work_examples"])
        comp = {"evidence": 5 * n_pass}
        if checks["originality"] == "PASS":
            comp["originality"] = min(20, 12 + 4 * min(2, nex))
        elif checks["originality"] == "FAIL":
            comp["originality"] = 3
        else:
            comp["originality"] = 0
        comp["signal_noise"] = None  # ölçülmedi; editör 20 maddelik örneklem yapmalı
        langs = [l for l in m.get("languages", []) if l != "en"]
        comp["coverage"] = min(15, 5 + (5 if langs else 0) + (3 if m["region"] in {"Kafkasya", "Afrika", "Asya", "Karadeniz & Rusya"} else 0))
        meth = 1 if d.get("methodology_or_about_urls") else 0
        comp["transparency"] = 4 * (checks["ownership"] == "PASS") + 3 * (checks["perspective"] == "PASS") + 3 * meth
        access = str(v.get("paywall_or_access_notes", "")).lower()
        blocked = any(w in access for w in ["blocked", "paywall", "robots", "engel"])
        comp["continuity"] = (6 if checks["activity"] == "PASS" else 0) + (0 if blocked else 4)
        newest = max((e["published_at"] for e in rec["original_work_examples"]), default=None)
        days = (TODAY - date.fromisoformat(newest[:10])).days if newest else None
        comp["timeliness"] = 0 if checks["activity"] != "PASS" else (5 if days is not None and days <= 14 else 3)
        lower = sum(x for x in comp.values() if x is not None)
        known_max = sum(WEIGHTS[k] for k, x in comp.items() if x is not None)
        # ---- recommendation ----
        stype = m.get("source_type", "")
        official = stype in {"Devlet ajansı", "Resmi kurum"}
        if n_pass == 5:
            if stype == "OSINT":
                tier = "EVENT"
            elif stype in {"Think tank", "Conflict data"}:
                tier = "WEEKLY"
            else:
                tier = "RADAR"
            decision, why = tier, "5/5 zorunlu kontrol; imzalar/puan/insan editör eksik; signal_noise ölçülmedi"
        elif official:
            role_ok = all(checks[mname] == "PASS" for mname in MANDATORY if mname != "originality")
            if role_ok:
                decision, why = "RADAR", ("resmî pozisyon izleme rolü (yalnız atıflı beyan; olgu teyidi/özgün üretim sayılmaz); "
                                           "rol kontrolleri geçti; imzalar/puan/insan editör eksik")
            else:
                missing = [mname for mname in MANDATORY if mname != "originality" and checks[mname] != "PASS"]
                decision, why = "HOLD", "resmî pozisyon izleme rolü; eksik kontrol: " + ", ".join(missing)
        else:
            missing = [m for m in MANDATORY if checks[m] != "PASS"]
            decision, why = "HOLD", "eksik zorunlu kontrol: " + ", ".join(missing)
        if sid == "K039":
            why += "; mahkeme kapatma kararı 27 Ekim 2026 (RT-006)"
        rec["editorial_recommendation"] = {"decision": decision, "reason": why, "score_status": "provisional_lower_bound",
                                           "note": "öneridir; katama editöre aittir"}
        if sid == "N001":
            rec["activation_trigger"] = ("Somut bir saldırı/hasar/askerî hareket iddiasında görüntü-video jeolokasyonu veya doğrulaması "
                                         "gerektiğinde ve en az iki bağımsız ham görüntü ailesi bulunduğunda (öneri; editör onayı gerekir)")
        editorial.append({"source_id": sid, "name": m.get("canonical_name"), "checks": checks, "score_components": comp,
                          "score_lower_bound": lower, "score_known_max": known_max + (15 if comp["signal_noise"] is None else 0),
                          "decision": decision, "reason": why, "open_findings": [r["finding_id"] for r in rt if r["source_id"] == sid]})
    (ROOT / "data/source_universe/pilot_30.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in pilot), encoding="utf-8")
    keep = ["from_source_id", "to_source_id", "level", "relationship", "evidence_url", "observed_at", "claim_or_topic_scope", "claim_id", "confidence", "limitations"]
    (ROOT / "data/source_universe/provenance_edges.json").write_text(
        json.dumps([{k: e.get(k) for k in keep} for e in edges], ensure_ascii=False, indent=1), encoding="utf-8")
    (ROOT / "data/source_universe/set_findings.json").write_text(
        json.dumps([{"finding_id": r["finding_id"], "severity": r["severity"], "resolved": False, "issue": r["issue"][:500],
                     **({"partial_mitigation": "K112, K238, N001 yeniden doğrulandı (cowork-verifier-D, sayfa-bazlı date -u zaman damgası); diğer 27 kaynak için açık"}
                        if r["finding_id"] == "RT-001" else {})}
                    for r in rt if r["source_id"] == "SET"], ensure_ascii=False, indent=1), encoding="utf-8")
    (OUT / "editorial.jsonl").write_text("".join(json.dumps(e, ensure_ascii=False) + "\n" for e in editorial), encoding="utf-8")
    from collections import Counter
    print(Counter(e["decision"] for e in editorial))
    print({e["source_id"]: e["score_lower_bound"] for e in editorial})


if __name__ == "__main__":
    main()
