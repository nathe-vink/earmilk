"""The render model: the speaker as the engine draws it, from the same CAD as the cut files (fab/cad.py), the bought
parts from their datasheets (fab/components.py) and the letters from the same outlines the metal is cut from
(fab/typeset.py). One named part each, so the engine paints by name and the critic can measure a part by name.

    .venv-fab/bin/python fab/render_model.py           -> out/render/earmilk-floorstander.glb and .json

The inside is in it too, for cutaways and exploded views: the panels inside the box (top, bottom, brace, shelf,
divider, the amplifier's box), the cables, the tweeter's connector, the seals, the insert's magnets and pins.
"""
import json, math, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from params import *  # noqa: F401,F403
import cad
import components as C
from build123d import Compound, Face, Polyline, Pos, Wire, export_gltf, extrude, Vector, Unit

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out-bookshelf' if BOOK else 'out', 'render')
NAME = 'earmilk-bookshelf' if BOOK else 'earmilk-floorstander'
VISIBLE = ['front-baffle', 'back-panel', 'side-left', 'side-right', 'gable-block', 'waveguide-insert', 'port-tube', 'terminal-cup']
# AMP: the plate amplifier replaces the terminal cup (fab/components.amp_plate)
# Inside the box, for cutaways and exploded views (no closed-box camera sees them)
INSIDE = ['top-panel', 'bottom-panel', 'window-brace', 'mid-shelf', 'mid-divider', 'amp-box-floor', 'amp-box-lid', 'amp-box-front']


def inside_parts():
    """The hardware inside, placed as fab/sheets.py's sheets 3 and 4 describe it: the tweeter's own flexible lead from its
    tabs into the connector bay behind the insert's boss, the connector mated standing in the bay, the cabinet's lead down
    the channel (sealed with silicone under the bay's floor), through the brace's window and into its own gland in the
    amplifier box's lid; the woofer's and mid's leads to theirs; the insert's magnets and pins."""
    I, T = INSERT, TWEETER_PART
    zc, yt = WAVEGUIDE['throat_z'], WAVEGUIDE['throat_y']
    yw = cad.wire_hole_y(); zb = zc + I['bay_dz']
    y0a, y1a, z0a, z1a = cad.amp_box_extent()
    gl = cad.amp_glands_xy(); gz = z1a + WALL                     # one gland per cable in the lid: tweeter, woofer, mid
    gx, gy = gl[0]
    # the drop: inside the brace's window, or (no brace) down the back corner beside the amplifier box's lid's gland
    half = BRACE_WINDOW / 2 - min(20.0, BRACE_WINDOW / 6) if BRACE_Z else (PLAN - WALL - 40 - 12) - RUN
    dx, dy = RUN + half, RUN + half
    xc = RUN + 4.0                                                 # just off the centre plane, so a cut on it shows the cable whole
    zcon = cad.connector_z()                                       # the connector standing in the bay, above the channel's seal
    out = {}
    out.update(C.connector_2p((xc, yw, zcon)))
    out['cable-tweeter-lead'] = C.cable([(xc + 6, yt + T['flange_t'] + T['body_depth'] - 2, zc - 6), (xc + 6, I['boss_back_y'] + 4, zb + 4),
                                         (xc + 2, yw + I['bay_l'] / 2 - 6, zb + 6), (xc, yw + 2, zcon + 16), (xc, yw, zcon + 11)], 4.0)
    top = TOP_Z0 - 14
    out['cable-tweeter'] = C.cable([(xc, yw, zcon - 11), (xc, yw, top), (dx, dy, top), (dx, dy, gz + 30), (gx, gy, gz + 30), (gx, gy, gz - WALL - 30)], 5.0)
    # the channel sealed round the cable with 20 mm of silicone from the bay (a grommet will not seat in 18 mm: d16)
    out['seal-channel'] = cad.cyl_z(xc, yw, WIRE_HOLE_D - 0.2, zb - I['bay_d'] / 2 - 20.0, zb - I['bay_d'] / 2)
    for k, (x_, y_) in enumerate(gl):
        out[f'gland-amp-{k + 1}'] = C.cable_gland(x_, y_, gz, AMP_BOX['gland_hole'] - 0.5, (7.0, 9.0, 8.0)[k] if k < 3 else 7.0)
    wx, wy = gl[1] if len(gl) > 1 else gl[0]
    mx, my = gl[2] if len(gl) > 2 else gl[-1]
    wf = DRIVER_SET['woofer']; ws = C.DRIVERS[wf]
    wt = (RUN + ws['frame_od'] * 0.28, WOOFER_REBATE['depth'] + ws['depth'] * 0.55, WOOFER['z'] - ws['frame_od'] * 0.28)
    out['cable-woofer'] = C.cable([wt, (wx, dy - 70, max(WOOFER['z'], gz + 24)), (wx, wy, gz + 24), (wx, wy, gz - WALL - 30)], 7.0)
    if MID:
        ms = C.DRIVERS[DRIVER_SET['mid']]
        mt = (RUN + ms['frame_od'] * 0.28, MID_REBATE['depth'] + ms['depth'] * 0.6, MID['z'] - ms['frame_od'] * 0.28)
        hole = (RUN - 120, WALL + MID_CHAMBER_DEPTH, MID_SHELF_TOP + 40)
        out['cable-mid'] = C.cable([mt, (hole[0], hole[1] - 20, hole[2]), (hole[0], hole[1] + 30, hole[2]), (dx - 9, dy + 9, hole[2] - 30),
                                    (dx - 9, dy + 9, gz + 36), (mx, my, gz + 36), (mx, my, gz - WALL - 30)], 6.0)
    mags, pins = cad.insert_fixings()
    out['magnets-insert'] = C.discs(mags, I['back_y'] - I['magnet_t'], I['back_y'] - 0.05, I['magnet_d'])
    out['magnets-pocket'] = C.discs(mags, I['back_y'] + I['clear'] + 0.05, I['back_y'] + I['clear'] + I['magnet_t'], I['magnet_d'])
    out['pins-insert'] = C.discs(pins, I['back_y'] - I['pin_l'] / 2, I['back_y'] + I['pin_l'] / 2, I['pin_d'])
    return out


