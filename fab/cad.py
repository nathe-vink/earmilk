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


def cyl_x(y, z, d, x0, x1):
    """A cylinder along x (side to side) between x0 and x1."""
    return Pos((x0 + x1) / 2, y, z) * Rot(0, 90, 0) * Cylinder(d / 2, abs(x1 - x0))


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


AMP_CUT_R = 3.0      # the amplifier's cut-out's corner radius in the back (a 6 mm cutter or smaller)


def back_panel():
    p = outer_corners(box(0, PLAN - WALL, 0, PLAN, PLAN, BODY), PLAN)
    if PORT: p -= cyl_y(RUN, PORT['z'], PORT['bore'] + 2 * PORT_WALL + 0.5, PLAN - WALL - 1, PLAN + 1)   # the tube's 100 OD, a push fit
    if AMP:
        # the amplifier: its cutout through the back, and a rebate for its plate so the plate lies level with the finish
        p -= rounded_rect_prism(RUN - AMP['cut_w'] / 2, PLAN - WALL - 1, AMP['z'] - AMP['cut_h'] / 2, RUN + AMP['cut_w'] / 2, PLAN + 1,
                                AMP['z'] + AMP['cut_h'] / 2, AMP_CUT_R, axis='y')     # R3 corners: a 6 mm cutter (d18, round 3)
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
    p = box(WALL, y0, MID_SHELF_TOP, PLAN - WALL, y0 + WALL, TOP_Z0 - DIVIDER_SHORT)   # short of the top panel (G4, G6)
    p -= cyl_y(RUN - 120, MID_SHELF_TOP + 40, 12, y0 - 1, y0 + WALL + 1)   # the mid's wires, sealed after with putty
    return p


def wire_hole_y():
    if WAVEGUIDE:   # the middle of the connector bay behind the insert's boss
        return INSERT['boss_back_y'] + INSERT['bay_l'] / 2
    return TWEETER['faceplate_y'] + TWEETER['faceplate_t'] + TWEETER['body_depth'] / 2


def connector_z():
    """The mated connector's centre: standing in the bay on its floor, clear of the channel below, whose top 20 mm the
    silicone fills (drawn in the channel's mouth it sat where the seal goes: the drawing check's d12, round 3)."""
    return WAVEGUIDE['throat_z'] + INSERT['bay_dz'] - INSERT['bay_d'] / 2 + 1.0 + CONNECTOR['mated_l'] / 2


def dowel_points():
    """The four dowels that register the gable block on the body: the front pair behind the insert's pocket (at y 200
    they stood 5 mm inside the insert's foot, the drawing check's d2), the back pair near the back."""
    r = lambda v: round(v * 2) / 2                       # to 0.5 mm, so the drawings print what the router cuts
    a = r(60.0 * PLAN / 390); b = PLAN - a
    yf = r(INSERT['back_y'] + max(12.0, 15.0 * PLAN / 390) if WAVEGUIDE else 200.0 * PLAN / 390)
    # the back pair 8 mm of block under the back slope, normal to it: the bookshelf's at 186 kept 1.8 (d7, round 6)
    t_, c_ = math.tan(math.radians(SLOPE_DEG)), math.cos(math.radians(SLOPE_DEG))
    yr = math.floor(2 * min(330.0 * PLAN / 390, PLAN - DOWEL_D / 2 - (DOWEL_DEPTH + 8.0 / c_) / t_)) / 2    # to 0.5, forward
    return [(a, yf), (b, yf), (a, yr), (b, yr)]


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
    return _hold_boss(out, grow)


BOSS_COVER = 0.5     # the insert's outline at least this far outside the boss's circle, seen from the front


def _hold_boss(out, grow=0.0):
    """The outline grown, above the throat's axis, to hold the boss's circle (+ BOSS_COVER + grow): the boss stands behind
    the insert's back face, and the insert slides in from the front, so seen from the front the boss has to pass under the
    pocket's ceiling, which is this outline + clear. The bookshelf's 68.4 boss stood 2.4 above its outline and jammed (the
    drawing check's d1, round 3); there the seam on the roof moves up about 3 mm at the top. Each point above the axis
    within the circle is pushed out to it along the ray from the axis (the outline is star-shaped about the throat)."""
    zc_ = WAVEGUIDE['throat_z'] - BODY
    R = INSERT['boss_d'] / 2 + BOSS_COVER + grow
    res = []
    for (u, s_) in out:
        dz = DZ * s_ - zc_
        r = math.hypot(u, dz)
        if dz > 0 and 1e-9 < r < R:
            u, dz = u * R / r, dz * R / r
            s_ = (zc_ + dz) / DZ
        res.append((u, s_))
    return res


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
    # down until 2.5 of material stands between a pin's hole and every magnet's (the bookshelf's sat 1.0 from its upper
    # magnet: the drawing check's d14, round 4)
    r_need = (INSERT['pin_d'] + 0.2) / 2 + (INSERT['magnet_d'] + 0.2) / 2 + 2.5
    while min(math.hypot(wp - abs(mx - RUN), zp - mz) for (mx, mz) in mags) < r_need and zp > z0 + 6:
        zp -= 0.5
    pins = [(RUN - wp, zp), (RUN + wp, zp)]
    return mags, pins


