#!/usr/bin/env python3
"""Time from starting playback to the sound reaching the USB mic. Run on the board, speakers and mic on the sound card (card 1).
usage: python3 play_latency.py   (set the Speaker mixer first). Prints one JSON line of ms values for spawn and open-stream playback."""
import array, json, math, subprocess, sys, threading, time, wave
R = 48000
def tone(ms=300):
    n = R * ms // 1000
    a = array.array("h")
    for i in range(n):
        v = int(20000 * math.sin(2 * math.pi * 1000 * i / R))
        a.extend((v, v))
    return a.tobytes()
BEEP = tone()
with wave.open("/tmp/beep.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(R); w.writeframes(BEEP)

rec = subprocess.Popen(["arecord", "-q", "-D", "plughw:1,0", "-f", "S16_LE", "-r", str(R), "-c", "1", "-t", "raw"],
                       stdout=subprocess.PIPE, bufsize=0)
chunks = []  # (arrival time, peak)
def reader():
    while True:
        b = rec.stdout.read(960)  # 10 ms
        if not b:
            return
        a = array.array("h", b)
        chunks.append((time.time(), max(abs(x) for x in a)))
threading.Thread(target=reader, daemon=True).start()
time.sleep(1.5)
noise = max(p for _, p in chunks)
thr = max(2000, noise * 4)

def onset(t0):
    for t, p in chunks:
        if t >= t0 and p > thr:
            return round((t - t0) * 1000)

res = {"noise_peak": noise, "thr": thr, "spawn": [], "stream": []}
for _ in range(5):
    t0 = time.time()
    subprocess.Popen(["aplay", "-q", "-D", "plughw:1,0", "/tmp/beep.wav"])
    time.sleep(1.5)
    res["spawn"].append(onset(t0))
# open stream fed with silence, swap in the beep on demand
ap = subprocess.Popen(["aplay", "-q", "-D", "plughw:1,0", "-t", "raw", "-f", "S16_LE", "-r", str(R), "-c", "2",
                       "--buffer-time=40000"], stdin=subprocess.PIPE, bufsize=0)
import fcntl
fcntl.fcntl(ap.stdin.fileno(), 1031, 4096)  # shrink the pipe so silence does not queue ahead of the beep
SIL = bytes(R * 4 // 100)  # 10 ms
pending = []
def feeder():
    while True:
        if pending:
            ap.stdin.write(pending.pop(0))
        else:
            ap.stdin.write(SIL)
threading.Thread(target=feeder, daemon=True).start()
time.sleep(1.5)
for _ in range(5):
    t0 = time.time()
    pending.append(BEEP)
    time.sleep(1.5)
    res["stream"].append(onset(t0))
print(json.dumps(res))
rec.kill(); ap.kill()
