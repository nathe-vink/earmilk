"""barkhorn (a working name): a two-way hybrid horn loudspeaker in the manner of Friendly Pressure's modular horns
(a big paper-cone bass cabinet with a round wooden horn on top, after the vintage Altec, JBL and Tannoy monitors),
in two finishes: birch bark and eucalyptus bark, each horn painted from its bark's colours.

    .venv-fab/bin/python studio/fabkit/build.py spinoffs/barkhorn/product.py
    .venv-fab/bin/python spinoffs/barkhorn/product.py            # the bass box's numbers

Drawn from descriptions of Friendly Pressure's work, not from the owner's reference photograph (resistormag.com is
blocked from this environment): the layout, the proportions and the horn's shape are proposals to adjust once the
photograph can be seen. Parts from the horn-speaker research of 2026-10-10 (components.json): FaitalPRO 15PR400-8
woofer (treated paper cone), BMS 4550-16 compression driver (polyester diaphragm, crossed at 800 Hz or above) on a
round tractrix horn, a Hypex FusionAmp FA122 doing the crossover.
"""
import math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'studio', 'fabkit'))
from kit import *                                                    # noqa: E402,F403
from speaker.drivers import driver_part, place                      # noqa: E402
from speaker.horn import tractrix, round_horn, outer_radius_at      # noqa: E402

import json  # noqa: E402
LIB = json.load(open(os.path.join(HERE, '..', '..', 'studio', 'fabkit', 'library', 'components.json')))
LIB.update(json.load(open(os.path.join(HERE, 'components.json'))))

P = dict(
    W=520.0, D=460.0, H=760.0, T=18.0, feet_h=30.0,                  # the bass cabinet, outside; it stands on four feet
    woofer='faital-15pr400-8', woofer_z=470.0,                       # centre height above the cabinet's underside
    ports=2, port_bore=100.0, port_wall=5.0, port_flange=(130.0, 5.0), port_z=140.0, port_dx=120.0, fb=38.0,
    gasket=1.0,
    brace_z=260.0, brace_window=(380.0, 320.0),                      # a window brace under the woofer, above the ports
    amp='hypex-fa122', amp_z=420.0,
    horn_fc=320.0, horn_r0=12.7, horn_wall=12.0, horn_lip=25.0,      # a 1 in throat to a mouth that holds to about 320 Hz
    horn_flange=dict(d=130.0, t=12.0, bolt_d=76.2, bolts=2, bolt_hole=6.5),
    hf='bms-4550-16',
    horn_clear=10.0,                                                 # the roll's underside above the cabinet's top
    saddles=(70.0, 300.0), saddle_w=(300.0, 150.0), felt=3.0,        # back from the mouth; widths
    foot_d=60.0, foot_in=55.0,
)


def port_length(P, net_l):
    """Each port's length for `ports` round ports tuning `net_l` litres to fb (one end flanged, one free)."""
    c = 343.0
    sp = math.pi * (P['port_bore'] / 2000) ** 2
    w = 2 * math.pi * P['fb']
    return (P['ports'] * sp * c * c / (w * w * net_l * 1e-3) - 0.732 * P['port_bore'] / 1000) * 1000


def net_volume(P, port_l=None):
    W, D, H, T = P['W'], P['D'], P['H'], P['T']
    gross = (W - 2 * T) * (D - 2 * T) * (H - 2 * T) / 1e6
    od = P['port_bore'] + 2 * P['port_wall']
    ports = P['ports'] * math.pi * (od / 2000) ** 2 * ((port_l or 160.0) / 1000) * 1000
    brace = ((W - 2 * T) * (D - 2 * T) - P['brace_window'][0] * P['brace_window'][1]) * T / 1e6
    return gross - 4.5 - 1.3 - ports - brace          # woofer (estimated), amplifier module, ports, brace


def horn_profile(P):
    return tractrix(P['horn_fc'], P['horn_r0'], n=60)


