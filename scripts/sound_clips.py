"""Cut single clips from long CC0 effect files and level-match every sound.

usage: sound_clips.py SRC_DIR OUT_DIR [--rms 0.12]
Splits each file at quiet gaps (50 ms envelope, 20% of peak), keeps bursts of 0.4 s or more,
fades the edges, scales each clip to one RMS and checks the peak stays under 0.95.
Writes OUT_DIR/<name>_<n>.wav at 22050 Hz mono and prints start, length and peak.
"""
import sys
from pathlib import Path
import numpy as np, soundfile as sf
from scipy.signal import resample_poly

SR = 22050


def bursts(x, gap=0.25, thr=0.2, win=0.05):
    w = int(SR * win)
    env = np.sqrt(np.convolve(x ** 2, np.ones(w) / w, "same"))
    on = env > thr * env.max()
    out, start, last = [], None, 0
    for i in range(len(on)):
        if on[i]:
            if start is None: start = i
            last = i
        elif start is not None and i - last > gap * SR:
            out.append((start, last)); start = None
    if start is not None: out.append((start, last))
    return [(a, b) for a, b in out if b - a >= 0.4 * SR]


if __name__ == "__main__":
    src, out = Path(sys.argv[1]), Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
    rms = float(sys.argv[sys.argv.index("--rms") + 1]) if "--rms" in sys.argv else 0.12
    for f in sorted(src.iterdir()):
        try: x, sr = sf.read(f)
        except Exception as e: print("skip", f.name, e); continue
        x = resample_poly(x.mean(axis=1) if x.ndim > 1 else x, SR, sr)
        for n, (a, b) in enumerate(bursts(x) or [(0, len(x) - 1)]):
            c = x[max(0, a - int(.05 * SR)): b + int(.15 * SR)].copy()
            k = int(.03 * SR); c[:k] *= np.linspace(0, 1, k); c[-k:] *= np.linspace(1, 0, k)
            c *= rms / np.sqrt(np.mean(c ** 2))
            pk = np.abs(c).max()
            if pk > 0.95: c *= 0.95 / pk
            sf.write(out / f"{f.stem}_{n}.wav", c, SR, subtype="PCM_16")
            print(f"{f.stem}_{n}: from {a / SR:.1f}s, {len(c) / SR:.1f}s long, peak {np.abs(c).max():.2f}")
