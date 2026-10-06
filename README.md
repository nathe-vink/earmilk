# earmilk — handoff for renders and critic

Floorstanding hi-fi speaker shaped like a half-gallon gable-top milk carton. Concept is settled on the canvas; this repo exists to (1) produce photoreal renders the canvas cannot, (2) run the fresh-context critic against a studio bar, and (3) hold the spec so nothing drifts.

Canvas (source of truth for layout, copy and proportions): https://claude.ai/artifact/2XeD5nstYFumubxf6jdS1g

## The idea in four lines

- A serious passive three-way that is, unmistakably, a half gallon of milk — and a cabinet that outlives its skin.
- The treble fires forward from the throat of a concave bowl carved into the front gable panel. The bowl is the waveguide.
- The cabinet is birch; the carton is a two-piece sleeve of heavy printed board (tube + lid). Swap the sleeve, keep the speaker. *Amended 2026-10-02: no sleeve. The carton is the cabinet, finished in the flavour's colours; the colour is fixed per speaker. See Amendments, 2026-10-02.*
- Flavor is the colorway. Five flavors. One voicing.

Voice: dairy deadpan. The spec sheet is an FDA-style Nutrition Facts panel. One joke per surface, maximum.

## Decisions already made (do not reopen)

- Tweeter lives in the gable, facing forward, set back in a **concave** bowl. Not square, not angled up, not sunk vertically.
- Gable and fin are the **same color as the body** (the lid covers them). Bare birch shows in exactly two places: the back window and the bowl's exploded/section views. *Amended 2026-10-01: on the white-board flavours (Whole, 2%, Skim) the lid is printed in the flavour's print colour; Chocolate and Oat stay one colour, lid included.* *Amended 2026-10-02: the same colours, now as a finish on the birch gable itself; the bare birch places are the back panel and the section views.*
- **No tuning concept.** No cap, no tuning plates, no swappable tweeter modules. Flavor = colorway only.
- Nutrition Facts are **engraved** on the birch back window, above the port, with the binding posts below. The printed label frame is a separate deliverable (the label artboard), not printed on the sleeve.
- The sleeve's back panel is a frame around the birch window. *Amended 2026-10-02: no sleeve; the birch panel stays, inset in the finished back, and carries the engraved wordmark above the Nutrition Facts.*
- Sleeve options are the five flavors; "Dairy / Kraft / Night" no longer exist as names. *Amended 2026-10-02: the five flavours are finishes, chosen once.*
- Pint (desk-size, six to a crate, crate = amp + charger) is **parked**. Render it only in the mixed-crate shot; do not design its electronics.

### Amendments, 2026-10-01

Made after the first render and critic rounds, from the explorations in `explore/`. They stand with the Decisions above.

- **Lids.** Whole, 2% and Skim carry the lid (gable and fin) in the flavour's print colour. Chocolate and Oat stay one colour.
- **Band.** A printed band of the print colour, 110 mm tall, wraps the base of the sleeve (front and sides; on the back only the frame below the window). The wordmark sits in the band, reversed in the board colour, on the front and the right side. Nothing is printed under the gable.
- **Stand, optional.** A painted block in the print colour, 390 × 390 × 110, with a 6 mm reveal under the carton. It takes the band's job and its wordmark; a sleeve used on a stand is printed without the band. It does not swap with the sleeve. The speaker stays passive; if a version ever went active, the stand is where controls would live.
- **Owner's panel, optional.** A print-to-order "Have you heard me?" panel on the right side above the band, 300 × 330 mm, in the print colour: headline, a halftone portrait, four rows the owner fills in. Not on the default sleeve.
- **Dropped.** Print rings around the drivers and whole-side colour fields.
- Prices stay open: add `[STAND PRICE]` to the list.

### Amendments, 2026-10-02

Made on the v4 and v5 renders. They stand with the Decisions above and replace the 2026-10-01 amendments where the two disagree.

