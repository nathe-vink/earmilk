"""earnest: builds the parts from params.py and exports them for rendering and printing.

    .venv-fab/bin/python spinoffs/earnest/model.py

Writes out/stl/<part>.stl, out/step/<part>.step and out/parts.json (part names, materials, volumes, and for each
pack the cups' centres, which scene.py fills with eggs).

The crate is a moulded tray grown into a chassis: a rounded block whose sides lean in, its top pressed into cups on a
square pitch with a cone standing between every four. The valves are eggs: a glass envelope blown egg-shaped, the
anode and its glowing heater inside, the getter's silver in the dome, the Bakelite base seated in a socket in the
cup's floor. Two of the eggs are not glass: a white one is the volume knob and a brown one picks the input.
"""
import json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from params import *  # noqa: F401,F403
from build123d import (Axis, Box, Circle, Cone, Cylinder, Plane, Polyline, Pos, RectangleRounded, Spline, export_step,
                       export_stl, fillet, loft, make_face, revolve, scale)

OUT = os.path.join(HERE, 'out')


def egg_profile(L, D, k, n=48):
    """(r, z) from the tip (z 0) to the dome (z L): an egg narrower at its tip end by k, widest D."""
    pts = []
    for i in range(n + 1):
        t = math.pi * i / n
        pts.append((math.sin(t) * (1 - k * math.cos(t)), L / 2 * (1 - math.cos(t))))
    s = (D / 2) / max(r for r, _ in pts)
    return [(r * s, z) for r, z in pts]


def egg(L=EGG_L, D=EGG_D, k=EGG_K):
    """A solid egg standing on its tip at the origin, its axis along z."""
    prof = egg_profile(L, D, k)
    inner = [(r, 0, z) for r, z in prof[1:-1]]
    curve = Spline((0, 0, 0), *inner, (0, 0, L), tangents=((1, 0, 0), (-1, 0, 0)))
    face = make_face([curve, Polyline((0, 0, L), (0, 0, 0))])
    return revolve(face, Axis.Z, 360)


def valve():
    """The egg valve's parts in its own frame, tip at the origin: glass, getter, anode, micas, heater, base."""
    outer = egg()
    inner = Pos(0, 0, GLASS_T) * egg(EGG_L - 2 * GLASS_T, EGG_D - 2 * GLASS_T)
    glass = outer - inner
    # the getter: a mirror on the inside of the dome, a hair inside the glass
    film_o = Pos(0, 0, GLASS_T + 0.15) * egg(EGG_L - 2 * GLASS_T - 0.3, EGG_D - 2 * GLASS_T - 0.3)
    film_i = Pos(0, 0, GLASS_T + 0.55) * egg(EGG_L - 2 * GLASS_T - 1.1, EGG_D - 2 * GLASS_T - 1.1)
    zg = GETTER_FROM * EGG_L
    getter = (film_o - film_i) & (Pos(0, 0, zg + EGG_L) * Box(EGG_D * 2, EGG_D * 2, 2 * EGG_L))
    # the anode: a box tube open top and bottom, so the heater's glow shows through it
    pw, pd, ph = PLATE
    zc = 0.47 * EGG_L
    anode = Pos(0, 0, zc) * Box(pw, pd, ph) - Pos(0, 0, zc) * Box(pw - 2.4, pd - 2.4, ph + 2)
    micas = (Pos(0, 0, zc + ph / 2 + 2.0) * Cylinder(15.5, 0.8)) + (Pos(0, 0, zc - ph / 2 - 2.0) * Cylinder(13.0, 0.8))
    heater = (Pos(-3.2, 0, zc) * Cylinder(0.9, ph - 4)) + (Pos(3.2, 0, zc) * Cylinder(0.9, ph - 4))
    # the base: a Bakelite collar round the tip, its lower half in the socket
    base = Pos(0, 0, BASE_H / 2 - BASE_SINK + 1.0) * Cylinder(BASE_D / 2, BASE_H)
    base = fillet(base.edges().group_by(Axis.Z)[-1], 2.0)
    return {'glass': glass, 'getter': getter, 'anode': anode, 'mica': micas, 'heater': heater, 'base': base}