def waveguide_insert():
    """The insert: the roof inside its outline from the slope back to INSERT['back_y'] (to the top panel near the
    eave), with a boss round the tweeter to boss_back_y; less the waveguide's air, one bore at the tweeter's flange's
    diameter from the boss's back to the throat (the tweeter goes in from behind and seats on the throat's ring), the
    holes that hold it (the retaining sleeve's pilots in the boss's back face, or the bookshelf's faceplate screws'
    inserts in the seat), the magnets' and pins' holes in its back face, and a groove under its front edge for a pull
    loop (the drawing check's d15)."""
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
    if RETAINER:            # the sleeve's three screws go into pilots in the boss's wall, outside the bore
        for (x, z) in retainer_screw_points():
            ins -= cyl_y(x, z, RETAINER['pilot_d'], I['boss_back_y'] - RETAINER['pilot_depth'], I['boss_back_y'] + 0.01)
    else:                   # the faceplate's screws, from behind through its own holes, into inserts in the seat
        for (x, z) in seat_screw_points():
            ins -= cyl_y(x, z, INSERT_SCREW['hole_d'], y0 - INSERT_SCREW['depth'], y0 + 0.01)
    mags, pins = insert_fixings()
    for (x, z) in mags:
        ins -= cyl_y(x, z, I['magnet_d'] + 0.2, I['back_y'] - I['magnet_t'] - 0.3, I['back_y'] + 1)
    for (x, z) in pins:     # bonded with epoxy, 0.1 over the pin (a 0.1 press fit is inside a print's tolerance: d9)
        ins -= cyl_y(x, z, I['pin_d'] + 0.1, I['back_y'] - I['pin_l'] / 2 - 0.5, I['back_y'] + 1)
    bb = ins.bounding_box()  # the pull loop's groove: 12 wide, 1.5 deep, 30 back from the front edge of its base
    ins -= box(RUN - PULL_GROOVE[0] / 2, bb.min.Y - 1.0, bb.min.Z - 1.0, RUN + PULL_GROOVE[0] / 2, bb.min.Y + PULL_GROOVE[2], bb.min.Z + PULL_GROOVE[1])
    return ins


PULL_GROOVE = (12.0, 1.5, 30.0)     # width, depth, length back from the front edge: a ribbon loop glued in it


def pull_loop():
    """The ribbon pull loop (the BOM's 10 mm grosgrain), for the render model: folded double and tucked into the groove
    under the insert's front edge, its ends glued at the back of the groove, so the front edge shows the ribbon in the
    groove rather than the front panel's white top edge through an empty notch (critic rounds 9 and 10 on shot 03 read
    the empty groove as a modelling error, the brightest thing in the frame)."""
    plain = _y_prism(insert_outline(), -5.0, INSERT['back_y']) & gable_prism()
    bb = plain.bounding_box()
    w = PULL_GROOVE[0] - 2.0
    return box(RUN - w / 2, bb.min.Y + 0.3, bb.min.Z + 0.15, RUN + w / 2, bb.min.Y + PULL_GROOVE[2] - 2.0, bb.min.Z + PULL_GROOVE[1] - 0.1)


def insert_split_pins():
    """Where the two 3 x 16 pins cross the insert's split at the centre plane when it is printed in halves, as (y, z): one
    under the tweeter's bore, one over it, between the bore and the insert's top (the drawing check's d13, round 3)."""
    zc = WAVEGUIDE['throat_z']; bore_r = (TWEETER_PART['flange_d'] + 0.4) / 2
    top = max(DZ * s_ + BODY for (u, s_) in insert_outline() if abs(u) < 3.0)
    return [(INSERT['back_y'] - 25, zc - bore_r - 12), (INSERT['back_y'] - 10, (zc + bore_r + top) / 2)]


def insert_printed_in_halves():
    """The insert is wider than a 250 mm print bed (the floorstander's): then it is printed in halves at the centre plane."""
    out = insert_outline()
    return max(u for u, _ in out) - min(u for u, _ in out) > 250


def seat_screw_points():
    """The bookshelf's faceplate screws on its bolt circle in the seat round the throat, as (x, z)."""
    T = TWEETER_PART; zc = WAVEGUIDE['throat_z']
    a0 = math.radians(45.0 if T['screws'] == 4 else 90.0)
    return [(RUN + T['bolt_circle'] / 2 * math.cos(a0 + 2 * math.pi * k / T['screws']),
             zc + T['bolt_circle'] / 2 * math.sin(a0 + 2 * math.pi * k / T['screws'])) for k in range(T['screws'])]


def retainer_screw_points():
    """The retaining sleeve's screws on its circle in the boss's back face, as (x, z): one on the horizontal at the speaker's
    right, two at 120 degrees from it (the connector bay behind the boss is inside the circle). Not one at the top: that
    one drove into the insert's split at the centre plane, where its halves are glued (the drawing check's d5, round 3)."""
    R, zc = RETAINER, WAVEGUIDE['throat_z']
    a0 = R.get('start_deg', 0.0)
    return [(RUN + R['screw_circle'] / 2 * math.cos(math.radians(a0 + 120 * k)),
             zc + R['screw_circle'] / 2 * math.sin(math.radians(a0 + 120 * k))) for k in range(R['screws'])]


def retainer_y():
    """The retainer's front face and the boss's back face: a sleeve's on the tweeter's front ring (behind its gasket), a
    cap's on the motor's back face, `preload` further forward so the screws press the gasket by that much."""
    T = TWEETER_PART
    yf = WAVEGUIDE['throat_y'] + RETAINER['gasket'] + T['flange_t']
    if RETAINER.get('mode') == 'cap':
        yf += T['body_depth']
    return yf - RETAINER.get('preload', 0.0), INSERT['boss_back_y']


