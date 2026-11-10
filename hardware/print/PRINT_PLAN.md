# Print plan

P2S Combo, AMS 2 Pro, 0.4 mm nozzle, PLA+. Open each 3MF in Bambu Studio, set the process, slice, check the preview, print.
Grams and hours are estimates from the mesh volume (about 0.6 g per cm3 printed, about 21 g per hour, both from the
plate 06 slice of the old layout: 291 g, 13h41m). Plates 01 and 02 are real slices.

## Order

Print in this order: what the demo needs first (head, face, dispenser, spine), then body, wings, plinth last.

### Run to 11:15 on 2026-11-10 (printer never idle, plates swapped at once)

04 waits: the bench prototype rig stands in for it this week. Every 04 part changed after that rig (sweet path 3 mm
wider, servo plate and shelf 3 mm wider, short statue chute), so none of the rig parts can be mixed with 04 parts.

| Start | File | Time | Ends |
|---|---|---|---|
| 11:40 09 Nov | 05 clear spine, re-sliced 11:38: 3h54m, 58.6 g + 14.0 g support, 193 layers | 3h54m | 15:35 |
| 16:00 | 07 body + throat splints | 2h58m | 19:00 |
| 19:10 | 08 body + splints | 2h38m | 21:50 |
| 22:00 | 06 body + tongue | 7h55m | 05:55 |
| 06:05 10 Nov | 04 dispenser, if wanted | 5h12m | 11:15 |

Times are from the real slices. 06 to 08 may come down with the body settings below; re-slice before each starts.

Body shell check (2026-11-09, slices of print/body3 pieces, 25 levels each): only 5 to 18 % of each section is
thicker than 6 mm and most of the shell is 3 to 5 mm, against a 3.4 mm floor for 2 walls a side. Thinning the inside
would save little and puts the joints to the printed 01 to 03 at risk, so the geometry stays. The saving is in settings.
Real slices are 0.28 mm layers at the old settings; the fast settings below should take 15 to 25 % off.

