"""The waveguide study: compare throat candidates from fab/bem.py's results against the midrange it crosses to.

    .venv-fab/bin/python fab/wg_study.py out/acoustics/waveguide          (reads every NAME-*.json there)

For each candidate: the horizontal and vertical -6 dB half-angles, the directivity index (on-axis power against the
average over the sphere) and the vertical angle of the loudest direction, by frequency, beside the same for the
midrange: a rigid piston of the mid's effective area in an infinite baffle (2 J1(x) / x, x = ka sin theta), which is
how a cone of that size beams up to its breakup. A good crossover sits where the waveguide's directivity meets the
mid's and the waveguide's stays smooth above it.

Writes study.json, study.md (the table) and study.png (four panels) in the same directory.
"""
import glob, json, os, re, sys

import numpy as np
from scipy.special import j1

C_AIR = 343.0


def mid_piston(f, sd_cm2):
    a = np.sqrt(sd_cm2 * 1e-4 / np.pi); ka = 2 * np.pi * f / C_AIR * a
    th = np.radians(np.arange(0, 90.01, 0.25))
    x = ka * np.sin(th); D = np.where(x > 1e-9, 2 * j1(np.maximum(x, 1e-9)) / np.maximum(x, 1e-9), 1.0)
    lvl = 20 * np.log10(np.abs(D) + 1e-12)
    bw = next((float(np.degrees(th[i])) for i in range(len(th)) if lvl[i] <= -6), None)
    di = 10 * np.log10(ka ** 2 / (1 - j1(2 * ka) / ka)) if ka > 1e-3 else 3.0
    return bw, float(di)


def load(directory):
    cands = {}
    for p in sorted(glob.glob(os.path.join(directory, '*-*.json'))):
        name = os.path.basename(p).rsplit('-', 1)[0]
        if name == 'study': continue
        d = json.load(open(p))
        c = cands.setdefault(name, {'meta': d['meta'], 'rows': {}})
        for r in d['results']:
            c['rows'][r['f']] = r
    return cands


def main():
    directory = sys.argv[1] if len(sys.argv) > 1 else 'out/acoustics/waveguide'
    sd = float(sys.argv[2]) if len(sys.argv) > 2 else 118.0      # SB17MFC35-8
    cands = load(directory)
    freqs = sorted({f for c in cands.values() for f in c['rows']})
    table = ['| f (Hz) | mid: H half-angle, DI | ' + ' | '.join(f'{n}: H / up / down, DI, peak' for n in cands) + ' |',
             '|---|---|' + '---|' * len(cands)]
    out = {'mid_sd_cm2': sd, 'candidates': {}}
    for n, c in cands.items():
        out['candidates'][n] = {'waveguide': c['meta']['waveguide'], 'mesh': c['meta']['mesh'], 'by_f': {}}
    for f in freqs:
        bw, di = mid_piston(f, sd)
        cells = [f'{f:.0f}', f"{'>90' if bw is None else f'{bw:.0f}'}, {di:.1f}"]
        for n, c in cands.items():
            r = c['rows'].get(f)
            if r is None:
                cells.append('-'); continue
            fmt = lambda v: '>90' if v is None else f'{v:.0f}'
            cells.append(f"{fmt(r['beamwidth_h'])} / {fmt(r['beamwidth_up'])} / {fmt(r['beamwidth_down'])}, {r['di']:.1f}, {r['vertical_peak']:+.0f}")
            # the level 0 deg against the loudest vertical direction: what the listener loses to the tilt
            vert = r['v_down'][::-1] + r['v_up'][1:]
            out['candidates'][n]['by_f'][f] = {k: r[k] for k in ('beamwidth_h', 'beamwidth_up', 'beamwidth_down', 'di', 'vertical_peak')}
            out['candidates'][n]['by_f'][f]['axis_below_peak_db'] = round(max(vert) - r['h_right'][0], 2)
        table.append('| ' + ' | '.join(cells) + ' |')
    md = ['# Waveguide study', '', 'Half-angles in degrees to -6 dB from the horizontal axis (the listener); DI in dB; peak: the vertical angle '
          'of the loudest direction (+ up). The mid: a piston of its Sd in an infinite baffle.', ''] + table + ['']
    for n, c in out['candidates'].items():
        md.append(f"- **{n}**: throat y {c['waveguide'].get('throat_y', '?')}, "
                  f"mouth {c['waveguide']['mouth_width']} wide, s {c['waveguide']['mouth_s']}, depths H {c['waveguide']['depth_horizontal']} "
                  f"up {c['waveguide']['depth_up']} down {c['waveguide']['depth_down']}, eave angle {c['waveguide']['eave_angle']}; "
                  'axis below the vertical peak (dB): ' + ', '.join(f"{f:.0f} Hz {v['axis_below_peak_db']}" for f, v in sorted(c['by_f'].items())))
    open(os.path.join(directory, 'study.md'), 'w').write('\n'.join(md) + '\n')
    json.dump(out, open(os.path.join(directory, 'study.json'), 'w'), indent=1)
    print('\n'.join(md))

    import matplotlib; matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(2, 2, figsize=(11, 8))
    ff = np.geomspace(800, 12000, 120)
    mids = [mid_piston(f, sd) for f in ff]
    ax = axs[0, 0]; ax.plot(ff, [90 if b is None else b for b, _ in mids], 'k--', lw=1, label='mid (piston)')
    ax2 = axs[0, 1]; ax2.plot(ff, [d for _, d in mids], 'k--', lw=1, label='mid (piston)')
    for n, c in cands.items():
        fs = sorted(c['rows']); rows = [c['rows'][f] for f in fs]
        ax.plot(fs, [90 if r['beamwidth_h'] is None else r['beamwidth_h'] for r in rows], 'o-', label=n)
        ax2.plot(fs, [r['di'] for r in rows], 'o-', label=n)
        axs[1, 0].plot(fs, [90 if r['beamwidth_up'] is None else r['beamwidth_up'] for r in rows], 'o-', label=f'{n} up')
        axs[1, 0].plot(fs, [-(90 if r['beamwidth_down'] is None else r['beamwidth_down']) for r in rows], 'o--', label=f'{n} down')
        axs[1, 1].plot(fs, [r['vertical_peak'] for r in rows], 'o-', label=n)
    for a_, t in ((ax, 'horizontal -6 dB half-angle (deg)'), (ax2, 'directivity index (dB)'),
                  (axs[1, 0], 'vertical -6 dB half-angles, up + / down - (deg)'), (axs[1, 1], 'loudest vertical direction (deg, + up)')):
        a_.set_xscale('log'); a_.set_title(t, fontsize=10); a_.grid(True, which='both', alpha=0.3); a_.legend(fontsize=7)
        a_.set_xlim(800, 12000); a_.set_xlabel('Hz')
    fig.tight_layout(); fig.savefig(os.path.join(directory, 'study.png'), dpi=130)


if __name__ == '__main__':
    main()