def retainer_rings():
    """(outside, inside) diameters of the retainer's tube: in the bore, round the motor (a sleeve) or open in its middle
    for the tabs and the lead, bearing on the motor's back rim (a cap)."""
    R, T = RETAINER, TWEETER_PART
    od = T['flange_d'] + 0.4 - 2 * R['fit']
    idd = (T['body_d'] - 2 * R.get('rim', 6.0)) if R.get('mode') == 'cap' else (T['body_d'] + 2 * R['clear'])
    return od, idd


def tweeter_retainer():
    """The floorstander's printed retainer: a tube in the bore from its bearing face to the boss's back face, and a
    flange there with three holes for its screws. A cap (RETAINER mode 'cap', the default since round 7) bears on the
    motor's back rim; a sleeve (the drawing check's d1, round 2) slides over the motor onto the front ring. Screwed home
    either presses the front ring onto its gasket on the throat's seat; both follow TWEETER_PART when it is measured."""
    R, T, zc = RETAINER, TWEETER_PART, WAVEGUIDE['throat_z']
    yf, yb = retainer_y()                # preload included: the tube a little longer than its gap (d5, round 5)
    od, idd = retainer_rings()
    sl = cyl_y(RUN, zc, od, yf, yb) + cyl_y(RUN, zc, R['flange_d'], yb, yb + R['flange_t'])
    sl -= cyl_y(RUN, zc, idd, yf - 1, yb + R['flange_t'] + 1)
    for (x, z) in retainer_screw_points():
        sl -= cyl_y(x, z, R['hole_d'], yb - 1, yb + R['flange_t'] + 1)
    return sl


def pocket_bore_behind_boss():
    """How far the pocket's bore runs behind the boss's back face: the sleeve's flange, its pan heads (head_h) and 1.1 of
    clearance (at the flange and 1.0 the heads stopped the insert short of home: the drawing check's d3, round 3)."""
    if RETAINER:
        return RETAINER['flange_t'] + RETAINER.get('head_h', 0.0) + 1.1
    return 1.0


def insert_pocket():
    """The insert's pocket in the gable block: its outline grown by INSERT['clear'] from the slope back to back_y,
    the boss's bore, the connector bay behind it, the magnets' and pins' holes in the pocket's back wall, and the cable
    channel from the bay's floor down through the block to the top panel's hole."""
    I = INSERT
    zc = WAVEGUIDE['throat_z']
    pk = _y_prism(insert_outline(I['clear']), -5.0, I['back_y'] + I['clear'])
    deep = pocket_bore_behind_boss()     # room behind the boss for the sleeve's flange and its screws' heads
    pk += cyl_y(RUN, zc, I['boss_d'] + 2 * I['clear'], I['back_y'], I['boss_back_y'] + deep)   # (below the body's top it cuts nothing)
    pk += cyl_y(RUN, zc + I['bay_dz'], I['bay_d'], I['boss_back_y'], I['boss_back_y'] + I['bay_l'])   # the connector bay
    mags, pins = insert_fixings()
    # the holes measured from the pocket's back wall (back_y + clear), as deep as the insert's own (d11, round 5)
    yw = I['back_y'] + I['clear']
    for (x, z) in mags:
        pk += cyl_y(x, z, I['magnet_d'] + 0.2, I['back_y'], yw + I['magnet_t'] + 0.3)
    for (x, z) in pins:     # a slip fit: 0.2 over the pin
        pk += cyl_y(x, z, I['pin_d'] + 0.2, I['back_y'], yw + I['pin_l'] / 2 + 0.5)
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


def amp_glands_xy():
    """The glands' centres in the amplifier box's lid, [(x, y), ...]: one per cable, the first 40 in from the right side's
    inner face, the rest leftward on AMP_BOX['gland_pitch'] centres, all 25 behind the box's front panel (43 from the
    lid's front edge, which is the front panel's)."""
    y0 = amp_box_extent()[0]
    return [(PLAN - WALL - 40.0 - k * AMP_BOX['gland_pitch'], y0 + 25.0) for k in range(AMP_BOX['glands'])]


def amp_gland_xy():
    """The first gland (the tweeter's and the mid's runs start there)."""
    return amp_glands_xy()[0]


