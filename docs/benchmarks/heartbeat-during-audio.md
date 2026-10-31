# Heartbeat during long audio, real MCU

Date: 2026-10-31 (board clock read 2026-10-30 21:40 UTC)
Board: Arduino UNO Q, 4 GB, Debian 13 image 20260528-558, arduino-app-cli 0.14.0, Ethernet. USB sound card attached. No jaw, wheel or LEDs wired; the sketch ran with placeholder pins.
Code: `app/sketch/sketch.ino` at commit 785f48f (heartbeat watchdog, 1000 ms) and the `play()` loop from `app/python/main.py` (aplay started with Popen, `Bridge.call("heartbeat")` every 0.3 s on the same thread). Run as a separate app, `arduino-app-cli app start`, so the main app was untouched.

## Pass rule (set before the run)

Zero failed heartbeat calls, the largest gap between two heartbeats under 700 ms, and the MCU not in the safe state after playback. The control run must show that the safe state really is reachable.

## What was played

Digital silence, 22.05 kHz 16-bit mono WAV, to `plughw:1,0`. The test is about the timing of `aplay` and the Bridge, not loudness. Speech and silence use the same Popen and the same device path. Sound tests are done in the morning session.

## How the safe state was read

`Bridge.call("set_mode", 1)` returns 1 when the MCU is running and -2 when it is in the safe state (set_mode refuses everything but a clear). It was called right after each playback. No jaw was attached, so the jaw position was not looked at.

## Result

| Condition | Calls | Failed | Median gap | Max gap | Median RTT | Max RTT | set_mode(1) after |
|---|---|---|---|---|---|---|---|
| 5 s audio | 17 | 0 | 307 ms | 307 ms | 6.9 ms | 7.0 ms | 1 |
| 20 s audio | 66 | 0 | 307 ms | 309 ms | 6.8 ms | 7.3 ms | 1 |
| 60 s audio | 197 | 0 | 307 ms | 309 ms | 6.9 ms | 9.0 ms | 1 |
| 20 s audio, 3 busy loops on the board | 66 | 0 | 307 ms | 313 ms | 7.0 ms | 13.3 ms | 1 |

Control, no heartbeat for 1.5 s: `set_mode(1)` returned -2 (safe). A fresh heartbeat plus `set_mode(0)` returned 0, and `set_mode(1)` then returned 1 again.

All conditions pass. The longest gap was 313 ms against a 1000 ms watchdog, so the margin is more than 3 times with 3 CPU hogs running.

Raw: `raw/heartbeat-during-audio-2026-10-31.txt` (summary rows and every gap and RTT).

## Limits
One run per condition. The three busy loops are a stand-in for the cascade load, not the camera, sound and keyword bricks or llama.cpp, so a run with the real load is still to do. The game loop was not running, so no `tick()` or Stub work competed with the heartbeat. The jaw and wheel were not wired, so the safe state is shown by the return code only.
