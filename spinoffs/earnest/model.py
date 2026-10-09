"""earnest: builds the parts from params.py and exports them for rendering and printing.

    .venv-fab/bin/python spinoffs/earnest/model.py

Writes out/stl/<part>.stl, out/step/<part>.step (for a crate, its top surface: <crate>-top.step) and out/parts.json (part names, materials, volumes, and for each
pack the cups' centres, which scene.py fills with eggs).

The crate is a moulded tray grown into a chassis: a rounded block whose sides lean in, its top a pulp tray's surface
(cups filling their cells on a square pitch, low ridges between them, a cone where four meet). The valves are eggs: a glass envelope blown egg-shaped, the
anode and its glowing heater inside, the getter's silver in the dome, the Bakelite base seated in a socket in the
cup's floor. Two of the eggs are not glass: a white one is the volume knob and a brown one picks the input.
"""
import json, math, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from params import *  # noqa: F401,F403
from build123d import (Axis, Box, Cylinder, Face, Plane, Polyline, Pos, RectangleRounded, Spline, export_step,
                       export_stl, extrude, fillet, loft, make_face, revolve, scale)

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


def crate_size(rows, cols):
    return (cols - 1) * PITCH + CUP_TOP + 2 * MARGIN, (rows - 1) * PITCH + CUP_TOP + 2 * MARGIN


def cup_centres(rows, cols):
    """The cups' centres in plan: x across, y front to back with row 0 at the back (+y)."""
    return (np.arange(cols) - (cols - 1) / 2) * PITCH, ((rows - 1) / 2 - np.arange(rows)) * PITCH


def _smax(a, b, k):
    """A smooth maximum: max(a, b) with a fillet about k wide where they meet."""
    h = np.clip(k - np.abs(a - b), 0, None) / k
    return np.maximum(a, b) + h * h * k / 4


def top_height(X, Y, rows, cols):
    """The top's height above the top plane (mm) at plan points X, Y: the pulp tray's surface."""
    W, D = crate_size(rows, cols)
    cx, cy = cup_centres(rows, cols)
    # each point belongs to its nearest cup; rho is 1 at the middle of its cell's edges, more toward the cell's corners
    ix = np.clip(np.round(X / PITCH + (cols - 1) / 2), 0, cols - 1).astype(int)
    iy = np.clip(np.round((rows - 1) / 2 - Y / PITCH), 0, rows - 1).astype(int)
    u = np.abs(X - cx[ix]) / (PITCH / 2); v = np.abs(Y - cy[iy]) / (PITCH / 2)
    rho = (u ** CUP_PLAN_P + v ** CUP_PLAN_P) ** (1 / CUP_PLAN_P)
    r0 = FLOOR_R / (PITCH / 2)
    t = np.clip((rho - r0) / (1 - r0), 0, None)
    # the cup's wall: a flat floor, a rounded foot, steepest halfway, easing into the ridge, and rising gently past it
    s = np.where(t < 1, 0.5 - 0.5 * np.cos(np.pi * np.clip(t, 0, 1)), 1.0)
    h = -CUP_DEPTH + (CUP_DEPTH + RIDGE_H) * s + 6.0 * np.clip(t - 1, 0, None)
    # a cone at every corner four cups share, dropping away fast past its foot so it never reaches into a cup
    dp = np.full(np.shape(X), 1e9)
    for x in cx[:-1] + PITCH / 2:
        for y in cy[:-1] - PITCH / 2:
            dp = np.minimum(dp, np.hypot(X - x, Y - y))
    tip_r = POST_TIP_D / 2
    q = np.clip((dp - tip_r) / (CONE_FOOT_R - tip_r), 0, None)
    hc = np.where(q <= 1, POST_H - (POST_H - RIDGE_H) * np.clip(q, 0, 1) ** 0.85, RIDGE_H - 60.0 * (q - 1))
    hc = hc - 2.0 * (1 - np.cos(np.pi / 2 * np.clip(dp / tip_r, 0, 1)))              # the tip rounded over
    h = _smax(h, hc, CONE_BLEND)
    # the flange round the edge: e is the distance in from the rounded outline
    qx = np.abs(X) - (W / 2 - EDGE_R); qy = np.abs(Y) - (D / 2 - EDGE_R)
    e = -(np.hypot(np.clip(qx, 0, None), np.clip(qy, 0, None)) + np.minimum(np.maximum(qx, qy), 0) - EDGE_R)
    w = np.clip(e / FLANGE[1], 0, 1); w = w * w * (3 - 2 * w)
    return FLANGE[0] + (h - FLANGE[0]) * w


