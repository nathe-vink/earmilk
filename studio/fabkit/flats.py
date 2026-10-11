"""Cut files for every sheet part, read off its solid: no product writes its own DXF.

A sheet part is a prism of its stock's thickness along one axis (model.Sheet). The kit finds that axis, looks at the
part from its outer face, and reads what a CNC router must do from the solid's faces:

- the outline: the outer face's boundary, `CUT_OUTSIDE` (tool outside the line);
- through holes: openings in both faces, `CUT_INSIDE` (tool inside the line); a round one is written as a circle;
- pockets from the outer face: each flat floor between the faces, at its depth, `POCKET_<d>MM` (clear inside);
- pockets from the inner face: the same, in a second file seen from the inner face (`<part>-underside.dxf`, the panel
  turned over left to right), with the through cuts drawn on `REF_THROUGH` to register on;
- any face neither parallel nor square to the sheet (a bevel, a roundover, an angled edge): listed on `NOTES` and in the
  cut list, since a 2D file cannot carry it.

Then every part, times its quantity and the set's count, is nested on its stock's sheets (largest first, turned 90
degrees where the part's grain allows), and the cut list says what each part needs.

    flats.write(product, parts, out_dir)  ->  dxf/<part>.dxf, dxf/<part>-underside.dxf, dxf/nest-<stock>[-<option>]-<n>.dxf,
                                              dxf/nest.svg, cutlist.csv; returns the per-part records
"""
import csv, math, os

import numpy as np

from model import SHEETS, Sheet

TOL = 0.05


def _axis_frame(axis, sign):
    """The 2D frame of a panel seen from outside its outer face: (normal, right, up) as unit vectors."""
    e = np.eye(3)
    n = sign * e[axis]
    d = -n                                          # the viewer looks into the face
    up = e[2] if axis != 2 else (e[1] if sign > 0 else -e[1])
    right = np.cross(d, up)
    return n, right / np.linalg.norm(right), up


def _edge_pts(e, step=1.0):
    if e.geom_type.name == 'LINE':
        ts = [0.0, 1.0]
    else:
        ts = np.linspace(0, 1, int(min(400, max(8, e.length / step))) + 1)
    return [np.array([p.X, p.Y, p.Z]) for p in (e.position_at(t) for t in ts)]


def _wire_poly(w):
    pts = []
    for e in w.order_edges() if hasattr(w, 'order_edges') else w.edges():
        q = _edge_pts(e)
        if pts and np.linalg.norm(pts[-1] - q[0]) > 1e-3 and np.linalg.norm(pts[-1] - q[-1]) < np.linalg.norm(pts[-1] - q[0]):
            q = q[::-1]
        pts += q if not pts else q[1:]
    return np.array(pts)


def _circle(w):
    """A wire that is one full circle: (centre 3D, radius), else None."""
    es = w.edges()
    if len(es) == 1 and es[0].geom_type.name == 'CIRCLE':
        e = es[0]
        try:
            return np.array(tuple(e.arc_center)), e.radius
        except Exception:
            return None
    return None


