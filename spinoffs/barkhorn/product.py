"""barkhorn (a working name): a two-way horn loudspeaker after the owner's reference photograph of Friendly Pressure's
speakers (reference/friendly-pressure-owner-2026-10-10.jpg), in two finishes: birch bark and eucalyptus bark, each
with its waveguide cast in a translucent resin tinted from its bark.

    .venv-fab/bin/python studio/fabkit/build.py spinoffs/barkhorn/product.py
    .venv-fab/bin/python spinoffs/barkhorn/product.py            # the bass box's numbers

What the photograph shows, and how it is read here:
- a bass cabinet about 1 : 1.6 (wide to tall), a thin wooden shell (walnut there; bark here) framing a pale front
  panel set back in it;
- a 15 in black paper cone in a wide off-white ring, its centre a little above the cabinet's middle;
- a small square port at the bottom right;
- a frosted, translucent waveguide on top: a rounded rectangle about 2.1 : 1, wider than the cabinet (about 1.14
  times), the driver's dark throat at its centre, floating on four thin rods.
Sizes are scaled from the photograph by its turntable (about 450 wide): the cabinet about 560 x 880, the waveguide
about 640 x 300, the gap 80.

Parts from the horn-speaker research of 2026-10-10 (components.json): FaitalPRO 15PR400-8 woofer (treated paper cone),
BMS 4550-16 compression driver (polyester diaphragm, crossed at 800 Hz or above), a Hypex FusionAmp FA122.
"""
import math, os, random, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'studio', 'fabkit'))
from kit import *                                                    # noqa: E402,F403
from speaker.drivers import driver_part, place                      # noqa: E402
from speaker.horn import waveguide_shell                            # noqa: E402

import json  # noqa: E402
LIB = json.load(open(os.path.join(HERE, '..', '..', 'studio', 'fabkit', 'library', 'components.json')))
LIB.update(json.load(open(os.path.join(HERE, 'components.json'))))

P = dict(
    W=560.0, D=420.0, H=880.0, T=18.0,           # the cabinet's shell, outside; it stands on the floor on glides
    inset=24.0,                                  # the front panel set back in the shell (the photograph's frame): deep
                                                 # enough for a cover to clear the cone at twice its Xmax
    woofer='faital-15pr400-8', woofer_z=478.0,   # its centre 45.7 % down from the top, as photographed
    gasket=1.0,
    ring=dict(od=436.0, id=350.0, t=6.0),        # the off-white ring over the frame, 6 mm MDF, standing on the panel
    port=dict(a=100.0, wall=4.0, x=455.0, z=113.0),   # the square port, bottom right, as photographed
    fb=38.0,
    brace_z=200.0, brace_window=(420.0, 300.0),
    amp='hypex-fa122', amp_z=520.0,
    hf='bms-4550-16',
    # the waveguide: a hollow cast shell, a rounded rectangle 640 x 300, 170 deep, its mouth filling the face (612 x 272)
    horn=dict(mouth_w=612.0, mouth_h=272.0, d=170.0, r0=12.7, wall=6.0, rim=10.0, n_mouth=4.5,
              pod_r=74.0, pod_back=70.0, dome=45.0, boss=dict(d=130.0, t=12.0, bolt_d=76.2, bolts=2, bolt_hole=6.5)),
    gap=80.0, rod_d=10.0, rods_front=(150.0, 40.0),   # the two front rods: +-x from the centre, y back from the face
    # the front's covers, options (the photograph shows the panel bare), each in the recess in front of the panel, 1.5
    # clear of the shell all round: a cloth grille (an MDF frame, the cloth stretched over it), a slotted grille
    # (lenticels for birch: short horizontal dashes; strips for eucalyptus: long vertical ones), each flush with the
    # shell's front on four pegs into cups in the panel's corners; or the panel faced in bark or cork round the ring
    # and the port
    cover=dict(gap=1.5, cloth_face=1.0, frame_t=6.0, frame_w=30.0, bar_z=205.0, bar_w=24.0,
               grille_t=6.0, border=22.0, slot_w=6.0,
               lenticel=dict(pitch=14.0, length=(22.0, 120.0), gap=(10.0, 34.0), seed=11),
               strips=dict(pitch=16.0, length=(90.0, 260.0), gap=(14.0, 30.0), seed=5),
               face_t=dict(bark=1.0, cork=3.0)),
)


