"""earwig: writes shots.json for studio/pathtrace.py from params.py and the model's out/parts.json.

    .venv-fab/bin/python spinoffs/earwig/model.py && python3 spinoffs/earwig/scene.py
    python3 studio/pathtrace.py spinoffs/earwig/shots.json --shot hero

The case stands on the floor, its chestnut lid split like an earwig's wing covers. The buds lie in front of it on their
outer sides, the way buds lie on a table, and each tail, a flexible run of overlapping plates since 2026-10-06, leaves
its collar and drapes on the floor to the forceps; the path tracer draws the tails plate by plate along the paths laid here.
"""
import json, math, os, struct, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from params import *  # noqa: F401,F403

M = json.load(open(os.path.join(HERE, 'out', 'parts.json')))
facts, parts = M['facts'], M['parts']


def stl_vertices(name):
    b = open(os.path.join(HERE, 'out', 'stl', f'{name}.stl'), 'rb').read()
    n = struct.unpack('<I', b[80:84])[0]
    a = np.frombuffer(b[84:84 + 50 * n], dtype=np.dtype([('n', '<f4', 3), ('v', '<f4', (3, 3)), ('a', '<u2')]))
    return a['v'].reshape(-1, 3).astype(float)


def euler_xyz(R):
    """Blender's XYZ Euler (R = Rz Ry Rx), degrees."""
    b = math.asin(max(-1, min(1, -R[2, 0])))
    return [math.degrees(math.atan2(R[2, 1], R[2, 2])), math.degrees(b), math.degrees(math.atan2(R[1, 0], R[0, 0]))]


def rot(axis, deg):
    a = np.asarray(axis, float); a /= np.linalg.norm(a); t = math.radians(deg)
    K = np.array([[0, -a[2], a[1]], [a[2], 0, -a[0]], [-a[1], a[0], 0]])
    return np.eye(3) + math.sin(t) * K + (1 - math.cos(t)) * K @ K


def euler_matrix(e):
    """The rotation Blender applies for an XYZ Euler in degrees (R = Rz Ry Rx)."""
    a, b, c = [math.radians(v) for v in e]
    Rx = np.array([[1, 0, 0], [0, math.cos(a), -math.sin(a)], [0, math.sin(a), math.cos(a)]])
    Ry = np.array([[math.cos(b), 0, math.sin(b)], [0, 1, 0], [-math.sin(b), 0, math.cos(b)]])
    Rz = np.array([[math.cos(c), -math.sin(c), 0], [math.sin(c), math.cos(c), 0], [0, 0, 1]])
    return Rz @ Ry @ Rx


def lying_pose(side, heading, at, tilt=5.0):
    """A bud on its outer side (the inner side, with the nozzle, faces up), its head toward `heading` degrees on the floor
    and its tail's root the other way, the head end raised `tilt` degrees: since 2026-10-06 the tail hangs loose, so the bud
    rests on its body alone. Returns translate, rotate and the matrix Blender will apply."""
    V = np.vstack([stl_vertices(f'{p}-{side}') for p in ('bud', 'inner', 'tip', 'collar')])
    up_local = np.array([1.0 if side == 'r' else -1.0, 0, 0])            # the inner side faces up
    zg = np.array([math.cos(math.radians(heading)), math.sin(math.radians(heading)), 0])
    xg = np.array([0, 0, 1.0])
    yg = np.cross(zg, xg)
    R0 = np.column_stack([xg * up_local[0], yg * (1 if side == 'r' else -1) * up_local[0], zg])
    best = None
    for t in (tilt, -tilt):                                              # the sign that raises the head end
        R = euler_matrix(euler_xyz(rot(yg, t) @ R0))
        W = V @ R.T
        head = W[V[:, 2] > 6, 2].mean(); root = W[V[:, 2] < -11, 2].mean()
        if best is None or head - root > best[0]:
            best = (head - root, R)
    R = best[1]
    W = V @ R.T
    tr = [at[0], at[1], -W[:, 2].min() + 0.02]
    return {'translate': tr, 'rotate': euler_xyz(R), 'matrix': R}


