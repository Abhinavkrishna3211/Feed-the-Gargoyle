#!/usr/bin/env python3
"""Run llama-server in the brick's image at one thread count and time short generations.

usage: llm_bench.py THREADS OUT.jsonl [--ctx 2048] [--runs 5] [--max-tokens 40] [--flash on|off] [--cache] [--prefix N]
Writes one JSON line per request plus a final SUMMARY line. Stops the container on exit.
"""
import argparse, json, subprocess, sys, time, urllib.request

IMAGE = "ghcr.io/arduino/app-bricks/llamacpp-runner:0.13.0"
MODEL = "/models/unsloth/gemma-3-1b-it-GGUF/gemma-3-1b-it-Q4_0.gguf"
NAME = "gbench"
PORT = 9999
RULES = "Rules: keep it short, playful and spooky, never mention faces or bodies. "
PROMPT = ("You are a stone gargoyle guarding a bowl of sweets. A visitor just answered your riddle "
          "correctly. Say one short, spooky, playful line to them.")

ap = argparse.ArgumentParser()
ap.add_argument("threads", type=int)
ap.add_argument("out")
ap.add_argument("--ctx", type=int, default=2048)
ap.add_argument("--runs", type=int, default=5)
ap.add_argument("--max-tokens", type=int, default=40)
ap.add_argument("--flash", default="on", choices=["on", "off"])
ap.add_argument("--cache", action="store_true", help="send cache_prompt true")
ap.add_argument("--prefix", type=int, default=0, help="repeat a fixed rules sentence N times before the prompt")
a = ap.parse_args()


def sh(*cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def stop():
    sh("docker", "rm", "-f", NAME)


stop()
t_start = time.time()
r = sh("docker", "run", "-d", "--name", NAME, "--memory", "2500m", "--memory-swap", "2500m",
       "-p", f"127.0.0.1:{PORT}:{PORT}", "-v", "/var/lib/arduino-app-cli/models/llamacpp/:/models/",
       "--entrypoint", "/opt/pkg-cpu/bin/llama-server", "-e", "LD_LIBRARY_PATH=/opt/pkg-cpu/lib",
       "-e", "OMP_WAIT_POLICY=passive", "-e", "GOMP_SPINCOUNT=0", IMAGE,
       "--device", "none", "--host", "0.0.0.0", "--port", str(PORT), "-m", MODEL,
       "-t", str(a.threads), "-c", str(a.ctx), "-b", "512", "-ub", "128",
       "--cache-reuse", "256", "--flash-attn", a.flash, "--reasoning", "off")
if r.returncode:
    sys.exit("docker run failed: " + r.stderr)

ready = None
for _ in range(120):
    try:
        urllib.request.urlopen(f"http://127.0.0.1:{PORT}/health", timeout=2).read()
        ready = time.time() - t_start
        break
    except Exception:
        time.sleep(1)
if ready is None:
    print(sh("docker", "logs", "--tail", "30", NAME).stdout, sh("docker", "logs", "--tail", "30", NAME).stderr)
    stop()
    sys.exit("server never became healthy")

rows = []
with open(a.out, "w") as f:
    f.write(json.dumps({"event": "ready", "threads": a.threads, "ctx": a.ctx, "ready_s": round(ready, 2)}) + "\n")
    for i in range(a.runs):
        body = json.dumps({"messages": [{"role": "user", "content": RULES * a.prefix + PROMPT}], "max_tokens": a.max_tokens,
                           "temperature": 0.7, "seed": i, "cache_prompt": a.cache}).encode()
        req = urllib.request.Request(f"http://127.0.0.1:{PORT}/v1/chat/completions", body,
                                     {"Content-Type": "application/json"})
        t0 = time.time()
        d = json.load(urllib.request.urlopen(req, timeout=180))
        wall = (time.time() - t0) * 1000
        tm = d.get("timings", {})
        row = {"run": i, "threads": a.threads, "wall_ms": round(wall), "prompt_n": tm.get("prompt_n"),
               "prompt_ms": tm.get("prompt_ms"), "predicted_n": tm.get("predicted_n"),
               "predicted_per_second": tm.get("predicted_per_second"),
               "text": d["choices"][0]["message"]["content"]}
        rows.append(row)
        f.write(json.dumps(row) + "\n")
        f.flush()
    first = rows[1:] or rows  # run 0 warms caches; summary uses the rest
    tps = sorted(r["predicted_per_second"] for r in first)
    pm = sorted(r["prompt_ms"] for r in first)
    summ = {"event": "SUMMARY", "threads": a.threads, "ctx": a.ctx, "n": len(first),
            "tok_per_s_median": tps[len(tps) // 2], "prompt_ms_median": pm[len(pm) // 2],
            "wall_ms_max": max(r["wall_ms"] for r in first)}
    f.write(json.dumps(summ) + "\n")
    print(json.dumps(summ))
stop()
