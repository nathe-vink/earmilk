"""earmilk's crossover, a starting point: the three shortlisted drivers modelled from their datasheets, placed where
the spec puts them, joined by a textbook three-way network that the optimiser then fits to Linkwitz-Riley targets.

    .venv-fab/bin/python fab/crossover.py

Writes fab/out/xover/: design.json (the network, the drivers, the targets: open it with studio/xover/xover.py),
response.png and .pdf, parts.csv, starting-point.json (the textbook values before fitting).

REPLACE WITH MEASUREMENTS. The drivers here are lumped models, not the drivers in the cabinet: a real crossover is
fitted to each driver measured in its own box (an FRD and a ZMA per driver, gated, on the listening axis), which
studio/xover/xover.py reads in place of the models. Until then this network is for budgeting parts and for hearing
the shape of the problem, not for building.
"""
import json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'studio', 'xover'))
import xover  # noqa: E402
from params import WOOFER, MID, TWEETER, PLAN  # noqa: E402

OUT = os.path.join(HERE, 'out', 'xover')
DRV = json.load(open(os.path.join(HERE, 'drivers.json')))
ACOU = json.load(open(os.path.join(HERE, 'out', 'acoustics.json')))

XO_LOW, XO_HIGH = 350.0, 2200.0   # the label's targets (README, Target specs): under the 12 in cone's beaming, over the dome's Fs x 5
LEVEL = 86.5                       # PROPOSAL: the woofer's level on the 390 mm baffle with about 3 dB of baffle-step gain made up


def pick(group, id_):
    return dict(next(d for d in DRV[group] if d['id'] == id_))


def drivers():
    w = pick('woofers', 'dsa315-8')
    wa = next(x for x in ACOU['woofers'] if x['id'] == 'dsa315-8')
    w.update(box={'type': 'vented', 'Vb_l': wa['Vb_net_l'], 'fb': ACOU['fb_target_hz'], 'QL': 7.0},
             baffle_mm=PLAN, z_mm=WOOFER['z'], offset_mm=60.0, hf=[1600.0, 0.6], polarity='+')
    m = pick('mids', 'sb17mfc35-8')
    ma = next(x for x in ACOU['mids'] if x['id'] == 'sb17mfc35-8')
    m.update(Le_mH=m.get('Le_mH') or 0.5, box={'type': 'sealed', 'Vb_l': ma['Vb_l'], 'QL': 10.0},
             baffle_mm=PLAN, z_mm=MID['z'], offset_mm=30.0, hf=[7000.0, 0.7], polarity='+')
    t = pick('tweeters', 'r3004-602200')
    t.update(Re=t.get('Re') or 3.2, Le_mH=t.get('Le_mH') or 0.03, Qts=t.get('Qts') or 0.6, Qms=2.0, Qes=1.0,
             z_mm=TWEETER['z'], offset_mm=TWEETER['faceplate_y'], polarity='+')
    assumed = {
        'woofer': 'acoustic centre 60 mm behind the baffle; on-axis roll-off from beaming and cone breakup as a 2nd-order low-pass at 1.6 kHz, Q 0.6',
        'mid': 'Le 0.5 mH (not found in what was searched); acoustic centre 30 mm behind the baffle; roll-off at 7 kHz, Q 0.7',
        'tweeter': 'Re 3.2 ohm, Le 0.03 mH, Qts 0.6, Qms 2, Qes 1 (typical for a 4 ohm 1 in dome; not from its datasheet); acoustic centre at the faceplate, 170 mm behind the front face; the bowl\'s loading and directivity are not modelled',
    }
    return {'woofer': w, 'mid': m, 'tweeter': t}, assumed


