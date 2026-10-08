"""Vector files for the metal and the marks, set exactly as the renders set them (render/src/textures.mjs).

    /root/.venvs/fab/bin/python fab/typeset.py

Fonts: render/fonts (Archivo Black and Archivo, SIL Open Font License). Text is shaped with HarfBuzz, the same shaper
the browser used, with the renders' tracking, so the metal matches the pictures.

Writes to out/metal and out/marks:
  wordmark-letters.dxf / .svg       the cast-letter wordmark at 44 mm type size, one closed outline per piece (8 pieces:
                                    the i's dot is its own), for laser, waterjet or CNC cutting from 1.5 mm metal (2026-10-08; 2.5 to 3 before)
  wordmark-letters.step / .stl      the same, 1.5 mm thick, for a casting service or a printed casting master
  wordmark-template-front.pdf/svg   1:1 drilling and placing template for the plinth's front (and the back)
  facts-print.svg / .pdf            the Nutrition Facts printed on the back under the clear (2026-10-07), 266 x 260, 1:1
  stencil-open-other-side.svg       vinyl mask letters for the fin's back face (2026-10-07; the back slope before), 27 mm Archivo Bold with the arrow
  stencil-shake-well.svg            vinyl mask letters for the plinth's back face (26 mm)
"""
import io, json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from params import *  # noqa: F401,F403
import numpy as np
from fontTools.ttLib import TTFont
from fontTools.pens.basePen import BasePen
import uharfbuzz as hb

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, '..', 'render', 'fonts')
OUT = os.path.join(HERE, 'out-bookshelf' if BOOK else 'out')


import sys as _sys
_sys.path.insert(0, os.path.join(HERE, '..', 'studio'))
from typeset import Font, FlatPen, set_line, area, inside, pieces, bbox, svg_path, write_svg, write_dxf, write_pdf  # noqa: E402


# --- the parts ------------------------------------------------------------------------------------------------------
def wordmark(center_x, center_z, spec):
    """The badge as the renders draw it: the texture's centre at (center_x, center_z), baseline 0.35 em below it."""
    f = Font('ArchivoBlack-Regular.woff')
    size = spec['type']
    contours, width = set_line(f, 'earmilk', size, spec['tracking'], center_x, center_z - 0.35 * size, align='center')
    return contours, width


def stud_points(outer, holes, max_studs=2, stud_d=3.0):
    """Where to put mounting studs in a piece: the deepest points inside it (largest inscribed circles), via a distance
    transform on a 0.1 mm raster. Returns [(x, y, inscribed radius)]."""
    from scipy import ndimage
    from matplotlib.path import Path as MPath
    x0, y0, x1, y1 = bbox([outer])
    res = 0.1
    nx, ny = int((x1 - x0) / res) + 3, int((y1 - y0) / res) + 3
    gx, gy = np.meshgrid(x0 + (np.arange(nx) - 1) * res, y0 + (np.arange(ny) - 1) * res)
    pts = np.c_[gx.ravel(), gy.ravel()]
    mask = MPath(outer).contains_points(pts)
    for h in holes:
        mask &= ~MPath(h).contains_points(pts)
    mask = mask.reshape(ny, nx)
    dist = ndimage.distance_transform_edt(mask) * res
    found = []
    for _ in range(max_studs):
        j = np.unravel_index(np.argmax(dist), dist.shape)
        r = dist[j]
        if r < stud_d / 2 + 1.0 or (found and r < 0.6 * found[0][2]):
            break
        px, py = gx[j], gy[j]
        found.append((float(px), float(py), float(r)))
        # suppress a disc around it so the next stud lands elsewhere in the letter
        keep = (gx - px) ** 2 + (gy - py) ** 2 > (0.45 * max(x1 - x0, y1 - y0)) ** 2
        dist = dist * keep
    return found


