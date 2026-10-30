# App Lab bricks: what the docs say

Date: 2026-10-30
Source: files on the board, `/var/lib/arduino-app-cli/assets/0.13.1/` (`bricks-list.yaml` and `api-docs/arduino/...`), arduino-app-cli 0.14.0. Read only. No brick listed here was run for this note.

## Bricks we care about

| Brick | Id | Environment variables | Notes from the file |
|---|---|---|---|
| Audio classification | `arduino:audio_classification` | `EI_AUDIO_CLASSIFICATION_MODEL`, `CUSTOM_MODEL_PATH`, `BIND_ADDRESS` | Default model `glass-breaking`. Takes an optional `Microphone` and a confidence. |
| Keyword spotting | `arduino:keyword_spotting` | `EI_KEYWORD_SPOTTING_MODEL`, `CUSTOM_MODEL_PATH`, `BIND_ADDRESS` | Default model `keyword-spotting-hey-arduino`. |
| Object detection | `arduino:object_detection` | `EI_OBJ_DETECTION_MODEL`, `CUSTOM_MODEL_PATH`, `BIND_ADDRESS` | Candidate for the visitor gate. |
| Image classification | `arduino:image_classification` | `EI_CLASSIFICATION_MODEL`, `CUSTOM_MODEL_PATH`, `BIND_ADDRESS` | Candidate for costumes. |
| Sound generator | `arduino:sound_generator` | none | Synthesises notes with wave forms and effects (overdrive, chorus, ADSR, tremolo, vibrato, bitcrusher, octaver). Does not play recorded files. |
| Text to speech | `arduino:tts` | none | Lists only the `ventunoq` board and requires the `arduino:genie_audio` service. Not listed for the UNO Q, so Piper stays our own install. |

## Microphone selection

The `Microphone` class takes a `device` argument. It accepts an integer (the n-th plugged microphone, USB first, then jack), an ALSA name such as `hw:1,0` or `plughw:CARD=...,DEV=0`, a `/dev/snd/by-id/...` path, a PipeWire device, or a WebSocket URL. Default is 0. A brick given no microphone creates a default one, so with two USB mics attached (sound card and camera) the app should pass the device explicitly, not rely on index 0.

Measured on this board: the sound card captures mono at 44.1 or 48 kHz only, so a 16 kHz model needs a resample step, and the camera mic reads full scale in its first second after opening (`mic-and-speaker.md`). Whether the brick resamples, and whether it drops that first second, is not tested.

## Not tested yet

- Whether each brick starts with a custom `.eim` under `/home/arduino/.arduino-bricks/ei-models`.
- Whether the audio brick runs on the sound card, the camera mic, or both.
- Memory and CPU of each brick runner next to the language model.
- Whether the LLM brick passes `LLAMA_ARG_THREADS` through (`llm-threads.md`).

## Audio classification brick, run on the board

Date: 2026-10-29, about 21:38 UTC (board clock). A throwaway app with `arduino:audio_classification` and the pre-installed `glass-breaking` model called `classify_from_file(path, confidence=0.0)` on 48 kHz mono, 16-bit recordings from `mic-and-speaker.md`. The same app was started twice. The brick built in 0.18 to 0.25 s and the runner container (`ei-audio-classifier-runner`) came up healthy. First `app start` included the image already present on the board.

| File | Result | Call time (ms) |
|---|---|---|
| speech4-boya (noise off, speech) | Glass_Breaking, 52.35 | 235 and 219 |
| speech4-cam (noise off, speech) | Background, 99.95 | 175 |
| floor-fan-boya (noise on, no speech) | Glass_Breaking, 99.83 | 166 |
| speech4-boya with DC offset removed | Glass_Breaking, 52.35 | 167 |
| floor-fan-boya with DC offset removed | Glass_Breaking, 99.83 | 155 |

- CORRECTION, see the section at the end: these file results are not valid. `classify_from_file` does not resample or cut windows, so the model scored the first 16000 samples of a 48 kHz file (0.33 s) as if they were 16 kHz.
- The default glass model labels the Boya recordings as glass breaking, including a recording of fan noise only. The Arducam recording of speech came back as Background. Removing the Boya's DC offset (mean about 252 to 254 counts) changed nothing, so the offset is not the cause. The cause is not found. This model is not ours and was not trained for these inputs, so this is not a verdict on either mic. It is a reminder to train and test on recordings from the mic that will be used.
- Live microphone input is covered in the sections below.