- **No sleeve.** The carton is the cabinet. The colourway is a finish on the birch: the body in the board colour, the gable and fin in the accent colour on Whole, 2% and Skim, Chocolate and Oat one colour all over. The colour is fixed per speaker, so every edge and bevel takes it. Nothing swaps. `[SLEEVE PRICE]`, the board-stock question and the sleeve-swap shot go away.
- **Plinth.** The band and the stand are one thing: a built-in plinth, the bottom 110 mm of the cabinet on all four sides, in the accent colour, inside the 1,055 overall height, with a 3 mm shadow line where it meets the body. (The shadow line, and the plinth sitting inside the height rather than under it, are this repo's reading; say so if either is wrong.)
- **Wordmark.** On the front only, as cast metal letters: the wordmark itself standing in relief on the plinth's front, no plate behind it, the way the lettering sits on a La Marzocco machine. On the back, engraved in the birch above the Nutrition Facts panel. Nowhere else: not on the sides, not under the gable. *(A plate version was rendered first and withdrawn the same day.)*
- **Dropped.** The owner's panel. Other milk-themed marks that are not about the owner are explored in `explore/2026-10-02/` and are proposals, not spec.
- **Shots.** 07 (sleeve swap) is retired. 02 (two rooms) loses the swap that was its point; it is rendered meanwhile with the same Whole in both rooms and needs a new brief. In 03 the fold of the lid's die-cut becomes the finish's edge at the mouth; in 04 the sleeve frame becomes the finished back around the birch panel.
- Prices: `[PAIR PRICE]` and `[CRATE PRICE]` stay open. `[SLEEVE PRICE]` and `[STAND PRICE]` are gone.
- **Back panel, contained** *(later the same day)*. The bare birch field is the Nutrition Facts panel plus a 26 mm margin all round: `x` 36 → 354, `z` 504 → 796. The port, the binding posts and the engraved wordmark sit on the finish outside it; the wordmark is engraved through the lacquer and ink-filled in the panel's brown, baseline at `z` 812; the post plate moves up to `z` 150 so it clears the plinth's shadow line. The full-height field (`x` 26 → 364, `z` 140 → 830, the same 26 margin at the sides and above the plinth) is kept as an option; both are rendered in `explore/2026-10-02/r4-*`.
- **Marks** *(later the same day)*. Two carton lines are spec and nothing else is printed: OPEN OTHER SIDE with its arrow on the back slope of the gable, 27 mm caps in the gable's other colour (board colour on the white flavours, accent on Chocolate and Oat), and SHAKE WELL on the plinth's back face, 26 mm caps reversed in the body colour. The other proposals in `explore/` are dropped.
- **Facts border** *(later the same day)*. The engraved panel is 266 × 260: "Contains no milk." sits inside the border with the same 14 mm padding as every other side. The bronze plate grows with it to `z` 484 → 796.
- **Bronze plate** *(later the same day)*. The Nutrition Facts are an engraved bronze plate, not bare birch: the Facts panel plus a 26 mm margin (x 36 → 354, z 504 → 796), 3 mm thick, 1.5 mm proud of the finish, the engraving dark with patina. The wordmark above it is the same cast metal letters as the front (44 mm, 2.5 mm proud, centred at z 826). Bare birch now shows only in the section views.
- **Shot 02, rebriefed.** The two rooms are the same pair in two homes, years apart: a bright first apartment, then a darker older house. The point is no longer the swap but that the speaker outlives its rooms, the finish fixed and the birch back ageing with the house.

### Notes, 2026-10-03

Render notes, not product decisions. Nothing here changes the Geometry or the Decisions.

- **The render path is now path-traced.** Chat image models could not hold the carton (two hand-made attempts, in `explore/2026-10-03/`), and the free Gemini API tier refuses image calls. So the model built from `spec/geometry.md` is exported from the real-time scene and rendered in Blender's Cycles (`render/pathtrace.py`, the `-pt` frames): the same geometry and copy, real light. The real-time frames stay as the layout check.
- **Rooms and sets.** The three rooms are closed boxes now (ceiling, right wall, a wall behind the camera), so the only daylight is what the window admits; the studio floor sweeps up into a backdrop. Out of frame in every shot.
- **Eased arrises.** The path tracer rounds the cabinet's edges by 4 mm in the shader (since v15; about a millimetre before), the way lacquer on birch actually sits; the silhouette does not change. Until v16 the rounding never reached the corners: each panel of the finish is its own mesh and the bevel only sees its own object, so the path tracer now joins each cabinet's finish into one object first. The prompts' rule against softening edges is about the silhouette. *Say if the spec wants the arrises dead sharp.*
- **Critic notes that are spec, not render** (path-traced round 1): the spout reads as a lens barrel at room distance (02b); the crate's wall hides the pints' drivers (06); the chair is a massing model, not furniture (02a). None acted on.

### Notes, 2026-10-04: fabrication

Fabrication notes, not product decisions. Nothing here changes the Geometry or the Decisions.

- **`fab/` turns the spec into things a shop can make:** a parametric CAD model (STEP and STL for every part), DXF cut files for the 18 mm birch panels with a cut list and nesting (three 5 x 5 ft sheets for a pair), the gable as a laminated block split for 3-axis milling or as four printable pieces, the bowl test slice, a two-piece printed port, the cast-letter wordmark and its placing templates, the engraved Facts plate, the terminal plate, vinyl stencils for the two marks, shop drawings, an acoustic worksheet, a driver shortlist and a parts list. Start at `fab/README.md`.
- **The outside is the spec; the inside is proposed.** Joinery, the mid's 8.0 L chamber, the brace, the groove, the gable's split and the tweeter pocket are marked `PROPOSAL` in `fab/params.py` and listed in `fab/README.md`.
- **From the solids:** 88.1 L net for the woofer (inside the 85 to 90 L assumed), a 152 mm port for 32 Hz, 27 kg of wood per cabinet.
- **The label and the physics disagree on one line.** The engraved Facts say 91 dB; a woofer that reaches 32 Hz in this box is rated about 90 dB, and voiced flat on this baffle the speaker should measure 85 to 88 dB. Engrave after measuring. "8 ohm" may become 6: every tweeter that fits the bowl is 4 ohm.
- **The wordmark at 44 mm type is 172 mm wide,** as the renders show; geometry.md's "about 155" is an estimate the type size overrides. The fab files follow the type size.

### Amendments, 2026-10-05: the pint and the crate

Made by the owner on the v13 crate shot ("the top driver is missing … the crate itself can be improved"). They stand with the Decisions above; the pint stays parked otherwise.

- **The pint mirrors the floorstander's drivers.** A woofer low and a mid high on its face, the big one's heights scaled by the body ratio (woofer ø 68 at 67, mid ø 40 at 160, replacing the single full-range at 95), and a small dome tweeter at the throat of its bowl, as the floorstander's sits at the throat of its own: a faceplate filling the ø 17 throat and a dome of about ø 9. The owner chose this layout over keeping one driver on the face. Its electronics stay undesigned.
- **The crate is a dairy crate.** The same 340 × 250 × 130 and 2 × 3, now moulded in warm white instead of five boards: rounded corners, a rolled rim, latticed walls, a hand-hold in each short end, a floor. The long walls have one window per pint, sized and placed to frame each front pint's woofer whole, which the plain crate's wall hid (path-traced round 1 asked whether the wall should drop; the windows answer it without changing the height); the mids stand above the rim. Still a crate and nothing more: no ports, lights, cables or controls.
- **Render polish, not product decisions** (v14): the tweeters' faceplates carry a polished chamfer, so the driver deep in each bowl reads as a driver; the domes are coated textile, not black holes; the lacquer has a faint orange peel, the cones pressed paper, the floors grain and the walls plaster; the studio adds two tall strips behind the subject for edge lines; the chair is a dining chair, not a massing model.

### Amendments, 2026-10-06: the critics' design points

Made by the owner on four points the refinement critics raised (v14 to v16). They stand with the Decisions above.

- **Dark letters on the light plinths.** The cast letters on Chocolate's cream plinth and Skim's pale blue one are dark bronze (`#6B4A2C` faces, `#45301D` sides); polished, they read as white on white, as two critic rounds said of the line-up. The other three plinths keep polished letters. The back's letters are unchanged.
- **A polished lip at the scoop.** A stainless half-round lip rings the bowl's mouth over the finish's cut edge and the bowl's joint, 4.8 wide and 1.6 proud on the floorstander and scaled on the pint, the same on every flavour, so the opening reads as a made scoop and not a hole at room distance (every critic round read it as a hole, an eye or a lens).
- **A three-quarter back view.** Shot 04 has two frames: the straight-on back as before, and a three-quarter from the back-left with the gable's end, a side and the cabinet's shadow, which every critic round on the back asked for.
- **Chocolate's throat runs dark,** from the body brown at the mouth to a dark chocolate at the throat (`#5E3A1F` to `#2B170B`; it ran cream to tan, paler than the brown face around it).
- **Render polish, not product decisions** (v17): the tweeter's faceplate sits in a moulded ring where the throat ends (the close-up's critic saw no seat); the hero's window moves to the wall behind the camera so the sun takes the fronts; the bright room's window narrows so its beam lands on the cabinet; the older room's window widens so its patch shows on the back wall.

