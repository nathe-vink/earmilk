"""The retouch: the product's paints matched to their swatches in the finished frame, as a retoucher matches a
photograph to the physical sample before it ships.

A path tracer reproduces a paint's swatch only under light that is white and even all round (the furnace the view
transform is built for). Under a studio's lamps the lit face of a red lacquer mirrors a dark room instead of the 4 %
white haze the tone curve allows for, and the curve's toe takes its green and blue to nothing: #C62828 renders
(182, 14, 15), dE 4 to 9 off the swatch, on every shot (critic rounds, 2026-10-09). Lights cannot fix that; a
masked correction can, and it is what product photography does.

The mask pass renders a swatch mask beside the frame: each product pixel carries the id of its paint and the copy
it belongs to (IMG.swatch.png and .json, from the materials the flavour colours: body, accent, insert). Per copy and
paint, a reference is read off the frame, its lit face (the pixels between the 40th and 90th percentile of lightness
that carry at least the paint's median chroma, so not its highlights or its edges), and corrected toward the swatch:

- a white paint (the swatch near #FFFFFF) is neutralised: every pixel's own cast (its a* and b*) shrinks by the share
  `neutral` (1 in a studio; less in a room, where the light's colour is the picture's), so a warm sunlit front and a
  side in a cool fill both come to neutral, while a colour the white mirrors (more than four times the face's cast)
  is left;
- a colour is matched: hue and chroma to the swatch by the share `match`, and its lightness by the share `lightness`
  (a gain on its light, as a lighter or darker paint would be), as the swatch reads under the light that the copy's
  own white shows (Bradford adaptation from D65 to that white, so a red in late sun stays sunlit beside its white);

each pixel by how much it is the paint: the mask softened over its edge pixels, times its chroma against the
reference's (a highlight or an edge blended with the background takes less). The raw frame stays beside it as
IMG.raw.png, and the report lists every paint's reference before and after, in dE2000 against its swatch.

    retouch: {"enabled": true, "match": 1.0, "lightness": 0.5, "neutral": 1.0, "adapt": 1.0}

`adapt` (0 to 1) is how far a colour's target follows the copy's white: 1 matches it to the swatch as the light that
white shows would colour it, 0 to the plain swatch; with `neutral` under 1 in a room (a trace of the morning's warmth
kept in the white, 02a's round 9) `adapt` 0 still holds the reds on their swatch.
"""
import json, math
from pathlib import Path

import numpy as np
from PIL import Image

M_RGB2XYZ = np.array([[0.4124564, 0.3575761, 0.1804375],
                      [0.2126729, 0.7151522, 0.0721750],
                      [0.0193339, 0.1191920, 0.9503041]])
M_XYZ2RGB = np.linalg.inv(M_RGB2XYZ)
D65 = np.array([0.95047, 1.0, 1.08883])
BRADFORD = np.array([[0.8951, 0.2664, -0.1614], [-0.7502, 1.7135, 0.0367], [0.0389, -0.0685, 1.0296]])
DEFAULTS = {'enabled': True, 'match': 1.0, 'lightness': 0.5, 'neutral': 1.0, 'adapt': 1.0}


def srgb_lin(c):
    c = np.asarray(c, float) / 255.0
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def lin_srgb(c):
    c = np.clip(c, 0.0, 1.0)
    return np.where(c <= 0.0031308, 12.92 * c, 1.055 * np.power(c, 1 / 2.4) - 0.055) * 255.0


def xyz_lab(X):
    t = X / D65
    f = np.where(t > (6 / 29) ** 3, np.cbrt(t), t / (3 * (6 / 29) ** 2) + 4 / 29)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])], -1)


def lab_xyz(L):
    fy = (L[..., 0] + 16) / 116; fx = fy + L[..., 1] / 500; fz = fy - L[..., 2] / 200
    f = np.stack([fx, fy, fz], -1)
    return np.where(f > 6 / 29, f ** 3, 3 * (6 / 29) ** 2 * (f - 4 / 29)) * D65


def lin_lab(rgb):
    return xyz_lab(rgb @ M_RGB2XYZ.T)


def lab_lin(lab):
    return lab_xyz(lab) @ M_XYZ2RGB.T


def hex_lab(h):
    return lin_lab(srgb_lin([int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16)]))


