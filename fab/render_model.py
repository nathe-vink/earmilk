"""The render model: the speaker as the engine draws it, from the same CAD as the cut files (fab/cad.py), the bought
parts from their datasheets (fab/components.py) and the letters from the same outlines the metal is cut from
(fab/typeset.py). One named part each, so the engine paints by name and the critic can measure a part by name.

    .venv-fab/bin/python fab/render_model.py           -> out/render/earmilk-floorstander.glb and .json

What it leaves out: the panels inside the box (top, bottom, brace, shelf, divider), which no camera sees.
"""
import json, math, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from params import *  # noqa: F401,F403
import cad
import components as C
from build123d import Compound, Face, Polyline, Pos, Wire, export_gltf, extrude, Vector, Unit

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out', 'render')
VISIBLE = ['front-baffle', 'back-panel', 'side-left', 'side-right', 'gable-block', 'port-tube', 'terminal-cup']


def letters(face='front'):
    """The cast letters as solids standing BADGE['relief'] proud of the plinth's front (or the back, mirrored so they
    read from behind), set by the same code as the cut file."""
    # fab/typeset.py imports studio/typeset.py by the same module name, so load it under its own name
    import importlib.util
    spec = importlib.util.spec_from_file_location('fab_typeset', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'typeset.py'))
    T = importlib.util.module_from_spec(spec); spec.loader.exec_module(T)
    wordmark, pieces, bbox = T.wordmark, T.pieces, T.bbox
    contours, _ = wordmark(RUN, BADGE['z'], BADGE)
    bx0, by0, bx1, by1 = bbox(contours)
    dx = RUN - (bx0 + bx1) / 2
    contours = [[(x + dx, z) for (x, z) in c] for c in contours]
    out = []
    for (o, hs) in pieces(contours):
        if face == 'front':
            P = lambda x, z: (x, 0.0, z)                                         # on the front face, y = 0
            amount, d = BADGE['relief'], (0, -1, 0)
        else:
            oz = BACK_BADGE['z'] - BADGE['z']
            P = lambda x, z, oz=oz: (2 * RUN - x, PLAN, z + oz)                 # mirrored: read from behind
            amount, d = BACK_BADGE['relief'], (0, 1, 0)
        ow = Wire(Polyline(*[P(x, z) for (x, z) in o], close=True).edges())
        hw = [Wire(Polyline(*[P(x, z) for (x, z) in h], close=True).edges()) for h in hs]
        out.append(extrude(Face(ow, hw), amount=amount, dir=Vector(*d)))
    return out


def build():
    t0 = time.time()
    fab = cad.build()
    parts = {k: fab[k] for k in VISIBLE}
    print(f'cabinet {time.time() - t0:.0f}s', flush=True)
    wo, _ = C.driver_parts('woofer', C.DRIVERS['dsa315-8'], (RUN, 0.0, WOOFER['z']), ring_d=WOOFER_REBATE['d'] - 1.6)
    mi, _ = C.driver_parts('mid', C.DRIVERS['sb17mfc35-8'], (RUN, 0.0, MID['z']), ring_d=MID_REBATE['d'] - 1.6)
    tw, _ = C.driver_parts('tweeter', C.DRIVERS['tweeter-1in'], (RUN, WAVEGUIDE['throat_y'], WAVEGUIDE['throat_z']), flange_recess=0.0)
    parts.update(wo); parts.update(mi); parts.update(tw)
    for i, s in enumerate(letters('front')):
        parts[f'letters-front-{i}'] = s
    for i, s in enumerate(letters('back')):
        parts[f'letters-back-{i}'] = s
    print(f'all parts {time.time() - t0:.0f}s', flush=True)
    return parts


def main():
    os.makedirs(OUT, exist_ok=True)
    parts = build()
    kids = []
    for name, solid in parts.items():
        solid.label = name
        kids.append(solid)
    asm = Compound(children=kids); asm.label = 'earmilk-floorstander'
    path = os.path.join(OUT, 'earmilk-floorstander.glb')
    export_gltf(asm, path, unit=Unit.MM, binary=True, linear_deflection=0.0005, angular_deflection=0.08)
    info = {'parts': {}}
    for name, s in parts.items():
        bb = s.bounding_box()
        info['parts'][name] = [round(v, 1) for v in (bb.min.X, bb.min.Y, bb.min.Z, bb.max.X, bb.max.Y, bb.max.Z)]
    info['waveguide'] = WAVEGUIDE
    with open(os.path.join(OUT, 'earmilk-floorstander.json'), 'w') as f:
        json.dump(info, f, indent=1)
    print(path, os.path.getsize(path) // 1024, 'KB,', len(parts), 'parts')


if __name__ == '__main__':
    main()
