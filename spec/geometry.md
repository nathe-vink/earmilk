# Geometry

Every number the README gives, expanded into one coordinate frame so a model can be built from this file alone.

- **README** numbers are the spec. If this file and the README disagree, the README wins and this file is wrong.
- **Derived** numbers follow from the README by arithmetic.
- **As drawn** numbers are measured off the canvas artboards (Section, Back, Sleeves, Hero). Treat them as ±1 mm; the artboards are illustrations, not drawings to scale in every stroke.
- **Assumption** marks a reading this file had to make to be buildable. Confirm before relying on it.

## Frame

- Millimetres.
- `x` across the width: 0 at the left face as seen from the front, 390 at the right face. Centerline `x = 195`.
- `y` depth: 0 at the front face, 390 at the back face.
- `z` height: 0 at the floor.
- Everything is symmetric about `x = 195`.

## Floorstander

### Body

| | |
|---|---|
| Plan | 390 × 390 |
| Height, floor to the front top edge | 860 |
| Walls | 18 mm Baltic birch, braced |
| Internal, gross (derived) | 354 × 354 × 824 = 103.3 L before bracing, the mid's enclosure and driver displacement. The README's 32 Hz target assumes 85–90 L net for the woofer, which is an open question, not a result. |

### Gable (a solid carved birch block on top of the body, CNC)

| | |
|---|---|
| Ridge | runs along `x` at `y = 195`, `z = 1010` (derived: 860 + 150) |
| Rise | 150, front top edge to ridge |
| Slope panel length | 246. Derived check: √(195² + 150²) = 246.0, so the ridge is centred front to back. |
| Slope angle (derived) | 37.6° from horizontal |
| End faces | triangles in the `x = 0` and `x = 390` planes: base 390 at `z = 860`, apex at the ridge (as drawn, Sleeves artboard). The block is a plain triangular prism; no folded carton ears. |
| Point at distance `s` along the front slope, measured from the front top edge (derived) | `x` free, `y = 0.7927·s`, `z = 860 + 0.6098·s` |

### Fin

| | |
|---|---|
| Height | 45 above the ridge: `z` 1010 → 1055 |
| Thickness | ~8. Centred on the ridge, `y` 191 → 199 (assumption) |
| Length | full width, `x` 0 → 390 (as drawn) |
| Overall height | 1,055 |

### Carton scale

A US half gallon scaled ×4.1 (derived): 390 / 4.1 = 95.1 plan, 860 / 4.1 = 209.8 body, 1,055 / 4.1 = 257.3 overall.

### Front drivers (on the baffle, `y = 0`, on the centreline `x = 195`)

| Driver | Centre `z` | Frame ø | Extents |
|---|---|---|---|
| 12 in woofer | 290 | ~310 | `x` 40 → 350, `z` 135 → 445. *2026-10-08 (the owner): centre `z = 320`, `z` 165 → 475, its frame 52 clear of the plinth's shadow line (was 22).* |
| 6.5 in mid | 690 | ~170 | `x` 110 → 280, `z` 605 → 775 |

Black paper cones. No grilles. The sleeve's die-cuts equal the frame diameters (as drawn, Sleeves artboard). Gap between the woofer's top and the mid's bottom: 160 (derived). Mid top to the front top edge: 85 (derived). *2026-10-08 (the owner): the gap 130 with the woofer at 320. Both drivers flush: each frame sits in a rebate, a satin black trim ring over it and its screws level with the finish, with a 0.8 reveal round it whose floor is dark; the cones charcoal paper with pressed concentric ribs, the dust caps satin.*

### Tweeter

