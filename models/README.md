# models

Notes for the Edge Impulse model builds. Model binaries (`*.eim`) are not tracked in git.

For every model, record here:

- the Edge Impulse project name and the impulse design (input, processing block, learning block);
- the dataset version and split;
- accuracy on the held-out test set, and on-device latency, RAM and flash;
- the build date and the SHA-256 of the deployed file, copied into `CHECKSUMS.txt`.

| Model | Task |
|---|---|
| Visitor detector | FOMO person and face detection |
| Sound classifier | Scream, howl, growl, other |
| Keyword spotter | Riddle answers |
| Costume classifier | Worn items and costumes |
