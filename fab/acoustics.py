"""The acoustic worksheet: the woofer box from the CAD, the port for 32 Hz, and a vented-box simulation of each candidate
driver in fab/drivers.json. Proposals for the README's open question, not decisions.

    /root/.venvs/fab/bin/python fab/acoustics.py      (after fab/cad.py, which measures the air)

Model: the standard lumped-element vented box (Thiele and Small): the driver from its published Thiele-Small
parameters, the box as a compliance, the port as an acoustic mass, leakage losses QL = 7, radiation into half space
(the way sensitivity is quoted), 2.83 V in. It predicts the bass response, cone excursion and port air speed well
below the baffle step; above a few hundred hertz the real baffle, the room and the crossover take over.

Writes out/acoustics.json and three charts in out/acoustics/; fab/README.md carries the numbers in words.
"""
import json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from params import *  # noqa: F401,F403
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'out')
RHO, C = 1.204, 343.0
FB_TARGET = 32.0          # README target tuning
QL = 7.0                  # box leakage losses, a typical well-built box
QP = 60.0                 # port losses
END_CORR = 0.732          # end correction x port diameter: one flanged end (the outside flange) and one free end
BAFFLE_W = PLAN / 1000.0  # 390 mm baffle: the baffle step sits near 115 / W = 295 Hz


def load_drivers():
    return json.load(open(os.path.join(HERE, 'drivers.json')))


def sens_2v83(d):
    """Sensitivity at 2.83 V / 1 m. Datasheets quote either 2.83 V or 1 W into the nominal impedance."""
    s = d['sens_db']
    if d.get('sens_ref', '2.83V').upper().startswith('1W'):
        s += 10 * math.log10(8.0 / d['nominal_ohm'])
    return s


def mech(d):
    Sd = d['Sd_cm2'] * 1e-4
    Cms = d['Vas_l'] * 1e-3 / (RHO * C * C * Sd * Sd)
    w = 2 * math.pi * d['Fs']
    Mms = 1.0 / (w * w * Cms)
    Rms = w * Mms / d['Qms']
    Bl = math.sqrt(w * Mms * d['Re'] / d['Qes'])
    return dict(Sd=Sd, Cms=Cms, Mms=Mms, Rms=Rms, Bl=Bl, Re=d['Re'], Le=d.get('Le_mH', 0.0) * 1e-3)


def port_length_mm(Vb_l, fb=FB_TARGET, bore_mm=PORT['bore']):
    """Physical port length for tuning fb in Vb litres with a round port of the given bore."""
    Sp = math.pi * (bore_mm / 2000) ** 2
    w = 2 * math.pi * fb
    Leff = Sp * C * C / (w * w * Vb_l * 1e-3)
    return (Leff - END_CORR * bore_mm / 1000) * 1000, Leff * 1000


def simulate(d, Vb_l, fb=FB_TARGET, volts=2.83, f=None):
    """Returns frequency, SPL at 1 m (half space), cone excursion (peak, mm), port air speed (peak, m/s), |Z| (ohm)."""
    m = mech(d)
    f = np.geomspace(10, 1000, 400) if f is None else np.asarray(f, float)
    s = 1j * 2 * np.pi * f
    Vb = Vb_l * 1e-3
    Cab = Vb / (RHO * C * C)
    Map = 1.0 / ((2 * math.pi * fb) ** 2 * Cab)
    Z0 = math.sqrt(Map / Cab)
    Ral, Rap = QL * Z0, Z0 / QP
    Sp = math.pi * (PORT['bore'] / 2000) ** 2
    Ze = m['Re'] + s * m['Le']
    F = m['Bl'] * volts / Ze
    Zab = 1.0 / (s * Cab + 1.0 / Ral + 1.0 / (s * Map + Rap))
    Zmech = m['Rms'] + s * m['Mms'] + 1.0 / (s * m['Cms'])
    u = F / (Zmech + m['Bl'] ** 2 / Ze + m['Sd'] ** 2 * Zab)
    pb = -m['Sd'] * u * Zab
    Up = pb / (s * Map + Rap)
    Ul = pb / Ral
    U = m['Sd'] * u + Up + Ul
    p = s * RHO * U / (2 * np.pi * 1.0)              # half space, 1 m, RMS (the drive is RMS)
    spl = 20 * np.log10(np.abs(p) / 20e-6)
    x_pk = np.abs(u / s) * math.sqrt(2) * 1000        # mm
    v_pk = np.abs(Up) / Sp * math.sqrt(2)              # m/s
    Zin = np.abs(Ze + m['Bl'] ** 2 / (Zmech + m['Sd'] ** 2 * Zab))
    return f, spl, x_pk, v_pk, Zin


