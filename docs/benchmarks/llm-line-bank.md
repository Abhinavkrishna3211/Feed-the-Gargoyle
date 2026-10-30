# Gemma 3 1B writing gargoyle lines: three prompt designs

Date: 2026-10-30, about 12:45 to 14:00 UTC (board clock)
Board: Arduino UNO Q, 4 GB, Debian 13 image 20260528-558, arduino-app-cli 0.14.0, Ethernet. Nothing else running. Power: iPhone charger through the powered hub, rating not read.
Harness: `scripts/line_bank.py` (3 threads, `-c 2048`, `--cache-reuse 256`, `max_tokens` 30, one request per attempt, a new seed each time). The validator accepts a line only if it is plain ASCII text, 14 words or fewer, ends in `.`, `!` or `?`, contains no banned term (face, body, age and size words, riddle answers, filler such as silence and dust) and has no repeat, and contains one cue word for its situation (for example "wrong" or "not" for a wrong answer). Raw values: `raw/line-bank-{1,2,3}-2026-10-30.jsonl`.

## Result

| Batch | Prompt | Attempts | Accepted | Notes |
|---|---|---|---|---|
| 1 | Whole persona document as the prompt | 39 | 0 | Rescored with the final validator. Output was atmosphere, not the situation: "a silent plea", "dust motes dance". |
| 2 | Short prompt, 3 hand-written examples of the situation | 48 | 8 (17%) | 24 had no verdict cue, 9 failed on curly apostrophes, 7 used a riddle answer. |
| 3 | Same, plus a ban on filler words, curly apostrophes fixed, up to 8 tries per line | 86 | 22 (26%) | Only 1 of 5 wanted lines for two situations. |

Wall time per attempt (prompt cached after the first request in a situation): median 4.4 s, max 21.2 s.

## What the accepted lines look like

Some are fine ("Well done, a delightful treat awaits."). Many are not, even though they pass: "Right, right, another?" for a wrong sound, "Stuck! Wait, a chilling request.", lines starting with "- ". A cue-word check cannot tell a line that fits the situation from one that merely contains a cue word.

## Conclusion

- Gemma 3 1B at Q4_0 does not reliably write on-situation, in-character lines, even with examples. About 4 attempts are needed per accepted line, and the accepted lines still need a human read.
- The line bank therefore cannot be "the model writes the voice, a validator checks it". The workable design is hand-written lines as the core, with Gemma used for narrower jobs where a wrong output is easy to catch (picking a word for a slot in a template, proposing variants that a person approves).
- Not tested: a larger model, 4-bit variants other than Q4_0, other sampling settings, a grammar-constrained output, slot filling. Those are the next measurements.
