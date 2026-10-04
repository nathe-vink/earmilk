#!/usr/bin/env python3
"""Passive crossover design for any product in this repo: simulate a network, sum the drivers on a listening axis,
optimise the parts to target slopes, snap them to values you can buy, and draw it.

    .venv-fab/bin/python studio/xover/xover.py design.json [--optimize] [--out DIR]

A design file (JSON) holds the drivers, where they sit, the network and the targets. See studio/xover/README.md and
fab/crossover.py, which writes earmilk's. Units: mm, Hz, ohm, mH, uF, dB.

Drivers come from measurements when you have them (an FRD file of SPL and phase at 2.83 V, a ZMA file of impedance)
or, until then, from Thiele-Small parameters through a lumped model (cone, box, port, baffle step, voice coil
inductance). A model is a starting point, not a design: the network that ships is fitted to measurements.

Physics, briefly:
  * the network is solved by nodal analysis at every frequency; inductors carry their wire's resistance (DCR)
  * each driver's pressure = its response at 2.83 V x the voltage the network leaves across it, with its polarity and
    the delay from its acoustic centre to the listener; the system response is the complex sum
  * the optimiser fits each way to a Linkwitz-Riley (or Butterworth) acoustic target and the sum to flat, keeping the
    impedance above a floor; values move in log space within a decade of where they start
"""
import argparse, json, math, os, sys
import numpy as np

RHO, C_AIR, P_REF = 1.204, 343.0, 20e-6
E12 = [1.0, 1.2, 1.5, 1.8, 2.2, 2.7, 3.3, 3.9, 4.7, 5.6, 6.8, 8.2]
E24 = [1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4, 2.7, 3.0, 3.3, 3.6, 3.9, 4.3, 4.7, 5.1, 5.6, 6.2, 6.8, 7.5, 8.2, 9.1]
AWG_DCR = {14: 0.28, 15: 0.34, 16: 0.42, 18: 0.68, 20: 1.08}   # air-core DCR ~ k * sqrt(L in mH), ohm (typical)


def grid(f0=20.0, f1=20000.0, n=480):
    return np.geomspace(f0, f1, n)


# --- files -----------------------------------------------------------------------------------------------------------
def read_curve(path):
    """FRD or ZMA: lines of frequency, magnitude (dB or ohm), phase (degrees, optional). Comments start with * ; #."""
    rows = []
    for line in open(path):
        t = line.strip().replace(',', ' ').split()
        if not t or t[0][0] in '*;#"' or not _num(t[0]):
            continue
        rows.append([float(v) for v in t[:3]] + ([0.0] if len(t) < 3 else []))
    a = np.array(rows)
    return a[:, 0], a[:, 1], a[:, 2] if a.shape[1] > 2 else None


def write_curve(path, f, mag, phase_deg, header):
    with open(path, 'w') as fh:
        fh.write(f'* {header}\n')
        for a, b, c in zip(f, mag, phase_deg):
            fh.write(f'{a:.3f} {b:.4f} {c:.3f}\n')


def _num(s):
    try:
        float(s); return True
    except ValueError:
        return False