def f3(f, spl, ref):
    """Lowest frequency where the response is within 3 dB of `ref` (searching up from the bottom)."""
    idx = np.where(spl >= ref - 3.0)[0]
    return float(f[idx[0]]) if len(idx) else float('nan')


def max_output(d, Vb_l, fb=FB_TARGET):
    """Largest clean level at each frequency: the lower of the excursion limit (Xmax) and the thermal limit (rated
    power into Re). Returns frequency, max SPL, the port air speed at that level."""
    f, spl1, x1, v1, Z = simulate(d, Vb_l, fb, volts=1.0)
    v_thermal = math.sqrt(d['Pe_w'] * d['Re'])
    v_xmax = d['Xmax_mm'] / x1
    volts = np.minimum(v_xmax, v_thermal)
    return f, spl1 + 20 * np.log10(volts), v1 * volts


def mid_box(d, Vb_l):
    a = d['Vas_l'] / Vb_l
    return d['Qts'] * math.sqrt(1 + a), d['Fs'] * math.sqrt(1 + a)


def main():
    cad = json.load(open(os.path.join(OUT, 'cad.json')))
    drv = load_drivers()
    air = cad['woofer_chamber_air_l']
    mid_gross = cad['mid_chamber_gross_l']
    res = {'woofer_chamber_air_l': air, 'fb_target_hz': FB_TARGET, 'woofers': [], 'mids': [], 'tweeters': []}
    for d in drv['woofers']:
        Vb = air - d.get('displacement_l', 4.0)
        L, Leff = port_length_mm(Vb)
        f, spl, x, v, Z = simulate(d, Vb)
        ref = float(np.median(spl[(f > 150) & (f < 300)]))
        fo, mx, vmx = max_output(d, Vb)
        band = (fo >= 25) & (fo <= 80)
        res['woofers'].append(dict(
            id=d['id'], label=f"{d['maker']} {d['model']}", Vb_net_l=round(Vb, 1), port_length_mm=round(L, 1),
            sens_2v83_datasheet=round(sens_2v83(d), 1), sim_midband_2pi_db=round(ref, 1),
            f3_hz=round(f3(f, spl, ref), 1), f10_hz=round(float(f[np.where(spl >= ref - 10)[0][0]]), 1),
            max_spl_40hz_db=round(float(np.interp(40, fo, mx)), 1), max_spl_30hz_db=round(float(np.interp(30, fo, mx)), 1),
            port_speed_at_max_25_80hz_ms=round(float(vmx[band].max()), 1),
            z_min_ohm=round(float(Z[(f > 20) & (f < 300)].min()), 2), price_usd=d.get('price_usd'), url=d.get('url')))
    for d in drv.get('mids', []):
        Vb = mid_gross - d.get('displacement_l', 0.6)
        qtc, fc = mid_box(d, Vb)
        res['mids'].append(dict(id=d['id'], label=f"{d['maker']} {d['model']}", Vb_l=round(Vb, 1), Qtc=round(qtc, 2),
                                Fc_hz=round(fc, 0), sens_2v83=round(sens_2v83(d), 1), price_usd=d.get('price_usd'), url=d.get('url')))
    for d in drv.get('tweeters', []):
        res['tweeters'].append(dict(id=d['id'], label=f"{d['maker']} {d['model']}", Fs=d['Fs'], sens_2v83=round(sens_2v83(d), 1),
                                    faceplate_mm=d.get('faceplate_mm'), price_usd=d.get('price_usd'), url=d.get('url')))
    rec = drv.get('recommended_woofer') or res['woofers'][0]['id']
    pick = next(w for w in res['woofers'] if w['id'] == rec)
    total = pick['port_length_mm']
    res['port'] = {'for_woofer': rec, 'Vb_net_l': pick['Vb_net_l'], 'total_length_mm': total,
                   'tube_length_mm': round(total - PORT_FLARE_R, 1), 'tube_length_note':
                   'the printed tube runs from the flange face to the collar; the flare collar adds 18 mm. Print it 10 mm long, '
                   'measure the impedance dip, and trim to put it at 32 Hz.'}
    res['port']['tube_length_mm_for_cad'] = res['port']['tube_length_mm']
    charts(drv, res, air)
    json.dump(res, open(os.path.join(OUT, 'acoustics.json'), 'w'), indent=1)
    print(json.dumps({k: v for k, v in res.items() if k in ('port',)}, indent=1))
    for w in res['woofers']:
        print(w)
    for mm in res['mids']:
        print(mm)


