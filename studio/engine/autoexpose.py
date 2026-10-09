#!/usr/bin/env python3
"""Expose a shot to its critic's accept tests before rendering it in full.

    python3 studio/engine/autoexpose.py studio/shots/earmilk/08.json critic/rounds/DAY/shot-08-e1-r1.json [--save]

A critic predicts the levels its changes will give and writes accept tests for them; the prediction is most often
wrong in exposure (a view transform's shoulder hides how far over a white is). This renders the shot once, small and
scene-linear (meter.py's EXR), and turns it into the final image at each exposure within --range EV (1) of the shot's
with Blender's own colour management (the shot's view transform, look and white balance: what the render will do),
then reads every test whose reading exposure moves: brightness (lum_median, lum_mean, lum_p5, lum_p95, r/g/b_median)
and colour (delta_e), each the way critic/measure.py reads it, in its region (a box in the critic's 0.75-scale pixels,
a part, or a part within a box). It takes the exposure that passes the most of them; among those, one that clips under
1 % of the product's pixels, then one that clears every test by a margin (8 levels, 2 dE), then the smallest change.
Colour counts because PBR Neutral's shoulder bleaches a saturated red toward white: exposure that lifts the whites
can undo a fix to the red (02b's sun lowered for its plinth, then raised back in exposure). A test that only a larger
change would pass is not exposure's to fix: it is left failing, for the render and the next round to show. It prints
each test's value now and at that exposure, and with --save writes the exposure into the shot. Edge and falloff tests
are left to the render.
"""
import argparse, fnmatch, json, subprocess, sys, tempfile
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import shot as S  # noqa: E402
import meter as Mt  # noqa: E402

LUM_METRICS = {'lum_median': np.median, 'lum_mean': np.mean,
               'lum_p5': lambda v: np.percentile(v, 5), 'lum_p95': lambda v: np.percentile(v, 95),
               'r_median': np.median, 'g_median': np.median, 'b_median': np.median}
CHANNEL = {'r_median': 0, 'g_median': 1, 'b_median': 2}      # these read one channel, the rest the luminance


