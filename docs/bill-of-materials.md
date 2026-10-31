# Bill of materials

Quantities are for one unit. Substitute freely where the note says so.

## Compute and power

| Part | Qty | Notes |
|---|---|---|
| Arduino UNO Q, 4 GB | 1 | 4 GB is needed to run the models and the language model together |
| USB-C hub, powered, with power-delivery pass-through | 1 | The board has one USB-C port; the camera and microphone share it |
| USB-C PD supply for the board | 1 | A weak supply caused boot loops in earlier tests |
| 5 V 4 A supply for LEDs, mist and the paddle servo | 1 | Separate rail, shared ground with the board |
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
| WS2812B strip, 5 V, 60 LED per metre, black PCB (InLightss) | 1 | Spine plates. Cut at the pads into five pieces of three pixels (about 50 mm each), rejoined with 5 V, GND and data wires, arrows all pointing the same way. Filled tail to head as a level bar |
| 5 V ultrasonic mist maker board with 20 mm disc (Electronic Spices, micro-USB, no tank or fan) | 1 | Mouth fog. Needs its own water cup and a cotton wick or felt to the disc; it must never run dry. Own switched supply branch, low-side MOSFET with a pulldown so it is off by default |
| Small drip tray | 1 | Under the mist chamber; keeps water off the electronics. The mist rises to the mouth through a short open channel, no fan or tube |
| WS2812 7-pixel round boards (xcluma) | 2 | Eyes, behind translucent windows, 5 to 10 mm gap, dark collars. One spare owned |
| 74AHCT125 level shifter | 1 | 3.3 V logic to 5 V LED data |
| 1000 uF capacitor, 330 to 470 ohm resistor | 1 each | LED power and data protection |
| MG90S micro servo, 180 degree positional | 2 | Candy paddle (one in use, one spare). Calibrate the load and dump angles in firmware. |
| USB audio adapter and small speaker | 1 each | Optional, for spoken lines |

## Structure and finish

| Part | Qty | Notes |
|---|---|---|
| Stone-block plinth, printed panels or a box with a printed skin | 1 | Dry electronics bay with a back access door; the gargoyle crouches on top. Size to be set when the body is designed |
| Gargoyle shell: printed pieces, or paper pulp over a steel wire frame | 1 | Holds the sweet tube, paddle and chute in the torso; refill hatch on the back. Wire stays insulated and away from the boards and the 5 V rail; seal pulp against moisture |
| PETG | 1 spool | Candy path parts: sweet tube, paddle, chute, tongue slide |
| PLA | 1 spool | Head, torso, wings and mounts |
| Translucent white PETG | 1 spool | Spine plates and eye windows. Print a thickness swatch first |
| M3 screws, inserts, rubber grommets | as needed | Rubber grommets keep motor noise away from the microphone |
| Stone-texture spray, primer, paint | as needed | Keep paint off the tongue slide and chute |
| Small cauldron-style bowl | 1 | Catches the candy |

## Consumables

| Part | Notes |
|---|---|
| Individually wrapped soft toffees, one type | Avoid chocolate, lollipops and loose sweets |

## Power budget

Cap LED brightness in firmware (about 20 percent for the eyes and 50 percent for the spine) and verify the current draw with a meter before closing the enclosure.
