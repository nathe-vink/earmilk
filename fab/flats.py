"""Flat cut files for the cabinet panels, from fab/params.py.

    /root/.venvs/fab/bin/python fab/flats.py

Writes:
  out/dxf/<part>.dxf           one panel per file, drawn as seen from its outer face, in millimetres
  out/dxf/sheet-<n>.dxf        the panels for two speakers nested on 1525 x 1525 sheets (5 x 5 ft Baltic birch)
  out/dxf/sheets.svg           a preview of the nesting
  out/cutlist.csv              every part, quantity for a pair, size, material, operations

DXF layers (the names say what to do; CNC shops read them):
  CUT_OUTSIDE       through cut, tool outside the line (panel outlines)
  CUT_INSIDE        through cut, tool inside the line (holes and windows)
  POCKET_3MM        3 mm deep, from the outer face (the shadow-line groove)
  POCKET_1_5MM      1.5 mm deep, from the outer face (the bronze plate's seat)
  DRILL_10_DEEP10   10 mm holes, 10 deep (dowels)
  NOTES             part name and face, not cut
"""
import csv, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from params import *  # noqa: F401,F403
import ezdxf
from ezdxf.enums import TextEntityAlignment

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')
LAYERS = {'CUT_OUTSIDE': 7, 'CUT_INSIDE': 1, 'POCKET_3MM': 3, 'POCKET_1_5MM': 4, 'DRILL_10_DEEP10': 6, 'NOTES': 8}


def rect(x0, y0, x1, y1):
    return [('poly', [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], True)]


def rrect(x0, y0, x1, y1, r, n=8):
    pts = []
    for (cx, cy, a0) in ((x1 - r, y0 + r, -90), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180)):
        for k in range(n + 1):
            a = math.radians(a0 + 90 * k / n)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return [('poly', pts, True)]


def circle(cx, cy, d):
    return [('circle', (cx, cy), d / 2)]


def panel_defs():
    """Each panel: name, qty per speaker, width, height (as seen from its outer face), features by layer, note."""
    wh = TWEETER['faceplate_y'] + TWEETER['faceplate_t'] + TWEETER['body_depth'] / 2   # wire hole y (cad.wire_hole_y)
    P = []
    P.append(dict(name='front-baffle', qty=1, w=PLAN, h=BODY, layers={
        'CUT_INSIDE': circle(RUN, WOOFER['z'], WOOFER_CUTOUT) + circle(RUN, MID['z'], MID_CUTOUT),
        'POCKET_3MM': rect(0, PLINTH_H, PLAN, PLINTH_H + SHADOW)},
        note='outer face up; cutouts sized for the shortlisted Dayton DSA315-8 (272) and SB Acoustics SB17MFC35-8 (146): re-cut for other drivers'))
    tw, th = TERMINAL_CUTOUT
    pk = PLATE
    P.append(dict(name='back-panel', qty=1, w=PLAN, h=BODY, layers={
        'CUT_INSIDE': circle(RUN, PORT['z'], PORT['bore'] + 2 * PORT_WALL + 0.5)
                      + rect(RUN - tw / 2, POSTS['z'] - th / 2, RUN + tw / 2, POSTS['z'] + th / 2),
        'POCKET_1_5MM': rrect(PLAN - pk['x1'], pk['z0'], PLAN - pk['x0'], pk['z1'], pk['r']),
        'POCKET_3MM': rect(0, PLINTH_H, PLAN, PLINTH_H + SHADOW)},
        note='outer face up (seen from behind); 1.5 mm pocket seats the 3 mm bronze plate 1.5 proud'))
    P.append(dict(name='side', qty=2, w=INNER, h=BODY, layers={'POCKET_3MM': rect(0, PLINTH_H, INNER, PLINTH_H + SHADOW)},
                  note='outer face up; finish the groove across the front and back panels\' edges after glue-up'))
    dowels = [(60.0, 200.0), (PLAN - 60.0, 200.0), (60.0, 330.0), (PLAN - 60.0, 330.0)]
    P.append(dict(name='top-panel', qty=1, w=INNER, h=INNER, layers={
        'CUT_INSIDE': circle(RUN - WALL, wh - WALL, WIRE_HOLE_D),
        'DRILL_10_DEEP10': sum((circle(x - WALL, y - WALL, DOWEL_D) for (x, y) in dowels), [])},
        note='upper face up (front edge at the bottom of the drawing); dowels register the gable block'))
    P.append(dict(name='bottom-panel', qty=1, w=INNER, h=INNER, layers={}, note='either face'))
    h = BRACE_WINDOW / 2
    P.append(dict(name='window-brace', qty=1, w=INNER, h=INNER, layers={
        'CUT_INSIDE': rrect(INNER / 2 - h, INNER / 2 - h, INNER / 2 + h, INNER / 2 + h, BRACE_WINDOW_R)},
        note='sits at z 500 to 518, glued to all four walls'))
    P.append(dict(name='mid-shelf', qty=1, w=INNER, h=MID_CHAMBER_DEPTH + WALL, layers={},
                  note='z 572 to 590, from the baffle back to under the divider'))
    P.append(dict(name='mid-divider', qty=1, w=INNER, h=TOP_Z0 - MID_SHELF_TOP, layers={
        'CUT_INSIDE': circle(RUN - 120 - WALL, 40, 12)},
        note='y 108 to 126, z 590 to 842; seal the wire hole after wiring'))
    return P


