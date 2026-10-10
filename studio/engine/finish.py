"""The finish: the tone and sharpness a photographer gives a frame in post, after the path tracer and before it ships.

A render out of the view transform has no white: every critic of rounds 1 to 16 (2026-10-08 to 10) read the white
lacquer as "flat grey", and the frames bore it out, the white paint's lit face at 205 to 218 of 255 on every shot and
under 0.4 % of any frame above 235. Lights could not lift it: the view transform's shoulder starts near 200, so a
brighter key flattens the face it lights before it whitens it, and the critics' own tests held the faces under 216 to
keep their gradients. Two blind A/B judges (critic/ab/2026-10-10-finish.md) preferred the same frames with a white point
set in post, 7.0 over 6.0 (04b) and 6.2 over 5.3 (09), and named its faults: highlights clipped by too short a shoulder,
sharpening halos, a cyan LED bleached white, grain raised 40 %. This is that finish with those faults designed out:

- **white point** (`white_in` -> `white_out`): a gain on luminance, in sRGB, that takes the level `white_in` (the
  white paint's lit face, as the raw frame shows it) to `white_out`; above it a smooth shoulder rolls the rest of the
  range into `white_out` to `peak` (251), so nothing clips and a highlight keeps some gradient. The gain is applied to
  all three channels in linear light, so a colour keeps its hue and saturation, and lowered for any pixel where it
  would take a channel past the peak (the LED stays cyan);
- **contrast**: a mild S about mid-grey (the share of a smoothstep blended in), on luminance;
- **clarity**: local contrast at a large radius (`clarity_px`), in the midtones only, on luminance;
- **sharpen**: an unsharp mask on luminance at `sharpen_px` (scaled with the frame's width, at 1350 px), cored (a
  difference under `sharpen_core` levels is noise, not an edge) and clamped to its 3 x 3 neighbourhood's range, so an
  edge gets crisper without a halo past either side.

The post chain is raw -> tone (white point, contrast, clarity) -> retouch (the paints matched to their swatches, on the
toned frame, so the reds stay on their swatch) -> sharpen -> the frame. The raw frame stays beside it as IMG.raw.png.

    finish: {"enabled": true, "white_in": 213, "white_out": 236, "contrast": 0.12, "clarity": 0.08,
             "sharpen": 0.35, "sharpen_px": 0.7}

`python3 studio/engine/finish.py calibrate IMG` reads the white paint's lit face off IMG.raw.png (its 75th percentile
of brightness, from the swatch mask) and prints the `white_in` that would put it at `white_out`, the gain capped at
`max_gain` (1.12) so a white the light leaves in shade (08's cut-away side) is not dragged up to the lit one.
`python3 studio/engine/finish.py apply RAW OUT --spec JSON [--swatch S --legend L --retouch JSON]` runs the chain.
"""
import argparse, json
from pathlib import Path

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, maximum_filter, minimum_filter

DEFAULTS = {'enabled': False, 'white_in': 215.0, 'white_out': 236.0, 'peak': 251.0, 'contrast': 0.12,
            'clarity': 0.08, 'clarity_px': 25.0, 'sharpen': 0.35, 'sharpen_px': 0.7, 'sharpen_core': 2.0,
            'max_gain': 1.12}
W = np.array([0.2126, 0.7152, 0.0722])


def s2l(c):
    c = np.clip(c, 0, None)
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def l2s(c):
    c = np.clip(c, 0, None)
    return np.where(c <= 0.0031308, c * 12.92, 1.055 * c ** (1 / 2.4) - 0.055)


def curve(x, wi, wo, hi):
    """sRGB (0 to 1) -> sRGB: the gain wo/wi up to wi, then a rational shoulder from (wi, wo) to (1, hi) whose slope
    meets the gain at wi; past 1 (none in an 8-bit frame) it holds hi."""
    g = wo / wi
    y = x * g
    m = g * (1 - wi) / max(hi - wo, 1e-6)
    if m > 1.0001:
        c = 1 / (m - 1)
        u = np.clip((x - wi) / (1 - wi), 0, 1)
        sh = wo + (hi - wo) * u * (1 + c) / (u + c)
    else:
        # the gain alone stays under the peak: no shoulder needed, a straight line to (1, hi) at most
        sh = np.minimum(x * g, wo + (x - wi) * (hi - wo) / (1 - wi))
    return np.where(x > wi, sh, y)


def _scale_lin(lin, k, cap):
    """Each pixel's linear RGB times k, with k lowered where it would take a channel past cap."""
    mx = lin.max(axis=2)
    k = np.minimum(k, cap / np.maximum(mx, 1e-9))
    return lin * k[..., None]


