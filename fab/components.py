"""The bought parts as solids: drivers, their trim rings, and (later) the amplifier plate and hardware, from their
datasheets' dimensions, so the renders and the drawings show what will actually be fitted.

Every driver is a revolve about its axis (it faces -y, out of the front, or along its waveguide's axis), built from a
few dimensions that every datasheet gives: the frame's outside diameter and flange thickness, the cutout, the mounting
depth, the cone's effective area (Sd, which fixes the cone and surround), the magnet's diameter and height. What a
datasheet leaves out (the surround's roll, the cone's depth, the dust cap) is proportioned from those, and flagged
PROPORTIONED in the spec, to be measured on the part.

    from components import driver_parts, DRIVERS
    parts = driver_parts('woofer', DRIVERS['dsa315-8'], centre=(195, 0, 320), axis='-y', recess=3.0)

Returns {label: solid}: <role>-ring (the trim ring, its face level with the finish), <role>-frame (the flange and the
basket), <role>-surround, <role>-cone, <role>-cap, <role>-motor. Units mm, the CAD's frame.
"""
import math

from build123d import Axis, Plane, Polyline, Pos, Rot, Solid, Spline, Location, extrude, make_face, revolve, Wire, Edge, Face, Vector

# Datasheet numbers (fab/drivers.json, fab/research/) and proportions for what datasheets omit.
DRIVERS = {
    'dsa315-8': dict(kind='cone', frame_od=314.0, flange_t=5.0, cutout=272.0, depth=130.0, sd_cm2=506.7,
                     magnet_d=140.0, magnet_h=48.0, cone='aluminium', cap='inverted', cap_d=104.0),
    'sb17mfc35-8': dict(kind='cone', frame_od=171.0, flange_t=3.0, cutout=146.0, depth=75.0, sd_cm2=118.0,
                        magnet_d=90.0, magnet_h=33.0, cone='paper', cap='convex', cap_d=36.0),
    'tweeter-1in': dict(kind='dome', dome_d=26.0, surround_w=2.5, flange_d=50.0, flange_t=4.0, body_d=43.0, body_depth=30.0,
                        dome_h=7.5),
    # 2026-10-08, the research's set (fab/research/drivers-floorstander.md); magnet, cap and roll PROPORTIONED where unpublished
    'rss315hf-4': dict(kind='cone', frame_od=314.0, flange_t=5.0, cutout=282.0, depth=146.0, sd_cm2=515.0, surround_w=26.0, roll_h=13.0,
                       magnet_d=156.0, magnet_h=62.0, cone='aluminium', cap='convex', cap_d=112.0, cap_h=14.0),
    'mr16p-8': dict(kind='cone', frame_od=165.0, flange_t=7.5, cutout=140.3, depth=75.6, sd_cm2=119.0, surround_w=11.0, roll_h=5.0,
                    magnet_d=95.0, magnet_h=32.0, cone='paper', cap='convex', cap_d=42.0),
    'tw29dn-b': dict(kind='dome', dome_d=29.0, surround_w=8.0, flange_d=73.0, flange_t=6.0, body_d=66.0, body_depth=26.0, dome_h=9.5),
    # the bookshelf's (fab/research/drivers-small.md)
    'sb17nrx2c35-8': dict(kind='cone', frame_od=171.0, flange_t=6.5, cutout=144.9, depth=75.0, sd_cm2=118.0, surround_w=12.0, roll_h=5.5,
                          magnet_d=95.0, magnet_h=32.0, cone='paper', cap='convex', cap_d=38.0),
    'd3004-602200': dict(kind='dome', dome_d=26.0, surround_w=4.0, flange_d=62.0, flange_t=4.5, body_d=48.0, body_depth=17.0, dome_h=7.0),
    'nd25fn-4': dict(kind='dome', dome_d=25.0, surround_w=2.5, flange_d=41.0, flange_t=3.0, body_d=36.0, body_depth=18.0, dome_h=7.0),
}
RING = dict(width=20.0, t=3.0, crown=0.5, ease=1.0)    # params.TRIM_RING: printed, satin black, over the frame and its screws


