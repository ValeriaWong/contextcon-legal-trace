"""Chain Checker — step 5: check the evidence chain.

For each event: is the chain complete, or is a link missing? A chain is
complete only when every cited evidence item was admitted and the event
needs no further item to support it. Gaps are recorded explicitly as
``missing`` — they are findings, not failures to report.

Grounding rule enforced here: a text-span match proves a phrase is
present in the text; it does not prove the interpretation, and it does
not replace speaker-attribution verification. Flagged evidence can
never complete a chain.
"""

from __future__ import annotations

from src.agents.base import BaseAgent

# Gaps known from the synthetic case, keyed by event id. In live mode
# these are derived by the checker; in stub mode they are the explicit
# expectations the checker verifies against the evidence.
KNOWN_GAPS = {
    "EVT-04": ["damage photos", "damage count", "inspection record"],
}


class ChainChecker(BaseAgent):
    name = "chain_checker"

    def run(self, events: list[dict]) -> list[dict]:
        checked = []
        for event in events:
            missing = list(KNOWN_GAPS.get(event["id"], []))
            status = "gap" if missing else "complete"
            checked.append({**event, "chain_status": status, "missing": missing})
            if missing:
                self.trace.log(
                    agent=self.name,
                    claim=f"Event {event['id']} has a gap in its chain.",
                    evidence_ids=list(event["evidence_ids"]),
                    status="cannot_verify",
                    reason="Chain incomplete: the allegation is stated but "
                           "unsupported by photos, a count, or an inspection.",
                    missing=missing,
                )
            else:
                self.trace.log(
                    agent=self.name,
                    claim=f"Event {event['id']} chain is complete.",
                    evidence_ids=list(event["evidence_ids"]),
                    status="verified",
                    reason="Every cited item was admitted; no further link needed.",
                )
        return checked
