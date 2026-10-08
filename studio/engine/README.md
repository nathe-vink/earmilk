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

renders the shot three stops under with its mask, inverts the view transform, and prints each part's or region's
true scene-linear brightness, what the final image shows there now, and the exposure change that would put it at the
target. Exposure is where a critic's prediction is most often wrong (a view transform's shoulder hides how far over a
white is); after applying a round, meter the faces the accept tests name and set the key or the exposure from the
reading, not from the guess. Regions are in the critic's staged image's pixels (0.75 scale).

## Exposing to the critic's tests

    python3 studio/engine/render.py SHOT --apply REPLY --save-shot SHOT --no-render     # apply and save only
    python3 studio/engine/autoexpose.py SHOT REPLY --save                              # one small EXR, then the exposure
    python3 studio/engine/render.py SHOT --out IMG --masks                             # the one full render

`autoexpose.py` reads every brightness test in a critic's reply (lum_median, lum_mean, lum_p5, lum_p95) from one
small scene-linear render, and sets the exposure that passes the most of them by the widest margin. A critic's
relighting is usually right in shape and wrong by a fraction of a stop; this takes the fraction out before the
expensive render instead of after it.

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
