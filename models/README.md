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
| Costume classifier | Final. Costumes: batman, captain_america, iron_man, spiderman, superman, wonder_woman, pirate, princess, skeleton, witch, zombie, none |
| Props classifier | Worn items: hat, glasses, crown, scarf, none (still being improved) |
