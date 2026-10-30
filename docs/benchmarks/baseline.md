# Baseline: fresh image on the 4 GB board

Date: 2026-10-29
Board: Arduino UNO Q, 4 GB variant, Wi-Fi only, powered over USB from a laptop.
Image: Debian GNU/Linux 13 (trixie), Arduino flasher image 20260528-558, flashed with Arduino Flasher CLI 0.5.4 over EDL.
Tooling: arduino-app-cli 0.14.0 (after `apt` update from 0.11.0), daemon 0.14.0.

## Pass rule (written before measuring)

The board counts as a clean baseline when it boots to Debian, has the full 4 GB visible, joins Wi-Fi, accepts SSH, and a Python-to-sketch Bridge call returns from the MCU.

## System

| Item | Value | How measured |
|---|---|---|
| `uname -a` | `Linux gargoyle 7.0.0-g122c2c22d838 #1 SMP PREEMPT Tue May 19 15:08:13 UTC 2026 aarch64 GNU/Linux` | shell, after update and reboot |
| CPUs | 4 | `nproc` |
| MemTotal | 3,755,160 kB | `/proc/meminfo` |
| SwapTotal | 1,877,576 kB | `/proc/meminfo` |
| Update | 158 upgraded, 137 newly installed, exit 0 | `apt` |

## Idle, 17:41 UTC, 1 h 14 min after boot, no app running, no containers running

| Item | Result | How measured |
|---|---|---|
| MemAvailable | 3,165,144 kB | `/proc/meminfo` |
| MemFree | 1,568,952 kB | `/proc/meminfo` |
| Swap used | 0 | `/proc/meminfo` |
| CPU busy, n = 6 windows of 10 s | min 0.07 %, median 0.20 %, max 0.45 % | two reads of the `cpu` line in `/proc/stat` per window, 4 min after stopping the app |
| Load average | 0.00 / 0.12 / 0.13 | `/proc/loadavg` |
| Temperature, one read | cpuss0 36.5 C, cpuss1 37.1 C, gpu 35.6 C, hottest zone 37.1 C | `/sys/class/thermal/*/temp`, room temperature not recorded |
| `/` | 20 G, 8.3 G used, 11 G free (45 %) | `df -h` |
| `/home/arduino` | 8.1 G, 613 M used, 7.1 G free (8 %) | `df -h` |

Storage on first boot, before the update: `/` 6.1 G used, 13 G free. The update and one 909 MB container image account for the 2.2 G growth.

## Bridge hello-world

Command: `arduino-app-cli app start /home/arduino/ArduinoApps/hello-bridge`, an app created from the Arduino example "Call a sketch function from Python", with the Python loop changed to print the round trip time.
Result: the sketch compiled and flashed to the STM32U585, the container started, and `Bridge.call("say_hello", "Python")` returned every time.
Round trip, n = 10 calls on one run: 12.0 ms to 13.1 ms, median about 12.9 ms. Measured with `time.monotonic()` around the call inside the container.
Negative check: `Bridge.call("no_such_fn")` raised `RpcError ... method no_such_fn not available (2)`, so a successful call is a real answer from the sketch.
Not seen: the sketch's `Monitor.println` text. `arduino-app-cli monitor` printed nothing in 8 s. The Bridge result does not depend on it, but the serial monitor path is not confirmed.

## Bugs found and fixed

- `ssh.service` failed with "no hostkeys available" on the fresh image. Fixed with `ssh-keygen -A`.
- `arduino-app-cli app start` died at 20 % of the container image pull twice (killed after about 7 min). A direct `docker pull` of the same image finished. The board's Wi-Fi moved about 130 to 150 KB/s during the pull (read from `/proc/net/dev`, three samples 5 s apart), and several layers retried.
- The USB/ADB link did not come back after one reboot until the board was power-cycled. Cause not found. Not yet retested.

## Conclusion

The 4 GB board is a clean Debian 13 baseline with about 3.1 GB of RAM free and the CPU idle at a median 0.20 %. The Bridge works with a median round trip of about 12.9 ms in this one run. Not measured yet: idle temperature over time, idle power, serial monitor output, reboot repeatability.
