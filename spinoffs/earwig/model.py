"""earwig: builds the parts from params.py and exports them for rendering and printing.

    .venv-fab/bin/python spinoffs/earwig/model.py

Writes out/stl/<part>.stl, out/step/<part>.step and out/parts.json (part names, materials, volumes, and the case's
dimensions, which the wig in hair.py grows on). The wig is not CAD: the path tracer grows it (hair.py).
"""
import json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from params import *  # noqa: F401,F403
from build123d import (Axis, Box, Circle, Cylinder, Ellipse, Plane, Polyline, Pos, Spline, Vertex, export_step, export_stl,
                       extrude, fillet, loft, make_face, mirror, revolve)
import numpy as np

OUT = os.path.join(HERE, 'out')


def bud_body():
    secs = [Plane.XY.offset(z) * Pos(cx, 0) * Ellipse(a, b) for (z, a, b, cx) in BUD_SECTIONS]
    body = loft([Vertex(BUD_TOP[0], 0, BUD_TOP[1])] + secs + [Vertex(BUD_BOTTOM[0], 0, BUD_BOTTOM[1])])
    # the abdomen's segments: shallow grooves round the stem
    for zg in STEM_GROOVES:
        zs = [s[0] for s in BUD_SECTIONS][::-1]
        a = float(np.interp(zg, zs, [s[1] for s in BUD_SECTIONS][::-1]))
        b = float(np.interp(zg, zs, [s[2] for s in BUD_SECTIONS][::-1]))
        cx = float(np.interp(zg, zs, [s[3] for s in BUD_SECTIONS][::-1]))
        ring = extrude(Plane.XY.offset(zg - GROOVE_W / 2) * Pos(cx, 0) * (Ellipse(a + 2, b + 2) - Ellipse(a - GROOVE_D, b - GROOVE_D)), amount=GROOVE_W)
        body -= ring
    # the nozzle: a short tapered barrel into the canal
    d = np.array(NOZZLE_DIR) / np.linalg.norm(NOZZLE_DIR)
    p0 = np.array(NOZZLE_AT) - d * 4.0
    pl = Plane(origin=tuple(p0), z_dir=tuple(d))
    noz = loft([pl * Circle(NOZZLE_R + 0.4), pl.offset(4.0 + NOZZLE_LEN) * Circle(NOZZLE_R)])
    body += noz
    return body, d, np.array(NOZZLE_AT) + d * NOZZLE_LEN


def ear_tip(end, d):
    """A mushroom silicone tip over the nozzle's end; its front face carries the sound hole."""
    r = TIP_D / 2
    pts = [(0, 1.9), (0.0, 3.0), (1.0, r * 0.84), (2.8, r * 0.99), (4.8, r), (6.6, r * 0.8), (TIP_LEN, NOZZLE_R + 0.5)]
    sp = Spline(*[(x, y, 0) for x, y in pts])
    f = make_face([sp, Polyline((TIP_LEN, NOZZLE_R + 0.5, 0), (TIP_LEN, 1.9, 0), (0, 1.9, 0))]).face()
    tip = revolve(f, Axis.X, 360)
    # front of the tip at the nozzle's end + 1.2, pointing along d; the tip's local +x runs back toward the body
    o = end + d * 1.2
    pl = Plane(origin=tuple(o), x_dir=tuple(-d), z_dir=tuple(np.cross(-d, [0, 0, 1]) / np.linalg.norm(np.cross(-d, [0, 0, 1]))))
    return pl * tip


def pincer(sign):
    """One forceps arm: circles along a bowed curve in the y-z plane, tapering to the tip."""
    cx = BUD_SECTIONS[-1][3]
    n = 10
    def P(t):
        z = PINCER_TOP_Z - PINCER_LEN_Z * t
        y = PINCER_BASE_Y + PINCER_BOW * math.sin(math.pi * t ** 0.85) - (PINCER_BASE_Y - PINCER_TIP_Y) * t
        return np.array([cx, sign * y, z])
    secs = []
    for i in range(n + 1):
        t = i / n
        p = P(t); q = P(min(1, t + 1e-3)) - P(max(0, t - 1e-3)); q /= np.linalg.norm(q)
        r = PINCER_R0 + (PINCER_R1 - PINCER_R0) * t ** 1.3 + 0.12 * math.sin(math.pi * min(1, t * 2.5))
        secs.append(Plane(origin=tuple(p), z_dir=tuple(q)) * Circle(r))
    return loft(secs)


def case():
    b = Pos(0, 0, CASE_H / 2) * Box(CASE_W, CASE_D, CASE_H)
    b = fillet(b.edges(), CASE_R)
    zs = CASE_H * LID_SPLIT
    base = b & (Pos(0, 0, (zs - LID_GAP / 2) / 2) * Box(CASE_W + 2, CASE_D + 2, zs - LID_GAP / 2))
    lid = b & (Pos(0, 0, (zs + LID_GAP / 2 + CASE_H + 1) / 2) * Box(CASE_W + 2, CASE_D + 2, CASE_H + 1 - zs - LID_GAP / 2))
    led = Pos(0, -CASE_D / 2 + 0.25, zs - 7.0) * Cylinder(0.6, 1.0, rotation=(90, 0, 0))   # status light on the front
    return base, lid, led, zs


def build():
    body, d, end = bud_body()
    tip = ear_tip(end, d)
    pins = pincer(1) + pincer(-1)
    base, lid, led, zs = case()
    parts = {
        'bud-r': (body, 'shell'), 'pincers-r': (pins, 'pincer'), 'tip-r': (tip, 'silicone'),
        'bud-l': (mirror(body, Plane.YZ), 'shell'), 'pincers-l': (mirror(pins, Plane.YZ), 'pincer'), 'tip-l': (mirror(tip, Plane.YZ), 'silicone'),
        'case-base': (base, 'shell'), 'case-lid': (lid, 'shell'), 'case-led': (led, 'led'),
    }
    facts = {'case': {'w': CASE_W, 'd': CASE_D, 'h': CASE_H, 'r': CASE_R, 'split_z': zs},
             'bud_height_mm': round(BUD_TOP[1] - (PINCER_TOP_Z - PINCER_LEN_Z), 1)}
    return parts, facts


def main():
    os.makedirs(os.path.join(OUT, 'stl'), exist_ok=True); os.makedirs(os.path.join(OUT, 'step'), exist_ok=True)
    parts, facts = build()
    manifest = {'parts': {}, 'facts': facts}
    for name, (solid, mat) in parts.items():
        export_stl(solid, os.path.join(OUT, 'stl', f'{name}.stl'), tolerance=0.01, angular_tolerance=0.08)
        export_step(solid, os.path.join(OUT, 'step', f'{name}.step'))
        manifest['parts'][name] = {'material': mat, 'volume_cm3': round(solid.volume / 1000, 3)}
    json.dump(manifest, open(os.path.join(OUT, 'parts.json'), 'w'), indent=1)
    print(json.dumps(manifest, indent=1))


if __name__ == '__main__':
    main()
