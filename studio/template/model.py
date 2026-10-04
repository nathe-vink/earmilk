"""{{TITLE}}: builds the parts from params.py and exports them for rendering and printing.

    .venv-fab/bin/python spinoffs/{{NAME}}/model.py

Writes out/stl/<part>.stl, out/step/<part>.step and out/parts.json (part names, materials, volumes, facts for scene.py).
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from params import *  # noqa: F401,F403
from build123d import Box, export_step, export_stl

OUT = os.path.join(HERE, 'out')


def build():
    """Return ({part name: (solid, material name)}, facts): facts are numbers scene.py needs (where a cable starts,
    where the floor is). Keep separate solids a hair apart or overlapping, never coplanar: Cycles renders coplanar
    faces black."""
    body = Box(WIDTH, DEPTH, HEIGHT)
    return {'body': (body, 'body')}, {'floor_z': -HEIGHT / 2}


def main():
    os.makedirs(os.path.join(OUT, 'stl'), exist_ok=True); os.makedirs(os.path.join(OUT, 'step'), exist_ok=True)
    parts, facts = build()
    manifest = {'parts': {}, 'facts': facts}
    for name, (solid, mat) in parts.items():
        export_stl(solid, os.path.join(OUT, 'stl', f'{name}.stl'), tolerance=0.02, angular_tolerance=0.1)
        export_step(solid, os.path.join(OUT, 'step', f'{name}.step'))
        manifest['parts'][name] = {'material': mat, 'volume_cm3': round(solid.volume / 1000, 2)}
    json.dump(manifest, open(os.path.join(OUT, 'parts.json'), 'w'), indent=1)
    print(json.dumps(manifest, indent=1))


if __name__ == '__main__':
    main()