def parts(P):
    W, D, H, T = P['W'], P['D'], P['H'], P['T']
    z0 = P['feet_h']
    cx = W / 2
    wf = LIB[P['woofer']]['geom']; amp = LIB[P['amp']]['geom']; hf = LIB[P['hf']]['geom']
    plen = round(port_length(P, net_volume(P)), 1)
    ply = lambda grain, face=None: Sheet('baltic-birch', T, face=face, grain=grain)

    # the baffle: the woofer flush in a rebate for its flange and gasket, its T-nut holes, two flanged ports below
    baffle = box(T, 0, z0 + T, W - T, T, z0 + H - T)
    wz = z0 + P['woofer_z']
    baffle -= cyl('y', (cx, wz), wf['frame_od'] + 1.6, -1, wf['flange_t'] + P['gasket'])
    baffle -= cyl('y', (cx, wz), wf['cutout'], -1, T + 1)
    for k in range(wf['bolts']):
        a = 2 * math.pi * (k + 0.5) / wf['bolts']
        baffle -= cyl('y', (cx + wf['bolt_d'] / 2 * math.cos(a), wz + wf['bolt_d'] / 2 * math.sin(a)), 7.0, -1, T + 1)
    od = P['port_bore'] + 2 * P['port_wall']
    fd, ft = P['port_flange']
    pz = z0 + P['port_z']
    port_x = [cx - P['port_dx'], cx + P['port_dx']][:P['ports']]
    for px in port_x:
        baffle -= cyl('y', (px, pz), fd + 0.5, -1, ft)
        baffle -= cyl('y', (px, pz), od + 0.4, -1, T + 1)

    # the back: the amplifier's plate flush in its 4.5 mm rebate, the module through Hypex's cut-out; a hole for the
    # horn's cable into the box, by the amplifier
    back = box(T, D - T, z0 + T, W - T, D, z0 + H - T)
    az = z0 + P['amp_z']
    back -= box(cx - (amp['plate_w'] + 0.5) / 2, D - 4.5, az - (amp['plate_h'] + 0.5) / 2, cx + (amp['plate_w'] + 0.5) / 2, D + 1, az + (amp['plate_h'] + 0.5) / 2)
    back -= box(cx - amp['cutout_w'] / 2, D - T - 1, az - amp['cutout_h'] / 2, cx + amp['cutout_w'] / 2, D, az + amp['cutout_h'] / 2)

    top = box(T, 0, z0 + H - T, W - T, D, z0 + H)
    top -= cyl('z', (cx, D - 60.0), 16.5, z0 + H - T - 1, z0 + H + 1)        # the horn's cable, through an M16 gland
    brace = box(T, T, z0 + P['brace_z'], W - T, D - T, z0 + P['brace_z'] + T)
    bw, bd = P['brace_window']
    brace -= box(cx - bw / 2, D / 2 - bd / 2, z0 + P['brace_z'] - 1, cx + bw / 2, D / 2 + bd / 2, z0 + P['brace_z'] + T + 1)

    out = [
        Part('left', box(0, 0, z0, T, D, z0 + H), ply('z'), finish='bark', group='cabinet'),
        Part('right', box(W - T, 0, z0, W, D, z0 + H), ply('z'), finish='bark', group='cabinet'),
        Part('top', top, ply('x', '+z'), finish='bark', group='cabinet'),
        Part('bottom', box(T, 0, z0, W - T, D, z0 + T), ply('x'), finish='bark', group='cabinet'),
        Part('baffle', baffle, ply('z', '-y'), finish='bark', group='cabinet'),
        Part('back', back, ply('z', '+y'), finish='bark', group='cabinet'),
        Part('brace', brace, ply('x', '+z'), finish='raw', group='cabinet', inside=True),
    ]

    # the ports: printed tubes, flange flush in the baffle, `plen` long from the baffle's face
    for i, px in enumerate(port_x, 1):
        tube = cyl('y', (px, pz), fd, 0, ft) + cyl('y', (px, pz), od, ft, plen)
        tube -= cyl('y', (px, pz), P['port_bore'], -1, plen + 1)
        out.append(Part(f'port-{i}', tube, Printed('asa', orient='flange down'), finish='port', group='ports',
                        notes=[f'{plen:.0f} long tunes the box to {P["fb"]:g} Hz; print 15 longer and trim to tune by impedance']))

    woofer, _ = driver_part('woofer', P['woofer'], wf, centre=(cx, 0.0, wz))
    out.append(woofer)
    plate = box(cx - amp['plate_w'] / 2, D - 3.0, az - amp['plate_h'] / 2, cx + amp['plate_w'] / 2, D, az + amp['plate_h'] / 2)
    module = box(cx - amp['cutout_w'] / 2 + 4, D - amp['depth'], az - amp['cutout_h'] / 2 + 6, cx + amp['cutout_w'] / 2 - 4, D - 3.0, az + amp['cutout_h'] / 2 - 6)
    out.append(Part('amp-plate', plate.fuse(module), Bought(P['amp']), finish='amp'))

    # the horn on top: its mouth flush with the cabinet's front, its axis high enough that the rolled lip clears the top
    prof = horn_profile(P)
    L = prof[-1][0]
    shell, liner = round_horn(prof, P['horn_wall'], P['horn_flange'], P['horn_lip'], liner=0.4)
    r_max = shell.bounding_box().max.X
    za = z0 + H + r_max + P['horn_clear']
    C = (cx, L, za)                                         # the throat; the mouth at y = 0
    horn_w = place(shell, C, (0, -1, 0))
    horn_l = place(liner, C, (0, -1, 0))
    out.append(Part('horn', horn_w, Machined('birch-hardwood', 'cnc-lathe'), finish='horn-out', group='horn',
                    pieces={'shell': (horn_w, 'horn-out'), 'bell': (horn_l, 'horn-in')},
                    notes=[f'tractrix to {P["horn_fc"]:g} Hz, 1 in throat, mouth {2 * prof[-1][1]:.0f} across, {L:.0f} long, '
                           f'{P["horn_wall"]:g} wall, lip rolled on {P["horn_lip"]:g}: laminated birch rings, turned, sealed and painted '
                           '(or the bought beech Le Cleac\'h horn, components.json)']))
    hfp, _ = driver_part('hf', P['hf'], hf, centre=(cx, L + P['horn_flange']['t'], za))
    out.append(hfp)

    # two saddles carry it, felt-lined, each notched to the horn's outside where it stands; a strap holds it down
    for i, (back_from_mouth, sw) in enumerate(zip(P['saddles'], P['saddle_w']), 1):
        x = L - back_from_mouth                             # along the horn from its throat
        r = outer_radius_at(prof, x, P['horn_wall'], P['horn_lip']) + P['felt']
        y = back_from_mouth
        s = box(cx - sw / 2, y - T / 2, z0 + H, cx + sw / 2, y + T / 2, za)
        s -= cyl('y', (cx, za), 2 * r, y - T, y + T)
        out.append(Part(f'saddle-{i}', s, Sheet('baltic-birch', T, face='-y'), finish='saddle', group='horn',
                        notes=[f'notch r {r:.1f} at {back_from_mouth:g} behind the mouth, lined with 3 mm felt']))

    for i, (fx, fy) in enumerate([(P['foot_in'], P['foot_in']), (W - P['foot_in'], P['foot_in']),
                                  (P['foot_in'], D - P['foot_in']), (W - P['foot_in'], D - P['foot_in'])], 1):
        out.append(Part(f'foot-{i}', cyl('z', (fx, fy), P['foot_d'], 0.0, z0), Machined('oak', 'lathe'), finish='foot', group='feet'))

    out += [
        Part('woofer-fixings', None, Bought('m4-tnut-set'), qty=2, notes=['M6 in practice: the 15PR400 takes M6; buy 8 M6 T-nuts and screws']),
        Part('hf-fixings', None, Bought('m6-hf-screws')),
        Part('gasket', None, Bought('gasket-foam'), qty=2),
        Part('damping', None, Bought('damping-fill'), qty=2),
        Part('amp-fixings', None, Bought('amp-screws')),
        Part('cable', None, Bought('speaker-cable-1m'), qty=3),
        Part('terminals', None, Bought('push-on-terminal'), qty=4),
        Part('hf-pad', None, Bought('attenuator-l-pad')),
        Part('strap', None, Bought('horn-strap')),
        Part('felt', None, Bought('felt-tape')),
    ]
    return out


