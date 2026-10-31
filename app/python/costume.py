"""Costume model from the Edge Impulse project, run as its own .eim process next to the bricks.

costume(frame_jpeg) -> (label, confidence). The frame is the one the detector brick already hands over,
so the camera has a single reader. The .eim is copied to python/models/costume.eim (float32 build,
the int8 build crashes on the board, see docs/benchmarks/eim-on-board.md).
"""
import io, json, os, socket, subprocess, time
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SOCK, SIZE = "/tmp/costume.sock", 160


def make(path=os.path.join(HERE, "models", "costume.eim")):
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