def lenticels(x0, z0, x1, z1, w, pitch, length, gap, seed):
    """Birch's lenticels as a grille's slots: rows of short horizontal dashes, their lengths and gaps random (seeded,
    so a rebuild cuts the same panel), most short, a few long, and each row starting at its own offset."""
    rng = random.Random(seed)
    out, z = [], z0 + w / 2
    while z <= z1 - w / 2:
        x = x0 + rng.uniform(0.0, length[0])
        while True:
            L = rng.uniform(*length) if rng.random() < 0.25 else rng.uniform(length[0], (length[0] + length[1]) / 2.5)
            L = min(L, x1 - x)
            if L < length[0]:
                break
            out.append((x + L / 2, z, L, w, False))
            x += L + rng.uniform(*gap)
        z += pitch
    return out


def strips(x0, z0, x1, z1, w, pitch, length, gap, seed):
    """A eucalyptus's strips as a grille's slots: columns of long vertical slots, their lengths and the bridges
    between them random (seeded), so the slats between the columns are tied every 90 to 260."""
    rng = random.Random(seed)
    out, x = [], x0 + w / 2
    while x <= x1 - w / 2:
        z = z0 + rng.uniform(0.0, length[0] * 0.6)
        while True:
            L = min(rng.uniform(*length), z1 - z)
            if L < length[0] * 0.5:
                break
            out.append((x, z + L / 2, L, w, True))
            z += L + rng.uniform(*gap)
        x += pitch
    return out


def port_length(P, net_l):
    """The square port's length tuning `net_l` litres to fb (one end flanged, one free; the end correction of the
    round port of the same area)."""
    c, a = 343.0, P['port']['a'] / 1000
    sp = a * a
    d_eq = 2 * a / math.sqrt(math.pi)
    w = 2 * math.pi * P['fb']
    return (sp * c * c / (w * w * net_l * 1e-3) - 0.732 * d_eq) * 1000


def net_volume(P, port_l=60.0):
    W, D, H, T = P['W'], P['D'], P['H'], P['T']
    inner = (W - 2 * T) * (D - T - (P['inset'] + T)) * (H - 2 * T) / 1e6
    o = P['port']['a'] + 2 * P['port']['wall']
    port = o * o * port_l / 1e6
    brace = ((W - 2 * T) * (D - P['inset'] - 3 * T) - P['brace_window'][0] * P['brace_window'][1]) * T / 1e6
    return inner - 4.5 - 1.3 - port - brace      # woofer (estimated), amplifier module, port, brace


