# Decision log

| ID | Decision | Reason | Status |
|---|---|---|---|
| D1 | Build a stationary gargoyle, not a moving statue | A wheeled base adds drivetrain, balance and collision risk around children without adding to the machine-learning content | Accepted |
| D2 | Use both UNO Q processors with clear roles | The MPU runs models and logic; the MCU owns real-time output and the safe state | Accepted |
| D3 | Edge Impulse models make the decisions; the language model only writes | Keeps behaviour measurable and lets every model be compared with a simple baseline | Accepted |
| D4 | Generate dialogue ahead of time and pre-render speech | Measured generation speed on the board is too slow to run during a visit | Accepted |
| D5 | Gemma 3 1B for the line bank, capped at 3 threads | It is the open-weight model available to the App Lab runner. 3 threads leaves a core for the other models; a 16 minute run at 4 threads did not reset the board, so the earlier reset claim is unverified (docs/benchmarks/llm-threads.md) | Accepted |
| D6 | Gate the sound and keyword models behind a visitor detector | Saves CPU and prevents false starts when nobody is present | Accepted |
| D7 | Candy path uses a pocket wheel and an IR break-beam sensor | Releases one candy at a time and confirms the drop without machine learning | Accepted |
| D8 | No accelerometer model | The break-beam and a timeout already handle jams, and a threshold handles tampering | Accepted |
| D9 | Costume feature is core. It speaks only when confident and defaults to silence | Costume-aware roasts are a headline feature, and staying silent when unsure avoids wrong or unwelcome comments | Accepted |
| D10 | Riddles use a small fixed answer set | Keyword spotting is reliable on a few words and unreliable on open speech from children | Accepted |
| D11 | Training data from consenting adult volunteers only | Privacy; cloud tools receive no images of children | Accepted |
| D12 | Nothing is stored during play and nothing leaves the device | Privacy, and it works with no network | Accepted |
| D13 | Riddle keyword spotting is a core feature, not optional | Vision, keyword spotting, LEDs and a language model are the cascade the project is built around | Accepted |
| D14 | One audience setting for everyone: content written for children, teenagers and young people, no age or size classification | Visitors are a mix and adults enjoy it too. Skipping the split avoids collecting child data and avoids misreading a short adult or a tall child (D11) | Accepted |
| D15 | Final build powers the board from a 45 W USB-C PD charger through a USB-C hub with PD pass-through; LEDs, servo, stepper and speakers stay on their own 5 V rail | The board has one USB-C port, so power and peripherals share the hub. Every benchmark so far used a 5 V 3 A iPhone charger and a Portronics Mport 51 whose pass-through rating is unknown (docs/benchmarks/cascade-load.md) | Proposed, check the hub rating and log the current with a USB meter |
| D16 | Costume training images come from web photos of adults (Openverse and Wikimedia Commons), with source, licence and author logged in a manifest; any accuracy claim for the deployed gargoyle needs a test set of real camera frames | No volunteers are available for photos and this is a hobby build, so all licences are accepted. Web photos are posed and well lit, so accuracy on them does not predict accuracy in front of the gargoyle camera. Children are excluded as in D11. The public repo holds the manifest and fetch script, not the images | Accepted, amends D11 for the costume images only (sound data rules unchanged) |
