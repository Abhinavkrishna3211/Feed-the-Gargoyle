# Roadmap

Each phase has exit criteria. A phase is finished when its criteria are met, not when time runs out.

## Phase 0: Repository and design

- [x] Design settled and documented
- [ ] Repository published with a clean history
- [ ] Edge Impulse projects created for each model

## Phase 1: Bench

Exit: the board, camera, microphone and speaker run stably together under load, and the candy mechanism works without the cosmetic parts.

- [ ] Microphone captures without clipping at the fixed gain
- [ ] Camera and microphone work through the powered hub
- [ ] `llama-server` runs supervised at 3 threads without resets
- [ ] Piper renders speech on the board
- [ ] Pocket wheel, jaw servo and drop sensor run from the MCU
- [ ] A loudness-threshold version of the game works end to end (the fallback)

## Phase 2: Data

Exit: datasets are collected, documented and split by person.

- [ ] Volunteers recruited, consent forms signed
- [ ] Sound recordings at three distances and several environments
- [ ] Adversarial and long-stream test sets recorded
- [ ] Visitor images captured at camera height
- [ ] Splits fixed and recorded

## Phase 3: Models

Exit: each model beats its baseline on held-out data.

- [ ] Sound classifier trained, calibrated and compared with the loudness baseline
- [ ] Visitor detector trained and gated
- [ ] Keyword spotter trained on the answer set
- [ ] Costume classifier trained (optional tier)
- [ ] Line bank generated, validated and rendered

## Phase 4: Integration

Exit: 50 consecutive clean visits.

- [ ] Game state machine integrated with all models
- [ ] Bridge contract finalised and tested
- [ ] Safe state verified by fault injection
- [ ] Enclosure assembled around the electronics

## Phase 5: Evaluation

Exit: every table in the [evaluation plan](evaluation-plan.md) is filled in.

- [ ] Claims 1 to 5 measured
- [ ] System measurements and a soak test of at least two hours

## Phase 6: Documentation

Exit: a reader can rebuild the project from the repository alone.

- [ ] Build and run instructions in the README
- [ ] Photos, wiring diagrams and a demo video
- [ ] Public Edge Impulse projects linked
- [ ] Write-up published

## If scope has to shrink

Cut in this order, and keep everything above the line:

1. Riddle mode
2. Costume classifier, then the worn-item detector
3. Spoken lines (show text on the eye panels instead)
4. Own visitor-detector training (use the App Lab face detection example)

Never cut: the sound classifier and its comparison with the baseline, the candy mechanism, and the MCU safe state.
