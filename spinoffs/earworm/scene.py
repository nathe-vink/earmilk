"""earworm: writes shots.json for studio/pathtrace.py from params.py and the model's out/parts.json.

    .venv-fab/bin/python spinoffs/earworm/model.py && .venv-fab/bin/python spinoffs/earworm/scene.py
    python3 studio/pathtrace.py spinoffs/earworm/shots.json --shot hero

Wired in-ear earphones on a table. The buds lie on their sides, tips toward the camera (poses solved so each rests on
its tip and its back). A worm leaves the back of each bud through its burrow and crawls to the splitter, where the two
become one and go on to the plug. The cable is drawn here as tubes whose segments overlap like a jointed snake toy;
the saddle on the right branch, 120 mm from the bud, is the remote.
"""
import json, math, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'studio'))
from params import *  # noqa: F401,F403
from poses import stl_vertices, lying_pose, to_world, dir_world

M = json.load(open(os.path.join(HERE, 'out', 'parts.json')))
parts, facts = M['parts'], M['facts']
STL = lambda n: os.path.join(HERE, 'out', 'stl', f'{n}.stl')
BUD_PARTS = ('bud-cap', 'bud-shell', 'bud-mesh', 'bud-tip')


def length(P, n=24):
    """Arc length of the Catmull-Rom curve the path tracer draws through P (same construction)."""
    Q = [[2 * P[0][i] - P[1][i] for i in range(3)]] + P + [[2 * P[-1][i] - P[-2][i] for i in range(3)]]
    L, prev = 0.0, P[0]
    for j in range(1, len(Q) - 2):
        p0, p1, p2, p3 = Q[j - 1], Q[j], Q[j + 1], Q[j + 2]
        for t in [k / n for k in range(1, n + 1)]:
            t2, t3 = t * t, t * t * t
            c = [0.5 * ((2 * p1[i]) + (-p0[i] + p2[i]) * t + (2 * p0[i] - 5 * p1[i] + 4 * p2[i] - p3[i]) * t2 + (-p0[i] + 3 * p1[i] - 3 * p2[i] + p3[i]) * t3) for i in range(3)]
            L += math.dist(prev, c); prev = c
    return L


def add(p, d, k):
    return [p[i] + d[i] * k for i in range(3)]


# --- the lay (v4) ------------------------------------------------------------------------------------------------------
# Built for a camera low at the front (in-ear round 3 on the hero: a camera built around one bud side-on, the set behind it).
# The right earphone in front, side-on to the camera, its tip to the left; the left one behind it and further left, turned
# with its tip toward the camera. Each worm leaves its burrow backward, the near one in a hook round to the right; they come
# together behind the pair and run back side by side like a rope settled on the floor (touching here, apart there: two
# paths, not one curve offset), then round to the left to the splitter. The main worm curls back and round to the right,
# and the plug lies at the back of the right third, pointing in.
def catmull(P, n=16):
    P = [np.asarray(p, float) for p in P]
    Q = [2 * P[0] - P[1]] + P + [2 * P[-1] - P[-2]]
    out = [P[0]]
    for j in range(1, len(Q) - 2):
        p0, p1, p2, p3 = Q[j - 1], Q[j], Q[j + 1], Q[j + 2]
        for t in [k / n for k in range(1, n + 1)]:
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    return np.array(out)


def arclen(curve):
    return np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(curve[:, :2], axis=0), axis=1))])


def offset_var(curve, d):
    """The curve moved sideways (in plan) by d[i] mm at each point; positive is to the left of travel."""
    T = np.gradient(curve[:, :2], axis=0); T /= np.linalg.norm(T, axis=1, keepdims=True)
    Nl = np.column_stack([-T[:, 1], T[:, 0]])
    out = curve.copy(); out[:, :2] += Nl * np.asarray(d)[:, None]
    return out


