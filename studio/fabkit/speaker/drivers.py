"""Drivers as solids from the few numbers every datasheet gives, so the drawings, clash checks and renders show what
will be fitted (ported from earmilk's fab/components.py, which the drawing checks went over for eight rounds).

A cone driver is built from its frame's outside diameter and flange thickness, its cut-out, its mounting depth, its
cone area (Sd), and its magnet's diameter and height; what datasheets leave out (the surround's roll, the cone's depth,
the dust cap, the motor's insides) is proportioned from those and should be measured on the part. A dome tweeter from
its dome, surround, flange and body. A compression driver (for a horn) from its body diameter and depth and its exit.

    from speaker.drivers import cone_driver, dome_tweeter, compression_driver, place, driver
    solids = driver('woofer', spec, centre=(0, 0, 300), axis=(0, -1, 0), recess=0.0)   # {'woofer-cone': ..., ...}

Local frame of every builder: the driver's axis is z, forward (out of the speaker) is +z, the flange's front face at
z = 0 (a profile's `a` grows backwards into the box: z = -a).
"""
import math

from build123d import Axis, Polyline, Pos, Rot, extrude, make_face, revolve, Location, Vector

def _revolve_profile(pts):
    """A closed (r, a) profile (a < 0 is forward of the flange's front face), revolved about the axis. Local frame: the
    axis is z, forward is +z (z = -a), the flange's front at z = 0."""
    # a corner given twice (a body as wide as its front ring, as SB draws the TW29DN-B: round 8) is one corner, and a
    # zero-length edge stops OpenCascade
    clean = []
    for q in pts:
        if not clean or abs(q[0] - clean[-1][0]) > 1e-6 or abs(q[1] - clean[-1][1]) > 1e-6:
            clean.append(q)
    if len(clean) > 1 and abs(clean[0][0] - clean[-1][0]) <= 1e-6 and abs(clean[0][1] - clean[-1][1]) <= 1e-6:
        clean.pop()
    face = make_face(Polyline(*[(r, 0, -a) for (r, a) in clean], close=True))   # in the XZ plane: x = radius, z = -a
    return revolve(face, Axis.Z, 360)


def _arc(c, rad, a0, a1, n=16):
    return [(c[0] + rad * math.cos(a0 + (a1 - a0) * i / n), c[1] + rad * math.sin(a0 + (a1 - a0) * i / n)) for i in range(n + 1)]


