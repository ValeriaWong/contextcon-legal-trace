#!/usr/bin/env python3
"""Render 1280x720 dark terminal-style frames for the Traceable Counsel demo.

All on-screen text comes from the real live trace
(video/demo-live-take1.txt) and the synthetic case
(data/synthetic-case.json). No invented screens.
Every frame carries the footer bar: datapack name, SYNTHETIC CASE label,
and the not-legal-advice disclaimer.
"""
import json
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent  # video/
OUT = ROOT / "frames"
OUT.mkdir(parents=True, exist_ok=True)

W, H = 1280, 720
BG = (11, 15, 20)
PANEL = (17, 24, 33)
FOOTER_BG = (13, 20, 28)
WHITE = (229, 231, 235)
BODY = (209, 213, 219)
MUTED = (156, 163, 175)
GREEN = (74, 222, 128)
AMBER = (251, 191, 36)
RED = (248, 113, 113)
CYAN = (125, 211, 252)
RULE = (55, 65, 81)

SANS = "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf"
SANS_B = "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf"
MONO = "/usr/share/fonts/truetype/noto/NotoSansMono-Regular.ttf"
MONO_B = "/usr/share/fonts/truetype/noto/NotoSansMono-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap by measured width."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def render(frame_id, title, blocks, accent=GREEN):
    """blocks: list of (kind, text, size, color) where kind in
    h (heading), p (paragraph), mono, big, blank, rule."""
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    # top accent strip
    d.rectangle([0, 0, W, 6], fill=accent)
    # title
    tf = font(SANS_B, 30)
    d.text((64, 34), title, font=tf, fill=WHITE)
    d.line([(64, 84), (W - 64, 84)], fill=RULE, width=2)
    y = 112
    max_w = W - 128
    for kind, text, size, color in blocks:
        if kind == "blank":
            y += size
            continue
        if kind == "rule":
            d.line([(64, y + 8), (W - 64, y + 8)], fill=RULE, width=2)
            y += 28
            continue
        fpath = SANS_B if kind in ("h", "big") else (MONO if kind == "mono" else SANS)
        fnt = font(fpath, size)
        leading = int(size * 1.45)
        for line in wrap(d, text, fnt, max_w):
            d.text((64, y), line, font=fnt, fill=color)
            y += leading
        y += 10
    # footer bar on every frame
    d.rectangle([0, H - 52, W, H], fill=FOOTER_BG)
    d.line([(0, H - 52), (W, H - 52)], fill=RULE, width=2)
    ff = font(SANS, 19)
    left = "datapack: legal-audit-synthetic"
    center = "SYNTHETIC CASE — FICTIONAL"
    right = "Not legal advice. Not court-ready."
    d.text((24, H - 38), left, font=ff, fill=MUTED)
    cw = d.textlength(center, font=ff)
    d.text(((W - cw) / 2, H - 38), center, font=ff, fill=AMBER)
    rw = d.textlength(right, font=ff)
    d.text((W - 24 - rw, H - 38), right, font=ff, fill=MUTED)
    img.save(OUT / f"{frame_id}.png")
    print("wrote", frame_id)


F = []
# ---- F01 title ----
F.append(("f01_title", "TRACEABLE COUNSEL  ·  CONTEXTCON TRACK 07", [
    ("big", "Traceable Counsel", 66, WHITE),
    ("blank", "", 8, WHITE),
    ("h", "Best auditability — five agents, one shared Meko datapack", 30, CYAN),
    ("blank", "", 10, WHITE),
    ("p", "Every conclusion cites its evidence — or says it cannot be verified.", 28, BODY),
    ("blank", "", 8, WHITE),
    ("mono", "LIVE — Meko datapack legal-audit-synthetic", 26, GREEN),
    ("blank", "", 8, WHITE),
    ("p", "The case: The Blue Mountain delivery (fictional). 200 gift boxes, 48,000; 20,000 paid; balance disputed.", 26, BODY),
    ("blank", "", 6, WHITE),
    ("p", "\u201cLawyers don't need an agent that sounds confident. They need one that can prove what it says — or admit what it can't.\u201d", 26, MUTED),
], GREEN))

