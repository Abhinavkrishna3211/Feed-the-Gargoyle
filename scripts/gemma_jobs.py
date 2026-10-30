#!/usr/bin/env python3
"""Two narrow jobs for Gemma 3 1B on the board, each easy to check by machine.

usage: gemma_jobs.py OUT.jsonl LINES.json [--threads 3] [--seeds 3]
1. slot: given a costume, pick its prop from a closed list of 11. Run twice, with a GBNF grammar that
   allows only list words and without one. Scored against a fixed key.
2. variant: rewrite one hand-written bank line in different words. Scored by line_bank.verdict
   (length, characters, banned words, cue word where the category has one) plus: differs from the original.
   Passing is not proof of a good line, so the log keeps every text for a human read.
LINES.json maps category to a list of lines (notes/line-bank-all.json). Server flags as in line_bank.py.
"""
import argparse, json, random, sys, time, urllib.request

import line_bank as lb

KEY = {"witch": "broom", "ghost": "sheet", "skeleton": "bones", "zombie": "rags", "pirate": "cutlass",
       "princess": "crown", "spider-man": "web", "batman": "bat", "superman": "cape",
       "wonder-woman": "lasso", "captain-america": "shield"}
COSTUMES = {"witch", "ghost", "skeleton", "zombie", "pirate", "princess", "spider-man", "batman",
            "superman", "wonder-woman", "captain-america"}


def ask(prompt, seed, max_tokens, grammar=None):
    body = {"messages": [{"role": "user", "content": prompt}], "max_tokens": max_tokens,
            "temperature": 0.7, "seed": seed, "cache_prompt": True}
    if grammar:
        body["grammar"] = grammar
    t0 = time.time()
    d = json.load(urllib.request.urlopen(urllib.request.Request(
        f"http://127.0.0.1:{lb.PORT}/v1/chat/completions", json.dumps(body).encode(),
        {"Content-Type": "application/json"}), timeout=300))
    return d["choices"][0]["message"]["content"], round(time.time() - t0, 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out"); ap.add_argument("lines")
    ap.add_argument("--threads", type=int, default=3); ap.add_argument("--seeds", type=int, default=3)
    a = ap.parse_args()
    lines = json.load(open(a.lines))
    lb.sh("docker", "rm", "-f", lb.NAME)
    r = lb.sh("docker", "run", "-d", "--name", lb.NAME, "--memory", "2500m", "--memory-swap", "2500m",
              "-p", f"127.0.0.1:{lb.PORT}:{lb.PORT}", "-v", "/var/lib/arduino-app-cli/models/llamacpp/:/models/",
              "--entrypoint", "/opt/pkg-cpu/bin/llama-server", "-e", "LD_LIBRARY_PATH=/opt/pkg-cpu/lib",
              "-e", "OMP_WAIT_POLICY=passive", "-e", "GOMP_SPINCOUNT=0", lb.IMAGE,
              "--device", "none", "--host", "0.0.0.0", "--port", str(lb.PORT), "-m", lb.MODEL,
              "-t", str(a.threads), "-c", "2048", "-b", "512", "-ub", "128", "--cache-reuse", "256",
              "--flash-attn", "on", "--reasoning", "off")
    if r.returncode:
        sys.exit(r.stderr)
    for _ in range(120):
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{lb.PORT}/health", timeout=2).read()
            break
        except Exception:
            time.sleep(1)
    else:
        lb.sh("docker", "rm", "-f", lb.NAME)
        sys.exit("server never became healthy")
    props = sorted(KEY.values())
    grammar = "root ::= " + " | ".join(f'"{p}"' for p in props)
    seed = 0
    try:
        with open(a.out, "w") as f:
            def log(**row):
                f.write(json.dumps(row) + "\n"); f.flush()
            for run in range(a.seeds):  # slot: shuffle the list each run so position does not decide
                for costume, want in KEY.items():
                    order = random.Random(run * 100 + len(costume)).sample(props, len(props))
                    q = (f"A visitor wears a {costume} costume. Which one of these props belongs to that costume: "
                         f"{', '.join(order)}? Answer with that one word only.")
                    for mode in ("grammar", "free"):
                        seed += 1
                        text, wall = ask(q, seed, 6, grammar if mode == "grammar" else None)
                        got = text.strip().strip(".!\"' ").lower()
                        log(job="slot", mode=mode, costume=costume, want=want, got=got, ok=got == want,
                            in_list=got in props, wall_s=wall)
            seen = {l.lower() for v in lines.values() for l in v}
            for cat, ls in lines.items():  # variant: first two lines of every category, seeds variants each
                for orig in ls[:2]:
                    for _ in range(a.seeds):
                        seed += 1
                        q = ("Rewrite this line spoken by a sly stone gargoyle in different words. Keep the same meaning "
                             "and the same situation. Plain words, 12 words at most. Never use the words silence, shadow, "
                             f"dust or echo. Reply with only the new line.\nLine: {orig}")
                        text, wall = ask(q, seed, 40)
                        text = lb.clean(text)
                        v = lb.verdict(text, seen - {orig.lower()}, cat if cat in lb.CUES else None)
                        if v == "ok" and text.lower() == orig.lower():
                            v = "same_as_original"
                        log(job="variant", cat=cat, orig=orig, text=text, verdict=v, wall_s=wall)
    finally:
        lb.sh("docker", "rm", "-f", lb.NAME)


if __name__ == "__main__":
    main()