def analyse(part, centre):
    """The cutting record of one sheet part: its thickness axis, frame, outline, holes, pockets (both sides) and the
    faces a 2D file cannot carry. `centre` is the product's centre, to tell the outer face when the part does not."""
    mk: Sheet = part.make
    T = mk.thickness
    b = part.solid.bounding_box()
    lo = np.array([b.min.X, b.min.Y, b.min.Z]); hi = np.array([b.max.X, b.max.Y, b.max.Z])
    ext = hi - lo
    if mk.face:
        axis = 'xyz'.index(mk.face[1]); sign = 1 if mk.face[0] == '+' else -1
    else:
        cands = [i for i in range(3) if abs(ext[i] - T) < TOL]
        if not cands:
            raise ValueError(f'{part.name}: no extent equals its sheet thickness {T} (extents {ext.round(2).tolist()})')
        axis = min(cands, key=lambda i: abs(ext[i] - T))
        mid = (lo[axis] + hi[axis]) / 2
        sign = 1 if mid >= centre[axis] else -1
    if abs(ext[axis] - T) > TOL:
        raise ValueError(f'{part.name}: {ext[axis]:.2f} thick along {"xyz"[axis]}, its sheet is {T}')
    n, right, up = _axis_frame(axis, sign)
    a_out = hi[axis] if sign > 0 else lo[axis]
    a_in = lo[axis] if sign > 0 else hi[axis]
    rec = dict(name=part.name, axis='xyz'[axis], sign=sign, T=T, outline=None, holes=[], circles=[], pockets={},
               under={}, odd=[], frame=(right.tolist(), up.tolist()))
    outer_open, inner_open, floor_inner, under_outer, under_inner = [], [], [], [], []
    for f in part.solid.faces():
        c = f.center()
        try:
            fn = f.normal_at(c)
        except Exception:
            rec['odd'].append('a face without a normal'); continue
        fn = np.array([fn.X, fn.Y, fn.Z]); a = np.array([c.X, c.Y, c.Z])[axis]
        along = abs(fn[axis])
        if along < 1e-4:
            continue                                           # a wall square to the sheet: the cutter's side
        if f.geom_type.name != 'PLANE' or along < 1 - 1e-4:
            rec['odd'].append(f'{f.geom_type.name.lower()} face at {"xyz"[axis]} {a:.1f}, {math.degrees(math.acos(min(1, along))):.0f} deg off the sheet')
            continue
        outward = np.sign(fn[axis]) == sign
        if abs(a - a_out) < TOL and outward:
            rec['outline'] = _wire_poly(f.outer_wire())
            outer_open += list(f.inner_wires())
        elif abs(a - a_in) < TOL and not outward:
            inner_open += list(f.inner_wires())
            if rec['outline'] is None:
                rec['outline'] = _wire_poly(f.outer_wire())
        elif outward:                                          # a floor seen from the outer face: a pocket
            d = round(abs(a_out - a), 2)
            rec['pockets'].setdefault(d, []).append(_wire_poly(f.outer_wire()))
            floor_inner += list(f.inner_wires())
        else:                                                  # a floor seen from the inner face
            d = round(abs(a - a_in), 2)
            rec['under'].setdefault(d, []).append(_wire_poly(f.outer_wire()))
            under_outer.append(f.outer_wire()); under_inner += list(f.inner_wires())

    cache = {}
    def sig(w):                                            # the opening's box in the sheet's plane: centre, size
        if id(w) not in cache:                             # once a wire: a grille's hundreds of slots meet each other
            P = _wire_poly(w); Q = np.delete(P, axis, axis=1)
            cache[id(w)] = ((Q.min(axis=0) + Q.max(axis=0)) / 2, float(np.ptp(Q, axis=0).sum()))
        return cache[id(w)]
    def table(ws):
        S = [sig(x) for x in ws]
        return np.array([m for m, _ in S]).reshape(-1, 2), np.array([z for _, z in S])
    def matches(w, tab):
        M, Z = tab
        m, s_ = sig(w)
        return bool(len(Z)) and bool(np.any((np.linalg.norm(M - m, axis=1) < 0.3) & (np.abs(Z - s_) < 0.6)))
    t_open, t_under_in, t_under_out = table(outer_open + floor_inner), table(under_inner), table(under_outer)
    through = [w for w in inner_open if matches(w, t_open)]
    t_through = table(through)
    through += [w for w in outer_open if matches(w, t_under_in) and not matches(w, t_through)]
    for w in through:
        circ = _circle(w)
        if circ is not None:
            rec['circles'].append((circ[0], circ[1]))
        else:
            rec['holes'].append(_wire_poly(w))
    stray = [w for w in inner_open if not matches(w, t_open) and not matches(w, t_under_out)]
    if stray:
        rec['odd'].append(f'{len(stray)} opening(s) in the inner face that reach neither face nor a pocket')
    if rec['outline'] is None:
        raise ValueError(f'{part.name}: no outer face found')
    return rec


def to2d(rec, P):
    right, up = (np.array(v) for v in rec['frame'])
    P = np.atleast_2d(P)
    return np.c_[P @ right, P @ up]


def layers(rec):
    """The record as 2D layers, origin at the outline's lower left: {layer: [('poly', pts, closed) | ('circle', c, r)]}."""
    O = to2d(rec, rec['outline'])
    o = O.min(axis=0)
    L = {'CUT_OUTSIDE': [('poly', O - o, True)], 'CUT_INSIDE': [], 'NOTES': []}
    for P in rec['holes']:
        L['CUT_INSIDE'].append(('poly', to2d(rec, P) - o, True))
    for c, r in rec['circles']:
        L['CUT_INSIDE'].append(('circle', to2d(rec, c)[0] - o, r))
    for d, ws in sorted(rec['pockets'].items()):
        L.setdefault(f'POCKET_{d:g}MM', []).extend(('poly', to2d(rec, P) - o, True) for P in ws)
    w, h = np.ptp(O, axis=0)
    return L, float(w), float(h), o


