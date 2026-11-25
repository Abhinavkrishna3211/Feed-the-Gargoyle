"""Costume and props models from the Edge Impulse projects, each run as its own .eim process next to the bricks.

costume(frame_jpeg) -> (label, confidence). main.py hands it a JPEG of the latest frame the visitor brick read from the
camera, so the device still has a single reader. The .eim files are copied to python/models/ (float32 builds,
the int8 build crashes on the board, see docs/benchmarks/eim-on-board.md).

The props model is an object detector trained on head-and-shoulder crops, so make() runs YuNet (models/yunet.onnx, OpenCV
Zoo) on the frame first and cuts the same crop as the training data. A classifier .eim gets the whole frame as before.
"""
import io, json, os, socket, subprocess, time
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
NONE = {"none", "empty"}  # the no-costume label of the classifier builds
# Per-class score thresholds for props.eim (E7), tuned on the validation crops only.
THR = {"glasses": 0.45, "hat": 0.40, "scarf": 0.35, "crown": 0.55, "eye_mask": 0.15}
HOLD = 5  # props: a prop stays on for 4 calls after its last detection. Picked on validation sequences in the tracking study:
# on held-out it lifted presence F1 0.867 to 0.899 and cut flicker 0.37 to 0.02 per second with no added delay
S, UP, TILE, MIN_FACE = 3.2, 0.42, 160, 20  # head crop: side in face heights, share above the face centre; same rule as training


def crop_box(fb, w, h):
    """fb: x0,y0,x1,y1 face box in pixels. Returns the square head crop in pixels (may run past the image)."""
    s = S * max(fb[3] - fb[1], fb[2] - fb[0]); cx, cy = (fb[0] + fb[2]) / 2, (fb[1] + fb[3]) / 2
    return round(cx - s / 2), round(cy - UP * s), round(cx + s / 2), round(cy + (1 - UP) * s)


# Costume classifier crop around the face centre, in face sizes: medians of the C37 training crops against YuNet faces
# on their source photos (636 of 746 train photos with a face, notes/model-work/costume/work/STATE.md). Clipped to the
# frame, as the training crops were clipped to the photo.
BODY_SIDE, BODY_UP, BODY_DOWN = 2.25, 0.95, 7.8


def body_box(fb, w, h):
    """fb: x0,y0,x1,y1 face box in pixels. Returns the costume crop in pixels, inside the frame."""
    fw, fh = fb[2] - fb[0], fb[3] - fb[1]; cx, cy = (fb[0] + fb[2]) / 2, (fb[1] + fb[3]) / 2
    return (max(0, round(cx - BODY_SIDE * fw)), max(0, round(cy - BODY_UP * fh)),
            min(w, round(cx + BODY_SIDE * fw)), min(h, round(cy + BODY_DOWN * fh)))


def boxes_to_label(boxes, size, held):
    """Edge Impulse bounding_boxes (pixels at the model input) -> (label, confidence) after thresholds and the hold.
    held maps label -> [calls left, last confidence]. A score at its class threshold maps to 0.6, the gate in
    best() and game.py, so each class is judged at its own threshold; 1.0 stays 1.0."""
    for k in list(held):
        held[k][0] -= 1
        if held[k][0] <= 0:
            del held[k]
    for b in boxes:
        t = THR.get(b["label"])
        if t is None or b["value"] < t:
            continue
        conf = 0.6 + 0.4 * (b["value"] - t) / (1 - t)
        if b["label"] not in held or held[b["label"]][0] < HOLD or conf > held[b["label"]][1]:
            held[b["label"]] = [HOLD, conf]
    if not held:
        return None, 0.0
    label = max(held, key=lambda k: held[k][1])
    return label, held[label][1]


