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
  6  Panel details: the panels the other sheets do not detail, holes dimensioned from each one's corner; the trim
     rings' sections
  7  Notes: what to measure first; sheets 1 to 3's notes by number (3.4 is sheet 3's fourth)
  8  Notes: sheets 4 to 6's notes; the glue-up order and the fixings

Every text on every sheet is 2.5 mm high or more (MIN_PT), view titles 3.5 mm, the sheet's title 5 mm (ISO 3098 at
A3); the long notes live on sheets 7 and 8 so the drawings keep their room (the drawing check's d22, round 3: at
2.5 mm they fill two sheets).

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
SHEETS = 8                                                             # sheets in each size's set: six drawings and two of notes
NOTES_ON = {1: 7, 2: 7, 3: 7, 4: 8, 5: 8, 6: 8}                        # which notes sheet holds each drawing's notes
REVISION = 'D'                                                         # B after the drawing check's round 1, C after round 2, D after round 3
MIN_PT = 10.0                                                           # the smallest text on any sheet, points: 2.5 mm caps (DejaVu Sans), ISO 3098 for A3
VIEW_PT = 14.0                                                          # view titles, 3.5 mm caps
TITLE_PT = 19.0                                                         # the sheet's title in its title block, 5 mm caps
NOTES = {}                                                              # sheet number: [(title, [note, ...]), ...], drawn on the notes sheet


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
    from build123d import Compound
    try:
        h = solid.split(Plane.YZ.offset(plane_x), keep=Keep.TOP if keep == 'TOP' else Keep.BOTTOM)
        if isinstance(h, (list, tuple)):
            h = Compound(children=list(h)) if h else None
        return h if h is not None and h.volume > 1e-3 else None
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
        """The title block, 190 x 40 at the lower right: the sheet's title (5 mm caps), the product and what the sheet
        shows, the units, issue and tolerances; the sheet's place in the set, its drawing number and revision, and the
        first-angle symbol (the drawing check's d22, rounds 2 and 3)."""
        import textwrap
        ax = self.ax; x0, y0, w, h = A3[0] - 10 - 190, 10, 190, 40
        ax.add_patch(Rectangle((x0, y0), w, h, fill=False, lw=0.5 * PT, ec=INK))
        ax.plot([x0, x0 + w], [y0 + 16, y0 + 16], color=INK, lw=0.25 * PT)
        ax.plot([x0 + 146, x0 + 146], [y0, y0 + 16], color=INK, lw=0.25 * PT)
        ax.text(x0 + 3, y0 + 34.5, self.title, fontsize=TITLE_PT, fontweight='bold', va='center')
        sub = textwrap.wrap(f'{PRODUCT}. {subtitle}', 86)
        for i, ln in enumerate(sub[:2]):
            ax.text(x0 + 3, y0 + 26.3 - i * 4.4, ln, fontsize=MIN_PT, va='center', color=INK)
        ax.text(x0 + 3, y0 + 11.2, 'mm  |  issue 2026-10-09  |  from fab/sheets.py (the CAD)', fontsize=MIN_PT, va='center')
        ax.text(x0 + 3, y0 + 5.0, 'Tolerances: panels ±0.5, pockets ±0.2, holes +0.2/0, prints ±0.15', fontsize=MIN_PT, va='center')
        ax.text(x0 + 168, y0 + 10.5, f'{self.number} of {SHEETS}', fontsize=16, fontweight='bold', ha='center', va='center')
        ax.text(x0 + 168, y0 + 3.6, f'EM-{"BS" if BOOK else "FS"}-{self.number:03d}  rev {REVISION}', fontsize=MIN_PT, ha='center', va='center')
        # first-angle projection (a view from the left is drawn to the right): the frustum and its end view, ISO 5456-2
        cx, cy = x0 + 170.0, y0 + 30.0
        ax.add_patch(MPoly([(cx - 8, cy - 1.8), (cx, cy - 3.2), (cx, cy + 3.2), (cx - 8, cy + 1.8)], closed=True, fill=False, lw=0.3 * PT, ec=INK, zorder=6))
        for r in (3.2, 1.8):
            ax.add_patch(Circle((cx + 7.5, cy), r, fill=False, lw=0.3 * PT, ec=INK, zorder=6))
        ax.plot([cx - 9.5, cx + 11.5], [cy, cy], color=INK, lw=0.15 * PT, ls=(0, (6, 1.5, 1, 1.5)), zorder=6)

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
        self.ax.text(x, y, s, fontsize=VIEW_PT, fontweight='bold', ha='center', zorder=6)

    def dim(self, p0, p1, off, text=None, origin=(0, 0), scale=1.0, size=5.5, ext=True, at=0.5):
        """A linear dimension between model points p0 and p1 (2D, the view's frame), its line `off` paper mm to the side,
        its value `at` that fraction along it (off the middle where a cutting plane's arrow crosses it there)."""
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
        m = a2 + (b2 - a2) * at + n * 1.6
        ang = math.degrees(math.atan2(u[1], u[0]))
        if ang > 90.1 or ang < -89.9: ang += 180
        self.ax.text(m[0], m[1], val, fontsize=size, ha='center', va='center', rotation=ang, zorder=6,
                     bbox=dict(fc='white', ec='none', pad=0.3))

    def dim_in(self, ax, k, p0, p1, off, text, size=5.5):
        """A dimension drawn in an inset's axes (model coordinates, `k` paper mm per model mm), above its section fills."""
        a, b = np.array(p0, float), np.array(p1, float)
        d = b - a; L = np.linalg.norm(d)
        if L < 1e-6: return
        u = d / L; n = np.array([-u[1], u[0]]); o = off / k
        a2, b2 = a + n * o, b + n * o
        # nothing clipped at the inset's edge: a dimension under the section's last panel lies outside it (the
        # bookshelf's '36' and '95 to the throat' lost their lines)
        for p, q in ((a, a2), (b, b2)):
            ax.plot([p[0] + n[0] * np.sign(o) / k, q[0] + n[0] * 1.5 * np.sign(o) / k], [p[1] + n[1] * np.sign(o) / k, q[1] + n[1] * 1.5 * np.sign(o) / k],
                    color=INK, lw=LW['dim'] * PT, zorder=10, clip_on=False)
        an = ax.annotate('', xy=b2, xytext=a2, arrowprops=dict(arrowstyle='<|-|>', lw=LW['dim'] * PT, color=INK, shrinkA=0, shrinkB=0, mutation_scale=4),
                         zorder=10, annotation_clip=False)
        an.arrow_patch.set_clip_on(False)
        m = (a2 + b2) / 2 + n * 1.6 / k
        ang = math.degrees(math.atan2(u[1], u[0]))
        if ang > 90.1 or ang < -89.9: ang += 180
        ax.text(m[0], m[1], text, fontsize=size, ha='center', va='center', rotation=ang, zorder=11, bbox=dict(fc='white', ec='none', pad=0.3), clip_on=False)

    def cutting_plane(self, p0, p1, letter, arrow_dir, origin, scale):
        """A section's cutting plane on a view: a chain line, thick at its ends, arrows the way the section looks, lettered."""
        ox, oy = origin
        a = np.array([ox + scale * p0[0], oy + scale * p0[1]]); b = np.array([ox + scale * p1[0], oy + scale * p1[1]])
        self.ax.plot([a[0], b[0]], [a[1], b[1]], color=INK, lw=0.25 * PT, ls=(0, (10, 2, 1.5, 2)), zorder=5)
        u = (b - a) / np.linalg.norm(b - a); dv = np.array(arrow_dir, float); dv /= np.linalg.norm(dv)
        for e, sgn in ((a, 1), (b, -1)):
            self.ax.plot([e[0], e[0] + sgn * u[0] * 5], [e[1], e[1] + sgn * u[1] * 5], color=INK, lw=0.7 * PT, zorder=5)
            self.ax.annotate('', xy=e + dv * 5, xytext=e, arrowprops=dict(arrowstyle='-|>', lw=0.4 * PT, color=INK, mutation_scale=6), zorder=5)
            self.ax.text(*(e + dv * 7.5), letter, fontsize=8, fontweight='bold', ha='center', va='center', zorder=6)

    def centreline(self, p0, p1, origin, scale):
        ox, oy = origin
        self.ax.plot([ox + scale * p0[0], ox + scale * p1[0]], [oy + scale * p0[1], oy + scale * p1[1]], color=RED, lw=LW['centre'] * PT, ls=(0, (8, 2, 1.5, 2)), zorder=2)

    def balloon(self, x, y, n, tx, ty):
        self.ax.plot([tx, x], [ty, y], color=INK, lw=LW['dim'] * PT, zorder=5)
        self.ax.add_patch(Circle((x, y), 4.0, fc='white', ec=INK, lw=0.3 * PT, zorder=6))
        self.ax.text(x, y, str(n), fontsize=MIN_PT, ha='center', va='center', zorder=7)
        self.ax.add_patch(Circle((tx, ty), 0.5, fc=INK, ec='none', zorder=6))

    def notes(self, x, y, title, items, width=95, size=5.6):
        """The sheet's notes go on a notes sheet (7 or 8, NOTES_ON) at 2.5 mm, numbered by sheet (3.1, 3.2, ...); here a line
        says where (they ran to 1.5 mm high here: the drawing check's d22, round 3). Returns the y under it."""
        NOTES.setdefault(self.number, []).append((title, list(items)))
        first = sum(len(it) for (_, it) in NOTES[self.number][:-1])
        a, b = first + 1, first + len(items)
        self.ax.text(x, y, f'{title}: notes {self.number}.{a} to {self.number}.{b}, sheet {NOTES_ON[self.number]}', fontsize=MIN_PT, fontweight='bold', va='top', zorder=6)
        return y - 6

    def inset(self, x0, y0, clip, k):
        """An axes at paper (x0, y0) showing the model region clip = (x0, y0, x1, y1) at scale k, so everything outside
        the region is cut off at its edge. Returns (axes, origin, scale) to draw into with the same helpers."""
        cx0, cy0, cx1, cy1 = clip
        w, h = k * (cx1 - cx0), k * (cy1 - cy0)
        ax = self.fig.add_axes([x0 / A3[0], y0 / A3[1], w / A3[0], h / A3[1]])
        ax.set_xlim(cx0, cx1); ax.set_ylim(cy0, cy1); ax.set_aspect('equal'); ax.axis('off')
        ax.patch.set_alpha(0)
        ax.set_zorder(self.ax.get_zorder() - 1)     # under the sheet's axes, so leaders and labels drawn there cross it
        return ax

    def save(self, pdf):
        # no text under MIN_PT: the drawing check (d25) found notes down to 1 mm high at A3. 2.5 mm (10 pt) would need a
        # sheet more for the notes; MIN_PT is the floor these layouts hold without overlapping
        import matplotlib.text as mtext
        for t in self.fig.findobj(mtext.Text):
            if 0 < t.get_fontsize() < MIN_PT:
                t.set_fontsize(MIN_PT)
            if t.get_color() in ('#555', '#555555', '#333', '#333333', '#444', '#444444'):
                t.set_color('#222222')     # notes print near black (grey #555 was faint: d22, round 3)
        os.makedirs(OUT, exist_ok=True)
        self.fig.savefig(os.path.join(OUT, f'sheet-{self.number}.png'), dpi=200)
        pdf.savefig(self.fig)
        plt.close(self.fig)


# --- model for drawing ---------------------------------------------------------------------------------------------------
def _cad_parts(cad):
    """The CAD's solids: the STEP files fab/cad.py exported, when every one is there and newer than the sources they come
    from (or EARMILK_SHEETS_STEP=1 says to use them anyway, to lay out sheets quickly), else built again."""
    from build123d import import_step
    here = os.path.dirname(os.path.abspath(__file__))
    names = ['front-baffle', 'back-panel', 'side-left', 'side-right', 'top-panel', 'bottom-panel', 'gable-block', 'waveguide-insert']
    names += (['tweeter-retainer'] if RETAINER else []) + (['window-brace'] if BRACE_Z else []) + (['mid-shelf', 'mid-divider'] if MID else [])
    names += (['port-tube'] if PORT else []) + (['amp-box-floor', 'amp-box-lid', 'amp-box-front'] if AMP else ['terminal-cup'])
    step = os.path.join(here, 'out-bookshelf' if BOOK else 'out', 'step')
    files = [os.path.join(step, f'{n}.step') for n in names]
    if all(os.path.exists(f) for f in files):
        newest_src = max(os.path.getmtime(os.path.join(here, f)) for f in ('cad.py', 'params.py', 'components.py', 'waveguide.py'))
        if os.environ.get('EARMILK_SHEETS_STEP') == '1' or min(os.path.getmtime(f) for f in files) > newest_src:
            print('  the solids from out/step (fab/cad.py\'s export)', flush=True)
            return {n: import_step(f) for n, f in zip(names, files)}
    return cad.build()


