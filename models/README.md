# models

Notes for the Edge Impulse model builds. Model binaries (`*.eim`) are not tracked in git.

For every model, record here:

- the Edge Impulse project name and the impulse design (input, processing block, learning block);
- the dataset version and split;
- accuracy on the held-out test set, and on-device latency, RAM and flash;
- the build date and the SHA-256 of the deployed file, copied into `CHECKSUMS.txt`.

| Model | Task |
|---|---|
| Visitor classifier | Visitor or empty scene (final) |
| Sound classifier | Dropped (docs/decisions.md D28), not deployed |
| Keyword spotter | Riddle answers (final) |
| Costume classifier | Final (C39). Costumes: batman, captain_america, iron_man, spiderman, superman, wonder_woman, pirate, princess, skeleton, witch, zombie, none. Project gargoyle-costume: 224x224 squash, Image (RGB), Transfer Learning EfficientNet B2 (pretrained, freeze 70 percent, 40 cycles, lr 0.0005, batch 16, dropout 0.3, flip/crop/brightness, 15 percent validation, GPU). 970 images, 784 train / 186 test, fixed split by source. Validation 90.7 percent; test 172 of 186 top answer (92.5 percent), 88.17 percent in Studio's own count with uncertain answers, float32. Studio estimate on the UNO Q: 337 ms float32, 537 ms int8. float32 .eim 44.3 MB, built 2026-11-25, sha256 3ec9ff4a...1d26759d. Board timing to come |
| Props detector | Final (E7). Object detection on a head crop: crown, eye_mask, glasses, hat, scarf |
| Face finder | `app/python/models/yunet.onnx` (tracked, MIT licence), for the props head crop (below) |

## yunet.onnx

The props detector looks at a crop around the largest face. The face comes from YuNet,
`face_detection_yunet_2023mar.onnx` from the OpenCV Zoo, run with onnxruntime by `app/python/yunet.py` because the App Lab
OpenCV has no dnn module. It ships in `app/python/models/`, so copying the app installs it. The Zoo file has a fixed 640 x 640 input; the deployed copy has its input height and width
made symbolic, so it runs at the frame's own shape, as OpenCV does:

```python
import onnx
m = onnx.load("face_detection_yunet_2023mar.onnx")
for d, n in zip(m.graph.input[0].type.tensor_type.shape.dim[2:], "hw"): d.ClearField("dim_value"); d.dim_param = n
for o in m.graph.output:
    for d in o.type.tensor_type.shape.dim: d.ClearField("dim_value"); d.dim_param = "n"
del m.graph.value_info[:]
onnx.save(m, "yunet.onnx")
```
