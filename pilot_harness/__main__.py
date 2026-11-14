"""30-source source-universe pilot. Standard library only; never fetches articles or writes to Supabase."""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "data/kaynak_envanteri_v3.csv"
PILOT = ROOT / "data/source_universe/pilot_30.jsonl"
POLICY = ROOT / "data/source_universe/pilot_policy.json"
CLAIMS = ROOT / "data/source_universe/claims.json"
EDGES = ROOT / "data/source_universe/provenance_edges.json"
SET_FINDINGS = ROOT / "data/source_universe/set_findings.json"
VALID_CHECKS = {"UNKNOWN", "PASS", "FAIL", "NA"}
VALID_TIERS = {"RADAR", "WEEKLY", "EVENT"}
VALID_STATUSES = {"CANDIDATE", "VERIFIED", "REJECTED"}


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def inventory() -> dict[str, dict]:
    with INVENTORY.open(encoding="utf-8", newline="") as f:
        return {r["ID"]: r for r in csv.DictReader(f)}


def normalize_url(value: str) -> str:
    p = urlsplit(value.strip())
    host = (p.hostname or "").lower().removeprefix("www.")
    return host + p.path.rstrip("/").lower()


def is_url(value: object) -> bool:
    if not isinstance(value, str):
        return False
    p = urlsplit(value)
    if not (p.scheme == "https" and p.hostname and not p.username and not p.password):
        return False
    return not is_placeholder_host(p.hostname)


PLACEHOLDER_HOSTS = {"example.com", "example.org", "example.net", "localhost", "publisher.example"}
PLACEHOLDER_SUFFIXES = (".example", ".invalid", ".test", ".localhost", ".local")
CLAIM_DEPENDENT_RELATIONSHIPS = {
    "republishes", "derives_from", "same_wire", "same_statement", "same_dataset",
    "same_imagery", "same_anonymous_tip", "same_leak",
}


def is_placeholder_host(host: str) -> bool:
    h = host.lower().rstrip(".")
    return (h in PLACEHOLDER_HOSTS or h.endswith(PLACEHOLDER_SUFFIXES)
            or any(h.endswith("." + x) for x in PLACEHOLDER_HOSTS))


def is_date(value: object) -> bool:
    if not isinstance(value, str):
        return False
    try:
        d = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    d = d if d.tzinfo else d.replace(tzinfo=timezone.utc)
    return d <= datetime.now(timezone.utc)


def materialize() -> list[dict]:
    legacy = inventory()
    result = []
    for record in read_jsonl(PILOT):
        r = dict(record)
        if r.get("source_origin") == "legacy":
            src = legacy.get(r.get("id"))
            if src is None:
                r["_missing_inventory"] = True
            else:
                r.update({
                    "canonical_name": src["Kaynak"],
                    "canonical_url": src["URL"],
                    "region": src["Bölge"],
                    "country": src["Ülke"],
                    "languages": [v for v in re.split(r"[/,+ ]+", src["Dil"]) if v],
                    "source_type": src["Tür"],
                    "legacy_status": src["Durum"],
                    "legacy_verification": src["Doğrulama"],
                    "legacy_verified_at": src["Doğrulama tarihi (UTC)"],
                    "legacy_evidence_context": src.get("Bağlam kanıtı", ""),
                })
        result.append(r)
    return result


def check_evidence(record: dict, check: str, days: int, now: datetime | None = None) -> bool:
    now = now or datetime.now(timezone.utc)
    verifier = (record.get("signoffs") or {}).get("verifier")
    discoverer = record.get("discoverer")
    if not verifier or verifier == discoverer:
        return False
    for e in record.get("evidence", []):
        if e.get("check") != check or not is_url(e.get("url")):
            continue
        if not str(e.get("observation") or "").strip():
            continue  # ne görüldüğü yazılmamış kanıt geçersiz
        if e.get("reviewer") != verifier or e.get("reviewer") == discoverer:
            continue
        try:
            observed = datetime.fromisoformat(e["observed_at"].replace("Z", "+00:00"))
            if observed.tzinfo is None:
                continue
            age = now - observed.astimezone(timezone.utc)
            if timedelta(0) <= age <= timedelta(days=days):
                return True
        except (KeyError, ValueError, TypeError):
            pass
    return False