def under_layers(rec, o, w):
    """The inner face's pockets, seen from the inner face (mirrored left to right), with the through cuts to register."""
    if not rec['under']:
        return None
    flip = lambda Q: np.c_[w - Q[:, 0], Q[:, 1]]
    L = {'REF_THROUGH': [], 'NOTES': []}
    for P in rec['holes']:
        L['REF_THROUGH'].append(('poly', flip(to2d(rec, P) - o), True))
    for c, r in rec['circles']:
        L['REF_THROUGH'].append(('circle', flip(to2d(rec, c) - o)[0], r))
    for d, ws in sorted(rec['under'].items()):
        L.setdefault(f'POCKET_{d:g}MM_UNDERSIDE', []).extend(('poly', flip(to2d(rec, P) - o), True) for P in ws)
    return L


COLORS = {'CUT_OUTSIDE': 1, 'CUT_INSIDE': 5, 'REF_THROUGH': 8, 'NOTES': 7}


def _doc():
    import ezdxf
    doc = ezdxf.new('R2010'); doc.units = ezdxf.units.MM
    return doc


def _draw(doc, msp, L, ox=0.0, oy=0.0, rot=False, h=0.0):
    def tr(p):
        x, y = float(p[0]), float(p[1])
        return (ox + (h - y if rot else x), oy + (x if rot else y))
    for name, items in L.items():
        if name not in doc.layers:
            doc.layers.add(name, color=COLORS.get(name, 3 if 'UNDERSIDE' not in name else 6))
        for it in items:
            if it[0] == 'poly':
                msp.add_lwpolyline([tr(p) for p in it[1]], close=it[2], dxfattribs={'layer': name})
            elif it[0] == 'circle':
                msp.add_circle(tr(it[1]), it[2], dxfattribs={'layer': name})
            elif it[0] == 'text':
                msp.add_text(it[2], height=it[3], dxfattribs={'layer': name}).set_placement(tr(it[1]))


def pack(items, sheet, margin=15.0, gap=12.0):
    """Shelf packing, largest first, turned 90 degrees where allowed. items: dicts with w, h, may_turn. Returns sheets,
    each a list of (item, x, y, turned)."""
    W, H = sheet
    order = sorted(items, key=lambda p: (max(p['w'], p['h']), min(p['w'], p['h'])), reverse=True)
    sheets = []
    def place(s, p):
        for rot in ((False, True) if p['may_turn'] else (False,)):
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
    for p in order:
        if not any(place(s, p) for s in sheets):
            s = {'shelves': [], 'items': []}
            if not place(s, p):
                raise ValueError(f"{p['name']} ({p['w']:.0f} x {p['h']:.0f}) does not fit a {W:.0f} x {H:.0f} sheet")
            sheets.append(s)
    return [s['items'] for s in sheets]


