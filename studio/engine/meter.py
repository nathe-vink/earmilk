#!/usr/bin/env python3
"""A light meter for a shot: the scene's true brightness by part or region, read where nothing clips, and the
exposure that would put each at a target value in the final image.

    python3 studio/engine/meter.py studio/shots/earmilk/04b.json [--part back-panel --part side-left]
        [--region 783 440 805 620] [--target 225] [--set path=value ...]

It renders the shot small and 3 stops under (so the brightest white sits far below any clip or shoulder), with the
part mask, inverts the shot's view transform (Standard, or Khronos PBR Neutral's offset), and prints for each part
or region its median scene-linear luminance at exposure 0, what the final image shows there now, and the EV change
that would bring it to --target (an sRGB value, 0 to 255). Regions are in the pixels of the image they were measured
on, a critic's staged render at 0.75 scale by default (--ref-scale).
A critic predicting an exposure guesses; this measures.
"""
import argparse, json, math, os, subprocess, sys, tempfile
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import shot as S  # noqa: E402

UNDER = 3.0          # stops under
LUM = np.array([0.2126, 0.7152, 0.0722])


def srgb_inv(v):
    return np.where(v <= 0.04045, v / 12.92, ((v + 0.055) / 1.055) ** 2.4)


def srgb(v):
    v = np.clip(v, 0, 1)
    return np.where(v <= 0.0031308, v * 12.92, 1.055 * v ** (1 / 2.4) - 0.055)


def pbr_neutral(c):
    """Khronos PBR Neutral on linear RGB (n, 3)."""
    c = np.array(c, dtype=float, ndmin=2)
    x = c.min(axis=1, keepdims=True)
    off = np.where(x < 0.08, x - 6.25 * x * x, 0.04)
    c = c - off
    start, desat = 0.8 - 0.04, 0.15
    peak = c.max(axis=1, keepdims=True)
    d = 1 - start
    new_peak = 1 - d * d / (peak + d - start)
    comp = np.where(peak < start, c, c * new_peak / np.maximum(peak, 1e-9))
    g = 1 - 1 / (desat * (peak - new_peak) + 1)
    mixed = comp * (1 - g) + new_peak * g
    return np.where(peak < start, c, mixed)


def pbr_neutral_inv_low(y):
    """The inverse below the shoulder (all a 3-stops-under render needs): undo the toe's offset per pixel."""
    m_out = y.min(axis=-1, keepdims=True)
    m_in = np.where(m_out < 6.25 * 0.08 ** 2, np.sqrt(np.maximum(m_out, 0) / 6.25), m_out + 0.04)
    return y + (m_in - m_out)


def display_value(scene_lum, view):
    """What a grey of this scene-linear luminance shows as in the final image (0 to 255)."""
    if view == 'Standard':
        return float(srgb(np.array([scene_lum]))[0] * 255)
    return float(srgb(pbr_neutral([[scene_lum] * 3])[0, 0]) * 255)


def ev_to_target(scene_lum, target, view):
    lo, hi = -8.0, 8.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if display_value(scene_lum * 2 ** mid, view) < target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('shot'); ap.add_argument('--part', action='append', default=[])
    ap.add_argument('--region', type=float, nargs=4, action='append', default=[])
    ap.add_argument('--target', type=float, default=225.0)
    ap.add_argument('--set', action='append', default=[], dest='sets')
    ap.add_argument('--scale', type=float, default=0.4); ap.add_argument('--samples', type=int, default=24)
    ap.add_argument('--ref-scale', type=float, default=0.75, help='the scale of the image the regions were measured on (a critic\'s: 0.75)')
    a = ap.parse_args()
    sh = S.load(a.shot); S.apply_overrides(sh, a.sets)
    view = sh.get('render', {}).get('view', 'Khronos PBR Neutral')
    exp0 = sh.get('render', {}).get('exposure', 0.0)
    W, H = sh.get('size', [1600, 1000])
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / 'meter.png'
        cmd = [sys.executable, str(HERE / 'render.py'), a.shot, '--out', str(out), '--samples', str(a.samples), '--scale', str(a.scale),
               '--masks', '--set', f'render.exposure={exp0 - UNDER}'] + sum((['--set', s_] for s_ in a.sets), [])
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode or not out.exists():
            raise SystemExit(r.stderr[-2000:])
        img = np.asarray(Image.open(out).convert('RGB')).astype(float) / 255.0
        mask = np.asarray(Image.open(out.with_suffix('.mask.png')).convert('RGB'))[:, :, 0]
        legend = json.loads(out.with_suffix('.mask.json').read_text())
    lin = srgb_inv(img)
    scene = (lin if view == 'Standard' else pbr_neutral_inv_low(lin)) * 2 ** (UNDER - exp0)   # at exposure 0
    lum = scene @ LUM
    k = img.shape[1] / (W * a.ref_scale)
    rows = []
    for p in a.part:
        ids = [int(i) for i, n in legend.items() if __import__('fnmatch').fnmatchcase(n, p)]
        sel = np.isin(mask, ids)
        if sel.any():
            rows.append((f'part:{p}', lum[sel]))
    for (x0, y0, x1, y1) in a.region:
        rows.append((f'[{x0:g},{y0:g},{x1:g},{y1:g}]', lum[int(y0 * k):int(y1 * k), int(x0 * k):int(x1 * k)].ravel()))
    print(f'{a.shot}: view {view}, exposure {exp0:+g} EV; target {a.target:g}')
    print(f'{"where":34s} {"scene lum":>10s} {"shows now":>10s} {"EV to target":>13s}')
    for name, v in rows:
        m = float(np.median(v))
        now = display_value(m * 2 ** exp0, view)
        print(f'{name:34s} {m:10.3f} {now:10.1f} {ev_to_target(m * 2 ** exp0, a.target, view):+13.2f}')


if __name__ == '__main__':
    main()
