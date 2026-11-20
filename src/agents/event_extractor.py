"""Event Extractor — steps 3-4: organise a timeline, extract key events.

Extracts each event exactly once, from admitted evidence only, and
promotes it to shared memory. Later agents reuse the event; they do not
re-read the raw chat. In stub mode the extraction rules are explicit and
deterministic (group admitted messages by date and topic); in live mode
the same event IDs and evidence citations must be produced.
"""

from __future__ import annotations

from src.agents.base import BaseAgent

# Deterministic stub rules: (event id, title, evidence ids).
# Each rule names the admitted evidence it is built on — nothing else.
RULES = [
    ("EVT-01", "Contract formed: 200 boxes, 48000, pay in 7 days",
     "2026-03-02", ["EV-001", "EV-002"]),
    ("EVT-02", "Delivery: 200 boxes signed for",
     "2026-03-10", ["EV-003", "EV-004"]),
    ("EVT-03", "Part payment: 20000 received",
     "2026-03-15", ["EV-006", "EV-007"]),
    ("EVT-04", "Damage alleged: 'maybe 30' boxes",
     "2026-03-18", ["EV-008"]),
    ("EVT-05", "Respondent promises to 'sort it out'",
     "2026-03-20", ["EV-010", "EV-011"]),
    ("EVT-06", "Demand: balance unpaid, no damage photos received",
     "2026-03-25", ["EV-012"]),
]


class EventExtractor(BaseAgent):
    name = "event_extractor"

    def run(self, admitted: list[dict]) -> list[dict]:
        by_id = {item["id"]: item for item in admitted}
        events = []
        for event_id, title, date, evidence_ids in RULES:
            if any(eid not in by_id for eid in evidence_ids):
                self.trace.log(
                    agent=self.name,
                    claim=f"Event {event_id} cannot be extracted.",
                    evidence_ids=[], status="cannot_verify",
                    reason="A cited evidence item was not admitted.",
                    missing=[eid for eid in evidence_ids if eid not in by_id],
                )
                continue
            event = {"id": event_id, "namespace": "case_fact",
                     "title": title, "date": date,
                     "evidence_ids": list(evidence_ids)}
            events.append(event)
            self.store.save_shared(event)
            self.trace.log(
                agent=self.name,
                claim=f"Event {event_id} extracted: {title}.",
                evidence_ids=list(evidence_ids), status="verified",
                reason="extracted once from admitted evidence; "
                       "promoted to shared memory",
                retrieved=[{"query": title, "datapack": self.store.datapack}],
            )
        return events