| | |
|---|---|
| Unit | 1 in dome with a small faceplate, ≤ 62 mm |
| Axis | horizontal, firing forward (toward −y), along `x = 195`, `z = 903.5` |
| Faceplate plane | `y = 170`, i.e. 170 back from the front face. *2026-10-08 (the owner): `y = 125`, 125 back (from 170 the faceplate showed, from every camera off the axis, pushed into the far end of the mouth and cut by its rim).* |
| Faceplate (as drawn) | 62 tall, 6 thick: `y` 170 → 176. *`y` 125 → 131 since 2026-10-08.* |
| Dome apex (as drawn) | about 8 forward of the faceplate plane, `y ≈ 162`. *`y ≈ 117` since 2026-10-08.* |
| Body behind the faceplate (as drawn) | about 38 deep × 60 tall, `y` 176 → 214, inside the block. *`y` 131 → 169 since 2026-10-08.* |
| Seat (2026-10-06, as modelled) | *2026-10-08 (the owner): the throat's own floor, a flat ring ø 62 → 74 in the plane `y = 125`, in the throat's colour, the faceplate flush in it and its edge black.* *2026-10-07: moulded black, as the tweeter's chamfer (the owner: no bright metal at the scoop).* A ring where the throat ends, ø 64 on its centreline (between the faceplate's 62 and the throat's 66), 3 across, the faceplate's edge seated in it; satin metal since v19 (moulded satin black, it vanished against the faceplate). A render detail answering a critic ("no visible seat"), not a dimension the owner set. |

### Bowl (the waveguide)

| | |
|---|---|
| Throat | circle ø 66 in the plane `y = 170`, centre (195, 170, 903.5): `x` 162 → 228, `z` 870.5 → 936.5. *2026-10-08 (the owner): ø 74 in the plane `y = 125`, centre (195, 125, 903.5): `x` 158 → 232, `z` 866.5 → 940.5. The mouth is unchanged, so the bowl is shallower, its ceiling a short arch.* |
| Mouth | ellipse lying in the front slope plane. Along the slope: `s` 20 → 138 (118 long), centre `s = 79`. Across: 211 wide, `x` 89.5 → 300.5 |
| Mouth lower lip (derived) | (195, 15.9, 872.2) |
| Mouth centre (derived) | (195, 62.6, 908.2) |
| Mouth upper lip (derived) | (195, 109.4, 944.1) |
| Mouth side lips (derived) | (89.5, 62.6, 908.2) and (300.5, 62.6, 908.2) |
| Surface | one smooth loft from the mouth ellipse to the throat circle. No flats, no edges. Painted: light at the mouth, dark at the throat (`spec/colorways.json`). |
| Centreline section (as drawn) | the floor runs almost straight from the lower lip back to the throat bottom, sagging about 3 below that chord; the ceiling arches about 6 above the chord from the throat top to the upper lip. The hollow reads as a concave bowl, deeper above the axis than below it. |
| Clearances (derived) | the throat bottom is 10.5 above the body top; the slope surface directly above the throat is at `z ≈ 991`; the bowl is carved entirely within the block. *2026-10-08: 6.5 above the body top, the slope above the throat at `z ≈ 956`.* |
| Lip (2026-10-06, the owner) | *Withdrawn 2026-10-07 (the owner): no lip; the mouth is the finish's cut edge, eased 1.5.* polished stainless, half-round, round the mouth ellipse over the finish's cut edge and the bowl's joint: radius 2.4, its centre on the ellipse 0.84 below the finish's outer face, so 4.8 wide and 1.6 proud of the finish. The same on every flavour. |

**Pattern angles.** The README's ~12° down and ~37° up are measured from the dome apex, 8 forward of the faceplate plane, which is how the Section artboard draws them. Derived from the lip coordinates above: 12.1° down and 37.7° up from the apex at `y = 162`; 11.5° and 33.8° if measured from the faceplate plane instead. Build the model with the apex at `y ≈ 162` and the README's figures hold. *2026-10-08 (the owner, the tweeter at 125): 17.2° down and 79.4° up from the apex at `y ≈ 117`. The lower lip still bounds the pattern, at about 17° below the axis; the upper lip no longer does. The tweeter reaches a seated listener about a third sooner (`fab/README.md`, Crossover).*

### Back (plane `y = 390`)

