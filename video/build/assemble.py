#!/usr/bin/env python3
"""Assemble frame + narration segments into the final demo mp4.

Frame duration = its narration length (refusal trace f10 forced to >= 20s,
end card f14 fixed at 5s silent). Total must stay under 300s.
"""
import json
import subprocess
from pathlib import Path

BUILD = Path(__file__).resolve().parent
VIDEO = BUILD.parent
FRAMES = VIDEO / "frames"
AUDIO = BUILD / "audio"
SEG = BUILD / "segments"
SEG.mkdir(exist_ok=True)

durations = json.loads((BUILD / "durations.json").read_text())

# (frame, audio or None, duration override or None)
PLAN = [
    ("f01_title", "n01", None),
    ("f02_screener", "n02", None),
    ("f03_extractor", "n03", None),
    ("f04_strategy", "n04", None),
    ("f05_reviewer", "n05", None),
    ("f06_counter", "n06", None),
    ("f07_chain", "n07", None),
    ("f08_question", "n08", None),
    ("f09_challenge", "n09", None),
    ("f10_refusal", "n10", 20.0),   # refusal trace: min 20s on screen
    ("f11_downgrade", "n11", None),
    ("f12_missing", "n12", None),
    ("f13_closing", "n13", None),
    ("f14_endcard", None, 5.0),     # silent end card
]

list_lines = []
total = 0.0
for i, (frame, audio, override) in enumerate(PLAN):
    seg = SEG / f"seg{i:02d}.mp4"
    if audio:
        adur = durations[audio]
        dur = max(adur + 0.15, override or 0)
        cmd = ["ffmpeg", "-y", "-v", "error",
               "-loop", "1", "-i", str(FRAMES / f"{frame}.png"),
               "-i", str(AUDIO / f"{audio}.mp3"),
               "-af", f"apad=whole_dur={dur:.2f}",
               "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30",
               "-c:a", "aac", "-t", f"{dur:.2f}", str(seg)]
    else:
        dur = override
        cmd = ["ffmpeg", "-y", "-v", "error",
               "-loop", "1", "-i", str(FRAMES / f"{frame}.png"),
               "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
               "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30",
               "-c:a", "aac", "-t", f"{dur:.2f}", str(seg)]
    subprocess.run(cmd, check=True)
    print(f"seg{i:02d} {frame}: {dur:.2f}s")
    list_lines.append(f"file '{seg}'")
    total += dur

(BUILD / "concat.txt").write_text("\n".join(list_lines) + "\n")
print(f"TOTAL planned: {total:.2f}s")
assert total < 300, "over 5-minute cap"

out = VIDEO / "traceable-counsel-demo.mp4"
subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0",
                "-i", str(BUILD / "concat.txt"),
                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30",
                "-c:a", "aac", "-shortest", str(out)], check=True)
print("wrote", out, out.stat().st_size, "bytes")
