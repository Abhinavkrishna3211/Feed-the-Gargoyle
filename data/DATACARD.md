# Data card

All training data comes from public datasets. No visitor is ever recorded. Sources and counts are in the Edge Impulse projects.

| Dataset | Purpose | Source | Consent | Size | Split |
|---|---|---|---|---|---|
| Riddle keywords | Keyword spotter | Multilingual Spoken Words, Speech Commands, LibriSpeech, Piper voices, FSD50K noise | Public datasets | 569 test windows | By speaker or voice |
| Visitor images | Visitor classifier | COCO 2017, audited by eye | Public dataset | 475 test images | By COCO split |
| Costumes | Costume classifier | Openverse and Wikimedia Commons photos of adults (D16) | Public, logged in a manifest | 155 test images | By photographer |
| Worn items | Props classifier | Open Images V7, Openverse | Public datasets | 287 test images | By photographer |
| Long stream | False-accept measurement | Own recording of ambience | Notice posted | - | Test only |

For each dataset, also record the recording device and gain, the class list, the speaker count and the Edge Impulse project version.
