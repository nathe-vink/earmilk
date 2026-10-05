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


# --- the lay ------------------------------------------------------------------------------------------------------------
# Deliberate, not a heart (critic, in-ear round 1): the earphones at the front, tips toward the camera; the two worms
# leave their burrows, meet behind them and run side by side, back and round to the splitter; the main worm comes
# forward again on the right and the plug points in, toward the earphones.
def catmull(P, n=16):
    P = [np.asarray(p, float) for p in P]
    Q = [2 * P[0] - P[1]] + P + [2 * P[-1] - P[-2]]
    out = [P[0]]
    for j in range(1, len(Q) - 2):
        p0, p1, p2, p3 = Q[j - 1], Q[j], Q[j + 1], Q[j + 2]
        for t in [k / n for k in range(1, n + 1)]:
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    return np.array(out)


def offset(curve, d):
    """The curve moved sideways (in plan) by d mm; positive is to the left of travel."""
    T = np.gradient(curve[:, :2], axis=0); T /= np.linalg.norm(T, axis=1, keepdims=True)
    Nl = np.column_stack([-T[:, 1], T[:, 0]])
    out = curve.copy(); out[:, :2] += Nl * d
    return out


Vb = np.vstack([stl_vertices(STL(n)) for n in BUD_PARTS])
bud_ends = (BUD_LEN + 3.0, 1.0)                       # rests on its tip and on its back
POSE = {'l': lying_pose(Vb, up=(0, 0, 1), axis=(1, 0, 0), heading=-118, at=(-48, -14), ends=bud_ends),
        'r': lying_pose(Vb, up=(0, 0, 1), axis=(1, 0, 0), heading=-94, at=(-22, -30), ends=bud_ends)}
spine = catmull([[-33, 10, 0], [-42, 34, 0], [-31, 62, 0], [-4, 77, 0], [25, 74, 0], [41, 63, 0]])   # the pair's centreline
sp_dir = spine[-1] - spine[-2]; sp_dir /= np.linalg.norm(sp_dir)
heading_split = math.degrees(math.atan2(-sp_dir[1], -sp_dir[0]))     # the splitter's +x points back toward the branches
Vs = stl_vertices(STL('splitter'))
split_at = spine[-1] + sp_dir * (SPLIT_LEN + 9)
SPLIT = lying_pose(Vs, up=(0, 0, 1), axis=(1, 0, 0), heading=heading_split, at=(split_at[0], split_at[1]), ends=(SPLIT_LEN - 1.5, 1.5))

zb, zm = BRANCH_R * 0.94 + 0.05, MAIN_R * 0.94 + 0.05  # centrelines of branch and main where they lie on the floor (flattened 6 %)
GAP = 3.0                                              # half the spacing of the pair: 6 mm centre to centre, 2.3 mm apart


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
    sf = facts['splitter']
    h = to_world(SPLIT, sf['branch_holes'][k]); d = dir_world(SPLIT, sf['branch_dir'])
    outer = add(h, d, 7); outer[2] = zb + 0.3
    return [outer, add(h, d, 3), h, add(h, d, -5)]


def side_of(p):
    """+1 if p is to the left of the spine's direction of travel at its end, -1 if to the right."""
    v = np.asarray(p[:2]) - spine[-1][:2]
    return 1 if (sp_dir[0] * v[1] - sp_dir[1] * v[0]) > 0 else -1


holes = facts['splitter']['branch_holes']
hole_side = [side_of(to_world(SPLIT, h)) for h in holes]
# which bud is on the left of the spine where it starts
t0 = spine[1] - spine[0]; t0 /= np.linalg.norm(t0)
def start_side(pose):
    v = np.asarray(to_world(pose, facts['bud']['worm_mouth'])[:2]) - spine[0][:2]
    return 1 if (t0[0] * v[1] - t0[1] * v[0]) > 0 else -1


def branch(side):
    sgn = start_side(POSE[side])
    run = offset(spine, sgn * GAP)[2:-1:3]             # every third point of the offset spine, dropping the ends
    run[:, 2] = zb
    k = hole_side.index(sgn) if sgn in hole_side else 0
    return leave_bud(side) + run.tolist() + into_splitter(k)


right, left = branch('r'), branch('l')
sf = facts['splitter']
mh = to_world(SPLIT, sf['main_hole']); md = dir_world(SPLIT, sf['main_dir'])
main = [add(mh, md, -5), mh, add(mh, md, 4), [mh[0] + md[0] * 12, mh[1] + md[1] * 12, zm]] + \
       [[74, 30, zm], [80, 6, zm], [71, -17, zm], [54, -33, zm], [38, -41, zm], [24, -43, zm]]
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


