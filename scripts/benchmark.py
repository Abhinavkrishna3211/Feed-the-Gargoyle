#!/usr/bin/env python3
"""System sampler for the UNO Q (Linux only, stdlib only). Run it on the board.

  benchmark.py sample out.jsonl [--interval 5] [--duration 0]   one JSON line per sample
  benchmark.py summary out.jsonl                                 markdown table, reset count
  benchmark.py selftest

A reset shows up as a new boot_id between two lines. NUL bytes at the end of the
file also mean the board lost power mid-write. Bridge latency is logged by the app
(see app/python/main.py, bench.on); model timings are logged by the model runners.
"""
import glob
import json
import os
import statistics
import sys
import time


def read(path):
    with open(path) as f:
        return f.read()


def cpu_times():
    v = [int(x) for x in read("/proc/stat").split("\n")[0].split()[1:9]]
    return sum(v), v[3] + v[4]  # total, idle + iowait


def temp_max_c():
    ts = [int(read(z)) for z in glob.glob("/sys/class/thermal/thermal_zone*/temp")]
    return max(ts) / 1000 if ts else None


def meminfo():
    return {k: int(v.split()[0]) for k, v in (l.split(":") for l in read("/proc/meminfo").splitlines())}


def sample(out, interval, duration):
    t0, (tot, idle) = time.monotonic(), cpu_times()
    boot_id = read("/proc/sys/kernel/random/boot_id").strip()
    with open(out, "a") as f:
        while True:
            time.sleep(interval)
            tot2, idle2 = cpu_times()
            m = meminfo()
            row = {
                "wall": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "t": round(time.monotonic() - t0, 1),
                "uptime": float(read("/proc/uptime").split()[0]),
                "boot_id": boot_id,
                "cpu_busy_pct": round(100 * (1 - (idle2 - idle) / max(tot2 - tot, 1)), 2),
                "mem_avail_kb": m["MemAvailable"],
                "swap_used_kb": m["SwapTotal"] - m["SwapFree"],
                "temp_max_c": temp_max_c(),
                "load1": float(read("/proc/loadavg").split()[0]),
            }
            tot, idle = tot2, idle2
            f.write(json.dumps(row) + "\n")
            f.flush()
            os.fsync(f.fileno())
            if duration and row["t"] >= duration:
                return


def summarize(rows):
    resets = sum(1 for a, b in zip(rows, rows[1:]) if a["boot_id"] != b["boot_id"] or b["uptime"] < a["uptime"])
    def col(k, unit):
        xs = [r[k] for r in rows if r[k] is not None]
        return f"| {k} | {min(xs):g} | {statistics.median(xs):g} | {max(xs):g} | {unit} |"
    lines = [
        f"Samples: {len(rows)}, span {rows[-1]['t'] - rows[0]['t']:.0f} s, resets: {resets}",
        "",
        "| Metric | Min | Median | Max | Unit |",
        "|---|---|---|---|---|",
        col("cpu_busy_pct", "%"), col("mem_avail_kb", "kB"), col("swap_used_kb", "kB"),
        col("temp_max_c", "C"), col("load1", ""),
    ]
    return "\n".join(lines), resets


def load(path):
    with open(path, "rb") as f:
        raw = f.read()
    if raw.rstrip(b"\n").endswith(b"\x00") or b"\x00" in raw:
        print("NUL bytes in file: the board lost power during a write", file=sys.stderr)
    return [json.loads(l) for l in raw.replace(b"\x00", b"").decode().splitlines() if l.strip().startswith("{")]


def selftest():
    base = dict(wall="", cpu_busy_pct=1, mem_avail_kb=100, swap_used_kb=0, temp_max_c=40.0, load1=0.1)
    rows = [dict(base, t=0, uptime=10, boot_id="a"), dict(base, t=5, uptime=15, boot_id="a"),
            dict(base, t=10, uptime=3, boot_id="b")]
    assert summarize(rows)[1] == 1
    assert summarize(rows[:2])[1] == 0
    print("ok")


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["sample"]:
        opt = lambda n, d: float(a[a.index(n) + 1]) if n in a else d
        sample(a[1], opt("--interval", 5), opt("--duration", 0))
    elif a[:1] == ["summary"]:
        print(summarize(load(a[1]))[0])
    elif a[:1] == ["selftest"]:
        selftest()
    else:
        sys.exit(__doc__)
