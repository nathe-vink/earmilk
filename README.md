# earmilk — handoff for renders and critic

Floorstanding hi-fi speaker shaped like a half-gallon gable-top milk carton. Concept is settled on the canvas; this repo exists to (1) produce photoreal renders the canvas cannot, (2) run the fresh-context critic against a studio bar, and (3) hold the spec so nothing drifts.

Canvas (source of truth for layout, copy and proportions): https://claude.ai/artifact/2XeD5nstYFumubxf6jdS1g

## The idea in four lines

- A serious passive three-way that is, unmistakably, a half gallon of milk — and a cabinet that outlives its skin.
- The treble fires forward from the throat of a concave bowl carved into the front gable panel. The bowl is the waveguide.
- The cabinet is birch; the carton is a two-piece sleeve of heavy printed board (tube + lid). Swap the sleeve, keep the speaker.
- Flavor is the colorway. Five flavors. One voicing.

Voice: dairy deadpan. The spec sheet is an FDA-style Nutrition Facts panel. One joke per surface, maximum.

## Decisions already made (do not reopen)

- Tweeter lives in the gable, facing forward, set back in a **concave** bowl. Not square, not angled up, not sunk vertically.
- Gable and fin are the **same color as the body** (the lid covers them). Bare birch shows in exactly two places: the back window and the bowl's exploded/section views. *Amended 2026-10-01: on the white-board flavours (Whole, 2%, Skim) the lid is printed in the flavour's print colour; Chocolate and Oat stay one colour, lid included.*
- **No tuning concept.** No cap, no tuning plates, no swappable tweeter modules. Flavor = colorway only.
- Nutrition Facts are **engraved** on the birch back window, above the port, with the binding posts below. The printed label frame is a separate deliverable (the label artboard), not printed on the sleeve.
- The sleeve's back panel is a frame around the birch window.
- Sleeve options are the five flavors; "Dairy / Kraft / Night" no longer exist as names.
- Pint (desk-size, six to a crate, crate = amp + charger) is **parked**. Render it only in the mixed-crate shot; do not design its electronics.

### Amendments, 2026-10-01

Made after the first render and critic rounds, from the explorations in `explore/`. They stand with the Decisions above.

- **Lids.** Whole, 2% and Skim carry the lid (gable and fin) in the flavour's print colour. Chocolate and Oat stay one colour.
- **Band.** A printed band of the print colour, 110 mm tall, wraps the base of the sleeve (front and sides; on the back only the frame below the window). The wordmark sits in the band, reversed in the board colour, on the front and the right side. Nothing is printed under the gable.
- **Stand, optional.** A painted block in the print colour, 390 × 390 × 110, with a 6 mm reveal under the carton. It takes the band's job and its wordmark; a sleeve used on a stand is printed without the band. It does not swap with the sleeve. The speaker stays passive; if a version ever went active, the stand is where controls would live.
- **Owner's panel, optional.** A print-to-order "Have you heard me?" panel on the right side above the band, 300 × 330 mm, in the print colour: headline, a halftone portrait, four rows the owner fills in. Not on the default sleeve.
- **Dropped.** Print rings around the drivers and whole-side colour fields.
- Prices stay open: add `[STAND PRICE]` to the list.

## Geometry (mm)

Floorstander — square plan, gable-top.
- Plan 390 × 390. Body 860 tall. Gable rise 150 (front edge → ridge). Fin 45 above the ridge, ~8 thick. Total height 1,055.
- Carton proportions match a US half gallon scaled ×4.1. Slope panel length along the slope: 246.
- Cabinet: 18 mm Baltic birch, braced. The gable is a solid carved birch block on top of the body (CNC).
- Front drivers (centers from floor, on the baffle centerline): 12 in woofer at 290 (frame ø ~310); 6.5 in mid at 690 (frame ø ~170).
- Tweeter: 1 in dome with a small faceplate (≤ 62 mm). Faceplate plane is 170 back from the front face; dome center height 903.5.
- Bowl: mouth is an ellipse on the front slope panel, 211 wide × 118 long along the slope, centered 79 up the 246 slope (from 20 to 138). Throat ø 66 around the faceplate at the 170 setback. Surface is a smooth loft from mouth ellipse to throat circle — no flats, no edges. As drawn the lower lip holds the pattern to ~12° below the tweeter axis and the upper lip to ~37° above. Deeper bowl = narrower; wider mouth = wider.
- Back (bare birch window inside the sleeve frame): window x 26→364, z 40→798. Engraved Nutrition Facts panel 266 wide × 240 tall, top at z 770. Round port ø ~100 centered at z 405. Binding posts on a 128 × 64 plate centered at z 144.
- Sleeve: tube 390 × 390 × 860 (open top and bottom, die-cut for woofer and mid, back panel is a frame), plus a lid covering gable + fin, die-cut at the bowl mouth. Both lock at the back seam. Board: heavy carton board / SBS, target ~1.2–1.5 mm; whether it holds a crisp fold at this size is an open test.