def amp_box_panels():
    """Three 18 mm panels between the sides make the amplifier's sealed box: a floor, a lid and a front. The lid has a
    gland per speaker lead (one cable each, sealed by the gland)."""
    y0, y1, z0, z1 = amp_box_extent()
    floor = box(WALL, y0 - WALL, z0 - WALL, PLAN - WALL, y1, z0)
    lid = box(WALL, y0 - WALL, z1, PLAN - WALL, y1, z1 + WALL)
    cb_d, cb_t = AMP_BOX['nut_cb']           # each gland's lock nut, from below (cut before the lid goes in)
    for (gx, gy) in amp_glands_xy():
        lid -= cyl_z(gx, gy, AMP_BOX['gland_hole'], z1 - 1, z1 + WALL + 1)
        lid -= cyl_z(gx, gy, cb_d, z1 - 1, z1 + cb_t)
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
    if RETAINER:
        parts['tweeter-retainer'] = tweeter_retainer()
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
                       'magnets': [[round(x - RUN, 2), round(z, 2)] for (x, z) in mags], 'magnet_hole': [I['magnet_d'] + 0.2, I['magnet_t'] + 0.3],
                       'pins': [[round(x - RUN, 2), round(z, 2)] for (x, z) in pins], 'pin_hole_insert': I['pin_d'] + 0.1, 'pins_bonded': True,
                       'pull_groove': {'w': PULL_GROOVE[0], 'depth': PULL_GROOVE[1], 'from_front': PULL_GROOVE[2]},
                       'pin_hole_pocket': I['pin_d'] + 0.2, 'bay_d': I['bay_d'], 'bay_l': I['bay_l'], 'bay_z': WAVEGUIDE['throat_z'] + I['bay_dz'],
                       'channel': {'x': RUN, 'y': round(wire_hole_y(), 2), 'd': WIRE_HOLE_D},
                       'pocket': {'clear': I['clear'], 'back_wall_y': I['back_y'] + I['clear'],
                                  'boss_bore_d': I['boss_d'] + 2 * I['clear'], 'boss_bore_to_y': round(I['boss_back_y'] + pocket_bore_behind_boss(), 2),
                                  'bay': {'d': I['bay_d'], 'from_y': I['boss_back_y'], 'to_y': I['boss_back_y'] + I['bay_l'], 'axis_z': WAVEGUIDE['throat_z'] + I['bay_dz']}}}
        if RETAINER:
            R = RETAINER; yf, yb = retainer_y(); od_, id_ = retainer_rings()
            f['insert']['tweeter_retainer'] = {'mode': R.get('mode', 'sleeve'), 'tube_od': od_, 'tube_id': id_,
                                               'from_y': yf, 'to_y': yb, 'flange_d': R['flange_d'], 'flange_t': R['flange_t'],
                                               'screws': {'n': R['screws'], 'circle_d': R['screw_circle'], 'pilot': [R['pilot_d'], R['pilot_depth']],
                                                          'hole_d': R['hole_d'], 'screw': R['screw'], 'head_h': R.get('head_h'),
                                                          'points': [[round(x - RUN, 2), round(z, 2)] for (x, z) in retainer_screw_points()]}}
        else:
            f['insert']['tweeter_screws'] = {'n': T['screws'], 'pcd': T['bolt_circle'], **INSERT_SCREW}
    if AMP:
        y0, y1, z0, z1 = amp_box_extent()
        f['amp'] = {'cutout': [AMP['cut_w'], AMP['cut_h']], 'cutout_corner_r': AMP_CUT_R, 'rebate': [AMP['plate_w'] + 1, AMP['plate_h'] + 1, AMP['rebate']], 'z': AMP['z'],
                    'box_inside': {'y': [y0, y1], 'z': [z0, z1]},
                    'glands': {'size': AMP_BOX['gland'], 'hole_d': AMP_BOX['gland_hole'], 'nut_counterbore': list(AMP_BOX['nut_cb']),
                               'centres': [[round(x, 2), round(y, 2)] for (x, y) in amp_glands_xy()]}}
    if PORT:
        L = port_length_mm()
        f['port'] = {'z': PORT['z'], 'bore': PORT['bore'], 'od': PORT['bore'] + 2 * PORT_WALL, 'hole_d': PORT['bore'] + 2 * PORT_WALL + 0.5,
                     'flange_d': PORT['flange'], 'flange_t': PORT_FLANGE_T, 'tube_from_flange_face': L, 'collar': PORT_FLARE_R, 'overall': L + PORT_FLARE_R,
                     'printed_from_flange_face': L + PORT_TRIM}
    return f


