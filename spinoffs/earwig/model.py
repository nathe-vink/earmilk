"""earwig: builds the parts from params.py and exports them for rendering and printing.

    .venv-fab/bin/python spinoffs/earwig/model.py

Writes out/stl/<part>.stl, out/step/<part>.step and out/parts.json (part names, materials, volumes, the case's
dimensions, and the tail's root and direction in each bud's frame). The tail is not CAD: it is a moulded sleeve of
overlapping plates over a soft core, and the path tracer draws it, plate by plate, along the path scene.py lays.
"""
import json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from params import *  # noqa: F401,F403
from build123d import (Axis, Box, Circle, Cylinder, Ellipse, Plane, Polyline, Pos, Sphere, Spline, Vertex, export_step, export_stl,
                       extrude, fillet, loft, make_face, mirror, revolve, scale)
import numpy as np

OUT = os.path.join(HERE, 'out')


def bud_body():
    secs = [Plane.XY.offset(z) * Pos(cx, 0) * Ellipse(a, b) for (z, a, b, cx) in BUD_SECTIONS]
    body = loft([Vertex(BUD_TOP[0], 0, BUD_TOP[1])] + secs + [Vertex(BUD_BOTTOM[0], 0, BUD_BOTTOM[1])])
    # since 2026-10-06 the body ends at a short neck; the tail (scene.py, drawn by the path tracer) leaves it there
    # the nozzle: a short tapered barrel into the canal
    d = np.array(NOZZLE_DIR) / np.linalg.norm(NOZZLE_DIR)
    p0 = np.array(NOZZLE_AT) - d * 4.0
    pl = Plane(origin=tuple(p0), z_dir=tuple(d))
    noz = loft([pl * Circle(NOZZLE_R + 0.4), pl.offset(4.0 + NOZZLE_LEN) * Circle(NOZZLE_R)])
    body += noz
    return body, d, np.array(NOZZLE_AT) + d * NOZZLE_LEN


def ear_tip(end, d):
    """A mushroom silicone tip over the nozzle's end; its front face carries the sound hole."""
    # as bought: a stem that grips the nozzle and a thin skirt flaring back from its front lip, an air gap between them
    # (a solid dome read as taupe putty with a black hole: softer round 2); the skirt drawn for a medium tip, scaled
    k = TIP_D / 11.5
    ri, rs = NOZZLE_R + 0.02, NOZZLE_R + 0.7
    outer = Spline(*[(x, y * k, 0) for x, y in [(0, (rs + 0.3) / k), (0.45, 4.6), (1.6, 5.45), (3.2, 5.75), (5.0, 5.6), (6.6, 5.0), (TIP_LEN, 4.5)]])
    inner = Spline(*[(x, y * k, 0) for x, y in [(TIP_LEN - 0.2, 4.05), (6.3, 4.6), (4.9, 5.12), (3.2, 5.28), (1.8, 4.95), (1.0, 4.25)]] + [(0.85, rs, 0)])
    f = make_face([outer, Polyline((TIP_LEN, 4.5 * k, 0), (TIP_LEN - 0.2, 4.05 * k, 0)), inner,
                   Polyline((0.85, rs, 0), (5.8, rs, 0), (5.8, ri, 0), (0, ri, 0), (0, rs + 0.3, 0))]).face()
    tip = revolve(f, Axis.X, 360)
    # front of the tip at the nozzle's end + 1.2, pointing along d; the tip's local +x runs back toward the body
    o = end + d * 1.2
    pl = Plane(origin=tuple(o), x_dir=tuple(-d), z_dir=tuple(np.cross(-d, [0, 0, 1]) / np.linalg.norm(np.cross(-d, [0, 0, 1]))))
    return pl * tip


def pincer(sign):
    """One forceps arm, in the forceps' own frame: circles along a bowed curve in the y-z plane, tapering to the tip."""
    cx = 0.0
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
    tip_r = PINCER_R0 + (PINCER_R1 - PINCER_R0) + 0.12 * math.sin(math.pi * 1.0)
    return loft(secs) + Pos(*P(1.0)) * Sphere(tip_r)                    # rounded tips: a pinch, not a stab


def forceps():
    """The tail's last plate, a small knob, with the two arms running from it down -z: the forceps the tail ends in, in
    their own frame so the scene can set them at the tail's end. Pinching them is the control."""
    kx, ky, kz = FORCEPS_KNOB[1], FORCEPS_KNOB[0], FORCEPS_KNOB[2]
    knob = scale(Sphere(1.0), by=(kx, ky, kz))
    return knob + pincer(1) + pincer(-1)


def collar():
    """A satin collar round the tail's root, where the plates leave the body."""
    return Pos(*TAIL_ROOT) * Cylinder(COLLAR_R, COLLAR_LEN)


