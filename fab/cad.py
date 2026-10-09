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

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out-bookshelf' if BOOK else 'out')
NAME = 'earmilk-bookshelf' if BOOK else 'earmilk-floorstander'
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
    if MID: p -= cyl_y(RUN, MID['z'], MID_CUTOUT, -1, WALL + 1)
    # 2026-10-08, the owner: the drivers flush, each frame and the trim ring over it in a rebate from the outer face
    p -= cyl_y(RUN, WOOFER['z'], WOOFER_REBATE['d'], -1, WOOFER_REBATE['depth'])
    if MID: p -= cyl_y(RUN, MID['z'], MID_REBATE['d'], -1, MID_REBATE['depth'])
    p -= shadow_groove('front')
    p -= shadow_groove('front', GABLE_SHADOW_Z0)
    return p


def back_panel():
    p = outer_corners(box(0, PLAN - WALL, 0, PLAN, PLAN, BODY), PLAN)
    if PORT: p -= cyl_y(RUN, PORT['z'], PORT['bore'] + 2 * PORT_WALL + 0.5, PLAN - WALL - 1, PLAN + 1)   # the tube's 100 OD, a push fit
    if AMP:
        # the amplifier: its cutout through the back, and a rebate for its plate so the plate lies level with the finish
        p -= box(RUN - AMP['cut_w'] / 2, PLAN - WALL - 1, AMP['z'] - AMP['cut_h'] / 2, RUN + AMP['cut_w'] / 2, PLAN + 1, AMP['z'] + AMP['cut_h'] / 2)
        p -= rounded_rect_prism(RUN - AMP['plate_w'] / 2 - 0.5, PLAN - AMP['rebate'], AMP['z'] - AMP['plate_h'] / 2 - 0.5,
                                RUN + AMP['plate_w'] / 2 + 0.5, PLAN + 1, AMP['z'] + AMP['plate_h'] / 2 + 0.5, AMP['plate_r'] + 0.5, axis='y')
    else:
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
    if WAVEGUIDE:   # the middle of the connector bay behind the insert's boss
        return INSERT['boss_back_y'] + INSERT['bay_l'] / 2
    return TWEETER['faceplate_y'] + TWEETER['faceplate_t'] + TWEETER['body_depth'] / 2


def dowel_points():
    """The four dowels that register the gable block on the body: the front pair behind the insert's pocket (at y 200
    they stood 5 mm inside the insert's foot, the drawing check's d2), the back pair near the back."""
    r = lambda v: round(v * 2) / 2                       # to 0.5 mm, so the drawings print what the router cuts
    a = r(60.0 * PLAN / 390); b = PLAN - a
    yf = r(INSERT['back_y'] + max(12.0, 15.0 * PLAN / 390) if WAVEGUIDE else 200.0 * PLAN / 390)
    return [(a, yf), (b, yf), (a, r(330.0 * PLAN / 390)), (b, r(330.0 * PLAN / 390))]


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


def waveguide_cavity(sections=None):
    """The waveguide's air (fab/waveguide.py, params.WAVEGUIDE): a ruled loft through its rings, throat to mouth, each a
    polygon round the axis; the last ring lies on the roof, and a short extrusion along the slope's normal makes the cut
    clean. 96 meridians evenly round the axis, one on each crease of the wall, and more wherever neighbouring walls
    differ in length by over 2 mm (Waveguide.phis): there the stations fell at different depths and the ruled quads
    twisted into the teeth a gloss coat showed. EARMILK_WG_SECTIONS sets the even count."""
    from waveguide import Waveguide
    sections = sections or int(os.environ.get('EARMILK_WG_SECTIONS', 96))
    wg = Waveguide(**WAVEGUIDE, sections=sections)
    G, _ = wg.grid(wg.phis())
    wires = [Wire.make_polygon([Vector(*map(float, G[k, i])) for k in range(G.shape[0])], close=True) for i in range(G.shape[1])]
    loft = Solid.make_loft(wires, ruled=True)
    ext = extrude(Face(wires[-1]), amount=30, dir=Vector(0, -DZ, DY))
    return loft + ext


