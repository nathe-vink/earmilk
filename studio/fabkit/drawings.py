"""Drawings to build from, for any product: A3 sheets projected from the same solids as the cut files (hidden-line
removal on the CAD), dimensioned, numbered and titled, in one PDF.

Sheets, in order:
  1  General arrangement: front, right side and top at one standard scale, the overall sizes, the section line
  2  Section A-A: the product cut down its middle and seen from the right, cut faces hatched part by part
  3  Exploded view, each part ballooned with its line on the parts list
  4+ Sheet parts: the plain panels on one sheet; every panel with holes or pockets on its own, flat as the router sees
     it from its outer face, each feature marked and listed (size, centre from the lower-left corner, depth)
  .  Printed and machined parts, one per parts-list line, three views with hidden lines and their sizes
  .  The parts list (from bom.py) and the product's notes

    drawings.write(product, parts, recs, bom_rows, out)  ->  drawings/<name>-sheets.pdf and sheet-N.png

Conventions: millimetres, first-angle projection, views named for where they are seen from; every text 2.5 mm or more.
"""
import datetime, math, os, textwrap

import numpy as np

from model import Sheet, Printed, Machined, Bought

A3 = (420.0, 297.0)
PT = 72 / 25.4
INK, RED, CUT, POCKET = '#1a1a1a', '#b03030', '#e9e1d2', '#cdbfa6'
MIN_PT = 7.1                       # 2.5 mm text
SCALES = [1, 2, 5, 10, 20, 50]
VIEWS = {
    'front': ((0, -1, 0), (0, 0, 1)),
    'back': ((0, 1, 0), (0, 0, 1)),
    'left': ((-1, 0, 0), (0, 0, 1)),
    'right': ((1, 0, 0), (0, 0, 1)),
    'top': ((0, 0, 1), (0, 1, 0)),
    'iso': ((1, -1.2, 0.9), (0, 0, 1)),
}


def basis(view):
    d, up = (np.array(v, float) for v in VIEWS[view])
    d /= np.linalg.norm(d)
    up = up - d * (up @ d); up /= np.linalg.norm(up)
    return np.cross(up, d), up


def to2d(view, pts):
    X, Y = basis(view)
    return np.c_[np.asarray(pts, float) @ X, np.asarray(pts, float) @ Y]


def hlr(shapes, view, hidden=False):
    """Visible (and hidden) edges seen from `view`, as 2D polylines in the view's frame (orthographic, origin at the
    world origin; the same frame as to2d)."""
    from build123d import Compound, Drawing
    comp = Compound(children=list(shapes))
    d, up = VIEWS[view]
    dr = Drawing(comp, look_from=d, look_up=up, look_at=(0, 0, 0), with_hidden=hidden)

    def polys(c):
        out = []
        if c is None:
            return out
        for e in c.edges():
            L = e.length
            if L < 0.2:
                continue
            n = 2 if e.geom_type.name == 'LINE' else int(min(240, max(6, L / 1.0)))
            pts = [e.position_at(t) for t in np.linspace(0, 1, n)]
            out.append(np.array([[p.X, p.Y] for p in pts]))
        return out
    return polys(dr.visible_lines), (polys(dr.hidden_lines) if hidden else [])


def fit_scale(w, h, box_w, box_h):
    """The largest standard reduction (1:n) at which a w x h model fits a box_w x box_h area of paper."""
    for n in SCALES:
        if w / n <= box_w and h / n <= box_h:
            return n
    return SCALES[-1]


def _bounds(polys):
    P = np.vstack(polys) if polys else np.zeros((1, 2))
    return P.min(axis=0), P.max(axis=0)