def textbook_network():
    """Third-order low-pass on the woofer, second-order band-pass and an L-pad on the mid, third-order high-pass and
    an L-pad on the tweeter: Butterworth values for the drivers' nominal impedance."""
    Rw, Rm, Rt = 8.0, 8.0, 4.0
    f1, f2 = XO_LOW, XO_HIGH
    lpad = lambda R, a: (R * (1 - 10 ** (-a / 20)), R * 10 ** (-a / 20) / (1 - 10 ** (-a / 20)))
    rm_s, rm_p = lpad(Rm, 1.5)
    rt_s, rt_p = lpad(Rt, 3.0)
    net = [
        # woofer: L1 - C1 - L2
        {'id': 'L1', 'type': 'L', 'nodes': ['in', 'w1'], 'value': 0.2387 * Rw / f1 * 1e3, 'awg': 14},
        {'id': 'C1', 'type': 'C', 'nodes': ['w1', '0'], 'value': 0.2122 / (Rw * f1) * 1e6},
        {'id': 'L2', 'type': 'L', 'nodes': ['w1', 'w2'], 'value': 0.0796 * Rw / f1 * 1e3, 'awg': 14},
        {'id': 'WOOFER', 'type': 'driver', 'driver': 'woofer', 'nodes': ['w2', '0']},
        # mid: C2 - L3 (high-pass), L4 - C3 (low-pass), R1 - R2 (L-pad)
        {'id': 'C2', 'type': 'C', 'nodes': ['in', 'm1'], 'value': 0.1125 / (Rm * f1) * 1e6},
        {'id': 'L3', 'type': 'L', 'nodes': ['m1', '0'], 'value': 0.2251 * Rm / f1 * 1e3, 'awg': 18},
        {'id': 'L4', 'type': 'L', 'nodes': ['m1', 'm2'], 'value': 0.2251 * Rm / f2 * 1e3, 'awg': 18},
        {'id': 'C3', 'type': 'C', 'nodes': ['m2', '0'], 'value': 0.1125 / (Rm * f2) * 1e6},
        {'id': 'R1', 'type': 'R', 'nodes': ['m2', 'm3'], 'value': rm_s},
        {'id': 'R2', 'type': 'R', 'nodes': ['m3', '0'], 'value': rm_p},
        {'id': 'MID', 'type': 'driver', 'driver': 'mid', 'nodes': ['m3', '0']},
        # tweeter: C4 - L5 - C5, R3 - R4 (L-pad)
        {'id': 'C4', 'type': 'C', 'nodes': ['in', 't1'], 'value': 0.1061 / (Rt * f2) * 1e6},
        {'id': 'L5', 'type': 'L', 'nodes': ['t1', '0'], 'value': 0.1194 * Rt / f2 * 1e3, 'awg': 20},
        {'id': 'C5', 'type': 'C', 'nodes': ['t1', 't2'], 'value': 0.3183 / (Rt * f2) * 1e6},
        {'id': 'R3', 'type': 'R', 'nodes': ['t2', 't3'], 'value': rt_s},
        {'id': 'R4', 'type': 'R', 'nodes': ['t3', '0'], 'value': rt_p},
        {'id': 'TWEETER', 'type': 'driver', 'driver': 'tweeter', 'nodes': ['t3', '0']},
    ]
    for e in net:
        if e['type'] == 'L':
            e['dcr'] = xover.AWG_DCR[e['awg']] * math.sqrt(e['value'])
    return net


def main():
    os.makedirs(OUT, exist_ok=True)
    drv, assumed = drivers()
    design = {
        'title': f'earmilk three-way, starting point (models, not measurements): LR4 at {XO_LOW:g} Hz and {XO_HIGH:g} Hz',
        'listener': {'distance_mm': 2500.0, 'height_mm': 950.0},
        'drivers': drv,
        'network': textbook_network(),
        'targets': {'level_db': LEVEL, 'sum_band': [150, 16000], 'z_min': 3.6, 'z_weight': 40.0, 'range': 6.0,
                    'ways': {'woofer': {'lp': XO_LOW, 'order': 4, 'align': 'LR', 'from': 120, 'to': 3000},
                             'mid': {'hp': XO_LOW, 'lp': XO_HIGH, 'order': 4, 'align': 'LR', 'from': 120, 'to': 12000},
                             'tweeter': {'hp': XO_HIGH, 'order': 4, 'align': 'LR', 'from': 800, 'to': 20000}}},
        'assumed': assumed,
    }
    json.dump(design, open(os.path.join(OUT, 'starting-point.json'), 'w'), indent=1)
    sim0 = xover.simulate(design)
    # the tweeter sits 170 mm back in the bowl: try both mid polarities and keep the better fit
    best = None
    for pol in ('+', '-'):
        d = json.loads(json.dumps(design)); d['drivers']['mid']['polarity'] = pol
        res = xover.optimize(d, verbose=False)
        err = math.sqrt(sum(res.fun ** 2) / len(res.fun))
        print(f'mid polarity {pol}: rms error {err:.2f} dB')
        if best is None or err < best[0]:
            best = (err, d)
    design = best[1]
    xover.snap(design)
    sim = xover.simulate(design)
    xover.plot(design, sim, os.path.join(OUT, 'response.png'), design['title'])
    xover.parts_list(design, os.path.join(OUT, 'parts.csv'))
    out = {**design, 'result': xover.summary(design, sim), 'result_textbook': xover.summary(design, sim0)}
    json.dump(out, open(os.path.join(OUT, 'design.json'), 'w'), indent=1)
    print(json.dumps(out['result'], indent=1))


if __name__ == '__main__':
    main()
