# Keyword spotter on a continuous stream

Date: 2026-11-25 (board clock)
Board: Arduino UNO Q, 4 GB, Debian 13 image 20260528-558. The Feed the Gargoyle app was running at the same time.
Model: `keywords.eim` as installed (float32, sha256 starts 2d4aa68f4a1f253b), the build in [eim-on-board](eim-on-board.md).
Tool: `scripts/kws_stream.py` on the board, talking to the `.eim` runner over its socket.

## Method

All 569 frozen test clips (306 answers in six words, the rest `unknown` and `noise`), padded to 1 s, joined back to back in a fixed random order (seed 7) into one 569 s recording. A 1000 ms window every 100 ms gives 5681 windows. A window fires when its top answer word scores 0.5 or more, the threshold the app gives the keyword brick.

- An answer counts as caught when a window starting within 0.5 s of the clip fires that clip's word.
- A false alarm is a run of firing windows whose word does not match a clip within 0.5 s. One run counts once.
- The vote fires only when 3 of the last 4 windows fire the same word, scored on the same windows.

## Results

| Rule | Caught | False alarms in 569 s |
|---|---|---|
| Single window at 0.5 (the app) | 299 of 306 (97.7 %) | 96 |
| 3 of 4 windows | 292 of 306 (95.4 %) | 13 |

The recording is nonstop speech with no gaps, so it is harsher than a riddle, where the app only listens for a few seconds after asking. The app keeps the single-window rule because a missed answer costs a visitor their sweet.
