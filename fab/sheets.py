"""Drawings to build from: A3 sheets projected from the CAD (hidden-line removal on the same solids the cut files and
the renders come from), dimensioned, with the waveguide drawn from its own equations rather than from its facets.

    .venv-fab/bin/python fab/sheets.py [--only 1 2]      -> out/drawings/earmilk-sheets.pdf and sheet-N.png

Sheets:
  1  General arrangement: front, left side, back and top at 1:5, the overall sizes and every centre height
  2  Section on the centreline at 1:5, and the roof at 1:2: the chambers, the panels, the waveguide insert, the
     tweeter, the wires' path
  3  The waveguide insert and the tweeter's mount at 1:2: front, section on the axis, back; how it goes together
  4  Wiring: amplifier to drivers, connectors and the cable runs
  5  Exploded view and parts list

Conventions: millimetres; views are named for where they are seen from; heights from the floor, depths from the front
face, across from the left side as seen from the front (the CAD's frame).
"""
import argparse, math, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from params import *  # noqa: F401,F403
import numpy as np

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MPoly, Circle, FancyBboxPatch, Rectangle
from matplotlib.backends.backend_pdf import PdfPages

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out-bookshelf' if BOOK else 'out', 'drawings')
PRODUCT = 'earmilk bookshelf' if BOOK else 'earmilk floorstander'
# drawing scales per size: the bookshelf is drawn larger so its views fill the same sheets
K = dict(ga=1 / 3, sec=1 / 3, roof=1.0, ins=1.0, back=1 / 3, exp=0.28) if BOOK else dict(ga=0.2, sec=0.2, roof=0.5, ins=0.5, back=0.2, exp=0.16)
SC = {k: f'1:{round(1 / v):d}' for k, v in K.items()}
XS = PLAN / 390.0     # model offsets that were set for the floorstander scale with the plan
A3 = (420.0, 297.0)
INK = '#111111'; LIGHT = '#777777'; RED = '#B3261E'; CUT = '#d9d4c7'
LW = dict(outline=0.5, thin=0.25, dim=0.18, hidden=0.25, centre=0.18)   # line weights, mm on paper
PT = 72 / 25.4                                                          # points per mm


# --- projection ---------------------------------------------------------------------------------------------------------
VIEWS = {   # look_from (toward the eye), look_up; 2D x = up x dir
    'front': ((0, -1, 0), (0, 0, 1)),
    'back':  ((0, 1, 0), (0, 0, 1)),
    'left':  ((-1, 0, 0), (0, 0, 1)),
    'right': ((1, 0, 0), (0, 0, 1)),
    'top':   ((0, 0, 1), (0, 1, 0)),
    'iso':   ((1, -1.2, 0.9), (0, 0, 1)),
}


def basis(view):
    d, up = (np.array(v, float) for v in VIEWS[view])
    d /= np.linalg.norm(d)
    up = up - d * (up @ d); up /= np.linalg.norm(up)
    return np.cross(up, d), up


def to2d(view, pts):
    X, Y = basis(view)
    P = np.asarray(pts, float)
    return np.c_[P @ X, P @ Y]


def hlr(shapes, view, hidden=False):
    """Visible (and hidden) edges of the shapes seen from `view`, as lists of 2D polylines in the view's frame
    (orthographic, origin at the world origin)."""
    from build123d import Compound, Drawing
    comp = Compound(children=list(shapes))
    d, up = VIEWS[view]
    dr = Drawing(comp, look_from=d, look_up=up, look_at=(0, 0, 0), with_hidden=hidden)
    def polylines(c):
        out = []
        for e in c.edges():
            L = e.length
            if L < 0.2:
                continue
            n = 2 if e.geom_type.name == 'LINE' else int(min(240, max(6, L / 1.0)))
            pts = [e.position_at(t) for t in np.linspace(0, 1, n)]
            out.append(np.array([[p.X, p.Y] for p in pts]))
        return out
    return polylines(dr.visible_lines), (polylines(dr.hidden_lines) if hidden else [])


def half(solid, plane_x, keep='TOP'):
    """The part of a solid on +x (TOP) or -x (BOTTOM) of the plane x = plane_x, or None."""
    from build123d import Plane, Keep
    try:
        h = solid.split(Plane.YZ.offset(plane_x), keep=Keep.TOP if keep == 'TOP' else Keep.BOTTOM)
        return h if h.volume > 1e-3 else None
    except Exception:
        return None


def section_faces(solid, plane_x, keep='TOP'):
    """The outlines of the faces a solid leaves on the plane x = plane_x when cut, as 3D point loops."""
    h = half(solid, plane_x, keep)
    if h is None:
        return []
    loops = []
    for f in h.faces():
        c = f.center(); n = f.normal_at(c)
        if abs(c.X - plane_x) < 0.05 and abs(abs(n.X) - 1) < 1e-3:
            for w in [f.outer_wire()] + list(f.inner_wires()):
                pts = []
                for e in w.edges():
                    m = 2 if e.geom_type.name == 'LINE' else int(min(200, max(6, e.length / 1.0)))
                    pts += [(p.X, p.Y, p.Z) for p in (e.position_at(t) for t in np.linspace(0, 1, m))]
                loops.append((np.array(pts), w is f.outer_wire()))
    return loops


