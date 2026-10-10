#!/usr/bin/env python3
"""Measurements on a rendered frame, for the critic (critic/PROMPT.md, v2) and for checking its acceptance tests.

The critic backs every claim with a number from this tool, and every change it prescribes carries a test written in
the same terms, so the next render can be checked without a second opinion. Coordinates are pixels from the top left
of the image as rendered (x right, y down); a region is X0 Y0 X1 Y1, end-exclusive. Luminance is Rec. 709 luma on the
8-bit sRGB values (0 to 255), the same scale the critic reads off the picture.

    python3 critic/measure.py IMAGE summary
    python3 critic/measure.py IMAGE stats X0 Y0 X1 Y1
    python3 critic/measure.py IMAGE profile X0 Y0 X1 Y1 [--axis y] [--bins 8]
    python3 critic/measure.py IMAGE delta-e X0 Y0 X1 Y1 '#C62828'
    python3 critic/measure.py IMAGE edge X0 Y0 X1 Y1 [--axis x]
    python3 critic/measure.py IMAGE grid --out PATH [--step 100]
    python3 critic/measure.py IMAGE crop X0 Y0 X1 Y1 --out PATH [--scale 3]
    python3 critic/measure.py IMAGE check TESTS.json      (a list of tests, or a critic reply with "changes")

Parts: when the engine rendered the frame with --masks, IMAGE.mask.png and IMAGE.mask.json sit beside it, and a
region can name a part instead of a box: "part:front-baffle", "part:woofer-*|mid-*" (fnmatch, | for or), or
{"part": "gable-block", "box": [x0, y0, x1, y1]} for a part inside a box. A part's region follows the part when the
camera moves, so tests written on parts survive a reframing. A zone split off as its own part ("back-panel.plinth")
is in its part's region too ("part:back-panel"); "part:*.plinth" is the band alone. On the command line, give the
region as one argument:

    python3 critic/measure.py IMAGE parts                  (every visible part: pixels, box, luminance, colour)
    python3 critic/measure.py IMAGE stats part:front-baffle
    python3 critic/measure.py IMAGE delta-e part:gable-block '#C62828'

Reflections: the engine's mask pass also writes IMAGE.mirror.png and IMAGE.mirror.json, what every product pixel
mirrors (the camera's ray reflected about the surface's shading normal, followed to the first lamp face, panel, surface
or the sky). A highlight, sheen or dark band on a glossy part is whatever its pixels mirror, so prescribe a change to
that (its strength, ramp, position, colour), not to a lamp those pixels do not see:

    python3 critic/measure.py IMAGE mirrors X0 Y0 X1 Y1       (what a region of the product mirrors, by share)
    python3 critic/measure.py IMAGE mirrors part:waveguide-insert

A test is {"id", "region": [x0, y0, x1, y1], "metric", "op", "value"}; metrics: lum_median, lum_mean, lum_p5,
lum_p95, lum_range (p95 - p5), r/g/b_median, clip_pct, crush_pct, falloff (first bin minus last bin of a profile
along "axis"), delta_e (needs "hex"), edge (the largest step across "axis"); ops: <, <=, >, >=, between (value
[lo, hi]). Exit status 1 if any test fails.
"""
import argparse, json, math, sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont


def load(path):
    im = Image.open(path).convert('RGB')
    return im, np.asarray(im).astype(np.float64)


def luma(a):
    return 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]


def region(a, r):
    x0, y0, x1, y1 = (int(v) for v in r)
    h, w = a.shape[:2]
    x0, x1 = max(0, min(x0, w)), max(0, min(x1, w)); y0, y1 = max(0, min(y0, h)), max(0, min(y1, h))
    if x1 <= x0 or y1 <= y0:
        raise SystemExit(f'empty region {r} in a {w}x{h} image')
    return a[y0:y1, x0:x1]


MASK = {}   # the current image's part mask: {'ids': HxW array, 'legend': {id: name}}


def load_mask(image_path):
    mp, lp = Path(image_path).with_suffix('.mask.png'), Path(image_path).with_suffix('.mask.json')
    if mp.exists() and lp.exists():
        MASK['ids'] = np.asarray(Image.open(mp).convert('RGB'))[..., 0].astype(int)
        MASK['legend'] = {int(k): v for k, v in json.loads(lp.read_text()).items()}


MIRROR = {}  # what each product pixel mirrors: {'ids': HxW array, 'legend': {id: label}}


