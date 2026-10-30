"""Score how well a speech recogniser reads voice samples: word accuracy against the known line.

usage: voice_score.py DIR [DIR ...]   (files named <voice>_<style>_<line>.wav, lines 0 to 3 as in voice_test.py)
Needs transformers, torch, scipy and the openai/whisper-base.en weights. Run on the PC.
"""
import re, sys, wave
from collections import defaultdict
from pathlib import Path
import numpy as np
from scipy.signal import resample_poly
from transformers import pipeline

LINES = ["You solved my stone-cold puzzle. Hold out your hand, clever one.",
         "Wrong answer! The stone shakes its head. Try again.",
         "Who knocks at my stone door? Speak, sweet seeker.",
         "Pointed hat, wicked grin. Do you stir spells, or only sweets?"]
words = lambda t: re.findall(r"[a-z']+", t.lower().replace("-", " "))


def wer(ref, hyp):  # word error rate by edit distance
    d = list(range(len(hyp) + 1))
    for i, r in enumerate(ref, 1):
        prev, d[0] = d[0], i
        for j, h in enumerate(hyp, 1):
            prev, d[j] = d[j], min(d[j] + 1, d[j - 1] + 1, prev + (r != h))
    return d[-1] / len(ref)


asr = pipeline("automatic-speech-recognition", model="openai/whisper-base.en", device=-1)
res = defaultdict(list)
for f in sorted(p for d in sys.argv[1:] for p in Path(d).glob("*.wav")):
    with wave.open(str(f)) as w:
        x = np.frombuffer(w.readframes(w.getnframes()), np.int16) / 32768
        x = resample_poly(x, 16000, w.getframerate()).astype(np.float32)
    hyp = asr({"raw": x, "sampling_rate": 16000})["text"]
    ref = LINES[int(f.stem.rsplit("_", 1)[1])]
    e = wer(words(ref), words(hyp))
    res[f.parent.name + "/" + f.stem.rsplit("_", 1)[0].split("_", 1)[1]].append(e)
    print(f"{e:4.0%} {f.name}: {hyp.strip()}")
print()
for k, v in sorted(res.items(), key=lambda kv: np.mean(kv[1])):
    print(f"{np.mean(v):5.0%} word error  {k}")