### Notes, 2026-10-04: tools and the family

Tooling notes, not product decisions. Nothing here changes the Geometry or the Decisions.

- **From scratch.** `studio/setup.sh` installs every tool the repo uses on a bare machine (render/'s node modules, Blender's `bpy`, the CAD venv) and `python3 studio/doctor.py` runs each one for real. In a Claude Code cloud session the start hook does this before work begins. `studio/README.md` lists the tools: a path tracer for any product's scene, canvas-exact typesetting, a crossover designer, a product template.
- **Crossover, from models.** `fab/crossover.py` fits a three-way network to the shortlisted drivers (`fab/out/xover/`): Linkwitz-Riley targets at the label's 350 Hz and 2.2 kHz, 14 parts, the sum within about 2 dB from 150 Hz to 16 kHz in the model. Two numbers to carry: the tweeter, 170 mm back in the bowl, reaches a seated listener 0.37 ms after the mid; the network's impedance bottoms at 3.7 ohm, a 4 ohm speaker. Fit the built network to measurements.
- **The family.** Two spin-offs are started in `spinoffs/`, each with its own brief, model, renders and critic log: **earworm**, wired headphones whose cable is an earthworm (the saddle is the remote), and **earwig**, earbuds whose flexible tails of overlapping plates end in forceps, with a case whose lid is split like an earwig's wing covers (the wig went, 2026-10-06). Proposals for the owner; neither touches earmilk's spec.