def drawing_model():
    """Solids for projection: the cabinet's panels as cut, the gable block and the insert without the waveguide's facets
    (drawn from its equations instead), the drivers, port and terminal cup."""
    import cad
    import components as C
    from build123d import Plane
    parts = _cad_parts(cad)
    # the gable block for drawing: the prism and fin with the insert's pocket outline only (no faceted air)
    g = cad.gable_prism()
    hips = [e for e in g.edges() if (abs(e.center().X) < 0.01 or abs(e.center().X - PLAN) < 0.01) and e.center().Z > BODY + 1]
    g = g.fillet(EDGE_R, hips)
    fin = cad.box(0, RUN - FIN_T / 2, RIDGE_Z - 12, PLAN, RUN + FIN_T / 2, TOTAL)
    fin = fin.fillet(FIN_EDGE_R, [e for e in fin.edges() if e.center().Z > RIDGE_Z])
    parts['gable-plain'] = g + fin
    wo, _ = C.driver_parts('woofer', C.DRIVERS[DRIVER_SET['woofer']], (RUN, 0.0, WOOFER['z']), ring_d=WOOFER_REBATE['d'] - 1.6, detail=4, ring_id=TRIM_RING_ID['woofer'])
    mi = C.driver_parts('mid', C.DRIVERS[DRIVER_SET['mid']], (RUN, 0.0, MID['z']), ring_d=MID_REBATE['d'] - 1.6, detail=4, ring_id=TRIM_RING_ID['mid'])[0] if MID else {}
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
    try:
        parts['gable-pocket'] = parts['gable-plain'] - plain     # the roof with its pocket, so the insert has somewhere to go
    except Exception:
        parts['gable-pocket'] = parts['gable-plain']
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
    S.label(org[0] + k * (xs.min() + xs.max()) / 2, org[1] + k * ys.min() - 13, text)


def _typeset():
    """fab/typeset.py's numbers (the wordmark's ink box, the marks' widths), or {} before it has run."""
    import json
    f = os.path.join(os.path.dirname(OUT), 'typeset.json')
    try:
        return json.load(open(f))
    except Exception:
        return {}


def _letters_note():
    tj = _typeset().get('wordmark', {})
    w, h = tj.get('ink_width_mm'), tj.get('ink_height_mm')
    size = (f'{w:.1f} x {h:.1f} of ink, ' if w else '')
    return (f'The cast letters (out/metal/wordmark-letters.*), {BADGE["relief"]:g} proud: {size}centred across the plinth\'s front, the badge\'s centre z '
            f'{BADGE["z"]:g}; on the back the same at z {BACK_BADGE["z"]:g}. Place and drill them from the 1:1 templates, '
            'out/metal/wordmark-template-front.pdf and -back.pdf, after the clear coat.')


def sheet1(pdf, M, W):
    S = Sheet(1, 'General arrangement', f'Front, left side and top at {SC["ga"]}. Heights from the floor; depths from the front face.')
    k = K['ga']
    shapes = [M[n] for n in GA_PARTS if n in M]
    # the drivers' frames and cones close their holes, or the front view shows the inside of the box through them
    occl = [M[n] for n in M if n.split('-')[0] in ('woofer', 'mid') and n.split('-')[-1] in ('frame', 'cone', 'cap', 'surround')]
    places = {'front': (34, 65), 'left': (250, 65), 'top': (300, 188)}     # 65 up: the left side's label clears the title block
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
        view_label(S, vis, org, k, {'front': 'FRONT', 'left': 'LEFT SIDE', 'top': 'VIEW T (FROM ABOVE)'}[view])
    o = places['front']
    S.centreline((RUN, -10), (RUN, TOTAL + 10), o, k)
    S.dim((0, 0), (PLAN, 0), -6, origin=o, scale=k)
    S.dim((0, 0), (0, TOTAL), 14, f'{TOTAL:g}', origin=o, scale=k)
    S.dim((0, 0), (0, BODY), 7, origin=o, scale=k)
    S.dim((0, 0), (0, PLINTH_H), 2.5, origin=o, scale=k, size=4.5)
    heights = [(WOOFER['z'], f'{WOOFER["z"]:.0f} woofer')] + ([(MID['z'], f'{MID["z"]:.0f} mid')] if MID else []) + [(WAVEGUIDE['throat_z'], f'{WAVEGUIDE["throat_z"]:.0f} tweeter axis')]
    for i, (z, lab) in enumerate(heights):
        S.dim((PLAN, 0), (PLAN, z), -8 - 7 * i, lab, origin=o, scale=k, size=5)
    for role, z, rb, cut in [('woofer', WOOFER['z'], WOOFER_REBATE, WOOFER_CUTOUT)] + ([('mid', MID['z'], MID_REBATE, MID_CUTOUT)] if MID else []):
        sc = DRIVER_SCREWS.get(role)
        # the frame's screw holes on their bolt circle
        if sc:
            for kk in range(sc['n']):
                a_ = math.radians(sc['start_deg'] + 360.0 * kk / sc['n'])
                S.lines([circle_pts(RUN + sc['pcd'] / 2 * math.cos(a_), z + sc['pcd'] / 2 * math.sin(a_), sc['hole'], 24)], o, k, lw=LW['thin'])
        # the note inside the front, in the larger clear face above or below the driver (the heights' dimensions run
        # outside it on the right), its leader to the rebate's edge on that side
        edges = sorted([PLINTH_H, BODY] + [zz + s_ * r_['d'] / 2 for (zz, r_) in [(WOOFER['z'], WOOFER_REBATE)] + ([(MID['z'], MID_REBATE)] if MID else [])
                                          if zz != z for s_ in (-1, 1)])
        up = min([e for e in edges if e > z]) - (z + rb['d'] / 2); down = (z - rb['d'] / 2) - max([e for e in edges if e < z])
        sg = 1 if up * k >= 14 else (-1 if down * k >= 14 else (1 if up >= down else -1))   # above when 14 mm of sheet allow it
        tx, ty_ = o[0] + k * RUN, o[1] + k * (z + sg * rb['d'] / 2) + sg * 6.5
        S.ax.annotate(f'rebate ø{rb["d"]:g} x {rb["depth"]:g} deep, through ø{cut:g}' +
                      (f';\n{sc["n"]} x ø{sc["hole"]:g} on ø{sc["pcd"]:g} for M4 T-nuts (1.2, M{2 if role == "woofer" else 3})' if sc else ''),
                      xy=(o[0] + k * (RUN + rb['d'] / 2 * 0.5), o[1] + k * (z + sg * rb['d'] / 2 * 0.866)), xytext=(tx, ty_), fontsize=4.6, ha='center', va='center',
                      color='#333', zorder=7, bbox=dict(fc='white', ec='none', pad=0.4),
                      arrowprops=dict(arrowstyle='-', lw=LW['dim'] * PT, color=INK, shrinkA=0, shrinkB=0))
    # the view from above (VIEW T), placed by its arrow: in first angle it would sit under the front, where the sheet ends
    ax_, ay_ = o[0] + k * RUN, o[1] + k * TOTAL
    S.ax.annotate('', xy=(ax_, ay_ + 2.0), xytext=(ax_, ay_ + 9.0), arrowprops=dict(arrowstyle='-|>', lw=0.5 * PT, color=INK, mutation_scale=8), zorder=6)
    S.ax.text(ax_ + 2.5, ay_ + 6.5, 'T', fontsize=VIEW_PT, fontweight='bold', va='center', zorder=6)
    # the cast letters: their ink box on the plinth, from fab/typeset.py's own numbers
    tj = _typeset()
    if tj.get('wordmark'):
        bx0, bz0, bx1, bz1 = tj['wordmark']['ink_box_front_mm']
        S.lines([np.array([[bx0, bz0], [bx1, bz0], [bx1, bz1], [bx0, bz1], [bx0, bz0]])], o, k, lw=LW['thin'], ls=(0, (2, 1)))
        S.text(o[0] + k * RUN, o[1] + k * (bz1 + 4) + 1.0, 'cast letters (1.6)', size=MIN_PT, ha='center', va='bottom')
    S.ax.annotate('waveguide insert (sheet 3)', xy=(o[0] + k * (RUN + 60 * XS), o[1] + k * (WAVEGUIDE['throat_z'] + 30 * XS)),
                  xytext=(o[0] + k * (PLAN + 30 * XS), o[1] + k * (WAVEGUIDE['throat_z'] + 70 * XS)), fontsize=4.6, va='center', color='#333', zorder=7,
                  arrowprops=dict(arrowstyle='-', lw=LW['dim'] * PT, color=INK, shrinkA=0, shrinkB=0))
    # left side: the depth and the throat
    o = places['left']
    S.dim((-PLAN, 0), (0, 0), -6, origin=o, scale=k)
    S.dim((-PLAN, BODY), (-PLAN, RIDGE_Z), 6, f'{RISE:g}', origin=o, scale=k)
    S.dim((-PLAN, RIDGE_Z), (-PLAN, TOTAL), 6, f'{FIN_H:g}', origin=o, scale=k)
    ty, tz = WAVEGUIDE['throat_y'], WAVEGUIDE['throat_z']
    S.ax.add_patch(Circle((o[0] - k * ty, o[1] + k * tz), 1.0, fc=RED, ec='none', zorder=6))
    S.dim((-ty, tz), (0, tz), -8, f'{ty:.0f}', origin=o, scale=k, size=5)
    S.text(o[0] - k * ty - 2.0, o[1] + k * tz - 1.5, 'throat\n(hidden)', size=4.2, ha='right', va='top', color=RED)    # under the slopes, clear of them
    S.text(o[0] - k * (PLAN - 0.18 * PLAN), o[1] + k * BODY + 2.2, f'{SLOPE_DEG:.1f}°', size=5.5, ha='center', va='bottom')     # in the back slope's eave
    S.ax.annotate(f'fin {FIN_T:g} thick, centred on the ridge\n(y {RUN - FIN_T / 2:g} to {RUN + FIN_T / 2:g}), edges R{FIN_EDGE_R:g}',
                  xy=(o[0] - k * RUN + k * FIN_T / 2, o[1] + k * (TOTAL - 0.4 * FIN_H)), xytext=(o[0] - k * RUN + 8, o[1] + k * TOTAL - 1),
                  fontsize=MIN_PT, ha='left', va='center', zorder=7, arrowprops=dict(arrowstyle='-', lw=LW['dim'] * PT, color=INK, shrinkA=0, shrinkB=0))
    # top
    o = places['top']
    S.dim((0, 0), (PLAN, 0), -6, origin=o, scale=k, at=0.3)
    S.dim((PLAN, 0), (PLAN, PLAN), -8, origin=o, scale=k)
    # section A-A (sheet 2): the centre plane, seen from the left (looking toward +x)
    S.cutting_plane((RUN, -12), (RUN, PLAN + 12), 'A', (1, 0), o, k)
    S.text(o[0] + k * RUN, o[1] - 16, 'black: the waveguide\'s mouth, where its lip meets the roof\ngrey: the insert\'s seam', size=4.5, ha='center', va='top')
    S.notes(300, 160, 'Notes', [
        f'Cabinet: 18 mm Baltic birch, glued. The vertical corners and the gable\'s hips are rounded {EDGE_R:.0f} mm, the fin\'s edges {FIN_EDGE_R:.0f} mm. 3 x 3 mm shadow lines at z {PLINTH_H:.0f} and z {GABLE_SHADOW_Z0:.0f}.',
        (f'The drivers sit flush: each rebate is the measured flange + 1.0 (a 1.5 mm closed-cell foam gasket, pressed) + {TRIM_RING["t"]:.0f} (the ring): '
         + ', '.join(f'{r} {rb["depth"]:g} for a {rb["depth"] - 1.0 - TRIM_RING["t"]:g} flange' for (r, rb) in [('woofer', WOOFER_REBATE)] + ([('mid', MID_REBATE)] if MID else []))
         + '; measure each flange before cutting (M2, M3): the rebate is the flange + 4.0 only while 7.5 of birch stays under it for the T-nuts. '
         + 'The screws and T-nuts as F1, pressed in before the glue-up. '
         + 'A printed trim ring over each flange (stl/trim-ring-*.stl, ' + ', '.join(f'{r} ø{(rb["d"] - 1.6):g} / ø{TRIM_RING_ID[r]:g} x {TRIM_RING["t"]:g}' for (r, rb) in [('woofer', WOOFER_REBATE)] + ([('mid', MID_REBATE)] if MID else []))
         + ', flat, a channel in its back over the screws\' heads: the sections at 2:1 on sheet 6) held by three 5 mm dots of neutral-cure silicone, 0.8 reveal all round. Its inner ø is the surround at its glue line + 2: measure the drivers and print the rings last (the woofer\'s ring needs a 320 bed, or a print service).'),
        f'The tweeter is at the throat of a waveguide insert in the roof (sheet 3): axis z {WAVEGUIDE["throat_z"]:g}, {WAVEGUIDE["throat_y"]:g} behind the front face. The shape is set by simulation (fab/{os.path.basename(os.path.dirname(OUT))}/acoustics/waveguide).',
        ('The back (the amplifier) is drawn on sheet 4 with the wiring; the Nutrition Facts are printed on the right side.' if BOOK else 'The back (port, amplifier, label) is drawn on sheet 4 with the wiring.'),
        'Finish: colour coat and 2K clear; the Facts printed between them.',
        _letters_note(),
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
    'amp-box-floor': WOOD, 'amp-box-lid': WOOD, 'amp-box-front': WOOD,
    'mid-shelf': WOOD, 'mid-divider': WOOD, 'gable-block': WOOD, 'waveguide-insert': INSERT_FILL,
    'port-tube': PRINT_FILL, 'terminal-cup': PRINT_FILL,
    'woofer-frame': METAL_FILL, 'woofer-motor': METAL_FILL, 'woofer-cone': DRIVER_FILL, 'woofer-surround': DRIVER_FILL, 'woofer-cap': DRIVER_FILL, 'woofer-ring': METAL_FILL,
    'mid-frame': METAL_FILL, 'mid-motor': METAL_FILL, 'mid-cone': DRIVER_FILL, 'mid-surround': DRIVER_FILL, 'mid-cap': DRIVER_FILL, 'mid-ring': METAL_FILL,
    'tweeter-frame': METAL_FILL, 'tweeter-dome': DRIVER_FILL, 'tweeter-surround': DRIVER_FILL, 'tweeter-retainer': PRINT_FILL,
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
                                                           'window-brace', 'mid-shelf', 'mid-divider', 'gable-plain', 'port-tube',
                                                           'amp-box-floor', 'amp-box-lid', 'amp-box-front') if n in M) if h is not None]
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
    """The cables' runs in the centre section's frame (2D 'left': x = -y, y = z): every one leaves the amplifier's box
    through the gland in its lid; the tweeter's and the mid's go up on the gland's line, inside the brace's window
    (its frame is solid from 322 to 372 in the floorstander), the woofer's forward to the woofer."""
    import cad
    zt = WAVEGUIDE['throat_z']; yw = cad.wire_hole_y()
    gx, gy = cad.amp_gland_xy(); y0, y1, z0, z1 = cad.amp_box_extent()
    inside = (-(PLAN - WALL - 30 * XS), AMP['z'])            # at the amplifier's module
    out_ = z1 + WALL + 12 * XS                                # just above the gland
    tweeter = [(-(WAVEGUIDE['throat_y'] + TWEETER_PART['flange_t'] + TWEETER_PART['body_depth']), zt), (-yw, zt), (-yw, TOP_Z0 - 25 * XS),
               (-gy, TOP_Z0 - 25 * XS), (-gy, out_), (-gy, z1), inside]
    woofer = [(-(WALL + 125 * XS), WOOFER['z']), (-(gy - 14 * XS), WOOFER['z']), (-(gy - 14 * XS), out_), (-(gy - 14 * XS), z1), inside]
    if not MID:
        return dict(tweeter=np.array(tweeter), woofer=np.array(woofer))
    mid = [(-(WALL + 70), MID['z']), (-(WALL + MID_CHAMBER_DEPTH + 30), MID_SHELF_TOP + 40), (-(gy - 7), MID_SHELF_TOP + 40),
           (-(gy - 7), out_), (-(gy - 7), z1), inside]
    return dict(tweeter=np.array(tweeter), mid=np.array(mid), woofer=np.array(woofer))


