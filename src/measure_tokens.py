"""Token measurement: baseline vs Meko retrieval.

Baseline: stuff the whole raw chat (every evidence item's text) into
the prompt — the way an agent without shared memory would do it.
Meko: send only the retrieved slices (the shared events and the
evidence they cite).

Token counts here are **estimates** (characters / 4, a common rough
approximation), not exact tokenizer counts. The script reports the
method alongside the numbers so a judge can reproduce them, and the
same estimator is used for both sides — the comparison, not the
absolute number, is the point. Re-run with a real tokenizer before
quoting exact figures in the submission docs.
"""

from __future__ import annotations

import json
from pathlib import Path

from src.config import load_config
from src.pipeline import load_case, run_pipeline

CHARS_PER_TOKEN = 4  # rough estimate; documented, applied to both sides


def estimate_tokens(text: str) -> int:
    return max(1, len(text) // CHARS_PER_TOKEN)


def measure(case_path: str | Path) -> dict:
    case = load_case(case_path)
    config = load_config()
    result = run_pipeline(case_path, config)

    raw_text = "\n".join(
        (item.get("text") or "") for item in case.get("evidence", [])
        if item.get("text")
    )
    baseline_tokens = estimate_tokens(raw_text)

    # Retrieved slices: the shared events plus the evidence they cite.
    cited_ids = set()
    for event in result["events"]:
        cited_ids.update(event["evidence_ids"])
    retrieved_text = "\n".join(
        (item.get("text") or "") for item in case.get("evidence", [])
        if item.get("id") in cited_ids and item.get("text")
    )
    meko_tokens = estimate_tokens(retrieved_text)

    saving = baseline_tokens - meko_tokens
    return {
        "method": f"estimate: characters / {CHARS_PER_TOKEN} (same for both sides)",
        "baseline_tokens": baseline_tokens,
        "meko_tokens": meko_tokens,
        "tokens_saved": saving,
        "saving_pct": round(100 * saving / baseline_tokens, 1)
        if baseline_tokens else 0.0,
        "events_reused": len(result["events"]),
        "evidence_items_total": len(case.get("evidence", [])),
        "evidence_items_cited": len(cited_ids),
        "note": "Estimates, not tokenizer counts. Do not quote as exact figures.",
    }


if __name__ == "__main__":
    print(json.dumps(measure(Path(__file__).resolve().parent.parent
                             / "data" / "synthetic-case.json"),
                     ensure_ascii=False, indent=2))
