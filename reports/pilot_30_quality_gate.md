# Pilot 30 — Kalite kapısı (gerçek çalıştırma)

_Tarih: 2026-11-15. Pilot: feat/source-universe-pilot-30-harness. Bu rapor editoryal kabul değildir._


## `-m unittest discover -s pilot_harness/tests -v` → exit 0
```
test_attributed_official_statement_not_a_confirmed_fact (test_quality.PilotQualityTests.test_attributed_official_statement_not_a_confirmed_fact) ... ok
test_control_fully_formed_record_passes (test_quality.PilotQualityTests.test_control_fully_formed_record_passes) ... ok
test_dependent_families_via_edge_count_as_one (test_quality.PilotQualityTests.test_dependent_families_via_edge_count_as_one) ... ok
test_duplicate_canonical_url_fails (test_quality.PilotQualityTests.test_duplicate_canonical_url_fails) ... ok
test_duplicate_id_fails (test_quality.PilotQualityTests.test_duplicate_id_fails) ... ok
test_evidence_without_observation_rejected (test_quality.PilotQualityTests.test_evidence_without_observation_rejected) ... ok
test_model_cannot_sign_as_editor (test_quality.PilotQualityTests.test_model_cannot_sign_as_editor) ... ok
test_open_set_wide_high_finding_blocks_readiness (test_quality.PilotQualityTests.test_open_set_wide_high_finding_blocks_readiness) ... ok
test_pilot_structural_gate (test_quality.PilotQualityTests.test_pilot_structural_gate) ... ok
test_placeholder_domain_evidence_rejected (test_quality.PilotQualityTests.test_placeholder_domain_evidence_rejected) ... ok
test_same_host_different_path_fails (test_quality.PilotQualityTests.test_same_host_different_path_fails) ... ok
test_same_provenance_is_not_two_confirmations (test_quality.PilotQualityTests.test_same_provenance_is_not_two_confirmations) ... ok
test_score_and_signoff_cannot_be_skipped (test_quality.PilotQualityTests.test_score_and_signoff_cannot_be_skipped) ... ok
test_seed_does_not_pass_editorial_readiness (test_quality.PilotQualityTests.test_seed_does_not_pass_editorial_readiness) ... ok
test_shared_external_origin_merges_families (test_quality.PilotQualityTests.test_shared_external_origin_merges_families) ... ok
test_source_level_partnership_merges_families (test_quality.PilotQualityTests.test_source_level_partnership_merges_families) ... ok
test_undated_original_work_rejected (test_quality.PilotQualityTests.test_undated_original_work_rejected) ... ok
test_unknown_is_not_pass (test_quality.PilotQualityTests.test_unknown_is_not_pass) ... ok
test_unknown_with_suffix_is_still_unknown (test_quality.PilotQualityTests.test_unknown_with_suffix_is_still_unknown) ... ok

----------------------------------------------------------------------
Ran 19 tests in 0.103s

OK
```

## `-m pilot_harness gate --mode structural` → exit 0
```
STRUCTURAL: PASS
```

## `-m pilot_harness materialize` → exit 0
```
/home/claude/dis-gundem/data/out/source_universe_pilot.jsonl
```

## `-m pilot_harness report` → exit 0
```
/home/claude/dis-gundem/data/out/pilot_quality_report.md
```

## `-m pilot_harness gate --mode readiness` → exit 2
```
READINESS: NO_GO
Accepted: 0 / 30
SET-WIDE RED-TEAM BLOCKER: RT-001: observed_at is a batch/write-time stamp, not a per-fetch time. In verification.jsonl all 7
SET-WIDE RED-TEAM BLOCKER: RT-002: State/official sources dominate the proposed RADAR tier and cannot be reconciled with the 
SET-WIDE RED-TEAM BLOCKER: RT-003: Same-evidence-family corroboration passes the gate today. provenance_edges.json in the rep
SET-WIDE RED-TEAM BLOCKER: RT-004: Gate logic can undercount dependence and accept 'unknown' provenance. (1) independent_fami
SET-WIDE RED-TEAM BLOCKER: RT-005: 'provenance PASS' is awarded without upstream tracing, inflating min_verified_provenance. 
SET-WIDE RED-TEAM BLOCKER: RT-020: English/Western/institutional over-weighting and local-language blind spots. The 30 record
```

## Kriter tablosu
| Kriter | Ölçülen | Sonuç |
|---|---|---|
| Tam 30 benzersiz kaynak | 30 | GEÇTİ |
| ≥9 bölge | 9 | GEÇTİ |
| ≥5 dil | 5 | GEÇTİ |
| ≥2 OSINT/veri | 2 | GEÇTİ |
| ≥27 kabul | 0 | GEÇMEDİ |
| 30 kimlik teyidi | 18 | GEÇMEDİ |
| ≥29 kanonik URL | 19 | GEÇMEDİ |
| ≥27 özgünlük | 8 | GEÇMEDİ |
| ≥27 provenance | 13 | GEÇMEDİ |
| Açık yüksek/kritik red-team yok | 8 | GEÇMEDİ |
| İnsan editör onayı | 0 | GEÇMEDİ |

**Kapının kapsamı:** `structural` yalnız kayıt biçimini ve kotaları denetler; gerçek URL/içerik doğrulaması yapmaz. Bu turda gerçek doğrulama web araçlarıyla ajanlarca yapıldı ve kapı bu kayıtların biçimini/tutarlılığını denetledi. Yapısal PASS editoryal teyit değildir.
**Hazırlık sonucu: NO_GO.** Kabul: 0/30.
Bu turda kod değişiklikleri (eşik gevşetilmeden): yer tutucu alan adı reddi, observation zorunluluğu, tarihli özgün örnek, `human:` editör imzası, alan adı tekilliği, iddia düzeyi bağımlılık birleştirme (EXT/ortaklık), UNKNOWN-önekli aile reddi, set genelinde açık yüksek bulgu engeli; test sayısı 8 → 19.
GitHub Actions bu oturumda çalıştırılmadı; PR'ye push sonrası sonucu izlenmeli.
