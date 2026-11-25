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
MOODS = {"!": (1.07, 0.90, 1.0, 0.89, +0.06, 1.15, 0.55),  # clearer pass 2: +0.04 length, +0.06 pitch
         "?": (1.17, 0.80, 0.9, 0.90, +0.12, 1.00, 0.75),
         ".": (1.22, 0.60, 0.9, 0.85, -0.07, 0.95, 0.65)}
LAST = (0.12, 0.82, -0.10, 0.90)  # extra length_scale, pitch, bend, gain for the closing sentence
LOUD = 2.5  # limiter drive; 5.0 was louder but blurred words. Clearer pass 2 (with the pitch, WET, SUB and PRES changes) scored 0.94 Whisper base.en word accuracy against 0.91 on five lines (render-v3 A/B)
WET = 0.1  # cave reverb level
SUB, PRES = 0.08, 1.6  # fx octave-down layer and consonant presence per sentence
TRAIL = 0.5  # extra pause after a sentence that trails off with "...", the dramatic beat


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
        x = piper(s.strip(), voice, ls, ns, nw)
        g.STYLES["_s"] = {**g.STYLES["gargoyle"], "sub": SUB, "presence": PRES, "pitch": pitch, "verb": 0, "verb_s": 0}
        y = g.fx(x, SR, "_s")[: -int(SR * 0.7)]  # drop the silent tail fx appends
        y = bend(y[: np.nonzero(np.abs(y) > 0.01)[0][-1] + 1], amt) * gain
        parts += [y, np.zeros(int(SR * (pause + TRAIL * s.endswith("..."))))]
    y = np.concatenate(parts[:-1])
    y = g.reverb(np.concatenate([y, np.zeros(SR)]), SR, WET, 1.0)
    return np.tanh(LOUD * y / np.abs(y).max()) / np.tanh(LOUD) * 0.9  # soft limiter: about 7 dB louder at the same peak, the small speaker needs it


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("out"); ap.add_argument("text"); ap.add_argument("--voice", default="en_GB-alan-medium")
    a = ap.parse_args()
    g.write(a.out, speak(a.text, a.voice), SR)
