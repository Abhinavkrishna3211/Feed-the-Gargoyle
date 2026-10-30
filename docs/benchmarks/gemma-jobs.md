# Gemma 3 1B on two narrow jobs: slot filling and line variants

Date: 2026-10-31
Board: Arduino UNO Q, 4 GB, same image and server setup as `llm-line-bank.md`, Ethernet, nothing else running. Versions were not re-read for this run.
Command: `python3 gemma_jobs.py jobs.jsonl line-bank-all.json` (`scripts/gemma_jobs.py`; llama-server at 3 threads, `-c 2048`, `--cache-reuse 256`, Q4_0, temperature 0.7, a new seed per request). Raw log: `raw/gemma-jobs-2026-10-31.jsonl`, 198 requests.

## Job 1: pick the prop for a costume from a closed list of 11

Three runs per costume with the list shuffled each run, once with a GBNF grammar that allows only list words, once without. Scored against a fixed key (witch broom, ghost sheet, and so on). Chance is 1 in 11, about 9%.

| Mode | Correct | In the list | Mean wall time per request |
|---|---|---|---|
| Grammar | 11 of 33 (33%) | 33 of 33 | 7.8 s |
| No grammar | 9 of 33 (27%) | 30 of 33 | 1.2 s |

Correct answers came only for batman, princess, skeleton, spider-man and superman. Witch, ghost, zombie, pirate and captain-america scored 0 in both modes. The grammar guarantees a word from the list, not the right word, and it cost about six times the time per request here (the grammar run uses the same server, so this is the cost of constrained decoding on this board, one measurement).

Conclusion: not usable. The costume to prop mapping stays a fixed table in code.

## Job 2: rewrite a hand-written line in different words

The first two lines of each of the 22 categories, 3 seeds each, 132 rewrites, mean 6.1 s per request. The line validator (length, characters, banned words, verdict cue where the category has one) plus "differs from the original".

| Result | Count |
|---|---|
| Accepted | 83 |
| No verdict cue (win, fail and similar categories) | 34 |
| Bad characters | 7 |
| Banned word (plea 4, face 2, fright 1, little 1) | 8 |

Categories with a required cue (greet, win, wrong_answer, too_quiet, wrong_sound, timeout, goodbye, jam): 7 of 48 accepted. Costume and announce categories: 76 of 84 accepted, but the validator only checks form there. Reading them, many accepted lines lost the situation ("Stone eyes observe, a cold, watchful gaze." for the witch line) or changed it. A passing validator does not mean the line is good.

Conclusion: not usable unreviewed, and no live use. At most a drafting aid with a human choosing from the output, which the hand-written bank already covers.

## Limits
One model, one prompt per job, one run of three seeds. A larger model or a different prompt was not tried.