def _port_note():
    import cad
    L_ = cad.port_length_mm()
    return (f'The port: a {PORT["bore"]:g} bore, its tube {PORT["bore"] + 2 * PORT_WALL:g} outside in a ø{PORT["bore"] + 2 * PORT_WALL + 0.5:g} hole through the back, '
            f'centre z {PORT["z"]:g}; its ø{PORT["flange"]:g} x {PORT_FLANGE_T:g} flange glued to the finish. {L_:g} from the flange\'s face, with the {PORT_FLARE_R:g} '
            f'flare collar {L_ + PORT_FLARE_R:g} long. Printed {L_ + PORT_TRIM:g} and trimmed at its inner end until the impedance dip sits at the tuning (README).')


def sheet2(pdf, M, W):
    S = Sheet(2, 'Section on the centreline', f'Section A-A on the centre plane (x {RUN:.0f}), from the left, at {SC["sec"]}; the roof at {SC["roof"]}. The insert hatched the other way.')
    loops, bg = centre_section(M)
    k = K['sec']; org = (120 if BOOK else 132, 48)     # its back about 50 mm from the sheet's edge: room for the back's labels
    draw_section(S, loops, bg, org, k)
    S.label(org[0] - k * RUN, org[1] - 13, 'SECTION A-A')
    for name, path in wire_paths().items():
        S.lines([path], org, k, lw=0.35, color=RED, ls=(0, (3, 1.5)))
    import cad
    lab = lambda y, z, t, dx=-26, dy=0: (S.ax.annotate(t, xy=(org[0] - k * y, org[1] + k * z), xytext=(org[0] - k * y + dx, org[1] + k * z + dy),
                                                          fontsize=5, ha='right' if dx < 0 else 'left', va='center', zorder=7,
                                                          arrowprops=dict(arrowstyle='-', lw=LW['dim'] * PT, color=INK, shrinkA=0, shrinkB=0)))
    # labels, on the left of the section (the back) and right (the front)
    yfb = PLAN - WALL - AMP_BOX['depth'] - WALL          # the amplifier box's front face: the label sits in front of it
    S.text(org[0] - k * min(PLAN / 2, (WALL + yfb) / 2), org[1] + k * 160, 'woofer chamber', size=5, ha='center')
    if MID:
        lab(WALL + 45, MID['z'] + 70, 'mid chamber,\nsealed', dx=30)
        lab(MID_REBATE['depth'] + 40, MID['z'], 'mid', dx=40)
    if PORT:
        import cad as cad_
        L_ = cad_.port_length_mm()
        lab(PLAN - WALL - 20, PORT['z'], f'port: ø{PORT["bore"]:g} bore,\nø{PORT["bore"] + 2 * PORT_WALL:g} in a ø{PORT["bore"] + 2 * PORT_WALL + 0.5:g}\nhole, {L_ + PORT_FLARE_R:g} long\n(2.5)', dx=-8)
    lab(WOOFER_REBATE['depth'] + 60 * XS, WOOFER['z'], 'woofer', dx=40)
    yb0, yb1, zb0, zb1 = cad.amp_box_extent()
    lab(PLAN - WALL - 45 * XS, AMP['z'], f'amplifier\'s\nbox, sealed:\n{AMP_BOX["depth"]:g} clear,\nz {zb0:g}\nto {zb1:g}', dx=-14)
    if not BOOK:      # the bookshelf's roof detail is drawn large and its labels fill that space: its ring, lettered C, says it
        lab(WAVEGUIDE['throat_y'] - 40, WAVEGUIDE['throat_z'] + 30, 'waveguide insert\nand tweeter\n(detail C)', dx=60, dy=12)
    lab(cad.wire_hole_y(), 880, 'tweeter cable:\n14 mm channel', dx=-30, dy=14)
    S.text(org[0] - k * PLAN, org[1] - 21, 'red dashed: the cables\' runs to the amplifier (sheet 4)', size=4.6, color=RED)
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
    S.label(org2[0] - k2 * RUN, y0p - 11, f'DETAIL C, {SC["roof"]}')
    # the detail's boundary on section A-A, lettered (d24, round 3)
    cx0, cz0, cx1, cz1 = -PLAN - 6 * XS, BODY - 40 * XS, 8 * XS, TOTAL + 8 * XS
    S.lines([np.array([[cx0, cz0], [cx1, cz0], [cx1, cz1], [cx0, cz1], [cx0, cz0]])], org, k, lw=LW['thin'], ls=(0, (6, 1.5, 1, 1.5)))
    S.ax.text(org[0] + k * cx0 - 1.5, org[1] + k * cz1 + 1.5, 'C', fontsize=VIEW_PT, fontweight='bold', ha='right', va='bottom', zorder=6)
    ty, tz = WAVEGUIDE['throat_y'], WAVEGUIDE['throat_z']
    S.centreline((-(ty + 70), tz), (12, tz), org2, k2)
    S.dim_in(iax, k2, (-ty, tz + 60 * XS), (0, tz + 60 * XS), 0, f'{ty:g} to the throat', size=5)
    S.dim_in(iax, k2, (0, BODY), (0, tz), -10, f'{tz - BODY:g}', size=5)
    S.dim_in(iax, k2, (-INSERT['back_y'], tz + 15 * XS), (0, tz + 15 * XS), 0, f'{INSERT["back_y"]:g} to the insert\'s back', size=5)
    for (y, z, t, dx, dy) in ((ty - 60, tz + 8, 'the waveguide (air)', 15 if BOOK else 12, 45 if BOOK else 18),
                              (WAVEGUIDE['throat_y'] + 20, tz + 10, 'tweeter, rear-mounted', -75, 34), (cad.wire_hole_y(), BODY - 15, 'cable channel', -45, -12),
                              (cad.wire_hole_y() + 6, tz + INSERT['bay_dz'] + 6, 'connector bay', -40, 30),
                              # the two solids named on themselves, in white, under the waveguide's floor and in the block
                              (0.5 * ty, BODY + 0.35 * (tz - WAVEGUIDE['r0'] - BODY), 'insert', 0, 0),
                              (0.73 * PLAN, BODY + 0.27 * RISE, 'gable block (birch)', 0, 0)):
        xy_ = (org2[0] - k2 * y, org2[1] + k2 * z)
        if dx == 0 and dy == 0:
            S.ax.text(xy_[0], xy_[1], t, fontsize=5.2, ha='center', va='center', zorder=8, bbox=dict(fc='white', ec='none', pad=0.3))
            continue
        S.ax.annotate(t, xy=xy_, xytext=(xy_[0] + dx, xy_[1] + dy), fontsize=5.2,
                      ha='left' if dx > 0 else 'right', va='center', zorder=8, bbox=dict(fc='white', ec='none', pad=0.3),
                      arrowprops=dict(arrowstyle='-', lw=LW['dim'] * PT, color=INK))
    S.notes(250, 112, 'The roof', [
        f'The waveguide insert (light blue) sits in a pocket in the gable block, {INSERT["clear"]:g} mm clear all round: the pocket +0.2/0, the insert 0/-0.15, so 0.3 to 0.65 a side. Paint only the insert\'s face: mask its sides, base and back and the pocket\'s walls. It slides out forward, level, with the tweeter on it.',
        (f'The tweeter is rear-mounted: it goes in from behind through a ø{TWEETER_PART["flange_d"] + 0.4:g} bore and its front ring seats on the ring round the throat, its dome and surround filling the {2 * WAVEGUIDE["r0"]:g} mm throat, so the wall runs on from the surround with no step. A printed sleeve over its motor holds it there, screwed to the boss\'s back face (sheet 3).'
         if RETAINER else
         f'The tweeter is rear-mounted: it goes in from behind through a ø{TWEETER_PART["flange_d"] + 0.4:g} bore and its faceplate seats on the ring round the throat, its dome and surround filling the {2 * WAVEGUIDE["r0"]:g} mm throat, screwed from behind through its own holes (sheet 3).'),
        f'Its lead leaves the boss\'s open back into the connector bay behind it (ø{INSERT["bay_d"]:.0f} x {INSERT["bay_l"]:.0f} deep), where it plugs into the cabinet\'s lead; that runs down a {WIRE_HOLE_D:.0f} mm channel through the block and the top panel, sealed round the cable with neutral-cure silicone from the bay.',
        'Four magnets and two pins in the insert\'s back face meet their partners in the pocket\'s back wall (sheet 3).',
    ] + ([_port_note()] if PORT else []), width=150)
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
    S.centreline((xmin - 15 * XS, WAVEGUIDE['throat_z']), (xmax + 15 * XS, WAVEGUIDE['throat_z']), of, k)
    S.cutting_plane((RUN, BODY - 12 * XS), (RUN, RIDGE_Z - 15 * XS), 'B', (1, 0), of, k)    # section B-B, seen from the left
    xs = W['outline'][:, 0]
    S.dim((xs.min(), BODY), (xs.max(), BODY), -7, f'{xs.max() - xs.min():.1f} (pocket {xs.max() - xs.min() + 2 * INSERT["clear"]:.1f})', origin=of, scale=k, at=0.3)
    # its height, so the pocket's ceiling can be checked against the boss behind it (the drawing check's d1, round 3)
    zo = W['outline'][:, 2].max()
    S.dim((RUN, BODY), (RUN, zo), k * (RUN - xs.min()) + 8, f'{zo - BODY:.1f}', origin=of, scale=k, size=5)     # on the left: the section's labels fill the right
    mw = W['mouth'][:, 0]
    ztop = W['outline'][:, 2].max() + 10 * XS
    S.dim((mw.min(), ztop), (mw.max(), ztop), 4, f'mouth {mw.max() - mw.min():.0f}', origin=of, scale=k, size=5, at=0.3)
    S.label(of[0] + k * RUN, of[1] + k * BODY - 16, 'FRONT')
    # section on the axis (x = RUN), from the left: the insert, the tweeter and the gable round them, in an inset
    clip = (-(INSERT['boss_back_y'] + 40 * XS), BODY - 40 * XS, 8 * XS, RIDGE_Z)
    x0p, y0p = 250, (190 if BOOK else 205) - k * 40 * XS     # the bookshelf's is drawn larger: lower, to clear the border
    os_ = (x0p - k * clip[0], y0p - k * clip[1])
    loops, bg = centre_section(M)
    sub = {n: loops[n] for n in ('gable-block', 'top-panel', 'front-baffle', 'waveguide-insert', 'tweeter-frame', 'tweeter-dome', 'tweeter-surround',
                                 'tweeter-retainer') if n in loops}
    iax = S.inset(x0p, y0p, clip, k)
    draw_section(S, sub, [], os_, k, ax=iax)
    S.centreline((-(INSERT['boss_back_y'] + 20), WAVEGUIDE['throat_z']), (10, WAVEGUIDE['throat_z']), os_, k)
    ty, tz = WAVEGUIDE['throat_y'], WAVEGUIDE['throat_z']
    zb = TOP_Z0 - 6.0 / k                 # 6 mm of sheet under the top panel, clear of its hatching
    S.dim_in(iax, k, (-ty, zb), (0, zb), 0, f'{ty:g} to the throat', size=5)
    S.dim_in(iax, k, (-INSERT['boss_back_y'], zb), (-ty, zb), 0, f'{INSERT["boss_back_y"] - ty:g}', size=5)
    S.dim_in(iax, k, (6 * XS, BODY), (6 * XS, tz), 0, f'{tz - BODY:g}', size=5)
    S.ax.annotate(f'bore ø{TWEETER_PART["flange_d"] + 0.4:g} from the back:\nthe tweeter goes in from behind,\nits {"front ring" if RETAINER else "faceplate"} seats at the throat (y {ty:g})', xy=(os_[0] - k * (ty + 8), os_[1] + k * (tz + TWEETER_PART['flange_d'] / 2 - 2)),
                  xytext=(os_[0] - k * (ty + 2) + 18, os_[1] + k * (tz + 55 * XS)), fontsize=5, zorder=8, arrowprops=dict(arrowstyle='-', lw=LW['dim'] * PT, color=INK))
    wxy = (os_[0] - k * (ty - 50), os_[1] + k * (tz - 5))
    S.ax.annotate('the waveguide (air)', xy=wxy, xytext=((wxy[0] - 4, wxy[1] + 12) if BOOK else (wxy[0] + 22, os_[1] + k * (tz + 28))),
                  fontsize=5, ha='center' if BOOK else 'left', zorder=8, arrowprops=dict(arrowstyle='-', lw=LW['dim'] * PT, color=INK))
    # the wiring in the section: the tweeter's lead into the bay, the connector at the channel's mouth, the cabinet's
    # lead down the channel and through the top panel, sealed there with silicone (the same runs as the render model's)
    I_, T_ = INSERT, TWEETER_PART
    yw = cad.wire_hole_y(); zbay = tz + I_['bay_dz']; zcon = cad.connector_z()     # the mated pair standing in the bay (d12, round 3)
    lead = np.array([(ty + T_['flange_t'] + T_['body_depth'] - 2, tz - 6), (I_['boss_back_y'] + 4, zbay + 4),
                     (yw + I_['bay_l'] / 2 - 6, zbay + 6), (yw + 2, zcon + 16), (yw, zcon + 11)])
    down = np.array([(yw, zcon - 11), (yw, BODY - 38 * XS)])
    for pth in (lead, down):
        iax.plot(-pth[:, 0], pth[:, 1], color=RED, lw=0.9 * PT, solid_capstyle='round', zorder=6)
    iax.add_patch(Rectangle((-(yw + 4), zcon - 12), 8, 24, fc='#f4f1e8', ec=INK, lw=0.4 * PT, zorder=7))
    iax.plot([-(yw + 4), -(yw - 4)], [zcon, zcon], color=INK, lw=0.3 * PT, zorder=8)
    iax.add_patch(Rectangle((-(yw + WIRE_HOLE_D / 2), zbay - I_['bay_d'] / 2 - 20), WIRE_HOLE_D, 20, fc='#bdbdbd', ec=INK, lw=0.3 * PT, zorder=7))   # the silicone plug
    # labels to the left, right-aligned in the gap between the front view and this section
    gx_ = lambda y: x0p - 7 - (os_[0] - k * y)
    # the lead's label sits under the bay's: its target is further in and lower, so their leaders do not cross
    labs = []
    for (y, z, t, dx, dy) in ((I_['boss_back_y'] + 2, zbay + 4, f'tweeter\'s own lead, 2 x 0.75 mm2 flex', gx_(I_['boss_back_y'] + 2), 12),
                              (yw, zcon - 4, 'connector, 2 pole, locking\n(JST VH): plug on the lead,\nsocket on the cabinet\'s', gx_(yw), -12),
                              (yw + I_['bay_l'] / 2 - 4, zbay + I_['bay_d'] / 2 - 4, f'connector bay ø{I_["bay_d"]:.0f}', gx_(yw + I_['bay_l'] / 2 - 4), 30),
                              (yw, zbay - I_['bay_d'] / 2 - 10, 'silicone round the cable,\n20 deep, from the bay', gx_(yw), -24),
                              (yw, (BODY + zcon - 12) / 2, f'channel ø{WIRE_HOLE_D:.0f}', gx_(yw), -32),
                              (yw, BODY - 36 * XS, 'to the amplifier\n(sheet 4)', gx_(yw), -30)):
        labs.append([y, z, t, dx, os_[1] + k * z + dy])
    # stacked from the top: a label that would overlap the one above it moves down (at 1:1 the bookshelf's silicone and
    # channel labels printed over each other)
    hgt = lambda L_: 4.3 * (L_[2].count('\n') + 1)
    order = sorted(range(len(labs)), key=lambda j_: -labs[j_][4])
    for p_, i_ in zip(order, order[1:]):          # each under the one above it, in their order down the sheet
        labs[i_][4] = min(labs[i_][4], labs[p_][4] - hgt(labs[p_]) / 2 - 1.5 - hgt(labs[i_]) / 2)
    for (y, z, t, dx, ty_) in labs:
        S.ax.annotate(t, xy=(os_[0] - k * y, os_[1] + k * z), xytext=(os_[0] - k * y + dx, ty_), fontsize=4.8,
                      ha='right' if dx < 0 else 'left', va='center', zorder=9, color=INK,
                      arrowprops=dict(arrowstyle='-', lw=LW['dim'] * PT, color=INK, shrinkA=0, shrinkB=0))
    S.label(os_[0] - k * 110 * XS, os_[1] + k * BODY - 18 - k * 25 * XS, 'SECTION B-B (WITH THE GABLE)')
    if cad.insert_printed_in_halves():
        # the halves' pins cross the section's plane, the split: drawn as their circles, and named (d13, round 3)
        for (py, pz) in cad.insert_split_pins():
            iax.add_patch(Circle((-py, pz), 1.6, fc='white', ec=INK, lw=0.4 * PT, zorder=9))
        py, pz = max(cad.insert_split_pins(), key=lambda p_: p_[1])      # named at the upper one, over the insert in clear paper
        S.ax.annotate('split pins ø3.2 x 16, two (3.9)', xy=(os_[0] - k * py, os_[1] + k * pz), xytext=(os_[0] - k * py + 30, os_[1] + k * pz),
                      fontsize=MIN_PT, ha='left', va='center', zorder=9, bbox=dict(fc='white', ec='none', pad=0.3),
                      arrowprops=dict(arrowstyle='-', lw=LW['dim'] * PT, color=INK, shrinkA=0, shrinkB=0))
    if not RETAINER:
        # the bookshelf's tweeter seats its faceplate's front on the throat's ring: that face must be flat (d7, round 3)
        S.ax.annotate('its faceplate\'s front flat from\nthe throat to its edge, the grille\noff: measure first (M3)',
                      xy=(os_[0] - k * (ty + 1), os_[1] + k * (tz - TWEETER_PART['flange_d'] / 2 + 3)),
                      xytext=(os_[0] - k * ty + 24, os_[1] + k * tz - 12), fontsize=MIN_PT, ha='left', va='center', zorder=9,     # in the waveguide's air
                      bbox=dict(fc='white', ec='none', pad=0.3), arrowprops=dict(arrowstyle='-', lw=LW['dim'] * PT, color=INK, shrinkA=0, shrinkB=0))
    # back view: the insert from behind, magnets, pins, the boss
    ob = (40 + k * xmax, 70 - k * BODY)
    visb, _ = hlr([ins], 'back')
    S.lines(visb, ob, k, lw=LW['thin'])
    mags, pins = cad.insert_fixings()
    for (x, z) in mags:
        S.lines([circle_pts(-x, z, INSERT['magnet_d'])], ob, k, lw=LW['outline'])
        S.text(ob[0] + k * (-x), ob[1] + k * (z + INSERT['magnet_d'] / 2) + 2.0, f'magnet ø{INSERT["magnet_d"]:g}x{INSERT["magnet_t"]:g}', size=4.6, ha='center')
    for (x, z) in pins:     # labelled outboard: above, they run into the magnets' circles
        S.lines([circle_pts(-x, z, INSERT['pin_d'])], ob, k, lw=LW['outline'])
        sx = 1 if -x > -RUN else -1
        S.text(ob[0] + k * (-x + sx * INSERT['pin_d'] / 2) + sx * 1.5, ob[1] + k * z, f'pin ø{INSERT["pin_d"]:g}', size=4.6,
               ha='left' if sx > 0 else 'right', va='center')
    # the throat as a closed circle seen through the bore (the wall's creases broke it into slots: d26)
    S.lines([circle_pts(-RUN, WAVEGUIDE['throat_z'], 2 * WAVEGUIDE['r0'])], ob, k, lw=LW['thin'])
    T_ = TWEETER_PART
    if RETAINER:
        # the retaining sleeve's three pilots in the boss's back face
        pts = cad.retainer_screw_points()
        for (x, z) in pts:
            S.lines([circle_pts(-x, z, RETAINER['pilot_d'])], ob, k, lw=LW['outline'])
        hx, hz = pts[0]
        # three lines from the frame's left edge, clear of the back view (two right-aligned on the pilot ran off the sheet)
        S.ax.annotate(f'{RETAINER["screws"]} x ø{RETAINER["pilot_d"]:g} x {RETAINER["pilot_depth"]:g} pilots on ø{RETAINER["screw_circle"]:g} in the boss\'s back face,\n'
                      + ("one at the top" if abs(RETAINER.get('start_deg', 0.0) - 90.0) < 1 else "one on the horizontal at the speaker's right (left here)")
                      + f', 120° apart, for the retaining sleeve\'s\n{RETAINER["screw"]}',
                      xy=(ob[0] + k * (-hx), ob[1] + k * hz), xytext=(16, ob[1] + k * (WAVEGUIDE['throat_z'] + 75 * XS)),
                      fontsize=4.6, ha='left', va='center', zorder=8, arrowprops=dict(arrowstyle='-', lw=LW['dim'] * PT, color=INK, shrinkA=0, shrinkB=0))
    else:
        # the faceplate's screws' inserts in the seat, seen through the bore
        pts = cad.seat_screw_points()
        for (x, z) in pts:
            S.lines([circle_pts(-x, z, INSERT_SCREW['hole_d'])], ob, k, lw=LW['thin'])
        hx, hz = pts[0]
        S.ax.annotate(f'{T_["screws"]} x ø{INSERT_SCREW["hole_d"]:g} x {INSERT_SCREW["depth"]:g} holes on ø{T_["bolt_circle"]:g} in the seat, one at the top, 120° apart,\n'
                      f'for {INSERT_SCREW["insert"]} inserts bonded with {INSERT_SCREW["bond"]};\n'
                      f'{INSERT_SCREW["screw"]} through the faceplate: measure it first',
                      xy=(ob[0] + k * (-hx), ob[1] + k * hz), xytext=(16, ob[1] + k * (WAVEGUIDE['throat_z'] + 75 * XS)),
                      fontsize=4.6, ha='left', va='center', zorder=8, arrowprops=dict(arrowstyle='-', lw=LW['dim'] * PT, color=INK, shrinkA=0, shrinkB=0))
    S.label(ob[0] + k * (-RUN), ob[1] + k * BODY - 14, 'BACK (THE FACE THAT MEETS THE POCKET)')
    S.notes(230, 130, 'Fitting the tweeter and the insert', [
        f'Solder the tweeter\'s own lead ({TWEETER_LEAD["l"]:g} mm of {TWEETER_LEAD["wire"]}) to its tabs and crimp the plug half of a two-pole locking connector (JST VH) on its end.',
        (f'Pass the tweeter in from behind through the ø{T_["flange_d"] + 0.4:g} bore, dome first, and seat its front ring on a {RETAINER["gasket"]:g} mm foam gasket on the throat\'s seat. '
         f'Slide the printed retaining sleeve (stl/tweeter-retainer.stl: bore ø{T_["body_d"] + 2 * RETAINER["clear"]:g}, outside ø{T_["flange_d"] + 0.4 - 2 * RETAINER["fit"]:g}, flange ø{RETAINER["flange_d"]:g} x {RETAINER["flange_t"]:g}) over its motor, '
         f'lead through it, and drive its {RETAINER["screws"]} {RETAINER["screw"]} into the boss until the ring is held: no thread to SB\'s own screw holes is needed. Measure the motor first: the sleeve\'s bore is its diameter + {2 * RETAINER["clear"]:g}.'
         if RETAINER else
         f'Bond {T_["screws"]} {INSERT_SCREW["insert"]} inserts into the seat with {INSERT_SCREW["bond"]} (ø{INSERT_SCREW["hole_d"]:g} x {INSERT_SCREW["depth"]:g} holes on ø{T_["bolt_circle"]:g}; a heat-set insert will not melt into cured resin). '
         f'Pass the tweeter in from behind through the ø{T_["flange_d"] + 0.4:g} bore, dome first, seat its faceplate on a 0.5 mm foam gasket and screw it to the inserts with {INSERT_SCREW["screw"]} through its own holes. '
         f'Measure first: the heads need 0.5 clear of the body (the circle at least the body + {INSERT_SCREW["head_d"] + 1:g}).'),
        f'Glue the magnets into the insert\'s back with epoxy, polarity marked, and their partners into the pocket\'s back wall, opposite poles out. Bond the two pins into the insert with epoxy.',
        (f'The cabinet\'s lead runs up the channel and ends in the socket standing in the bay, {LEAD_ABOVE_GROMMET:g} mm above the top panel\'s underside (30 past the bay\'s floor); '
         f'seal the channel round it with 20 mm of neutral-cure silicone from the bay before the first fitting. The slack is the tweeter\'s own lead, {TWEETER_LEAD["l"]:g} mm of '
         f'{TWEETER_LEAD["wire"]}: hold the insert just in front of its pocket, plug the lead into the socket in the bay, and slide the insert home; the lead folds into the sleeve and the bay.'),
        f'Slide the insert in, level, until the pins seat and the magnets pull it home: its face flush with the roof, the seam even. Fit: the pocket +0.2/0, the insert 0/-0.15 ({INSERT["clear"]:g} to {INSERT["clear"] + 0.35:g} a side); paint only the insert\'s face.',
        f'Service: pull it out by a ribbon loop glued in the {PULL_GROOVE_NOTE} groove under its front edge, unplug, and the tweeter comes out with it.',
        pocket_note(cad),
        fixings_note(cad),
    ] + ([_halves_note(cad)] if cad.insert_printed_in_halves() else []), width=265)     # about 165 mm wide: at 95 the eight notes ran into the title block
    S.save(pdf)


