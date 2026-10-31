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

## Cue clips and a speech line played through the speakers

Date: 2026-10-30, board clock about 17:40. Same board and placement as above. Speaker mixer 15, both mics recording 7 s at 48000 Hz mono (S16_LE) at their maximum gain, the clip started 1.2 s after the recording. One play per clip. The first second of the camera mic capture is the start-up burst and is ignored.
File levels (22050 Hz clips, dBFS): the greeting line RMS -15.3, peak -0.9; every effect clip RMS -18.4 (scaled by `scripts/sound_clips.py`), peak -4.9 to -1.8. The effects are about 3 dB below the speech line, near 70% of its amplitude.

| Clip | Boya M1 loudest second (peak / RMS) | Camera mic loudest second (peak / RMS) |
|---|---|---|
| greeting line | -21.5 / -33.9 | -15.2 / -31.3 |
| stone door | -23.1 / -35.4 | -23.0 / -34.4 |
| growl | -25.2 / -37.3 | -18.4 / -32.3 |
| long laugh (eviljest) | -20.1 / -33.8 | -13.2 / -27.4 |
| cave in (boom stand-in) | -22.1 / -35.0 | -19.0 / -30.6 |

No mic reached clipping (loudest peak -13.2 dBFS on the camera mic during the laugh). Quiet seconds sat near -39 dBFS RMS, so at mixer 15 the clips are only 2 to 12 dB above the room (growl on the Boya M1 about 2 dB, laugh on the camera mic 12 dB), and the Boya M1 hears the speakers 1 to 6 dB lower than the camera mic does by RMS. The camera mic and the Boya M1 do not hear equal levels from the same speaker, so any leakage rule needs to be set per mic. Not measured: other mixer values with these clips, speech heard by the mics while a clip plays (the cue rule is to stay silent while listening), and whether the clips sound right to a person.

### Same clips at mixer 27 (2026-10-30, about 17:55)
The builder reported the playback was very low at mixer 15 (15 of 30). At mixer 27 the greeting line reached the mics about 12 dB higher: Boya M1 loudest second -8.1 peak / -21.4 RMS, camera mic 0.0 peak (clipped) in two seconds of the line, RMS -18.7. The camera mic clipping from its own speaker is harmless while the cue rule holds (mics ignored during playback) but it means leakage rejection by level alone will not work at this volume. The long laugh read the same on both mics at mixer 15 and 27 (peaks -20.1 and -20.5 on the Boya M1, -13.2 on the camera mic both times); I could not explain that and did not repeat it. Not measured: mixer 20 to 24, which may be a better setting.

### Same clips at mixer 30, the maximum (2026-10-30, about 18:00)
Greeting line: Boya M1 loudest second -2.8 peak / -16.9 RMS (3 dB below clipping), camera mic clipped in two seconds, RMS -15.2. The long laugh again read about the same (Boya M1 -19.4 peak, camera mic -14.2). The builder said the level was good after this run. One play per clip; whether 27 would have been enough was not asked.

### Laugh volume (2026-10-30, about 18:10)
The builder said speech was good and the long laugh low at mixer 30. At the mic the plain laugh was about 13 dB below the greeting at the same mixer (Boya M1 loudest second -19.4 against -2.8 peak) although its file RMS is only 3 dB lower (-18.4 against -15.3 dBFS); 0.8 s of silence in front did not change it (-18.8 peak), so a start-up ramp is ruled out and the cause is unknown. A tanh limiter (`scripts/sound_clips.py --limit 6`, file RMS -7.4, peak -0.4 dBFS) read -12.0 peak / -24.5 RMS on the Boya M1, about 6 to 9 dB higher. One play each; the builder said the louder version was good.

### Other effects, plain and limited (2026-10-30, about 18:25)
Mixer 30, Boya M1, 6 s capture, one play each, loudest second peak / RMS in dBFS. Plain clips (RMS-matched at 0.12): growl -20.5 / -37.0, stone door -25.8 / -38.6, creaking hinge -20.8 / -36.1, roar -20.9 / -35.0, against the greeting line at -2.8 / -16.9. Limited with `sound_clips.py --limit 6`: growl -14.4 / -29.0, stone door -19.4 / -34.0, creaking hinge -16.3 / -32.0, roar -17.5 / -30.5. So the effects reach the mic about 15 to 23 dB below speech when plain and about 11 to 17 dB below when limited, with the room floor near -39 RMS. The limited stone door is still only 5 dB over the floor. No one listened to these yet; the builder's verdict covers the laugh only.

### Speech level and effect level pick (2026-10-31)
Board: Arduino UNO Q, 4 GB, over SSH. The builder's fan was off for the whole run. Speaker mixer set to 30 before every play. The speaker sits about 20 cm from both mics (reported by the builder, not measured). Both mics at maximum gain, 48000 Hz mono S16_LE. Each version played 8 lines (first line of greet, win, wrong_answer, too_quiet, timeout, announce_scream, witch, batman) in two passes, recorded on both mics at once, then read by Whisper base.en on the PC. The first second of the camera capture is ignored (start-up burst). Word error is edit distance against the known line, 16 lines per cell. The two passes differ by up to 6 points, so gaps under about 3 points are not a ranking.

