# Custom .eim models on the board

Date: 2026-10-31. Board: Arduino UNO Q 4 GB, App Lab 0.13.1 bricks (ei-models-runner 0.13.0 containers). Models: Linux aarch64 builds from the Edge Impulse projects, exported through the Studio API (`build-ondevice-model`, type `runner-linux-aarch64`, engine tflite). Each result below is one run unless it says otherwise.

## Loading through the bricks

The files sit in `/home/arduino/.arduino-bricks/ei-models/`, which is the default `CUSTOM_MODEL_PATH` of the bricks. The brick takes the file name from an `app.yaml` variable:

| Brick | Variable |
|---|---|
| video_object_detection | EI_V_OBJ_DETECTION_MODEL |
| audio_classification | EI_AUDIO_CLASSIFICATION_MODEL |
| keyword_spotting | EI_KEYWORD_SPOTTING_MODEL |

All three runner containers started with the project's own files and reported the project name and class list in their logs. The Python app has no `pw-dump` (PipeWire is masked on the image), so the audio bricks must be given `Microphone(device="hw:N,0")`; the default device index fails with `Failed to enumerate audio devices via pw-dump`.

## int8 builds crash on classify

Run directly on the board (`./model.eim /tmp/x.sock`, one JSON `hello`, then one `classify` with zeros):

| Model | Build | Result |
|---|---|---|
| keywords (MFCC, 16000 samples) | int8 | segmentation fault on the first classify |
| keywords | float32 | answers, dsp 6 ms, whole message 10 ms |
| costume (160 x 160 RGB) | int8 | segmentation fault on the first classify |
| costume | float32 | answers |
| visitor (FOMO) | int8 | runs for several minutes inside the video brick |

So the keywords, costume and sound files deployed here are the float32 builds. Cause not found; the Studio int8 evaluation of the same models ran without error.

## Four models at once

The real app (`gargoyle`, `python/sensors.on` present) with the video, audio and keyword bricks plus the costume process, camera at 10 FPS, no visitor in front. `docker stats --no-stream` and `free -m` taken once, about 60 s after start:

| Container | CPU | Memory |
|---|---|---|
| main (Python app and costume.eim) | 48 % | 99 MiB |
| video runner (visitor) | 95 % | 159 MiB |
| audio runner (sound) | 16 % | 106 MiB |
| keyword runner | 9 % | 106 MiB |

`free -m`: 1164 MB used, 2502 MB available of 3667 MB. The video runner's health check read `unhealthy` once the camera client was connected (the check tests that port 5050 is listening and the server takes one connection); it kept detecting frames. CPU percent is per core, so 95 % is about one core.

## Camera sharing

Only the detector brick reads the camera. With `camera_preview=True` its callback also receives each frame as JPEG bytes (about 88 kB at the default size), and the costume model is called on that frame at most once a second. No second consumer opens the camera.
