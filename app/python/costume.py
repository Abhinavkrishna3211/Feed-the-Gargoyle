"""Costume model from the Edge Impulse project, run as its own .eim process next to the bricks.

costume(frame_jpeg) -> (label, confidence). The frame is the one the detector brick already hands over,
so the camera has a single reader. The .eim is copied to python/models/costume.eim (float32 build,
the int8 build crashes on the board, see docs/benchmarks/eim-on-board.md).
"""
import io, json, os, socket, subprocess, time
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SIZE = 160


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
        return json.loads(f.readline())
    ask({"hello": 1, "id": 1})

    def costume(frame_jpeg):
        px = np.asarray(Image.open(io.BytesIO(frame_jpeg)).convert("RGB").resize((SIZE, SIZE)), dtype=np.uint32)
        feat = ((px[..., 0] << 16) | (px[..., 1] << 8) | px[..., 2]).ravel().tolist()
        scores = ask({"classify": feat, "id": 2})["result"]["classification"]
        label = max(scores, key=scores.get)
        return (None, 0.0) if label == "none" else (label, scores[label])
    costume.proc = proc
    return costume


def best(*models):
    """Run every model on the frame, keep the most confident label. A model that is not installed is simply left out (None)."""
    models = [m for m in models if m]

    def pick(frame_jpeg):
        out = [m(frame_jpeg) for m in models]
        return max(out, key=lambda r: r[1], default=(None, 0.0))
    return pick


def demo():
    assert best(None)(b"") == (None, 0.0)
    assert best(lambda f: ("hat", 0.6), lambda f: ("witch", 0.8), None)(b"") == ("witch", 0.8)
    print("costume ok")


if __name__ == "__main__":
    demo()
