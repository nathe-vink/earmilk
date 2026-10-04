"""Shop drawings, generated from fab/params.py: a dimensioned general arrangement and the gable block in detail.

    /root/.venvs/fab/bin/python fab/drawings.py

Writes out/drawings/earmilk-shop-drawings.pdf (A3 landscape, two sheets, 1:5 and 1:2) and a PNG of each sheet.
All dimensions in millimetres. Third-angle projection.
"""
import json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from params import *  # noqa: F401,F403
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Circle, Ellipse, Polygon as MPoly, Rectangle, FancyBboxPatch

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'out')
INK, THIN, CUT, NOTE = '#111111', '#555555', '#d9c49c', '#8a1c1c'
A3 = (420, 297)


def sheet(title, scale_note):
    fig = plt.figure(figsize=(A3[0] / 25.4, A3[1] / 25.4))
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, A3[0]); ax.set_ylim(0, A3[1]); ax.set_aspect('equal'); ax.axis('off')
    ax.add_patch(Rectangle((8, 8), A3[0] - 16, A3[1] - 16, fill=False, lw=0.8, color=INK))
    # Title block
    ax.add_patch(Rectangle((A3[0] - 128, 8), 120, 26, fill=False, lw=0.6, color=INK))
    ax.text(A3[0] - 124, 27, 'earmilk floorstander', fontsize=9, weight='bold')
    ax.text(A3[0] - 124, 20, title, fontsize=7)
    ax.text(A3[0] - 124, 13, f'{scale_note}  mm  third angle  2026-10-04  from fab/params.py', fontsize=5.5, color=THIN)
    return fig, ax


class View:
    """Maps model millimetres (u across, v up) onto the sheet at a scale, with its origin at (ox, oy) on the sheet."""
    def __init__(self, ax, ox, oy, scale):
        self.ax, self.ox, self.oy, self.k = ax, ox, oy, scale

    def p(self, u, v):
        return (self.ox + u * self.k, self.oy + v * self.k)

    def line(self, pts, lw=0.6, color=INK, ls='-', close=False):
        q = [self.p(u, v) for (u, v) in pts]
        if close:
            q.append(q[0])
        self.ax.plot([a for a, b in q], [b for a, b in q], lw=lw, color=color, ls=ls, solid_capstyle='butt')

    def rect(self, u0, v0, u1, v1, **kw):
        self.line([(u0, v0), (u1, v0), (u1, v1), (u0, v1)], close=True, **kw)

    def fill(self, pts, color=CUT, lw=0.5):
        self.ax.add_patch(MPoly([self.p(u, v) for (u, v) in pts], closed=True, facecolor=color, edgecolor=INK, lw=lw))

    def circle(self, u, v, d, lw=0.6, color=INK, ls='-'):
        self.ax.add_patch(Circle(self.p(u, v), d / 2 * self.k, fill=False, lw=lw, color=color, ls=ls))

    def text(self, u, v, s, size=5.5, color=INK, **kw):
        x, y = self.p(u, v); self.ax.text(x, y, s, fontsize=size, color=color, **kw)

    def dim(self, a, b, off, text=None, size=5.2, side=1):
        """Linear dimension between model points a and b, offset `off` mm (model) perpendicular to a->b."""
        (u0, v0), (u1, v1) = a, b
        L = math.hypot(u1 - u0, v1 - v0)
        nu, nv = -(v1 - v0) / L, (u1 - u0) / L
        A = (u0 + nu * off, v0 + nv * off); B = (u1 + nu * off, v1 + nv * off)
        ext = 2.0 / self.k
        for (pu, pv), (qu, qv) in ((a, A), (b, B)):
            self.line([(pu + nu * (1.0 / self.k) * (1 if off > 0 else -1), pv + nv * (1.0 / self.k) * (1 if off > 0 else -1)),
                       (qu + nu * ext * (1 if off > 0 else -1), qv + nv * ext * (1 if off > 0 else -1))], lw=0.25, color=THIN)
        pa, pb = self.p(*A), self.p(*B)
        self.ax.annotate('', xy=pb, xytext=pa, arrowprops=dict(arrowstyle='<|-|>', lw=0.35, color=THIN, mutation_scale=4,
                                                               shrinkA=0, shrinkB=0))
        mx, my = (pa[0] + pb[0]) / 2, (pa[1] + pb[1]) / 2
        ang = math.degrees(math.atan2(pb[1] - pa[1], pb[0] - pa[0]))
        if ang > 90 or ang < -90:
            ang += 180
        t = text if text is not None else f'{L:.0f}' if abs(L - round(L)) < 0.05 else f'{L:.1f}'
        self.ax.text(mx + nu * 1.6 * (1 if off > 0 else -1), my + nv * 1.6 * (1 if off > 0 else -1), t, fontsize=size,
                     rotation=ang, ha='center', va='center', color=INK,
                     bbox=dict(facecolor='white', edgecolor='none', pad=0.3))


