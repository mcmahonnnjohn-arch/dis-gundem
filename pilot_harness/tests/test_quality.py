"""Offline regression tests: fail-closed gates, provenance independence, score and editorial separation."""
import copy
import unittest
from datetime import datetime, timezone

from pilot_harness.__main__ import (
    audit, set_blockers, claim_issues, materialize, read_json, source_readiness, structural_issues, POLICY,
)


class PilotQualityTests(unittest.TestCase):
    def setUp(self):
        self.policy = read_json(POLICY)
        self.records = materialize()

    def test_pilot_structural_gate(self):
        self.assertEqual(len(self.records), 30)
        self.assertEqual(structural_issues(self.records, self.policy), [])

    def test_seed_does_not_pass_editorial_readiness(self):
        result = audit()
        self.assertEqual(result["go_no_go"], "NO_GO")
        self.assertEqual(len(result["accepted"]), 0)

    def test_duplicate_id_fails(self):
        rows = copy.deepcopy(self.records)
        rows[1]["id"] = rows[0]["id"]
        self.assertTrue(any("ID" in x for x in structural_issues(rows, self.policy)))

    def test_duplicate_canonical_url_fails(self):
        rows = copy.deepcopy(self.records)
        rows[1]["canonical_url"] = rows[0]["canonical_url"]
        self.assertTrue(any("kanonik URL" in x for x in structural_issues(rows, self.policy)))

    def test_same_provenance_is_not_two_confirmations(self):
        claims = [{
            "id": "claim-test", "kind": "factual", "statement": "Test claim",
            "evidence": [
                {"source_id": "K001", "provenance_family": "single-wire",
                 "url": "https://news-fixture.org/a"},
                {"source_id": "K004", "provenance_family": "single-wire",
                 "url": "https://news-fixture.org/b"},
            ],
        }]
        self.assertTrue(any("iki bağımsız" in x for x in claim_issues(
            claims, {r["id"] for r in self.records}
        )))
        claims[0]["evidence"][1]["provenance_family"] = "independent-field-report"
        self.assertEqual(claim_issues(claims, {r["id"] for r in self.records}), [])

    def test_attributed_official_statement_not_a_confirmed_fact(self):
        claim = [{
            "id": "statement", "kind": "attributed_statement", "attributed_to": "Ministry",
            "evidence": [{"source_id": "K003", "provenance_family": "ministry",
                          "url": "https://news-fixture.org/statement"}],
        }]
        self.assertEqual(claim_issues(claim, {r["id"] for r in self.records}), [])
        claim[0]["kind"] = "factual"
        self.assertTrue(claim_issues(claim, {r["id"] for r in self.records}))

    def test_score_and_signoff_cannot_be_skipped(self):
        r = copy.deepcopy(self.records[0])
        r["checks"] = {key: "PASS" for key in r["checks"]}
        r["assigned_tier"] = "RADAR"
        r["status"] = "VERIFIED"
        r["score_breakdown"] = dict(self.policy["weights"])
        r["provenance_family"] = "original-K001"
        r["original_work_examples"] = [{"url": "https://news-fixture.org/report"}]
        self.assertTrue(source_readiness(r, self.policy))

    def test_unknown_is_not_pass(self):
        r = copy.deepcopy(self.records[0])
        r["checks"] = {k: "UNKNOWN" for k in r["checks"]}
        r["evidence"] = []
        self.assertTrue(source_readiness(r, self.policy))
        self.assertEqual(r["checks"]["identity"], "UNKNOWN")

    # ---- Cowork baseline audit (2026-11-15): regression tests for gate bypasses found ----
    def _fully_faked(self):
        now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        r = copy.deepcopy(self.records[0])
        r["checks"] = {k: "PASS" for k in r["checks"]}
        r["discoverer"] = "scout"
        r["signoffs"] = {"verifier": "v1", "red_team": "r1", "editor": "human:editor-1"}
        r["evidence"] = [{"check": k, "url": "https://real-looking.org/p", "observed_at": now,
                          "reviewer": "v1", "observation": "görüldü"} for k in r["checks"]]
        r["original_work_examples"] = [{"url": "https://real-looking.org/a", "published_at": "2026-11-01"}]
        r["provenance_family"] = "fam"
        r["status"] = "VERIFIED"
        r["assigned_tier"] = "WEEKLY"
        r["score_breakdown"] = dict(self.policy["weights"])
        return r

    def test_control_fully_formed_record_passes(self):
        self.assertEqual(source_readiness(self._fully_faked(), self.policy), [])

    def test_placeholder_domain_evidence_rejected(self):
        r = self._fully_faked()
        for e in r["evidence"]:
            e["url"] = "https://example.org/x"
        self.assertTrue(source_readiness(r, self.policy))

    def test_evidence_without_observation_rejected(self):
        r = self._fully_faked()
        for e in r["evidence"]:
            e["observation"] = ""
        self.assertTrue(source_readiness(r, self.policy))

    def test_undated_original_work_rejected(self):
        r = self._fully_faked()
        r["original_work_examples"] = [{"url": "https://real-looking.org/a"}]
        self.assertTrue(any("tarihli" in x for x in source_readiness(r, self.policy)))

    def test_model_cannot_sign_as_editor(self):
        r = self._fully_faked()
        r["signoffs"]["editor"] = "claude"
        self.assertTrue(any("insan" in x for x in source_readiness(r, self.policy)))

    def test_same_host_different_path_fails(self):
        rows = copy.deepcopy(self.records)
        rows[1]["canonical_url"] = rows[0]["canonical_url"].rstrip("/") + "/en"
        self.assertTrue(any("alan adı" in x for x in structural_issues(rows, self.policy)))

    def test_dependent_families_via_edge_count_as_one(self):
        claims = [{"id": "c1", "kind": "factual", "evidence": [
            {"source_id": "K083", "provenance_family": "tass", "url": "https://a.real.org/1"},
            {"source_id": "K132", "provenance_family": "reprint", "url": "https://b.real.org/2"}]}]
        ids = {r["id"] for r in self.records}
        self.assertEqual(claim_issues(claims, ids), [])
        edges = [{"from_source_id": "K132", "to_source_id": "K083", "relationship": "republishes",
                  "claim_id": "c1", "evidence_url": "https://b.real.org/2"}]
        self.assertTrue(any("bağımlı" in x for x in claim_issues(claims, ids, edges)))


    def test_unknown_with_suffix_is_still_unknown(self):
        r = self._fully_faked()
        r["provenance_family"] = "UNKNOWN (own-field-reporting:K001 unconfirmed)"
        self.assertTrue(any("provenance family" in x for x in source_readiness(r, self.policy)))
        claims = [{"id": "c9", "kind": "factual", "evidence": [
            {"source_id": "K001", "provenance_family": "UNKNOWN (x)", "url": "https://a.real.org/1"},
            {"source_id": "K004", "provenance_family": "UNKNOWN", "url": "https://b.real.org/2"}]}]
        self.assertTrue(claim_issues(claims, {r["id"] for r in self.records}))

    def test_shared_external_origin_merges_families(self):
        ids = {r["id"] for r in self.records}
        claims = [{"id": "c2", "kind": "factual", "evidence": [
            {"source_id": "K029", "provenance_family": "a", "url": "https://a.real.org/1"},
            {"source_id": "K083", "provenance_family": "b", "url": "https://b.real.org/2"}]}]
        self.assertEqual(claim_issues(claims, ids), [])
        edges = [
            {"from_source_id": "K029", "to_source_id": "EXT:Reuters", "relationship": "derives_from", "claim_id": "c2"},
            {"from_source_id": "K083", "to_source_id": "EXT:Reuters", "relationship": "derives_from", "claim_id": "c2"}]
        self.assertTrue(any("bağımlı" in x for x in claim_issues(claims, ids, edges)))

    def test_source_level_partnership_merges_families(self):
        ids = {r["id"] for r in self.records}
        claims = [{"id": "c3", "kind": "factual", "evidence": [
            {"source_id": "K083", "provenance_family": "a", "url": "https://a.real.org/1"},
            {"source_id": "K132", "provenance_family": "b", "url": "https://b.real.org/2"}]}]
        edges = [{"from_source_id": "K083", "to_source_id": "K132", "level": "source", "relationship": "partnership"}]
        self.assertTrue(any("bağımlı" in x for x in claim_issues(claims, ids, edges)))


    def test_open_set_wide_high_finding_blocks_readiness(self):
        self.assertTrue(set_blockers([{"finding_id": "X", "severity": "high", "resolved": False, "issue": "i"}]))
        self.assertEqual(set_blockers([{"finding_id": "X", "severity": "high", "resolved": True}]), [])
        self.assertEqual(set_blockers([{"finding_id": "X", "severity": "medium", "resolved": False}]), [])


if __name__ == "__main__":
    unittest.main()
