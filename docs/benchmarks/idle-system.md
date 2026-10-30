# Idle system load, with and without the app

Date: 2026-10-29, board clock UTC
Board: Arduino UNO Q, 4 GB, Debian 13 image 20260528-558, arduino-app-cli 0.14.0. Wi-Fi only, USB-C power from a laptop, no peripherals.
Tool: `scripts/benchmark.py sample` run on the board. Raw lines: `raw/idle-after-boot-2026-10-29.jsonl` and `raw/app-heartbeat-2026-10-29.jsonl`.

## Pass rule

Zero resets in each 10 minute run. No other threshold, this is a baseline for later comparison.

## Command and conditions

`python3 benchmark.py sample out.jsonl --interval 5 --duration 600`, one sample every 5 s, 120 samples, nothing else running except the services that start at boot.

- **idle_after_boot**: started 19:06 UTC, 7 min after the board came up. No app running.
- **app_heartbeat**: started 19:17 UTC. The gargoyle app was running in normal mode, one `heartbeat` Bridge call per second, matrix showing the idle frame. Samples start about 60 s after the app start returned.

## Result (n = 120 samples each, no warm-up dropped)

| Metric | idle_after_boot: min / median / max | app_heartbeat: min / median / max | Unit |
|---|---|---|---|
| CPU busy | 0 / 0.15 / 3.3 | 0.15 / 0.30 / 1.15 | % |
| MemAvailable | 3,211,040 / 3,217,350 / 3,221,000 | 3,149,290 / 3,155,590 / 3,161,180 | kB |
| Swap used | 0 / 0 / 0 | 0 / 0 / 0 | kB |
| Hottest thermal zone | 36.2 / 36.5 / 37.8 | 36.2 / 36.5 / 37.5 | C |
| Load average (1 min) | 0 / 0.01 / 0.21 | 0 / 0 / 0.24 | |

Resets: 0 in both runs (same `boot_id` and rising uptime throughout).

## Bugs found and fixed

- `pgrep -f` over SSH matches the remote shell's own command line, so a check for "sampler still running" always said yes. Use `ps -eo args | grep "[b]enchmark.py sample"` instead.
- Backgrounding `nohup` inside an SSH command kept the session open until the sampler ended. Wrap it in a subshell: `(nohup ... &)`.

## Conclusion

The running app costs about 62 MB of available memory (median 3,217,350 to 3,155,590 kB, a single pair of runs) and about 0.15 percentage points of CPU. Temperature did not change. Nothing reset in 20 minutes of sampling at idle.

Wi-Fi link: one SSH attempt after the second run timed out, and ping to the board showed 2203 ms, 3 ms and 220 ms in three consecutive replies. Cause not found. This is the only route to the board while the hub is off, so a flaky link is a risk for long soak runs.

Not measured yet: load from the models, servo and stepper, supply type effects, runs longer than 10 minutes, and a true cold start from power-off (the board was power-cycled by hand before the first run).
