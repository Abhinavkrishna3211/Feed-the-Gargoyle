#!/usr/bin/env python3
"""Generate gargoyle lines with Gemma 3 1B on the board, validate them, write a JSONL bank.

usage: line_bank.py OUT.jsonl [--per 5] [--threads 3] [--tries 4] [--cats greet,win,...]
Runs llama-server in the LLM brick's image (same flags as llm_bench.py). The persona and rules
form a fixed prefix so --cache-reuse can skip it after the first request. Every attempt is logged
with its verdict, so the pass rate and retries per accepted line can be read from the file.
Examples per situation are hand-written in EX; the validator carries the persona rules.
"""
import argparse, json, re, subprocess, sys, time, urllib.request

IMAGE = "ghcr.io/arduino/app-bricks/llamacpp-runner:0.13.0"
MODEL = "/models/unsloth/gemma-3-1b-it-GGUF/gemma-3-1b-it-Q4_0.gguf"
NAME, PORT = "gbank", 9998
CATS = {
    "greet": "a visitor has just walked up; invite them to take part",
    "win": "the visitor answered the riddle correctly; a sweet is coming",
    "wrong_answer": "the visitor gave the wrong riddle answer; no sweet yet",
    "too_quiet": "the visitor's sound was too quiet; ask for louder",
    "wrong_sound": "the visitor made the wrong sound; ask for another",
    "timeout": "the visitor took too long; the chance has passed",
    "goodbye": "the visitor is leaving; send them off",
    "jam": "the gargoyle's jaw is stuck for a moment; ask them to wait",
}
EX = {  # hand-written examples shown to the model; the persona rules live in the validator
    "greet": ["Who comes knocking at a hungry stone's door? Speak, sweet seeker.",
              "Step closer, traveller. I have a riddle and a very empty stomach.",
              "Ah, a visitor! Who dares answer my riddle?"],
    "win": ["You solved my stone-cold puzzle. Hold out your hand, clever one.",
            "Correct! My jaw opens for you. Take your sweet.",
            "Right answer. Even gargoyles keep their promises."],
    "wrong_answer": ["Close, but my riddle bites back. Not that one, not today.",
                     "Wrong answer! The stone shakes its head. Try again.",
                     "No, no, no. My riddle laughs at that guess."],
    "too_quiet": ["Louder! A mouse sat in your voice and kept it tiny.",
                  "Too quiet! Stone ears need a bigger noise.",
                  "I heard nothing. Louder, and make the walls shiver."],
    "wrong_sound": ["That noise is not the key. Try another to open my jaw.",
                    "Wrong sound! My ears wanted something different.",
                    "Not that one. Give me another noise."],
    "timeout": ["Time crept past you like a cat. The chance has gone.",
                "Too slow! The sweets are waiting for the next brave voice.",
                "The moment passed, and so did your turn."],
    "goodbye": ["Walk on, wanderer. My stone eyes will wait for the next knock.",
                "Farewell! Come back when the night is darker.",
                "Goodnight, and mind the cracks in the pavement."],
    "jam": ["My jaw jammed on its own joke. One moment, patient one.",
            "Stuck! Wait while I wiggle my stone teeth.",
            "Hold on, my jaw needs a moment to behave."],
}
BANNED = ("little friend face faces body bodies fat thin tall old young child children kid kids boy girl "
          "ugly pretty beautiful handsome skin hair age aged size big small baby shadow pumpkin mirror "
          "candle spider scarecrow silence silent dust echo echoes plea fright frightful foolish fool stupid").split()
BAN_RE = re.compile(r"\b(" + "|".join(BANNED) + r")(s|es|ed|er|est)?\b", re.I)  # plurals and endings too
CUES = {  # the verdict must be clear: each category needs one of these words
    "greet": "who knocks come speak hungry riddle welcome step approach",
    "win": "sweet treat take earned solved correct right hand open yes reward",
    "wrong_answer": "wrong not no nope close nay miss",
    "too_quiet": "louder loud quiet whisper mouse hear speak",
    "wrong_sound": "wrong not another different again",
    "timeout": "time late gone passed slow waited too",
    "goodbye": "walk go farewell goodnight return leave night again",
    "jam": "moment wait stuck jam patient hold",
}


