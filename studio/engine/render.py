#!/usr/bin/env python3
"""The engine's render command: a shot file in, an image out, every setting from the file.

    python3 studio/engine/render.py studio/shots/earmilk/02a.json --out renders/2026-10-08/02a-e1.png
        [--set camera.lens_mm=85 --set lights.key.power_w=450]     any knob, by its dotted path
        [--apply critic/rounds/2026-10-08/02a-e1-r1.json [--only c1 c3]]   a critic's prescribed changes
        [--save-shot studio/shots/earmilk/02a.json]   write the changed shot back (after --set/--apply)
        [--samples 64 --scale 0.5]                    a quick proof
        [--crop X0 Y0 X1 Y1]                          a region, fractions of the frame from the top left
        [--masks]                                     also write NAME.mask.png (part ids) and NAME.mask.json

Beside the image it writes NAME.shot.json (the resolved shot, the exact settings used) and NAME.report.json (time,
samples, the changes applied, where each part lands in the frame, per-part statistics when --masks is on). critic/card.py reads the shot file to list
the knobs and their values; critic/measure.py reads the masks to measure a part by name.

Runs on the system Python with `bpy` (Blender 5). Lengths in metres, z up, the product at the origin facing -y.
"""
import argparse, json, math, os, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

import shot as S  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('shot')
    ap.add_argument('--out')
    ap.add_argument('--set', action='append', default=[], dest='sets')
    ap.add_argument('--apply'); ap.add_argument('--only', nargs='*')
    ap.add_argument('--save-shot')
    ap.add_argument('--samples', type=int); ap.add_argument('--scale', type=float, default=1.0)
    ap.add_argument('--crop', type=float, nargs=4)
    ap.add_argument('--masks', action='store_true')
    ap.add_argument('--masks-only', action='store_true', help='the report and the part masks for an image already rendered (a mask pass that died)')
    ap.add_argument('--threads', type=int, default=0)
    ap.add_argument('--no-render', action='store_true', help='apply and save the shot (--save-shot) without rendering')
    ap.add_argument('--probe', action='append', default=[], help='what a part mirrors into the camera (probe.py); no render')
    ap.add_argument('--mirrors', action='store_true', help='with the masks, the mirror map (probe.py); --masks-only writes it anyway')
    a = ap.parse_args()
    if not a.out and not a.no_render:
        ap.error('--out is required unless --no-render')

    sh = S.load(a.shot)
    applied, pending = [], []
    if a.apply:
        applied, pending = S.apply_changes(sh, json.loads(Path(a.apply).read_text()), a.only)
    S.apply_overrides(sh, a.sets)
    if a.save_shot:
        S.save(sh, a.save_shot)
    if a.no_render:
        print(json.dumps({'applied': applied, 'pending': pending}, indent=1, default=str))
        return

    import bpy  # noqa: E402
    from mathutils import Vector  # noqa: E402
    import lights as Lt, sets as St, product as Pr  # noqa: E402

    t0 = time.time()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.preferences.addon_enable(module='cycles')
    scene = bpy.context.scene

    # --- product -----------------------------------------------------------------------------------------------
    # one product ("product") or several side by side ("products": a list of product blocks, e.g. a family shot)
    blocks = sh.get('products') or ([sh['product']] if sh.get('product') else [])
    objs, part_of = [], {}
    centre = Vector((0, 0, 0.5))
    for blk in blocks:
        pdef = Pr.load_def(blk['def'], ROOT)
        templates = Pr.import_model(bpy, Path(ROOT, pdef['model']), pdef['origin_mm'], pdef.get('axes', 'gltf'))
        if pdef.get('smooth'):
            Pr.smooth_parts(bpy, templates, pdef['smooth'])
        if pdef.get('normals_from') and not a.masks_only:
            # shading normals, and the waveguide's facets refined onto its true surface (a few tenths of a millimetre):
            # nothing a flat id mask can show, and in a frame of six copies the refined mesh took the mask pass to
            # 9.7 GB (05-e7). A shot whose waveguides are a few dozen pixels across keeps the normals and skips the
            # refinement ("normals_refine": false in its product block)
            rules = pdef['normals_from'] if blk.get('normals_refine', True) else [dict(r, refine=0) for r in pdef['normals_from']]
            Pr.normals_from(bpy, templates, rules, pdef['origin_mm'], ROOT)
        o_, p_ = Pr.place(bpy, pdef, templates, {**sh, 'product': blk}, ROOT)
        objs += o_; part_of.update(p_)
    if objs:
        lo, hi = Pr.bounds(objs)
        centre = (lo + hi) / 2
    mats = sh.get('materials', {})

    # --- set -----------------------------------------------------------------------------------------------------
    st = sh.get('set', {'kind': 'none'})
    if st.get('kind') == 'sweep':
        St.sweep(bpy, st, mats)
    elif st.get('kind') == 'room':
        St.room(bpy, st, mats)

    # --- camera --------------------------------------------------------------------------------------------------
    cam_spec = sh['camera']
    cd = bpy.data.cameras.new('camera'); cam = bpy.data.objects.new('camera', cd); scene.collection.objects.link(cam)
    scene.camera = cam
    cd.sensor_fit = 'HORIZONTAL'; cd.sensor_width = cam_spec.get('sensor_mm', 36.0); cd.lens = cam_spec.get('lens_mm', 50.0)
    cd.clip_start = 0.01; cd.clip_end = 300
    C = Vector(cam_spec['position']); T = Vector(cam_spec.get('target', centre))
    W, H = sh.get('size', [1600, 1000])
    if cam_spec.get('level', True):
        # look level; shift the lens so the target lands where a tilted camera would put it (verticals stay vertical)
        d = T - C; flat = Vector((d.x, d.y, 0))
        cam.rotation_euler = flat.to_track_quat('-Z', 'Y').to_euler()
        tilt = math.atan2(d.z, flat.length)
        # Blender's shift is in units of the larger frame dimension
        cd.shift_y = math.tan(tilt) * cd.lens / cd.sensor_width * (1.0 if W >= H else W / H)
    else:
        cam.rotation_euler = (T - C).to_track_quat('-Z', 'Y').to_euler()
    cam.location = C
    if cam_spec.get('roll_deg'):
        cam.rotation_euler.rotate_axis('Z', math.radians(cam_spec['roll_deg']))
    cd.shift_x += cam_spec.get('shift_x', 0.0); cd.shift_y += cam_spec.get('shift_y', 0.0)
    if cam_spec.get('fstop', 0) > 0:
        cd.dof.use_dof = True; cd.dof.aperture_fstop = cam_spec['fstop']
        F = cam_spec.get('focus', 'target')
        F = T if F == 'target' else Vector(F)
        cd.dof.focus_distance = (F - C).dot((T - C).normalized())
    pol = cam_spec.get('polariser') or {}
    if pol.get('strength', 0) > 0:
        import materials as M
        M.polarise(bpy, cam.rotation_euler, pol['strength'], pol.get('angle_deg', 90.0))

    # --- light -----------------------------------------------------------------------------------------------------
    sun_aim = None
    if (sh.get('sun') or {}).get('aim') and (sh.get('set') or {}).get('kind') == 'room':
        # the sun placed by where its light should land: through a window's point onto a point in the room
        az, el = St.sun_through_window(sh['set'], sh['sun']['aim'])
        sh['sun']['azimuth_deg'], sh['sun']['elevation_deg'] = round(az, 2), round(el, 2)
        sun_aim = {'azimuth_deg': round(az, 2), 'elevation_deg': round(el, 2)}
    if 'sun' in sh and sh['sun'].get('irradiance', 0) > 0:
        Lt.sun(bpy, sh['sun'])
    Lt.world(bpy, sh.get('sky', {'kind': 'gradient'}), sh.get('sun'))
    for name, spec in (sh.get('lights') or {}).items():
        if not spec or spec.get('off'):
            continue
        kind = spec.get('type', 'area')
        ob = {'area': Lt.area, 'spot': Lt.spot, 'point': Lt.point, 'panel': Lt.panel, 'flag': Lt.flag}[kind](bpy, name, spec, centre)
        if spec.get('receivers') and kind != 'flag':
            recv = [o for o in objs if any(Pr._match(part_of[o.name], r) for r in spec['receivers'])]
            for o in [ob] + Lt.twins(bpy, ob):
                Lt.link_receivers(bpy, o, recv)
        elif kind in ('area', 'spot', 'point') and spec.get('shadow_on_set', 1.0) < 1.0:
            # the lamp's shadow on the set lightened, the product's light and shadows as they were
            set_objs = [o for o in bpy.context.scene.objects if o.type == 'MESH' and o.name not in part_of and not o.get('engine_light')]
            Lt.split_set_shadow(bpy, ob, objs, set_objs, max(0.0, spec['shadow_on_set']))
    # a flag scoped to some lamps (`lights`: [names]) shades only those; every other lamp sees through it
    for fname, fspec in (sh.get('lights') or {}).items():
        if fspec and not fspec.get('off') and fspec.get('type') == 'flag' and fspec.get('lights'):
            Lt.scope_flag(bpy, bpy.data.objects[fname], set(fspec['lights']))
    gl = sh.get('glints') or []
    names = list(gl.keys()) if isinstance(gl, dict) else [str(i) for i in range(len(gl))]
    gl = list(gl.values()) if isinstance(gl, dict) else list(gl)
    glint_log = []
    for i, (gname, g) in enumerate(zip(names, gl)):
        if not g:
            continue                                                       # a gap in a list of glints
        recv = [o for o in objs if any(Pr._match(part_of[o.name], r) for r in g['receivers'])] if g.get('receivers') else objs
        g, note = Lt.true_glint(bpy, g, recv, C)
        glint_log.append({'glint': gname, **note})
        if note.get('skipped'):
            continue
        ob = Lt.glint(bpy, f'glint{i}', g, C)
        if g.get('receivers'):
            for o in [ob] + Lt.twins(bpy, ob):
                Lt.link_receivers(bpy, o, recv)

    # --- render settings ---------------------------------------------------------------------------------------------
    R = sh.get('render', {})
    scene.render.engine = 'CYCLES'
    cy = scene.cycles
    cy.device = 'CPU'
    cy.samples = a.samples or R.get('samples', 256)
    cy.use_adaptive_sampling = R.get('adaptive', 0.02) > 0
    if cy.use_adaptive_sampling:
        cy.adaptive_threshold = R.get('adaptive', 0.02)
    cy.use_denoising = R.get('denoise', True)
    if cy.use_denoising:
        cy.denoiser = 'OPENIMAGEDENOISE'; cy.denoising_input_passes = 'RGB_ALBEDO_NORMAL'
    cy.max_bounces = R.get('bounces', 12); cy.diffuse_bounces = min(cy.max_bounces, R.get('diffuse_bounces', 6))
    cy.glossy_bounces = min(cy.max_bounces, 8); cy.transmission_bounces = min(cy.max_bounces, 8)
    cy.sample_clamp_indirect = R.get('clamp', 10.0)
    cy.blur_glossy = R.get('filter_glossy', 0.5)
    cy.caustics_reflective = False; cy.caustics_refractive = False
    if a.threads:
        scene.render.threads_mode = 'FIXED'; scene.render.threads = a.threads
    scene.render.resolution_x = int(W * a.scale); scene.render.resolution_y = int(H * a.scale)
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = False
    if a.crop or R.get('crop'):
        x0, y0, x1, y1 = a.crop or R['crop']
        scene.render.use_border = True; scene.render.use_crop_to_border = True
        scene.render.border_min_x, scene.render.border_max_x = x0, x1
        scene.render.border_min_y, scene.render.border_max_y = 1 - y1, 1 - y0
    vs = scene.view_settings
    vs.view_transform = R.get('view', 'Khronos PBR Neutral')
    if R.get('look'):
        vs.look = R['look']
    vs.exposure = R.get('exposure', 0.0)
    if R.get('white_balance_k'):
        vs.use_white_balance = True; vs.white_balance_temperature = R['white_balance_k']; vs.white_balance_tint = R.get('white_balance_tint', 10.0)
    if R.get('format') == 'EXR':
        # scene-linear radiance, no view transform: what the meter reads
        scene.render.image_settings.file_format = 'OPEN_EXR'; scene.render.image_settings.color_depth = '32'
    else:
        scene.render.image_settings.file_format = 'PNG'; scene.render.image_settings.color_depth = '8'

    out = Path(a.out); out.parent.mkdir(parents=True, exist_ok=True)
    if a.probe:
        import probe as Pb
        res = {}
        for pat in a.probe:
            if '#' in pat:          # 'part#x0,y0,x1,y1': a per-pixel map of what shades that box of the part, per lamp
                pp, bx = pat.split('#')
                res[pat] = Pb.shadow_map(bpy, scene, cam, objs, part_of, pp, Pr._match, [int(v) for v in bx.split(',')],
                                         str(out.with_suffix('.shadows.png')))
            elif '@' in pat:        # 'part@x0,y0,x1,y1': a per-pixel map of what that box of the part reflects
                pp, bx = pat.split('@')
                res[pat] = Pb.reflection_map(bpy, scene, cam, objs, part_of, pp, Pr._match, [int(v) for v in bx.split(',')],
                                             str(out.with_suffix('.map.png')))
            else:
                res[pat] = Pb.reflections(bpy, scene, cam, objs, part_of, pat, Pr._match)
        out.with_suffix('.probe.json').write_text(json.dumps({'shot': a.shot, 'scale': a.scale, 'glints': glint_log, 'probes': res}, indent=1) + '\n')
        for pat, r in res.items():
            print(f'{pat}: {r.get("pixels_sampled", 0)} pixels sampled' + (f' ({r["error"]})' if 'error' in r else ''))
            for what, v in r.get('seen', {}).items():
                print(f'  {v["share"] * 100:5.1f}%  {what:34s} box {v["box_px"]}  az {v["az_deg"]}  el {v["el_deg"]}')
        return
    scene.render.filepath = str(out.resolve())
    t1 = time.time()
    if a.masks_only:
        if not out.exists():
            ap.error(f'--masks-only: {out} is not rendered yet')
        a.masks = True
    else:
        # a new frame: the raw kept by the last retouch at this path is stale
        out.with_suffix('.raw.png').unlink(missing_ok=True)
        bpy.ops.render.render(write_still=True)
    t2 = time.time()

    report = {'shot': a.shot, 'image': str(out), 'seconds': {'build': round(t1 - t0, 1), 'render': round(t2 - t1, 1)},
              'samples': int(cy.samples), 'size': [scene.render.resolution_x, scene.render.resolution_y],
              'applied': applied, 'pending': pending, 'sets': a.sets, 'glints': glint_log, 'sun_aim': sun_aim}
    tside = Path(a.shot).with_suffix('.tune.json')
    if tside.exists():
        report['tuning'] = json.loads(tside.read_text())

    report['parts_2d'] = _parts_2d(scene, cam, objs, part_of)
    # the retouch (retouch.py) matches the paints to their swatches in the finished frame; it needs the swatch mask
    ret = sh.get('retouch') or {}
    ret_on = bool(ret.get('enabled')) and R.get('format') != 'EXR'
    if a.masks_only or (a.masks and a.mirrors):
        # what each product pixel mirrors (probe.py), before the mask pass overrides the materials and hides the lamps:
        # the critic reads which lamp, panel or surface draws a reflection instead of guessing (03's round 8 graded
        # rim_left for the waveguide's wall, which mirrors the glint5 panel)
        import probe as Pb
        mm = Pb.mirror_map(bpy, scene, cam, objs, part_of, str(out.with_suffix('.mirror.png')))
        report['mirrors'] = {'image': str(out.with_suffix('.mirror.png')), 'step': mm['step'], 'parts': mm['parts']}
    if a.masks or ret_on:
        report['masks'] = _masks(bpy, scene, objs, part_of, out)
    if ret_on:
        import shutil, retouch as Rt
        raw = out.with_suffix('.raw.png')
        if not raw.exists():
            shutil.copy(out, raw)
        report['retouch'] = Rt.retouch(str(raw), str(out.with_suffix('.swatch.png')),
                                       json.loads(out.with_suffix('.swatch.json').read_text()), ret, str(out))
        for p_ in report['retouch']['paints']:
            print(f"retouch {p_['paint']}#{p_['copy']} ({p_['mode']}): dE {p_['de_before']} -> {p_['de_after']}")
    S.save(sh, out.with_suffix('.shot.json'))
    out.with_suffix('.report.json').write_text(json.dumps(report, indent=1, default=str) + '\n')
    for gl_ in glint_log:
        if gl_.get('skipped') or gl_.get('normal_off_deg', 0) > 10:
            print('glint', gl_)
    print(f'{out}  {report["seconds"]}  samples {report["samples"]}')


