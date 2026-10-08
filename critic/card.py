#!/usr/bin/env python3
"""The shot card the critic reads in stage 2: what the frame is for, what is fixed and why, every setting it may
change with its current value, unit and range, and the parts it can measure by name.

    python3 critic/card.py shot-02a --shot renders/2026-10-08/02a-e1.shot.json [--image renders/.../02a-e1.png] --out card.md

The fixed part comes from critic/cards/earmilk.yaml; the settings from the engine's resolved shot file (written beside
every render as NAME.shot.json), described by studio/engine/knobs.py; the parts from the render's mask (--masks).
"""
import argparse, json, sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'studio' / 'engine'))
import knobs as K  # noqa: E402
import shot as S  # noqa: E402

LOCKED = ('product', 'products', 'size', 'render.samples', 'render.adaptive', 'render.denoise')


def fmt(v):
    if isinstance(v, float):
        return f'{v:g}'
    if isinstance(v, list) and all(isinstance(x, (int, float)) for x in v):
        return '[' + ', '.join(f'{x:g}' if isinstance(x, float) else str(x) for x in v) + ']'
    return json.dumps(v) if not isinstance(v, str) else v


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('shot_id'); ap.add_argument('--shot', required=True); ap.add_argument('--image')
    ap.add_argument('--card', default=str(ROOT / 'critic' / 'cards' / 'earmilk.yaml')); ap.add_argument('--out')
    ap.add_argument('--report', help="the render's report (its engine notes), when --image is a staged copy")
    a = ap.parse_args()
    card = yaml.safe_load(Path(a.card).read_text())
    sc = card['shots'][a.shot_id]
    sh = json.loads(Path(a.shot).read_text())
    L = [f'# Shot card: {sc["title"]}', '']
    # the product's description: the shot's own, else the one for its product file, else the card's
    pdef_ = (sh.get('product') or (sh.get('products') or [{}])[0]).get('def', '')
    ptext = sc.get('product') or card.get('products', {}).get(pdef_, card['product'])
    L += ['## The product', '', ' '.join(ptext.split()), '']
    L += ['## What this frame is for', '', ' '.join(sc['purpose'].split()) if isinstance(sc['purpose'], str) else sc['purpose'], '',
          'It must show: ' + '; '.join(sc['must_show']) + '.', '']
    L += ['## Fixed: never prescribe a change to these', '']
    for f in card['fixed'] + sc.get('fixed', []):
        L.append('- ' + ' '.join(f.split()))
    L += ['- The product, its flavour, its placement in this frame, and any exploded or cut-away arrangement of its parts '
          '(everything under `product`), the frame size and the sampling settings.', '']
    L += ['## Settings you may change', '',
          'Name a setting by its path. Units and ranges are the engine\'s. Lengths are metres; the product stands at the '
          'origin with its front toward -y, z up; the camera\'s position and target are world points. Relative values are '
          'allowed in "to": "+0.5", "-20", "x0.8", "+15%". To add a light, set `lights.NEWNAME` to a whole spec, e.g. '
          '`{"type": "area", "size_m": [0.6, 0.6], "orbit": {"azimuth_deg": 30, "elevation_deg": 20, "distance_m": 2}, '
          '"irradiance": 1.0, "color": 5600}` (an orbit is round the product\'s centre; `"position": [x, y, z]` places a '
          'lamp anywhere else); to remove one, set `lights.NAME.off` to true. A graduated light for a gloss surface to '
          'mirror as a smooth ramp is a panel: `{"type": "panel", "size_m": [1.2, 0.25], "position": [x, y, z], "target": '
          '[x, y, z], "strength": 1.0, "color": "#FFFFFF", "ramp": {"axis": "y", "at_m": [0.2, 0.45], "values": [0, 1]}, '
          '"diffuse": false}` (strength the peak radiance; the ramp along a world axis; diffuse false: seen only in '
          'reflections). A glint (a highlight exactly '
          'where a surface would mirror a small lamp into the camera) is `glints.N`: `{"at": [x, y, z], "normal": [nx, ny, nz], '
          '"size_m": 0.05, "power_w": 2, "receivers": ["part name"]}`.', '',
          '| setting | now | unit | range | meaning |', '|---|---|---|---|---|']
    seen = set()
    for path, val in S.flatten(sh):
        if any(path == l or path.startswith(l + '.') for l in LOCKED) or path.startswith('title'):
            continue
        d = K.describe(path) or ('', None, '')
        unit, rng, meaning = d
        rtxt = '' if rng is None else (f'{rng[0]:g} to {rng[1]:g}' if isinstance(rng, tuple) and len(rng) == 2 and all(isinstance(x, (int, float)) for x in rng) else ', '.join(map(str, rng)))
        flag = '' if K.in_range(val, rng) else ' (outside range)'
        L.append(f'| `{path}` | {fmt(val)}{flag} | {unit} | {rtxt} | {meaning} |')
        seen.add(path)
    # knobs the shot does not set yet but may (the common ones)
    extra = [k for k in ('camera.fstop', 'camera.shift_x', 'camera.shift_y', 'render.exposure', 'render.white_balance_k', 'render.look')
             if k not in seen]
    for k in extra:
        unit, rng, meaning = K.describe(k)
        rtxt = '' if rng is None else (f'{rng[0]:g} to {rng[1]:g}' if isinstance(rng, tuple) and all(isinstance(x, (int, float)) for x in rng) else ', '.join(map(str, rng)))
        L.append(f'| `{k}` | (default) | {unit} | {rtxt} | {meaning} |')
    L.append('')
    L.append('Material settings take the preset\'s keys (`materials.paint.coat_roughness`, `materials.oak.plank_contrast`, ...): '
             + '; '.join(f'**{n}**: ' + ', '.join(f'{k} {fmt(v)}' for k, v in p.items()) for n, p in _presets().items()) + '.')
    L.append('')
    if a.image:
        mp = Path(a.image).with_suffix('.mask.json')
        if mp.exists():
            sys.path.insert(0, str(ROOT / 'critic'))
            import measure as Me
            im, arr = Me.load(a.image); Me.load_mask(a.image)
            parts = Me.parts(arr)
            L += ['## Parts in this frame', '', 'Measure a part by name with `part:NAME` (or `part:woofer-*`) wherever a region is asked for, in the '
                  'tool and in accept tests: it follows the part if the camera moves.', '', '| part | pixels | box | luminance median | rgb median |', '|---|---|---|---|---|']
            for n, v in sorted(parts.items(), key=lambda kv: -kv[1]['pixels']):
                L.append(f'| {n} | {v["pixels"]} | {v["box"]} | {v["lum_median"]} | {v["rgb_median"]} |')
            L.append('')
        # what the engine could not do in this render, in its own words: the critic's prescriptions meet the physics here
        rp = Path(a.report) if a.report else Path(a.image).with_suffix('.report.json')
        if rp.exists():
            rep = json.loads(rp.read_text())
            notes = [f'- glint `{g["glint"]}` was skipped: {g["skipped"]}.' for g in rep.get('glints', []) if g.get('skipped')]
            notes += [f'- glint `{g["glint"]}` was moved {g["moved_mm"]} mm onto the {g["on"]}; the surface\'s own normal '
                      f'there is {g["normal_off_deg"]} degrees from the one given, so its lamp was placed from the surface\'s.'
                      for g in rep.get('glints', []) if not g.get('skipped') and g.get('normal_off_deg', 0) > 10]
            notes += [f'- change `{p_["id"]}` was not applied: {p_["why"]}.' for p_ in rep.get('pending', []) if p_.get('why') != 'not selected']
            for tr in rep.get('tuning', []):
                tried = ', '.join(f'{v:g} gave {r}' for v, r in tr['proofs'])
                verdict = ('it was set to %g' % tr['set'] if tr.get('set') is not None else 'nothing was set') + \
                          ('' if tr['moves_the_test'] else '; the test did not move with this setting, so it is not the lever for it')
                notes.append(f'- the engine tuned `{tr["setting"]}` for {tr["change"]} ({tr["test"].get("metric")} {tr["test"].get("op")} '
                             f'{tr["test"].get("value")}) by proof renders: {tried}; {verdict}.')
            if notes:
                L += ['## What the engine did and could not do in this render', '',
                      'A glint is placed from the surface the camera sees at its point: where that surface mirrors a part of '
                      'the set or the product into the camera, no lamp can be there, so the glint is skipped.', ''] + notes + ['']
    text = '\n'.join(L) + '\n'
    if a.out:
        Path(a.out).write_text(text)
    else:
        print(text)


def _presets():
    import materials as M
    return {k: v for k, v in M.PRESET_DEFAULTS.items() if k in ('paint', 'oak', 'plaster', 'sweep', 'metal', 'gunmetal', 'rubber', 'paper_cone')}


if __name__ == '__main__':
    main()