# --- the sheet -----------------------------------------------------------------------------------------------------------
class Sheet:
    def __init__(self, number, title, subtitle=''):
        self.fig = plt.figure(figsize=(A3[0] / 25.4, A3[1] / 25.4))
        self.ax = self.fig.add_axes([0, 0, 1, 1]); ax = self.ax
        ax.set_xlim(0, A3[0]); ax.set_ylim(0, A3[1]); ax.set_aspect('equal'); ax.axis('off')
        ax.add_patch(Rectangle((10, 10), A3[0] - 20, A3[1] - 20, fill=False, lw=0.6 * PT, ec=INK))
        self.number, self.title = number, title
        self._title_block(subtitle)

    def _title_block(self, subtitle):
        ax = self.ax; x0, y0, w, h = A3[0] - 10 - 150, 10, 150, 26
        ax.add_patch(Rectangle((x0, y0), w, h, fill=False, lw=0.5 * PT, ec=INK))
        ax.plot([x0, x0 + w], [y0 + 13, y0 + 13], color=INK, lw=0.25 * PT)
        ax.plot([x0 + 110, x0 + 110], [y0, y0 + 13], color=INK, lw=0.25 * PT)
        ax.text(x0 + 3, y0 + 19.5, f'{PRODUCT}  |  {self.title}', fontsize=9, fontweight='bold', va='center')
        ax.text(x0 + 3, y0 + 15.2, subtitle, fontsize=5.2, va='center', color='#333')
        ax.text(x0 + 3, y0 + 8.5, 'mm  |  first issue 2026-10-08  |  from fab/sheets.py (the CAD)', fontsize=5.5, va='center')
        ax.text(x0 + 3, y0 + 3.6, 'Check every bought part against its own drawing before cutting.', fontsize=5, va='center', color='#444')
        ax.text(x0 + 130, y0 + 6.5, f'{self.number}', fontsize=16, fontweight='bold', ha='center', va='center')

    # drawing primitives in paper mm
    def lines(self, polys, origin, scale, lw=LW['outline'], color=INK, ls='-', z=3):
        ox, oy = origin
        for p in polys:
            self.ax.plot(ox + scale * p[:, 0], oy + scale * p[:, 1], color=color, lw=lw * PT, ls=ls, solid_capstyle='round', zorder=z)

    def fill(self, poly2d, origin, scale, color=CUT, hatch=None, z=1, ec=None):
        ox, oy = origin
        pts = np.c_[ox + scale * poly2d[:, 0], oy + scale * poly2d[:, 1]]
        self.ax.add_patch(MPoly(pts, closed=True, fc=color, ec=ec or 'none', lw=0.0 if ec is None else LW['thin'] * PT, hatch=hatch, zorder=z))

    def text(self, x, y, s, size=6, **kw):
        self.ax.text(x, y, s, fontsize=size, zorder=6, **kw)

    def label(self, x, y, s):
        self.ax.text(x, y, s, fontsize=8, fontweight='bold', ha='center', zorder=6)

    def dim(self, p0, p1, off, text=None, origin=(0, 0), scale=1.0, size=5.5, ext=True):
        """A linear dimension between model points p0 and p1 (2D, the view's frame), its line `off` paper mm to the side."""
        ox, oy = origin
        a = np.array([ox + scale * p0[0], oy + scale * p0[1]]); b = np.array([ox + scale * p1[0], oy + scale * p1[1]])
        d = b - a; L = np.linalg.norm(d)
        if L < 1e-6: return
        u = d / L; n = np.array([-u[1], u[0]])
        a2, b2 = a + n * off, b + n * off
        if ext:
            for p, q in ((a, a2), (b, b2)):
                self.ax.plot([p[0] + n[0] * 1.0 * np.sign(off), q[0] + n[0] * 1.5 * np.sign(off)], [p[1] + n[1] * 1.0 * np.sign(off), q[1] + n[1] * 1.5 * np.sign(off)], color=INK, lw=LW['dim'] * PT, zorder=4)
        self.ax.annotate('', xy=b2, xytext=a2, arrowprops=dict(arrowstyle='<|-|>', lw=LW['dim'] * PT, color=INK, shrinkA=0, shrinkB=0, mutation_scale=4), zorder=4)
        val = text if text is not None else f'{np.linalg.norm((np.array(p1) - np.array(p0))):.0f}'
        m = (a2 + b2) / 2 + n * 1.6
        ang = math.degrees(math.atan2(u[1], u[0]))
        if ang > 90.1 or ang < -89.9: ang += 180
        self.ax.text(m[0], m[1], val, fontsize=size, ha='center', va='center', rotation=ang, zorder=6,
                     bbox=dict(fc='white', ec='none', pad=0.3))

    def centreline(self, p0, p1, origin, scale):
        ox, oy = origin
        self.ax.plot([ox + scale * p0[0], ox + scale * p1[0]], [oy + scale * p0[1], oy + scale * p1[1]], color=RED, lw=LW['centre'] * PT, ls=(0, (8, 2, 1.5, 2)), zorder=2)

    def balloon(self, x, y, n, tx, ty):
        self.ax.plot([tx, x], [ty, y], color=INK, lw=LW['dim'] * PT, zorder=5)
        self.ax.add_patch(Circle((x, y), 3.2, fc='white', ec=INK, lw=0.3 * PT, zorder=6))
        self.ax.text(x, y, str(n), fontsize=5.5, ha='center', va='center', zorder=7)
        self.ax.add_patch(Circle((tx, ty), 0.5, fc=INK, ec='none', zorder=6))

    def notes(self, x, y, title, items, width=95, size=5.6):
        self.ax.text(x, y, title, fontsize=7, fontweight='bold', va='top', zorder=6)
        yy = y - 5
        import textwrap
        for i, it in enumerate(items):
            lines = textwrap.wrap(it, int(width / (size * 0.33)))
            for j, ln in enumerate(lines):
                self.ax.text(x + (0 if j == 0 else 3.5), yy, (f'{i + 1}. ' if j == 0 else '') + ln, fontsize=size, va='top', zorder=6)
                yy -= size * 0.48
            yy -= 0.8
        return yy

    def inset(self, x0, y0, clip, k):
        """An axes at paper (x0, y0) showing the model region clip = (x0, y0, x1, y1) at scale k, so everything outside
        the region is cut off at its edge. Returns (axes, origin, scale) to draw into with the same helpers."""
        cx0, cy0, cx1, cy1 = clip
        w, h = k * (cx1 - cx0), k * (cy1 - cy0)
        ax = self.fig.add_axes([x0 / A3[0], y0 / A3[1], w / A3[0], h / A3[1]])
        ax.set_xlim(cx0, cx1); ax.set_ylim(cy0, cy1); ax.set_aspect('equal'); ax.axis('off')
        ax.patch.set_alpha(0)
        return ax

    def save(self, pdf):
        os.makedirs(OUT, exist_ok=True)
        self.fig.savefig(os.path.join(OUT, f'sheet-{self.number}.png'), dpi=200)
        pdf.savefig(self.fig)
        plt.close(self.fig)


# --- model for drawing ---------------------------------------------------------------------------------------------------
def drawing_model():
    """Solids for projection: the cabinet's panels as cut, the gable block and the insert without the waveguide's facets
    (drawn from its equations instead), the drivers, port and terminal cup."""
    import cad
    import components as C
    from build123d import Plane
    parts = cad.build()
    # the gable block for drawing: the prism and fin with the insert's pocket outline only (no faceted air)
    g = cad.gable_prism()
    hips = [e for e in g.edges() if (abs(e.center().X) < 0.01 or abs(e.center().X - PLAN) < 0.01) and e.center().Z > BODY + 1]
    g = g.fillet(EDGE_R, hips)
    fin = cad.box(0, RUN - FIN_T / 2, RIDGE_Z - 12, PLAN, RUN + FIN_T / 2, TOTAL)
    fin = fin.fillet(FIN_EDGE_R, [e for e in fin.edges() if e.center().Z > RIDGE_Z])
    parts['gable-plain'] = g + fin
    wo, _ = C.driver_parts('woofer', C.DRIVERS[DRIVER_SET['woofer']], (RUN, 0.0, WOOFER['z']), ring_d=WOOFER_REBATE['d'] - 1.6, detail=4)
    mi = C.driver_parts('mid', C.DRIVERS[DRIVER_SET['mid']], (RUN, 0.0, MID['z']), ring_d=MID_REBATE['d'] - 1.6, detail=4)[0] if MID else {}
    tspec = dict(C.DRIVERS[DRIVER_SET['tweeter']], **{k: TWEETER_PART[k] for k in ('dome_d', 'surround_w', 'flange_d', 'flange_t', 'body_d', 'body_depth')})
    tw, _ = C.driver_parts('tweeter', tspec, (RUN, WAVEGUIDE['throat_y'], WAVEGUIDE['throat_z']), flange_recess=0.0)
    parts.update(wo); parts.update(mi); parts.update(tw)
    # the insert drawn plain too (its outline prism trimmed to the roof), for the projections; the real one for sections.
    # A spline through the outline, so its sides project as smooth faces rather than 192 facets.
    from build123d import Edge, Wire, Face, extrude, Vector
    plain = None
    try:
        out = cad.insert_outline()[::3]
        pts = [Vector(RUN + u, -5.0, BODY + DZ * s_) for (u, s_) in out]
        face = Face(Wire([Edge.make_spline(pts, periodic=True)]))
        plain = extrude(face, amount=INSERT['back_y'] + 5.0, dir=Vector(0, 1, 0)) & cad.gable_prism()
        if plain is None or not plain.is_valid or plain.volume < 1.0:
            plain = None
    except Exception:
        plain = None
    if plain is None:      # the spline failed (a sharp eave clip): the polygon prism, facets and all
        plain = cad._y_prism(cad.insert_outline(), -5.0, INSERT['back_y']) & cad.gable_prism()
    parts['insert-plain'] = plain
    return parts