| # | File | Pieces | g | h | Notes |
|---|---|---|---|---|---|
| 01 | 01_head_cap_2colour | Hab + 2 eyes, 2 pupils | 304 | 14.8 | done 2026-11-08 |
| 02 | 02_face_ears_jaw_hatch_grey | Haa0, Haa1, Hb, lid, Ga1 | 55.6 | 2.7 | done 2026-11-09 |
| 03 | 03_face_throat_grey | Gbb0a1 | 252 | 9.8 | done 2026-11-09 11:17. fast preset, support threshold 25: 9h45m, 59 g support, 464 layers. At 20 it is 8h53m and 39 g, but the 20 to 25 degree faces are the mouth, the jaw and the tooth roots, which are seen and sit on the sweet path, so print at 25. 2026-11-09: mist port added (10.4 mm socket for a 10 mm OD tube, 8 mm exit, 45 degrees forward and down through the roof of the mouth on the centre line x -11.5, checked clear of the dispenser: chute 21 mm away), +2 cm3. Re-sliced with the port, fast preset, threshold 25: 10h01m, 254 g (16 min and 2 g more than before the port) |
| 13 | 13_dispenser_grey | housing, rotor, servo plate, chute, tube | 209 | 5.2 | Sliced 2026-11-09 at 0.20 mm, 3 walls, top 4, 15 % gyroid, threshold 25: 5h12m, 198 g + 10 g support, 446 layers. Brim 6 mm on chute and tube |
| 10 | clear_10_spine_plates | plate1 to plate8 | 94 | 4.4 | Sliced 2026-11-09, clear filament slot 1, 0.20 mm, threshold 25, outer brim 4 mm: 4h21m, 83 g + 11 g support. Bambu flags 1 small region on plate7. Transparent. Domes stand on their rims on purpose: support stays inside, off the glowing face |
| 08 | 08_body_grey | Gbb0bb1a1, Ga0 | 216 | 7.9 | Sliced 2026-11-09, fast preset (threshold 25): 7h55m, 176 g + 40 g support, 529 layers. Print as is; keep 25, the tongue underside shows |
| 06 | 06_body_grey | Gbb0bb1a0, splint_Gbb0a1_1, splint_Gbb0a1_2 | 91 | 3.0 | Sliced 2026-11-09, fast preset (threshold 25): 2h58m, 72.4 g + 18.9 g support. Print as is. Re-sliced 2026-11-09 16:10 with the Numakers PLA+ preset (228 C, 21 mm3/s), threshold 25, no brim: 2h56m print, 3h03m total, 74.0 g + 18.9 g support, 430 layers, 120.3 mm tall. Two support trees, both inside the shell. Print it |
| 09 | 09_body_grey | Gbb0a0, splint_Gbb0baa_1, splint_Gbb0baa_2 | 65 | 2.6 | Sliced 2026-11-09, fast preset (threshold 25): 2h38m, 53.3 g + 11.3 g support. Print as is |
| 04 | 04_body_grey | Gbab0b, Gbb1 | 300 | 12.2 | Sliced 2026-11-09, fast preset (threshold 25): 12h12m, 221 g + 79 g support, 329 layers. Option: Gbab0b turned X 90 (see Speed plan 6) |
| 05 | 05_body_grey | Gbb0bb1b, Gbab0a | 371 | 11.9 | Sliced 2026-11-09, fast preset (threshold 25): 11h53m, 293 g + 77 g support, 619 layers, 173 mm tall. Brim 6 mm. Bambu flags 1 small region on Gbab0a |
| 07 | 07_body_grey | Gbb0baa | 177 | 6.7 | Sliced 2026-11-09, fast preset (threshold 25): 6h39m, 121 g + 56 g support, 550 layers, 154 mm tall on a small footprint. Brim 6 mm. Re-sliced 2026-11-09 18:45 with the Numakers PLA+ preset (228 C, 21 mm3/s), threshold 25, outer brim 6 mm, after Studio repaired reversed faces: 6h32m print, 6h39m total, 122.1 g + 54.5 g support, 550 layers, 153.9 mm tall. Print on Standard speed (tall on a small footprint) |
| 11 | 11_wing_right_grey | Gbaa, Gbab1, Gbb0bb0 | 316 | 11.2 | Sliced 2026-11-09, fast preset (threshold 25): 11h10m, 254 g + 62 g support. Tall free-standing support trees, brim 6 mm |
| 12 | 12_wing_left_grey | Gbb0bab | 360 | 13.2 | Sliced 2026-11-09, fast preset (threshold 25): 13h12m, 266 g + 94 g support, 766 layers, 214 mm tall. Brim 6 mm, spaghetti detection on |
| 14 | 14_plinth_grey | P1 door frame | 58 | 1.3 | Sliced 2026-11-09, fast preset, threshold 15: 1h18m, 58.1 g, no support, 45 layers, 12.5 mm tall. Long thin ring across the bed: clean plate, glue stick on the corners |
| 17 | 17_plinth_grey | door | 136.8 | 2.45 | flat. Sliced 2026-11-09, fast preset (0.28, 10 % lightning): 2h27m, 136.8 g. The volume estimate said 6 h |
| 15 | 15_plinth_grey | P0bbb walls | 274 | 6.9 | Sliced 2026-11-09, fast preset, brim 6 mm. Support threshold 30: 8h57m, 104 g support. 25: 8h39m, 95 g. 20: 7h45m, 72 g. 15: 6h55m, 44 g (use this; Bambu flags 2 small regions it cannot support). deck split off at z 222, bottom trimmed 0.6 mm so it stands flat (157 cm2 on the bed) |
| 16 | 16_plinth_grey | P0ba walls | 265 | 6.3 | Sliced 2026-11-09, fast preset, threshold 15, brim 6 mm: 6h15m, 223 g + 43 g support, 791 layers, 221 mm tall. Bambu flags 3 small regions; on the mesh at 15 they are strips of 0.3 to 3.7 cm2 (bed edge at z 0.9, top lip at z 211 and 221), safe |
| 18 | 18_plinth_grey | P0ab walls | 295 | 7.5 | Sliced 2026-11-09, fast preset, threshold 15, brim 6 mm: 7h29m, 236 g + 59 g support, 791 layers, 221 mm tall. Bambu flags 2 small regions; on the mesh at 15 every patch is under 1.2 cm2, safe. Re-sliced 2026-11-09 13:49 with the GARGOYLE PROJECT preset (threshold 25, flow up to 21 mm3/s, 220 C): 8h43m, 235 g + 98.6 g support. Line types: outer wall 1h58m, inner wall 1h33m, support 2h18m, travel 1h14m, internal solid 41m, bridge 21m. Walls run at 250 mm/s, so speed, not flow, sets the wall time. Re-sliced 14:14 at threshold 15: 7h27m, 236 g + 58.9 g support, 2 small regions flagged as before. Print it at threshold 15 |
| 19 | 19_plinth_grey | P0aa walls | 257 | 6.4 | Sliced 2026-11-09, fast preset, threshold 15, brim 6 mm: 6h21m, 211 g + 46 g support, 791 layers, 221 mm tall. Bambu flags 3 small regions; on the mesh at 15 every patch is 1 cm2 or less, safe |
| 20 | 20_plinth_grey | P0bba (on its side), P0bba_deck | 146 | 4.6 | Sliced 2026-11-09, fast preset, threshold 15: 4h34m, 136 g + 10 g support, 417 layers, 117 mm tall. Bambu flags 5 regions on the deck: flat steps of its stepped underside 1 to 3.5 mm above the bed, too low for support. They droop a little on a face hidden inside the plinth, safe |
| 21 | 21_plinth_top_grey | P0bbb_top | 164 | 7.4 | 21 mm tall, cut face down. First slice 2026-11-09, walls 3, top 4, 15 % gyroid, threshold 20: 7h26m, 120 g + 43 g support, 75 layers. Twice the estimate: the cut face is only the wall ring (25 cm2 on the bed) and the inside ceiling (about 140 cm2 at z 3 to 10, hidden) needs support. Flipped is no better (the rock top has the same overhang). Re-slice as 22 (10 % lightning, threshold 15, top 3, walls 3) |
| 22 | 22_plinth_top_grey | P0ba_top | 159 | 7.4 | as 21. First slice 2026-11-09, walls 3, top 4, 15 % gyroid, threshold 20: 7h21m, 118 g + 42 g support, 75 layers. Re-sliced with 10 % lightning, threshold 15, top 3, walls 3: 6h43m, 107 g + 37 g support. Use this for 21 to 24 |
| 23 | 23_plinth_top_grey | P0ab_top | about 120 | about 5 | as 21 |
| 24 | 24_plinth_top_grey | P0aa_top | about 100 | about 4 | as 21 |
| 25 | 25_splints_grey | splint_Gbaa_Gbb0baa_x1, splint_Haa0_Gbaa_y1 | about 4 | est under 1 | Built 2026-11-10 (tmp/splint_any.py) for seams with a printed piece on one side. Laid flat, 12 mm tall, body settings, threshold 20 (hidden). Not sliced yet. Print before body step 7. |