Mixer finding: the Speaker control read 15,15 on the board before anything set it, and 30,30 after `amixer sset Speaker 30`. Some earlier quiet auditions were probably played at half level. `app/python/voice.py` now sets 30 before every play, not only at start.

Versions: O is the unprocessed bank. H1 to H4 are the same lines with plain gain to -11, -10, -9 and -8 dBFS RMS (speech samples above 0.02 only) and a soft knee above 0.7. A is the earlier loud bank (tanh limiter).

| Version | Clean file, 8 lines | Boya M1 | Camera mic | Boya peak | Camera mic clipped samples |
|---|---|---|---|---|---|
| O | 6.2% | 23.6% | 21.2% | 0.37 | 0 |
| H1 | 6.2% | 18.3% | 30.4% | 0.60 | 223 |
| H2 | 6.2% | 20.2% | 30.9% | 0.65 | 437 |
| H3 | 6.2% | 18.0% | 29.1% | 0.69 | 711 |
| H4 | 8.1% | 22.1% | 29.1% | 0.73 | 1001 |
| A | 8.1% | 25.5% | 36.6% | 0.57 | 281 |

Quiet floor, 12 s, nobody speaking, before and after the run: Boya M1 -41.6 and -41.9 dBFS RMS, camera mic -47.7 and -48.3.

Pick: voice at -9 dBFS RMS (H3), Boya M1 as the answer mic. The Boya never clipped on speech or effects. The camera mic clipped on every version except O, and on the effects (evil jest laugh 1284 samples, the two creaks 146 and 158), because its gain is at maximum; lowering it was not tried. The camera mic has the lower floor, about 6 dB. A person speaking or screaming at 1 m was not tested, so the mic pick is provisional until the speech-take comparison.

Effects (one play each, Boya M1, level of the played clip above the quiet floor, before the final level change): stone door 17 dB, growl 21, snarls 21 to 24, roar 19, laughs 22 to 25, creaks 23. The files were then set to -8 dBFS RMS, about 1 dB above the voice at -9. The old clips ranged from -3.7 to -13.3 dBFS, so the creaks were quieter than the voice and the laughs and door were much louder. The final -8 level has not been recorded on the mics; the numbers above are from the -9 set.

### Volume resets, clipped effects and camera mic gain (2026-10-31)
Board: Arduino UNO Q, 4 GB, over SSH, fan off, speaker 20 cm from both mics (reported, not measured).

Volume reset: the Speaker mixer of the USB card (ALSA card 1, control numid=6) went from 30 to 15 by itself several times. Cause found: `Linger=no` for user `arduino`, so each SSH login after the previous session had ended started a new user session, which started `pipewire` and `wireplumber`, and wireplumber set the card back to 15 (set to 30, new login 100 s later: read 15, wireplumber start time equal to the login time). Polling the mixer once a second for 40 s without a new login never showed a change. The first play after such a login was about 19 dB quieter (stone door peak 0.06 against 0.54 warm, camera mic). Fix: `systemctl --user mask --now wireplumber.service pipewire.service pipewire.socket pipewire-pulse.service pipewire-pulse.socket` as `arduino`. After it, two fresh logins 100 s apart both read 30,30, no pipewire process ran for `arduino`, and a play left the mixer at 30. The app talks to ALSA directly (`aplay -D plughw:1,0`). Undo with `systemctl --user unmask` on the same units. The system user `lightdm` still runs its own pipewire; it did not change the mixer. `voice.py` still sets 30 before each play.

Clipped effects: the files used until now were hard limited earlier, then only turned down, so 20 to 28 percent of their samples sat within 10 percent of the peak in the stone door, growl, roar and the laughs (flat tops). Rebuilt from the unlimited originals: 120 Hz high-pass (the speaker does not reproduce bass below about 150 Hz), gain set so the flat-top share stays under 1.5 percent, soft knee above 0.6. Result: RMS -10.7 to -14.4 dBFS (speech samples above 0.02), peak 0.95 to 0.98, flat-top share 0.2 to 1.1 percent. These are about 2 to 5 dB below the voice at -9. Listening verdict by the builder is pending.

Camera mic gain (Mic capture control of card 0, 0 to 256; 10 clips played at mixer 30, floor 12 s, camera first second ignored):

| Camera gain | Floor (dBFS RMS) | Mean level above floor | Clipped samples | Loudest peak |
|---|---|---|---|---|
| 256 | -47.4, -47.0 | 31.6, 31.3 dB | 2327, 2285 | 1.00 |
| 192 | -50.1 | 29.6 dB | 0 | 0.93 |
| 128 | -65.2 | 31.4 dB | 0 | 0.12 |
| 64 | -70.9 | 32.0 dB | 0 | 0.12 |

