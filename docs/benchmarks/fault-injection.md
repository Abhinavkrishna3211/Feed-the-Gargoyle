# Fault injection: does the MCU reach its safe state?

Date: 2026-11-25, 12:50 to 13:05 UTC (board clock)
Board: Arduino UNO Q, 4 GB, Debian 13 image 20260528-558, arduino-app-cli 0.14.0.
Sketch: `app/sketch/sketch.ino` as in the repo (same md5 as the board copy), so `BEAT_MS` is 1000.
Test app: a throwaway App Lab app (not in the repo) with that sketch and a Python probe. Its Bridge calls use a 1 s timeout and try again on a timeout, as `app/python/runner.py` does.

## What the sketch promises

With no `heartbeat` (or `set_talk`) for more than `BEAT_MS`, `loop()` calls `enter_safe()`: paddle back to the load position, fog off, a still idle glow. In the safe state `set_level` and `set_fog` return -2, and `set_mode` returns -2 for anything but an idle request that follows a fresh heartbeat.

The method in [evaluation-plan.md](../evaluation-plan.md) section 4 has three faults. Two of them were run here (MPU application stall and kill). The third (unplugging the camera and microphone) was not, see the end.

## 1. The MPU stops sending heartbeats

Each trial: heartbeat, `set_mode(1)` (listening, spine meter live), `set_level(40)`, a heartbeat, then no Bridge call for a set gap, then `set_level(60)`. `set_level` does not count as a heartbeat, so its reply says whether the MCU went safe during the gap. When it said -2, the probe also tried `set_mode(2)` and `set_fog(300)` without a new heartbeat. Then heartbeat plus `set_mode(0)` cleared the safe state for the next trial. The gap is timed on the MPU from sending the heartbeat to sending `set_level`.

| Gap (s, measured) | Trials | Safe (`set_level` -2) | `set_mode(2)` and `set_fog` refused while safe |
|---|---|---|---|
| 0.607 | 10 | 0 | n/a |
| 0.807 | 10 | 0 | n/a |
| 0.907 | 10 | 0 | n/a |
| 0.957 | 10 | 2 | 2 of 2 |
| 1.057 | 10 | 10 | 10 of 10 |
| 1.107 | 10 | 10 | 10 of 10 |
| 1.207 | 10 | 10 | 10 of 10 |
| 1.507 | 10 | 10 | 10 of 10 |
| 3.007 | 10 | 10 | 10 of 10 |

So the MCU goes safe between 0.96 and 1.06 s after the last heartbeat leaves the MPU, in line with the 1000 ms watchdog plus the Bridge transit time. It never went safe below 0.9 s and went safe every time from 1.06 s on. Every safe state held: no command without a fresh heartbeat got out of it, and `heartbeat` plus `set_mode(0)` cleared it every time (final check returned 0).

Four calls in the run timed out after 1 s (two `heartbeat`, two `set_mode`) and each went through on the next try. A first run with the Bridge's default 10 s timeout and no retry stopped on one such stuck call, which is why the app's own calls use the short timeout and the retry.

## 2. The MPU application is killed mid-visit

The probe held `set_mode(1)` with a heartbeat every 0.3 s. The app container was then killed with `docker kill` (SIGKILL, no clean shutdown) and started again 3 s later with `docker start`, which does not reflash the MCU. The first calls after the restart were `set_level(10)` and `set_fog(300)`, then a `heartbeat`, whose reply is the MCU's `millis()`.

| Fault | Trials | `set_level` and `set_fog` after restart | MCU uptime at restart (ms) |
|---|---|---|---|
| `docker kill` (SIGKILL) | 5 | -2 and -2 every time | 206037, 217072, 228063, 238829, 250025 |
| `docker restart` (SIGTERM) | 1 | -2 and -2 | 187176 |

The uptime kept growing, so the MCU did not reset: it went to the safe state on its own after the Python side vanished, and refused fog and the meter until a fresh heartbeat and an idle request.

## Not covered

- Restarting the Bridge router (`arduino-router.service`) needs root on the board and was not run. Killing the container closes the app's side of the Bridge, which is the fault the watchdog sees either way: no heartbeat arrives.
- Unplugging the camera and microphone mid-visit needs someone at the statue and was not run.
- The safe state was read from the sketch's return codes, not by watching the paddle and fog. The paddle's move to the load position is the same code path the dispenser runs use ([paddle-and-mist](paddle-and-mist.md)).
