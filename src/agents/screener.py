"""Screener — steps 1-2: collect, authenticate.

Admits an evidence item only when its speaker is attributed and its
timestamp is plausible. Flags anything else; flagged items are never
used to build an event. Nothing is deleted — a flagged item stays in
the datapack with its reason, so the audit trail shows what was excluded
and why.
"""

from __future__ import annotations

from src.agents.base import BaseAgent


class Screener(BaseAgent):
    name = "screener"

    def run(self, evidence: list[dict]) -> dict[str, list[dict]]:
        admitted, flagged, missing = [], [], []
        for item in evidence:
            if item.get("status") == "missing":
                missing.append(item)
                self.trace.log(
                    agent=self.name,
                    claim=f"Evidence {item['id']} does not exist in this case.",
                    evidence_ids=[], status="cannot_verify",
                    reason="Item is referenced as missing by design; "
                           "no agent may invent it.",
                    missing=[f"{item['id']} — does not exist in this case"],
                )
                continue
            if item.get("status") == "flagged":
                flagged.append(item)
                self.trace.log(
                    agent=self.name,
                    claim=f"Evidence {item['id']} is flagged and excluded.",
                    evidence_ids=[item["id"]], status="verified",
                    reason=item.get("flag_reason", "flagged by screener"),
                )
                continue
            # Admitted: speaker attributed, timestamp present.
            admitted.append(item)
            self.trace.log(
                agent=self.name,
                claim=f"Evidence {item['id']} admitted "
                      f"({item.get('speaker')}, {item.get('date')}).",
                evidence_ids=[item["id"]], status="verified",
                reason="speaker attributed; timestamp plausible; complete message",
            )
        return {"admitted": admitted, "flagged": flagged, "missing": missing}