def _halves_note(cad):
    (y1, z1), (y2, z2) = cad.insert_split_pins()
    return ('Printing the insert: one piece from a service (SLA tough resin or MJF nylon, a build of 290 x 220 x 130 or more) is the default, with no '
            'seam in the waveguide. On a desktop resin printer (218 x 123 x 220) print it in halves split at the centre plane, the section B-B: each half '
            f'fits only tilted (about 209 x 117 x 213). Join them with two ø3.2 x 16 steel pins across the split, at y {y1:.1f}, z {z1:.1f} and y {y2:.1f}, '
            f'z {z2:.1f} (3.2 holes, 8 deep each side), and epoxy; fill and sand the seam on the waveguide\'s wall flush.')


def fixings_note(cad):
    """Where the magnets and pins sit and how they fit, the same in the insert's back and the pocket's back wall (mirrored)."""
    mags, pins = cad.insert_fixings()
    I = INSERT
    def where(pts):
        seen = []
        for (x, z) in pts:
            t = f'±{abs(x - RUN):.1f} across, {z - BODY:.1f} up'
            if t not in seen: seen.append(t)
        return '; '.join(seen)
    return (f'Fixings, from the centreline and the insert\'s base (mirrored in the pocket\'s wall): magnets {where(mags)}; pins {where(pins)}. '
            f'Magnets ø{I["magnet_d"]:g} x {I["magnet_t"]:g} in ø{I["magnet_d"] + 0.2:g} x {I["magnet_t"] + 0.3:g} holes, epoxied, poles marked; '
            f'pins ø{I["pin_d"]:g} x {I["pin_l"]:g} bonded with epoxy in ø{I["pin_d"] + 0.1:g} x {I["pin_l"] / 2 + 0.5:g} in the insert, a slip fit in ø{I["pin_d"] + 0.2:g} x {I["pin_l"] / 2 + 0.5:g} in the wall '
            f'(these holes are outside the title block\'s +0.2/-0).')