def clean(raw):
    """Gemma often adds a lead-in line and curly quotes; keep the last non-empty line, unquoted."""
    lines = [l.strip() for l in raw.splitlines() if l.strip()]
    return lines[-1].replace(chr(0x2019), chr(39)).strip("\"'\u201c\u201d\u2018\u2019 ") if lines else ""


def verdict(text, seen, cat=None):
    if not text or "\n" in text:
        return "empty_or_multiline"
    if not re.fullmatch(r"[A-Za-z' ,.!?;:-]+", text):
        return "bad_chars"  # no digits, emoji, quotes or long dashes
    if len(text.split()) > 14:
        return "too_long"
    if not text[-1] in ".!?":
        return "no_end"
    m = BAN_RE.search(text)
    if m:
        return "banned:" + m.group(1).lower()
    if text.lower() in seen:
        return "duplicate"
    if cat and not set(re.findall(r"[a-z]+", text.lower())) & set(CUES[cat].split()):
        return "no_verdict_cue"
    return "ok"


def prompt(cat):
    shots = "\n".join("- " + e for e in EX[cat])
    return ("You write one short line of speech for a sly stone gargoyle at a Halloween sweet stand. "
            "Plain words, playful, a little spooky, 12 words at most. Never use the words silence, shadow, dust or echo. Say the outcome in the first words.\n"
            f"Situation: {CATS[cat]}.\nExamples:\n{shots}\n"
            "Write one NEW line like these, in different words. Reply with only the line.")


def sh(*c):
    return subprocess.run(c, capture_output=True, text=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--per", type=int, default=5)
    ap.add_argument("--threads", type=int, default=3)
    ap.add_argument("--tries", type=int, default=4)
    ap.add_argument("--cats", default=",".join(CATS))
    a = ap.parse_args()
    sh("docker", "rm", "-f", NAME)
    r = sh("docker", "run", "-d", "--name", NAME, "--memory", "2500m", "--memory-swap", "2500m",
           "-p", f"127.0.0.1:{PORT}:{PORT}", "-v", "/var/lib/arduino-app-cli/models/llamacpp/:/models/",
           "--entrypoint", "/opt/pkg-cpu/bin/llama-server", "-e", "LD_LIBRARY_PATH=/opt/pkg-cpu/lib",
           "-e", "OMP_WAIT_POLICY=passive", "-e", "GOMP_SPINCOUNT=0", IMAGE,
           "--device", "none", "--host", "0.0.0.0", "--port", str(PORT), "-m", MODEL,
           "-t", str(a.threads), "-c", "2048", "-b", "512", "-ub", "128", "--cache-reuse", "256",
           "--flash-attn", "on", "--reasoning", "off")
    if r.returncode:
        sys.exit(r.stderr)
    for _ in range(120):
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{PORT}/health", timeout=2).read()
            break
        except Exception:
            time.sleep(1)
    else:
        sh("docker", "rm", "-f", NAME)
        sys.exit("server never became healthy")
    seen, seed = {e.lower() for v in EX.values() for e in v}, 0
    try:
        with open(a.out, "w") as f:
            for cat in a.cats.split(","):
                got = 0
                while got < a.per:
                    for _ in range(a.tries):
                        seed += 1
                        body = json.dumps({"messages": [{"role": "user", "content": prompt(cat)}],
                            "max_tokens": 30, "temperature": 0.7, "seed": seed, "cache_prompt": True}).encode()
                        t0 = time.time()
                        d = json.load(urllib.request.urlopen(urllib.request.Request(
                            f"http://127.0.0.1:{PORT}/v1/chat/completions", body,
                            {"Content-Type": "application/json"}), timeout=300))
                        text = clean(d["choices"][0]["message"]["content"])
                        v = verdict(text, seen, cat)
                        f.write(json.dumps({"cat": cat, "seed": seed, "text": text, "verdict": v,
                                            "wall_s": round(time.time() - t0, 1)}) + "\n")
                        f.flush()
                        if v == "ok":
                            seen.add(text.lower())
                            got += 1
                            break
                    else:
                        break  # tries used up for this slot: stop this category, the log shows why
    finally:
        sh("docker", "rm", "-f", NAME)


if __name__ == "__main__":
    main()