def tail_path(pose, side, curl, wobble=0.0, step=1.5):
    """The tail's centreline: straight out of the collar for 3 mm, down to the floor within about 10 mm, then lying on it,
    its heading turning by `curl` degrees over the length (a slow S if `wobble`), so the two tails are never copies."""
    T = facts['tail']; R = pose['matrix']; t0 = np.array(pose['translate'])
    root = R @ np.array(T['root_r' if side == 'r' else 'root_l']) + t0
    d = R @ np.array(T['dir']); h0 = math.atan2(d[1], d[0])
    L = T['len']; n = int(L / step)
    r = lambda s: T['r0'] + (T['r1'] - T['r0']) * (s / L)
    pts, p = [], root[:2].copy()
    for i in range(n + 1):
        s = i * step
        u = s / L
        h = h0 + math.radians(curl) * (3 * u * u - 2 * u ** 3) + math.radians(wobble) * math.sin(2 * math.pi * u)
        lie = r(s) * 0.94 + 0.05                                         # resting on the floor, a little flattened
        z = lie + (root[2] - lie) * max(0.0, 1 - s / 10.0) ** 2 if s > 3 else root[2] + d[2] * s
        pts.append([float(p[0]), float(p[1]), float(z)])
        p = p + step * np.array([math.cos(h), math.sin(h)])
    end = np.array(pts[-1]); tan = end - np.array(pts[-2]); tan[2] = 0; tan /= np.linalg.norm(tan)
    return pts, end, tan


FV = stl_vertices('forceps')


def forceps_pose(end, tan, droop=7.0):
    """The forceps at the tail's end: local -z (the arms) along the tail's last heading, local x up, nosed down `droop` degrees
    so the tips and the knob both touch the floor."""
    zl = -tan                                                            # local +z points back up the tail
    xl = np.array([0, 0, 1.0]); yl = np.cross(zl, xl)
    R = rot(yl, droop) @ np.column_stack([xl, yl, zl])
    R = euler_matrix(euler_xyz(R))
    kz = facts['forceps']['knob'][2]
    W = FV @ R.T
    c = end + tan * kz
    return {'translate': [float(c[0]), float(c[1]), float(-W[:, 2].min() + 0.02)], 'rotate': euler_xyz(R)}


def tail_tube(key, pts):
    T = facts['tail']
    return {'id': f'tail-{key}', 'type': 'tube', 'points': pts, 'radius': T['r0'], 'material': 'tail', 'segments': 32,
            'flatten': 0.05, 'profile_mm': [[0, 1.0], [-1, T['r1'] / T['r0']]],
            'rings': {'shape': 'shingle', 'pitch': T['pitch'], 'depth': T['flare'], 'lip': 0.1, 'curve': 0.6, 'width': 0.05,
                      'undercut': 0.45, 'jitter': 0.02, 'depth_jitter': 0.06, 'wobble': 0.01}}


# 2026-10-06 (the owner): no wig; the lid in the buds' chestnut lacquer, split like folded wing covers, on a cream base; the
# stiff stems become flexible tails of overlapping plates that hang loose, in the same lacquer, ending in the forceps
MAT = {
    'shell': {'preset': 'lacquer', 'color': '#5a2f1b', 'roughness': 0.28, 'coat': 0.8, 'coat_roughness': 0.05,
              'bump': {'type': 'noise', 'scale': 0.6, 'strength': 0.04}},            # a faint orange peel
    'tail': {'preset': 'lacquer', 'color': '#5a2f1b', 'top_color': '#4a2614', 'roughness': 0.3, 'coat': 0.75, 'coat_roughness': 0.07},
    'pincer': {'preset': 'lacquer', 'color': '#5a2f1b', 'roughness': 0.3, 'coat': 0.7, 'coat_roughness': 0.06,
               'bump': {'type': 'noise', 'scale': 0.6, 'strength': 0.04}},
    'satin': {'preset': 'satin_plastic', 'color': '#7d4a2e', 'roughness': 0.42, 'coat': 0.15, 'coat_roughness': 0.3},
    'case': {'preset': 'satin_plastic', 'color': '#ece4d6', 'roughness': 0.3, 'coat': 0.45, 'coat_roughness': 0.07},
    'grille': {'preset': 'fabric', 'color': '#5a5550'},                              # mid grey: a dark hole read as a pupil
    'sensor': {'preset': 'gloss_plastic', 'color': '#1c1512', 'roughness': 0.06},     # the wear sensor's window
    'silicone': {'preset': 'silicone', 'color': '#9a8e82', 'roughness': 0.42, 'sss': 0.6, 'sss_radius': [1.0, 0.8, 0.65], 'sss_scale': 1.6, 'sheen': 0.25},
    'led': {'preset': 'emissive', 'color': '#ffd9a8', 'emission': 3.0},
}
case = facts['case']
objects = [{'id': n, 'type': 'mesh', 'file': f'out/stl/{n}.stl', 'material': parts[n]['material']}
           for n in ('case-base', 'case-lid', 'case-led')]
