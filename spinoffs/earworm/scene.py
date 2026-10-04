"""earworm: writes shots.json for studio/pathtrace.py from params.py and the model's out/parts.json.

    .venv-fab/bin/python spinoffs/earworm/model.py && python3 spinoffs/earworm/scene.py
    python3 studio/pathtrace.py spinoffs/earworm/shots.json --shot hero

The worm is drawn here, not in CAD: a path from inside the left cup, out through the grommet, onto the floor and
across it, with the saddle (the inline remote) at CLITELLUM_FROM_HEAD along it and the plug at the tail. The plug is
CAD (out/stl/plug.stl), placed at the path's end along its last direction.
"""
import json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from params import *  # noqa: F401,F403

facts = json.load(open(os.path.join(HERE, 'out', 'parts.json')))['facts']
g = facts['grommet']
zf = FLOOR_Z + WORM_R + 0.05                       # the worm's centreline when it lies on the floor


def add(p, d, k):
    return [p[i] + d[i] * k for i in range(3)]


# --- the worm's path -------------------------------------------------------------------------------------------------
head = [add(g['start'], g['dir'], -10), g['start'], g['mouth'], add(g['mouth'], g['dir'], 6)]
landing = [[-110.0, -60.0, zf + 1.2], [-112.0, -78.0, zf]]
floor = [(-128, -116), (-120, -156), (-86, -186), (-36, -200), (14, -190), (58, -200), (78, -236), (52, -270),
         (2, -282), (-52, -282), (-96, -276), (-136, -262), (-170, -258)]
path = head + landing + [[x, y, zf] for x, y in floor]


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


L = length(path)
inside = 10 + math.dist(g['start'], g['mouth'])    # path length inside the cup and the grommet
s_c = inside + CLITELLUM_FROM_HEAD                 # saddle centre, from the path's start
c0, c1 = s_c - CLITELLUM_LEN / 2, s_c + CLITELLUM_LEN / 2
end, prev = path[-1], path[-2]
yaw = math.degrees(math.atan2(end[1] - prev[1], end[0] - prev[0]))

def radius_profile():
    """Radius factor along the worm, every 4 mm: a narrower head where it enters the cup, slow peristaltic waves (a
    uniform tube reads as a cable), the saddle's swell, and a blunt tail into the plug's ferrule."""
    pts, s = [], 0.0
    while s <= L:
        k = 1.0 + 0.055 * math.sin(2 * math.pi * s / 58.0) + 0.03 * math.sin(2 * math.pi * s / 23.0 + 1.3)
        if s < inside + 22:
            k = 0.62 + (min(max(s - (inside - 12), 0), 34) / 34) * (k - 0.62) if s > inside - 12 else 0.62
        if c0 - 6 <= s <= c1 + 6:
            e = min(1.0, (s - (c0 - 6)) / 10, ((c1 + 6) - s) / 10)
            k = k + (CLITELLUM_SWELL - k) * max(0.0, e)
        if s > L - 55:
            k = k + (0.7 - k) * ((s - (L - 55)) / 55) ** 1.4
        pts.append([round(s, 2), round(k, 4)])
        s += 4.0
    pts.append([round(L, 2), 0.7])
    return pts


worm = {
    'id': 'worm', 'type': 'tube', 'points': path, 'radius': WORM_R, 'material': 'worm', 'segments': 28,
    'profile_mm': radius_profile(),
    'rings': {'pitch': WORM_RING_PITCH, 'depth': WORM_RING_DEPTH, 'width': 0.24, 'jitter': 0.14, 'skip_mm': [[c0 + 2, c1 - 2]], 'skip_fade': 5.0},
    'attrs': [{'name': 'saddle', 'from': c0 + 2, 'to': c1 - 2, 'fade': 7.0}],
    'caps': True,
}

MAT = {
    'shell': {'preset': 'satin_plastic', 'color': '#2f2c2a', 'roughness': 0.36, 'coat': 0.12, 'coat_roughness': 0.3},
    'cushion': {'preset': 'protein_leather', 'color': '#211c19'},
    'cloth': {'preset': 'fabric', 'color': '#3c3a37'},
    'metal': {'preset': 'metal_satin', 'color': '#7d7974', 'roughness': 0.3},
    'rubber': {'preset': 'rubber', 'color': '#1c1815'},
    'worm': {'preset': 'skin', 'color': '#c08a80', 'top_color': '#77434b', 'coat': 0.45, 'coat_roughness': 0.24, 'roughness': 0.5,
             'sss': 0.45, 'sss_scale': 0.7,
             'attr_color': {'attr': 'saddle', 'color': '#dca88c', 'top_color': '#bd7d66'}},
    'plug': {'preset': 'metal_polished', 'color': '#dcd8d2'},
    'plug_rings': {'preset': 'gloss_plastic', 'color': '#0e0e0e'},
}
parts = json.load(open(os.path.join(HERE, 'out', 'parts.json')))['parts']
objects = [{'id': n, 'type': 'mesh', 'file': f'out/stl/{n}.stl', 'material': p['material']} for n, p in parts.items()
           if not n.startswith('plug')]
for n in ('plug-barrel', 'plug', 'plug-rings'):
    objects.append({'id': n, 'type': 'mesh', 'file': f'out/stl/{n}.stl', 'material': parts[n]['material'],
                                    'translate': [end[0], end[1], FLOOR_Z + PLUG_BARREL_D / 2 + 0.05], 'rotate': [0, 0, yaw]})
objects.append(worm)

RIG = {'type': 'sweep', 'color': '#d9d8d4', 'dome': 0.3,
       'key': {'azimuth': -42, 'elevation': 58, 'size': 1.6},
       'fill': {'azimuth': 50, 'elevation': 28, 'power': 0.45},
       'rim': {'azimuth': 150, 'elevation': 50, 'power': 0.7},
       'lights': [{'azimuth': -150, 'elevation': 22, 'size': [0.22, 1.5], 'distance': 2.0, 'power': 1.6},
                  {'azimuth': 140, 'elevation': 22, 'size': [0.22, 1.5], 'distance': 2.0, 'power': 1.3}]}
shots = {
    'hero': {'size': [1800, 1200], 'samples': 160, 'rig': RIG,
             'camera': {'position': [-300, -640, 125], 'target': [-2, -150, 14], 'lens': 40},
             'floor_z': FLOOR_Z},
    'detail': {'size': [1800, 1200], 'samples': 192, 'rig': RIG,
               'camera': {'position': [-500, -360, 6], 'target': [-76, -62, -18], 'lens': 70, 'fstop': 11, 'focus': [-110, -58, -42]},
               'floor_z': FLOOR_Z},
}
scene = {'materials': MAT, 'objects': objects, 'shots': shots,
         'notes': {'path_length_mm': round(L, 1), 'saddle_mm_from_cup': CLITELLUM_FROM_HEAD, 'plug_at': end}}
json.dump(scene, open(os.path.join(HERE, 'shots.json'), 'w'), indent=1)
print(f'shots.json: worm path {L:.0f} mm drawn ({CABLE_LEN:.0f} specified), saddle at {CLITELLUM_FROM_HEAD:.0f} mm from the cup')