def driver_circles():
    """The drivers as the front view draws them: the trim rings, the surrounds' edges, the cones and caps, as circles
    (centre x, z, diameter, weight)."""
    import components as C
    out = []
    drv = [(WOOFER['z'], DRIVER_SET['woofer'], WOOFER_REBATE['d'] - 1.6)] + ([(MID['z'], DRIVER_SET['mid'], MID_REBATE['d'] - 1.6)] if MID else [])
    for z, key, ring in drv:
        sp = C.DRIVERS[key]; _, info = C.cone_driver(sp, 4)
        out += [(RUN, z, ring, 'outline'), (RUN, z, ring - 2 * TRIM_RING['width'], 'thin'), (RUN, z, 2 * info['r_surround'], 'thin'),
                (RUN, z, 2 * info['r_cone'], 'thin'), (RUN, z, sp['cap_d'], 'thin')]
    return out


def waveguide_curves():
    """The waveguide as 3D curves: the mouth (where the lip meets the roof), the throat, the meridians every 45 deg,
    and the insert's outline on the roof."""
    from waveguide import Waveguide
    import cad
    G, ms = Waveguide(**WAVEGUIDE, sections=192).grid()
    mouth = np.vstack([G[:, -1, :], G[:1, -1, :]])
    lip_start = np.vstack([G[:, -WAVEGUIDE.get('lip_steps', 8) - 1, :], G[:1, -9, :]])
    throat = np.vstack([G[:, 0, :], G[:1, 0, :]])
    meridians = [G[k, :, :] for k in range(0, 192, 24)]
    out = cad.insert_outline()
    outline = np.array([slope_point(u, s) for (u, s) in out + out[:1]])
    return dict(mouth=mouth, lip=lip_start, throat=throat, meridians=meridians, outline=outline)


def flat(polys, ok):
    return [p for p in polys if ok(p)]


# --- sheet 1: general arrangement ------------------------------------------------------------------------------------------
GA_PARTS = ['front-baffle', 'back-panel', 'side-left', 'side-right', 'gable-plain', 'port-tube', 'terminal-cup']


def circle_pts(cx, cy, d, n=180):
    t = np.linspace(0, 2 * np.pi, n)
    return np.c_[cx + d / 2 * np.cos(t), cy + d / 2 * np.sin(t)]


def view_label(S, vis, org, k, text):
    xs = np.concatenate([p[:, 0] for p in vis]); ys = np.concatenate([p[:, 1] for p in vis])
    S.label(org[0] + k * (xs.min() + xs.max()) / 2, org[1] + k * ys.min() - 10, text)


def sheet1(pdf, M, W):
    S = Sheet(1, 'General arrangement', f'Front, left side and top at {SC["ga"]}. Heights from the floor; depths from the front face.')
    k = K['ga']
    shapes = [M[n] for n in GA_PARTS if n in M]
    # the drivers' frames and cones close their holes, or the front view shows the inside of the box through them
    occl = [M[n] for n in M if n.split('-')[0] in ('woofer', 'mid') and n.split('-')[-1] in ('frame', 'cone', 'cap', 'surround')]
    places = {'front': (34, 50), 'left': (250, 50), 'top': (300, 188)}
    for view, org in places.items():
        t = time.time()
        vis, _ = hlr(shapes + (occl if view == 'front' else []), view)
        S.lines(vis, org, k)
        if view in ('front', 'top'):
            S.lines([to2d(view, W['mouth'])], org, k, lw=LW['outline'])
            S.lines([to2d(view, W['outline'])], org, k, lw=LW['thin'], color=LIGHT)
        if view == 'front':
            S.lines([to2d(view, W['throat'])], org, k, lw=LW['thin'])
            for (cx, cz, d, w) in driver_circles():
                S.lines([circle_pts(cx, cz, d)], org, k, lw=LW[w])
        print(f'  sheet 1 {view}: {len(vis)} edges, {time.time() - t:.0f}s', flush=True)
        view_label(S, vis, org, k, {'front': 'FRONT', 'left': 'LEFT SIDE', 'top': 'TOP'}[view])
    o = places['front']
    S.centreline((RUN, -10), (RUN, TOTAL + 10), o, k)
    S.dim((0, 0), (PLAN, 0), -6, origin=o, scale=k)
    S.dim((0, 0), (0, TOTAL), 14, origin=o, scale=k)
    S.dim((0, 0), (0, BODY), 7, origin=o, scale=k)
    S.dim((0, 0), (0, PLINTH_H), 2.5, origin=o, scale=k, size=4.5)
    heights = [(WOOFER['z'], f'{WOOFER["z"]:.0f} woofer')] + ([(MID['z'], f'{MID["z"]:.0f} mid')] if MID else []) + [(WAVEGUIDE['throat_z'], f'{WAVEGUIDE["throat_z"]:.0f} tweeter axis')]
    for i, (z, lab) in enumerate(heights):
        S.dim((PLAN, 0), (PLAN, z), -8 - 7 * i, lab, origin=o, scale=k, size=5)
    for z, rb, cut in [(WOOFER['z'], WOOFER_REBATE, WOOFER_CUTOUT)] + ([(MID['z'], MID_REBATE, MID_CUTOUT)] if MID else []):
        S.text(o[0] + k * (RUN + rb['d'] / 2 + 6), o[1] + k * (z + rb['d'] / 2), f'rebate ø{rb["d"]:.1f} x {rb["depth"]:.0f} deep,\nthrough ø{cut:.0f}', size=4.2, va='bottom', color='#333')
    S.text(o[0] + k * (RUN + 150), o[1] + k * (WAVEGUIDE['throat_z'] + 50), 'waveguide insert\n(sheet 3)', size=4.5, va='bottom', color='#333')
    # left side: the depth and the throat
    o = places['left']
    S.dim((-PLAN, 0), (0, 0), -6, origin=o, scale=k)
    S.dim((-PLAN, BODY), (-PLAN, RIDGE_Z), 6, f'{RISE:.0f}', origin=o, scale=k)
    S.dim((-PLAN, RIDGE_Z), (-PLAN, TOTAL), 6, f'{FIN_H:.0f}', origin=o, scale=k)
    ty, tz = WAVEGUIDE['throat_y'], WAVEGUIDE['throat_z']
    S.ax.add_patch(Circle((o[0] - k * ty, o[1] + k * tz), 1.0, fc=RED, ec='none', zorder=6))
    S.dim((-ty, tz), (0, tz), -8, f'{ty:.0f}', origin=o, scale=k, size=5)
    S.text(o[0] - k * ty - 2, o[1] + k * tz + 1.5, 'throat\n(hidden)', size=4.2, ha='right', color=RED)
    S.text(o[0] - k * 115, o[1] + k * 930, f'{SLOPE_DEG:.1f}°', size=5.5, ha='center')
    # top
    o = places['top']
    S.dim((0, 0), (PLAN, 0), -6, origin=o, scale=k)
    S.dim((PLAN, 0), (PLAN, PLAN), 6, origin=o, scale=k)
    S.text(o[0] + k * RUN, o[1] - 16, 'black: the waveguide\'s mouth, where its lip meets the roof\ngrey: the insert\'s seam', size=4.5, ha='center', va='top')
    S.notes(300, 160, 'Notes', [
        f'Cabinet: 18 mm Baltic birch, glued. The vertical corners and the gable\'s hips are rounded {EDGE_R:.0f} mm, the fin\'s edges {FIN_EDGE_R:.0f} mm. 3 x 3 mm shadow lines at z {PLINTH_H:.0f} and z {GABLE_SHADOW_Z0:.0f}.',
        f'The drivers sit flush: each frame in a rebate, a {TRIM_RING["t"]:.0f} mm trim ring over its flange and screws, level with the finish.',
        f'The tweeter is at the throat of a waveguide insert in the roof (sheet 3): axis z {WAVEGUIDE["throat_z"]:.0f}, {WAVEGUIDE["throat_y"]:.0f} behind the front face. The shape is set by simulation (fab/out/acoustics/waveguide).',
        ('The back (the amplifier) is drawn on sheet 4 with the wiring; the Nutrition Facts are printed on the right side.' if BOOK else 'The back (port, amplifier, label) is drawn on sheet 4 with the wiring.'),
        'Finish: colour coat and 2K clear; the Facts printed between them.',
    ], width=96)
    S.save(pdf)


