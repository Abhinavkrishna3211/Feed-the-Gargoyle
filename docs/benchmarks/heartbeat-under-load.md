# Heartbeat under the cascade load, and the LED redraw that broke it

Date: 2026-10-31, 06:10 to 07:25 UTC (board clock)
Board: Arduino UNO Q, 4 GB, Debian 13 image 20260528-558, arduino-app-cli 0.14.0, Ethernet. USB sound card attached, Arducam on the hub. No jaw, wheel, LEDs or mist board wired; the sketch ran with its placeholder pins, so the NeoPixel data pin drove nothing. The board lost power once at about 06:45 and came back with a new boot_id; runs 1 to 4 are before that, runs 5 to 9 after (a first attempt at run 5 was cut off by the power loss and is not counted).
Test app: a throwaway app (not in the repo) running the heartbeat loop of `play()` in `app/python/main.py`: `aplay` of digital silence to `plughw:1,0`, `Bridge.call("heartbeat")` every 0.3 s on the same thread, every call timed. Conditions are 60 s, 120 s and 120 s of audio, one after the other, after a control that must reach the safe state. "Load" is the three bricks of `cascade-load.md` (camera object detection at 10 FPS on the stand-in model, sound model on the camera mic, keyword model on the Boya M1) plus `scripts/llm_bench.py 3` sending back-to-back requests to Gemma 3 1B at 3 threads (2.25 to 2.29 tok/s median while the heartbeat runs, 4.1 alone).

## Pass rule (same as `heartbeat-during-audio.md`)

Zero failed heartbeat calls, the largest gap between two heartbeats under 700 ms, and the MCU not in the safe state after playback. The watchdog is 1000 ms.

## Result

| Run | Sketch idle LED redraw | Load | Heartbeat timeout | Calls | Lost | Largest gap | Safe state after |
|---|---|---|---|---|---|---|---|
| 1 | every 100 ms | bricks and model | 10 s (default) | n/a | n/a | n/a | n/a |
| 2 | every 100 ms | bricks and model | 10 s | 293 | 9 | 10.3 s | no answer (set_mode timed out) |
| 3 | every 100 ms | bricks only | 10 s | n/a | n/a | n/a | n/a |
| 4 | every 100 ms | none | 10 s | 666 | 10 | 10.3 s | yes (-2) |
| 5 | none | none | 10 s | 980 | 0 | 312 ms | no (1) |
| 6 | every 100 ms | none | 0.25 s | 970 | 12 | 551 ms | no (1) |
| 7 | every 100 ms | bricks and model | 0.25 s | 128 | 62, then the app stopped | continuous outage | n/a |
| 8 | none | bricks and model | 0.25 s | 951 | 0 | 411 ms | no (1) |
| 9 | none (final sketch) | bricks and model | 0.25 s | 951 | 0 | 379 ms | no (1) |

- Run 1: the Bridge client logged a UTF-8 decode error in its read loop at 06:11:44, the router logged the connection closed and a new one at 06:11:47, and the next `set_mode` timed out after 10 s, which stopped the app. No timing rows were written.
- Run 2: the 60 s and first 120 s conditions finished (99 and 194 calls, 3 and 6 lost, each loss a 10.3 s stall); the next heartbeat then timed out and stopped the app, so there is no third condition.
- Run 3: the first heartbeat, 40 s after the app started, timed out and stopped the app.
- Run 7: from 29.8 s on every call was lost, one every 0.55 s, until the audio ended; the next call stopped the app.
- Run 9 is the final `app/sketch/sketch.ino` and `app/python/main.py` of this commit. Medians: gap 312 to 314 ms, round trip 9.0 to 9.7 ms, largest round trip 62.4 ms. The model ran at 2.25 tok/s median, so the load was real.
- A single lost call with the default 10 s timeout blocks the loop for 10 s. That alone exceeds the 1000 ms watchdog, so the MCU went to its safe state (run 4). With a 0.25 s timeout (run 6) a lost call costs one beat and the largest gap stayed at 551 ms.

Raw: `raw/heartbeat-under-load-2026-10-31.txt` holds run 9 only (summary rows, every gap and round trip). The other rows are from the summary lines printed by each run; their containers were removed to get a clean log, so their raw gaps were not kept.

## What it says

