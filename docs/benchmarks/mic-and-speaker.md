# Microphone levels and speaker leakage

Date: 2026-10-30 (board clock)
Board: Arduino UNO Q, 4 GB, Debian 13 image 20260528-558, arduino-app-cli 0.14.0, over SSH on Ethernet. No app running. Power: an iPhone charger through the powered hub, rating not read.
Devices: Boya BY-M1 on the USB sound card (Generalplus 1b3f:2008, ALSA card 1), and the microphone of the Arducam B0490 camera (ALSA card 0). Speakers on the sound card output, one each side. The mics sit between the speakers, about 20 cm from each (reported by the builder, not measured with a rule). The builder's pedestal fan in the room was on throughout every capture. The builder said "without fan" before the quieter take and "my fan is back" before the next one, and suspected the laptop fan; which source changed between takes is not confirmed.
Capture: `arecord`, S16_LE, mono, 48000 Hz, both mics at once. Levels from `lvl.py` per second, in dBFS. Both mics were at their maximum gain (+30 dB on the sound card, 0 to 256 range on the camera at its top step). The camera mic was not checked at other gains.

## Speaker leakage

Stereo test tones (left, right, both) played on the sound card at Speaker mixer 15 and 30, six seconds recorded with the tone starting after 1.5 s. One run per setting. The files are `leak50-*` and `leak100-*` on the board (the names predate the mixer values and are not percentages).

| Mixer | Boya M1, loudest second (peak / RMS) | Arducam mic, loudest second (peak / RMS) | Quiet seconds RMS |
|---|---|---|---|
| 15 | -23.5 / -33.2 | -20.9 / -32.4 | about -39 |
| 30 | -8.6 / -15.5 | -8.2 / -15.6 | about -39 |

The tone is about 6 dB above the room noise at mixer 15 and about 24 dB above it at mixer 30. The camera mic reads 0 dBFS in the first second of every capture (start-up burst), so that second is ignored.
Not measured: left and right speaker separately, a spoken line instead of a tone, and any distance other than the present placement.

## Speech at about 1 m

One take: a beep, then "feed the gargoyle" said three times with pauses, 12 s recorded. Speech showed up in seconds 1, 2 and 4 (from 0).

| Mic | Speech seconds RMS | Quiet seconds RMS | Margin | Loudest peak in speech |
|---|---|---|---|---|
| Boya M1 | -27.0 to -28.1 | -37.3 to -39.5 | about 10 to 11 dB | -9.7 |
| Arducam mic | -25.5 to -27.7 | -35.4 to -38.7 | about 9 to 11 dB | -10.7 |

The mics agree within about a dB on this take. One take cannot rank them. An earlier take (`speech2`) showed no clear speech and is not used. Second 0 of the Boya capture (-9.2 peak) may be the beep tail and is ignored.

## Speech at about 1 m, quieter room

Same script, same placement and gains, the builder reported switching something off (see the note under Devices), one take (`speech4`). Speech was in seconds 0 to 4, quiet from second 5.

| Mic | Speech seconds RMS | Quiet seconds RMS | Margin | Loudest peak in speech |
|---|---|---|---|---|
| Boya M1 | -33.0 to -37.3 | -41.8 to -42.4 | about 5 to 8 dB | -18.6 |
| Arducam mic | -36.0 to -40.9 | -50.4 to -54.5 | about 10 to 17 dB | -15.6 |

The speaker said the line more quietly or from further away than in the first fan-room take (speech RMS about 9 dB lower on both mics), so margins cannot be compared between takes. Within this take the Arducam mic has the larger margin because its quiet floor fell about 15 dB without the fan, against about 4 dB for the Boya M1. So most of the noise on the camera mic came from whatever was switched off, and the Boya floor (steady near -42 dBFS) looks like its own noise or the sound card. The latter is untested.

## Quiet floor, noise back

