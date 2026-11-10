"""Costume model from the Edge Impulse project, run as its own .eim process next to the bricks.

costume(frame_jpeg) -> (label, confidence). main.py hands it a JPEG of the latest frame the visitor brick read from the
camera, so the device still has a single reader. The .eim is copied to python/models/costume.eim (float32 build,
the int8 build crashes on the board, see docs/benchmarks/eim-on-board.md).
"""
import io, json, os, socket, subprocess, time
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
NONE = {"none", "empty"}  # the no-costume label: props calls it none, the 12-label costume model empty


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
    size = (mp["image_input_width"], mp["image_input_height"])  # 224 for costume, 160 for props

    def costume(frame_jpeg):
        px = np.asarray(Image.open(io.BytesIO(frame_jpeg)).convert("RGB").resize(size), dtype=np.uint32)
        feat = ((px[..., 0] << 16) | (px[..., 1] << 8) | px[..., 2]).ravel().tolist()
        scores = ask({"classify": feat, "id": 2})["result"]["classification"]
        label = max(scores, key=scores.get)
        return (None, 0.0) if label in NONE else (label, scores[label])
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
    print("costume ok")


if __name__ == "__main__":
    demo()