class Page:
    def __init__(self, product, number, total, title):
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        from matplotlib.patches import Rectangle
        self.plt = plt
        self.fig = plt.figure(figsize=(A3[0] / 25.4, A3[1] / 25.4))
        self.ax = self.fig.add_axes([0, 0, 1, 1]); ax = self.ax
        ax.set_xlim(0, A3[0]); ax.set_ylim(0, A3[1]); ax.set_aspect('equal'); ax.axis('off')
        ax.add_patch(Rectangle((10, 10), A3[0] - 20, A3[1] - 20, fill=False, lw=0.6 * PT, ec=INK))
        self.product, self.number, self.total, self.title = product, number, total, title
        self.head_y = 281.0
        self._title_block()

    def _title_block(self):
        from matplotlib.patches import Rectangle
        ax = self.ax; x0, y0, w, h = A3[0] - 10 - 190, 10, 190, 34
        p = self.product
        ax.add_patch(Rectangle((x0, y0), w, h, fill=False, lw=0.5 * PT, ec=INK, zorder=8))
        ax.add_patch(Rectangle((x0, y0), w, h, fc='white', ec='none', zorder=7))
        ax.plot([x0, x0 + w], [y0 + 14, y0 + 14], color=INK, lw=0.25 * PT, zorder=8)
        ax.plot([x0 + 146, x0 + 146], [y0, y0 + 14], color=INK, lw=0.25 * PT, zorder=8)
        ax.text(x0 + 3, y0 + 28.5, self.title, fontsize=14, fontweight='bold', va='center', zorder=9)
        ax.text(x0 + 3, y0 + 20.0, f'{p.title}: {p.kind}'[:105], fontsize=MIN_PT, va='center', zorder=9)
        ax.text(x0 + 3, y0 + 9.3, f'mm  |  issue {datetime.date.today().isoformat()}  |  first angle', fontsize=MIN_PT, va='center', zorder=9)
        ax.text(x0 + 3, y0 + 4.0, 'Tolerances: sheet parts ±0.5, pockets ±0.2, holes +0.2/0, prints ±0.15', fontsize=MIN_PT, va='center', zorder=9)
        pre = p.drawing_prefix or p.name[:3].upper()
        ax.text(x0 + 168, y0 + 9.0, f'{self.number} of {self.total}', fontsize=13, fontweight='bold', ha='center', va='center', zorder=9)
        ax.text(x0 + 168, y0 + 3.4, f'{pre}-{self.number:03d}  rev {p.revision}', fontsize=MIN_PT, ha='center', va='center', zorder=9)

    def head(self, s, width=150):
        """A note at the top left of the sheet (its scale, how to read it), wrapped; each call goes under the last."""
        for ln in textwrap.wrap(s, width):
            self.ax.text(20, self.head_y, ln, fontsize=8.5, va='center', zorder=6)
            self.head_y -= 4.6

    def lines(self, polys, origin, k, lw=0.35, color=INK, ls='-', z=3):
        ox, oy = origin
        for q in polys:
            self.ax.plot(ox + q[:, 0] / k, oy + q[:, 1] / k, color=color, lw=lw * PT, ls=ls, solid_capstyle='round', zorder=z)

    def text(self, x, y, s, size=MIN_PT, **kw):
        self.ax.text(x, y, s, fontsize=max(size, MIN_PT), zorder=kw.pop('zorder', 6), **kw)

    def dim(self, a, b, off, text, size=MIN_PT):
        """A linear dimension between paper points a and b, its line `off` mm to the left of a->b."""
        a = np.array(a, float); b = np.array(b, float)
        d = b - a; L = np.linalg.norm(d)
        if L < 1e-6:
            return
        u = d / L; n = np.array([-u[1], u[0]])
        a2, b2 = a + n * off, b + n * off
        for p_, q_ in ((a, a2), (b, b2)):
            self.ax.plot([p_[0] + n[0] * np.sign(off), q_[0] + n[0] * 1.5 * np.sign(off)],
                         [p_[1] + n[1] * np.sign(off), q_[1] + n[1] * 1.5 * np.sign(off)], color=INK, lw=0.18 * PT, zorder=4)
        self.ax.annotate('', xy=b2, xytext=a2, arrowprops=dict(arrowstyle='<|-|>', lw=0.18 * PT, color=INK, shrinkA=0, shrinkB=0,
                                                               mutation_scale=4), zorder=4)
        m = (a2 + b2) / 2 + n * 1.8
        ang = math.degrees(math.atan2(u[1], u[0]))
        if ang > 90.1 or ang < -89.9:
            ang += 180
        self.ax.text(m[0], m[1], text, fontsize=size, ha='center', va='center', rotation=ang, zorder=6,
                     bbox=dict(fc='white', ec='none', pad=0.2))

    def box_dims(self, lo, hi, w_mm, h_mm):
        """Overall width (above) and height (right) of a view drawn between paper points lo and hi."""
        self.dim((lo[0], hi[1]), (hi[0], hi[1]), 6, f'{w_mm:.1f}'.rstrip('0').rstrip('.'))
        self.dim((hi[0], lo[1]), (hi[0], hi[1]), -6, f'{h_mm:.1f}'.rstrip('0').rstrip('.'))

    def save(self, pdf, out):
        os.makedirs(out, exist_ok=True)
        self.fig.savefig(os.path.join(out, f'sheet-{self.number}.png'), dpi=150)
        pdf.savefig(self.fig)
        self.plt.close(self.fig)


