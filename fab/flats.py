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
  POCKET_<n>MM      n mm deep, from the outer face, clearing inside the circle (2026-10-08: the flush drivers' rebates)
  DRILL_10_DEEP10   10 mm holes, 10 deep (dowels)
  POCKET_<n>MM_UNDERSIDE  n mm deep from the face the file is drawn from: only in <part>-underside.dxf, a second set-up
                    drawn as seen from the underside (the panel turned over left to right)
  REF_HOLES_CUT_FROM_TOP  in an underside file, the through holes already cut, to register on; not cut
  NOTES             part name and face, not cut
"""
import csv, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from params import *  # noqa: F401,F403
import ezdxf
from ezdxf.enums import TextEntityAlignment

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out-bookshelf' if BOOK else 'out')
WOOFER_POCKET = f"POCKET_{WOOFER_REBATE['depth']:g}MM"
MID_POCKET = f"POCKET_{MID_REBATE['depth']:g}MM" if MID else 'POCKET_MID'
PLATE_POCKET = f"POCKET_{AMP['rebate']:g}MM" if AMP else 'POCKET_PLATE'
NUT_POCKET = f"POCKET_{AMP_BOX['nut_cb'][1]:g}MM_UNDERSIDE" if AMP else 'POCKET_NUT'
LAYERS = {'CUT_OUTSIDE': 7, 'CUT_INSIDE': 1, 'POCKET_3MM': 3, WOOFER_POCKET: 4, MID_POCKET: 5, PLATE_POCKET: 2, 'DRILL_D10_DEPTH10': 6,
          'DRILL_D5.5_THROUGH': 30, NUT_POCKET: 40, 'REF_HOLES_CUT_FROM_TOP': 9, 'NOTES': 8}
# what each layer asks of the shop, for the cut list
OPS = {'CUT_INSIDE': 'cut inside', 'POCKET_3MM': 'pocket 3 mm deep', WOOFER_POCKET: f"pocket {WOOFER_REBATE['depth']:g} mm deep (woofer)",
       MID_POCKET: f"pocket {MID_REBATE['depth']:g} mm deep (mid)" if MID else '', PLATE_POCKET: f"pocket {AMP['rebate']:g} mm deep (amplifier plate)" if AMP else '',
       'DRILL_D10_DEPTH10': 'drill ø10, 10 deep', 'DRILL_D5.5_THROUGH': 'drill ø5.5 through (M4 T-nuts from inside; measure the frame first)',
       NUT_POCKET: f"then pocket {AMP_BOX['nut_cb'][1]:g} mm deep from the underside with amp-box-lid-underside.dxf: turn the panel over left to right (its FRONT EDGE still nearest you) and centre each pocket on its hole; before the lid goes in" if AMP else '',
       'REF_HOLES_CUT_FROM_TOP': 'the holes already cut from the top, drawn to register on (not cut)', 'NOTES': 'notes'}


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
    import cad
    wh = cad.wire_hole_y()
    P = []
    front = {'CUT_INSIDE': circle(RUN, WOOFER['z'], WOOFER_CUTOUT) + (circle(RUN, MID['z'], MID_CUTOUT) if MID else []),
             'POCKET_3MM': rect(0, PLINTH_H, PLAN, PLINTH_H + SHADOW) + rect(0, GABLE_SHADOW_Z0, PLAN, BODY)}
    front[WOOFER_POCKET] = front.get(WOOFER_POCKET, []) + circle(RUN, WOOFER['z'], WOOFER_REBATE['d'])
    if MID:
        front[MID_POCKET] = front.get(MID_POCKET, []) + circle(RUN, MID['z'], MID_REBATE['d'])
    # the drivers' screw holes on their bolt circles (DRIVER_SCREWS, PLACEHOLDER until a frame is measured)
    holes = []
    for role, z in [('woofer', WOOFER['z'])] + ([('mid', MID['z'])] if MID else []):
        sc = DRIVER_SCREWS.get(role)
        if sc:
            for k in range(sc['n']):
                a = math.radians(sc['start_deg'] + 360.0 * k / sc['n'])
                holes += circle(RUN + sc['pcd'] / 2 * math.cos(a), z + sc['pcd'] / 2 * math.sin(a), sc['hole'])
    if holes:
        front['DRILL_D5.5_THROUGH'] = holes
    drivers = ', '.join(f'{k} {v}' for k, v in DRIVER_SET.items() if v)
    P.append(dict(name='front-baffle', qty=1, w=PLAN, h=BODY, layers=front,
        note=f'outer face up; round the two vertical outer edges {EDGE_R:g} mm after glue-up; cutouts and rebates sized for {drivers} (flush under trim rings): re-cut for other drivers'))
    back = {'CUT_INSIDE': [], 'POCKET_3MM': rect(0, PLINTH_H, PLAN, PLINTH_H + SHADOW) + rect(0, GABLE_SHADOW_Z0, PLAN, BODY)}
    if PORT:
        back['CUT_INSIDE'] += circle(RUN, PORT['z'], PORT['bore'] + 2 * PORT_WALL + 0.5)
    if AMP:
        back['CUT_INSIDE'] += rrect(RUN - AMP['cut_w'] / 2, AMP['z'] - AMP['cut_h'] / 2, RUN + AMP['cut_w'] / 2, AMP['z'] + AMP['cut_h'] / 2, cad.AMP_CUT_R)
        back[PLATE_POCKET] = rrect(RUN - AMP['plate_w'] / 2 - 0.5, AMP['z'] - AMP['plate_h'] / 2 - 0.5,
                                   RUN + AMP['plate_w'] / 2 + 0.5, AMP['z'] + AMP['plate_h'] / 2 + 0.5, AMP['plate_r'] + 0.5)
        what = (f'the {AMP["model"]}\'s module goes through its {AMP["cut_w"]:g} x {AMP["cut_h"]:g} cutout, its plate on 3 mm EPDM tape '
                f'flush in the {AMP["rebate"]:g} mm rebate; the cut-out\'s corners R{cad.AMP_CUT_R:g} (a 6 mm cutter or smaller); the plate\'s '
                f'screw holes drilled ø3.5 through the {WALL - AMP["rebate"]:g} left under the rebate, from the plate in hand, centred in its flange')
    else:
        tw, th = TERMINAL_CUTOUT
        back['CUT_INSIDE'] += rect(RUN - tw / 2, POSTS['z'] - th / 2, RUN + tw / 2, POSTS['z'] + th / 2)
        what = 'the terminal cup\'s body goes through the 113 x 49 hole'
    facts = 'the Facts are printed on this face after the colour coat, under the clear' if LABEL.get('face', 'back') == 'back' else 'the Facts go on the right side'
    P.append(dict(name='back-panel', qty=1, w=PLAN, h=BODY, layers=back,
        note=f'outer face up (seen from behind); round the two vertical outer edges {EDGE_R:g} mm after glue-up; {what}; {facts}'))
    P.append(dict(name='side', qty=2, w=INNER, h=BODY, layers={'POCKET_3MM': rect(0, PLINTH_H, INNER, PLINTH_H + SHADOW) + rect(0, GABLE_SHADOW_Z0, INNER, BODY)},
                  note='outer face up; finish the groove across the front and back panels\' edges after glue-up' +
                       ('; the Facts are printed on the right side\'s outer face' if LABEL.get('face') == 'right' else '')))
    dowels = cad.dowel_points()
    P.append(dict(name='top-panel', qty=1, w=INNER, h=INNER, layers={
        'CUT_INSIDE': circle(RUN - WALL, wh - WALL, WIRE_HOLE_D),
        'DRILL_D10_DEPTH10': sum((circle(x - WALL, y - WALL, DOWEL_D) for (x, y) in dowels), []),
        # its holes are not symmetric front to back and the panel is square: the front edge marked (d3, round 5)
        'NOTES': [('text', (INNER / 2, 6.0), 'FRONT EDGE', 6.0)]},
        note=f'upper face up, FRONT EDGE to the open front (the ø{WIRE_HOLE_D:g} hole {wh - WALL:g} from it and {INNER - (wh - WALL):g} from the back): '
             'turned round, the channel opens under the insert and the dowels miss the gable; dowels register the gable block; '
             'the tweeter cable\'s hole is sealed with silicone from the bay after wiring'))
    P.append(dict(name='bottom-panel', qty=1, w=INNER, h=INNER, layers={}, note='either face'))
    if BRACE_Z:
        h = BRACE_WINDOW / 2
        P.append(dict(name='window-brace', qty=1, w=INNER, h=INNER, layers={
            'CUT_INSIDE': rrect(INNER / 2 - h, INNER / 2 - h, INNER / 2 + h, INNER / 2 + h, BRACE_WINDOW_R)},
            note=f'sits at z {BRACE_Z:g} to {BRACE_Z + WALL:g}, glued to all four walls'))
    if MID:
        P.append(dict(name='mid-shelf', qty=1, w=INNER, h=MID_CHAMBER_DEPTH + WALL, layers={},
                      note=f'z {MID_SHELF_TOP - WALL:g} to {MID_SHELF_TOP:g}, from the baffle back to under the divider'))
        # an inner panel has no outer face: drawn seen from the front, the mid chamber's side, its face and top edge named
        # (read from the woofer's side the hole moved from x 75 to 315: the drawing check's d12, round 6)
        P.append(dict(name='mid-divider', qty=1, w=INNER, h=TOP_Z0 - MID_SHELF_TOP, layers={
            'CUT_INSIDE': circle(RUN - 120 - WALL, 40, 12),
            'NOTES': [('text', (INNER / 2, TOP_Z0 - MID_SHELF_TOP - 8.0), 'FRONT FACE, TOP EDGE', 6.0)]},
            note=f'seen from the front (the mid chamber\'s side), its top edge up: the hole {RUN - 120 - WALL:g} from its left end; y {WALL + MID_CHAMBER_DEPTH:g} to '
                 f'{2 * WALL + MID_CHAMBER_DEPTH:g}, z {MID_SHELF_TOP:g} to {TOP_Z0:g}; seal the wire hole after wiring'))
    if AMP:
        y0, y1, z0, z1 = cad.amp_box_extent()
        d = y1 - y0 + WALL
        P.append(dict(name='amp-box-floor', qty=1, w=INNER, h=d, layers={}, note=f'the amplifier box\'s floor, z {z0 - WALL:g} to {z0:g}, against the back'))
        gl = cad.amp_glands_xy()
        # the nuts' counterbores are cut from the underside, a second set-up with its own file drawn as seen from there
        # (the panel turned over left to right, the FRONT EDGE still at the bottom), so no one runs them in the top
        # face's coordinates (the drawing check's d5, round 6)
        under = dict(name='amp-box-lid-underside', qty=0, w=INNER, h=d,
                     layers={NUT_POCKET: sum((circle(INNER - (gx - WALL), gy - (y0 - WALL), AMP_BOX['nut_cb'][0]) for (gx, gy) in gl), []),
                             'REF_HOLES_CUT_FROM_TOP': sum((circle(INNER - (gx - WALL), gy - (y0 - WALL), AMP_BOX['gland_hole']) for (gx, gy) in gl), []),
                             'NOTES': [('text', (INNER / 2, 6.0), 'FRONT EDGE', 6.0),
                                       ('text', (INNER / 2, d - 8.0), 'UNDERSIDE: TURNED OVER LEFT TO RIGHT', 5.0)]})
        P.append(dict(name='amp-box-lid', qty=1, w=INNER, h=d, second_side=under,
                      layers={'CUT_INSIDE': sum((circle(gx - WALL, gy - (y0 - WALL), AMP_BOX['gland_hole']) for (gx, gy) in gl), []),
                              'NOTES': [('text', (INNER / 2, 6.0), 'FRONT EDGE', 6.0)]},
                      # short: the glands and their nuts are note 4.7 (4.6 on the bookshelf); a longer one ran into
                      # sheet 6's title block (the drawing check's d16, round 6)
                      note=f'the amplifier box\'s lid, z {z1:g} to {z1 + WALL:g}, its FRONT EDGE over the box\'s front; the glands and their nuts: note {"4.7" if MID else "4.6"}'))
        P.append(dict(name='amp-box-front', qty=1, w=INNER, h=z1 - z0, layers={},
                      note=f'the amplifier box\'s front, between floor and lid, {AMP_BOX["depth"]:g} in front of the back\'s inner face; glue and seal all round'))
    return P


def gable_layers():
    """Rough blanks for gluing up the gable block: 11 layers of 18 mm birch, each a rectangle a little larger than the
    block's footprint at that layer's bottom face, so the CNC has stock to carve. The top two carry only the fin."""
    out = []
    n = int(math.ceil((RISE + FIN_H) / GABLE_LAYER))
    for i in range(n):
        z0 = BODY + i * GABLE_LAYER
        d = depth_at(z0)
        d = max(d, FIN_T) + 8
        out.append(dict(name=f'gable-layer-{i + 1:02d}', qty=1, w=PLAN + 8, h=round(d, 1), layers={},
                        note=f'gable glue-up, layer {i + 1} of {n} (z {z0:.0f} to {z0 + GABLE_LAYER:.0f}); centre on y = {RUN:g}'))
    return out


def draw(msp, part, ox=0.0, oy=0.0, label=True):
    w, h = part['w'], part['h']
    msp.add_lwpolyline([(ox, oy), (ox + w, oy), (ox + w, oy + h), (ox, oy + h)], close=True, dxfattribs={'layer': 'CUT_OUTSIDE'})
    for layer, items in part['layers'].items():
        for it in items:
            if it[0] == 'poly':
                pts = [(ox + (w if x is None else x), oy + y) for (x, y) in it[1]]
                msp.add_lwpolyline(pts, close=it[2], dxfattribs={'layer': layer})
            elif it[0] == 'text':
                (tx, ty), txt, hgt = it[1], it[2], it[3]
                t_ = msp.add_text(txt, height=hgt, dxfattribs={'layer': layer})
                t_.set_placement((ox + tx, oy + ty), align=TextEntityAlignment.MIDDLE_CENTER)
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
            elif it[0] == 'text':
                out.append(('text', tr(*it[1]), it[2], it[3]))
            else:
                (cx, cy), r = it[1], it[2]
                out.append(('circle', tr(cx, cy), r))
        layers[layer] = out
    return dict(p, w=h, h=w, layers=layers)


def main():
    os.makedirs(os.path.join(OUT, 'dxf'), exist_ok=True)
    for f in os.listdir(os.path.join(OUT, 'dxf')):      # every file here is written below: none left from an older build
        if f.endswith('.dxf') or f == 'sheets.svg':
            os.remove(os.path.join(OUT, 'dxf', f))
    panels = panel_defs()
    layers = gable_layers()
    for p in panels + layers:
        doc = new_doc(); draw(doc.modelspace(), p); doc.saveas(os.path.join(OUT, 'dxf', f"{p['name']}.dxf"))
        if p.get('second_side'):
            q = p['second_side']
            doc = new_doc(); draw(doc.modelspace(), q); doc.saveas(os.path.join(OUT, 'dxf', f"{q['name']}.dxf"))

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
            ops = [OPS.get(k, k.replace('_', ' ').lower()) for k in p['layers'] if p['layers'][k] and k != 'NOTES'] or ['outline only']
            if p.get('second_side'):
                ops += [OPS.get(k, k.replace('_', ' ').lower()) for k in p['second_side']['layers']
                        if p['second_side']['layers'][k] and k not in ('NOTES', 'REF_HOLES_CUT_FROM_TOP')]
            wr.writerow([p['name'], p['qty'], p['qty'] * 2, f"{p['w']:.1f}", f"{p['h']:.1f}", f'{WALL:.0f}',
                         f'Baltic birch plywood, B/BB, {WALL:g} mm nominal: measure the sheet first (sheet 7, M1)', '; '.join(ops), p['note']])
    area = sum(p['w'] * p['h'] * p['qty'] * 2 for p in panels + layers) / 1e6
    print(f'{len(panels)} panel types, {len(layers)} gable layers; pair area {area:.2f} m2 on {len(sheets)} sheets of 1525 x 1525')
    for i, items in enumerate(sheets):
        print(f'  sheet {i + 1}: ' + ', '.join(p['name'] + ('*' if r else '') for (p, x, y, r) in items))


if __name__ == '__main__':
    main()