PULL_GROOVE_NOTE = '12 x 1.5 x 30'


def pocket_note(cad):
    """The pocket in the gable block, dimensioned from cad.json's features (the drawing check's d6): what the CNC or the
    printed block must have for the insert, its tweeter and the connector."""
    f = cad.features()['insert']; p = f['pocket']
    bb = cad.insert_pocket().bounding_box()
    dw = ', '.join(f'({x:g}, {y:g})' for (x, y) in cad.dowel_points())
    return (f'The pocket (gable-block.step): the insert\'s outline + {p["clear"]:g} a side ({bb.max.X - bb.min.X:.1f} wide at its base), from the slope to its back wall at '
            f'y {p["back_wall_y"]:g}; the boss\'s bore ø{p["boss_bore_d"]:g} to y {p["boss_bore_to_y"]:g}; the connector bay ø{p["bay"]["d"]:g} from y {p["bay"]["from_y"]:g} '
            f'to {p["bay"]["to_y"]:g} on an axis at z {p["bay"]["axis_z"]:g}; the channel ø{f["channel"]["d"]:g} at x {f["channel"]["x"]:g}, y {f["channel"]["y"]:g} down to the '
            f'top panel; internal corners R3 or less (the insert\'s match); dowel holes ø{DOWEL_D:g} x {DOWEL_DEPTH:g} in the base at {dw}.')


