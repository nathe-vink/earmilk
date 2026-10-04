"""Text as outlines, set the way a browser sets it: HarfBuzz shaping (kerning on), canvas-style tracking, em-size type.
Shared by every product's metal, stencil and label files. Outlines are lists of (x, y) millimetre points, y up.

    from typeset import Font, set_line, pieces, bbox, write_svg, write_dxf, write_pdf
    contours, width = set_line(Font('ArchivoBlack-Regular.woff'), 'earmilk', 44.0, -0.035, x=0, baseline=0, align='center')

Font() looks in render/fonts by default; pass a path to use another font. TrueType and WOFF both work.
"""
import io, math, os
import numpy as np
from fontTools.ttLib import TTFont
from fontTools.pens.basePen import BasePen
import uharfbuzz as hb

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = os.path.join(ROOT, 'render', 'fonts')


class Font:
    def __init__(self, fname):
        tt = TTFont(fname if os.path.sep in fname else os.path.join(FONTS, fname))
        tt.flavor = None
        buf = io.BytesIO(); tt.save(buf); self.data = buf.getvalue()
        self.tt = TTFont(io.BytesIO(self.data))
        self.upem = self.tt['head'].unitsPerEm
        self.glyphset = self.tt.getGlyphSet()
        self.order = self.tt.getGlyphOrder()
        self.hbfont = hb.Font(hb.Face(hb.Blob(self.data)))

    def shape(self, text):
        buf = hb.Buffer(); buf.add_str(text); buf.guess_segment_properties()
        hb.shape(self.hbfont, buf, {'kern': True, 'liga': False})
        return [(self.order[i.codepoint], p.x_advance, p.x_offset, p.y_offset) for i, p in zip(buf.glyph_infos, buf.glyph_positions)]


class FlatPen(BasePen):
    """Collects glyph contours as polylines, flattening curves to a chord error well under 0.02 mm at these sizes."""
    def __init__(self, glyphset, sx, ox, oy, step=0.25):
        super().__init__(glyphset)
        self.sx, self.ox, self.oy, self.step = sx, ox, oy, step
        self.contours, self.cur = [], None

    def _pt(self, p):
        return (self.ox + p[0] * self.sx, self.oy + p[1] * self.sx)

    def _moveTo(self, p):
        self.cur = [self._pt(p)]; self.last = p

    def _lineTo(self, p):
        self.cur.append(self._pt(p)); self.last = p

    def _qCurveToOne(self, p1, p2):
        p0 = self.last
        L = (math.dist(p0, p1) + math.dist(p1, p2)) * self.sx
        n = max(4, int(math.ceil(L / self.step)))
        for k in range(1, n + 1):
            t = k / n
            x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0]
            y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]
            self.cur.append(self._pt((x, y)))
        self.last = p2

    def _curveToOne(self, p1, p2, p3):
        p0 = self.last
        L = (math.dist(p0, p1) + math.dist(p1, p2) + math.dist(p2, p3)) * self.sx
        n = max(4, int(math.ceil(L / self.step)))
        for k in range(1, n + 1):
            t = k / n
            x = (1 - t) ** 3 * p0[0] + 3 * (1 - t) ** 2 * t * p1[0] + 3 * (1 - t) * t * t * p2[0] + t ** 3 * p3[0]
            y = (1 - t) ** 3 * p0[1] + 3 * (1 - t) ** 2 * t * p1[1] + 3 * (1 - t) * t * t * p2[1] + t ** 3 * p3[1]
            self.cur.append(self._pt((x, y)))
        self.last = p3

    def _closePath(self):
        if self.cur and len(self.cur) > 2:
            if math.dist(self.cur[0], self.cur[-1]) < 1e-6:
                self.cur.pop()
            self.contours.append(self.cur)
        self.cur = None

    _endPath = _closePath


def set_line(font, text, size, tracking_em, x, baseline, align='left'):
    """Canvas-style text: `size` is the em in mm, tracking added after every glyph (as canvas letterSpacing does).
    Returns (contours, advance width in mm). Contours are lists of (x, y) in mm, y up."""
    sx = size / font.upem
    glyphs = font.shape(text)
    track = tracking_em * size
    width = sum(adv * sx + track for (_, adv, _, _) in glyphs)
    if align == 'right':
        x = x - width
    elif align == 'center':
        x = x - width / 2
    contours, pen_x = [], x
    for (name, adv, xo, yo) in glyphs:
        pen = FlatPen(font.glyphset, sx, pen_x + xo * sx, baseline + yo * sx)
        font.glyphset[name].draw(pen)
        contours += pen.contours
        pen_x += adv * sx + track
    return contours, width


