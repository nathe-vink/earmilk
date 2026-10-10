# fabkit: one product file in, a fabrication package out

The kit builds any concept's whole fabrication package from one Python file that says what the parts are. The concept
can be a speaker, a lamp or a valve amp. The product file gives its numbers and a function that turns them into
parts. Each part is a solid (build123d, placed where it sits), how it is made, and how it is finished. Everything
else is the kit's job, read off the solids. A product never writes its own DXF, drawing or parts list.

    .venv-fab/bin/python studio/fabkit/build.py studio/fabkit/example/product.py      # the worked example, ~15 s

| writes (under the product's `out/`) | from |
|---|---|
| `step/<name>.step`, `step/<part>.step` | every part in place, and the assembly, for any CAD program or shop |
| `stl/<part>.stl` | every part (prints first) |
| `dxf/<part>.dxf`, `dxf/<part>-underside.dxf` | each sheet part's cut file, read off its solid (`flats.py`) |
| `dxf/nest-<stock>-<n>.dxf`, `dxf/nest.svg`, `cutlist.csv` | the set's sheet parts nested on their stock, grain kept |
| `checks.json` | clashes, stock thicknesses, thin print walls, missing library entries (`checks.py`) |
| `bom.csv`, `bom.md` | the parts list for the set and its budget (`bom.py`) |
| `drawings/<name>-sheets.pdf` (+ `sheet-N.png`) | the drawing set (`drawings.py`) |
| `render/<name>.glb`, `studio/products/<name>.json`, `studio/shots/<name>/proof.json` | the render model, the engine's product file and a first shot (`render.py`) |
| `build.json` | what was built, the totals, whether the checks passed |

The build stops before the drawings if two parts clash, unless you pass `--force`.

## A product file

```python
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'studio', 'fabkit'))
from kit import *                              # Part, Product, Sheet, Printed, Machined, Bought, box, cyl, prism, ...
from speaker.drivers import driver_part       # optional: the speaker helpers

def parts(P):
    side = Sheet('baltic-birch', 18, grain='z')
    return [Part('left', box(0, 0, 0, 18, P['D'], P['H']), side, finish='birch'),
            Part('damping', None, Bought('damping-fill'))]      # bought, nothing to draw: still on the parts list

PRODUCT = Product('name', 'Title', 'What it is', params=dict(D=260, H=400), parts=parts,
                  materials={'birch': {'preset': 'birch'}}, notes=['Glue-up: ...'])
```

- **Frame**:
  - Units are millimetres.
  - x runs across, left to right seen from the front.
  - y runs back from the front face.
  - z runs up from the floor.
- **Part**: `Part(name, solid, make, finish='', qty=1, notes=[], group='', render=True, inside=False, draw=None,
  pieces={})`.
  - `qty` is per product; the set is `Product.count` (2 for a pair).
  - `draw` is a simpler stand-in for the drawings, such as a driver without its fine detail.
  - `pieces` maps `{piece: (solid, finish)}`: the render shows these instead of the solid, each in its own finish.
- **How a part is made** (stock tables in `model.py`, prices rough, 2026 USD):
  - `Sheet(material, thickness, face=None, grain=None)`: CNC or laser from flat stock. The part must be a prism of
    that thickness along one axis. `face` names the show face: `'+x'`, `'-y'` and so on. Without it, the face farther
    from the product's centre is used. `grain` is the axis the face grain must run along.
  - `Printed(material, orient='', min_wall=None)`: resin, MJF nylon, PETG, PLA or ASA. The wall check uses the
    material's minimum unless `min_wall` overrides it.
  - `Machined(material, process='cnc-mill', stock=None)`: from solid wood or metal. The blank defaults to the bounding
    box plus 5 mm a side.
  - `Bought(ref)`: a key of `library/components.json`, or of a `components.json` beside the product file, which adds
    to or overrides the kit's library.
- **Product**: `Product(name, title, kind, params, parts, count=2, notes=[], touching=[], materials={}, variants={},
  origin=(0,0,0), revision='A', drawing_prefix='')`.
  - `touching` lists name patterns (fnmatch) of pairs allowed to overlap, such as a press fit or a squeezed gasket.
  - `materials` maps finish names to the engine's presets (`studio/engine/materials.py`).
  - `variants` is the colourways, which the engine reads as flavours.

## What the kit reads off the solids

- **Cut files** (`flats.py`):
  - **Thickness and show face.** It finds the part's thickness axis and looks at it from the show face.
  - **Outline.** `CUT_OUTSIDE`.
  - **Through holes.** `CUT_INSIDE`, with round ones written as circles. An opening counts as a through hole when it
    matches across both faces, or across a face and a pocket's floor.
  - **Pockets from the face.** `POCKET_<depth>MM`, one layer per depth.
  - **Pockets from the inner face.** These go in their own file, seen from that face and turned over left to right,
    with the through cuts on `REF_THROUGH` to register them.
  - **Faces a 2D file can't carry.** Bevels and roundovers are listed on `NOTES`, in the cut list and on the
    drawings, in red.
  - **Nesting.** It packs the set's parts per stock in shelves, largest first, turning a part 90 degrees only when it
    has no grain.
- **Checks** (`checks.py`):
  - **Clashes.** Every pair of solids is tested for shared volume: bounding boxes first, then the boolean. Glue joints
    are faces that touch without overlapping, so they pass.
  - **Print walls.** Rays are cast inward from 400 points on the surface. A wall is thin where a ray leaves through a
    face that looks back at it, closer than the material allows. A face the ray only grazes is a corner, not a wall.
  - **Stock.** Each sheet part's thickness must be one its stock comes in.
  - **Library.** Every bought part must be in the library.
- **Parts list** (`bom.py`):
  - **Prices.** Bought parts come from the library, each with its supplier and the date of the listing. Made parts
    come from the stock rates:
    - sheet parts: their area with 25 % for offcuts;
    - prints: their volume plus a handling charge;
    - machined parts: their blank plus a setup charge per line.
  - **Merging.** Identical lines merge. Made parts merge only when their solids match.
  - **Unknown prices.** A price nobody has found prints as `[PRICE]`. The kit never invents one.
- **Drawings** (`drawings.py`, A3, first angle, hidden-line removal on the solids, all text 2.5 mm or more):
  1. **General arrangement**, with the section line.
  2. **Section A-A** down the middle, each part's cut faces hatched at its own angle.
  3. **Exploded view**, ballooned to the parts list.
  4. **Plain panels**, on one sheet.
  5. **Panels with features**, one sheet each, with a feature table. Each feature is marked P (pocket), H (through
     cut) or U (inner-face pocket) and listed with its size, its centre from the lower-left corner and its depth.
  6. **Printed and machined parts**, one sheet per parts-list line, three views with hidden lines and their sizes.
  7. **The parts list and the notes.**
- **Render** (`render.py`):
  - One named mesh per part, or per piece when the part has pieces.
  - The engine's product file: materials by finish, the origin at the footprint's centre on the floor, flavours from
    `variants`.
  - A proof shot on a grey sweep, which a rebuild leaves alone once you have edited it. Render it with
    `python3 studio/engine/render.py studio/shots/<name>/proof.json --out ...`.

## The speaker helpers (`speaker/`)

- **`drivers.py`**: driver solids from datasheet numbers (`geom` in the library):
  - `cone_driver`, `dome_tweeter` and `compression_driver`;
  - `driver_part(name, ref, geom, centre, axis, recess)`, which gives a bought part with render pieces and a light
    stand-in for the drawings;
  - `place()`, for any axis.
- **`box.py`**: the bass box from Thiele-Small figures (`ts` in the library), using the same lumped model as earmilk's
  `fab/acoustics.py`:
  - `vented(ts, Vb_l, fb, bore_mm)` gives f3, maximum SPL, port length and port air speed;
  - `sealed(ts, Vb_l)` gives Qtc and fc;
  - `suggest_vented(ts)` gives a starting alignment.
- **`horn.py`**: horn and waveguide profiles (`conical`, `exponential`, `tractrix`, `os`) and their shells:
  - `round_horn` (revolved, with a flange and a rolled lip);
  - `rect_horn` (lofted);
  - `mouth_for_coverage(fc, angle)`, Keele's rule.

  Nothing here simulates a horn's response. That needs a BEM run, like earmilk's `fab/bem.py`.

## Habits that keep the solids honest

- **Extend every cutter past the faces it opens**, by 1 mm. A cutting surface that is coplanar with a face, or tangent
  to it, can make OpenCascade return the body uncut, and it raises no error. A roundover run tangent into a face did
  exactly this to the example's waveguide. The clash check caught it: the tweeter overlapped the uncut puck. A clash
  you didn't expect is the first sign. The example's waveguide shows the fix: the arc stops at 80 degrees and runs
  straight out through the face.
- **Draw curves as curves.** Use `revolve_profile(..., smooth=[(i, j)])` to turn a run of profile points into one
  spline. A curve made of many short lines draws as rings and renders faceted.
- **Keep drivers inside their cut-outs.** `cone_driver` keeps the basket inside the maker's cut-out, because it passes
  through it.
- **Numbers come from datasheets** via the library, and each library entry says where it came from. Measure the part
  before cutting a baffle.
