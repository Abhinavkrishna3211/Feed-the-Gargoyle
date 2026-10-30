#!/usr/bin/env python3
"""Speak a line with sentence-by-sentence delivery in the gargoyle voice.

usage: gargoyle_speak.py OUT.wav "Sentence one. Sentence two? Sentence three!" [--voice en_GB-alan-medium]
Each sentence is rendered by Piper on the board (over SSH, helper in $GARGOYLE_SSH), then given its own
pace, pitch, pitch bend, loudness and pause by its ending: "!" quick and up, "?" slower and rising,
"." steady and falling, the last sentence slow with a long fall. The joined line gets one cave reverb.
"""
import argparse, os, re, shlex, subprocess
import numpy as np
import gargoyle_fx as g

SSH = os.environ.get("GARGOYLE_SSH", "b.sh")
PIPER = "LD_LIBRARY_PATH=~/piper/piper ~/piper/piper/piper"
SR = 22050  # medium voices
# ending: Piper length_scale, noise_scale, noise_w | fx pitch, pitch bend over the last 40% | gain | pause after (s)
MOODS = {"!": (1.03, 0.90, 1.0, 0.83, +0.06, 1.15, 0.30),  # clearer pass: +0.08 length, +0.04 pitch
         "?": (1.13, 0.80, 0.9, 0.84, +0.12, 1.00, 0.45),
         ".": (1.18, 0.60, 0.9, 0.79, -0.07, 0.95, 0.30)}
LAST = (0.12, 0.76, -0.10, 0.90)  # extra length_scale, pitch, bend, gain for the closing sentence


def sentences(text):
    return [s for s in re.findall(r"[^.!?]+[.!?]+", text.strip())] or [text.strip()]


def piper(text, voice, ls, ns, nw):
    cmd = f"echo {shlex.quote(text)} | {PIPER} -m ~/piper/voices/{voice}.onnx --output-raw " \
          f"--length_scale {ls} --noise_scale {ns} --noise_w {nw} 2>/dev/null"
    raw = subprocess.run(["sh", SSH, cmd], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float64) / 32768


def bend(y, amount):  # pitch glide over the last 40%: playback rate ramps 1 -> 1+amount
    rate = np.ones(len(y)); k = int(len(y) * 0.6); rate[k:] = np.linspace(1, 1 + amount, len(y) - k)
    return np.interp(np.cumsum(rate) - rate[0], np.arange(len(y)), y)[: int(len(y) / rate.mean())]


def speak(text, voice, care=0.0):  # care slows each sentence by that much and lifts pitch by half of it, for hard lines
    parts, ss = [], sentences(text)
    for i, s in enumerate(ss):
        ls, ns, nw, pitch, amt, gain, pause = MOODS.get(s[-1], MOODS["."])
        if i == len(ss) - 1 and i > 0:
            ls, pitch, amt, gain = ls + LAST[0], LAST[1], LAST[2], LAST[3]
        ls, pitch = ls + care, pitch + care / 2
        x = piper(s, voice, ls, ns, nw)
        g.STYLES["_s"] = {**g.STYLES["gargoyle"], "sub": 0.15, "presence": 1.2, "pitch": pitch, "verb": 0, "verb_s": 0}
        y = g.fx(x, SR, "_s")[: -int(SR * 0.7)]  # drop the silent tail fx appends
        y = bend(y[: np.nonzero(np.abs(y) > 0.01)[0][-1] + 1], amt) * gain
        parts += [y, np.zeros(int(SR * pause))]
    y = np.concatenate(parts[:-1])
    y = g.reverb(np.concatenate([y, np.zeros(SR)]), SR, 0.2, 1.0)
    return y / np.abs(y).max() * 0.9


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("out"); ap.add_argument("text"); ap.add_argument("--voice", default="en_GB-alan-medium")
    a = ap.parse_args()
    g.write(a.out, speak(a.text, a.voice), SR)
