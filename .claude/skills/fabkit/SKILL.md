---
name: fabkit
description: Build a fabrication package (STEP, STL, DXF cut files and nesting, clash and wall checks, parts list, A3 drawing set, render model and proof shot) for any new product concept from one product file with studio/fabkit. Use when starting a new physical concept, adding parts to one, or the user asks for build files for something that is not earmilk.
---

# fabkit

- **Start from the example.** Copy `studio/fabkit/example/product.py` to `spinoffs/<name>/product.py` and change the
  numbers and parts. Every way of making a part is in it: `Sheet`, `Printed`, `Machined`, `Bought`, and `Bought` with
  no solid.
- **Build.** `.venv-fab/bin/python studio/fabkit/build.py spinoffs/<name>/product.py`, add `--skip drawings,render`
  for a quick pass. Outputs land in `spinoffs/<name>/out/`. Never edit them by hand: change the product file and
  rebuild.
- **Read `checks.json` first.**
  - **A clash** means two solids share volume. Fix the geometry. List a pair in `touching` only when the overlap is
    meant, such as a press fit or a gasket.
  - **An unexpected clash** can be a boolean that silently failed. A cutter that is coplanar with a face, or tangent to
    it, leaves the body uncut. Extend cutters 1 mm past the faces they open.
  - **Thin print walls** are listed with their locations.
- **Bought parts** come from `studio/fabkit/library/components.json`, or a `components.json` beside the product file.
  - Every price needs a supplier and a date.
  - Leave `usd` as null when no price was found. The parts list then prints `[PRICE]`. Never invent one.
- **Speakers.**
  - `speaker/drivers.py` (`driver_part`) builds drivers from their library `geom`.
  - `speaker/box.py` (`sealed`, `vented`) works out the box from `ts`.
  - `speaker/horn.py` gives horn profiles and shells. It does not simulate them; a response needs BEM.
- **Look at the drawings** (`out/drawings/sheet-N.png`) before you call a package done.
- **Render** with `python3 studio/engine/render.py studio/shots/<name>/proof.json --out renders/<day>/<name>-proof.png`.
  Give the finishes real presets in `PRODUCT.materials`.
- **The full reference** is `studio/fabkit/README.md`.