Totals (2026-11-09, after plates 15 and 17 were sliced). Left after plate 03: about 143 h and 4.2 kg (116 h and 3.6 kg from real slices of 04 to 20; tops 21 to 24 about 6.7 h and 145 g each, 27 h, from the 22 re-slice; the first estimate of 10 h was wrong). The statue alone (04 to 13) is 78 h. Whole job including 01 to 03: about 153 h, 4.65 kg (statue about 106 h, 2.8 kg; plinth about 47 h, 1.85 kg).
- Real slices: 15 (6h55m at threshold 15), 17 (2h27m). Plates 16, 18, 19 scaled from 15 by volume: about 7 h each.
  20 about 4 h, 14 about 1 h, tops 21 to 24 about 10 h together (scaled from the door, plus walls 3 and support).
- Body plates 04 to 09, 11, 12: old slices times 0.8 (plate 03 measured 20 % faster on the fast preset), 08 real: about 69 h. The old 08 figure was
  a guess, not a slice; the others were real slices, so they should hold better.
- 13 about 3.5 h at 0.20 mm, 10 4.6 h. Plinth about 45 h. Was about 167 h before the fast preset and threshold 15.

Totals (2026-11-08). Statue numbers are Bambu Studio slices; plinth numbers are estimates at 0.58 g per cm3 of mesh and 25 g
per hour (plates 06 and 08 without much support), so treat them as rough until you slice 15 and 21.
- Statue without wings (01 to 10, 13): about 1.85 kg, about 87 h. About 72 h left after the head cap.
- Wings (11, 12): 619 g, 30 h.
- Plinth (14 to 24): about 1.9 kg, about 76 h (was about 167 h before the decks were split off).
- Everything: about 4.4 kg, about 193 h at the old settings, roughly 150 to 165 h with the fast settings.
- One P2S with a 0.4 mm nozzle runs about 24 h a day, so this is 6 to 7 days of printing, not 2.

## Fast settings (all grey plates except 13)

