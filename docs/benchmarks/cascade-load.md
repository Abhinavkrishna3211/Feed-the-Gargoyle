# Language model speed with the camera, sound and keyword bricks running

Date: 2026-10-29, 22:58 to 23:11 UTC (board clock)
Board: Arduino UNO Q, 4 GB, Debian 13 image 20260528-558, arduino-app-cli 0.14.0, Ethernet. Power: an iPhone charger through the powered hub, rating not read. Arducam B0490 on the hub, Boya M1 on the USB sound card, speakers idle.

## What ran

A throwaway app (not in the repo) with three bricks inside `App.run()` for 700 s:

- `video_object_detection` on the Arducam at 10 FPS. It used the brick's default model (`yolox-object-detection`), not the face model; I did not find how to select the face model in `app.yaml`. Nobody stood in front of the camera, so this is a stand-in with the frame loop busy, not a visitor load.
- `audio_classification` on the Arducam mic (`hw:0,0`), model `glass-breaking`.
- `keyword_spotting` on the Boya M1 (`hw:1,0`), model `keyword-spotting-hey-arduino`.

At the same time `scripts/llm_bench.py` ran Gemma 3 1B, same settings as `llm-threads.md` (`-c 2048`, `--cache-reuse 256`, 40-token prompt, 30 requests per set, run 0 dropped), 3 threads first and then 4. `scripts/benchmark.py sample` logged at a 2 s interval for 680 s. Raw values: `raw/cascade-*-2026-10-29.*`.

## Result

| Measure | Value |
|---|---|
| Audio inference over 700 s (n = 1746) | median 124 ms, p95 193 ms, max 338 ms |
| Keyword inference (n = 1746) | median 118 ms, p95 178 ms, max 316 ms |
| Same two models with no LLM (first run, 300 s, n = 747) | median 108 and 103 ms, p95 174 and 163 ms |
| Board resets | 0 (boot_id the same before, after and in all 338 samples) |
| Swap | 0 kB |

| LLM set (n = 29 each) | Generation tok/s, median | 40-token prompt ms, median | Wall per reply ms, median / max |
|---|---|---|---|
| 3 threads, under load | 2.58 | 8,209 | 12,905 / 17,014 |
| 4 threads, first 14 requests, under load | 2.38 | 8,226 | 13,191 / 17,783 |
| 4 threads, last 15 requests, after the app had ended | 4.99 | 4,244 | 6,973 / 15,976 |

Compare the earlier runs of the model alone: 4.36 tok/s at 3 threads and 5.42 at 4 threads (`llm-threads.md`).

Sampler during the full-load window (about 22:58:50 to 23:09:45): CPU busy median 93 to 95%, load1 max 7.8, lowest MemAvailable about 2,317,000 kB, hottest zone 74.6 C (60.0 C for the model alone at 4 threads). The app finished at 23:09:51 and the sampler at 23:09:54, so the tail of the 4-thread set was not sampled.

## What it says

- The board stayed up with all three bricks and the model at 4 threads. The old claim that 4 threads resets it did not reproduce here either, on this supply.
- Under load the model is about 40% slower at 3 threads (2.58 against 4.36 tok/s) and 4 threads gives no gain (2.38). The cores are already full, so the extra thread only fights the bricks. A reply takes about 13 s, which is another reason lines must come from the pre-rendered bank. Generate them at idle only.
- The bricks slowed by about 15% (audio median 108 to 124 ms) with the model running. That is still well inside the 250 ms stride planned for the sound model. The keyword brick produced a window about every 0.38 s earlier; I did not check the window rate under load.
- Temperature reached 74.6 C. Whether that throttles this board was not checked.
- Not covered: a person in front of the camera, speech rendering, the MCU, LEDs, a PD supply, runs longer than 12 minutes, and whether the LLM brick passes `LLAMA_ARG_THREADS`. The first attempt (`raw/cascade-run1-*`) is kept, but its app stopped after 300 s, so only about 90 s of the 3-thread set overlapped it; it is not used.

## 30 minute soak, 3 threads
Date: 2026-10-30, 05:17 to 05:49 UTC (board clock). Same board, bricks, camera stand-in and settings as above; the board had restarted between the two sessions for a reason I did not see, so the boot_id differs (`0ee3a9f5-f2db-4594-b794-461ba475e6d2` throughout this soak). The app ran 1902 s, the sampler 1830 s at a 2 s interval (908 samples), and `llm_bench.py 3 --runs 140` sent back-to-back requests. I stopped it after 126 requests; the last one or two ended after the sampler and the app had stopped, so they ran lightly loaded. Raw values: `raw/cascade-soak-*-2026-10-30.*`.

| Measure | Result |
|---|---|
| Board resets | 0 (boot_id the same before, after and in all 908 samples) |
| Swap | 0 kB |
| CPU busy | median 95.0%, max 98.9%; load1 max 8.4 |
| Hottest zone | median 71.2 C, max 73.4 C |
| Lowest MemAvailable | about 2,332,000 kB |
| Audio inference (n = 4747) | median 125 ms, p95 198 ms, max 379 ms |
| Keyword inference (n = 4747) | median 115 ms, p95 177 ms, max 357 ms |
| Camera frame callbacks | 56 (nobody in front of the camera) |
| LLM requests (run 0 dropped, n = 125) | wall median 14.6 s, p95 18.5 s, max 20.9 s |
| LLM generation | median 2.21 tok/s, min 2.10, max 4.09 (the 4.09 is the last request, partly unloaded) |
| LLM 40-token prompt, median | 9.2 s |
| First 25 / last 25 requests, tok/s | 2.28 / 2.18, no clear slowdown with heat |

The cascade held for 30 minutes at 3 threads with no reset and no memory pressure. The language model was about 15% slower than in the 12 minute run (2.21 against 2.58 tok/s), at 71 C instead of 75 C, so I cannot say why; the longer run may simply have had more camera frames or noise to process. Not covered: a person in front of the camera, speech rendering, the MCU, a PD supply, and runs beyond 30 minutes.

## Supply rating (read 2026-10-30)
The iPhone charger used in every run on this board is labelled: input 200-240 V, 50-60 Hz, 0.5 A; output 5 V 2.4 A, and with PD 5 V 3 A or 9 V 2.22 A. It was read by the builder from the label; the charger was not measured under load. It feeds a powered hub that also carries the Ethernet adapter, sound card and camera, and the hub's own supply (if it has one) was not recorded, so the current drawn by the board alone is unknown. Every reset question in these notes was tested on this supply, so a "no reset" result is for 5 V at up to 3 A shared with those peripherals.

The builder confirmed the hub has no supply of its own: the same charger powers the hub and everything on it, and the board. So the camera, sound card, Ethernet adapter, microphone and the board all share one 5 V supply rated 3 A on its label. The board came back up cleanly after a clean shutdown and unplug (boot_id `f6597188-3b7e-4663-ac58-877ac3f8642d`, 06:07:52 UTC, 3,667 MB total memory).

Hub model (from the builder's product page screenshot): Portronics Mport 51, a 5-in-1 USB-C hub with a PD 3.0 pass-through port, one USB 3.0 port, one USB 2.0 port, HDMI and RJ45 Ethernet. The page text in the screenshot does not give the pass-through wattage, so the power the board receives through the hub is not known. The camera and sound card use the two USB-A ports and the Ethernet adapter is the hub's own, all on the hub's single upstream USB-C link to the board.
