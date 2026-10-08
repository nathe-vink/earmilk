"""The active crossover: a starting setup for the plate amplifier's DSP (Hypex Filter Design), from the geometry, the
drivers' datasheets and the waveguide study. A starting point for measurement, not a finished tuning.

    .venv-fab/bin/python fab/dsp.py        -> out/dsp/<size>.json and .md

What it decides, and from what:
  crossovers   woofer to mid at XO_LOW (above the mid's sealed-box corner and the baffle step, low enough that the
               12 in has not begun to beam); mid to tweeter at XO_HIGH, where the waveguide's directivity meets the mid's
               (fab/out/acoustics/waveguide/README.md). Linkwitz-Riley 4th order (24 dB/oct) both.
  delays       each driver's acoustic centre, depth behind the front face, aligned to the deepest (the tweeter at the
               waveguide's throat): delay = (depth_tweeter - depth_driver) / c.
  levels       the drivers' sensitivities at 2.83 V and their impedance, brought to the least sensitive.
  woofer EQ    the vented alignment's peak (fab/acoustics.py) taken out with one peaking band.
  tweeter EQ   the waveguide's on-axis gain against a bare piston, read from the BEM (fab/bem.py results), as shelf and
               peaking bands.
"""
import glob, json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from params import *  # noqa: F401,F403

HERE = os.path.dirname(os.path.abspath(__file__))
C_AIR = 343.0

XO_LOW = None if BOOK else 300.0       # Hz, woofer to mid (the floorstander's 3-way)
XO_HIGH = 2200.0 if BOOK else 2800.0   # Hz, to the tweeter: the floorstander's from the waveguide study's directivity match,
                                       # the bookshelf's the research's (the Illuminator's Fs 440 allows it; see its study)
OUTDIR = os.path.join(HERE, 'out-bookshelf' if BOOK else 'out')

# acoustic centres behind the front face (mm): a cone's is about where its voice coil drives it, a dome's at the dome
CENTRES = {'woofer': WOOFER_REBATE['depth'] + (22.0 if BOOK else 45.0), 'tweeter': WAVEGUIDE['throat_y'] - 4.0}
if MID:
    CENTRES['mid'] = MID_REBATE['depth'] + 22.0


def sens_at_2v83(d):
    s = d.get('sens_db')
    if isinstance(s, str):
        s = float(s.split()[0].split('-')[0])
    return float(s) if s is not None else None


def waveguide_on_axis(name):
    """On-axis level (dB, relative) by frequency from the BEM runs for the chosen throat."""
    out = {}
    for p in glob.glob(os.path.join(OUTDIR, 'acoustics', 'waveguide', f'{name}-*.json')):
        for r in json.load(open(p))['results']:
            out[r['f']] = r['h_right'][0]
    return dict(sorted(out.items()))


def find(x, key):
    if isinstance(x, dict):
        if x.get('id') == key:
            return x
        for v in x.values():
            f_ = find(v, key)
            if f_: return f_
    elif isinstance(x, list):
        for v in x:
            f_ = find(v, key)
            if f_: return f_
    return None


