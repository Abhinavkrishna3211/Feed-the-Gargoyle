# Gemma 3 1B generation speed at 2, 3 and 4 threads

Date: 2026-10-29, 20:22 to 20:52 UTC (board clock)
Board: Arduino UNO Q, 4 GB, Debian 13 image 20260528-558, arduino-app-cli 0.14.0, Ethernet (Realtek adapter on a powered hub). No app running (`arduino-app-cli app ps` empty), nothing else attached to the board. Power during these runs: an iPhone charger through the powered hub, rating not read (the label was not visible while the board was in use), so the supply's current limit is unknown.
Model: `gemma-3-1b-it-Q4_0.gguf`, installed with `arduino-app-cli model install llamacpp:gemma-3-1b-it-Q4_0`. It took about 2 minutes over Ethernet and 705,024 kB of disk (`df` before and after).
Server: `llama-server` version 0.4.1-dev (build 11036, commit 911f6cdc8), built with GNU 14.2.0 for aarch64, from the image `ghcr.io/arduino/app-bricks/llamacpp-runner:0.13.0` that the LLM brick uses.

## Why this test

The brick's service file on the board (`/var/lib/arduino-app-cli/assets/0.13.1/services/arduino/llamacpp/service_compose.unoq.yaml`) defaults to `LLAMA_ARG_THREADS=4`, `LLAMA_ARG_CTX_SIZE=16384` and a 2500 MB memory limit. Our working rule says 4 threads reset this board. This run checks the speed cost of 2 and 3 threads and whether 4 threads resets the board in a short burst.

## Command

`scripts/llm_bench.py`, copied to the board and run there. For each thread count it starts the runner image with `docker run --memory 2500m --memory-swap 2500m`, entrypoint `llama-server --device none -m <gguf> -t N -c 2048 -b 512 -ub 128 --cache-reuse 256 --flash-attn on --reasoning off`, waits for `/health`, then sends the same chat request 5 times (`max_tokens` 40, temperature 0.7, seeds 0 to 4, `cache_prompt` false). The prompt is 40 tokens: one sentence asking for a short, playful gargoyle line for a visitor who answered a riddle. Timings come from the `timings` object in the server reply. Wall time is measured by the client around the HTTP call on the board. Run 0 of each set is dropped from the medians, so n = 4. `scripts/benchmark.py sample` ran at a 2 s interval during each set. Raw values: `raw/llm-t{2,3,4}-2026-10-29.jsonl` and `raw/llm-t{2,3,4}-sampler-2026-10-29.jsonl`.

## Result (n = 4 per thread count, run 0 dropped)

| Threads | Generation (tok/s, median) | 40-token prompt (ms, median) | Wall per reply (ms, max) | Resets |
|---|---|---|---|---|
| 2 | 3.09 | 7,607 | 12,046 | 0 |
| 3 | 4.36 | 5,139 | 8,386 | 0 |
| 4 | 5.42 | 3,984 | 6,572 | 0 |

Replies were 10 to 15 tokens long, for example "You've earned a little sweetness, little friend." Server start to healthy took 6.9 s (3 threads), 6.9 s (2) and 6.8 s (4).

Sampler during each set (2 s interval):

| Threads | Samples | CPU busy median / max (%) | Lowest MemAvailable (kB, about) | Hottest zone max (C) |
|---|---|---|---|---|
| 2 | 31 over 60 s | 50 / 56 | 3,011,700 | 52.5 |
| 3 | 26 over 50 s | 73 / 80 | 3,015,220 | 54.6 |
| 4 | 18 over 34 s | 94 / 99.5 | 3,007,750 | 60.0 |

Swap use was 0 at 3 threads. Idle MemAvailable was a median of 3,217,350 kB earlier the same day (`idle-system.md`), so the model and server cost about 200 MB.

## Soak at 4 threads

Same harness and settings, `--runs 150`, back-to-back requests, started 20:35:49 UTC. The boot_id before and after was the same (`cd85d30b-ec9f-4d95-a8b7-c9fe79628ccd`). Raw values: `raw/llm-t4-soak-2026-10-29.jsonl` and `raw/llm-t4-soak-sampler-2026-10-29.jsonl`.

| Measure | Result |
|---|---|
| Requests | 150, all completed, board up 1:07 at the end |
| Sampler | 478 samples over 960 s, 0 resets, swap 0 kB |
| Wall per reply (ms) | min 5,151, median 6,280, p95 7,750, max 8,817 |
| Generation (tok/s) | median 5.51, min 4.53, max 5.54 |
| Median over first 24 runs / last 24 runs | 5.35 / 5.51 tok/s, no slowdown with heat |
| CPU busy | median 95.8%, max 99.6%; load1 max 4.55 |
| Hottest zone | median 62.1 C, max 64.3 C |
| Lowest MemAvailable | about 2,986,630 kB |

## Conclusion

- At 3 threads a 12-token reply takes 7 to 8 s from request to end. That is far too slow to sit between a visitor's answer and the gargoyle's reaction, which supports generating lines ahead of time (D4) and playing them from the bank.
- 4 threads was about 24% faster than 3 for generation (5.42 against 4.36 tok/s). It did not reset the board in the 34 s burst or in the 960 s soak below.
- The earlier rule that 4 threads resets this board did not reproduce. It is not refuted for other loads: the soak ran the language model alone, with no camera, microphone or speech rendering, on one supply. Treat the old claim as unverified. 3 threads stays the setting for play so one core is left for the other models, and that reason is untested too.
- The brick's own default (4 threads, 16384 context) is what a plain `LargeLanguageModel()` call would use. The app has to override both. Whether the brick passes `LLAMA_ARG_THREADS` through is not tested: its documented variable list only names `LLAMA_ARG_CTX_SIZE`.

## Not explained (see llm-probes.md for flash attention and caching)

Prompt processing ran at about 7.8 tok/s at 3 threads (40 tokens in 5.1 s), while generation ran at 4.4 tok/s. Prompt processing is usually several times faster than generation, so this is odd. I did not test why. Flash attention is on in the brick's settings, and `--device none` is used. Both are untested suspects.

## Not measured yet

- Runs longer than 16 minutes, and any load at 2 or 3 threads beyond the short sets above.
- 4 threads with the camera, microphone and Piper running at the same time, on a PD supply.
- The effect of `--cache-reuse 256`, because `cache_prompt` was off here.
- Flash attention off, other batch sizes, a longer prompt, and the 16384 default context.
- Memory and speed with the camera and microphone pipelines running at the same time.
- Piper speech rendering time, and whether the generated lines pass the line validator.
- Power: the supply used was not logged, so a brownout cannot be ruled out as the cause of any later reset.
