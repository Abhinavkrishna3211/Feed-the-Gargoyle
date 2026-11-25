# Roadmap

Each phase has exit criteria. A phase is finished when its criteria are met, not when time runs out.

## Phase 0: Repository and design

- [x] Design settled and documented
- [x] Repository published with a clean history
- [x] Edge Impulse projects created for each model

## Phase 1: Bench

Exit: the board, camera, microphone and speaker run stably together under load, and the candy mechanism works without the cosmetic parts.

- [x] Microphone captures without clipping at the fixed gain ([mic-and-speaker](benchmarks/mic-and-speaker.md))
- [x] Camera and microphone work through the powered hub ([cascade-load](benchmarks/cascade-load.md))
- [x] `llama-server` runs supervised at 3 threads without resets ([llm-threads](benchmarks/llm-threads.md))
- [x] Piper renders speech on the board ([piper-render](benchmarks/piper-render.md))
- [x] Paddle servo and drop sensor run from the MCU ([paddle-and-mist](benchmarks/paddle-and-mist.md))
- [x] A loudness-threshold version of the game works end to end (it became the scream challenge, D28)

## Phase 2: Data

Exit: datasets are collected, documented and split. All data is from public datasets ([data card](../data/DATACARD.md)), so the volunteer items were dropped.

- [ ] ~~Volunteers recruited, consent forms signed~~ dropped, public datasets only
- [ ] ~~Sound recordings at three distances and several environments~~ dropped with the sound classifier (D28)
- [ ] Adversarial and long-stream test sets recorded
- [ ] ~~Visitor images captured at camera height~~ dropped, COCO 2017 instead
- [x] Splits fixed and recorded (by speaker, photographer or source)

## Phase 3: Models

Exit: each model beats its baseline on held-out data.

- [ ] ~~Sound classifier trained, calibrated and compared with the loudness baseline~~ dropped, the scream is judged on loudness (D28)
- [x] Visitor classifier trained and gated (91.8 percent, final)
- [x] Keyword spotter trained on the answer set (90.5 percent, final)
- [x] Costume classifier trained and tested on held-out images (172 of 186, 92.5 percent in Studio, final, timed on the board)
- [x] Props detector trained on head crops (Studio mAP@50 0.82 on 1,153 held-out crops, final)
- [x] Line bank generated, validated and rendered (164 lines, [piper-render](benchmarks/piper-render.md))

## Phase 4: Integration

Exit: 50 consecutive clean visits (done).

- [x] Game state machine integrated with all models
- [x] Bridge contract finalised and tested ([bridge-latency](benchmarks/bridge-latency.md))
- [x] Safe state verified by fault injection
- [x] Enclosure assembled around the electronics (every outcome played on the finished statue)

## Phase 5: Evaluation

Exit: every table in the [evaluation plan](evaluation-plan.md) is filled in.

- [ ] Claims 1 to 5 measured
- [x] System measurements and a soak test of at least two hours

## Phase 6: Documentation

Exit: a reader can rebuild the project from the repository alone.

- [x] Build and run instructions in the README
- [x] Photos, wiring diagrams and a demo video
- [ ] Public Edge Impulse projects linked
- [ ] Write-up published

## Quality bar

Everything planned ships, and it ships in good condition. Cut no feature. If time or hardware gets tight, shrink the breadth inside a feature and keep the feature:

- Fewer costume classes (start with the ones that recognise most reliably), but keep the costume classifier and the worn-item detector.
- Fewer riddles and answer words, but keep the keyword spotter.

A feature counts as done when it has measured accuracy on held-out data, a measured latency and RAM figure, a test, and a safe failure mode. Never cut: the keyword spotter, the costume classifier, the language-model line bank, the candy mechanism, and the MCU safe state.