def _ds(p):
    """What a part's drawings show: its simpler stand-in if it has one (a driver's outline), else its solid."""
    return p.draw if getattr(p, 'draw', None) is not None else p.solid


def _extent(parts):
    allb = [p.solid.bounding_box() for p in parts]
    lo = np.array([min(b.min.X for b in allb), min(b.min.Y for b in allb), min(b.min.Z for b in allb)])
    hi = np.array([max(b.max.X for b in allb), max(b.max.Y for b in allb), max(b.max.Z for b in allb)])
    return lo, hi


def sheet_ga(pg, parts, cut_x):
    """Front, right and top in first angle (the right side drawn to the left of the front, the top below it), with the
    section line A-A on the front."""
    shapes = [_ds(p) for p in parts if not p.inside]
    views = {v: hlr(shapes, v)[0] for v in ('front', 'right', 'top')}
    b = {v: _bounds(views[v]) for v in views}
    W = b['front'][1][0] - b['front'][0][0]; H = b['front'][1][1] - b['front'][0][1]
    D = b['right'][1][0] - b['right'][0][0]
    k = fit_scale(W + D + 80, H + D + 60, 390 - 40, 250 - 60)
    fx = 30 + D / k + 35 - b['front'][0][0] / k; fy = 60 + D / k + 20 - b['front'][0][1] / k
    pg.lines(views['front'], (fx, fy), k)
    rx = 30 - b['right'][0][0] / k; ry = fy + (b['front'][0][1] - b['right'][0][1]) / k
    pg.lines(views['right'], (rx, ry), k)
    tx = fx; ty = 60 - b['top'][0][1] / k
    pg.lines(views['top'], (tx, ty), k)
    f0 = (fx + b['front'][0][0] / k, fy + b['front'][0][1] / k); f1 = (fx + b['front'][1][0] / k, fy + b['front'][1][1] / k)
    pg.dim((f0[0], f1[1]), (f1[0], f1[1]), 8, f'{W:.0f}')
    pg.dim((f1[0], f0[1]), (f1[0], f1[1]), -8, f'{H:.0f}')
    r0 = (rx + b['right'][0][0] / k, ry + b['right'][0][1] / k); r1 = (rx + b['right'][1][0] / k, ry + b['right'][1][1] / k)
    pg.dim((r0[0], r1[1]), (r1[0], r1[1]), 8, f'{D:.0f}')
    pg.text(f0[0], f0[1] - 7, 'FRONT', size=9, fontweight='bold')
    pg.text(r0[0], r0[1] - 7, 'FROM THE RIGHT', size=9, fontweight='bold')
    tb0 = (tx + b['top'][0][0] / k, ty + b['top'][0][1] / k)
    pg.text(tb0[0], tb0[1] - 7, 'FROM ABOVE', size=9, fontweight='bold')
    # the section plane, x = cut_x, seen from the right: a chain line with arrows pointing the way it is looked at
    sx = fx + to2d('front', [[cut_x, 0, 0]])[0][0] / k
    pg.ax.plot([sx, sx], [f0[1] - 4, f1[1] + 4], color=INK, lw=0.25 * PT, ls=(0, (8, 2, 1, 2)), zorder=5)
    for y, va in ((f1[1] + 4, 'bottom'), (f0[1] - 4, 'top')):
        pg.ax.annotate('', xy=(sx - 5, y), xytext=(sx, y), arrowprops=dict(arrowstyle='-|>', lw=0.3 * PT, color=INK, mutation_scale=6), zorder=5)
        pg.text(sx - 7, y + (1.5 if va == 'bottom' else -1.5), 'A', size=9, fontweight='bold', ha='center', va=va)
    pg.head(f'Scale 1:{k}. First angle: the view from the right is drawn to the left of the front, the view from above '
            'under it. A-A: the section on sheet 2.')
    return k


def _wire_pts(w, step=1.0):
    pts = []
    for e in (w.order_edges() if hasattr(w, 'order_edges') else w.edges()):
        n = 2 if e.geom_type.name == 'LINE' else int(min(240, max(8, e.length / step)))
        q = [e.position_at(t) for t in np.linspace(0, 1, n)]
        if pts and (pts[-1] - q[0]).length > 1e-3 and (pts[-1] - q[-1]).length < (pts[-1] - q[0]).length:
            q = q[::-1]
        pts += q if not pts else q[1:]
    return pts