def de2000(l1, l2):
    """CIEDE2000 between two Lab colours."""
    L1, a1, b1 = l1; L2, a2, b2 = l2
    C1, C2 = math.hypot(a1, b1), math.hypot(a2, b2); Cm = (C1 + C2) / 2
    G = 0.5 * (1 - math.sqrt(Cm ** 7 / (Cm ** 7 + 25 ** 7)))
    a1p, a2p = a1 * (1 + G), a2 * (1 + G)
    C1p, C2p = math.hypot(a1p, b1), math.hypot(a2p, b2)
    h1p = math.degrees(math.atan2(b1, a1p)) % 360; h2p = math.degrees(math.atan2(b2, a2p)) % 360
    dL, dC = L2 - L1, C2p - C1p
    dh = 0.0 if C1p * C2p == 0 else (h2p - h1p if abs(h2p - h1p) <= 180 else h2p - h1p - 360 if h2p > h1p else h2p - h1p + 360)
    dH = 2 * math.sqrt(C1p * C2p) * math.sin(math.radians(dh / 2))
    Lm, Cmp = (L1 + L2) / 2, (C1p + C2p) / 2
    hm = h1p + h2p if C1p * C2p == 0 else ((h1p + h2p) / 2 if abs(h1p - h2p) <= 180 else (h1p + h2p + 360) / 2 if h1p + h2p < 360 else (h1p + h2p - 360) / 2)
    T = 1 - 0.17 * math.cos(math.radians(hm - 30)) + 0.24 * math.cos(math.radians(2 * hm)) + 0.32 * math.cos(math.radians(3 * hm + 6)) - 0.20 * math.cos(math.radians(4 * hm - 63))
    Sl = 1 + 0.015 * (Lm - 50) ** 2 / math.sqrt(20 + (Lm - 50) ** 2); Sc = 1 + 0.045 * Cmp; Sh = 1 + 0.015 * Cmp * T
    Rt = -2 * math.sqrt(Cmp ** 7 / (Cmp ** 7 + 25 ** 7)) * math.sin(math.radians(60 * math.exp(-((hm - 275) / 25) ** 2)))
    return math.sqrt((dL / Sl) ** 2 + (dC / Sc) ** 2 + (dH / Sh) ** 2 + Rt * (dC / Sc) * (dH / Sh))


def adapt(lab, white_lab):
    """A swatch's Lab as it reads under a light whose white reads `white_lab` (Bradford, from D65; chromaticity only)."""
    X = lab_xyz(np.asarray(lab, float))
    W = lab_xyz(np.asarray(white_lab, float)); W = W / W[1]
    M = np.linalg.inv(BRADFORD) @ np.diag((BRADFORD @ W) / (BRADFORD @ D65)) @ BRADFORD
    return xyz_lab(M @ X)


def _target(swatch, white, share):
    """The swatch as the colour should read: the share `share` of the way from the plain swatch to the swatch under the
    light the copy's white shows (0: the plain swatch, as brand guidelines judge it; 1: as the room's light colours it)."""
    if white is None or share <= 0:
        return swatch
    return swatch + (adapt(swatch, white) - swatch) * min(1.0, share)


def _into_gamut(lab, steps=10):
    """Lab colours brought inside sRGB by lowering their chroma (lightness and hue kept), each only as far as it has
    to go, so a saturated face keeps its modelling instead of clipping a channel to 0 across it."""
    rgb = lab_lin(lab)
    out = (rgb < -1e-4).any(axis=1) | (rgb > 1 + 1e-4).any(axis=1)
    if not out.any():
        return lab
    sub = lab[out]; lo = np.zeros(len(sub)); hi = np.ones(len(sub))
    for _ in range(steps):
        mid = (lo + hi) / 2
        t = sub.copy(); t[:, 1:] *= mid[:, None]
        r = lab_lin(t)
        ok = ~((r < -1e-4).any(axis=1) | (r > 1 + 1e-4).any(axis=1))
        lo = np.where(ok, mid, lo); hi = np.where(ok, hi, mid)
    sub = sub.copy(); sub[:, 1:] *= lo[:, None]
    lab = lab.copy(); lab[out] = sub
    return lab


def _soft(m):
    """A binary mask softened over its edge pixels (3 x 3 box): 1 inside, a fraction on the edge."""
    p = np.pad(m.astype(float), 1, mode='edge')
    return sum(p[1 + dy:p.shape[0] - 1 + dy, 1 + dx:p.shape[1] - 1 + dx] for dy in (-1, 0, 1) for dx in (-1, 0, 1)) / 9.0