def write(product, parts, out):
    """Cut files, nesting and the cut list for every Sheet part. Returns {part name: record} for the drawings and BOM."""
    os.makedirs(os.path.join(out, 'dxf'), exist_ok=True)
    for f in os.listdir(os.path.join(out, 'dxf')):     # a rebuild with fewer or renamed parts leaves no stale files
        if f.endswith('.dxf') or f == 'nest.svg':
            os.remove(os.path.join(out, 'dxf', f))
    allb = [p.solid.bounding_box() for p in parts]
    centre = np.array([(min(b.min.X for b in allb) + max(b.max.X for b in allb)) / 2,
                       (min(b.min.Y for b in allb) + max(b.max.Y for b in allb)) / 2,
                       (min(b.min.Z for b in allb) + max(b.max.Z for b in allb)) / 2])
    recs = {}
    for p in parts:
        if not isinstance(p.make, Sheet):
            continue
        rec = analyse(p, centre)
        L, w, h, o = layers(rec)
        L['NOTES'].append(('text', (2.0, h + 4.0), f'{p.name}  {p.make.thickness:g} mm {p.make.material}, outer face', 6.0))
        for i, s in enumerate(rec['odd'][:6]):
            L['NOTES'].append(('text', (2.0, -8.0 - 7 * i), f'not in this file: {s}', 4.0))
        doc = _doc(); _draw(doc, doc.modelspace(), L); doc.saveas(os.path.join(out, 'dxf', f'{p.name}.dxf'))
        U = under_layers(rec, o, w)
        if U:
            U['NOTES'].append(('text', (2.0, h + 4.0), f'{p.name}  seen from the inner face (turned over left to right)', 6.0))
            doc = _doc(); _draw(doc, doc.modelspace(), U); doc.saveas(os.path.join(out, 'dxf', f'{p.name}-underside.dxf'))
        rec.update(layers=L, under_layers=U, w=w, h=h, origin2d=o.tolist(), part=p)
        recs[p.name] = rec
    # nest per stock (material and thickness), an option's parts on sheets of their own
    stocks = {}
    for name, r in recs.items():
        p = r['part']; key = (p.make.material, p.make.thickness, p.option)
        grain = p.make.grain
        may_turn = grain is None
        for _ in range(p.qty * product.count):
            stocks.setdefault(key, []).append(dict(name=name, w=r['w'], h=r['h'], may_turn=may_turn, layers=r['layers']))
    nests = {}
    svg = []
    for (mat, t, opt), items in stocks.items():
        W, H = SHEETS.get(mat, SHEETS['baltic-birch'])['sheet']
        sheets = pack(items, (W, H))
        stock = f'{mat}-{t:g}' + (f'-{opt}' if opt else '')
        nests[stock] = len(sheets)
        for i, s in enumerate(sheets, 1):
            doc = _doc(); msp = doc.modelspace()
            msp.add_lwpolyline([(0, 0), (W, 0), (W, H), (0, H)], close=True, dxfattribs={'layer': 'SHEET_EDGE'})
            for it, x, y, rot in s:
                _draw(doc, msp, {k: v for k, v in it['layers'].items() if k != 'NOTES'}, x, y, rot, it['h'])
                msp.add_text(it['name'], height=12, dxfattribs={'layer': 'NOTES'}).set_placement((x + 10, y + 10))
            doc.saveas(os.path.join(out, 'dxf', f'nest-{stock}-{i}.dxf'))
            svg.append(((mat, t, i, opt), (W, H), [(it['name'], x, y, (it['h'] if rot else it['w']), (it['w'] if rot else it['h'])) for it, x, y, rot in s]))
    _nest_svg(svg, os.path.join(out, 'dxf', 'nest.svg'))
    with open(os.path.join(out, 'cutlist.csv'), 'w', newline='') as fh:
        wr = csv.writer(fh)
        wr.writerow(['part', 'qty per set', 'width mm', 'height mm', 'thickness mm', 'material', 'through cuts', 'pockets (depth mm)',
                     'underside pockets (depth mm)', 'not in the 2D file'])
        for name, r in recs.items():
            p = r['part']
            wr.writerow([name, p.qty * product.count, f"{r['w']:.1f}", f"{r['h']:.1f}", f'{p.make.thickness:g}', p.make.material,
                         len(r['holes']) + len(r['circles']), ' '.join(f'{d:g}' for d in sorted(r['pockets'])),
                         ' '.join(f'{d:g}' for d in sorted(r['under'])), '; '.join(r['odd'][:3])])
    return recs, nests


def _nest_svg(sheets, path):
    if not sheets:
        return
    k = 0.2
    gap = 20
    Wt = sum(W * k + gap for (_, (W, H), _) in sheets) + gap
    Ht = max(H * k for (_, (W, H), _) in sheets) + 60
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{Wt:.0f}" height="{Ht:.0f}" font-family="sans-serif" font-size="9">']
    x0 = gap
    for (mat, t, i, opt), (W, H), items in sheets:
        out.append(f'<rect x="{x0:.1f}" y="30" width="{W * k:.1f}" height="{H * k:.1f}" fill="#f4efe6" stroke="#333"/>')
        out.append(f'<text x="{x0:.1f}" y="20">{mat} {t:g} mm' + (f' (option: {opt})' if opt else '') + f', sheet {i}</text>')
        for name, x, y, w, h in items:
            out.append(f'<rect x="{x0 + x * k:.1f}" y="{30 + (H - y - h) * k:.1f}" width="{w * k:.1f}" height="{h * k:.1f}" fill="#d9c7a3" stroke="#6b5532"/>')
            out.append(f'<text x="{x0 + (x + 8) * k:.1f}" y="{30 + (H - y - h + 40) * k:.1f}">{name}</text>')
        x0 += W * k + gap
    out.append('</svg>')
    open(path, 'w').write('\n'.join(out))