def bowl_profile():
    """Centreline section of the bowl: the ceiling (theta = 90 deg) and floor (270 deg) from mouth (t = 0) to throat."""
    from cad import bowl_point
    ceil = [bowl_point(math.pi / 2, t / 40) for t in range(41)]
    floor = [bowl_point(3 * math.pi / 2, t / 40) for t in range(41)]
    return [(y, z) for (x, y, z) in ceil], [(y, z) for (x, y, z) in floor]


def general_arrangement(pdf):
    fig, ax = sheet('General arrangement', '1:5')
    k = 0.2
    acous = json.load(open(os.path.join(OUT, 'acoustics.json'))) if os.path.exists(os.path.join(OUT, 'acoustics.json')) else {}
    port_total = acous.get('port', {}).get('total_length_mm', 152)
    base = 40
    # FRONT
    step = (PLAN + 105) * k
    F = View(ax, 36, base, k)
    F.text(0, TOTAL + 40, 'FRONT', size=7, weight='bold')
    F.line([(0, 0), (PLAN, 0), (PLAN, BODY), (0, BODY)], close=True)
    F.line([(0, BODY), (PLAN, BODY), (PLAN, RIDGE_Z), (0, RIDGE_Z)], close=True)
    F.rect(0, RIDGE_Z, PLAN, TOTAL)
    F.line([(0, PLINTH_H), (PLAN, PLINTH_H)], lw=0.3); F.line([(0, PLINTH_H + SHADOW), (PLAN, PLINTH_H + SHADOW)], lw=0.3)
    F.circle(RUN, WOOFER['z'], WOOFER['frame'], lw=0.35, ls='--'); F.circle(RUN, WOOFER['z'], WOOFER_CUTOUT)
    F.circle(RUN, MID['z'], MID['frame'], lw=0.35, ls='--'); F.circle(RUN, MID['z'], MID_CUTOUT)
    # mouth ellipse seen from the front: its across width is true, its height is the slope length times the vertical
    mz0, mz1 = BODY + DZ * (BOWL['mouth_s'] - BOWL['mouth_l'] / 2), BODY + DZ * (BOWL['mouth_s'] + BOWL['mouth_l'] / 2)
    ax.add_patch(Ellipse(F.p(RUN, (mz0 + mz1) / 2), BOWL['mouth_w'] * k, (mz1 - mz0) * k, fill=False, lw=0.6))
    F.rect(RUN - 86, 39, RUN + 86, 71.5, lw=0.3, color=NOTE); F.text(RUN, 22, 'cast letters, 44 mm type, 2.5 proud', size=4.5, color=NOTE, ha='center')
    F.dim((0, 0), (PLAN, 0), -60)
    F.dim((0, 0), (0, TOTAL), -95); F.dim((0, 0), (0, BODY), -55); F.dim((0, 0), (0, PLINTH_H), -25)
    F.dim((PLAN, 0), (PLAN, WOOFER['z']), 35); F.dim((PLAN, 0), (PLAN, MID['z']), 75)
    F.text(RUN, WOOFER['z'] - 8, f'cutout {WOOFER_CUTOUT:.0f}', size=4.6, ha='center'); F.text(RUN, MID['z'] - 6, f'cutout {MID_CUTOUT:.0f}', size=4.6, ha='center')
    F.text(RUN, WOOFER['z'] - WOOFER['frame'] / 2 - 18, 'frame 310 (dashed)', size=4.2, ha='center', color=THIN)

    # RIGHT SIDE (looking at x = 390 from outside: front to the left... third angle puts the right view to the right)
    S = View(ax, 36 + step, base, k)
    S.text(0, TOTAL + 40, 'RIGHT SIDE', size=7, weight='bold')
    S.line([(0, 0), (PLAN, 0), (PLAN, BODY), (RUN, RIDGE_Z), (0, BODY)], close=True)
    S.rect(RUN - FIN_T / 2, RIDGE_Z - 3, RUN + FIN_T / 2, TOTAL)
    S.line([(0, PLINTH_H), (PLAN, PLINTH_H)], lw=0.3); S.line([(0, PLINTH_H + SHADOW), (PLAN, PLINTH_H + SHADOW)], lw=0.3)
    S.text(4, -16, 'front', size=4.5, color=THIN); S.text(PLAN - 18, -16, 'back', size=4.5, color=THIN)
    S.dim((0, BODY), (RUN, RIDGE_Z), 18, f'slope {SLOPE:.0f}, {SLOPE_DEG:.1f}°')
    S.dim((PLAN, BODY), (PLAN, RIDGE_Z), 30, '150'); S.dim((PLAN, RIDGE_Z), (PLAN, TOTAL), 30, '45')
    S.dim((0, 0), (PLAN, 0), -60)
    S.text(RUN, TOTAL + 10, f'fin {FIN_T:.0f} thick, full width', size=4.5, ha='center')
    S.text(RUN, PLINTH_H + 12, 'shadow line 3 x 3 groove at 110', size=4.5, ha='center')

    # BACK (seen from behind)
    B = View(ax, 36 + 2 * step, base, k)
    B.text(0, TOTAL + 40, 'BACK', size=7, weight='bold')
    B.line([(0, 0), (PLAN, 0), (PLAN, BODY), (0, BODY)], close=True)
    B.line([(0, BODY), (PLAN, BODY), (PLAN, RIDGE_Z), (0, RIDGE_Z)], close=True); B.rect(0, RIDGE_Z, PLAN, TOTAL)
    B.line([(0, PLINTH_H), (PLAN, PLINTH_H)], lw=0.3); B.line([(0, PLINTH_H + SHADOW), (PLAN, PLINTH_H + SHADOW)], lw=0.3)
    ax.add_patch(FancyBboxPatch(B.p(PLATE['x0'], PLATE['z0']), (PLATE['x1'] - PLATE['x0']) * k, (PLATE['z1'] - PLATE['z0']) * k,
                                boxstyle=f'round,pad=0,rounding_size={PLATE["r"] * k}', fill=False, lw=0.6))
    B.text(RUN, (PLATE['z0'] + PLATE['z1']) / 2, 'bronze Facts plate\n318 x 312 x 3, 1.5 proud', size=4.6, ha='center', va='center')
    B.circle(RUN, PORT['z'], PORT['flange']); B.circle(RUN, PORT['z'], PORT['bore'])
    B.rect(RUN - POSTS['w'] / 2, POSTS['z'] - POSTS['h'] / 2, RUN + POSTS['w'] / 2, POSTS['z'] + POSTS['h'] / 2)
    for sx in (-1, 1):
        B.circle(RUN + sx * POSTS['spacing'] / 2, POSTS['z'], POSTS['post_d'], lw=0.4)
    B.rect(RUN - 86, 810, RUN + 86, 842.5, lw=0.3, color=NOTE)
    B.text(RUN, (BODY + RIDGE_Z) / 2 - 4, 'OPEN OTHER SIDE ->', size=4.5, ha='center', color=NOTE)
    B.text(RUN, 50, 'SHAKE WELL', size=4.5, ha='center', color=NOTE)
    B.dim((PLAN, 0), (PLAN, PORT['z']), 35); B.dim((PLAN, 0), (PLAN, POSTS['z']), 70)
    B.dim((0, PLATE['z0']), (0, PLATE['z1']), -30, '312'); B.dim((0, 0), (0, PLATE['z0']), -30)
    B.dim((PLATE['x0'], PLATE['z1']), (PLATE['x1'], PLATE['z1']), 26, '318')
    B.text(RUN + 62, PORT['z'] - 3, f'port: 92 bore, 112 flange,\n{port_total:.0f} long incl. flare', size=4.4)

    # SECTION A-A on the centreline (cut x = 195, seen from the right)
    X = View(ax, 36 + 3 * step - 4, base, k)
    X.text(0, TOTAL + 40, 'SECTION A-A (centreline)', size=7, weight='bold')
    W = WALL
    X.fill([(0, 0), (W, 0), (W, BODY), (0, BODY)])                         # front baffle
    X.fill([(PLAN - W, 0), (PLAN, 0), (PLAN, BODY), (PLAN - W, BODY)])     # back
    X.fill([(W, 0), (PLAN - W, 0), (PLAN - W, W), (W, W)])                 # bottom
    X.fill([(W, TOP_Z0), (PLAN - W, TOP_Z0), (PLAN - W, BODY), (W, BODY)])  # top
    yd = WALL + MID_CHAMBER_DEPTH
    X.fill([(W, MID_SHELF_TOP - W), (yd + W, MID_SHELF_TOP - W), (yd + W, MID_SHELF_TOP), (W, MID_SHELF_TOP)])  # shelf
    X.fill([(yd, MID_SHELF_TOP), (yd + W, MID_SHELF_TOP), (yd + W, TOP_Z0), (yd, TOP_Z0)])                       # divider
    h = BRACE_WINDOW / 2
    X.fill([(W, BRACE_Z), (RUN - h, BRACE_Z), (RUN - h, BRACE_Z + W), (W, BRACE_Z + W)])
    X.fill([(RUN + h, BRACE_Z), (PLAN - W, BRACE_Z), (PLAN - W, BRACE_Z + W), (RUN + h, BRACE_Z + W)])
    # holes through the baffle
    for (zc, d) in ((WOOFER['z'], WOOFER_CUTOUT), (MID['z'], MID_CUTOUT)):
        ax.add_patch(Rectangle(X.p(-0.5, zc - d / 2), (W + 1) * k, d * k, facecolor='white', edgecolor='none'))
        X.line([(0, zc - d / 2), (W, zc - d / 2)], lw=0.5); X.line([(0, zc + d / 2), (W, zc + d / 2)], lw=0.5)
    # port tube
    pb = PORT['bore'] / 2; L = port_total
    X.line([(PLAN + 5, PORT['z'] + PORT['flange'] / 2), (PLAN + 5, PORT['z'] - PORT['flange'] / 2)], lw=0.6)
    X.line([(PLAN, PORT['z'] + pb + 4), (PLAN - L + 18, PORT['z'] + pb + 4)], lw=0.6)
    X.line([(PLAN, PORT['z'] - pb - 4), (PLAN - L + 18, PORT['z'] - pb - 4)], lw=0.6)
    X.line([(PLAN - L + 18, PORT['z'] + pb + 4), (PLAN - L, PORT['z'] + pb + 18)], lw=0.6)
    X.line([(PLAN - L + 18, PORT['z'] - pb - 4), (PLAN - L, PORT['z'] - pb - 18)], lw=0.6)
    # gable block with the bowl
    ceil, floor = bowl_profile()
    X.fill([(0, BODY), (PLAN, BODY), (RUN, RIDGE_Z)], color='#e7d6b4')
    X.fill([(RUN - FIN_T / 2, RIDGE_Z - 3), (RUN + FIN_T / 2, RIDGE_Z - 3), (RUN + FIN_T / 2, TOTAL), (RUN - FIN_T / 2, TOTAL)], color='#e7d6b4')
    X.fill(floor + list(reversed(ceil)), color='white')
    X.fill([(TWEETER['faceplate_y'], TWEETER['z'] - 32), (TWEETER['faceplate_y'] + 6, TWEETER['z'] - 32),
            (TWEETER['faceplate_y'] + 6, TWEETER['z'] - 22.5), (TWEETER['faceplate_y'] + 40, TWEETER['z'] - 22.5),
            (TWEETER['faceplate_y'] + 40, TWEETER['z'] + 22.5), (TWEETER['faceplate_y'] + 6, TWEETER['z'] + 22.5),
            (TWEETER['faceplate_y'] + 6, TWEETER['z'] + 32), (TWEETER['faceplate_y'], TWEETER['z'] + 32)], color='white')
    X.line([(0, GABLE_SPLIT_Z), (PLAN, GABLE_SPLIT_Z)], lw=0.3, ls=(0, (4, 2)), color=NOTE)
    X.text(PLAN - 120, GABLE_SPLIT_Z + 6, 'split for 3-axis', size=4.2, color=NOTE)
    X.text(W + 6, (MID_SHELF_TOP + TOP_Z0) / 2, f'mid\nchamber\n{MID_CHAMBER_DEPTH * INNER * (TOP_Z0 - MID_SHELF_TOP) / 1e6:.1f} L', size=4.5, va='center')
    X.text(RUN, 300, f'woofer chamber\n{acous.get("woofers", [{}])[0].get("Vb_net_l", 88):.0f} L net', size=5, ha='center')
    X.dim((W, MID_SHELF_TOP - W), (W, MID_SHELF_TOP), -14, '18')
    X.dim((PLAN, BRACE_Z), (PLAN, BRACE_Z + W), 40, f'brace {BRACE_Z:.0f}')
    X.dim((PLAN, MID_SHELF_TOP), (PLAN, TOP_Z0), 40)
    X.text(TWEETER['faceplate_y'] / 2, TWEETER['z'] + 4, f'throat at {TWEETER["faceplate_y"]:.0f}', size=4.3, ha='center')
    X.text(PLAN / 2, -30, 'cut faces shaded; front to the left', size=4.5, ha='center', color=THIN)

    ax.text(16, 16, 'Proposals (not Decisions): butt-jointed 18 mm birch, the mid chamber, the brace, the groove, the split. '
            'Driver cutouts are for the shortlisted drivers (fab/drivers.json): re-cut for others.', fontsize=5.5, color=THIN)
    pdf.savefig(fig); fig.savefig(os.path.join(OUT, 'drawings', 'sheet-1-general-arrangement.png'), dpi=110); plt.close(fig)


