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

The shell's local frame: the axis is z, the throat at z = 0, the mouth at z = L, the driver's flange behind the throat
at z = -t (place it with speaker.drivers.place). The wall is offset along its normal and the lip rolls back over the
outside, so a tractrix (square to the axis at its mouth) keeps its full wall.
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


def shell_profile(profile, wall=4.0, lip=0.0):
    """The horn's wall in its (x, r) half plane: the inner (air) surface along `profile` [(x, r)], throat to mouth,
    then, if `lip` > 0, rolled back over the outside on a quarter-plus arc of radius `lip` (as a trumpet's bell: from
    the mouth's slope round until it points back toward the throat), and the outer surface `wall` away along the
    surface's normal (not straight out from the axis: a tractrix's wall turns square to the axis at its mouth, where
    a radial offset would leave no wall at all). Returns (inner, outer), each [(x, r)] from the throat."""
    P = np.array(_clean([(float(x), float(r)) for x, r in profile]))
    inner = [tuple(q) for q in P]
    if lip > 0:
        assert lip > wall + 1.0, f'the lip ({lip}) must be wider than the wall ({wall}) to roll round it'
        t = P[-1] - P[-2]; t /= np.linalg.norm(t)
        a0 = math.atan2(t[1], t[0])                     # the mouth's slope, from the axis
        nl = np.array([-t[1], t[0]])                    # left of the way along: into the wall
        c = P[-1] + lip * nl
        for ph in np.linspace(a0 - math.pi / 2, math.pi / 2, 16)[1:]:
            inner.append((c[0] + lip * math.cos(ph), c[1] + lip * math.sin(ph)))
    I = np.array(inner)
    T = np.gradient(I, axis=0); T /= np.linalg.norm(T, axis=1, keepdims=True)
    N = np.c_[-T[:, 1], T[:, 0]]
    outer = [tuple(q) for q in I + wall * N]
    return inner, outer


def round_horn(profile, wall=4.0, flange=None, lip=0.0, liner=0.0):
    """A revolved horn shell: the inner surface on `profile` [(x, r)] (x from the throat), `wall` thick along its
    normal, its mouth rolled back on a lip of radius `lip` (0: a plain edge), and a throat flange behind the throat
    (dict d, t, and optionally bolt_d, bolts, bolt_hole): the driver bolts to its back face, at z = -t. Local frame:
    the axis is z, the throat at z = 0, the mouth toward +z. Each surface is a spline, so it draws and renders smooth.
    With `liner` > 0 it returns (shell, liner): a skin that thick just inside the air surface, for painting the bell's
    inside apart from its outside in a render."""
    from geom import revolve_profile
    inner, outer = shell_profile(profile, wall, lip)
    n = len(inner)
    pts = [(r, x) for x, r in inner] + [(r, x) for x, r in reversed(outer)]
    shell = revolve_profile(pts, axis='z', smooth=[(0, n - 1), (n, 2 * n - 1)])
    if flange:
        r0 = inner[0][1]
        fl = Pos(0, 0, -flange['t']) * (Cylinder(flange['d'] / 2, flange['t'], align=(Align.CENTER, Align.CENTER, Align.MIN)) -
                                        Cylinder(r0, flange['t'] + 1, align=(Align.CENTER, Align.CENTER, Align.MIN)))
        if flange.get('bolts'):
            for k in range(flange['bolts']):
                a = 2 * math.pi * (k + 0.5) / flange['bolts']
                fl = fl - Pos(flange['bolt_d'] / 2 * math.cos(a), flange['bolt_d'] / 2 * math.sin(a), -flange['t'] - 0.5) * \
                     Cylinder(flange['bolt_hole'] / 2, flange['t'] + 1, align=(Align.CENTER, Align.CENTER, Align.MIN))
        shell = shell + fl
    if liner > 0:
        I = np.array(inner)
        T = np.gradient(I, axis=0); T /= np.linalg.norm(T, axis=1, keepdims=True)
        Ni = I - liner * np.c_[-T[:, 1], T[:, 0]]       # a skin on the air side
        lp = [(r, x) for x, r in I] + [(r, x) for x, r in reversed(Ni)]
        return shell, revolve_profile(lp, axis='z', smooth=[(0, n - 1), (n, 2 * n - 1)])
    return shell


