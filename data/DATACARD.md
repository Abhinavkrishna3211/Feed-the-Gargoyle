# Data card

All training data comes from public datasets. No visitor is ever recorded. Sources and counts are in the Edge Impulse projects.

| Dataset | Purpose | Source | Consent | Size | Split |
|---|---|---|---|---|---|
| Riddle keywords | Keyword spotter | Multilingual Spoken Words, Speech Commands, LibriSpeech, Piper voices, FSD50K noise | Public datasets | 569 test windows | By speaker or voice |
| Visitor images | Visitor classifier | COCO 2017, audited by eye | Public dataset | 475 test images | By COCO split |
| Costumes | Costume classifier | Wikimedia Commons, Flickr and Openverse photos of adults, each person cropped out (D16) | Public, logged in a manifest | 970 images, 186 test | By source |
| Worn items | Props detector | Open Images V7, Fashionpedia, Openverse; head crops cut with YuNet, boxes checked by eye | Public datasets | 5,495 train, 1,153 test crops | By photographer |
| Long stream | False-accept measurement | Own recording of ambience | Notice posted | - | Test only |

For each dataset, also record the recording device and gain, the class list, the speaker count and the Edge Impulse project version.