def cone_driver(spec, detail=24):
    """Local solids for a cone driver: (r, a) profiles revolved, the flange's front at a = 0, a growing into the box.
    `detail` is the points round the surround's roll (4 for line drawings, where every profile point draws a circle)."""
    R_eff = math.sqrt(spec['sd_cm2'] * 100 / math.pi)                # effective radius, mid-roll, mm
    sw = spec.get('surround_w', max(8.0, 0.08 * 2 * R_eff))           # PROPORTIONED roll width
    r_cone = R_eff - sw / 2; r_sur = R_eff + sw / 2
    rh = spec.get('roll_h', 0.45 * sw)                                # PROPORTIONED: the roll stands proud of its seat
    seat = spec.get('roll_seat', 0.0)       # how far behind the flange's front the surround is glued (a pro woofer's sits
                                            # in a step, its roll's top about level with the flange); 0: on the front
    cone_depth = spec.get('cone_depth', 0.42 * r_cone)                 # PROPORTIONED
    cap_r = spec['cap_d'] / 2; t = 1.2
    out = {}
    # frame: the flange (front ring) and a basket cone down to the motor
    fo, ft = spec['frame_od'] / 2, spec['flange_t']
    fi = r_sur + 1.0
    # the basket's outside just behind the flange stays inside the maker's cut-out (it goes through it), its wall 3 thick
    rb = min(fi + 6, spec['cutout'] / 2 - 0.5) if spec.get('cutout') else fi + 6
    ri = min(fi + 3, rb - 3)
    frame = _revolve_profile([(fi, 0), (fo, 0), (fo, ft), (rb, ft), (spec['magnet_d'] / 2 + 6, spec['depth'] - spec['magnet_h'] - 4),
                              (spec['magnet_d'] / 2 - 4, spec['depth'] - spec['magnet_h'] - 4), (spec['magnet_d'] / 2 - 4, spec['depth'] - spec['magnet_h'] - 7),
                              (spec['magnet_d'] / 2 + 3, spec['depth'] - spec['magnet_h'] - 7), (ri, ft + 3), (min(fi, ri), ft + 3)])
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
    # surround: a half roll, outer edge glued to the flange's front (or its step, `seat` behind) at r_sur, inner edge to
    # the cone at r_cone
    c = ((r_cone + r_sur) / 2, 0.0); rr = sw / 2
    nd = detail
    outer = [(c[0] + rr * math.cos(th), seat - rh * math.sin(th)) for th in [math.pi * i / nd for i in range(nd + 1)]]   # a < 0: forward
    inner = [(c[0] + (rr - t) * math.cos(th), seat - (rh - t) * math.sin(th)) for th in [math.pi * (nd - i) / nd for i in range(nd + 1)]]
    out['surround'] = _revolve_profile([(r_sur + 1.0, seat)] + outer[1:-1] + [(r_cone - 1.0, seat), (r_cone - 1.0, seat + t * 0.6)]
                                       + inner[1:-1] + [(r_sur + 1.0, seat + t * 0.6)])
    # cone: straight-sided (metal) or a slight curve (paper), from the roll's inner edge to the voice coil
    rc_in = cap_r * 1.08
    if spec.get('cone') == 'paper' and detail > 6:
        prof = [(r_cone - (r_cone - rc_in) * u, seat + cone_depth * (u ** 0.85)) for u in [i / 12 for i in range(13)]]
    else:
        prof = [(r_cone, seat), (rc_in, seat + cone_depth)]
    back = [(r, a + t) for (r, a) in reversed(prof)]
    out['cone'] = _revolve_profile(prof + back)
    # dust cap: convex (forward) or inverted, seated where the cone meets the coil
    ch = spec.get('cap_h', 0.28 * cap_r)
    nc = 12 if detail > 6 else 3
    if spec.get('cap') == 'inverted':
        cap = [(cap_r * (1 - u), seat + cone_depth - 2 + ch * math.sin(math.pi / 2 * u)) for u in [i / nc for i in range(nc + 1)]]
    else:
        cap = [(cap_r * (1 - u), seat + cone_depth - 2 - ch * math.sin(math.pi / 2 * u)) for u in [i / nc for i in range(nc + 1)]]
    capb = [(r, a + 1.0) for (r, a) in reversed(cap)]
    out['cap'] = _revolve_profile([(cap_r * 1.08, seat + cone_depth)] + cap + capb)
    # motor: the magnet and its plates, behind the basket
    md, mh = spec['magnet_d'] / 2, spec['magnet_h']
    D = spec['depth']
    a0 = D - mh
    if detail <= 6:     # line drawings: the motor's outline
        out['motor'] = _revolve_profile([(0.0, a0), (md, a0), (md, D - 3), (md - 3, D), (0.0, D)])
        return out, dict(r_eff=R_eff, r_cone=r_cone, r_surround=r_sur, roll_h=rh, roll_seat=seat)
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
    neck = seat + cone_depth
    out['coil'] = _revolve_profile([(r_coil - 0.15, neck), (rc_in, neck), (rc_in, neck + 1.0), (r_coil + 0.15, neck + 1.0),
                                    (r_coil + 0.15, a0 - 1.5), (r_coil + w, a0 - 1.5), (r_coil + w, a0 + tp + 1.5),
                                    (r_coil - w, a0 + tp + 1.5), (r_coil - w, a0 - 1.5), (r_coil - 0.15, a0 - 1.5)])
    # the spider sits a little in front of the top plate; its rim on the basket's inner wall there
    a_s = a0 - max(6.0, 0.15 * mh)
    (r1, b1), (r2, b2) = (ri, ft + 3), (md + 3, a0 - 7)
    r_out = r1 + (r2 - r1) * (a_s - b1) / (b2 - b1) - 0.6
    r_in = r_coil + 0.15
    amp, th, nroll = (1.2 if spec['frame_od'] > 250 else 0.8), 0.8, 5
    us = [i / 60 for i in range(61)]
    front = [(r_in + (r_out - r_in) * u, a_s - th / 2 + amp * math.sin(2 * math.pi * nroll * u)) for u in us]
    rear = [(r, a + th) for (r, a) in reversed(front)]
    out['spider'] = _revolve_profile(front + rear)
    return out, dict(r_eff=R_eff, r_cone=r_cone, r_surround=r_sur, roll_h=rh, roll_seat=seat)


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