### Rerun, same app, both mics

Second run of the same app on the same board, with two new 10 s recordings of the room with nobody speaking, made while the builder said the fan was on (`floor-fan2-*`). One call per file.

| File | Result | Call time (ms) |
|---|---|---|
| speech4-boya | Glass_Breaking, 52.35 | 223 |
| speech4-cam | Background, 99.95 | 177 |
| floor-fan-boya | Glass_Breaking, 99.83 | 176 |
| floor-fan2-boya | Glass_Breaking, 99.95 | 153 |
| floor-fan2-cam | Background, 99.91 | 169 |

The three files that were classified before gave the same class and confidence as in the first run. Every Boya recording of the room is called glass breaking and every Arducam recording is called Background, with or without speech. Five files, so this is a pattern in these recordings, not a rate. A test with the fan switched off is still to do.

### Rerun with the pedestal fan switched off

Two new 10 s recordings of the quiet room (`floor-nofan-*`), nobody speaking, same app, one call per file.

| File | Result | Call time (ms) |
|---|---|---|
| floor-nofan-boya | Glass_Breaking, 100.0 | 187 |
| floor-nofan-cam | Glass_Breaking, 100.0 | 140 |

With the fan off, the Arducam recording is also called glass breaking at 100%, where the same mic with the fan on was called Background. So the class follows the input level and the noise, not the mic: the default glass model calls a very quiet room glass breaking. The model has no class for that case, and a quiet room is the most common input in play, so a model trained on our own recordings must include silence and room noise in its "other" class.

## Live microphone through the brick

Date: 2026-10-29, about 21:55 UTC (board clock). Same throwaway app, now with `Microphone(device="hw:0,0")` (the Arducam mic) passed to `AudioClassification(mic=..., confidence=0.5)`, run under `App.run()` for 30 s. The room was quiet, nobody spoke, and the fan state was not confirmed by the builder at this point. One run.

- `start()` alone does nothing useful. The brick's reading and inference loops only run once `App.run()` has started the brick. A first attempt that called `start()` and slept produced 0 events in 30 s.
- Callbacks must be plain functions that take no arguments, not even a default one (`ValueError` otherwise). Keys are lower-cased.
- The model (`glass-breaking`) asks for 16000 Hz, 1 channel, a window of 16000 samples (1 s). The brick got 16 kHz features from the 48 kHz-capable camera mic without any resampling code in the app. The microphone log line names a `plug` ALSA device and says a requested buffer of 1024 frames is not supported and 2000 is used. How the resampling is done is not read from source beyond that.
- First inference started 1.39 s after the script started. Then one window every 2.15 s on average. That cadence comes from the brick's own debounce (2 s per class after a callback); the brick otherwise slides its window by 40% of the window length. Whether a detection of a different class would arrive faster than 2 s later is not tested.
- Inference call time (HTTP to the runner, measured around `infer_from_features`): 57 to 169 ms, median about 112 ms over 28 windows in 30 s. The callback ran right after the inference returned.
- Result: Background at 0.90 to 1.00 in every window, Glass_Breaking at most 0.10. The fan state was not confirmed for this run. The file test that seemed to disagree with this was invalid (see the correction at the end).
- The camera mic's start-up full-scale burst did not produce a false Glass_Breaking in this run. The first window already contained the first second.

## Correction: what classify_from_file really does

Read from the brick source in the `python-apps-base:0.13.1` image (`app_bricks/audio_classification/__init__.py`). `classify_from_file` unpacks every sample of the WAV into one list and sends it to the runner as features. It does no resampling, no channel mixing and no windowing. The model takes 16000 samples, so a 48 kHz file is scored on its first 16000 samples, 0.33 s of audio played back as if it were 16 kHz. For the Arducam mic that stretch is the start-up burst. So the file results above (all 5 + 2 + 2 rows) are not usable and I withdraw the conclusions drawn from them about "the Boya is called glass breaking" and "the Arducam is called Background".