def gable_detail(pdf):
    fig, ax = sheet('Gable block and bowl', '1:2')
    k = 0.5
    ceil, floor = bowl_profile()
    # SECTION on the centreline, 1:2
    G = View(ax, 30, 60, k)
    ax.text(30, 178, 'GABLE SECTION ON THE CENTRELINE  (1:2)', fontsize=7, weight='bold')
    zb = BODY
    def gz(z): return z - zb
    G.fill([(0, 0), (PLAN, 0), (RUN, RISE)], color='#e7d6b4')
    G.fill([(RUN - FIN_T / 2, RISE - 3), (RUN + FIN_T / 2, RISE - 3), (RUN + FIN_T / 2, RISE + FIN_H), (RUN - FIN_T / 2, RISE + FIN_H)], color='#e7d6b4')
    G.fill([(y, gz(z)) for (y, z) in floor] + [(y, gz(z)) for (y, z) in reversed(ceil)], color='white')
    tz = gz(TWEETER['z']); fy = TWEETER['faceplate_y']
    G.fill([(fy, tz - 32), (fy + 6, tz - 32), (fy + 6, tz - 22.5), (fy + 40, tz - 22.5), (fy + 40, tz + 22.5),
            (fy + 6, tz + 22.5), (fy + 6, tz + 32), (fy, tz + 32)], color='white')
    G.fill([(fy + 13, 0), (fy + 27, 0), (fy + 27, tz - 22.5), (fy + 13, tz - 22.5)], color='white')
    for i in range(1, 9):
        v = i * GABLE_LAYER; inset = v * RUN / RISE
        G.line([(inset, v), (PLAN - inset, v)], lw=0.2, color=THIN, ls=(0, (1, 2)))
    vs = gz(GABLE_SPLIT_Z); G.line([(vs * RUN / RISE - 10, vs), (PLAN - vs * RUN / RISE + 10, vs)], lw=0.5, color=NOTE, ls=(0, (5, 2)))
    G.text(PLAN + 6, gz(GABLE_SPLIT_Z) - 2, 'split z 914: mill each half from its open side', size=5, color=NOTE)
    G.text(PLAN + 6, 3 * GABLE_LAYER + 30, '11 layers of 18 mm birch, glued, top trimmed', size=5, color=THIN)
    lip_lo = slope_point(0, BOWL['mouth_s'] - BOWL['mouth_l'] / 2); lip_hi = slope_point(0, BOWL['mouth_s'] + BOWL['mouth_l'] / 2)
    for (lbl, (x, y, z)) in (('lower lip', lip_lo), ('upper lip', lip_hi)):
        G.circle(y, gz(z), 2.2, lw=0.5, color=NOTE)
        G.text(y - 4, gz(z) + (5 if lbl == 'upper lip' else -9), f'{lbl}  y {y:.1f}  z {z:.1f}', size=5, color=NOTE, ha='right')
    G.text(fy + 2, tz + 36, f'throat ø{BOWL["throat"]:.0f} at y {fy:.0f}, axis z {TWEETER["z"]}', size=5)
    G.text(fy + 44, tz - 2, 'tweeter pocket:\nfaceplate ø64 x 6\nbody ø45 x 34\n(for a 62 mm Scan-Speak)', size=4.6, va='center')
    G.text(fy + 30, 8, 'wire hole ø14', size=4.6)
    G.dim((0, 0), (PLAN, 0), -18)
    G.dim((0, 0), (0, RISE), -16, '150'); G.dim((0, RISE), (0, RISE + FIN_H), -16, '45')
    G.dim((0, tz), (fy, tz), -36, f'{fy:.0f} to the faceplate')
    G.text(RUN, RISE + FIN_H + 6, 'fin 8 thick', size=5, ha='center')
    G.text(30, -40, 'Bowl surface: one smooth loft from the mouth ellipse to the throat circle; the floor sags 3 below the lip-to-throat chord, the ceiling arches 6 above it.', size=5)

    # MOUTH seen square to the slope, 1:2
    M = View(ax, 318, 150, 0.4)
    ax.text(238, 268, 'THE MOUTH, SEEN SQUARE TO THE FRONT SLOPE  (1:2.5)', fontsize=7, weight='bold')
    M.rect(-RUN, 0, RUN, SLOPE, lw=0.5)
    ax.add_patch(Ellipse(M.p(0, BOWL['mouth_s']), BOWL['mouth_w'] * M.k, BOWL['mouth_l'] * M.k, fill=False, lw=0.8))
    M.circle(0, BOWL['mouth_s'], 2, lw=0.4)
    M.dim((-BOWL['mouth_w'] / 2, BOWL['mouth_s']), (BOWL['mouth_w'] / 2, BOWL['mouth_s']), -66, '211')
    M.dim((BOWL['mouth_w'] / 2 + 20, BOWL['mouth_s'] - BOWL['mouth_l'] / 2), (BOWL['mouth_w'] / 2 + 20, BOWL['mouth_s'] + BOWL['mouth_l'] / 2), -10, '118')
    M.dim((-RUN, 0), (-RUN, BOWL['mouth_s']), 14, '79 to the centre')
    M.dim((-RUN, 0), (-RUN, SLOPE), 40, f'{SLOPE:.0f} slope')
    M.text(0, -12, 'front top edge', size=5, ha='center', color=THIN); M.text(0, SLOPE + 5, 'ridge', size=5, ha='center', color=THIN)

    ax.text(16, 16, 'The bowl is spec (README, geometry.md); its surface is the same loft the renders draw. The pocket and the split are proposals.',
            fontsize=5.5, color=THIN)
    pdf.savefig(fig); fig.savefig(os.path.join(OUT, 'drawings', 'sheet-2-gable.png'), dpi=110); plt.close(fig)


def main():
    os.makedirs(os.path.join(OUT, 'drawings'), exist_ok=True)
    with PdfPages(os.path.join(OUT, 'drawings', 'earmilk-shop-drawings.pdf')) as pdf:
        general_arrangement(pdf)
        gable_detail(pdf)
    print('out/drawings/earmilk-shop-drawings.pdf')


if __name__ == '__main__':
    main()
