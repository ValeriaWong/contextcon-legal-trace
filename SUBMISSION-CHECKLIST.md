# Submission checklist — ContextCon Legal (Track 07)

Deadline: **Jan 17, 2027, 11:59 PM PT** (Beijing time Jan 18, 2027, 15:59).
Submission: recorded demo under 5 minutes + public GitHub repo + optional docs.
Track: 07 Best auditability. Registered: Allen Xiao, geekxl15@gmail.com, solo.

## Done in this scaffold (2026-11-21)

- [x] PLAN.md — architecture, datapack design, judging-criteria mapping
- [x] README.md — what it is / is not, stub-mode setup, free-model notes
- [x] datapack-schema.md — three namespaces, record shapes, synthetic case
- [x] demo-script.md — two scenes, timed to 4 min 30 s
- [x] Code skeleton in Python (stdlib only): Meko client wrapper, five
      agents, trace logger with evidence-ID enforcement, token measurement,
      CLI runner, trace-logger tests
- [x] Synthetic case file (`data/synthetic-case.json`) — one fictional
      case only, labelled synthetic throughout
- [x] Meko docs verified (endpoint, free tier, auth) — see PLAN.md §3.
      No contradiction with the free-tier numbers in the brief.
- [x] `.env.example` with placeholders only; `.gitignore` covers `.env`

## Still missing — needs Allen

- [ ] **Meko account + key, created by Allen himself.** Sign up at
      https://mekodata.ai, create datapack `legal-audit-synthetic`,
      generate a key (Settings > API Keys, `mko_tkn_…`, shown once).
      **Do not ask anyone else to create it, and do not record the key
      anywhere** — not in chat, not in a file, not in a trace log.
      The key lives only in Allen's local `.env` (see `.env.example`).
- [ ] **GitHub repo, created under ValeriaWong.** Suggested name:
      `ValeriaWong/contextcon-legal-trace` (confirm the name with Allen;
      do not create the repo in this scaffold). Push this folder's contents,
      add a licence (MIT is the usual default — Allen to confirm), and
      confirm the repo is public before submission. Verify no `.env` and
      no key was ever committed (check with `git log --all -p | grep -i
      mko_tkn_` before the first push, and again before submission).
- [ ] **Live Meko run.** Run `python3 run_demo.py --backend meko` once
      the account exists. First list the MCP server's tools and update
      `src/meko_client.py` if the live tool names differ from the two
      documented ones (`datapack_list`, `context_search`). Confirm the
      live trace matches the stub trace item for item; if it does not,
      record the demo with the stub backend.
- [ ] **Allen reviews the synthetic case for accidental real-data leak.**
      Read `data/synthetic-case.json` and `datapack-schema.md` §5 end to
      end. If any name, company, date, amount, or message resembles a
      real person or a real case, rename / change it and re-run the tests.
      Do not submit until this review is done.
- [ ] **Allen verifies the four KNOW topics** (`datapack-schema.md` §2.2).
      Each is a topic summary, not a quotation, and no article number is
      asserted in this scaffold. Verify against the official text, or
      present the item in the demo as "topic to verify".
- [ ] **Demo video recorded (< 5 min)** following `demo-script.md`.
      Record scene A and scene B as separate takes. Use the stub take if
      the live take disagrees with the stub trace.
- [ ] **Free-model decision (optional).** The stub agents are the default
      and the fallback. If Allen wants a free model plugged in via
      `src/llm.py`, do it through his existing free-API process, keep the
      key in env vars only, and re-run the trace tests — the logger must
      still reject uncited claims.
- [ ] **Final pre-submit sweep (day before deadline):** re-run
      `python3 -m unittest discover -s tests -v`, re-run
      `python3 run_demo.py`, confirm the demo link plays, confirm the
      repo is public and contains no key, confirm the submission form
      lists Track 07 and the correct repo URL.

## Deliberately NOT done

- No GitHub repo created, no Meko account created, no API key recorded,
  nothing paid for. All of those are Allen-only steps above.
- No real data of any kind. No real chat export, no real case name, no
  real personal data.
- No claim of court-readiness or legal advice anywhere in the scaffold.
