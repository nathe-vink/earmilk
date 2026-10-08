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

from build123d import Axis, Plane, Polyline, Pos, Rot, Solid, Spline, Location, make_face, revolve, Wire, Edge, Face, Vector

# Datasheet numbers (fab/drivers.json, fab/research/) and proportions for what datasheets omit.
DRIVERS = {
    'dsa315-8': dict(kind='cone', frame_od=314.0, flange_t=5.0, cutout=272.0, depth=130.0, sd_cm2=506.7,
                     magnet_d=140.0, magnet_h=48.0, cone='aluminium', cap='inverted', cap_d=104.0),
    'sb17mfc35-8': dict(kind='cone', frame_od=171.0, flange_t=3.0, cutout=146.0, depth=75.0, sd_cm2=118.0,
                        magnet_d=90.0, magnet_h=33.0, cone='paper', cap='convex', cap_d=36.0),
    'tweeter-1in': dict(kind='dome', dome_d=26.0, surround_w=2.5, flange_d=50.0, flange_t=4.0, body_d=43.0, body_depth=30.0,
                        dome_h=7.5),
}
RING = dict(width=20.0, t=3.0, crown=0.5, ease=1.0)    # params.TRIM_RING: printed, satin black, over the frame and its screws


def _revolve_profile(pts):
    """A closed (r, a) profile (a < 0 is forward of the flange's front face), revolved about the axis. Local frame: the
    axis is z, forward is +z (z = -a), the flange's front at z = 0."""
    face = make_face(Polyline(*[(r, 0, -a) for (r, a) in pts], close=True))   # in the XZ plane: x = radius, z = -a
    return revolve(face, Axis.Z, 360)


def _arc(c, rad, a0, a1, n=16):
    return [(c[0] + rad * math.cos(a0 + (a1 - a0) * i / n), c[1] + rad * math.sin(a0 + (a1 - a0) * i / n)) for i in range(n + 1)]


def cone_driver(spec):
    """Local solids for a cone driver: (r, a) profiles revolved, the flange's front at a = 0, a growing into the box."""
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
    out['frame'] = _revolve_profile([(fi, 0), (fo, 0), (fo, ft), (fi + 6, ft), (spec['magnet_d'] / 2 + 6, spec['depth'] - spec['magnet_h'] - 4),
                                     (spec['magnet_d'] / 2 - 4, spec['depth'] - spec['magnet_h'] - 4), (spec['magnet_d'] / 2 - 4, spec['depth'] - spec['magnet_h'] - 7),
                                     (spec['magnet_d'] / 2 + 3, spec['depth'] - spec['magnet_h'] - 7), (fi + 3, ft + 3), (fi, ft + 3)])
    # surround: a half roll, outer edge glued to the flange's front at r_sur, inner edge to the cone at r_cone
    c = ((r_cone + r_sur) / 2, 0.0); rr = sw / 2
    outer = [(c[0] + rr * math.cos(th), -rh * math.sin(th)) for th in [math.pi * i / 24 for i in range(25)]]       # a < 0: forward
    inner = [(c[0] + (rr - t) * math.cos(th), -(rh - t) * math.sin(th)) for th in [math.pi * (24 - i) / 24 for i in range(25)]]
    out['surround'] = _revolve_profile([(r_sur + 1.0, 0.0)] + outer[1:-1] + [(r_cone - 1.0, 0.0), (r_cone - 1.0, t * 0.6)] + inner[1:-1] + [(r_sur + 1.0, t * 0.6)])
    # cone: straight-sided (metal) or a slight curve (paper), from the roll's inner edge to the voice coil
    rc_in = cap_r * 1.08
    if spec.get('cone') == 'paper':
        prof = [(r_cone - (r_cone - rc_in) * u, cone_depth * (u ** 0.85)) for u in [i / 12 for i in range(13)]]
    else:
        prof = [(r_cone, 0.0), (rc_in, cone_depth)]
    back = [(r, a + t) for (r, a) in reversed(prof)]
    out['cone'] = _revolve_profile(prof + back)
    # dust cap: convex (forward) or inverted, seated where the cone meets the coil
    ch = spec.get('cap_h', 0.28 * cap_r)
    if spec.get('cap') == 'inverted':
        cap = [(cap_r * (1 - u), cone_depth - 2 + ch * math.sin(math.pi / 2 * u)) for u in [i / 12 for i in range(13)]]
    else:
        cap = [(cap_r * (1 - u), cone_depth - 2 - ch * math.sin(math.pi / 2 * u)) for u in [i / 12 for i in range(13)]]
    capb = [(r, a + 1.0) for (r, a) in reversed(cap)]
    out['cap'] = _revolve_profile([(cap_r * 1.08, cone_depth)] + cap + capb)
    # motor: the magnet and its plates, behind the basket
    md, mh = spec['magnet_d'] / 2, spec['magnet_h']
    a0 = spec['depth'] - mh
    out['motor'] = _revolve_profile([(0.0, a0), (md, a0), (md, spec['depth'] - 3), (md - 3, spec['depth']), (0.0, spec['depth'])])
    return out, dict(r_eff=R_eff, r_cone=r_cone, r_surround=r_sur, roll_h=rh)


