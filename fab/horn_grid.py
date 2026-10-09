"""The waveguide's wall as a fine grid, for the renders' shading.

    .venv-fab/bin/python fab/horn_grid.py            (EARMILK_SIZE=bookshelf for the bookshelf)

The CAD makes the waveguide as a ruled loft through polygon rings (fab/cad.py): within 0.05 mm of the true surface,
which is finer than a print layer and nothing to the sound, but its flat facets show in a gloss coat's reflection as
stair-steps. This writes the true surface itself, sampled four times finer round the axis and along the wall, as
out*/render/<name>-horn.npy (meridians x stations x 3, mm, the CAD's frame) with its unit normals, pointing into the
air, as <name>-horn-normals.npy. The render engine sets the insert's shading normals from it ("normals_from" in the
product file); the geometry stays the CAD's.
"""
import os

import numpy as np

from params import WAVEGUIDE
from waveguide import Waveguide

BOOK = os.environ.get('EARMILK_SIZE') == 'bookshelf'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out-bookshelf' if BOOK else 'out', 'render')
NAME = 'earmilk-bookshelf' if BOOK else 'earmilk-floorstander'


def main(sections=384, steps=192, lip_steps=32):
    wg = Waveguide(**WAVEGUIDE, sections=sections, steps=steps, lip_steps=lip_steps)
    G, _ = wg.grid(wg.phis(max_jump=0.5))                           # the CAD's creases and refinement, finer
    # tangents round the axis (wrapping) and along the wall; their cross product, one orientation for the whole grid
    d_th = np.roll(G, -1, axis=0) - np.roll(G, 1, axis=0)
    d_s = np.gradient(G, axis=1)
    N = np.cross(d_th, d_s)
    N /= np.linalg.norm(N, axis=2, keepdims=True)
    # into the air: at the throat the wall's normal points toward its ring's centre
    j = 2
    c = G[:, j, :].mean(axis=0)
    if np.mean(np.sum(N[:, j, :] * (c - G[:, j, :]), axis=1)) < 0:
        N = -N
    os.makedirs(OUT, exist_ok=True)
    np.save(os.path.join(OUT, f'{NAME}-horn.npy'), G.astype(np.float64))
    np.save(os.path.join(OUT, f'{NAME}-horn-normals.npy'), N.astype(np.float64))
    print(NAME, G.shape, 'bbox', G.reshape(-1, 3).min(axis=0).round(1), G.reshape(-1, 3).max(axis=0).round(1))


if __name__ == '__main__':
    main()