Vb = np.vstack([stl_vertices(STL(n)) for n in BUD_PARTS])
bud_ends = (BUD_LEN + 3.0, 1.0)                       # rests on its tip and on its back
POSE = {'r': lying_pose(Vb, up=(0, 0, 1), axis=(1, 0, 0), heading=180, at=(0, 0), ends=bud_ends),
        'l': lying_pose(Vb, up=(0, 0, 1), axis=(1, 0, 0), heading=245, at=(-42, 33), ends=bud_ends)}
# the pair's centreline, from behind the earphones (where the two worms come together) back and round to the splitter
spine = catmull([[-12, 62, 0], [-5, 92, 0], [5, 121, 0], [2, 150, 0], [-18, 169, 0], [-44, 175, 0]])
sp_dir = spine[-1] - spine[-2]; sp_dir /= np.linalg.norm(sp_dir)
heading_split = math.degrees(math.atan2(-sp_dir[1], -sp_dir[0]))     # the splitter's +x points back toward the branches
Vs = stl_vertices(STL('splitter'))
split_at = spine[-1] + sp_dir * (SPLIT_LEN + 9)
SPLIT = lying_pose(Vs, up=(0, 0, 1), axis=(1, 0, 0), heading=heading_split, at=(split_at[0], split_at[1]), ends=(SPLIT_LEN - 1.5, 1.5))

zb, zm = BRANCH_R * 0.94 + 0.05, MAIN_R * 0.94 + 0.05  # centrelines of branch and main where they lie on the floor (flattened 6 %)


def leave_bud(side):
    """The first points of a branch: inside the bud, the burrow's mouth, out along the bud's axis, down to the floor."""
    b, pose = facts['bud'], POSE[side]
    d = dir_world(pose, b['out_dir'])
    m = to_world(pose, b['worm_mouth'])
    pts = [to_world(pose, b['worm_start']), m, add(m, d, 4)]
    q = add(m, d, 10); q[2] = max(zb + 1.0, q[2] - 2.0)
    pts.append(q)
    return pts


def into_splitter(k):
    """The last points of a branch: along the splitter's axis, rising from the floor to the hole over 16 mm, into the hole."""
    sf = facts['splitter']
    h = to_world(SPLIT, sf['branch_holes'][k]); d = dir_world(SPLIT, sf['branch_dir'])
    far = add(h, d, 16); far[2] = zb + 0.15
    mid = add(h, d, 9); mid[2] = zb + 0.45 * (h[2] - zb)
    near = add(h, d, 3.5); near[2] = h[2] - 0.15
    return [far, mid, near, h, add(h, d, -5)]


def side_of(p):
    """+1 if p is to the left of the spine's direction of travel at its end, -1 if to the right."""
    v = np.asarray(p[:2]) - spine[-1][:2]
    return 1 if (sp_dir[0] * v[1] - sp_dir[1] * v[0]) > 0 else -1


holes = facts['splitter']['branch_holes']
hole_side = [side_of(to_world(SPLIT, h)) for h in holes]
# which bud runs on the left of the spine: the one whose burrow lies further left of its start
t0 = spine[1] - spine[0]; t0 /= np.linalg.norm(t0)
def start_sides():
    c = {}
    for s, pose in POSE.items():
        v = np.asarray(to_world(pose, facts['bud']['worm_mouth'])[:2]) - spine[0][:2]
        c[s] = t0[0] * v[1] - t0[1] * v[0]
    hi = max(c, key=c.get)
    return {s: (1 if s == hi else -1) for s in c}
SIDES = start_sides()

# Each worm's own offset from the centreline, by distance along it: 3 mm either side on average (6 apart, 2.3 between),
# each wandering on its own slow waves, so they touch in places and part by up to 9 mm in others (in-ear round 3: the two
# branches ran exactly parallel). Never closer than touching.
s_sp = arclen(spine)
def wander(sgn):
    a, b, c, e = (1.7, 63.0, 0.3, 0.6) if sgn < 0 else (2.1, 77.0, 1.9, 0.5)
    return sgn * 3.0 + a * np.sin(2 * math.pi * s_sp / b + c) + e * np.sin(2 * math.pi * s_sp / (b / 3.1) + 2.0 * c + 0.7)


