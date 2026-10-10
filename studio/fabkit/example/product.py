"""The kit's worked example: a small two-way speaker in 18 mm birch plywood, a 6.5 in paper-cone woofer and a dome
tweeter in a printed waveguide, a DSP plate amplifier in the back and four turned oak feet. Every way of making a part
is in it (cut, printed, machined, bought, and bought with nothing to draw), so it is the file to copy for a new
product:

    .venv-fab/bin/python studio/fabkit/build.py studio/fabkit/example/product.py

The cabinet is butt-jointed and glued: the sides run the full height and depth, the top and bottom sit between them,
and the baffle and back sit inside all four. Sealed, about 14 L net, with a DSP shelf for the bass (speaker/box.py
gives the numbers: `.venv-fab/bin/python studio/fabkit/example/product.py`).
"""
import math, os, sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from kit import *                                                   # noqa: E402,F403
from speaker.drivers import driver_part                            # noqa: E402
from speaker.horn import os as os_profile                          # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
LIB = __import__('json').load(open(os.path.join(HERE, '..', 'library', 'components.json')))

P = dict(
    W=230.0, D=260.0, H=400.0, T=18.0,          # outside sizes and the plywood
    woofer='sb17nrx2c35-8', woofer_z=130.0,     # library key, centre height
    tweeter='d3004-602200', tweeter_z=290.0,
    amp='hypex-fa122', amp_z=200.0,
    gasket=1.0,                                 # compressed gasket under each flange, in its rebate
    wg=dict(d=100.0, depth=32.0, flange_d=116.0, flange_t=5.0, r0=17.5, angle=90.0, round=8.0),
    foot_d=30.0, foot_h=12.0, foot_in=30.0,
)


def waveguide(P, cx, cz):
    """A puck with an oblate-spheroidal waveguide in it, its flange flush in the baffle: the tweeter's faceplate screws
    to its back, the dome at the throat. Profile (r, h): h runs back from the baffle's front face."""
    g = P['wg']
    L, R = g['depth'], g['round']
    body = revolve_profile([(0.0, 0.0), (g['flange_d'] / 2, 0.0), (g['flange_d'] / 2, g['flange_t']), (g['d'] / 2, g['flange_t']),
                            (g['d'] / 2, L), (0.0, L)], axis='y', centre=(cx, 0.0, cz))
    prof = os_profile(g['r0'], g['angle'], L - R, n=40)              # (x from the throat, r)
    wall = [(r, L - x) for x, r in prof]                               # throat (h = L) forward to h = R
    re = wall[-1][0]
    # the roundover to 80 degrees, then straight on out through the face: a surface that met the face tangentially
    # would leave the boolean nothing to cut along (OpenCascade returns the body uncut)
    t_end = math.radians(80)
    arc = [(re + R - R * math.cos(t), R - R * math.sin(t)) for t in [t_end * i / 8 for i in range(1, 9)]]
    (ra, ha), (tr, th) = arc[-1], (math.sin(t_end), -math.cos(t_end))
    mouth = ra + tr / -th * ha                                          # where it crosses the face, h = 0
    out = (ra + tr / -th * (ha + 1.0), -1.0)
    cav = [(0.0, L + 1.0), (g['r0'], L + 1.0)] + wall + arc + [out, (0.0, -1.0)]
    i0, i1 = 2, 2 + len(wall) - 1                                       # the wall, then the roundover, each one spline
    cavity = revolve_profile(cav, axis='y', centre=(cx, 0.0, cz), smooth=[(i0, i1), (i1, i1 + len(arc))])
    puck = body - cavity
    # three pilot holes for the tweeter's faceplate screws, on its 54 mm circle, 8 deep from the back
    for k in range(3):
        a = math.radians(90 + 120 * k)
        puck = puck - cyl('y', (cx + 27 * math.cos(a), cz + 27 * math.sin(a)), 2.4, L - 8, L + 1)
    return puck, mouth