def source_readiness(record: dict, policy: dict, now: datetime | None = None) -> list[str]:
    issues = []
    checks = record.get("checks") or {}
    role = is_official_monitor(record, policy)
    mandatory = [c for c in policy["mandatory_checks"] if not (role and c == "originality")]
    if role:
        if record.get("attribution_only") is not True:
            issues.append("resmî kanal rolü: attribution_only=true zorunlu")
        if not str(record.get("provenance_family") or "").startswith(OFFICIAL_FAMILY_PREFIXES):
            issues.append("resmî kanal rolü: provenance_family state-statement/state-media/institution olmalı")
        if checks.get("originality") not in {"PASS", "FAIL", "NA", "UNKNOWN"}:
            issues.append("originality: geçersiz durum")
    for check in mandatory:
        if checks.get(check) != "PASS":
            issues.append(f"{check}: PASS değil")
        elif not check_evidence(record, check, policy["acceptance"]["max_evidence_age_days"], now):
            issues.append(f"{check}: güncel ve bağımsız denetçi kanıtı yok")
    for check in policy["optional_documented_checks"]:
        if checks.get(check) not in {"PASS", "UNKNOWN", "NA"}:
            issues.append(f"{check}: geçersiz durum")
        if checks.get(check) == "UNKNOWN" and not record.get("unknowns"):
            issues.append(f"{check}: UNKNOWN gerekçesi yazılmamış")
        if checks.get(check) == "PASS" and not check_evidence(
            record, check, policy["acceptance"]["max_evidence_age_days"], now
        ):
            issues.append(f"{check}: kanıt yok")
    examples = record.get("original_work_examples") or []
    if not role and (not examples or not all(is_url(x.get("url")) and is_date(x.get("published_at")) for x in examples)):
        issues.append("tarihli (published_at) özgün çalışma örneği ve URL yok")
    if is_unknown_family(record.get("provenance_family")):
        issues.append("provenance family bilinmiyor")
    score = record.get("score_breakdown")
    if not isinstance(score, dict) or set(score) != set(policy["weights"]):
        issues.append("yedi bileşenli puan eksik")
    else:
        for key, maximum in policy["weights"].items():
            value = score.get(key)
            if type(value) is not int or not (0 <= value <= maximum):
                issues.append(f"{key}: 0..{maximum} dışında")
        if not issues or not any("dışında" in x for x in issues):
            tier = record.get("assigned_tier")
            if tier in VALID_TIERS and sum(score.values()) < policy["tier_score_floors"][tier]:
                issues.append(f"{tier}: puan eşiği altında")
    signoffs = record.get("signoffs") or {}
    people = [signoffs.get(k) for k in ("verifier", "red_team", "editor")]
    if not all(people) or len(set(people)) != 3 or record.get("discoverer") in people:
        issues.append("üç ayrı imza ve keşif-denetim ayrılığı yok")
    if not str(signoffs.get("editor") or "").startswith("human:"):
        issues.append("editör imzası insan değil (human:<ad> biçimi gerekli)")
    if record.get("assigned_tier") not in VALID_TIERS:
        issues.append("editörce atanmış tekil katman yok")
    if record.get("status") != "VERIFIED":
        issues.append("durum VERIFIED değil")
    if record.get("assigned_tier") == "EVENT" and not record.get("activation_trigger"):
        issues.append("EVENT için tetikleyici yok")
    for finding in record.get("red_team_findings") or []:
        if finding.get("severity") in {"high", "critical"} and not finding.get("resolved", False):
            issues.append("açık yüksek/kritik red-team bulgusu")
    return issues