def gable_layers():
    """Rough blanks for gluing up the gable block: 11 layers of 18 mm birch, each a rectangle a little larger than the
    block's footprint at that layer's bottom face, so the CNC has stock to carve. The top two carry only the fin."""
    out = []
    for i in range(11):
        z0 = BODY + i * GABLE_LAYER
        d = depth_at(z0)
        d = max(d, FIN_T) + 8
        out.append(dict(name=f'gable-layer-{i + 1:02d}', qty=1, w=PLAN + 8, h=round(d, 1), layers={},
                        note=f'gable glue-up, layer {i + 1} of 11 (z {z0:.0f} to {z0 + GABLE_LAYER:.0f}); centre on y = 195'))
    return out


def draw(msp, part, ox=0.0, oy=0.0, label=True):
    w, h = part['w'], part['h']
    msp.add_lwpolyline([(ox, oy), (ox + w, oy), (ox + w, oy + h), (ox, oy + h)], close=True, dxfattribs={'layer': 'CUT_OUTSIDE'})
    for layer, items in part['layers'].items():
        for it in items:
            if it[0] == 'poly':
                pts = [(ox + (w if x is None else x), oy + y) for (x, y) in it[1]]
                msp.add_lwpolyline(pts, close=it[2], dxfattribs={'layer': layer})
            else:
                (cx, cy), r = it[1], it[2]
                msp.add_circle((ox + cx, oy + cy), r, dxfattribs={'layer': layer})
    if label:
        t = msp.add_text(part['name'], height=min(14, h / 6), dxfattribs={'layer': 'NOTES'})
        t.set_placement((ox + w / 2, oy + h / 2 + 10), align=TextEntityAlignment.MIDDLE_CENTER)


def new_doc():
    doc = ezdxf.new('R2010', setup=True)
    doc.units = ezdxf.units.MM
    for name, color in LAYERS.items():
        if name not in doc.layers:
            doc.layers.add(name, color=color)
    return doc


def pack(parts, sheet=(1525.0, 1525.0), margin=15.0, gap=12.0):
    """Shelf packing, largest first, rotation allowed. Returns a list of sheets, each a list of (part, x, y, rotated)."""
    items = []
    for p in parts:
        items += [p] * p['qty']
    items.sort(key=lambda p: (max(p['w'], p['h']), min(p['w'], p['h'])), reverse=True)
    W, H = sheet
    sheets = []
    for p in items:
        placed = False
        for s in sheets:
            if place(s, p, W, H, margin, gap):
                placed = True
                break
        if not placed:
            s = {'shelves': [], 'items': []}
            assert place(s, p, W, H, margin, gap), p['name']
            sheets.append(s)
    return [s['items'] for s in sheets]


