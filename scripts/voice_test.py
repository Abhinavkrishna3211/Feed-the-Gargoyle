#!/usr/bin/env python3
"""Render a few gargoyle lines with Piper in several voices and settings and time them.

usage: voice_test.py OUTDIR   (run on the board; needs ~/piper/piper/piper and ~/piper/voices)
Writes OUTDIR/<voice>_<setting>_<n>.wav and OUTDIR/timings.jsonl (render seconds, audio seconds).
"""
import json, os, subprocess, sys, time, wave
from pathlib import Path

PIPER = Path.home() / "piper/piper/piper"
VOICES = sorted((Path.home() / "piper/voices").glob("*.onnx"))
LINES = ["You solved my stone-cold puzzle. Hold out your hand, clever one.",
         "Wrong answer! The stone shakes its head. Try again.",
         "Who knocks at my stone door? Speak, sweet seeker.",
         "Pointed hat, wicked grin. Do you stir spells, or only sweets?"]
SETTINGS = {"base": [], "slow": ["--length_scale", "1.3", "--noise_scale", "0.5", "--noise_w", "0.9"]}
ENV = {**os.environ, "LD_LIBRARY_PATH": str(PIPER.parent)}
out = Path(sys.argv[1])
out.mkdir(parents=True, exist_ok=True)
with open(out / "timings.jsonl", "w") as log:
    for v in VOICES:
        for name, extra in SETTINGS.items():
            for n, line in enumerate(LINES):
                wav = out / f"{v.stem}_{name}_{n}.wav"
                t0 = time.time()
                subprocess.run([str(PIPER), "-m", str(v), "-f", str(wav), *extra],
                               input=line, text=True, capture_output=True, check=True, env=ENV)
                took = time.time() - t0
                with wave.open(str(wav)) as w:
                    dur = w.getnframes() / w.getframerate()
                log.write(json.dumps({"voice": v.stem, "setting": name, "line": n,
                                      "render_s": round(took, 2), "audio_s": round(dur, 2)}) + "\n")
                log.flush()