def sheet_section(pg, parts, cut_x):
    """The product cut at x = cut_x, the half toward the viewer taken away, seen from the right: the cut faces hatched
    (each part its own angle, so neighbours read apart) over the edges beyond them."""
    from build123d import Box, Pos, Align
    from matplotlib.patches import PathPatch
    from matplotlib.path import Path
    lo, hi = _extent(parts)
    pad = 50.0
    keep = Pos(lo[0] - pad, lo[1] - pad, lo[2] - pad) * Box(cut_x - lo[0] + pad, hi[1] - lo[1] + 2 * pad, hi[2] - lo[2] + 2 * pad,
                                                           align=(Align.MIN, Align.MIN, Align.MIN))
    halves, faces = [], []
    for i, p in enumerate(parts):
        try:
            hv = _ds(p) & keep
        except Exception:
            continue
        if hv is None or not hv.faces():
            continue
        halves.append(hv)
        for f in hv.faces():
            c = f.center()
            if abs(c.X - cut_x) < 1e-3 and f.geom_type.name == 'PLANE':
                rings = [to2d('right', np.array([[q.X, q.Y, q.Z] for q in _wire_pts(w)])) for w in [f.outer_wire()] + list(f.inner_wires())]
                faces.append((i, rings))
    vis, _ = hlr(halves, 'right')
    blo, bhi = _bounds(vis)
    k = fit_scale(*(bhi - blo), 360, 215)
    ox = 30 - blo[0] / k + (360 - (bhi - blo)[0] / k) / 2; oy = 52 - blo[1] / k + (215 - (bhi - blo)[1] / k) / 2
    pg.lines(vis, (ox, oy), k, lw=0.3)
    hatches = ['////', '\\\\\\\\', '|||', '---', '++', 'xx']
    for i, rings in faces:
        verts, codes = [], []
        for j, R in enumerate(rings):
            R = np.asarray(R)
            area = 0.5 * np.sum(R[:-1, 0] * R[1:, 1] - R[1:, 0] * R[:-1, 1])
            if (j == 0) != (area > 0):        # the outer ring anticlockwise, holes clockwise
                R = R[::-1]
            pts = np.c_[ox + R[:, 0] / k, oy + R[:, 1] / k]
            verts += pts.tolist() + [pts[0].tolist()]
            codes += [Path.MOVETO] + [Path.LINETO] * (len(pts) - 1) + [Path.CLOSEPOLY]
        pg.ax.add_patch(PathPatch(Path(verts, codes), fc='white', ec=INK, lw=0.35 * PT, hatch=hatches[i % len(hatches)], zorder=4))
    pg.head(f'Scale 1:{k}. Section A-A (sheet 1): the product cut at x {cut_x:.1f} and seen from the right; cut faces '
            'hatched, a different angle for each part.')
    return k


def sheet_exploded(pg, parts, numbers):
    """Each part pushed out from the product's centre along the line to its own centre, drawn in the iso view, and
    ballooned with its parts-list number in two columns either side, so no balloon sits on another."""
    from build123d import Pos
    from matplotlib.patches import Circle
    allb = [p.solid.bounding_box() for p in parts]
    lo, hi = _extent(parts)
    C = (lo + hi) / 2
    moved, centres = [], {}
    for p, b in zip(parts, allb):
        c = np.array([(b.min.X + b.max.X) / 2, (b.min.Y + b.max.Y) / 2, (b.min.Z + b.max.Z) / 2])
        v = (c - C) * 0.6
        moved.append(Pos(*v) * _ds(p))
        centres[p.name] = c + v
    vis, _ = hlr(moved, 'iso')
    blo, bhi = _bounds(vis)
    k = fit_scale(*(bhi - blo), 280, 215)
    ox = 70 - blo[0] / k + (280 - (bhi - blo)[0] / k) / 2; oy = 55 - blo[1] / k + (215 - (bhi - blo)[1] / k) / 2
    pg.lines(vis, (ox, oy), k, lw=0.3)
    anchors = []
    for p in parts:
        n = numbers.get(p.name)
        if n is None:
            continue
        q = to2d('iso', [centres[p.name]])[0]
        anchors.append((n, ox + q[0] / k, oy + q[1] / k))
    mid = ox + (blo[0] + bhi[0]) / 2 / k
    left, right = max(28.0, ox + blo[0] / k - 22), min(392.0, ox + bhi[0] / k + 22)
    for side, xb in ((-1, left), (1, right)):
        col = sorted([a for a in anchors if (a[1] < mid) == (side < 0)], key=lambda a: -a[2])
        ys, prev = [], 272.0 + 9
        for _, _, y in col:
            yb = min(max(y, 60.0), prev - 9.0)
            ys.append(yb); prev = yb
        if ys and ys[-1] < 60:                        # pushed off the bottom: lift the column
            ys = [y + (60 - ys[-1]) for y in ys]
        for (n, x, y), yb in zip(col, ys):
            pg.ax.plot([x, xb - side * 3.6], [y, yb], color=INK, lw=0.18 * PT, zorder=5)
            pg.ax.plot([x], [y], marker='o', ms=1.6, color=INK, zorder=5)
            pg.ax.add_patch(Circle((xb, yb), 3.6, fc='white', ec=INK, lw=0.3 * PT, zorder=6))
            pg.ax.text(xb, yb, str(n), fontsize=MIN_PT, ha='center', va='center', zorder=7)
    pg.head(f'Scale 1:{k}, parts drawn apart. Balloons are the parts list\'s numbers (last sheet).')