def compression_driver(spec, detail=24):
    """A compression driver: a round body (`body_d` x `body_depth`) behind a mounting flange (`flange_d` x `flange_t`)
    with its exit (`exit_d`, the throat it feeds) at the flange's front face; bolt-on (a flange) or screw-on (a thread
    stub, `thread_d`). Local frame as the others: the exit faces +z, the flange's front at z = 0."""
    out = {}
    fo, ft = spec['flange_d'] / 2, spec['flange_t']
    bo, bd = spec['body_d'] / 2, spec['body_depth']
    re_ = spec['exit_d'] / 2
    if spec.get('thread_d'):
        td = spec['thread_d'] / 2
        out['frame'] = _revolve_profile([(re_, 0.0), (td, 0.0), (td, ft), (re_, ft)])
        out['motor'] = _revolve_profile([(0.0, ft), (bo, ft), (bo, ft + bd - 4), (bo - 4, ft + bd), (0.0, ft + bd)])
    else:
        out['frame'] = _revolve_profile([(re_, 0.0), (fo, 0.0), (fo, ft), (re_, ft)])
        out['motor'] = _revolve_profile([(0.0, ft), (bo, ft), (bo, ft + bd - 5), (bo - 5, ft + bd), (0.0, ft + bd)])
    # the phase plug seen down the exit: a cone inside the throat, so a render looking into the horn finds a driver
    pp = re_ * 0.85
    out['plug'] = _revolve_profile([(0.0, 1.0), (pp, ft * 0.9), (0.0, ft * 0.9)])
    return out, dict(r_exit=re_)


RING = dict(t=6.0, crown=0.0, ease=1.0, inner_r=2.5, width=14.0)


def trim_ring(r_in, r_out, ring=RING):
    """A trim ring's profile, outer to inner, eased at both edges; local frame as the drivers', a = 0 at the finish."""
    t, e, ir = ring['t'], ring['ease'], ring.get('inner_r', 2.5)
    pts = [(r_out, t), (r_out, e)] + [(r_out - e + e * math.cos(th), e - e * math.sin(th)) for th in [math.pi / 2 * i / 6 for i in range(7)]][1:]
    pts += [(r_in + ir, 0.0)]
    pts += [(r_in + ir - ir * math.sin(th), ir - ir * math.cos(th)) for th in [math.pi / 2 * i / 6 for i in range(7)]][1:]
    pts += [(r_in, t)]
    return _revolve_profile(pts)


def place(local, centre, axis=(0, -1, 0), recess=0.0):
    """Move a local solid (forward +z, its flange's front at z = 0) to `centre`, facing the unit vector `axis`, its
    z = 0 plane `recess` mm behind `centre` along the axis."""
    ax = Vector(*axis).normalized()
    z = Vector(0, 0, 1)
    c = Vector(*centre) - ax * recess
    cross = z.cross(ax)
    if cross.length < 1e-9:
        rot = Location() if ax.Z > 0 else Location((0, 0, 0), (1, 0, 0), 180)
    else:
        ang = math.degrees(math.acos(max(-1.0, min(1.0, z.dot(ax)))))
        rot = Location((0, 0, 0), (cross.X, cross.Y, cross.Z), ang)
    return Pos(c.X, c.Y, c.Z) * (rot * local)


def driver(role, spec, centre, axis=(0, -1, 0), recess=0.0, detail=24, ring=None):
    """A driver's labelled solids in place: {'<role>-<piece>': solid}. spec['kind'] picks the builder: 'cone', 'dome' or
    'compression'. `ring` (inner, outer diameter) adds a trim ring level with `centre`'s face."""
    b = {'cone': cone_driver, 'dome': dome_tweeter, 'compression': compression_driver}[spec['kind']]
    local, info = b(spec, detail)
    out = {f'{role}-{k}': place(v, centre, axis, recess) for k, v in local.items()}
    if ring:
        out[f'{role}-ring'] = place(trim_ring(ring[0] / 2, ring[1] / 2), centre, axis, 0.0)
    return out, info


# the render finishes a driver's pieces get, unless the product names others
DRIVER_FINISH = {'frame': 'driver-frame', 'motor': 'driver-motor', 'magnet': 'driver-magnet', 'cone': 'driver-cone',
                 'surround': 'driver-surround', 'cap': 'driver-cap', 'coil': 'driver-coil', 'spider': 'driver-spider',
                 'dome': 'driver-dome', 'plug': 'driver-plug', 'ring': 'driver-ring'}


def driver_part(name, ref, spec, centre, axis=(0, -1, 0), recess=0.0, detail=24, ring=None, finishes=None, **kw):
    """A bought driver as one part: its library `ref` for the parts list, its pieces united for the checks and
    drawings, and each piece in its own finish for the render. Returns (Part, info)."""
    from build123d import Compound
    from model import Part, Bought
    solids, info = driver(name, spec, centre, axis, recess, detail, ring)
    line, _ = driver(name, spec, centre, axis, recess, 4, ring)          # the drawings' outline: few rings to draw
    fin = dict(DRIVER_FINISH, **(finishes or {}))
    pieces = {k[len(name) + 1:]: (s, fin.get(k[len(name) + 1:], 'driver-frame')) for k, s in solids.items()}
    return Part(name, Compound(children=list(solids.values())), Bought(ref), finish='driver', pieces=pieces,
                draw=Compound(children=list(line.values())), **kw), info
