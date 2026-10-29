# Decision log

| ID | Decision | Reason | Status |
|---|---|---|---|
| D1 | Build a stationary gargoyle, not a moving statue | A wheeled base adds drivetrain, balance and collision risk around children without adding to the machine-learning content | Accepted |
| D2 | Use both UNO Q processors with clear roles | The MPU runs models and logic; the MCU owns real-time output and the safe state | Accepted |
| D3 | Edge Impulse models make the decisions; the language model only writes | Keeps behaviour measurable and lets every model be compared with a simple baseline | Accepted |
| D4 | Generate dialogue ahead of time and pre-render speech | Measured generation speed on the board is too slow to run during a visit | Accepted |
| D5 | Gemma 3 1B for the line bank, capped at 3 threads | It is the open-weight model available to the App Lab runner; 4 threads reset the board under full load | Accepted |
| D6 | Gate the sound and keyword models behind a visitor detector | Saves CPU and prevents false starts when nobody is present | Accepted |
| D7 | Candy path uses a pocket wheel and an IR break-beam sensor | Releases one candy at a time and confirms the drop without machine learning | Accepted |
| D8 | No accelerometer model | The break-beam and a timeout already handle jams, and a threshold handles tampering | Accepted |
| D9 | Costume feature is optional, speaks only when confident and defaults to silence | Limits the risk of wrong or unwelcome comments | Accepted |
| D10 | Riddles use a small fixed answer set | Keyword spotting is reliable on a few words and unreliable on open speech from children | Accepted |
| D11 | Training data from consenting adult volunteers only | Privacy; cloud tools receive no images of children | Accepted |
| D12 | Nothing is stored during play and nothing leaves the device | Privacy, and it works with no network | Accepted |
