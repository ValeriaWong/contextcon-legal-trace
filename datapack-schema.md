# Datapack schema — `legal-audit-synthetic`

> **SYNTHETIC DATA ONLY.** All parties, dates, amounts, and messages below
> are fictional. This file is the entire case: there is no other case file,
> no real chat export, and no real personal data anywhere in this project.

## 1. The one datapack

| Field | Value |
|---|---|
| Datapack name (to create in the Meko portal) | `legal-audit-synthetic` |
| Owner | Allen Xiao (Meko account created by Allen himself) |
| Purpose | One shared context for the five agents; the only source of truth |
| Free-tier cost | 1 of 10 datapacks; knowledge < 100 KB of the 100 MB allowance |

Meko endpoint (verified): `https://mcp.mekodata.ai/mcp`. The datapack is
selected by `datapack_id` / datapack name in each MCP tool call; the URL
does not change between datapacks.

## 2. The three namespaces — never mixed

Every record in the datapack carries a `namespace` field with exactly one
of these values. A record that mixes namespaces is a schema violation and
is rejected on ingest.

### 2.1 `case_fact` — what (allegedly) happened

- Source: the synthetic WeChat excerpts in §5 / `data/synthetic-case.json`.
- Identifiers: evidence items `EV-001` … `EV-014`; extracted events
  `EVT-01` … `EVT-06`.
- A case fact is citable **only** by its evidence ID. A fact with no
  evidence ID is not a fact — it is a gap.
- Speaker attribution is part of the fact. An item whose speaker cannot
  be attributed is `flagged`, never `admitted`, and no event may be built
  on it. (Allen's grounding caveat: a text-span match proves a phrase is
  *present in the text*; it does not prove the interpretation, and it does
  not replace speaker-attribution verification.)

### 2.2 `legal_knowledge` — what the law (allegedly) says

- Source: topics Allen curates. Identifiers: `KNOW-001` …
- **Every knowledge item is a labelled summary, not a quotation.**
  Format: `summary`, `topic`, `jurisdiction`, `source_label`,
  `verify_before_use: true`.
- **No statute article number is asserted as authoritative in this
  scaffold.** The entries below name topics only. Before submission,
  Allen verifies each one against the official text; an unverified entry
  is presented in the demo as "topic to verify", never as law.
- Knowledge is never cited as a case fact. A strategy claim that rests
  on law cites `KNOW-xxx` **and** the case facts it applies to
  (`EV-xxx` / `EVT-xx`). Law alone proves nothing about this case.

Knowledge entries in this scaffold (topics only — verify before use):

| ID | Topic | Jurisdiction | Source label | Status |
|---|---|---|---|---|
| KNOW-001 | Electronic data as evidence: authenticity, integrity, and the need to prove source and completeness | PRC (general principle) | Topic summary — verify against official text | `verify_before_use: true` |
| KNOW-002 | Contract formation: offer, acceptance, and when a chat message can amount to an agreement | PRC (general principle) | Topic summary — verify against official text | `verify_before_use: true` |
| KNOW-003 | Burden of proof: who must prove what, and what happens when a fact cannot be proved | PRC (general principle) | Topic summary — verify against official text | `verify_before_use: true` |
| KNOW-004 | WeChat records as evidence: collection, authentication, and the six-step method (collect, authenticate, timeline, extract, check chain, strategy) | Allen's public WeChat-evidence work | Method summary, not a statute | `verify_before_use: true` |

### 2.3 `decision_trace` — why the agent did that

- One trace record per agent turn. Fields: `turn_id`, `agent`,
  `retrieved` (what was retrieved, with relevance score), `claim`,
  `evidence_ids`, `status` (`verified` / `unsupported` / `cannot_verify` /
  `refused`), `reason`, `tokens_in`, `tokens_out`.
- A trace record with a claim and empty `evidence_ids` and status other
  than `cannot_verify` / `refused` is invalid and is rejected by
  `src/trace.py` (see `tests/test_trace.py`).
- Traces are the audit log. They are what the demo shows on screen and
  what a judge reads to answer "why did it do that?" in under 2 minutes.

## 3. Record shapes (JSON)

### Evidence item

```json
{
  "id": "EV-003",
  "namespace": "case_fact",
  "kind": "wechat_message",
  "speaker": "Fang Qing (fictional claimant)",
  "timestamp": "2026-03-14T10:24:00+08:00",
  "text": "…",
  "status": "admitted",
  "auth_notes": "speaker attributed; timestamp plausible; complete message",
  "synthetic": true
}
```

### Event

```json
{
  "id": "EVT-02",
  "namespace": "case_fact",
  "title": "…",
  "date": "2026-03-14",
  "evidence_ids": ["EV-003", "EV-004"],
  "chain_status": "complete",
  "missing": []
}
```

### Strategy claim

```json
{
  "id": "CLM-01",
  "namespace": "decision_trace",
  "claim": "…",
  "evidence_ids": ["EVT-02"],
  "knowledge_ids": ["KNOW-002"],
  "status": "verified",
  "agent": "strategy"
}
```

### Refusal (the important one)