# --- sheet 2: section on the centreline ------------------------------------------------------------------------------------
WOOD = dict(color='#efe6d2', hatch='////')
INSERT_FILL = dict(color='#dde6ee', hatch='\\\\\\\\')
DRIVER_FILL = dict(color='#c9c9c9', hatch=None)
METAL_FILL = dict(color='#9a9a9a', hatch=None)
PRINT_FILL = dict(color='#e4e4e4', hatch='....')
SECTION_PARTS = {   # part: fill
    'front-baffle': WOOD, 'back-panel': WOOD, 'top-panel': WOOD, 'bottom-panel': WOOD, 'window-brace': WOOD,
    'mid-shelf': WOOD, 'mid-divider': WOOD, 'gable-block': WOOD, 'waveguide-insert': INSERT_FILL,
    'port-tube': PRINT_FILL, 'terminal-cup': PRINT_FILL,
    'woofer-frame': METAL_FILL, 'woofer-motor': METAL_FILL, 'woofer-cone': DRIVER_FILL, 'woofer-surround': DRIVER_FILL, 'woofer-cap': DRIVER_FILL, 'woofer-ring': METAL_FILL,
    'mid-frame': METAL_FILL, 'mid-motor': METAL_FILL, 'mid-cone': DRIVER_FILL, 'mid-surround': DRIVER_FILL, 'mid-cap': DRIVER_FILL, 'mid-ring': METAL_FILL,
    'tweeter-frame': METAL_FILL, 'tweeter-dome': DRIVER_FILL, 'tweeter-surround': DRIVER_FILL,
}
_SECTION_CACHE = {}


def centre_section(M):
    """Cut faces on x = RUN (the right half kept, seen from the left), per part, as 2D loops in the 'left' frame."""
    if 'loops' not in _SECTION_CACHE:
        loops = {}
        for name, fillspec in SECTION_PARTS.items():
            if name not in M: continue
            ls = section_faces(M[name], RUN, 'TOP')
            loops[name] = [(to2d('left', pts), outer) for (pts, outer) in ls]
        bg = [h for h in (half(M[n], RUN, 'TOP') for n in ('front-baffle', 'back-panel', 'side-right', 'top-panel', 'bottom-panel',
                                                           'window-brace', 'mid-shelf', 'mid-divider', 'gable-plain', 'port-tube') if n in M) if h is not None]
        vis, _ = hlr(bg, 'left')
        _SECTION_CACHE['loops'] = loops; _SECTION_CACHE['bg'] = vis
    return _SECTION_CACHE['loops'], _SECTION_CACHE['bg']


def draw_section(S, loops, bg, org, k, ax=None):
    """Fill the cut faces (holes cut out of their outer loops) and draw the background's edges. With `ax` (an inset
    from Sheet.inset), draw in model coordinates there, clipped to its region; else on the sheet at org and k."""
    from matplotlib.path import Path as MPath
    from matplotlib.patches import PathPatch
    tgt = ax or S.ax
    tf = (lambda p: p) if ax is not None else (lambda p: np.c_[org[0] + k * p[:, 0], org[1] + k * p[:, 1]])
    for name, ls in loops.items():
        fs = SECTION_PARTS[name]
        verts, codes = [], []
        for (p, outer) in ls:
            q = tf(p)
            verts += list(q) + [q[0]]; codes += [MPath.MOVETO] + [MPath.LINETO] * (len(q) - 1) + [MPath.CLOSEPOLY]
        if not verts: continue
        tgt.add_patch(PathPatch(MPath(verts, codes), fc=fs['color'], ec=INK, lw=LW['outline'] * PT, hatch=fs['hatch'], zorder=2))
    for p in bg:
        q = tf(p)
        tgt.plot(q[:, 0], q[:, 1], color=LIGHT, lw=LW['thin'] * PT, zorder=1.5)


def wire_paths():
    """The cables' runs in the centre section's frame (2D 'left': x = -y, y = z): tweeter, mid, woofer to the amplifier."""
    import cad
    zt = WAVEGUIDE['throat_z']; yw = cad.wire_hole_y()
    amp_y, amp_z = PLAN - WALL - 30 * XS, AMP['z']
    tweeter = [(-(WAVEGUIDE['throat_y'] + TWEETER_PART['flange_t'] + TWEETER_PART['body_depth']), zt), (-yw, zt), (-yw, TOP_Z0 - 25 * XS),
               (-(PLAN - WALL - 15 * XS), TOP_Z0 - 25 * XS), (-(PLAN - WALL - 15 * XS), amp_z + 40 * XS), (-amp_y, amp_z + 40 * XS)]
    woofer = [(-(WALL + 125 * XS), WOOFER['z']), (-(PLAN - WALL - 35 * XS), WOOFER['z']), (-(PLAN - WALL - 35 * XS), amp_z + 20 * XS), (-amp_y, amp_z + 20 * XS)]
    if not MID:
        return dict(tweeter=np.array(tweeter), woofer=np.array(woofer))
    mid = [(-(WALL + 70), MID['z']), (-(WALL + MID_CHAMBER_DEPTH + 30), MID_SHELF_TOP + 40), (-(PLAN - WALL - 25), MID_SHELF_TOP + 40),
           (-(PLAN - WALL - 25), amp_z + 30), (-amp_y, amp_z + 30)]
    return dict(tweeter=np.array(tweeter), mid=np.array(mid), woofer=np.array(woofer))


