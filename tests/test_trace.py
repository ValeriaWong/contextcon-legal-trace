"""Tests for the decision-trace logger (stdlib unittest only)."""

import unittest

from src.trace import TraceLogger


class TestTraceLogger(unittest.TestCase):
    def setUp(self):
        self.trace = TraceLogger()

    def test_cited_claim_accepted(self):
        r = self.trace.log(agent="strategy", claim="A contract was formed.",
                           evidence_ids=["EV-001", "EV-002"], status="verified")
        self.assertEqual(r.status, "verified")
        self.assertEqual(len(self.trace.records), 1)

    def test_uncited_claim_rejected(self):
        with self.assertRaises(ValueError):
            self.trace.log(agent="strategy",
                           claim="The respondent admitted the debt.",
                           evidence_ids=[], status="verified")

    def test_cannot_verify_without_evidence_accepted(self):
        r = self.trace.log(agent="chain_checker",
                           claim="Damage cannot be verified.",
                           evidence_ids=[], status="cannot_verify",
                           missing=["damage photos"])
        self.assertEqual(r.status, "cannot_verify")

    def test_refusal_without_evidence_accepted(self):
        r = self.trace.log(agent="adversarial",
                           claim="The respondent admitted the debt in writing.",
                           evidence_ids=[], status="refused",
                           reason="No written admission exists.",
                           missing=["EV-014"])
        self.assertEqual(r.status, "refused")
        self.assertIn("EV-014", self.trace.missing_evidence())

    def test_unknown_status_rejected(self):
        with self.assertRaises(ValueError):
            self.trace.log(agent="strategy", claim="Something.",
                           evidence_ids=["EV-001"], status="probably")

    def test_empty_claim_rejected(self):
        with self.assertRaises(ValueError):
            self.trace.log(agent="strategy", claim="   ",
                           evidence_ids=["EV-001"], status="verified")


if __name__ == "__main__":
    unittest.main()
