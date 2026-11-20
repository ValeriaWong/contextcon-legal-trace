# PLAN — ContextCon Legal Auditability (Track 07)

> Status: scaffolding only. No Meko account, no GitHub repo, no API key, no payment.
> Everything in this folder is synthetic. No real client, no real case, no real personal data.

## 1. What this project is

**Name (working):** Traceable Counsel — a legal agent that shows its work.

A multi-agent system that takes a small set of fictional WeChat chat records,
turns them into a checkable evidence chain, and produces a litigation
strategy draft — where **every conclusion cites the evidence item it came
from, or says it cannot be verified**.

The demo question the project answers, in the words of Track 07:

> "Anyone should be able to answer 'why did the agent do that?' in 2 minutes."

That is the whole product. It is not a lawyer, not a court filing tool,
and not legal advice.

### 1.1 The one-sentence pitch

Five agents share one Meko datapack. An event extracted once is reused by
every later agent without re-reading the raw chat — and when the evidence
does not support a conclusion, the system says so, names the missing item,
and shows the trace.

## 2. ContextCon facts relied on (verified 2026-11-21)

Source: ContextCon official page, https://www.hackerearth.com/lp/challenges/contextcon

- Track 07, "Best auditability": *Show Your Work — Anyone should be able to
  answer "why did the agent do that?" in 2 minutes. Trace end to end. Make
  it readable. Span several agents. Replay and resume.*
- Submission due: **Jan 17, 2027, 11:59 PM PT**. Submission = recorded demo
  under 5 minutes + GitHub repository (public / open-source) + optional
  documentation.
- Judging: Yugabyte experts review every submission, Jan 18–24, 2027.
- Total prize pool $10,000: Grand $4,000, Runner-up $2,500,
  Second runner-up $1,500, Best use of shared memory $1,000,
  People's choice $1,000. Solo builders and teams compete for the same prizes.
- Registration: Allen Xiao, geekxl15@gmail.com, solo, already registered
  2026-11-20. Team "Allen's Team", 1 member.

### Judging criteria — and how this project meets each one

| Criterion | Weight | How this project meets it |
|---|---|---|
| Use of Meko | 30% | One datapack shared by all five agents. Conversations, memory (private → shared), knowledge, artifacts, and decision traces are all used — see §4. No agent keeps a private copy of the evidence; the datapack is the only source of truth. |
| Impact & usefulness | 25% | A real, painful problem for lawyers: an agent that asserts a fact it cannot prove is worse than useless in litigation. The system makes "cannot verify" a first-class, visible outcome. |
| Technical execution | 20% | Working demo, clean module boundaries, a trace log that is machine-checkable (every claim carries evidence IDs), a token-measurement script, tests for the trace logger. |
| Innovation | 15% | The audit trail is the feature, not an afterthought: refusal/downgrade is a scored behaviour, and the missing-evidence list is generated, not hand-written. |
| Presentation | 10% | Two-scene demo under 5 minutes (§7), with the trace readable on screen in under 2 minutes. |

## 3. Meko — verified facts and what was relied on

Verified 2026-11-21 from the sources below. **No contradiction found:**
the free-tier numbers in the task brief match the Meko blog and docs exactly.

