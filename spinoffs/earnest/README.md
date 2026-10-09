# earnest: handoff for design, renders and critic

A standalone valve amplifier in the earmilk family. As with earmilk, there is one joke, said once, on a product that would be good without it. This file is the
brief: the idea, the decisions, the numbers, the shots. `params.py` holds the numbers the model is built from.

Status: concept (the owner's idea, 2026-10-08). Everything below marked *proposal* waits on the owner.

## The idea in four lines

- An egg crate grown into a chassis. The top is the carton's tray, pressed into cups, with a cone standing between every four.
- The eggs are the valves: egg-shaped glass envelopes standing blunt end up in the cups, the heater glowing through the
  anode, the getter's silver in the dome.
- Two eggs are not glass. A white one turns the volume and a brown one picks the input.
- Sold by the pack: a half-dozen, a dozen, and a warehouse-club flat of 24.

Voice: deadpan, like earmilk's Nutrition Facts. One joke per surface, maximum.

## Decisions (proposals until the owner signs them)

- **What each pack is.** earmilk is active: its amplifiers are inside it (`fab/README.md`). So for earmilk, the
  half-dozen is a valve line stage, with input, volume and a valve's colour, feeding the speakers' line inputs. The dozen and
  the flat are integrated amplifiers for passive speakers. The dozen's ten glass eggs make a real push-pull stereo amp:
  four output valves, four small signal valves, a rectifier, and a voltage regulator that glows violet. The flat's 22
  are a parallel push-pull amp for big speakers, or partly eggs that only glow. *Proposal*: see open questions.
- **The envelopes are custom glass** (*placeholder*). Valves come in standard bottles, tubular or globe-shaped (the "ST"
  shape). Some makers still blow special envelopes, such as KR Audio's balloon 300B. An egg is a custom envelope, and
  waits on a maker's quote; the model's valve inside (anode, micas, heater, getter) is a placeholder of the right size.
- **Blunt end up.** Eggs sit in a carton blunt end up, so the valves stand on their tips. Each Bakelite base sits in a
  socket 9 mm under its cup's floor, and the getter's mirror is in the dome.
- **The "pulp" is metal.** Valve glass runs hot enough to burn, and moulded pulp would scorch. The crate is pressed
  steel (or cast aluminium) with a textured powder coat that reads as pulp. Under the cup floors there are 74 mm for the
  transformers and the circuit; vents round each socket draw air up past the glass.
- **A lid, like a carton's** (*proposal, not modelled yet*). It's a perforated cage hinged at the back that closes over the
  eggs. It keeps fingers and pets off hot glass and high voltage; open it to listen.

## Geometry (mm)

| | |
|---|---|
| Cup pitch, both ways | 74 |
| Cup mouth (rounded square, r 22) | 66 |
| Cup depth, top plane to floor | 38 |
| Cup floor | Ø 40 |
| Cones between cups | Ø 26 at the top plane to Ø 9, 26 high |
| Crate height, floor to top plane | 112, on four Ø 34 × 6 rubber feet |
| Draft | 5°, so the base is 20 larger each way than the top |
| Half-dozen (2 × 3), top plane | 246 × 172 |
| Dozen (2 × 6), top plane | 468 × 172 |
| Flat (4 × 6), top plane | 468 × 320 |
| Egg valve | 80 long, Ø 58, glass 1.4; base Ø 30 × 14 |
| Knob eggs | 0.86 of a valve egg: 69 long, Ø 50 |

## Colourways

| Name | Body | Accent | Notes |
|---|---|---|---|
| Recycled | #B9B4A9 grey | white and brown knob eggs | the carton everyone pictures; the default |
| Free range | #C8B08A kraft | white and brown knob eggs | warmer; sits well beside oak |
| Flavours | an earmilk flavour's body colour | its accent on the cones' tips | *proposal*: a crate to match a pair |

## Shots

1. **Hero.** The dozen, three-quarter from above (azimuth −28°, elevation 30°, 85 mm), heaters lit, on the sweep.
   `scene.py`'s `hero`.
2. **Family.** The three packs side by side: half-dozen, dozen, flat. `scene.py`'s `family`.
3. **Detail** (to do). One egg valve close up: the heater's glow through the anode's open ends, the getter's mirror,
   the base in its socket.
4. **With earmilk** (to do). The half-dozen beside a pair of bookshelf earmilks, cable running to the back panel.

## What a render must not do

- Change the proportions in `params.py`, soften what is meant to be crisp, or add a second joke to a surface.
- Show any real mark, including egg-grading or dairy marks, stamps on the eggs, certification shields, or a real egg or
  warehouse-club brand. The pack sizes carry the joke; no logo does.
- Make the valves glow like light bulbs. A heater is a dull orange line inside the anode, and the glass stays clear.

## Open questions (do not assume answers)

- Which pack is the line stage and which the integrated amp, and whether the half-dozen is the only one most
  people need.
- How many eggs are working valves. Ten in the dozen can all work; the flat's 22 can't sensibly all be output valves.
- Who blows the egg envelopes, and what they cost: [PACK PRICE] stays open.
- The lid: a cage, a clear cover, or none.
- How a knob egg turns: a twist on a shaft under its cup, the input detented.
- The name: earnest (ear + nest).

## Vibe-fab notes

- `model.py` builds everything in build123d. The crate's 2.2 mm fillet over the cups' rims is tried and skipped when OCC
  refuses it (it does at present), so the rims print sharp; round them in post or by hand.
- STLs are meshed to 0.05 mm (finer than any printer); a valve's glass is about 73k triangles. The renderer loads each
  part once and instances it, so a family shot holds one valve in memory, not 37.

## Files

- `params.py` the numbers (SPEC, PROPOSAL, PLACEHOLDER, as in earmilk's fab/params.py)
- `model.py` builds the parts in build123d and exports `out/stl`, `out/step`, `out/parts.json`
- `scene.py` writes `shots.json`, the scene for `studio/pathtrace.py`; renders land in `renders/`
- `critic/LOG.md` one row per critic round, as in earmilk's critic/LOG.md
