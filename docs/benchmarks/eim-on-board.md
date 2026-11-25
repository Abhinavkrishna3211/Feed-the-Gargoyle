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

## The costume builds from the Enterprise project crash too (2026-11-25)

Board: Arduino UNO Q 4 GB, Debian 13 image 20260528-558. Each costume `.eim` run directly as above, one `hello`, then one `classify` of a flat grey 224 x 224 frame:

| Build | Project | Result |
|---|---|---|
| C30, EfficientNetV2B0, float32 | personal project | answers |
| C34, Studio EfficientNet B0 block, float32 | Enterprise project | segmentation fault |
| C37, Studio EfficientNet B2 block, float32 | Enterprise project | segmentation fault on the first classify |
| C39, same setup as C37 retrained, float32 | Enterprise project | segmentation fault on the first classify (signal 11, also with `ulimit -s unlimited`) |

The network itself is fine. The C39 float32 `.tflite` from Studio's dashboard downloads, run with LiteRT (`ai-edge-litert` 2.4.0) inside the app's own `python-apps-base:0.13.1` image on the board, on Studio's 186 test windows (`dsp-data` testing features scaled back to 0 to 255):

| Delegate | Threads | Load | Correct | Median ms | p95 ms |
|---|---|---|---|---|---|
| XNNPACK | 4 | no app running | 172/186 | 158.5 | 160.7 |
| none (built-in kernels) | 4 | no app running | 10/186 (input left at 0 to 1) | 321.4 | 324.6 |
| XNNPACK | 2 | full gargoyle app running | 172/186 | 362.1 | 466.8 |

172/186 is Studio's own top-answer count for C39. The second row was run before the input scale was found and only shows that the plain kernels do not crash either. So the app loads the costume model as `app/python/models/costume.tflite` with LiteRT at 2 threads (D33), and the props detector stays an `.eim`. Cause of the runner crash not found.