def minimum_phase(f, db):
    """Minimum phase (radians) for a magnitude response, by the folded real cepstrum on a linear grid."""
    fs, n = 96000.0, 1 << 16
    lin = np.linspace(0, fs / 2, n // 2 + 1)
    lf = np.log(np.maximum(f, 1e-3))
    mag = np.interp(np.log(np.maximum(lin, f[0])), lf, db)          # flat extension beyond the data
    logm = mag / 20.0 * np.log(10)
    cep = np.fft.irfft(logm, n)
    fold = np.zeros(n); fold[0] = cep[0]; fold[1:n // 2] = 2 * cep[1:n // 2]; fold[n // 2] = cep[n // 2]
    ph = np.imag(np.fft.rfft(fold, n))
    return np.interp(f, lin, ph)


# --- drivers ---------------------------------------------------------------------------------------------------------
def driver_response(d, f):
    """Complex pressure at 1 m for 2.83 V at the terminals (Pa), and complex impedance (ohm), on frequencies f."""
    if d.get('frd'):
        ff, db, ph = read_curve(d['frd'])
        mag = np.interp(np.log(f), np.log(ff), db)
        phase = np.deg2rad(np.interp(np.log(f), np.log(ff), ph)) if ph is not None and np.any(ph) else minimum_phase(f, mag)
        p = 10 ** (mag / 20) * P_REF * np.exp(1j * phase)
    else:
        p = None
    if d.get('zma'):
        ff, zm, zp = read_curve(d['zma'])
        Z = np.interp(np.log(f), np.log(ff), zm) * np.exp(1j * np.deg2rad(np.interp(np.log(f), np.log(ff), zp if zp is not None else 0 * ff)))
    else:
        Z = None
    if p is None or Z is None:
        pm, Zm = lumped(d, f)
        p = pm if p is None else p
        Z = Zm if Z is None else Z
    return p, Z


def lumped(d, f):
    """Thiele-Small lumped model. Box: infinite (tweeter), sealed or vented. Adds the baffle step, a high-frequency
    roll-off for cone breakup and beaming (`hf`: [f, Q]), and, for drivers with only Fs/Qts/sensitivity (tweeters),
    a second-order high-pass with the voice coil's inductance."""
    s = 1j * 2 * np.pi * f
    Re = d['Re']; Le = d.get('Le_mH', 0.0) * 1e-3
    Ze = Re + s * Le
    box = d.get('box', {'type': 'infinite'})
    if all(d.get(k) for k in ('Vas_l', 'Sd_cm2', 'Qms', 'Qes')):
        Sd = d['Sd_cm2'] * 1e-4
        Cms = d['Vas_l'] * 1e-3 / (RHO * C_AIR ** 2 * Sd ** 2)
        w = 2 * np.pi * d['Fs']; Mms = 1 / (w * w * Cms); Rms = w * Mms / d['Qms']; Bl = math.sqrt(w * Mms * Re / d['Qes'])
        Zmech = Rms + s * Mms + 1 / (s * Cms)
        if box['type'] == 'infinite':
            Zab = np.zeros_like(s); Map = None
        else:
            Cab = box['Vb_l'] * 1e-3 / (RHO * C_AIR ** 2)
            QL = box.get('QL', 7.0)
            if box['type'] == 'sealed':
                Zab = 1 / (s * Cab); Map = None
            else:
                Map = 1 / ((2 * np.pi * box['fb']) ** 2 * Cab); Z0 = math.sqrt(Map / Cab)
                Ral, Rap = QL * Z0, Z0 / box.get('QP', 60.0)
                Zab = 1 / (s * Cab + 1 / Ral + 1 / (s * Map + Rap))
        u = (Bl * 2.83 / Ze) / (Zmech + Bl ** 2 / Ze + Sd ** 2 * Zab)
        U = Sd * u
        if Map is not None:                                                  # the port's output joins the cone's
            pb = -Sd * u * Zab
            U = U + pb / (s * Map + Rap) + pb / Ral
        p = s * RHO * U / (2 * np.pi)                                         # half space, 1 m
        Z = Ze + Bl ** 2 / (Zmech + Sd ** 2 * Zab)
    else:                                                                     # a tweeter on its datasheet numbers
        x = f / d['Fs']; q = d.get('Qts', 0.7)
        hp = (1j * x) ** 2 / (1 + 1j * x / q + (1j * x) ** 2)
        p = 10 ** (d['sens_db'] / 20) * P_REF * hp * (Re / Ze)
        Qms, Qes = d.get('Qms', 2.0), d.get('Qes', q * 2.0 / max(2.0 - q, 1e-3))
        Res = Re * Qms / Qes
        Z = Ze + Res / (1 + 1j * Qms * (x - 1 / x))
    if d.get('baffle_mm'):                                                    # 2 pi to 4 pi: -6 dB below the step
        fb = 115.0 / (d['baffle_mm'] / 1000.0)
        p = p * (0.5 + 1j * f / fb) / (1 + 1j * f / fb)
    if d.get('hf'):
        f0, q = d['hf']; x = f / f0
        p = p / (1 + 1j * x / q + (1j * x) ** 2)
    if d.get('gain_db'):
        p = p * 10 ** (d['gain_db'] / 20)
    return p, Z


# --- network ---------------------------------------------------------------------------------------------------------
def element_admittance(e, w, drivers_Z):
    t = e['type']
    if t == 'R':
        return np.full_like(w, 1 / e['value'], dtype=complex)
    if t == 'L':
        return 1 / (e.get('dcr', 0.0) + 1j * w * e['value'] * 1e-3)
    if t == 'C':
        return 1 / (e.get('esr', 0.0) + 1 / (1j * w * e['value'] * 1e-6))
    if t == 'driver':
        return 1 / drivers_Z[e['driver']]
    raise ValueError(f'unknown element type {t}')


def solve(network, f, drivers_Z):
    """Nodal analysis with 'in' held at 1 (that is, 2.83 V) and '0' as ground. Returns node voltages, driver
    voltages and the input impedance."""
    w = 2 * np.pi * f
    nodes = sorted({n for e in network for n in e['nodes']} - {'in', '0'})
    ix = {n: i for i, n in enumerate(nodes)}
    F, N = len(f), len(nodes)
    Y = np.zeros((F, N, N), complex); I = np.zeros((F, N), complex)
    Iin = np.zeros(F, complex)
    adm = {}
    for e in network:
        y = element_admittance(e, w, drivers_Z); adm[e['id']] = y
        a, b = e['nodes']
        for p, q in ((a, b), (b, a)):
            if p in ix:
                Y[:, ix[p], ix[p]] += y
                if q in ix:
                    Y[:, ix[p], ix[q]] -= y
                elif q == 'in':
                    I[:, ix[p]] += y
    V = np.linalg.solve(Y, I[..., None])[..., 0] if N else np.zeros((F, 0), complex)
    volt = lambda n: np.ones(F, complex) if n == 'in' else (np.zeros(F, complex) if n == '0' else V[:, ix[n]])
    for e in network:
        a, b = e['nodes']
        if 'in' in (a, b):
            other = b if a == 'in' else a
            Iin += adm[e['id']] * (1 - volt(other))
    dv = {e['driver']: volt(e['nodes'][0]) - volt(e['nodes'][1]) for e in network if e['type'] == 'driver'}
    return dv, 1 / Iin


def delays(design):
    """Seconds from each driver's acoustic centre to the listener, minus the earliest."""
    L = design.get('listener', {'distance_mm': 2500, 'height_mm': 950})
    out = {}
    for name, d in design['drivers'].items():
        y = L['distance_mm'] + d.get('offset_mm', 0.0)                       # offset: acoustic centre behind the baffle
        z = L['height_mm'] - d.get('z_mm', L['height_mm'])
        x = d.get('x_mm', 0.0) - L.get('x_mm', 0.0)
        out[name] = math.sqrt(x * x + y * y + z * z) / 1000 / C_AIR
    t0 = min(out.values())
    return {k: v - t0 for k, v in out.items()}


def simulate(design, f=None):
    f = grid() if f is None else f
    resp = {k: driver_response(d, f) for k, d in design['drivers'].items()}
    dZ = {k: v[1] for k, v in resp.items()}
    dv, Zin = solve(design['network'], f, dZ)
    dl = delays(design)
    ways = {}
    for k, d in design['drivers'].items():
        pol = -1.0 if d.get('polarity', '+') == '-' else 1.0
        ways[k] = resp[k][0] * dv[k] * pol * np.exp(-1j * 2 * np.pi * f * dl[k])
    total = sum(ways.values())
    return {'f': f, 'ways': ways, 'sum': total, 'Zin': Zin, 'raw': {k: v[0] for k, v in resp.items()}, 'delays': dl}


def spl(p):
    return 20 * np.log10(np.maximum(np.abs(p), 1e-12) / P_REF)


# --- targets and optimisation ----------------------------------------------------------------------------------------
def target_shape(t, f):
    """Acoustic target magnitude (linear, complex) for a way: kind lp/hp/bp, crossover f, order, alignment."""
    def section(fc, kind, order, align):
        s = 1j * f / fc
        if align == 'LR':
            bw = section_bw(s, order // 2)
            h = bw * bw
        else:
            h = section_bw(s, order)
        return h if kind == 'lp' else h * s ** order
    def section_bw(s, order):
        if order == 1:
            return 1 / (1 + s)
        if order == 2:
            return 1 / (1 + math.sqrt(2) * s + s * s)
        if order == 3:
            return 1 / ((1 + s) * (1 + s + s * s))
        if order == 4:
            return 1 / ((1 + 0.7654 * s + s * s) * (1 + 1.8478 * s + s * s))
        raise ValueError(order)
    h = np.ones_like(f, dtype=complex)
    if t.get('hp'):
        h = h * section(t['hp'], 'hp', t.get('order', 4), t.get('align', 'LR'))
    if t.get('lp'):
        h = h * section(t['lp'], 'lp', t.get('order', 4), t.get('align', 'LR'))
    return h


def optimize(design, f=None, iters=400, verbose=True):
    from scipy.optimize import least_squares
    f = grid(20, 20000, 240) if f is None else f
    T = design['targets']
    level = T['level_db']
    free = [e for e in design['network'] if e['type'] in ('R', 'L', 'C') and not e.get('fixed')]
    x0 = np.log([e['value'] for e in free])
    lo = x0 - math.log(T.get('range', 10.0)); hi = x0 + math.log(T.get('range', 10.0))
    for i, e in enumerate(free):                                              # keep resistors sane
        if e['type'] == 'R':
            lo[i] = max(lo[i], math.log(0.1)); hi[i] = min(hi[i], math.log(100.0))
    band = (f >= T.get('sum_band', [150, 16000])[0]) & (f <= T.get('sum_band', [150, 16000])[1])
    resp = {k: driver_response(d, f) for k, d in design['drivers'].items()}
    dZ = {k: v[1] for k, v in resp.items()}
    dl = delays(design)
    shapes = {k: target_shape(t, f) for k, t in T['ways'].items()}
    zfloor = T.get('z_min', 3.2)

    def evaluate(x):
        for e, v in zip(free, np.exp(x)):
            e['value'] = float(v)
            if e['type'] == 'L' and e.get('awg'):
                e['dcr'] = AWG_DCR[e['awg']] * math.sqrt(e['value'])
        dv, Zin = solve(design['network'], f, dZ)
        ways = {}
        for k, d in design['drivers'].items():
            pol = -1.0 if d.get('polarity', '+') == '-' else 1.0
            ways[k] = resp[k][0] * dv[k] * pol * np.exp(-1j * 2 * np.pi * f * dl[k])
        return ways, Zin

    def residuals(x):
        ways, Zin = evaluate(x)
        r = []
        for k, t in T['ways'].items():
            want = level + 20 * np.log10(np.abs(shapes[k]))
            got = spl(ways[k])
            m = (want > level - 24) & (f >= t.get('from', 20)) & (f <= t.get('to', 20000))
            r.append(t.get('weight', 1.0) * (got - want)[m])
        tot = sum(ways.values())
        r.append(T.get('sum_weight', 2.0) * (spl(tot) - level)[band])
        r.append(T.get('z_weight', 30.0) * np.maximum(0, zfloor - np.abs(Zin)))
        return np.concatenate(r)

    res = least_squares(residuals, x0, bounds=(lo, hi), max_nfev=iters, x_scale=1.0, diff_step=1e-3)
    evaluate(res.x)
    if verbose:
        print(f'optimised {len(free)} parts: rms error {math.sqrt(np.mean(res.fun ** 2)):.2f} dB ({res.nfev} evaluations)')
    return res


def snap(design):
    """Values you can buy: capacitors E12 (uF), resistors E24 (ohm), inductors to 0.05 mH under 1 mH and 0.1 mH over."""
    def nearest(v, series):
        e = math.floor(math.log10(v)); best = None
        for k in (e - 1, e, e + 1):
            for s in series:
                c = s * 10 ** k
                if best is None or abs(math.log(c / v)) < abs(math.log(best / v)):
                    best = c
        return best
    for e in design['network']:
        if e['type'] == 'C':
            e['value'] = round(nearest(e['value'], E12), 3)
        elif e['type'] == 'R':
            e['value'] = round(nearest(e['value'], E24), 2)
        elif e['type'] == 'L':
            step = 0.05 if e['value'] < 1.0 else 0.1
            e['value'] = round(max(step, round(e['value'] / step) * step), 3)
            if e.get('awg'):
                e['dcr'] = round(AWG_DCR[e['awg']] * math.sqrt(e['value']), 3)


# --- output ----------------------------------------------------------------------------------------------------------
def plot(design, sim, path, title):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.ticker import FixedLocator, NullFormatter, FuncFormatter
    f = sim['f']; T = design.get('targets', {})
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(10, 8.2), gridspec_kw={'height_ratios': [3, 1.6]}, sharex=True)
    colors = ['#4a6fa5', '#c06c3e', '#5b8c5a', '#8e5b9e', '#9a9a9a']
    for (k, p), c in zip(sim['ways'].items(), colors):
        a1.semilogx(f, spl(p), color=c, lw=1.6, label=k)
        if T.get('ways', {}).get(k):
            a1.semilogx(f, T['level_db'] + 20 * np.log10(np.abs(target_shape(T['ways'][k], f))), color=c, lw=0.8, ls='--')
    a1.semilogx(f, spl(sim['sum']), color='#1d1d1f', lw=2.2, label='sum')
    lvl = T.get('level_db', float(np.median(spl(sim['sum']))))
    a1.set_ylim(lvl - 30, lvl + 9); a1.set_ylabel('SPL at 1 m, 2.83 V (dB)')
    a1.grid(True, which='both', color='#e4e4e4', lw=0.6); a1.legend(loc='lower right', ncol=2, frameon=False)
    a1.set_title(title, loc='left', fontsize=11)
    a2.semilogx(f, np.abs(sim['Zin']), color='#1d1d1f', lw=1.6)
    a2.set_ylabel('|Z| (ohm)'); a2.set_ylim(0, max(16, float(np.abs(sim['Zin']).max()) * 1.1))
    a2.grid(True, which='both', color='#e4e4e4', lw=0.6)
    ticks = [20, 50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000]
    a2.xaxis.set_major_locator(FixedLocator(ticks)); a2.xaxis.set_minor_formatter(NullFormatter())
    a2.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f'{v / 1000:g}k' if v >= 1000 else f'{v:g}'))
    a2.set_xlim(20, 20000); a2.set_xlabel('Frequency (Hz)')
    fig.tight_layout(); fig.savefig(path, dpi=130); fig.savefig(os.path.splitext(path)[0] + '.pdf'); plt.close(fig)


