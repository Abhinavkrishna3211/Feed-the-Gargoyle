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
- [ ] Paddle servo and drop sensor run from the MCU
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
- [ ] Costume classifier trained and tested on held-out volunteers
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

## Quality bar

Everything planned ships, and it ships in good condition. Cut no feature. If time or hardware gets tight, shrink the breadth inside a feature and keep the feature:

- Fewer costume classes (start with the ones that recognise most reliably), but keep the costume classifier and the worn-item detector.
- Fewer riddles and answer words, but keep the keyword spotter.
- Start the visitor detector from the App Lab face detection example, then train our own.

A feature counts as done when it has measured accuracy on held-out data, a measured latency and RAM figure, a test, and a safe failure mode. Never cut: the sound classifier and its baseline comparison, the keyword spotter, the costume classifier, the language-model line bank, the candy mechanism, and the MCU safe state.