def _reference(lab, m, colour):
    """The pixels of mask `m` that read as the paint's lit face: for a colour, lightness between its 30th and 95th
    percentile and among those the most saturated 30 %; for a white, lightness between its 50th and 90th percentile."""
    L = lab[..., 0][m]; C = np.hypot(lab[..., 1], lab[..., 2])[m]
    lo, hi = np.percentile(L, 30 if colour else 50), np.percentile(L, 95 if colour else 90)
    keep = (L >= lo) & (L <= hi)
    if colour:
        # the paint as its swatch shows it is its most saturated well-lit pixels: a face mirroring the sweep at a grazing
        # angle is paler, and set as the reference it made 08b e7's lit slope be pushed x1.65 out of gamut
        keep &= C >= np.percentile(C[keep] if keep.any() else C, 70)
    if keep.sum() < 20:
        keep = np.ones_like(L, bool)
    return keep


def retouch(raw_png, swatch_png, legend, spec, out_png):
    """Retouch `raw_png` into `out_png` by the swatch mask; returns the report (per paint: before and after)."""
    spec = {**DEFAULTS, **(spec or {})}
    a = np.asarray(Image.open(raw_png).convert('RGB')).astype(float)
    ids = np.asarray(Image.open(swatch_png).convert('RGB'))[..., 0].astype(int)
    if ids.shape != a.shape[:2]:
        raise SystemExit(f'retouch: the swatch mask is {ids.shape[::-1]}, the frame {a.shape[1::-1]}')
    lin = srgb_lin(a)
    groups = []
    for k, g in legend.items():
        m = ids == int(k)
        if m.sum() < 50:
            continue
        t = hex_lab(g['hex'])
        groups.append(dict(g, id=int(k), mask=m, target=t,
                           mode='neutral' if math.hypot(t[1], t[2]) < 5 and t[0] > 90 else 'match'))
    report, whites = [], {}
    lab = lin_lab(lin)
    # whites first: per copy, the white its light shows, after the share of its cast taken out
    for g in [g for g in groups if g['mode'] == 'neutral']:
        m = g['mask']; px = lab[m]; ref = _reference(lab, m, False)
        cast = np.median(px[ref][:, 1:], axis=0); Lr = float(np.median(px[ref][:, 0]))
        Cr = float(math.hypot(*cast))
        C = np.hypot(px[:, 1], px[:, 2])
        # each pixel's own cast shrinks, not the lit face's taken from all: a sunlit front is warm where the side in a
        # cool fill is blue, and one cast subtracted from both turns the side bluer (02a e9: its side 2.6 to 4.9 dE).
        # A colour mirrored in the white (a red plinth's reflection, a print) is more than a cast and is left: full
        # weight up to twice the face's cast (at least 4), none from four times it (at least 10)
        lo_, hi_ = max(2 * Cr + 3, 4.0), max(4 * Cr + 6, 10.0)
        cw = np.clip((hi_ - C) / (hi_ - lo_), 0, 1)
        w = _soft(m)[m] * cw * spec['neutral']
        new = px.copy(); new[:, 1:] *= (1 - w)[:, None]
        lab[m] = new
        after = np.median(new[ref], axis=0)
        whites.setdefault(g['instance'], np.array([Lr, *(cast * (1 - spec['neutral']))]))
        report.append({'paint': g['material'] + (f" ({g['part']})" if g.get('part') else ''), 'copy': g['instance'], 'swatch': g['hex'], 'mode': 'neutral',
                       'pixels': int(m.sum()), 'cast_before': [round(float(v), 2) for v in cast],
                       'cast_after': [round(float(v), 2) for v in after[1:]],
                       'de_before': round(de2000([Lr, *cast], [Lr, 0, 0]), 2),
                       'de_after': round(de2000(list(after), [after[0], 0, 0]), 2)})
    lin = lab_lin(lab)
    any_white = next(iter(whites.values()), None)
    # one lightness per paint and copy, read off the lit faces of all its parts together: a gain on the paint (its
    # albedo) keeps each face's shading against the others, which is the lighting's; each part then takes its own hue
    paint_gain = {}
    for g in [g for g in groups if g['mode'] == 'match']:
        pk = (g['instance'], g.get('paint_key', g['material']))
        paint_gain.setdefault(pk, []).append(g)
    for pk, gs in paint_gain.items():
        mm = np.zeros(ids.shape, bool)
        for g in gs:
            mm |= g['mask']
        refp = _reference(lab, mm, True)
        whole = np.median(lab[mm][refp], axis=0)
        white = whites.get(pk[0], any_white)
        tgt = _target(gs[0]['target'], white, spec['adapt'])
        Yr, Yt = float(lab_xyz(whole)[1]), float(lab_xyz(tgt)[1])
        paint_gain[pk] = (Yt / max(Yr, 1e-6)) ** spec['lightness'] if Yr > 0 else 1.0
    for g in [g for g in groups if g['mode'] == 'match']:
        m = g['mask']; px_lab = lab[m]; ref = _reference(lab, m, True)
        before = np.median(px_lab[ref], axis=0)
        white = whites.get(g['instance'], any_white)
        target = _target(g['target'], white, spec['adapt'])
        Cr0 = math.hypot(before[1], before[2])
        C = np.hypot(px_lab[:, 1], px_lab[:, 2])
        w = _soft(m)[m] * np.clip(C / max(Cr0, 1e-6), 0, 1)
        # lightness: the paint's gain (above), weighted per pixel
        gain = paint_gain[(g['instance'], g.get('paint_key', g['material']))]
        px_lin = lin[m] * (gain ** w)[:, None]
        px_lab = lin_lab(px_lin)
        mid = np.median(px_lab[ref], axis=0)
        Cm, hm = math.hypot(mid[1], mid[2]), math.atan2(mid[2], mid[1])
        # the swatch as this face shows it: the same paint under the face's own light (its chromaticity, at the face's
        # lightness), so a face in shade is matched to a darker red of lower chroma, not pushed to the lit swatch's
        # full chroma (04b e15: the side plinth x1.28 to G = 0, a flat crimson beside the shaded gable)
        t_lin = lab_lin(np.asarray(target, float))
        Yt_, Ym_ = float(lab_xyz(np.asarray(target, float))[1]), float(lab_xyz(mid)[1])
        if 0 < Ym_ < Yt_:
            target_face = lin_lab(t_lin * (Ym_ / Yt_))
        else:
            target_face = np.asarray(target, float)
        Ct, ht = math.hypot(target_face[1], target_face[2]), math.atan2(target_face[2], target_face[1])
        k = min(2.0, max(0.5, Ct / max(Cm, 1e-6)))
        dh = (ht - hm + math.pi) % (2 * math.pi) - math.pi
        s = w * spec['match']
        C0 = np.hypot(px_lab[:, 1], px_lab[:, 2])
        C = C0 * k ** s
        if k > 1:
            # a boost takes no pixel past the swatch's chroma: a face already as strong as the swatch (a lit slope beside
            # a pale grazing face that set the reference) keeps its own (08b e7: the slope pushed x1.65 out of gamut)
            C = np.minimum(C, np.maximum(C0, Ct * 1.05))
        h = np.arctan2(px_lab[:, 2], px_lab[:, 1]) + dh * s
        px_lab[:, 1], px_lab[:, 2] = C * np.cos(h), C * np.sin(h)
        px_lab = _into_gamut(px_lab)
        lab[m] = px_lab; lin[m] = lab_lin(px_lab)
        after = np.median(px_lab[ref], axis=0)
        report.append({'paint': g['material'] + (f" ({g['part']})" if g.get('part') else ''), 'copy': g['instance'], 'swatch': g['hex'], 'mode': 'match',
                       'pixels': int(m.sum()), 'adapted_to_white': white is not None and spec['neutral'] < 1,
                       'reference_before': [round(float(v), 1) for v in before], 'reference_after': [round(float(v), 1) for v in after],
                       'de_before': round(de2000(list(before), list(g['target'])), 2),
                       'de_after': round(de2000(list(after), list(g['target'])), 2),
                       'lightness_gain': round(float(gain), 3), 'chroma_scale': round(k, 3), 'hue_turn_deg': round(math.degrees(dh), 1)})
    out = lin_srgb(lin)
    Image.fromarray(np.clip(np.rint(out), 0, 255).astype(np.uint8)).save(out_png)
    return {'spec': spec, 'paints': report}


if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser(description='retouch a rendered frame by its swatch mask (normally run by render.py)')
    ap.add_argument('raw'); ap.add_argument('out'); ap.add_argument('--swatch'); ap.add_argument('--spec', default='{}')
    o = ap.parse_args()
    sw = Path(o.swatch or Path(o.raw).with_suffix('').with_suffix('.swatch.png'))
    leg = json.loads(sw.with_suffix('.json').read_text())
    print(json.dumps(retouch(o.raw, str(sw), leg, json.loads(o.spec), o.out), indent=1))
