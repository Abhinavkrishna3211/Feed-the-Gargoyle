# References and credits

## Edge Impulse examples this design builds on

- Model cascade on the UNO Q (detector then recogniser): [mpous/ocr-linux-arduino-uno-q](https://github.com/mpous/ocr-linux-arduino-uno-q)
- Cascaded vision model and small language model on the UNO Q: [SolomonGithu/edge-ai-behavioral-coaching-assistant](https://github.com/SolomonGithu/edge-ai-behavioral-coaching-assistant) and its [write-up](https://docs.edgeimpulse.com/projects/expert-network/behavioural-coach-vision-model-cascade-slm-arduino-unoq)
- Continuous keyword spotting on the UNO Q with the App Lab microphone and the Linux runner: [Clawrophyll](https://docs.edgeimpulse.com/projects/expert-network/clawrophyll-on-device-wake-word-detection-using-keyword-spotting-arduino-unoq)
- Edge Impulse documentation: [Arduino UNO Q](https://docs.edgeimpulse.com/hardware/boards/arduino-uno-q), [deploying through Arduino App Lab](https://docs.edgeimpulse.com/hardware/deployments/run-arduino-app-lab), Performance Calibration and the EON Tuner
- [Edge Impulse Linux Python SDK](https://github.com/edgeimpulse/linux-sdk-python)

## Arduino platform

- [arduino/app-bricks-py](https://github.com/arduino/app-bricks-py): the microphone peripheral, audio classification brick and language model brick, read at source level
- Arduino App Lab, Bridge and the bundled bricks

## Models and tools

- Gemma 3 1B, open weights released by Google under the Gemma terms of use
- llama.cpp, MIT licence
- Piper text-to-speech; check the licence of the exact version and voice used

## Datasets under evaluation

- Fashionpedia (`detection-datasets/fashionpedia` on Hugging Face) for worn-item classes such as hat, hood and cape. Licence to be verified before use.
- Roboflow Universe hat and costume datasets. Licences vary; use only those that allow it and credit them.

## Earlier work by the author

Measurements and engineering patterns reused here come from earlier UNO Q projects:

- [Abhinavkrishna3211/jarvis-lab-assistant](https://github.com/Abhinavkrishna3211/jarvis-lab-assistant): language model and speech timings on the App Lab runner, Bridge and LED timing, microphone gain
- [Abhinavkrishna3211/Daybreak](https://github.com/Abhinavkrishna3211/Daybreak): supervised `llama-server` settings, the generate-validate-retry loop for language model output, thread and load measurements, and the capture-then-replay method for threshold sweeps
- [Abhinavkrishna3211/EleTect-X](https://github.com/Abhinavkrishna3211/EleTect-X): MCU and MPU split, microphone health checks, decision records and per-sample dataset manifests
- [Abhinavkrishna3211/ProjectPulse](https://github.com/Abhinavkrishna3211/ProjectPulse): measurement log format and host-side tests
- [Abhinavkrishna3211/Sloth-Clock](https://github.com/Abhinavkrishna3211/Sloth-Clock): App Lab app layout and the Bridge handler pattern

Any figure quoted from those projects is labelled with the board it was measured on and will be re-measured for this build.