def sheet2(pdf, M, W):
    S = Sheet(2, 'Section on the centreline', f'Section A-A on the centre plane (x {RUN:.0f}) seen from the left at {SC["sec"]}, and the roof at {SC["roof"]}. Cut wood hatched; the insert hatched the other way.')
    loops, bg = centre_section(M)
    k = K['sec']; org = (110, 48)
    draw_section(S, loops, bg, org, k)
    S.label(org[0] - k * RUN, org[1] - 10, 'SECTION A-A')
    for name, path in wire_paths().items():
        S.lines([path], org, k, lw=0.35, color=RED, ls=(0, (3, 1.5)))
    import cad
    lab = lambda y, z, t, dx=-26, dy=0: (S.ax.annotate(t, xy=(org[0] - k * y, org[1] + k * z), xytext=(org[0] - k * y + dx, org[1] + k * z + dy),
                                                          fontsize=5, ha='right' if dx < 0 else 'left', va='center', zorder=7,
                                                          arrowprops=dict(arrowstyle='-', lw=LW['dim'] * PT, color=INK, shrinkA=0, shrinkB=0)))
    # labels, on the left of the section (the back) and right (the front)
    S.text(org[0] - k * (PLAN / 2), org[1] + k * 160, 'woofer chamber', size=5, ha='center')
    if MID:
        lab(WALL + 45, MID['z'] + 70, 'mid chamber,\nsealed', dx=30)
        lab(MID_REBATE['depth'] + 40, MID['z'], 'mid', dx=40)
    if PORT:
        lab(PLAN - WALL - 20, PORT['z'], 'port', dx=-8)
    lab(WOOFER_REBATE['depth'] + 60 * XS, WOOFER['z'], 'woofer', dx=40)
    lab(PLAN - WALL - 45 * XS, AMP['z'], 'amplifier\'s sealed box', dx=-14)
    lab(WAVEGUIDE['throat_y'] - 40, WAVEGUIDE['throat_z'] + 30, 'waveguide insert\nand tweeter (detail)', dx=60, dy=12)
    lab(cad.wire_hole_y(), 880, 'tweeter cable:\n14 mm channel', dx=-30, dy=14)
    S.text(org[0] - k * PLAN, org[1] - 18, 'red dashed: the cables\' runs to the amplifier (sheet 4)', size=4.6, color=RED)
    S.dim((-PLAN, 0), (0, 0), -6, origin=org, scale=k)
    if MID:
        S.dim((0, MID_SHELF_TOP), (0, TOP_Z0), 6, f'{TOP_Z0 - MID_SHELF_TOP:.0f}', origin=org, scale=k, size=4.6)
        S.dim((-WALL, TOP_Z0), (-(WALL + MID_CHAMBER_DEPTH), TOP_Z0), 4, f'{MID_CHAMBER_DEPTH:.0f}', origin=org, scale=k, size=4.6)
    # the roof at 1:2, in an inset clipped to the gable and the top of the body
    k2 = K['roof']; clip = (-PLAN - 8 * XS, BODY - 60 * XS, 12 * XS, TOTAL + 8 * XS)
    x0p, y0p = (160, 140) if BOOK else (192, 132)
    org2 = (x0p - k2 * clip[0], y0p - k2 * clip[1])
    iax = S.inset(x0p, y0p, clip, k2)
    draw_section(S, loops, bg, org2, k2, ax=iax)
    iax.plot(wire_paths()['tweeter'][:3, 0], wire_paths()['tweeter'][:3, 1], color=RED, lw=0.45 * PT, ls=(0, (3, 1.5)), zorder=5)
    S.label(org2[0] - k2 * RUN, y0p - 8, f'DETAIL: THE ROOF, {SC["roof"]}')
    ty, tz = WAVEGUIDE['throat_y'], WAVEGUIDE['throat_z']
    S.centreline((-(ty + 70), tz), (12, tz), org2, k2)
    S.dim((-ty, tz), (0, tz), -5, f'{ty:.0f} to the throat', origin=org2, scale=k2, size=5)
    S.dim((0, BODY), (0, tz), -10, f'{tz - BODY:.0f}', origin=org2, scale=k2, size=5)
    S.dim((-INSERT['back_y'], 815), (0, 815), 0, f'{INSERT["back_y"]:.0f} to the insert\'s back', origin=org2, scale=k2, size=5, ext=False)
    for (y, z, t, dx, dy) in ((ty - 60, tz + 8, 'the waveguide (air)', 50, 18), (ty - 20, BODY + 18, 'insert', 55, -6),
                              (WAVEGUIDE['throat_y'] + 20, tz + 10, 'tweeter, rear-mounted', -75, 34), (cad.wire_hole_y(), 845, 'cable channel', -45, -12),
                              (PLAN - 60, 930, 'gable block (birch)', -20, 30)):
        S.ax.annotate(t, xy=(org2[0] - k2 * y, org2[1] + k2 * z), xytext=(org2[0] - k2 * y + dx, org2[1] + k2 * z + dy), fontsize=5.2,
                      ha='left' if dx > 0 else 'right', va='center', zorder=8, arrowprops=dict(arrowstyle='-', lw=LW['dim'] * PT, color=INK))
    S.notes(250, 112, 'The roof', [
        'The waveguide insert (light blue) sits in a pocket in the gable block, 0.3 mm clear all round. It slides out forward, level, with the tweeter on it.',
        f'The tweeter is rear-mounted: its flange in a counterbore behind the throat, its dome and surround filling the {2 * WAVEGUIDE["r0"]:.0f} mm throat, so the wall runs on from the surround with no step.',
        f'Its cable leaves through the boss\'s open back into a {WIRE_HOLE_D:.0f} mm channel down through the block and the top panel, to a connector in the woofer chamber with slack for the insert\'s travel.',
        'Four magnets and two pins in the insert\'s back face meet their partners in the pocket\'s back wall (sheet 3).',
    ], width=150)
    S.save(pdf)