def outer_radius_at(profile, x, wall=4.0, lip=0.0):
    """The shell's outside radius at axial position x (from the throat), for a saddle or a clamp, ignoring the rolled
    lip's return (the largest r of the outer surface at that x)."""
    _, outer = shell_profile(profile, wall, lip)
    O = np.array(outer)
    best = None
    for (x0, r0), (x1, r1) in zip(O[:-1], O[1:]):
        if (x0 - x) * (x1 - x) <= 0 and abs(x1 - x0) > 1e-9:
            r = r0 + (r1 - r0) * (x - x0) / (x1 - x0)
            best = r if best is None else max(best, r)
    return best


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


def _se_wire(w, h, n, z, pts=72):
    """A closed superellipse |x/w|^n + |y/h|^n = 1 at height z, as one periodic spline (one smooth face when lofted:
    no seams at the corners, as a rounded rectangle's straight-and-arc edges leave)."""
    from build123d import Edge, Wire, Vector
    P = []
    for k in range(pts):
        t = 2 * math.pi * k / pts
        c, s_ = math.cos(t), math.sin(t)
        P.append(Vector(w * math.copysign(abs(c) ** (2 / n), c), h * math.copysign(abs(s_) ** (2 / n), s_), z))
    return Wire([Edge.make_spline(P, periodic=True)])


def _se_sections(r0, half_w, half_h, depth, n_mouth=4.5, n=12, beyond=0.0, grow=0.0, z0=0.0, before=0.0):
    """Superellipse sections of a rectangular waveguide: round at the throat (n = 2, radius r0), each half dimension
    growing as sqrt(r0^2 + (z tan a)^2), squaring off toward the mouth (n -> n_mouth). `grow` inflates every section
    (the wall's outside), `beyond` runs straight on past the mouth so a cut opens through the face."""
    ta = math.sqrt(max(half_w ** 2 - r0 ** 2, 0.0)) / depth
    tb = math.sqrt(max(half_h ** 2 - r0 ** 2, 0.0)) / depth
    out = [_se_wire(r0 + grow, r0 + grow, 2.0, z0 - before)] if before else []      # straight on behind the throat
    for i in range(n + 1):
        z = depth * (i / n) ** 1.3
        w = math.sqrt(r0 ** 2 + (z * ta) ** 2) + grow
        h = math.sqrt(r0 ** 2 + (z * tb) ** 2) + grow
        out.append(_se_wire(w, h, 2.0 + (n_mouth - 2.0) * (z / depth) ** 1.2, z0 + z))
    if beyond:
        out.append(_se_wire(half_w + grow, half_h + grow, n_mouth, z0 + depth + beyond))
    return out


def _rr_sections(r0, half_w, half_h, depth, corner, n=10, beyond=0.0, grow=0.0, z0=0.0):
    """Rounded-rectangle sections of an oblate-spheroidal-like waveguide from a round throat (radius r0, z = z0) to a
    rounded-rectangle mouth (half_w x half_h, corner radius `corner`, z = z0 + depth): each half dimension grows as
    sqrt(r0^2 + (z tan a)^2), so the walls start square to the throat and open to their mouth angle; the corners go
    from round at the throat to `corner` at the mouth. `grow` inflates every section (an offset of the wall), `beyond`
    adds a straight run past the mouth (so a cut opens through the face)."""
    from build123d import RectangleRounded, Plane
    ta = math.sqrt(max(half_w ** 2 - r0 ** 2, 0.0)) / depth
    tb = math.sqrt(max(half_h ** 2 - r0 ** 2, 0.0)) / depth
    secs = []
    zs = [depth * (i / n) ** 1.3 for i in range(n + 1)]
    for z in zs:
        w = math.sqrt(r0 ** 2 + (z * ta) ** 2) + grow
        h = math.sqrt(r0 ** 2 + (z * tb) ** 2) + grow
        s = (z / depth) ** 1.5
        rc = min(w, h) * (1 - s) + (corner + grow) * s
        rc = min(rc, min(w, h) - 0.02)
        secs.append(Plane.XY.offset(z0 + z) * RectangleRounded(2 * w, 2 * h, rc))
    if beyond:
        secs.append(Plane.XY.offset(z0 + depth + beyond) * RectangleRounded(2 * (half_w + grow), 2 * (half_h + grow), min(corner + grow, min(half_w, half_h) + grow - 0.02)))
    return secs


