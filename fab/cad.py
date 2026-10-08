"""Builds the floorstander as fabrication solids from fab/params.py and writes them to fab/out/.

    /root/.venvs/fab/bin/python fab/cad.py          (or any Python with build123d; see fab/README.md)

Writes:
  out/step/earmilk-floorstander.step   the whole speaker, every part in place (for a CNC shop or any CAD program)
  out/step/<part>.step                 one file per fabricated part, in place
  out/stl/<part>.stl                   the same, for printing or viewing
  out/stl/gable-test-slice*.stl        the bowl test piece (README open question: does the bowl work as a waveguide?)
  out/cad.json                         volumes, masses and the woofer chamber's air, for fab/acoustics.py and the drawings
"""
import json, math, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from params import *  # noqa: F401,F403
import params as P
from build123d import (Align, Box, Cylinder, Edge, Face, Plane, Polygon, Pos, Rot, Solid, Vector, Wire, Compound,
                       export_step, export_stl, extrude, Axis)

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')
MIN = (Align.MIN, Align.MIN, Align.MIN)


def box(x0, y0, z0, x1, y1, z1):
    return Pos(x0, y0, z0) * Box(x1 - x0, y1 - y0, z1 - z0, align=MIN)


def cyl_y(x, z, d, y0, y1):
    """A cylinder along y (front to back) between y0 and y1."""
    return Pos(x, (y0 + y1) / 2, z) * Rot(90, 0, 0) * Cylinder(d / 2, abs(y1 - y0))


def cyl_z(x, y, d, z0, z1):
    return Pos(x, y, (z0 + z1) / 2) * Cylinder(d / 2, z1 - z0)


def rounded_rect_prism(x0, y0, z0, x1, y1, z1, r, axis='z'):
    """A box with its edges parallel to `axis` rounded at radius r (for windows and plates)."""
    b = box(x0, y0, z0, x1, y1, z1)
    ax = {'x': Axis.X, 'y': Axis.Y, 'z': Axis.Z}[axis]
    return b.fillet(r, b.edges().filter_by(ax))


# --- Body panels --------------------------------------------------------------------------------------------------------
def shadow_groove(face, z0=PLINTH_H):
    """The 3 x 3 shadow line on a wall's outer face, cut full length: z 110 to 113 above the plinth, and (2026-10-07) z 857 to
    860 under the gable, where it is a rebate along the wall's top edge that the gable overhangs."""
    z1, d = z0 + SHADOW, SHADOW_DEPTH
    if face == 'front':
        return box(-1, -1, z0, PLAN + 1, d, z1)
    if face == 'back':
        return box(-1, PLAN - d, z0, PLAN + 1, PLAN + 1, z1)
    if face == 'left':
        return box(-1, -1, z0, d, PLAN + 1, z1)
    return box(PLAN - d, -1, z0, PLAN + 1, PLAN + 1, z1)


def outer_corners(p, y_face):
    """2026-10-07: round the panel's two vertical edges on its outer face (the cabinet's corners) at EDGE_R. The front and back
    run the full width, so each corner's round lies wholly in them."""
    edges = [e for e in p.edges().filter_by(Axis.Z) if abs(e.center().Y - y_face) < 0.01 and (e.center().X < 0.01 or e.center().X > PLAN - 0.01)]
    return p.fillet(EDGE_R, edges)


def front_panel():
    p = outer_corners(box(0, 0, 0, PLAN, WALL, BODY), 0)
    p -= cyl_y(RUN, WOOFER['z'], WOOFER_CUTOUT, -1, WALL + 1)
    p -= cyl_y(RUN, MID['z'], MID_CUTOUT, -1, WALL + 1)
    # 2026-10-08, the owner: the drivers flush, each frame and the trim ring over it in a rebate from the outer face
    p -= cyl_y(RUN, WOOFER['z'], WOOFER_REBATE['d'], -1, WOOFER_REBATE['depth'])
    p -= cyl_y(RUN, MID['z'], MID_REBATE['d'], -1, MID_REBATE['depth'])
    p -= shadow_groove('front')
    p -= shadow_groove('front', GABLE_SHADOW_Z0)
    return p


