"""The tweeter's waveguide, shaped for what it does to sound, not for how it looks (the owner, 2026-10-08).

The wall follows the oblate-spheroidal profile (OS, after Geddes), in the form the Ath tools use. For an axial distance
x from the throat, in each direction phi round the axis,

    r(x) = sqrt((k r0)^2 + 2 k r0 x tan(a0) + x^2 tan(a)^2) + r0 (1 - k)

r0 is the throat's radius (the tweeter's dome and surround), a0 the wall's angle at the throat (about the dome's own
wavefront), a the coverage half-angle in that direction and k how fast the throat opens.

Why it is not a textbook horn. The roof is a plane at 37.6 degrees, so the mouth is cut obliquely: each direction's wall
runs until it meets the roof, which this module finds, and its length differs round the axis. Downward, the eave (the
front top edge) is only a little below the axis, so a downward wall that opens too fast would run out through the front
face: the coverage in each direction is narrowed, where it must be, until its wall meets the roof at least `s_min` up
the slope from the eave. Upward, the roof falls away behind the throat, so the upper wall is short and the slope above
it acts as the baffle. The mouth is then rounded into the roof on a radius `lip_r`, built as an arc in each direction's
meridian plane, tangent to the wall and to the roof, which is what keeps the mouth from diffracting.

Frame: the spec's (x across 0 to 390, y depth 0 at the front face, z up). The tweeter faces -y, tipped down by `tilt`
degrees if set. Directions round the axis: phi = 0 to the right (+x), 90 up.
"""
from dataclasses import dataclass, asdict
from math import atan, atan2, cos, radians, sin, sqrt, tan, degrees, hypot

import numpy as np

try:
    from params import BODY, RUN, RISE, PLAN, TWEETER
except ImportError:
    from fab.params import BODY, RUN, RISE, PLAN, TWEETER

SLOPE_LEN = hypot(RUN, RISE)
U_SLOPE = np.array([0.0, RUN / SLOPE_LEN, RISE / SLOPE_LEN])      # up the front slope (backward and up)
N_SLOPE = np.array([0.0, -RISE / SLOPE_LEN, RUN / SLOPE_LEN])     # the front slope's outward normal (forward and up)
P_EAVE = np.array([RUN, 0.0, BODY])                               # a point on the slope: the eave, at the centreline


def slope_coords(P):
    """(u across from the centreline, s up the slope from the eave, w out of the slope) for a 3D point."""
    d = np.asarray(P, float) - P_EAVE
    return float(d[0]), float(d @ U_SLOPE), float(d @ N_SLOPE)