Pint — 100 × 100 plan, body 200, gable 35, fin 12. Single full-range ø ~68 at 95; tiny bowl at the top. Crate 340 × 250 × 130, 2 × 3.

Stand (optional accessory, amended 2026-10-01) — 390 × 390 × 110 painted block, 6 mm reveal. With the stand: overall 1,171; tweeter axis 1,019.5.

## Target specs (label copy — marked as targets, not measured)

Sensitivity 91 dB (2.83 V / 1 m) · 32 Hz–20 kHz ±3 dB · 8 Ω · 40–250 W · crossover 350 Hz and 2.2 kHz · 36 kg each · 1,055 mm.
Footnote stays: "Contains no milk. Not a significant source of Bluetooth."

## Colorways (flavors)

White board unless noted. Print = wordmark on front and side. Throat = bowl interior, light at the mouth → dark at the throat. *Amended 2026-10-01: print = the lid on the white flavours, a 110 mm base band, and the wordmark in the band on the front and the right side; see Amendments.*

| Flavor | Board | Print | Throat (mouth → throat) |
|---|---|---|---|
| Whole | #FFFFFF | #C62828 | #C62828 → #8E1B1B |
| 2% | #FFFFFF | #1F4FCF | #1F4FCF → #153792 |
| Skim | #FFFFFF | #6FA5DC | #8FBBE8 → #4F86BF |
| Chocolate | #5E3A1F (whole board) | #F1E3CC | #E2CBA3 → #A97E4F |
| Oat | #D9BC92 unbleached | #2B2118 | #8E6A3E → #5C4224 |

Birch: #EAD8B0 face, #D4BE95 side, engraving #6B5232. Ground for flat compositions: #F8F7F4.

## Type

Archivo Black (wordmark, label title) over Archivo (everything else). The wordmark is lowercase "earmilk", tight tracking. Nutrition Facts panel follows FDA proportions: heavy title, 10 px rule, 1 px row rules, bold labels, right-aligned values.

## What this repo produces

### 1. Renders (image generation happens here, not in chat)

Photoreal, physically plausible materials: matte printed board with visible fold creases at the gable, birch end-grain at the back window, black paper cones, the throat as a smooth painted bowl. No grilles. No glossy plastic. Proportions exactly as the geometry above — the carton silhouette is the whole idea, so do not "improve" it.

Shot list, in priority order:
1. **Hero pair in a room.** Whole, late-afternoon window light, a chair or sofa arm in frame for scale, speakers ~2 m apart, 3/4 view, camera at 1.2 m with a ~50 mm look.
2. **Two rooms, years apart.** The same floor spot and the same speaker, once in Whole in a bright apartment, once in Oat in a darker, older room. This is the sleeve argument; it must read as one object that changed its skin.
3. **Bowl close-up.** Front 3/4 at gable height, the throat and the dome in focus, the fold of the lid's die-cut visible at the mouth edge.
4. **Back.** Straight-on, engraved label legible, port and posts, the sleeve frame around the birch.
5. **Five flavors lineup.** Flat ground, equal spacing, in flavor order.
6. **Mixed crate** on a desk, six pints, five flavors.
7. **Sleeve swap**, three frames: lid off, tube sliding, new flavor on.

Keep every render's dimensions consistent; drift in the carton's proportions between shots is a failure.

### 2. Critic

Run after each render batch. Fresh context, screenshot only — the critic sees images, not the brief, not this file. Prompt it as a design-studio creative director with a shipping bar: name the three biggest gaps, say what a studio would fix first, score /10. Iterate at most three rounds per shot. Log each round in `critic/LOG.md` (shot, round, gaps, score, what changed).

### 3. Spec drift check

Before any render or edit, re-read the Geometry and Decisions sections. If a change to them seems necessary, stop and ask; do not improvise a new mechanism, a new flavor, or a new driver layout.

## Open questions (do not assume answers)

- Price points for the pair, a sleeve set, and the crate. Leave as `[PAIR PRICE]`, `[SLEEVE PRICE]`, `[CRATE PRICE]`, and since the amendments `[STAND PRICE]`.
- Driver selection and port tuning. The 32 Hz target assumes ~85–90 L net for the woofer; confirm before quoting it as more than a target.
- Whether the bowl works as a waveguide. The test is physical: one carved gable, one candidate tweeter, on/off-axis measurements vs. a flat baffle. Renders do not settle this.
- Board stock for the sleeve and whether the lock survives repeated swaps.

## Suggested layout

```
spec/        geometry.md (this file's numbers, expanded), colorways.json
copy/        label.md, hero.md
prompts/     one file per shot, versioned
renders/     YYYY-MM-DD/shot-NN-vN.png
critic/      LOG.md
```

## Deliver pass already applied (for context)

Cut: the cap and all tuning concepts; the four-way treble study (replaced by one section); printed Nutrition Facts on the side panel (now engraved on the back; side carries the wordmark); the flavor word under the wordmark; the Gallery sleeve; the Ingredients footnote; duplicate engravings; the full-carton sleeve (now tube + lid); the Dairy/Kraft/Night skins (folded into flavors).