def structural_issues(records: list[dict], policy: dict) -> list[str]:
    issues = []
    if len(records) != policy["pilot_size"]:
        issues.append(f"pilot boyutu {len(records)}, hedef {policy['pilot_size']}")
    ids = [r.get("id") for r in records]
    if len(set(ids)) != len(ids):
        issues.append("tekrarlanan kaynak ID")
    urls = [normalize_url(r.get("canonical_url") or "") for r in records]
    if any(not is_url(r.get("canonical_url")) for r in records):
        issues.append("eksik/geçersiz HTTPS kanonik URL")
    if len(set(urls)) != len(urls):
        issues.append("tekrarlanan kanonik URL")
    hosts = [(urlsplit(r.get("canonical_url") or "").hostname or "").lower().removeprefix("www.") for r in records]
    if len(set(hosts)) != len(hosts):
        issues.append("tekrarlanan kanonik alan adı (aynı kuruluş iki kez sayılmış olabilir)")
    if any(r.get("_missing_inventory") for r in records):
        issues.append("legacy ID envanterde yok")
    if any(r.get("source_origin") not in {"legacy", "new"} for r in records):
        issues.append("geçersiz source_origin")
    if any(r.get("proposed_tier") not in VALID_TIERS for r in records):
        issues.append("geçersiz önerilen katman")
    if any(r.get("assigned_tier") not in VALID_TIERS | {None} for r in records):
        issues.append("geçersiz atanmış katman")
    if any(r.get("status") not in VALID_STATUSES for r in records):
        issues.append("geçersiz durum")
    if any(set((r.get("checks") or {}).values()) - VALID_CHECKS for r in records):
        issues.append("geçersiz kontrol değeri")
    if any(not set(policy["mandatory_checks"] + policy["optional_documented_checks"]).issubset(
        (r.get("checks") or {}).keys()
    ) for r in records):
        issues.append("eksik kalite kontrol alanı")
    regions = {r.get("region") for r in records if r.get("region")}
    languages = {lang for r in records for lang in r.get("languages", [])}
    special = [r for r in records if r.get("source_type") in {"OSINT", "Conflict data"}]
    if len(regions) < policy["min_regions"]:
        issues.append(f"bölge çeşitliliği {len(regions)} < {policy['min_regions']}")
    if len(languages) < policy["min_distinct_languages"]:
        issues.append("dil çeşitliliği yetersiz")
    if len(special) < policy["min_osint_data"]:
        issues.append("OSINT/çatışma verisi pilot kapsamı yetersiz")
    return issues


SOURCE_DEPENDENT_RELATIONSHIPS = {"shared_owner", "partnership"}
OFFICIAL_ROLE = "official_position_monitor"
OFFICIAL_FAMILY_PREFIXES = ("state-statement", "state-media", "institution")


def is_official_monitor(record: dict, policy: dict) -> bool:
    """State/official channels tracked ONLY for attributed official positions (editor decision 2026-11-15).

    The role never counts as original reporting and never as independent factual corroboration.
    """
    return bool((policy.get("official_monitor") or {}).get("enabled")) and record.get("monitoring_role") == OFFICIAL_ROLE


def originality_required(policy: dict, n_exempt: int) -> int:
    """Default keeps the threshold unchanged; lowering it needs an explicit editor-set policy switch."""
    base = policy["acceptance"]["min_verified_originality"]
    if (policy.get("official_monitor") or {}).get("adjust_originality_threshold"):
        return max(0, base - n_exempt)
    return base


def is_unknown_family(value: object) -> bool:
    """'UNKNOWN', 'UNKNOWN (… unconfirmed)', empty or non-string all count as unknown."""
    return not isinstance(value, str) or not value.strip() or value.strip().upper().startswith("UNKNOWN")


def independent_families(claim: dict, edges: list[dict], official_ids: set[str] | None = None) -> int:
    """Count independent evidence origins for one claim.

    Sources are merged when they (a) share a provenance_family string, (b) are linked by a claim-level
    dependent edge carrying this claim's id (this also merges through shared EXT: nodes such as one
    wire agency), or (c) are linked by a source-level shared_owner/partnership edge.
    """
    parent: dict[str, str] = {}

    def find(x: str) -> str:
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: str, b: str) -> None:
        parent[find(a)] = find(b)

    by_family: dict[str, str] = {}
    sources = []
    for e in claim.get("evidence") or []:
        sid, fam = e.get("source_id"), e.get("provenance_family")
        if is_unknown_family(fam) or not sid or sid in (official_ids or set()):
            continue
        sources.append(sid)
        find(sid)
        if fam in by_family:
            union(sid, by_family[fam])
        else:
            by_family[fam] = sid
    for edge in edges:
        rel = edge.get("relationship")
        a, b = edge.get("from_source_id"), edge.get("to_source_id")
        if not a or not b:
            continue
        if edge.get("claim_id") == claim.get("id") and rel in CLAIM_DEPENDENT_RELATIONSHIPS:
            union(a, b)
        elif edge.get("level") == "source" and rel in SOURCE_DEPENDENT_RELATIONSHIPS:
            union(a, b)
    return len({find(x) for x in sources})