# --- sheet 3: the insert and the tweeter's mount ----------------------------------------------------------------------------
def sheet3(pdf, M, W):
    import cad
    S = Sheet(3, 'Waveguide insert and tweeter mount', f'The insert at {SC["ins"]}: front, section on the axis, back; the pocket; fitting and service.')
    k = K['ins']
    ins = M['waveguide-insert']
    # front view (from the front, 'front' frame: x, z)
    xs_ = W['outline'][:, 0]; xmin, xmax = xs_.min(), xs_.max()
    of = (40 - k * xmin, 205 - k * BODY)
    vis, _ = hlr([M['insert-plain']], 'front')
    S.lines(vis, of, k, lw=LW['thin'], color=LIGHT)
    S.lines([to2d('front', W['mouth'])], of, k)
    S.lines([to2d('front', W['lip'])], of, k, lw=LW['thin'])
    S.lines([to2d('front', W['throat'])], of, k)
    S.lines([to2d('front', W['outline'])], of, k, lw=LW['outline'])
    S.lines([circle_pts(RUN, WAVEGUIDE['throat_z'], TWEETER_PART['dome_d'])], of, k, lw=LW['thin'])
    for m in W['meridians']:
        S.lines([to2d('front', m)], of, k, lw=LW['dim'], color=LIGHT)
    S.centreline((RUN, BODY - 10 * XS), (RUN, RIDGE_Z - 20 * XS), of, k); S.centreline((xmin - 15 * XS, WAVEGUIDE['throat_z']), (xmax + 15 * XS, WAVEGUIDE['throat_z']), of, k)
    xs = W['outline'][:, 0]
    S.dim((xs.min(), BODY), (xs.max(), BODY), -7, f'{xs.max() - xs.min():.0f}', origin=of, scale=k)
    mw = W['mouth'][:, 0]
    ztop = W['outline'][:, 2].max() + 10 * XS
    S.dim((mw.min(), ztop), (mw.max(), ztop), 4, f'mouth {mw.max() - mw.min():.0f}', origin=of, scale=k, size=5)
    S.label(of[0] + k * RUN, of[1] + k * BODY - 16, 'FRONT')
    # section on the axis (x = RUN), from the left: the insert, the tweeter and the gable round them, in an inset
    clip = (-(INSERT['boss_back_y'] + 40 * XS), BODY - 15 * XS, 8 * XS, RIDGE_Z)
    x0p, y0p = 250, 205 - k * 15 * XS
    os_ = (x0p - k * clip[0], y0p - k * clip[1])
    loops, bg = centre_section(M)
    sub = {n: loops[n] for n in ('gable-block', 'top-panel', 'front-baffle', 'waveguide-insert', 'tweeter-frame', 'tweeter-dome', 'tweeter-surround') if n in loops}
    iax = S.inset(x0p, y0p, clip, k)
    draw_section(S, sub, [], os_, k, ax=iax)
    S.centreline((-(INSERT['boss_back_y'] + 20), WAVEGUIDE['throat_z']), (10, WAVEGUIDE['throat_z']), os_, k)
    ty, tz = WAVEGUIDE['throat_y'], WAVEGUIDE['throat_z']
    zb = BODY - 15 * XS
    S.dim((-ty, zb), (0, zb), -6, f'{ty:.0f} to the throat', origin=os_, scale=k, size=5)
    S.dim((-INSERT['boss_back_y'], zb), (-ty, zb), -6, f'{INSERT["boss_back_y"] - ty:.0f}', origin=os_, scale=k, size=5)
    S.dim((8 * XS, BODY), (8 * XS, tz), -6, f'{tz - BODY:.0f}', origin=os_, scale=k, size=5)
    S.ax.annotate(f'counterbore ø{TWEETER_PART["flange_d"] + 0.4:.1f} x {TWEETER_PART["flange_t"] + 0.2:.1f}\nfor the tweeter\'s flange', xy=(os_[0] - k * (ty + 2), os_[1] + k * (tz + TWEETER_PART['flange_d'] / 2 - 2)),
                  xytext=(os_[0] - k * (ty + 2) + 18, os_[1] + k * (tz + 55)), fontsize=5, zorder=8, arrowprops=dict(arrowstyle='-', lw=LW['dim'] * PT, color=INK))
    S.ax.annotate('the waveguide (air)', xy=(os_[0] - k * (ty - 50), os_[1] + k * (tz - 5)), xytext=(os_[0] - k * (ty - 50) + 22, os_[1] + k * (tz + 28)),
                  fontsize=5, zorder=8, arrowprops=dict(arrowstyle='-', lw=LW['dim'] * PT, color=INK))
    S.label(os_[0] - k * 110 * XS, os_[1] + k * BODY - 16, 'SECTION ON THE AXIS (WITH THE GABLE)')
    # back view: the insert from behind, magnets, pins, the boss
    ob = (40 + k * xmax, 70 - k * BODY)
    visb, _ = hlr([ins], 'back')
    S.lines(visb, ob, k, lw=LW['thin'])
    mags, pins = cad.insert_fixings()
    for (x, z) in mags:
        S.lines([circle_pts(-x, z, INSERT['magnet_d'])], ob, k, lw=LW['outline'])
        S.text(ob[0] + k * (-x), ob[1] + k * z - 5.2, f'magnet ø{INSERT["magnet_d"]:.0f}x{INSERT["magnet_t"]:.0f}', size=3.8, ha='center')
    for (x, z) in pins:
        S.lines([circle_pts(-x, z, INSERT['pin_d'])], ob, k, lw=LW['outline'])
        S.text(ob[0] + k * (-x), ob[1] + k * z - 4.5, f'pin ø{INSERT["pin_d"]:.0f}', size=3.8, ha='center')
    S.label(ob[0] + k * (-RUN), ob[1] + k * BODY - 14, 'BACK (THE FACE THAT MEETS THE POCKET)')
    S.notes(230, 112, 'Fitting the tweeter and the insert', [
        'Solder the tweeter\'s lead (2 x 1.5 mm2, 450 mm) to its tabs and fit the plug half of the connector. Feed the lead through the boss from the front.',
        f'Seat the tweeter in the counterbore from behind, dome toward the throat, on a 0.5 mm foam gasket. Fix its {TWEETER_PART["screws"]} screws into the insert (heat-set brass inserts, M3).',
        'Glue the magnets into the insert\'s back with epoxy, polarity marked, and their partners into the pocket\'s back wall, opposite poles out. Fit the two pins in the insert.',
        'From the front, feed the lead into the pocket\'s channel, plug it into the socket on the cabinet\'s lead (pulled up through the channel from the woofer chamber), push the slack back down.',
        'Slide the insert in, level, until the pins seat and the magnets pull it home: its face flush with the roof, the seam even.',
        'Service: lift it out with a suction lifter on its flat border (or a pull loop under its lower edge), unplug, and the tweeter comes out with it.',
    ], width=150)
    S.save(pdf)


# --- sheet 4: the back and the wiring ----------------------------------------------------------------------------------------
def _box(S, x, y, w, h, title, lines=(), fc='#ffffff', ec=INK, size=5.2, bold=True):
    S.ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0,rounding_size=1.5', fc=fc, ec=ec, lw=0.4 * PT, zorder=4))
    S.ax.text(x + 2, y + h - 2.2, title, fontsize=size + 0.6, fontweight='bold' if bold else 'normal', va='top', zorder=5)
    for i, ln in enumerate(lines):
        S.ax.text(x + 2, y + h - 6.4 - i * (size * 0.5), ln, fontsize=size - 0.6, va='top', zorder=5, color='#222')


def _wire(S, pts, color, lw=0.6, label=None, at=0.5):
    P = np.array(pts, float)
    S.ax.plot(P[:, 0], P[:, 1], color=color, lw=lw * PT, solid_capstyle='round', zorder=3)
    if label:
        i = int(at * (len(P) - 1)); m = (P[i] + P[min(i + 1, len(P) - 1)]) / 2
        S.ax.text(m[0], m[1] + 1.2, label, fontsize=4.6, ha='center', va='bottom', color=color, zorder=6,
                  bbox=dict(fc='white', ec='none', pad=0.2))


