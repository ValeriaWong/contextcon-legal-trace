"""Decision-trace logger.

Hard rule: every claim must cite the evidence it came from, or say it
cannot be verified. A claim with empty ``evidence_ids`` and a status
other than ``cannot_verify`` / ``refused`` is rejected here — by the
logger, not by good intentions. That is the auditability guarantee.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

VALID_STATUSES = ("verified", "unsupported", "cannot_verify", "refused")


@dataclass
class TraceRecord:
    turn_id: str
    agent: str
    claim: str
    evidence_ids: list[str] = field(default_factory=list)
    knowledge_ids: list[str] = field(default_factory=list)
    status: str = "cannot_verify"
    reason: str = ""
    retrieved: list[dict] = field(default_factory=list)
    missing: list[str] = field(default_factory=list)
    tokens_in: int = 0
    tokens_out: int = 0
    timestamp: str = ""

    def validate(self) -> None:
        if self.status not in VALID_STATUSES:
            raise ValueError(f"unknown trace status {self.status!r}")
        if not self.claim.strip():
            raise ValueError("trace record has an empty claim")
        if not self.evidence_ids and self.status not in ("cannot_verify", "refused"):
            raise ValueError(
                f"uncited claim rejected ({self.agent} / {self.turn_id}): "
                f"{self.claim!r} — cite evidence_ids or mark cannot_verify/refused"
            )


class TraceLogger:
    """Append-only, in-memory trace log. Export with :meth:`to_json`."""

    def __init__(self) -> None:
        self.records: list[TraceRecord] = []
        self._n = 0

    def log(
        self,
        agent: str,
        claim: str,
        evidence_ids: list[str] | None = None,
        knowledge_ids: list[str] | None = None,
        status: str = "cannot_verify",
        reason: str = "",
        retrieved: list[dict] | None = None,
        missing: list[str] | None = None,
        tokens_in: int = 0,
        tokens_out: int = 0,
    ) -> TraceRecord:
        self._n += 1
        record = TraceRecord(
            turn_id=f"T{self._n:03d}",
            agent=agent,
            claim=claim,
            evidence_ids=list(evidence_ids or []),
            knowledge_ids=list(knowledge_ids or []),
            status=status,
            reason=reason,
            retrieved=list(retrieved or []),
            missing=list(missing or []),
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        record.validate()
        self.records.append(record)
        return record

    def missing_evidence(self) -> list[str]:
        """Distinct missing items named anywhere in the trace."""
        out: list[str] = []
        for r in self.records:
            for item in r.missing:
                if item not in out:
                    out.append(item)
        return out

    def uncited_claims(self) -> list[TraceRecord]:
        return [r for r in self.records if not r.evidence_ids]

    def to_json(self) -> str:
        return json.dumps([asdict(r) for r in self.records], ensure_ascii=False, indent=2)

    def write(self, path: str | Path) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.to_json(), encoding="utf-8")
        return path