def segs(pitch, skip=()):
    """Overlapping segments like a jointed toy snake, each a little different and a little out of line."""
    return {'shape': 'shingle', 'pitch': pitch, 'depth': SEG_DEPTH, 'lip': 0.12, 'curve': 0.6, 'width': 0.05,
            'undercut': 0.4, 'jitter': 0.05, 'depth_jitter': 0.25, 'wobble': 0.035,
            'skip_mm': list(skip), 'skip_fade': 2.0, 'skip_depth': 0.25}


worm_r = {'id': 'worm-r', 'type': 'tube', 'points': right, 'radius': BRANCH_R, 'material': 'worm', 'segments': 32,
          'flatten': 0.06, 'profile_mm': prof(Lr, (c0, c1)), 'rings': segs(SEG_PITCH_BRANCH, [[c0 + 1, c1 - 1]]),
          'attrs': [{'name': 'saddle', 'from': c0 + 1, 'to': c1 - 1, 'fade': 2.5}]}
worm_l = {'id': 'worm-l', 'type': 'tube', 'points': left, 'radius': BRANCH_R, 'material': 'worm', 'segments': 32,
          'flatten': 0.06, 'profile_mm': prof(Ll), 'rings': segs(SEG_PITCH_BRANCH)}
worm_m = {'id': 'worm-main', 'type': 'tube', 'points': main, 'radius': MAIN_R, 'material': 'worm', 'segments': 32,
          'flatten': 0.06, 'profile_mm': [[0, 0.95], [8, 1.0], [-40, 1.0], [-8, 0.9], [0, 0.88]], 'rings': segs(SEG_PITCH_MAIN)}

MAT = {
    'shell': {'preset': 'satin_plastic', 'color': '#2c2a28', 'roughness': 0.34, 'coat': 0.15, 'coat_roughness': 0.3},
    'metal': {'preset': 'metal_satin', 'color': '#7d7974', 'roughness': 0.28},
    'silicone': {'preset': 'silicone', 'color': '#3b3734', 'roughness': 0.6, 'sss': 0.15, 'sheen': 0.2},
    'grille': {'preset': 'fabric', 'color': '#111111'},
    'worm': {'preset': 'lacquer', 'color': '#b97a72', 'top_color': '#6f3c42', 'coat': 0.6, 'coat_roughness': 0.08, 'roughness': 0.34,
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

RIG = {'type': 'sweep', 'color': '#ecebe7', 'dome': 0.12, 'cove_depth': 4.0, 'cove_radius': 2.5,
       'key': {'azimuth': -30, 'elevation': 60, 'size': 0.8, 'power': 0.9},
       'fill': {'azimuth': 50, 'elevation': 25, 'power': 0.12},
       'rim': {'azimuth': 170, 'elevation': 50, 'size': 1.2, 'power': 1.1},
       'lights': [{'azimuth': -135, 'elevation': 20, 'size': [0.16, 1.4], 'distance': 1.6, 'power': 2.8},
                  {'azimuth': 135, 'elevation': 20, 'size': [0.16, 1.4], 'distance': 1.6, 'power': 2.4},
                  {'azimuth': 0, 'elevation': 72, 'size': [0.1, 1.6], 'distance': 1.8, 'power': 1.6},
                  {'azimuth': -20, 'elevation': 35, 'size': 0.03, 'distance': 2.0, 'power': 1.4}]}
shots = {
    'hero': {'size': [1800, 1200], 'samples': 160, 'rig': RIG, 'floor_z': 0, 'exposure': 0.3,
             'camera': {'position': [6, -250, 205], 'target': [6, 22, 0], 'lens': 58}},
    'detail': {'size': [1800, 1200], 'samples': 192, 'rig': RIG, 'floor_z': 0, 'exposure': 0.3,
               'camera': {'position': [40, 36, 62], 'target': [-30, -26, 2], 'lens': 60}},
}
json.dump({'materials': MAT, 'objects': objects, 'shots': shots,
           'notes': {'branch_r_mm': round(Lr), 'branch_l_mm': round(Ll), 'main_mm': round(Lm), 'saddle_from_bud_mm': SADDLE_FROM_BUD}},
          open(os.path.join(HERE, 'shots.json'), 'w'), indent=1)
print(f'shots.json: right branch {Lr:.0f} mm (saddle at {SADDLE_FROM_BUD:.0f}), left {Ll:.0f} mm, main {Lm:.0f} mm drawn')