def back_panel():
    p = outer_corners(box(0, PLAN - WALL, 0, PLAN, PLAN, BODY), PLAN)
    p -= cyl_y(RUN, PORT['z'], PORT['bore'] + 2 * PORT_WALL + 0.5, PLAN - WALL - 1, PLAN + 1)   # the tube's 100 OD, a push fit
    tw, th = TERMINAL_CUTOUT
    p -= box(RUN - tw / 2, PLAN - WALL - 1, POSTS['z'] - th / 2, RUN + tw / 2, PLAN + 1, POSTS['z'] + th / 2)
    # 2026-10-07: no plate pocket. The Facts are printed on the finish, under the clear.
    p -= shadow_groove('back')
    p -= shadow_groove('back', GABLE_SHADOW_Z0)
    return p


def side_panel(side):
    x0 = 0 if side == 'left' else PLAN - WALL
    p = box(x0, WALL, 0, x0 + WALL, PLAN - WALL, BODY)
    p -= shadow_groove(side)
    p -= shadow_groove(side, GABLE_SHADOW_Z0)
    return p


def top_panel():
    p = box(WALL, WALL, TOP_Z0, PLAN - WALL, PLAN - WALL, BODY)
    p -= cyl_z(RUN, wire_hole_y(), WIRE_HOLE_D, TOP_Z0 - 1, BODY + 1)
    for (x, y) in dowel_points():
        p -= cyl_z(x, y, DOWEL_D, BODY - 10, BODY + 1)  # 10 deep into the top panel, 20 into the block
    return p


def bottom_panel():
    return box(WALL, WALL, 0, PLAN - WALL, PLAN - WALL, WALL)


def brace_panel():
    p = box(WALL, WALL, BRACE_Z, PLAN - WALL, PLAN - WALL, BRACE_Z + WALL)
    h = BRACE_WINDOW / 2
    p -= rounded_rect_prism(RUN - h, RUN - h, BRACE_Z - 1, RUN + h, RUN + h, BRACE_Z + WALL + 1, BRACE_WINDOW_R, axis='z')
    return p


def mid_shelf():
    y1 = WALL + MID_CHAMBER_DEPTH + WALL
    return box(WALL, WALL, MID_SHELF_TOP - WALL, PLAN - WALL, y1, MID_SHELF_TOP)


def mid_divider():
    y0 = WALL + MID_CHAMBER_DEPTH
    p = box(WALL, y0, MID_SHELF_TOP, PLAN - WALL, y0 + WALL, TOP_Z0)
    p -= cyl_y(RUN - 120, MID_SHELF_TOP + 40, 12, y0 - 1, y0 + WALL + 1)   # the mid's wires, sealed after with putty
    return p


def wire_hole_y():
    return TWEETER['faceplate_y'] + TWEETER['faceplate_t'] + TWEETER['body_depth'] / 2


def dowel_points():
    a, b = 60.0, PLAN - 60.0
    return [(a, 200.0), (b, 200.0), (a, 330.0), (b, 330.0)]


# --- Gable block and bowl -----------------------------------------------------------------------------------------------
def bowl_point(th, t):
    rx, ry, R = BOWL['mouth_w'] / 2, BOWL['mouth_l'] / 2, BOWL['throat'] / 2
    mx, my, mz = slope_point(rx * math.cos(th), BOWL['mouth_s'] + ry * math.sin(th))
    tx, ty, tz = RUN + R * math.cos(th), TWEETER['faceplate_y'], TWEETER['z'] + R * math.sin(th)
    amp = (BOWL['bulge'] + BOWL['bulge'] / 3 * math.sin(th)) * math.sin(math.pi * t)
    rad = (math.cos(th), DY * math.sin(th), DZ * math.sin(th))
    return (mx * (1 - t) + tx * t + rad[0] * amp, my * (1 - t) + ty * t + rad[1] * amp, mz * (1 - t) + tz * t + rad[2] * amp)


