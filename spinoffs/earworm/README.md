# earworm: handoff for design, renders and critic

Wired in-ear earphones in the earmilk family. One joke, said once, on a product that would be good without it. This
file is the brief: the idea, the decisions, the numbers, the shots. `params.py` holds the numbers the model is built
from.

Status: concept, second pass (2026-10-05). Everything below is a *proposal* until the owner signs it, except what the
owner chose: in-ear, not over-ear (2026-10-04), and a worm whose segments overlap like a jointed toy snake, each one
lapping over the next like an insect's plates.

## The idea in four lines

- Small bullet earphones, plain and well made: a gunmetal back cap, a graphite front shell, a silicone tip.
- The cable is an earthworm: two worms, one burrowing into the back of each earphone, that meet at a gunmetal splitter
  and go on as one to the plug.
- The worm's body is made of segments that overlap toward the tail, like a jointed snake toy or a beetle's back; the
  right worm's saddle (the clitellum) is the inline remote and microphone, 120 mm from the earphone.
- Nothing else on the product says worm.

Voice: deadpan, like earmilk's Nutrition Facts. One joke per surface, maximum.

## Decisions (proposals until the owner signs them)

- **Earphones**: a 10 mm barrel, 17 mm long, with a 5.2 mm nozzle and a medium silicone tip (11.5 mm). The back cap is
  gunmetal, the front shell graphite, a parting line between them; a dark mesh inside the nozzle.
- **The burrow**: a gunmetal collar on the back cap whose bore is a little under the worm, so the head looks gripped,
  not plugged.
- **The worm**: segments 2.5 mm long on the branches (3.7 mm across) and 2.9 mm on the main cable (4.6 mm across), each
  flaring about 16 % toward its rear lip and lapping over the next; slow swellings along the body, darker on top, paler
  underneath. Moulded silicone over a four-conductor cable.
- **The saddle** on the right branch: 22 mm long, swelling to 5.7 mm, smooth (the segments show only faintly through
  it), paler and warmer; one button (squeeze: play, pause, answer; twice: next) and the microphone's hole underneath.
- **Splitter** a 7 x 13 mm gunmetal barrel; **plug** 3.5 mm TRRS (CTIA) in a gunmetal barrel, the tail tapering into it.
- **Lengths**: 300 mm from each earphone to the splitter, 900 mm from the splitter to the plug.

## Geometry (mm)

| | |
|---|---|
| Earphone barrel: diameter, length | 10, 17 |
| Nozzle: diameter, length | 5.2, 5 |
| Tip (bought) | 11.5 diameter, 7.4 long: a stem on the nozzle and a thin skirt, smoky translucent silicone |
| Burrow collar | 5 diameter, 2.4 long |
| Worm: branch and main diameter | 3.7, 4.6 |
| Segment pitch: branch, main; flare | 2.5, 2.9; 16 % of the radius |
| Saddle: from the earphone, length, diameter | 120, 22, 5.7 |
| Splitter | 7 x 13 |
| Plug barrel | 6 x 13 |
| Lengths: earphone to splitter, splitter to plug | 300, 900 |

## Colourways (proposals)

| Name | Earphones | Worm | Saddle | Notes |
|---|---|---|---|---|
| Nightcrawler (hero) | gunmetal and graphite | `#c08a80`, back `#77434b` | `#dca88c` | the common earthworm |
| Red Wiggler | gunmetal and graphite | brick `#a8453a`, back `#6e2a26` | ochre `#d59a4a` | a composting worm; a pale line where the segments lap |
| Glowworm | gunmetal and graphite | pale `#e6dccb` in phosphorescent silicone | `#efe4cf` | glows green after dark; you can find your earphones |

## Shots

1. **Hero.** On a pale sweep, seen from above at about 35 degrees: the two earphones in front with their tips toward the
   camera, the two worms side by side up the left, across the top and down the right to the splitter, the main worm
   curling back so the plug points in from the right third. Everything sharp. Lit for small dark metal: a high, fairly
   small key that is most of the light on the floor, two strips behind for edge lines, a narrow overhead strip for a
   line down each barrel, a pin light for glints, little fill.
2. **Detail.** From behind the pair and low: both worms lead in from the bottom of the frame and burrow into the backs of
   the earphones, the segments lapping toward the camera; both earphones whole and sharp (focus blur doubled the near
   edge in round 1).

## What a render must not do

- Give the worm a face, eyes, slime, soil or a hook. Put a worm on the earphones. Change the proportions in `params.py`.
- Let the cable read as a worm from across the room; it should read as a good cable first and a worm on the second
  look.

## Open questions (do not assume answers)

- Detachable cable (MMCX at the burrow) or fixed? A worm does not detach; a cable that breaks should.
- Drivers: a 9 to 10 mm dynamic driver, 16 or 32 ohm (placeholder), or a balanced armature.
- Over-the-ear routing (the worm over the ear) or straight down? The renders assume straight down.
- Packaging: a waxed bait cup with a lid ("One dozen. Keep cool.") is a proposal and a second surface; the owner's call.
- `[PRICE]`.

## Making one (vibe fab)

- **Earphones**: resin-print `out/stl/print/print-cap.stl` and `print-shell.stl` (1.2 mm walls) twice, seat a 9.4 mm
  dynamic driver in the front shell against the nozzle's shoulder, and glue cap to shell at the parting line. Buy the
  tips (medium, 5 to 6 mm bore). Paint the cap gunmetal, or print it in a metal-filled resin and polish.
- **The worm**: cast platinum-cure silicone (Shore 20A to 30A), pigmented, over a four-conductor cable (left, right,
  microphone, ground) in a two-part mould resin-printed with the overlapping segments. Segment moulds index, so cast
  the branches and the main cable in 150 mm sections, or print the segments as hollow beads in a flexible resin and
  thread them over the cable like a toy snake. Brush a darker silicone along the top before demoulding.
- **Remote**: one momentary button across microphone and ground with an electret capsule, inside the saddle: the
  standard one-button headset circuit that phones understand.
- **Splitter and plug**: a turned or bought 7 mm metal Y-splitter; a solder-type 3.5 mm TRRS plug in a 6 mm barrel.

## Where the renders stand

The in-ear look has had its three critic rounds (`critic/LOG.md`): hero 4, 4, 4 and detail 4, 5, 5. Round 2 found two
real bugs (both branches ran in one place; each lead out of its burrow kinked) that v3 fixed. What a next pass should do
is at the end of the log: a camera built around one bud side-on, placed strips for the metal, a cable settled like rope. The over-ear version's renders are in `renders/over-ear/` and its rounds are in the log; its model is in
git history.

## Files

- `params.py` the numbers (PROPOSAL, PLACEHOLDER, as in earmilk's fab/params.py)
- `model.py` builds the earphone (cap, shell, mesh, tip), the splitter and the plug in build123d and exports
  `out/stl`, `out/step`, `out/parts.json`, and a printable cap and shell in `out/stl/print/`
- `scene.py` writes `shots.json`: the earphones' resting poses (solved with `studio/poses.py`), the worms' paths from
  each burrow to the splitter and on to the plug, their segments, swellings and saddle, the lights and cameras
- `renders/` hero and detail, by version; `critic/LOG.md` one row per critic round