10 s, nobody speaking, same placement and gains, the noise back (`floor-fan-*`), one run, after the quieter take.

| Mic | RMS per second, range (dBFS) | Quieter take, quiet seconds (dBFS) |
|---|---|---|
| Boya M1 | -38.1 to -39.6 | -41.8 to -42.4 |
| Arducam mic | -32.5 (second 1) falling to -38.6 | -50.4 to -54.5 |

The noise that came back costs the Boya about 3 to 4 dB and the Arducam mic about 12 to 18 dB. The Arducam floor drops over the first seconds of a capture in this run (-32.5 to -38.6) and in the earlier first fan-room takes, so it may settle after opening. That is untested; it would matter for how long the camera mic has to be open before it is used.

Repeat, 10 s, nobody speaking, after the builder said the fan was on again (`floor-fan2-*`): Boya -37.9 to -39.2 dBFS RMS, Arducam mic -32.6 to -37.3 after the first second. This matches the run above within about 2 dB on both mics, so the two noisy floors repeat and the quieter take (Arducam -50 to -54) is a different condition, not drift. Still one run per condition.

## What follows

- The listening path must be muted while sound plays, plus a short tail.
- The limit is the noise floor, not gain. The camera mic floor was much lower in the quieter take; any fan in the enclosure will matter.
- Choosing a mic is left to step 5, on keyword accuracy. Repeat the speech takes at a measured distance and a fixed loudness before using the margins.

## Quiet floor, pedestal fan switched off

10 s, nobody speaking, same placement and gains, the builder's pedestal fan switched off before the run (`floor-nofan-*`), one run.

| Mic | RMS per second (dBFS), first second dropped | Peak range (dBFS) |
|---|---|---|
| Boya M1 | -41.5 to -41.9 | -37.3 to -38.2 |
| Arducam mic | -47.5 (second 1), then -53.9 to -56.1 | -37.8 to -43.3 |

The Arducam floor is 17 to 21 dB lower than with the fan on (-32.6 to -37.3) and matches the earlier quieter take (-50 to -54). The Boya floor is only about 3 to 4 dB lower and steady near -42, so it looks limited by its own noise or the sound card. With the fan off, the Arducam mic is about 14 dB quieter than the Boya M1. The Boya mean offset is 267 counts here (252 to 254 earlier). The Arducam floor again falls over the first seconds after opening (-47.5, then below -53.9).

## Speech at about 1 m, pedestal fan off

Same script and placement, fan switched off before the run, one take (`speech5`). Speech bursts fall in seconds 0, 2 and 4 (from 0), about 2 s apart; second 0 of both captures is ignored (beep tail, and the Arducam start-up burst), so two bursts are scored.

| Mic | Speech seconds RMS (2 and 4) | Quiet seconds RMS | Margin | Loudest peak in speech |
|---|---|---|---|---|
| Boya M1 | -29.3 and -33.0 | -41.6 to -42.6 | about 9 to 13 dB | -14.6 |
| Arducam mic | -28.8 and -33.1 | -52.3 to -55.5 | about 19 to 27 dB | -11.8 |

Speech level is nearly the same on the two mics (within about 0.5 dB at second 2 and 0.1 dB at second 4), so with the fan off the larger margin on the Arducam mic comes from its lower floor, not from hearing the speech better. Speech peaks stay below -11 dBFS on both at maximum gain. Seconds 1 and 5 hold partial speech or the tails of words and are not scored. Still one take, one speaker, an unmeasured distance of about 1 m.

## Speaker order
2026-10-30, Speaker mixer 20. A 0.4 s 800 Hz tone on the left channel only, then the same tone twice on the right channel only (`aplay` to `plughw:1,0`, stereo). The builder reported "left" when asked which speaker made the single beep, taken as the speaker on the left when facing the gargoyle's front. They did not name the double-beep side, and the facing direction was an assumption from my question. So channel 0 (left) plays on the left speaker.
