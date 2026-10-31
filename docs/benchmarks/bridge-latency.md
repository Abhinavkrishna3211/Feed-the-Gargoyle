# Bridge round trip with LED redraw

Date: 2026-10-29, 18:32 UTC (board clock, NTP synced)
Board: Arduino UNO Q, 4 GB, Debian 13 image 20260528-558, arduino-app-cli 0.14.0, Wi-Fi, USB power from a laptop. Nothing else attached.
Code: `app/` at this commit (sketch and `python/main.py`), run on the board as the app "Feed the Gargoyle".

## Pass rule

Zero failed calls, and p95 under 20 ms in every condition. The 20 ms figure was picked after the first run, from the 6 to 8 ms per call noted in `docs/architecture.md` for the earlier ring, so it is not a pre-registered threshold.

## Command

`touch app/python/bench.on`, then `arduino-app-cli app start /home/arduino/ArduinoApps/gargoyle`. For each condition the app sets the LED mode through the Bridge, makes 10 warm-up calls, then 200 timed `Bridge.call("heartbeat")` calls 50 ms apart. Time is `time.monotonic()` around the call inside the Python container. Raw values: `raw/bridge-latency-2026-10-29.jsonl`.

## Conditions

LED means the 8x13 matrix on the UNO Q, driven from the MCU with `loadFrame`. The conditions run in this fixed order, one run each:

1. `led_on_change_only`: one frame drawn when the mode is set, nothing from `loop()`.
2. `redraw_500ms`: the sketch redraws a frame every 500 ms.
3. `redraw_100ms`: every 100 ms.
4. `redraw_40ms`: every 40 ms, the rate that broke an LED ring earlier.

## Result (ms, n = 200 per condition, 10 warm-up calls dropped each)

| Condition | Failed calls | Min | Median | p95 | Max |
|---|---|---|---|---|---|
| led_on_change_only | 0 | 5.3 | 5.6 | 5.9 | 6.0 |
| redraw_500ms | 0 | 5.5 | 5.7 | 5.9 | 6.0 |
| redraw_100ms | 0 | 5.4 | 5.7 | 5.9 | 6.0 |
| redraw_40ms | 0 | 5.4 | 5.7 | 5.9 | 6.6 |

## Bugs found and fixed

- `adb push` from Git Bash rewrote the remote path to `C:/Program Files/Git/...`. Fixed with `MSYS_NO_PATHCONV=1`.

## Conclusion

On this board the matrix redraw did not change Bridge latency, even at 40 ms: medians stayed within 0.1 ms and nothing timed out. This does not reproduce the earlier finding for an LED ring, so that finding does not carry over to the built-in matrix. It says nothing yet about the spine bar and the two eye panels, which are larger and use different drivers, so the test repeats once those exist.

Not explained: the first hello-bridge run measured a median of about 12.9 ms (n = 10) for a call whose handler printed to `Monitor`. Here the handler returns a number and the median is 5.7 ms. The print is a plausible cause but I did not test it.

Not measured yet: latency with the servo running, under model load, over a long run, and with a different order of conditions.