def _shape(P):
    """What a closed 2D outline is, for the feature table: ('Ø', d) for a circle, ('rect', w, h), else ('profile',)."""
    P = np.asarray(P)
    c = (P.min(axis=0) + P.max(axis=0)) / 2
    r = np.linalg.norm(P - c, axis=1)
    if len(P) > 12 and r.std() < 0.05:
        return ('Ø', 2 * r.mean())
    w, h = np.ptp(P, axis=0)
    area = 0.5 * abs(np.sum(P[:-1, 0] * P[1:, 1] - P[1:, 0] * P[:-1, 1]))
    if w * h > 0 and area / (w * h) > 0.995:
        return ('rect', w, h)
    return ('profile',)


def flat_features(rec):
    """The panel's features in its drawing's frame (outer face, origin the outline's lower left): through cuts H, pockets
    from the face P, pockets from the inner face U, each with its shape, centre and depth."""
    import flats as _fl
    L = rec['layers']
    o = np.array(rec['origin2d'])
    feats = []
    for it in L['CUT_INSIDE']:
        if it[0] == 'circle':
            feats.append(dict(kind='H', shape=('Ø', 2 * it[2]), c=np.array(it[1]), r=it[2], pts=None, depth='through'))
        else:
            P = it[1]
            feats.append(dict(kind='H', shape=_shape(P), c=(P.min(axis=0) + P.max(axis=0)) / 2, pts=P, depth='through'))
    for name, items in L.items():
        if name.startswith('POCKET_') and not name.endswith('UNDERSIDE'):
            d = float(name[7:-2])
            for it in items:
                P = it[1]
                feats.append(dict(kind='P', shape=_shape(P), c=(P.min(axis=0) + P.max(axis=0)) / 2, pts=P, depth=d))
    for d, ws in sorted(rec['under'].items()):
        for P3 in ws:
            P = _fl.to2d(rec, P3) - o
            feats.append(dict(kind='U', shape=_shape(P), c=(P.min(axis=0) + P.max(axis=0)) / 2, pts=P, depth=d))
    size = lambda f: f['shape'][1] if len(f['shape']) > 1 else 0.0
    out = []
    for kind in 'PHU':                     # numbered largest first: a rebate before the cut-out inside it
        fs = sorted([f for f in feats if f['kind'] == kind], key=lambda f: (-size(f), -f['c'][1], f['c'][0]))
        for i, f in enumerate(fs, 1):
            f['mark'] = f'{kind}{i}'
            out.append(f)
    return out


