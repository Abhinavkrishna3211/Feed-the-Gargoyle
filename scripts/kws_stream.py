"""Stream replay: test clips joined in a fixed random order, 1000 ms window every 100 ms through the .eim.
usage: kws_stream.py <model.eim> <testing dir>   -> per-window scores in stream.csv, summary on stdout"""
import array, json, os, pathlib, random, socket, subprocess, sys, tempfile, time, wave
model, root = sys.argv[1], pathlib.Path(sys.argv[2])
KW = ["candle", "mirror", "pumpkin", "scarecrow", "shadow", "spider"]
files = sorted(root.glob("*/*.wav")); random.Random(7).shuffle(files)
x, spans = array.array("h"), []
for f in files:
    w = wave.open(str(f)); a = array.array("h", w.readframes(w.getnframes()))[:16000]
    a.extend([0] * (16000 - len(a))); spans.append((len(x), f.parent.name)); x.extend(a)
sock = os.path.join(tempfile.mkdtemp(), "r.sock"); proc = subprocess.Popen([model, sock], stdout=subprocess.DEVNULL)
while not os.path.exists(sock): time.sleep(0.05)
c = socket.socket(socket.AF_UNIX); c.connect(sock); ix = 0
def send(m):
    global ix
    ix += 1; m["id"] = ix; c.sendall(json.dumps(m).encode()); d = b""
    while not d.endswith(b"\x00"): d += c.recv(65536)
    return json.loads(d[:-1].decode()[d.index(b"{"):])
send({"hello": 1})
wins = []  # (start sample, top keyword or None)
fh = open("stream.csv", "w"); fh.write("start_s,label_here," + ",".join(KW) + "\n")
for s0 in range(0, len(x) - 16000 + 1, 1600):
    sc = send({"classify": x[s0:s0 + 16000].tolist()})["result"]["classification"]
    top = max(KW, key=lambda k: sc[k]); wins.append((s0, top if sc[top] >= 0.5 else None))
    fh.write(f"{s0/16000:.1f},{spans[s0//16000][1]}," + ",".join(f"{sc[k]:.3f}" for k in KW) + "\n")
proc.terminate(); hours = len(x) / 16000 / 3600
def score(fires):  # fires: list of (start sample, keyword) per window, None for no fire
    caught = sum(1 for a, lab in spans if lab in KW and any(k == lab and abs(s - a) <= 8000 for s, k in fires if k))
    fa, prev = 0, None
    for s, k in fires:  # one false alarm per run of firing windows not matching an overlapping clip of that word
        ok = k and any(lab == k and abs(s - a) <= 8000 for a, lab in spans[max(0, s//16000-1): s//16000+2])
        bad = k if (k and not ok) else None
        if bad and bad != prev: fa += 1
        prev = bad
    return caught, fa
n = sum(1 for _, l in spans if l in KW)
c1, f1 = score(wins)
vote = [(s, wins[i][1] if wins[i][1] and sum(1 for j in range(max(0, i-3), i+1) if wins[j][1] == wins[i][1]) >= 3 else None) for i, (s, _) in enumerate(wins)]
c3, f3 = score(vote)
print(f"clips {len(spans)} answers {n} stream {len(x)/16000:.0f} s windows {len(wins)}")
print(f"single window: caught {c1}/{n} = {100*c1/n:.1f} %, false alarms {f1} = {f1/hours:.0f} per hour")
print(f"3 of 4 vote:   caught {c3}/{n} = {100*c3/n:.1f} %, false alarms {f3} = {f3/hours:.0f} per hour")
