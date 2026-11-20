"""Shared agent base.

Every agent reads from the shared datapack and writes back to it. No
agent talks to another agent directly. Every claim an agent makes goes
through the trace logger, which enforces the cite-or-refuse rule.
"""

from __future__ import annotations

from src.meko_client import DatapackStore
from src.trace import TraceLogger


class BaseAgent:
    name: str = "base"

    def __init__(self, store: DatapackStore, trace: TraceLogger):
        self.store = store
        self.trace = trace

    def cite(self, claim: str, evidence_ids: list[str], **kwargs) -> None:
        """Log a cited claim (status 'verified' unless stated otherwise)."""
        self.trace.log(agent=self.name, claim=claim,
                       evidence_ids=evidence_ids, **kwargs)

    def refuse(self, claim: str, reason: str,
               missing: list[str] | None = None, **kwargs) -> None:
        """Log a refusal: the claim is not supported, and why not."""
        self.trace.log(agent=self.name, claim=claim, evidence_ids=[],
                       status="refused", reason=reason,
                       missing=missing or [], **kwargs)
