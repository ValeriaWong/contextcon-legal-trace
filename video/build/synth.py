#!/usr/bin/env python3
"""Synthesize one TTS segment per script beat; measure each with ffprobe."""
import json
import subprocess
import sys
from pathlib import Path

BUILD = Path(__file__).resolve().parent
AUDIO = BUILD / "audio"
AUDIO.mkdir(exist_ok=True)

narr = json.loads((BUILD / "narration.json").read_text())
durations = {}
for key in sorted(narr):
    out = AUDIO / f"{key}.mp3"
    if out.exists():
        print(f"skip {key} (exists)")
    else:
        r = subprocess.run(
            ["/opt/hatch/bin/tts", "speak", "--output", str(out),
             "--voice", "avocado_v2:MAI_03", "--language", "en",
             "--text-stdin"],
            input=narr[key].encode(), capture_output=True, timeout=300)
        if r.returncode != 0:
            print(f"FAILED {key}: {r.stdout.decode()[:300]} {r.stderr.decode()[:300]}")
            sys.exit(1)
        print(f"synthesized {key}: {out.stat().st_size} bytes")
    p = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                        "format=duration", "-of",
                        "default=noprint_wrappers=1:nokey=1", str(out)],
                       capture_output=True, text=True)
    durations[key] = float(p.stdout.strip())
    print(f"  {key}: {durations[key]:.2f}s")

total = sum(durations.values())
print(f"TOTAL narration: {total:.2f}s")
(BUILD / "durations.json").write_text(json.dumps(durations, indent=2))