def load_mirror(image_path):
    mp, lp = Path(image_path).with_suffix('.mirror.png'), Path(image_path).with_suffix('.mirror.json')
    if mp.exists() and lp.exists():
        MIRROR['ids'] = np.asarray(Image.open(mp).convert('RGB'))[..., 0].astype(int)
        MIRROR['legend'] = {int(k): v for k, v in json.loads(lp.read_text())['legend'].items()}
        zp = Path(image_path).with_suffix('.mirror.npz')
        if zp.exists():
            z = np.load(zp)
            MIRROR.update(label=z['label'], radiance=z['radiance'], xyz=z['xyz'], step=int(z['step']))


def mirrors(a, r):
    """What the product's pixels in a region mirror: each thing seen (an area lamp, a panel, a surface, the sky) with
    its share of those pixels and where they are."""
    if 'ids' not in MIRROR:
        raise SystemExit('no mirror map beside this image (the engine writes it in its mask pass)')
    _, ys, xs = select(a, r)
    v = MIRROR['ids'][ys, xs]
    on = v > 0
    if not on.any():
        return {'region': describe_region(r), 'pixels_on_product': 0, 'mirrors': []}
    seen = []
    q = lambda arr: [round(float(np.nanpercentile(arr, f)), 3) for f in (5, 50, 95)]
    for i in sorted(set(v[on].tolist()), key=lambda i: -(v == i).sum()):
        m = v == i
        what = MIRROR['legend'].get(i, f'id {i}')
        e = {'what': what, 'share_pct': round(100 * float(m.sum()) / float(on.sum()), 1),
             'box': [int(xs[m].min()), int(ys[m].min()), int(xs[m].max()) + 1, int(ys[m].max()) + 1]}
        if 'label' in MIRROR:
            st = MIRROR['step']
            cells = {(int(y) // st, int(x) // st) for y, x in zip(ys[m], xs[m])}
            cells = [c for c in cells if MIRROR['label'][c] == i]
            if cells:
                jj, ii = np.array(cells).T
                layers = (what.split(' over ')[0].split(' + ') + what.split(' over ')[1:]) if ' over ' in what else [what]
                rad = MIRROR['radiance'][jj, ii]
                e['radiance'] = {n: q(rad[:, k]) for k, n in enumerate(layers[:3]) if np.isfinite(rad[:, k]).any()}
                xyz = MIRROR['xyz'][jj, ii]
                if np.isfinite(xyz).any():
                    e['met_at_m'] = {ax: q(xyz[:, k]) for k, ax in enumerate('xyz')}
        seen.append(e)
    return {'region': describe_region(r), 'pixels_on_product': int(on.sum()), 'mirrors': seen,
            'note': 'what: the emitters a reflected ray meets, brightest first, over what lies behind them; radiance: '
                    'each emitter\'s where met (p5, median, p95; a panel strength times its ramp there, a lamp its '
                    'radiance times its specular share; a clear coat shows about 0.05 of it head-on, up to 0.3 to 0.5 '
                    'near grazing); met_at_m: where the nearest of them was met, world metres (p5, median, p95)'}


def mirror_profile(a, r, name, axis='y', bins=4):
    """How bright the emitter `name` is where a region's product pixels mirror it, in `bins` slices along `axis`
    (median radiance per slice; None where no pixel there mirrors it): which way a reflected ramp runs across a part."""
    if 'label' not in MIRROR:
        return None
    _, ys, xs = select(a, r)
    st = MIRROR['step']
    cells = sorted({(int(y) // st, int(x) // st) for y, x in zip(ys, xs)})
    vals = []
    for (j, i) in cells:
        w = MIRROR['legend'].get(int(MIRROR['label'][j, i]), '')
        comps = (w.split(' over ')[0].split(' + ') + w.split(' over ')[1:]) if ' over ' in w else [w]
        for k, c in enumerate(comps[:3]):
            if c.split(' ', 1)[-1] == name and np.isfinite(MIRROR['radiance'][j, i, k]):
                vals.append(((j if axis == 'y' else i), float(MIRROR['radiance'][j, i, k])))
    if not vals:
        return None
    c = np.array([v[0] for v in vals]); v = np.array([v[1] for v in vals])
    lo, hi = c.min(), c.max() + 1
    out = []
    for b in range(bins):
        m = (c >= lo + (hi - lo) * b / bins) & (c < lo + (hi - lo) * (b + 1) / bins)
        out.append(round(float(np.median(v[m])), 3) if m.any() else None)
    return out


def parse_region(r):
    """A region from the command line or a test: four numbers, 'part:NAME', or {'part': ..., 'box': [...]}."""
    if isinstance(r, str):
        return {'part': r.split(':', 1)[1]} if r.startswith('part:') else [float(v) for v in r.replace(',', ' ').split()]
    return r


def select(a, r):
    """(pixels N x 3, ys, xs) for a box, a part, or a part inside a box."""
    r = parse_region(r)
    if isinstance(r, dict):
        if 'ids' not in MASK:
            raise SystemExit('no part mask beside this image (render it with the engine\'s --masks)')
        import fnmatch
        names = [n.strip() for n in r['part'].split('|')]
        # a zone part ("back-panel.plinth") answers to its own name and to its part's, as in the engine
        base = lambda n: (n, n.split('.', 1)[0]) if '.' in n else (n,)
        ids = [i for i, n in MASK['legend'].items() if any(fnmatch.fnmatchcase(b_, pat) for b_ in base(n) for pat in names)]
        m = np.isin(MASK['ids'], ids)
        if 'box' in r:
            x0, y0, x1, y1 = (int(v) for v in r['box']); bm = np.zeros_like(m); bm[y0:y1, x0:x1] = True; m &= bm
        ys, xs = np.nonzero(m)
        if ys.size == 0:
            raise SystemExit(f'part {r["part"]!r} has no pixels in this frame')
        return a[ys, xs], ys, xs
    x0, y0, x1, y1 = (int(v) for v in r)
    s = region(a, r)
    yy, xx = np.mgrid[max(0, y0):max(0, y0) + s.shape[0], max(0, x0):max(0, x0) + s.shape[1]]
    return s.reshape(-1, 3), yy.ravel(), xx.ravel()


def describe_region(r):
    r = parse_region(r)
    return r if isinstance(r, dict) else [int(v) for v in r]


def stats(a, r):
    s, ys, xs = select(a, r); L = luma(s)
    pct = lambda v, q: float(np.percentile(v, q))
    return {
        'region': describe_region(r), 'pixels': int(L.size), 'box': [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1],
        'lum_mean': round(float(L.mean()), 1), 'lum_median': round(pct(L, 50), 1), 'lum_p5': round(pct(L, 5), 1), 'lum_p95': round(pct(L, 95), 1),
        'lum_range': round(pct(L, 95) - pct(L, 5), 1),
        'r_median': round(pct(s[..., 0], 50), 1), 'g_median': round(pct(s[..., 1], 50), 1), 'b_median': round(pct(s[..., 2], 50), 1),
        'clip_pct': round(100 * float((s.max(axis=-1) >= 254).mean()), 2), 'crush_pct': round(100 * float((L <= 3).mean()), 2),
    }


def profile(a, r, axis='y', bins=8):
    """Median luminance in `bins` equal slices along the axis, across the region (a part: across its pixels' box)."""
    s, ys, xs = select(a, r); L = luma(s)
    c = ys if axis == 'y' else xs
    edges = np.linspace(c.min(), c.max() + 1, bins + 1)
    out = []
    for i in range(bins):
        k = (c >= edges[i]) & (c < edges[i + 1])
        out.append(round(float(np.median(L[k])), 1) if k.any() else None)
    return out


def srgb_to_lab(rgb):
    c = np.asarray(rgb, float) / 255.0
    c = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    M = np.array([[0.4124564, 0.3575761, 0.1804375], [0.2126729, 0.7151522, 0.0721750], [0.0193339, 0.1191920, 0.9503041]])
    xyz = M @ c / np.array([0.95047, 1.0, 1.08883])
    f = np.where(xyz > (6 / 29) ** 3, np.cbrt(xyz), xyz / (3 * (6 / 29) ** 2) + 4 / 29)
    return np.array([116 * f[1] - 16, 500 * (f[0] - f[1]), 200 * (f[1] - f[2])])


def ciede2000(lab1, lab2):
    L1, a1, b1 = lab1; L2, a2, b2 = lab2
    C1, C2 = math.hypot(a1, b1), math.hypot(a2, b2); Cb = (C1 + C2) / 2
    G = 0.5 * (1 - math.sqrt(Cb ** 7 / (Cb ** 7 + 25 ** 7)))
    a1p, a2p = (1 + G) * a1, (1 + G) * a2
    C1p, C2p = math.hypot(a1p, b1), math.hypot(a2p, b2)
    h1p = math.degrees(math.atan2(b1, a1p)) % 360; h2p = math.degrees(math.atan2(b2, a2p)) % 360
    dLp, dCp = L2 - L1, C2p - C1p
    dhp = 0 if C1p * C2p == 0 else (h2p - h1p if abs(h2p - h1p) <= 180 else (h2p - h1p - 360 if h2p > h1p else h2p - h1p + 360))
    dHp = 2 * math.sqrt(C1p * C2p) * math.sin(math.radians(dhp / 2))
    Lbp, Cbp = (L1 + L2) / 2, (C1p + C2p) / 2
    hbp = h1p + h2p if C1p * C2p == 0 else ((h1p + h2p) / 2 if abs(h1p - h2p) <= 180 else ((h1p + h2p + 360) / 2 if h1p + h2p < 360 else (h1p + h2p - 360) / 2))
    T = 1 - 0.17 * math.cos(math.radians(hbp - 30)) + 0.24 * math.cos(math.radians(2 * hbp)) + 0.32 * math.cos(math.radians(3 * hbp + 6)) - 0.20 * math.cos(math.radians(4 * hbp - 63))
    SL = 1 + 0.015 * (Lbp - 50) ** 2 / math.sqrt(20 + (Lbp - 50) ** 2); SC = 1 + 0.045 * Cbp; SH = 1 + 0.015 * Cbp * T
    RT = -2 * math.sqrt(Cbp ** 7 / (Cbp ** 7 + 25 ** 7)) * math.sin(math.radians(60 * math.exp(-((hbp - 275) / 25) ** 2)))
    return math.sqrt((dLp / SL) ** 2 + (dCp / SC) ** 2 + (dHp / SH) ** 2 + RT * (dCp / SC) * (dHp / SH))


def delta_e(a, r, hexcol):
    med = np.median(select(a, r)[0], axis=0)
    h = hexcol.lstrip('#'); ref = [int(h[i:i + 2], 16) for i in (0, 2, 4)]
    return {'region_rgb': [round(float(v)) for v in med], 'reference': '#' + h.upper(), 'delta_e2000': round(ciede2000(srgb_to_lab(med), srgb_to_lab(ref)), 2)}


def edge(a, r, axis='x'):
    r = parse_region(r)
    if isinstance(r, dict):          # a part: its pixels' box
        _, ys, xs = select(a, r); r = [xs.min(), ys.min(), xs.max() + 1, ys.max() + 1]
    L = luma(region(a, r)); prof = L.mean(axis=0) if axis == 'x' else L.mean(axis=1)
    d = np.diff(prof); i = int(np.argmax(np.abs(d))) if d.size else 0
    return {'largest_step': round(float(d[i]) if d.size else 0.0, 1), 'at_offset_px': i,
            'width_10_90_px': width_10_90(prof)}


def width_10_90(prof):
    """How many pixels an edge takes to go from 10 % to 90 % of its step (sharp: 1 to 2; soft: many)."""
    if prof.size < 3: return None
    lo, hi = float(prof.min()), float(prof.max())
    if hi - lo < 4: return None
    t10, t90 = lo + 0.1 * (hi - lo), lo + 0.9 * (hi - lo)
    rising = prof[-1] > prof[0]
    idx10 = np.argmax(prof >= t10) if rising else np.argmax(prof <= t90)
    idx90 = np.argmax(prof >= t90) if rising else np.argmax(prof <= t10)
    return int(abs(int(idx90) - int(idx10)))


def summary(a):
    L = luma(a); h, w = L.shape
    return {'size': [w, h], 'lum_mean': round(float(L.mean()), 1),
            'lum_p1': round(float(np.percentile(L, 1)), 1), 'lum_p50': round(float(np.percentile(L, 50)), 1), 'lum_p99': round(float(np.percentile(L, 99)), 1),
            'clip_pct': round(100 * float((a.max(axis=-1) >= 254).mean()), 2), 'below_40_pct': round(100 * float((L < 40).mean()), 1),
            'thirds': {'x': [w // 3, 2 * w // 3], 'y': [h // 3, 2 * h // 3]}}


def parts(a):
    """Every part in the mask with its pixel count, box and median luminance and colour."""
    if 'ids' not in MASK:
        raise SystemExit('no part mask beside this image')
    out = {}
    for i, n in sorted(MASK['legend'].items(), key=lambda kv: kv[1]):
        ys, xs = np.nonzero(MASK['ids'] == i)
        if ys.size < 20: continue
        px = a[ys, xs]; L = luma(px)
        out[n] = {'pixels': int(ys.size), 'box': [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1],
                  'lum_median': round(float(np.median(L)), 1), 'lum_p5': round(float(np.percentile(L, 5)), 1),
                  'lum_p95': round(float(np.percentile(L, 95)), 1),
                  'rgb_median': [int(round(float(v))) for v in np.median(px, axis=0)]}
    return out


def grid(im, out, step=100):
    g = im.copy(); d = ImageDraw.Draw(g); w, h = g.size
    try: font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', max(12, step // 6))
    except Exception: font = ImageFont.load_default()
    for x in range(0, w, step):
        d.line([(x, 0), (x, h)], fill=(255, 0, 255), width=1); d.text((x + 2, 2), str(x), fill=(255, 0, 255), font=font)
    for y in range(0, h, step):
        d.line([(0, y), (w, y)], fill=(0, 255, 255), width=1); d.text((2, y + 2), str(y), fill=(0, 255, 255), font=font)
    Path(out).parent.mkdir(parents=True, exist_ok=True); g.save(out); return {'grid': str(out), 'step': step}


def crop(im, r, out, scale=3):
    x0, y0, x1, y1 = (int(v) for v in r)
    c = im.crop((x0, y0, x1, y1)); c = c.resize((c.width * scale, c.height * scale), Image.NEAREST)
    Path(out).parent.mkdir(parents=True, exist_ok=True); c.save(out); return {'crop': str(out), 'region': [x0, y0, x1, y1], 'scale': scale}


def metric(a, t):
    m, r = t['metric'], t['region']
    if m in ('lum_median', 'lum_mean', 'lum_p5', 'lum_p95', 'lum_range', 'r_median', 'g_median', 'b_median', 'clip_pct', 'crush_pct'):
        return stats(a, r)[m]
    if m == 'falloff':
        p = profile(a, r, t.get('axis', 'y'), t.get('bins', 8)); return round(p[0] - p[-1], 1)
    if m == 'delta_e':
        return delta_e(a, r, t['hex'])['delta_e2000']
    if m == 'edge':
        return abs(edge(a, r, t.get('axis', 'x'))['largest_step'])
    raise SystemExit(f'unknown metric {m}')


def passes(v, op, want):
    if op == 'between': return want[0] <= v <= want[1]
    return {'<': v < want, '<=': v <= want, '>': v > want, '>=': v >= want}[op]


def check(a, tests):
    if isinstance(tests, dict) and 'changes' in tests:
        tests = [dict(c['accept'], id=c.get('id', '?')) for c in tests['changes'] if c.get('accept')]
    results, ok = [], True
    for t in tests:
        v = metric(a, t); p = passes(v, t['op'], t['value']); ok &= p
        results.append({'id': t.get('id'), 'metric': t['metric'], 'measured': v, 'op': t['op'], 'value': t['value'], 'pass': p})
    return {'pass': ok, 'tests': results}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('image'); ap.add_argument('cmd', choices=['summary', 'parts', 'mirrors', 'stats', 'profile', 'delta-e', 'edge', 'grid', 'crop', 'check'])
    ap.add_argument('args', nargs='*'); ap.add_argument('--axis', default=None); ap.add_argument('--bins', type=int, default=8)
    ap.add_argument('--out'); ap.add_argument('--step', type=int, default=100); ap.add_argument('--scale', type=int, default=3)
    o = ap.parse_args(); im, a = load(o.image); load_mask(o.image); load_mirror(o.image)
    nums = lambda k: [float(v) for v in o.args[:k]]
    # a region is four numbers, or one argument naming a part ("part:NAME")
    reg = lambda: (o.args[0], o.args[1:]) if o.args and o.args[0].startswith('part:') else (nums(4), o.args[4:])
    if o.cmd == 'summary': res = summary(a)
    elif o.cmd == 'parts': res = parts(a)
    elif o.cmd == 'mirrors': res = mirrors(a, reg()[0])
    elif o.cmd == 'stats': res = stats(a, reg()[0])
    elif o.cmd == 'profile': res = {'axis': o.axis or 'y', 'bins': profile(a, reg()[0], o.axis or 'y', o.bins)}
    elif o.cmd == 'delta-e': r, rest = reg(); res = delta_e(a, r, rest[0])
    elif o.cmd == 'edge': res = edge(a, reg()[0], o.axis or 'x')
    elif o.cmd == 'grid': res = grid(im, o.out or 'grid.png', o.step)
    elif o.cmd == 'crop': res = crop(im, nums(4), o.out or 'crop.png', o.scale)
    else:
        res = check(a, json.loads(Path(o.args[0]).read_text())); print(json.dumps(res, indent=1)); sys.exit(0 if res['pass'] else 1)
    print(json.dumps(res, indent=1))


if __name__ == '__main__':
    main()