| Fact | Source |
|---|---|
| MCP endpoint for every account and datapack: `https://mcp.mekodata.ai/mcp` — the URL does not change when you switch datapacks; the `datapack_id` / datapack name in each MCP tool call selects the datapack. | docs.mekodata.ai/use-meko/connect/ — "MCP server URL" |
| Add to any MCP client, e.g. `claude mcp add --transport http meko https://mcp.mekodata.ai/mcp`, then `context_search("...")`. | mekodata.ai homepage — Quickstart |
| Free plan: **$0, no credit card. 10 datapacks, 100 MB knowledge, community support.** | mekodata.ai homepage — Pricing |
| Free tier includes: **10 datapacks, 1,000 conversations per month, 10,000 retrievals per month, 10M workbench tokens, 100 MB knowledge storage (5 MB max file size).** | yugabyte.com/blog/meko-self-sign-up-get-started/ (July 6, 2026) |
| MCP tool usage counts toward the free tier, including **1,000 conversation messages and 10,000 retrieval requests per month** (memory and knowledge-base searches). | docs.mekodata.ai/use-meko/connect/ — Free tier note |
| Auth, API key: keys are long-lived personal access tokens, each starts with `mko_tkn_`. Create in Settings > API Keys or the datapack Connect dialog. The full key is shown once. | docs.mekodata.ai/use-meko/connect/ — "API key" |
| Auth, headers: send `Authorization: Bearer <key>` **and** `User-Agent: meko-mcp-installer/1.0`. Meko rejects requests without either. A header / env var named `API_KEY`, `MEKO_API_KEY`, or `X-Api-Key` does not work. | docs.mekodata.ai/use-meko/connect/ — "Send the key as a Bearer" |
| Auth, OAuth: alternative to API key; point the client at the MCP URL and complete the browser handshake. OAuth does not work from the command line (local `http://127.0.0.1` callback returns HTML 403). Use the installer or an API key for CLI clients. Use only one method per client. | docs.mekodata.ai/use-meko/connect/ — "Choose an authentication method" |
| Installer (recommended for Claude/Cursor/Codex etc.): `npx @yugabytedb/meko-mcp@latest --client <client> --url "https://mcp.mekodata.ai/mcp"` | docs.mekodata.ai/use-meko/connect/ — Quick start |
| Check the connection: ask the agent "List my datapacks in Meko." — it calls the `datapack_list` tool. | docs.mekodata.ai/use-meko/connect/ — "To check the connection" |
| Datapack contents: conversations (verbatim, auto-tiered), memory (private → shared), knowledge (hybrid search), decision traces (reasoning + tokens), artifacts (versioned outputs). One datapack replaces database + vector store + RAG pipeline + memory + conversation store. | mekodata.ai homepage — "One datapack" |
| Self-learning loop: Search → Score (0–1 relevance) → Explain (what fell short) → Ask (gaps become a list of missing information) → Ingest. | mekodata.ai homepage — "Self-learning" |

### What was NOT verified from the docs

- The exact MCP tool names beyond `datapack_list` and `context_search`,
  which are the two names the docs actually print. The code in `src/`
  therefore lists tools at runtime (`list_tools`) before calling anything,
  and never hard-codes an unverified tool name as if it were documented.
  See `src/meko_client.py`.
- Whether ContextCon gives any Meko quota beyond the public free tier.
  The ContextCon page says only "get free Meko access". The plan budgets
  strictly inside the public free tier (§4.4).

## 4. Architecture

### 4.1 The six-step method (Allen's public WeChat-evidence work)

The pipeline follows the six steps Allen teaches for WeChat chat records
as court evidence. Each step is owned by one agent or stage, so the trace
can say which step produced which claim:

1. **Collect** — gather the chat records into the datapack, one evidence
   item per message group, with a stable ID (`EV-001`, …).
2. **Authenticate** — check each item for speaker attribution, timestamp
   plausibility, and completeness. Items that fail are marked, not deleted.
3. **Organise timeline** — order the surviving items chronologically.
4. **Extract key events** — turn dated, attributed messages into events
   (`EVT-01`, …), each citing its evidence IDs.
5. **Check the evidence chain** — for each event, ask: is the chain
   complete, or is a link missing? Record gaps explicitly.
6. **Form a strategy** — draft a strategy only from events whose chain
   is complete; everything else is labelled "cannot verify" or "needs
   further evidence".