def make_offs(wide=None):
    """Both worms' offsets, pushed apart wherever they would overlap; `wide` (s0, s1 along the spine) keeps room for the
    saddle's swelling beside the other worm."""
    d_l, d_r = wander(1), wander(-1)
    need = np.full_like(s_sp, 2 * BRANCH_R + 0.3)
    if wide:
        need[(s_sp >= wide[0]) & (s_sp <= wide[1])] = BRANCH_R * (1 + SADDLE_SWELL) + 0.4
    push = np.clip(need - (d_l - d_r), 0, None) / 2
    return {1: d_l + push, -1: d_r - push}
OFFS = make_offs()


def blend(p0, d0, p1, d1, step=4.0):
    """Points about `step` mm apart on a cubic Hermite from p0 (heading d0) to p1 (heading d1), ends excluded."""
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    L = float(np.linalg.norm(p1 - p0)); n = max(2, int(round(L / step)))
    m0 = np.asarray(d0, float) / np.linalg.norm(d0) * L; m1 = np.asarray(d1, float) / np.linalg.norm(d1) * L
    out = []
    for i in range(1, n):
        u = i / n
        out.append(((2 * u**3 - 3 * u**2 + 1) * p0 + (u**3 - 2 * u**2 + u) * m0 + (-2 * u**3 + 3 * u**2) * p1 + (u**3 - u**2) * m1).tolist())
    return out


def branch(side):
    sgn = SIDES[side]
    run = offset_var(spine, OFFS[sgn])[1:-1:2]        # every other point of this worm's own path, dropping the ends
    run[:, 2] = zb
    k = hole_side.index(sgn) if sgn in hole_side else 0
    lead = leave_bud(side)
    d_out = np.asarray(dir_world(POSE[side], facts['bud']['out_dir']))
    ent = into_splitter(k)
    toward = -np.asarray(dir_world(SPLIT, facts['splitter']['branch_dir']))                # along the splitter, toward it
    run = run[(run - np.asarray(ent[0])) @ toward < -6.0]                                   # the run stops 6 mm short of the entry
    tail = blend(run[-1], run[-1] - run[-2], ent[0], toward)
    out = blend(lead[-1], d_out, run[0], run[1] - run[0], step=3.0)
    out = [[p[0], p[1], max(p[2], zb)] for p in out]   # the Hermite overshot below the floor where the bud's tilt pointed it down
    return lead + out + run.tolist() + tail + ent


right = branch('r')
# where the saddle lies along the spine (it is 120 mm from the bud along the right branch), so the other worm keeps clear of it
_s = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(np.asarray(right), axis=0), axis=1))])
_in = math.dist(right[0], right[1]) + SADDLE_FROM_BUD
_pts = np.asarray(right)[(_s >= _in - SADDLE_LEN / 2 - 6) & (_s <= _in + SADDLE_LEN / 2 + 6)]
_near = [int(np.argmin(np.linalg.norm(spine[:, :2] - q[:2], axis=1))) for q in _pts]
OFFS = make_offs((s_sp[min(_near)], s_sp[max(_near)]))
right, left = branch('r'), branch('l')
sf = facts['splitter']
mh = to_world(SPLIT, sf['main_hole']); md = dir_world(SPLIT, sf['main_dir'])
# the main worm leaves the splitter to the left, curls back and round to the right behind everything, and comes forward on
# the right so the plug lies at the back of the right third, pointing in toward the earphones
main = [add(mh, md, -5), mh, add(mh, md, 4), [mh[0] + md[0] * 12, mh[1] + md[1] * 12, zm]] + \
       [[-84, 184, zm], [-80, 201, zm], [-58, 206, zm], [-30, 198, zm], [-2, 204, zm], [26, 202, zm], [44, 186, zm], [50, 164, zm], [46, 143, zm]]