def draw_flat(pg, rec, x0, y0, k, feats):
    """One sheet part, flat, at paper (x0, y0) and 1:k: outline, through cuts, pockets hatched, inner-face pockets dashed,
    each feature's mark beside it, and the overall size."""
    from matplotlib.patches import Polygon as MPoly, Circle
    L = rec['layers']
    for it in L['CUT_OUTSIDE']:
        P = it[1]
        pg.ax.add_patch(MPoly(np.c_[x0 + P[:, 0] / k, y0 + P[:, 1] / k], closed=True, fc=CUT, ec=INK, lw=0.35 * PT, zorder=2))
    for f in sorted(feats, key=lambda f: 'PHU'.index(f['kind'])):
        if f['kind'] == 'P':
            P = f['pts']
            pg.ax.add_patch(MPoly(np.c_[x0 + P[:, 0] / k, y0 + P[:, 1] / k], closed=True, fc=POCKET, ec=INK, lw=0.2 * PT, hatch='////', zorder=3))
        elif f['kind'] == 'H':
            if f['pts'] is None:
                pg.ax.add_patch(Circle((x0 + f['c'][0] / k, y0 + f['c'][1] / k), f['r'] / k, fc='white', ec=INK, lw=0.3 * PT, zorder=4))
            else:
                P = f['pts']
                pg.ax.add_patch(MPoly(np.c_[x0 + P[:, 0] / k, y0 + P[:, 1] / k], closed=True, fc='white', ec=INK, lw=0.3 * PT, zorder=4))
        else:
            P = f['pts']
            pg.ax.add_patch(MPoly(np.c_[x0 + P[:, 0] / k, y0 + P[:, 1] / k], closed=True, fill=False, ec=INK, lw=0.3 * PT, ls=(0, (3, 2)), zorder=5))
    # marks: on a ray from the feature's centre, just outside its edge, turned round until clear of the marks placed
    taken = []
    for f in feats:
        c = np.array(f['c'])
        half = None if f['shape'][0] == 'Ø' else np.ptp(f['pts'], axis=0) / 2
        a0 = {'P': 45, 'H': 20, 'U': 135}[f['kind']]
        for da in (0, 25, -25, 50, -50, 75, -75, 100, -100, 140, -140, 180):
            ang = math.radians(a0 + da)
            u = np.array([math.cos(ang), math.sin(ang)])
            if half is None:
                rr = f['shape'][1] / 2
            else:                              # where the ray leaves the feature's box
                rr = min(half[0] / max(abs(u[0]), 1e-9), half[1] / max(abs(u[1]), 1e-9))
            tip = c / k + u * (rr / k)
            lab = tip + u * 3.0
            bw, bh = 1.7 * len(f['mark']) + 1.0, 3.2
            bx = lab[0] + 0.6 * u[0] - (bw if u[0] < 0 else 0)
            box = (bx, lab[1], bx + bw, lab[1] + bh)
            if not any(box[0] < t[2] and t[0] < box[2] and box[1] < t[3] and t[1] < box[3] for t in taken):
                break
        taken.append(box)
        pg.ax.plot([x0 + tip[0], x0 + lab[0]], [y0 + tip[1], y0 + lab[1]], color=INK, lw=0.18 * PT, zorder=6)
        pg.ax.text(x0 + lab[0] + 0.6 * u[0], y0 + lab[1] + 0.6 * u[1], f['mark'], fontsize=MIN_PT, ha='left' if u[0] > 0 else 'right',
                   va='bottom', zorder=7, bbox=dict(fc='white', ec='none', pad=0.1))
    w, h = rec['w'], rec['h']
    pg.dim((x0, y0 + h / k), (x0 + w / k, y0 + h / k), 6, f'{w:.1f}')
    pg.dim((x0, y0), (x0, y0 + h / k), 6, f'{h:.1f}')


def feature_table(pg, feats, x, y):
    """The features of one panel as a table: mark, size, centre (from the outline's lower left, outer face), depth."""
    cols = [(x, 'mark'), (x + 11, 'size'), (x + 40, 'x'), (x + 55, 'y'), (x + 70, 'depth')]
    for cx, t in cols:
        pg.text(cx, y, t, size=8, fontweight='bold')
    y -= 5.2
    for f in feats:
        s = f['shape']
        size = f'Ø{s[1]:.1f}' if s[0] == 'Ø' else (f'{s[1]:.1f} x {s[2]:.1f}' if s[0] == 'rect' else 'profile (DXF)')
        depth = 'through' if f['depth'] == 'through' else (f"{f['depth']:g} from face" if f['kind'] == 'P' else f"{f['depth']:g} from inside")
        for (cx, _), v in zip(cols, [f['mark'], size, f"{f['c'][0]:.1f}", f"{f['c'][1]:.1f}", depth]):
            pg.text(cx, y, v)
        y -= 4.6
        if y < 70:
            pg.text(x, y, 'more in the DXF', color=RED); y -= 4.6; break
    y -= 2
    for ln in ['H: cut through. P: pocket from the face shown.', 'U: pocket from the inner face (dashed; its own DXF).',
               'Centres from the lower-left corner,', 'seen from the outer face.']:
        pg.text(x, y, ln); y -= 4.4


