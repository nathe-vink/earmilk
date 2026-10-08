"""Polar maps of one waveguide from fab/bem.py's runs: how loud every direction is against the listening axis, by
frequency, horizontally and vertically, beside the on-axis response and the directivity index.

    .venv-fab/bin/python fab/wg_polar.py out/acoustics/waveguide C22 [--xo 2800]
        -> out/acoustics/waveguide/C22-polar.png and C22-polar.json

Reads every NAME-*.json in the directory (a run's frequencies may be spread over several files: lo, hi, lo2, ...)
and merges them by frequency. Darker is louder; the black line is -6 dB, the dashed one -3 dB. A waveguide that
holds its pattern draws straight, parallel contours; where the contours flare, it has lost control.
"""
import argparse, glob, json, os

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

INK = '#1a1a1a'; MUTED = '#6b6b6b'; GRID = '#e3e1dc'


def load(d, name):
    by_f = {}
    for p in sorted(glob.glob(os.path.join(d, f'{name}-*.json'))):
        if p.endswith('-polar.json'):
            continue
        for r in json.load(open(p))['results']:
            by_f[r['f']] = r
    return [by_f[f] for f in sorted(by_f)]


def arcs(r):
    on = r['h_right'][0]
    a = np.arange(0, 91, 5)
    h = np.concatenate([np.array(r['h_left'][::-1]), np.array(r['h_right'][1:])]) - on
    v = np.concatenate([np.array(r['v_down'][::-1]), np.array(r['v_up'][1:])]) - on
    ang = np.concatenate([-a[::-1], a[1:]])
    return ang, h, v


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('dir'); ap.add_argument('name'); ap.add_argument('--xo', type=float)
    ap.add_argument('--title', default=None)
    a = ap.parse_args()
    rows = load(a.dir, a.name)
    if not rows:
        raise SystemExit('no runs')
    f = np.array([r['f'] for r in rows])
    ang, _, _ = arcs(rows[0])
    H = np.array([arcs(r)[1] for r in rows]).T
    V = np.array([arcs(r)[2] for r in rows]).T
    on = np.array([r['h_right'][0] for r in rows]); on -= on[np.argmin(abs(f - (a.xo or f[len(f) // 2])))]
    di = np.array([r['di'] for r in rows])

    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9, 'axes.edgecolor': MUTED, 'axes.labelcolor': INK,
                         'xtick.color': MUTED, 'ytick.color': MUTED})
    fig = plt.figure(figsize=(12, 7.2), dpi=150)
    gs = fig.add_gridspec(2, 2, width_ratios=[1, 1], height_ratios=[1, 0.62], hspace=0.38, wspace=0.18)
    levels = np.arange(-30, 3.01, 3)
    lf = np.log10(f)
    for i, (M, title, lab) in enumerate(((H, 'Horizontal', 'angle from the axis (deg), + to the right'),
                                         (V, 'Vertical', 'angle from the axis (deg), + up'))):
        ax = fig.add_subplot(gs[0, i])
        Mc = np.clip(M, -30, 3)
        cs = ax.contourf(lf, ang, Mc, levels=levels, cmap='Blues', vmin=-36, vmax=3, extend='both')
        ax.contour(lf, ang, M, levels=[-6], colors=INK, linewidths=1.6, negative_linestyles='solid')
        ax.contour(lf, ang, M, levels=[-3], colors=INK, linewidths=0.8, linestyles='--')
        if a.xo:
            ax.axvline(np.log10(a.xo), color='#B3261E', lw=1.0, ls=':')
            ax.text(np.log10(a.xo), 86, f' crossover {a.xo / 1000:g} kHz', color='#B3261E', fontsize=8, va='top')
        ax.set_yticks(range(-90, 91, 30)); ax.set_ylim(-90, 90)
        ticks = [1000, 2000, 5000, 10000]
        ax.set_xticks([np.log10(t) for t in ticks if f.min() <= t <= f.max() * 1.01])
        ax.set_xticklabels([f'{t / 1000:g}k' for t in ticks if f.min() <= t <= f.max() * 1.01])
        ax.set_xlim(lf.min(), lf.max())
        ax.set_title(f'{title}: level against the axis', loc='left', fontsize=10, color=INK)
        ax.set_xlabel('frequency (Hz)'); ax.set_ylabel(lab)
        for s_ in ('top', 'right'):
            ax.spines[s_].set_visible(False)
    cb = fig.colorbar(cs, ax=fig.axes[:2], orientation='vertical', fraction=0.025, pad=0.02)
    cb.set_label('dB against the axis'); cb.outline.set_edgecolor(MUTED)
    ax = fig.add_subplot(gs[1, :])
    ax.plot(f, on, color=INK, lw=2.0, marker='o', ms=4, label='on axis, against its level at the crossover')
    ax.plot(f, di - di[np.argmin(abs(f - (a.xo or f[len(f) // 2])))], color='#3E6FB0', lw=2.0, marker='s', ms=4,
            label='directivity index, against its value at the crossover')
    for x, y, t in zip(f, di - di[np.argmin(abs(f - (a.xo or f[len(f) // 2])))], di):
        ax.annotate(f'{t:.1f}', (x, y), textcoords='offset points', xytext=(0, 7), ha='center', fontsize=7, color='#3E6FB0')
    ax.set_xscale('log'); ax.set_xlim(f.min() * 0.95, f.max() * 1.05)
    ax.set_xticks([1000, 2000, 5000, 10000]); ax.set_xticklabels(['1k', '2k', '5k', '10k'])
    ax.axhline(0, color=GRID, lw=1); ax.grid(True, which='major', color=GRID, lw=0.6)
    if a.xo:
        ax.axvline(a.xo, color='#B3261E', lw=1.0, ls=':')
    ax.set_ylabel('dB'); ax.set_xlabel('frequency (Hz)')
    ax.legend(frameon=False, loc='upper left', fontsize=8)
    for s_ in ('top', 'right'):
        ax.spines[s_].set_visible(False)
    ax.set_title('On axis and directivity index (the DI values in dB above each point)', loc='left', fontsize=10, color=INK)
    fig.suptitle(a.title or f'Waveguide {a.name}: simulated directivity (boundary elements, the cabinet and roof included)',
                 x=0.06, ha='left', fontsize=12, color=INK)
    out = os.path.join(a.dir, f'{a.name}-polar.png')
    fig.savefig(out, bbox_inches='tight', facecolor='white'); plt.close(fig)
    json.dump({'f_hz': f.tolist(), 'angles_deg': ang.tolist(), 'horizontal_db_rel_axis': H.T.round(2).tolist(),
               'vertical_db_rel_axis': V.T.round(2).tolist(), 'on_axis_db_rel_xo': on.round(2).tolist(), 'di_db': di.round(2).tolist()},
              open(os.path.join(a.dir, f'{a.name}-polar.json'), 'w'), indent=1)
    print(out)


if __name__ == '__main__':
    main()