def letters(face='front'):
    """The cast letters as solids standing BADGE['relief'] proud of the plinth's front (or the back, mirrored so they
    read from behind), set by the same code as the cut file."""
    # fab/typeset.py imports studio/typeset.py by the same module name, so load it under its own name
    import importlib.util
    spec = importlib.util.spec_from_file_location('fab_typeset', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'typeset.py'))
    T = importlib.util.module_from_spec(spec); spec.loader.exec_module(T)
    wordmark, pieces, bbox = T.wordmark, T.pieces, T.bbox
    contours, _ = wordmark(RUN, BADGE['z'], BADGE)
    bx0, by0, bx1, by1 = bbox(contours)
    dx = RUN - (bx0 + bx1) / 2
    contours = [[(x + dx, z) for (x, z) in c] for c in contours]
    out = []
    for (o, hs) in pieces(contours):
        if face == 'front':
            P = lambda x, z: (x, 0.0, z)                                         # on the front face, y = 0
            amount, d = BADGE['relief'], (0, -1, 0)
        else:
            oz = BACK_BADGE['z'] - BADGE['z']
            P = lambda x, z, oz=oz: (2 * RUN - x, PLAN, z + oz)                 # mirrored: read from behind
            amount, d = BACK_BADGE['relief'], (0, 1, 0)
        ow = Wire(Polyline(*[P(x, z) for (x, z) in o], close=True).edges())
        hw = [Wire(Polyline(*[P(x, z) for (x, z) in h], close=True).edges()) for h in hs]
        out.append(extrude(Face(ow, hw), amount=amount, dir=Vector(*d)))
    return out