end, prev = main[-1], main[-2]
yaw = math.degrees(math.atan2(end[1] - prev[1], end[0] - prev[0]))
inside = math.dist(right[0], right[1])                # length inside the bud
Lr, Ll, Lm = length(right), length(left), length(main)
s_c = inside + SADDLE_FROM_BUD
c0, c1 = s_c - SADDLE_LEN / 2, s_c + SADDLE_LEN / 2


def prof(L, saddle=None):
    """Radius factor by distance: a full head in the burrow (no thin neck), slow swellings, the saddle, a tapered tail."""
    pts, d = [], 0.0
    while d <= L:
        k = 1.0 + 0.04 * math.sin(2 * math.pi * d / 47.0) + 0.02 * math.sin(2 * math.pi * d / 19.0 + 1.1)
        if d < inside + 10:
            k = 0.95 + (k - 0.95) * min(1.0, max(0.0, d - inside + 2) / 12)
        if saddle:
            a, b = saddle
            if a - 3 <= d <= b + 3:
                e = min(1.0, (d - (a - 3)) / 4, ((b + 3) - d) / 4)
                k = k + (SADDLE_SWELL - k) * max(0.0, e)
        pts.append([round(d, 2), round(k, 4)]); d += 2.0
    pts.append([round(L, 2), pts[-1][1]])
    return pts


def settle(P, profile):
    """Resample a lying worm every 2 mm and lift each point that lies on the floor by its swelling, so a swollen stretch
    (the saddle above all) rests on the floor and rises above it instead of sinking through it (it swelled into the floor, so
    from any height it read as a colour change, in-ear round 3)."""
    C = catmull(P, 24); s = arclen(C)
    keep = [0]
    for i in range(1, len(C)):
        if s[i] - s[keep[-1]] >= 2.0: keep.append(i)
    if keep[-1] != len(C) - 1: keep.append(len(C) - 1)
    C, s = C[keep], s[keep]
    pd, pk = np.array([p[0] for p in profile]), np.array([p[1] for p in profile])
    kz = np.interp(s, pd, pk)
    on_floor = np.abs(C[:, 2] - zb) < 0.05
    C[on_floor, 2] += np.maximum(kz[on_floor] - 1.0, 0.0) * BRANCH_R * 0.94
    return C.tolist()


def segs(pitch, skip=()):
    """Overlapping segments like a jointed toy snake, each a little different and a little out of line."""
    return {'shape': 'shingle', 'pitch': pitch, 'depth': SEG_DEPTH, 'lip': 0.12, 'curve': 0.6, 'width': 0.05,
            'undercut': 0.4, 'jitter': 0.05, 'depth_jitter': 0.25, 'wobble': 0.035,
            'skip_mm': list(skip), 'skip_fade': 2.0, 'skip_depth': 0.25}


prof_r, prof_l = prof(Lr, (c0, c1)), prof(Ll)
right, left = settle(right, prof_r), settle(left, prof_l)
worm_r = {'id': 'worm-r', 'type': 'tube', 'points': right, 'radius': BRANCH_R, 'material': 'worm', 'segments': 32,
          'flatten': 0.06, 'profile_mm': prof_r, 'rings': segs(SEG_PITCH_BRANCH, [[c0 + 1, c1 - 1]]),
          'attrs': [{'name': 'saddle', 'from': c0 + 1, 'to': c1 - 1, 'fade': 2.5}]}
worm_l = {'id': 'worm-l', 'type': 'tube', 'points': left, 'radius': BRANCH_R, 'material': 'worm', 'segments': 32,
          'flatten': 0.06, 'profile_mm': prof_l, 'rings': segs(SEG_PITCH_BRANCH)}
worm_m = {'id': 'worm-main', 'type': 'tube', 'points': main, 'radius': MAIN_R, 'material': 'worm', 'segments': 32,
          'flatten': 0.06, 'profile_mm': [[0, 0.95], [8, 1.0], [-40, 1.0], [-8, 0.9], [0, 0.88]], 'rings': segs(SEG_PITCH_MAIN)}

