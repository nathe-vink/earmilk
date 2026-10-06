# earwig: handoff for design, renders and critic

True-wireless Bluetooth earbuds in the earmilk family. One joke, said once per surface, on a product that would be
good without it. This file is the brief: the idea, the decisions, the numbers, the shots. `params.py` holds the
numbers the model is built from.

Status: concept, third pass (2026-10-06). Everything below is a *proposal* until the owner signs it, except what the
owner asked for: a little less grotesque (2026-10-04); the tails hanging loose like the earworm's cable, a flexible
exoskeleton instead of a stiff stem; no hair on the case; a lid split like an earwig's wing covers (2026-10-06).

## The idea in four lines

- True-wireless earbuds in glossy chestnut, the colour of an earwig.
- Each bud's tail is a flexible run of overlapping plates, like the earworm's cable or a jointed toy snake, that hangs
  loose from the ear and drapes on a table, and ends in a small pair of forceps with rounded tips. Pinching them is the
  control: play, pause, answer.
- The charging case has a cream base and a chestnut lid split down the middle, front to back, like an earwig's folded
  wing covers.
- The buds are the insect, from head to forceps; the lid is its back. One quiet detail per surface.

Voice: deadpan. The box could say "Hypoallergenic. Not a real earwig." and nothing more.

## Decisions (proposals until the owner signs them)

- **Bud**: one lofted body, 20.4 x 17.2 mm across, 24 mm from its top to the neck where the tail leaves it, a satin
  collar round the neck.
- **Shell** in two parts that meet on a parting line across the head: the outer half glossy chestnut, the inner half,
  the nozzle's side, a lighter satin chestnut with the wear sensor's dark gloss window. Signs that it was made.
- **Tail**: 46 mm of overlapping plates from the collar to the forceps, 5.3 mm across at the root tapering to 3.8, one
  plate every 2.3 mm, each flaring toward its rear lip and lapping over the next. Moulded plates over a soft core, so it
  bends anywhere and hangs loose; the antenna and the microphone's lead run inside it.
- **Forceps**: the tail's last plate, a small knob, carries two short arms that bow gently apart and end in rounded
  tips, 3.2 mm thick at the root, 10.5 mm long: a pinch, not a stab. Pinching flexes them onto a force sensor in the
  knob; the voice microphone opens between them.
- **Nozzle** angled into the canal (inward, forward, a little up), 5.6 mm, with a dark mesh just inside its end and a
  medium silicone tip, 12.4 mm, in translucent pale taupe: a stem on the nozzle and a thin skirt.
- **Case**: 62 x 26 x 48, every edge rounded at 10, the lid splitting at 62 % of the height (29.8 mm), a status light
  on the front of the base. The base cream, glossy; the lid the buds' chestnut lacquer, with a seam 0.6 wide and 0.45
  deep down its middle, front to back over the top: the wing covers.

## Geometry (mm)

| | |
|---|---|
| Bud body (x, y, z) | 20.4 x 17.2 x 24 to the neck |
| Tail: length, diameter root to tip, plate pitch, flare | 46; 5.3 to 3.8; 2.3; 21 % of the radius |
| Forceps: length, root thickness, tips | 10.5, 3.2, rounded (1.36 across) |
| Ear tip | 12.4 diameter, 7.4 long |
| Wear sensor window | 2.2 x 3.2 oval on the inner half |
| Case (w x d x h), edge radius | 62 x 26 x 48, 10 |
| Lid split from the floor; wing seam | 29.8; 0.6 wide, 0.45 deep |

## Colourways (proposals)

| Name | Buds and lid | Case base | Notes |
|---|---|---|---|
| Chestnut (hero) | `#5a2f1b` gloss, `#7d4a2e` satin inside, tips `#9a8e82` | cream `#ece4d6` | the common earwig |
| Black | `#1d1714` gloss, `#3a2f29` satin | cream | the night one |
| Amber | `#8a4a1c` gloss, `#a8673a` satin | cream | a young earwig, just moulted |

## Shots

1. **Hero.** The case standing left of centre with headroom, its wing covers catching the light; the two buds lying on
   their sides in front of it and to its right, each tail draped back toward the group and curling its own way, as buds
   lie on a table. Warm cream sweep darkening behind, everything sharp. The cream base is the brightest thing in frame:
   a key low and just right of the camera, a white card low in front for the lid's face, tall strips either side for
   highlight lines, pins for a glint on each bud and on the lid's corner, little fill.
2. **Detail.** From above (about 37 degrees), one bud in profile against the cream floor (silicone tip up, the tail
   curling away to the forceps), the case behind it for context, whole, with headroom. Everything sharp; one key from
   high camera-left, so the case throws its shadow back and to the right.

## Where the renders stand

The 2026-10-06 look (no wig, flexible tails, the wing-case lid; v7) starts its own critic count in `critic/LOG.md`. The
softer look with the wig (v4 to v6) had three rounds: hero 5, 5, 5 and detail 4, 5, 6; its renders stay in `renders/`.
What the earlier rounds taught, carried into v7:

- **Light.** The cream base brighter than the backdrop: a key low and near the camera, so the case's face takes more of
  it than the floor does; strips for lines on the gloss; a pin for a crisp highlight on each lacquered part.
- **Context in macro.** Alone and brown on brown, the bud read as a pipe; with its silicone tip and the case in frame
  it reads as an earbud. Keep the case in the close-up, whole.
- **Headroom.** Leave 10 to 15 % on every side for a 16:9 crop, and floor between the pieces: outlines that touch merge.
- **Focus.** Everything sharp: shallow focus on a 50 mm object reads as per-object blur.

## What a render must not do

- Give the buds antennae, legs, eyes or wings, or the case a face.
- Change the proportions in `params.py`, or let the forceps grow back into claws: they are small, gentle, rounded.
- Make the tail stiff: it hangs, drapes and curls; no two lie the same way.

## Open questions (do not assume answers)

- Electronics: a donor module or a designed board; where the battery goes now the stem is a flexible tail (the body,
  or a slim cell in the knob?).
- Forceps as the control: force sensor, or a capacitive pinch?
- The tail in the case: does it coil into a groove round each seat, or lie in a channel under the lid?
- `[PRICE]`.

## Making one (vibe fab)

- **Buds**: resin-print `out/stl/bud-*.stl`, `inner-*.stl` and `collar-*.stl` in a tough resin, sand, and lacquer
  chestnut over a sealer. The render model is solid: hollow it and lay out the parts before printing (next step).
  The practical route is a reshell: open a cheap TWS pair and move the board, driver (usually 10 mm) and battery into
  the printed shells.
- **Tail**: thread printed plates (flexible resin, chestnut) over a silicone cord with the antenna and microphone lead
  inside, like a toy snake, and glue the last one to the printed forceps (`forceps.stl`).
- **Case**: print base and lid, cut the wing seam with a fine file if the print softens it, lacquer the lid chestnut,
  add two 3 x 2 mm magnets for the lid and two for each bud's seat, and move the donor case's charging board across.
- **Tips**: buy medium silicone tips with a 5 to 6 mm bore.

## Files

- `params.py` the numbers (PROPOSAL, PLACEHOLDER)
- `model.py` builds the buds, collars, sensor windows, forceps, tips and case in build123d and exports `out/stl`,
  `out/step`, `out/parts.json` (with the tail's root and size in each bud's frame)
- `scene.py` writes `shots.json`: each bud's resting pose, each tail's draped path (drawn plate by plate by the path
  tracer), the forceps at its end, the lights and cameras
- `renders/` hero and detail, by version; `critic/LOG.md` one row per critic round
