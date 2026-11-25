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

## Final statue dispenser (2026-11-13)

Board: Arduino UNO Q 4 GB. Printed PLA+ statue dispenser fully assembled, SG90 on D9, LM393 IR module on D2. Test sketch with the game's angles and sweep (load 170, dump 25, 3 ms per degree, 500 ms hold at dump), driven by hand over SSH: one dump and return per command, a 3 s wait at load before the next. The IR line was polled every 20 ms by the Python side, and falling edges were counted on the MCU.

| Run | Dispenses | Sweets out (seen) | IR edges | Board resets |
|---|---|---|---|---|
| 1 | 4 | 3 | 2 | 1, 4 s after the run |
| 2 | 1 | 1 | 1 | 0 |
| 3 | 5 | 5 | 5 (per dispense 0, 2, 0, 2, 1) | 0 |

The rotor was re-seated on the horn before these runs so the pocket lines up with the tube at 170. In run 3 every dispense gave one sweet, so the uneven per-dispense edge counts are bounce: a sweet can cross the beam twice, or slip past it. The game sketch takes the first edge after a dump as the drop and ignores the rest, and a dispense with no edge is retried once before `jam`, so the bounce is harmless there.

Four board resets happened in about 20 minutes of earlier testing on the same supply. Each journal ends without a shutdown, which is a loss of power, and three of them came right after servo runs. Runs 2 and 3 above, after a power cycle, had none. The servo still needs to be on the separate 5 V rail with only ground shared before this is trusted in play.

## Mist burst (switch D4)

| Call | Return | Meaning |
|---|---|---|
| `set_fog(2000)` at 8.1 s | 2000 | burst started |
| `set_fog(2000)` at 11.2 s | -1 | refused, inside the 6 s rest pause |
| `set_fog(3500)` at 18.3 s | 3000 | request capped at the 3 s maximum |

The mist was seen working during the bursts. Not yet tested with the real servo and mist together under a missed heartbeat (watchdog safe state), or with the supply current measured.