def parts_list(design, path):
    with open(path, 'w') as fh:
        fh.write('id,type,value,unit,between,note\n')
        for e in design['network']:
            if e['type'] == 'driver':
                continue
            unit = {'R': 'ohm', 'L': 'mH', 'C': 'uF'}[e['type']]
            note = {'R': '10 W wirewound or metal oxide', 'C': 'polypropylene film, 100 V or more',
                    'L': f"air core, {e.get('awg', 18)} AWG, DCR about {e.get('dcr', 0):.2f} ohm"}[e['type']]
            fh.write(f"{e['id']},{e['type']},{e['value']:g},{unit},{e['nodes'][0]}-{e['nodes'][1]},{note}\n")


def summary(design, sim):
    f = sim['f']; Z = np.abs(sim['Zin'])
    band = (f >= 150) & (f <= 16000)
    s = spl(sim['sum'])
    return {'sum_band_db': [round(float(s[band].min()), 1), round(float(s[band].max()), 1)],
            'z_min_ohm': round(float(Z[(f > 20)].min()), 2), 'z_min_at_hz': round(float(f[np.argmin(Z)]), 0),
            'delays_ms': {k: round(v * 1000, 3) for k, v in sim['delays'].items()}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('design'); ap.add_argument('--optimize', action='store_true'); ap.add_argument('--out', default=None)
    a = ap.parse_args()
    design = json.load(open(a.design))
    base = os.path.dirname(os.path.abspath(a.design))
    for d in design['drivers'].values():
        for k in ('frd', 'zma'):
            if d.get(k) and not os.path.isabs(d[k]):
                d[k] = os.path.join(base, d[k])
    out = a.out or os.path.join(base, 'xover-out'); os.makedirs(out, exist_ok=True)
    if a.optimize:
        optimize(design); snap(design)
    sim = simulate(design)
    plot(design, sim, os.path.join(out, 'response.png'), design.get('title', 'crossover'))
    parts_list(design, os.path.join(out, 'parts.csv'))
    json.dump({**design, 'result': summary(design, sim)}, open(os.path.join(out, 'design-out.json'), 'w'), indent=1)
    print(json.dumps(summary(design, sim)))


if __name__ == '__main__':
    main()