def edge_endpoint_ok(value: object, known_ids: set[str]) -> bool:
    """A provenance edge endpoint is a pilot source ID or an explicit external origin 'EXT:<name>'."""
    return isinstance(value, str) and (value in known_ids or (value.startswith("EXT:") and len(value) > 4))


def claim_issues(claims: list[dict], known_ids: set[str], edges: list[dict] | None = None,
                 official_ids: set[str] | None = None) -> list[str]:
    edges = edges or []
    problems = []
    for claim in claims:
        cid = claim.get("id", "UNKNOWN")
        evidence = claim.get("evidence") or []
        if not evidence:
            problems.append(f"{cid}: kanıt yok")
            continue
        for item in evidence:
            if item.get("source_id") not in known_ids or not is_url(item.get("url")):
                problems.append(f"{cid}: geçersiz kaynak/kanıt URL")
        official = official_ids or set()
        if claim.get("kind") == "factual" and any(e.get("source_id") in official for e in evidence):
            problems.append(f"{cid}: resmî kanal rolündeki kaynak olgusal iddiada kanıt sayılamaz (yalnız attributed_statement)")
        families = {
            e.get("provenance_family") for e in evidence
            if not is_unknown_family(e.get("provenance_family"))
            and not (claim.get("kind") == "factual" and e.get("source_id") in official)
        }
        if claim.get("kind") == "factual" and len(families) >= 2 and independent_families(claim, edges, official) < 2:
            problems.append(f"{cid}: kanıt aileleri provenance edge ile birbirine bağımlı; tek köken sayıldı")
        if claim.get("kind") == "factual" and len(families) < 2:
            problems.append(f"{cid}: aynı kökenli teyit; iki bağımsız kanıt ailesi yok")
        elif claim.get("kind") == "attributed_statement":
            if not claim.get("attributed_to"):
                problems.append(f"{cid}: beyanın atfedildiği aktör yok")
            if len(families) < 1:
                problems.append(f"{cid}: atıf kanıtı yok")
        elif claim.get("kind") not in {"factual", "attributed_statement"}:
            problems.append(f"{cid}: geçersiz iddia türü")
    return problems


def set_blockers(findings: list[dict]) -> list[str]:
    """Set-wide (not per-source) red-team findings: unresolved high/critical ones block readiness."""
    return [f"{f.get('finding_id', '?')}: {str(f.get('issue', ''))[:90]}" for f in findings
            if f.get("severity") in {"high", "critical"} and not f.get("resolved", False)]


def audit() -> dict:
    policy = read_json(POLICY)
    records = materialize()
    structural = structural_issues(records, policy)
    per_source = {r["id"]: source_readiness(r, policy) for r in records}
    accepted = [r for r in records if not per_source[r["id"]]]
    counter = Counter()
    for r in records:
        for k in ("identity", "canonical_url", "originality", "provenance"):
            if r["checks"].get(k) == "PASS" and check_evidence(
                r, k, policy["acceptance"]["max_evidence_age_days"]
            ):
                counter[k] += 1
    edges = read_json(EDGES)
    official_ids = {r["id"] for r in records if is_official_monitor(r, policy)}
    claims = claim_issues(read_json(CLAIMS), {r["id"] for r in records}, edges, official_ids)
    ids = {r["id"] for r in records}
    for e in edges:
        ends = (e.get("from_source_id"), e.get("to_source_id"))
        if not all(edge_endpoint_ok(x, ids) for x in ends) or not any(x in ids for x in ends) \
                or not is_url(e.get("evidence_url")):
            structural.append("kanıtsız veya bilinmeyen provenance edge")
    blockers = set_blockers(read_json(SET_FINDINGS) if SET_FINDINGS.exists() else [])
    limits = policy["acceptance"]
    ready = (
        not structural and not claims and not blockers
        and len(accepted) >= limits["min_accepted"]
        and counter["identity"] >= limits["min_verified_identity"]
        and counter["canonical_url"] >= limits["min_verified_url"]
        and counter["originality"] >= originality_required(policy, len(official_ids))
        and counter["provenance"] >= limits["min_verified_provenance"]
        and sum(r["source_type"] in {"OSINT", "Conflict data"} for r in accepted)
            >= limits["min_accepted_osint_data"]
    )
    return {
        "pilot_count": len(records), "structural_issues": structural,
        "claim_issues": claims, "set_blockers": blockers, "per_source": per_source,
        "accepted": [r["id"] for r in accepted],
        "check_counts": dict(counter), "go_no_go": "GO" if ready else "NO_GO",
        "records": records, "official_monitor_ids": sorted(official_ids),
    }