def _revolve_profile(pts):
    """A closed (r, a) profile (a < 0 is forward of the flange's front face), revolved about the axis. Local frame: the
    axis is z, forward is +z (z = -a), the flange's front at z = 0."""
    face = make_face(Polyline(*[(r, 0, -a) for (r, a) in pts], close=True))   # in the XZ plane: x = radius, z = -a
    return revolve(face, Axis.Z, 360)


def _arc(c, rad, a0, a1, n=16):
    return [(c[0] + rad * math.cos(a0 + (a1 - a0) * i / n), c[1] + rad * math.sin(a0 + (a1 - a0) * i / n)) for i in range(n + 1)]


def cone_driver(spec, detail=24):
    """Local solids for a cone driver: (r, a) profiles revolved, the flange's front at a = 0, a growing into the box.
    `detail` is the points round the surround's roll (4 for line drawings, where every profile point draws a circle)."""
    R_eff = math.sqrt(spec['sd_cm2'] * 100 / math.pi)                # effective radius, mid-roll, mm
    sw = spec.get('surround_w', max(8.0, 0.08 * 2 * R_eff))           # PROPORTIONED roll width
    r_cone = R_eff - sw / 2; r_sur = R_eff + sw / 2
    rh = spec.get('roll_h', 0.45 * sw)                                # PROPORTIONED: the roll stands proud of the flange
    cone_depth = spec.get('cone_depth', 0.42 * r_cone)                 # PROPORTIONED
    cap_r = spec['cap_d'] / 2; t = 1.2
    out = {}
    # frame: the flange (front ring) and a basket cone down to the motor
    fo, ft = spec['frame_od'] / 2, spec['flange_t']
    fi = r_sur + 1.0
    frame = _revolve_profile([(fi, 0), (fo, 0), (fo, ft), (fi + 6, ft), (spec['magnet_d'] / 2 + 6, spec['depth'] - spec['magnet_h'] - 4),
                              (spec['magnet_d'] / 2 - 4, spec['depth'] - spec['magnet_h'] - 4), (spec['magnet_d'] / 2 - 4, spec['depth'] - spec['magnet_h'] - 7),
                              (spec['magnet_d'] / 2 + 3, spec['depth'] - spec['magnet_h'] - 7), (fi + 3, ft + 3), (fi, ft + 3)])
    # a cast basket is spokes and windows, not a solid cone: the wall between the flange's ring and the motor's seat is
    # cut into windows between `spokes` (PROPORTIONED: six, each about 5 % of the frame's diameter wide)
    n = spec.get('spokes', 6)
    if n and detail > 6:
        a0, a1 = ft + 8.0, spec['depth'] - spec['magnet_h'] - 12.0
        r_mid = (fi + spec['magnet_d'] / 2) / 2
        half = math.pi / n - max(10.0, 0.05 * spec['frame_od']) / r_mid / 2
        R = fo + 10.0
        if a1 > a0 + 5 and half > 0.05:
            for i in range(n):
                th = 2 * math.pi * i / n             # windows at 0, 60, ...: spokes up and down, where the sheets cut
                pts = [(0.0, 0.0)] + [(R * math.cos(th - half + 2 * half * k / 8), R * math.sin(th - half + 2 * half * k / 8)) for k in range(9)]
                wedge = Pos(0, 0, -a1) * extrude(make_face(Polyline(*pts, close=True)), amount=a1 - a0)
                frame = frame - wedge
    out['frame'] = frame
    # surround: a half roll, outer edge glued to the flange's front at r_sur, inner edge to the cone at r_cone
    c = ((r_cone + r_sur) / 2, 0.0); rr = sw / 2
    nd = detail
    outer = [(c[0] + rr * math.cos(th), -rh * math.sin(th)) for th in [math.pi * i / nd for i in range(nd + 1)]]       # a < 0: forward
    inner = [(c[0] + (rr - t) * math.cos(th), -(rh - t) * math.sin(th)) for th in [math.pi * (nd - i) / nd for i in range(nd + 1)]]
    out['surround'] = _revolve_profile([(r_sur + 1.0, 0.0)] + outer[1:-1] + [(r_cone - 1.0, 0.0), (r_cone - 1.0, t * 0.6)] + inner[1:-1] + [(r_sur + 1.0, t * 0.6)])
    # cone: straight-sided (metal) or a slight curve (paper), from the roll's inner edge to the voice coil
    rc_in = cap_r * 1.08
    if spec.get('cone') == 'paper' and detail > 6:
        prof = [(r_cone - (r_cone - rc_in) * u, cone_depth * (u ** 0.85)) for u in [i / 12 for i in range(13)]]
    else:
        prof = [(r_cone, 0.0), (rc_in, cone_depth)]
    back = [(r, a + t) for (r, a) in reversed(prof)]
    out['cone'] = _revolve_profile(prof + back)
    # dust cap: convex (forward) or inverted, seated where the cone meets the coil
    ch = spec.get('cap_h', 0.28 * cap_r)
    nc = 12 if detail > 6 else 3
    if spec.get('cap') == 'inverted':
        cap = [(cap_r * (1 - u), cone_depth - 2 + ch * math.sin(math.pi / 2 * u)) for u in [i / nc for i in range(nc + 1)]]
    else:
        cap = [(cap_r * (1 - u), cone_depth - 2 - ch * math.sin(math.pi / 2 * u)) for u in [i / nc for i in range(nc + 1)]]
    capb = [(r, a + 1.0) for (r, a) in reversed(cap)]
    out['cap'] = _revolve_profile([(cap_r * 1.08, cone_depth)] + cap + capb)
    # motor: the magnet and its plates, behind the basket
    md, mh = spec['magnet_d'] / 2, spec['magnet_h']
    D = spec['depth']
    a0 = D - mh
    if detail <= 6:     # line drawings: the motor's outline
        out['motor'] = _revolve_profile([(0.0, a0), (md, a0), (md, D - 3), (md - 3, D), (0.0, D)])
        return out, dict(r_eff=R_eff, r_cone=r_cone, r_surround=r_sur, roll_h=rh)
    # the motor as it is built, so a section reads as a driver (PROPORTIONED where datasheets are silent): a steel yoke
    # (back plate and pole piece, vented), a ferrite ring, a steel top plate, the voice coil in the gap between plate
    # and pole on a former from the cone's neck, and a corrugated spider from the former to the basket's seat
    r_coil = spec.get('coil_d', min(spec['cap_d'] * 0.9, spec['magnet_d'] * 0.45)) / 2
    w, cl = 0.4, 0.35                                   # the winding's half thickness, the gap's clearance each side
    rp, pin = r_coil - w - cl, r_coil + w + cl          # the pole's radius, the top plate's bore
    tp = bp = max(4.0, 0.2 * mh)                        # top plate, back plate
    rv = max(3.0, 0.28 * rp)                            # the pole's vent
    rt = 0.82 * md                                      # the top plate, a little smaller than the magnet
    rmi = pin + 4.0                                     # the magnet's bore
    yoke = _revolve_profile([(rv, a0), (rp, a0), (rp, D - bp), (md, D - bp), (md, D - 2), (md - 2, D), (rv, D)])
    plate = _revolve_profile([(pin, a0), (rt, a0), (rt, a0 + tp), (pin, a0 + tp)])
    out['motor'] = yoke + plate
    out['magnet'] = _revolve_profile([(rmi, a0 + tp), (md, a0 + tp), (md, D - bp), (rmi, D - bp)])
    neck = cone_depth
    out['coil'] = _revolve_profile([(r_coil - 0.15, neck), (rc_in, neck), (rc_in, neck + 1.0), (r_coil + 0.15, neck + 1.0),
                                    (r_coil + 0.15, a0 - 1.5), (r_coil + w, a0 - 1.5), (r_coil + w, a0 + tp + 1.5),
                                    (r_coil - w, a0 + tp + 1.5), (r_coil - w, a0 - 1.5), (r_coil - 0.15, a0 - 1.5)])
    # the spider sits a little in front of the top plate; its rim on the basket's inner wall there
    a_s = a0 - max(6.0, 0.15 * mh)
    (r1, b1), (r2, b2) = (fi + 3, ft + 3), (md + 3, a0 - 7)
    r_out = r1 + (r2 - r1) * (a_s - b1) / (b2 - b1) - 0.6
    r_in = r_coil + 0.15
    amp, th, nroll = (1.2 if spec['frame_od'] > 250 else 0.8), 0.8, 5
    us = [i / 60 for i in range(61)]
    front = [(r_in + (r_out - r_in) * u, a_s - th / 2 + amp * math.sin(2 * math.pi * nroll * u)) for u in us]
    rear = [(r, a + th) for (r, a) in reversed(front)]
    out['spider'] = _revolve_profile(front + rear)
    return out, dict(r_eff=R_eff, r_cone=r_cone, r_surround=r_sur, roll_h=rh)


