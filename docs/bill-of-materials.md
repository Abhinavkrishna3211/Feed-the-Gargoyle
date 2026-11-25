# Bill of materials

Quantities are for one unit. Substitute freely where the note says so.

## Compute and power

| Part | Qty | Notes |
|---|---|---|
| Arduino UNO Q, 4 GB | 1 | 4 GB is needed to run the models and the language model together |
| USB-C hub, powered, with power-delivery pass-through | 1 | The board has one USB-C port; the camera and microphone share it |
| USB-C PD supply for the board | 1 | A weak supply caused boot loops in earlier tests |
| 5 V 4 A supply for LEDs, mist and the paddle servo | 1 | Separate rail, shared ground with the board |
| Inline fuse (2.5 A fast-blow) and a kill switch | 1 each | On the 5 V rail. Fuse sized from about 1.8 A worst case, to be confirmed with a meter |
| IRLZ44N logic-level N-MOSFET (TO-220) | 1 | Low-side switch for the mist maker, 100 ohm gate resistor and 10 k pulldown |

## Sensing

| Part | Qty | Notes |
|---|---|---|
| Arducam B0490 USB camera (IMX462, M12 3.9 mm lens) | 1 | Third eye in the forehead, held by its lens in a 14.2 mm bore (D23) |
| Small USB microphone | 1 | Mounted in a carved ear cavity with a foam windscreen. Fix the gain. |
| IR reflective sensor module, LM393 (FC-51 style) | 1 | Looks into the candy chute through a side window and confirms each drop. Far wall painted matte black, trimmer set on the bench. Powered from the UNO Q 3.3 V pin so OUT stays at 3.3 V logic |

## Output

| Part | Qty | Notes |
|---|---|---|
| WS2812B strip, 5 V, 60 LED per metre, black PCB (InLightss) | 1 | Spine plates. Cut at the copper pads into 24 single pixels, wired in eight groups of three (one group per spine plate) with 5 V, GND and data wires, arrows all pointing the same way. Filled tail to head as a level bar |
| 5 V ultrasonic mist maker board with 20 mm disc (Electronic Spices, micro-USB, no tank or fan) | 1 | Mouth fog. Needs its own water cup and a cotton wick or felt to the disc; it must never run dry. Own switched supply branch, low-side MOSFET with a pulldown so it is off by default |
| Small drip tray | 1 | Under the mist chamber; keeps water off the electronics. The mist rises to the mouth through a short open channel, no fan or tube |
| WS2812 7-pixel round boards (xcluma) | 2 | Eyes, in an open pocket behind the transparent cap printed with the head (D24). One spare owned |
| 1000 uF capacitor (6.3 V or more) | 1 | Across 5 V and GND where power enters the LED chains |
| 330 to 470 ohm resistor | 2 | One in each LED data line (D5 eyes, D6 spine), at the first pixel (D32) |
| SG90S micro servo, 180 degree positional | 2 | Candy paddle (one in use, one spare). Calibrate the load and dump angles in firmware. |
| USB audio adapter | 1 | Spoken lines and sounds |
| Small speaker, fits a 130 mm cube | 2 | One on each plinth end wall, left and right channel (D26) |

## Structure and finish

| Part | Qty | Notes |
|---|---|---|
| Stone-block plinth, printed panels or a box with a printed skin | 1 | Dry electronics bay with a back access door; the gargoyle crouches on top. Size to be set when the body is designed |
| Gargoyle shell: printed pieces, or paper pulp over a steel wire frame | 1 | Holds the sweet tube, paddle and chute in the torso; refill hatch on the back. Wire stays insulated and away from the boards and the 5 V rail; seal pulp against moisture |
| Grey PLA+ | 2 spools | Head, torso, wings, plinth, mounts and the candy path: sweet tube, rotor, chute, servo plate, shelf, tongue slide |
| Translucent PLA+ | 1 spool | Spine plates and the front of each eye cap. Print a thickness swatch first |
| M3 heat-set inserts, 5.7 mm long, for a 4.0 mm pocket | 4 | Gargoyle to plinth joint, one in each boss under the gargoyle (D22) |
| M3 x 16 socket head screws | 4 | Up through the plinth bosses into the inserts (D22) |
| M3 x 10 thread-forming screws for plastic | 3 | Hold the dispenser on its posts in the head (D25) |
| 6 x 2 mm disc magnets | 8 | Refill lid, four in the lid and four in the tabs. Glue in, mind the poles (D25) |
| 2.5 mm ball-end hex key, long arm | 1 | Reaches the joint screws through the bores from the bottom door |
| USB-C panel-mount extension, male to female, about 30 cm | 1 | Female end sits in the 14 x 7.5 mm hole low on the back of the plinth (D22) |
| M3 screws, inserts, rubber grommets | as needed | Other mounts. Rubber grommets keep motor noise away from the microphone |
| Stone-texture spray, primer, paint | as needed | Keep paint off the tongue slide and chute |
| Small cauldron-style bowl | 1 | Catches the candy |

## Consumables

| Part | Notes |
|---|---|
| Individually wrapped soft toffees, one type | Avoid chocolate, lollipops and loose sweets |

## Power budget

Cap LED brightness in firmware (about 20 percent for the eyes and 50 percent for the spine) and verify the current draw with a meter before closing the enclosure.