PRODUCT = Product(
    'barkhorn', 'barkhorn', 'Two-way hybrid horn loudspeaker, birch bark or eucalyptus bark', params=P, parts=parts,
    touching=[('saddle-*', 'horn')],          # the felt's 3 mm is in the notch; the horn rests in it
    notes=['Bark: real birch bark sheet (Betula papyrifera, from fallen or felled trees) laminated to the plywood with PVA in a vacuum bag, sealed with a matt waterborne lacquer; for eucalyptus, the shed bark of a smooth-barked gum (spotted or snow gum) pressed flat and laminated the same way, or a UV-printed veneer of it. Approve a sample board first.',
           'Glue-up: sides to the bottom, the brace, then the baffle and back, then the top.',
           'The woofer flush in its rebate on a gasket, eight M6 T-nuts from inside; the ports pushed in dry, trimmed to tune (impedance minimum at fb), then bonded.',
           'The FA122 crosses at about 800 Hz (LR4) with the HF channel about 14 dB down, part of it in the passive L-pad after the amplifier, so its hiss stays inaudible through a 113 dB driver.',
           'The horn rests in its felt-lined saddles, strapped down; its cable runs through an M16 gland in the top.',
           'Hypex advises a sealed box round the amplifier module (left out here, as in the kit\'s example).'],
    materials={'bark': {'preset': '$bark'}, 'raw': {'preset': 'birch'},
               'horn-out': {'preset': 'satin_paint', 'color': '$horn_out', 'roughness': 0.5, 'specular': 0.35},
               'horn-in': {'preset': 'satin_paint', 'color': '$horn_in', 'roughness': 0.55, 'specular': 0.3},
               'saddle': {'preset': 'satin_paint', 'color': '$saddle', 'roughness': 0.5, 'specular': 0.35},
               'foot': {'preset': 'satin_paint', 'color': '$saddle', 'roughness': 0.5},
               'port': {'preset': 'satin_paint', 'color': '#1C1A18', 'roughness': 0.6},
               'amp': {'preset': 'metal', 'color': '#2A2A2A'},
               'driver-frame': {'preset': 'satin_paint', 'color': '#1E1E1E'}, 'driver-cone': {'preset': 'paper_cone'},
               'driver-surround': {'preset': 'rubber', 'color': '#151515'}, 'driver-cap': {'preset': 'paper_cone'},
               'driver-motor': {'preset': 'metal', 'color': '#3A3A3A'}, 'driver-magnet': {'preset': 'satin_paint', 'color': '#2B2B2B'},
               'driver-coil': {'preset': 'metal', 'color': '#B87333'}, 'driver-spider': {'preset': 'rubber', 'color': '#C8B88A'},
               'driver-plug': {'preset': 'metal', 'color': '#8A8A8A'}},
    # each horn from its bark: birch's chalk white (the bell a shade deeper so its depth reads) on charcoal saddles,
    # the lenticels' colour; eucalyptus's sage outside, its salmon inside, on the bark's warm grey
    variants={'birch': {'bark': 'birch_bark', 'horn_out': '#E9E3D7', 'horn_in': '#DAD2C3', 'saddle': '#2B2724'},
              'eucalyptus': {'bark': 'eucalyptus_bark', 'horn_out': '#97A38B', 'horn_in': '#C99B86', 'saddle': '#B9B3A5'}},
)


if __name__ == '__main__':
    from speaker.box import vented, suggest_vented
    ts = LIB[P['woofer']]['ts']
    net = net_volume(P)
    pl = port_length(P, net)
    net = net_volume(P, pl)
    print(f"QB3 start: {suggest_vented(ts)} (L, Hz)")
    print(f"net {net:.1f} L, {P['ports']} x {P['port_bore']:g} ports {pl:.0f} long")
    r = vented(ts, net, P['fb'], bore_mm=P['port_bore'] * math.sqrt(P['ports']))
    print(r)
    prof = horn_profile(P)
    print(f"horn: {prof[-1][0]:.0f} long, mouth {2 * prof[-1][1]:.0f}")