def dome_tweeter(spec, detail=24):
    """A dome tweeter as the waveguide sees it: dome and roll at the throat, a small flange, the body behind. With
    `detail` above 6 the body is a cup with the motor inside it (PROPORTIONED): a steel top plate behind the dome, a
    neodymium ring, a back plate and pole piece, the voice coil in the gap, and the rear chamber behind."""
    rd = spec['dome_d'] / 2; sw = spec['surround_w']; h = spec['dome_h']
    out = {}
    dome = [(rd * math.sin(th), -h * math.cos(th)) for th in [math.pi / 2 * i / 16 for i in range(17)]]   # apex to rim
    out['dome'] = _revolve_profile(dome + [(rd, 0.5), (0.0, 0.5)])
    c = rd + sw / 2
    roll = [(c + sw / 2 * math.cos(th), -0.5 * sw * math.sin(th)) for th in [math.pi * i / 12 for i in range(13)]]   # outer to inner
    out['surround'] = _revolve_profile(roll + [(rd - 0.3, 0.8), (rd + sw + 0.5, 0.8)])
    fo, ft, bo = spec['flange_d'] / 2, spec['flange_t'], spec['body_d'] / 2
    L = ft + spec['body_depth']; fi = rd + sw + 0.2
    if detail <= 6:
        out['frame'] = _revolve_profile([(fi, 0.0), (fo, 0.0), (fo, ft), (bo, ft), (bo, L), (0.0, L), (0.0, 1.5), (fi, 1.5)])
        return out, dict(r_radiating=rd + sw)
    wall = 1.5
    out['frame'] = _revolve_profile([(fi, 0.0), (fo, 0.0), (fo, ft), (bo, ft), (bo, L), (0.0, L), (0.0, L - wall),
                                     (bo - wall, L - wall), (bo - wall, ft), (fi, ft)])
    r_coil = rd - 0.5; w, cl = 0.25, 0.2
    rp, pin = r_coil - w - cl, r_coil + w + cl
    rv = max(1.5, 0.25 * rp)
    mt, bt = max(3.0, 0.25 * spec['body_depth']), max(2.0, 0.12 * spec['body_depth'])
    ro = bo - wall - 0.5
    out['motor'] = (_revolve_profile([(pin, 1.0), (fi - 0.5, 1.0), (fi - 0.5, ft), (pin, ft)]) +                 # top plate
                    _revolve_profile([(rv, 1.0), (rp, 1.0), (rp, ft + mt), (ro, ft + mt), (ro, ft + mt + bt), (rv, ft + mt + bt)]))
    out['magnet'] = _revolve_profile([(pin + 2.5, ft), (ro, ft), (ro, ft + mt), (pin + 2.5, ft + mt)])
    out['coil'] = _revolve_profile([(r_coil - 0.15, 0.5), (r_coil + 0.15, 0.5), (r_coil + 0.15, 1.0), (r_coil + w, 1.0),
                                    (r_coil + w, ft + 0.8), (r_coil - w, ft + 0.8), (r_coil - w, 1.0), (r_coil - 0.15, 1.0)])
    return out, dict(r_radiating=rd + sw)