def dome_tweeter(spec):
    """A dome tweeter as the waveguide sees it: dome and roll at the throat, a small flange, the body behind."""
    rd = spec['dome_d'] / 2; sw = spec['surround_w']; h = spec['dome_h']
    out = {}
    dome = [(rd * math.sin(th), -h * math.cos(th)) for th in [math.pi / 2 * i / 16 for i in range(17)]]   # apex to rim
    out['dome'] = _revolve_profile(dome + [(rd, 0.5), (0.0, 0.5)])
    c = rd + sw / 2
    roll = [(c + sw / 2 * math.cos(th), -0.5 * sw * math.sin(th)) for th in [math.pi * i / 12 for i in range(13)]]   # outer to inner
    out['surround'] = _revolve_profile(roll + [(rd - 0.3, 0.8), (rd + sw + 0.5, 0.8)])
    fo = spec['flange_d'] / 2
    out['frame'] = _revolve_profile([(rd + sw + 0.2, 0.0), (fo, 0.0), (fo, spec['flange_t']), (spec['body_d'] / 2, spec['flange_t']),
                                     (spec['body_d'] / 2, spec['flange_t'] + spec['body_depth']), (0.0, spec['flange_t'] + spec['body_depth']),
                                     (0.0, 1.5), (rd + sw + 0.2, 1.5)])
    return out, dict(r_radiating=rd + sw)


def trim_ring(r_in, r_out, ring=RING):
    """The trim ring's profile, outer to inner: eased outer edge level with the finish, a crown `crown` proud, a rounded
    inner edge down onto the frame. Local frame: a = 0 at the finish, the ring sits in a = 0 to t."""
    t, cr, e = ring['t'], ring['crown'], ring['ease']
    pts = [(r_out, t), (r_out, e)] + [(r_out - e + e * math.cos(th), e - e * math.sin(th)) for th in [math.pi / 2 * i / 6 for i in range(7)]][1:]
    mid = (r_in + r_out) / 2
    pts += [(r_out - e - 2, 0.0), (mid + 3, -cr), (mid - 3, -cr), (r_in + 2.5, 0.0)]
    pts += [(r_in + 2.5 - 2.5 * math.sin(th), 2.5 - 2.5 * math.cos(th)) for th in [math.pi / 2 * i / 6 for i in range(7)]][1:]
    pts += [(r_in, t)]
    return _revolve_profile(pts)


def place(local, centre, axis='-y', recess=0.0):
    """Move a local solid (forward +z, a = 0 at z = 0) to `centre` facing `axis`, its a = 0 plane `recess` mm
    behind the face it sits in. axis: '-y' (the front) or a unit vector (a waveguide's axis)."""
    x, y, z = centre
    if axis == '-y':
        # local +z (forward) -> world -y: a rotation of +90 degrees about x
        return Pos(x, y + recess, z) * Rot(90, 0, 0) * local
    raise ValueError(axis)


def driver_parts(role, spec, centre, axis='-y', ring_d=None, flange_recess=3.0):
    """The labelled solids of one driver in place: the ring level with the finish at `centre`'s face, the driver's
    flange `flange_recess` behind it (under the ring)."""
    if spec['kind'] == 'cone':
        local, info = cone_driver(spec)
    else:
        local, info = dome_tweeter(spec)
    parts = {f'{role}-{k}': place(v, centre, axis, flange_recess) for k, v in local.items()}
    if ring_d:
        r_out = ring_d / 2
        r_in = max(info.get('r_surround', 0) + 1.0, r_out - RING['width'])
        parts[f'{role}-ring'] = place(trim_ring(r_in, r_out), centre, axis, 0.0)
    return parts, info