def bowl_cavity(n_th=96, n_t=24):
    """The air of the bowl: a loft from the mouth ellipse (in the slope plane) to the throat circle (y = 125 since 2026-10-08),
    the same surface render/src/model.mjs draws, plus a short extrusion of the mouth outward so the cut is clean. Faceted: flat
    strips between 25 polygon sections of 96 points, within 0.05 mm of the surface. Since the throat came forward, the smooth
    loft through 12 spline sections overshot the throat plane by 11 mm where the ceiling meets it at a grazing angle, and a
    ruled loft between splines left a block that no plane could split."""
    wires = []
    for i in range(n_t + 1):
        t = i / n_t
        wires.append(Wire.make_polygon([Vector(*bowl_point(2 * math.pi * k / n_th, t)) for k in range(n_th)], close=True))
    loft = Solid.make_loft(wires, ruled=True)
    mouth = Face(wires[0])
    normal = Vector(0, -DZ, DY)
    ext = extrude(mouth, amount=30, dir=normal)
    return loft + ext


def tweeter_pocket():
    """Placeholder pocket for a 1 in dome with a 62 mm faceplate: a counterbore for the faceplate at the throat, a bore for
    the body, and the wire hole down into the cabinet. Re-cut to the chosen tweeter's drawing."""
    y0 = TWEETER['faceplate_y']
    yf = y0 + TWEETER['faceplate_t']
    yb = yf + TWEETER['body_depth'] + 4
    zc = TWEETER['z']
    fp = cyl_y(RUN, zc, TWEETER['faceplate'] + 2 * CLEAR, y0 - 0.5, yf)
    body = cyl_y(RUN, zc, TWEETER['body_d'] + 2 * CLEAR, yf - 0.5, yb)
    wire = cyl_z(RUN, wire_hole_y(), WIRE_HOLE_D, BODY - 1, zc)
    return fp + body + wire


def gable_block():
    tri = Polygon((0, BODY), (PLAN, BODY), (RUN, RIDGE_Z), align=None)
    prism = extrude(Plane.YZ * tri, amount=PLAN)
    # 2026-10-07: the four hips (where a slope meets an end) rounded at EDGE_R, the fin's top and end edges at FIN_EDGE_R
    hips = [e for e in prism.edges() if (abs(e.center().X) < 0.01 or abs(e.center().X - PLAN) < 0.01) and e.center().Z > BODY + 1]
    prism = prism.fillet(EDGE_R, hips)
    fin = box(0, RUN - FIN_T / 2, RIDGE_Z - 12, PLAN, RUN + FIN_T / 2, TOTAL)
    fin = fin.fillet(FIN_EDGE_R, [e for e in fin.edges() if e.center().Z > RIDGE_Z])
    g = prism + fin
    g -= bowl_cavity()
    g -= tweeter_pocket()
    for (x, y) in dowel_points():
        g -= cyl_z(x, y, DOWEL_D, BODY - 1, BODY + DOWEL_DEPTH)
    return g


# --- Port ----------------------------------------------------------------------------------------------------------------
def port_length_mm():
    if P.PORT_LENGTH:
        return P.PORT_LENGTH
    path = os.path.join(OUT, 'acoustics.json')
    if os.path.exists(path):
        return json.load(open(path))['port']['tube_length_mm']
    return 160.0


def port_tube(length=None):
    """A printed port in two pieces, because neither end could pass through the back's 100 mm hole otherwise:
    the tube (92 bore, 4 mm wall = 100 OD, the spec's port) with the 112 flange, pushed in from outside; and a flare
    collar that slips over the tube's inner end from inside (glued, reached through the woofer hole), its bore
    trumpeting from 92 out on an 18 mm radius. Axial 0 is the back's outer face; inward is negative."""
    tube, flare = port_parts(length)
    return tube + flare


