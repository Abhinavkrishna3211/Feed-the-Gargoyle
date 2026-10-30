#!/usr/bin/env python3
"""Turn a plain Piper WAV into a gargoyle voice: bigger throat, sub layer, growl, grit, cave echo.

usage: gargoyle_fx.py IN.wav OUT.wav [--style imp|demon|ancient|ancient_clear|gargoyle|clear]
Needs numpy and scipy. Stages: resample down (pitch and formants fall, as for a bigger creature),
phase-vocoder time stretch to bring the speed back up, add an octave-down layer with a slow
growl wobble, soft clip for grit, then three delay taps for a stone-room echo.
"""
import argparse, wave
import numpy as np
from scipy.signal import stft, istft, fftconvolve, butter, sosfilt

STYLES = {  # pitch factor, final length vs the input, sub layer gain, growl depth, drive, echo gain
    "imp":   dict(pitch=0.86, length=1.10, sub=0.25, growl=0.15, drive=1.5, echo=1.0),
    "demon": dict(pitch=0.74, length=1.20, sub=0.45, growl=0.35, drive=2.5, echo=1.4),
    # ancient: deeper, two detuned doubles, breathy whisper, buzzy rasp, long cave reverb instead of taps
    "ancient": dict(pitch=0.64, length=1.30, sub=0.40, growl=0.30, drive=2.0, echo=0.0,
                    double=0.35, whisper=0.18, rasp=0.25, verb=0.35, verb_s=1.8),
    # ancient_clear: the ancient character with the clutter cut (less rasp, breath and reverb), consonants lifted
    "ancient_clear": dict(pitch=0.68, length=1.15, sub=0.30, growl=0.20, drive=1.6, echo=0.0,
                          double=0.18, whisper=0.05, rasp=0.08, verb=0.16, verb_s=0.9, presence=1.0),
    # gargoyle: lowest pitch that kept word error near 20% on whisper-base.en; sub, growl and a short cave add character at no cost
    "gargoyle": dict(pitch=0.76, length=1.15, sub=0.30, growl=0.25, drive=1.4, echo=0.0,
                     verb=0.20, verb_s=1.0, presence=0.8),
    # clear: words first. Mild pitch drop, no ring-mod, short quiet room, presence boost for consonants
    "clear": dict(pitch=0.82, length=1.12, sub=0.20, growl=0.15, drive=1.2, echo=0.0,
                  double=0.12, whisper=0.05, verb=0.14, verb_s=0.7, presence=0.8),
}


def read(p):
    with wave.open(p) as w:
        return np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float64) / 32768, w.getframerate()


def write(p, x, sr):
    with wave.open(p, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())


def resample(x, f):  # f < 1 lowers pitch and lengthens
    return np.interp(np.arange(0, len(x) - 1, f), np.arange(len(x)), x)


def stretch(x, rate, n=512, hop=128):  # n=512 scored clearer than 1024 or 2048 (voice_score.py)
    """Phase vocoder: rate > 1 plays faster, pitch unchanged."""
    _, _, Z = stft(x, nperseg=n, noverlap=n - hop, boundary=None)
    steps = np.arange(0, Z.shape[1] - 1, rate)
    omega = 2 * np.pi * hop * np.fft.rfftfreq(n) * 1.0
    phase = np.angle(Z[:, 0]); out = np.zeros((Z.shape[0], len(steps)), complex)
    for i, s in enumerate(steps):
        a, b = Z[:, int(s)], Z[:, int(s) + 1]
        out[:, i] = (1 - s % 1) * np.abs(a) + (s % 1) * np.abs(b)
        out[:, i] = out[:, i] * np.exp(1j * phase)
        d = np.angle(b) - np.angle(a) - omega
        phase = phase + omega + d - 2 * np.pi * np.round(d / (2 * np.pi))
    return istft(out, nperseg=n, noverlap=n - hop)[1]


def reverb(y, sr, wet, secs):  # cave reverb: decaying noise as the impulse response
    n = int(sr * secs); r = np.random.default_rng(1).standard_normal(n) * np.exp(-np.arange(n) / sr * 3.5)
    return y + wet * fftconvolve(y, r / np.sqrt(np.sum(r ** 2)))[: len(y)]


def fx(x, sr, style):
    s = STYLES[style]
    low = stretch(resample(x, s["pitch"]), 1 / s["pitch"] / s["length"])
    sub = stretch(resample(low, 0.5), 2.0)  # an octave down, same length as low
    sub = np.pad(sub, (0, max(0, len(low) - len(sub))))[: len(low)]
    t = np.arange(len(low)) / sr
    sub = sub * (1 - s["growl"] + s["growl"] * np.sin(2 * np.pi * 38 * t))
    y = low + s["sub"] * sub
    if s.get("double"):  # two copies a few percent off pitch, same length: a chorus of throats
        for f in (0.96, 1.04):
            d = stretch(resample(low, f), f)
            y = y + s["double"] * np.pad(d, (0, max(0, len(low) - len(d))))[: len(low)]
    if s.get("rasp"):  # ring-mod buzz at 70 Hz, mixed under the voice
        y = y * (1 - s["rasp"]) + s["rasp"] * y * np.sin(2 * np.pi * 70 * t)
    if s.get("whisper"):  # breath noise that follows the voice loudness
        env = sosfilt(butter(2, 20, fs=sr, output="sos"), np.abs(y))
        hiss = sosfilt(butter(2, [1500, 6000], "bandpass", fs=sr, output="sos"), np.random.default_rng(0).standard_normal(len(y)))
        y = y + s["whisper"] * hiss * env / (env.max() + 1e-9) * np.std(y) * 3
    if s.get("presence"):  # lift 2 to 4.5 kHz so consonants stay sharp under the low voice
        y = y + s["presence"] * sosfilt(butter(2, [2000, 4500], "bandpass", fs=sr, output="sos"), y)
    y = np.tanh(y * s["drive"]) / np.tanh(s["drive"])
    y = np.concatenate([y, np.zeros(int(sr * (s.get("verb_s", 0) + 0.7)))])
    if s.get("verb"):
        y = reverb(y, sr, s["verb"], s["verb_s"])
    out = y.copy()
    for d, g in (() if not s["echo"] else ((0.08, 0.30), (0.16, 0.22), (0.27, 0.14), (0.41, 0.08))):
        n = int(sr * d); out[n:] += s["echo"] * g * y[:-n]
    return out / np.max(np.abs(out)) * 0.9


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("inp"); ap.add_argument("out"); ap.add_argument("--style", default="imp", choices=STYLES)
    a = ap.parse_args()
    x, sr = read(a.inp)
    write(a.out, fx(x, sr, a.style), sr)