def trim_ring(r_in, r_out, ring=RING, groove=None):
    """The trim ring's profile, outer to inner: eased outer edge level with the finish, a crown `crown` proud, a rounded
    inner edge down onto the frame. Local frame: a = 0 at the finish, the ring sits in a = 0 to t. `groove` (radius,
    width, depth): a channel in its back over the frame's screw heads, so the ring lies on the flange, not on them."""
    t, cr, e = ring['t'], ring['crown'], ring['ease']
    pts = [(r_out, t), (r_out, e)] + [(r_out - e + e * math.cos(th), e - e * math.sin(th)) for th in [math.pi / 2 * i / 6 for i in range(7)]][1:]
    mid = (r_in + r_out) / 2
    pts += [(r_out - e - 2, 0.0), (mid + 3, -cr), (mid - 3, -cr), (r_in + 2.5, 0.0)]
    pts += [(r_in + 2.5 - 2.5 * math.sin(th), 2.5 - 2.5 * math.cos(th)) for th in [math.pi / 2 * i / 6 for i in range(7)]][1:]
    pts += [(r_in, t)]
    if groove:
        rg, gw, gd = groove
        pts += [(rg - gw / 2, t), (rg - gw / 2, t - gd), (rg + gw / 2, t - gd), (rg + gw / 2, t)]
    return _revolve_profile(pts)


