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
  7  Notes: what to measure first and what may be cut now; sheet 1's notes by number (1.4 is sheet 1's fourth)
  8  Notes: sheets 2 and 4 to 6's notes; the glue-up order and the fixings
  9  Notes: sheet 3's, fitting the tweeter and the insert

Every text on every sheet is 2.5 mm high or more (MIN_PT), view titles 3.5 mm, the sheet's title 5 mm (ISO 3098 at
A3); the long notes live on sheets 7 to 9 so the drawings keep their room (the drawing check's d22, round 3: at
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
OUTNAME = 'out-bookshelf' if BOOK else 'out'                          # this size's folder, for the notes' file paths
PRODUCT = 'earmilk bookshelf' if BOOK else 'earmilk floorstander'
# drawing scales per size: the bookshelf is drawn larger so its views fill the same sheets
K = dict(ga=1 / 3, sec=1 / 3, roof=1.0, ins=1.0, back=1 / 3, exp=0.28) if BOOK else dict(ga=0.2, sec=0.2, roof=0.5, ins=0.5, back=0.2, exp=0.16)
SC = {k: f'1:{round(1 / v):d}' for k, v in K.items()}
XS = PLAN / 390.0     # model offsets that were set for the floorstander scale with the plan
A3 = (420.0, 297.0)
INK = '#111111'; LIGHT = '#777777'; RED = '#B3261E'; CUT = '#d9d4c7'
LW = dict(outline=0.5, thin=0.25, dim=0.18, hidden=0.25, centre=0.18)   # line weights, mm on paper
PT = 72 / 25.4                                                          # points per mm
SHEETS = 9                                                             # sheets in each size's set: six drawings and three of notes (a third when 7 filled: round 7)
NOTES_ON = {1: 7, 2: 8, 3: 9, 4: 8, 5: 8, 6: 8}                        # which notes sheet holds each drawing's notes (2's moved to 8, 3's to 9, as 7 filled)
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
def sheet_status(n):
    """The release status a sheet's title block prints: HOLD until the bought parts it fits are measured (sheet 7)."""
    m_ = lambda *ks: ', '.join(f'M{M_NUM[k]}' for k in ks if k in M_NUM)
    return {1: f'HOLD until {m_("woofer", "mid")} (the drivers)', 3: f'HOLD until {m_("tweeter", "connector")} (tweeter, connector)',
            4: f'HOLD until {m_("amp")} (the amplifier)', 6: f'cut after M1; the trim rings HOLD until {m_("woofer", "mid")}'}.get(
            n, 'for reference' if n in (2, 5) else 'notes')


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
        st = sheet_status(self.number)      # what may be cut or printed from this sheet yet (the drawing check's d4, round 7)
        ax.text(x0 + 3, y0 + 11.2, f'mm  |  issue 2026-10-09  |  {st}', fontsize=MIN_PT, va='center',
                fontweight='bold' if st.startswith('HOLD') else 'normal', color=RED if st.startswith('HOLD') else INK)
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

    def dim_in(self, ax, k, p0, p1, off, text, size=5.5, feet=None):
        """A dimension drawn in an inset's axes (model coordinates, `k` paper mm per model mm), above its section fills.
        `feet`: the two features it measures between (model points), when the line stands away from them: an extension
        line runs from each to the dimension line and 1.5 mm past it (the drawing check's d16, round 5)."""
        a, b = np.array(p0, float), np.array(p1, float)
        d = b - a; L = np.linalg.norm(d)
        if L < 1e-6: return
        u = d / L; n = np.array([-u[1], u[0]]); o = off / k
        a2, b2 = a + n * o, b + n * o
        for f_, e_ in zip(feet or (), (a2, b2)):
            f_ = np.array(f_, float); v_ = e_ - f_; lv = np.linalg.norm(v_)
            if lv > 1e-6:
                q_ = e_ + v_ / lv * 1.5 / k
                ax.plot([f_[0] + v_[0] / lv * 0.8 / k, q_[0]], [f_[1] + v_[1] / lv * 0.8 / k, q_[1]], color=INK, lw=LW['dim'] * PT, zorder=10, clip_on=False)
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

    def wrap(self, text, width_mm, size=MIN_PT):
        """Word-wrap text to a width in sheet mm, measured at the size it prints at (save() raises anything smaller to
        MIN_PT); returns the text and its height in mm, without a bbox's pad."""
        r_, inv = self.fig.canvas.get_renderer(), self.ax.transData.inverted()
        probe = self.ax.text(0, 0, '', fontsize=size)
        ext = lambda s: (probe.set_text(s), probe.get_window_extent(r_).transformed(inv))[1]
        lines = []
        for para in text.split('\n'):
            cur = ''
            for word in para.split(' '):
                trial = (cur + ' ' + word).strip()
                if cur and ext(trial).width > width_mm:
                    lines.append(cur); cur = word
                else:
                    cur = trial
            lines.append(cur)
        out = '\n'.join(lines); h = ext(out).height
        probe.remove()
        return out, h

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
    drv = [(WOOFER['z'], DRIVER_SET['woofer'], WOOFER_REBATE['d'] - 1.6, 'woofer')] + ([(MID['z'], DRIVER_SET['mid'], MID_REBATE['d'] - 1.6, 'mid')] if MID else [])
    for z, key, ring, role in drv:
        sp = C.DRIVERS[key]; _, info = C.cone_driver(sp, 4)
        # the ring's inner edge from its bore, as printed (TRIM_RING's 20 mm width drew it inside the surround: d17, round 4)
        out += [(RUN, z, ring, 'outline'), (RUN, z, TRIM_RING_ID[role], 'thin'), (RUN, z, 2 * info['r_surround'], 'thin'),
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
    o_ = OUTNAME                                         # this size's own files (the bookshelf's pointed at the floorstander's: d3, round 4)
    return (f'The cast letters ({o_}/metal/wordmark-letters.*), {BADGE["relief"]:g} thick and proud: {size}centred across the plinth\'s front, the badge\'s centre z '
            f'{BADGE["z"]:g}; on the back the same at z {BACK_BADGE["z"]:g}. Place and drill them from the 1:1 templates, '
            f'{o_}/metal/wordmark-template-front.pdf and -back.pdf, after the clear coat.')


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
        # wrapped to the front's width at the size it prints (its white ground inside the outline), then set in the
        # larger clear face, clear of the circles: at 1:5 a four-line note overran the 17 mm over the mid, and at 1:3
        # the bookshelf's covered its rebate's foot
        pad_ = 0.4 * MIN_PT / PT
        # the screw holes' pattern is in the Driver holes block at the right: two notes of four lines met between the
        # mid and the woofer at 1:5
        note_, h_ = S.wrap(f'rebate ø{rb["d"]:g} x {rb["depth"]:g} deep,\nthrough ø{cut:g}' + ('; holes: Driver holes' if sc else ''),
                           k * PLAN - 2 * pad_ - 3.0)
        h_ += 2 * pad_
        need = h_ + 2.0
        sg = 1 if up * k >= need else (-1 if down * k >= need else (1 if up >= down else -1))   # above when there is room
        off_ = min(1.5 + h_ / 2, (up if sg > 0 else down) * k / 2)           # 1.5 off the circle, or centred in a tight gap
        tx, ty_ = o[0] + k * RUN, o[1] + k * (z + sg * rb['d'] / 2) + sg * off_
        S.ax.annotate(note_,
                      xy=(o[0] + k * (RUN + rb['d'] / 2 * 0.5), o[1] + k * (z + sg * rb['d'] / 2 * 0.866)), xytext=(tx, ty_), fontsize=MIN_PT, ha='center', va='center',
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
    S.ax.annotate('waveguide insert\n(sheet 3)', xy=(o[0] + k * (RUN + 60 * XS), o[1] + k * (WAVEGUIDE['throat_z'] + 30 * XS)),
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
    # the drivers' holes, each pattern in full: where the front view has no room for them (above)
    yb_ = 150.0
    S.text(300, yb_, 'Driver holes (front baffle, from its front face)', size=MIN_PT, fontweight='bold', va='top')
    for role, z, rb, cut, m_ in [('woofer', WOOFER['z'], WOOFER_REBATE, WOOFER_CUTOUT, 'M2')] + ([('mid', MID['z'], MID_REBATE, MID_CUTOUT, 'M3')] if MID else []):
        sc = DRIVER_SCREWS.get(role)
        yb_ -= 6.0 if role == 'woofer' else 3.0
        S.text(300, yb_, f'{role.capitalize()}, centre z {z:g} on the centreline ({m_})', size=MIN_PT, fontweight='bold', va='top')
        body_, hb_ = S.wrap(f'rebate ø{rb["d"]:g} x {rb["depth"]:g} deep; through ø{cut:g}' +
                            (f'; {sc["n"]} x ø{sc["hole"]:g} on ø{sc["pcd"]:g}, the first {sc["start_deg"]:g}° above the horizontal, '
                             f'{360.0 / sc["n"]:g}° apart, for M4 T-nuts (1.2).' if sc else '.'), 104.0)
        yb_ -= 4.6
        S.text(300, yb_, body_, size=MIN_PT, va='top', color='#222')
        yb_ -= hb_
    S.notes(300, 160, 'Notes', [
        f'Cabinet: 18 mm Baltic birch, glued. The vertical corners and the gable\'s hips are rounded {EDGE_R:.0f} mm, the fin\'s edges {FIN_EDGE_R:.0f} mm. 3 x 3 mm shadow lines at z {PLINTH_H:.0f} and z {GABLE_SHADOW_Z0:.0f}.',
        (f'The drivers sit flush: each rebate is the measured flange + 1.0 (a 1.5 mm closed-cell foam gasket, pressed) + {TRIM_RING["t"]:.0f} (the ring): '
         + ', '.join(f'{r} {rb["depth"]:g} for a {rb["depth"] - 1.0 - TRIM_RING["t"]:g} flange' for (r, rb) in [('woofer', WOOFER_REBATE)] + ([('mid', MID_REBATE)] if MID else []))
         + '; measure each flange before cutting (M2' + (', M3' if MID else '') + '): the rebate is the flange + 4.0 only while the T-nut\'s barrel + 0.5 of birch stays under it: '
         + ', '.join(f'{WALL - rb["depth"]:g} under the {r}\'s (barrel {DRIVER_SCREW["tnut_barrel"][r]:g} or less)' for (r, rb) in [('woofer', WOOFER_REBATE)] + ([('mid', MID_REBATE)] if MID else []))
         + '. '
         + 'The screws and T-nuts as F1, pressed in before the glue-up. '
         + 'A printed trim ring over each flange (stl/trim-ring-*.stl, ' + ', '.join(f'{r} ø{(rb["d"] - 1.6):g} / ø{TRIM_RING_ID[r]:g} x {TRIM_RING["t"]:g}' for (r, rb) in [('woofer', WOOFER_REBATE)] + ([('mid', MID_REBATE)] if MID else []))
         + ', flat, a channel in its back over the screws\' heads: the sections at 2:1 on sheet 6) held by three 5 mm dots of neutral-cure silicone, 0.8 reveal all round. Its inner ø is the surround at its glue line + 2: measure the drivers and print the rings last '
         + f'(the woofer\'s ring, ø{WOOFER_REBATE["d"] - 1.6:g}, needs a bed of {math.ceil((WOOFER_REBATE["d"] - 1.6 + 6) / 10) * 10:g} or more' + (', or a print service).' if WOOFER_REBATE['d'] > 250 else ').')),
        f'The tweeter is at the throat of a waveguide insert in the roof (sheet 3): axis z {WAVEGUIDE["throat_z"]:g}, {WAVEGUIDE["throat_y"]:g} behind the front face. The shape is set by simulation (fab/{OUTNAME}/acoustics/waveguide).',
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
    'front-baffle': WOOD, 'back-panel': WOOD, 'side-left': WOOD, 'side-right': WOOD, 'top-panel': WOOD, 'bottom-panel': WOOD, 'window-brace': WOOD,
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


def runs_3d():
    """The floorstander's runs in the model (x, y, z), and the cable-tie mounts that hold them (the drawing check's d9 and
    d17, round 6). The glands, from the right: the tweeter's (x 332), the mid's (297), the woofer's (262). The tweeter's
    and the mid's rise from their glands, bend left inside the brace's window (its frame is solid from x 322) and pass
    it together 30 in from its back edge, tied to a mount on the brace's top face; the mid's then runs along the right
    side's inner face and the divider's back face to the divider's hole (x 75, z 630); the tweeter's up to the top panel
    and along its underside to the channel. The woofer's goes forward to the woofer. Returns (runs, mounts), mounts as
    [(surface, (x, y, z))] at the face each sticks to."""
    import cad
    gl = cad.amp_glands_xy()
    (tx, gy), (mx, _), (wx, _) = gl[0], gl[1], gl[2]
    z1 = cad.amp_box_extent()[3]; zl = z1 + WALL                     # the lid's top
    wy1 = WALL + INNER / 2 + BRACE_WINDOW / 2; wx1 = wy1              # the window's back and right edges, 322
    yb = wy1 - 30.0                                                   # 30 in from its back edge, 292
    xb = wx1 - 6.0                                                    # the two runs just inside its right edge, 316
    zr = MID_SHELF_TOP + 50.0                                         # the mid's run above the brace, 10 over its hole
    xh, zh = RUN - 120.0, MID_SHELF_TOP + 40.0                        # the divider's hole, (75, 630)
    yd = WALL + MID_CHAMBER_DEPTH + WALL                              # the divider's back face, 126
    xs = PLAN - WALL                                                  # the right side's inner face, 372
    yw = cad.wire_hole_y()
    zt = TOP_Z0 - 8.0                                                 # under the top panel, on its mounts
    # none under the top panel: its mounts would have to slide over the divider's top, 0.3 below it, and their ties be
    # closed blind 470 mm in (the drawing check's d1, round 7); the tweeter's run hangs from its channel's silicone seal
    mounts = [('the brace\'s top face', (wx1 + 12.0, yb, BRACE_Z + WALL)),
              ('the right side', (xs, yb - 2.0, zr)), ('the right side', (xs, yd + 14.0, zr)),
              ('the divider\'s back face', (xs - 72.0, yd, zr)), ('the divider\'s back face', (xh + 75.0, yd, zr))]
    up = BRACE_Z - 20.0
    tweeter = [(tx, gy, zl), (tx, gy, up), (xb, yb, BRACE_Z), (xb, yb, BRACE_Z + WALL + 8.0), (RUN, yw, TOP_Z0)]
    mid = [(mx, gy, zl), (mx, gy, up), (xb, yb, BRACE_Z), (xb, yb, zr), (xs - 8.0, yb - 2.0, zr), (xs - 8.0, yd + 14.0, zr), (xs - 72.0, yd + 8.0, zr),
           (xh + 75.0, yd + 8.0, zr), (xh, yd + 8.0, zr), (xh, yd + 8.0, zh), (xh, WALL + MID_CHAMBER_DEPTH - 10.0, zh), (RUN - 60.0, WALL + 70.0, MID['z'] - 20.0)]
    woofer = [(wx, gy, zl), (wx, gy, WOOFER['z']), (RUN + 40.0, WALL + 125.0, WOOFER['z'])]
    return dict(tweeter=np.array(tweeter), mid=np.array(mid), woofer=np.array(woofer)), mounts


def wire_paths():
    """The cables' runs in the centre section's frame (2D 'left': x = -y, y = z): every one leaves the amplifier's box
    through the gland in its lid; the floorstander's are its runs_3d() projected onto the centre plane; the bookshelf's
    tweeter's goes up on the gland's line, its woofer's forward to the woofer."""
    import cad
    zt = WAVEGUIDE['throat_z']; yw = cad.wire_hole_y()
    if MID:
        runs, _ = runs_3d()
        inside = (-(PLAN - WALL - 30 * XS), AMP['z']); z1 = cad.amp_box_extent()[3]
        head = [(-(WAVEGUIDE['throat_y'] + TWEETER_PART['flange_t'] + TWEETER_PART['body_depth']), zt), (-yw, zt)]
        out = {}
        for nm, r in runs.items():
            pr = [(-y, z) for (x, y, z) in r]
            pr = pr[::-1] + [(pr[0][0], z1), inside]                  # from the driver to the module, like the bookshelf's
            out[nm] = np.array((head if nm == 'tweeter' else []) + pr)
        return out
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


def plan_section(M, z, names):
    """Cut faces on the plane z (the part below kept, seen from above), per part, as 2D loops (x, y)."""
    from build123d import Plane, Keep, Compound
    out = {}
    for n in names:
        if n not in M:
            continue
        try:
            h = M[n].split(Plane.XY.offset(z), keep=Keep.BOTTOM)
            if isinstance(h, (list, tuple)):
                h = Compound(children=list(h)) if h else None
        except Exception:
            h = None
        if h is None or h.volume < 1e-3:
            continue
        loops = []
        for f in h.faces():
            c = f.center(); nrm = f.normal_at(c)
            if abs(c.Z - z) < 0.05 and abs(abs(nrm.Z) - 1) < 1e-3:
                for w in [f.outer_wire()] + list(f.inner_wires()):
                    pts = []
                    for e in w.edges():
                        m = 2 if e.geom_type.name == 'LINE' else int(min(200, max(6, e.length / 1.0)))
                        pts += [(p_.X, p_.Y) for p_ in (e.position_at(t) for t in np.linspace(0, 1, m))]
                    loops.append((np.array(pts), w is f.outer_wire()))
        if loops:
            out[n] = loops
    return out


def draw_plan(S, loops, org, k):
    from matplotlib.path import Path as MPath
    from matplotlib.patches import PathPatch
    for name, ls in loops.items():
        fs = SECTION_PARTS.get(name, WOOD)
        verts, codes = [], []
        for (p_, outer) in ls:
            q = np.c_[org[0] + k * p_[:, 0], org[1] + k * p_[:, 1]]
            verts += list(q) + [q[0]]; codes += [MPath.MOVETO] + [MPath.LINETO] * (len(q) - 1) + [MPath.CLOSEPOLY]
        S.ax.add_patch(PathPatch(MPath(verts, codes), fc=fs['color'], ec=INK, lw=LW['thin'] * PT, hatch=fs['hatch'], zorder=2))


def plan_sections(S, M, org_a, k_a):
    """The floorstander's runs in plan (the drawing check's d17, round 6): section D-D at the port's axis, where the
    tweeter's and the mid's runs rise beside the port, and E-E at the mid's run over the brace, with the cable-tie
    mounts; their cutting planes drawn on section A-A."""
    runs, mounts = runs_3d()
    zD, zE = PORT['z'], runs['mid'][3][2]
    for z_, L_ in ((zD, 'D'), (zE, 'E')):
        S.cutting_plane((-(PLAN + 10), z_), (14, z_), L_, (0, -1), org_a, k_a)
    names = ['front-baffle', 'back-panel', 'side-left', 'side-right', 'mid-divider', 'port-tube', 'woofer-frame', 'woofer-motor',
             'woofer-cone', 'woofer-surround', 'woofer-cap', 'woofer-ring', 'mid-frame', 'mid-motor', 'mid-cone', 'mid-surround', 'mid-cap', 'mid-ring']
    k = 0.1; ov = 3.0                     # 1:10
    org_d, org_e = (184.0, 60.0), (294.0, 60.0)
    col = {'tweeter': RED, 'mid': RED, 'woofer': RED}
    dia = {'tweeter': 6.4, 'mid': 8.0, 'woofer': 9.0}
    lead = lambda xy, txt, dx, dy: S.ax.annotate(txt, xy=xy, xytext=(xy[0] + dx, xy[1] + dy), fontsize=5, ha='left', va='center', zorder=8,
                                                  arrowprops=dict(arrowstyle='-', lw=LW['dim'] * PT, color=INK, shrinkA=0, shrinkB=0))
    P = lambda org, x, y: (org[0] + k * x, org[1] + k * y)
    for org, z_, L_ in ((org_d, zD, 'D'), (org_e, zE, 'E')):
        draw_plan(S, plan_section(M, z_, names), org, k)
        S.label(org[0] + k * PLAN / 2, org[1] + k * PLAN + 3.0, f'SECTION {L_}-{L_}, 1:10')
        S.text(org[0] + k * PLAN / 2, org[1] - 4.5, f'front (z {z_:g})', size=5, ha='center', va='center')
        # each run where it crosses the plane: a dot; along it: a line
        for nm, r in runs.items():
            for a, b in zip(r[:-1], r[1:]):
                if (a[2] - z_) * (b[2] - z_) < 0 or (abs(a[2] - z_) < 1e-6 and abs(b[2] - z_) > 1e-6):
                    t = (z_ - a[2]) / (b[2] - a[2]); x_, y_ = a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])
                    S.ax.add_patch(Circle(P(org, x_, y_), k * dia[nm] / 2 + 0.25, fc=col[nm], ec='none', zorder=6))
            seg = [p_ for p_ in r if abs(p_[2] - z_) < 1e-6]
            if len(seg) > 1:
                q = np.array([P(org, x_, y_) for (x_, y_, _) in seg])
                S.ax.plot(q[:, 0], q[:, 1], color=RED, lw=0.35 * PT, ls=(0, (3, 1.5)), zorder=6)
        for (surf, (x_, y_, zz)) in mounts:
            if abs(zz - z_) < 1e-6:
                q = P(org, x_, y_)
                S.ax.add_patch(Rectangle((q[0] - 1.0, q[1] - 1.0), 2.0, 2.0, fc=INK, ec='none', zorder=7))
    # D-D: the port and the two runs beside it, labelled on its right (E-E's labels go on E-E's right, its hole's on its left)
    tube_r = PORT['bore'] / 2 + PORT_WALL
    (tx, gy), (mx, _) = (runs['tweeter'][0][0], runs['tweeter'][0][1]), (runs['mid'][0][0], runs['mid'][0][1])
    xl = org_d[0] + k * PLAN + 4.0
    S.ax.annotate(f'port tube ø{2 * tube_r:g}', xy=P(org_d, RUN + tube_r, PLAN - 30), xytext=(xl, org_d[1] + 36.5), fontsize=5, ha='left', va='center', zorder=8,
                  arrowprops=dict(arrowstyle='-', lw=LW['dim'] * PT, color=INK, shrinkA=0, shrinkB=0))
    for xx in (mx, tx):
        S.ax.annotate('' if xx == tx else f'mid x {mx:g}, tweeter x {tx:g}, rising\nfrom their glands, {mx - RUN - tube_r:g} and {tx - RUN - tube_r:g}\nfrom the tube', xy=P(org_d, xx, gy), xytext=(xl, org_d[1] + 26.0),
                      fontsize=5, ha='left', va='center', zorder=8, arrowprops=dict(arrowstyle='-', lw=LW['dim'] * PT, color=INK, shrinkA=0, shrinkB=0))
    # E-E: the mid's run to the divider's hole, the mounts, the tweeter's rising
    xh, _, zh = runs['mid'][9]
    S.ax.add_patch(Rectangle((org_e[0] + k * (xh - 6), org_e[1] + k * (WALL + MID_CHAMBER_DEPTH)), k * 12, k * WALL, fc='white', ec=INK,
                             lw=LW['hidden'] * PT, ls=(0, (2, 1)), zorder=5))
    S.ax.annotate(f'ø12 hole, z {zh:g},\nbelow (4.3)', xy=P(org_e, xh, WALL + MID_CHAMBER_DEPTH + WALL / 2), xytext=(org_e[0] - 4.0, org_e[1] + 5.0), fontsize=5,
                  ha='right', va='center', zorder=8, arrowprops=dict(arrowstyle='-', lw=LW['dim'] * PT, color=INK, shrinkA=0, shrinkB=0))
    xr = org_e[0] + k * PLAN + 4.0
    def cross(r, z_):      # where a run crosses a plane
        for a_, b_ in zip(r[:-1], r[1:]):
            if (a_[2] - z_) * (b_[2] - z_) < 0:
                t = (z_ - a_[2]) / (b_[2] - a_[2]); return a_[0] + t * (b_[0] - a_[0]), a_[1] + t * (b_[1] - a_[1])
        return r[-1][0], r[-1][1]
    xb, yb = cross(runs['tweeter'], zE)
    S.ax.annotate('the tweeter\'s, rising\nto its channel', xy=P(org_e, xb, yb), xytext=(xr, org_e[1] + 35.0), fontsize=5, ha='left', va='center', zorder=8,
                  arrowprops=dict(arrowstyle='-', lw=LW['dim'] * PT, color=INK, shrinkA=0, shrinkB=0))
    S.ax.annotate('the mid\'s run on its\ncable-tie mounts (4.6)', xy=P(org_e, PLAN - WALL, WALL + MID_CHAMBER_DEPTH + WALL + 14.0), xytext=(xr, org_e[1] + 21.0),
                  fontsize=5, ha='left', va='center', zorder=8, arrowprops=dict(arrowstyle='-', lw=LW['dim'] * PT, color=INK, shrinkA=0, shrinkB=0))
    # the brace's window seen below E-E (its outline, thin grey)
    c0, c1, r_ = WALL + INNER / 2 - BRACE_WINDOW / 2, WALL + INNER / 2 + BRACE_WINDOW / 2, BRACE_WINDOW_R
    pts = []
    for (cx, cy, a0) in ((c1 - r_, c0 + r_, -90), (c1 - r_, c1 - r_, 0), (c0 + r_, c1 - r_, 90), (c0 + r_, c0 + r_, 180)):
        pts += [P(org_e, cx + r_ * math.cos(math.radians(a0 + 90 * t)), cy + r_ * math.sin(math.radians(a0 + 90 * t))) for t in np.linspace(0, 1, 9)]
    pts.append(pts[0]); pts = np.array(pts)
    S.ax.plot(pts[:, 0], pts[:, 1], color=LIGHT, lw=LW['thin'] * PT, zorder=1.5)


def _port_note():
    import cad
    L_ = cad.port_length_mm()
    return (f'The port: a {PORT["bore"]:g} bore, its tube {PORT["bore"] + 2 * PORT_WALL:g} outside in a ø{PORT["bore"] + 2 * PORT_WALL + 0.5:g} hole through the back, '
            f'centre z {PORT["z"]:g}; its ø{PORT["flange"]:g} x {PORT_FLANGE_T:g} flange glued to the finish. {L_:g} from the flange\'s face, with the {PORT_FLARE_R:g} '
            f'flare collar {L_ + PORT_FLARE_R:g} long. Printed {L_ + PORT_TRIM:g} and trimmed at its inner end until the impedance dip sits at the tuning, measured in the '
            f'sealed box (the glands tightened, the mid fitted, the divider\'s hole puttied, the fill in, the amplifier\'s cut-out closed by a scrap board on the EPDM): a '
            f'DATS V3 (or a sound-card jig) clipped to the woofer cable\'s free end inside the amplifier\'s box; trim 2 mm at a time until the minimum between the two peaks '
            f'is at {_fb_hz():g} Hz (README, step 9).')


def _fb_hz():
    import json
    try:
        return json.load(open(os.path.join(OUT, '..', 'acoustics.json')))['fb_target_hz']
    except Exception:
        return 32.0


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
        # anchored on the tube's lower wall and set below it: section D-D's cutting plane runs along the port's axis
        lab(PLAN - WALL - 20, PORT['z'] - PORT['bore'] / 2 - 2, f'port: ø{PORT["bore"]:g} bore,\nø{PORT["bore"] + 2 * PORT_WALL:g} in a ø{PORT["bore"] + 2 * PORT_WALL + 0.5:g}\nhole, {L_ + PORT_FLARE_R:g} long\n(2.5)', dx=-8, dy=-10)
    lab(WOOFER_REBATE['depth'] + 60 * XS, WOOFER['z'], 'woofer', dx=40)
    yb0, yb1, zb0, zb1 = cad.amp_box_extent()
    lab(PLAN - WALL - 45 * XS, AMP['z'], f'amplifier\'s\nbox, sealed:\n{AMP_BOX["depth"]:g} clear,\nz {zb0:g}\nto {zb1:g}', dx=-14)
    if not BOOK:      # the bookshelf's roof detail is drawn large and its labels fill that space: its ring, lettered C, says it
        lab(WAVEGUIDE['throat_y'] - 40, WAVEGUIDE['throat_z'] + 30, 'waveguide insert\nand tweeter\n(detail C)', dx=60, dy=12)
    lab(cad.wire_hole_y(), 880, 'tweeter cable:\n14 mm channel', dx=-30, dy=14)
    S.text(org[0] - k * PLAN, org[1] - 18, ('red dashed: the cables\' runs to the amplifier (sheet 4),\nprojected onto the centre plane (in plan: sections D-D and E-E);\n'
                                         'black squares: cable-tie mounts (4.6)') if MID else 'red dashed: the cables\' runs to the amplifier (sheet 4)', size=4.6, color=RED, va='top')
    if MID:
        plan_sections(S, M, org, k)
        for (surf, (x_, y_, z_)) in runs_3d()[1]:
            S.ax.add_patch(Rectangle((org[0] - k * y_ - 1.0, org[1] + k * (z_ + (4 if z_ < TOP_Z0 - 1 else -4)) - 1.0), 2.0, 2.0, fc=INK, ec='none', zorder=7))
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
    iax.plot(wire_paths()['tweeter'][:4, 0], wire_paths()['tweeter'][:4, 1], color=RED, lw=0.45 * PT, ls=(0, (3, 1.5)), zorder=5)
    S.label(org2[0] - k2 * RUN, y0p - 11, f'DETAIL C, {SC["roof"]}')
    S.text(org2[0] - k2 * RUN, y0p - 17, 'the cable simplified: its connector and the tweeter\'s own lead on sheet 3', size=4.6, ha='center', va='center', color=RED)
    # the detail's boundary on section A-A, lettered (d24, round 3)
    cx0, cz0, cx1, cz1 = -PLAN - 6 * XS, BODY - 40 * XS, 8 * XS, TOTAL + 8 * XS
    S.lines([np.array([[cx0, cz0], [cx1, cz0], [cx1, cz1], [cx0, cz1], [cx0, cz0]])], org, k, lw=LW['thin'], ls=(0, (6, 1.5, 1, 1.5)))
    S.ax.text(org[0] + k * cx0 - 1.5, org[1] + k * cz1 + 1.5, 'C', fontsize=VIEW_PT, fontweight='bold', ha='right', va='bottom', zorder=6)
    ty, tz = WAVEGUIDE['throat_y'], WAVEGUIDE['throat_z']
    S.centreline((-(ty + 70), tz), (12, tz), org2, k2)
    r0 = WAVEGUIDE['r0']
    S.dim_in(iax, k2, (-ty, tz + 60 * XS), (0, tz + 60 * XS), 0, f'{ty:g} to the throat', size=5, feet=((-ty, tz + r0), (0, BODY)))
    S.dim_in(iax, k2, (0, BODY), (0, tz), -10, f'{tz - BODY:g}', size=5)
    zv = (BODY + tz - INSERT['boss_d'] / 2) / 2          # the insert's back face shows below its boss (none on the bookshelf)
    if tz - INSERT['boss_d'] / 2 - BODY > 6:
        S.dim_in(iax, k2, (-INSERT['back_y'], zv), (0, zv), 0, f'{INSERT["back_y"]:g}', size=5, feet=(None, (0, BODY)))     # to the insert's back, under its boss
    else:
        S.dim_in(iax, k2, (-INSERT['boss_back_y'], tz + 15 * XS), (0, tz + 15 * XS), 0, f'{INSERT["boss_back_y"]:g} to the boss\'s back',
                 size=5, feet=((-INSERT['boss_back_y'], tz), (0, BODY)))
    # the waveguide named in its air under the axis, clear of the dimension lines over it (the bookshelf's label sits
    # in the air too, over the insert's floor)
    cap_lab = [((cad.retainer_y()[0] + cad.retainer_y()[1]) / 2, tz - sum(cad.retainer_rings()) / 4, 'retaining cap (3.2)', -14, -40)] if RETAINER else []
    for (y, z, t, dx, dy) in [((ty - 40, tz - 10, 'the waveguide (air)', 20, -8) if BOOK else (ty - 62, tz - 10, 'the waveguide (air)', 12, 27)),
                              (WAVEGUIDE['throat_y'] + 20, tz + 10, 'tweeter, rear-mounted', -20, 55),     # above the left slope: clear of the bay's label (cad.wire_hole_y(), BODY - 15, 'cable channel', -45, -12),
                              ] + cap_lab + [
                              (cad.wire_hole_y() + 6, tz + INSERT['bay_dz'] + 6, 'connector bay', -40, 30),
                              # the two solids named on themselves, in white, under the waveguide's floor and in the block
                              (0.7 * ty, BODY + 0.6 * (tz - WAVEGUIDE['r0'] - BODY), 'insert', 0, 0),     # clear of the insert's back's dimension
                              (0.73 * PLAN, BODY + 0.27 * RISE, 'gable block (birch)', 0, 0)]:
        xy_ = (org2[0] - k2 * y, org2[1] + k2 * z)
        if dx == 0 and dy == 0:
            S.ax.text(xy_[0], xy_[1], t, fontsize=5.2, ha='center', va='center', zorder=8, bbox=dict(fc='white', ec='none', pad=0.3))
            continue
        S.ax.annotate(t, xy=xy_, xytext=(xy_[0] + dx, xy_[1] + dy), fontsize=5.2,
                      ha='left' if dx > 0 else 'right', va='center', zorder=8, bbox=dict(fc='white', ec='none', pad=0.3),
                      arrowprops=dict(arrowstyle='-', lw=LW['dim'] * PT, color=INK))
    S.notes(250, 112, 'The roof', [
        f'The waveguide insert (light blue) sits in a pocket in the gable block, {INSERT["clear"]:g} mm clear all round: the pocket +0.2/0 and the insert 0/-0.15 on their widths, so {INSERT["clear"]:.2f} to {INSERT["clear"] + 0.175 + 1e-9:.2f} a side. Paint only the insert\'s face: mask its sides, base and back and the pocket\'s walls. It slides out forward, level, with the tweeter on it.',
        (f'The tweeter is rear-mounted: it goes in from behind through a ø{TWEETER_PART["flange_d"] + 0.4:g} bore and its front face seats on the ring round the throat, its dome and surround filling the {2 * WAVEGUIDE["r0"]:g} mm throat, so the wall runs on from the surround with no step. A printed cap bearing on its motor\'s back holds it there, screwed to the boss\'s back face (sheet 3).'
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
    # the bookshelf's is drawn larger: lower, to clear the border, and 4 mm right, so its labels clear the front view
    x0p, y0p = (254 if BOOK else 250), (190 if BOOK else 205) - k * 40 * XS
    os_ = (x0p - k * clip[0], y0p - k * clip[1])
    loops, bg = centre_section(M)
    sub = {n: loops[n] for n in ('gable-block', 'top-panel', 'front-baffle', 'waveguide-insert', 'tweeter-frame', 'tweeter-dome', 'tweeter-surround',
                                 'tweeter-retainer') if n in loops}
    iax = S.inset(x0p, y0p, clip, k)
    draw_section(S, sub, [], os_, k, ax=iax)
    S.centreline((-(INSERT['boss_back_y'] + 20), WAVEGUIDE['throat_z']), (10, WAVEGUIDE['throat_z']), os_, k)
    ty, tz = WAVEGUIDE['throat_y'], WAVEGUIDE['throat_z']
    zb = TOP_Z0 - 6.0 / k                 # 6 mm of sheet under the top panel, clear of its hatching
    r0_ = WAVEGUIDE['r0']
    S.dim_in(iax, k, (-ty, zb), (0, zb), 0, f'{ty:g} to the throat', size=5, feet=((-ty, tz - r0_), (0, BODY)))
    S.dim_in(iax, k, (-INSERT['boss_back_y'], zb), (-ty, zb), 0, f'{INSERT["boss_back_y"] - ty:g}', size=5,
             feet=((-INSERT['boss_back_y'], tz - INSERT['boss_d'] / 2 + 1), None))
    S.dim_in(iax, k, (6 * XS, BODY), (6 * XS, tz), 0, f'{tz - BODY:g}', size=5)
    S.ax.annotate(f'bore ø{TWEETER_PART["flange_d"] + 0.4:g} from the back:\nthe tweeter goes in from behind,\nits {"front face" if RETAINER else "faceplate"} seats at the throat (y {ty:g})', xy=(os_[0] - k * (ty + 8), os_[1] + k * (tz + TWEETER_PART['flange_d'] / 2 - 2)),
                  xytext=(os_[0] - k * (ty + 2) + 18, os_[1] + k * (tz + 55 * XS)), fontsize=5, zorder=8, arrowprops=dict(arrowstyle='-', lw=LW['dim'] * PT, color=INK))
    wxy = (os_[0] - k * (ty - 50), os_[1] + k * (tz - 5))
    S.ax.annotate('the waveguide (air)', xy=wxy, xytext=((wxy[0] - 4, wxy[1] + 12) if BOOK else (wxy[0] + 22, os_[1] + k * (tz + 28))),
                  fontsize=5, ha='center' if BOOK else 'left', zorder=8, arrowprops=dict(arrowstyle='-', lw=LW['dim'] * PT, color=INK))
    # the wiring in the section: the tweeter's lead into the bay, the connector at the channel's mouth, the cabinet's
    # lead down the channel and through the top panel, sealed there with silicone (the same runs as the render model's)
    I_, T_ = INSERT, TWEETER_PART
    yw = cad.wire_hole_y(); zbay = tz + I_['bay_dz']; zcon = cad.connector_z()     # the mated pair standing in the bay (d12, round 3)
    # the tweeter lead's spare, home: a loop in the bay between the connector and the bay's end (the drawing check's
    # d1, round 4), the lead passing through it on its way to the plug
    y_in, y_out = yw + 5.5, yw + I_['bay_l'] / 2 - 1.5
    ly, ry = (y_in + y_out) / 2, max((y_out - y_in) / 2, 2.0)
    lz, rz = zbay + 2.0, min(max(2 * ry, 4.0), I_['bay_d'] / 2 - 6.0)
    lead = np.array([(ty + T_['flange_t'] + T_['body_depth'] - 2, tz - 6), (I_['boss_back_y'] + 4, zbay + 4),
                     (ly - 0.6 * ry, lz + 0.8 * rz), (yw + 2, zcon + 16), (yw, zcon + 11)])
    down = np.array([(yw, zcon - 11), (yw, BODY - 38 * XS)])
    for pth in (lead, down):
        iax.plot(-pth[:, 0], pth[:, 1], color=RED, lw=0.9 * PT, solid_capstyle='round', zorder=6)
    iax.add_patch(Rectangle((-(yw + 4), zcon - CONNECTOR['mated_l'] / 2), 8, CONNECTOR['mated_l'], fc='#f4f1e8', ec=INK, lw=0.4 * PT, zorder=7))
    iax.plot([-(yw + 4), -(yw - 4)], [zcon, zcon], color=INK, lw=0.3 * PT, zorder=8)
    a_ = np.linspace(0, 2 * np.pi, 60)
    iax.plot(-(ly + ry * np.cos(a_)), lz + rz * np.sin(a_), color=RED, lw=0.6 * PT, ls=(0, (2, 1)), zorder=6)
    iax.add_patch(Rectangle((-(yw + WIRE_HOLE_D / 2), zbay - I_['bay_d'] / 2 - 20), WIRE_HOLE_D, 20, fc='#bdbdbd', ec=INK, lw=0.3 * PT, zorder=7))   # the silicone plug
    # labels to the left, right-aligned in the gap between the front view and this section
    gx_ = lambda y: x0p - 7 - (os_[0] - k * y)
    # down the sheet in the order of their targets, so no two leaders cross: the bay at its roof, the lead across it,
    # the loop's lower left, the connector
    labs = []
    ym = (I_['boss_back_y'] + 4 + ly - 0.6 * ry) / 2
    for (y, z, t, dx, dy) in ((yw, zbay + I_['bay_d'] / 2, f'connector bay ø{I_["bay_d"]:.0f}', gx_(yw), 22),
                              (ym, zbay + 4 + (lz + 0.8 * rz - zbay - 4) * (ym - I_['boss_back_y'] - 4) / (ly - 0.6 * ry - I_['boss_back_y'] - 4),
                               f'tweeter\'s own lead,\n2 x 0.75 mm2 flex', gx_(ym), 14),
                              (ly + 0.87 * ry, lz - 0.5 * rz, 'the lead\'s spare, looped\nin the bay (3.4)', gx_(ly + 0.87 * ry), 4),
                              (yw, zcon - 4, 'connector, Mini-Fit\nJr. (3.1): the plug on\nthe tweeter\'s lead, the\nsocket on the cabinet\'s', gx_(yw), -12),
                              (yw, zbay - I_['bay_d'] / 2 - 10, 'silicone round the cable,\n20 deep, from the bay', gx_(yw), -24),
                              # the channel named at its wall under the silicone, so its leader runs below the silicone's
                              (yw + WIRE_HOLE_D / 2, (zbay - I_['bay_d'] / 2 - 20 + TOP_Z0) / 2, f'channel ø{WIRE_HOLE_D:.0f}', gx_(yw + WIRE_HOLE_D / 2), -32),
                              (yw, BODY - 36 * XS, 'to the amplifier\n(sheet 4)', gx_(yw), -30)):
        labs.append([y, z, t, dx, os_[1] + k * z + dy])
    if RETAINER:     # the cap behind the motor, named (the drawing check's d14, round 7)
        (yf_c, yb_c), (od_c, id_c) = cad.retainer_y(), cad.retainer_rings()
        yc_, zc_ = (yf_c + yb_c) / 2, WAVEGUIDE['throat_z'] + (od_c + id_c) / 4
        # at the head of the column, its two lines under the frame's top edge (round 7's first print had it across it)
        labs.append([yc_, zc_, f'retaining cap (3.2), its {RETAINER["screws"]}\nscrews into the boss', gx_(yc_),
                     min(os_[1] + k * zc_ + 30, A3[1] - 10 - 2 - 4.3)])
    # stacked from the top: a label that would overlap the one above it moves down (at 1:1 the bookshelf's silicone and
    # channel labels printed over each other)
    hgt = lambda L_: 4.3 * (L_[2].count('\n') + 1)
    order = sorted(range(len(labs)), key=lambda j_: -labs[j_][4])
    for p_, i_ in zip(order, order[1:]):          # each under the one above it, in their order down the sheet
        labs[i_][4] = min(labs[i_][4], labs[p_][4] - hgt(labs[p_]) / 2 - 1.5 - hgt(labs[i_]) / 2)
    for (y, z, t, dx, ty_) in labs:
        # each leader leaves its label's near end, so a lower label's leader cannot run through the text above it
        S.ax.annotate(t, xy=(os_[0] - k * y, os_[1] + k * z), xytext=(os_[0] - k * y + dx, ty_), fontsize=4.8,
                      ha='right' if dx < 0 else 'left', va='center', zorder=9, color=INK,
                      arrowprops=dict(arrowstyle='-', lw=LW['dim'] * PT, color=INK, shrinkA=0, shrinkB=0,
                                      relpos=(1.0, 0.5) if dx < 0 else (0.0, 0.5)))
    S.label(os_[0] - k * 110 * XS, os_[1] + k * BODY - 18 - k * 25 * XS, 'SECTION B-B (WITH THE GABLE)')
    if cad.insert_printed_in_halves():
        # the halves' pins cross the section's plane, the split: drawn as their circles, and named (d13, round 3)
        for (py, pz) in cad.insert_split_pins():
            iax.add_patch(Circle((-py, pz), 1.6, fc='white', ec=INK, lw=0.4 * PT, zorder=9))
        py, pz = max(cad.insert_split_pins(), key=lambda p_: p_[1])      # named at the upper one, over the insert in clear paper
        S.ax.annotate('split pins ø3 x 16, two (3.9)', xy=(os_[0] - k * py, os_[1] + k * pz), xytext=(os_[0] - k * py + 30, os_[1] + k * pz),
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
    zm = sum(z for _, z in mags) / len(mags)
    for (x, z) in mags:     # the upper row named above, the lower below: the pins sit between the rows
        S.lines([circle_pts(-x, z, INSERT['magnet_d'])], ob, k, lw=LW['outline'])
        up = z >= zm
        S.text(ob[0] + k * (-x), ob[1] + k * (z + (1 if up else -1) * INSERT['magnet_d'] / 2) + (2.0 if up else -2.0),
               f'magnet ø{INSERT["magnet_d"]:g}x{INSERT["magnet_t"]:g}', size=4.6, ha='center', va='baseline' if up else 'top')
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
                      + f', 120° apart, for the retaining cap\'s\n{RETAINER["screw"]}',
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
        (f'Solder the tweeter\'s own lead ({TWEETER_LEAD["l"]:g} mm of {TWEETER_LEAD["wire"]}) to its tabs and crimp the connector\'s plug on its end: {CONNECTOR["series"]}, '
         f'{CONNECTOR["plug"]}, pin 1 {CONNECTOR["pin1"]}. The socket on the cabinet\'s lead: {CONNECTOR["socket"]}. Mated, {CONNECTOR["mated_l"]:g} long or less.'),
        (f'Pass the tweeter in from behind through the ø{T_["flange_d"] + 0.4:g} bore, dome first, and seat its front face on the throat\'s seat on a {RETAINER["gasket"]:g} mm '
         f'closed-cell foam ring, ID {2 * WAVEGUIDE["r0"] + 1:g} / OD {T_["flange_d"]:g}, punched (its ID never inside the throat). Fit the printed retaining cap '
         f'(stl/tweeter-retainer.stl: a ring ø{cad.retainer_rings()[0]:g} / ø{cad.retainer_rings()[1]:g} x {cad.retainer_y()[1] - cad.retainer_y()[0]:g} long on a flange ø{RETAINER["flange_d"]:g} x {RETAINER["flange_t"]:g}) '
         f'into the bore behind it, the lead through its middle: its ring bears on the motor\'s back rim and its flange stands {RETAINER.get("preload", 0.0):g} off the boss. Drive its {RETAINER["screws"]} {RETAINER["screw"]} '
         f'into the boss until the flange seats, pressing the gasket by that much: no thread to SB\'s own screw holes is needed, and any motor up to the ring\'s diameter fits.'
         if RETAINER else
         f'Bond {T_["screws"]} {INSERT_SCREW["insert"]} inserts into the seat with {INSERT_SCREW["bond"]} (ø{INSERT_SCREW["hole_d"]:g} x {INSERT_SCREW["depth"]:g} holes on ø{T_["bolt_circle"]:g}; a heat-set insert will not melt into cured resin). '
         f'Pass the tweeter in from behind through the ø{T_["flange_d"] + 0.4:g} bore, dome first, seat its faceplate on a 0.5 mm closed-cell foam ring, ID {2 * WAVEGUIDE["r0"] + 1:g} / OD {T_["flange_d"]:g}, punched (its ID never inside the throat), and screw it to the inserts with {INSERT_SCREW["screw"]} through its own holes. '
         f'Measure first: the heads need 0.5 clear of the body (the circle at least the body + {INSERT_SCREW["head_d"] + 1:g}).'),
        f'Glue the magnets into the insert\'s back with epoxy, polarity marked, and their partners into the pocket\'s back wall, opposite poles out. Bond the two pins into the insert with epoxy.',
        (f'The cabinet\'s lead is fed down the channel from the bay, through the empty pocket, and caught through the woofer\'s cut-out (it cannot be pushed up from inside). '
         f'Its socket stands on the bay\'s floor, the lead\'s end {LEAD_ABOVE_GROMMET:g} mm above the top panel\'s underside (10 past the floor); seal the channel round it with '
         f'20 mm of neutral-cure silicone from the bay before the first fitting. To fit: hold the insert just clear of its pocket, reach in and plug the tweeter\'s lead into the '
         f'socket (its {TWEETER_LEAD["l"]:g} mm reaches with a hand in the pocket), then slide the insert home, feeding the spare into the bay as a loop, '
         + ('clear of the 1.1 mm between the cap\'s screw heads and the bore\'s floor.' if RETAINER else 'behind the tweeter\'s body in the boss\'s bore and the bay.')),
        f'Slide the insert in, level, until the pins seat and the magnets pull it home: its face flush with the roof, the seam even. Fit: the pocket +0.2/0 and the insert 0/-0.15 on their widths ({INSERT["clear"]:.2f} to {INSERT["clear"] + 0.175 + 1e-9:.2f} a side; the boss in its bore the same); paint only the insert\'s face. '
        f'A print service holds about 0.2 to 0.3 % (0.6 to 0.9 on {max(u for (u, _) in cad.insert_outline()) - min(u for (u, _) in cad.insert_outline()):.0f}): order the base\'s width and the boss\'s ø{INSERT["boss_d"]:g} as critical dimensions, '
        'or sand the unpainted sides, base and boss until it slides home with 0.3 to 0.5 a side; never sand the waveguide, the seat or the bore. Check the width before painting.',
        f'Service: pull it out by a ribbon loop glued at the back of the {PULL_GROOVE_NOTE} groove under its front edge, unplug, and the tweeter comes out with it. Between times the loop folds back into its groove: only its end shows, under the insert\'s front edge.',
        pocket_note(cad),
        fixings_note(cad),
    ] + [_halves_note(cad) if cad.insert_printed_in_halves() else _one_piece_note()], width=265)     # about 165 mm wide: at 95 the eight notes ran into the title block
    gable_print_view(S, cad)
    S.save(pdf)


def _gable_pins():
    import json
    try:
        return json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), OUTNAME, 'cad.json'))).get('gable_print_pins') or []
    except Exception:
        return []


def gable_print_view(S, cad, x0=228.0, y_top=121.0):
    """The printed gable (route B, README step 1) in plan: its split planes and every joint's two pins, from cad.json's
    gable_print_pins, with the pins' heights, the bonding and the hollowing rules (the drawing check's d10, round 6)."""
    import textwrap
    pins = _gable_pins()
    if not pins:
        return
    k = 0.2 if BOOK else 0.1
    size = k * PLAN
    o = (x0, y_top - 7.0 - size)
    S.ax.text(x0, y_top, f'PRINTED GABLE (ROUTE B), PLAN, 1:{round(1 / k):d}', fontsize=VIEW_PT, fontweight='bold', va='top', zorder=6)
    P_ = lambda x, y: (o[0] + k * x, o[1] + k * y)
    S.ax.add_patch(Rectangle(o, size, size, fill=False, lw=LW['outline'] * PT, ec=INK, zorder=3))
    S.ax.add_patch(Rectangle(P_(0, RUN - FIN_T / 2), size, k * FIN_T, fill=False, lw=LW['thin'] * PT, ec=LIGHT, zorder=3))      # the fin
    w_ = max(u for (u, _) in cad.insert_outline()) - min(u for (u, _) in cad.insert_outline()) + 2 * INSERT['clear']
    S.ax.add_patch(Rectangle(P_(RUN - w_ / 2, 0), k * w_, k * INSERT['back_y'], fill=False, lw=LW['thin'] * PT, ec=LIGHT, ls=(0, (2, 1)), zorder=3))  # the pocket
    S.ax.add_patch(Circle(P_(RUN, cad.wire_hole_y()), k * WIRE_HOLE_D / 2, fill=False, lw=LW['thin'] * PT, ec=INK, zorder=4))
    planes = sorted({j['plane'] for j in pins})
    for pl in planes:
        ax_, v = pl.split(' = '); v = float(v)
        pts = [P_(v, 0), P_(v, PLAN)] if ax_ == 'x' else [P_(0, v), P_(PLAN, v)]
        S.ax.plot([pts[0][0], pts[1][0]], [pts[0][1], pts[1][1]], color=INK, lw=0.5 * PT, ls=(0, (8, 1.5, 1.5, 1.5)), zorder=5)
    for j in pins:
        ax_, v = j['plane'].split(' = '); v = float(v)
        for (u, z) in j['pins']:
            a_, b_ = ((P_(v - 10, u), P_(v + 10, u)) if ax_ == 'x' else (P_(u, v - 10), P_(u, v + 10)))
            S.ax.plot([a_[0], b_[0]], [a_[1], b_[1]], color=INK, lw=1.4 * PT, solid_capstyle='butt', zorder=6)
    S.text(o[0] + size / 2, o[1] - 3.5, 'front', size=5, ha='center', va='center')
    n = sum(len(j['pins']) for j in pins)
    rows = ['Split planes (chain lines) and pins (bars): stl/gable-print/']
    nb = '\u00a0'                     # a coordinate pair never splits across lines
    for pl in planes:
        ax_ = pl.split(' = ')[0]
        at = [f'({"y" if ax_ == "x" else "x"}{nb}{u:g},{nb}z{nb}{z:g})' for j in pins if j['plane'] == pl for (u, z) in j['pins']]
        rows += textwrap.wrap(f'{pl}: ' + ', '.join(at), 62)
    rows += textwrap.wrap(f'{n} steel pins ø4 x 20 a speaker, in ø4.2 holes 10.5 deep each side; dry-fit each joint closed, then 3M DP420 over its full rim, '
                          'and seal the channel halves\' seam along its length. Hollow the pieces to 3 mm walls, two ø3 drains each in the outer slopes or '
                          'end faces only (none in the base, a joint face, the channel, the bay or the pocket), plugged with resin and filled before paint.', 62)
    tx = o[0] + size + 6.0
    for i, ln in enumerate(rows):
        S.text(tx, y_top - 7.0 - i * 4.3, ln, size=MIN_PT, va='top', fontweight='bold' if i == 0 else 'normal', color='#222')


def fixings_list():
    """The bought fixings a speaker takes, counted from the CAD: (what, how many)."""
    import cad
    mags, pins = cad.insert_fixings()
    nt = sum(DRIVER_SCREWS[r]['n'] for r in ('woofer', 'mid') if DRIVER_SCREWS.get(r))
    I = INSERT
    rows = [(f'M4 T-nuts and M4 x 20 low button heads (F1)', f'{nt}'),
            (f'{AMP_BOX["gland"]} cable glands and their lock nuts', f'{len(cad.amp_glands_xy())}'),
            (f'magnets ø{I["magnet_d"]:g} x {I["magnet_t"]:g} (insert and pocket)', f'{2 * len(mags)}'),
            (f'pins ø{I["pin_d"]:g} x {I["pin_l"]:g}', f'{len(pins)}'),
            (f'fluted dowels {DOWEL_D:g} x 28 (F3)', f'{len(cad.dowel_points())}'),
            ('Molex Mini-Fit Jr. 2-circuit plug and socket (3.1)', '1 pair')]
    if RETAINER:
        rows.append((f'{RETAINER["screw"].split(" (")[0]} (cap)', f'{RETAINER["screws"]}'))
    if INSERT_SCREW:
        rows.append((f'{INSERT_SCREW["insert"]} inserts and {INSERT_SCREW["screw"].split(" (")[0]}', f'{TWEETER_PART["screws"]}'))
    gp = sum(len(j['pins']) for j in _gable_pins())
    halves = cad.insert_printed_in_halves()
    if halves or gp:      # one row, so the list keeps clear of the title block
        rows.append(('steel pins: ' + ', '.join((['ø3 x 16 (insert halves)'] if halves else []) + (['ø4 x 20 (printed gable)'] if gp else [])),
                     ' + '.join((['2'] if halves else []) + ([f'{gp}'] if gp else []))))
    rows += [('foam gaskets 1.5 and 0.5 mm, EPDM tape 3 mm (the plate)', 'a strip each'),
             ('4.3 x 16 self-tapping pan heads (the plate)', 'as drilled')]
    return rows


def _one_piece_note():
    """How the bookshelf's insert, one piece on any resin printer's bed, is printed (the drawing check's d8, round 5)."""
    return ('Printing the insert: one piece, SLA tough resin or MJF nylon. MJF prints solid; SLA solid, or hollow to 4 mm walls with two ø3 drain holes in the '
            'base face between the pins, plugged with resin: none in the waveguide, the seat or the bore, and none within 5 mm of a magnet, pin or insert hole.')


def _halves_note(cad):
    (y1, z1), (y2, z2) = cad.insert_split_pins()
    return ('Printing the insert: one piece from a service (SLA tough resin or MJF nylon, a build of 290 x 220 x 130 or more) is the default, with no '
            'seam in the waveguide. On a desktop resin printer (218 x 123 x 220) print it in halves split at the centre plane, the section B-B: each half '
            f'fits only tilted (about 209 x 117 x 213). Join them with two ø3 x 16 steel dowel pins across the split, at y {y1:.1f}, z {z1:.1f} and y {y2:.1f}, '
            f'z {z2:.1f}, epoxied in ø3.2 holes 8.5 deep each side (0.5 longer than the pin, for the epoxy); dry-fit the halves closed on the pins before mixing the epoxy; fill and sand the seam on the waveguide\'s wall flush. MJF prints solid; SLA solid, or hollow to '
            f'4 mm walls with two ø3 drain holes in the base face between the pins, plugged with resin: none in the waveguide, the seat or the bore, and none within '
            f'5 mm of a magnet, pin, pilot or insert hole.')


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
            f'(their own tolerances, not the title block\'s: the insert\'s pin holes ø{I["pin_d"] + 0.1:g} +0.05/0, the wall\'s ø{I["pin_d"] + 0.2:g} +0.1/0, the magnets\' '
            f'ø{I["magnet_d"] + 0.2:g} +0.1/0 x {I["magnet_t"] + 0.3:g} +0.2/0, each depth from its own face).')


PULL_GROOVE_NOTE = '12 x 1.5 x 30'


def pocket_note(cad):
    """The pocket in the gable block, dimensioned from cad.json's features (the drawing check's d6): what the CNC or the
    printed block must have for the insert, its tweeter and the connector."""
    f = cad.features()['insert']; p = f['pocket']
    us = [u for (u, _) in cad.insert_outline()]          # the width sheet 3 dimensions (the solid's box read 0.1 less: d15, round 4)
    dw = ', '.join(f'({x:g}, {y:g})' for (x, y) in cad.dowel_points())
    return (f'The pocket (gable-block.step): the insert\'s outline + {p["clear"]:g} a side ({max(us) - min(us) + 2 * p["clear"]:.1f} wide at its base), from the slope to its back wall at '
            f'y {p["back_wall_y"]:g}; the boss\'s bore ø{p["boss_bore_d"]:g} to y {p["boss_bore_to_y"]:g}; the connector bay ø{p["bay"]["d"]:g} from y {p["bay"]["from_y"]:g} '
            f'to {p["bay"]["to_y"]:g} on an axis at z {p["bay"]["axis_z"]:g}; the channel ø{f["channel"]["d"]:g} at x {f["channel"]["x"]:g}, y {f["channel"]["y"]:g} down to the '
            f'top panel; R3 or less in the profile\'s corners only, and sharp where the back wall meets the walls (a flat-ended cutter), as the insert\'s back edges are; '
            f'dowel holes ø{DOWEL_D:g} x {DOWEL_DEPTH:g} in the base at {dw}. Milled (route A), the back wall is {p["back_wall_y"]:g} and the bay {p["bay"]["to_y"]:g} from the front: '
            f'a cutter with that reach, or print the block (route B).')


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
    # the plate's and the port's heights are to their centres: a centreline through each, out to the edge the
    # dimensions stand on, so their extension lines start on something (the drawing check's d18, round 6)
    S.centreline((-RUN - (AMP['plate_w'] + 1) / 2 - 6, AMP['z']), (0, AMP['z']), o, k)
    S.dim((0, 0), (0, AMP['z']), -6, f'{AMP["z"]:.0f}', origin=o, scale=k, size=4.8)
    if PORT:
        S.centreline((-RUN - PORT['flange'] / 2 - 6, PORT['z']), (0, PORT['z']), o, k)
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
                   ('Woofer, SB Acoustics SB17NRX2C35-8', '6.5 in, sealed, DSP shelf to 45 Hz', grn, 'CH1', 1.5, 148)]
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
            f'Tweeter (CH2): from its gland up behind the woofer\'s magnet to the top panel, through the 14 mm channel in the top panel and the gable block, 0.6 m of 1.0 mm2, ending {LEAD_ABOVE_GROMMET:g} above the top panel\'s underside in the socket of the connector (3.1, sheet 3) standing on the bay\'s floor, fed down from the bay (3.4).',
            'Seal the tweeter cable in its channel with 20 mm of neutral-cure silicone from the bay (sheet 3): the box is sealed, and the insert\'s pocket is open to the room through its seam.',
            'Round-sheathed cable (H05VV-F 2 x 1.5 and 2 x 1.0 mm2, about 8.0 and 6.4 across), so each gland grips its cable and the silicone seals round the tweeter\'s. Inside the amplifier\'s box cut each of Hypex\'s harness pairs to about 150 mm and butt-splice it to its round cable (woofer 1.5, tweeter 1.0 mm2; crimped splices under heat-shrink): only round cable passes the glands. Tie the woofer\'s run to the amplifier box\'s lid beside its gland and to the box\'s front face at z 380 (adhesive cable-tie mounts); the tweeter\'s run is about 60 mm long and needs no tie.',
            gland_note(),
            f'The crossover (2.4 kHz, LR4), the woofer\'s shelf to 45 Hz (+{shelf_db():g} dB) with a 35 Hz high-pass under it, a limiter and the delays are set in the DSP (out-bookshelf/dsp/). Wire red to + throughout.',
            _stencils_note(),
        ], width=118, size=5.2)
    else:
        S.notes(X0 - 72, 118, 'Runs, connectors and seals', [
            _plate_note(),
            'Woofer (CH1): from its gland in the amplifier box\'s lid straight to the woofer\'s terminals, 0.6 m of 2.5 mm2. Fit 6.3 mm push-on terminals to suit the driver.',
            'Mid (CH2): from its gland up through the brace\'s window, 30 mm in from its back edge, then through the 12 mm hole in the mid chamber\'s divider (x 75, z 630), 1.0 m of 1.5 mm2. Seal the hole round the cable with putty: the mid\'s chamber must stay closed.',
            f'Tweeter (CH3): from its gland up through the brace\'s window to the top panel, through the 14 mm channel in the top panel and the gable block, 1.2 m of 1.0 mm2, ending {LEAD_ABOVE_GROMMET:g} above the top panel\'s underside in the socket of the connector (3.1, sheet 3) standing on the bay\'s floor, fed down from the bay (3.4).',
            'Seal the tweeter cable in its channel with 20 mm of neutral-cure silicone from the bay (sheet 3). The insert\'s pocket is open to the room through its 0.3 mm seam, so an unsealed channel would be a leak in the woofer\'s box. Fill the woofer chamber lightly (about 150 g of polyester fibre), a port\'s diameter from its inner end and off the amplifier\'s box.',
            'Round-sheathed cable (H05VV-F 2 x 2.5, 2 x 1.5 and 2 x 1.0 mm2, about 9.0, 8.0 and 6.4 across), so each gland grips its cable and the silicone seals round the tweeter\'s. Inside the amplifier\'s box cut each of Hypex\'s harness pairs to about 150 mm and butt-splice it to its round cable (woofer 2.5, mid 1.5, tweeter 1.0 mm2; crimped splices under heat-shrink): only round cable passes the glands. The glands, from the right: the tweeter\'s (x 332), the mid\'s (x 297), the woofer\'s (x 262). Hold the runs with adhesive cable-tie mounts (black squares on section A-A and E-E, sheet 2), each stuck on its panel before that panel goes in, a tie threaded loose through it (G1, G3, G4): one on the lid beside each gland; one on the brace\'s top face beside its window\'s right edge at (x 334, y 292), for the tweeter\'s and the mid\'s together; the mid\'s on the right side\'s inner face at (y 290, z 640) and (y 140, z 640) and on the divider\'s back face at (x 300, z 640) and (x 150, z 640), then down to its hole at (x 75, z 630); the tweeter\'s rises from the brace\'s mount straight to its channel at (x 195, y 233.5), held there by the channel\'s silicone seal (4.5) and pulled taut from below, no mount under the top panel. At step 9 feed each run through its loose ties and pull them tight, reaching in through the woofer\'s cut-out and the brace\'s window (the highest, on the side and the divider at z 640, about 180 above the cut-out); keep every run 20 mm clear of the port\'s flare (ø' + f'{PORT["bore"] + 2 * PORT_FLARE_R:g} round z {PORT["z"]:g}' + ').',
            gland_note() + ' The box itself is glued and sealed; its front is the woofer chamber\'s wall.',
            'Polarity, delay, the crossover (about 2.8 kHz tweeter to mid, from the waveguide study), the woofer\'s 25 Hz high-pass and a limiter set to its excursion are set in the DSP (out/dsp/): wire red to + throughout and let the filters do the rest.',
            _stencils_note(),
        ], width=118, size=5.2)
    S.save(pdf)


