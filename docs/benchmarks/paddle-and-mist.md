# Paddle drop and mist burst bench test

Board: Arduino UNO Q 4 GB, real `app/sketch/sketch.ino` flashed through App Lab, Python side a throwaway test app that sends a heartbeat every 0.5 s, calls `set_mode(0)` once, then calls the command under test. Servo and mist board on the separate 5 V rail, common ground with the board. Date: 2026-11-01 (bench session of 2026-10-31).

## Paddle and break-beam (servo D9, beam D2)

Three `dispense` calls, 10 s apart, one wrapped sweet loaded by hand before rounds 2 and 3.

| Call | Return | Drop notice |
|---|---|---|
| 1 | 0 | none (paddle empty) |
| 2 | 0 | `drop_confirmed` 1.5 s after the call |
| 3 | 0 | `drop_confirmed` 1.2 s after the call |

One miss does not trip the jam; two misses in a row send `jam` and enter the safe state (seen in an earlier run, where the third call returned -1). Paddle angles were the defaults (load 10, dump 80, 500 ms) and were not tuned.

## Mist burst (switch D4)

| Call | Return | Meaning |
|---|---|---|
| `set_fog(2000)` at 8.1 s | 2000 | burst started |
| `set_fog(2000)` at 11.2 s | -1 | refused, inside the 6 s rest pause |
| `set_fog(3500)` at 18.3 s | 3000 | request capped at the 3 s maximum |

The mist was seen working during the bursts. Not yet tested with the real servo and mist together under a missed heartbeat (watchdog safe state), or with the supply current measured.