def _parts_2d(scene, cam, objs, part_of):
    """Where each part lands in the frame, in pixels from the top left: its box's centre and the box's extent, and its
    distance in front of the camera. For callouts and labels laid over the image (a deck, an exploded view)."""
    import bpy
    from bpy_extras.object_utils import world_to_camera_view
    from mathutils import Vector
    # a render evaluates the scene; without one (--masks-only) the parts' and the camera's matrices are stale until
    # the view layer updates: 07-e6's exploded parts came out behind the camera, thousands of pixels off the frame
    bpy.context.view_layer.update()
    W, H = scene.render.resolution_x, scene.render.resolution_y
    out = {}
    for ob in objs:
        if ob.hide_render:
            continue
        cs = [ob.matrix_world @ Vector(c) for c in ob.bound_box]
        pts = [world_to_camera_view(scene, cam, c) for c in cs]
        ctr = world_to_camera_view(scene, cam, sum(cs, Vector()) / 8)
        xs = [p.x * W for p in pts]; ys = [(1 - p.y) * H for p in pts]
        out[ob.name] = {'part': part_of[ob.name], 'centre_px': [round(ctr.x * W, 1), round((1 - ctr.y) * H, 1)],
                        'box_px': [round(min(xs)), round(min(ys)), round(max(xs)), round(max(ys))], 'depth_m': round(ctr.z, 3)}
    return out


