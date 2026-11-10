# Final costume model on the board

Board: Arduino UNO Q 4 GB on Wi-Fi, idle (no app running), measured 2026-11-10. Model: the 12-label costume classifier (EfficientNetV2B0, 224 x 224 RGB input), float32 `runner-linux-aarch64` build from Edge Impulse Studio, 36.9 MB. It runs as its own `.eim` process over a unix socket inside the `python-apps-base:0.13.1` container. SHA-256 is in `models/CHECKSUMS.txt`.

## Test set on the board

The 155 held-out test images were taken from Studio, squashed to 224 x 224 with bilinear resizing on the PC and sent over the socket, three passes (465 classifies).

| Measure | Result |
|---|---|
| Round trip per classify (socket, wall clock) | median 161 ms, p95 176 ms, max 290 ms |
| Runner start to first reply | 0.06 s |
| Runner memory (VmRSS) | 102 MB |
| Correct (argmax vs label) | 144 of 155 |
| Same top label as Studio | 152 of 155 |
| CPU temperature (`thermal_zone0`) | 42.1 C before, 51.8 C after the three passes |

Studio scores 141 of 155 on the same images. The three images where the board disagrees with Studio come from the resize: Studio scales the images itself and the board test used the PC's bilinear scaling, so the board's 144 is not a better model, only a different resize. The runner's own `timing.classification` field read 316 ms median, which is above the wall-clock round trip, so it is not used here.

## App path

`app/python/costume.py` (`costume.make`) on the board, same container:

- 20 test JPEGs (every eighth test image): 18 right.
- Live camera (Arducam, 640 x 480), 41 frames over 30 s, one every 0.5 s: median 227 ms and max 238 ms per frame for JPEG encode, decode, resize and classify. No costume in view: top score at most 0.14, under the 0.6 gate, so nothing was said.

The game asks for a costume at most once a second while a visitor is held, so 227 ms fits. Not measured yet: the costume model with the camera, sound and keyword bricks and the props model all running.

## Fixes found by this test

- `costume.py` had the input fixed at 160 px. This model takes 224 px. The size is now read from the runner's hello reply, so props (160 px) and costume (224 px) both get the right input.
- The new model calls its no-costume class `empty`, not `none`. Both now count as no costume.