R_HEADING, R_AT = 40, (4, -54)                     # the bud the close-up looks at
# the hero's buds in front of the case and to its right, each tail draped back toward the group, curling its own way;
# the close-up has its own right bud
LAYOUT = {'r': (340, (42, -64), 70, 8), 'l': (300, (78, -26), -55, -6), 'r-d': (R_HEADING, R_AT, -85, 6)}
BUD = ('bud', 'inner', 'grille', 'collar', 'sensor', 'tip')
for key, (hd, at, curl, wob) in LAYOUT.items():
    side = key[0]
    pose = lying_pose(side, hd, at)
    for p in BUD:
        objects.append({'id': f'{p}-{key}', 'type': 'mesh', 'file': f'out/stl/{p}-{side}.stl', 'material': parts[f'{p}-{side}']['material'],
                        'translate': pose['translate'], 'rotate': pose['rotate']})
    pts, end, tan = tail_path(pose, side, curl, wob)
    objects.append(tail_tube(key, pts))
    objects.append({'id': f'forceps-{key}', 'type': 'mesh', 'file': 'out/stl/forceps.stl', 'material': 'pincer', **forceps_pose(end, tan)})
HERO_SET = [f'{p}-{k}' for p in BUD + ('tail', 'forceps') for k in ('r', 'l')]
DETAIL_SET = [f'{p}-r-d' for p in BUD + ('tail', 'forceps')]

# v7 light (2026-10-06): the v6 key, low and just right of the camera so the cream base is the brightest thing in frame,
# a white card low in front to lift the chestnut lid's face, and pins for a glint on the lid's corner and on each bud
RIG7 = {'type': 'sweep', 'color': '#d3cabc', 'wall_color': '#8f8273', 'wall_range': [0.2, 1.3], 'dome': 0.06,
        'key': {'azimuth': 18, 'elevation': 34, 'size': 1.0, 'power': 1.3},
        'fill': {'azimuth': 45, 'elevation': 25, 'power': 0.08},
        'rim': {'azimuth': 180, 'elevation': 12, 'power': 1.2, 'size': 0.8},
        'lights': [{'azimuth': -72, 'elevation': 18, 'size': [0.16, 1.5], 'distance': 1.5, 'power': 1.6},
                   {'azimuth': 150, 'elevation': 24, 'size': [0.14, 1.4], 'distance': 1.6, 'power': 2.4},
                   {'azimuth': 0, 'elevation': 6, 'size': [1.4, 0.35], 'distance': 2.4, 'power': 0.35},
                   {'azimuth': -30, 'elevation': 35, 'size': 0.03, 'distance': 2.0, 'power': 0.8},
                   {'azimuth': -55, 'elevation': 48, 'size': 0.025, 'distance': 2.2, 'power': 0.5}],
        'cards': [{'azimuth': 80, 'elevation': 12, 'distance': 1.5, 'size': [1.2, 1.2]}]}
shots = {
    'hero': {'size': [1800, 1200], 'samples': 160, 'rig': RIG7, 'exposure': 0.15,
             'camera': {'position': [-176, -510, 312], 'target': [30, -30, 14], 'lens': 100},
             'hide': DETAIL_SET, 'floor_z': 0},
    # from above, pulled back about 12 % with the group lower in frame (the case's top sat under 5 % from the edge)
    'detail': {'size': [1800, 1200], 'samples': 192,
               'rig': {**{k: v for k, v in RIG7.items() if k not in ('wall_color', 'wall_range')},
                       'key': {'azimuth': -45, 'elevation': 48, 'size': 0.8, 'power': 1.4},
                       'rim': {**RIG7['rim'], 'power': 0.6},
                       'lights': [RIG7['lights'][0], {**RIG7['lights'][1], 'power': 0.8}] + RIG7['lights'][2:]},
               'camera': {'position': [92, -252, 196], 'target': [0, -24, 14], 'lens': 60},
               'hide': HERO_SET, 'floor_z': 0},
}
json.dump({'materials': MAT, 'objects': objects, 'shots': shots}, open(os.path.join(HERE, 'shots.json'), 'w'), indent=1)
print('shots.json written:', len(objects), 'objects')
