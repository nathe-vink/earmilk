# earwig: handoff for design, renders and critic

True-wireless Bluetooth earbuds in the earmilk family. One joke, said once per surface, on a product that would be
good without it. This file is the brief: the idea, the decisions, the numbers, the shots. `params.py` holds the
numbers the model is built from.

Status: concept, second pass (2026-10-05). Everything below is a *proposal* until the owner signs it, except what the
owner asked for: a little less grotesque (2026-10-04). Since then the forceps are shorter with rounded tips, the stem's
segments are overlapping plates, the case is cream and the bob is sleek and side-parted.

## The idea in four lines

- Stem-style true-wireless earbuds in glossy chestnut, the colour of an earwig.
- Each stem ends in a small pair of forceps with rounded tips. Pinching them is the control: play, pause, answer. The
  stem is four overlapping plates, like an insect's abdomen or a jointed toy.
- The cream charging case wears a wig: a sleek bob of fine synthetic hair, parted to one side, cut level just below
  the lid's edge. The lid opens with its hair on.
- Ear wig. The buds are the insect; the case is the wig. One joke per surface.

Voice: deadpan. The box could say "Hypoallergenic. Not a real earwig." and nothing more.

## Decisions (proposals until the owner signs them)

- **Bud**: one lofted body and stem, 20.4 x 17.2 mm across the body, 46 mm tall from the body's top to the forceps'
  tips. The stem hangs from the body's outer side, as on every stem bud, and is four plates that each widen toward
  their lower edge and lap over the next.
- **Shell** in two parts that meet on a parting line across the head: the outer half (and the stem) glossy chestnut,
  the inner half, the nozzle's side, a lighter satin chestnut. Signs that it was made, and a place for the seam to go.
- **Nozzle** angled into the canal (inward, forward, a little up), 5.6 mm, with a dark mesh just inside its end and a
  medium silicone tip, 12.4 mm, in translucent pale taupe: a stem on the nozzle and a thin skirt. (A cream inner half
  round a dark tip read as an eyeball; a solid dome read as putty.)
- **Forceps**: two short arms that bow gently apart and end in rounded tips, 2.8 mm thick at the root, 9.5 mm long:
  a pinch, not a stab. Pinching flexes them onto a force sensor in the stem's end; the voice microphone opens between
  them, where the noise is least.
- **Case**: 62 x 26 x 48, every edge rounded at 10, the lid splitting at 62 % of the height (29.8 mm), a status light
  on the front. Cream, glossy.
- **The wig**: synthetic doll hair (70 micron, about 30,000 strands) rooted on the lid's crown, parted 5 mm to one
  side, combed sleekly down over the edges and cut level 0.7 mm below the split, so the bob just covers the seam.

## Geometry (mm)

| | |
|---|---|
| Bud body (x, y, z) | 20.4 x 17.2 x 20 |
| Stem: length, plates | 17.7; four plates 3.4 to 3.6 long, each 0.24 proud at its lower edge |
| Forceps: length, root thickness, tips | 9.5, 2.8, rounded (1.24 across) |
| Bud overall height | 46 |
| Ear tip | 12.4 diameter, 7.4 long |
| Case (w x d x h), edge radius | 62 x 26 x 48, 10 |
| Lid split from the floor | 29.8 |
| Bob cut below the split, part from the centre | 0.7, 5 |

## Colourways (proposals)

The buds stay chestnut (an earwig is chestnut) and the case stays cream; the wig changes.

| Name | Buds | Case | Wig | Notes |
|---|---|---|---|---|
| Chestnut (hero) | `#5a2f1b` gloss, `#7d4a2e` satin inside, tips `#a08f80` | cream `#ece4d6` | chestnut (melanin 0.55, redness 0.42) | |
| Blonde | chestnut | cream | ash blonde | |
| Ginger | chestnut | cream | copper | |
| Black | chestnut | cream | blue-black | |
| Silver | chestnut | cream | silver grey | the distinguished one |

## Shots