def make_wordmark_files():
    os.makedirs(os.path.join(OUT, 'metal'), exist_ok=True)
    # Set as the renders set it (44 mm, tracking -0.035 em, baseline 0.35 em below the badge's centre), then centre the
    # ink on x = 195: the renders centred the text's advance box, which leaves the ink 1.5 mm right of centre.
    contours, width = wordmark(RUN, BADGE['z'], BADGE)
    bx0, by0, bx1, by1 = bbox(contours)
    dx = RUN - (bx0 + bx1) / 2
    contours = [[(x + dx, y) for (x, y) in c] for c in contours]
    groups = pieces(contours)
    bx0, by0, bx1, by1 = bbox(contours)
    info = {'type_size_mm': BADGE['type'], 'tracking_em': BADGE['tracking'], 'advance_width_mm': round(width, 2),
            'ink_box_front_mm': [round(v, 2) for v in (bx0, by0, bx1, by1)], 'ink_width_mm': round(bx1 - bx0, 2),
            'ink_height_mm': round(by1 - by0, 2), 'pieces': len(groups), 'ink_shift_to_centre_mm': round(dx, 2)}
    allc = [c for (o, hs) in groups for c in [o] + hs]
    # The cut sheet: the pieces in place, origin at the ink box's lower left.
    pad = 5.0
    shifted = [[(x - bx0 + pad, y - by0 + pad) for (x, y) in c] for c in allc]
    W, H = bx1 - bx0 + 2 * pad, by1 - by0 + 2 * pad
    write_dxf(os.path.join(OUT, 'metal', 'wordmark-letters.dxf'), [('CUT', shifted)])
    write_svg(os.path.join(OUT, 'metal', 'wordmark-letters.svg'), W, H, [('letters', shifted, 'fill="#000" fill-rule="evenodd"')])
    # 3D: each piece BADGE relief thick (1.5 mm since 2026-10-08), for a casting service or a printed casting master.
    try:
        from build123d import Face, Wire, Polyline, extrude, export_step, export_stl, Compound
        solids = []
        for (o, hs) in groups:
            ow = Wire(Polyline(*[(x - bx0, y - by0, 0) for (x, y) in o], close=True).edges())
            hw = [Wire(Polyline(*[(x - bx0, y - by0, 0) for (x, y) in h], close=True).edges()) for h in hs]
            solids.append(extrude(Face(ow, hw), amount=BADGE['relief']))
        comp = Compound(children=solids)
        export_step(comp, os.path.join(OUT, 'metal', 'wordmark-letters.step'))
        export_stl(comp, os.path.join(OUT, 'metal', 'wordmark-letters.stl'), tolerance=0.02, angular_tolerance=0.1)
    except Exception as ex:  # the 2D files are the deliverable; the 3D ones are a convenience
        print('3D letters skipped:', ex)

    studs = []
    for (o, hs) in groups:
        studs += stud_points(o, hs)
    info['studs_front_mm'] = [[round(x, 1), round(y, 1), round(r, 1)] for (x, y, r) in studs]

    # Placing templates, 1:1, cropped to 250 x 140 mm so they print on Letter or A4 landscape.
    import matplotlib.patches as mpatches
    X0, X1 = RUN - 125, RUN + 125
    for which, base_z, ref_z, ref_label in (
            ('front', BADGE['z'], 0.0, 'FLOOR LINE: align with the bottom edge of the plinth'),
            ('back', BACK_BADGE['z'], BODY, 'TOP EDGE: align with the body\'s top edge, where the gable block starts')):
        oz = base_z - BADGE['z']                      # the back's letters are the front's moved up
        cs = [[(x - X0, y + oz) for (x, y) in c] for c in allc]
        st = [(x - X0, y + oz, r) for (x, y, r) in studs]
        zlo = min(ref_z, base_z - 40) - 12; zhi = max(ref_z, base_z + 40) + 12
        cs = [[(x, y - zlo) for (x, y) in c] for c in cs]
        st = [(x, y - zlo, r) for (x, y, r) in st]
        rz = ref_z - zlo

        def extra(ax, st=st, rz=rz, ref_label=ref_label, zh=zhi - zlo):
            ax.plot([0, X1 - X0], [rz, rz], color='#000', lw=0.8)
            ax.text(2, rz + (2 if rz < zh / 2 else -6), ref_label, fontsize=5.5)
            ax.plot([RUN - X0] * 2, [0, zh], color='#c00', lw=0.4, ls='--')
            ax.text(RUN - X0 + 1.5, zh - 5, 'CENTRELINE: align with the panel\'s centre (195 mm from either side)', fontsize=5, color='#c00')
            for (x, y, r) in st:
                ax.plot([x - 3.5, x + 3.5], [y, y], color='#000', lw=0.35); ax.plot([x, x], [y - 3.5, y + 3.5], color='#000', lw=0.35)
                ax.add_patch(mpatches.Circle((x, y), 1.5, fill=False, lw=0.35))
            ax.plot([5, 105], [-8, -8], color='#000', lw=0.8)
            ax.text(5, -13, '100 mm. Measure it before drilling.', fontsize=5.5)
        write_pdf(os.path.join(OUT, 'metal', f'wordmark-template-{which}.pdf'), X1 - X0, zhi - zlo,
                  fills=[(cs, '#d4d4d4')], extra=extra,
                  title=f'earmilk letter template, {which}, 1:1. Print at 100%, no fit-to-page. Tape on along the reference line and centreline; glue each letter on its shape (epoxy). Optional pins: 2 mm x 10 mm holes at the crosses.')
    return info