def _plate_note():
    return (f'The amplifier\'s plate ({AMP["plate_w"]:g} x {AMP["plate_h"]:g} x {AMP["plate_t"]:g}) lies on 3 mm EPDM tape in its {AMP["rebate"]:g} deep rebate, '
            f'R{AMP["plate_r"] + 0.5:g} corners, its module through the {AMP["cut_w"]:g} x {AMP["cut_h"]:g} cut-out (R3 corners: a 6 mm cutter or smaller). '
            f'Drill its screw holes ø3.5 through the {WALL - AMP["rebate"]:g} left under the rebate, from the plate in hand, centred in its flange, 8 or 10 to suit it: '
            '4.3 x 16 self-tapping pan heads (Hypex\'s 4.3 x 25 kit also works, its tips 7 mm into the sealed box).')


def _stencils_note():
    return (f'The stencils ({OUTNAME}/marks/stencil-*.svg), sprayed through vinyl masks before the clear: SHAKE WELL, {MARK_SHAKE["type"]:g} mm type, centred on the '
            f'plinth\'s back at z {MARK_SHAKE["z"]:g}; OPEN OTHER SIDE, {MARK_OPEN["type"]:g} mm type with its arrow, centred on the fin\'s back face.')


def gland_note():
    """The amplifier box's glands, from AMP_BOX: one M16 per cable (a multi-hole seal could not take three cables of
    three sizes: the drawing check's d8, round 3), long-thread for the 18 mm lid."""
    import cad
    gl = cad.amp_glands_xy(); y0 = cad.amp_box_extent()[0]
    xs = ', '.join(f'{gx - WALL:g}' for (gx, _) in gl)
    cb_d, cb_t = AMP_BOX['nut_cb']
    return (f'The amplifier box\'s lid: {len(gl)} {AMP_BOX["gland"]} long-thread (15 mm) cable glands, one per cable (clamping about 4.5 to 10), '
            f'in ø{AMP_BOX["gland_hole"]:g} holes {xs} from the left side\'s inner face and {gl[0][1] - (y0 - WALL):g} from the lid\'s front edge. Their lock nuts, '
            f'20 AF or less (23 across corners) and 5 thick, are epoxied into the ø{cb_d:g} x {cb_t:g} counterbores under the lid before it goes in (G2), each centred '
            f'on a gland\'s body screwed through it and taken out again: a spanner cannot reach a nut sunk 3 deep. After the finish screw the bodies into them from '
            f'above, feed the cables, then tighten the domes.')


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
        10: ('port-tube', (RUN + 0.35 * PORT['flange'], PLAN + PORT_FLANGE_T, PORT['z'] - 0.35 * PORT['flange']) if PORT else (0, 0, 0)),   # its flange's lower half, outside: the upper hid behind the side's corner (d13, round 7)
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
            (8, 'Gable block', '1', 'laminated birch, CNC, or printed in four pieces (step 1)'),
            (9, 'Waveguide insert', '1', 'SLA tough resin or MJF nylon; magnets, pins'),
            (11, 'Amplifier box', '3', 'birch floor, lid (2 glands) and front; sealed'),
            (12, 'Woofer', '1', 'SB Acoustics SB17NRX2C35-8, 6.5 in'),
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
            (8, 'Gable block', '1', 'laminated birch, CNC, or printed in six pieces (step 1)'),
            (9, 'Waveguide insert', '1', 'SLA tough resin or MJF nylon; magnets, pins'),
            (10, 'Port', '1', 'printed tube and flare collar, 92 bore'),
            (11, 'Amplifier box', '3', 'birch floor, lid (3 glands) and front; sealed'),
            (12, 'Woofer', '1', 'Dayton Audio RSS315HF-4, 12 in, 4 ohm'),
            (13, 'Trim rings', '2', 'printed, satin black, over each frame, screws'),
            (14, 'Midrange', '1', 'SB Acoustics Satori MR16P-8, 6.5 in'),
            (15, 'Tweeter', '1', 'SB Acoustics Satori TW29DN-B, faceplate off'),
            (16, 'Amplifier', '1', f'{AMP["model"]}, DSP, 3 channels'),
            (17, 'Tweeter retainer', '1', f'printed cap on the motor\'s back, {RETAINER["screws"]} screws'),
        ]
    # the bookshelf's parts numbered 1 to 12 without gaps (d24, round 3), the balloons with them
    renum = {old: i + 1 for i, (old, *_r) in enumerate(rows)}
    X, Y, rh_ = 262, 272, (9.0 if len(rows) > 14 else 9.6)     # the floorstander's 17 tighter, so the fixings fit above the title block
    S.text(X, Y + 6, 'Parts', size=12, fontweight='bold')
    for i, (n, part, q, what) in enumerate(rows):
        yy = Y - i * rh_
        S.ax.add_patch(Circle((X + 3.6, yy - 1.6), 3.4, fc='white', ec=INK, lw=0.3 * PT, zorder=6))
        S.text(X + 3.6, yy - 1.6, str(renum[n]), size=MIN_PT, ha='center', va='center')
        S.text(X + 9, yy + 0.6, f'{part}  x{q}', size=MIN_PT, fontweight='bold', va='top')
        S.text(X + 9, yy - 3.8, what, size=MIN_PT, va='top', color='#222')
    S.text(X, Y - len(rows) * rh_ - 2, f'Glue-up order: G1 to G{len(general_notes()[0][1])}, sheet 8', size=MIN_PT, va='top')
    # the bought fixings, a speaker's worth, so the parts list is the whole kit (the drawing check's d15, round 5)
    fy = Y - len(rows) * rh_ - 11
    S.text(X, fy, 'Fixings, a speaker (bom.csv)', size=MIN_PT, fontweight='bold', va='top')
    for j, (item, q) in enumerate(fixings_list()):
        S.text(X, fy - 4.6 * (j + 1), item, size=MIN_PT, va='top', color='#222')
        S.text(X + 140, fy - 4.6 * (j + 1), q, size=MIN_PT, va='top', ha='right', color='#222')
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
    # the lid's notes are the longest: it goes where the title block leaves room under it (the drawing check's d16, round 6)
    want = ['top-panel', 'bottom-panel', 'window-brace', 'mid-divider', 'mid-shelf', 'amp-box-lid', 'amp-box-floor', 'amp-box-front']
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
                    if len(txt) > 24:
                        continue          # a shop note for the router (the lid's second set-up): the text under the panel says it
                    # the DXF's note, at least 2.4 mm in from the edge on paper: at 1:5 its 6 mm would print over the edge
                    S.text(x + k * tx, y0 + max(k * ty, 2.4), txt, size=MIN_PT, ha='center', va='center', color='#555')
        lines = [f'{len(at)} x ' * (len(at) > 1) + f'ø{d:g} at {", ".join(at)}: {op}' for (d, op), at in holes.items()] + lines
        q_ = p.get('second_side')
        if q_:       # a second set-up from the underside (the drawing check's d5, round 6): dashed here, in its own file
            for layer, items in q_['layers'].items():
                if layer in ('NOTES', 'REF_HOLES_CUT_FROM_TOP'):
                    continue
                at, dd = [], 0.0
                for it in items:
                    if it[0] == 'circle':
                        (cx, cy), r = it[1], it[2]
                        S.ax.add_patch(Circle((x + k * (p['w'] - cx), y0 + k * cy), k * r, fill=False, lw=LW['hidden'] * PT, ec=INK, ls=(0, (2, 1)), zorder=4))
                        at.append(f'({round(cx, 1):g}, {round(cy, 1):g})'); dd = round(2 * r, 1)
                if at:
                    lines.append(f'{len(at)} x ø{dd:g} x {AMP_BOX["nut_cb"][1]:g} from the underside (dashed): {q_["name"]}.dxf, the panel turned over left to right, '
                                 f'at {", ".join(at)}')
        body = [ln for t in lines for ln in wrap(t)]; note = wrap(p['note'])
        for j, ln in enumerate(body):
            S.text(x, y0 - 10 - j * lh, ln, size=MIN_PT, va='top', color='#222')
        for j, ln in enumerate(note):
            S.text(x, y0 - 10.5 - (len(body) + j) * lh, ln, size=MIN_PT, va='top', color='#555')
        row_h = max(row_h, h + 12 + (len(body) + len(note)) * lh)
    # the rings' sections under the last row when it is full, else in its first empty column (the bookshelf's one panel
    # in its second row put them over that panel's note: the drawing check's d16, round 4)
    free = len(P) % cols
    trim_ring_sections(S, *((x0 + free * pitch + 2.0, y - 46.0) if free else (26.0, 20.0)))
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
        reach = (sc['pcd'] - DRIVER_SCREW['head_d']) / 2 if sc else None
        if reach is not None and r_in > reach:
            # a bore wider than where the heads reach in leaves part of each head showing inside the ring (the drawing
            # check's d11, round 8): said over the ring's label, where there is room
            note_, _ = S.wrap(f'{r_in - reach:g} of each head shows inside the ø{2 * r_in:g} bore (they reach in to ø{2 * reach:g}; '
                              f'a ø{2 * reach - 2:g} bore covers them): owner', 95.0)
            S.text(ox + k * r_in, oy - k * t - 2 - 4.8, note_, size=MIN_PT, ha='left', va='top', color='#222')
        x += k * (r_out - r_in + 4) + 70
    S.text(x0, y0 - 4, f'the channel clears the {DRIVER_SCREW["thread"]} heads (F1): {DRIVER_SCREW["head_d"]:g} across, {DRIVER_SCREW["head_h"]:g} high or less',
           size=MIN_PT, va='top')


