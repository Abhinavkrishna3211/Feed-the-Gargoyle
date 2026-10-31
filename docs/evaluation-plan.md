# Evaluation plan

The project makes a few specific claims. Each claim has a method, a baseline and a pass condition that is written down before the test is run. The numbers below are proposals to be confirmed when the first measurements exist.

## Claims and tests

### 1. The sound classifier beats a loudness threshold

- **Method:** run the classifier and a plain loudness threshold on the same held-out and adversarial recordings.
- **Baselines:** loudness threshold; a classical model on spectral features.
- **Metrics:** per-class precision and recall on unseen speakers; false accepts per hour on adversarial sounds at matched recall.
- **Pass:** at the same recall on held-out screams (proposal: at least 90 percent), the classifier's false accepts per hour on adversarial sounds are clearly lower than the loudness threshold's.
- **Also report:** how often a phone playing a scream fools the model.

### 2. The visitor gate saves compute and prevents false starts

- **Method:** run the same recorded scenarios (empty porch with ambient noise, people walking past, people standing in front) with and without the gate.
- **Metrics:** CPU use per stage, false wakes per hour, missed visitors, wake delay, and candy released with nobody present.
- **Pass:** lower CPU and fewer false starts with the gate, with no meaningful increase in missed visitors.

### 3. Generating lines while idle hides the language model's latency

- **Method:** measure time from a failed challenge to the first audio, using the pre-rendered bank, and compare with generating live.
- **Metrics:** latency, validator pass rate, retries per accepted line.
- **Pass:** playback starts without a perceptible wait.

### 4. The MCU fails safe

- **Method:** fault injection. Stop the MPU application, kill the Bridge, and unplug the camera and microphone mid-visit.
- **Metrics:** time from fault to safe state; behaviour of paddle, fog and bar.
- **Pass:** the safe state is reached within the configured limit every time, over repeated trials.

### 5. The costume feature is reliable when it speaks

- **Method:** held-out volunteers in costumes, ordinary clothes and traditional clothes.
- **Metrics:** precision when the classifier speaks; rate of speaking on everyday clothing.
- **Pass:** precision when speaking is high (proposal: at least 90 percent) and the classifier stays silent on everyday and traditional clothes.

## System measurements

- End-to-end latency from a visitor appearing to the eyes opening.
- Bridge call latency with the LEDs running.
- CPU, memory and temperature per stage, with the language model idle and active.
- On-device latency, RAM and flash for every Edge Impulse model, from Studio.
- A soak test of at least two hours with repeated visits.
- Candy mechanism: success and jam rate over 50 consecutive trials with the real candy.

## Method notes

- Capture long streams once and replay them through different thresholds, so results are comparable and repeatable.
- Use Edge Impulse Performance Calibration to choose the false-accept and false-reject trade-off, then confirm it on the long recording.
- Compare DSP block choices and use the EON Tuner with latency and RAM limits set for the UNO Q.
- Report the confusion matrix on unseen speakers and say how many speakers and clips each figure is based on.