def make_facts_print():
    """The Nutrition Facts as printed on the back's finish (2026-10-07, the owner; an engraved bronze plate before): the
    panel 266 x 260, black = ink, 1:1 and right-reading, for a screen (film positive) or a water-slide decal. A 15 mm
    margin carries crop marks at the corners and centre marks top and bottom; on the cabinet the panel is centred on the
    back with its top border at z 770, 90 mm below the body's top edge. Frame: x right, y up, origin at the sheet's
    bottom-left corner."""
    m = 15.0
    LW, LH = LABEL['w'], LABEL['h']
    f = LW / 266.0                           # the layout was set at 266 wide; the bookshelf's panel is the same at 0.564
    W, H = LW + 2 * m, LH + 2 * m
    ox, top = m, H - m                       # panel's left edge and top edge in sheet coordinates
    def Y(v):                                # panel y (mm down from its top, at the 266 layout) to sheet y (up)
        return top - v * f
    ink = []
    # Border: 1.2 wide, its outer edge at the panel's edge.
    t = 1.2 * max(f, 0.75)
    ink.append([(ox, top), (ox + LW, top), (ox + LW, top - LH), (ox, top - LH)])
    ink.append([(ox + t, top - t), (ox + t, top - LH + t), (ox + LW - t, top - LH + t), (ox + LW - t, top - t)])   # hole (reverse)
    x0, x1 = ox + 14 * f, ox + LW - 14 * f
    def rule(y, th):
        th = th * f
        ink.append([(x0, Y(y) - th / 2), (x1, Y(y) - th / 2), (x1, Y(y) + th / 2), (x0, Y(y) + th / 2)][::-1])
    black, bold, reg = Font('ArchivoBlack-Regular.woff'), Font('Archivo-Bold.woff'), Font('Archivo-Regular.woff')
    # Title: 34 mm Archivo Black (scaled), tracking fixed at -0.02 em, shrunk by 3 % steps until it fits the measure.
    size = 34.0 * f; track_mm = -0.02 * size
    while True:
        c, w = set_line(black, 'Nutrition Facts', size, track_mm / size, x0, Y(38))
        if w <= (x1 - x0) or size < 4:
            break
        size *= 0.97
    ink += c
    rule(48, 1.4); rule(72, 7.6)
    if BOOK:   # PROPOSAL 2026-10-08: the bookshelf's own true values (an active speaker has no sensitivity or impedance to state)
        rows = [('Amplifier', '2 x 125 W'), ('Frequency response', '45 Hz to 20 kHz'), ('Inputs', 'XLR or RCA'),
                ('Woofer', '6 in'), ('Tweeter', '1 in'), ('Box', 'sealed, 10 L')]
    else:
        rows = [('Sensitivity', '91 dB'), ('Frequency response', '32 Hz to 20 kHz'), ('Impedance', '8 ohm'),
                ('Woofer', '12 in'), ('Midrange', '6.5 in'), ('Tweeter', '1 in')]
    for i, (k, v) in enumerate(rows):
        b = 98 + 22 * i
        ink += set_line(bold, k, 12.0 * f, 0.0, x0, Y(b))[0]
        ink += set_line(bold, v, 12.0 * f, 0.0, x1, Y(b), align='right')[0]   # 2026-10-08: the values bold like the names
        rule(105 + 22 * i, 1.4)
    rule(226, 7.6)
    ink += set_line(reg, 'Contains no milk.', 11.0 * f, 0.0, x0, Y(244))[0]
    # Crop marks (8 mm, 3 mm off the panel's corners) and centre marks, as thin filled bars outside the panel.
    marks, mw = [], 0.25
    def bar(xa, ya, xb, yb):
        if xa == xb:
            marks.append([(xa - mw / 2, ya), (xa + mw / 2, ya), (xa + mw / 2, yb), (xa - mw / 2, yb)])
        else:
            marks.append([(xa, ya - mw / 2), (xb, ya - mw / 2), (xb, ya + mw / 2), (xa, ya + mw / 2)])
    for (cx, cy, dx, dy) in ((ox, top, -1, 1), (ox + LW, top, 1, 1), (ox, top - LH, -1, -1), (ox + LW, top - LH, 1, -1)):
        bar(min(cx + dx * 3, cx + dx * 11), cy, max(cx + dx * 3, cx + dx * 11), cy)
        bar(cx, min(cy + dy * 3, cy + dy * 11), cx, max(cy + dy * 3, cy + dy * 11))
    bar(W / 2, top + 3, W / 2, top + 11); bar(W / 2, top - LH - 11, W / 2, top - LH - 3)
    os.makedirs(os.path.join(OUT, 'marks'), exist_ok=True)
    write_svg(os.path.join(OUT, 'marks', 'facts-print.svg'), W, H, [
        ('marks', marks, 'fill="#000"'),
        ('ink', ink, 'fill="#000" fill-rule="nonzero"')])
    write_pdf(os.path.join(OUT, 'marks', 'facts-print.pdf'), W, H, fills=[(ink, '#000'), (marks, '#000')], strokes=[],
              title='earmilk Nutrition Facts, printed under the 2K clear. 1:1, black = ink. Centre on the back, top border 90 mm below the body\'s top edge.')
    return {'title_size_mm': round(size, 2), 'panel_mm': [LW, LH], 'sheet_mm': [W, H]}