class Mesh:
    """A triangle mesh (vertices in mm, faces as vertex indices, wound outward), and optionally a CAD face to STEP."""
    def __init__(self, V, F, step=None):
        self.V, self.F, self.step = V, F, step

    @property
    def volume(self):
        a, b, c = (self.V[self.F[:, k]] for k in range(3))
        return float(np.einsum('ij,ij->i', a, np.cross(b, c)).sum() / 6)

    def write_stl(self, path):
        a, b, c = (self.V[self.F[:, k]] for k in range(3))
        n = np.cross(b - a, c - a); n /= np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-12)
        rec = np.zeros(len(self.F), dtype=[('n', '<f4', 3), ('v', '<f4', (3, 3)), ('attr', '<u2')])
        rec['n'] = n; rec['v'] = np.stack([a, b, c], axis=1)
        with open(path, 'wb') as f:
            f.write(b'earnest crate, from model.py'.ljust(80, b' ')); f.write(np.uint32(len(self.F)).tobytes()); f.write(rec.tobytes())


def top_surface(rows, cols, step=SURFACE_STEP):
    """The top as a B-spline face over the crate's outline (fitted to the height field within about 0.05 mm): the
    surface a press tool would be cut to. About half a minute a pack."""
    W, D = crate_size(rows, cols)
    xs = np.linspace(-W / 2, W / 2, int(round(W / step)) + 1); ys = np.linspace(-D / 2, D / 2, int(round(D / step)) + 1)
    X, Y = np.meshgrid(xs, ys); Z = HEIGHT + top_height(X, Y, rows, cols)
    return Face.make_surface_from_array_of_points(
        [[(float(X[j, i]), float(Y[j, i]), float(Z[j, i])) for i in range(len(xs))] for j in range(len(ys))], tol=0.05)