# --- sheet 4: the back and the wiring ----------------------------------------------------------------------------------------
def _box(S, x, y, w, h, title, lines=(), fc='#ffffff', ec=INK, size=MIN_PT, bold=True):
    S.ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0,rounding_size=1.5', fc=fc, ec=ec, lw=0.4 * PT, zorder=4))
    S.ax.text(x + 2, y + h - 2.0, title, fontsize=size, fontweight='bold' if bold else 'normal', va='top', zorder=5)
    for i, ln in enumerate(lines):
        S.ax.text(x + 2, y + h - 7.0 - i * 4.3, ln, fontsize=size, va='top', zorder=5, color='#222')


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
        S.text(o[0] + k * (-RUN), o[1] - 30, f'The Nutrition Facts go on the {LABEL["face"]} side: {LABEL["w"]:g} x {LABEL["h"]:g}, top at z {LABEL["top"]:g},\n'
               f'centred across its depth, {(PLAN - LABEL["w"]) / 2:g} from each vertical corner.', size=4.6, ha='center', va='top', color='#555')
    S.dim((0, 0), (0, AMP['z']), -6, f'{AMP["z"]:.0f}', origin=o, scale=k, size=4.8)
    if PORT:
        S.dim((0, 0), (0, PORT['z']), -12, f'{PORT["z"]:.0f}', origin=o, scale=k, size=4.8)
    if LABEL.get('face', 'back') == 'back':
        S.dim((0, 0), (0, lz1), -18, f'{lz1:.0f}', origin=o, scale=k, size=4.8)
    # the plate's rebate dimensioned on the view (its width under it, its height off the left edge), and its note in the
    # clear face above it, inside the back's outline
    rw, rh = AMP['plate_w'] + 1, AMP['plate_h'] + 1; zb_, zt_ = AMP['z'] - rh / 2, AMP['z'] + rh / 2
    S.dim((-RUN - rw / 2, zb_), (-RUN + rw / 2, zb_), -4 if BOOK else -7, f'{rw:g} rebate', origin=o, scale=k, size=4.6)   # its value clear of the plinth's line
    S.dim((-RUN - rw / 2, zb_), (-RUN - rw / 2, zt_), k * (PLAN - RUN - rw / 2) + 6, f'{rh:g} rebate', origin=o, scale=k, size=4.6)
    z_above = (PORT['z'] - PORT['flange'] / 2) if PORT else (BODY - 6.0 / k)
    S.ax.annotate(f'plate {AMP["plate_w"]:g} x {AMP["plate_h"]:g}, in a\n{rw:g} x {rh:g} x {AMP["rebate"]:g} rebate;\ncut-out {AMP["cut_w"]:g} x {AMP["cut_h"]:g}, R3 (4.1)',
                  # the bookshelf's back wordmark sits just over its plate: the note goes right of the view instead
                  xy=((o[0] + k * (-RUN + rw / 2), o[1] + k * (AMP['z'] - rh / 4)) if BOOK else (o[0] + k * (-RUN + rw * 0.3), o[1] + k * zt_)),
                  xytext=((o[0] + 16, o[1] + 45) if BOOK else (o[0] + k * (-RUN), o[1] + k * (zt_ + z_above) / 2)), fontsize=4.6, ha='left' if BOOK else 'center', va='center',
                  color='#333', zorder=7, bbox=dict(fc='white', ec='none', pad=0.4), arrowprops=dict(arrowstyle='-', lw=LW['dim'] * PT, color=INK, shrinkA=0, shrinkB=0))
    S.dim((-PLAN, 0), (0, 0), -16, origin=o, scale=k)
    S.label(o[0] - k * RUN, o[1] - 26, 'BACK')
    # the cast letters and the two stencilled marks on the back, from fab/typeset.py's numbers (d19, round 3)
    tj = _typeset(); wm = tj.get('wordmark'); mk = tj.get('marks', {})
    def mark_box(cx, cz, w, h, text, dx=0.0, dy=0.0, below=False):
        S.lines([np.array([[cx - w / 2, cz - h / 2], [cx + w / 2, cz - h / 2], [cx + w / 2, cz + h / 2], [cx - w / 2, cz + h / 2], [cx - w / 2, cz - h / 2]])],
                o, k, lw=LW['thin'], ls=(0, (2, 1)))
        if text and below:
            S.text(o[0] + k * cx + dx, o[1] + k * (cz - h / 2) - 1.0 + dy, text, size=MIN_PT, ha='center', va='top')
        elif text:
            S.text(o[0] + k * cx + dx, o[1] + k * (cz + h / 2) + 1.0 + dy, text, size=MIN_PT, ha='center', va='bottom')
    if wm:
        bx0, bz0, bx1, bz1 = wm['ink_box_front_mm']; dz = BACK_BADGE['z'] - BADGE['z']
        mark_box(-RUN, (bz0 + bz1) / 2 + dz, bx1 - bx0, bz1 - bz0, 'cast letters (1.6)')
    if 'SHAKE WELL' in mk:
        # its label under it: over it, the plate rebate's dimension printed on it
        m_ = mk['SHAKE WELL']; mark_box(-RUN, MARK_SHAKE['z'], m_['ink_width_mm'], m_['cap_height_mm'], 'stencil (4.9)' if not BOOK else 'stencil (4.8)', below=True)
    if 'OPEN OTHER SIDE' in mk:
        m_ = mk['OPEN OTHER SIDE']; w_ = min(m_['ink_width_mm'], PLAN - 20)
        mark_box(-RUN, RIDGE_Z + FIN_H / 2, w_, m_['cap_height_mm'], '')
        S.ax.annotate('stencil on the fin (4.9)' if not BOOK else 'stencil on the fin (4.8)', xy=(o[0] + k * (-RUN + w_ / 2), o[1] + k * (RIDGE_Z + FIN_H / 2)),
                      xytext=(o[0] + k * (-RUN), o[1] + k * TOTAL + 8), fontsize=MIN_PT, ha='center', va='center', zorder=7,     # over the view: right of it the schematic's boxes start
                      arrowprops=dict(arrowstyle='-', lw=LW['dim'] * PT, color=INK, shrinkA=0, shrinkB=0))
    # the schematic, right of the view
    X0 = 205
    red, blu, grn, gry = '#B3261E', '#1F4FCF', '#2E7D32', '#555555'
    _box(S, X0, 212, 118, 54, AMP['model'], [
        ('2 channels, DSP crossover and EQ' if BOOK else '3 channels, DSP crossover and EQ (ADAU1452)'),
        ('125 + 125 W into 4 ohm' if BOOK else '250 + 250 W into 4 ohm, 100 W tweeter channel'),
        ('upright on the back' if BOOK else 'on its side across the back\'s foot'),
        'in its own sealed box (not airtight itself)',
        'filters: Hypex Filter Design, over USB',
        'mains in on the plate (IEC C14 with switch)'], fc='#f4f4f4')
    _box(S, X0 - 72, 250, 64, 16, 'Mains', ['IEC C14 inlet, switch'])
    _box(S, X0 - 72, 220, 64, 24, 'Signal in', ['XLR or RCA', 'USB for the DSP'])
    _wire(S, [(X0 - 8, 258), (X0, 258)], gry); _wire(S, [(X0 - 8, 232), (X0, 232)], gry)
    if BOOK:
        drivers = [('Tweeter, Scan-Speak D3004/602200', '26 mm dome, faceplate behind the insert', red, 'CH2', 1.0, 176),
                   ('Woofer, SB Acoustics SB17NRX2C35-8', '6 in, sealed, DSP shelf to 45 Hz', grn, 'CH1', 1.5, 148)]
    else:
        drivers = [('Tweeter, SB Satori TW29DN-B', '29 mm dome, faceplate off, on the insert', red, 'CH3 (100 W)', 1.0, 180),
                   ('Midrange, SB Satori MR16P-8', '6.5 in papyrus, its own sealed chamber', blu, 'CH2', 1.5, 152),
                   ('Woofer, Dayton Audio RSS315HF-4', '12 in, 4 ohm, vented to 32 Hz', grn, 'CH1', 2.5, 124)]
    for i, (name, sub, col, ch, mm2, y) in enumerate(drivers):
        _box(S, X0 + 85, y, 112, 22, name, [sub, f'{mm2:g} mm2 pair, red +, black -'])
        xw = X0 + 20 + 16 * (len(drivers) - 1 - i)     # the top box's wire nearest the boxes: no wire crosses another
        _wire(S, [(xw, 212), (xw, y + 11), (X0 + 85, y + 11)], col, label=ch, at=0.45)
    # connectors and seals
    if BOOK:
        S.notes(X0 - 72, 118, 'Runs, connectors and seals', [
            _plate_note(),
            'Woofer (CH1): from its gland in the amplifier box\'s lid to the woofer\'s terminals, 0.4 m of 1.5 mm2.',
            f'Tweeter (CH2): from its gland up behind the woofer\'s magnet to the top panel, through the 14 mm channel in the top panel and the gable block, 0.6 m of 1.0 mm2, ending {LEAD_ABOVE_GROMMET:g} above the top panel\'s underside in the socket of a two-pole locking connector (JST VH) standing in the bay behind the insert.',
            'Seal the tweeter cable in its channel with 20 mm of neutral-cure silicone from the bay (sheet 3): the box is sealed, and the insert\'s pocket is open to the room through its seam.',
            'Round-sheathed cable (H05VV-F 2 x 1.5 and 2 x 1.0 mm2, about 8.0 and 6.4 across), so each gland grips its cable and the silicone seals round the tweeter\'s; splice any extension of Hypex\'s harness inside the amplifier\'s box (crimped butt splices under heat-shrink).',
            gland_note(),
            f'The crossover (2.4 kHz, LR4), the woofer\'s shelf to 45 Hz (+{shelf_db():g} dB) and the delays are set in the DSP. Wire red to + throughout.',
            _stencils_note(),
        ], width=118, size=5.2)
    else:
        S.notes(X0 - 72, 118, 'Runs, connectors and seals', [
            _plate_note(),
            'Woofer (CH1): from its gland in the amplifier box\'s lid straight to the woofer\'s terminals, 0.6 m of 2.5 mm2. Fit 6.3 mm push-on terminals to suit the driver.',
            'Mid (CH2): from its gland up through the brace\'s window, 30 mm in from its back edge, then through the 12 mm hole in the mid chamber\'s divider (x 75, z 630), 1.0 m of 1.5 mm2. Seal the hole round the cable with putty: the mid\'s chamber must stay closed.',
            f'Tweeter (CH3): from its gland up through the brace\'s window to the top panel, through the 14 mm channel in the top panel and the gable block, 1.2 m of 1.0 mm2, ending {LEAD_ABOVE_GROMMET:g} above the top panel\'s underside in the socket of a two-pole locking connector (JST VH) standing in the bay behind the insert. The supplied 1.25 m Hypex harness is too short once it is spliced: extend it (4.6).',
            'Seal the tweeter cable in its channel with 20 mm of neutral-cure silicone from the bay (sheet 3). The insert\'s pocket is open to the room through its 0.3 mm seam, so an unsealed channel would be a leak in the woofer\'s box.',
            'Round-sheathed cable (H05VV-F 2 x 2.5, 2 x 1.5 and 2 x 1.0 mm2, about 9.0, 8.0 and 6.4 across), so each gland grips its cable and the silicone seals round the tweeter\'s; splice the tweeter\'s extension to Hypex\'s harness inside the amplifier\'s box (crimped butt splices under heat-shrink).',
            gland_note() + ' The box itself is glued and sealed; its front is the woofer chamber\'s wall.',
            'Polarity, delay and the crossover (about 2.8 kHz tweeter to mid, from the waveguide study) are set in the DSP: wire red to + throughout and let the filters do the rest.',
            _stencils_note(),
        ], width=118, size=5.2)
    S.save(pdf)


def _plate_note():
    return (f'The amplifier\'s plate ({AMP["plate_w"]:g} x {AMP["plate_h"]:g} x {AMP["plate_t"]:g}) lies on 3 mm EPDM tape in its {AMP["rebate"]:g} deep rebate, '
            f'R{AMP["plate_r"] + 0.5:g} corners, its module through the {AMP["cut_w"]:g} x {AMP["cut_h"]:g} cut-out (R3 corners: a 6 mm cutter or smaller). '
            f'Drill its screw holes ø3.5 through the {WALL - AMP["rebate"]:g} left under the rebate, from the plate in hand, centred in its flange, 8 or 10 to suit it: '
            '4.3 x 16 self-tapping pan heads (Hypex\'s 4.3 x 25 kit also works, its tips 7 mm into the sealed box).')


def _stencils_note():
    return (f'The stencils (out/marks/stencil-*.svg), sprayed through vinyl masks before the clear: SHAKE WELL, {MARK_SHAKE["type"]:g} mm type, centred on the '
            f'plinth\'s back at z {MARK_SHAKE["z"]:g}; OPEN OTHER SIDE, {MARK_OPEN["type"]:g} mm type with its arrow, centred on the fin\'s back face.')


def gland_note():
    """The amplifier box's glands, from AMP_BOX: one M16 per cable (a multi-hole seal could not take three cables of
    three sizes: the drawing check's d8, round 3), long-thread for the 18 mm lid."""
    import cad
    gl = cad.amp_glands_xy(); y0 = cad.amp_box_extent()[0]
    xs = ', '.join(f'{gx - WALL:g}' for (gx, _) in gl)
    cb_d, cb_t = AMP_BOX['nut_cb']
    return (f'The amplifier box\'s lid: {len(gl)} {AMP_BOX["gland"]} long-thread (15 mm) cable glands, one per cable (clamping about 4.5 to 10), '
            f'in ø{AMP_BOX["gland_hole"]:g} holes {xs} from the left side\'s inner face and {gl[0][1] - (y0 - WALL):g} from the lid\'s front edge, each lock nut '
            f'in a ø{cb_d:g} x {cb_t:g} counterbore under the lid. Fit them after the finish, the bodies from above and the nuts from below through the '
            f'amplifier\'s cut-out; feed the cables, then tighten.')


def shelf_db():
    import json
    try:
        return json.load(open(os.path.join(os.path.dirname(OUT), 'acoustics.json')))['linkwitz_transform']['low_shelf_db']
    except Exception:
        return 8.3