def sheet_plain(pg, recs, product):
    """Panels with nothing but their outline, alike ones together, at one scale."""
    from matplotlib.patches import Rectangle
    groups = {}
    for nm, r in recs.items():
        p = r['part']
        key = (round(r['w'], 1), round(r['h'], 1), p.make.thickness, p.make.material)
        groups.setdefault(key, []).append(nm)
    keys = list(groups)[:6]
    one_row = len(keys) <= 3
    cells = [(25 + 128 * (i % 3), 268 - 108 * (i // 3)) for i in range(6)]
    k = max(fit_scale(kk[0], kk[1], 100, 180 if one_row else 72) for kk in keys)
    for (x0, ytop), kk in zip(cells, keys):
        w, h, T, mat = kk
        x, y = x0 + 8, ytop - 12 - h / k
        pg.ax.add_patch(Rectangle((x, y), w / k, h / k, fc=CUT, ec=INK, lw=0.35 * PT, zorder=2))
        pg.dim((x, y + h / k), (x + w / k, y + h / k), 5, f'{w:.1f}')
        pg.dim((x + w / k, y), (x + w / k, y + h / k), -5, f'{h:.1f}')
        names = groups[kk]
        qty = sum(recs[n]['part'].qty for n in names) * product.count
        pg.text(x, y - 6, ', '.join(names), size=8, fontweight='bold')
        pg.text(x, y - 10.5, f'{T:g} mm {mat}, {qty} for the set')
    pg.head(f'Scale 1:{k}. Panels cut to their outline only (DXF files in dxf/); sizes as seen from the outer face.')


def sheet_featured(pg, rec, product):
    feats = flat_features(rec)
    k = fit_scale(rec['w'] + 30, rec['h'] + 30, 250, 200)
    x0 = 32; y0 = 62 + (200 - rec['h'] / k) / 2
    draw_flat(pg, rec, x0, y0, k, feats)
    p = rec['part']
    pg.text(x0, y0 - 9, f"{rec['name']}: {rec['T']:g} mm {p.make.material}, {p.qty * product.count} for the set, seen from its outer face",
            size=8, fontweight='bold')
    if rec['under']:
        pg.text(x0, y0 - 13.5, f"inner-face pockets: dxf/{rec['name']}-underside.dxf (seen from that face)")
    if rec['odd']:
        pg.text(x0, y0 - 18, 'not in the cut file: ' + rec['odd'][0][:90], color=RED)
    feature_table(pg, feats, 300, 268)
    pg.head(f'Scale 1:{k}. As the router sees it from the outer face; DXF: dxf/{rec["name"]}.dxf. Marks listed at the right.', 62)


def sheet_solids(pg, items):
    """Printed and machined parts, one parts-list line each: front, right and top with hidden lines, their sizes."""
    rows = [266.0, 154.0]
    for ytop, (p, row, n) in zip(rows, items):
        vh = {v: hlr([_ds(p)], v, hidden=True) for v in ('front', 'right', 'top')}
        b = {v: _bounds(vh[v][0] + vh[v][1]) for v in vh}
        sz = {v: b[v][1] - b[v][0] for v in vh}
        k = fit_scale(sz['front'][0] + sz['right'][0] + sz['top'][0], max(s[1] for s in sz.values()), 360 - 110, 64)
        x = 30.0
        y_base = ytop - 24 - max(s[1] for s in sz.values()) / k
        for v, label in (('front', 'FRONT'), ('right', 'FROM THE RIGHT'), ('top', 'FROM ABOVE')):
            vis, hid = vh[v]
            o = (x - b[v][0][0] / k, y_base - b[v][0][1] / k)
            pg.lines(vis, o, k)
            pg.lines(hid, o, k, lw=0.2, ls=(0, (2.5, 1.5)))
            lo = (x, y_base); hi = (x + sz[v][0] / k, y_base + sz[v][1] / k)
            pg.box_dims(lo, hi, sz[v][0], sz[v][1])
            pg.text(x, y_base - 6, label, size=8, fontweight='bold')
            x = hi[0] + 34
        m = p.make
        what = (f'{m.material} print' + (f', {m.orient}' if getattr(m, 'orient', '') else '')) if isinstance(m, Printed) else f'{m.process}, {m.material}'
        pg.text(30, ytop - 6, f"{n}. {row['item']}: {what}; {p.solid.volume / 1000:.0f} cm3 each; {row['qty']} for the set; 1:{k}", size=8, fontweight='bold')
        if p.notes:
            pg.text(30, ytop - 10.5, '; '.join(p.notes)[:150])
    pg.head('Three views each, hidden edges dashed; STL and STEP files in stl/ and step/. Numbers are the parts list\'s.')


def sheet_parts_list(pg, rows, notes):
    y = 268
    cols = [(20, 'no.', 4), (30, 'item', 30), (88, 'make', 8), (104, 'qty', 5), (116, 'what', 82), (276, 'size', 40), (360, 'each USD', 12)]
    for x, t, _ in cols:
        pg.text(x, y, t, size=8, fontweight='bold')
    y -= 6
    for i, r in enumerate(rows, 1):
        vals = [str(i), r['item'], r['kind'], str(r['qty']), str(r['what']), str(r['size']),
                f"{r['usd_each']:,.2f}" if isinstance(r['usd_each'], (int, float)) else '[PRICE]']
        wrapped = [textwrap.wrap(v, w) or [''] for v, (_, _, w) in zip(vals, cols)]
        nl = min(3, max(len(wl) for wl in wrapped))
        for (x, _, _), wl in zip(cols, wrapped):
            for j, ln in enumerate(wl[:nl]):
                pg.text(x, y - 4.2 * j, ln)
        y -= 4.2 * nl + 1.6
        if y < 110:
            pg.text(20, y, f'{len(rows) - i} more lines: bom.md', color=RED); break
    y -= 5
    pg.text(20, y, 'Notes', size=9, fontweight='bold'); y -= 6
    for j, n in enumerate(notes, 1):
        for ln in textwrap.wrap(f'{j}. {n}', 120):
            pg.text(20, y, ln); y -= 4.4
        if y < 50:
            break


def write(product, parts, recs, bom_rows, out):
    from matplotlib.backends.backend_pdf import PdfPages
    dd = os.path.join(out, 'drawings'); os.makedirs(dd, exist_ok=True)
    plain = {n: r for n, r in recs.items() if not (r['holes'] or r['circles'] or r['pockets'] or r['under'] or r['odd'])}
    featured = [n for n in recs if n not in plain]
    numbers = {}
    for i, r in enumerate(bom_rows, 1):
        for n in r['item'].split(', '):
            numbers[n] = i
    by_name = {p.name: p for p in parts}
    solids = []
    for i, r in enumerate(bom_rows, 1):
        p = by_name.get(r['item'].split(', ')[0])
        if p is not None and isinstance(p.make, (Printed, Machined)):
            solids.append((p, r, i))
    solid_pages = [solids[i:i + 2] for i in range(0, len(solids), 2)]
    total = 3 + bool(plain) + len(featured) + len(solid_pages) + 1
    lo, hi = _extent(parts)
    cut_x = (lo[0] + hi[0]) / 2
    path = os.path.join(dd, f'{product.name}-sheets.pdf')
    for f in os.listdir(dd):                  # a rebuild with fewer sheets leaves no stale ones
        if f.startswith('sheet-') and f.endswith('.png'):
            os.remove(os.path.join(dd, f))
    with PdfPages(path) as pdf:
        n = 1
        pg = Page(product, n, total, 'General arrangement'); sheet_ga(pg, parts, cut_x); pg.save(pdf, dd); n += 1
        pg = Page(product, n, total, 'Section A-A'); sheet_section(pg, parts, cut_x); pg.save(pdf, dd); n += 1
        pg = Page(product, n, total, 'Exploded view'); sheet_exploded(pg, parts, numbers); pg.save(pdf, dd); n += 1
        if plain:
            pg = Page(product, n, total, 'Sheet parts: plain panels'); sheet_plain(pg, plain, product); pg.save(pdf, dd); n += 1
        for nm in featured:
            pg = Page(product, n, total, f'Sheet part: {nm}'); sheet_featured(pg, recs[nm], product); pg.save(pdf, dd); n += 1
        for items in solid_pages:
            pg = Page(product, n, total, 'Printed and machined parts'); sheet_solids(pg, items); pg.save(pdf, dd); n += 1
        pg = Page(product, n, total, 'Parts list and notes')
        pg.head(f'For {product.count}; prices are budgets (bom.md says where each comes from).')
        sheet_parts_list(pg, bom_rows, product.notes); pg.save(pdf, dd)
    return path, total
