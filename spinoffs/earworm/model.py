"""earworm: builds the parts from params.py and exports them for rendering and printing.

    .venv-fab/bin/python spinoffs/earworm/model.py

Writes out/stl/<part>.stl, out/step/<part>.step and out/parts.json (part names, materials, volumes, and the worm's
start point and direction at the grommet, which scene.py reads). The cable itself is not CAD: it is a moulded sleeve
over a bought cable, and the path tracer draws it from the path in scene.py.
"""
import json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'studio'))
from params import *  # noqa: F401,F403
from build123d import (Axis, Box, Cylinder, Face, Plane, Polyline, Pos, Rectangle, RectangleRounded, Rot, Wire,
                       export_step, export_stl, extrude, fillet, make_face, mirror, revolve)

OUT = os.path.join(HERE, 'out')
R_CUP = CUP_D / 2
SHELL_FRONT_X = CUSHION_IN_X + CUSHION_T          # 96
SHELL_BACK_X = SHELL_FRONT_X + SHELL_DEPTH         # 126
YOKE_X = SHELL_FRONT_X + SHELL_DEPTH * 0.5         # the yoke and the band end sit over the shell's middle


def profile(pts, rounds):
    """A closed polygon in the XY plane (x along the cup axis, y as radius) with some corners rounded."""
    f = make_face(Polyline(*[(x, y, 0) for x, y in pts], close=True)).face()
    for (cx, cy), r in rounds:
        v = [v for v in f.vertices() if abs(v.X - cx) < 1e-6 and abs(v.Y - cy) < 1e-6]
        f = f.fillet_2d(r, v)
    return f


def cup_parts():
    """The right cup; the left is its mirror image."""
    x0, x1 = SHELL_FRONT_X, SHELL_BACK_X
    shell = revolve(profile([(x0, 0), (x0, R_CUP), (x1, R_CUP), (x1, 0)], [((x1, R_CUP), SHELL_ROUND), ((x0, R_CUP), 1.5)]), Axis.X, 360)
    # signs of being made: a parting line round the side, and the line of the back cap that carries the wordmark
    xp = x0 + PARTING_X
    shell -= revolve(profile([(xp - SEAM_W / 2, R_CUP - SEAM_D), (xp - SEAM_W / 2, R_CUP + 1), (xp + SEAM_W / 2, R_CUP + 1), (xp + SEAM_W / 2, R_CUP - SEAM_D)], []), Axis.X, 360)
    shell -= revolve(profile([(x1 - SEAM_D, CAP_R - SEAM_W / 2), (x1 - SEAM_D, CAP_R + SEAM_W / 2), (x1 + 1, CAP_R + SEAM_W / 2), (x1 + 1, CAP_R - SEAM_W / 2)], []), Axis.X, 360)
    ci, co = CUSHION_IN_X, SHELL_FRONT_X - 0.4                        # a hair off the shell: no coplanar faces
    rh = CUSHION_HOLE_D / 2
    cushion = revolve(profile([(ci, rh), (ci, R_CUP - 0.5), (co, R_CUP - 0.5), (co, rh)],
                              [((ci, R_CUP - 0.5), CUSHION_ROUND), ((ci, rh), 7.0), ((co, R_CUP - 0.5), 3.0), ((co, rh), 2.0)]), Axis.X, 360)
    # the pad's welt: the seam where its leather is sewn, near the back
    xs = co - 3.6
    cushion -= revolve(profile([(xs - SEAM_W / 2, R_CUP - 0.5 - SEAM_D), (xs - SEAM_W / 2, R_CUP + 1), (xs + SEAM_W / 2, R_CUP + 1), (xs + SEAM_W / 2, R_CUP - 0.5 - SEAM_D)], []), Axis.X, 360)
    baffle = Pos(x0 - 1.4, 0, 0) * Rot(0, 90, 0) * Cylinder(rh + 1.0, 0.8)   # the driver's cloth, seen through the ear opening
    # The yoke: a U around the cup's top half, revolved about the cup axis; an eye at each pivot; a stem up to the slider.
    sec = Pos(YOKE_X, YOKE_R, 0) * RectangleRounded(YOKE_T, YOKE_W, 2.0)
    yoke = revolve(sec, Axis.X, 180)
    for sy in (1, -1):
        yoke += Pos(YOKE_X, sy * YOKE_R, 0) * Rot(90, 0, 0) * Cylinder(6.5, YOKE_W)
        yoke += Pos(YOKE_X, sy * (R_CUP + 1.5), 0) * Rot(90, 0, 0) * Cylinder(PIVOT_D / 2, 9.0)
    return shell, cushion, baffle, yoke