def sheet4(pdf, M, W):
    import components as C
    S = Sheet(4, 'Back and wiring', f'The back at {SC["back"]} and the amplifier, drivers, cables and connectors. Active: the amplifier\'s DSP is the crossover.')
    k = K['back']; o = (112, 50)
    back_parts = [M[n] for n in ('back-panel', 'gable-plain', 'side-left', 'side-right', 'port-tube') if n in M]
    vis, _ = hlr(back_parts, 'back')
    S.lines(vis, o, k)
    amp = C.amp_plate(AMP, RUN, PLAN, AMP['z'])
    va, _ = hlr([amp['amp-plate'], amp['amp-connectors'], amp['amp-rca']], 'back')
    S.lines(va, o, k, lw=LW['thin'])
    S.centreline((-RUN, -10), (-RUN, TOTAL + 10), o, k)
    lx0, lx1 = -RUN - LABEL['w'] / 2, -RUN + LABEL['w'] / 2; lz1 = LABEL['top']; lz0 = lz1 - LABEL['h']
    if LABEL.get('face', 'back') == 'back':
        S.lines([np.array([[lx0, lz0], [lx1, lz0], [lx1, lz1], [lx0, lz1], [lx0, lz0]])], o, k, lw=LW['thin'], color=LIGHT, ls='--')
        S.text(o[0] + k * (-RUN), o[1] + k * (lz0 + lz1) / 2, f'Nutrition Facts, printed\n{LABEL["w"]:.0f} x {LABEL["h"]:.0f}', size=4.3, ha='center', va='center', color='#555')
    else:
        S.text(o[0] + k * (-RUN), o[1] + k * (BODY - 20 * XS), f'(the Nutrition Facts are on the {LABEL["face"]} side: {LABEL["w"]:.0f} x {LABEL["h"]:.0f}, top at z {LABEL["top"]:.0f})', size=4.3, ha='center', color='#555')
    S.dim((0, 0), (0, AMP['z']), -6, f'{AMP["z"]:.0f}', origin=o, scale=k, size=4.8)
    if PORT:
        S.dim((0, 0), (0, PORT['z']), -12, f'{PORT["z"]:.0f}', origin=o, scale=k, size=4.8)
    if LABEL.get('face', 'back') == 'back':
        S.dim((0, 0), (0, lz1), -18, f'{lz1:.0f}', origin=o, scale=k, size=4.8)
    S.dim((-RUN - AMP['plate_w'] / 2, AMP['z'] - AMP['plate_h'] / 2), (-RUN + AMP['plate_w'] / 2, AMP['z'] - AMP['plate_h'] / 2), -5,
          f'plate {AMP["plate_w"]:.0f} x {AMP["plate_h"]:.0f}, flush in a {AMP["rebate"]:.0f} mm rebate; cutout {AMP["cut_w"]:.0f} x {AMP["cut_h"]:.0f}', origin=o, scale=k, size=4.4)
    S.dim((-PLAN, 0), (0, 0), -16, origin=o, scale=k)
    S.label(o[0] - k * RUN, o[1] - 24, 'BACK')
    # the schematic, right of the view
    X0 = 182
    red, blu, grn, gry = '#B3261E', '#1F4FCF', '#2E7D32', '#555555'
    _box(S, X0, 205, 70, 46, AMP['model'], [
        ('2 channels, DSP crossover and EQ' if BOOK else '3 channels, DSP crossover and EQ (ADAU1452)'),
        ('125 + 125 W into 4 ohm' if BOOK else '250 + 250 W into 4 ohm, 100 W tweeter channel'),
        ('upright on the back' if BOOK else 'on its side across the back\'s foot'),
        'in its own sealed box (not airtight itself)',
        'filters: Hypex Filter Design, over USB',
        'mains in on the plate (IEC C14 with switch)'], fc='#f4f4f4')
    _box(S, X0 - 2 - 40, 236, 36, 15, 'Mains', ['IEC C14 inlet, switch'], size=5)
    _box(S, X0 - 2 - 40, 214, 36, 18, 'Signal in', ['XLR (balanced) or RCA', 'USB for the DSP'], size=5)
    _wire(S, [(X0 - 6, 243), (X0, 243)], gry); _wire(S, [(X0 - 6, 223), (X0, 223)], gry)
    if BOOK:
        drivers = [('Tweeter, Scan-Speak D3004/602200', '26 mm dome, faceplate behind the insert', red, 'CH2', 1.0, 165),
                   ('Woofer, SB Acoustics SB17NRX2C35-8', '6 in, sealed box, DSP shelf to 45 Hz', grn, 'CH1', 1.5, 135)]
    else:
        drivers = [('Tweeter, SB Satori TW29DN-B', '29 mm dome, faceplate off, on the insert', red, 'CH3 (100 W)', 1.0, 177),
                   ('Midrange, SB Satori MR16P-8', '6.5 in papyrus, its own sealed chamber', blu, 'CH2', 1.5, 152),
                   ('Woofer, Dayton Audio RSS315HF-4', '12 in, 4 ohm, vented to 32 Hz', grn, 'CH1', 2.5, 127)]
    for (name, sub, col, ch, mm2, y) in drivers:
        _box(S, X0 + 96, y, 66, 17, name, [sub, f'{mm2:g} mm2 pair, red +, black -'], size=4.8)
        _wire(S, [(X0 + 70, 214 + (y - 127) / 5), (X0 + 80, 214 + (y - 127) / 5), (X0 + 80, y + 8.5), (X0 + 96, y + 8.5)], col, label=ch, at=0.7)
    # connectors and seals
    if BOOK:
        S.notes(X0 - 44, 118, 'Runs, connectors and seals', [
            'Woofer (CH1): from the amplifier box\'s gland to the woofer\'s terminals, 0.4 m of 1.5 mm2.',
            'Tweeter (CH2): up the back wall to the top panel, through the 14 mm channel in the top panel and the gable block, 0.6 m of 1.0 mm2, to a two-pole locking connector at the insert.',
            'Seal the tweeter cable where it passes the top panel (grommet and sealant): the box is sealed, and the insert\'s pocket is open to the room through its seam.',
            'The amplifier box\'s lid: a 16 mm gland for the two pairs; seal it.',
            'The crossover (about 2 to 2.5 kHz), the woofer\'s shelf to 45 Hz (+7.6 dB) and the delays are set in the DSP. Wire red to + throughout.',
        ], width=118, size=5.2)
    else:
        S.notes(X0 - 44, 118, 'Runs, connectors and seals', [
            'Woofer (CH1): from the amplifier box\'s gland straight to the woofer\'s terminals, 0.6 m of 2.5 mm2. Fit 6.3 mm push-on terminals to suit the driver.',
            'Mid (CH2): up the back wall, through the 12 mm hole in the mid chamber\'s divider, 1.0 m of 1.5 mm2. Seal the hole round the cable with putty: the mid\'s chamber must stay closed.',
            'Tweeter (CH3): up the back wall to the top panel, through the 14 mm channel in the top panel and the gable block, 1.3 m of 1.0 mm2, to a two-pole locking connector (JST VH or Molex Mini-Fit) at the insert. The supplied 1.25 m Hypex harness is too short: extend it.',
            'Seal the tweeter cable where it passes the top panel with a rubber grommet and sealant. The insert\'s pocket is open to the room through its 0.3 mm seam, so an unsealed channel would be a leak in the woofer\'s box.',
            'The amplifier box\'s lid: a 20 mm gland (PG11) for the three pairs; seal it. The box itself is glued and sealed; its front is the woofer chamber\'s wall.',
            'Polarity, delay and the crossover (about 2.8 kHz tweeter to mid, from the waveguide study) are set in the DSP: wire red to + throughout and let the filters do the rest.',
        ], width=118, size=5.2)
    S.save(pdf)


