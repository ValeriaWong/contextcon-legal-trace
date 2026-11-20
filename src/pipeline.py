"""Pipeline: run the five agents in order through one shared datapack.

Order follows Allen's six-step method: Screener (collect, authenticate)
→ Event Extractor (timeline, extract) → Chain Checker (check chain)
→ Strategy Agent (form strategy) → Adversarial Reviewer (attack it).

No agent talks to another directly; all communication goes through the
datapack. In stub mode the datapack is in-memory; in live mode it is the
Meko datapack named in the config.
"""

from __future__ import annotations

import json
from pathlib import Path

from src.agents.adversarial import AdversarialReviewer
from src.agents.chain_checker import ChainChecker
from src.agents.event_extractor import EventExtractor
from src.agents.screener import Screener
from src.agents.strategy import StrategyAgent
from src.config import Config
from src.meko_client import DatapackStore, LocalDatapack, MekoMCPClient
from src.trace import TraceLogger


def load_case(path: str | Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def make_store(config: Config, case: dict) -> DatapackStore:
    if config.backend == "meko":
        return MekoMCPClient(config.meko_mcp_url, config.meko_api_key,
                             config.meko_datapack)
    store = LocalDatapack(config.meko_datapack)
    for item in case.get("evidence", []):
        store.add({**item, "namespace": "case_fact"})
    for topic in case.get("knowledge_topics", []):
        store.add({**topic, "namespace": "legal_knowledge"})
    return store


def run_pipeline(case_path: str | Path, config: Config,
                 trace: TraceLogger | None = None) -> dict:
    case = load_case(case_path)
    trace = trace or TraceLogger()
    store = make_store(config, case)

    screener = Screener(store, trace)
    screened = screener.run(case.get("evidence", []))

    extractor = EventExtractor(store, trace)
    events = extractor.run(screened["admitted"])

    checker = ChainChecker(store, trace)
    checked = checker.run(events)

    strategist = StrategyAgent(store, trace)
    draft = strategist.run(checked)

    reviewer = AdversarialReviewer(store, trace)
    review = reviewer.run(draft, checked)

    return {
        "case": case.get("title"),
        "synthetic": case.get("synthetic"),
        "datapack": config.meko_datapack,
        "backend": config.backend,
        "screened": {k: len(v) for k, v in screened.items()},
        "events": checked,
        "strategy_draft": draft,
        "review": review,
        "trace": trace,
        "missing_evidence": trace.missing_evidence(),
    }
