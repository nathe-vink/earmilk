# The engine: CAD in, photographs out, every setting named

A product's CAD is the single source of its shape; a shot file is the single source of everything else in a
photograph. The engine joins the two in Blender's Cycles, and it writes beside every image what it did and where each
part landed, so a critic can measure the image by part and prescribe changes as settings, and the next render
applies them. No hand-tweaking happens anywhere in between.

```
fab/params.py ─► fab/cad.py, fab/components.py ─► fab/render_model.py ─► out/render/<product>.glb  (one named part each)
                                                                               │
studio/products/<product>.json  (materials by part name, flavours, prints) ───┤
studio/shots/<product>/<shot>.json  (camera, light, set, render) ─────────────┤
                                                                               ▼
                                     python3 studio/engine/render.py SHOT --out IMG [--masks]
                                                                               │
                                IMG.png  IMG.shot.json  IMG.report.json  IMG.mask.png/.json
                                                                               │
              critic/round.py stage ─► a fresh critic (critic/PROMPT.md) ─► critic/rounds/…/*.json
                                                                               │
                                     render.py SHOT --apply that.json [--save-shot SHOT] ◄───┘
```

## Running it

    python3 studio/engine/render.py studio/shots/earmilk/01.json --out renders/DAY/01-e1.png \
        [--set camera.lens_mm=85 --set lights.key.irradiance=2.5]     any setting, by its dotted path
        [--apply critic/rounds/DAY/shot-01-e1-r1.json [--only c1 c3]] a critic's prescribed changes
        [--save-shot studio/shots/earmilk/01.json]                    write the changed shot back
        [--samples 64 --scale 0.5] [--crop X0 Y0 X1 Y1]               a quick proof, or a region
        [--masks]                                                     the part-id mask, for measuring by part

It runs on the system Python with `bpy` (Blender 5); the CAD runs in `.venv-fab` (numpy 2). Lengths are metres, z up,
the product's footprint centred on the origin with its front toward -y.

## The shot file

A shot names its parts by path (`camera.position`, `sun.elevation_deg`, `set.windows.0.along`,
`materials.paint.coat_roughness`, ...), and `knobs.py` gives each path its unit, range and meaning: the vocabulary
`critic/card.py` prints for the critic and the only one the engine reads. `extends` chains a shot to defaults
(`base.json`). Relative changes are allowed: `"+0.5"`, `"x0.8"`, `"+15%"`. Setting a path that is missing makes it,
lists included (`glints.0` adds the first glint).

- **camera:** position and target, lens, `level` (look level and frame by lens shift, so verticals stay vertical),
  extra shift, roll, depth of field and focus.
- **sun and sky:** the sun by azimuth, elevation and irradiance (W/m2), its size and colour; a gradient or physical
  sky, or none.
- **lights:** area, spot and point lamps placed by orbit round the product or by position, aimed at a target, sized,
  in W or in irradiance at the target; light linking (`receivers`) to light only some parts; glints, small lamps set
  exactly where a surface would mirror them into the camera.
- **set:** a sweep (a cove of any size and colour, with flags and bounce cards) or a room (walls with real window
  openings, reveals, mullions and sills, skirting, wainscot, a ceiling, an oak floor by plank, plaster walls) and props
  (rug, table, books, sideboard with a turntable, vase with branches, floor lamp, sofa, sheer curtain, framed print).
- **product:** which product file, which flavour, how many copies where (`instances`), and:
  - `hide`: parts left out, by name pattern;
  - `explode`: `[{"match": "waveguide-insert|magnets-insert", "offset_m": [0, -0.3, 0]}, ...]`, each part moved along
    its own fixing axis in the product's frame, for an exploded view;
  - `cutaway`: `{"box_m": [x0, y0, z0, x1, y1, z1], "skip": "cable-*", "sections": [{"match": "...", "color": "#..."}]}`,
    a boolean cut per part and the cut faces coloured by material (wood shows wood, a printed part its resin, a bought
    part its own material), for a technical cutaway.
- **products:** a list of product blocks instead of one, for a family shot (two sizes in one room).
- **render:** samples, adaptive threshold, denoise, clamp, bounces, the view transform (Khronos PBR Neutral keeps brand
  colours true), exposure, white balance.

## The product file

`studio/products/<product>.json`: the GLB, the CAD point that stands on the origin, the flavours (colour sets),
materials (`materials.py` presets: paint under a clear coat with a faint orange peel, metals, rubber, paper and
coated cones, birch, plastics, glass), `assign` rules from part names to materials, colour `zones` (a band of faces
by height), and `decals`: the print files themselves (the Nutrition Facts, the stencilled marks) laid inside a
material's colour coat, under its clear, exactly where the fab files put them.

## What it writes

- `IMG.shot.json`: the resolved shot, every setting as used.
- `IMG.report.json`: times, samples, the changes applied and any it could not, and `parts_2d`: each part's box and
  centre in the frame's pixels and its distance from the camera, so labels and callouts can be laid over the image
  exactly (a deck, an exploded view).