def report(result: dict) -> str:
    lines = [
        "# Kaynak evreni: 30 kaynak pilot kalite raporu",
        "",
        f"**Karar: {result['go_no_go']}** — {len(result['accepted'])}/{result['pilot_count']} kabul.",
        "",
        "Bu rapor otomatik kanıt toplamaz. Eski envanter doğrulaması güncel, bağımsız pilot imzası yerine geçmez.",
        "",
        "## Yapısal kalite kapısı",
        "",
        "PASS" if not result["structural_issues"] else "FAIL",
        "",
    ]
    lines += ["- " + x for x in result["structural_issues"]] or ["- 30 benzersiz kayıt ve kapsama kotaları sağlandı."]
    lines += ["", "## Kanıt kalite kapısı", ""]
    for key in ("identity", "canonical_url", "originality", "provenance"):
        lines.append(f"- {key}: {result['check_counts'].get(key, 0)}/{result['pilot_count']} güncel bağımsız kanıt")
    lines += ["", "## Pilot matrisi", "",
              "| ID | Kaynak | Bölge | Öneri | Atanan | Karar | Eksik kontrol |",
              "|---|---|---|---|---|---|---|"]
    for r in result["records"]:
        issues = result["per_source"][r["id"]]
        status = "PASS" if not issues else "PENDING/FAIL"
        lines.append(
            f"| {r['id']} | {r.get('canonical_name','?')} | {r.get('region','?')} | "
            f"{r['proposed_tier']} | {r.get('assigned_tier') or '—'} | {status} | "
            f"{'; '.join(issues[:3]) or '—'} |"
        )
    lines += ["", "## Set genelinde açık yüksek/kritik red-team bulguları", ""]
    lines += ["- " + x for x in result["set_blockers"]] or ["- Yok."]
    lines += ["", "## İddia bağımsızlığı", ""]
    lines += ["- " + x for x in result["claim_issues"]] or ["- Kaydedilmiş iddia yok; bağımsız teyit performansı henüz ölçülmedi."]
    lines += [
        "", "## Ölçekleme kararı", "",
        "GO yalnız kabul eşikleri, bölge/dil çeşitliliği, özgünlük, bağımsız provenance ve üçlü imza birlikte sağlanırsa verilir.",
        "NO_GO halinde 150'ye ölçekleme ve otomatik yayın yetkisi açılmaz.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Dış Gündem 30 kaynak kalite harness")
    sub = parser.add_subparsers(dest="command", required=True)
    p_gate = sub.add_parser("gate")
    p_gate.add_argument("--mode", choices=["structural", "readiness"], default="structural")
    p_report = sub.add_parser("report")
    p_report.add_argument("--out", default="data/out/pilot_quality_report.md")
    p_materialize = sub.add_parser("materialize")
    p_materialize.add_argument("--out", default="data/out/source_universe_pilot.jsonl")
    args = parser.parse_args()
    result = audit()
    if args.command == "gate":
        if args.mode == "structural":
            for issue in result["structural_issues"]:
                print("FAIL:", issue)
            print("STRUCTURAL:", "PASS" if not result["structural_issues"] else "FAIL")
            return 1 if result["structural_issues"] else 0
        print("READINESS:", result["go_no_go"])
        print("Accepted:", len(result["accepted"]), "/", result["pilot_count"])
        for issue in result["claim_issues"]:
            print("CLAIM FAIL:", issue)
        for issue in result["set_blockers"]:
            print("SET-WIDE RED-TEAM BLOCKER:", issue)
        return 0 if result["go_no_go"] == "GO" else 2
    out = ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    if args.command == "materialize":
        out.write_text(
            "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in result["records"]),
            encoding="utf-8",
        )
    else:
        out.write_text(report(result), encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
