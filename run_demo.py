#!/usr/bin/env python3
"""Run the Traceable Counsel demo pipeline (stub mode by default).

Usage:
    python3 run_demo.py                  # stub, full pipeline, prints trace
    python3 run_demo.py --scene refusal  # only the refusal (demo scene B)
    python3 run_demo.py --backend meko   # live Meko (needs .env with a key)
    python3 run_demo.py --trace-out traces/trace.json

Stub mode needs no Meko account, no model call, and no key.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from src.config import load_config
from src.pipeline import run_pipeline
from src.trace import TraceLogger

ROOT = Path(__file__).resolve().parent
CASE = ROOT / "data" / "synthetic-case.json"


def main() -> int:
    parser = argparse.ArgumentParser(description="Traceable Counsel demo")
    parser.add_argument("--backend", choices=["stub", "meko"], default=None,
                        help="stub (default) or meko (live, needs .env key)")
    parser.add_argument("--scene", choices=["all", "refusal"], default="all")
    parser.add_argument("--case", default=str(CASE))
    parser.add_argument("--trace-out", default=None)
    args = parser.parse_args()

    config = load_config()
    if args.backend:
        # Rebuild config with the CLI backend (config already validated env).
        from dataclasses import replace
        config = replace(config, backend=args.backend)
        if config.backend == "meko" and not config.meko_api_key:
            parser.error("MEKO_BACKEND=meko requires MEKO_API_KEY in .env")

    trace = TraceLogger()
    result = run_pipeline(args.case, config, trace)

    print("Traceable Counsel — ContextCon Track 07 (SYNTHETIC CASE ONLY)")
    print(f"Datapack: {result['datapack']}  |  Backend: {result['backend']}")
    print(f"Screened: {result['screened']}")
    print()
    print("Events (chain status):")
    for event in result["events"]:
        print(f"  {event['id']} {event['date']} [{event['chain_status']}] "
              f"{event['title']}  — {', '.join(event['evidence_ids'])}")
    print()
    print("Strategy draft:")
    print(f"  {result['strategy_draft']['headline']}")
    print(f"  {result['strategy_draft']['disclaimer']}")
    print()
    print("Adversarial review:", result["review"]["verdict"])
    print("Missing evidence:", result["missing_evidence"])
    print()
    print("Decision trace:")
    records = trace.records
    if args.scene == "refusal":
        records = [r for r in records if r.status in ("refused", "cannot_verify")]
    for r in records:
        ev = ", ".join(r.evidence_ids) if r.evidence_ids else "—"
        print(f"  [{r.turn_id}] {r.agent} ({r.status}) evidence: {ev}")
        print(f"      {r.claim}")
        if r.reason:
            print(f"      reason: {r.reason}")
        if r.missing:
            print(f"      missing: {', '.join(r.missing)}")
    if args.trace_out:
        path = trace.write(args.trace_out)
        print(f"\nTrace written to {path}")

    # Exit non-zero if any claim in the trace is uncited without a
    # cannot_verify / refused status — the logger should already have
    # rejected those, so this is a belt-and-braces check.
    bad = [r for r in trace.records
           if not r.evidence_ids and r.status not in ("cannot_verify", "refused")]
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