- `IMG.mask.png` and `.mask.json` (with `--masks`): a flat render where each part's pixels carry its id, so
  `critic/measure.py` measures `part:front-baffle` wherever the camera puts it.

## The meter

    python3 studio/engine/meter.py SHOT --part back-panel --region 783 440 805 620 --target 225

renders the shot small as a scene-linear EXR with its mask and prints each part's or region's true scene-linear
brightness, what the final image shows there now through the view, and the exposure change that would put it at the
target. Exposure is where a critic's prediction is most often wrong (a view transform's shoulder hides how far over a
white is); after applying a round, meter the faces the accept tests name and set the key or the exposure from the
reading, not from the guess. Regions are in the critic's staged image's pixels (0.75 scale).

## Exposing to the critic's tests

    python3 studio/engine/render.py SHOT --apply REPLY --save-shot SHOT --no-render     # apply and save only
    python3 studio/engine/autoexpose.py SHOT REPLY --save                              # one small EXR, then the exposure
    python3 studio/engine/render.py SHOT --out IMG --masks                             # the one full render

`autoexpose.py` reads every brightness and colour test in a critic's reply (lum_median, lum_mean, lum_p5, lum_p95,
r/g/b_median, delta_e) from one small scene-linear render, turned into the final image at each exposure by Blender's
own colour management (the shot's view, look and white balance), and sets the exposure within 1 EV of the shot's that
passes the most of them without clipping the product's whites, by a margin of a few levels, with the smallest change.
Colour counts: PBR Neutral's shoulder bleaches a lit red toward white (scene-linear 1.5, 0.1, 0.1 shows as 248, 91, 91),
so an exposure chosen for the whites alone undid 02b's lowered sun on its plinth (dE 5.6 in the proof, 10.9 after). A test only a bigger change
would pass is not exposure's (a glint that misses, a lamp too weak) and is left to fail. A critic's
relighting is usually right in shape and wrong by a fraction of a stop; this takes the fraction out before the
expensive render instead of after it.

## Tuning one setting by proof

    python3 studio/engine/tune.py SHOT REPLY c3 lights.roof_ramp.strength 0.5 1.5 --save
    python3 studio/engine/tune.py SHOT REPLY '{"region": {"part": "woofer-cone"}, "metric": "lum_p95", "op": "between",
        "value": [100, 150]}' glints.1.power_w,glints.2.power_w 12 24 --save

A critic names the setting and the reading the next image must have; how far to move the setting is a guess until
something is rendered. `tune.py` renders proofs at the critic's scale with the setting at two values, reads the test
exactly as `critic/round.py check` will, and follows the secant toward a reading a margin inside the test (the middle
of a "between"), three or four proofs in all, printing every other test of the reply on each proof. A test of your
own can stand in for the critic's (where its "expected" gives a band and its test only a floor), and several settings
can move together (a symmetric pair of glints).

## The reflection probe

    python3 studio/engine/render.py SHOT --out IMG --probe 'woofer-cone' --scale 0.75

What a glossy part mirrors into the camera, from the scene itself: the camera's rays through the frame, reflected
about the surface's own normal at each hit on the part, followed to the first thing they meet, a lamp's face, a panel,
a surface of the set or the product, or the sky. It prints each thing's share of the part's pixels, the box of those
pixels in the frame and the band of directions they look along, so a card or a lamp is sized and placed to cover the
pixels that should light up (on 05 it showed the critic's 8 x 3 m card reaching 5 % of the cones, which mirror the
open sky in front). Nothing is rendered.

## What the engine makes exact

