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
    V = np.vstack([stl_vertices(f'{p}-{side}') for p in ('bud', 'inner', 'pincers', 'tip')])
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


# 2026-10-04, a little less grotesque (the owner): a cream case, a sleek side-parted bob, buds in gloss chestnut with a
# satin inner half and taupe tips (a cream inner half round a dark tip read as an eyeball)
MAT = {
    'shell': {'preset': 'lacquer', 'color': '#5a2f1b', 'roughness': 0.3, 'coat': 0.7, 'coat_roughness': 0.06,
              'bump': {'type': 'noise', 'scale': 0.6, 'strength': 0.04}},            # a faint orange peel
    'pincer': {'preset': 'lacquer', 'color': '#5a2f1b', 'roughness': 0.3, 'coat': 0.7, 'coat_roughness': 0.06,
               'bump': {'type': 'noise', 'scale': 0.6, 'strength': 0.04}},           # the shells' own lacquer (critic, softer round 1)
    'satin': {'preset': 'satin_plastic', 'color': '#7d4a2e', 'roughness': 0.42, 'coat': 0.15, 'coat_roughness': 0.3},
    'case': {'preset': 'satin_plastic', 'color': '#ece4d6', 'roughness': 0.3, 'coat': 0.45, 'coat_roughness': 0.07},
    'cap': {'preset': 'matte_plastic', 'color': '#3b2416', 'roughness': 0.8},       # the lid under the hair, like a wig's cap
    'grille': {'preset': 'fabric', 'color': '#5a5550'},                              # mid grey: a dark hole read as a pupil
    'silicone': {'preset': 'silicone', 'color': '#8f8173', 'roughness': 0.6, 'sss': 0.3, 'sheen': 0.2},
    'led': {'preset': 'emissive', 'color': '#ffd9a8', 'emission': 3.0},
    'hair': {'preset': 'hair', 'melanin': 0.55, 'redness': 0.42, 'roughness': 0.2, 'radial_roughness': 0.3, 'coat': 0.12},
}
case = facts['case']
objects = [{'id': n, 'type': 'mesh', 'file': f'out/stl/{n}.stl', 'material': 'cap' if n == 'case-lid' else parts[n]['material']}
           for n in ('case-base', 'case-lid', 'case-led')]
objects.append({'id': 'wig', 'type': 'python', 'file': 'hair.py',
                'args': {'w': case['w'], 'd': case['d'], 'h': case['h'], 'r': case['r'], 'split_z': case['split_z'],
                         'count': HAIR_COUNT, 'radius': HAIR_RADIUS, 'volume': [0.3, 2.4], 'cut_below': 0.7,
                         'clump': 0.8, 'clump_turn': 2.5, 'flyaway': 0.0, 'cut_jitter': 0.12, 'part_cross': 0.0,
                         'part_y': 5.0, 'frizz': 0.04, 'rise': 1.2, 'tuck': 0.55, 'part_gap': 0.35, 'part_flat': 2.5}})
R_HEADING, R_AT = 40, (4, -54)                     # the bud the close-up looks at
poses = {'r': lying_pose('r', heading=R_HEADING, at=R_AT), 'l': lying_pose('l', heading=198, at=(50, -44))}
for side, pose in poses.items():
    for p in ('bud', 'inner', 'grille', 'pincers', 'tip'):
        objects.append({'id': f'{p}-{side}', 'type': 'mesh', 'file': f'out/stl/{p}-{side}.stl', 'material': parts[f'{p}-{side}']['material'], **pose})

RIG = {'type': 'sweep', 'color': '#e8ded1', 'wall_color': '#a39383', 'wall_range': [0.2, 1.9], 'dome': 0.2,
       'key': {'azimuth': -40, 'elevation': 50, 'power': 0.7},
       'fill': {'azimuth': 45, 'elevation': 25, 'power': 0.35},
       'rim': {'azimuth': 180, 'elevation': 12, 'power': 1.6, 'size': 1.2},
       'lights': [{'azimuth': -72, 'elevation': 18, 'size': [0.16, 1.5], 'distance': 1.5, 'power': 2.2},
                  {'azimuth': 72, 'elevation': 18, 'size': [0.16, 1.5], 'distance': 1.5, 'power': 1.8},
                  {'azimuth': 0, 'elevation': 86, 'size': 0.7, 'distance': 2.0, 'power': 1.2}]}
# v5 (softer look, round 2): one large soft key high front-left at about three times the fill, so the fringe drops a
# shadow band on the case and everything sits in a dense contact shadow; a strip behind-right as a rim; a black card
# camera-right so the case's face falls off toward its right edge; the top light low, so the crown stops sparkling
RIG3 = {'type': 'sweep', 'color': '#efe9df', 'wall_color': '#b3a594', 'wall_range': [0.4, 2.2], 'dome': 0.06,
        'key': {'azimuth': -38, 'elevation': 62, 'size': 1.6, 'power': 1.15},
        'fill': {'azimuth': 45, 'elevation': 25, 'power': 0.08},
        'rim': {'azimuth': 180, 'elevation': 12, 'power': 1.2, 'size': 0.8},
        'lights': [{'azimuth': -72, 'elevation': 18, 'size': [0.16, 1.5], 'distance': 1.5, 'power': 1.6},
                   {'azimuth': 150, 'elevation': 24, 'size': [0.14, 1.4], 'distance': 1.6, 'power': 2.4},
                   {'azimuth': 0, 'elevation': 86, 'size': 0.7, 'distance': 2.0, 'power': 0.2},
                   {'azimuth': 14, 'elevation': 34, 'size': [1.1, 0.45], 'distance': 2.4, 'power': 0.45}],
        'cards': [{'azimuth': 80, 'elevation': 12, 'distance': 1.5, 'size': [1.2, 1.2]}]}
shots = {
    'hero': {'size': [1800, 1200], 'samples': 160, 'rig': RIG3, 'exposure': 0.15,
             'camera': {'position': [-176, -510, 312], 'target': [32, -32, 16], 'lens': 100},
             'floor_z': 0},
    'detail': {'size': [1800, 1200], 'samples': 192, 'rig': {**{k: v for k, v in RIG3.items() if k not in ('wall_color', 'wall_range')},
                                                            'cove_depth': 5.0, 'cove_radius': 6.0},
               # low (about 12 degrees) and pulled back (critic, softer round 1): the case left of centre with space above
               # its hair, the bud in front and to the right, its forceps toward the open side
               'camera': {'position': [160, -246, 62], 'target': [-20, -22, 18], 'lens': 60},
               'hide': ['bud-l', 'inner-l', 'grille-l', 'pincers-l', 'tip-l'],
               'floor_z': 0},
}
json.dump({'materials': MAT, 'objects': objects, 'shots': shots}, open(os.path.join(HERE, 'shots.json'), 'w'), indent=1)
print('shots.json written; bud poses', json.dumps(poses))