def band_parts():
    ex, ez = BAND_END
    zc = (ex ** 2 + ez ** 2 - BAND_APEX_Z ** 2) / (2 * (ez - BAND_APEX_Z))
    R = BAND_APEX_Z - zc
    th = math.degrees(math.atan2(ex, ez - zc))
    axis = Axis((0, 0, zc), (0, 1, 0))
    sec = Plane.YZ * Pos(0, BAND_APEX_Z, 0) * RectangleRounded(BAND_W, BAND_T, 2.4)
    band = revolve(sec.rotate(axis, -th), axis, 2 * th)
    # stitch lines along the band's outer face, 2.6 in from each edge
    for sy in (1, -1):
        g = Plane.YZ * Pos(sy * (BAND_W / 2 - 2.6), BAND_APEX_Z + BAND_T / 2, 0) * Rectangle(SEAM_W, 2 * SEAM_D * 0.8)
        band -= revolve(g.rotate(axis, -th - 1), axis, 2 * th + 2)
    rp = R - BAND_T / 2 - PAD_T / 2 + 0.6                             # the pad overlaps the band by 0.6: no coplanar faces
    psec = Plane.YZ * Pos(0, zc + rp, 0) * RectangleRounded(PAD_W, PAD_T, 4.2)
    pad = revolve(psec.rotate(axis, -PAD_SPAN_DEG / 2), axis, PAD_SPAN_DEG)
    # Sliders: a sleeve over each band end, along the band's tangent there, and the yoke's stem into it.
    beta = math.degrees(math.atan2(-(ez - zc), ex))                  # tilt of the band's tangent from vertical, right end
    t = (-(ez - zc) / R, 0, ex / R)
    sl = fillet(Box(SLIDER_T, SLIDER_W, SLIDER_LEN).edges(), 3.6)
    off = SLIDER_LEN / 2 - 6
    slider_r = Pos(ex + t[0] * off, 0, ez + t[2] * off) * Rot(0, beta, 0) * sl
    stem_r = Pos(ex + t[0] * 4, 0, ez - 3.5 + t[2] * 4) * Rot(0, beta, 0) * Cylinder(4.5, 14)
    sliders = slider_r + stem_r + mirror(slider_r + stem_r, Plane.YZ)
    return band, pad, sliders, dict(zc=zc, R=R, theta=th)


def wordmark(plane):
    from typeset import Font, set_line, pieces
    contours, w = set_line(Font('ArchivoBlack-Regular.woff'), 'earworm', WORDMARK_SIZE, WORDMARK_TRACK, 0, 0, 'center')
    ys = [p[1] for c in contours for p in c]
    dy = -(min(ys) + max(ys)) / 2                                     # centre the ink box, not the baseline
    solids = None
    for o, hs in pieces(contours):
        ow = Wire(Polyline(*[(x, y + dy, 0) for (x, y) in o], close=True).edges())
        hw = [Wire(Polyline(*[(x, y + dy, 0) for (x, y) in h], close=True).edges()) for h in hs]
        s = extrude(plane * Face(ow, hw), amount=WORDMARK_DEPTH, both=True)   # both ways: glyph faces may point either way
        solids = s if solids is None else solids + s
    return solids, w