- **Glints** are placed from the surface the camera sees at their point, with that surface's own normal (the camera's
  ray through `at`, else the nearest receiving surface that faces the camera); a glint whose lamp would have to sit
  behind the floor or inside the product is skipped, because that surface mirrors the floor there, and the render's
  report and the next critic's card say so. The test for what hides the lamp ignores the surface itself: a hit within
  2 mm, a face seen from behind (a connector's bezel sunk in its module), and the parts in `occlusion_ignore`.
- **Flags**: a reflect-only flag (`set.flags`, `reflect_only`) is one-sided, seen only from the side its normal faces,
  so a card laid on the floor shows in the product's lacquer while the floor's own gloss, looking at its back, sees
  through it; two-sided it printed a straight-edged patch on the sweep.
- **The sun through a window**: `sun.aim` `{"at": [x, y, z], "window": 0, "through": [0.5, 0.5]}` sets the azimuth
  and elevation that send the sunlight through that point of the window onto `at`.
- **Panels**: `{"type": "panel", ...}` is an emissive rectangle the camera cannot see, its brightness ramped along a
  world axis, lighting one side, casting no shadow, with `diffuse: false` seen only in reflections and with
  `receivers` only in the parts named: a graduated scrim for a lacquered roof, a reflection card for a cone.
- **The inside**: in a cutaway or an exploded view, the faces inside the product (a cavity's walls, a face another
  part covers) take the product's `interior` materials (raw birch, bare resin), found by rays from each face against
  the assembled product before it is opened; a shadow line's walls stay painted.
- **Sections**: a cut face takes its rule's section material. A plywood panel's (a birch rule, a part thinner than
  40 mm) shows its veneers: 1.4 mm each across its thickness, long and end grain alternating, a glue line between; a
  driver cut through shows bare steel (the motor) and aluminium (the basket).
- **True surfaces**: a part made by a ruled loft through polygon rings (the waveguide) takes its shading normals from
  its analytic surface sampled finely (`normals_from`, the grid from `fab/horn_grid.py`), interpolated linearly across
  each grid triangle; `refine` cuts its facets and sets the new corners on that surface, and `skin` lays the surface
  itself over the facets a hair into the air, because a concave bowl mirrors its own far wall and its facets show in
  reflections however its normals are set. None of that cured the teeth along the bowl's floor; the mesh did. Where
  the side walls turn into the floor, neighbouring meridians differed in length by 10 to 15 mm, so stations at the same
  fraction of each wall sat at different depths and the ruled quads between them twisted; and the wall has a true
  crease there (in the floorstander at 205 and 335 degrees, where the coverage starts to be narrowed). The CAD now puts
  a meridian on each crease and adds them wherever neighbours differ by more than 2 mm (`Waveguide.phis`: 256 instead
  of 96 in the floorstander, 160 in the bookshelf), and the teeth are gone. A reflection that breaks into teeth is the mesh's parameterisation before it is the shading's.
- **Real blacks**: the products' black paint, rubber, plastic and anodising reflect 3 to 4 %, as real ones do; at
  under 1 % no light can model a driver's basket or an amplifier's plate.
- **Oak boards**: each board is its own piece of wood. A second brick texture gives every board a random number that
  offsets its grain (the grain stops at the seams, where laminate's runs on), sets its sheen and its cut: flat-sawn
  boards show their growth rings as cathedral arches, rift-sawn ones as straight lines, the latewood a thin dark line.
  Each row is slid along by its own random amount, so the end joints fall at random (a brick texture's regular offset
  lined them up in every other row, a column of joints the 01 critic found).
- **A polarising filter** (`camera.polariser`: `strength` 0 to 1, `angle_deg` the pass axis from horizontal). A clear
  coat's reflection is polarised: across the plane of incidence (s) it reflects more than in it (p), and at Brewster's
  angle (56 degrees off the normal for a 1.5 lacquer) only s reflects. The filter scales each camera ray's specular
  on every dielectric (coat and specular level; not metals or glass) by 2 (Rs cos2 a + Rp sin2 a) / (Rs + Rp), from
  the Fresnel terms at that ray's angle and the angle a between s and the pass axis, and leaves the diffuse alone,
  the exposure made good. So it clears the veil a bright room lays over a lacquered red on a roof slope or a plinth's
  side, as it does on a camera, and does nothing head-on. Only camera rays see it: what the surfaces light and mirror
  for each other is unchanged. On 03 at full strength, the axis vertical, the lit roof went from dE 6.5 to 4.0 off
  #C62828 and the horn's floor from 75 to 55, darker than the roof, as a recess reads; the dome's highlight and the
  left wall's band, at other angles, stayed (`renders/2026-10-09/engine/polariser-03-proof.png`, without and with).
- **A wainscot's sheen** (`set.wainscot.roughness`, 0.38 satin by default): a satin dado mirrors a lamp's panel as a
  soft halo behind the product, a backlight no light in the room explains (the 02b critic's round 5); at 0.7, eggshell,
  it blurs the lamps into its own shade, so a reflection panel can stay on for the lacquer.
- **Part positions after a masks-only pass**: `render.py --masks-only` evaluates the scene before it reads where each
  part lands in the frame. Without a render nothing had moved the exploded parts or the camera into place, and 07-e6's
  report put its parts behind the camera; the deck's callouts read these positions.

The critic may also move and turn the product within its set (`product.instances.N.position`, `.rotate_z`), set how
far an exploded part is drawn out along its own axis (`product.explode.N.offset_m`), and dress a room with the
engine's props (`set.props.N`: rug, table, books, sideboard, vase, lamp, sofa, curtain, frame; `off` takes one out).
The product's geometry, flavour, marks and what is cut stay fixed.

## The loop

`critic/round.py stage` copies the image under a neutral name with its mask and card, and writes the message for a
fresh critic, who scores it blind first, then reads the card and measures (`critic/measure.py`) before prescribing at
most eight changes, each one setting with its current value, the value to set and an accept test the next render must
pass. `render.py --apply` applies them; `critic/round.py check` runs the accept tests on the new image. A change the
card forbids (the product's geometry, its colours, a waveguide set by acoustics, the drivers) is listed as out of scope
with its reason, and a change the engine cannot make yet comes back as an "asset" request.

## Adding a product

Give it a CAD script that exports one named part each to a GLB (`fab/render_model.py` is the pattern), a product file
for its materials, and shots. Nothing in the engine is specific to earmilk.
