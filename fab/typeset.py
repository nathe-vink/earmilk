"""Vector files for the metal and the marks, set exactly as the renders set them (render/src/textures.mjs).

    /root/.venvs/fab/bin/python fab/typeset.py

Fonts: render/fonts (Archivo Black and Archivo, SIL Open Font License). Text is shaped with HarfBuzz, the same shaper
the browser used, with the renders' tracking, so the metal matches the pictures.

Writes to out/metal and out/marks:
  wordmark-letters.dxf / .svg       the cast-letter wordmark at 44 mm type size, one closed outline per piece (8 pieces:
                                    the i's dot is its own), for laser, waterjet or CNC cutting from 2.5 to 3 mm metal
  wordmark-letters.step / .stl      the same, 2.5 mm thick, for a casting service or a printed casting master
  wordmark-template-front.pdf/svg   1:1 drilling and placing template for the plinth's front (and the back)
  plate-facts.svg / .pdf / .dxf     the bronze Nutrition Facts plate, 318 x 312: outline, and the engraving as filled areas
  terminal-plate.dxf                128 x 64 plate for the binding posts
  stencil-open-other-side.svg       vinyl mask letters for the back slope (27 mm Archivo Bold with the arrow)
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
OUT = os.path.join(HERE, 'out')


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
    # 3D: each piece 2.5 mm thick, for a casting service or a printed casting master.
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


def make_plate_files():
    """The Facts plate: 318 x 312, the engraved panel 266 x 260 centred with a 26 margin. Plate frame: x right, y up,
    origin at the plate's bottom-left corner."""
    W, H = PLATE['x1'] - PLATE['x0'], PLATE['z1'] - PLATE['z0']
    m = 26.0
    LW, LH = LABEL['w'], LABEL['h']
    ox, top = m, H - m                       # label's left edge and top edge in plate coordinates
    def Y(v):                                # label y (mm down from its top) to plate y (up)
        return top - v
    etch = []
    # Border: 1.2 wide, its outer edge at the label's edge.
    t = 1.2
    etch.append([(ox, Y(0)), (ox + LW, Y(0)), (ox + LW, Y(LH)), (ox, Y(LH))])
    etch.append([(ox + t, Y(t)), (ox + t, Y(LH - t)), (ox + LW - t, Y(LH - t)), (ox + LW - t, Y(t))])   # hole (reverse)
    x0, x1 = ox + 14, ox + LW - 14
    def rule(y, th):
        etch.append([(x0, Y(y - th / 2)), (x1, Y(y - th / 2)), (x1, Y(y + th / 2)), (x0, Y(y + th / 2))][::-1])
    black, bold, reg = Font('ArchivoBlack-Regular.woff'), Font('Archivo-Bold.woff'), Font('Archivo-Regular.woff')
    # Title: 34 mm Archivo Black, tracking fixed at -0.02 x 34 mm, shrunk by 3 % steps until it fits the 238 mm measure.
    size, track_mm = 34.0, -0.02 * 34.0
    while True:
        c, w = set_line(black, 'Nutrition Facts', size, track_mm / size, x0, Y(38))
        if w <= (x1 - x0) or size < 4:
            break
        size *= 0.97
    etch += c
    rule(48, 1.4); rule(72, 7.6)
    rows = [('Sensitivity', '91 dB'), ('Frequency response', '32 Hz to 20 kHz'), ('Impedance', '8 ohm'),
            ('Woofer', '12 in'), ('Midrange', '6.5 in'), ('Tweeter', '1 in')]
    for i, (k, v) in enumerate(rows):
        b = 98 + 22 * i
        etch += set_line(bold, k, 12.0, 0.0, x0, Y(b))[0]
        etch += set_line(reg, v, 12.0, 0.0, x1, Y(b), align='right')[0]
        rule(105 + 22 * i, 1.4)
    rule(226, 7.6)
    etch += set_line(reg, 'Contains no milk.', 11.0, 0.0, x0, Y(244))[0]
    # Plate outline with 3 mm corners.
    r = PLATE['r']; outline = []
    for (cx, cy, a0) in ((W - r, r, -90), (W - r, H - r, 0), (r, H - r, 90), (r, r, 180)):
        for k in range(9):
            a = math.radians(a0 + 90 * k / 8); outline.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    os.makedirs(os.path.join(OUT, 'metal'), exist_ok=True)
    write_svg(os.path.join(OUT, 'metal', 'plate-facts.svg'), W, H, [
        ('outline', [outline], 'fill="none" stroke="#000" stroke-width="0.25"'),
        ('etch', etch, 'fill="#000" fill-rule="nonzero"')])
    write_pdf(os.path.join(OUT, 'metal', 'plate-facts.pdf'), W, H, fills=[(etch, '#000')], strokes=[([outline], '#000', 0.4)],
              title='earmilk: bronze Nutrition Facts plate, 318 x 312 x 3 mm, R3 corners. Black = engrave or etch ~0.3 mm deep, then darken. 1:1.')
    groups = pieces(etch)
    write_dxf(os.path.join(OUT, 'metal', 'plate-facts.dxf'), [('OUTLINE_CUT', [outline]), ('ENGRAVE_OUTLINES', etch)],
              fills=[('ENGRAVE_FILL', groups)])
    return {'title_size_mm': round(size, 2), 'plate_mm': [W, H]}


def make_terminal_plate():
    import ezdxf
    w, h, r = POSTS['w'], POSTS['h'], 3.0
    doc = ezdxf.new('R2010'); doc.units = ezdxf.units.MM; msp = doc.modelspace()
    for n in ('CUT_OUTSIDE', 'CUT_INSIDE', 'NOTES'):
        doc.layers.add(n)
    pts = []
    for (cx, cy, a0) in ((w - r, r, -90), (w - r, h - r, 0), (r, h - r, 90), (r, r, 180)):
        for k in range(9):
            a = math.radians(a0 + 90 * k / 8); pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    msp.add_lwpolyline(pts, close=True, dxfattribs={'layer': 'CUT_OUTSIDE'})
    for sx in (-1, 1):
        msp.add_circle((w / 2 + sx * POSTS['spacing'] / 2, h / 2), POST_HOLE / 2, dxfattribs={'layer': 'CUT_INSIDE'})
    for sx in (-1, 1):
        for sy in (-1, 1):
            msp.add_circle((w / 2 + sx * 56, h / 2 + sy * 25), 1.75, dxfattribs={'layer': 'CUT_INSIDE'})
    msp.add_text('terminal plate 128 x 64 x 3, post holes 10 mm (placeholder: match the posts), screws M3/#4', height=2.5,
                 dxfattribs={'layer': 'NOTES'}).set_placement((0, -6))
    doc.saveas(os.path.join(OUT, 'metal', 'terminal-plate.dxf'))


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
    info = {'wordmark': make_wordmark_files(), 'plate': make_plate_files(), 'marks': make_stencils()}
    make_terminal_plate()
    json.dump(info, open(os.path.join(OUT, 'typeset.json'), 'w'), indent=1)
    print(json.dumps(info, indent=1))


if __name__ == '__main__':
    main()