def grommet():
    a = math.radians(GROMMET_ANGLE)
    d = (0.0, -math.sin(a), -math.cos(a))                             # toward the front and down, from the cup axis
    x = -(SHELL_FRONT_X + SHELL_DEPTH * 0.45)
    start = (x, (R_CUP - 2.5) * d[1], (R_CUP - 2.5) * d[2])
    # a rubber strain relief, revolved: rounded lip, the hole a little under the worm so its head is gripped
    hl, ro, rh = GROMMET_LEN + 2.5, GROMMET_D / 2, WORM_R * 0.86 - 0.12   # the bore grips: the worm presses into it
    prof = profile([(0, rh), (0, ro), (hl - 2.0, ro), (hl, ro - 1.6), (hl, rh)], [((hl - 2.0, ro), 2.2), ((hl, ro - 1.6), 0.8), ((hl, rh), 0.6)])
    g = revolve(prof, Axis.X, 360)
    pl = Plane(origin=start, x_dir=(1, 0, 0) if abs(d[0]) < 0.9 else (0, 1, 0), z_dir=d)
    g = pl * Rot(0, -90, 0) * g
    tip = tuple(start[i] + d[i] * (GROMMET_LEN + 2.5) for i in range(3))
    return g, dict(start=start, dir=d, mouth=tip)


def plug():
    """A 3.5 mm TRRS plug along +x from the cable's end at x = 0: a gunmetal barrel the worm's tail runs into (the
    strain relief is the tail), a dark collar, the pin."""
    bx0, bx1, br = -PLUG_BARREL_LEN + 1.5, 1.5, PLUG_BARREL_D / 2
    fer = revolve(profile([(bx0, 0), (bx0, br), (bx1, br), (bx1, 0)], [((bx0, br), 1.4), ((bx1, br), 0.7)]), Axis.X, 360)
    r = PLUG_D / 2
    x0, x1 = bx1 + 0.8, bx1 + 0.8 + PLUG_LEN
    pin = revolve(profile([(x0, 0), (x0, r), (x1 - 2.0, r), (x1 - 1.0, r * 0.62), (x1, 0)], [((x1 - 2.0, r), 0.8), ((x1 - 1.0, r * 0.62), 0.4)]), Axis.X, 360)
    rings = Pos(bx1 + 0.4, 0, 0) * Rot(0, 90, 0) * Cylinder(2.3, 0.8)          # the collar between barrel and pin
    for d in PLUG_RINGS:
        xr = x1 - d
        ring = Pos(xr, 0, 0) * Rot(0, 90, 0) * Cylinder(r + 0.02, 0.7)
        rings = rings + ring
    return fer, pin, rings


def printables(shell_r, shell_l):
    """For making one: each shell hollowed to WALL with its front open, and a flat baffle that carries a 50 mm driver
    and takes the pad's lip round its edge. Printed back-face down; the baffle is glued or screwed in."""
    x0, x1, w = SHELL_FRONT_X, SHELL_BACK_X, PRINT_WALL
    cav = revolve(profile([(x0 - 1, 0), (x0 - 1, R_CUP - w), (x1 - w, R_CUP - w), (x1 - w, 0)],
                          [((x1 - w, R_CUP - w), SHELL_ROUND - w)]), Axis.X, 360)
    ledge = revolve(profile([(x0 + BAFFLE_T, R_CUP - w - 1.2), (x0 + BAFFLE_T, R_CUP - w + 0.01), (x0 + BAFFLE_T + 2.0, R_CUP - w + 0.01), (x0 + BAFFLE_T + 2.0, R_CUP - w - 1.2)], []), Axis.X, 360)
    pr = shell_r - cav + ledge
    pl = shell_l - mirror(cav, Plane.YZ) + mirror(ledge, Plane.YZ)
    disc = Pos(x0 + BAFFLE_T / 2, 0, 0) * Rot(0, 90, 0) * Cylinder(R_CUP - w - 0.15, BAFFLE_T)
    disc -= Pos(x0 + BAFFLE_T / 2, 0, 0) * Rot(0, 90, 0) * Cylinder(DRIVER_HOLE_D / 2, BAFFLE_T + 2)
    disc -= Pos(x0 + BAFFLE_T - 0.75, 0, 0) * Rot(0, 90, 0) * Cylinder(DRIVER_FLANGE_D / 2, 1.5)
    for k in range(4):                                                   # pressure-relief holes, damped with felt
        a = math.radians(45 + 90 * k)
        disc -= Pos(x0 + BAFFLE_T / 2, 36 * math.cos(a), 36 * math.sin(a)) * Rot(0, 90, 0) * Cylinder(1.0, BAFFLE_T + 2)
    return {'print-shell-r': pr, 'print-shell-l': pl, 'print-baffle-r': disc, 'print-baffle-l': mirror(disc, Plane.YZ)}