# --- sheet 7: the notes ---------------------------------------------------------------------------------------------------
def measure_first():
    """What to measure on the bought parts and the ply before cutting or printing, the value the drawings assume, and
    what it drives: one table in place of notes scattered over four sheets (round 3's sixth question)."""
    H_ = RISE + FIN_H; n_ = int(math.ceil(H_ / GABLE_LAYER))
    under = [f'woofer t - {WOOFER_REBATE["depth"]:g}'] + ([f'mid t - {MID_REBATE["depth"]:g}'] if MID else [])
    rows = [f'Ply: {WALL:g} thick; the sides and inner panels are {PLAN:g} - 2 x {WALL:g} = {INNER:g} wide. For a real thickness t: '
            f'{PLAN:g} - 2t (heights, pockets and rebates unchanged); set WALL = t in params.py and run fab/build.sh again. The gable\'s layers '
            f'are t too: {n_} for its {H_:g} (one more under t {H_ / n_:.2f}). The birch under each rebate is t less its depth '
            f'({", ".join(under)}): buy T-nuts whose barrels are 0.5 shorter than that (a CAD check).']
    T = TWEETER_PART
    import cad
    room_ = INSERT['boss_back_y'] + cad.pocket_bore_behind_boss() - (WAVEGUIDE['throat_y'] + (RETAINER['gasket'] if RETAINER else 0.5) + T['flange_t']) - 1.0
    for role, rb, cut, name in [('woofer', WOOFER_REBATE, WOOFER_CUTOUT, 'woofer')] + ([('mid', MID_REBATE, MID_CUTOUT, 'mid')] if MID else []):
        sc = DRIVER_SCREWS.get(role); fl = rb['depth'] - 1.0 - TRIM_RING['t']
        drv = C_DRIVER_NAME.get(DRIVER_SET[role], DRIVER_SET[role])
        alt = (' (SB\'s drawing, its labels not seen: measure the flange at its screw holes and anything standing above it; over 6.5 at the rim, stop: '
               'a flush rebate would leave 3.1 of birch, too little for any T-nut)' if (BOOK and role == 'woofer') else '')
        src = ' (Audiophonics\' figure)' if (not BOOK and role == 'woofer') else ''
        rows.append(f'{drv}: flange {fl:g} thick{alt} sets the rebate, {rb["depth"]:g} deep; the frame\'s diameter + 1.6 sets the rebate\'s ø{rb["d"]:g}; '
                    f'the cut-out ø{cut:g}' + (f'; {sc["n"]} holes on ø{sc["pcd"]:g}{src}' if sc else '') + f'; the surround at its glue line + 2 sets the trim ring\'s bore, ø{TRIM_RING_ID[role]:g}.')
    if RETAINER:
        od_, id_ = cad.retainer_rings(); yf_, yb_ = cad.retainer_y()
        rows.append(f'{T["model"]}, its faceplate off, drawn from SB\'s drawing: one body ø{T["body_d"]:g}, {T["flange_t"] + T["body_depth"]:g} behind the 5.0 faceplate (29.3 overall). '
                    f'Its widest part behind the dome sets the bore, + 0.4 (ø{T["flange_d"] + 0.4:g}), which centres it, and the cap\'s ring, ø{od_:g}; its depth behind its front face '
                    f'({T["flange_t"] + T["body_depth"]:g}) sets the cap\'s length, the boss\'s back less that ({yb_ - yf_:g}, {RETAINER.get("preload", 0.0):g} over its gap); '
                    f'its back needs a flat rim {RETAINER.get("rim", 6.0):g} wide round its edge, its tabs inside ø{id_:g} or on its side. The dome and surround, {2 * WAVEGUIDE["r0"]:g} across, '
                    f'set the throat. Lift the faceplate as SB says, slowly (glue at the diaphragm\'s rim can stick to it): if the rim is not held without it, the unit needs SB\'s '
                    f'adapter ring (with the WG29-187) or a printed one on the faceplate\'s screws, and the bore grows to its outside diameter (README). Print nothing until it is measured.')
    else:
        rows.append(f'{T["model"]}: the faceplate ø{T["flange_d"]:g} sets the bore, ø{T["flange_d"] + 0.4:g}; its hole circle, ø{T["bolt_circle"]:g}, and its body, '
                    f'ø{T["body_d"] + 0.3:g} or less, set the seat\'s screws; its thickness t ({T["flange_t"]:g}) sets their length, M2.5 x (t + 3.5); its front must be flat from '
                    f'ø{2 * WAVEGUIDE["r0"]:g} to ø{T["flange_d"]:g} and the grille off (or a seat recess for it); the dome and surround {2 * WAVEGUIDE["r0"]:g} across or less. '
                    f'The seat\'s holes take {INSERT_SCREW["insert"]} inserts {INSERT_SCREW["hole_d"] - 0.1:g} or less across, bonded: each hole is the insert\'s '
                    f'outside diameter + 0.1 (ø{INSERT_SCREW["hole_d"]:g} for {INSERT_SCREW["hole_d"] - 0.1:g}). Shops give its cut-out 47.8 to 48, three ø3.3 holes, 45.3 deep '
                    f'(from where?). Go or no-go: its body {room_:g} or less behind the faceplate\'s rear face (the bore runs y {WAVEGUIDE["throat_y"] + T["flange_t"]:g} to '
                    f'{INSERT["boss_back_y"]:g}); over that, print nothing: the owner chooses the fallback (README). Its solder tabs: measure each one\'s angle from the nearest hole and '
                    f'its radius from the axis; each head (ø{INSERT_SCREW["head_d"]:g} on ø{T["bolt_circle"]:g}) needs 1.0 clear of a tab and its solder, or bond the faceplate to the seat '
                    f'with epoxy instead of screwing it. Print nothing until it is measured.')
    rows.append(f'{AMP["model"]} (Hypex\'s manual: vertical or horizontal, in its own compartment; here {"upright" if BOOK else "on its side"}): the plate {AMP["plate_w"]:g} x {AMP["plate_h"]:g} sets the rebate, '
                f'{AMP["plate_w"] + 1:g} x {AMP["plate_h"] + 1:g}; its corner radius r '
                f'sets the rebate\'s corners, R = r + 0.5 (R{AMP["plate_r"] + 0.5:g} for r {AMP["plate_r"]:g}: a square corner, or one under R2.8, will not seat); '
                f'its thickness t ({AMP["plate_t"]:g}) sets the rebate\'s depth, t + 1.5 ({AMP["plate_t"] + 1.5:g}, over the EPDM pressed), and the screws\' length, '
                f't + 13 ({AMP["plate_t"] + 13:g}); the module sets the cut-out, {AMP["cut_w"]:g} x {AMP["cut_h"]:g}; the screw holes come from the plate in hand.')
    rows.append(f'{CONNECTOR["series"]} pair (39-01-2020 and 39-01-2021): its mated length L ({CONNECTOR["mated_l"]:g} drawn, from no maker\'s drawing: Molex SD-5557-003 '
                f'and 55590020-SD give it) sets the bay, ø{INSERT["bay_d"]:g}, which leaves {INSERT["bay_d"] - CONNECTOR["mated_l"]:g} over the mated pair for the lead\'s bend. '
                f'Print the test bay first (stl/connector-test-bay.stl, README, step 1) and mate and unlatch the pair in it by hand.')
    return rows