# --- sheet 5: exploded view and parts list ---------------------------------------------------------------------------------
def sheet5(pdf, M, W):
    from build123d import Pos
    S = Sheet(5, 'Exploded view and parts', 'Isometric, not to scale: the parts pulled apart along the way they go together, and what each one is.')
    k = K['exp'] if BOOK else 0.15; o = (130, 80) if BOOK else (130, 76)     # the bookshelf's fin clear of the border
    mv = {   # part: (dx, dy, dz, number)
        'front-baffle': (0, -330, 0, 1), 'back-panel': (0, 330, 0, 2), 'side-left': (-300, 0, 0, 3), 'side-right': (300, 0, 0, 3),
        'top-panel': (0, 0, 80, 4), 'bottom-panel': (0, 0, -120, 5), 'window-brace': (0, 0, 0, 6), 'mid-shelf': (0, 0, 0, 7),
        'mid-divider': (0, 0, 0, 7), 'gable-pocket': (0, 0, 330, 8), 'insert-plain': (0, -420, 330, 9), 'port-tube': (0, 520, 0, 10),
        'amp-box-floor': (0, 140, 0, 11), 'amp-box-lid': (0, 140, 0, 11), 'amp-box-front': (0, 140, 0, 11),
        'woofer-ring': (0, -560, 0, 13), 'woofer-frame': (0, -470, 0, 12), 'woofer-cone': (0, -470, 0, 12), 'woofer-surround': (0, -470, 0, 12),
        'woofer-motor': (0, -470, 0, 12), 'mid-ring': (0, -560, 0, 13), 'mid-frame': (0, -470, 0, 14), 'mid-cone': (0, -470, 0, 14),
        'mid-surround': (0, -470, 0, 14), 'mid-motor': (0, -470, 0, 14),
        'tweeter-frame': (0, -330, 330, 15), 'tweeter-dome': (0, -330, 330, 15), 'tweeter-surround': (0, -330, 330, 15),
        'tweeter-retainer': (0, -230, 330, 17),
    }
    import components as C
    amp = C.amp_plate(AMP, RUN, PLAN, AMP['z'])
    # each balloon's dot on a face the view sees (the iso view looks from +x, -y, +z): a part's centre is often hidden
    # behind another (the left side behind the baffle), and a flange facing away from the eye cannot be seen
    sc_t = C.DRIVERS[DRIVER_SET['tweeter']]
    y0b, y1b, z0b, z1b = __import__('cad').amp_box_extent() if AMP else (0, 0, 0, 0)
    seen = {
        1: ('front-baffle', (RUN + 0.3 * PLAN, 0.0, 0.62 * BODY)),
        2: ('back-panel', (RUN + 0.25 * PLAN, PLAN - WALL / 2, BODY)),
        3: ('side-right', (PLAN, RUN, 0.55 * BODY)),
        4: ('top-panel', (RUN + 0.3 * PLAN, RUN, BODY)),
        5: ('bottom-panel', (RUN + 0.3 * PLAN, WALL, WALL / 2)),
        6: ('window-brace', (PLAN - WALL - 10, RUN, (BRACE_Z or 0) + WALL)),
        7: ('mid-shelf', (RUN + 0.3 * PLAN, (MID_CHAMBER_DEPTH or 0) / 2 + WALL, MID_SHELF_TOP or 0)),
        8: ('gable-pocket', (PLAN - 0.12 * PLAN, 0.5 * RUN, BODY + 0.5 * RISE)),
        9: ('insert-plain', (RUN + 0.15 * PLAN, 0.2 * RUN, BODY + 0.3 * RISE)),
        10: ('port-tube', (RUN + 0.35 * PORT['flange'], PLAN + PORT_FLANGE_T, PORT['z'] + 0.35 * PORT['flange']) if PORT else (0, 0, 0)),   # its flange, outside
        11: ('amp-box-front', (WALL + 0.15 * PLAN, y0b - WALL, (z0b + z1b) / 2)),     # its front face, left of the side's shadow
        12: ('woofer-frame', (RUN + 0.45 * C.DRIVERS[DRIVER_SET['woofer']]['frame_od'] / 2, 3.0, WOOFER['z'] + 0.45 * C.DRIVERS[DRIVER_SET['woofer']]['frame_od'] / 2)),
        13: ('woofer-ring', (RUN - 0.96 * (WOOFER_REBATE['d'] - 1.6) / 2, 0.0, WOOFER['z'] - 0.28 * (WOOFER_REBATE['d'] - 1.6) / 2)),   # its lower left
        14: ('mid-frame', (RUN + 0.45 * C.DRIVERS[DRIVER_SET['mid']]['frame_od'] / 2, 3.0, MID['z'] + 0.45 * C.DRIVERS[DRIVER_SET['mid']]['frame_od'] / 2) if MID else (0, 0, 0)),
        15: ('tweeter-frame', (RUN + 0.4 * TWEETER_PART['flange_d'], WAVEGUIDE['throat_y'], WAVEGUIDE['throat_z'])),
        17: ('tweeter-retainer', (RUN + 0.45 * (RETAINER['flange_d'] if RETAINER else 0), INSERT['boss_back_y'] + (RETAINER['flange_t'] if RETAINER else 0), WAVEGUIDE['throat_z'])),
    }
    shapes, anchors = [], {}
    for name, (dx, dy, dz, n) in mv.items():
        if name not in M: continue
        sh = Pos(dx * XS, dy * XS, dz * XS) * M[name]
        shapes.append(sh)
        if n in seen and seen[n][0] == name:
            x_, y_, z_ = seen[n][1]
            anchors[n] = (x_ + dx * XS, y_ + dy * XS, z_ + dz * XS)
    for name in ('amp-plate', 'amp-module'):
        sh = Pos(0, 600 * XS, 0) * amp[name]; shapes.append(sh)
    anchors[16] = (RUN + 0.3 * AMP['plate_w'], PLAN + 600 * XS, AMP['z'] + AMP['plate_h'] / 2)    # the plate's top edge
    t = time.time()
    vis, _ = hlr(shapes, 'iso')
    print(f'  sheet 5 iso: {len(vis)} edges, {time.time() - t:.0f}s', flush=True)
    # the view fitted into the sheet's left part, x 18 to 250, y 20 to 282, so the parts list beside it reads at 2.5 mm
    allp = np.concatenate(vis); (vx0, vy0), (vx1, vy1) = allp.min(axis=0), allp.max(axis=0)
    k = min(232.0 / (vx1 - vx0), 262.0 / (vy1 - vy0), k)
    o = (18.0 - k * vx0 + (232.0 - k * (vx1 - vx0)) / 2, 20.0 - k * vy0)
    S.lines(vis, o, k, lw=0.3)
    if BOOK:
        rows = [
            (1, 'Front baffle', '1', '18 mm Baltic birch, CNC: the woofer\'s cut-out, rebate'),
            (2, 'Back', '1', '18 mm birch: the amplifier\'s cut-out and rebate'),
            (3, 'Sides', '2', '18 mm birch; the Facts printed on the right one'),
            (4, 'Top panel', '1', '18 mm birch: the 14 mm cable hole, 4 dowel holes'),
            (5, 'Bottom panel', '1', '18 mm birch'),
            (8, 'Gable block', '1', 'laminated birch, CNC, or printed in four pieces'),
            (9, 'Waveguide insert', '1', 'SLA tough resin or MJF nylon; magnets, pins'),
            (11, 'Amplifier box', '3', 'birch floor, lid (2 glands) and front; sealed'),
            (12, 'Woofer', '1', 'SB Acoustics SB17NRX2C35-8, 6 in'),
            (13, 'Trim ring', '1', 'printed, satin black, over the frame and screws'),
            (15, 'Tweeter', '1', 'Scan-Speak Illuminator D3004/602200'),
            (16, 'Amplifier', '1', f'{AMP["model"]}, DSP, 2 channels'),
        ]
    else:
        rows = [
            (1, 'Front baffle', '1', '18 mm Baltic birch, CNC: cut-outs and rebates'),
            (2, 'Back', '1', '18 mm birch: port hole, amplifier cut-out, rebate'),
            (3, 'Sides', '2', '18 mm birch'),
            (4, 'Top panel', '1', '18 mm birch: the 14 mm cable hole, 4 dowel holes'),
            (5, 'Bottom panel', '1', '18 mm birch'),
            (6, 'Window brace', '1', '18 mm birch'),
            (7, 'Mid shelf and divider', '2', '18 mm birch; the divider\'s 12 mm cable hole'),
            (8, 'Gable block', '1', 'laminated birch, CNC, or printed in six pieces'),
            (9, 'Waveguide insert', '1', 'SLA tough resin or MJF nylon; magnets, pins'),
            (10, 'Port', '1', 'printed tube and flare collar, 92 bore'),
            (11, 'Amplifier box', '3', 'birch floor, lid (3 glands) and front; sealed'),
            (12, 'Woofer', '1', 'Dayton Audio RSS315HF-4, 12 in, 4 ohm'),
            (13, 'Trim rings', '2', 'printed, satin black, over each frame, screws'),
            (14, 'Midrange', '1', 'SB Acoustics Satori MR16P-8, 6.5 in'),
            (15, 'Tweeter', '1', 'SB Acoustics Satori TW29DN-B, faceplate off'),
            (16, 'Amplifier', '1', f'{AMP["model"]}, DSP, 3 channels'),
            (17, 'Tweeter retainer', '1', f'printed sleeve over the motor, {RETAINER["screws"]} screws'),
        ]
    # the bookshelf's parts numbered 1 to 12 without gaps (d24, round 3), the balloons with them
    renum = {old: i + 1 for i, (old, *_r) in enumerate(rows)}
    X, Y, rh_ = 262, 272, 9.6
    S.text(X, Y + 6, 'Parts', size=12, fontweight='bold')
    for i, (n, part, q, what) in enumerate(rows):
        yy = Y - i * rh_
        S.ax.add_patch(Circle((X + 3.6, yy - 1.6), 3.4, fc='white', ec=INK, lw=0.3 * PT, zorder=6))
        S.text(X + 3.6, yy - 1.6, str(renum[n]), size=MIN_PT, ha='center', va='center')
        S.text(X + 9, yy + 0.6, f'{part}  x{q}', size=MIN_PT, fontweight='bold', va='top')
        S.text(X + 9, yy - 3.8, what, size=MIN_PT, va='top', color='#222')
    S.text(X, Y - len(rows) * rh_ - 2, f'Glue-up order: G1 to G{len(general_notes()[0][1])}, sheet 8', size=MIN_PT, va='top')
    for n, (x, y, z) in anchors.items():
        if n not in renum:
            continue
        p2 = to2d('iso', [(x, y, z)])[0]
        px, py = o[0] + k * p2[0], o[1] + k * p2[1]
        dx_, dy_ = {13: (-11, -8)}.get(n, (10, 8))     # the woofer's ring's to the lower left, clear of the woofer's
        S.balloon(px + dx_, py + dy_, renum[n], px, py)
    S.save(pdf)


# --- sheet 6: panel details --------------------------------------------------------------------------------------------------
def sheet6(pdf, M, W):
    """The panels the other sheets do not detail, each drawn from its lower-left corner as its DXF is (fab/flats.py), with
    every hole and pocket dimensioned from that corner: for a builder with a table saw and a drill rather than a CNC."""
    import flats as F
    S = Sheet(6, 'Panel details', f'At {"1:3" if BOOK else "1:5"}: each panel seen from its outer (upper) face, from its lower-left corner as its DXF; holes from that corner. 18 mm birch.')
    want = ['top-panel', 'bottom-panel', 'window-brace', 'mid-divider', 'mid-shelf', 'amp-box-floor', 'amp-box-lid', 'amp-box-front']
    P = sorted([p for p in F.panel_defs() if p['name'] in want], key=lambda p: want.index(p['name']))
    k = 1 / 3 if BOOK else 0.2
    import textwrap
    cols, x0, pitch, lh = 4, 24.0, (A3[0] - 24.0 - 12.0) / 4, 4.3      # four to a row; line height at MIN_PT (2.5 mm)
    wrap = lambda t: textwrap.wrap(t, 47)
    y, row_h = 272.0, 0.0
    for i, p in enumerate(P):
        if i and i % cols == 0:
            y -= row_h + 14; row_h = 0.0
        x = x0 + (i % cols) * pitch
        w, h = p['w'] * k, p['h'] * k
        y0 = y - h
        S.ax.add_patch(Rectangle((x, y0), w, h, fill=False, lw=LW['outline'] * PT, ec=INK, zorder=3))
        S.text(x, y + 2.5, f'{p["name"]}  x{p["qty"]}', size=6.5, fontweight='bold')
        S.dim((0, 0), (p['w'], 0), -5, f'{p["w"]:g}', origin=(x, y0), scale=k, size=MIN_PT)
        S.dim((0, 0), (0, p['h']), 5, f'{p["h"]:g}', origin=(x, y0), scale=k, size=MIN_PT)
        lines, holes = [], {}          # holes of one size and operation on one line, with all their positions (the lid's
        for layer, items in p['layers'].items():     # three glands ran a line each into the title block)
            for it in items:
                if it[0] == 'circle':
                    (cx, cy), r = it[1], it[2]
                    S.ax.add_patch(Circle((x + k * cx, y0 + k * cy), k * r, fill=False, lw=LW['outline'] * PT, ec=INK, zorder=4))
                    S.ax.plot([x + k * cx - 1.2, x + k * cx + 1.2], [y0 + k * cy, y0 + k * cy], color=RED, lw=0.15 * PT, zorder=4)
                    S.ax.plot([x + k * cx, x + k * cx], [y0 + k * cy - 1.2, y0 + k * cy + 1.2], color=RED, lw=0.15 * PT, zorder=4)
                    holes.setdefault((round(2 * r, 1), F.OPS.get(layer, layer)), []).append(f'({round(cx, 1):g}, {round(cy, 1):g})')
                elif it[0] == 'poly':
                    pts = np.array([(px, py) for (px, py) in it[1]])
                    S.ax.add_patch(MPoly(np.c_[x + k * pts[:, 0], y0 + k * pts[:, 1]], closed=it[2], fill=False, lw=LW['thin'] * PT, ec=INK, zorder=4))
                    rad = f', R{BRACE_WINDOW_R:g} corners' if (p['name'] == 'window-brace' and BRACE_WINDOW_R) else ''    # d18, round 3
                    lines.append(f'{F.OPS.get(layer, layer)}: {round(pts[:, 0].min(), 1):g} to {round(pts[:, 0].max(), 1):g} across, {round(pts[:, 1].min(), 1):g} to {round(pts[:, 1].max(), 1):g} up{rad}')
                elif it[0] == 'text':
                    (tx, ty), txt, hgt = it[1], it[2], it[3]
                    S.text(x + k * tx, y0 + k * ty, txt, size=MIN_PT, ha='center', va='center', color='#555')
        lines = [f'{len(at)} x ' * (len(at) > 1) + f'ø{d:g} at {", ".join(at)}: {op}' for (d, op), at in holes.items()] + lines
        body = [ln for t in lines for ln in wrap(t)]; note = wrap(p['note'])
        for j, ln in enumerate(body):
            S.text(x, y0 - 10 - j * lh, ln, size=MIN_PT, va='top', color='#222')
        for j, ln in enumerate(note):
            S.text(x, y0 - 10.5 - (len(body) + j) * lh, ln, size=MIN_PT, va='top', color='#555')
        row_h = max(row_h, h + 12 + (len(body) + len(note)) * lh)
    trim_ring_sections(S, 26.0, 24.0)
    S.save(pdf)


