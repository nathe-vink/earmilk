"""Horns and waveguides as solids: a profile r(x) from throat to mouth, a wall of some thickness, a flange at the
throat for the driver and an optional rolled lip at the mouth. Round horns are revolved; rectangular ones lofted
between their sections.

Profiles (x from the throat, r the half width, mm):
  conical(r0, angle_deg, L)                 straight walls
  exponential(r0, fc, L)                    r = r0 e^(m x / 2), m = 4 pi fc / c: loads the driver down to fc
  tractrix(fc, r0)                          the mouth radius c / (2 pi fc), the length set by r0 (the classic shape)
  os(r0, angle_deg, L)                      oblate-spheroidal waveguide: r = sqrt(r0^2 + (x tan a)^2), constant
                                            directivity to its coverage angle, the throat's slope continuous

    from speaker.horn import tractrix, round_horn, rect_horn
    prof = tractrix(fc=500, r0=12.7)
    shell = round_horn(prof, wall=4, flange=dict(d=110, t=10, bolt_d=76, bolts=4, bolt_hole=6.5), lip=12)

The shell's local frame: the axis is z, the throat at z = 0, the mouth at z = L (place it with speaker.drivers.place).
Nothing here simulates: a horn's real response wants a BEM run (earmilk's fab/bem.py does that for its waveguide).
"""
import math

import numpy as np
from build123d import Axis, Polyline, Pos, loft, make_face, revolve, Wire, Sketch, Plane, Rectangle, Solid, Cylinder, Align

C_MM = 343000.0


def conical(r0, angle_deg, L, n=40):
    t = math.tan(math.radians(angle_deg / 2))
    return [(x, r0 + x * t) for x in np.linspace(0, L, n)]


def exponential(r0, fc, L, n=60):
    m = 4 * math.pi * fc / C_MM
    return [(x, r0 * math.exp(m * x / 2)) for x in np.linspace(0, L, n)]


def tractrix(fc, r0, n=80):
    """The tractrix from a throat radius r0 to its mouth radius rm = c / (2 pi fc), where the wall turns square to the
    axis. x is measured from the throat."""
    rm = C_MM / (2 * math.pi * fc)
    if r0 >= rm:
        raise ValueError(f'throat radius {r0} is not smaller than the mouth {rm:.0f} for {fc} Hz')
    def xm(r):           # distance back from the mouth plane for radius r
        s = math.sqrt(max(rm * rm - r * r, 0.0))
        return rm * math.log((rm + s) / r) - s
    L = xm(r0)
    rs = np.geomspace(r0, rm * 0.999, n)
    return [(L - xm(r), r) for r in rs]


def os(r0, angle_deg, L, n=50):
    t = math.tan(math.radians(angle_deg / 2))
    return [(x, math.sqrt(r0 * r0 + (x * t) ** 2)) for x in np.linspace(0, L, n)]


def _clean(pts):
    out = []
    for q in pts:
        if not out or abs(q[0] - out[-1][0]) > 1e-6 or abs(q[1] - out[-1][1]) > 1e-6:
            out.append(q)
    return out


def round_horn(profile, wall=4.0, flange=None, lip=0.0):
    """A revolved horn shell: the inner surface on `profile` [(x, r)], `wall` thick (measured square to the axis),
    a throat flange (dict d, t, and optionally bolt_d, bolts, bolt_hole) and a lip rolled outward at the mouth of
    radius `lip` (0: a plain cut edge)."""
    prof = _clean([(r, x) for x, r in profile])
    outer = [(r + wall, x) for r, x in prof]
    if lip > 0:
        rm, xm = prof[-1]
        arc = [(rm + lip - lip * math.cos(a), xm + lip * math.sin(a)) for a in np.linspace(0, math.pi / 2, 10)][1:]
        arc_o = [(rm + lip + wall - (lip + wall) * math.cos(a), xm + (lip + wall) * math.sin(a)) for a in np.linspace(0, math.pi / 2, 10)][1:]
        # the lip curls out and back: inner surface onto the arc, the outer one round its outside
        inner = prof + arc
        outer = outer + arc_o
        loop = inner + [(inner[-1][0], inner[-1][1] + wall)] + list(reversed(outer))
    else:
        loop = prof + list(reversed(outer))
    face = make_face(Polyline(*[(r, 0.0, z) for r, z in loop], close=True))
    shell = revolve(face, Axis.Z, 360)
    if flange:
        r0 = prof[0][0]
        fl = Cylinder(flange['d'] / 2, flange['t'], align=(Align.CENTER, Align.CENTER, Align.MIN)) - \
             Cylinder(r0, flange['t'] + 1, align=(Align.CENTER, Align.CENTER, Align.MIN))
        if flange.get('bolts'):
            for k in range(flange['bolts']):
                a = 2 * math.pi * (k + 0.5) / flange['bolts']
                fl = fl - Pos(flange['bolt_d'] / 2 * math.cos(a), flange['bolt_d'] / 2 * math.sin(a), -0.5) * \
                     Cylinder(flange['bolt_hole'] / 2, flange['t'] + 1, align=(Align.CENTER, Align.CENTER, Align.MIN))
        shell = shell + fl
    return shell


def rect_horn(profile_w, profile_h, wall=4.0, n_sections=12, flange=None):
    """A rectangular horn: half widths from `profile_w` [(x, half width)] and half heights from `profile_h` [(x, half
    height)] (sampled at the same x), the shell lofted between rectangular sections, `wall` thick."""
    xs = np.linspace(profile_w[0][0], profile_w[-1][0], n_sections)
    hw = np.interp(xs, [p[0] for p in profile_w], [p[1] for p in profile_w])
    hh = np.interp(xs, [p[0] for p in profile_h], [p[1] for p in profile_h])
    def body(grow):
        secs = [Plane.XY.offset(x) * Rectangle(2 * (w + grow), 2 * (h + grow)) for x, w, h in zip(xs, hw, hh)]
        return loft(secs)
    shell = body(wall) - body(0.0)
    if flange:
        fl = Pos(0, 0, 0) * Cylinder(flange['d'] / 2, flange['t'], align=(Align.CENTER, Align.CENTER, Align.MIN))
        shell = shell + (fl - body(0.0))
    return shell


def mouth_for_coverage(fc, angle_deg):
    """The mouth width (mm) a horn needs to hold its coverage `angle_deg` down to fc Hz: Keele's rule (AES preprint
    1038, 1975), W = 25e3 / (theta f) metres; a 90 degree horn holds to 1 kHz with a 278 mm mouth."""
    return 25.0e6 / (angle_deg * fc)
