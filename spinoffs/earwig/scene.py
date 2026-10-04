"""earwig: writes shots.json for studio/pathtrace.py from params.py and the model's out/parts.json.

    .venv-fab/bin/python spinoffs/earwig/model.py && python3 spinoffs/earwig/scene.py
    python3 studio/pathtrace.py spinoffs/earwig/shots.json --shot hero

The case stands on the floor wearing its wig (hair.py grows it at render time). The buds lie in front of it on their
outer sides, the way buds lie on a table: each pose is solved here so the bud rests on its body and its pincer tips.
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


def lying_pose(side, heading, at, roll=0.0):
    """A bud on its outer side (the inner side, with the nozzle, faces up), its stem pointing along `heading` degrees on
    the floor, tilted so it rests on its body and its pincer tips; returns translate and rotate for the scene."""
    V = np.vstack([stl_vertices(f'{p}-{side}') for p in ('bud', 'pincers', 'tip')])
    up_local = np.array([1.0 if side == 'r' else -1.0, 0, 0])            # the inner side faces up
    zg = np.array([math.cos(math.radians(heading)), math.sin(math.radians(heading)), 0])
    xg = np.array([0, 0, 1.0])
    yg = np.cross(zg, xg)
    # columns: where local x, y, z go (for the left bud local x is the outer side, so flip it)
    R0 = np.column_stack([xg * up_local[0], yg * (1 if side == 'r' else -1) * up_local[0], zg])
    R0 = rot(zg, roll) @ R0
    body = V[:, 2] > -9; far = V[:, 2] < -24
    lo, hi = -40.0, 40.0
    for _ in range(60):                                                  # tilt about the floor axis across the stem
        t = (lo + hi) / 2
        R = rot(yg, t) @ R0
        W = V @ R.T
        if W[body, 2].min() < W[far, 2].min():                           # the far end is still in the air: tip it down
            lo = t
        else:
            hi = t
    R = rot(yg, (lo + hi) / 2) @ R0
    W = V @ R.T
    tr = [at[0], at[1], -W[:, 2].min() + 0.02]
    return {'translate': tr, 'rotate': euler_xyz(R)}


MAT = {
    'shell': {'preset': 'lacquer', 'color': '#5b2e1a', 'roughness': 0.22, 'coat': 0.9, 'coat_roughness': 0.05},
    'pincer': {'preset': 'lacquer', 'color': '#7f3c18', 'roughness': 0.22, 'coat': 0.9, 'coat_roughness': 0.05},
    'silicone': {'preset': 'silicone', 'color': '#3a2219', 'roughness': 0.42},
    'led': {'preset': 'emissive', 'color': '#ffd9a8', 'emission': 3.0},
    'hair': {'preset': 'hair', 'melanin': 0.66, 'redness': 0.45, 'roughness': 0.26, 'radial_roughness': 0.32, 'coat': 0.08},
}
case = facts['case']
objects = [{'id': n, 'type': 'mesh', 'file': f'out/stl/{n}.stl', 'material': parts[n]['material']} for n in ('case-base', 'case-lid', 'case-led')]
objects.append({'id': 'wig', 'type': 'python', 'file': 'hair.py',
                'args': {'w': case['w'], 'd': case['d'], 'h': case['h'], 'r': case['r'], 'split_z': case['split_z'],
                         'count': HAIR_COUNT, 'radius': HAIR_RADIUS, 'volume': list(HAIR_VOLUME), 'cut_below': HAIR_CUT_BELOW_SPLIT}})
poses = {'r': lying_pose('r', heading=160, at=(-24, -40)), 'l': lying_pose('l', heading=204, at=(14, -80))}
for side, pose in poses.items():
    for p in ('bud', 'pincers', 'tip'):
        objects.append({'id': f'{p}-{side}', 'type': 'mesh', 'file': f'out/stl/{p}-{side}.stl', 'material': parts[f'{p}-{side}']['material'], **pose})

shots = {
    'hero': {'size': [1800, 1200], 'samples': 160,
             'rig': {'type': 'sweep', 'color': '#eadfd2', 'key': {'azimuth': -48, 'elevation': 52}, 'rim': {'azimuth': 155, 'elevation': 32, 'power': 1.4}},
             'camera': {'position': [-160, -395, 318], 'target': [8, -34, 16], 'lens': 100},
             'floor_z': 0},
    'detail': {'size': [1800, 1200], 'samples': 192,
               'rig': {'type': 'sweep', 'color': '#eadfd2', 'key': {'azimuth': -40, 'elevation': 45}, 'rim': {'azimuth': 160, 'elevation': 25}},
               'camera': {'position': [140, -200, 40], 'target': [30, -72, 6], 'lens': 100, 'fstop': 5.6, 'focus': [42, -68, 4]},
               'floor_z': 0},
}
json.dump({'materials': MAT, 'objects': objects, 'shots': shots}, open(os.path.join(HERE, 'shots.json'), 'w'), indent=1)
print('shots.json written; bud poses', json.dumps(poses))