def _masks(bpy, scene, objs, part_of, out):
    """A second, flat render where each part's pixels carry its id (red channel, 1 to 255), for measuring by part."""
    names = sorted(set(part_of.values()))
    ids = {n: i + 1 for i, n in enumerate(names)}
    for o in scene.objects:
        if o.type == 'MESH':
            o.pass_index = ids.get(part_of.get(o.name), 0)
    m = bpy.data.materials.new('mask-id'); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
    oi = nt.nodes.new('ShaderNodeObjectInfo'); div = nt.nodes.new('ShaderNodeMath'); div.operation = 'DIVIDE'; div.inputs[1].default_value = 255.0
    nt.links.new(oi.outputs['Object Index'], div.inputs[0])
    comb = nt.nodes.new('ShaderNodeCombineColor'); nt.links.new(div.outputs['Value'], comb.inputs['Red'])
    em = nt.nodes.new('ShaderNodeEmission'); nt.links.new(comb.outputs['Color'], em.inputs['Color'])
    o_ = nt.nodes.new('ShaderNodeOutputMaterial'); nt.links.new(em.outputs['Emission'], o_.inputs['Surface'])
    vl = scene.view_layers[0]; vl.material_override = m
    W = scene.world; scene.world = None
    cy = scene.cycles; cy.samples = 1; cy.use_denoising = False; cy.use_adaptive_sampling = False; cy.filter_width = 0.01
    scene.camera.data.dof.use_dof = False
    scene.render.dither_intensity = 0.0      # dither would add +-1 to the ids
    for ob in scene.objects:
        if ob.type == 'LIGHT':
            ob.hide_render = True
    vs = scene.view_settings; vs.view_transform = 'Standard'; vs.exposure = 0.0; vs.use_white_balance = False
    vs.look = 'None'
    scene.display_settings.display_device = 'sRGB'
    # an sRGB view would bend the ids; write linear values straight through
    try:
        vs.view_transform = 'Raw'
    except TypeError:
        pass
    scene.render.image_settings.file_format = 'PNG'; scene.render.image_settings.color_depth = '8'
    mp = out.with_suffix('.mask.png')
    scene.render.filepath = str(mp.resolve())
    bpy.ops.render.render(write_still=True)
    vl.material_override = None
    legend = {str(v): k for k, v in ids.items()}
    out.with_suffix('.mask.json').write_text(json.dumps(legend, indent=1) + '\n')
    # the swatch mask, for the retouch: each product pixel carries the id of its paint and copy (the materials a
    # flavour colours carry their swatch, product.build_materials), every other surface 0. Per slot, so a zoned part's
    # plinth is its accent; linked on the object for the pass, so copies sharing a mesh keep their own ids
    def flat(name, v):
        m_ = bpy.data.materials.new(name); m_.use_nodes = True; t_ = m_.node_tree; t_.nodes.clear()
        e_ = t_.nodes.new('ShaderNodeEmission'); e_.inputs['Color'].default_value = (v / 255.0, 0, 0, 1)
        o2 = t_.nodes.new('ShaderNodeOutputMaterial'); t_.links.new(e_.outputs['Emission'], o2.inputs['Surface'])
        return m_
    zero = flat('swatch-0', 0); sw_ids, sw_mats, sw_leg, saved = {}, {}, {}, []
    inst_of = {o.name: o.get('instance', 0) for o in objs}
    for ob in scene.objects:
        if ob.type != 'MESH':
            continue
        for sl in ob.material_slots:
            src = sl.material
            link = sl.link; sl.link = 'OBJECT'; saved.append((sl, link, sl.material))
            # per copy, paint and part: each face group takes its own hue (a plinth band under other light than its
            # roof), while the retouch sets one lightness for the paint (the faces' shading is the lighting's)
            key = (inst_of[ob.name], src.name, part_of.get(ob.name, '')) if (ob.name in inst_of and src is not None and src.get('swatch')) else None
            if key is None:
                sl.material = zero
                continue
            if key not in sw_ids:
                sw_ids[key] = len(sw_ids) + 1
                sw_mats[key] = flat(f'swatch-{sw_ids[key]}', sw_ids[key])
                sw_leg[str(sw_ids[key])] = {'material': src['swatch_name'], 'instance': key[0], 'hex': src['swatch'],
                                            'flavour': src.name.split('@', 1)[-1], 'part': key[2], 'paint_key': src.name}
            sl.material = sw_mats[key]
    sp = out.with_suffix('.swatch.png')
    scene.render.filepath = str(sp.resolve())
    bpy.ops.render.render(write_still=True)
    for sl, link, m_ in saved:
        sl.material = m_; sl.link = link
    scene.world = W
    out.with_suffix('.swatch.json').write_text(json.dumps(sw_leg, indent=1) + '\n')
    return {'image': str(mp), 'parts': len(ids), 'swatch': str(sp), 'paints': len(sw_leg)}


if __name__ == '__main__':
    main()
