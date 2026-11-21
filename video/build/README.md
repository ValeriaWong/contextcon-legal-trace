# Traceable Counsel demo — build notes

Output: `../traceable-counsel-demo.mp4` — 115.43 s (1:55), 1280x720,
H.264 + AAC, 2,152,069 bytes. Under the 300 s cap.

## Sources (all real, nothing fabricated)
- Narration: script wording per beat (`../../demo-script.md`), 13 beats.
- On-screen text: only `../demo-live-take1.txt` (live Meko run 2026-11-21,
  exit 0, backend meko, datapack legal-audit-synthetic) and
  `../../data/synthetic-case.json`.
- Voice: Helio (`avocado_v2:MAI_03`), en, `/opt/hatch/bin/tts`.

## Rebuild
```
python3 render_frames.py   # frames/ (14 PNGs)
python3 synth.py           # audio/ (13 MP3s) + durations.json
python3 assemble.py        # traceable-counsel-demo.mp4
```
Frame duration = its narration length, except the refusal trace (f10,
forced 20 s) and the end card (f14, 5 s silent). The concat step MUST use
`-shortest`: without it the first build came out 212.12 s because the
concatenated audio track carried ~102 s of trailing silence.

## Known gaps vs the script (kept honest, not papered over)
1. 1:35 reviewer beat: no adversarial trace item explicitly cites EVT-01.
   The video shows what the trace has — EVT-01 cited by T015 (extractor),
   T021 (chain checker), T027 (strategy), and the reviewer (T033–T035)
   testing the draft from the same shared events. Narration keeps the
   script wording.
2. The script's "1 context_search, 0 raw-chat reads" is a retrieval-log
   figure the live take does not contain, so the Strategy frame says
   "reads the event from shared memory — the raw chat is not opened"
   with no count. Likewise "raw chat read 1 time (at ingest)" on the
   counter frame is the pipeline's design (Screener ingests once), not a
   number from the trace.
3. Runtime is 1:55, not the script's 4:30 budget: beats run at narration
   speed, order and wording preserved, refusal trace held a full 20 s.