def case():
    b = Pos(0, 0, CASE_H / 2) * Box(CASE_W, CASE_D, CASE_H)
    b = fillet(b.edges(), CASE_R)
    zs = CASE_H * LID_SPLIT
    base = b & (Pos(0, 0, (zs - LID_GAP / 2) / 2) * Box(CASE_W + 2, CASE_D + 2, zs - LID_GAP / 2))
    lid = b & (Pos(0, 0, (zs + LID_GAP / 2 + CASE_H + 1) / 2) * Box(CASE_W + 2, CASE_D + 2, CASE_H + 1 - zs - LID_GAP / 2))
    # the wing-case lid (2026-10-06): a seam down the middle, front to back over the top, like an earwig's folded wing covers.
    # The groove is the lid's outer skin (the lid less a copy shrunk by the seam's depth) inside a thin slab at x = 0.
    c = lid.center()
    k = WING_SEAM_D * 2
    inner = Pos(c.X, c.Y, c.Z) * scale(Pos(-c.X, -c.Y, -c.Z) * lid, by=((CASE_W - k) / CASE_W, (CASE_D - k) / CASE_D, 1 - k / (CASE_H - zs)))
    seam = (lid - inner) & Pos(0, 0, CASE_H / 2) * Box(WING_SEAM_W, CASE_D + 4, CASE_H + 4)
    lid = lid - seam
    led = Pos(0, -CASE_D / 2 + 0.25, zs - 7.0) * Cylinder(0.6, 1.0, rotation=(90, 0, 0))   # status light on the front
    return base, lid, led, zs


def split_shell(body):
    """Two-part shell: the outer half gloss, the inner half (the nozzle's side) satin, a parting line between them.
    Only the head splits; the stem stays one piece."""
    big = 80.0
    outer_box = Pos(SPLIT_X - SEAM / 2 - big / 2, 0, SPLIT_ZMIN + big / 2) * Box(big, big, big)
    inner_box = Pos(SPLIT_X + SEAM / 2 + big / 2, 0, SPLIT_ZMIN + big / 2) * Box(big, big, big)
    gap = Pos(SPLIT_X, 0, SPLIT_ZMIN + big / 2) * Box(SEAM, big, big)
    lower = Pos(0, 0, SPLIT_ZMIN - big / 2) * Box(big, big, big)
    outer = (body & outer_box) + (body & lower)
    inner = body & inner_box
    return outer - gap, inner


def sensor(body):
    """The wear sensor's window, a dark gloss oval on the inner half: the shell grown 0.6 % about its centre, clipped to an
    elliptical prism through the window, less the shell itself, so the window follows the surface (critic, softer round 3)."""
    c = body.center()
    big = Pos(c.X, c.Y, c.Z) * scale(Pos(-c.X, -c.Y, -c.Z) * body, by=1.006)
    prism = Plane.YZ.offset(SPLIT_X + 1) * Pos(SENSOR_AT[0], SENSOR_AT[1]) * extrude(Ellipse(SENSOR_AB[0], SENSOR_AB[1]), 14)
    return (big & prism) - body


def grille(end, d):
    """The nozzle's mesh, just in front of its end face, so the tip's hole reads as an opening."""
    pl = Plane(origin=tuple(end + d * 0.05), z_dir=tuple(d))
    return pl * Cylinder(1.85, 0.1)


def build():
    body, d, end = bud_body()
    tip = ear_tip(end, d)
    body, inner = split_shell(body)
    win = sensor(inner)
    mesh = grille(end, d)
    fc = forceps()
    col = collar()
    base, lid, led, zs = case()
    parts = {
        'bud-r': (body, 'shell'), 'inner-r': (inner, 'satin'), 'grille-r': (mesh, 'grille'), 'collar-r': (col, 'satin'), 'tip-r': (tip, 'silicone'),
        'bud-l': (mirror(body, Plane.YZ), 'shell'), 'inner-l': (mirror(inner, Plane.YZ), 'satin'), 'grille-l': (mirror(mesh, Plane.YZ), 'grille'),
        'collar-l': (mirror(col, Plane.YZ), 'satin'), 'tip-l': (mirror(tip, Plane.YZ), 'silicone'),
        'sensor-r': (win, 'sensor'), 'sensor-l': (mirror(win, Plane.YZ), 'sensor'),
        'forceps': (fc, 'pincer'),
        'case-base': (base, 'case'), 'case-lid': (lid, 'shell'), 'case-led': (led, 'led'),
    }
    rx, ry, rz = TAIL_ROOT
    facts = {'case': {'w': CASE_W, 'd': CASE_D, 'h': CASE_H, 'r': CASE_R, 'split_z': zs},
             'tail': {'root_r': [rx, ry, rz], 'root_l': [-rx, ry, rz], 'dir': [0, 0, -1.0], 'len': TAIL_LEN,
                      'r0': TAIL_R0, 'r1': TAIL_R1, 'pitch': TAIL_PITCH, 'flare': TAIL_FLARE},
             'forceps': {'knob': list(FORCEPS_KNOB), 'len': PINCER_LEN_Z - PINCER_TOP_Z},
             'bud_height_mm': round(BUD_TOP[1] - BUD_BOTTOM[1], 1)}
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
