"""Bass boxes from Thiele-Small parameters: the standard lumped-element model (the driver as published, the box as a
compliance, a port as an acoustic mass, leakage QL = 7, radiation into half space, 2.83 V in), ported from earmilk's
fab/acoustics.py. It predicts the bass response, cone excursion and port air speed well below the baffle step.

    from speaker.box import vented, sealed, port_length_mm, suggest_vented
    r = vented(drv, Vb_l=80, fb=32, port_bore_mm=92)      # {'f3', 'port_mm', 'spl', 'x_pk', 'v_port', 'max_spl', ...}

A driver is a dict with Fs, Qts, Qes, Qms, Vas_l, Re, Sd_cm2, Xmax_mm, Pe_w, sens_db (and optionally Le_mH, sens_ref
'2.83V' or '1W', nominal_ohm).
"""
import math

import numpy as np

RHO, C = 1.204, 343.0
QL, QP = 7.0, 60.0
END_CORR = 0.732          # x the port's diameter: one flanged end and one free


def mech(d):
    Sd = d['Sd_cm2'] * 1e-4
    Cms = d['Vas_l'] * 1e-3 / (RHO * C * C * Sd * Sd)
    w = 2 * math.pi * d['Fs']
    Mms = 1.0 / (w * w * Cms)
    Rms = w * Mms / d['Qms']
    Bl = math.sqrt(w * Mms * d['Re'] / d['Qes'])
    return dict(Sd=Sd, Cms=Cms, Mms=Mms, Rms=Rms, Bl=Bl, Re=d['Re'], Le=d.get('Le_mH', 0.0) * 1e-3)


def port_length_mm(Vb_l, fb, bore_mm):
    """Physical length of a round port of `bore_mm` tuning Vb litres to fb."""
    Sp = math.pi * (bore_mm / 2000) ** 2
    w = 2 * math.pi * fb
    Leff = Sp * C * C / (w * w * Vb_l * 1e-3)
    return (Leff - END_CORR * bore_mm / 1000) * 1000


def _response(d, Vb_l, fb=None, bore_mm=92.0, volts=2.83, f=None):
    m = mech(d)
    f = np.geomspace(10, 1000, 400) if f is None else np.asarray(f, float)
    s = 1j * 2 * np.pi * f
    Vb = Vb_l * 1e-3
    Cab = Vb / (RHO * C * C)
    Ze = m['Re'] + s * m['Le']
    F = m['Bl'] * volts / Ze
    Zmech = m['Rms'] + s * m['Mms'] + 1.0 / (s * m['Cms'])
    if fb:
        Map = 1.0 / ((2 * math.pi * fb) ** 2 * Cab)
        Z0 = math.sqrt(Map / Cab)
        Ral, Rap = QL * Z0, Z0 / QP
        Zab = 1.0 / (s * Cab + 1.0 / Ral + 1.0 / (s * Map + Rap))
    else:
        Ral = QL * 50 / (2 * math.pi * 30 * Cab)
        Zab = 1.0 / (s * Cab + 1.0 / Ral)
    u = F / (Zmech + m['Bl'] ** 2 / Ze + m['Sd'] ** 2 * Zab)
    pb = -m['Sd'] * u * Zab
    U = m['Sd'] * u + pb / Ral
    v_port = np.zeros_like(f)
    if fb:
        Up = pb / (s * Map + Rap)
        U = U + Up
        v_port = np.abs(Up) / (math.pi * (bore_mm / 2000) ** 2) * math.sqrt(2)
    p = s * RHO * U / (2 * np.pi * 1.0)
    spl = 20 * np.log10(np.abs(p) / 20e-6)
    x_pk = np.abs(u / s) * math.sqrt(2) * 1000
    return f, spl, x_pk, v_port


def f3(f, spl, ref):
    idx = np.where(spl >= ref - 3.0)[0]
    return float(f[idx[0]]) if len(idx) else float('nan')


def _summary(d, Vb_l, fb, bore_mm):
    f, spl, x, v = _response(d, Vb_l, fb, bore_mm)
    ref = float(np.median(spl[(f > 150) & (f < 400)]))
    f1, s1, x1, v1 = _response(d, Vb_l, fb, bore_mm, volts=1.0)
    v_th = math.sqrt(d.get('Pe_w', 100) * d['Re'])
    volts = np.minimum(d['Xmax_mm'] / np.maximum(x1, 1e-9), v_th)
    maxspl = s1 + 20 * np.log10(volts)
    at = lambda arr, hz: float(np.interp(hz, f, arr))
    out = dict(Vb_l=round(Vb_l, 1), fb=fb, f3=round(f3(f, spl, ref), 1), ref_db=round(ref, 1),
               max_spl_db={hz: round(at(maxspl, hz), 1) for hz in (30, 40, 50, 80)})
    if fb:
        out['port_bore_mm'] = bore_mm
        out['port_mm'] = round(port_length_mm(Vb_l, fb, bore_mm), 1)
        out['port_air_m_s_at_max'] = round(float(np.max(v1 * volts)), 1)
    return out


def vented(d, Vb_l, fb, bore_mm=92.0):
    return _summary(d, Vb_l, fb, bore_mm)


def sealed(d, Vb_l):
    a = d['Vas_l'] / Vb_l
    r = _summary(d, Vb_l, None, 0)
    r.update(Qtc=round(d['Qts'] * math.sqrt(1 + a), 3), fc=round(d['Fs'] * math.sqrt(1 + a), 1))
    return r


def suggest_vented(d):
    """A starting alignment (Keele's QB3-like rule of thumb): Vb = 15 Vas Qts^2.87, fb = 0.42 Fs Qts^-0.9."""
    Vb = 15 * d['Vas_l'] * d['Qts'] ** 2.87
    fb = 0.42 * d['Fs'] * d['Qts'] ** -0.9
    return round(Vb, 1), round(fb, 1)