def place(local, centre, axis='-y', recess=0.0):
    """Move a local solid (forward +z, a = 0 at z = 0) to `centre` facing `axis`, its a = 0 plane `recess` mm
    behind the face it sits in. axis: '-y' (the front) or a unit vector (a waveguide's axis)."""
    x, y, z = centre
    if axis == '-y':
        # local +z (forward) -> world -y: a rotation of +90 degrees about x
        return Pos(x, y + recess, z) * Rot(90, 0, 0) * local
    raise ValueError(axis)


def driver_parts(role, spec, centre, axis='-y', ring_d=None, flange_recess=3.0, detail=24, ring_id=None):
    """The labelled solids of one driver in place: the ring level with the finish at `centre`'s face, the driver's
    flange `flange_recess` behind it (under the ring). `ring_id`, the ring's inner diameter from params.TRIM_RING_ID
    (the surround at its glue line + 2), else from the drawn surround."""
    if spec['kind'] == 'cone':
        local, info = cone_driver(spec, detail)
    else:
        local, info = dome_tweeter(spec, detail)
    parts = {f'{role}-{k}': place(v, centre, axis, flange_recess) for k, v in local.items()}
    if ring_d:
        r_out = ring_d / 2
        r_in = ring_id / 2 if ring_id else max(info.get('r_surround', 0) + 1.0, r_out - RING['width'])
        parts[f'{role}-ring'] = place(trim_ring(r_in, r_out), centre, axis, 0.0)
    return parts, info