def insert_outline(grow=0.0):
    """The waveguide insert's outline on the roof as (u, s): the mouth (the waveguide's last ring, where its lip meets
    the roof) grown by INSERT['margin'] + grow, and taken down to the eave where it would come within eave_clip of it
    (a strip of block that thin would break off)."""
    from waveguide import Waveguide, slope_coords
    G, _ = Waveguide(**WAVEGUIDE, sections=192).grid()
    pts = [slope_coords(P)[:2] for P in G[:, -1, :]]
    cu = sum(u for u, _ in pts) / len(pts); cs = sum(s for _, s in pts) / len(pts)
    out = []
    n = len(pts)
    for i, (u, s_) in enumerate(pts):
        (u0, s0), (u1, s1) = pts[i - 1], pts[(i + 1) % n]
        tu, ts = u1 - u0, s1 - s0; L = math.hypot(tu, ts)
        nu, ns = ts / L, -tu / L
        if nu * (u - cu) + ns * (s_ - cs) < 0: nu, ns = -nu, -ns
        g = INSERT['margin'] + grow
        uu, ss = u + g * nu, s_ + g * ns
        out.append((uu, 0.0 if ss < INSERT['eave_clip'] else ss))
    return out


def _y_prism(outline, y0, y1, grow_z=0.0):
    """A prism along y (front to back) from y0 to y1 whose section is the outline (u, s) seen from the front: each
    point's x and its height on the roof, so the prism meets the roof exactly on the outline."""
    pts = [Vector(RUN + u, y0, BODY + DZ * s_) for (u, s_) in outline]
    return extrude(Face(Wire.make_polygon(pts, close=True)), amount=y1 - y0, dir=Vector(0, 1, 0))


def gable_prism():
    tri = Polygon((0, BODY), (PLAN, BODY), (RUN, RIDGE_Z), align=None)
    return extrude(Plane.YZ * tri, amount=PLAN)


def insert_fixings():
    """Magnets and pins in the insert's back face (y = back_y), as (x, z): the lower pair inside the outline at 60 % of
    its half-width, a quarter of its height up; the upper pair level with the throat's axis, half-way between the boss
    (its bore in the pocket, plus 3 mm) and 8 mm inside the outline (at 75 % of the height they sat on the boss, the
    drawing check's d5); the pins between them, clear of the tweeter's boss."""
    out = insert_outline()
    zs = [BODY + DZ * s_ for (_, s_) in out]; z0, z1 = min(zs), max(zs)
    def half_width(z):
        xs = [abs(u) for (u, s_) in out if abs(BODY + DZ * s_ - z) < 4.0]
        return min(xs) if xs else 0.0
    mags, pins = [], []
    z = z0 + 0.25 * (z1 - z0); w = 0.6 * half_width(z)
    mags += [(RUN - w, z), (RUN + w, z)]
    zc = WAVEGUIDE['throat_z']
    inner = INSERT['boss_d'] / 2 + INSERT['clear'] + INSERT['magnet_d'] / 2 + 3.0
    outer = half_width(zc) - INSERT['magnet_d'] / 2 - 8.0
    w = (inner + outer) / 2 if outer > inner else inner
    mags += [(RUN - w, zc), (RUN + w, zc)]
    zp = z0 + 0.5 * (z1 - z0) - 6; wp = 0.8 * half_width(zp)
    pins = [(RUN - wp, zp), (RUN + wp, zp)]
    return mags, pins


