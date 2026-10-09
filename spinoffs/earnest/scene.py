"""earnest: writes shots.json for studio/pathtrace.py from params.py and the model's out/parts.json.

    .venv-fab/bin/python spinoffs/earnest/model.py && python3 spinoffs/earnest/scene.py
    python3 studio/pathtrace.py spinoffs/earnest/shots.json --shot hero --samples 32 --scale 0.4 --out /tmp/p1.png

Each pack's crate is filled cup by cup: a glass egg valve in every cup but the front row's last two, where the white
egg (volume) and the brown egg (input) sit; the half-dozen has room for the white one only. The heaters glow.
"""
import json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from params import *  # noqa: F401,F403

M = json.load(open(os.path.join(HERE, 'out', 'parts.json')))
parts, facts = M['parts'], M['facts']

MAT = {
    # recycled moulded pulp, in looks: a grey, fibrous, dead-matte surface (made as a pressed steel top with a textured
    # powder coat, since valves run hot)
    'pulp': {'preset': 'paper', 'color': '#b9b4a9', 'roughness': 0.92, 'sheen': 0.15,
             'bump': {'type': 'noise', 'scale': 0.9, 'strength': 0.9}},
    'rubber': {'preset': 'rubber', 'color': '#2a2826'},
    'glass': {'preset': 'glass', 'color': '#f6f3ec', 'roughness': 0.015},
    'getter': {'preset': 'metal_polished', 'color': '#a7a39c', 'roughness': 0.12},
    'anode': {'preset': 'metal_satin', 'color': '#55555a', 'roughness': 0.45},
    'mica': {'preset': 'satin_plastic', 'color': '#d8d0bd', 'roughness': 0.55},
    'heater': {'preset': 'emissive', 'color': '#ff7a2c', 'emission': 60.0},
    'bakelite': {'preset': 'gloss_plastic', 'color': '#2b1c13', 'roughness': 0.25},
    'egg_white': {'preset': 'satin_plastic', 'color': '#f2eee5', 'roughness': 0.55, 'sheen': 0.1},
    'egg_brown': {'preset': 'satin_plastic', 'color': '#b27a4c', 'roughness': 0.55, 'sheen': 0.1},
}
VALVE = ['glass', 'getter', 'anode', 'mica', 'heater', 'base']


def pack_objects(n, dx=0.0):
    """The objects for pack n, its crate centred at x dx."""
    p = facts['packs'][str(n)]
    rows, cols = p['rows'], p['cols']
    obs = [{'id': f'crate-{n}', 'type': 'mesh', 'file': f'out/stl/crate-{n}.stl', 'material': 'pulp', 'translate': [dx, 0, 0], 'smooth': 40},
           {'id': f'feet-{n}', 'type': 'mesh', 'file': f'out/stl/feet-{n}.stl', 'material': 'rubber', 'translate': [dx, 0, 0]}]
    front = [(rows - 1) * cols + c for c in range(cols)]
    knobs = {front[-1]: 'white'}
    if n >= 12:
        knobs[front[-2]] = 'brown'
    for i, (x, y, fz) in enumerate(p['cups']):
        if i in knobs:
            obs.append({'id': f'knob-{n}-{i}', 'type': 'mesh', 'file': f'out/stl/knob-{knobs[i]}.stl', 'material': f'egg_{knobs[i]}',
                        'translate': [x + dx, y, fz + facts['knob_tip_above_floor']], 'rotate': [0, 0, 0], 'smooth': 60})
            continue
        turn = (37 * i) % 90 - 45                                   # each valve turned its own way in its socket
        for v in VALVE:
            obs.append({'id': f'v{n}-{i}-{v}', 'type': 'mesh', 'file': f'out/stl/valve-{v}.stl', 'material': parts[f'valve-{v}']['material'],
                        'translate': [x + dx, y, fz - facts['valve_tip_below_floor']], 'rotate': [0, 0, turn], 'smooth': 60})
    return obs


def family():
    """The three packs side by side, the half-dozen in front of the flat."""
    w6, w12, w24 = (facts['packs'][k]['size'][0] for k in ('6', '12', '24'))
    gap = 120.0
    x12 = 0.0; x6 = -(w12 / 2 + gap + w6 / 2); x24 = w12 / 2 + gap + w24 / 2
    return pack_objects(6, x6) + pack_objects(12, x12) + pack_objects(24, x24)


RIG = {'type': 'sweep', 'color': '#d9d4cb', 'key': {'azimuth': -50, 'elevation': 55, 'power': 0.8},
       'lights': [{'azimuth': -150, 'elevation': 25, 'size': [0.3, 1.6], 'distance': 2.2, 'power': 1.1},
                  {'azimuth': 140, 'elevation': 30, 'size': [0.3, 1.6], 'distance': 2.2, 'power': 0.8}]}
objects = pack_objects(12)
shots = {
    'hero': {'size': [1800, 1200], 'samples': 192, 'rig': RIG, 'floor_z': facts['floor_z'],
             'camera': {'azimuth': -28, 'elevation': 42, 'lens': 85, 'fill': 0.78}},   # high enough to see the tray's surface
}
fam = family()
shots['hero']['hide'] = [o['id'] for o in fam if o['id'] not in {q['id'] for q in objects}]
shots['family'] = {'size': [2000, 1000], 'samples': 160, 'rig': RIG, 'floor_z': facts['floor_z'],
                   'camera': {'azimuth': -20, 'elevation': 34, 'lens': 70, 'fill': 0.85}}
seen = {o['id'] for o in objects}
all_objects = objects + [o for o in fam if o['id'] not in seen]
json.dump({'materials': MAT, 'objects': all_objects, 'shots': shots}, open(os.path.join(HERE, 'shots.json'), 'w'), indent=1)
print('shots.json written:', len(all_objects), 'objects')