# --- sheet 5: exploded view and parts list ---------------------------------------------------------------------------------
def sheet5(pdf, M, W):
    from build123d import Pos
    S = Sheet(5, 'Exploded view and parts', 'The parts pulled apart along the way they go together, and what each one is.')
    k = K['exp']; o = (130, 92)
    mv = {   # part: (dx, dy, dz, number)
        'front-baffle': (0, -330, 0, 1), 'back-panel': (0, 330, 0, 2), 'side-left': (-300, 0, 0, 3), 'side-right': (300, 0, 0, 3),
        'top-panel': (0, 0, 80, 4), 'bottom-panel': (0, 0, -120, 5), 'window-brace': (0, 0, 0, 6), 'mid-shelf': (0, 0, 0, 7),
        'mid-divider': (0, 0, 0, 7), 'gable-plain': (0, 0, 330, 8), 'insert-plain': (0, -420, 330, 9), 'port-tube': (0, 520, 0, 10),
        'amp-box-floor': (0, 140, 0, 11), 'amp-box-lid': (0, 140, 0, 11), 'amp-box-front': (0, 140, 0, 11),
        'woofer-ring': (0, -560, 0, 13), 'woofer-frame': (0, -470, 0, 12), 'woofer-cone': (0, -470, 0, 12), 'woofer-surround': (0, -470, 0, 12),
        'woofer-motor': (0, -470, 0, 12), 'mid-ring': (0, -560, 0, 13), 'mid-frame': (0, -470, 0, 14), 'mid-cone': (0, -470, 0, 14),
        'mid-surround': (0, -470, 0, 14), 'mid-motor': (0, -470, 0, 14),
        'tweeter-frame': (0, -330, 330, 15), 'tweeter-dome': (0, -330, 330, 15), 'tweeter-surround': (0, -330, 330, 15),
    }
    import components as C
    amp = C.amp_plate(AMP, RUN, PLAN, AMP['z'])
    shapes, anchors = [], {}
    for name, (dx, dy, dz, n) in mv.items():
        if name not in M: continue
        sh = Pos(dx * XS, dy * XS, dz * XS) * M[name]
        shapes.append(sh)
        c = sh.center(); anchors.setdefault(n, (c.X, c.Y, c.Z))
    for name in ('amp-plate', 'amp-module'):
        sh = Pos(0, 600 * XS, 0) * amp[name]; shapes.append(sh); c = sh.center(); anchors.setdefault(16, (c.X, c.Y, c.Z))
    t = time.time()
    vis, _ = hlr(shapes, 'iso')
    print(f'  sheet 5 iso: {len(vis)} edges, {time.time() - t:.0f}s', flush=True)
    S.lines(vis, o, k, lw=0.3)
    if BOOK:
        rows = [
            (1, 'Front baffle', '1', '18 mm Baltic birch, CNC: the woofer\'s cutout and rebate'),
            (2, 'Back', '1', '18 mm birch: the amplifier\'s cutout and rebate'),
            (3, 'Sides', '2', '18 mm birch; the Facts printed on the right one'),
            (4, 'Top panel', '1', '18 mm birch, the tweeter cable\'s 14 mm hole, four dowel holes'),
            (5, 'Bottom panel', '1', '18 mm birch'),
            (6, 'Window brace', '1', '18 mm birch'),
            (8, 'Gable block', '1', 'laminated birch or printed whole: the insert\'s pocket and the cable channel'),
            (9, 'Waveguide insert', '1', 'printed (SLA, MJF) or CNC from solid; magnets, pins'),
            (11, 'Amplifier box', '3', '18 mm birch floor, lid (gland) and front, glued and sealed'),
            (12, 'Woofer', '1', 'SB Acoustics SB17NRX2C35-8, 6 in coated paper'),
            (13, 'Trim ring', '1', 'printed, satin black or gunmetal, over the frame and its screws'),
            (15, 'Tweeter', '1', 'Scan-Speak Illuminator D3004/602200, faceplate behind the insert'),
            (16, 'Amplifier', '1', f'{AMP["model"]}, DSP, 2 channels'),
        ]
    else:
        rows = [
            (1, 'Front baffle', '1', '18 mm Baltic birch, CNC: cutouts and rebates for the drivers'),
            (2, 'Back', '1', '18 mm birch: port hole, the amplifier\'s cutout and rebate'),
            (3, 'Sides', '2', '18 mm birch'),
            (4, 'Top panel', '1', '18 mm birch, the tweeter cable\'s 14 mm hole, four dowel holes'),
            (5, 'Bottom panel', '1', '18 mm birch'),
            (6, 'Window brace', '1', '18 mm birch'),
            (7, 'Mid chamber shelf and divider', '2', '18 mm birch; the divider\'s 12 mm cable hole'),
            (8, 'Gable block', '1', 'laminated birch, CNC: the insert\'s pocket and the cable channel'),
            (9, 'Waveguide insert', '1', 'CNC from solid (MDF, HDPE) or printed (SLA, MJF); magnets, pins'),
            (10, 'Port', '1', 'printed tube and flare collar, 92 bore'),
            (11, 'Amplifier box', '3', '18 mm birch floor, lid (gland) and front, glued and sealed'),
            (12, 'Woofer', '1', 'Dayton Audio RSS315HF-4, 12 in, 4 ohm, black anodised aluminium cone'),
            (13, 'Trim rings', '2', 'printed, satin black or gunmetal, over each frame and its screws'),
            (14, 'Midrange', '1', 'SB Acoustics Satori MR16P-8, 6.5 in papyrus cone'),
            (15, 'Tweeter', '1', 'SB Acoustics Satori TW29DN-B, faceplate off, rear-mounted on the insert'),
            (16, 'Amplifier', '1', f'{AMP["model"]}, DSP, 3 channels'),
        ]
    X, Y = 290, 262
    S.text(X, Y + 5, 'Parts', size=7, fontweight='bold')
    for i, (n, part, q, what) in enumerate(rows):
        yy = Y - i * 6.0
        S.ax.add_patch(Circle((X + 2.5, yy + 1.2), 2.2, fc='white', ec=INK, lw=0.3 * PT, zorder=6))
        S.text(X + 2.5, yy + 1.2, str(n), size=4.6, ha='center', va='center')
        S.text(X + 7, yy + 2.6, f'{part}  x{q}', size=5.0, fontweight='bold', va='top')
        S.text(X + 7, yy - 0.4, what, size=4.3, va='top', color='#333')
    for n, (x, y, z) in anchors.items():
        p2 = to2d('iso', [(x, y, z)])[0]
        px, py = o[0] + k * p2[0], o[1] + k * p2[1]
        S.balloon(px + 9, py + 7, n, px, py)
    S.save(pdf)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--only', nargs='*', type=int)
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    t = time.time(); M = drawing_model(); W = waveguide_curves(); print(f'model {time.time() - t:.0f}s', flush=True)
    with PdfPages(os.path.join(OUT, 'earmilk-sheets.pdf')) as pdf:
        for n, fn in ((1, sheet1), (2, sheet2), (3, sheet3), (4, sheet4), (5, sheet5)):
            if a.only and n not in a.only: continue
            fn(pdf, M, W)
    print('wrote', OUT)


if __name__ == '__main__':
    main()