def crate(rows, cols, with_step=True):
    """The crate for rows x cols eggs, centred in plan, standing on z 0; and the cups' floor centres.

    Built as a mesh straight from the height field, MESH_STEP apart, rather than by cutting a block with a B-spline
    surface (OCC took over ten minutes a pack for the cut). A grid over the outline, its corner squares pulled onto
    the rounded corners; the side walls leaning in from the base to the flange; a flat base. The sockets are not
    cut: each valve's base stands in the floor, where a 0.6 mm gap round it would not show."""
    W, D = crate_size(rows, cols)
    lean = HEIGHT * math.tan(math.radians(DRAFT_DEG))
    nx, ny = int(round(W / MESH_STEP)) + 1, int(round(D / MESH_STEP)) + 1
    X, Y = np.meshgrid(np.linspace(-W / 2, W / 2, nx), np.linspace(-D / 2, D / 2, ny))
    # the corner squares onto quarter discs (an elliptical grid mapping: a square's edges to the arc, its inner edges kept)
    ax_, ay_ = np.abs(X) - (W / 2 - EDGE_R), np.abs(Y) - (D / 2 - EDGE_R)
    m = (ax_ > 0) & (ay_ > 0)
    a, b = ax_[m] / EDGE_R, ay_[m] / EDGE_R
    X[m] = np.sign(X[m]) * ((W / 2 - EDGE_R) + EDGE_R * a * np.sqrt(1 - b * b / 2))
    Y[m] = np.sign(Y[m]) * ((D / 2 - EDGE_R) + EDGE_R * b * np.sqrt(1 - a * a / 2))
    Z = HEIGHT + top_height(X, Y, rows, cols)
    V = [np.stack([X, Y, Z], axis=-1).reshape(-1, 3)]
    idx = np.arange(nx * ny).reshape(ny, nx)
    q00, q10, q01, q11 = idx[:-1, :-1], idx[:-1, 1:], idx[1:, :-1], idx[1:, 1:]
    F = [np.stack([q00, q10, q11], -1).reshape(-1, 3), np.stack([q00, q11, q01], -1).reshape(-1, 3)]   # up, CCW
    # the outline, counter-clockwise from above, and the base's outline under it, pushed out by the draft
    ring = np.concatenate([idx[0, :], idx[1:, -1], idx[-1, -2::-1], idx[-2:0:-1, 0]])
    P = V[0][ring]
    cxr = np.clip(P[:, 0], -(W / 2 - EDGE_R), W / 2 - EDGE_R); cyr = np.clip(P[:, 1], -(D / 2 - EDGE_R), D / 2 - EDGE_R)
    out = P[:, :2] - np.stack([cxr, cyr], -1); out /= np.maximum(np.linalg.norm(out, axis=1, keepdims=True), 1e-9)
    base = np.column_stack([P[:, :2] + lean * out, np.zeros(len(P))])
    n0 = nx * ny; k = len(ring); kb = n0 + np.arange(k)
    V.append(base); V.append(np.array([[0.0, 0.0, 0.0]]))
    nxt = np.roll(np.arange(k), -1)
    F.append(np.stack([ring, kb, kb[nxt]], -1)); F.append(np.stack([ring, kb[nxt], ring[nxt]], -1))       # the sides
    F.append(np.stack([np.full(k, n0 + k), kb[nxt], kb], -1))                                               # the base
    mesh = Mesh(np.concatenate(V), np.concatenate(F).astype(np.int64), top_surface(rows, cols) if with_step else None)
    floor_z = HEIGHT - CUP_DEPTH
    cx, cy = cup_centres(rows, cols)
    centres = [(round(float(x), 3), round(float(y), 3), floor_z) for y in cy for x in cx]
    fx, fy = W / 2 + lean - FOOT[0], D / 2 + lean - FOOT[0]
    feet = [Pos(sx * fx, sy * fy, -FOOT[1] / 2 + 0.2) * Cylinder(FOOT[0] / 2, FOOT[1]) for sx in (-1, 1) for sy in (-1, 1)]
    foot = feet[0]
    for f in feet[1:]:
        foot = foot + f
    return mesh, foot, centres, (W, D)


def build():
    parts, facts = {}, {'floor_z': -FOOT[1] + 0.2, 'packs': {}}
    with_step = os.environ.get('EARNEST_STEP', '1') != '0'
    for n, (rows, cols) in PACKS.items():
        body, feet, centres, (W, D) = crate(rows, cols, with_step)
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
        if isinstance(solid, Mesh):
            solid.write_stl(os.path.join(OUT, 'stl', f'{name}.stl'))
            if solid.step is not None:                                  # the top surface alone, for the press tool
                export_step(solid.step, os.path.join(OUT, 'step', f'{name}-top.step'))
        else:
            export_stl(solid, os.path.join(OUT, 'stl', f'{name}.stl'), tolerance=0.05, angular_tolerance=0.2)  # finer than any printer
            export_step(solid, os.path.join(OUT, 'step', f'{name}.step'))
        manifest['parts'][name] = {'material': mat, 'volume_cm3': round(solid.volume / 1000, 2)}
    json.dump(manifest, open(os.path.join(OUT, 'parts.json'), 'w'), indent=1)
    print(json.dumps({k: v for k, v in manifest.items() if k != 'facts'}, indent=1))


if __name__ == '__main__':
    main()