def checks(parts):
    """Clearances that the parameters alone do not guarantee, measured on the solids where they can be: each a name, the
    measured margin in mm and the least it may be. A failure stops the build, the way a failing test would."""
    out = []
    def chk(name, margin, least):
        # judged on the margin as printed (to 0.01): 1.4999... against a least of 1.5 is the 1.5 the drawings give
        out.append({'check': name, 'margin_mm': round(margin, 2), 'least_mm': least, 'ok': round(margin, 2) >= least})
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
        yr_ = dowel_points()[2][1]
        chk('block over the rear dowels, normal to the back slope', ((PLAN - yr_ - DOWEL_D / 2) * math.tan(math.radians(SLOPE_DEG)) - DOWEL_DEPTH)
            * math.cos(math.radians(SLOPE_DEG)), 8.0)
        mags, pins = insert_fixings()
        bore_r = I['boss_d'] / 2 + I['clear']
        for (x, z) in mags + pins:
            d_ = (I['magnet_d'] if (x, z) in mags else I['pin_d']) / 2
            chk(f'magnet or pin at ({x - RUN:+.1f}, {z:g}) clear of the boss\'s bore', math.hypot(x - RUN, z - zc) - d_ - bore_r, 3.0)
        chk('pins\' holes clear of the magnets\' holes (material between)', min(math.hypot(px - mx, pz - mz) for (px, pz) in pins for (mx, mz) in mags)
            - (I['pin_d'] + 0.2) / 2 - (I['magnet_d'] + 0.2) / 2, 2.0)
        if RETAINER:
            R = RETAINER; od_, id_ = retainer_rings(); yf_, yb_ = retainer_y()
            if R.get('mode') == 'cap':
                chk('retaining cap\'s ring on the motor\'s back (its width)', (min(T['body_d'], od_) - id_) / 2, 4.0)
                chk('retaining cap\'s wall', (od_ - id_) / 2, 1.5)
                chk('retaining cap\'s ring at least 1 long (the motor\'s back in front of the boss\'s)', yb_ - yf_, 1.0)
            else:
                chk('retaining sleeve clear of the tweeter\'s motor (a side)', R['clear'], 0.4)
                chk('retaining sleeve\'s wall', (od_ - id_) / 2, 1.5)
            chk('sleeve\'s pilots in the boss\'s wall, inside', R['screw_circle'] / 2 - R['pilot_d'] / 2 - (T['flange_d'] + 0.4) / 2, 1.5)
            chk('sleeve\'s pilots in the boss\'s wall, outside', I['boss_d'] / 2 - R['screw_circle'] / 2 - R['pilot_d'] / 2, 1.5)
            chk('sleeve\'s flange inside the pocket\'s bore (a side)', I['boss_d'] / 2 + I['clear'] - R['flange_d'] / 2, 0.5)
            chk('sleeve\'s screw heads (5.6 pan) clear of the pocket\'s bore', I['boss_d'] / 2 + I['clear'] - R['screw_circle'] / 2 - 2.8, 0.3)
            # the heads stand head_h proud of the flange inside the pocket's bore (d3, round 3)
            chk('sleeve\'s screw heads clear of the pocket\'s bore floor (along the axis)', pocket_bore_behind_boss() - R['flange_t'] - R.get('head_h', 0.0), 0.8)
            if bb.max.X - bb.min.X > 250:     # printed in halves at the centre plane: no pilot in the glued seam (d5)
                chk('sleeve\'s pilots off the insert\'s split at the centre plane', min(abs(x - RUN) for (x, _) in retainer_screw_points()) - R['pilot_d'] / 2, 3.0)
        else:
            hd = INSERT_SCREW['head_d']
            chk('faceplate screws\' heads clear of the tweeter\'s body', T['bolt_circle'] / 2 - hd / 2 - T['body_d'] / 2, 0.5)
            chk('faceplate screws\' inserts in the seat, inside the bore', (T['flange_d'] + 0.4) / 2 - T['bolt_circle'] / 2 - INSERT_SCREW['hole_d'] / 2, 1.5)
        # the tweeter's body inside the boss's bore and the pocket's bore behind it, along the axis (a shop lists the
        # bookshelf's D3004/602200 45.3 deep: the datasheets of 2026-10-09)
        body_end = WAVEGUIDE['throat_y'] + (RETAINER['gasket'] if RETAINER else 0.5) + T['flange_t'] + T['body_depth']
        chk('tweeter\'s body inside its bore, along the axis', I['boss_back_y'] + pocket_bore_behind_boss() - body_end, 1.0)
        # the boss passes under the pocket's ceiling only if the insert's outline holds its circle (d1, round 3), and the
        # insert keeps a wall over the tweeter's bore at the top
        out_ = insert_outline()
        up = [(u, s_) for (u, s_) in out_ if DZ * s_ + BODY > zc]
        chk('the boss\'s circle inside the insert\'s outline (seen from the front)', min(math.hypot(u, DZ * s_ + BODY - zc) for (u, s_) in up) - I['boss_d'] / 2, 0.4)
        top = max(DZ * s_ + BODY for (u, s_) in out_ if abs(u) < 3.0)
        chk('insert material over the tweeter\'s bore, at the top', top - (zc + (T['flange_d'] + 0.4) / 2), 2.0)
        # the pocket's boss bore under the back slope (the bookshelf's came within 0.26: d4, round 3)
        yb_ = I['boss_back_y'] + pocket_bore_behind_boss()
        roof_b = RIDGE_Z - (yb_ - RUN) * tan_ if yb_ > RUN else BODY + yb_ * tan_
        chk('gable over the pocket\'s boss bore, under the back slope (vertical)', roof_b - (zc + I['boss_d'] / 2 + I['clear']), 3.0)
        yb = I['boss_back_y'] + I['bay_l']; zt = zc + I['bay_dz'] + I['bay_d'] / 2
        roof = RIDGE_Z - (yb - RUN) * tan_ if yb > RUN else BODY + yb * tan_
        chk('birch over the connector bay, under the back slope (vertical)', roof - zt, 8.0)
        chk('connector bay above the top panel', zc + I['bay_dz'] - I['bay_d'] / 2 - BODY, 4.0)
        # the tweeter's own lead has to reach the socket standing in the bay while the insert is held just clear of its
        # pocket (its back face at y 0), with 75 to spare for a hand in the pocket (the drawing check's d1, round 4)
        T_ = TWEETER_PART
        tabs_y = WAVEGUIDE['throat_y'] + (RETAINER['gasket'] if RETAINER else 0.0) + T_['flange_t'] + T_['body_depth'] - I['back_y']
        sock_z = zc + I['bay_dz'] - I['bay_d'] / 2 + 1.0 + CONNECTOR['mated_l'] / 2
        reach = math.hypot(wire_hole_y() - tabs_y, sock_z - zc)
        chk('tweeter\'s lead reaches the socket with the insert clear of its pocket (75 for a hand)', TWEETER_LEAD['l'] - reach - 75.0, 0.0)
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
    # the birch left under each rebate holds its T-nuts' barrels with 0.5 to spare: a thinner sheet (M1) eats it first
    # (the drawing check's d4, round 5)
    for role, reb in (('woofer', WOOFER_REBATE), ('mid', MID_REBATE)):
        barrel = (DRIVER_SCREW.get('tnut_barrel') or {}).get(role)
        if reb and barrel:
            chk(f'birch under the {role}\'s rebate for its T-nuts\' barrels (+0.5)', WALL - reb['depth'] - barrel - 0.5, 0.0)
    # each T-nut's flange, on the baffle's inside face, clear of its driver's cut-out (on the woofer's 295 circle a
    # 15 mm flange overhung the 282 cut-out by 1: the datasheets of 2026-10-09)
    for role, cut in (('woofer', WOOFER_CUTOUT), ('mid', MID_CUTOUT if MID else None)):
        sc = DRIVER_SCREWS.get(role); fl = (DRIVER_SCREW.get('tnut_flange') or {}).get(role)
        if sc and cut and fl:
            chk(f'{role}\'s T-nut flanges ({fl:g}) clear of its cut-out', sc['pcd'] / 2 - fl / 2 - cut / 2, 0.5)
    if AMP:
        chk('amplifier plate above the plinth\'s shadow line', AMP['z'] - AMP['plate_h'] / 2 - bot_front, 2.0)
        chk('amplifier plate inside the back, across', (PLAN - AMP['plate_w']) / 2 - EDGE_R, 2.0)
        y0, y1, z0, z1 = amp_box_extent()
        chk('amplifier box above the bottom panel', z0 - WALL - WALL, 0.0)
        gl = amp_glands_xy(); cb = AMP_BOX['nut_cb'][0]
        if len(gl) > 1:
            chk('birch between the glands\' counterbores', AMP_BOX['gland_pitch'] - cb, 5.0)
        chk('glands\' counterbores inside the lid (from the sides\' inner faces)',
            min(min(x for x, _ in gl) - cb / 2 - WALL, PLAN - WALL - max(x for x, _ in gl) - cb / 2), 5.0)
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



