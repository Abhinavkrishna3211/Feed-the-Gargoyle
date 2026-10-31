# app

The Arduino App Lab application.

| Path | Contents |
|---|---|
| `python/` | MPU side: model runners, game state machine, line bank, audio playback |
| `sketch/` | MCU side: lights, candy paddle servo, drop sensor, watchdog |

The Bridge contract between the two is described in [docs/architecture.md](../docs/architecture.md). Build and run instructions are added once the first version runs on the board.

## Run on the board

Copy `app/` to `/home/arduino/ArduinoApps/gargoyle` on the board, then `arduino-app-cli app start /home/arduino/ArduinoApps/gargoyle`. The first start compiles and flashes the sketch.

Create `python/bench.on` before starting to run the Bridge latency check once instead of the heartbeat. Results are in [docs/benchmarks/bridge-latency.md](../docs/benchmarks/bridge-latency.md).