| | |
|---|---|
| Birch window (bare, inside the sleeve frame) | `x` 26 → 364, `z` 40 → 798, so 338 × 758. *Amended 2026-10-02: a bare birch field in the finished back. Default, contained: the Facts panel plus a 26 margin all round, `x` 36 → 354, `z` 504 → 796 (318 × 292); the port, the posts and the engraved wordmark sit on the finish outside it. Option, full: `x` 26 → 364, `z` 140 → 830 (338 × 690), the same 26 margin at the sides and above the plinth's shadow line.* |
| Sleeve frame margins (derived) | 26 each side, 40 at the bottom, 62 at the top. *2026-10-02: 26 each side, the plinth and its shadow line below, 30 at the top.* |
| Engraved wordmark (amended 2026-10-02) | "earmilk", Archivo Black, 36 mm type size, centred on `x = 195`. With the contained field: on the finish above it, baseline at `z = 812`, engraved through the lacquer and ink-filled in the panel's brown. With the full field: inside it, baseline at `z = 788`. *Superseded the same day: the back wordmark is the same cast metal letters as the front, 44 mm type, 2.5 proud (1.5 since 2026-10-08), centred on `x = 195` at `z = 826`.* *2026-10-07 (the owner): centred between the body's top edge and the Facts: its ink (32.5 tall, the set point 0.3 below the ink's middle) at `z` 797.3 → 829.7, so 27.3 of white above it to the gable line's foot (857) and 27.3 below to the Facts' top border (770); set at `z = 813`.* |
| Bronze plate (2026-10-02, replaces the bare birch field as the default) | the Facts panel plus a 26 margin: `x` 36 → 354, `z` 484 → 796 (318 × 312), 3 thick, 1.5 proud of the finish, 3 corner radius; the Facts engraved into it, dark with patina. The port, the posts and the letters sit on the finish outside it. *Withdrawn 2026-10-07 (the owner): no plate; the Facts are printed on the finish (below).* |
| Marks (spec since 2026-10-02) | OPEN OTHER SIDE with its arrow, 27 mm caps, centred on the back slope, in the gable's other colour *(2026-10-07, the owner: on the fin's back face instead, centred across it and on its visible height, about `z` 1031; caps 19.2 tall in a fin face about 49 tall)*. SHAKE WELL, 26 mm caps, centred on the plinth's back face at `z = 55`, reversed in the body colour. Nothing else is printed. |
| Engraved Nutrition Facts panel | 266 × 240 with its top at `z = 770`: `x` 62 → 328, `z` 530 → 770. Copy and proportions in `copy/label.md`, engraved version. *Amended 2026-10-02: 266 × 260, `z` 510 → 770, so "Contains no milk." sits inside the border with the same 14 mm padding as every other side.* *Amended 2026-10-07 (the owner): printed directly on the back's finish, like a carton's panel, at the same place and size: ink on the cured colour coat (screen print with a catalysed ink, or a water-slide decal), sealed under the 2K clear and flatted level, so it cannot scratch off without cutting through the clear. Ink `#1E1A17` (a warm near-black) on the white flavours, the print colour on Chocolate (cream `#F1E3CC`) and Oat (brown `#2B2118`); `spec/colorways.json`, facts.* |
| Port | round, ø ~100, centre (195, 390, 405): `z` 355 → 455. As drawn: a 92 bore in a 112 flange. |
| Binding post plate | 128 × 64, centre `z = 144`: `x` 131 → 259, `z` 112 → 176. As drawn: dark plate, two posts ø 24 at ±32 from the centre; seen from behind, red on the left, black on the right. *Amended 2026-10-02: centre `z = 150` (`z` 118 → 182) so the plate clears the plinth's shadow line; inside the full field, centre `z = 185`.* *2026-10-08 (the owner): a recessed terminal cup in place of the plate: its flange 128 × 64 at centre `z = 175` (`z` 143 → 207, 30 above the shadow line), 3 proud of the finish on four screws; the cup 106 × 42 inside, the posts on its floor 18 in from the flange's face.* |
| Vertical gaps (derived) | 75 between the panel's bottom and the port's top; 179 between the port's bottom and the plate's top. *2026-10-07, with no plate: 55 between the panel's bottom (`z` 510 since 2026-10-02) and the port's top (455).* *2026-10-08: 148 between the port's bottom and the terminal cup's top.* |

### Sleeve

| | |
|---|---|
| Tube | 390 × 390 × 860 outer, open top and bottom. Die-cut for the woofer (ø 310 at `z` 290) and the mid (ø 170 at `z` 690). The back panel is a frame around the window above. |
| Lid | covers the gable and the fin; die-cut at the bowl mouth (the ellipse above). |
| Lock | both pieces lock at the back seam. Where on the back the seam sits is not drawn. |
| Board | heavy carton board / SBS, target 1.2–1.5 mm. Open test: whether it holds a crisp fold at this size. |
| Fold creases | at the gable: the lid's folds at the ridge and along the front and back top edges, and the fin's fold. They should be visible in a render. |
| Dimension note (assumption) | The render model keeps the cabinet and block at the spec numbers and puts the board outside them, so the sleeved speaker is 393 wide and deep. Whether 390 is the cabinet or the outer dimension is decided when the board stock is chosen; at any shot scale the difference does not show. |