# --- the amplifier's plate -----------------------------------------------------------------------------------------------
def amp_plate(spec, centre_x, face_y, centre_z):
    """A FusionAmp-style plate amplifier lying on its side on the back: the plate (black anodised aluminium, its outer
    face at face_y), the module behind it through the cutout, and the connectors on the plate: a mains inlet with its
    switch, XLR and RCA inputs, USB for the DSP, a status light. The connectors' positions are schematic until Hypex's
    drawing is in hand (fab/research/amps.md); the plate's size, cutout and depth are the maker's.

    Seen from behind, u runs across the plate to the viewer's right (-x) and v up."""
    from build123d import Box, Cylinder, Pos, Rot, fillet, Axis, Align
    W, H, T, R = spec['plate_w'], spec['plate_h'], spec['plate_t'], spec['plate_r']
    def P(u, v, dy=0.0):            # plate-local (u, v) to the CAD's frame; dy out of the back (+y)
        return (centre_x - u, face_y + dy, centre_z + v)
    def boxy(u, v, w, h, y0, y1):   # a box w (across) x h (up), from y0 to y1 out of the face
        b = Box(w, abs(y1 - y0), h)
        x, y, z = P(u, v, (y0 + y1) / 2)
        return Pos(x, y, z) * b
    def cyl(u, v, d, y0, y1):
        x, y, z = P(u, v, (y0 + y1) / 2)
        return Pos(x, y, z) * Rot(90, 0, 0) * Cylinder(d / 2, abs(y1 - y0))
    plate = boxy(0, 0, W, H, -T, 0)
    plate = plate.fillet(R, plate.edges().filter_by(Axis.Y))
    # connector positions along the plate's long side (across when it lies on its side, up when it stands)
    portrait = H > W
    L = max(W, H)
    def at(t):          # a distance t from the long side's far end -> (u, v)
        return (0.0, L / 2 - t) if portrait else (W / 2 - t, 0.0)
    (iec_u, iec_v), (xlr_u, xlr_v), (rca_u, rca_v), (usb_u, usb_v), (led_u, led_v) = at(40), at(92), at(124), at(146), at(164)
    iw, ih = (28, 46) if portrait else (46, 28)
    holes = [boxy(iec_u, iec_v, iw, ih, -T - 1, 1), cyl(xlr_u, xlr_v, 24, -T - 1, 1), cyl(rca_u, rca_v, 11, -T - 1, 1),
             boxy(usb_u, usb_v, 13, 12, -T - 1, 1), cyl(led_u, led_v, 4, -T - 1, 1)]
    for h in holes:
        plate -= h
    parts = {'amp-plate': plate}
    # the module behind the plate (through the cutout)
    parts['amp-module'] = boxy(0, 0, spec['cut_w'] - 8, spec['cut_h'] - 8, -T - spec['module_depth'], -T)
    # connectors: bodies a little proud of the plate, their sockets recessed
    sw = (0, 15) if portrait else (15, 0)       # the switch beside the inlet's socket, along the long side
    if portrait:
        iec = boxy(iec_u, iec_v, 30, 48, -6, 1.5) - boxy(iec_u, iec_v - 7, 19, 24, -4, 2)
        iec -= boxy(iec_u, iec_v + 15, 18, 11, -3, 2)
        rocker = boxy(iec_u, iec_v + 15, 16, 10, -2, 1.2)
    else:
        iec = boxy(iec_u, iec_v, 48, 30, -6, 1.5) - boxy(iec_u + 7, iec_v, 24, 19, -4, 2)   # the inlet's socket
        iec -= boxy(iec_u - 15, iec_v, 11, 18, -3, 2)                                       # the switch's opening
        rocker = boxy(iec_u - 15, iec_v, 10, 16, -2, 1.2)
    xlr = cyl(xlr_u, xlr_v, 26, -10, 1.6) - cyl(xlr_u, xlr_v, 19.5, -8, 2)
    rca = cyl(rca_u, rca_v, 8.4, -8, 9.0) - cyl(rca_u, rca_v, 6.2, -6, 10)
    rca_nut = cyl(rca_u, rca_v, 12.5, 0, 1.8)
    usb = boxy(usb_u, usb_v, 15, 14, -9, 0.8) - boxy(usb_u, usb_v, 12, 11, -7, 1.5)
    led = cyl(led_u, led_v, 4.0, -2, 0.6)
    parts['amp-connectors'] = iec + xlr + usb
    parts['amp-switch'] = rocker
    parts['amp-rca'] = rca + rca_nut
    parts['amp-led'] = led
    # screws: countersunk heads flush in the plate, five along each long edge
    heads = None
    for i in range(5):
        t = -L / 2 + 10 + i * (L - 20) / 4
        for e in (-1, 1):
            u, v = ((e * (W / 2 - 7), t) if portrait else (t, e * (H / 2 - 7)))
            c = cyl(u, v, 7.0, -0.6, 0.02)
            heads = c if heads is None else heads + c
    parts['amp-screws'] = heads
    return parts