MAT = {
    'shell': {'preset': 'satin_plastic', 'color': '#2c2a28', 'roughness': 0.34, 'coat': 0.15, 'coat_roughness': 0.3},
    'metal': {'preset': 'metal_satin', 'color': '#7d7974', 'roughness': 0.28},
    'silicone': {'preset': 'silicone', 'color': '#5f5a55', 'roughness': 0.42, 'sss': 0.6, 'sss_radius': [1.0, 0.85, 0.75], 'sss_scale': 1.6, 'sheen': 0.25},   # smoky translucent tips
    'grille': {'preset': 'fabric', 'color': '#111111'},
    'worm': {'preset': 'lacquer', 'color': '#b97a72', 'top_color': '#6f3c42', 'coat': 0.6, 'coat_roughness': 0.13, 'roughness': 0.34,   # v4: the coat a little softer, so every crest does not take the same hard glint
             'sss': 0.08, 'sss_scale': 0.3, 'attr_color': {'attr': 'saddle', 'color': '#e4c6b0', 'top_color': '#c79a82'}},
    'plug': {'preset': 'metal_polished', 'color': '#dcd8d2'},
    'plug_rings': {'preset': 'gloss_plastic', 'color': '#0e0e0e'},
}
objects = []
for side, pose in POSE.items():
    for n in BUD_PARTS:
        objects.append({'id': f'{n}-{side}', 'type': 'mesh', 'file': f'out/stl/{n}.stl', 'material': parts[n]['material'],
                        'translate': pose['translate'], 'rotate': pose['rotate']})
objects.append({'id': 'splitter', 'type': 'mesh', 'file': 'out/stl/splitter.stl', 'material': 'metal',
                'translate': SPLIT['translate'], 'rotate': SPLIT['rotate']})
for n in ('plug-barrel', 'plug', 'plug-rings'):
    objects.append({'id': n, 'type': 'mesh', 'file': f'out/stl/{n}.stl', 'material': parts[n]['material'],
                    'translate': [end[0], end[1], PLUG_BARREL_D / 2 + 0.05], 'rotate': [0, 0, yaw]})
objects += [worm_r, worm_l, worm_m]

# v4 (in-ear round 3): a key small and hard enough to lay a line down the metal, from behind and above so the shadows fall
# toward the camera; little fill; strips laid for each camera, each along one cap, so the cap carries one unbroken line.
CAM_HERO = {'position': [-10, -319, 91], 'target': [-10, 100, 0], 'lens': 110}
CAM_DETAIL = {'position': [69, -113, 113], 'target': [-24, 14, 4], 'lens': 70}


def cap_centre(side):
    """The middle of a bud's gunmetal back cap, in the scene (mm)."""
    return np.asarray(to_world(POSE[side], [BUD_SPLIT / 2 - 1.2, 0, 0]), float)


def strip_for(side, camera, tilt=40.0, dist=200.0, size=(0.05, 0.6), power=1.0):
    """A strip that lays one unbroken line along a bud's cap for this camera: placed where the cap mirrors it (the normal
    tilted `tilt` degrees from the top toward the camera), its long side turned to lie along the cap. For the studio tracer:
    `at`, `aim`, `roll` (about its own axis; Blender tracks -Z to the aim with Y up), size [short, long] in subject sizes."""
    c = cap_centre(side)
    a = np.asarray(dir_world(POSE[side], [1, 0, 0]), float); a /= np.linalg.norm(a)
    V = np.asarray(camera['position'], float) - c; V /= np.linalg.norm(V)
    Vp = V - (V @ a) * a; Vp[2] = 0.0
    up = np.array([0, 0, 1.0])
    t = math.radians(tilt)
    n = math.cos(t) * up + math.sin(t) * (Vp / max(np.linalg.norm(Vp), 1e-9))   # a normal of the cap, toward the camera
    n -= (n @ a) * a; n /= np.linalg.norm(n)
    L = 2 * (n @ V) * n - V; L /= np.linalg.norm(L)                                # where the cap mirrors the camera from
    Z = L; Y = up - (up @ Z) * Z; Y /= np.linalg.norm(Y); X = np.cross(Y, Z)
    d = a - (a @ Z) * Z
    roll = math.degrees(math.atan2(-(d @ X), d @ Y))                                # turn the strip's long side (Y) onto the cap
    return {'at': (c + L * dist).round(1).tolist(), 'aim': c.round(2).tolist(), 'roll': round(roll, 1),
            'size': list(size), 'power': power}


