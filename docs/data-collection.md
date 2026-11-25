# Data collection

## Principles

- All training and test data comes from public datasets, listed in [data/DATACARD.md](../data/DATACARD.md). No volunteers were recorded and no visitor is ever recorded. The volunteer protocol further down was the original plan and was not used.
- Children are not recorded for training and no images of children are uploaded to cloud tools.
- Train, validation and test splits are made by speaker, voice, photographer or source, never by clip, and are fixed before any training run.
- The microphone, gain and mounting match the final build. Peak levels are logged and clipped clips are rejected.

## Sound events

| Class | Contents |
|---|---|
| `scream` | Screams at several intensities |
| `howl` | Wolf and ghost style howls |
| `growl` | Low growls |
| `other` | Claps, bangs, shouted and normal speech, laughter, music, the machine's own servo and speaker noise, room and porch ambience, silence |

A recording played back from a phone is not a training class. It is a test condition, and the evaluation reports how often it fools the model.

## Riddle keywords

A small fixed answer set of six words (currently shadow, pumpkin, mirror, candle, spider, scarecrow: two or three syllables, different first sounds, no rhymes) plus `noise` and `unknown`. Every riddle offers a few of these words as its possible answers, so recognition never has to handle open speech.

## Visitor classifier

Two classes, visitor and empty, from COCO 2017, every label audited by eye. Hard empty scenes (statues, screens, mirrors, animals, figurines) were added as negatives.

## Costume and worn-item classifier

- Worn items (props detector, boxes on a head crop): crown, eye_mask, glasses, hat, scarf.
- Costumes (costume model): batman, captain_america, iron_man, spiderman, superman, wonder_woman, pirate, princess, skeleton, witch, zombie.
- `none` is the default and covers ordinary and traditional clothing. The classifier speaks only above a confidence threshold.
- Photos of adults only, from public datasets (see [data/DATACARD.md](../data/DATACARD.md)). Children, dolls, statues and cartoons were removed by eye.

## Recording protocol

- Distances: 0.5 m, 1 m and 2 m from the microphone.
- Environments: a quiet room, a porch or outdoor space with normal ambient noise, and a noisy setting.
- Target: 12 to 15 volunteers, with at least 5 held out entirely for testing.
- Metadata for every clip: `speaker_id`, `distance_m`, `environment`, `gain`, `device`, `date`.

## Test sets

1. **Unseen speakers:** the held-out volunteers.
2. **Adversarial sounds:** claps, bangs, shouted speech, music, phone playback of screams, the gargoyle's own noises.
3. **Long stream:** at least one to two hours of recorded ambience with labelled events, used to measure false accepts per hour and to confirm calibration.

## Storage

Raw recordings stay outside version control (`data/raw/` is ignored). This repository keeps the documentation only. Volunteers can ask for their data to be deleted at any time.