Body shells are 3.4 to 5.5 mm thick (mean 4 mm, volume over half the surface area, body3 meshes), so 2 walls each side cover
most of the wall and infill hardly matters. Time goes into the textured faces and the support. Change these, in this order:
- Printer: speed mode Sport on the screen (Ludicrous rings on the texture and runs into the flow cap anyway).
- Filament: Max volumetric speed 21 mm3/s if the profile says less (Generic PLA is 12), nozzle 225 to 230 C for PLA+.
- Support: Tree (auto), style Tree Slim, threshold angle 20, top Z distance 0.28, top interface layers 2, bottom 0,
  base pattern hollow. Most support sits inside the hollow, where a rough ceiling does no harm.
- Walls 2, top 3, bottom 3, sparse infill 10 % lightning (used on plate 03, sliced without "Infill failed"), ironing off, seam aligned. Plinth tops 21 to 24: 3 walls for the screw bosses, top 3, 10 % lightning, threshold 15 (the supported ceiling is hidden inside the plinth): 6h43m on 22. 15 % gyroid, top 4, threshold 20 took 7h21m. Most of the time is the rock skin top and bottom, so settings move it little.
- Brim only where the plan says so; prime tower off on single colour plates.
- Support: untick Independent support layer height, top Z distance 0.28, base pattern hollow. Brim off unless the plan says so,
  no scarf joint on inner walls. Measured on plate 03 (Bambu Studio, P2S, 0.28 mm): 12h12m and 247 g down to 8h53m and 232 g.
  Keep the support threshold at 25 on visible faces (plate 03); 20 is fine on hidden body pieces.
- Save the result as your own process preset (Gargoyle fast 0.28) and use it on every grey plate.
- 0.4 mm nozzle only, so widen the lines nobody sees: inner wall 0.55, sparse infill 0.6, internal solid infill 0.5,
  support 0.5. Keep outer wall 0.42 so the texture stays sharp. Layer height 0.28 is the most the P2S 0.4 nozzle profile allows.
- Keep plate 13 (dispenser) and the spine at 0.20 mm and 0.42 lines: fits and light matter there.

## Speed plan (2026-11-09)

Checked on the meshes (tmp/orient_scan.py, tmp/ext_orient.py, tmp/contact.py, tmp/deck_under.py). Nothing here changes
the outside of a piece or the size of the statue. Hours marked "est" are the line model, not a slice.

What does not help:
- Turning body pieces. The orientations with the least support all stand on under 1 cm2 of bed and are 124 to 237 mm
  tall (Ga0, Gbaa, Gbb0bab, Gbb0a0, Gbab0a). They would need a support tower to stand on and are likely to fall over.
  The pieces stay with their cut face down. Nearly all support area is on the outside skin whatever the turn
  (the shells are thin, so the inside faces barely overhang).
- Turning plinth pieces. Walls, frame, door and tops are already in their best orientation (all 24 turns tried).
- Making the deck tops support free. The deck underside is stepped between 4 and 10 mm above the cut; filling it to
  a flat face adds about as much plastic as the support it saves.
- Thinning the plinth walls in the mesh. About 3 h and 100 g, and the 2 mm pin holes in the 5 mm walls no longer fit.
  Fewer walls in the slicer gets more of the same saving and keeps the pins.

What helps, biggest first:
1. Fast preset (above) on every grey body plate not yet printed: 04, 05, 06, 07, 08, 09, 11, 12. Measured 20 % on
   plate 03, so about 16 h off 82 h. Look at plate 03 off the plate first. If the face texture is fine, use it everywhere.
2. Plinth walls (15, 16, 18, 19, 20) and door (17): fast preset as it is (0.28 mm, walls 2, 10 % lightning), support
   threshold 15 (a lower threshold means less support; on plate 15 it took 1h44m and 51 g off the threshold 25 slice),
   brim 6 mm on the 221 mm walls. The P2S 0.4 nozzle profile caps layers at 0.28, so 0.30 is out. Keep walls 3 on the tops (21 to 24): the screw
   bosses are there. About 15 h off 77 h (est). Slice 15 once and send the time so the rest can be checked.
3. Door (17), frame (14), tops underside: hidden. Support threshold 15 to 20, no interface on hidden faces.
   The flat deck underside gets support at any threshold; a lower one only drops the sloped bits.