def build():
    """Return {part name: (solid, material name)} and the scene facts scene.py needs."""
    shell, cushion, baffle, yoke = cup_parts()
    band, pad, sliders, arc = band_parts()
    parts = {}
    pr = Plane(origin=(SHELL_BACK_X, 0, 0), x_dir=(0, 1, 0), z_dir=(1, 0, 0))
    pl = Plane(origin=(-SHELL_BACK_X, 0, 0), x_dir=(0, -1, 0), z_dir=(-1, 0, 0))
    wr, wmm = wordmark(pr)
    wl, _ = wordmark(pl)
    g, gfacts = grommet()
    parts['shell-r'] = (shell - wr, 'shell')
    parts['shell-l'] = (mirror(shell, Plane.YZ) - wl - Plane(origin=gfacts['start'], z_dir=gfacts['dir']) * Cylinder(WORM_R + 0.25, 30), 'shell')
    parts['cushion-r'] = (cushion, 'cushion')
    parts['cushion-l'] = (mirror(cushion, Plane.YZ), 'cushion')
    parts['baffle-r'] = (baffle, 'cloth')
    parts['baffle-l'] = (mirror(baffle, Plane.YZ), 'cloth')
    parts['yoke-r'] = (yoke, 'metal')
    parts['yoke-l'] = (mirror(yoke, Plane.YZ), 'metal')
    parts['band'] = (band, 'shell')
    parts['pad'] = (pad, 'cushion')
    parts['sliders'] = (sliders, 'metal')
    parts['grommet'] = (g, 'metal')                                    # a gunmetal eyelet, like the yokes
    barrel, pin, prr = plug()
    parts['plug-barrel'] = (barrel, 'metal')
    parts['plug'] = (pin, 'plug')
    parts['plug-rings'] = (prr, 'plug_rings')
    facts = {'grommet': gfacts, 'band': arc, 'wordmark_width_mm': round(wmm, 1), 'floor_z': FLOOR_Z}
    prints = printables(parts['shell-r'][0], parts['shell-l'][0])
    return parts, facts, prints


def main():
    os.makedirs(os.path.join(OUT, 'stl'), exist_ok=True); os.makedirs(os.path.join(OUT, 'step'), exist_ok=True)
    parts, facts, prints = build()
    manifest = {'parts': {}, 'facts': facts, 'print': {}}
    os.makedirs(os.path.join(OUT, 'stl', 'print'), exist_ok=True)
    for name, solid in prints.items():
        export_stl(solid, os.path.join(OUT, 'stl', 'print', f'{name}.stl'), tolerance=0.02, angular_tolerance=0.1)
        export_step(solid, os.path.join(OUT, 'step', f'{name}.step'))
        manifest['print'][name] = {'volume_cm3': round(solid.volume / 1000, 2), 'valid': solid.is_valid}
    for name, (solid, mat) in parts.items():
        export_stl(solid, os.path.join(OUT, 'stl', f'{name}.stl'), tolerance=0.02, angular_tolerance=0.1)
        export_step(solid, os.path.join(OUT, 'step', f'{name}.step'))
        manifest['parts'][name] = {'material': mat, 'volume_cm3': round(solid.volume / 1000, 2)}
    json.dump(manifest, open(os.path.join(OUT, 'parts.json'), 'w'), indent=1)
    print(json.dumps(manifest, indent=1))


if __name__ == '__main__':
    main()
