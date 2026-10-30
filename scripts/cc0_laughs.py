"""Turn CC0 laugh recordings into gargoyle laughs: lower, bigger, stone-room reverb.

usage: cc0_laughs.py SRC_DIR OUT_DIR     (SRC_DIR holds .ogg .flac .mp3 files, read as audio data only)
Writes OUT_DIR/<name>_raw.wav (resampled, level-matched) and <name>_gargoyle.wav.
"""
import sys
from pathlib import Path
import numpy as np, soundfile as sf
from scipy.signal import resample_poly
import gargoyle_fx as g

SR = 22050
g.STYLES["laugh"] = dict(pitch=0.80, length=1.0, sub=0.30, growl=0.25, drive=1.6, echo=0.0, verb=0.30, verb_s=1.5, presence=0.4)
src, out = Path(sys.argv[1]), Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
for f in sorted(src.iterdir()):
    try:
        x, sr = sf.read(f)
    except Exception as e:
        print("skip", f.name, e); continue
    x = x.mean(axis=1) if x.ndim > 1 else x
    x = resample_poly(x, SR, sr); x = x / np.abs(x).max() * 0.9
    g.write(str(out / f"{f.stem}_raw.wav"), x, SR)
    g.write(str(out / f"{f.stem}_gargoyle.wav"), g.fx(x, SR, "laugh"), SR)
    print(f.name, f"{len(x) / SR:.1f}s")