def parts(P):
    W, D, H, T = P['W'], P['D'], P['H'], P['T']
    ply = lambda grain: Sheet('baltic-birch', T, grain=grain)
    cx = W / 2
    wf = LIB[P['woofer']]['geom']
    tw = LIB[P['tweeter']]['geom']
    amp = LIB[P['amp']]['geom']
    g = P['wg']

    # the baffle: the woofer's cut-out in a rebate for its flange (flush, on its gasket), four holes for its T-nuts,
    # the waveguide's flange in a rebate and its body through
    baffle = box(T, 0, T, W - T, T, H - T)
    reb_w = wf['flange_t'] + P['gasket']
    baffle = baffle - cyl('y', (cx, P['woofer_z']), wf['frame_od'] + 1.0, -1, reb_w)
    baffle = baffle - cyl('y', (cx, P['woofer_z']), wf['cutout'], -1, T + 1)
    for k in range(wf.get('bolts', 4)):
        a = math.radians(45 + 90 * k)
        baffle = baffle - cyl('y', (cx + wf['bolt_d'] / 2 * math.cos(a), P['woofer_z'] + wf['bolt_d'] / 2 * math.sin(a)), 5.0, -1, T + 1)
    baffle = baffle - cyl('y', (cx, P['tweeter_z']), g['flange_d'] + 0.5, -1, g['flange_t'])
    baffle = baffle - cyl('y', (cx, P['tweeter_z']), g['d'] + 0.4, -1, T + 1)

    # the back: the amplifier's plate flush in a 4.5 mm rebate (3 mm plate on 1.5 mm of squeezed EPDM tape), its
    # module through the cut-out Hypex gives
    back = box(T, D - T, T, W - T, D, H - T)
    back = back - box(cx - (amp['plate_w'] + 0.5) / 2, D - 4.5, P['amp_z'] - (amp['plate_h'] + 0.5) / 2,
                      cx + (amp['plate_w'] + 0.5) / 2, D + 1, P['amp_z'] + (amp['plate_h'] + 0.5) / 2)
    back = back - box(cx - amp['cutout_w'] / 2, D - T - 1, P['amp_z'] - amp['cutout_h'] / 2,
                      cx + amp['cutout_w'] / 2, D, P['amp_z'] + amp['cutout_h'] / 2)

    puck, mouth_r = waveguide(P, cx, P['tweeter_z'])
    woofer, _ = driver_part('woofer', P['woofer'], wf, centre=(cx, 0.0, P['woofer_z']))
    # the tweeter's faceplate on the puck's back face, facing forward
    tweeter, _ = driver_part('tweeter', P['tweeter'], tw, centre=(cx, g['depth'], P['tweeter_z']))
    plate = box(cx - amp['plate_w'] / 2, D - 3.0, P['amp_z'] - amp['plate_h'] / 2, cx + amp['plate_w'] / 2, D, P['amp_z'] + amp['plate_h'] / 2)
    module = box(cx - amp['cutout_w'] / 2 + 4, D - amp['depth'], P['amp_z'] - amp['cutout_h'] / 2 + 6,
                 cx + amp['cutout_w'] / 2 - 4, D - 3.0, P['amp_z'] + amp['cutout_h'] / 2 - 6)

    feet = []
    for i, (fx, fy) in enumerate([(P['foot_in'], P['foot_in']), (W - P['foot_in'], P['foot_in']),
                                  (P['foot_in'], D - P['foot_in']), (W - P['foot_in'], D - P['foot_in'])]):
        f = cyl('z', (fx, fy), P['foot_d'], -P['foot_h'], 0.0)
        feet.append(Part(f'foot-{i + 1}', f, Machined('oak', 'lathe'), finish='oak', group='feet'))

    return [
        Part('left', box(0, 0, 0, T, D, H), ply('z'), finish='birch', group='cabinet'),
        Part('right', box(W - T, 0, 0, W, D, H), ply('z'), finish='birch', group='cabinet'),
        Part('top', box(T, 0, H - T, W - T, D, H), ply('x'), finish='birch', group='cabinet'),
        Part('bottom', box(T, 0, 0, W - T, D, T), ply('x'), finish='birch', group='cabinet'),
        Part('baffle', baffle, Sheet('baltic-birch', T, face='-y', grain='z'), finish='birch', group='cabinet'),
        Part('back', back, Sheet('baltic-birch', T, face='+y', grain='z'), finish='birch', group='cabinet'),
        Part('waveguide', puck, Printed('resin-tough', orient='front face down'), finish='waveguide', group='tweeter',
             notes=[f'oblate-spheroidal, r0 {g["r0"]:g}, {g["angle"]:g} degrees, mouth {2 * mouth_r:.0f} across']),
        woofer, tweeter,
        Part('amp-plate', plate.fuse(module), Bought(P['amp']), finish='amp'),
        *feet,
        Part('woofer-fixings', None, Bought('m4-tnut-set')),
        Part('gasket', None, Bought('gasket-foam')),
        Part('damping', None, Bought('damping-fill')),
        Part('amp-fixings', None, Bought('amp-screws')),
        Part('cable', None, Bought('speaker-cable-1m')),
        Part('terminals', None, Bought('push-on-terminal'), qty=4),
    ]


PRODUCT = Product(
    'birchbox', 'Birch Box', 'Two-way active bookshelf speaker (the kit\'s example)', params=P, parts=parts,
    notes=['Glue-up: sides to the bottom, then the baffle and back, then the top; wood glue, clamped 1 h each.',
           'Fit the drivers on their gaskets with the T-nuts hammered in from inside before the back goes on.',
           'The amplifier\'s screw holes are drilled from the plate in hand (Hypex does not publish the pattern).',
           'Hypex advises a sealed box round the module; this example leaves it out for clarity.',
           'Oil the plywood; print the waveguide in black or spray it satin black.'],
    materials={'birch': {'preset': 'birch'}, 'oak': {'preset': 'veneer', 'color': '#b08a5a'},
               'waveguide': {'preset': 'satin_paint', 'color': '#1c1c1c'}, 'amp': {'preset': 'metal', 'color': '#2a2a2a'},
               'driver-frame': {'preset': 'satin_paint', 'color': '#202020'}, 'driver-cone': {'preset': 'paper_cone'},
               'driver-surround': {'preset': 'rubber', 'color': '#141414'}, 'driver-cap': {'preset': 'paper_cone'},
               'driver-dome': {'preset': 'dome'}, 'driver-motor': {'preset': 'metal', 'color': '#3a3a3a'},
               'driver-magnet': {'preset': 'satin_paint', 'color': '#2b2b2b'}, 'driver-coil': {'preset': 'metal', 'color': '#b87333'},
               'driver-spider': {'preset': 'rubber', 'color': '#c8b88a'}},
)


if __name__ == '__main__':
    # the box's numbers from its sizes: net volume, and the sealed alignment with the woofer from the library
    from speaker.box import sealed
    W, D, H, T = P['W'], P['D'], P['H'], P['T']
    gross = (W - 2 * T) * (D - 2 * T) * (H - 2 * T) / 1e6
    net = gross - 0.63 - 0.5 - 0.3          # woofer, amplifier module, tweeter and waveguide (displacements, estimated)
    r = sealed(LIB[P['woofer']]['ts'], net)
    print(f'gross {gross:.1f} L, net {net:.1f} L: {r}')