@dataclass
class Waveguide:
    r0: float = 15.0          # throat radius, mm (from the chosen tweeter's dome and surround)
    a0: float = 12.0          # degrees, the wall's angle at the throat
    a_h: float = 45.0         # degrees, coverage half-angle horizontally
    a_up: float = 35.0        # degrees, upward
    a_down: float = 30.0      # degrees, downward, before the eave narrows it
    k: float = 1.4            # throat expansion
    throat_y: float = 125.0   # the throat plane (the tweeter's mounting face), mm behind the front face
    throat_z: float = TWEETER['z']
    lip_r: float = 12.0       # the mouth's rounding into the roof, mm
    s_min: float = 15.0       # the mouth's lowest point at least this far up the slope from the eave, mm
    sections: int = 96        # directions round the axis
    steps: int = 48           # stations along each wall, throat to the lip
    lip_steps: int = 8        # stations round the lip's arc
    tilt: float = 0.0         # degrees the axis is tipped down from horizontal (the tweeter aimed lower)

    # --- the wall ------------------------------------------------------------------------------------------------
    def coverage(self, phi):
        av = self.a_up if sin(phi) >= 0 else self.a_down
        th, tv = tan(radians(self.a_h)), tan(radians(av))
        return atan(sqrt((th * cos(phi)) ** 2 + (tv * sin(phi)) ** 2))

    def r_os(self, x, a):
        k, r0 = self.k, self.r0
        return sqrt((k * r0) ** 2 + 2 * k * r0 * x * tan(radians(self.a0)) + x * x * tan(a) ** 2) + r0 * (1 - k)

    def dr_os(self, x, a):
        k, r0 = self.k, self.r0
        root = sqrt((k * r0) ** 2 + 2 * k * r0 * x * tan(radians(self.a0)) + x * x * tan(a) ** 2)
        return (k * r0 * tan(radians(self.a0)) + x * tan(a) ** 2) / root

    def axes(self):
        """(axis, across, up): the axis points out of the throat, tipped down by `tilt`; up is square to it."""
        t = radians(self.tilt)
        return (np.array([0.0, -cos(t), -sin(t)]), np.array([1.0, 0.0, 0.0]), np.array([0.0, -sin(t), cos(t)]))

    def point(self, x, r, phi):
        e_ax, e_x, e_up = self.axes()
        return np.array([RUN, self.throat_y, self.throat_z]) + x * e_ax + r * (cos(phi) * e_x + sin(phi) * e_up)

    def height_above_roof(self, P):
        return float((np.asarray(P) - P_EAVE) @ N_SLOPE)

    def meet(self, phi, a):
        """Axial distance where the wall in direction phi (half-angle a) crosses the roof plane, or None."""
        f = lambda x: self.height_above_roof(self.point(x, self.r_os(x, a), phi))
        lo, hi = 0.0, 600.0
        if f(lo) >= 0 or f(hi) < 0: return None
        for _ in range(64):
            m = 0.5 * (lo + hi)
            lo, hi = (m, hi) if f(m) < 0 else (lo, m)
        return 0.5 * (lo + hi)

    def ok(self, phi, a):
        x = self.meet(phi, a)
        if x is None: return False
        u, s, _ = slope_coords(self.point(x, self.r_os(x, a), phi))
        return s >= self.s_min and abs(u) <= RUN - 20 - self.lip_r and s <= SLOPE_LEN - 14 - self.lip_r

    def fitted_coverage(self, phi):
        """The design half-angle in direction phi, narrowed until the wall meets the roof inside the slope."""
        a = self.coverage(phi)
        if self.ok(phi, a): return a
        lo, hi = radians(0.5), a
        for _ in range(48):
            m = 0.5 * (lo + hi)
            lo, hi = (m, hi) if self.ok(phi, m) else (lo, m)
        return lo

    # --- one direction: wall, then the lip's arc onto the roof -------------------------------------------------
    def meridian(self, phi):
        """Points from the throat to the roof in direction phi: the OS wall, then an arc of radius lip_r tangent to
        the wall and to the roof's line in this meridian plane, ending on the roof."""
        a = self.fitted_coverage(phi)
        X = self.meet(phi, a)
        e_ax, e_x, e_up = self.axes()
        er = cos(phi) * e_x + sin(phi) * e_up               # radial direction in this meridian plane
        ex = e_ax                                           # forward along the axis
        # the roof's line in this plane: points p(x, r) with height_above_roof = 0, linear in (x, r)
        hx = float(ex @ N_SLOPE); hr = float(er @ N_SLOPE)
        roof_dir = np.array([hr, -hx]); roof_dir /= np.linalg.norm(roof_dir)   # (dx, dr) along the roof line
        if roof_dir[1] < 0: roof_dir = -roof_dir           # pointing outward (growing r)
        # find the wall station where an arc of radius lip_r is tangent to both the wall and the roof line
        def wall(x): return np.array([x, self.r_os(x, a)])
        def tangent(x):
            t = np.array([1.0, self.dr_os(x, a)]); return t / np.linalg.norm(t)
        grad = np.array([hx, hr]); gnorm = float(np.linalg.norm(grad))
        def roof_dist(p):   # distance in the meridian plane from p=(x, r) to the roof line, positive inside the wood
            P = self.point(p[0], p[1], phi); return -self.height_above_roof(P) / gnorm
        rho = self.lip_r
        def centre(x):      # the arc's centre lies in the wood, rho from the wall: along the wall's normal away from the axis
            t = tangent(x); n_wood = np.array([-t[1], t[0]])      # (-r', 1)/|.|: toward larger r
            return wall(x) + rho * n_wood
        g = lambda x: roof_dist(centre(x)) - rho          # zero where the centre is also rho inside the roof
        lo, hi = 0.0, X
        if g(lo) < 0:      # even at the throat the centre is too close to the roof: no room for the lip
            x_t = 0.0
        else:
            for _ in range(64):
                m = 0.5 * (lo + hi)
                lo, hi = (m, hi) if g(m) > 0 else (lo, m)
            x_t = 0.5 * (lo + hi)
        # stations closer together at the throat, where the wall is narrow (better-shaped triangles for the BEM)
        tt = np.linspace(0.0, 1.0, self.steps + 1) ** 1.6
        pts = [self.point(x, self.r_os(x, a), phi) for x in x_t * tt]
        # the arc from the wall's tangent point round to the roof's tangent point
        C = centre(x_t); p0 = wall(x_t)
        # the roof tangent point: foot of the perpendicular from C to the roof line
        n_roof = grad / gnorm                              # out of the wood, toward the outside air
        p1 = C + n_roof * roof_dist(C)
        v0, v1 = p0 - C, p1 - C
        a0_, a1_ = atan2(v0[1], v0[0]), atan2(v1[1], v1[0])
        da = (a1_ - a0_ + np.pi) % (2 * np.pi) - np.pi
        for i in range(1, self.lip_steps + 1):
            ang = a0_ + da * i / self.lip_steps
            p = C + rho * np.array([cos(ang), sin(ang)])
            pts.append(self.point(p[0], p[1], phi))
        return dict(phi=phi, a=a, x_meet=X, x_lip=x_t, pts=np.array(pts))

    def grid(self, phis=None):
        """All meridians: an array (sections, steps + lip_steps + 1, 3). The last ring lies on the roof. `phis` (from
        phis()) for the CAD's meridians; evenly spaced by default, as the BEM and summary() expect."""
        phis = [2 * np.pi * i / self.sections for i in range(self.sections)] if phis is None else phis
        ms = [self.meridian(p) for p in phis]
        return np.stack([m['pts'] for m in ms]), ms

    def crease_angles(self, n=720):
        """Where the fitted coverage starts narrowing (the wall would leave the slope there): the coverage has a kink, so
        the surface has a crease along that meridian, and a mesh should have an edge on it."""
        narrowed = lambda phi: not self.ok(phi, self.coverage(phi))
        out, prev = [], narrowed(0.0)
        for i in range(1, n + 1):
            phi = 2 * np.pi * i / n; cur = narrowed(phi)
            if cur != prev:
                lo, hi = 2 * np.pi * (i - 1) / n, phi
                for _ in range(40):
                    m = 0.5 * (lo + hi)
                    lo, hi = (m, hi) if narrowed(m) == prev else (lo, m)
                out.append(0.5 * (lo + hi) % (2 * np.pi))
            prev = cur
        return out

    def phis(self, max_jump=2.0, levels=4):
        """The CAD's meridians: `sections` evenly round the axis, one on each crease, and more wherever neighbours' walls
        differ in length by more than max_jump mm. Stations sit at the same fraction of each wall, so between meridians
        of very different lengths they fall at different depths, and the ruled quads between them twist into a sawtooth
        that a gloss coat shows (most where the side walls turn into the floor, the walls 10 to 15 mm apart per 3.75
        degrees at 96 sections)."""
        ph = sorted(set([2 * np.pi * i / self.sections for i in range(self.sections)] + self.crease_angles()))
        x = {p: self.meridian(p)['x_lip'] for p in ph}
        for _ in range(levels):
            new = []
            for a, b in zip(ph, ph[1:] + [ph[0] + 2 * np.pi]):
                if abs(x[a] - x[b % (2 * np.pi)]) > max_jump:
                    m = 0.5 * (a + b) % (2 * np.pi); x[m] = self.meridian(m)['x_lip']; new.append(m)
            if not new:
                break
            ph = sorted(set(ph + new))
        return ph

    def summary(self):
        G, ms = self.grid()
        mouth = G[:, -1, :]
        uu = [slope_coords(P)[0] for P in mouth]; ss = [slope_coords(P)[1] for P in mouth]
        cov = {f'{int(round(degrees(m["phi"])))}': round(degrees(m['a']), 1) for m in ms[:: self.sections // 8]}
        return dict(mouth_width=round(max(uu) - min(uu), 1), mouth_s=[round(min(ss), 1), round(max(ss), 1)],
                    depth_horizontal=round(ms[0]['x_meet'], 1), depth_down=round(ms[3 * self.sections // 4]['x_meet'], 1),
                    depth_up=round(ms[self.sections // 4]['x_meet'], 1), coverage_by_direction=cov,
                    eave_angle=round(degrees(atan((self.throat_z - BODY) / self.throat_y)), 1))


if __name__ == '__main__':
    import json
    for ty, tz in ((125.0, 903.5), (150.0, 903.5), (176.0, 903.5), (150.0, 925.0), (176.0, 935.0)):
        w = Waveguide(throat_y=ty, throat_z=tz)
        print(ty, tz, json.dumps(w.summary()))