def rasterize_marks(dpi=300):
    """The prints as images for the renders' decals, from the same vector files the printer and the vinyl cutter get:
    the Facts panel (its crop marks left out) and the two stencilled marks, black on white."""
    import re, subprocess, tempfile
    src = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out-bookshelf' if BOOK else 'out', 'marks')
    dst = os.path.join(OUT, 'marks'); os.makedirs(dst, exist_ok=True)
    jobs = {'facts': 'facts-print.svg', 'open-other-side': 'stencil-open-other-side.svg', 'shake-well': 'stencil-shake-well.svg'}
    for name, fn in jobs.items():
        svg = open(os.path.join(src, fn)).read()
        svg = re.sub(r'<g id="marks">.*?</g>', '', svg, flags=re.S)          # the Facts sheet's crop marks
        with tempfile.NamedTemporaryFile('w', suffix='.svg', delete=False) as t:
            t.write(svg); tmp = t.name
        subprocess.run(['rsvg-convert', '-d', str(dpi), '-p', str(dpi), '-b', 'white', '-o', os.path.join(dst, f'{name}.png'), tmp], check=True)
        os.unlink(tmp)
    return dst


def build():
    t0 = time.time()
    fab = cad.build()
    parts = {k: fab[k] for k in VISIBLE + INSIDE + ['tweeter-retainer'] if k in fab}
    parts['pull-loop'] = cad.pull_loop()        # the ribbon in the groove under the insert's front edge (BOM line 35)
    parts.update(inside_parts())
    if AMP:
        parts.update(C.amp_plate(AMP, RUN, PLAN, AMP['z']))
    print(f'cabinet {time.time() - t0:.0f}s', flush=True)
    wo, _ = C.driver_parts('woofer', C.DRIVERS[DRIVER_SET['woofer']], (RUN, 0.0, WOOFER['z']), ring_d=WOOFER_REBATE['d'] - 1.6, ring_id=TRIM_RING_ID['woofer'])
    mi = {}
    if MID:
        mi, _ = C.driver_parts('mid', C.DRIVERS[DRIVER_SET['mid']], (RUN, 0.0, MID['z']), ring_d=MID_REBATE['d'] - 1.6, ring_id=TRIM_RING_ID['mid'])
    tspec = dict(C.DRIVERS[DRIVER_SET['tweeter']], **{k: TWEETER_PART[k] for k in ('dome_d', 'surround_w', 'flange_d', 'flange_t', 'body_d', 'body_depth')})
    tw, _ = C.driver_parts('tweeter', tspec, (RUN, WAVEGUIDE['throat_y'], WAVEGUIDE['throat_z']), flange_recess=0.0)
    parts.update(wo); parts.update(mi); parts.update(tw)
    for i, s in enumerate(letters('front')):
        parts[f'letters-front-{i}'] = s
    for i, s in enumerate(letters('back')):
        parts[f'letters-back-{i}'] = s
    print(f'all parts {time.time() - t0:.0f}s', flush=True)
    return parts


def main():
    os.makedirs(OUT, exist_ok=True)
    print('marks', rasterize_marks())
    parts = build()
    kids = []
    for name, solid in parts.items():
        solid.label = name
        kids.append(solid)
    asm = Compound(children=kids); asm.label = NAME
    path = os.path.join(OUT, f'{NAME}.glb')
    # written beside and moved into place, so a render that starts meanwhile never reads half a file
    export_gltf(asm, path + '.part.glb', unit=Unit.MM, binary=True, linear_deflection=0.0005, angular_deflection=0.08)
    os.replace(path + '.part.glb', path)
    info = {'parts': {}}
    for name, s in parts.items():
        bb = s.bounding_box()
        info['parts'][name] = [round(v, 1) for v in (bb.min.X, bb.min.Y, bb.min.Z, bb.max.X, bb.max.Y, bb.max.Z)]
    info['waveguide'] = WAVEGUIDE
    with open(os.path.join(OUT, f'{NAME}.json'), 'w') as f:
        json.dump(info, f, indent=1)
    print(path, os.path.getsize(path) // 1024, 'KB,', len(parts), 'parts')


if __name__ == '__main__':
    main()