# --- the hardware inside: cables, the tweeter's connector, the seals, the insert's magnets and pins ------------------------
def cable(points, d):
    """A cable through 3D points (mm): round segments joined by spheres at the bends, one solid."""
    from build123d import Sphere
    r = d / 2; out = None
    for a, b in zip(points[:-1], points[1:]):
        A, B = Vector(*a), Vector(*b)
        L = (B - A).length
        if L < 1e-6:
            continue
        seg = Solid.make_cylinder(r, L, Plane(origin=A, z_dir=(B - A).normalized()))
        out = seg if out is None else out + seg
    for p in points[1:-1]:
        out += Pos(*p) * Sphere(r)
    return out


def connector_2p(centre, length=24.0, w=10.0, t=8.0):
    """A two-pole locking connector (JST VH or Molex Mini-Fit Jr. size), mated, standing along z at `centre`: the plug
    on top (the tweeter's lead), the socket below (the cabinet's), 0.6 apart where they latch."""
    from build123d import Box
    x, y, z = centre; h = (length - 0.6) / 2
    plug = Pos(x, y, z + 0.3 + h / 2) * Box(w, t, h)
    sock = Pos(x, y, z - 0.3 - h / 2) * Box(w + 0.8, t + 0.8, h)
    latch = Pos(x, y + t / 2 + 0.6, z + 0.3 + h * 0.35) * Box(w * 0.45, 1.2, h * 0.5)
    return {'connector-plug': plug + latch, 'connector-socket': sock}


def grommet(x, y, z_face, hole_d, cable_d, below=True):
    """A rubber grommet sealing a cable where it passes a panel's hole: a flange 4 thick on the panel's face (below it
    when `below`), a sleeve in the hole, the cable's bore through both."""
    s = -1 if below else 1
    fl = Solid.make_cylinder(hole_d / 2 + 4, 4, Plane(origin=(x, y, z_face + (s * 4 if below else 0)), z_dir=(0, 0, 1)))
    sl = Solid.make_cylinder(hole_d / 2 - 0.3, 12, Plane(origin=(x, y, z_face - (0 if below else 12)), z_dir=(0, 0, 1)))
    bore = Solid.make_cylinder(cable_d / 2, 40, Plane(origin=(x, y, z_face - 20), z_dir=(0, 0, 1)))
    return fl + sl - bore


def cable_gland(x, y, z_face, d=20.0, cable_d=7.0):
    """A nylon cable gland (M20 or PG13.5) through a panel at z_face, from above: a hex body on the face and its dome
    nut, the lock nut under the panel."""
    from build123d import RegularPolygon, extrude as ex, Plane as Pl
    hexb = ex(Pl.XY.offset(z_face) * Pos(x, y) * RegularPolygon(d * 0.62, 6), amount=6)
    dome = Solid.make_cylinder(d * 0.45, 9, Plane(origin=(x, y, z_face + 6), z_dir=(0, 0, 1)))
    nut = ex(Pl.XY.offset(z_face - 18 - 5) * Pos(x, y) * RegularPolygon(d * 0.62, 6), amount=5)
    bore = Solid.make_cylinder(cable_d / 2, 60, Plane(origin=(x, y, z_face - 30), z_dir=(0, 0, 1)))
    return hexb + dome + nut - bore


def discs(points_xz, y0, y1, d):
    """Discs (magnets, pins) along y at (x, z) points, from y0 to y1, as one solid."""
    out = None
    for (x, z) in points_xz:
        c = Solid.make_cylinder(d / 2, y1 - y0, Plane(origin=(x, y0, z), z_dir=(0, 1, 0)))
        out = c if out is None else out + c
    return out
