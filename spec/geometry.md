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
| 12 in woofer | 290 | ~310 | `x` 40 → 350, `z` 135 → 445 |
| 6.5 in mid | 690 | ~170 | `x` 110 → 280, `z` 605 → 775 |

Black paper cones. No grilles. The sleeve's die-cuts equal the frame diameters (as drawn, Sleeves artboard). Gap between the woofer's top and the mid's bottom: 160 (derived). Mid top to the front top edge: 85 (derived).

### Tweeter

| | |
|---|---|
| Unit | 1 in dome with a small faceplate, ≤ 62 mm |
| Axis | horizontal, firing forward (toward −y), along `x = 195`, `z = 903.5` |
| Faceplate plane | `y = 170`, i.e. 170 back from the front face |
| Faceplate (as drawn) | 62 tall, 6 thick: `y` 170 → 176 |
| Dome apex (as drawn) | about 8 forward of the faceplate plane, `y ≈ 162` |
| Body behind the faceplate (as drawn) | about 38 deep × 60 tall, `y` 176 → 214, inside the block |

### Bowl (the waveguide)

| | |
|---|---|
| Throat | circle ø 66 in the plane `y = 170`, centre (195, 170, 903.5): `x` 162 → 228, `z` 870.5 → 936.5 |
| Mouth | ellipse lying in the front slope plane. Along the slope: `s` 20 → 138 (118 long), centre `s = 79`. Across: 211 wide, `x` 89.5 → 300.5 |
| Mouth lower lip (derived) | (195, 15.9, 872.2) |
| Mouth centre (derived) | (195, 62.6, 908.2) |
| Mouth upper lip (derived) | (195, 109.4, 944.1) |
| Mouth side lips (derived) | (89.5, 62.6, 908.2) and (300.5, 62.6, 908.2) |
| Surface | one smooth loft from the mouth ellipse to the throat circle. No flats, no edges. Painted: light at the mouth, dark at the throat (`spec/colorways.json`). |
| Centreline section (as drawn) | the floor runs almost straight from the lower lip back to the throat bottom, sagging about 3 below that chord; the ceiling arches about 6 above the chord from the throat top to the upper lip. The hollow reads as a concave bowl, deeper above the axis than below it. |
| Clearances (derived) | the throat bottom is 10.5 above the body top; the slope surface directly above the throat is at `z ≈ 991`; the bowl is carved entirely within the block. |

**Pattern angles.** The README's ~12° down and ~37° up are measured from the dome apex, 8 forward of the faceplate plane, which is how the Section artboard draws them. Derived from the lip coordinates above: 12.1° down and 37.7° up from the apex at `y = 162`; 11.5° and 33.8° if measured from the faceplate plane instead. Build the model with the apex at `y ≈ 162` and the README's figures hold.

### Back (plane `y = 390`)

