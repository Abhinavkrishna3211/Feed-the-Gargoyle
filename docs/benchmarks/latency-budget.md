# Reaction latency: measured stages and gaps

Everything here comes from other notes in this folder, on the same 4 GB UNO Q. Stages without a measurement are marked so; no figure below is a target I have met.

| Stage | Measured | Where |
|---|---|---|
| Keyword model, one inference | median 115 ms, p95 177 ms, max 357 ms (n = 4747, all bricks and the language model running) | cascade-load.md |
| Sound model, one inference | median 125 ms, p95 198 ms, max 379 ms (same run) | cascade-load.md |
| Keyword and sound windows under load | 4747 inferences in 1902 s, so one about every 0.40 s (0.38 s without load) | cascade-load.md, step2-bricks.md |
| Bridge call, Python to MCU and back | median 5.7 ms, p95 5.9 ms (n = 200, built-in matrix only) | bridge-latency.md |
| Line from the bank | no generation at play time (D4); lookup time not measured | |
| First audio out after a decision | 132 to 142 ms from starting `aplay` to the beep reaching the mic (5 runs); 116 to 122 ms with an `aplay` process already open and fed silence (5 runs) | play latency section below |
| Camera frame to visitor detection | not measured (the stand-in model fired only 56 callbacks in 30 min with nobody in view) | |
| Jaw and eye response on the MCU | not measured (hardware not built) | |
| Mic muted during playback and tail | length of tail not chosen | mic-and-speaker.md |

Reading it: the model stages cost about 0.1 s each, and the Bridge is negligible. The unmeasured stages (audio start, detection delay, window cadence under load) will decide how fast the gargoyle feels, so they are the next measurements, in that order. A second language model request is out of the path altogether, since replies take 13 s under load (cascade-load.md) and 7 to 8 s alone (llm-threads.md), and 2 to 4 s only for a fully cached prompt (llm-probes.md).

## Play latency
Date: 2026-10-30, about 06:25 UTC (board clock). Same 4 GB board, idle, Ethernet, Speaker mixer 30 on the sound card (ALSA card 1), the Boya M1 on the same card recording at the same time. Speakers about 20 cm from the mic. `scripts/play_latency.py` runs on the board. It starts `arecord` (48 kHz, mono, read in 10 ms chunks with an arrival time), plays a 300 ms 1 kHz stereo beep, and takes the first chunk whose peak is over 4 times the idle peak and at least 2000 counts. Time is from the call (`Popen`, or putting the beep into a pipe) to that chunk's arrival in Python.

| Method | Runs (ms) |
|---|---|
| Start `aplay` with a WAV file each time | 142, 139, 137, 135, 132 |
| `aplay` kept open on a raw pipe, fed silence, beep swapped in (`--buffer-time=40000`, pipe 4096 B) | 122, 121, 119, 118, 116 |

A first attempt of the second method gave 395 to 516 ms because the default 64 KB pipe held about 340 ms of queued silence ahead of the beep; shrinking the pipe to 4096 B gave the figures in the table. The first attempt was not saved. Both figures include the microphone's own capture delay and the 10 ms chunking, which I did not separate, so the real time to sound is somewhat lower and the difference between methods (about 20 ms) is the safer number. The earlier run of the spawn method (before the pipe fix) gave 150 to 162 ms on the same setup, so run-to-run spread is about 20 ms. Not measured: other mixer levels, stereo panning, and playback while the cascade bricks are busy.

Playback starts in about 0.13 s either way, so keeping a stream open is not worth the extra code at this point. Still unmeasured: camera frame to detection (needs a person in view) and jaw or eye response on the MCU.
