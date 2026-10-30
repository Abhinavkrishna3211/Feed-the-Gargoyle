# Bill of materials

Quantities are for one unit. Substitute freely where the note says so.

## Compute and power

| Part | Qty | Notes |
|---|---|---|
| Arduino UNO Q, 4 GB | 1 | 4 GB is needed to run the models and the language model together |
| USB-C hub, powered, with power-delivery pass-through | 1 | The board has one USB-C port; the camera and microphone share it |
| USB-C PD supply for the board | 1 | A weak supply caused boot loops in earlier tests |
| 5 V 4 A supply for LEDs, servo and stepper | 1 | Separate rail, shared ground with the board |
| Inline fuse and a kill switch | 1 each | On the 5 V rail |

## Sensing

| Part | Qty | Notes |
|---|---|---|
| USB webcam, wide angle, good low-light performance | 1 | Mounted between the eyes |
| Small USB microphone | 1 | Mounted in a carved ear cavity with a foam windscreen. Fix the gain. |
| IR break-beam pair | 1 | In the candy chute, confirms each drop |

## Output

| Part | Qty | Notes |
|---|---|---|
| WS2812B pixels, 15 (five plates of three) | 15 | Spine plates, filled tail to head as a level bar. Cut from a strip or use single pixels, wired in one chain |
| 5 V ultrasonic mist module with water tank | 1 | Mouth fog. Own switched supply branch, low-side MOSFET with a pulldown so it is off by default |
| Silicone tube, about 10 mm, and a small drip tray | 1 | Carries the mist to the mouth and keeps water off the electronics |
| WS2812 8x8 panels | 2 | Eyes |
| 74AHCT125 level shifter | 1 | 3.3 V logic to 5 V LED data |
| 1000 uF capacitor, 330 to 470 ohm resistor | 1 each | LED power and data protection |
| MG90S micro servo, 180 degree positional | 1 | Jaw. Calibrate the end stops in firmware. |
| 28BYJ-48 stepper with ULN2003 driver | 1 | Pocket wheel |
| USB audio adapter and small speaker | 1 each | Optional, for spoken lines |

## Structure and finish

| Part | Qty | Notes |
|---|---|---|
| Hollow craft pumpkin, about 30 cm | 1 | Body and candy hopper; the stem lid is the refill hatch |
| PETG | 1 spool | Candy path parts: wheel, housing, funnel, chute, tongue slide |
| PLA | 1 spool | Head, torso, wings and mounts |
| Translucent white PETG | 1 spool | Spine segments |
| M3 screws, inserts, rubber grommets | as needed | Rubber grommets keep motor noise away from the microphone |
| Stone-texture spray, primer, paint | as needed | Keep paint off the tongue slide and chute |
| Small cauldron-style bowl | 1 | Catches the candy |

## Consumables

| Part | Notes |
|---|---|
| Individually wrapped soft toffees, one type | Avoid chocolate, lollipops and loose sweets |

## Power budget

Cap LED brightness in firmware (about 20 percent for the eyes and 50 percent for the spine) and verify the current draw with a meter before closing the enclosure.
