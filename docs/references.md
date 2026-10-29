# References and credits

## Edge Impulse examples this design builds on

- Model cascade on the UNO Q (detector then recogniser): [mpous/ocr-linux-arduino-uno-q](https://github.com/mpous/ocr-linux-arduino-uno-q)
- Cascaded vision model and small language model on the UNO Q: [SolomonGithu/edge-ai-behavioral-coaching-assistant](https://github.com/SolomonGithu/edge-ai-behavioral-coaching-assistant)
- Edge Impulse documentation on Performance Calibration, the EON Tuner and deploying to the UNO Q

## Models and tools

- Gemma 3 1B, open weights released by Google under the Gemma terms of use
- llama.cpp, MIT licence
- Piper text-to-speech; check the licence of the exact version and voice used
- Arduino App Lab, Bridge and the bundled bricks

## Datasets under evaluation

- Fashionpedia (`detection-datasets/fashionpedia` on Hugging Face) for worn-item classes such as hat, hood and cape. Licence to be verified before use.
- Roboflow Universe hat and costume datasets. Licences vary; use only those that allow it and credit them.

## Earlier work by the author

Measurements and engineering patterns reused here come from two earlier UNO Q projects:

- [Abhinavkrishna3211/jarvis-lab-assistant](https://github.com/Abhinavkrishna3211/jarvis-lab-assistant): language model and speech timings on the App Lab runner, Bridge and LED timing, microphone gain
- [Abhinavkrishna3211/Daybreak](https://github.com/Abhinavkrishna3211/Daybreak): supervised `llama-server` settings, the generate-validate-retry loop for language model output, thread and load measurements, and the capture-then-replay method for threshold sweeps

Any figure quoted from those projects is labelled with the board it was measured on and will be re-measured for this build.
