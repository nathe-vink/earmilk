---
name: pathtrace
description: Path-trace a product scene with Blender Cycles through studio/pathtrace.py (any product in this repo). Use for photoreal renders, proofs, new materials, cables or hair, and for debugging dark, black or cave-like renders.
---

# Path tracing with studio/pathtrace.py

`python3 studio/pathtrace.py SCENE.json --shot NAME [--out file.png] [--samples N] [--scale 0.4] [--blend file.blend]`

Runs on the **system Python** with `bpy` 5.0 (numpy 1). Never install build123d or numpy 2 into the system Python;
CAD lives in `.venv-fab`. `studio/setup.sh` repairs both.

## Scene JSON (mm, sRGB hex)

- `materials`: `{name: {preset, color, ...overrides}}`. Presets: satin_plastic, matte_plastic, gloss_plastic,
  soft_touch, rubber, silicone, gummy, skin, lacquer, metal_polished, metal_satin, metal_brushed, anodized, leather,
  protein_leather, fabric, glass, smoked_glass, emissive, paper, wood, hair (Principled Hair: melanin, redness,
  roughness, radial_roughness, coat, tint). Overrides: roughness, metallic, coat, coat_roughness, sheen, sss,
  sss_scale (mm), transmission, ior, emission, bump, `top_color` (a second colour on upward faces, e.g. a worm's back).
- `objects`: `mesh` (STL in mm, GLB, OBJ; translate mm, rotate degrees XYZ, smooth angle), `tube` (Catmull-Rom path
  through `points`; `radius`; `profile` by fraction or `profile_mm` by distance, negative from the end; `rings` with
  pitch, depth, width, `skip_mm` and `skip_fade`; `bands` of another material by distance; caps; segments), `python`
  (a hook module with `build(ctx, **args)`; ctx has bpy, np, MM, material(), scene, base).
- `shots`: size, samples, `rig` (`sweep`: cove colour, key/fill/rim azimuth, elevation, power, dome; `table`: surface,
  wall, window), `camera` (position and target in mm, or azimuth/elevation/fill; lens; fstop and focus for depth of
  field), hide, objects_extra, exposure, look, floor_z.

## Habits that keep renders good

- Proof at `--scale 0.4 --samples 24..32` (20 to 50 s) and look at it before any full render (about 8 minutes at
  1800 x 1200, 160 samples, 4 CPUs). Run finals in the background.
- Rigs size themselves to the subject's bounding box; lights are in physical units scaled to it. Keep the key on
  the camera's side. The dome is fill only.
- Depth of field: product heroes want everything sharp (no `fstop`); macros want f/4 to f/5.6 with `focus` set.
  At 100 mm and 0.4 m, f/16 still holds only about 2 cm.
- No coplanar faces between solids. Keep parts 0.3 to 0.5 mm apart or overlapping.
- A `KHR_materials_unlit` glTF surface imports as camera-only emission and lights nothing; rebuild it as an emitter.
- Hair: 30,000 curves render fine; see `spinoffs/earwig/hair.py` for a vectorised groom on a rounded box.