def waveguide_insert():
    """The insert: the roof inside its outline from the slope back to INSERT['back_y'] (to the top panel near the
    eave), with a boss round the tweeter to boss_back_y; less the waveguide's air, one bore at the tweeter's flange's
    diameter from the boss's back to the throat (the tweeter goes in from behind and seats on the throat's ring), the
    holes for the heat-set inserts its screws go into, and the magnets' and pins' holes in its back face."""
    I, T = INSERT, TWEETER_PART
    y0, zc = WAVEGUIDE['throat_y'], WAVEGUIDE['throat_z']
    ins = _y_prism(insert_outline(), -5.0, I['back_y']) & gable_prism()
    boss = cyl_y(RUN, zc, I['boss_d'], I['back_y'] - 1.0, I['boss_back_y'])
    if zc - I['boss_d'] / 2 < BODY + I['clear']:
        # the boss would reach below the body's top: flattened there, it rests on the top panel (the bookshelf's)
        boss &= box(0, I['back_y'] - 2.0, BODY + I['clear'], PLAN, I['boss_back_y'] + 1.0, RIDGE_Z)
    ins += boss
    ins -= waveguide_cavity()
    # the tweeter goes in from behind: one bore at its flange's diameter from the boss's back to the throat, where the
    # flange seats on the ring round the throat (the dome forward through it) and is screwed to that seat
    ins -= cyl_y(RUN, zc, T['flange_d'] + 0.4, y0, I['boss_back_y'] + 1.0)
    for k in range(T['screws']):
        a = math.radians(45.0 if T['screws'] == 4 else 90.0) + 2 * math.pi * k / T['screws']
        ins -= cyl_y(RUN + T['bolt_circle'] / 2 * math.cos(a), zc + T['bolt_circle'] / 2 * math.sin(a), INSERT_SCREW['hole_d'],
                     y0 - INSERT_SCREW['depth'], y0 + 0.01)
    mags, pins = insert_fixings()
    for (x, z) in mags:
        ins -= cyl_y(x, z, I['magnet_d'] + 0.2, I['back_y'] - I['magnet_t'] - 0.3, I['back_y'] + 1)
    for (x, z) in pins:     # pressed in: 0.1 under the pin
        ins -= cyl_y(x, z, I['pin_d'] - 0.1, I['back_y'] - I['pin_l'] / 2 - 0.5, I['back_y'] + 1)
    return ins


def insert_pocket():
    """The insert's pocket in the gable block: its outline grown by INSERT['clear'] from the slope back to back_y,
    the boss's bore, the connector bay behind it, the magnets' and pins' holes in the pocket's back wall, and the cable
    channel from the bay's floor down through the block to the top panel's hole."""
    I = INSERT
    zc = WAVEGUIDE['throat_z']
    pk = _y_prism(insert_outline(I['clear']), -5.0, I['back_y'] + I['clear'])
    pk += cyl_y(RUN, zc, I['boss_d'] + 2 * I['clear'], I['back_y'], I['boss_back_y'] + 1.0)   # (below the body's top it cuts nothing)
    pk += cyl_y(RUN, zc + I['bay_dz'], I['bay_d'], I['boss_back_y'], I['boss_back_y'] + I['bay_l'])   # the connector bay
    mags, pins = insert_fixings()
    for (x, z) in mags:
        pk += cyl_y(x, z, I['magnet_d'] + 0.2, I['back_y'], I['back_y'] + I['magnet_t'] + 0.3)
    for (x, z) in pins:     # a slip fit: 0.2 over the pin
        pk += cyl_y(x, z, I['pin_d'] + 0.2, I['back_y'], I['back_y'] + I['pin_l'] / 2 + 0.5)
    pk += cyl_z(RUN, wire_hole_y(), WIRE_HOLE_D, BODY - 1, zc + I['bay_dz'])
    return pk


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
    if WAVEGUIDE:
        g -= insert_pocket()
        g -= waveguide_cavity()
    else:
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
    L = L - T                 # the length is from the flange's outer face (axial T), as acoustics.json gives it
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


# --- The amplifier's box ----------------------------------------------------------------------------------------------------
def amp_box_extent():
    """The amplifier box's clear inside, (y0, y1, z0, z1): AMP_BOX['depth'] in front of the back's inner face, the cutout's
    height and a margin above and below."""
    y1 = PLAN - WALL; y0 = y1 - AMP_BOX['depth']
    z0 = AMP['z'] - AMP['cut_h'] / 2 - AMP_BOX['margin']; z1 = AMP['z'] + AMP['cut_h'] / 2 + AMP_BOX['margin']
    return y0, y1, z0, z1


