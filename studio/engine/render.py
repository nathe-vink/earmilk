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
    ap.add_argument('--threads', type=int, default=0)
    ap.add_argument('--no-render', action='store_true', help='apply and save the shot (--save-shot) without rendering')
    ap.add_argument('--probe', action='append', default=[], help='what a part mirrors into the camera (probe.py); no render')
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
        ob = {'area': Lt.area, 'spot': Lt.spot, 'point': Lt.point, 'panel': Lt.panel}[kind](bpy, name, spec, centre)
        if spec.get('receivers'):
            Lt.link_receivers(bpy, ob, [o for o in objs if any(Pr._match(part_of[o.name], r) for r in spec['receivers'])])
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
            Lt.link_receivers(bpy, ob, recv)

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
        res = {pat: Pb.reflections(bpy, scene, cam, objs, part_of, pat, Pr._match) for pat in a.probe}
        out.with_suffix('.probe.json').write_text(json.dumps({'shot': a.shot, 'scale': a.scale, 'glints': glint_log, 'probes': res}, indent=1) + '\n')
        for pat, r in res.items():
            print(f'{pat}: {r.get("pixels_sampled", 0)} pixels sampled' + (f' ({r["error"]})' if 'error' in r else ''))
            for what, v in r.get('seen', {}).items():
                print(f'  {v["share"] * 100:5.1f}%  {what:34s} box {v["box_px"]}  az {v["az_deg"]}  el {v["el_deg"]}')
        return
    scene.render.filepath = str(out.resolve())
    t1 = time.time()
    bpy.ops.render.render(write_still=True)
    t2 = time.time()

    report = {'shot': a.shot, 'image': str(out), 'seconds': {'build': round(t1 - t0, 1), 'render': round(t2 - t1, 1)},
              'samples': int(cy.samples), 'size': [scene.render.resolution_x, scene.render.resolution_y],
              'applied': applied, 'pending': pending, 'sets': a.sets, 'glints': glint_log, 'sun_aim': sun_aim}

    report['parts_2d'] = _parts_2d(scene, cam, objs, part_of)
    if a.masks:
        report['masks'] = _masks(bpy, scene, objs, part_of, out)
    S.save(sh, out.with_suffix('.shot.json'))
    out.with_suffix('.report.json').write_text(json.dumps(report, indent=1, default=str) + '\n')
    for gl_ in glint_log:
        if gl_.get('skipped') or gl_.get('normal_off_deg', 0) > 10:
            print('glint', gl_)
    print(f'{out}  {report["seconds"]}  samples {report["samples"]}')


def _parts_2d(scene, cam, objs, part_of):
    """Where each part lands in the frame, in pixels from the top left: its box's centre and the box's extent, and its
    distance in front of the camera. For callouts and labels laid over the image (a deck, an exploded view)."""
    from bpy_extras.object_utils import world_to_camera_view
    from mathutils import Vector
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
    vl.material_override = None; scene.world = W
    legend = {str(v): k for k, v in ids.items()}
    out.with_suffix('.mask.json').write_text(json.dumps(legend, indent=1) + '\n')
    return {'image': str(mp), 'parts': len(ids)}


if __name__ == '__main__':
    main()
