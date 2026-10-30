"""Render every line of a line-bank JSON in the gargoyle voice.

usage: render_bank.py BANK.json OUTDIR     (set GARGOYLE_SSH as for gargoyle_speak.py)
Writes OUTDIR/<category>_<n>.wav and OUTDIR/index.jsonl (category, n, text). Skips files that exist,
so an interrupted run can be restarted.
"""
import json, sys
from pathlib import Path
import gargoyle_fx as g, gargoyle_speak as sp

bank, out = json.load(open(sys.argv[1], encoding="utf-8")), Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)
with open(out / "index.jsonl", "a", encoding="utf-8") as idx:
    for cat, lines in bank.items():
        for n, line in enumerate(lines):
            text = line if isinstance(line, str) else line["text"]
            f = out / f"{cat}_{n}.wav"
            if f.exists():
                continue
            g.write(str(f), sp.speak(text, "en_GB-alan-medium"), sp.SR)
            idx.write(json.dumps({"category": cat, "n": n, "text": text}) + "\n"); idx.flush()
            print(f.name, flush=True)