def crate(rows, cols):
    """The crate for rows x cols eggs, centred in plan, standing on z 0; and the cups' floor centres."""
    W = (cols - 1) * PITCH + CUP_TOP + 2 * MARGIN
    D = (rows - 1) * PITCH + CUP_TOP + 2 * MARGIN
    lean = HEIGHT * math.tan(math.radians(DRAFT_DEG))
    body = loft([Plane.XY * RectangleRounded(W + 2 * lean, D + 2 * lean, EDGE_R + lean),
                 Plane.XY.offset(HEIGHT) * RectangleRounded(W, D, EDGE_R)])
    floor_z = HEIGHT - CUP_DEPTH
    centres = []
    for r in range(rows):
        for c in range(cols):
            x = (c - (cols - 1) / 2) * PITCH; y = ((rows - 1) / 2 - r) * PITCH      # row 0 at the back (+y)
            centres.append((round(x, 3), round(y, 3), floor_z))
            cup = loft([Plane.XY.offset(HEIGHT + 2) * Pos(x, y) * RectangleRounded(CUP_TOP + 4, CUP_TOP + 4, CUP_TOP_R + 2),
                        Plane.XY.offset(HEIGHT) * Pos(x, y) * RectangleRounded(CUP_TOP, CUP_TOP, CUP_TOP_R),
                        Plane.XY.offset(floor_z) * Pos(x, y) * Circle(CUP_FLOOR_D / 2)])
            body = body - cup
            body = body - Pos(x, y, floor_z - BASE_SINK / 2) * Cylinder(BASE_D / 2 + 0.6, BASE_SINK + 0.2)
    for r in range(rows - 1):
        for c in range(cols - 1):
            x = (c + 0.5 - (cols - 1) / 2) * PITCH; y = ((rows - 1) / 2 - r - 0.5) * PITCH
            body = body + Pos(x, y, HEIGHT - 3 + (POST_H + 3) / 2) * Cone(POST_D[0] / 2, POST_D[1] / 2, POST_H + 3)
    # the flange round the top edge, where a carton's lid would close on it
    rim = (Plane.XY.offset(HEIGHT - 0.5) * RectangleRounded(W, D, EDGE_R)).face()
    from build123d import extrude, offset
    ring = extrude(rim, RIM[1] + 0.5) - extrude(offset(rim, -RIM[0]), RIM[1] + 0.5)
    body = body + ring
    try:
        body = fillet(body.edges().filter_by_position(Axis.Z, HEIGHT - 0.5, HEIGHT + POST_H + 0.5), 2.2)
    except Exception as e:                                        # the cups' rims are soft on a moulded tray; skip if OCC balks
        print('crate fillet skipped:', type(e).__name__)
    fx, fy = W / 2 + lean - FOOT[0], D / 2 + lean - FOOT[0]
    feet = [Pos(sx * fx, sy * fy, -FOOT[1] / 2 + 0.2) * Cylinder(FOOT[0] / 2, FOOT[1]) for sx in (-1, 1) for sy in (-1, 1)]
    foot = feet[0]
    for f in feet[1:]:
        foot = foot + f
    return body, foot, centres, (W, D)


def build():
    parts, facts = {}, {'floor_z': -FOOT[1] + 0.2, 'packs': {}}
    for n, (rows, cols) in PACKS.items():
        body, feet, centres, (W, D) = crate(rows, cols)
        parts[f'crate-{n}'] = (body, 'pulp')
        parts[f'feet-{n}'] = (feet, 'rubber')
        facts['packs'][str(n)] = {'rows': rows, 'cols': cols, 'cups': centres, 'size': [round(W, 1), round(D, 1), HEIGHT]}
    for name, solid in valve().items():
        parts[f'valve-{name}'] = (solid, {'glass': 'glass', 'getter': 'getter', 'anode': 'anode', 'mica': 'mica',
                                          'heater': 'heater', 'base': 'bakelite'}[name])
    knob = scale(egg(), by=KNOB_SCALE)
    parts['knob-white'] = (knob, 'egg_white')
    parts['knob-brown'] = (knob, 'egg_brown')
    facts['valve_tip_below_floor'] = 1.0          # the valve's tip sits this far under its cup's floor (in the socket)
    facts['knob_tip_above_floor'] = 3.0
    return parts, facts


def main():
    os.makedirs(os.path.join(OUT, 'stl'), exist_ok=True); os.makedirs(os.path.join(OUT, 'step'), exist_ok=True)
    parts, facts = build()
    manifest = {'parts': {}, 'facts': facts}
    for name, (solid, mat) in parts.items():
        export_stl(solid, os.path.join(OUT, 'stl', f'{name}.stl'), tolerance=0.05, angular_tolerance=0.2)   # finer than any printer
        export_step(solid, os.path.join(OUT, 'step', f'{name}.step'))
        manifest['parts'][name] = {'material': mat, 'volume_cm3': round(solid.volume / 1000, 2)}
    json.dump(manifest, open(os.path.join(OUT, 'parts.json'), 'w'), indent=1)
    print(json.dumps({k: v for k, v in manifest.items() if k != 'facts'}, indent=1))


if __name__ == '__main__':
    main()