## Geometry (mm)

Floorstander — square plan, gable-top.
- Plan 390 × 390. Body 860 tall. Gable rise 150 (front edge → ridge). Fin 45 above the ridge, ~8 thick. Total height 1,055.
- Carton proportions match a US half gallon scaled ×4.1. Slope panel length along the slope: 246.
- Cabinet: 18 mm Baltic birch, braced. The gable is a solid carved birch block on top of the body (CNC).
- Front drivers (centers from floor, on the baffle centerline): 12 in woofer at 290 (frame ø ~310); 6.5 in mid at 690 (frame ø ~170).
- Tweeter: 1 in dome with a small faceplate (≤ 62 mm). Faceplate plane is 170 back from the front face; dome center height 903.5.
- Bowl: mouth is an ellipse on the front slope panel, 211 wide × 118 long along the slope, centered 79 up the 246 slope (from 20 to 138). Throat ø 66 around the faceplate at the 170 setback. Surface is a smooth loft from mouth ellipse to throat circle — no flats, no edges. As drawn the lower lip holds the pattern to ~12° below the tweeter axis and the upper lip to ~37° above. Deeper bowl = narrower; wider mouth = wider.
- Back (bare birch window inside the sleeve frame): window x 26→364, z 40→798. Engraved Nutrition Facts panel 266 wide × 240 tall, top at z 770 *(266 × 260 since 2026-10-02)*. Round port ø ~100 centered at z 405. Binding posts on a 128 × 64 plate centered at z 144.
- Sleeve: tube 390 × 390 × 860 (open top and bottom, die-cut for woofer and mid, back panel is a frame), plus a lid covering gable + fin, die-cut at the bowl mouth. Both lock at the back seam. Board: heavy carton board / SBS, target ~1.2–1.5 mm; whether it holds a crisp fold at this size is an open test. *Amended 2026-10-02: no sleeve. The outer dimensions stay; the skin is the finish.*

Pint — 100 × 100 plan, body 200, gable 35, fin 12. Single full-range ø ~68 at 95; tiny bowl at the top. Crate 340 × 250 × 130, 2 × 3. *Amended 2026-10-05: a woofer ø 68 at 67 and a mid ø 40 at 160 on the face, a small dome tweeter at the bowl's throat; the crate is a moulded dairy crate whose windows frame the front pints' woofers.*

