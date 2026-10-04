"""{{TITLE}}: writes shots.json for studio/pathtrace.py from params.py and the model's out/parts.json.

    .venv-fab/bin/python spinoffs/{{NAME}}/model.py && python3 spinoffs/{{NAME}}/scene.py
    python3 studio/pathtrace.py spinoffs/{{NAME}}/shots.json --shot hero --samples 32 --scale 0.4 --out /tmp/p1.png

Generated things that are not CAD (cables as tubes, hair from a Python hook) and solved poses go here too: see
spinoffs/earworm/scene.py (a worm cable) and spinoffs/earwig/scene.py (buds resting on the floor, a wig).
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from params import *  # noqa: F401,F403

M = json.load(open(os.path.join(HERE, 'out', 'parts.json')))
parts, facts = M['parts'], M['facts']

MAT = {
    'body': {'preset': 'satin_plastic', 'color': '#f2f0ec'},
}
objects = [{'id': n, 'type': 'mesh', 'file': f'out/stl/{n}.stl', 'material': p['material']} for n, p in parts.items()]
RIG = {'type': 'sweep', 'color': '#e8e4dc', 'key': {'azimuth': -45, 'elevation': 55},
       'lights': [{'azimuth': -150, 'elevation': 22, 'size': [0.22, 1.5], 'distance': 2.0, 'power': 1.4},
                  {'azimuth': 145, 'elevation': 22, 'size': [0.22, 1.5], 'distance': 2.0, 'power': 1.2}]}
shots = {
    'hero': {'size': [1800, 1200], 'samples': 160, 'rig': RIG, 'floor_z': facts.get('floor_z', 0),
             'camera': {'azimuth': -35, 'elevation': 20, 'lens': 85, 'fill': 0.7}},
}
json.dump({'materials': MAT, 'objects': objects, 'shots': shots}, open(os.path.join(HERE, 'shots.json'), 'w'), indent=1)
print('shots.json written')