def main():
    big = json.load(open(os.path.join(HERE, 'research', 'drivers-floorstander.json')))
    small = json.load(open(os.path.join(HERE, 'research', 'drivers-small.json')))
    drivers = json.load(open(os.path.join(HERE, 'drivers.json')))
    roles = [r for r in ('woofer', 'mid', 'tweeter') if DRIVER_SET.get(r)]
    parts = {}
    for r in roles:
        key = DRIVER_SET[r]
        parts[r] = find(small, key) or find(big, key) or next((x for x in drivers['woofers'] if x['id'] == key), None) or {}
    def sens(d, fallback):
        ts = d.get('ts', d); v = ts.get('sens_dB', ts.get('sens_db'))
        if isinstance(v, str):
            try: v = float(v.split()[0].split('-')[0].split('(')[0])
            except ValueError: v = None
        return float(v) if v is not None else fallback
    S = {'woofer': sens(parts['woofer'], 87.0), 'tweeter': 90.5 if BOOK else 96.5}
    if MID: S['mid'] = sens(parts['mid'], 88.0)
    deepest = max(CENTRES.values())
    delays = {k: round((deepest - v) / 1000 / C_AIR * 1000, 3) for k, v in CENTRES.items()}
    ref = min(S.values())
    gains = {k: round(ref - v, 1) for k, v in S.items()}
    ac_path = os.path.join(OUTDIR, 'acoustics.json')
    ac = json.load(open(ac_path)) if os.path.exists(ac_path) else {}
    wg = waveguide_on_axis('BkF' if BOOK else 'C22')
    near = min(wg, key=lambda x: abs(x - XO_HIGH)) if wg else None
    wg_rel = {f: round(v - wg[near], 1) for f, v in wg.items()} if wg else {}
    names = {r: f'{parts[r].get("maker", "")} {parts[r].get("model", DRIVER_SET[r])}'.strip() for r in roles}
    xos = ([{'between': 'woofer-mid', 'f_hz': XO_LOW, 'type': 'Linkwitz-Riley', 'order': 4}] if MID else []) + \
          [{'between': ('mid' if MID else 'woofer') + '-tweeter', 'f_hz': XO_HIGH, 'type': 'Linkwitz-Riley', 'order': 4}]
    if BOOK:
        lt = ac.get('linkwitz_transform', {})
        woofer_eq = [{'type': 'linkwitz-transform', **lt, 'why': 'the sealed box\'s corner moved down to 45 Hz (fab/acoustics.py)'}]
    else:
        woofer_eq = [{'type': 'peaking', 'f_hz': 37.0, 'gain_db': -3.3, 'q': 1.2, 'why': 'the vented alignment\'s bump (fab/research/drivers-floorstander.md)'}]
    plan = {'size': SIZE, 'amplifier': AMP['model'],
            'channels': {f'CH{i + 1}': f'{r}, {names[r]}' for i, r in enumerate(roles)},
            'crossovers': xos, 'acoustic_centres_mm_behind_front': CENTRES, 'delays_ms': delays,
            'sensitivity_db_2v83': S, 'gains_db': gains, 'woofer_eq': woofer_eq,
            'waveguide_on_axis_rel_db': wg_rel,
            'workflow': ['Load the channels and the crossovers in Hypex Filter Design (Windows), USB to the amplifier',
                         'Measure each driver alone at 1 m on the tweeter axis (REW, UMIK-1), gated',
                         'Set levels and delays from the measurements (these numbers are where to start)',
                         'Check the summed response and the reverse-null at each crossover, then EQ the system flat on axis',
                         'Save to the amplifier; it stays silent until a filter is loaded']}
    os.makedirs(os.path.join(OUTDIR, 'dsp'), exist_ok=True)
    json.dump(plan, open(os.path.join(OUTDIR, 'dsp', f'{SIZE}.json'), 'w'), indent=1)
    cols = roles
    md = [f'# DSP starting point: the {SIZE}', '',
          f'Amplifier: {plan["amplifier"]}. Channels: ' + '; '.join(f'{k} {v}' for k, v in plan['channels'].items()) + '.', '',
          '| | ' + ' | '.join(cols) + ' |', '|---|' + '---|' * len(cols),
          '| acoustic centre behind the front (mm) | ' + ' | '.join(f'{CENTRES[c]:.0f}' for c in cols) + ' |',
          '| delay (ms) | ' + ' | '.join(str(delays[c]) for c in cols) + ' |',
          '| sensitivity, 2.83 V (dB) | ' + ' | '.join(str(S[c]) for c in cols) + ' |',
          '| gain to start (dB) | ' + ' | '.join(str(gains[c]) for c in cols) + ' |', '',
          'Crossovers: ' + '; '.join(f'{x["between"]} {x["f_hz"]:.0f} Hz' for x in xos) + ', Linkwitz-Riley 24 dB/octave.', '',
          'Woofer EQ: ' + json.dumps(woofer_eq), '',
          ('The waveguide\'s on-axis level against its level at the crossover (from the simulation): ' +
           ', '.join(f'{f:.0f} Hz {v:+.1f} dB' for f, v in wg_rel.items()) + '. Flatten it with a shelf after measuring.') if wg_rel else '',
          '', 'Workflow: ' + ' '.join(f'({i + 1}) {s_}.' for i, s_ in enumerate(plan['workflow']))]
    open(os.path.join(OUTDIR, 'dsp', f'{SIZE}.md'), 'w').write('\n'.join(md) + '\n')
    print('\n'.join(md))


if __name__ == '__main__':
    main()
