# Gemma 3 1B probes: flash attention and prompt caching

Date: 2026-10-30, about 05:50 to 06:05 UTC (board clock)
Board: Arduino UNO Q, 4 GB, Debian 13 image 20260528-558, arduino-app-cli 0.14.0, Ethernet. Nothing else running (the cascade app had been stopped). Power: iPhone charger through the powered hub, rating not read.
Harness: `scripts/llm_bench.py` at 3 threads, `-c 2048 -b 512 -ub 128 --cache-reuse 256`, `max_tokens` 40, 6 requests per set, run 0 dropped for medians. New flags `--flash`, `--cache` and `--prefix` were added for these runs. `--prefix 8` puts a fixed 8-sentence rules block before the prompt (168 prompt tokens in total). Raw values: `raw/llm-probe-*-2026-10-30.jsonl`.

## Result

| Set | Prompt tokens evaluated | Prompt time (ms) | Generation (tok/s) | Wall per reply (ms) |
|---|---|---|---|---|
| Flash attention on, 40-token prompt (n = 5) | 40 | 5,145 median | 4.32 | 7,944 median |
| Flash attention off, 40-token prompt (n = 5) | 40 | 5,266 median | 4.26 | 7,634 median |
| 168-token prompt, `cache_prompt` false (n = 6) | 168 | 21,404 to 21,648 | 4.2 | 22,848 to 24,809 |
| Same prompt, `cache_prompt` true | 168 first, then 5 | 21,538 first, then 787 to 807 | 4.2 to 4.3 | 23,681 first, then 2,206 to 4,354 |

## What it says

- Prompt processing runs at about 7.8 tokens per second at 3 threads on this board (40 tokens in 5.1 s, 168 in 21.5 s), the same rate at both lengths. Turning flash attention off changed nothing (5.3 s against 5.1 s), so attention is not the cause. This is slow against generation at 4.3 tok/s, but it is steady, so it is probably the speed of these cores on this model, not a fault. Batch size, `-ub` and thread count for prompt processing were not varied, so that stays unexplained.
- Prompt caching works with this server. After the first request a repeated prompt evaluated 5 new tokens in about 0.8 s, and a reply took 2.2 to 4.4 s against 23 to 25 s without it. The prompt in every request was identical apart from the sampling seed, so this is the best case. A real prompt will share a fixed prefix and change at the end, and only the changed part costs time. That was not measured.
- Replies are still not fast enough for a live visit (D4). Caching makes bank generation cheaper at idle: keep the rules and persona as a fixed prefix and vary only the tail.
