# Costume and props models on the board

Board: Arduino UNO Q 4 GB, idle app, Ethernet. Both models are float32 `runner-linux-aarch64` builds from Edge Impulse Studio, run as separate `.eim` processes over unix sockets inside the `python-apps-base:0.13.1` container, one classify per frame (160 x 160 RGB).

| Model | Classes | Test set | Result | On-board time per frame |
|---|---|---|---|---|
| costume | pirate, princess, superhero, undead | 59 images | Studio 64.4 percent | about 100 to 115 ms |
| props | hat, glasses, crown, scarf, none | 287 images after cleanup | Studio 69.0 percent, argmax 70.4 percent | about 100 ms |

Props confusion (argmax, rows are truth): hat 83 of 102 right, glasses 87 of 108, crown 10 of 12, scarf 5 of 20, none 17 of 47. Scarf and none are the weak classes.

Props cleanup: a CLIP zero-shot check on the Studio samples removed 325 images that looked mislabeled (280 none, 42 hat, 3 glasses and scarf). The test set shrank from 386 to 287 images in the process, so the 66.8 percent before and 70.4 percent after are not on the same images. The check is the same kind of model that picked the images, so treat the gain as an upper bound.

Both runners loaded together with about 3.0 GB memory free and a load average under 0.1 at idle. Costume is tried first and props second (`costume.best`, gate 0.6). Thirteen sample costume photos, some possibly in the training set, gave 8 right with the new costume model and 1 to 2 with the older 11-class build.

Bug found on the board: the runner ends each reply with a NUL byte, so `json.loads` failed on the first real classify. `costume.py` now strips it.

Not measured: both models together with the camera, sound and keyword bricks running.
