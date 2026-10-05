"""earworm: builds the parts from params.py and exports them for rendering and printing.

    .venv-fab/bin/python spinoffs/earworm/model.py

Wired in-ear earphones. Writes out/stl/<part>.stl, out/step/<part>.step, out/stl/print/ (a printable shell) and
out/parts.json: part names, materials, volumes, and the points scene.py needs (where the worm leaves each bud, where
the branches enter the splitter). The cable is not CAD: it is a moulded sleeve over a bought cable, and the path
tracer draws it, segment by overlapping segment, from the path in scene.py.
"""
import json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from params import *  # noqa: F401,F403
from build123d import (Axis, Cylinder, Plane, Polyline, Pos, Rot, Spline, export_step, export_stl, make_face, revolve)

OUT = os.path.join(HERE, 'out')
RB = BUD_D / 2


def profile(pts, rounds=()):
    """A closed polygon in the XY plane (x along the axis, y as radius) with some corners rounded."""
    f = make_face(Polyline(*[(x, y, 0) for x, y in pts], close=True)).face()
    for (cx, cy), r in rounds:
        v = [v for v in f.vertices() if abs(v.X - cx) < 1e-6 and abs(v.Y - cy) < 1e-6]
        f = f.fillet_2d(r, v)
    return f


def bud():
    """Back cap (gunmetal, with the burrow), front shell (graphite, with the nozzle), tip, mesh. Along +x."""
    s = BUD_SPLIT
    cap = revolve(profile([(0, 0), (0, RB), (s, RB), (s, 0)], [((0, RB), BUD_BACK_R)]), Axis.X, 360)
    shell = revolve(profile([(s, 0), (s, RB), (BUD_LEN, RB), (BUD_LEN, NOZZLE_D / 2 + 0.6), (BUD_LEN + NOZZLE_LEN, NOZZLE_D / 2),
                             (BUD_LEN + NOZZLE_LEN, 0)], [((BUD_LEN, RB), BUD_FRONT_R)]), Axis.X, 360)
    seam = revolve(profile([(s - SEAM_W / 2, RB - SEAM_D), (s - SEAM_W / 2, RB + 1), (s + SEAM_W / 2, RB + 1), (s + SEAM_W / 2, RB - SEAM_D)]), Axis.X, 360)
    cap, shell = cap - seam, shell - seam
    # the burrow: a collar on the back face with a bore a little under the worm, so the head looks gripped
    hole_r = BRANCH_R * 0.9                                                  # the worm (0.95 R at its head) presses into it
    eyelet = revolve(profile([(-EYELET_LEN, hole_r), (-EYELET_LEN, EYELET_D / 2), (0.6, EYELET_D / 2), (0.6, hole_r)],
                             [((-EYELET_LEN, EYELET_D / 2), 0.45)]), Axis.X, 360)
    cap = cap + eyelet - Pos(-EYELET_LEN - 1, 0, 0) * Rot(0, 90, 0) * Cylinder(hole_r, 12, align=None)
    end = BUD_LEN + NOZZLE_LEN
    shell = shell - Pos(end - 0.6, 0, 0) * Rot(0, 90, 0) * Cylinder(NOZZLE_D / 2 - 0.55, 1.4)       # the sound bore's mouth
    mesh = Pos(end - 1.0, 0, 0) * Rot(0, 90, 0) * Cylinder(NOZZLE_D / 2 - 0.5, 0.1)
    r = TIP_D / 2
    pts = [(0, 1.9), (0.0, 3.0), (1.0, r * 0.84), (2.8, r * 0.99), (4.6, r), (6.4, r * 0.8), (TIP_LEN, NOZZLE_D / 2 + 0.4)]
    f = make_face([Spline(*[(x, y, 0) for x, y in pts]), Polyline((TIP_LEN, NOZZLE_D / 2 + 0.4, 0), (TIP_LEN, 1.9, 0), (0, 1.9, 0))]).face()
    tip = Pos(end + 1.0, 0, 0) * Rot(0, 0, 180) * revolve(f, Axis.X, 360)          # front of the tip 1 mm past the nozzle
    return {'cap': cap, 'shell': shell, 'mesh': mesh, 'tip': tip}


def splitter():
    """Where the two worms become one: a short gunmetal barrel, the main cable out of x = 0, the branches into x = LEN."""
    R = SPLIT_D / 2
    body = revolve(profile([(0, 0), (0, R), (SPLIT_LEN, R), (SPLIT_LEN, 0)], [((0, R), 1.6), ((SPLIT_LEN, R), 2.0)]), Axis.X, 360)
    body -= Pos(-1, 0, 0) * Rot(0, 90, 0) * Cylinder(MAIN_R * 0.92, 8, align=None)
    for sy in (1, -1):
        body -= Pos(SPLIT_LEN - 6, sy * SPLIT_HOLE_OFFSET, 0) * Rot(0, 90, 0) * Cylinder(BRANCH_R * 0.92, 8, align=None)
    return body