def area(c):
    return 0.5 * sum(c[i][0] * c[(i + 1) % len(c)][1] - c[(i + 1) % len(c)][0] * c[i][1] for i in range(len(c)))


def inside(pt, poly):
    x, y = pt; n = len(poly); c = False
    for i in range(n):
        x1, y1 = poly[i]; x2, y2 = poly[(i + 1) % n]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1 + 1e-12) + x1:
            c = not c
    return c


def pieces(contours):
    """Groups glyph contours into physical pieces: each outer contour with the holes inside it."""
    outers = [c for c in contours if area(c) < 0]   # TrueType outers run clockwise (negative area, y up)
    holes = [c for c in contours if area(c) > 0]
    if not outers:  # some fonts run the other way
        outers, holes = holes, outers
    out = []
    for o in outers:
        hs = [h for h in holes if inside(h[0], o)]
        out.append((o, hs))
    return out


def bbox(contours):
    xs = [p[0] for c in contours for p in c]; ys = [p[1] for c in contours for p in c]
    return min(xs), min(ys), max(xs), max(ys)


# --- writers ------------------------------------------------------------------------------------------------------------
def svg_path(contours, flip_h=None):
    d = []
    for c in contours:
        pts = [(x, flip_h - y) if flip_h is not None else (x, y) for (x, y) in c]
        d.append('M' + ' L'.join(f'{x:.3f},{y:.3f}' for (x, y) in pts) + ' Z')
    return ' '.join(d)


def write_svg(path, w, h, layers):
    """layers: list of (id, contours, style). Coordinates in mm, y up; the file is y down."""
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:.2f}mm" height="{h:.2f}mm" viewBox="0 0 {w:.3f} {h:.3f}">']
    for (lid, contours, style) in layers:
        parts.append(f'<g id="{lid}"><path d="{svg_path(contours, h)}" {style}/></g>')
    parts.append('</svg>')
    open(path, 'w').write('\n'.join(parts))


def write_dxf(path, layers, fills=()):
    import ezdxf
    doc = ezdxf.new('R2010'); doc.units = ezdxf.units.MM
    msp = doc.modelspace()
    for (name, contours) in layers:
        if name not in doc.layers:
            doc.layers.add(name)
        for c in contours:
            msp.add_lwpolyline(c, close=True, dxfattribs={'layer': name})
    for (name, groups) in fills:
        if name not in doc.layers:
            doc.layers.add(name)
        for (outer, holes) in groups:
            h = msp.add_hatch(dxfattribs={'layer': name}); h.set_solid_fill()
            h.paths.add_polyline_path(outer, is_closed=True, flags=1)
            for ho in holes:
                h.paths.add_polyline_path(ho, is_closed=True, flags=16)
    doc.saveas(path)


def write_pdf(path, w, h, fills, strokes=(), title=None, extra=None):
    """A 1:1 vector PDF (sheet sized to the artwork plus a margin)."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.path import Path as MPath
    from matplotlib.patches import PathPatch
    m = 15.0
    W, H = w + 2 * m, h + 2 * m + (12 if title else 0)
    fig = plt.figure(figsize=(W / 25.4, H / 25.4)); ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(-m, w + m); ax.set_ylim(-m, h + m + (12 if title else 0)); ax.set_aspect('equal'); ax.axis('off')
    for (contours, color) in fills:
        verts, codes = [], []
        for c in contours:
            verts += list(c) + [c[0]]; codes += [MPath.MOVETO] + [MPath.LINETO] * (len(c) - 1) + [MPath.CLOSEPOLY]
        if verts:
            ax.add_patch(PathPatch(MPath(verts, codes), facecolor=color, edgecolor='none', lw=0))
    for (contours, color, lw) in strokes:
        for c in contours:
            xs = [p[0] for p in c] + [c[0][0]]; ys = [p[1] for p in c] + [c[0][1]]
            ax.plot(xs, ys, color=color, lw=lw)
    if extra:
        extra(ax)
    if title:
        ax.text(0, h + 6, title, fontsize=8, va='bottom', family='sans-serif')
    fig.savefig(path, format='pdf')
    fig.savefig(path[:-4] + '-preview.png', format='png', dpi=150); plt.close(fig)