def charts(drv, res, air):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.ticker import NullFormatter, FixedLocator, FixedFormatter
    os.makedirs(os.path.join(OUT, 'acoustics'), exist_ok=True)
    SERIES = ['#2a78d6', '#eb6834', '#1baf7a', '#eda100']   # reference palette slots 1-4, validated for light mode
    INK, INK2, GRID, SURF = '#0b0b0b', '#52514e', '#e4e3df', '#fcfcfb'
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10, 'axes.edgecolor': GRID, 'axes.labelcolor': INK2,
                         'xtick.color': INK2, 'ytick.color': INK2, 'axes.facecolor': SURF, 'figure.facecolor': SURF})
    woofers = drv['woofers'][:4]
    names = [f"{d['maker']} {d['model']}" for d in woofers]

    def frame(ax, title, ylabel, ticks=(20, 30, 40, 50, 100, 200, 300, 500), xmax=500):
        ax.set_xscale('log'); ax.set_xlim(15, xmax)
        ax.xaxis.set_major_locator(FixedLocator(ticks)); ax.xaxis.set_major_formatter(FixedFormatter([str(t) for t in ticks]))
        ax.xaxis.set_minor_formatter(NullFormatter())
        ax.grid(True, which='major', color=GRID, lw=0.8); ax.grid(False, which='minor')
        for sp in ('top', 'right'):
            ax.spines[sp].set_visible(False)
        ax.set_xlabel('Frequency (Hz)'); ax.set_ylabel(ylabel)
        ax.set_title(title, loc='left', color=INK, fontsize=12, pad=12)

    def end_labels(ax, ys, labels, colors, x):
        lo, hi = ax.get_ylim(); gap = 0.055 * (hi - lo)
        order = list(np.argsort(ys))
        pos = [ys[i] for i in order]
        for k in range(1, len(pos)):              # push labels apart, bottom up
            pos[k] = max(pos[k], pos[k - 1] + gap)
        for k, i in enumerate(order):
            ax.annotate(labels[i], xy=(x, ys[i]), xytext=(x * 1.06, pos[k]), fontsize=9, color=INK, va='center',
                        annotation_clip=False, arrowprops=dict(arrowstyle='-', color=colors[i], lw=0.8))

    def curves(fn):
        out = []
        for d in woofers:
            out.append(fn(d, air - d.get('displacement_l', 4.0)))
        return out

    # 1. Response in the box at 2.83 V.
    fig, ax = plt.subplots(figsize=(9, 5.2)); fig.subplots_adjust(right=0.72)
    data = curves(lambda d, Vb: simulate(d, Vb)[:2])
    for i, (f, spl) in enumerate(data):
        ax.plot(f, spl, color=SERIES[i], lw=2, label=names[i])
    ax.set_ylim(60, 100)
    ax.axvline(FB_TARGET, color=INK2, lw=0.8, ls=(0, (3, 3)))
    ax.text(FB_TARGET * 1.03, 61.5, 'port tuned to 32 Hz', color=INK2, fontsize=8)
    frame(ax, 'Each woofer in the 88 L box: bass at 2.83 V, 1 m, half space', 'Sound level (dB)')
    end_labels(ax, [float(np.interp(500, f, s)) for (f, s) in data], names, SERIES, 500)
    ax.legend(loc='lower right', frameon=False, fontsize=8)
    fig.savefig(os.path.join(OUT, 'acoustics', 'woofer-response.png'), dpi=150); plt.close(fig)

    # 2. Largest clean level (limited by excursion or heat).
    fig, ax = plt.subplots(figsize=(9, 5.2)); fig.subplots_adjust(right=0.72)
    data = curves(lambda d, Vb: max_output(d, Vb)[:2])
    for i, (f, mx) in enumerate(data):
        ax.plot(f, mx, color=SERIES[i], lw=2, label=names[i])
    ax.set_ylim(70, 120)
    frame(ax, 'Loudest clean bass, before the cone runs out of travel or overheats', 'Max sound level (dB at 1 m)')
    end_labels(ax, [float(np.interp(500, f, m)) for (f, m) in data], names, SERIES, 500)
    ax.legend(loc='lower right', frameon=False, fontsize=8)
    fig.savefig(os.path.join(OUT, 'acoustics', 'woofer-max-output.png'), dpi=150); plt.close(fig)

    # 3. Port air speed for the recommended woofer, at its loudest clean level and at a loud 100 dB.
    rec = next(d for d in woofers if d['id'] == drv.get('recommended_woofer', woofers[0]['id']))
    Vb = air - rec.get('displacement_l', 4.0)
    f, mx, vmx = max_output(rec, Vb)
    f1, spl1, x1, v1, _ = simulate(rec, Vb, volts=1.0)
    ref1 = float(np.median(spl1[(f1 > 150) & (f1 < 300)]))
    v100 = v1 * 10 ** ((100 - ref1) / 20)
    fig, ax = plt.subplots(figsize=(9, 5.2)); fig.subplots_adjust(right=0.95)
    ax.plot(f, vmx, color=SERIES[0], lw=2, label='at its loudest clean level')
    ax.plot(f1, v100, color=SERIES[1], lw=2, label='at 100 dB, loud listening')
    ax.set_ylim(0, 32)
    ax.axhline(17, color=INK2, lw=0.8, ls=(0, (3, 3))); ax.text(16, 17.5, 'about 17 m/s: a plain port starts to chuff', color=INK2, fontsize=8)
    ax.axhline(25, color=INK2, lw=0.8, ls=(0, (1, 2))); ax.text(16, 25.5, 'about 25 m/s: the limit for a flared port', color=INK2, fontsize=8)
    frame(ax, f"Port air speed, 92 mm flared port, {rec['maker']} {rec['model']}", 'Peak air speed (m/s)',
          ticks=(20, 30, 40, 50, 100, 200), xmax=200)
    pk = float(np.interp(30, f, vmx)); pk100 = float(np.interp(30, f1, v100))
    ax.text(36, pk - 0.4, f'loudest clean level: peaks near {pk:.0f} m/s', color=INK, fontsize=9, va='top')
    ax.text(58, 4.2, f'100 dB at 1 m: peaks near {pk100:.0f} m/s', color=INK, fontsize=9, va='center')
    ax.legend(loc='upper right', frameon=False, fontsize=8)
    fig.savefig(os.path.join(OUT, 'acoustics', 'port-speed.png'), dpi=150); plt.close(fig)
    res['port']['speed_at_100db_peak_ms'] = round(float(v100[(f1 >= 25) & (f1 <= 80)].max()), 1)


def simulate_port_curve(d, air):
    f, mx, vmx = max_output(d, air - d.get('displacement_l', 4.0))
    return f, vmx


if __name__ == '__main__':
    main()