Stand (optional accessory, amended 2026-10-01) — 390 × 390 × 110 painted block, 6 mm reveal. With the stand: overall 1,171; tweeter axis 1,019.5. *Amended 2026-10-02: replaced by the built-in plinth, z 0 → 110 of the cabinet, accent colour, 3 mm shadow line at z 110 → 113; overall height stays 1,055.*

Wordmark on the plinth (amended 2026-10-02) — cast metal letters, no plate: Archivo Black at 44 mm type size, 2.5 mm proud, centred on the plinth's front at z 55. Back wordmark engraved in the birch panel, 36 mm type size, baseline at z 788, centred; the birch panel now runs z 113 → 830 so it has room (x 26 → 364 as before).

## Target specs (label copy — marked as targets, not measured)

Sensitivity 91 dB (2.83 V / 1 m) · 32 Hz–20 kHz ±3 dB · 8 Ω · 40–250 W · crossover 350 Hz and 2.2 kHz · 36 kg each · 1,055 mm.
Footnote stays: "Contains no milk. Not a significant source of Bluetooth."

## Colorways (flavors)

White board unless noted. Print = wordmark on front and side. Throat = bowl interior, light at the mouth → dark at the throat. *Amended 2026-10-01: print = the lid on the white flavours, a 110 mm base band, and the wordmark in the band on the front and the right side; see Amendments.* *Amended 2026-10-02: "board" is the body finish and "print" is the accent finish (gable and fin on the white flavours, the plinth on all five); the wordmark is the badge and the back engraving, not print.*

| Flavor | Board | Print | Throat (mouth → throat) |
|---|---|---|---|
| Whole | #FFFFFF | #C62828 | #C62828 → #8E1B1B |
| 2% | #FFFFFF | #1F4FCF | #1F4FCF → #153792 |
| Skim | #FFFFFF | #6FA5DC | #8FBBE8 → #4F86BF |
| Chocolate | #5E3A1F (whole board) | #F1E3CC | #5E3A1F → #2B170B *(2026-10-06; was #E2CBA3 → #A97E4F)* |
| Oat | #D9BC92 unbleached | #2B2118 | #8E6A3E → #5C4224 |

Birch: #EAD8B0 face, #D4BE95 side, engraving #6B5232. Ground for flat compositions: #F8F7F4.

## Type

Archivo Black (wordmark, label title) over Archivo (everything else). The wordmark is lowercase "earmilk", tight tracking. Nutrition Facts panel follows FDA proportions: heavy title, 10 px rule, 1 px row rules, bold labels, right-aligned values.

## What this repo produces

### 1. Renders (image generation happens here, not in chat)

Photoreal, physically plausible materials: matte printed board with visible fold creases at the gable, birch end-grain at the back window, black paper cones, the throat as a smooth painted bowl. No grilles. No glossy plastic. Proportions exactly as the geometry above — the carton silhouette is the whole idea, so do not "improve" it.

Shot list, in priority order:
1. **Hero pair in a room.** Whole, late-afternoon window light, a chair or sofa arm in frame for scale, speakers ~2 m apart, 3/4 view, camera at 1.2 m with a ~50 mm look.
2. **Two rooms, years apart.** The same floor spot and the same speaker, once in Whole in a bright apartment, once in Oat in a darker, older room. This is the sleeve argument; it must read as one object that changed its skin. *Amended 2026-10-02: no sleeve, so no skin change. Rebriefed: the same pair in two homes, years apart, a bright first apartment and then a darker older house; the point is that the speaker outlives its rooms.*
3. **Bowl close-up.** Front 3/4 at gable height, the throat and the dome in focus, the fold of the lid's die-cut visible at the mouth edge. *Amended 2026-10-02: the mouth edge is the finish's edge on the carved gable.*
4. **Back.** Straight-on, engraved label legible, port and posts, the sleeve frame around the birch. *Amended 2026-10-02: the finished back with the bare birch field around the Facts panel only, the wordmark engraved above it, the port and posts on the finish below.* *Amended 2026-10-06: two frames, (a) straight-on as before and (b) a three-quarter from the back-left, about 33° off the back face and 10° up, with the gable's end, a side and the cabinet's shadow in frame.*
5. **Five flavors lineup.** Flat ground, equal spacing, in flavor order.
6. **Mixed crate** on a desk, six pints, five flavors.
7. **Sleeve swap**, three frames: lid off, tube sliding, new flavor on. *Retired 2026-10-02: no sleeve.*