def port_parts(length=None):
    from build123d import Polyline, make_face, revolve
    L = length or port_length_mm()
    bore, w, r, T = PORT['bore'] / 2, PORT_WALL, PORT_FLARE_R, PORT_FLANGE_T
    od, fl = bore + w, PORT['flange'] / 2
    # Tube with flange: a plain revolved rectangle-ish profile.
    tube_prof = make_face(Polyline((bore, T), (fl, T), (fl, 0.0), (od, 0.0), (od, -L), (bore, -L), close=True))
    tube = Pos(RUN, PLAN, PORT['z']) * revolve(Plane.XY * tube_prof, Axis.Y, 360)
    # Flare collar: a socket over the tube's last 15 mm (0.2 mm clearance, 3 mm wall), then the trumpet.
    sock_in, sock_out, sock_len = od + 0.2, od + 0.2 + 3.0, 15.0
    n = 16
    angles = [math.pi / 2 * k / n for k in range(n + 1)]
    c = bore + r
    inner_arc = [(c - r * math.cos(a), -L - r * math.sin(a)) for a in angles]          # bore 92 at -L, out to 128
    outer_arc = [(c - (r - w) * math.cos(a), -L - (r - w) * math.sin(a)) for a in reversed(angles)]
    # The collar is a socket ring and a trumpet, unioned.
    sock = make_face(Polyline((sock_in, -L), (sock_out, -L), (sock_out, -L + sock_len), (sock_in, -L + sock_len), close=True))
    trumpet = make_face(Polyline(*(inner_arc + outer_arc), close=True))
    collar = revolve(Plane.XY * sock, Axis.Y, 360) + revolve(Plane.XY * trumpet, Axis.Y, 360)
    collar = Pos(RUN, PLAN, PORT['z']) * collar
    return tube, collar


# --- The terminal cup on the back ------------------------------------------------------------------------------------------
def terminal_cup():
    """2026-10-08, the owner: a recessed terminal cup in place of the flat plate. Printed (PETG or ASA) and sprayed satin black:
    the 128 x 64 flange 3 thick on the back's face, the body 112 x 48 through the back to its inner face, a 3 mm wall and floor,
    the posts through the floor 18 in from the flange's face, four screws through the flange's corners."""
    C, w, h, z = TERMINAL_CUP, POSTS['w'], POSTS['h'], POSTS['z']
    face = PLAN + C['flange_t']
    cup = rounded_rect_prism(RUN - w / 2, PLAN, z - h / 2, RUN + w / 2, face, z + h / 2, C['flange_r'], axis='y')
    cup += rounded_rect_prism(RUN - C['w'] / 2, face - C['depth'], z - C['h'] / 2, RUN + C['w'] / 2, PLAN + 0.5, z + C['h'] / 2, C['r'], axis='y')
    iw, ih, floor_y = C['w'] - 2 * C['wall'], C['h'] - 2 * C['wall'], face - C['recess']
    cup -= rounded_rect_prism(RUN - iw / 2, floor_y, z - ih / 2, RUN + iw / 2, face + 1, z + ih / 2, C['r'] - C['wall'], axis='y')
    for sx in (-1, 1):
        cup -= cyl_y(RUN + sx * POSTS['spacing'] / 2, z, POST_HOLE, face - C['depth'] - 1, floor_y + 1)
        for sz in (-1, 1):
            cup -= cyl_y(RUN + sx * (w / 2 - 5.5), z + sz * (h / 2 - 5.5), 3.4, PLAN - 1, face + 1)
    return cup


