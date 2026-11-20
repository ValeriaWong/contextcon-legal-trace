# Traceable Counsel — ContextCon Track 07: Best auditability

> **SYNTHETIC DATA ONLY.** Every person, company, date, amount, and chat
> message in this project is fictional. Nothing here is a real case, a real
> client, or real personal data.

A legal agent whose every conclusion can be explained in under 2 minutes,
with a full decision trace. Five agents share one Meko datapack; an event
extracted once is reused by every later agent without re-reading the raw
chat; and when the evidence does not support a conclusion, the system says
so, names the missing evidence item, and shows the trace.

Built for **ContextCon: Remember Everything** (YugabyteDB / HackerEarth),
Track 07 "Best auditability" — *Show Your Work: anyone should be able to
answer "why did the agent do that?" in 2 minutes.*

- Submission due: **Jan 17, 2027, 11:59 PM PT**
- Submission: recorded demo under 5 minutes + public GitHub repo +
  optional documentation
- Registered: Allen Xiao, geekxl15@gmail.com, solo ("Allen's Team")

## What it is

- A pipeline over fictional WeChat chat records, following Allen's
  six-step method for WeChat records as evidence: collect, authenticate,
  organise a timeline, extract key events, check the evidence chain,
  form a strategy.
- Five agents, each with one job: Screener, Event Extractor, Chain
  Checker, Strategy Agent, Adversarial Reviewer. They communicate only
  through the shared Meko datapack — never directly with each other.
- A decision-trace logger: every claim carries the evidence IDs it came
  from, or a `cannot_verify` status. Claims with neither are rejected
  by the logger, not by good intentions.
- A token-measurement script: baseline (stuff the whole raw chat into
  the prompt) vs. Meko retrieval (send only the retrieved slices).

## What it is NOT

- **Not court-ready.** Nothing here is ready to file, and nothing is
  legally binding.
- **Not legal advice.** The strategy output is a *draft for a human
  lawyer to review*. If you are not a lawyer, do not rely on it.
- **Not a real case.** The synthetic case (`data/synthetic-case.json`)
  is invented. Any resemblance to a real person, company, or case is
  coincidence — and if Allen spots one, that name/date/amount is changed
  before submission.
- **Not a full implementation of ComplexEvidenceSociety.** The design
  draws on that paper's multi-agent pattern (agent roles: evidence
  screening, event extraction, evidence layering, adversarial review,
  strategy generation / analysis / verification / update, supplementary
  information). Those are **agent roles**, not human lawyer / client /
  judge roles, and this project implements a deliberate subset of five
  agents, not all ten roles.
- **Not a statute database.** Legal-knowledge items in the datapack are
  labelled summaries, not quotations. Article numbers and quotations
  must be verified against the official text by a lawyer before they are
  presented as law.

## Quick start (no paid service, no key required for the stub demo)

The scaffold runs in **stub mode** with no Meko account, no model call,
and no key. The agents are deterministic and rule-based over the
synthetic case, so the demo is reproducible.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt   # stdlib only; nothing to install
python3 run_demo.py               # runs the pipeline, prints the trace
python3 run_demo.py --scene refusal
python3 -m src.measure_tokens
python3 -m unittest discover -s tests -v
```

Expected output of `run_demo.py`: the timeline, the chain report, the
strategy draft, the adversarial review, and a trace summary — all with
evidence IDs. Exit code is 0 when every claim in the trace is cited or
marked `cannot_verify`.

## Setup with live Meko (Allen only)

1. Allen creates a Meko account himself at https://mekodata.ai
   (Sign Up) — **do not create it on his behalf, and do not record any
   key anywhere**.
2. In the Meko portal, create a datapack named `legal-audit-synthetic`.
3. Connect a client, either with the installer
   (`npx @yugabytedb/meko-mcp@latest --client <client> --url "https://mcp.mekodata.ai/mcp"`)
   or with an API key (Settings > API Keys; keys start with `mko_tkn_`,
   shown once). The MCP endpoint is `https://mcp.mekodata.ai/mcp`.
   Auth sends `Authorization: Bearer <key>` **and**
   `User-Agent: meko-mcp-installer/1.0` — Meko rejects requests without
   either.
4. Copy `.env.example` to `.env` and fill it in locally. **Never commit
   `.env`.** Never paste a key into chat, docs, or a trace log.
5. Run with the live client: `python3 run_demo.py --backend meko`
   (lists the MCP server's tools first; see `src/meko_client.py`).

Free-tier budget (verified against Meko docs, see PLAN.md §3): 1 datapack
of 10; knowledge well under 100 MB / 5 MB per file; under 100 retrieval
calls per run against 10,000/month; under 50 conversation messages per
run against 1,000/month. Rehearse in stub mode (zero Meko calls) whenever
possible.

## Free-model notes

- No model is required. The stub agents are the default and the fallback
  for the recorded demo.
- A free model may be plugged in later through `src/llm.py`
  (`LLMClient` interface). Use free APIs only, through Allen's existing
  free-API process, and keep every key in env vars only. The model is
  never the guardrail: the trace logger rejects uncited claims whatever
  the model says.
- If a plugged-in model hallucinates a citation, the demo falls back to
  stub mode. Do not record a demo with a hallucinated citation.

## Repository layout

```
PLAN.md                  architecture, datapack design, judging criteria
README.md                this file
datapack-schema.md       exact datapack structure + synthetic case
demo-script.md           <5 min demo, two scenes, timed
SUBMISSION-CHECKLIST.md  what is still missing before Jan 17, 2027
.env.example             placeholders only, no real values
run_demo.py              CLI entry point (stub mode by default)
data/synthetic-case.json the one fictional case
src/                     config, Meko client, trace logger, agents, pipeline
tests/                   trace-logger tests
```

## Licence

To be decided by Allen before the repo is made public (MIT is the usual
default for this kind of scaffold; do not assume it). No licence file is
included in this scaffold — add one when the GitHub repo is created.
