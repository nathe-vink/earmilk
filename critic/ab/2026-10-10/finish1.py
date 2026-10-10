"""A photographer's finish on a rendered frame (experiment, not in the repo yet).

1. White point: the white paint's diffuse highlight (its 97th percentile of luminance, from the swatch mask) is mapped
   to TARGET (sRGB 0-255) by a gain in encoded luminance with a soft shoulder above a knee, so speculars roll off.
2. Contrast: a mild S (smoothstep blend, share S) about mid-grey.
3. Clarity: local contrast at a large radius, midtones only.
4. Sharpen: an unsharp mask on luminance at a small radius, with a threshold.

All on luminance: each pixel's linear RGB is scaled by Y'/Y (hue and saturation kept), and a channel pushed past 1 is
desaturated toward Y' instead of clipping.

usage: finish.py IN.png OUT.png [--swatch IMG.swatch.png --legend IMG.swatch.json] [--target 244] [--s 0.15]
       [--clarity 0.08] [--sharpen 0.5] [--sigma 0.8]
"""
import argparse, json
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter

W = np.array([0.2126, 0.7152, 0.0722])


def s2l(c):
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def l2s(c):
    c = np.clip(c, 0, None)
    return np.where(c <= 0.0031308, c * 12.92, 1.055 * c ** (1 / 2.4) - 0.055)


def shoulder(x, g, k=0.85):
    kg = k * g
    if kg >= 1:
        kg = 0.999
    y = x * g
    hi = x > k
    y = np.where(hi, kg + (1 - kg) * (1 - np.exp(-(x - k) * g / (1 - kg))), y)
    return y


def solve_gain(ref, tgt, k=0.85):
    lo, hi = 0.5, 3.0
    for _ in range(60):
        g = (lo + hi) / 2
        if float(shoulder(np.array(ref), g, k)) < tgt:
            lo = g
        else:
            hi = g
    return (lo + hi) / 2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('inp'); ap.add_argument('out')
    ap.add_argument('--swatch'); ap.add_argument('--legend')
    ap.add_argument('--target', type=float, default=244)
    ap.add_argument('--pct', type=float, default=97, help='percentile of the white paint taken as its white')
    ap.add_argument('--ref', type=float, help='override the white reference (sRGB 0-255)')
    ap.add_argument('--s', type=float, default=0.15)
    ap.add_argument('--clarity', type=float, default=0.08)
    ap.add_argument('--clarity-sigma', type=float, default=25)
    ap.add_argument('--sharpen', type=float, default=0.5)
    ap.add_argument('--sigma', type=float, default=0.8)
    a = ap.parse_args()

    im = np.asarray(Image.open(a.inp).convert('RGB')).astype(np.float64) / 255
    lin = s2l(im)
    Y = lin @ W
    Ye = l2s(Y)

    if a.ref:
        ref = a.ref / 255
    else:
        sel = None
        if a.swatch and a.legend:
            sw = np.asarray(Image.open(a.swatch))
            if sw.ndim == 3:
                sw = sw[..., 0]
            leg = json.load(open(a.legend))
            ids = []
            items = leg.items() if isinstance(leg, dict) else enumerate(leg)
            for k_, v in items:
                if isinstance(v, dict) and str(v.get('hex', '')).upper() == '#FFFFFF':
                    try:
                        ids.append(int(k_))
                    except ValueError:
                        pass
            if ids:
                sel = np.isin(sw, ids)
        if sel is None or sel.sum() < 500:
            ref = float(np.percentile(Ye, 99.5))
        else:
            ref = float(np.percentile(Ye[sel], a.pct))
    g = solve_gain(ref, a.target / 255)
    y1 = shoulder(Ye, g)
    sm = 3 * y1 ** 2 - 2 * y1 ** 3
    y2 = (1 - a.s) * y1 + a.s * sm
    if a.clarity:
        bl = gaussian_filter(y2, a.clarity_sigma)
        w = 4 * y2 * (1 - y2)
        y2 = y2 + a.clarity * w * (y2 - bl)
    if a.sharpen:
        bl = gaussian_filter(y2, a.sigma)
        d = y2 - bl
        d = np.where(np.abs(d) < 1.5 / 255, 0, d)
        y2 = y2 + a.sharpen * d
    y2 = np.clip(y2, 0, 1)
    Y2 = s2l(y2)
    r = Y2 / np.maximum(Y, 1e-6)
    out = lin * r[..., None]
    mx = out.max(axis=2)
    over = mx > 1
    if over.any():
        k = np.where(over, (1 - Y2) / np.maximum(mx - Y2, 1e-6), 1)
        out = Y2[..., None] + (out - Y2[..., None]) * k[..., None]
    o = np.clip(l2s(out) * 255 + 0.5, 0, 255).astype(np.uint8)
    Image.fromarray(o).save(a.out)
    print(f'white ref {ref*255:.1f} -> {a.target}, gain {g:.4f}; S {a.s}; clarity {a.clarity}; sharpen {a.sharpen} @ {a.sigma}px')


if __name__ == '__main__':
    main()
