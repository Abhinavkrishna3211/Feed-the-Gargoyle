# Piper render time for the line bank

Date: 2026-10-30, about 17:15 to 17:20 board clock
Board: Arduino UNO Q, 4 GB, 4 cores, Debian 13, Ethernet. Load average 0.57 at the start (idle, nothing else running). Piper aarch64 binary, voice en_GB-alan-medium (22050 Hz), `--length_scale 1.1 --noise_scale 0.7 --noise_w 0.9`, `--output-raw` piped to `wc -c`. Voice effects (numpy and scipy) run on a PC, not on the board, and are not included.

## Method

12 lines taken evenly from the 164-line bank (every 14th line). Warm case: one Piper process reads all 12 lines from a file on the board, three runs, wall time by `date` around the command. Audio length from the byte count (16-bit mono). Cold case: one SSH call per line from the PC, each starting a new Piper process, one pass (same 12 lines).

## Result

| Case | Wall time | Audio | Render time per second of audio |
|---|---|---|---|
| Warm, one process, run 1 | 26.5 s | 49.1 s | 0.54 |
| Warm, run 2 | 25.3 s | 49.0 s | 0.52 |
| Warm, run 3 | 25.9 s | 49.2 s | 0.53 |
| Cold, per call, median of 12 | 5.1 s per line (max 8.3 s) | 3.9 s per line | 1.29 |

Warm, a line takes about 2.1 s to render on average. Load average rose to 2.9 during the runs, so Piper used about three cores.

## Conclusion

Rendering is faster than playback once the model is loaded, but not by a wide margin. That is fine for a pre-rendered bank and too slow to make a reply on the spot: a 4 s line would still take about 2 s plus the effects chain. Play from the bank. The cold figure includes model load and the SSH round trip, so it overstates what a resident process costs.

Not measured: render time while the camera, sound and keyword models are running, other voices, and the effects chain on the board.