def passes(v, op, target):
    return {'<': v < target if not isinstance(target, list) else False, '<=': v <= target if not isinstance(target, list) else False,
            '>': v > target if not isinstance(target, list) else False, '>=': v >= target if not isinstance(target, list) else False,
            'between': isinstance(target, list) and target[0] <= v <= target[1]}[op]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('shot'); ap.add_argument('critic'); ap.add_argument('--save', action='store_true')
    ap.add_argument('--scale', type=float, default=0.4); ap.add_argument('--samples', type=int, default=24)
    ap.add_argument('--ref-scale', type=float, default=0.75)
    ap.add_argument('--range', type=float, default=1.0, help='how far from the shot\'s exposure to look, EV')
    a = ap.parse_args()
    sh = S.load(a.shot)
    view = sh.get('render', {}).get('view', 'Khronos PBR Neutral')
    exp0 = sh.get('render', {}).get('exposure', 0.0)
    W, H = sh.get('size', [1600, 1000])
    tests = [c for c in json.loads(Path(a.critic).read_text()).get('changes', [])
             if c.get('accept', {}).get('metric') in LUM_METRICS or (c.get('accept', {}).get('metric') == 'delta_e' and c['accept'].get('hex'))]
    if not tests:
        raise SystemExit('no brightness or colour tests in that reply')
    sys.path.insert(0, str(HERE.parent.parent / 'critic'))
    import measure as Me
    R = sh.get('render', {})
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / 'ae.exr'
        r = subprocess.run([sys.executable, str(HERE / 'render.py'), a.shot, '--out', str(out), '--samples', str(a.samples),
                            '--scale', str(a.scale), '--masks', '--set', 'render.format=EXR'], capture_output=True, text=True)
        if r.returncode or not out.exists():
            raise SystemExit(r.stderr[-2000:])
        import bpy
        im = bpy.data.images.load(str(out)); w, h = im.size
        mask = np.asarray(Image.open(out.with_suffix('.mask.png')).convert('RGB'))[:, :, 0]
        legend = json.loads(out.with_suffix('.mask.json').read_text())
        # the final image at any exposure, from Blender's colour management: the view, its look, the white balance
        scene = bpy.context.scene; vs = scene.view_settings
        vs.view_transform = view
        if R.get('look'):
            vs.look = R['look']
        if R.get('white_balance_k'):
            vs.use_white_balance = True; vs.white_balance_temperature = R['white_balance_k']; vs.white_balance_tint = R.get('white_balance_tint', 10.0)
        scene.render.image_settings.file_format = 'PNG'; scene.render.image_settings.color_depth = '8'
        cache = {}
        def shown(ev):
            ev = round(float(ev), 2)
            if ev not in cache:
                vs.exposure = ev
                pth = Path(td) / f'ev{ev:+.2f}.png'
                im.save_render(str(pth), scene=scene)
                cache[ev] = np.asarray(Image.open(pth).convert('RGB'), dtype=float)
            return cache[ev]
        k = w / (W * a.ref_scale)
        sel = []
        for c in tests:
            reg = c['accept']['region']
            m = np.ones((h, w), dtype=bool)
            if isinstance(reg, str) and reg.startswith('part:'):
                reg = {'part': reg[5:]}
            if isinstance(reg, dict):
                ids = [int(i) for i, n in legend.items() if any(fnmatch.fnmatchcase(n, p.strip()) for p in reg['part'].split('|'))]
                m &= np.isin(mask, ids)
                box = reg.get('box')
            else:
                box = reg
            if box:
                x0, y0, x1, y1 = [int(v * k) for v in box]
                bm = np.zeros_like(m); bm[y0:y1, x0:x1] = True; m &= bm
            sel.append(m if m.any() else None)
        def reading(c, m, ev):
            img = shown(ev); px = img[m]
            acc = c['accept']; met = acc['metric']
            if met == 'delta_e':
                hx = acc['hex'].lstrip('#'); ref = [int(hx[i:i + 2], 16) for i in (0, 2, 4)]
                return float(Me.ciede2000(Me.srgb_to_lab(np.median(px, axis=0)), Me.srgb_to_lab(ref)))
            v = px[:, CHANNEL[met]] if met in CHANNEL else Me.luma(px)
            return float(LUM_METRICS[met](v))
        def margin(v, op, target):
            if op == 'between':
                return min(v - target[0], target[1] - v)
            return v - target if op in ('>', '>=') else target - v
        product = mask > 0
        best = None
        for ev in np.round(np.arange(exp0 - a.range, exp0 + a.range + 1e-6, 0.05), 2):
            n, worst = 0, 1e9
            for c, m in zip(tests, sel):
                if m is None:
                    continue
                acc = c['accept']; val = reading(c, m, ev)
                if passes(val, acc['op'], acc['value']):
                    n += 1
                    unit = 2.0 if acc['metric'] == 'delta_e' else 8.0       # a margin of 2 dE counts as 8 levels
                    worst = min(worst, margin(val, acc['op'], acc['value']) / unit)
            img = shown(ev)
            clip = float((Me.luma(img[product] if product.any() else img.reshape(-1, 3)) >= 253).mean() * 100)
            # the most tests passed; then no clipped whites on the product (a highlight's few pixels are allowed: under 1 %
            # of its pixels); then a margin on every passed test (up to 8 levels or 2 dE); then the smallest change
            key = (n, -(round(clip, 1) if clip >= 1.0 else 0.0), min(round(worst, 2), 1.0) if n else 0.0, -abs(ev - exp0))
            if best is None or key > best[0]:
                best = (key, ev)
        ev = best[1]
        print(f'{a.shot}: exposure {exp0:+.2f} -> {ev:+.2f} EV passes {best[0][0]} of {sum(m is not None for m in sel)} brightness and colour tests')
        for c, m in zip(tests, sel):
            acc = c['accept']
            if m is None:
                print(f"  {c['id']}: region empty"); continue
            now, then = reading(c, m, exp0), reading(c, m, ev)
            print(f"  {c['id']} {acc['metric']} {acc['op']} {acc['value']}: now {now:.1f}, at {ev:+.2f} EV {then:.1f}"
                  f" {'pass' if passes(then, acc['op'], acc['value']) else 'FAIL'}")
    if a.save:
        raw = json.loads(Path(a.shot).read_text())
        raw.setdefault('render', {})['exposure'] = float(ev)
        Path(a.shot).write_text(json.dumps(raw, indent=1) + '\n')
        print('saved', a.shot)


if __name__ == '__main__':
    main()