Boya M1 on the same clips: floor -40.8 to -41.7, 21.4 to 22.0 dB above floor, no clipping, peak 0.74 to 0.76. Whisper word error on the greeting and win lines was 46 to 56 percent at every gain and mic (two lines, recordings scaled to one peak), so gain did not change clarity. The floor falling 15 dB between 192 and 128 and the loudest peak falling from 0.93 to 0.12 suggest the control is not a smooth gain; not investigated. A real person at 1 m will be much quieter than the speaker at 20 cm, so which gain and which mic is not decided.

Boom: `boom_h` is the plain cave-in with the 30 to 140 Hz band turned into harmonics at 140 to 500 Hz, -10 dBFS RMS. Recorded on the Boya M1 it has 51 percent of its energy at 150 to 400 Hz against 7 percent for cave_in, and 3.4 percent at 50 to 150 Hz against 0.1. Its peak at the mic is lower (0.31 against 0.57). Listening verdict pending.

### Live voice test at 1 m (2026-10-31)
Board: Arduino UNO Q, 4 GB, fan off, both mics recording at once, builder standing about 1 m from the mics (reported, not measured). One take each of speech ("Who knocks at my stone door?"), scream, clap and whistle, 6 s, repeated with the camera mic at gain 192 and then 256. Boya M1 at its maximum. First second ignored. The silence take read -36.7 (Boya) and -37.5 (camera) dBFS, about 5 dB above the earlier quiet floors (-41 and -47), so the builder was probably not fully still and the "above floor" figures are low.

| Take | Boya peak / clipped | Camera peak / clipped | Whisper on the speech take |
|---|---|---|---|
| speech, camera gain 192 | 0.09 / 0 | 0.15 / 0 | Boya: "We'll knock at my storm door." Camera: "Will not set my stone door." |
| speech, camera gain 256 | 0.14 / 0 | 0.17 / 0 | Both: "Who knocks at my stone door?" (0 percent word error) |
| scream, 192 | 0.14 / 0 | 0.40 / 0 | n/a |
| scream, 256 | 0.08 / 0 | 0.14 / 0 | n/a |
| clap, 192 | 1.00 / 8 | 1.00 / 162 | n/a |
| clap, 256 | 1.00 / 9 | 1.00 / 47 | n/a |
| whistle, 192 | 0.19 / 0 | 0.23 / 0 | n/a |
| whistle, 256 | 0.33 / 0 | 0.62 / 0 | n/a |

One take per cell, so these are single observations. Speech was heard correctly on both mics only at camera gain 256; at 192 both mics misheard it, so the difference is more likely the take than the gain (the Boya setting did not change). The scream takes are weak (peaks 0.08 to 0.40, one Boya take almost empty), so the scream level at 1 m is not measured. Claps reach full scale on both mics; the camera mic clips more (47 to 162 samples against 8 or 9).

## Scream and clap redo, four takes each (2026-10-31)

Same board, speaker and both mics about 1 m from the person, Boya at its maximum (capture 28), camera mic at gain 256, 6 s per take, 4 rounds of scream and 4 of clap, fan off. Silence floor measured first: Boya -41.9 dBFS RMS, camera -48.9 dBFS RMS. "Active" is the RMS over 50 ms windows more than 3 times the floor. Single person, one room, so this shows the spread, not a limit.

| Take | Boya peak / clipped | Boya above floor | Camera peak / clipped | Camera above floor |
|---|---|---|---|---|
| scream 1 | 1.00 / 2383 | 32.9 dB | 0.97 / 0 | 30.7 dB |
| scream 2 | 0.94 / 0 | 21.5 dB | 1.00 / 22 | 31.7 dB |
| scream 3 | 0.54 / 0 | 16.3 dB | 0.88 / 0 | 26.5 dB |
| scream 4 | 0.91 / 0 | 22.4 dB | 1.00 / 146 | 32.4 dB |
| clap 1 | 1.00 / 131 | 28.4 dB | 1.00 / 705 | 34.6 dB |
| clap 2 | 1.00 / 16 | 24.1 dB | 1.00 / 112 | 29.9 dB |
| clap 3 | 1.00 / 12 | 22.4 dB | 1.00 / 82 | 28.4 dB |
| clap 4 | 1.00 / 5 | 23.3 dB | 1.00 / 56 | 30.5 dB |

- Scream: the camera mic is steadier, 26.5 to 32.4 dB above its floor. The Boya ranges from 16.3 to 32.9 dB, and one take clipped 2383 samples while another peaked at 0.54, so it depends more on how the person leans in.
- Clap: both mics reach full scale. The camera mic clips more samples (56 to 705 against 5 to 131) but sits 5 to 7 dB higher above its floor. A clap is a short click, so a few hundred clipped samples do not hide it.
- Speech was heard correctly on both mics at camera gain 256 (section above).

Pick: the Arducam built-in mic at gain 256 for play. It is the steadier mic for the scream, matches the Boya on speech and has the larger margin on claps. The Boya M1 stays as the fallback. Training audio for the scream and clap classes has to be recorded through the same mic and gain. Open: four takes per class from one person; the clipped scream takes (2 of 4 on the camera) should be watched when the sound model is tested with other voices.
