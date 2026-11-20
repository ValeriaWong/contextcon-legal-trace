"""Adversarial Reviewer — attacks the draft, forces refusal or downgrade.

Its job is to try to find a conclusion the evidence does not support.
In this synthetic case it attempts the classic upgrade: turning the
respondent's promise to "sort it out" (EV-011) into a written admission
of the debt. That upgrade fails — no written admission exists (EV-014
is missing by design) — so the reviewer forces a refusal and a
downgraded claim. The refusal, with its reason and its missing item,
is the centrepiece of demo scene B.
"""

from __future__ import annotations

from src.agents.base import BaseAgent


class AdversarialReviewer(BaseAgent):
    name = "adversarial"

    def run(self, draft: dict, checked_events: list[dict]) -> dict:
        # Attempt 1: upgrade EVT-05 (a promise) into an admission.
        by_id = {e["id"]: e for e in checked_events}
        evt05 = by_id.get("EVT-05", {})
        self.refuse(
            claim="The respondent admitted the debt in writing.",
            reason=(
                "No evidence item in the datapack is a written admission. "
                "The closest item, EV-011, is a promise to 'sort it out', "
                "which is not an admission of a specific debt. "
                "EVT-05 is a promise, not an admission."
            ),
            missing=["EV-014 (written admission — does not exist in this case)"],
        )
        # The downgraded claim that replaces it.
        self.trace.log(
            agent=self.name,
            claim=(
                "The respondent promised to sort it out on 2026-03-20 "
                "(EV-010, EV-011). Whether that promise amounts to an "
                "admission is a question for a human lawyer."
            ),
            evidence_ids=list(evt05.get("evidence_ids", ["EV-010", "EV-011"])),
            status="verified",
            reason="Downgraded to what the evidence actually says.",
        )
        # Attempt 2: the damage allegation. It is stated, not proved.
        self.trace.log(
            agent=self.name,
            claim="The damage allegation (EVT-04) cannot support a deduction.",
            evidence_ids=["EV-008"],
            status="cannot_verify",
            reason="Damage is alleged ('maybe 30' boxes) with no photos, "
                   "no count, and no inspection record.",
            missing=["damage photos", "damage count", "inspection record"],
        )
        return {
            "verdict": "draft stands, with one forced refusal and one downgrade",
            "refused_claims": ["The respondent admitted the debt in writing."],
            "missing_evidence": self.trace.missing_evidence(),
        }