1. **Hero.** The case standing in its bob, left of centre with headroom; the two buds lying on their sides in front of
   it and to its right, both tails pointing back into the group, as buds lie on a table. Warm cream sweep darkening
   behind, everything sharp. The white case is the brightest thing in frame: a key low and just right of the camera,
   tall strips either side for highlight lines, a small pin for a glint on each bud, a low back light to outline the
   hair, little fill.
2. **Detail.** From above (about 37 degrees), one bud in profile against the cream floor (silicone tip up, stem,
   forceps), the wigged case behind it for context, whole. Everything sharp; one key from high camera-left, so the case
   throws its shadow back and to the right. Alone in macro against a brown background the bud was read as a tobacco
   pipe; context keeps it an earbud. From low, the floor's far edge lined up with the hair's lower edge (round 2).

## Where the renders stand

The softer look (v4, 2026-10-05) starts its own critic count; v6 is its round 3, the last. The first look's three rounds per shot are in
`critic/LOG.md`: hero 5, 5, 5; close-up 4 (read as a tobacco pipe), 4, 4; `renders/hero-v3.png` and `detail-v3.png`.
What those rounds taught, carried into v4:

- **Light.** Key to fill near 3:1, a harder key so every forceps tip and the case leave a dense contact shadow, a rim
  behind the case for the hair's ends. Strips beside the case gave the gloss its lines; keep them.
- **The groom.** Roots that rise less along the part (or a skin-tone part line), no seam down the front (the clump grid
  and the part's ends meet there), some locks crossing, a few flyaways. At 3 % flyaways the bob turns to frizz.
- **Context in macro.** Alone and brown on brown, the bud read as a pipe; with its silicone tip and the wigged case in
  frame it reads as an earbud. Keep the case in the close-up, whole and soft.
- **Headroom.** Leave 10 to 15 % on every side for a 16:9 crop, and floor between the pieces: outlines that touch merge.
- **Focus.** Everything sharp (stopped down or stacked): shallow focus on a 50 mm object reads as per-object blur.

## What a render must not do

- Give the buds antennae, legs, eyes or wings, or the case a face. Mess up the wig: it is a good haircut.
- Change the proportions in `params.py`, or let the forceps grow back into claws: they are small, gentle, rounded.

## Open questions (do not assume answers)

- Hair on a charging case meets pockets, lint and chargers: a fitted hair net, a little brush in the box, or a short
  crop? A wig that comes off for the wash?
- Electronics: a donor module or a designed board; where the battery goes (the stem is long enough to hold it).
- Forceps as the control: force sensor, or a capacitive pinch? Will they snag hair (the user's, or the case's)?
- `[PRICE]`.

## Making one (vibe fab)

- **Buds**: resin-print `out/stl/bud-*.stl` with the forceps (`pincers-*.stl`) in a tough resin, sand, and lacquer
  chestnut over a sealer. The render model is solid: hollow it and lay out the parts before printing (next step).
  The practical route is a reshell: open a cheap stem-style TWS pair, which keeps its battery and antenna in the stem,
  and move the board, driver (usually 10 mm) and battery into the printed shells.
- **Case**: print base and lid, add two 3 x 2 mm magnets for the lid and two for each bud's seat, and move the donor
  case's charging board and pogo pins across.
- **The wig**: buy a doll wig sized for a 6 to 7 inch head (16 to 18 cm round, the 1/6 ball-jointed-doll size): the lid's
  crown measures about 16 cm round. Glue it to the lid, then cut the bob level with a strip of tape as the guide. Or
  glue doll-hair wefts in rows from the edge up and finish with a side part.
- **Tips**: buy medium silicone tips with a 5 to 6 mm bore.

## Files

- `params.py` the numbers (PROPOSAL, PLACEHOLDER)
- `model.py` builds the buds, forceps, tips and case in build123d and exports `out/stl`, `out/step`, `out/parts.json`
- `hair.py` grows the wig at render time (a `python` object in `shots.json`)
- `scene.py` writes `shots.json`, solving each bud's pose so it rests on its body and its forceps
- `renders/` hero and detail, by version; `critic/LOG.md` one row per critic round