def place(s, p, W, H, margin, gap):
    for rot in (False, True):
        w, h = (p['h'], p['w']) if rot else (p['w'], p['h'])
        for sh in s['shelves']:
            if h <= sh['h'] and sh['x'] + w <= W - margin:
                s['items'].append((p, sh['x'], sh['y'], rot)); sh['x'] += w + gap
                return True
        y = margin if not s['shelves'] else s['shelves'][-1]['y'] + s['shelves'][-1]['h'] + gap
        if y + h <= H - margin and margin + w <= W - margin:
            s['shelves'].append({'y': y, 'h': h, 'x': margin + w + gap})
            s['items'].append((p, margin, y, rot))
            return True
    return False


def rotated(p):
    """The same panel turned 90 degrees (for nesting)."""
    w, h = p['w'], p['h']
    def tr(x, y):
        return (h - y, w if x is None else x)
    layers = {}
    for layer, items in p['layers'].items():
        out = []
        for it in items:
            if it[0] == 'poly':
                out.append(('poly', [tr(x, y) for (x, y) in it[1]], it[2]))
            else:
                (cx, cy), r = it[1], it[2]
                out.append(('circle', tr(cx, cy), r))
        layers[layer] = out
    return dict(p, w=h, h=w, layers=layers)


def main():
    os.makedirs(os.path.join(OUT, 'dxf'), exist_ok=True)
    panels = panel_defs()
    layers = gable_layers()
    for p in panels + layers:
        doc = new_doc(); draw(doc.modelspace(), p); doc.saveas(os.path.join(OUT, 'dxf', f"{p['name']}.dxf"))

    # Two speakers' worth, nested.
    pair = [dict(p, qty=p['qty'] * 2) for p in panels + layers]
    sheet = (1525.0, 1525.0)
    sheets = pack(pair, sheet)
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {len(sheets) * 1625} 1525" width="{len(sheets) * 1625 / 4}" height="{1525 / 4}">']
    for i, items in enumerate(sheets):
        doc = new_doc(); msp = doc.modelspace()
        msp.add_lwpolyline([(0, 0), (sheet[0], 0), (sheet[0], sheet[1]), (0, sheet[1])], close=True, dxfattribs={'layer': 'NOTES'})
        ox = i * 1625
        svg.append(f'<rect x="{ox}" y="0" width="1525" height="1525" fill="#efe6d6" stroke="#999" stroke-width="4"/>')
        for (p, x, y, rot) in items:
            q = rotated(p) if rot else p
            draw(msp, q, x, y)
            svg.append(f'<rect x="{ox + x}" y="{1525 - y - q["h"]}" width="{q["w"]}" height="{q["h"]}" fill="#d9bf94" stroke="#6b5232" stroke-width="3"/>')
            svg.append(f'<text x="{ox + x + q["w"] / 2}" y="{1525 - y - q["h"] / 2}" font-size="{min(40, q["h"] / 3)}" text-anchor="middle" font-family="sans-serif">{p["name"]}</text>')
        doc.saveas(os.path.join(OUT, 'dxf', f'sheet-{i + 1}.dxf'))
    svg.append('</svg>')
    open(os.path.join(OUT, 'dxf', 'sheets.svg'), 'w').write('\n'.join(svg))

    with open(os.path.join(OUT, 'cutlist.csv'), 'w', newline='') as f:
        wr = csv.writer(f)
        wr.writerow(['part', 'qty per speaker', 'qty for a pair', 'width mm', 'height mm', 'thickness mm', 'material', 'operations', 'note'])
        for p in panels + layers:
            ops = [k.replace('_', ' ').lower() for k in p['layers'] if p['layers'][k]] or ['outline only']
            wr.writerow([p['name'], p['qty'], p['qty'] * 2, f"{p['w']:.1f}", f"{p['h']:.1f}", f'{WALL:.0f}',
                         'Baltic birch plywood, B/BB, 18 mm', '; '.join(ops), p['note']])
    area = sum(p['w'] * p['h'] * p['qty'] * 2 for p in panels + layers) / 1e6
    print(f'{len(panels)} panel types, {len(layers)} gable layers; pair area {area:.2f} m2 on {len(sheets)} sheets of 1525 x 1525')
    for i, items in enumerate(sheets):
        print(f'  sheet {i + 1}: ' + ', '.join(p['name'] + ('*' if r else '') for (p, x, y, r) in items))


if __name__ == '__main__':
    main()