def amp_gland_xy():
    """The gland's centre in the amplifier box's lid, (x, y): 40 in from the right side's inner face, 25 behind the
    box's front panel (43 from the lid's front edge, which is the front panel's)."""
    y0 = amp_box_extent()[0]
    return PLAN - WALL - 40.0, y0 + 25.0


def amp_box_panels():
    """Three 18 mm panels between the sides make the amplifier's sealed box: a floor, a lid and a front. The lid has a
    gland hole for the speaker leads (sealed round them after wiring)."""
    y0, y1, z0, z1 = amp_box_extent()
    floor = box(WALL, y0 - WALL, z0 - WALL, PLAN - WALL, y1, z0)
    lid = box(WALL, y0 - WALL, z1, PLAN - WALL, y1, z1 + WALL)
    gx, gy = amp_gland_xy()
    lid -= cyl_z(gx, gy, AMP_BOX['gland_d'] + 0.5, z1 - 1, z1 + WALL + 1)
    front = box(WALL, y0 - WALL, z0, PLAN - WALL, y0, z1)
    return {'amp-box-floor': floor, 'amp-box-lid': lid, 'amp-box-front': front}


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
        'gable-block': gable_block(),
        'waveguide-insert': waveguide_insert(),
    }
    if BRACE_Z:
        parts['window-brace'] = brace_panel()
    if MID:
        parts['mid-shelf'] = mid_shelf(); parts['mid-divider'] = mid_divider()
    if PORT:
        parts['port-tube'] = port_tube()
    if AMP:
        parts.update(amp_box_panels())
    else:
        parts['terminal-cup'] = terminal_cup()
    return parts


def woofer_air(parts):
    """The woofer chamber's air, from the solids: the inside of the box, less the mid chamber, the internal panels and
    the port tube. Driver displacement and damping are applied in fab/acoustics.py, per candidate driver."""
    inner = box(WALL, WALL, WALL, PLAN - WALL, PLAN - WALL, TOP_Z0)
    air = inner
    mid_vol = 0.0
    if MID:
        mid_ch = box(WALL, WALL, MID_SHELF_TOP, PLAN - WALL, WALL + MID_CHAMBER_DEPTH, TOP_Z0)
        air = inner - mid_ch; mid_vol = mid_ch.volume
    for k in ('window-brace', 'mid-shelf', 'mid-divider', 'port-tube'):
        if k in parts:
            air -= parts[k]
    if AMP:
        # the amplifier's sealed box and everything inside it is not the woofer's air
        y0, y1, z0, z1 = amp_box_extent()
        air -= box(WALL, y0 - WALL, z0 - WALL, PLAN - WALL, y1, z1 + WALL)
    return air.volume, mid_vol