def make(path=os.path.join(HERE, "models", "costume.eim")):
    """One image .eim as its own process and socket; make(".../props.eim") gives the props model the same way."""
    SOCK = "/tmp/" + os.path.splitext(os.path.basename(path))[0] + ".sock"
    if os.path.exists(SOCK):
        os.remove(SOCK)
    proc = subprocess.Popen([path, SOCK], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(50):
        if os.path.exists(SOCK):
            break
        time.sleep(0.1)
    f = socket.socket(socket.AF_UNIX)
    f.connect(SOCK)
    f = f.makefile("rw")

    def ask(msg):
        f.write(json.dumps(msg)); f.flush()
        return json.loads(f.readline().strip(chr(0) + chr(10)))  # the runner ends each reply with a NUL byte
    mp = ask({"hello": 1, "id": 1})["model_parameters"]
    size = (mp["image_input_width"], mp["image_input_height"])  # 224 for costume and props
    detector = "object_detection" in str(mp.get("model_type", ""))
    from yunet import YuNet  # the App Lab OpenCV has no dnn module, so cv2.FaceDetectorYN cannot load
    face = YuNet(os.path.join(os.path.dirname(path), "yunet.onnx"))
    held = {}

    def run(img):
        px = np.asarray(img.convert("RGB").resize(size), dtype=np.uint32)
        feat = ((px[..., 0] << 16) | (px[..., 1] << 8) | px[..., 2]).ravel().tolist()
        return ask({"classify": feat, "id": 2})["result"]

    def costume(frame_jpeg):
        img = Image.open(io.BytesIO(frame_jpeg))
        bgr = np.asarray(img.convert("RGB"))[..., ::-1].copy()
        faces = [x for x in face.detect(bgr) if x[3] >= MIN_FACE]
        if not detector:  # crop the visitor as the training crops were; no face (a full mask) keeps the whole frame
            if faces:
                x, y, w, h = max(faces, key=lambda x: x[3])[:4]
                img = img.convert("RGB").crop(body_box((x, y, x + w, y + h), bgr.shape[1], bgr.shape[0]))
            scores = run(img)["classification"]
            label = max(scores, key=scores.get)
            return (None, 0.0) if label in NONE else (label, scores[label])
        if not faces:  # no face, no crop: let the held props run down
            return boxes_to_label([], size, held)
        x, y, w, h = max(faces, key=lambda x: x[3])[:4]
        c = crop_box((x, y, x + w, y + h), bgr.shape[1], bgr.shape[0])
        tile = img.convert("RGB").crop(c).resize((TILE, TILE), Image.BILINEAR)  # PIL pads past the edge with black, as training did
        return boxes_to_label(run(tile)["bounding_boxes"], size, held)
    costume.proc = proc
    return costume


def best(*models, gate=0.6):
    """Models in priority order, e.g. best(costume, props). The first one that is sure (>= gate) wins, so a confident
    costume beats a prop and a prop beats nothing. A model that is not installed (None) is left out."""
    models = [m for m in models if m]

    def pick(frame_jpeg):
        for m in models:
            label, conf = m(frame_jpeg)
            if label and conf >= gate:
                return label, conf
        return None, 0.0
    return pick


def demo():
    assert best(None)(b"") == (None, 0.0)
    assert best(lambda f: ("witch", 0.8), lambda f: ("hat", 0.9))(b"") == ("witch", 0.8)  # costume first
    assert best(lambda f: ("witch", 0.3), lambda f: ("hat", 0.7))(b"") == ("hat", 0.7)  # unsure costume falls back to the prop
    assert best(lambda f: ("witch", 0.3), lambda f: (None, 0.0))(b"") == (None, 0.0)  # nothing sure: the generic tease
    # props: a 100 px face at (100, 100) gives a 320 px crop with the face centre 42% down
    assert crop_box((100, 100, 200, 200), 640, 480) == (-10, 16, 310, 336)
    # costume: a 40 px face centred at (320, 100) gives 180 px wide, 38 px above, clipped at the frame bottom
    assert body_box((300, 80, 340, 120), 640, 480) == (230, 62, 410, 412)
    assert body_box((0, 0, 40, 40), 640, 480)[:2] == (0, 0)  # never runs past the frame
    box = lambda l, v, cx, cy: {"label": l, "value": v, "x": cx * 224 - 10, "y": cy * 224 - 10, "width": 20, "height": 20}
    held = {}
    label, conf = boxes_to_label([box("hat", 0.40, 0.5, 0.2)], (224, 224), held)
    assert label == "hat" and abs(conf - 0.6) < 1e-9  # at its threshold a class lands on the 0.6 gate
    assert boxes_to_label([box("hat", 0.39, 0.5, 0.2)], (224, 224), {}) == (None, 0.0)  # under it: nothing
    assert [boxes_to_label([], (224, 224), held)[0] for _ in range(HOLD)] == ["hat"] * (HOLD - 1) + [None]  # held, then gone
    held = {}
    boxes_to_label([box("glasses", 0.5, 0.5, 0.42), box("crown", 0.95, 0.5, 0.15)], (224, 224), held)
    assert boxes_to_label([box("glasses", 0.5, 0.5, 0.42)], (224, 224), held)[0] == "crown"  # the surer held prop still wins
    print("costume ok")


if __name__ == "__main__":
    demo()