# --- Assembly ------------------------------------------------------------------------------------------------------------
def build():
    parts = {
        'front-baffle': front_panel(),
        'back-panel': back_panel(),
        'side-left': side_panel('left'),
        'side-right': side_panel('right'),
        'top-panel': top_panel(),
        'bottom-panel': bottom_panel(),
        'window-brace': brace_panel(),
        'mid-shelf': mid_shelf(),
        'mid-divider': mid_divider(),
        'gable-block': gable_block(),
        'port-tube': port_tube(),
        'terminal-cup': terminal_cup(),
    }
    return parts


def woofer_air(parts):
    """The woofer chamber's air, from the solids: the inside of the box, less the mid chamber, the internal panels and
    the port tube. Driver displacement and damping are applied in fab/acoustics.py, per candidate driver."""
    inner = box(WALL, WALL, WALL, PLAN - WALL, PLAN - WALL, TOP_Z0)
    mid_ch = box(WALL, WALL, MID_SHELF_TOP, PLAN - WALL, WALL + MID_CHAMBER_DEPTH, TOP_Z0)
    air = inner - mid_ch
    for k in ('window-brace', 'mid-shelf', 'mid-divider', 'port-tube'):
        air -= parts[k]
    return air.volume, mid_ch.volume


def main():
    t0 = time.time()
    os.makedirs(os.path.join(OUT, 'step'), exist_ok=True)
    os.makedirs(os.path.join(OUT, 'stl'), exist_ok=True)
    parts = build()
    report = {'parts': {}, 'units': 'mm, litres, kg'}
    wood = {'front-baffle', 'back-panel', 'side-left', 'side-right', 'top-panel', 'bottom-panel', 'window-brace',
            'mid-shelf', 'mid-divider', 'gable-block'}
    for name, solid in parts.items():
        assert solid.is_valid, name
        if name == 'port-tube':   # exported as its two printed pieces below; the union stays in the assembly
            report['parts'][name] = {'volume_l': round(solid.volume / 1e6, 4)}
            continue
        export_step(solid, os.path.join(OUT, 'step', f'{name}.step'))
        export_stl(solid, os.path.join(OUT, 'stl', f'{name}.stl'), tolerance=0.05 if name == 'gable-block' else 0.1,
                   angular_tolerance=0.1)
        bb = solid.bounding_box()
        rec = {'volume_l': round(solid.volume / 1e6, 4),
               'bbox_mm': [round(v, 2) for v in (bb.min.X, bb.min.Y, bb.min.Z, bb.max.X, bb.max.Y, bb.max.Z)]}
        if name in wood:
            rec['mass_kg'] = round(solid.volume / 1e9 * BIRCH_DENSITY, 2)
        report['parts'][name] = rec
    tube, collar = port_parts()
    for nm, part in (('port-tube-with-flange', tube), ('port-flare-collar', collar)):
        export_stl(part, os.path.join(OUT, 'stl', f'{nm}.stl'), tolerance=0.05, angular_tolerance=0.1)
        export_step(part, os.path.join(OUT, 'step', f'{nm}.step'))
    whole = Compound(label='earmilk floorstander', children=[s for s in parts.values()])
    export_step(whole, os.path.join(OUT, 'step', 'earmilk-floorstander.step'))

    # The bowl test piece: the middle of the block around the bowl, 250 x 240 x 150, which fits a 256 mm printer.
    g = parts['gable-block']
    slice_ = g & box(70, 0, BODY, 320, 240, RIDGE_Z + 1)
    export_stl(slice_, os.path.join(OUT, 'stl', 'gable-test-slice.stl'), tolerance=0.05, angular_tolerance=0.1)
    export_step(slice_, os.path.join(OUT, 'step', 'gable-test-slice.step'))
    lower = slice_ & box(0, -1, BODY - 1, PLAN, PLAN, GABLE_SPLIT_Z)
    upper = slice_ & box(0, -1, GABLE_SPLIT_Z, PLAN, PLAN, TOTAL + 1)
    export_stl(lower, os.path.join(OUT, 'stl', 'gable-test-slice-lower.stl'), tolerance=0.05, angular_tolerance=0.1)
    export_stl(upper, os.path.join(OUT, 'stl', 'gable-test-slice-upper.stl'), tolerance=0.05, angular_tolerance=0.1)
    # The vibe route: the block printed in four pieces that fit a 256 mm printer, split at x = 195 and y = 150, with
    # 3 mm pin holes on the faces that have solid material to spare. Painted like the rest, it looks the same.
    pins_y150 = [(40.0, 885.0), (40.0, 930.0), (350.0, 885.0), (350.0, 930.0)]        # (x, z) on the y = 150 face
    pins_x195 = [(200.0, 975.0), (250.0, 930.0), (300.0, 890.0)]                         # (y, z) on the back pieces' x = 195 face, all under the back slope and clear of the tweeter pocket
    def pin_y(x, z): return cyl_y(x, z, 3.2, 150 - 8, 150 + 8)
    def pin_x(y, z): return Pos(RUN, y, z) * Rot(0, 90, 0) * Cylinder(1.6, 16)
    holes = None
    for (x, z) in pins_y150:
        holes = pin_y(x, z) if holes is None else holes + pin_y(x, z)
    for (y, z) in pins_x195:
        holes = holes + pin_x(y, z)
    gp = g - holes
    quads = {'gable-print-front-left': box(-1, -1, BODY - 1, RUN, 150, TOTAL + 1),
             'gable-print-front-right': box(RUN, -1, BODY - 1, PLAN + 1, 150, TOTAL + 1),
             'gable-print-back-left': box(-1, 150, BODY - 1, RUN, PLAN + 1, TOTAL + 1),
             'gable-print-back-right': box(RUN, 150, BODY - 1, PLAN + 1, PLAN + 1, TOTAL + 1)}
    os.makedirs(os.path.join(OUT, 'stl', 'gable-print'), exist_ok=True)
    for nm, q in quads.items():
        piece = gp & q
        export_stl(piece, os.path.join(OUT, 'stl', 'gable-print', f'{nm}.stl'), tolerance=0.05, angular_tolerance=0.1)
        bb = piece.bounding_box()
        report['parts'][nm] = {'volume_l': round(piece.volume / 1e6, 3),
                               'size_mm': [round(bb.max.X - bb.min.X, 1), round(bb.max.Y - bb.min.Y, 1), round(bb.max.Z - bb.min.Z, 1)]}

    # The block in two halves for 3-axis milling.
    for nm, part in (('gable-block-lower', g & box(-1, -1, BODY - 1, PLAN + 1, PLAN + 1, GABLE_SPLIT_Z)),
                     ('gable-block-upper', g & box(-1, -1, GABLE_SPLIT_Z, PLAN + 1, PLAN + 1, TOTAL + 1))):
        export_step(part, os.path.join(OUT, 'step', f'{nm}.step'))
        report['parts'][nm] = {'volume_l': round(part.volume / 1e6, 4)}

    air, mid_gross = woofer_air(parts)
    cavity = bowl_cavity()
    wood_kg = sum(r.get('mass_kg', 0) for r in report['parts'].values() if 'mass_kg' in r)
    report['woofer_chamber_air_l'] = round(air / 1e6, 3)
    report['woofer_chamber_gross_l'] = round((INNER * INNER * (TOP_Z0 - WALL)) / 1e6, 3)
    report['mid_chamber_gross_l'] = round(mid_gross / 1e6, 3)
    report['bowl_cavity_l'] = round(cavity.volume / 1e6, 4)
    report['wood_mass_kg'] = round(wood_kg, 2)
    report['port_tube_length_mm'] = port_length_mm()
    json.dump(report, open(os.path.join(OUT, 'cad.json'), 'w'), indent=1)
    print(json.dumps({k: v for k, v in report.items() if k != 'parts'}, indent=1))
    print(f'{len(parts)} parts, {time.time() - t0:.1f}s')


if __name__ == '__main__':
    main()
