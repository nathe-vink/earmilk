#!/usr/bin/env python3
"""Starts a new product in the earmilk family from studio/template.

    python3 studio/new_product.py earworm --title earworm --kind "Wired headphones"

Creates spinoffs/<name>/ with a brief (README.md), params.py, model.py, scene.py, shots.json and critic/LOG.md, ready for
`.venv-fab/bin/python spinoffs/<name>/model.py` and `python3 studio/pathtrace.py spinoffs/<name>/shots.json`.
Refuses to overwrite an existing product.
"""
import argparse, shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('name', help='folder name, lower case, e.g. earworm')
    ap.add_argument('--title', default=None)
    ap.add_argument('--kind', default='A product')
    a = ap.parse_args()
    dest = ROOT / 'spinoffs' / a.name
    if dest.exists():
        sys.exit(f'{dest} exists; not overwriting')
    shutil.copytree(ROOT / 'studio' / 'template', dest)
    for f in dest.rglob('*'):
        if f.is_file() and f.suffix in ('.md', '.py', '.json'):
            t = f.read_text().replace('{{NAME}}', a.name).replace('{{TITLE}}', a.title or a.name).replace('{{KIND}}', a.kind)
            f.write_text(t)
    for d in ('out', 'renders'):
        (dest / d).mkdir(exist_ok=True)
    print(f'created {dest.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