4. Timelapse off except on the plates you want footage of. The traditional mode parks the head every layer, about
   2 to 3 s a layer, 20 to 40 min on a 600 to 800 layer plate.
5. Order: start a plate before bed that runs at least until you wake (04, 05, 11, 12, 15, 16, 18, 19 are 9 to 13 h at
   the fast settings). Chain the short ones in the day (13, 10, 06, 07, 08, 09, 14, 17, 20, 21 to 24). An idle
   printer costs more than anything above.
6. Optional: Gbab0b (plate 04) turned to stand on its side (rot 13 in tmp/ext_orient.py) has 33 cm2 of support area
   instead of 111, standing 173 mm tall on 20 cm2. Try it only with a 8 mm brim. Possibly 1 to 2 h off 16 h (est).

Failure checks, because a failed 12 h plate costs more than every saving above:
- Dry the PLA+ before the long plates (55 C, 6 to 8 h, or straight from the AMS 2 Pro dryer).
- AMS backup on: load two grey spools so a run-out switches spools. About 3.8 kg left to print.
- Spaghetti detection and first layer inspection on. Clean the plate with dish soap before the plinth plates.
- Brim 5 to 8 mm on everything over 150 mm tall: 05, 12, 15, 16, 18, 19.
- Keep the outer wall acceleration from the preset on the 221 mm plinth walls; do not raise it for speed.
- Plinth tops: glue stick on the plate. The 21 mm tall pieces have long straight edges that like to lift at the corners.

## Settings (grey plates)

- Process: 0.28 mm (initial layer 0.20), saved as your own preset. Check the layer count after slicing: about 3.6 layers per mm of height.
- If the layer count is far higher, untick Support > Independent support layer height.
- Walls 2 (plinth 3, it carries the statue screws), top layers 3, gyroid infill (statue 10 %, plinth 15 %).
- Supports: tree (auto), threshold 25 degrees. Brim: auto, outer only. Skirt 0. No prime tower on single colour plates.
- Do not use Bambu's Simplify model. The plate files are already thinned by plates.py to within 0.03 mm (about a third of the triangles).
- Sparse infill: gyroid. Plate 05 gave "Infill failed" with the old 1.2M triangle file; lightning is a likely cause, gyroid is the safe choice.
- Every plate file was checked after the rewrite: 0 open or pinched edges, 0 flipped faces, each part one closed solid (tmp/check_3mf.py, tmp/check_orient.py).
- Prime tower: on for plate 01 only. Untick it on every single colour plate.

## Assembly