def parts(P):
    W, D, H, T = P['W'], P['D'], P['H'], P['T']
    cx = W / 2
    yb = P['inset']                                   # the front panel's face
    wf = LIB[P['woofer']]['geom']; amp = LIB[P['amp']]['geom']; hf = LIB[P['hf']]['geom']
    pt = P['port']
    plen = round(port_length(P, net_volume(P)), 1)
    ply = lambda grain, face=None: Sheet('baltic-birch', T, face=face, grain=grain)

    # the front panel, set back in the shell: the woofer flush in its rebate, its T-nut holes, the square port
    baffle = box(T, yb, T, W - T, yb + T, H - T)
    wz = P['woofer_z']
    baffle -= cyl('y', (cx, wz), wf['frame_od'] + 1.6, yb - 1, yb + wf['flange_t'] + P['gasket'])
    baffle -= cyl('y', (cx, wz), wf['cutout'], yb - 1, yb + T + 1)
    for k in range(wf['bolts']):
        a = 2 * math.pi * (k + 0.5) / wf['bolts']
        baffle -= cyl('y', (cx + wf['bolt_d'] / 2 * math.cos(a), wz + wf['bolt_d'] / 2 * math.sin(a)), 7.0, yb - 1, yb + T + 1)
    o = pt['a'] + 2 * pt['wall']
    baffle -= box(pt['x'] - o / 2 - 0.2, yb - 1, pt['z'] - o / 2 - 0.2, pt['x'] + o / 2 + 0.2, yb + T + 1, pt['z'] + o / 2 + 0.2)

    back = box(T, D - T, T, W - T, D, H - T)
    az = P['amp_z']
    back -= box(cx - (amp['plate_w'] + 0.5) / 2, D - 4.5, az - (amp['plate_h'] + 0.5) / 2, cx + (amp['plate_w'] + 0.5) / 2, D + 1, az + (amp['plate_h'] + 0.5) / 2)
    back -= box(cx - amp['cutout_w'] / 2, D - T - 1, az - amp['cutout_h'] / 2, cx + amp['cutout_w'] / 2, D, az + amp['cutout_h'] / 2)

    # the top: inserts for the waveguide's three rods (two under its mouth, one under the driver's pod), and the HF
    # cable's gland behind them
    top = box(T, 0, H - T, W - T, D, H)
    hz = P['horn']
    rods = [(cx - P['rods_front'][0], P['rods_front'][1]), (cx + P['rods_front'][0], P['rods_front'][1]),
            (cx, hz['d'] + hz['pod_back'] * 0.5)]
    for rx, ry in rods:
        top -= cyl('z', (rx, ry), 12.0, H - 15.0, H + 1)          # M8 threaded inserts, 12 drilled 15 deep
    top -= cyl('z', (cx, D - 70.0), 16.5, H - T - 1, H + 1)
    bottom = box(T, 0, 0, W - T, D, T)
    brace = box(T, yb + T, P['brace_z'], W - T, D - T, P['brace_z'] + T)
    bw, bd = P['brace_window']
    ym = (yb + T + D - T) / 2
    brace -= box(cx - bw / 2, ym - bd / 2, P['brace_z'] - 1, cx + bw / 2, ym + bd / 2, P['brace_z'] + T + 1)

    out = [
        Part('left', box(0, 0, 0, T, D, H), ply('z'), finish='bark', group='cabinet'),
        Part('right', box(W - T, 0, 0, W, D, H), ply('z'), finish='bark', group='cabinet'),
        Part('top', top, ply('x', '+z'), finish='bark', group='cabinet'),
        Part('bottom', bottom, ply('x', '-z'), finish='bark', group='cabinet'),
        Part('front-panel', baffle, ply('z', '-y'), finish='panel', group='cabinet'),
        Part('back', back, ply('z', '+y'), finish='bark', group='cabinet'),
        Part('brace', brace, ply('x', '+z'), finish='raw', group='cabinet', inside=True),
    ]

    # the ring over the woofer's frame, standing on the panel; the square port's tube, printed
    r = P['ring']
    ring = cyl('y', (cx, wz), r['od'], yb - r['t'], yb) - cyl('y', (cx, wz), r['id'], yb - r['t'] - 1, yb + 1)
    for k in range(wf['bolts']):          # pockets behind it for the woofer's screw heads: it lies flat over the frame
        a = 2 * math.pi * (k + 0.5) / wf['bolts']
        ring -= cyl('y', (cx + wf['bolt_d'] / 2 * math.cos(a), wz + wf['bolt_d'] / 2 * math.sin(a)), 14.0, yb - 4.0, yb + 1)
    out.append(Part('woofer-ring', ring, Sheet('mdf', r['t'], face='-y'), finish='ring', group='cabinet',
                    notes=['sprayed in the ring colour; held by four dots of silicone on the panel; eight pockets behind it '
                           'clear the woofer\'s screw heads']))
    tube = box(pt['x'] - o / 2, yb, pt['z'] - o / 2, pt['x'] + o / 2, yb + plen, pt['z'] + o / 2)
    tube -= box(pt['x'] - pt['a'] / 2, yb - 1, pt['z'] - pt['a'] / 2, pt['x'] + pt['a'] / 2, yb + plen + 1, pt['z'] + pt['a'] / 2)
    out.append(Part('port', tube, Printed('asa', orient='on end'), finish='port', group='cabinet',
                    notes=[f'{pt["a"]:g} square, {plen:.0f} long from the panel\'s face: tunes the box to {P["fb"]:g} Hz; print 15 longer and trim to tune']))

    woofer, _ = driver_part('woofer', P['woofer'], wf, centre=(cx, yb, wz))
    out.append(woofer)
    plate = box(cx - amp['plate_w'] / 2, D - 3.0, az - amp['plate_h'] / 2, cx + amp['plate_w'] / 2, D, az + amp['plate_h'] / 2)
    module = box(cx - amp['cutout_w'] / 2 + 4, D - amp['depth'], az - amp['cutout_h'] / 2 + 6, cx + amp['cutout_w'] / 2 - 4, D - 3.0, az + amp['cutout_h'] / 2 - 6)
    out.append(Part('amp-plate', plate.fuse(module), Bought(P['amp']), finish='amp'))

    # the waveguide: a thin shell following its flare, a pod behind hiding the driver, its face flush with the
    # cabinet's front and its mouth's lower rim `gap` above the top; it stands on three rods cut to its underside
    zc = H + P['gap'] + hz['mouth_h'] / 2 + hz['rim']
    shell, cap = waveguide_shell(hz['mouth_w'], hz['mouth_h'], hz['d'], r0=hz['r0'], wall=hz['wall'], rim=hz['rim'],
                                 n_mouth=hz['n_mouth'], pod_r=hz['pod_r'], pod_back=hz['pod_back'], dome=hz['dome'], boss=hz['boss'])
    shell = place(shell, (cx, hz['d'], zc), (0, -1, 0))
    cap = place(cap, (cx, hz['d'], zc), (0, -1, 0))
    out.append(Part('waveguide', shell, Machined('cast-resin', 'cast', setup_usd=900.0), finish='horn', group='horn',
                    notes=[f'mouth {hz["mouth_w"]:g} x {hz["mouth_h"]:g}, {hz["d"]:g} deep, 1 in throat; a shell {hz["wall"]:g} thick following '
                           f'its flare, {hz["rim"]:g} at the rim, and a pod {2 * hz["pod_r"]:g} across behind it round the driver; cast in tinted '
                           'translucent polyurethane in a two-part silicone mould from a CNC-cut plug, bead-blasted to frost; '
                           'M8 inserts bonded into pads inside its underside take the rods']))
    out.append(Part('waveguide-cap', cap, Machined('cast-resin', 'cast', setup_usd=250.0), finish='horn', group='horn',
                    notes=['closes the pod behind the driver; a spigot locates it, three M4 screws hold it; the cable leaves through its centre']))
    hfp, _ = driver_part('hf', P['hf'], hf, centre=(cx, hz['d'] + hz['boss']['t'], zc))
    out.append(hfp)
    from build123d import Axis
    for i, (rx, ry) in enumerate(rods, 1):
        # where the rod meets the shell's underside: the lowest hit over its axis and its rim, so no edge pokes in
        ztop = 1e9
        for a in [None] + [2 * math.pi * k / 12 for k in range(12)]:
            px, py = (rx, ry) if a is None else (rx + P['rod_d'] / 2 * math.cos(a), ry + P['rod_d'] / 2 * math.sin(a))
            hits = shell.find_intersection_points(Axis((px, py, H + 1.0), (0, 0, 1)))
            ztop = min([ztop] + [h[0].Z for h in hits if h[0].Z > H + 1.0])
        ztop -= 0.2
        out.append(Part(f'rod-{i}', cyl('z', (rx, ry), P['rod_d'], H, ztop), Machined('stainless', 'lathe'), finish='rod',
                        group='horn', notes=[f'{ztop - H:.0f} long; M8 thread 15 deep each end']))

    out += covers(P, wz, o)
    out += [
        Part('bark', None, Bought('bark-sheet'), qty=2, notes=['about 1.75 m2 a speaker: the shell\'s sides, top, bottom, back and front edges']),
        Part('woofer-fixings', None, Bought('m6-tnut-set'), notes=['the T-nuts hammered in from inside before the glue-up']),
        Part('hf-fixings', None, Bought('m6-hf-screws')),
        Part('gasket', None, Bought('gasket-foam'), qty=2),
        Part('damping', None, Bought('damping-fill'), qty=2),
        Part('amp-fixings', None, Bought('amp-screws')),
        Part('cable', None, Bought('speaker-cable-1m'), qty=3),
        Part('terminals', None, Bought('push-on-terminal'), qty=4),
        Part('hf-pad', None, Bought('attenuator-l-pad')),
        Part('glides', None, Bought('felt-glides')),
    ]
    return out