Keep every render's dimensions consistent; drift in the carton's proportions between shots is a failure.

### 2. Critic

Run after each render batch. Fresh context, screenshot only — the critic sees images, not the brief, not this file. Prompt it as a design-studio creative director with a shipping bar: name the three biggest gaps, say what a studio would fix first, score /10. Iterate at most three rounds per shot. Log each round in `critic/LOG.md` (shot, round, gaps, score, what changed).

### 3. Spec drift check

Before any render or edit, re-read the Geometry and Decisions sections. If a change to them seems necessary, stop and ask; do not improvise a new mechanism, a new flavor, or a new driver layout.

## Open questions (do not assume answers)

- Price points for the pair, a sleeve set, and the crate. Leave as `[PAIR PRICE]`, `[SLEEVE PRICE]`, `[CRATE PRICE]`, and since the amendments `[STAND PRICE]`. *Amended 2026-10-02: `[PAIR PRICE]` and `[CRATE PRICE]` only.*
- Driver selection and port tuning. The 32 Hz target assumes ~85–90 L net for the woofer; confirm before quoting it as more than a target. *2026-10-04: the CAD measures 88.1 L net; `fab/README.md` has a driver shortlist, the port (152 mm for 32 Hz) and a simulation. Proposals, not answers.*
- Whether the bowl works as a waveguide. The test is physical: one carved gable, one candidate tweeter, on/off-axis measurements vs. a flat baffle. Renders do not settle this. *2026-10-04: `fab/out/stl/gable-test-slice.stl` is that gable, printable in a weekend.*
- *Added 2026-10-04, from the crossover model:* whether the label's crossover points (350 Hz and 2.2 kHz) survive measurement, whether the 0.37 ms the bowl puts between mid and tweeter is handled passively or the tweeter comes forward, and whether the label can say 4 ohm.
- *Added 2026-10-04, from fabrication:* whether the Facts should state targets or measured figures (91 dB and 8 ohm are unlikely as measured; the plate is permanent); whether the gable may be printed and painted instead of carved birch; the letters' metal (silver as rendered: stainless or aluminium; or brass to sit with the bronze plate); whether the wordmark's width (172 mm at 44 mm type) or geometry.md's "about 155" is the one that matters.
- *Added 2026-10-03, from the path-traced critic rounds:* whether the pint crate's wall should drop so the drivers show; whether the spout's dome needs a different read at room distance (three rounds called it a lens barrel); whether the cast letters on Chocolate and Oat should be a darker metal, since polished metal on a cream plinth reads as blank in a pale studio; and whether the tweeter wants a visible flange in the bowl. All geometry or materials; none acted on in renders.
- Board stock for the sleeve and whether the lock survives repeated swaps. *Gone 2026-10-02 with the sleeve. In its place: the finish system (lacquer, paint or laminate over the birch) and the badge's metal are open.*

## Suggested layout

```
spec/        geometry.md (this file's numbers, expanded), colorways.json
copy/        label.md, hero.md
prompts/     one file per shot, versioned
renders/     YYYY-MM-DD/shot-NN-vN.png
critic/      LOG.md
render/      the model, the real-time and path-traced renderers
fab/         fabrication: CAD, cut files, drawings, acoustics, crossover, parts list (fab/README.md)
studio/      the tools for any product: setup, doctor, path tracer, typesetting, crossover designer, template
spinoffs/    the rest of the family, one folder each: earworm (wired headphones), earwig (earbuds)
.claude/     the cloud session's start hook and the project skills (new-product, pathtrace, critic-round, fab-package)
```

## Deliver pass already applied (for context)

Cut: the cap and all tuning concepts; the four-way treble study (replaced by one section); printed Nutrition Facts on the side panel (now engraved on the back; side carries the wordmark); the flavor word under the wordmark; the Gallery sleeve; the Ingredients footnote; duplicate engravings; the full-carton sleeve (now tube + lid); the Dairy/Kraft/Night skins (folded into flavors).
