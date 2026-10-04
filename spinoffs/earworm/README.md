# earworm: handoff for design, renders and critic

Wired over-ear headphones in the earmilk family. One joke, said once, on a product that would be good without it. This
file is the brief: the idea, the decisions, the numbers, the shots. `params.py` holds the numbers the model is built
from.

Status: concept, first pass (2026-10-04). Everything below is a *proposal* until the owner signs it.

## The idea in four lines

- Closed-back over-ear headphones, plain and well made, in the colour of soil.
- The cable is an earthworm: a moulded silicone sleeve over a four-conductor cable, ringed along its length, pink-brown,
  darker along its back.
- The worm's saddle (the clitellum) is the inline remote and microphone, and it sits where a saddle sits on a real
  worm: about a quarter of the way from the head, 290 mm from the cup, which is where a remote belongs anyway.
- The head burrows into the left cup; the tail runs into the 3.5 mm plug. Nothing else on the product says worm.

Voice: deadpan, like earmilk's Nutrition Facts. One joke per surface, maximum. The cups carry the wordmark and
nothing else.

## Decisions (proposals until the owner signs them)

- **Single-sided cable**, entering the left cup low at the front through a rubber grommet: the burrow. The grommet's
  bore is a little under the worm, so the head looks gripped, not plugged.
- **Cups** 100 mm round, closed back, 30 mm deep shells with an 11 mm shoulder, a flat back cap carrying the wordmark
  debossed tone on tone (Archivo Black, 11 mm type, 51 mm wide, 0.5 mm deep) on both cups. A parting line round each
  shell and the cap's line on the back: signs that it was made.
- **Yokes and sliders** satin gunmetal; **band and cups** graphite satin; **cushions and crown pad** protein leather
  with a welt seam; two stitch lines along the band.
- **The worm**: 6.4 mm sleeve (thinner stops reading as a worm; thicker stops reading as a cable), annuli at about
  2.4 mm that wander by 14 % as real ones do, slow swellings along the length, darker on top. The saddle is 34 mm
  long and 8.2 mm across, smooth, paler and warmer, and fades into the body at both ends; it holds one button
  (squeeze: play, pause, answer; twice: next) and the microphone's hole on its underside.
- **Cable** 1.2 m. **Plug** 3.5 mm TRRS (CTIA) in a gunmetal barrel; the tail tapers into the barrel and is its strain
  relief.

## Geometry (mm)

| | |
|---|---|
| Between the cushions (uncompressed) | 144 |
| Cup diameter, shell depth, cushion thickness | 100, 30, 24 |
| Ear opening | 56 |
| Band: crown height above the ear canal, width, thickness | 140, 26, 6 |
| Yoke radius about the cup axis | 57 |
| Worm: diameter, ring pitch, saddle length and diameter | 6.4, 2.4, 34 and 8.2 |
| Saddle from the cup, along the cable | 290 |
| Plug barrel | 7 x 14 |
| Overall width (cup back to cup back) | 252 |

## Colourways (proposals)

| Name | Cups and band | Worm | Saddle | Notes |
|---|---|---|---|---|
| Nightcrawler (hero) | graphite `#2f2c2a` | `#c08a80`, back `#77434b` | `#dca88c` | the common earthworm |
| Red Wiggler | graphite | brick `#a8453a`, back `#6e2a26` | ochre `#d59a4a` | a composting worm; stripes between the annuli |
| Glowworm | graphite | pale `#e6dccb` in phosphorescent silicone | `#efe4cf` | glows green after dark; you can find your headphones |

## Shots

1. **Hero.** Standing on their cups on a neutral sweep, seen from about 30 degrees up so the floor fills the frame and
   no horizon shows; the worm leaves the left cup's burrow and crawls across the floor toward the camera, saddle and
   plug in frame, room on the right for copy. Everything sharp. Lit for dark gloss: a high soft key, a softbox high
   behind, two tall strips behind for edge lines, a small hard light for glints on the worm, little fill.