def tone(rgb8, spec):
    """The white point, contrast and clarity on an sRGB uint8 frame; returns a float sRGB frame (0 to 255)."""
    f = {**DEFAULTS, **(spec or {})}
    srgb = rgb8.astype(np.float64) / 255
    lin = s2l(srgb)
    hi = f['peak'] / 255
    cap = float(s2l(np.array(hi)))
    # contrast first, so the shoulder below has the last word on the highlights
    if f['contrast']:
        ye = l2s(lin @ W)
        y2 = (1 - f['contrast']) * ye + f['contrast'] * (3 * ye ** 2 - 2 * ye ** 3)
        lin = _scale_lin(lin, s2l(y2) / np.maximum(s2l(ye), 1e-9), 1.0)
    # the white point, on luminance, each pixel's gain lowered where it would take a channel past the peak
    ye = l2s(lin @ W)
    y2 = curve(ye, f['white_in'] / 255, f['white_out'] / 255, hi)
    lin = _scale_lin(lin, s2l(y2) / np.maximum(s2l(ye), 1e-9), cap)
    if f['clarity']:
        w_ = lin.shape[1]
        ye = l2s(lin @ W)
        bl = gaussian_filter(ye, f['clarity_px'] * w_ / 1350)
        y2 = ye + f['clarity'] * 4 * ye * (1 - ye) * (ye - bl)
        lin = _scale_lin(lin, s2l(np.clip(y2, 0, 1)) / np.maximum(s2l(ye), 1e-9), cap)
    return l2s(lin) * 255


def sharpen(rgb, spec):
    """The cored, clamped unsharp mask on luminance; float sRGB (0 to 255) in and out."""
    f = {**DEFAULTS, **(spec or {})}
    if not f['sharpen']:
        return rgb
    lin = s2l(rgb / 255)
    ye = l2s(lin @ W)
    s = f['sharpen_px'] * lin.shape[1] / 1350
    d = ye - gaussian_filter(ye, s)
    t = f['sharpen_core'] / 255
    d = np.sign(d) * np.maximum(np.abs(d) - t, 0)
    y2 = np.clip(ye + f['sharpen'] * d, minimum_filter(ye, 3), maximum_filter(ye, 3))
    lin = _scale_lin(lin, s2l(y2) / np.maximum(s2l(ye), 1e-9), 1.0)
    return l2s(lin) * 255


def _save(rgb, path):
    Image.fromarray(np.clip(np.rint(rgb), 0, 255).astype(np.uint8)).save(path)


def post(raw_png, out_png, fin=None, ret=None, swatch_png=None, legend=None):
    """The post chain: raw -> tone -> retouch (when on and a swatch mask is given) -> sharpen -> out.
    Returns {'finish': {...}, 'retouch': report or None}."""
    f = {**DEFAULTS, **(fin or {})}
    on = bool(f.get('enabled'))
    a = np.asarray(Image.open(raw_png).convert('RGB'))
    rep = {'finish': None, 'retouch': None}
    if on:
        _save(tone(a, f), out_png)
        src = out_png
    else:
        src = raw_png
    if ret and ret.get('enabled') and swatch_png:
        import retouch as Rt
        rep['retouch'] = Rt.retouch(str(src), str(swatch_png), legend, ret, str(out_png))
    elif src != out_png:
        Image.fromarray(a).save(out_png)
    if on:
        b = np.asarray(Image.open(out_png).convert('RGB')).astype(np.float64)
        _save(sharpen(b, f), out_png)
        g = f['white_out'] / f['white_in']
        rep['finish'] = {k: f[k] for k in ('white_in', 'white_out', 'peak', 'contrast', 'clarity', 'sharpen', 'sharpen_px')}
        rep['finish']['gain'] = round(g, 4)
    return rep


def white_face(raw_png, swatch_png, legend, pct=75):
    """The white paint's lit face off the raw frame: its `pct` percentile of luminance, as an sRGB level."""
    a = np.asarray(Image.open(raw_png).convert('RGB')).astype(np.float64) / 255
    ids = np.asarray(Image.open(swatch_png).convert('RGB'))[..., 0].astype(int)
    keys = [int(k) for k, g in legend.items() if str(g.get('hex', '')).upper() == '#FFFFFF']
    m = np.isin(ids, keys)
    if m.sum() < 200:
        return None
    return float(np.percentile(l2s(s2l(a) @ W)[m], pct) * 255)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    sub = ap.add_subparsers(dest='cmd', required=True)
    c = sub.add_parser('calibrate', help='the white_in that puts IMG\'s white paint at white_out')
    c.add_argument('img'); c.add_argument('--white-out', type=float, default=DEFAULTS['white_out'])
    c.add_argument('--max-gain', type=float, default=DEFAULTS['max_gain'])
    p = sub.add_parser('apply', help='run the post chain on a raw frame')
    p.add_argument('raw'); p.add_argument('out'); p.add_argument('--spec', default='{}')
    p.add_argument('--swatch'); p.add_argument('--legend'); p.add_argument('--retouch', default='{}')
    a = ap.parse_args()
    if a.cmd == 'calibrate':
        img = Path(a.img)
        raw = img.with_suffix('.raw.png') if img.with_suffix('.raw.png').exists() else img
        face = white_face(raw, img.with_suffix('.swatch.png'), json.loads(img.with_suffix('.swatch.json').read_text()))
        if face is None:
            print(json.dumps({'white_in': None, 'why': 'no white paint in the frame'}))
            return
        wi = max(face, a.white_out / a.max_gain)
        print(json.dumps({'face': round(face, 1), 'white_in': round(wi, 1), 'white_out': a.white_out,
                          'gain': round(a.white_out / wi, 4)}))
    else:
        leg = json.loads(Path(a.legend).read_text()) if a.legend else None
        spec = dict(json.loads(a.spec), enabled=True)
        rep = post(a.raw, a.out, spec, json.loads(a.retouch), a.swatch, leg)
        print(json.dumps(rep['finish']))


if __name__ == '__main__':
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    main()