def write_hold():
    """stl/HOLD.txt: which prints wait on which measurement of sheet 7 (the drawing check's d4, round 7)."""
    m_ = lambda *ks: ', '.join(f'M{M_NUM[k]}' for k in ks if k in M_NUM)
    open(os.path.join(OUT, 'stl', 'HOLD.txt'), 'w').write(
        f'HOLD: these prints wait on the measurements of drawings sheet 7 ("Measure first"). Enter each in fab/params.py and\n'
        f'run fab/build.sh before printing.\n\n'
        + (f'  waveguide-insert*.stl, tweeter-retainer.stl  the tweeter ({m_("tweeter")}): its front ring, motor and depth set the bore, the seat\n'
           f'                                               and the retaining cap\n' if RETAINER else
           f'  waveguide-insert.stl                         the tweeter ({m_("tweeter")}): its faceplate, body and depth set the bore and the seat\n')
        + f'  gable-block.stl, gable-print/*.stl           the tweeter and the connector ({m_("tweeter", "connector")}): the pocket\'s bore and bay\n'
        f'  trim-ring-*.stl                              the drivers ({m_("woofer", "mid")}): each surround at its glue line sets a ring\'s bore\n'
        + (f'  port-tube*.stl                               printed long and trimmed to the tuning (README, step 9)\n' if PORT else '')
        + '\nPrint the connector\'s test bay first (connector-test-bay.stl, README, step 1).\n')

def joint_pins(g, axis, val, region, margin=4.0, step=10.0):
    """Two points far apart on a joint plane (x or y = val), inside region (u0, u1, z0, z1) with u the plane's other
    horizontal axis, where a 4 mm pin has `margin` of the solid g all round it: the gable's pocket, bay and channel leave
    some of each joint face hollow. Returns [] when none fit."""
    u0, u1, z0, z1 = region
    slab = g & (box(val - 11, u0, z0, val + 11, u1, z1) if axis == 'x' else box(u0, val - 11, z0, u1, val + 11, z1))
    r = 2.0 + margin
    c = cyl_x if axis == 'x' else cyl_y
    ok = []
    u = u0 + r
    while u <= u1 - r:
        z = z0 + r
        while z <= z1 - r:
            face = c(u, z, 2 * r, val - 0.5, val + 0.5)          # the joint face round the pin
            hole = c(u, z, 2 * 3.5, val - 10.5, val + 10.5)      # 1.5 of wall round the 4.2 hole along its 10 each side
            if (face & slab).volume > 0.995 * face.volume and (hole & slab).volume > 0.995 * hole.volume:
                ok.append((u, z))
            z += step
        u += step
    if len(ok) < 2:
        return ok
    best = max(((p, q) for i, p in enumerate(ok) for q in ok[i + 1:]), key=lambda pq: math.hypot(pq[0][0] - pq[1][0], pq[0][1] - pq[1][1]))
    return list(best)


