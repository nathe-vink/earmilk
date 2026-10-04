# earwig: handoff for design, renders and critic

True-wireless Bluetooth earbuds in the earmilk family. One joke, said once per surface, on a product that would be
good without it. This file is the brief: the idea, the decisions, the numbers, the shots. `params.py` holds the
numbers the model is built from.

Status: concept, first pass (2026-10-04). Everything below is a *proposal* until the owner signs it.

## The idea in four lines

- Stem-style true-wireless earbuds in glossy chestnut, the colour of an earwig.
- Each stem ends in a pair of forceps. Pinching them is the control: play, pause, answer. The stem carries four shallow
  segment lines, like an abdomen.
- The charging case wears a wig: a bob of fine synthetic hair, parted in the centre, cut level just below the lid's
  edge. The lid opens with its hair on.
- Ear wig. The buds are the insect; the case is the wig. One joke per surface.

Voice: deadpan. The box could say "Hypoallergenic. Not a real earwig." and nothing more.

## Decisions (proposals until the owner signs them)

- **Bud**: one lofted body and stem, 20.4 x 17.2 mm across the body, 51 mm tall from the body's top to the forceps'
  tips (body 20, stem 17.7, forceps reaching 13 beyond the stem's end). The stem hangs from the body's outer side, as on
  every stem bud.
- **Nozzle** angled into the canal (inward, forward, a little up), 5.6 mm, with a medium silicone tip, 12.4 mm.
- **Forceps**: two tapering arms that bow apart (7.4 mm at the widest, centre to centre) and nearly touch at the tips,
  3.1 mm thick at the root, in a slightly redder chestnut than the body. Pinching flexes them onto a force sensor in the stem's end; the
  voice microphone opens between them, where the noise is least.
- **Case**: 62 x 26 x 48, every edge rounded at 10, the lid splitting at 62 % of the height (29.8 mm), a status light
  on the front. Glossy chestnut lacquer, the same as the buds.
- **The wig**: synthetic doll hair (70 micron, about 30,000 strands) rooted on the lid's crown, centre part, combed
  down over the edges and cut level 1.8 mm below the split, so the bob just covers the seam.

## Geometry (mm)

| | |
|---|---|
| Bud body (x, y, z) | 20.4 x 17.2 x 20 |
| Stem length, section | 17.7, 6.4 x 5.0 to 5.4 x 4.0 |
| Forceps: beyond the stem, root thickness, widest spread | 13, 3.1, 7.4 |
| Bud overall height | 51 |
| Ear tip | 12.4 diameter, 7.4 long |
| Case (w x d x h), edge radius | 62 x 26 x 48, 10 |
| Lid split from the floor | 29.8 |
| Bob cut below the split | 1.8 |

## Colourways (proposals)

The buds and case stay chestnut (an earwig is chestnut); the wig changes.

| Name | Buds and case | Wig | Notes |
|---|---|---|---|
| Chestnut (hero) | `#5b2e1a`, forceps `#7f3c18` | chestnut (melanin 0.66, redness 0.45) | tone on tone |
| Blonde | chestnut | ash blonde | |
| Ginger | chestnut | copper | |
| Black | chestnut | blue-black | |
| Silver | chestnut | silver grey | the distinguished one |

## Shots

1. **Hero.** The case standing in its bob; the two buds lying on their sides in front of it, forceps out, as buds lie on
   a table. Warm cream sweep, everything sharp.
2. **Detail.** Macro on a bud's stem and forceps, f/5.6, the case's hair soft behind.

## What a render must not do

- Give the buds antennae, legs, eyes or wings, or the case a face. Mess up the wig: it is a good haircut.
- Change the proportions in `params.py`, or let the forceps soften into blobs: they are crisp, tapering, glossy.

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
  glue doll-hair wefts in rows from the edge up and finish with a centre part.
- **Tips**: buy medium silicone tips with a 5 to 6 mm bore.

## Files

- `params.py` the numbers (PROPOSAL, PLACEHOLDER)
- `model.py` builds the buds, forceps, tips and case in build123d and exports `out/stl`, `out/step`, `out/parts.json`
- `hair.py` grows the wig at render time (a `python` object in `shots.json`)
- `scene.py` writes `shots.json`, solving each bud's pose so it rests on its body and its forceps
- `renders/` hero and detail, by version; `critic/LOG.md` one row per critic round