def covers(P, wz, port_o):
    """The front's covers, options: each in the recess in front of the panel (y 0 to 12), 1.5 clear of the shell."""
    W, H, T = P['W'], P['H'], P['T']
    cv, r, pt = P['cover'], P['ring'], P['port']
    cx, yb = W / 2, P['inset']
    x0, x1, z0, z1 = T + cv['gap'], W - T - cv['gap'], T + cv['gap'], H - T - cv['gap']
    out = []
    # the cloth grille: a 6 mm MDF frame (a border and a bar between the ring and the port) under acoustically
    # transparent cloth, stretched over its face and round its edges and glued behind; its face 1 back from the
    # shell's front; four pegs behind its corners
    yf = cv['cloth_face'] + 0.5
    fw, ft = cv['frame_w'], cv['frame_t']
    frame = box(x0 + 0.5, yf, z0 + 0.5, x1 - 0.5, yf + ft, z1 - 0.5) - box(x0 + fw, yf - 1, z0 + fw, x1 - fw, yf + ft + 1, z1 - fw)
    frame += box(x0 + fw - 1, yf, cv['bar_z'] - cv['bar_w'] / 2, x1 - fw + 1, yf + ft, cv['bar_z'] + cv['bar_w'] / 2)
    out.append(Part('cloth-frame', frame, Sheet('mdf', ft), finish='black', option='cloth', render=False,
                    notes=['sprayed black so it cannot show through the cloth; its face edges rounded so they cannot cut it; a peg '
                           'glued into each corner (25 in from its edges) meets a cup in the panel']))
    cloth = box(x0, cv['cloth_face'], z0, x1, yf + ft + 0.5, z1)
    out.append(Part('grille-cloth', cloth, Bought('grille-cloth'), finish='cloth', option='cloth',
                    notes=['stretched over the frame\'s face and round its edges, stapled or glued behind; the weave square to the frame']))
    out.append(Part('grille-pegs', None, Bought('grille-pegs'), option='cloth',
                    notes=['the cups in four 10 mm holes 12 deep in the panel\'s corners, 25 in from the recess\'s edges']))

    # the slotted grilles: 6 mm plywood, flush with the shell's front, on pegs as the cloth grille; the woofer plays
    # below 800 Hz only, so an open area about a quarter of the face costs it nothing audible (the air behind the grille
    # resonates in its slots near 1.9 kHz, over an octave above the crossover)
    t, b, sw = cv['grille_t'], cv['border'], cv['slot_w']
    for name, opt, fn, stock, fin in (('lenticel', 'lenticel-grille', lenticels, 'baltic-birch', 'grille-paint'),
                                      ('strips', 'strip-grille', strips, 'spotted-gum-ply', 'grille-timber')):
        g = cv[name]
        cuts = fn(x0 + b, z0 + b, x1 - b, z1 - b, sw, g['pitch'], g['length'], g['gap'], g['seed'])
        panel = slotted_panel(x0, z0, x1, z1, 0.0, t, cuts)
        open_pc = 100 * sum((L - sw) * sw + math.pi * sw * sw / 4 for _, _, L, _, _ in cuts) / ((x1 - x0) * (z1 - z0))
        out.append(Part(f'grille-{name}', panel, Sheet(stock, t, face='-y'), finish=fin, option=opt,
                        notes=[f'{len(cuts)} slots {sw:g} wide, round-ended (a {sw:g} mm bit), {open_pc:.0f} % open; '
                               + ('sprayed in the panel\'s colour' if name == 'lenticel' else 'oiled')
                               + '; pegs in its corners as the cloth grille\'s']))
        out.append(Part(f'grille-{name}-pegs', None, Bought('grille-pegs'), option=opt))

    # the facings: bark (1 mm) or cork (3 mm) laid on the panel round the ring and the port before the ring goes on
    holes = [('circle', cx, wz, r['od'] + 1.0), ('rect', pt['x'], pt['z'], port_o + 0.4, port_o + 0.4)]
    for name, make, fin in (('bark', Bought('bark-sheet'), 'bark'), ('cork', Sheet('cork', cv['face_t']['cork'], face='-y'), 'cork')):
        ft = cv['face_t'][name]
        face = slotted_panel(T + 0.5, T + 0.5, W - T - 0.5, H - T - 0.5, yb - ft, yb, holes=holes)
        out.append(Part(f'{name}-face', face, make, finish=fin, option=f'{name}-face',
                        notes=[f'{ft:g} thick, cut round the ring (Ø{r["od"] + 1:g}) and the port; laminated to the panel before the ring goes on']))
    return out