# ---- Scene A ----
F.append(("f02_screener", "SCENE A — THE SCREENER", [
    ("mono", "EV-001 · Fang Qing · 2026-03-02", 26, CYAN),
    ("p", "\u201cConfirming the order: 200 gift boxes, 48000 in total. Delivery by March 10.\u201d", 28, WHITE),
    ("blank", "", 14, WHITE),
    ("mono", "EV-002 · Zhou Mingyuan · 2026-03-02", 26, CYAN),
    ("p", "\u201cOK, send them. We pay within 7 days of delivery.\u201d", 28, WHITE),
    ("blank", "", 14, WHITE),
    ("p", "Screened (live trace): 12 admitted · 1 flagged — EV-013, speaker unattributed · 1 missing — EV-014", 26, BODY),
], GREEN))

F.append(("f03_extractor", "SCENE A — EVENT EXTRACTOR", [
    ("big", "EVT-01 — Contract formed, 2026-03-02", 40, WHITE),
    ("p", "Evidence: EV-001, EV-002", 26, BODY),
    ("p", "T015 · event_extractor — \u201cextracted once from admitted evidence; promoted to shared memory\u201d", 26, GREEN),
    ("rule", "", 0, WHITE),
    ("mono", "EVT-01 [complete] Contract formed", 24, BODY),
    ("mono", "EVT-02 [complete] Delivery: 200 boxes signed for", 24, BODY),
    ("mono", "EVT-03 [complete] Part payment: 20000 received", 24, BODY),
    ("mono", "EVT-04 [gap]      Damage alleged: \u2018maybe 30\u2019 boxes", 24, AMBER),
    ("mono", "EVT-05 [complete] Respondent promises to \u2018sort it out\u2019", 24, BODY),
    ("mono", "EVT-06 [complete] Demand: balance unpaid, no damage photos", 24, BODY),
], GREEN))

F.append(("f04_strategy", "SCENE A — STRATEGY AGENT", [
    ("p", "T027 · strategy — \u201cRely on EVT-01: Contract formed: 200 boxes, 48000, pay in 7 days.\u201d", 30, WHITE),
    ("blank", "", 10, WHITE),
    ("p", "Reason: \u201cPremise is a chain-complete event from shared memory.\u201d", 28, GREEN),
    ("blank", "", 10, WHITE),
    ("p", "The Strategy Agent reads the event from shared memory. The raw chat is not opened.", 28, BODY),
    ("blank", "", 10, WHITE),
    ("p", "Draft premises: EVT-01 contract · EVT-02 delivery · EVT-03 part payment  (T027–T029, T032)", 26, MUTED),
], GREEN))

F.append(("f05_reviewer", "SCENE A — ADVERSARIAL REVIEWER", [
    ("p", "EVT-01 cited by three agents — the same event in every panel:", 28, BODY),
    ("blank", "", 8, WHITE),
    ("mono", "T015 · event_extractor — EVT-01 extracted", 26, WHITE),
    ("mono", "T021 · chain_checker  — EVT-01 chain is complete", 26, WHITE),
    ("mono", "T027 · strategy       — Rely on EVT-01", 26, WHITE),
    ("blank", "", 14, WHITE),
    ("p", "Adversarial Reviewer (T033–T035) tests the draft from the same shared events — no private re-reads.", 26, GREEN),
], GREEN))

F.append(("f06_counter", "SCENE A — SHARED-MEMORY PROOF", [
    ("big", "EVT-01 read by 3 agents", 48, WHITE),
    ("blank", "", 6, WHITE),
    ("p", "Derived from the live trace: T015 (Event Extractor) · T021 (Chain Checker) · T027 (Strategy)", 28, BODY),
    ("blank", "", 10, WHITE),
    ("p", "Raw chat read once — at ingest, by the Screener. Every later agent reads shared memory.", 28, GREEN),
    ("blank", "", 10, WHITE),
    ("p", "One agent's learning becomes every agent's advantage.", 28, MUTED),
], GREEN))

F.append(("f07_chain", "SCENE A — CHAIN CHECKER", [
    ("p", "T021 · chain_checker — \u201cEvent EVT-01 chain is complete.\u201d", 30, WHITE),
    ("blank", "", 10, WHITE),
    ("p", "Reason: \u201cEvery cited item was admitted; no further link needed.\u201d", 28, GREEN),
    ("blank", "", 14, WHITE),
    ("p", "But the next event is not: T024 — EVT-04 has a gap in its chain. Damage alleged, no photos, no count, no inspection.", 28, AMBER),
], GREEN))