def make_stencils():
    os.makedirs(os.path.join(OUT, 'marks'), exist_ok=True)
    bold = Font('Archivo-Bold.woff')
    info = {}
    for spec, fname in ((MARK_OPEN, 'stencil-open-other-side.svg'), (MARK_SHAKE, 'stencil-shake-well.svg')):
        size = spec['type']
        c, tw = set_line(bold, spec['text'], size, spec['tracking'], 0.0, 0.0)
        if spec.get('arrow'):
            # The arrow exactly as label() draws it: a bar and a head after the text (canvas y down, so flip).
            x0 = tw + size * 0.35; yc = size * (1.0 - 0.64); hh = size * 0.5
            bar = [(x0, yc - hh * 0.18), (x0 + size * 0.7, yc - hh * 0.18), (x0 + size * 0.7, yc + hh * 0.18), (x0, yc + hh * 0.18)][::-1]
            head = [(x0 + size * 0.7, yc + hh * 0.5), (x0 + size * 1.2, yc), (x0 + size * 0.7, yc - hh * 0.5)]
            c += [bar, head]
        x0, y0, x1, y1 = bbox(c)
        pad = 4.0
        shifted = [[(x - x0 + pad, y - y0 + pad) for (x, y) in cc] for cc in c]
        W, H = x1 - x0 + 2 * pad, y1 - y0 + 2 * pad
        write_svg(os.path.join(OUT, 'marks', fname), W, H, [('mask-letters', shifted, 'fill="#000" fill-rule="nonzero"')])
        info[spec['text']] = {'type_size_mm': size, 'ink_width_mm': round(x1 - x0, 1), 'cap_height_mm': round(y1 - y0, 1)}
    return info


def main():
    info = {'wordmark': make_wordmark_files(), 'facts': make_facts_print(), 'marks': make_stencils()}
    json.dump(info, open(os.path.join(OUT, 'typeset.json'), 'w'), indent=1)
    print(json.dumps(info, indent=1))


if __name__ == '__main__':
    main()