```json
{
  "id": "CLM-09",
  "namespace": "decision_trace",
  "claim": "The respondent admitted the debt in writing.",
  "evidence_ids": [],
  "status": "refused",
  "reason": "No evidence item in the datapack is a written admission. The closest item, EV-011, is a promise to 'sort it out', which is not an admission of a specific debt.",
  "missing": ["EV-014 (written admission — does not exist in this case)"]
}
```

## 4. Memory promotion rule

- Private memory: per-agent working notes, drafts, rejected hypotheses.
  Never cited, never promoted silently.
- Shared memory: only admitted evidence items, extracted events, and
  chain verdicts. Promotion is an explicit, logged action
  (`promote(memory_id, reason, evidence_ids)`).
- Nothing is promoted on the basis of a model output alone. Promotion
  requires an evidence ID.

## 5. The synthetic case — "The Blue Mountain delivery"

**All of this is fictional.** Parties, company, dates, amounts, and
messages were invented for this scaffold. Label on every surface:
`SYNTHETIC CASE — FICTIONAL`.

- **Claimant (fictional):** Fang Qing, sole trader, "Qing's Studio"
  (fictional).
- **Respondent (fictional):** Zhou Mingyuan, manager of "Blue Mountain
  Trading Co. Ltd." (fictional company).
- **Dispute (fictional):** a delivery of 200 gift boxes, agreed price
  48,000 fictional yuan, delivery on 2026-03-10, payment due within
  7 days. The claimant says the goods were delivered and only 20,000
  was paid; the respondent says the goods were late and partly damaged.
- **What is in the datapack:** 14 evidence items (EV-001 … EV-014 is
  *reserved* — see below), 6 extracted events (EVT-01 … EVT-06).
- **What is deliberately NOT in the datapack:** EV-014, a written
  admission of the debt. It is referenced in the trace as a missing item
  so the refusal in demo scene B has something concrete to point at.
  It does not exist, and no agent may invent it.

### Evidence items (summary; full text in `data/synthetic-case.json`)

| ID | Date | Speaker (fictional) | Content (summary) | Status |
|---|---|---|---|---|
| EV-001 | 2026-03-02 | Fang Qing | Order confirmed: 200 gift boxes, 48,000 | admitted |
| EV-002 | 2026-03-02 | Zhou Mingyuan | "OK, send them. Pay within 7 days of delivery." | admitted |
| EV-003 | 2026-03-10 | Fang Qing | "Delivered today, signed for at the warehouse." + delivery photo note | admitted |
| EV-004 | 2026-03-10 | Warehouse (via Fang Qing) | Signed delivery note, 200 boxes | admitted |
| EV-005 | 2026-03-12 | Zhou Mingyuan | "Got them. Will check quality." | admitted |
| EV-006 | 2026-03-15 | Zhou Mingyuan | "20,000 sent today, rest after we check." | admitted |
| EV-007 | 2026-03-15 | Fang Qing | Bank receipt note: 20,000 received | admitted |
| EV-008 | 2026-03-18 | Zhou Mingyuan | "Some boxes were damaged, maybe 30." | admitted |
| EV-009 | 2026-03-18 | Fang Qing | "Send photos of the damage, please." | admitted |
| EV-010 | 2026-03-20 | Zhou Mingyuan | "Will sort it out next week." | admitted |
| EV-011 | 2026-03-20 | Zhou Mingyuan | "Let's sort it out — don't rush me." | admitted |
| EV-012 | 2026-03-25 | Fang Qing | "A week has passed, no photos, no payment." | admitted |
| EV-013 | 2026-03-25 | Unknown number | "The goods are fine, pay up." — speaker unattributed | **flagged** (speaker unverified; never used to build an event) |
| EV-014 | — | — | Written admission of the debt — **does not exist** | missing (by design) |

### Extracted events

| ID | Date | Event | Evidence | Chain |
|---|---|---|---|---|
| EVT-01 | 2026-03-02 | Contract formed: 200 boxes, 48,000, pay in 7 days | EV-001, EV-002 | complete |
| EVT-02 | 2026-03-10 | Delivery: 200 boxes signed for | EV-003, EV-004 | complete |
| EVT-03 | 2026-03-15 | Part payment: 20,000 received | EV-006, EV-007 | complete |
| EVT-04 | 2026-03-18 | Damage alleged: "maybe 30" boxes | EV-008 | gap — no photos, no count, no inspection record |
| EVT-05 | 2026-03-20 | Respondent promises to "sort it out" | EV-010, EV-011 | complete (as a promise, not as an admission) |
| EVT-06 | 2026-03-25 | Demand: balance unpaid, no damage photos received | EV-012 | complete |

Note EVT-05 carefully: it is a promise to sort things out. It is **not**
an admission of a specific debt, and no agent may upgrade it into one.
That distinction is the whole of demo scene B.

## 6. Ingest checklist (when the datapack is created)

1. Create datapack `legal-audit-synthetic` in the Meko portal.
2. Upload `data/synthetic-case.json` as the case-fact source (or ingest
   item by item through the pipeline — either way, IDs must match §5).
3. Upload the four KNOW topics as knowledge docs, each labelled
   `summary — verify against official text`.
4. Run `python3 run_demo.py --backend stub` first; only then
   `--backend meko`. Confirm the trace in Meko matches the stub trace
   item for item.
5. Do not upload anything else. No real chat export, no real names, no
   real documents — ever.