| | |
|---|---|
| Birch window (bare, inside the sleeve frame) | `x` 26 → 364, `z` 40 → 798, so 338 × 758. *Amended 2026-10-02: a bare birch field in the finished back. Default, contained: the Facts panel plus a 26 margin all round, `x` 36 → 354, `z` 504 → 796 (318 × 292); the port, the posts and the engraved wordmark sit on the finish outside it. Option, full: `x` 26 → 364, `z` 140 → 830 (338 × 690), the same 26 margin at the sides and above the plinth's shadow line.* |
| Sleeve frame margins (derived) | 26 each side, 40 at the bottom, 62 at the top. *2026-10-02: 26 each side, the plinth and its shadow line below, 30 at the top.* |
| Engraved wordmark (amended 2026-10-02) | "earmilk", Archivo Black, 36 mm type size, centred on `x = 195`. With the contained field: on the finish above it, baseline at `z = 812`, engraved through the lacquer and ink-filled in the panel's brown. With the full field: inside it, baseline at `z = 788`. *Superseded the same day: the back wordmark is the same cast metal letters as the front, 44 mm type, 2.5 proud, centred on `x = 195` at `z = 826`.* |
| Bronze plate (2026-10-02, replaces the bare birch field as the default) | the Facts panel plus a 26 margin: `x` 36 → 354, `z` 484 → 796 (318 × 312), 3 thick, 1.5 proud of the finish, 3 corner radius; the Facts engraved into it, dark with patina. The port, the posts and the letters sit on the finish outside it. |
| Marks (spec since 2026-10-02) | OPEN OTHER SIDE with its arrow, 27 mm caps, centred on the back slope, in the gable's other colour. SHAKE WELL, 26 mm caps, centred on the plinth's back face at `z = 55`, reversed in the body colour. Nothing else is printed. |
| Engraved Nutrition Facts panel | 266 × 240 with its top at `z = 770`: `x` 62 → 328, `z` 530 → 770. Copy and proportions in `copy/label.md`, engraved version. *Amended 2026-10-02: 266 × 260, `z` 510 → 770, so "Contains no milk." sits inside the border with the same 14 mm padding as every other side.* |
| Port | round, ø ~100, centre (195, 390, 405): `z` 355 → 455. As drawn: a 92 bore in a 112 flange. |
| Binding post plate | 128 × 64, centre `z = 144`: `x` 131 → 259, `z` 112 → 176. As drawn: dark plate, two posts ø 24 at ±32 from the centre; seen from behind, red on the left, black on the right. *Amended 2026-10-02: centre `z = 150` (`z` 118 → 182) so the plate clears the plinth's shadow line; inside the full field, centre `z = 185`.* |
| Vertical gaps (derived) | 75 between the panel's bottom and the port's top; 179 between the port's bottom and the plate's top. |

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
| Wordmark on the plinth | cast metal letters, the wordmark itself with no plate behind it, the way the lettering stands on a La Marzocco machine: Archivo Black, 44 mm type size, 2.5 proud, polished faces and satin sides, centred on the plinth's front at `z` 55 (about 155 wide). *The 2026-10-02 plate (180 × 56) lasted one render and is withdrawn.* |
| Wordmark elsewhere | engraved on the back panel (above); nowhere else |
| Edges | every edge and bevel takes the colour of its face, which a sleeve could not do |

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
| Woofer (2026-10-05) | frame ø 68, centre `z = 67`: `z` 33 → 101 (the floorstander's 290 / 860 of the body). Clears the plinth (top at 28.2 plus the shadow line). |
| Mid (2026-10-05) | frame ø 40, centre `z = 160`: `z` 140 → 180 (the floorstander's 690 / 860), 20 below the body's top. |
| Bowl | "tiny bowl at the top", not dimensioned. Assumption for the crate shot only: the floorstander's bowl scaled by the plan ratio 100/390, so a mouth of about 54 × 30 and a throat of about ø 17. |
| Tweeter (2026-10-05) | a small dome at the bowl's throat: faceplate ø 16.6 (the throat less 2 %), 1.4 thick; dome base ø 8.8, apex 2.4 forward. Three drivers, as the floorstander has. |
| Not a uniform scale of the floorstander (derived) | plan ×0.256, body ×0.233, gable ×0.233, fin ×0.267. The pint is squatter, like a real pint next to a half gallon. |
| Crate | 340 × 250 × 130, holding 2 × 3 pints. The pints stand about 117 proud of the rim (derived). Six pints, five flavors, so one flavor appears twice; which one is not specified. |
| Crate form (2026-10-05) | a moulded dairy crate in warm white: walls 4, corner radius 18, a rolled rim 7 tall standing 1.6 proud, a floor 6. Long walls: one window per pint, 80 × 73 (`z` 39 → 112, corner radius 10), centred on each pint, so each front pint's woofer (`z` 39 → 107 above the crate's base) shows whole; a solid band below, so the plinths do not show through in pieces. Short walls: a hand-hold 100 × 24 at `z` 86 → 110 and four windows 38 × 28 at `z` 44 → 72. The mids (`z` 146 → 186) stand above the rim. Renders only: the crate's electronics are not designed. |

## Checks a model must pass

- Overall height 1,055; ridge at 1,010; front top edge at 860.
- Slope panel 246 long at 37.6°; ridge centred at `y = 195`.
- Mouth: lower lip at `s = 20`, upper lip at `s = 138`, 211 wide at `s = 79`.
- Throat ø 66 centred at (195, 170, 903.5); dome apex about 8 forward of it.
- Woofer ø 310 at `z = 290`; mid ø 170 at `z = 690`; both on `x = 195`, `y = 0`.
- Back window 338 × 758; engraved panel 266 × 240 with its top at 770; port ø 100 at 405; post plate 128 × 64 at 144. *2026-10-02: the birch panel is 338 × 717 (`z` 113 → 830), the engraved wordmark's baseline at 788; the rest unchanged.*
- Lid colour by flavour and the 110 band with the wordmark in it, as `spec/colorways.json` says. *2026-10-02: the gable colour by flavour, the 110 plinth with the badge on its front, the engraved wordmark on the back, and nothing on the sides.*
- The same numbers in every shot. Drift is a failure.