def features():
    """The numbers the drawings carry, from the CAD's own sources, so a sheet can be checked against them: cut-outs,
    rebates, bores and the centres of the dowels, fixings, channel and gland (mm, the CAD's frame)."""
    f = {'woofer': {'cutout_d': WOOFER_CUTOUT, 'rebate_d': WOOFER_REBATE['d'], 'rebate_depth': WOOFER_REBATE['depth'], 'z': WOOFER['z'],
                    'screws': DRIVER_SCREWS.get('woofer')},
         'dowels': [[round(x, 2), round(y, 2)] for (x, y) in dowel_points()], 'dowel': {'d': DOWEL_D, 'depth_top_panel': 10.0, 'depth_block': DOWEL_DEPTH}}
    if MID:
        f['mid'] = {'cutout_d': MID_CUTOUT, 'rebate_d': MID_REBATE['d'], 'rebate_depth': MID_REBATE['depth'], 'z': MID['z'], 'screws': DRIVER_SCREWS.get('mid')}
    if WAVEGUIDE:
        I, T = INSERT, TWEETER_PART
        mags, pins = insert_fixings()
        f['waveguide'] = {'throat_y': WAVEGUIDE['throat_y'], 'throat_z': WAVEGUIDE['throat_z'], 'throat_d': 2 * WAVEGUIDE['r0']}
        f['insert'] = {'back_y': I['back_y'], 'boss_d': I['boss_d'], 'boss_back_y': I['boss_back_y'], 'clear': I['clear'],
                       'tweeter_bore_d': T['flange_d'] + 0.4, 'tweeter_bore_from_y': WAVEGUIDE['throat_y'], 'tweeter_bore_to_y': I['boss_back_y'],
                       'tweeter_screws': {'n': T['screws'], 'pcd': T['bolt_circle'], **INSERT_SCREW},
                       'magnets': [[round(x - RUN, 2), round(z, 2)] for (x, z) in mags], 'magnet_hole': [I['magnet_d'] + 0.2, I['magnet_t'] + 0.3],
                       'pins': [[round(x - RUN, 2), round(z, 2)] for (x, z) in pins], 'pin_hole_insert': I['pin_d'] - 0.1,
                       'pin_hole_pocket': I['pin_d'] + 0.2, 'bay_d': I['bay_d'], 'bay_l': I['bay_l'], 'bay_z': WAVEGUIDE['throat_z'] + I['bay_dz'],
                       'channel': {'x': RUN, 'y': round(wire_hole_y(), 2), 'd': WIRE_HOLE_D}}
    if AMP:
        y0, y1, z0, z1 = amp_box_extent(); gx, gy = amp_gland_xy()
        f['amp'] = {'cutout': [AMP['cut_w'], AMP['cut_h']], 'rebate': [AMP['plate_w'] + 1, AMP['plate_h'] + 1, AMP['rebate']], 'z': AMP['z'],
                    'box_inside': {'y': [y0, y1], 'z': [z0, z1]}, 'gland': {'x': gx, 'y': gy, 'hole_d': AMP_BOX['gland_d'] + 0.5}}
    if PORT:
        L = port_length_mm()
        f['port'] = {'z': PORT['z'], 'bore': PORT['bore'], 'od': PORT['bore'] + 2 * PORT_WALL, 'hole_d': PORT['bore'] + 2 * PORT_WALL + 0.5,
                     'flange_d': PORT['flange'], 'flange_t': PORT_FLANGE_T, 'tube_from_flange_face': L, 'collar': PORT_FLARE_R, 'overall': L + PORT_FLARE_R}
    return f