# ---- Scene B ----
F.append(("f08_question", "SCENE B — THE REFUSAL TEST", [
    ("blank", "", 60, WHITE),
    ("big", "\u201cDid the respondent admit the debt in writing?\u201d", 44, WHITE),
    ("blank", "", 24, WHITE),
    ("p", "A conclusion the evidence does not support — asked live.", 28, MUTED),
], AMBER))

F.append(("f09_challenge", "SCENE B — DRAFT vs CHALLENGE", [
    ("p", "Strategy first pass (T032): claim the unpaid balance on EVT-01, EVT-02, EVT-03.", 28, BODY),
    ("blank", "", 12, WHITE),
    ("p", "Reviewer challenge (T033): the closest item, EV-011, is a promise to \u2018sort it out\u2019 — which is not an admission of a specific debt.", 28, WHITE),
    ("blank", "", 12, WHITE),
    ("p", "EVT-05 is a promise, not an admission.", 30, AMBER),
], AMBER))

F.append(("f10_refusal", "DECISION TRACE — FULL SCREEN (LIVE)", [
    ("mono", "[T033] adversarial — REFUSED", 30, RED),
    ("p", "Claim: \u201cThe respondent admitted the debt in writing.\u201d", 28, WHITE),
    ("p", "Evidence: [ ]", 28, WHITE),
    ("p", "Reason: No evidence item in the datapack is a written admission. The closest item, EV-011, is a promise to \u2018sort it out\u2019, which is not an admission of a specific debt.", 26, BODY),
    ("p", "Missing: EV-014 (written admission — does not exist in this case)", 28, AMBER),
    ("rule", "", 0, WHITE),
    ("mono", "[T034] DOWNGRADED — promised to sort it out, 2026-03-20 (EV-010, EV-011)", 24, GREEN),
    ("mono", "[T035] CANNOT_VERIFY — damage allegation (EVT-04) cannot support a deduction", 24, AMBER),
], RED))

F.append(("f11_downgrade", "SCENE B — DOWNGRADED CONCLUSION", [
    ("p", "\u201cThe respondent promised to sort it out on 2026-03-20 (EV-010, EV-011). Whether that promise amounts to an admission is a question for a human lawyer.\u201d", 30, WHITE),
    ("blank", "", 14, WHITE),
    ("p", "T034 · adversarial — \u201cDowngraded to what the evidence actually says.\u201d", 28, GREEN),
    ("blank", "", 10, WHITE),
    ("p", "The system will not decide it. The legal judgment goes back to a human.", 28, BODY),
], AMBER))

F.append(("f12_missing", "SCENE B — WHAT WOULD CHANGE ITS MIND", [
    ("mono", "EV-014 — written admission (missing — does not exist in this case)", 28, AMBER),
    ("blank", "", 8, WHITE),
    ("mono", "damage photos · damage count · inspection record", 28, AMBER),
    ("p", "(EVT-04 gap — T024, T035)", 26, MUTED),
    ("blank", "", 14, WHITE),
    ("p", "This list is the trace's own missing fields (T014, T024, T035) — generated, not hand-written.", 26, BODY),
], AMBER))

F.append(("f13_closing", "SHOW YOUR WORK — OR SAY YOU CAN'T", [
    ("p", "Trace T001–T035 · live Meko backend · datapack legal-audit-synthetic", 28, BODY),
    ("blank", "", 10, WHITE),
    ("p", "Screener: 12 admitted · 1 flagged · 1 missing · 6 events · 1 refusal · 1 downgrade · 3 cannot_verify", 26, GREEN),
    ("blank", "", 10, WHITE),
    ("mono", "github.com/ValeriaWong/contextcon-legal-trace", 28, CYAN),
], GREEN))

F.append(("f14_endcard", "TRACEABLE COUNSEL", [
    ("blank", "", 80, WHITE),
    ("mono", "github.com/ValeriaWong/contextcon-legal-trace", 34, CYAN),
    ("blank", "", 24, WHITE),
    ("p", "Synthetic data only. Not legal advice. Not court-ready.", 30, BODY),
], GREEN))

for fid, title, blocks, accent in F:
    render(fid, title, blocks, accent)

print("frames:", len(F))
