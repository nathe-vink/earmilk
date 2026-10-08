# studio: the tools, for any product in the family

Everything here works from a bare container: `studio/setup.sh` installs it and `python3 studio/doctor.py` proves it
runs. In a Claude Code cloud session the start hook (`.claude/hooks/session-start.sh`) runs `setup.sh` for you.

| Tool | What it does | Runs on |
|---|---|---|
| `setup.sh` | Installs everything the repo needs: render/'s node modules, Blender's `bpy` with numpy 1, the CAD venv `.venv-fab` with build123d, ezdxf, HarfBuzz, matplotlib, scipy. Idempotent: a few seconds when nothing is missing. `--doctor` runs the doctor after. | bash |
| `doctor.py` | Runs every tool for real at a tiny size: Chromium draws WebGL 2, Cycles renders a cube, build123d builds and exports a solid and HarfBuzz sets the wordmark, earmilk's spec check passes. Exits non-zero on any failure. | system Python |
| `new_product.py` | Starts a product from `template/`: `python3 studio/new_product.py earworm --title earworm --kind "Wired headphones"` makes `spinoffs/earworm/` with a brief, `params.py`, `model.py`, `shots.json` and a critic log. | system Python |
| `engine/` | The render engine: a product's CAD (a GLB of named parts) and a shot file of named settings in, a photograph out, with the resolved settings, each part's place in the frame and a part-id mask beside it, so a critic can measure by part and prescribe changes the next render applies. Rooms and sweeps, sun, sky, lamps and glints, materials by part name, prints as decals under the finish, exploded views, cutaways, several products in one frame. See `engine/README.md`. | system Python (bpy) |
| `pathtrace.py` | Path-traces a product scene described in JSON with Blender's Cycles: CAD meshes, generated tubes (cables and worms: grooved rings or overlapping segments like a jointed toy snake, blended bands, radius by distance, flattening on a floor), Python hooks (hair), material presets, light rigs that size themselves to the subject with strips and pins, cameras with depth of field. | system Python (bpy) |
| `poses.py` | Lays small parts down on a floor: a part's up and length vectors, a heading, and it tilts until both ends rest (earbuds on a table). Returns the scene's translate and rotate, and maps points on the part into the world (where a cable leaves a bud). | any Python |
| `typeset.py` | Sets text exactly as the canvas does (HarfBuzz shaping, canvas-style tracking) and writes SVG, DXF and vector PDF: wordmarks, plates, stencils, debossed lettering in CAD. | `.venv-fab` |
| `xover/xover.py` | Passive crossover design: drivers from FRD/ZMA measurements or Thiele-Small models, any R/L/C network by nodal analysis, delays from where the drivers sit, a least-squares fit to Linkwitz-Riley or Butterworth targets, values snapped to parts you can buy, plots and a parts list. See `xover/README.md`. | `.venv-fab` |
| `template/` | The skeleton `new_product.py` copies. | |

Why two Pythons: Blender 5's `bpy` wheel needs numpy 1 and build123d needs numpy 2. `bpy` stays on the system Python
and the CAD stack lives in `.venv-fab`. Installing build123d into the system Python breaks the path tracer;
`setup.sh` puts numpy 1 back if that happens.

The workflows are written up as project skills in `.claude/skills/`: `new-product`, `pathtrace`, `critic-round` and
`fab-package`.