C_DRIVER_NAME = {'rss315hf-4': 'Woofer (Dayton RSS315HF-4)', 'mr16p-8': 'Mid (SB Satori MR16P-8)', 'sb17nrx2c35-8': 'Woofer (SB17NRX2C35-8)'}


def general_notes():
    """The notes that belong to no one sheet: the glue-up, the fixings, the pocket's floor (round 3's d11, d15, d20)."""
    # the front last, so every inner panel, the top included, slides in from the open front (the top dropped into a closed
    # box at +-0.5 could jam: the drawing check's d5, round 4); a clamp at every step, Titebond staying workable minutes
    glue = ([f'Cut the bottom panel and every inner panel at one fence setting, {INNER:g} ±0.2 wide (tighter than the title block\'s ±0.5: they set and fill '
             'the sides\' spacing). Lay the back face down. Glue both sides and the bottom to it' + (' (the right side with its two cable-tie mounts on its inner face, 4.6)' if MID else '') + '; clamp across the sides and check the diagonals.',
             'The amplifier box: epoxy the glands\' lock nuts into the lid\'s counterbores first (sheet 4); then its floor, front and lid between the sides, '
             'against the back, the joints sealed; clamp across the sides.']
            + ([f'The window brace at z {BRACE_Z:g}, glued to the sides and the back' + (', its cable-tie mount on its top face (4.6)' if MID else '') + '; clamp across the sides.'] if BRACE_Z else [])
            + ([f'Mark the mid chamber on the sides\' inner faces: the shelf\'s underside {MID_SHELF_TOP - 2 * WALL:g} above the bottom panel, the divider\'s front face '
                f'{MID_CHAMBER_DEPTH:g} behind the sides\' front edges. Glue the shelf, then the divider (its two cable-tie mounts on its back face, 4.6), to the marks; '
                f'clamp across the sides. The divider is cut {DIVIDER_SHORT:g} short of the top panel (sheet 6), so the top panel slides over it; G6\'s PU fillet closes the gap.',
                'Line the mid chamber with 10 mm wool or polyester felt (spray adhesive): the divider\'s front face, stopping 15 short of its top edge; the shelf\'s top; '
                'the sides between them; and the top panel\'s underside over the chamber before it goes in, 10 in from each side and stopping 15 short of the divider. '
                'Leave the front\'s back face bare.'] if MID else [])
            + ['The top panel, dowel holes up and its FRONT EDGE to the open front (sheet 6), no cable-tie mounts on its underside'
               + (f'; its felt (G5) {INNER - 20:g} wide and {MID_CHAMBER_DEPTH - 15:g} deep from its front edge, clear of the sides\' felt,' if MID else ',')
               + ' slid in from the front and glued to the sides and the back' + (', dry over the divider' if MID else '') + '; clamp across the sides.'
               + (f' Then, with the front still off, run a 5 mm fillet of PU sealant along the corner between the divider\'s front face and the top panel\'s underside, '
                  f'x {WALL:g} to {PLAN - WALL:g}: the mid\'s chamber\'s fourth wall (check it after G7 through the mid\'s cut-out).' if MID else ''),
               'Plane any inner panel\'s front edge that stands proud of the sides flush. Press the T-nuts into the front baffle\'s inside face; glue the baffle on last, onto '
               'the sides, the bottom, the top panel and every inner panel; clamp front to back. When the glue has set, sand the front\'s top edge flush with the top panel (F2), '
               'then fix the gable block (F3).'])
    return [
        ('Glue-up, in order', glue),
        ('Fixings and the pocket\'s floor', [
            f'Drivers: {DRIVER_SCREW["thread"]} {DRIVER_SCREW["head"]}, the head {DRIVER_SCREW["head_h"]:g} high or less and {DRIVER_SCREW["head_d"]:g} across or less '
            '(ISO 7380 is 2.2 high: the trim ring\'s channel is 2 deep). M4 T-nuts, flange ' +
            ', '.join(f'{v:g} or less across ({k_})' for k_, v in DRIVER_SCREW['tnut_flange'].items()) + ' (DIN 1624\'s M4 is 15: grind each flange flat 6.0 from its centre on the side facing the cut-out), barrel ' +
            ', '.join(f'{v:g} or less ({k_})' for k_, v in DRIVER_SCREW['tnut_barrel'].items()) + ', pressed in before the glue-up.',
            'Before the gable block goes on, sand the front panel\'s top edge flush with the top panel to 0.1: the insert sits on both. '
            'Mask the pocket\'s floor with the insert\'s sides, base and back when you spray: paint only the insert\'s face.',
            f'The gable block on four {DOWEL_D:g} x 28 fluted dowels ({DOWEL_D:g} deep in the top panel, {DOWEL_DEPTH:g} in the block): a birch block with wood glue; a printed one '
            'with epoxy (3M DP420) on its base, scuffed with 120 grit, and on the dowels: wood glue does not hold cured resin.',
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
                # a heading keeps its first note with it, whole, since a note never splits across columns (the
                # bookshelf's 'Sheet 1: Notes' sat at a column's foot with its 1.1 at the next one's head)
                nxt = blocks[i + 1] if i + 1 < len(blocks) else None
                lines = None; need = hgap + (len(textwrap.wrap(nxt[2], ww)) * lh if nxt and nxt[0] == 'p' else 2 * lh)
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


def _sheets_text(on):
    """'sheets 1 and 3', 'sheets 2 and 4 to 6': the drawings whose notes a notes sheet holds."""
    ns = sorted(n for n, o in NOTES_ON.items() if o == on)
    runs = []
    for n in ns:
        if runs and n == runs[-1][1] + 1:
            runs[-1][1] = n
        else:
            runs.append([n, n])
    parts = [f'{a}' if a == b else (f'{a} and {b}' if b == a + 1 else f'{a} to {b}') for a, b in runs]
    return ('sheet ' if len(ns) == 1 else 'sheets ') + (', '.join(parts[:-1]) + ' and ' + parts[-1] if len(parts) > 1 else parts[0])


def sheet7(pdf, M, W):
    """Notes 1: what to measure before cutting or printing (M1, M2, ...), then the notes of the drawings NOTES_ON puts here."""
    m_ = lambda *ks: ', '.join(f'M{M_NUM[k]}' for k in ks if k in M_NUM)
    rel = (f'Cut once M1 is entered: the sides, the bottom and top panels' + (', the window brace, the mid shelf and the divider' if MID else '') +
           f' and the amplifier box\'s panels (sheet 6). On hold until measured (HOLD in their title blocks and DXFs, stl/HOLD.txt): the front ({m_("woofer", "mid")}), '
           f'the back ({m_("amp")}), and every print: the insert, the gable, ' + ('the cap, ' if RETAINER else '') + ('the trim rings and the port.' if PORT else 'and the trim rings.'))
    blocks = [('h', 'Measure first')] + [('p', f'M{i + 1}', t) for i, t in enumerate(measure_first())] + [('p', 'Cut', rel)]
    blocks += _sheet_blocks([n for n, on in NOTES_ON.items() if on == 7])
    notes_sheet(pdf, 7, f'Notes: measure first; {_sheets_text(7)}', f'What to measure before cutting or printing, and the notes {_sheets_text(7)} point to by number.', blocks)


def sheet9(pdf, M, W):
    """Notes 3: the notes of the drawings NOTES_ON puts here (sheet 3's: the tweeter and the insert)."""
    notes_sheet(pdf, 9, f'Notes: {_sheets_text(9)}', f'The notes {_sheets_text(9)} points to by number: fitting the tweeter and the insert, printing it.',
                _sheet_blocks([n for n, on in NOTES_ON.items() if on == 9]))


def sheet8(pdf, M, W):
    """Notes 2: the notes of the drawings NOTES_ON puts here, then the glue-up order (G1, ...) and the fixings (F1, ...)."""
    blocks = _sheet_blocks([n for n, on in NOTES_ON.items() if on == 8])
    for title, items in general_notes():
        blocks.append(('h', title))
        blocks += [('p', f'{"G" if title.startswith("Glue") else "F"}{i + 1}', it) for i, it in enumerate(items)]
    notes_sheet(pdf, 8, f'Notes: {_sheets_text(8)}; glue-up', f'The notes {_sheets_text(8)} point to by number; the order of the glue-up; the fixings.', blocks)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--only', nargs='*', type=int)
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    t = time.time(); M = drawing_model(); W = waveguide_curves(); print(f'model {time.time() - t:.0f}s', flush=True)
    with PdfPages(os.path.join(OUT, 'earmilk-sheets.pdf')) as pdf:
        for n, fn in ((1, sheet1), (2, sheet2), (3, sheet3), (4, sheet4), (5, sheet5), (6, sheet6), (7, sheet7), (8, sheet8), (9, sheet9)):
            if a.only and n not in a.only: continue
            fn(pdf, M, W)
    print('wrote', OUT)


if __name__ == '__main__':
    main()