- The periodic NeoPixel redraw in the idle glow is what lost the calls. With the same code, board and audio, turning the redraw off took the loss from 10 of 666 calls (run 4) to 0 of 980 (run 5), and under the full load from continuous outage (run 7) to 0 of 951 (run 8).
- Mechanism, not measured: `Adafruit_NeoPixel::show()` blocks interrupts for about 0.9 ms for 29 pixels (29 x 24 bits x 1.25 us), and a Bridge packet arriving in that window is damaged. The router logged `invalid packet, expected array` on the damaged ones, and the Python client logged a UTF-8 decode error. I did not look at the UART or at the MCU side.
- Not explained: why the loss comes in clusters about 10 s apart without load, and why the outage lasts tens of seconds under load. The runs only show that it needs the redraw and is made much worse by the load.
- The earlier pass in `heartbeat-during-audio.md` was measured with a scratch copy of the sketch that had no NeoPixel code at all (no strip, no redraw), so it does not describe the sketch in the repo.

## What changed because of it

- `app/sketch/sketch.ino`: the idle glow is a fixed amber and a dim spine, drawn when the mode or level changes. Nothing redraws on a timer. `GLOW_MS` is gone.
- `app/python/runner.py`: Bridge calls from the game use a 1 s timeout; `set_mode`, `set_level` and `set_fog` get one retry.
- `app/python/main.py`: heartbeats go through `beat()`, a call with a 0.25 s timeout that swallows the error, so one lost call cannot hold up the next beat. Before, the main loop's heartbeat had no guard and a timeout would have stopped the app.

## Game loop under load (run 10)

Same board (4 GB UNO Q), same bricks (camera object detection, two audio classifiers, keyword spotting) and Gemma 3 1B through `llm_bench.py` at 3 threads with `--cache`, two bench runs back to back (59 and 39 requests, median 2.39 tok/s each) with a gap between them that I did not log. The real `Game`, `Runner` and `Voice` ran with the stand-in visitor (`Stub`, a visitor every 8 s for 15 s). 30 s settle, then 660 s counted. Raw line: `raw/game-loop-under-load-2026-10-31.txt`.

| Call | Sent | Lost | Median ms | Max ms |
|---|---|---|---|---|
| heartbeat (0.25 s timeout) | 3752 | 0 | 8.6 | 98.2 |
| set_mode | 42 | 0 | 8.3 | 37.2 |
| set_level | 46 | 0 | 8.2 | 31.1 |
| set_fog | 5 | 0 | 8.3 | 9.0 |
| dispense | 10 | 0 | 7.9 | 37.9 |

- Longest gap between heartbeats 482 ms, none over 700 ms. Runner errors 0.
- 12 visits: 5 wins, 5 jam lines, 3 too quiet, 2 wrong sound, 1 wrong answer, 2 riddles, 4 scream, 4 clap and 2 whistle challenges.
- The MCU sent two `jam` notices and refused two `set_mode` calls with -2. The break-beam pin is not wired on this board (it floats high), so every dispense counts as a miss, and two misses in a row put the sketch in its safe state. I read this from the sketch logic and the return codes, I did not log the state itself. The app cleared the safe state with `set_mode(0)` each time and play went on.
- Because nothing was lost, the 1 s timeout and the retry in `Runner.bridge` never had a lost call to act on. They were exercised only as the call path, not as recovery.
- A first run of this test was invalid: `main.py` never sent `set_mode(0)` after the app started, the MCU was already in its safe state, and both mode changes in it were refused. `main.py` now arms the MCU at start and again after any refused command.

## Limits

- The LED strip was not attached, so the redraw timing is for 29 pixels on an unconnected pin. The real chain draws the same bits, but I have not looked at it on a scope.
- Every redraw that remains (a mode change, a `set_level` step, up to 10 per listen window) can still damage one packet. Run 9 had none of these in it, because it only ran the heartbeat. Run 10 put 42 mode changes, 46 level steps and 5 fog bursts through under load with none lost, but on one board, one run and no LEDs attached, so a damaged packet is still possible.
- The other calls (`set_mode`, `set_level`, `set_fog`, `dispense`) now go through `Runner.bridge` with a 1 s timeout, and the first three are sent a second time if the first is lost. `dispense` is not retried, because a timeout does not say whether the wheel moved. Run 10 sent these calls on the board and none was lost, so the retry itself is still covered only by the host self-test.
- Nobody stood in front of the camera, the sound models were the stand-in `glass-breaking` and `hey-arduino` ones, and each condition ran once. Runs 1 to 3 stopped early, so they only show that failures happened.
- The jaw and wheel are not wired, so the safe state is read from the `set_mode` return code only.