- Short version: FINAL_PRINT/ASSEMBLY.md (one page, splint numbers, file number per piece). The notes below are the reasons.
- Splints 1 to 4 have 1 to 4 dots (1.2 mm holes, 1 mm deep; splint 1's dot is 1.6 mm) on the end that goes into the piece glued first (tmp/mark_splints.py, 2026-11-10). Plates 08 and 25 rebuilt with them; the old 08 is in FINAL_PRINT_bak.
- Pins: 1.75 mm filament cut 12 mm long, in 2 mm holes 6 mm deep each side. Head 14, body 31, plinth 38 across the side seams plus 39 into the deck tops: 122 pins, about 1.5 m of filament. Cut 140.
- Dry fit every seam first. Glue with CA (thin for pins, gel for faces) or 5 minute epoxy on the big plinth faces.
- Splints (plate 09): the upper back Gbb0baa lands on Gbb0bb1a0 and Gbb0bb1b where the wall is under 3 mm, too thin for pins. Glue splint_Gbb0baa_1 inside Gbb0bb1a0 and splint_Gbb0baa_2 inside Gbb0bb1b, half standing above the seam, then lower Gbb0baa onto them.
- Splints (plate 06): the face Gbb0a1 meets Gbb0bb1a1 and Gbb0bb1b at y -64.4 where no pin fits (the wall slopes away
  from the seam). Glue splint_Gbb0a1_1 inside Gbb0bb1a1 and splint_Gbb0a1_2 inside Gbb0bb1b, the long side down in the
  piece (about 80 % of it), then slide Gbb0a1 on. Both clear the stone by 0.25 mm (0 mm3 overlap, checked on the meshes).
- Assembly order follows the cut tree backwards. Each step joins two groups across one cut plane, so every pin and splint
  in that step points the same way and the groups slide straight together. Never add a piece that meets the group
  across two directions at once (for example Gbb0a1 after Gbab0b: x pins and y splints together lock it out).
  Pin directions per step were checked against the joint table (tmp/qc_joints3.log).
  Body, step by step (direction of the slide in brackets):
  1. Gbb0bb1a0 and Gbb0bb1a1 onto Gbb0bb1b (x pins).
  2. Gbb0bb0 into Gbb0bab (z pins), then that pair down onto Gbb0bb1b (z pins).
  3. Glue splint_Gbb0baa_1 in Gbb0bb1a0 and splint_Gbb0baa_2 in Gbb0bb1b. Lower Gbb0baa onto them (z). Its face on
     Gbb0bab is a vertical plane at x -61.3, so it slides down along it: glue that face as it goes. This order puts
     Gbb0baa on the splints and Gbb0bab on pins, so both are lined up (gluing them together first lined up neither).
  4. Glue splint_Gbb0a1_1 in Gbb0bb1a1 and splint_Gbb0a1_2 in Gbb0bb1b. Gbb0a0 and Gbb0a1 slide on together (y).
     Gbb0a0 and Gbb0a1 do not touch each other, so place them one after the other in the same direction.
  5. Gbab0a onto Gbab0b (y pins), Gbb1 onto Gbab0a (x pins; Gbb1 touches nothing else).
  6. That group and Gbab1 up into the right wing Gbaa (z pins).
  7. The right wing group onto the body from the side (x pins into Gbb0a1, Gbb0bb1a0 and Gbb0bb1a1; the wing face
     on Gbb0baa is glue only).
  8. Ga0 and Ga1 onto Gbb0a1 (y pins).
  9. Head: Haa0 and Haa1 onto Hab (x), Hb onto Hab (x), then the whole head down onto Gbb0a1 and Ga1 (z pins; the faces
     on Gbb0baa, Gbb0bab and Gbaa are glue only).
  Plinth, step by step:
  1. Each deck top onto its own walls (z, 9 or 10 pins each): P0aa_top, P0ab_top, P0ba_top, P0bbb_top.
  2. P0aa onto P0ab (x pins): the front.
  3. P0bba onto P0bbb (x), then P0bba_deck onto P0bbb_top (x, slide it in from the P0ba side).
  4. That group onto P0ba (x pins into P0ba and P0ba_top).
  5. Back onto front (y pins).
  6. P1 and the door.
- Ga0 is the tongue slide. It hangs from Gbb0a1 on 2 pins (9.8 cm2 face) and reaches 150 mm out in front of the plinth
  and 130 mm below the landing (lowest point z 112, at least 20 mm clear of the plinth front). Glue it with 5 minute
  epoxy, not CA, because a hand on the tip pulls hard on that small face. Keep paint off the slide.
- Ear tip Hb has one pin only (5.3 cm2 face): glue and hold it, the pin just lines it up.
- Splints (plate 25), for seams whose other piece was already printed, so no pins could be added:
  splint_Gbaa_Gbb0baa_x1 goes inside Gbb0baa at the x 92.7 seam before body step 7; the right wing group then slides on in x over it.
  splint_Haa0_Gbaa_y1 goes inside Gbaa at the y -65 seam before body step 9; the head then comes straight down over it.
  Both clear every piece by 0.25 mm in place and while the moving group slides on (0 mm3 overlap over a 30 mm slide, checked on the meshes).
  Faces left as glue only, each piece held by pins on its other faces: Gbab0b on Gbb0bb1a0 (1 pin, no hollow there),
  Gbb0bab on Gbb0baa (no hollow), Gbb0bab and Gbb0baa on Hab (the head has 10 pins below it), Gbaa on Haa0 at z 424.
- The statue sits on a flat landing at z 243 that follows its hollow shell wall, 3 mm wider each side. Inside the outline the plinth is open, front feet and back alike. Only the 4 screw bosses stand inside. The statue goes on and comes off with the 4 M3 screws from below (D22), nothing glued.
- The deck in front of the back opening is its own piece, P0bba_deck: 3 pins into P0ba_top, 3 into P0bbb_top and 1 into P0ab_top, plus glue (plinth step 3).
- The door frame P1 drops onto the plinth floor with its lip in the door hole. Glue it, no pins.
- The plinth front has one vertical seam at x 9 (the front is 392 mm wide and the plate is 256). Fill and sand it before weathering.
- Piece names say where they go: G body, H head, P plinth. Assembled-pose meshes for each piece are the .npz next to its .stl.