def waveguide_block(width, height, depth, mouth_w, mouth_h, mouth_corner, r0=12.7, wall=8.0, edge=40.0, corner_r=70.0,
                    back_edge=20.0, boss=None, solid=False, n_mouth=4.5):
    """A rectangular waveguide cast as one block: a rounded box `width` x `height` x `depth` (its depth-wise corners
    on `corner_r`, the front edges on `edge`, the back's on `back_edge`) with the waveguide (round throat r0 on the
    back face, a `mouth_w` x `mouth_h` rounded-rectangle mouth on the front) through it. Hollow unless `solid`: an outer
    skin and the waveguide's own skin, both `wall` thick, a void between (a cast or printed shell, not a solid ingot);
    `boss` (dict d, t, bolt_d, bolts, bolt_hole) on the back round the throat takes the driver. Local frame: x across,
    y up, z from the back face (z = 0, the throat) to the front (z = depth)."""
    from build123d import Box, Align, Pos, Cylinder, fillet, Axis, loft
    outer = Box(width, height, depth, align=(Align.CENTER, Align.CENTER, Align.MIN))
    outer = fillet(outer.edges().filter_by(Axis.Z), corner_r)
    outer = fillet(outer.edges().group_by(Axis.Z)[-1], edge)
    outer = fillet(outer.edges().group_by(Axis.Z)[0], back_edge)
    # the waveguide's surface: superellipse sections, round at the throat, squaring toward the mouth (n_mouth), lofted
    # through splines so it is one smooth face (`mouth_corner` is kept for the older rounded-rectangle sections)
    # the loft runs on straight through the back face and past the mouth, so it opens both (a cylinder unioned to it
    # at the throat would meet it edge to edge, a tangency OpenCascade mishandles)
    cav = Solid.make_loft(_se_sections(r0, mouth_w / 2, mouth_h / 2, depth, n_mouth, beyond=5.0, before=6.0), False)
    body = outer
    if not solid:
        t = wall
        void = Box(width - 2 * t, height - 2 * t, depth - 2 * t, align=(Align.CENTER, Align.CENTER, Align.MIN))
        void = Pos(0, 0, t) * fillet(void.edges().filter_by(Axis.Z), max(corner_r - t, 2.0))
        grown = Solid.make_loft(_se_sections(r0, mouth_w / 2, mouth_h / 2, depth, n_mouth, grow=t, beyond=5.0, before=6.0), False)
        body = body - (void - grown)
    body = body - cav
    if boss:
        b = Pos(0, 0, -boss['t']) * (Cylinder(boss['d'] / 2, boss['t'], align=(Align.CENTER, Align.CENTER, Align.MIN)) -
                                     Cylinder(r0, boss['t'] + 1, align=(Align.CENTER, Align.CENTER, Align.MIN)))
        for k in range(boss.get('bolts', 0)):
            a = 2 * math.pi * (k + 0.5) / boss['bolts']
            b = b - Pos(boss['bolt_d'] / 2 * math.cos(a), boss['bolt_d'] / 2 * math.sin(a), -boss['t'] - 0.5) * \
                Cylinder(boss['bolt_hole'] / 2, boss['t'] + 1, align=(Align.CENTER, Align.CENTER, Align.MIN))
        body = body + b
    return body