def plug():
    """A 3.5 mm TRRS plug along +x from the cable's end at x = 0: the tail runs into a gunmetal barrel, a dark collar,
    the pin."""
    bx0, bx1, br = -PLUG_BARREL_LEN + 1.5, 1.5, PLUG_BARREL_D / 2
    barrel = revolve(profile([(bx0, 0), (bx0, br), (bx1, br), (bx1, 0)], [((bx0, br), 1.3), ((bx1, br), 0.6)]), Axis.X, 360)
    r = PLUG_D / 2
    x0, x1 = bx1 + 0.8, bx1 + 0.8 + PLUG_LEN
    pin = revolve(profile([(x0, 0), (x0, r), (x1 - 2.0, r), (x1 - 1.0, r * 0.62), (x1, 0)], [((x1 - 2.0, r), 0.8), ((x1 - 1.0, r * 0.62), 0.4)]), Axis.X, 360)
    rings = Pos(bx1 + 0.4, 0, 0) * Rot(0, 90, 0) * Cylinder(2.2, 0.8)
    for d in PLUG_RINGS:
        rings = rings + Pos(x1 - d, 0, 0) * Rot(0, 90, 0) * Cylinder(r + 0.02, 0.7)
    return barrel, pin, rings


def printable(b):
    """For making one: the cap and shell hollowed to PRINT_WALL, a seat for the driver against the nozzle's shoulder,
    the sound bore through the nozzle. Resin-print both and glue at the parting line."""
    s, w = BUD_SPLIT, PRINT_WALL
    cav = revolve(profile([(w, 0), (w, RB - w), (BUD_LEN - w, RB - w), (BUD_LEN - w, 0)], [((w, RB - w), max(0.5, BUD_BACK_R - w))]), Axis.X, 360)
    seat = Pos(BUD_LEN - w - DRIVER_T / 2, 0, 0) * Rot(0, 90, 0) * Cylinder(DRIVER_D / 2 + 0.1, DRIVER_T)
    bore = Pos(BUD_LEN + NOZZLE_LEN / 2, 0, 0) * Rot(0, 90, 0) * Cylinder(1.3, NOZZLE_LEN + 4)
    return {'print-cap': b['cap'] - cav, 'print-shell': b['shell'] - cav - seat - bore}


def build():
    b = bud()
    barrel, pin, rings = plug()
    parts = {'bud-cap': (b['cap'], 'metal'), 'bud-shell': (b['shell'], 'shell'), 'bud-mesh': (b['mesh'], 'grille'),
             'bud-tip': (b['tip'], 'silicone'), 'splitter': (splitter(), 'metal'),
             'plug-barrel': (barrel, 'metal'), 'plug': (pin, 'plug'), 'plug-rings': (rings, 'plug_rings')}
    facts = {
        'bud': {'worm_start': [4.0, 0, 0], 'worm_mouth': [-EYELET_LEN, 0, 0], 'out_dir': [-1.0, 0, 0],
                'tip_front_x': BUD_LEN + NOZZLE_LEN + 1.0, 'back_x': -EYELET_LEN},
        'splitter': {'main_hole': [0.0, 0, 0], 'main_dir': [-1.0, 0, 0],
                     'branch_holes': [[SPLIT_LEN, SPLIT_HOLE_OFFSET, 0], [SPLIT_LEN, -SPLIT_HOLE_OFFSET, 0]], 'branch_dir': [1.0, 0, 0]},
    }
    return parts, facts, printable(b)


def main():
    for d in ('stl', 'step', os.path.join('stl', 'print')):
        os.makedirs(os.path.join(OUT, d), exist_ok=True)
    parts, facts, prints = build()
    manifest = {'parts': {}, 'facts': facts, 'print': {}}
    for name, (solid, mat) in parts.items():
        export_stl(solid, os.path.join(OUT, 'stl', f'{name}.stl'), tolerance=0.005, angular_tolerance=0.06)
        export_step(solid, os.path.join(OUT, 'step', f'{name}.step'))
        manifest['parts'][name] = {'material': mat, 'volume_cm3': round(solid.volume / 1000, 3)}
    for name, solid in prints.items():
        export_stl(solid, os.path.join(OUT, 'stl', 'print', f'{name}.stl'), tolerance=0.005, angular_tolerance=0.06)
        export_step(solid, os.path.join(OUT, 'step', f'{name}.step'))
        manifest['print'][name] = {'volume_cm3': round(solid.volume / 1000, 3), 'valid': solid.is_valid}
    json.dump(manifest, open(os.path.join(OUT, 'parts.json'), 'w'), indent=1)
    print(json.dumps({k: v['volume_cm3'] for k, v in manifest['parts'].items()}), json.dumps(manifest['print']))


if __name__ == '__main__':
    main()
