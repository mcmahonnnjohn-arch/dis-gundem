"""Offline regression tests: fail-closed gates, provenance independence, score and editorial separation."""
import copy
import unittest
from datetime import datetime, timezone

from pilot_harness.__main__ import (
    audit, claim_issues, materialize, read_json, source_readiness, structural_issues, POLICY,
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
                 "url": "https://example.org/a"},
                {"source_id": "K004", "provenance_family": "single-wire",
                 "url": "https://example.org/b"},
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
                          "url": "https://example.org/statement"}],
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
        r["original_work_examples"] = [{"url": "https://example.org/report"}]
        self.assertTrue(source_readiness(r, self.policy))

    def test_unknown_is_not_pass(self):
        r = copy.deepcopy(self.records[0])
        self.assertTrue(source_readiness(r, self.policy))
        self.assertEqual(r["checks"]["identity"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
