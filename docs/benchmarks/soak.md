# Two-hour soak with the full app

Date: 2026-11-25, 10:42:39 to 12:43:37 UTC (board clock)
Board: Arduino UNO Q, 4 GB (3667 MB reported by `free -m`), Debian 13 image 20260528-558, arduino-app-cli 0.14.0. The app's camera, Boya microphone and USB sound card connected, and the sketch running on the MCU.
Tool: `scripts/benchmark.py sample` on the board, one sample every 5 s for 7260 s. Raw lines: `raw/soak-2026-11-25.jsonl`.

## Pass rule

No reset (the same `boot_id` in every sample) and no swap. Temperature is recorded, not judged.

## Conditions

The Feed the Gargoyle app ran the whole time with real sensors (`python/sensors.on`): the visitor model and keyword spotter as App Lab bricks, the costume and props models as Edge Impulse runners, and the pre-rendered voice bank. The app had been running for about 53 minutes when sampling started. The riddle-only test switch was on, so every visit was a riddle. No language model ran (the line bank is pre-rendered).

## Results

1449 samples over 7259 s, all with `boot_id` `f9c47f5b-cec0-46e9-86a9-96ee272b6956`: 0 resets.

| Metric | Min | Median | Max |
|---|---|---|---|
| CPU busy (%) | 49.3 | 52.4 | 91.0 |
| Memory available (MB) | 2372 | 2442 | 2639 |
| Swap used (kB) | 0 | 0 | 0 |
| Hottest thermal zone (C) | 50.3 | 52.5 | 62.5 |
| Load average, 1 min | 1.67 | 2.76 | 5.15 |

From the app log (`docker logs`, the app's own `STATE` lines inside the soak window): 19 wakes, each going to LISTEN and then COOLDOWN on the timer. Nobody answered, so none reached a win, and no sweet was dispensed. Bridge errors stayed at 0 on every state line and the app printed no traceback.

## What this does and does not show

- The board ran the full model stack for two hours without a reset or swapping; the hottest thermal zone peaked at 62.5 C.
- Memory did not trend down over the run: the last sample (2442 MB available) matched the median.
- It does not cover the win path under load: no sweet was dispensed during the soak. The dispenser has its own runs in [paddle-and-mist](paddle-and-mist.md).
- The video runner's health check read `unhealthy` throughout, as noted in [eim-on-board](eim-on-board.md); the camera kept classifying (the 19 wakes came from it).