Redone properly: one-second segments (seconds 5 and 7) cut from the same recordings, reduced to 16 kHz mono by averaging groups of three samples (a crude filter, no anti-alias design), then `classify_from_file` on each. One call per segment, `confidence=0.0`.

| Recording | Both segments, both mics |
|---|---|
| floor-fan, floor-fan2 (fan on, nobody speaking) | Background, 100.0 (8 of 8) |
| floor-nofan (fan off, nobody speaking) | Glass_Breaking, 99.99 (4 of 4) |
| speech5 (fan off; second 5 has part of a word, second 7 is quiet) | Glass_Breaking, 73.4 to 99.99 (4 of 4) |

- This agrees with the live runs: Background with the fan on, on both mics. The earlier disagreement between file and live results came from the file path, not from the model.
- It also shows the real model behaviour. With the fan off the room is so quiet (Arducam about -55 dBFS RMS, Boya about -42) that the default glass model calls it glass breaking at 99.99%, on both mics. The model has no sense of "quiet room" and answers glass. Our own classifier needs silence and quiet-room recordings in its "other" class and must be tested at several noise levels.
- Live run on the Boya M1 (`hw:1,0`), 30 s, same app and brick settings: Background 1.0 in every window, Glass_Breaking 0. Inference call 75 to 145 ms. The fan state was not re-confirmed by the builder for this run (they had been asked to turn it back on). Windows came about every 2.1 s, as with the camera mic.
- Not tested: live input with the fan off (it would probably give Glass_Breaking by the file result), and a model of our own. The sound card and camera mic both feed 16 kHz windows to the brick without app code.

### Live, fan off (builder said "fan off now")

Same app and settings, 30 s per mic, nobody speaking, one run each. Windows counted from the app's own per-window log.

| Mic | Windows | Windows with Glass_Breaking above 0.5 | Highest Glass_Breaking |
|---|---|---|---|
| Arducam mic (`hw:0,0`) | 29 | 28 | 1.0 |
| Boya M1 (`hw:1,0`) | 29 | 29 | 1.0 |

So the quiet-room result from the cut segments holds live: with the fan off the default glass model reports glass breaking in almost every window on both mics, and with the fan on it reports Background. The model separates by room noise level here, not by any sound of glass. The one window on the camera mic that did not exceed 0.5 was not examined.

## Keyword spotting brick, run live

Date: 2026-10-29, about 22:34 UTC (board clock). Throwaway app with `arduino:keyword_spotting`, default model `keyword-spotting-hey-arduino` (classes `background`, `hey_arduino`, `other`), `Microphone(device="hw:0,0")` (Arducam mic), `confidence=0.5`, `debounce_sec=0.0`, run under `App.run()`. Pedestal fan off, room quiet. The builder was told to say "Hey Arduino" about 5 times, about 3 s apart, then "feed the gargoyle" twice, starting at a beep played 25 s after the app started. One run, 247 windows over 98.5 s.

- Windows came about every 0.38 s. Inference call time: median 123 ms, p95 133 ms, max 171 ms (HTTP to the runner).
- Windows with `hey_arduino` at 0.3 or more: 8, at 4.7, 7.5, 11.2, 14.3, 17.9, 18.3, 21.2 and 23.5 s after the beep, with scores 0.98, 0.99, 0.82, 1.00, 0.60, 0.77, 0.81 and 0.88. The windows at 17.9 and 18.3 s are one utterance seen twice because debounce was 0. That makes 7 events about 3 s apart, which matches 5 "Hey Arduino" plus 2 "feed the gargoyle" if each utterance fired. That reading comes from the timing only; the builder did not log which phrase was said when, so the last two events (0.81 and 0.88) are probably the "feed the gargoyle" lines being taken for "Hey Arduino". Not confirmed.
- `other` reached 0.36 once (at 17.9 s). Every other window, including the 21 s before the beep, the beep itself and about 74 s after the speech, stayed at `background` with no class at 0.3 or above.
- The brick keeps `on_detect` callbacks keyed by lower-cased class name, as in the audio brick. The classes are `hey_arduino`, not "Hey Arduino".
- Not tested: a recording of the same phrase at other distances, a different speaker, the Boya M1, other phrases to count false accepts, and a model of our own with the riddle words. A fixed list of non-keyword phrases is needed to measure false accepts.