def seal_stls(folder):
    """Every binary STL under folder: drop the triangles whose corners weld (at 0.1 micron) to fewer than three points,
    rewrite the file if any went, and report each file's edges used other than twice (0 for a closed mesh)."""
    import struct
    import numpy as np
    out = {}
    for root, _, files in os.walk(folder):
        for f in sorted(files):
            if not f.endswith('.stl'):
                continue
            path = os.path.join(root, f); b = open(path, 'rb').read()
            if b[:5] == b'solid' and b'facet' in b[:300]:
                continue                                  # ascii: none written here
            n = struct.unpack('<I', b[80:84])[0]
            dt = np.dtype([('n', '<3f4'), ('v', '<9f4'), ('a', '<u2')])
            a = np.frombuffer(b[84:84 + 50 * n], dtype=dt)
            q = np.round(a['v'].reshape(-1, 3, 3).astype(np.float64) / 1e-4).astype(np.int64)
            _, ids = np.unique(q.reshape(-1, 3), axis=0, return_inverse=True); ids = ids.reshape(-1, 3)
            good = (ids[:, 0] != ids[:, 1]) & (ids[:, 1] != ids[:, 2]) & (ids[:, 2] != ids[:, 0])
            if not good.all():
                keep = a[good]
                open(path, 'wb').write(b[:80] + struct.pack('<I', len(keep)) + keep.tobytes())
            e = np.sort(np.concatenate([ids[good][:, [0, 1]], ids[good][:, [1, 2]], ids[good][:, [2, 0]]]), axis=1)
            _, cnt = np.unique(e, axis=0, return_counts=True)
            out[os.path.relpath(path, folder)] = {'dropped': int((~good).sum()), 'open_edges': int((cnt != 2).sum())}
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
        if name == 'port-tube':   # printed as its two pieces below; the union as fitted (a STEP for the sheets) stays in the assembly
            report['parts'][name] = {'volume_l': round(solid.volume / 1e6, 4)}
            export_step(solid, os.path.join(OUT, 'step', 'port-tube.step'))
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
        # printed 10 mm long: trimmed at its inner end until the impedance dip sits at the tuning (fab/README.md)
        tube, collar = port_parts(port_length_mm() + PORT_TRIM)
        for nm, part in (('port-tube-with-flange', tube), ('port-flare-collar', collar)):
            export_stl(part, os.path.join(OUT, 'stl', f'{nm}.stl'), tolerance=0.05, angular_tolerance=0.1)
            export_step(part, os.path.join(OUT, 'step', f'{nm}.step'))
    whole = Compound(label=NAME, children=[s for s in parts.values()])
    export_step(whole, os.path.join(OUT, 'step', f'{NAME}.step'))
    # the trim rings for printing, each with a channel in its back over its frame's screw heads
    import components as C
    rings = [('woofer', WOOFER_REBATE)] + ([('mid', MID_REBATE)] if MID else [])
    for role, rb in rings:
        r_out = (rb['d'] - 1.6) / 2; r_in = TRIM_RING_ID[role] / 2      # the surround's glue line + 2 (measure it: d4)
        sc = DRIVER_SCREWS.get(role)
        ch = C.ring_channel(r_in, r_out, sc['pcd'] / 2, DRIVER_SCREW['head_d']) if sc else None
        ring = C.trim_ring(r_in, r_out, groove=ch)
        export_stl(ring, os.path.join(OUT, 'stl', f'trim-ring-{role}.stl'), tolerance=0.05, angular_tolerance=0.1)
        report['parts'][f'trim-ring-{role}'] = {'od_mm': round(2 * r_out, 1), 'id_mm': round(2 * r_in, 1), 't_mm': C.RING['t'],
                                                'channel': ({'from_d': round(2 * ch[0], 1), 'to_d': round(2 * ch[1], 1), 'depth': ch[2],
                                                             'open_to_bore': ch[0] <= r_in + 1e-6} if ch else None),
                                                'id_from': 'the surround at its glue line + 2: PLACEHOLDER, measure'}
    write_hold()
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
        # two 3 x 16 pins across the split, bonded: one under the tweeter's bore, one over it (the second sat in the
        # waveguide's air at the front and cut nothing: the drawing check's d13, round 3)
        pin_pts = insert_split_pins()
        pins = None
        for (py, pz) in pin_pts:
            c_ = Pos(RUN, py, pz) * Rot(0, 90, 0) * Cylinder(1.6, 17)      # 8.5 a side for a 16 pin: room for epoxy (d4, round 6)
            pins = c_ if pins is None else pins + c_
        report['insert_split_pins'] = [{'y': round(py, 1), 'z': round(pz, 1), 'd': 3.2, 'l': 16, 'hole_depth': 8.5} for (py, pz) in pin_pts]
        for nm, half in (('waveguide-insert-left', ins & box(-1, -10, BODY - 1, RUN, PLAN, TOTAL)),
                         ('waveguide-insert-right', ins & box(RUN, -10, BODY - 1, PLAN + 1, PLAN, TOTAL))):
            export_stl(half - pins, os.path.join(OUT, 'stl', f'{nm}.stl'), tolerance=0.02, angular_tolerance=0.05)
    # The gable block for printing (the cheap route), cut to fit a resin printer's 218 x 123 x 220 (or any FDM bed): the
    # floorstander's in six pieces, the bookshelf's in four (whole it is 220 x 220 x 110 and fits no orientation of that
    # printer: the drawing check's d2, round 3), every piece with a side of 120 or less, keyed at each joint by two 4 mm
    # pins (4.2 holes, 10.5 deep each side: 0.5 of room for the epoxy, the drawing check's d4, round 6) where the joint face has 4 mm of material round them, bonded with epoxy (the
    # drawing check's d5). Hollow the pieces to 3 mm walls with two drain holes in the slicer.
    g = parts['gable-block']
    os.makedirs(os.path.join(OUT, 'stl', 'gable-print'), exist_ok=True)
    for f_ in os.listdir(os.path.join(OUT, 'stl', 'gable-print')):
        os.remove(os.path.join(OUT, 'stl', 'gable-print', f_))
    if True:
        if PLAN > 256:
            ys, ym = 150.0, (150.0 + PLAN) / 2
            cells = {'front-left': (-1, RUN, -1, ys), 'front-right': (RUN, PLAN + 1, -1, ys),
                     'mid-left': (-1, RUN, ys, ym), 'mid-right': (RUN, PLAN + 1, ys, ym),
                     'rear-left': (-1, RUN, ym, PLAN + 1), 'rear-right': (RUN, PLAN + 1, ym, PLAN + 1)}
            joints = [('x', RUN, ('mid-left', 'mid-right'), (ys, ym)), ('x', RUN, ('rear-left', 'rear-right'), (ym, PLAN)),
                      ('y', ys, ('front-left', 'mid-left'), (0, RUN)), ('y', ys, ('front-right', 'mid-right'), (RUN, PLAN)),
                      ('y', ym, ('mid-left', 'rear-left'), (0, RUN)), ('y', ym, ('mid-right', 'rear-right'), (RUN, PLAN))]
        else:
            # behind the connector bay, so the front pieces' joint at the centre plane has solid round the bay for its pins
            # (just behind the pocket, at y 119, it was the 6 mm of wall behind the pocket and a sliver over it: no pin
            # fitted; at 160 one pin fitted, over the bay, the channel taking the room under it); the front pieces
            # 110 x 164 x 110 still fit the printer (164 along its 218)
            ys = min(PLAN - 40.0, INSERT['boss_back_y'] + INSERT['bay_l'] + 16.0)
            cells = {'front-left': (-1, RUN, -1, ys), 'front-right': (RUN, PLAN + 1, -1, ys),
                     'rear-left': (-1, RUN, ys, PLAN + 1), 'rear-right': (RUN, PLAN + 1, ys, PLAN + 1)}
            joints = [('x', RUN, ('front-left', 'front-right'), (0, ys)), ('x', RUN, ('rear-left', 'rear-right'), (ys, PLAN)),
                      ('y', ys, ('front-left', 'rear-left'), (0, RUN)), ('y', ys, ('front-right', 'rear-right'), (RUN, PLAN))]
        pieces = {nm: g & box(x0, y0, BODY - 1, x1, y1, TOTAL + 1) for nm, (x0, x1, y0, y1) in cells.items()}
        pin_log = []
        for axis, val, (a, b), (u0, u1) in joints:
            pts = joint_pins(g, axis, val, (u0, u1, BODY, RIDGE_Z))
            for (u, z) in pts:
                # 10.5 a side for a 20 pin: room for the epoxy at the bottom of each hole (d4, round 6)
                drill = (cyl_x(u, z, 4.2, val - 10.5, val + 10.5) if axis == 'x' else cyl_y(u, z, 4.2, val - 10.5, val + 10.5))
                pieces[a] = pieces[a] - drill; pieces[b] = pieces[b] - drill
            pin_log.append({'joint': f'{a} / {b}', 'plane': f'{axis} = {val:g}', 'pins': [[round(u, 1), round(z, 1)] for (u, z) in pts]})
        for nm, piece in pieces.items():
            export_stl(piece, os.path.join(OUT, 'stl', 'gable-print', f'gable-print-{nm}.stl'), tolerance=0.05, angular_tolerance=0.1)
            bb = piece.bounding_box()
            report['parts'][f'gable-print-{nm}'] = {'volume_l': round(piece.volume / 1e6, 3),
                                                    'size_mm': [round(bb.max.X - bb.min.X, 1), round(bb.max.Y - bb.min.Y, 1), round(bb.max.Z - bb.min.Z, 1)]}
        report['gable_print_pins'] = pin_log
    # the connector's test bay (README, step 1): the gable block round the bay, from just in front of the pocket's back
    # wall (the boss's bore behind it) to past the bay's end, with the channel below, printed first to mate and unlatch
    # the pair by hand before the gable is made (the drawing check's d5, round 8)
    if WAVEGUIDE:
        I_ = INSERT; zb_ = WAVEGUIDE['throat_z'] + I_['bay_dz']; rb_ = I_['boss_d'] / 2 + I_['clear'] + 12.0
        y0_, y1_ = I_['back_y'] + I_['clear'] - 6.0, I_['boss_back_y'] + I_['bay_l'] + 12.0
        bay_ = g & box(RUN - rb_, y0_, BODY - 1, RUN + rb_, y1_, zb_ + I_['bay_d'] / 2 + 12.0)
        export_stl(bay_, os.path.join(OUT, 'stl', 'connector-test-bay.stl'), tolerance=0.05, angular_tolerance=0.1)
        bb = bay_.bounding_box()
        report['parts']['connector-test-bay'] = {'volume_l': round(bay_.volume / 1e6, 3), 'from_y': round(y0_, 1), 'to_y': round(y1_, 1),
                                                 'size_mm': [round(bb.max.X - bb.min.X, 1), round(bb.max.Y - bb.min.Y, 1), round(bb.max.Z - bb.min.Z, 1)]}
    # every printed file closed: a tessellation can leave a zero-area triangle where a fillet meets a face (the gable
    # pieces' fin ends: the drawing check's d12, round 8), which a print service's file check flags; dropped here
    report['stl_sealed'] = seal_stls(os.path.join(OUT, 'stl'))
    open_ = [f for f, r in report['stl_sealed'].items() if r['open_edges']]
    if open_:
        raise SystemExit(f'{len(open_)} STL file(s) not closed after sealing: ' + ', '.join(open_))

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
