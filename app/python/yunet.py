"""YuNet face detector (OpenCV Zoo face_detection_yunet, models/yunet.onnx) on onnxruntime.

The App Lab container ships OpenCV without its dnn module, so cv2.FaceDetectorYN cannot load there. This decodes the
model the way OpenCV's face_detect.cpp does: the frame is padded (never stretched) to a multiple of 32, score =
sqrt(cls * obj), box centre from the anchor grid, size from exp, then NMS. models/yunet.onnx is the Zoo file with its
input height and width made symbolic so it runs at the frame's own shape. `size` caps the longest side; 640 is what
the props training and held-out crops used (at 480 or 320 it misses faces and the boxes move).
"""
import numpy as np
import onnxruntime as ort


class YuNet:
    def __init__(self, path, size=640, score=0.6, nms=0.3):
        self.s = ort.InferenceSession(path, providers=["CPUExecutionProvider"])
        self.size, self.score, self.nms = size, score, nms

    def detect(self, bgr):
        """bgr: HxWx3 uint8. Returns faces as rows of x, y, w, h, score in frame pixels, best first."""
        h, w = bgr.shape[:2]
        k = min(1.0, self.size / max(h, w))
        img = bgr if k == 1.0 else _resize(bgr, round(w * k), round(h * k))
        H, W = -(-img.shape[0] // 32) * 32, -(-img.shape[1] // 32) * 32
        pad = np.zeros((H, W, 3), np.float32)
        pad[:img.shape[0], :img.shape[1]] = img
        out = dict(zip([o.name for o in self.s.get_outputs()], self.s.run(None, {"input": pad.transpose(2, 0, 1)[None]})))
        rows = []
        for st in (8, 16, 32):
            r, c = np.divmod(np.arange((H // st) * (W // st)), W // st)
            sc = np.sqrt(np.clip(out[f"cls_{st}"][0, :, 0], 0, 1) * np.clip(out[f"obj_{st}"][0, :, 0], 0, 1))
            b = out[f"bbox_{st}"][0]
            bw, bh = np.exp(b[:, 2]) * st, np.exp(b[:, 3]) * st
            x, y = (c + b[:, 0]) * st - bw / 2, (r + b[:, 1]) * st - bh / 2
            rows.append(np.stack([x, y, bw, bh, sc], 1)[sc >= self.score])
        f = np.concatenate(rows)
        f = f[_nms(f, self.nms)]
        f[:, :4] /= k
        return f


def _resize(img, w, h):
    from PIL import Image
    return np.asarray(Image.fromarray(img[..., ::-1]).resize((w, h), Image.BILINEAR))[..., ::-1]


def _nms(f, thr):
    order, keep = list(np.argsort(-f[:, 4])), []
    while order:
        i = order.pop(0)
        keep.append(i)
        x0, y0 = np.maximum(f[i, 0], f[order, 0]), np.maximum(f[i, 1], f[order, 1])
        x1 = np.minimum(f[i, 0] + f[i, 2], f[order, 0] + f[order, 2])
        y1 = np.minimum(f[i, 1] + f[i, 3], f[order, 1] + f[order, 3])
        inter = np.clip(x1 - x0, 0, None) * np.clip(y1 - y0, 0, None)
        iou = inter / (f[i, 2] * f[i, 3] + f[order, 2] * f[order, 3] - inter)
        order = [j for j, v in zip(order, iou) if v <= thr]
    return keep


if __name__ == "__main__":  # usage: yunet.py yunet.onnx img.jpg... compares with cv2.FaceDetectorYN where cv2 has dnn
    import sys, cv2
    y, worst, n = YuNet(sys.argv[1]), [], 0
    for p in sys.argv[2:]:
        im = cv2.resize(cv2.imread(p), (640, 480))  # the camera frame size
        ref = cv2.FaceDetectorYN.create(sys.argv[1], "", (640, 480), 0.6, 0.3).detect(im)[1]
        got = y.detect(im)
        for a in [] if ref is None else ref:
            if a[3] >= 20:  # the faces the app uses
                worst.append((np.abs(got[:, :4] - a[:4]).max(1).min() if len(got) else 99) / a[3])
    worst = np.array(worst)
    assert np.mean(worst < 0.01) > 0.99 and np.median(worst) < 0.001, worst.max()  # NMS order can swap one overlapping face
    print("yunet ok,", len(sys.argv) - 2, "images,", len(worst), "faces;", int(np.sum(worst < 0.01)), "within 1% of face height")