2. **Detail.** The left cup whole, wordmark readable, the worm leaving the burrow; for this shot the cable is
   re-dressed in an S in front of the cup that turns back into the frame. f/22, the far cup soft.

## Where the renders stand (2026-10-04)

Three critic rounds per shot, the limit for this look (`critic/LOG.md`). Hero: 4, 5, 4; `renders/hero-v2.png` is the
one to show. Close-up: 4, 5, 5; `renders/detail-v3.png`. What every round asked for, and the next pass should do:

- **Light for dark gloss.** Strips behind for edge lines, a high soft key, a pin light for glints, little fill. Most of
  the gain came from this; the critic still wants more contrast on the black cups.
- **The worm alive, not machined.** Vary ring width and depth along the body, not just pitch; break the wet coat with a
  roughness texture instead of raising it (raised, it glints on every crest); a pinch where it enters the burrow; the
  saddle shot low enough that its swelling shows.
- **Signs of manufacture.** Real pleats in the pads (geometry, not bump), stitching and edge binding on the band, a
  grille in the driver openings.
- **The set.** A floor that runs past the frame from any camera height; frames chosen on purpose (the whole product
  with its band, or tight on the burrow).

## What a render must not do

- Give the worm a face, eyes, slime, soil or a hook. Put a worm on the cups. Change the proportions in `params.py`.
- Let the cable read as a worm from across the room; it should read as a good cable first and a worm on the second
  look. The hero is allowed to bring the worm close to the camera for that second look.

## Open questions (do not assume answers)

- Detachable cable (a 2.5 mm jack inside the burrow) or fixed? A worm does not detach; a cable that breaks should.
- Drivers: 40 or 50 mm dynamic; impedance (32 ohm suits phones).
- Packaging: a waxed bait cup with a lid ("One dozen. Keep cool.") is a proposal and a second surface; the owner's call.
- `[PRICE]`.

## Making one (vibe fab)

- **Cups**: print `out/stl/print/print-shell-l.stl` and `-r.stl` (2.4 mm walls, back face down, resin or PETG) and the
  two flat baffles `print-baffle-*.stl`, which seat a 50 mm driver in a 1.5 mm recess and have four relief holes to
  damp with felt. The baffle sits on a ledge 2.5 mm inside the shell's mouth; the pad's lip wraps its edge.
- **Drivers**: a pair of 50 mm dynamic headphone drivers, 32 ohm, sold as replacement parts. Choose a pair with a
  published frequency response.
- **Cushions**: 100 mm round protein-leather replacement pads are a common part; buy them.
- **Band**: a 2 mm spring-steel strip wrapped in leather over a foam strip, or print `band.stl` in nylon. Yokes and
  sliders print in PETG or are milled in aluminium and anodised gunmetal.
- **The worm**: cast platinum-cure silicone (Shore 10A to 20A), pigmented, over a four-conductor cable (left, right,
  microphone, ground), in a two-part mould resin-printed with the annuli. Pour in 300 mm indexed sections, or cast the
  saddle separately over the remote's board. Brush a darker silicone along the top before demoulding.
- **Remote**: one momentary button across microphone and ground with an electret capsule: the standard one-button
  headset circuit that phones understand.
- **Plug**: a solder-type 3.5 mm TRRS plug inside a turned or bought 7 mm metal barrel.

## Files

- `params.py` the numbers (PROPOSAL, PLACEHOLDER, as in earmilk's fab/params.py)
- `model.py` builds the cups, band, yokes, grommet and plug in build123d and exports `out/stl`, `out/step`, `out/parts.json`,
  and the printable shells and baffles in `out/stl/print/`
- `scene.py` writes `shots.json` (the worm's path, its rings, saddle and swellings, the plug's placement, lights, cameras)
- `renders/` hero and detail, by version; `critic/LOG.md` one row per critic round