### Finish and plinth (2026-10-02; replaces the print and the stand below)

No sleeve. The outer dimensions stay as above; the skin is a finish on the birch.

| | |
|---|---|
| Body | finished in the flavour's board colour, `z` 113 → 860 on the body and the whole gable on Chocolate and Oat |
| Gable and fin | finished in the accent (print) colour on Whole, 2% and Skim; body colour on Chocolate and Oat |
| Plinth | the bottom 110 of the cabinet, all four sides, in the accent colour, flush with the body; overall height stays 1,055 |
| Shadow line | 3 mm, `z` 110 → 113, a dark groove where the plinth meets the body (this repo's reading of "built in") |
| Gable shadow line (2026-10-07, the owner) | 3 mm, `z` 857 → 860, a dark groove where the gable meets the body, all four sides, like the plinth's; on the pint scaled (0.77) |
| Wordmark on the plinth | cast metal letters, the wordmark itself with no plate behind it, the way the lettering stands on a La Marzocco machine: Archivo Black, 44 mm type size, 2.5 proud (*1.5 since 2026-10-08, the owner, the sides finished like the faces: at 2.5 with darker sides they read as an extrusion with a drop shadow*), polished faces and satin sides, centred on the plinth's front at `z` 55 (about 155 wide). *The 2026-10-02 plate (180 × 56) lasted one render and is withdrawn.* *2026-10-06, the owner: dark bronze letters on the light plinths (Chocolate's cream, Skim's pale blue), polished on the others; per flavour in `spec/colorways.json`.* |
| Wordmark elsewhere | engraved on the back panel (above); nowhere else |
| Edges | every edge and bevel takes the colour of its face, which a sleeve could not do. *2026-10-07 (the owner): the body's four vertical corners and the gable's four hips rounded 3 mm, the fin's edges 1.5 mm, in the geometry, so the outline rounds too; scaled on the pint (0.77 and 0.38). The remaining edges eased 1.5 mm in the finish.* *2026-10-08 (the owner): 6 mm on the corners and the hips, 3 on the fin (at room distance a 3 mm round is two pixels); scaled on the pint (1.5 and 0.77).* |

### Print on the sleeve (locked 2026-10-01; superseded 2026-10-02, kept for the record; the as-drawn placement it replaced is below it)

| | |
|---|---|
| Lid | On the white-board flavours (Whole, 2%, Skim) the lid, gable and fin, is printed in the flavour's print colour. Chocolate and Oat stay one colour, lid included. |
| Band | A band of the print colour, 110 tall from the floor line, around the front and both sides. On the back it covers only the sleeve frame below the window, `z` 0 → 40. |
| Wordmark | "earmilk", Archivo Black, 52 mm type size, reversed in the board colour, centred in the band: on the front at `x = 195`, and on the right side centred on the depth, reading front to back. Nothing is printed under the gable. Tracking −0.035 em. |
| Owner's panel (optional, print to order) | Right side, above the band: 300 wide × 330 tall, centred on the depth, `z` 295 → 625, in the print colour. Headline, a halftone portrait, four rows the owner fills in. Copy in `copy/hero.md`. |

As drawn before the amendment (Sleeves and Hero artboards): front wordmark about 47 mm with its baseline 43 below the tube's top edge; side wordmark about 64 mm, baseline 94 below the top edge, starting 35 from the front edge.

### Stand (optional accessory; superseded 2026-10-02 by the built-in plinth above, kept for the record)

| | |
|---|---|
| Block | 390 × 390 × 110, painted in the flavour's print colour, 2 mm edge radius |
| Reveal | a 6 mm dark recess, 366 × 366, between the stand and the carton, so the two read as separate pieces |
| Wordmark | on the stand's front and right side as in the band; a sleeve used on a stand is printed without the band, so the wordmark does not double |
| Heights with the stand (derived) | carton bottom at 116; overall 1,171; tweeter axis 1,019.5; woofer centre 406; mid centre 806 |
| Not swappable | the stand stays one colour; the sleeve still swaps |

## Pint (parked: render it only in the mixed-crate shot, do not design its electronics)

| | |
|---|---|
| Plan | 100 × 100 |
| Body | 200. Gable rise 35, so the ridge is at `z = 235`. Fin 12, top at `z = 247`. |
| Slope (derived) | run 50, rise 35: 61.0 long at 35.0° |
| Driver | one full-range, frame ø ~68, centre `z = 95`: `z` 61 → 129. *Amended 2026-10-05, the owner: replaced by the two below.* |
| Woofer (2026-10-05) | frame ø 68, centre `z = 67`: `z` 33 → 101 (the floorstander's 290 / 860 of the body). Clears the plinth (top at 28.2 plus the shadow line). *The floorstander's woofer moved to 320 on 2026-10-08; the pint's stays at 67, where its crate's windows frame it.* |
| Mid (2026-10-05) | frame ø 40, centre `z = 160`: `z` 140 → 180 (the floorstander's 690 / 860), 20 below the body's top. |
| Bowl | "tiny bowl at the top", not dimensioned. Assumption for the crate shot only: the floorstander's bowl scaled by the plan ratio 100/390, so a mouth of about 54 × 30 and a throat of about ø 17. *ø 19, 32 behind the front face, since 2026-10-08, following the floorstander's.* |
| Tweeter (2026-10-05) | a small dome at the bowl's throat: faceplate ø 16.6 (the throat less 2 %; ø 18.6 since 2026-10-08), 1.4 thick; dome base ø 8.8, apex 2.4 forward. Three drivers, as the floorstander has. |
| Lip (2026-10-06, the owner) | *Withdrawn 2026-10-07 (the owner): no lip; the mouth is the finish's cut edge, eased 1.5.* the floorstander's polished lip round the mouth, radius 0.9 (its 2.4 scaled by the plan ratio would be 0.6, too fine to make or see), 0.6 proud. |
| Not a uniform scale of the floorstander (derived) | plan ×0.256, body ×0.233, gable ×0.233, fin ×0.267. The pint is squatter, like a real pint next to a half gallon. |
| Crate | 340 × 250 × 130, holding 2 × 3 pints. The pints stand about 117 proud of the rim (derived). Six pints, five flavors, so one flavor appears twice; which one is not specified. |
| Crate form (2026-10-05) | a moulded dairy crate in warm white: walls 4, corner radius 18, a rolled rim 7 tall standing 1.6 proud, a floor 6. Long walls: one window per pint, 80 × 73 (`z` 39 → 112, corner radius 10), centred on each pint, so each front pint's woofer (`z` 39 → 107 above the crate's base) shows whole; a solid band below, so the plinths do not show through in pieces. Short walls: a hand-hold 100 × 24 at `z` 86 → 110 and four windows 38 × 28 at `z` 44 → 72. The mids (`z` 146 → 186) stand above the rim. Renders only: the crate's electronics are not designed. |

## Checks a model must pass

- Overall height 1,055; ridge at 1,010; front top edge at 860.
- Slope panel 246 long at 37.6°; ridge centred at `y = 195`.
- Mouth: lower lip at `s = 20`, upper lip at `s = 138`, 211 wide at `s = 79`.
- Throat ø 66 centred at (195, 170, 903.5); dome apex about 8 forward of it. *2026-10-08: ø 74 at (195, 125, 903.5).*
- Woofer ø 310 at `z = 290`; mid ø 170 at `z = 690`; both on `x = 195`, `y = 0`. *2026-10-08: the woofer at `z = 320`, both flush.*
- Back window 338 × 758; engraved panel 266 × 240 with its top at 770; port ø 100 at 405; post plate 128 × 64 at 144 (*a terminal cup's flange at 175 since 2026-10-08*). *2026-10-02: the birch panel is 338 × 717 (`z` 113 → 830), the engraved wordmark's baseline at 788; the rest unchanged.*
- Lid colour by flavour and the 110 band with the wordmark in it, as `spec/colorways.json` says. *2026-10-02: the gable colour by flavour, the 110 plinth with the badge on its front, the engraved wordmark on the back, and nothing on the sides.*
- The same numbers in every shot. Drift is a failure.
