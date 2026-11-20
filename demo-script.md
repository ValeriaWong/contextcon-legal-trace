# Demo script — under 5 minutes, two scenes

> Total budget: **4 minutes 30 seconds**. Record the demo with the stub
> backend first; only re-record with live Meko if the live trace matches
> the stub trace item for item.
>
> On screen at all times: the datapack name (`legal-audit-synthetic`),
> the label `SYNTHETIC CASE — FICTIONAL`, and the disclaimer
> "Not legal advice. Not court-ready."

## 0:00–0:30 — The problem (30 s)

Presenter, to camera, one slide:

- "Lawyers don't need an agent that sounds confident. They need one that
  can prove what it says — or admit what it can't."
- "This is Traceable Counsel. Five agents, one shared Meko datapack,
  one fictional WeChat case. Every conclusion cites its evidence, or says
  it cannot be verified."
- Show the case in one line: fictional delivery dispute, 200 gift boxes,
  48,000, 20,000 paid, balance disputed.

## Scene A — 0:30–2:30 — Three agents, one memory (2 min)

**What the viewer must see:** one event, extracted once, reused by three
agents, with zero re-reads of the raw chat.

| Time | On screen | Narration |
|---|---|---|
| 0:30 | Raw WeChat excerpts EV-001 / EV-002 in the datapack. | "The Screener admitted two messages: an order and an acceptance. That's the contract." |
| 0:50 | Event Extractor output: `EVT-01 — Contract formed, 2026-03-02, evidence EV-001, EV-002`. | "The Event Extractor turns those two messages into one event — once. It is now shared memory." |
| 1:10 | Strategy Agent panel: it cites `EVT-01` for the claim "a contract was formed". The raw chat is not opened. Retrieval log shows 1 `context_search`, 0 raw-chat reads. | "The Strategy Agent needs the contract. It reads the event, not the chat. One search, no re-read." |
| 1:35 | Adversarial Reviewer panel: it cites the *same* `EVT-01` to test the claim. Same event ID on screen, highlighted in both panels. | "The reviewer attacks the same claim — from the same shared event. If the event were wrong, both agents would be wrong together, and we would see it in one place." |
| 2:00 | Shared-memory counter: `EVT-01 read by 3 agents, raw chat read 1 time (at ingest)`. | "One agent's learning becomes every agent's advantage — and the audit trail shows it." |
| 2:20 | Chain Checker verdict for EVT-01: `complete`. | "The chain for this event is complete. The next event is not — and that matters in scene B." |

**Cut line if running long:** the 1:35 reviewer beat. Never cut the
counter at 2:00 — it is the shared-memory proof.

## Scene B — 2:30–4:30 — The refusal (2 min)

**What the viewer must see:** a conclusion the evidence does not support,
refused in under 2 minutes, with the missing item named.

| Time | On screen | Narration |
|---|---|---|
| 2:30 | Presenter asks, live: "Did the respondent admit the debt in writing?" | "Now the test that matters. I am asking for a conclusion the evidence does not support." |
| 2:40 | Strategy Agent's first pass is shown, then the Adversarial Reviewer's challenge: "EV-011 is a promise to 'sort it out'. That is not an admission." | "The draft almost upgrades a promise into an admission. The reviewer catches it." |
| 3:05 | The trace, full screen, readable: claim `CLM-09`, status `refused`, evidence `[]`, reason, and `missing: EV-014 (written admission — does not exist in this case)`. | "Here is the whole answer, in under two minutes. No written admission exists in this case. The closest item is a promise, and a promise is not an admission." |
| 3:40 | Downgraded conclusion shown instead: "The respondent promised to sort it out on 2026-03-20 (EV-010, EV-011). Whether that promise amounts to an admission is a question for a human lawyer — the system will not decide it." | "So the system downgrades the claim to what the evidence actually says, and hands the legal judgment back to a human." |
| 4:05 | Missing-evidence list: `EV-014 — written admission (missing)`, plus the gap on EVT-04 (damage alleged, no photos). | "And it tells you what would change its mind: a written admission, and photos of the alleged damage. That list is generated, not hand-written." |
| 4:25 | Closing slide: trace, datapack, repo link. | "Show your work — or say you can't. That's the whole system." |

## Recording notes

- Record scene A and scene B as separate takes; edit to the timings above.
- If a live-Meko take disagrees with the stub trace, **use the stub take**.
  A deterministic trace beats a live hallucination.
- Never show a real chat screenshot, a real name, or a real document.
  Every message on screen must be from `data/synthetic-case.json`.
- Keep the trace on screen long enough to read: at least 20 seconds for
  the refusal trace at 3:05. Judges need to be able to pause and verify it.
- End card (5 s, inside the 5-minute limit): repo URL, "Synthetic data
  only. Not legal advice. Not court-ready."