PRODUCT = Product(
    'barkhorn', 'barkhorn', 'Two-way horn loudspeaker after Friendly Pressure, in birch bark or eucalyptus bark', params=P, parts=parts,
    notes=['Bark on the shell (sides, top, bottom and back): real birch bark sheet (Betula papyrifera, from fallen or felled trees) laminated to the plywood with PVA in a vacuum bag and sealed with a matt waterborne lacquer, wrapped round the shell\'s front edges; for eucalyptus, the shed bark of a smooth-barked gum (spotted or snow gum) pressed flat and laminated the same way, or a UV-printed veneer of it. Approve a sample board first.',
           'Glue-up: sides to the bottom, the brace, then the front panel (set back 24 mm), the back, then the top.',
           'The woofer flush in its rebate on a gasket, eight M6 T-nuts from inside, the ring over its frame; the port pushed in dry, trimmed to tune (impedance minimum at fb), then bonded.',
           'The waveguide stands on three 10 mm stainless rods, M8 at both ends, in inserts in the top and in pads cast inside its underside.',
           'Covers (options): a cloth grille, a slotted plywood grille (lenticels or strips), or the panel faced in bark or cork; a grille sits flush with the shell\'s front on four pegs into cups in the panel\'s corners, its back at least 12 clear of the cone at rest (twice the woofer\'s Xmax).',
           'The FA122 crosses at about 800 Hz (LR4) with the HF channel about 14 dB down, part of it in the passive L-pad after the amplifier, so its hiss stays inaudible through a 113 dB driver.',
           'Hypex advises a sealed box round the amplifier module (left out here, as in the kit\'s example).'],
    touching=[('grille-cloth', 'cloth-frame')],                 # the cloth wraps its frame
    materials={'bark': {'preset': '$bark'}, 'raw': {'preset': 'birch'},
               'cloth': {'preset': 'cloth', 'color': '$cloth'},
               'grille-paint': {'preset': 'satin_paint', 'color': '$panel', 'roughness': 0.6, 'specular': 0.3},
               'grille-timber': {'preset': 'birch', 'color': '#8E6E4E', 'roughness': 0.55},
               'cork': {'preset': 'cork', 'color': '$cork'},
               'panel': {'preset': 'satin_paint', 'color': '$panel', 'roughness': 0.6, 'specular': 0.3},
               'ring': {'preset': 'satin_paint', 'color': '$ring', 'roughness': 0.45, 'specular': 0.4},
               'horn': {'preset': 'frosted', 'color': '$horn', 'absorb': '$horn_deep', 'radius': 0.025, 'clear': 0.15, 'roughness': 0.45},
               'rod': {'preset': 'metal', 'color': '#C9C9C6', 'roughness': 0.3},
               'port': {'preset': 'satin_paint', 'color': '#1A1817', 'roughness': 0.7},
               'amp': {'preset': 'satin_paint', 'color': '#303033', 'roughness': 0.4, 'specular': 0.5},   # black anodised plate
               'driver-frame': {'preset': 'satin_paint', 'color': '#1E1E1E'}, 'driver-cone': {'preset': 'paper_cone', 'color': '#1D1B1A'},
               'driver-surround': {'preset': 'rubber', 'color': '#151515'}, 'driver-cap': {'preset': 'paper_cone', 'color': '#1D1B1A'},
               'driver-motor': {'preset': 'metal', 'color': '#3A3A3A'}, 'driver-magnet': {'preset': 'satin_paint', 'color': '#2B2B2B'},
               'driver-coil': {'preset': 'metal', 'color': '#B87333'}, 'driver-spider': {'preset': 'rubber', 'color': '#C8B88A'},
               'driver-plug': {'preset': 'satin_paint', 'color': '#111111'}},
    # each waveguide from its bark: birch's milk white (a warm white deep in the casting, as sap), on a pale panel and
    # an off-white ring as photographed; eucalyptus's sage, deepening to its leaf green, on a sage-grey panel and a
    # cream ring
    variants={'birch': {'bark': 'birch_bark', 'panel': '#D8D5CD', 'ring': '#EEEAE2', 'horn': '#F5F2EC', 'horn_deep': '#EFE5D3',
                        'cloth': '#DCD6C8', 'cork': '#3B2F28'},
              'eucalyptus': {'bark': 'eucalyptus_bark', 'panel': '#CBCFC4', 'ring': '#E8E2D4', 'horn': '#DEE6D4', 'horn_deep': '#B9C9A9',
                             'cloth': '#6F7F66', 'cork': '#3B2F28'}},
)


if __name__ == '__main__':
    from speaker.box import vented, suggest_vented
    ts = LIB[P['woofer']]['ts']
    net = net_volume(P)
    pl = port_length(P, net)
    net = net_volume(P, pl)
    pl = port_length(P, net)
    print(f"QB3 start: {suggest_vented(ts)} (L, Hz)")
    print(f"net {net:.1f} L, a {P['port']['a']:g} mm square port {pl:.0f} long for {P['fb']:g} Hz")
    for fb in (32.0, 35.0, 38.0):
        r = vented(ts, net, fb, bore_mm=2 * P['port']['a'] / math.sqrt(math.pi))
        print(fb, {k: r[k] for k in ('f3', 'ref_db', 'max_spl_db', 'port_air_m_s_at_max')})