def trim_ring_sections(S, x0, y0):
    """The trim rings' sections at 2:1, as fab/cad.py prints them (components.trim_ring): flat, flush, the channel in the
    back over the screws' heads, opened to the bore where the heads reach it (the drawing check's d9, round 3)."""
    import components as C
    k = 2.0
    S.text(x0, y0 + 38, 'Trim rings, section at 2:1 (stl/trim-ring-*.stl): flat, flush with the finish', size=MIN_PT, fontweight='bold', va='bottom')
    x = x0
    for role, rb in [('woofer', WOOFER_REBATE)] + ([('mid', MID_REBATE)] if MID else []):
        r_out = (rb['d'] - 1.6) / 2; r_in = TRIM_RING_ID[role] / 2; sc = DRIVER_SCREWS.get(role)
        ch = C.ring_channel(r_in, r_out, sc['pcd'] / 2, DRIVER_SCREW['head_d']) if sc else None
        t, e, ir = C.RING['t'], C.RING['ease'], C.RING.get('inner_r', 2.5)
        # the profile as trim_ring draws it, r across and the thickness down (the face at the top)
        pts = [(r_out, t), (r_out, e)] + [(r_out - e + e * math.cos(th), e - e * math.sin(th)) for th in [math.pi / 2 * i / 6 for i in range(7)]][1:]
        pts += [(r_in + ir, 0.0)] + [(r_in + ir - ir * math.sin(th), ir - ir * math.cos(th)) for th in [math.pi / 2 * i / 6 for i in range(7)]][1:]
        if ch and ch[0] <= r_in + 1e-6:
            pts += [(r_in, t - ch[2]), (ch[1], t - ch[2]), (ch[1], t)]
        else:
            pts += [(r_in, t)] + ([(ch[0], t), (ch[0], t - ch[2]), (ch[1], t - ch[2]), (ch[1], t)] if ch else [])
        P = np.array(pts); ox, oy = x - k * (r_in - 2), y0 + 20
        S.ax.add_patch(MPoly(np.c_[ox + k * P[:, 0], oy - k * P[:, 1]], closed=True, fc=CUT, ec=INK, lw=LW['outline'] * PT, hatch='////', zorder=3))
        S.ax.plot([ox + k * (r_in - 2), ox + k * (r_out + 2)], [oy, oy], color=LIGHT, lw=LW['thin'] * PT, ls='--', zorder=2)
        S.text(ox + k * r_in, oy + 3, f'{role}: ø{2 * r_out:g} / ø{2 * r_in:g} x {t:g}', size=MIN_PT, ha='left', va='bottom')
        if ch:
            what = 'open to the bore' if ch[0] <= r_in + 1e-6 else f'from ø{2 * ch[0]:.1f}'
            S.text(ox + k * r_in, oy - k * t - 2, f'channel {what} to ø{2 * ch[1]:.1f}, {ch[2]:g} deep', size=MIN_PT, ha='left', va='top')
        x += k * (r_out - r_in + 4) + 70
    S.text(x0, y0 - 4, f'the channel clears the {DRIVER_SCREW["thread"]} heads (F1): {DRIVER_SCREW["head_d"]:g} across, {DRIVER_SCREW["head_h"]:g} high or less',
           size=MIN_PT, va='top')


# --- sheet 7: the notes ---------------------------------------------------------------------------------------------------
def measure_first():
    """What to measure on the bought parts and the ply before cutting or printing, the value the drawings assume, and
    what it drives: one table in place of notes scattered over four sheets (round 3's sixth question)."""
    rows = [f'Ply: {WALL:g} thick; the sides and inner panels are {PLAN:g} - 2 x {WALL:g} = {INNER:g} wide. For a real thickness t: '
            f'{PLAN:g} - 2t (heights, pockets and rebates unchanged); set WALL = t in params.py and run fab/build.sh again.']
    T = TWEETER_PART
    for role, rb, cut, name in [('woofer', WOOFER_REBATE, WOOFER_CUTOUT, 'woofer')] + ([('mid', MID_REBATE, MID_CUTOUT, 'mid')] if MID else []):
        sc = DRIVER_SCREWS.get(role); fl = rb['depth'] - 1.0 - TRIM_RING['t']
        drv = C_DRIVER_NAME.get(DRIVER_SET[role], DRIVER_SET[role])
        alt = ' (one source gives 10.9: over 6.5, the rebate would leave under 7.5 for the T-nut barrels, the owner\'s call: a proud ring or a thicker baffle)' if (BOOK and role == 'woofer') else ''
        rows.append(f'{drv}: flange {fl:g} thick{alt} sets the rebate, {rb["depth"]:g} deep; the frame\'s diameter + 1.6 sets the rebate\'s ø{rb["d"]:g}; '
                    f'the cut-out ø{cut:g}' + (f'; {sc["n"]} holes on ø{sc["pcd"]:g}' if sc else '') + f'; the surround at its glue line + 2 sets the trim ring\'s bore, ø{TRIM_RING_ID[role]:g}.')
    if RETAINER:
        rows.append(f'{T["model"]}: the front ring ø{T["flange_d"]:g} sets the bore, ø{T["flange_d"] + 0.4:g}; the motor ø{T["body_d"]:g} sets the sleeve\'s bore, '
                    f'ø{T["body_d"] + 2 * RETAINER["clear"]:g}; the dome and surround, {2 * WAVEGUIDE["r0"]:g} across, set the throat. Print nothing until it is measured.')
    else:
        rows.append(f'{T["model"]}: the faceplate ø{T["flange_d"]:g} sets the bore, ø{T["flange_d"] + 0.4:g}; its hole circle, ø{T["bolt_circle"]:g}, and its body, '
                    f'ø{T["body_d"] + 0.3:g} or less, set the seat\'s screws; its front must be flat from ø{2 * WAVEGUIDE["r0"]:g} to ø{T["flange_d"]:g} and the grille '
                    f'off (or a seat recess for it); the dome and surround {2 * WAVEGUIDE["r0"]:g} across or less. Print nothing until it is measured.')
    rows.append(f'{AMP["model"]}: the plate {AMP["plate_w"]:g} x {AMP["plate_h"]:g} sets the rebate, {AMP["plate_w"] + 1:g} x {AMP["plate_h"] + 1:g}; '
                f'the module sets the cut-out, {AMP["cut_w"]:g} x {AMP["cut_h"]:g}; the screw holes come from the plate in hand.')
    return rows


C_DRIVER_NAME = {'rss315hf-4': 'Woofer (Dayton RSS315HF-4)', 'mr16p-8': 'Mid (SB Satori MR16P-8)', 'sb17nrx2c35-8': 'Woofer (SB17NRX2C35-8)'}


def general_notes():
    """The notes that belong to no one sheet: the glue-up, the fixings, the pocket's floor (round 3's d11, d15, d20)."""
    glue = (['Lay the back face down. Glue both sides and the bottom to it.', 'The amplifier box: its floor, front and lid between the sides, against the back; seal its joints.']
            + ([f'The window brace at z {BRACE_Z:g}, glued to the sides and the back.'] if BRACE_Z else [])
            + (['The mid chamber\'s shelf, then its divider.'] if MID else [])
            + ['Press the T-nuts into the front baffle\'s inside face, then glue the baffle on.', 'The top panel last, inside all four walls.',
               'Clamp across the sides at every inner panel. Then the gable block on its dowels.'])
    return [
        ('Glue-up, in order', glue),
        ('Fixings and the pocket\'s floor', [
            f'Drivers: {DRIVER_SCREW["thread"]} {DRIVER_SCREW["head"]}, the head {DRIVER_SCREW["head_h"]:g} high or less and {DRIVER_SCREW["head_d"]:g} across or less '
            '(ISO 7380 is 2.2 high: the trim ring\'s channel is 2 deep). M4 T-nuts, flange ' +
            ', '.join(f'{v:g} or less across ({k_})' for k_, v in DRIVER_SCREW['tnut_flange'].items()) + ', barrel ' +
            ', '.join(f'{v:g} or less ({k_})' for k_, v in DRIVER_SCREW['tnut_barrel'].items()) + ', pressed in before the glue-up.',
            'Before the gable block goes on, sand the front panel\'s top edge flush with the top panel to 0.1: the insert sits on both. '
            'Mask the pocket\'s floor with the insert\'s sides, base and back when you spray: paint only the insert\'s face.',
        ]),
    ]


def notes_sheet(pdf, number, title, subtitle, blocks):
    """A sheet of notes in three columns at 2.5 mm: blocks are ('h', heading) or ('p', label, text). Laid out first
    and placed once it fits: the leading tightens a step at a time (4.3 to 3.95 mm a line at 10 pt) before giving up."""
    import textwrap
    S = Sheet(number, title, subtitle)
    # x, top, bottom: the title block (x 220 to 410) lies under the second column's right half and all the third's
    cols = [(16.0, 278.0, 14.0), (151.0, 278.0, 56.0), (286.0, 278.0, 56.0)]
    ind = 9.0                                    # the text hangs this far right of its label (M1, 3.10, G7)
    ww = int((125.0 - ind) / 1.95)

    def layout(lh, gap, hgap):
        """Each block's column and top, or None when they do not fit."""
        out, c = [], 0
        x, y, ybot = cols[0]
        for i, bl in enumerate(blocks):
            if bl[0] == 'h':
                lines = None; need = hgap + 2 * lh             # a heading keeps its first note with it
            else:
                lines = textwrap.wrap(bl[2], ww); need = len(lines) * lh
            if y - need < ybot:
                c += 1
                if c >= len(cols):
                    return None, i
                x, y, ybot = cols[c]
            out.append((bl, lines, x, y))
            y -= (hgap if bl[0] == 'h' else len(lines) * lh + gap)
        return out, len(blocks)

    for lh, gap, hgap in ((4.3, 1.2, 6.0), (4.1, 1.0, 5.6), (3.95, 0.8, 5.4)):
        placed, n_ = layout(lh, gap, hgap)
        if placed:
            break
    if not placed:
        raise RuntimeError(f'sheet {number}: the notes do not fit: {n_} of {len(blocks)} blocks placed at the tightest leading')
    print(f'  sheet {number}: {len(blocks)} blocks at {lh} mm a line', flush=True)
    for (bl, lines, x, y) in placed:
        if bl[0] == 'h':
            S.ax.text(x, y, bl[1], fontsize=12, fontweight='bold', va='top', zorder=6)
            continue
        label = bl[1]
        for j, ln in enumerate(lines):
            if j == 0:
                S.ax.text(x, y, label, fontsize=MIN_PT, fontweight='bold', va='top', zorder=6)
            S.ax.text(x + ind, y - j * lh, ln, fontsize=MIN_PT, va='top', zorder=6)
    S.save(pdf)


def _sheet_blocks(numbers):
    """The notes the drawings registered (Sheet.notes), for these sheets, as blocks numbered n.1, n.2, ..."""
    blocks = []
    for n in sorted(k_ for k_ in NOTES if k_ in numbers):
        k_ = 0
        for (title, items) in NOTES[n]:
            blocks.append(('h', f'Sheet {n}: {title}'))
            for it in items:
                k_ += 1
                blocks.append(('p', f'{n}.{k_}', it))
    return blocks


def sheet7(pdf, M, W):
    """Notes 1: what to measure before cutting or printing (M1, M2, ...), then sheets 1 to 3's notes."""
    blocks = [('h', 'Measure first')] + [('p', f'M{i + 1}', t) for i, t in enumerate(measure_first())]
    blocks += _sheet_blocks([n for n, on in NOTES_ON.items() if on == 7])
    notes_sheet(pdf, 7, 'Notes: measure first; sheets 1 to 3', 'What to measure before cutting or printing, and the notes sheets 1 to 3 point to by number.', blocks)


def sheet8(pdf, M, W):
    """Notes 2: sheets 4 to 6's notes, then the glue-up order (G1, ...) and the fixings (F1, ...)."""
    blocks = _sheet_blocks([n for n, on in NOTES_ON.items() if on == 8])
    for title, items in general_notes():
        blocks.append(('h', title))
        blocks += [('p', f'{"G" if title.startswith("Glue") else "F"}{i + 1}', it) for i, it in enumerate(items)]
    notes_sheet(pdf, 8, 'Notes: sheets 4 to 6; glue-up and fixings', 'The notes sheets 4 to 6 point to by number; the order of the glue-up; the fixings.', blocks)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--only', nargs='*', type=int)
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    t = time.time(); M = drawing_model(); W = waveguide_curves(); print(f'model {time.time() - t:.0f}s', flush=True)
    with PdfPages(os.path.join(OUT, 'earmilk-sheets.pdf')) as pdf:
        for n, fn in ((1, sheet1), (2, sheet2), (3, sheet3), (4, sheet4), (5, sheet5), (6, sheet6), (7, sheet7), (8, sheet8)):
            if a.only and n not in a.only: continue
            fn(pdf, M, W)
    print('wrote', OUT)


if __name__ == '__main__':
    main()