RIG4 = {'type': 'sweep', 'color': '#ecebe7', 'dome': 0.06, 'cove_depth': 4.0, 'cove_radius': 2.5,
        'key': {'azimuth': 180, 'elevation': 42, 'size': 0.14, 'power': 1.5},
        'fill': {'azimuth': 0, 'elevation': 22, 'power': 0.14},
        'rim': {'azimuth': 140, 'elevation': 28, 'size': 0.6, 'power': 0.4},
        'lights': [strip_for('r', CAM_HERO, tilt=40, size=(0.04, 0.5), power=1.2),
                   {'azimuth': -115, 'elevation': 18, 'size': [0.12, 1.2], 'distance': 1.6, 'power': 0.7},
                   {'azimuth': 115, 'elevation': 18, 'size': [0.12, 1.2], 'distance': 1.6, 'power': 0.6},
                   {'azimuth': -25, 'elevation': 35, 'size': 0.03, 'distance': 2.0, 'power': 0.6}]}
RIG4D = {'type': 'sweep', 'color': '#ecebe7', 'dome': 0.06, 'cove_depth': 4.0, 'cove_radius': 2.5,
         'key': {'azimuth': 160, 'elevation': 45, 'size': 0.14, 'power': 1.5},
         'fill': {'azimuth': 0, 'elevation': 25, 'power': 0.14},
         'rim': {'azimuth': 200, 'elevation': 30, 'size': 0.6, 'power': 0.4},
         'lights': [strip_for('r', CAM_DETAIL, tilt=30, size=(0.04, 0.5), power=1.2),
                    strip_for('l', CAM_DETAIL, tilt=30, size=(0.04, 0.5), power=1.2),
                    {'azimuth': -25, 'elevation': 35, 'size': 0.03, 'distance': 2.0, 'power': 0.5}]}
shots = {
    # in-ear round 3 on the hero: a camera built around one bud. Low (15 degrees) on a long lens: the right earphone side-on in
    # front, from the tip's skirt to the burrow; the left one behind it, tip toward the camera; the worms settled back to the
    # splitter, the saddle swelling in the middle distance, the main worm curling away and the plug at the back. All sharp.
    'hero': {'size': [1800, 1200], 'samples': 160, 'rig': RIG4, 'floor_z': 0, 'exposure': 0.3, 'camera': CAM_HERO},
    # in-ear round 3 on the detail: from higher, so the floor reads as a floor under the earphones; the right one forward and
    # turned, the left one behind it; a strip laid along each cap
    'detail': {'size': [1800, 1200], 'samples': 192, 'rig': RIG4D, 'floor_z': 0, 'exposure': 0.3, 'camera': CAM_DETAIL},
}
json.dump({'materials': MAT, 'objects': objects, 'shots': shots,
           'notes': {'branch_r_mm': round(Lr), 'branch_l_mm': round(Ll), 'main_mm': round(Lm), 'saddle_from_bud_mm': SADDLE_FROM_BUD}},
          open(os.path.join(HERE, 'shots.json'), 'w'), indent=1)
print(f'shots.json: right branch {Lr:.0f} mm (saddle at {SADDLE_FROM_BUD:.0f}), left {Ll:.0f} mm, main {Lm:.0f} mm drawn')