Grounding rule (Allen's own caveat, kept as a hard rule): a text-span
match proves that a phrase is **present in the text**. It does not prove
the interpretation is correct, and it does not replace speaker-attribution
verification. The Chain Checker enforces this: an event whose speaker is
unverified can never be marked "verified".

### 4.2 The agents (5, not 10 — a deliberate, auditable subset)

The design draws on the **ComplexEvidenceSociety** multi-agent pattern
from the paper Allen studied. In that paper these are **agent roles in a
multi-agent system** — evidence screening, event extraction, evidence
layering, adversarial review, strategy generation / analysis /
verification / update, supplementary information — **not** human
lawyer / client / judge roles. This project does not claim otherwise,
and it does not implement all ten roles: it implements five, each with
one job, so that a human can audit each one in under two minutes.

| Agent | Module | Job | Input (from datapack) | Output (to datapack) |
|---|---|---|---|---|
| Screener | `agents/screener.py` | Step 1–2: admit or flag each evidence item; check speaker, timestamp, completeness. | Raw chat excerpts | `EV-xxx` items with status `admitted` / `flagged`, and a reason |
| Event Extractor | `agents/event_extractor.py` | Step 3–4: build the timeline, extract key events once. | Admitted `EV-xxx` items | `EVT-xx` events, each with `evidence_ids` |
| Chain Checker | `agents/chain_checker.py` | Step 5: verify each event's chain; list missing links. | `EVT-xx` events + evidence items | Chain verdict per event: `complete` / `gap`, plus `missing[]` |
| Strategy Agent | `agents/strategy.py` | Step 6: draft a strategy using only chain-complete events. | Chain-complete events only | Strategy draft; every claim carries `evidence_ids` |
| Adversarial Reviewer | `agents/adversarial.py` | Attacks the draft: tries to find a conclusion the evidence does not support; forces a refusal or downgrade. | Strategy draft + events + gaps | Review verdict; forced corrections; the missing-evidence list |

No agent talks to another agent directly. All communication goes through
the shared datapack. That is the point of the demo: remove Meko and the
agents cannot share anything.

### 4.3 Meko datapack design

One datapack: **`legal-audit-synthetic`** (name to be created by Allen in
the Meko portal — see SUBMISSION-CHECKLIST.md).

| Datapack layer | What lives there | Who writes it | Who reads it |
|---|---|---|---|
| Conversations | The run itself: each agent turn, verbatim, auto-tiered. The demo conversation is the audit log. | All agents (via Meko) | Anyone replaying the run |
| Memory — private | Per-agent working notes, drafts, rejected hypotheses. Never cited as evidence. | The agent that made them | That agent only |
| Memory — shared | Promoted facts only: admitted evidence items, extracted events, chain verdicts. Promotion is explicit and logged. | Screener, Extractor, Chain Checker | All agents |
| Knowledge | Legal knowledge, **strictly separated** from case facts (see below). | Allen / curator, uploaded as docs | All agents, cited as `KNOW-xxx`, never as case fact |
| Artifacts | Versioned outputs: timeline, chain report, strategy draft, review report, trace log. | Pipeline | Judges, demo |
| Decision traces | Reasoning + tokens per turn: which evidence was retrieved, with what relevance score, what was concluded, what was refused. | Trace logger (`src/trace.py`) + Meko | Anyone answering "why did it do that?" |

**Separation rule (hard):** case facts, legal knowledge, and decision
traces are three different namespaces and are never mixed in one record.

- A case fact cites `EV-xxx` / `EVT-xx` and lives in memory (shared).
- A legal-knowledge item cites `KNOW-xxx`, states its source, and is
  labelled `summary — not a quotation; verify against the official text`.
  No statute article number is asserted as authoritative in this scaffold;
  the knowledge entries are topics to be verified by Allen before
  submission (see `datapack-schema.md` §3).
- A decision trace cites the retrieval that produced it, the claim, and
  the evidence IDs — or records `evidence_ids: []` with status
  `cannot_verify`.

### 4.4 Free-tier budget

Design target: one full demo run must fit comfortably inside the free
tier, with headroom for rehearsals.

- 1 datapack (of 10).
- Knowledge: the synthetic case + knowledge summaries are a few tens of
  KB, far under 100 MB / 5 MB per file.
- Retrievals: the pipeline is designed for < 100 retrieval calls per run
  (one `context_search` per agent step, not one per claim); the free tier
  allows 10,000/month.
- Conversations: < 50 messages per run; the free tier allows 1,000/month.
- Tokens: no paid model is required. The scaffold runs in stub mode with
  no model call at all (deterministic, rule-based agents over the
  synthetic data). A free model may be plugged in later through the
  `LLMClient` interface in `src/llm.py` — never with a key committed to
  the repo.

If a rehearsal ever approaches a limit, the answer is to rehearse in stub
mode (zero Meko calls), not to upgrade. No paid tier, ever, for this project.

## 5. What the system must never do (hard rules)

1. **Never claim court-ready or legally binding.** Every output carries
   the disclaimer in README.md §1. The strategy draft is a *draft for
   a human lawyer to review*, not advice.
2. **Never use real data.** One fully fictional synthetic case only
   (`data/synthetic-case.json`). No real client data, no real case names,
   no real personal data, no real chat screenshots. If Allen spots anything
   in the synthetic case that resembles a real person or case, it is
   removed before submission — see SUBMISSION-CHECKLIST.md.
3. **Never assert a fact without evidence.** Every agent output must cite
   which evidence item it came from, or say it cannot be verified.
   The trace logger rejects claims with no `evidence_ids` and no
   `cannot_verify` status (see `src/trace.py`).
4. **Never invent a statute.** Knowledge items are labelled summaries;
   article numbers and quotations must be verified against the official
   text by Allen before they are presented as law.
5. **Never record a key.** No API key, token, or password anywhere in the
   repo, in docs, or in a trace log. Config is env vars only
   (`.env.example` contains placeholders, no real values).

## 6. Repository layout (this folder is the repo-to-be)

```
contextcon-legal/
  PLAN.md                  this file
  README.md                what it is / is not, setup, how to run the demo
  datapack-schema.md       exact datapack structure + synthetic case file
  demo-script.md           <5 min demo, two scenes, timed
  SUBMISSION-CHECKLIST.md  what is still missing before Jan 17, 2027
  .env.example             placeholders only, no real values
  .gitignore               .env, local traces, __pycache__
  requirements.txt         stdlib-only; optional httpx commented out
  run_demo.py              CLI: runs the pipeline in stub mode, prints the trace
  data/synthetic-case.json the one fictional case (labelled synthetic)
  src/
    config.py              env-var config, no defaults that look like keys
    meko_client.py         MCP/REST wrapper (Bearer + User-Agent), tool-list first
    trace.py               decision-trace logger, evidence-ID enforcement
    llm.py                 free-model interface (stub by default)
    pipeline.py            runs the five agents in order through one datapack
    agents/
      base.py              shared agent base: read/write datapack, cite-or-refuse
      screener.py          steps 1-2
      event_extractor.py   steps 3-4
      chain_checker.py     step 5
      strategy.py          step 6
      adversarial.py       attacks the draft, forces refusal/downgrade
    measure_tokens.py      baseline (stuff everything) vs Meko retrieval
  tests/
    test_trace.py          trace logger rejects uncited claims
```

## 7. Demo outline (full script in demo-script.md)

- **Scene A — three agents, one memory (approx. 2 min).** The Event
  Extractor extracts an event once. The Strategy Agent and the Adversarial
  Reviewer both reuse that same event from the shared datapack, without
  re-reading the raw WeChat chat. On screen: one event ID, three agents,
  zero re-reads.
- **Scene B — the refusal (approx. 2 min).** The presenter asks for a
  conclusion the evidence does **not** support ("the respondent admitted
  the debt in writing"). The system refuses / downgrades it, shows the
  trace in under 2 minutes, and names the missing evidence item
  (`EV-014`, a written admission that does not exist in the synthetic case).

## 8. Risks and open questions

- **Meko tool names:** only `datapack_list` and `context_search` are
  printed in the docs. The live MCP server may expose more tools
  (memory save/search, knowledge upload, trace tools). The first live
  run must list tools and update `meko_client.py` — do not guess.
- **Free-model quality:** the stub agents are deterministic and
  demo-safe. A free model plugged in later may hallucinate a citation;
  the trace logger is the guardrail, not the model. Keep the stub as
  the fallback for the recorded demo if the model misbehaves.
- **Synthetic-case leakage:** the fictional names, dates, and amounts
  were invented for this scaffold, but Allen must review them (checklist
  item) — a coincidence with a real case would be a reason to rename,
  not a reason to argue.
- **Two projects, one deadline:** Allen also approved the pet-memory
  project (Track 07, same deadline). These two projects share the track
  but are separate submissions. Do not merge them, and do not let work
  on one silently consume the other's demo time. Each has its own repo
  and its own datapack.