def checks(parts):
    """Clearances that the parameters alone do not guarantee, measured on the solids where they can be: each a name, the
    measured margin in mm and the least it may be. A failure stops the build, the way a failing test would."""
    out = []
    def chk(name, margin, least):
        out.append({'check': name, 'margin_mm': round(margin, 2), 'least_mm': least, 'ok': margin >= least})
    tan_ = RISE / RUN
    if WAVEGUIDE:
        I, T = INSERT, TWEETER_PART
        zc = WAVEGUIDE['throat_z']
        bb = parts['waveguide-insert'].bounding_box()
        chk('insert above the top panel (its lowest point to the body\'s top)', bb.min.Z - BODY, -0.01)
        chk('insert material under the tweeter\'s counterbore', zc - (T['flange_d'] + 0.4) / 2 - BODY, 1.5)
        chk('insert material under the tweeter\'s bore, above the top panel', zc - (T['flange_d'] + 0.4) / 2 - (BODY + I['clear']), 1.2)
        pocket = insert_pocket()
        for (x, y) in dowel_points()[:2]:
            chk(f'front dowel at y {y:g} clear of the insert\'s pocket', cyl_z(x, y, DOWEL_D, BODY - 1, BODY + DOWEL_DEPTH).distance_to(pocket), 3.0)
        mags, pins = insert_fixings()
        bore_r = I['boss_d'] / 2 + I['clear']
        for (x, z) in mags + pins:
            d_ = (I['magnet_d'] if (x, z) in mags else I['pin_d']) / 2
            chk(f'magnet or pin at ({x - RUN:+.1f}, {z:g}) clear of the boss\'s bore', math.hypot(x - RUN, z - zc) - d_ - bore_r, 3.0)
        yb = I['boss_back_y'] + I['bay_l']; zt = zc + I['bay_dz'] + I['bay_d'] / 2
        roof = RIDGE_Z - (yb - RUN) * tan_ if yb > RUN else BODY + yb * tan_
        chk('birch over the connector bay, under the back slope (vertical)', roof - zt, 8.0)
        chk('connector bay above the top panel', zc + I['bay_dz'] - I['bay_d'] / 2 - BODY, 4.0)
    bot_front = PLINTH_H + SHADOW
    w = WOOFER['z'] - WOOFER_REBATE['d'] / 2
    chk('woofer rebate above the plinth\'s shadow line', w - bot_front, 5.0)
    top_w = WOOFER['z'] + WOOFER_REBATE['d'] / 2
    if MID:
        chk('mid rebate above the woofer rebate', MID['z'] - MID_REBATE['d'] / 2 - top_w, 10.0)
        chk('mid rebate below the gable\'s shadow line', GABLE_SHADOW_Z0 - (MID['z'] + MID_REBATE['d'] / 2), 5.0)
        chk('mid rebate below the mid shelf\'s top (inside its chamber)', MID['z'] - MID_REBATE['d'] / 2 - MID_SHELF_TOP, 5.0)
    else:
        chk('woofer rebate below the gable\'s shadow line', GABLE_SHADOW_Z0 - top_w, 5.0)
    if AMP:
        chk('amplifier plate above the plinth\'s shadow line', AMP['z'] - AMP['plate_h'] / 2 - bot_front, 2.0)
        chk('amplifier plate inside the back, across', (PLAN - AMP['plate_w']) / 2 - EDGE_R, 2.0)
        y0, y1, z0, z1 = amp_box_extent()
        chk('amplifier box above the bottom panel', z0 - WALL - WALL, 0.0)
        if PORT:
            chk('port clear of the amplifier box\'s lid', PORT['z'] - (PORT['bore'] + 2 * PORT_WALL) / 2 - (z1 + WALL), 5.0)
        if BRACE_Z:
            chk('amplifier box below the brace', BRACE_Z - (z1 + WALL), 0.0)
    bad = [c for c in out if not c['ok']]
    for c in out:
        print(f"  {'ok  ' if c['ok'] else 'FAIL'} {c['check']}: {c['margin_mm']} mm (least {c['least_mm']})")
    if bad:
        raise SystemExit(f'{len(bad)} clearance check(s) failed: ' + '; '.join(c['check'] for c in bad))
    return out


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
    if PORT:
        tube, collar = port_parts()
        for nm, part in (('port-tube-with-flange', tube), ('port-flare-collar', collar)):
            export_stl(part, os.path.join(OUT, 'stl', f'{nm}.stl'), tolerance=0.05, angular_tolerance=0.1)
            export_step(part, os.path.join(OUT, 'step', f'{nm}.step'))
    whole = Compound(label=NAME, children=[s for s in parts.values()])
    export_step(whole, os.path.join(OUT, 'step', f'{NAME}.step'))
    # the trim rings for printing, each with a channel in its back over its frame's screw heads
    import components as C
    rings = [('woofer', WOOFER_REBATE)] + ([('mid', MID_REBATE)] if MID else [])
    for role, rb in rings:
        sp = C.DRIVERS[DRIVER_SET[role]]; _, info = C.cone_driver(sp, 4)
        r_out = (rb['d'] - 1.6) / 2; r_in = max(info['r_surround'] + 1.0, r_out - C.RING['width'])
        sc = DRIVER_SCREWS.get(role)
        ring = C.trim_ring(r_in, r_out, groove=(sc['pcd'] / 2, 10.0, 2.0) if sc else None)
        export_stl(ring, os.path.join(OUT, 'stl', f'trim-ring-{role}.stl'), tolerance=0.05, angular_tolerance=0.1)
        report['parts'][f'trim-ring-{role}'] = {'od_mm': round(2 * r_out, 1), 'id_mm': round(2 * r_in, 1), 't_mm': C.RING['t'],
                                                'groove': f'10 wide, 2 deep on ø{sc["pcd"]:g}' if sc else None}
    # a part this size has not got leaves no file behind (the bookshelf's brace)
    for stale in ([] if BRACE_Z else ['window-brace']) + ([] if MID else ['mid-shelf', 'mid-divider']):
        for f in (os.path.join(OUT, 'stl', f'{stale}.stl'), os.path.join(OUT, 'step', f'{stale}.step')):
            if os.path.exists(f):
                os.remove(f)

    # The waveguide insert for printing (SLA or MJF, or FDM finely) or CNC from solid: whole, and halved at the centre
    # plane with two 3 mm pin holes when it is wider than a 256 mm printer.
    ins = parts['waveguide-insert']
    export_stl(ins, os.path.join(OUT, 'stl', 'waveguide-insert.stl'), tolerance=0.02, angular_tolerance=0.05)
    bb = ins.bounding_box()
    if bb.max.X - bb.min.X > 250:
        zp = WAVEGUIDE['throat_z'] - TWEETER_PART['flange_d'] / 2 - 12
        pins = Pos(RUN, INSERT['back_y'] - 25, zp) * Rot(0, 90, 0) * Cylinder(1.6, 16)
        pins += Pos(RUN, 25, BODY + 15) * Rot(0, 90, 0) * Cylinder(1.6, 16)
        for nm, half in (('waveguide-insert-left', ins & box(-1, -10, BODY - 1, RUN, PLAN, TOTAL)),
                         ('waveguide-insert-right', ins & box(RUN, -10, BODY - 1, PLAN + 1, PLAN, TOTAL))):
            export_stl(half - pins, os.path.join(OUT, 'stl', f'{nm}.stl'), tolerance=0.02, angular_tolerance=0.05)
    # The gable block for printing (the cheap route): the floorstander's in four pieces for a 256 mm printer, the
    # bookshelf's whole. Painted like the rest, it looks the same.
    g = parts['gable-block']
    os.makedirs(os.path.join(OUT, 'stl', 'gable-print'), exist_ok=True)
    if PLAN > 256:
        ys = 150.0
        quads = {'gable-print-front-left': box(-1, -1, BODY - 1, RUN, ys, TOTAL + 1),
                 'gable-print-front-right': box(RUN, -1, BODY - 1, PLAN + 1, ys, TOTAL + 1),
                 'gable-print-back-left': box(-1, ys, BODY - 1, RUN, PLAN + 1, TOTAL + 1),
                 'gable-print-back-right': box(RUN, ys, BODY - 1, PLAN + 1, PLAN + 1, TOTAL + 1)}
        for nm, q in quads.items():
            piece = g & q
            export_stl(piece, os.path.join(OUT, 'stl', 'gable-print', f'{nm}.stl'), tolerance=0.05, angular_tolerance=0.1)
            bb = piece.bounding_box()
            report['parts'][nm] = {'volume_l': round(piece.volume / 1e6, 3),
                                   'size_mm': [round(bb.max.X - bb.min.X, 1), round(bb.max.Y - bb.min.Y, 1), round(bb.max.Z - bb.min.Z, 1)]}
    else:
        export_stl(g, os.path.join(OUT, 'stl', 'gable-print', 'gable-print-whole.stl'), tolerance=0.05, angular_tolerance=0.1)

    air, mid_gross = woofer_air(parts)
    cavity = waveguide_cavity() if WAVEGUIDE else bowl_cavity()
    wood_kg = sum(r.get('mass_kg', 0) for r in report['parts'].values() if 'mass_kg' in r)
    report['woofer_chamber_air_l'] = round(air / 1e6, 3)
    report['woofer_chamber_gross_l'] = round((INNER * INNER * (TOP_Z0 - WALL)) / 1e6, 3)
    report['mid_chamber_gross_l'] = round(mid_gross / 1e6, 3)
    report['waveguide_air_l'] = round(cavity.volume / 1e6, 4)
    report['wood_mass_kg'] = round(wood_kg, 2)
    report['port_tube_length_mm'] = port_length_mm() if PORT else None
    report['size'] = SIZE
    report['features'] = features()
    report['checks'] = checks(parts)
    json.dump(report, open(os.path.join(OUT, 'cad.json'), 'w'), indent=1)
    print(json.dumps({k: v for k, v in report.items() if k != 'parts'}, indent=1))
    print(f'{len(parts)} parts, {time.time() - t0:.1f}s')


if __name__ == '__main__':
    main()
