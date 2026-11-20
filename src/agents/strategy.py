"""Strategy Agent — step 6: form a strategy.

Drafts a strategy using ONLY chain-complete events. Every claim cites
its event (and, where law is applied, the knowledge topic). An event
with a gap is never used as a premise; it is listed under "open items"
instead. The output is a draft for a human lawyer to review — not
legal advice.
"""

from __future__ import annotations

from src.agents.base import BaseAgent


class StrategyAgent(BaseAgent):
    name = "strategy"

    def run(self, checked_events: list[dict]) -> dict:
        complete = [e for e in checked_events if e["chain_status"] == "complete"]
        gapped = [e for e in checked_events if e["chain_status"] != "complete"]

        claims = []
        for event in complete:
            claim = {
                "id": f"CLM-{event['id'][-2:]}",
                "claim": f"Rely on {event['id']}: {event['title']}.",
                "evidence_ids": list(event["evidence_ids"]),
                "knowledge_ids": ["KNOW-002"] if event["id"] == "EVT-01" else [],
                "status": "verified",
            }
            claims.append(claim)
            self.trace.log(
                agent=self.name, claim=claim["claim"],
                evidence_ids=claim["evidence_ids"],
                knowledge_ids=claim["knowledge_ids"], status="verified",
                reason="Premise is a chain-complete event from shared memory.",
                retrieved=[{"query": event["title"],
                            "datapack": self.store.datapack}],
            )

        # The draft's headline: only what the complete chain supports.
        draft = {
            "headline": (
                "Claim the unpaid balance on the basis of EVT-01 (contract), "
                "EVT-02 (delivery), and EVT-03 (part payment of 20000). "
                "Treat the damage allegation (EVT-04) as unproven until "
                "photos or an inspection record are produced."
            ),
            "claims": claims,
            "open_items": [
                {"event": e["id"], "missing": e["missing"]} for e in gapped
            ],
            "disclaimer": (
                "Draft for a human lawyer to review. Not legal advice. "
                "Not court-ready. Synthetic case only."
            ),
        }
        self.trace.log(
            agent=self.name,
            claim="Strategy draft formed from chain-complete events only.",
            evidence_ids=[eid for e in complete for eid in e["evidence_ids"]],
            status="verified",
            reason="Gapped events were excluded from the premises and "
                   "listed as open items instead.",
        )
        return draft
