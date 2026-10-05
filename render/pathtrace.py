#!/usr/bin/env python3
"""Path-traced pass: render a GLB exported by `node render.mjs --glb` in Blender's Cycles, on the CPU, with real light.

    python3 render/pathtrace.py --glb render/out/glb/shot-01-v11.glb --out renders/2026-10-03/shot-01-v11-pt.png [--samples 128] [--scale 1]

The sidecar JSON beside the GLB carries the real-time rig (sun, area fills, hemisphere, points), the camera and the exposure;
this script rebuilds them in Cycles units: a sun lamp with a real disc, area lamps (softboxes in the studio), a world dome, AgX view transform.
Needs the `bpy` wheel (pip install bpy); the scene geometry and materials come from the GLB untouched, so nothing drifts.
"""
import argparse, json, math, os, sys, time
from pathlib import Path

def hex_rgb(h):
    h = h.lstrip('#'); return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))

def srgb_to_linear(c):
    return tuple((v / 12.92) if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in c)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--glb', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--samples', type=int, default=128)
    ap.add_argument('--scale', type=float, default=1.0, help='resolution scale against the sidecar size')
    ap.add_argument('--time-limit', type=int, default=0, help='seconds per frame, 0 for none')
    ap.add_argument('--sun-strength', type=float, default=1.0, help='multiplier on the sidecar sun intensity')
    ap.add_argument('--area-strength', type=float, default=1.0)
    ap.add_argument('--world-strength', type=float, default=1.0)
    ap.add_argument('--sky-strength', type=float, default=1.0, help='multiplier on the glow of the sky planes outside the windows')
    ap.add_argument('--fstop', type=float, default=0.0, help='depth of field, focused on the shot\'s look-at point; 0 for none')
    ap.add_argument('--strips', type=float, default=1.0, help='studio only: strength of the two edge strips behind the subject (0 for none)')
    ap.add_argument('--surface', type=float, default=1.0, help='strength of the surface detail (orange peel, paper, plaster, grain); 0 for none')
    ap.add_argument('--bevel', type=float, default=2.0, help='eased edges on the finish, in the shader, mm (silhouette unchanged)')
    a = ap.parse_args()
    import bpy  # noqa: E402
    from mathutils import Vector  # noqa: E402

    side = json.loads(Path(a.glb).with_suffix('.json').read_text())
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.preferences.addon_enable(module='cycles')  # the bpy wheel ships Cycles as an add-on that factory settings leave off
    bpy.ops.import_scene.gltf(filepath=str(Path(a.glb).resolve()))
    scene = bpy.context.scene

    # Camera: the glTF camera, with the exact vertical field of view.
    cam = next(o for o in scene.objects if o.type == 'CAMERA')
    scene.camera = cam
    cam.data.sensor_fit = 'VERTICAL'
    cam.data.angle_y = math.radians(side['camera']['fov'])
    cam.data.clip_start = 0.02; cam.data.clip_end = 200

    # Lights. three.js lamps are gone from the glTF (only punctual ones survive, and those are rebuilt too), so clear and rebuild.
    # Units: a three.js DirectionalLight intensity is an irradiance, as a Cycles sun strength is (W/m²); a RectAreaLight intensity is
    # a radiance (nits), and a Cycles area lamp of power P over area A radiates P / (A·π); a PointLight intensity is in candela, and a
    # Cycles point lamp of power P radiates P / (4π) per steradian. The rooms are closed boxes, so daylight is only what the window
    # admits: the sun, the glowing sky plane outside it and the area fill standing just inside it. Cycles bounces the rest for real.
    for o in [o for o in scene.objects if o.type == 'LIGHT']:
        bpy.data.objects.remove(o, do_unlink=True)
    # three.js is Y-up, Z toward the camera; the glTF importer turns that into Blender's Z-up: (x, y, z) -> (x, -z, y)
    def P(v): return Vector((v[0], -v[2], v[1]))
    def aim(o, dirv): o.rotation_euler = dirv.normalized().to_track_quat('-Z', 'Y').to_euler()
    def lamp(name, kind, color):
        d = bpy.data.lights.new(name, kind); d.color = srgb_to_linear(hex_rgb(color))
        o = bpy.data.objects.new(name, d); scene.collection.objects.link(o); return d, o
    hemi = next((l for l in side['lights'] if l['type'] == 'hemi'), None)
    studio = side['room'] == 'studio'
    sun_e = max([l['intensity'] for l in side['lights'] if l['type'] == 'sun'] or [1.5])
    for i, l in enumerate([l for l in side['lights'] if l['type'] == 'sun']):
        pos, tgt = P(l['position']), P(l['target'])
        if studio:
            # The studio's directional lights stand in for softboxes: a large square lamp on the same axis, far enough back that its
            # irradiance at the subject equals the real-time intensity (E = P / (π d²) on axis), so the key stays soft and the fill broad.
            span = (tgt - pos).length  # the real-time rig's placement says how close the source was meant to be
            dist = min(max(span, 2.2), 5.0) if i == 0 else 6.0
            size = dist * 0.55 if i == 0 else 3.5
            if l.get('softbox'):  # a shot that sizes its softbox: where the rig put it, at that size, for a harder key and a crisper shadow
                dist, size = min(max(span, 1.2), 6.0), l['softbox']
            dirv = (tgt - pos).normalized()
            d, o = lamp('softbox' if i == 0 else 'fill', 'AREA', l['color']); d.shape = 'SQUARE'; d.size = size
            d.energy = l['intensity'] * math.pi * dist * dist * a.sun_strength
            if l.get('spread'): d.spread = math.radians(l['spread'])   # a grid on the softbox: the light stays on the subject
            o.location = tgt - dirv * dist; aim(o, dirv)
        else:
            # AgX keeps the highlights that ACES clipped, so a sun tuned to read as sun in the real-time pass needs twice the strength here
            d, o = lamp('sun', 'SUN', l['color']); d.energy = l['intensity'] * 2.0 * a.sun_strength; d.angle = math.radians(0.8)
            o.location = pos; aim(o, tgt - pos)
    for l in side['lights']:
        if l['type'] == 'area':
            d, o = lamp('fill', 'AREA', l['color']); d.shape = 'RECTANGLE'; d.size = l['width']; d.size_y = l['height']
            d.energy = l['intensity'] * l['width'] * l['height'] * math.pi * a.area_strength
            o.location = P(l['position']); aim(o, P(l['direction']))
        elif l['type'] == 'point':
            d, o = lamp('lamp', 'POINT', l['color']); d.energy = l['intensity'] * 4 * math.pi; d.shadow_soft_size = 0.08
            o.location = P(l['position'])

    strips = a.strips * (side.get('strips') if side.get('strips') is not None else 1.0)  # a shot can scale its strips in the sidecar
    if studio and strips > 0:
        # Two tall strips behind the subject, left and right of the camera's line, so dark edges and glossy corners take a line
        # of light (what every spin-off critic round asked for). Irradiance about 1.6 W/m2 at the subject each.
        cp, lk = P(side['camera']['position']), P(side['camera']['lookAt'])
        fwd = Vector((lk.x - cp.x, lk.y - cp.y, 0)).normalized()
        for k, sgn in enumerate((-1, 1)):
            ang = math.radians(sgn * 140)
            dirv = Vector((fwd.x * math.cos(ang) - fwd.y * math.sin(ang), fwd.x * math.sin(ang) + fwd.y * math.cos(ang), 0))
            d, o = lamp(f'strip{k}', 'AREA', '#ffffff'); d.shape = 'RECTANGLE'; d.size = 0.35; d.size_y = 2.6
            dist = 3.2; d.energy = (1.6 if sgn < 0 else 1.3) * math.pi * dist * dist * strips
            o.location = Vector((lk.x, lk.y, 0.9)) - dirv * dist; aim(o, Vector((lk.x, lk.y, 0.6)) - o.location)
    if side.get('reflector'):
        # A reflector card behind the camera that lights only the metal (light linking): the bronze plate and the posts mirror
        # it (the shot names the receivers by material), so the polished faces read bright against the dark engraving, while the
        # matte finish keeps the key's fall-off.
        r = side['reflector']
        cp, lk = P(side['camera']['position']), P(side['camera']['lookAt'])
        d, o = lamp('reflector', 'AREA', '#ffffff'); d.shape = 'RECTANGLE'; d.size = r['w']; d.size_y = r['h']
        d.energy = r['radiance'] * r['w'] * r['h'] * math.pi
        o.location = cp + (cp - lk).normalized() * r.get('behind', 1.0); aim(o, lk - o.location)
        rc = bpy.data.collections.new('reflector-receivers')
        for ob in scene.objects:
            if ob.type == 'MESH' and any(sl.material and sl.material.name.lower().startswith(tuple(r['receivers'])) for sl in ob.material_slots):
                rc.objects.link(ob)
        o.light_linking.receiver_collection = rc
    if studio and side.get('backdropLight'):
        # A wide softbox hung above and behind the subject, out of frame and facing down the sweep, unseen by the camera: the
        # backdrop goes clean and bright behind a pale product, so a white body reads against it by its own shading.
        # `backdropLight` is the irradiance (W/m2) it adds at the middle of the curve.
        cp, lk = P(side['camera']['position']), P(side['camera']['lookAt'])
        fwd = Vector((lk.x - cp.x, lk.y - cp.y, 0)).normalized()
        d, o = lamp('backdrop', 'AREA', '#ffffff'); d.shape = 'RECTANGLE'; d.size = 6.0; d.size_y = 1.0
        o.location = Vector((lk.x, lk.y, 2.2)) + fwd * 1.6; tgt = Vector((lk.x, lk.y, 0.5)) + fwd * 3.4
        dist = (tgt - o.location).length; d.energy = side['backdropLight'] * math.pi * dist * dist; aim(o, tgt - o.location)
        o.visible_camera = False
    if a.fstop > 0:
        cam.data.dof.use_dof = True; cam.data.dof.aperture_fstop = a.fstop
        cam.data.dof.focus_distance = (P(side['camera']['lookAt']) - P(side['camera']['position'])).length

    # World. The real-time hemisphere light is an irradiance E; a dome of radiance L gives E = π·L. In the rooms the ceiling and walls
    # keep the dome out (and Cycles bounces light for real, which the hemisphere was faking), so it only matters where a set is open:
    # the studio and the desk. The studio dome is a vertical gradient, white overhead and the backdrop tone at the horizon, so lacquer
    # and metal have a soft source above them to reflect instead of one flat value.
    world = bpy.data.worlds.new('world'); scene.world = world; world.use_nodes = True
    wt = world.node_tree; bg = wt.nodes['Background']
    base = srgb_to_linear(hex_rgb(side.get('background') or (hemi['sky'] if hemi else '#ffffff')))
    amb = ((hemi['intensity'] if hemi else 0.3) + 0.5 * side.get('environmentIntensity', 0)) / math.pi * a.world_strength
    if studio:
        tc = wt.nodes.new('ShaderNodeTexCoord'); sep = wt.nodes.new('ShaderNodeSeparateXYZ'); rng = wt.nodes.new('ShaderNodeMapRange'); ramp = wt.nodes.new('ShaderNodeValToRGB')
        rng.inputs['From Min'].default_value = -0.05; rng.inputs['From Max'].default_value = 0.85; rng.clamp = True
        ramp.color_ramp.elements[0].color = (*[c * 0.6 for c in base], 1); ramp.color_ramp.elements[1].color = (1, 1, 1, 1)
        wt.links.new(tc.outputs['Generated'], sep.inputs['Vector']); wt.links.new(sep.outputs['Z'], rng.inputs['Value'])
        wt.links.new(rng.outputs['Result'], ramp.inputs['Fac']); wt.links.new(ramp.outputs['Color'], bg.inputs['Color'])
        bg.inputs['Strength'].default_value = amb * 1.3  # fill strength: the softbox is the key (path-traced round 2)
    else:
        bg.inputs['Color'].default_value = (*base, 1); bg.inputs['Strength'].default_value = amb

    # Materials: glTF brought the colours, textures, roughness, metalness and clearcoat. The exporter names the ones that need a word here.
    emissive = set()
    for m in bpy.data.materials:
        if not m.use_nodes: continue
        nt = m.node_tree; name = (m.name or '').lower()
        if 'sky' in name:
            # The sky plane outside a window. glTF marks it unlit and the importer builds it as emission for camera rays only, mixed
            # with transparency for everything else, so it lit nothing. Rebuild it as a plain emitter: daylight to the eye, and in a
            # closed room the sky light the window admits. It scales with the room's sun, because the real-time rig's suns are
            # cinematic rather than solar and the sky has to keep the shade readable beside them.
            old = next((n for n in nt.nodes if n.type == 'EMISSION'), None)
            color = tuple(old.inputs['Color'].default_value) if old else (1, 1, 1, 1)
            for n in list(nt.nodes): nt.nodes.remove(n)
            out = nt.nodes.new('ShaderNodeOutputMaterial'); em = nt.nodes.new('ShaderNodeEmission')
            em.inputs['Color'].default_value = color; em.inputs['Strength'].default_value = 1.5 * sun_e * side.get('skyGlow', 1) * a.sky_strength
            nt.links.new(em.outputs['Emission'], out.inputs['Surface']); m.use_backface_culling = False
            emissive.add(m.name); continue
        bsdf = next((n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED'), None)
        if bsdf is None: continue
        if name.startswith('bronze'):
            # The real-time renderer fakes bronze with a part-diffuse material because it has one pale environment map; here it is a metal.
            bsdf.inputs['Metallic'].default_value = 1.0; bsdf.inputs['Roughness'].default_value = 0.35
        def noise_bump(scale_m, strength, normal_in=None, distortion=0.0, detail=6.0, stretch=None):
            """A bump from world-space noise with features about `scale_m` metres across; chained after `normal_in`."""
            geo = nt.nodes.new('ShaderNodeNewGeometry'); tx = nt.nodes.new('ShaderNodeTexNoise')
            tx.inputs['Scale'].default_value = 1.0 / scale_m; tx.inputs['Detail'].default_value = detail
            if 'Distortion' in tx.inputs: tx.inputs['Distortion'].default_value = distortion
            vec = geo.outputs['Position']
            if stretch:                                   # grain: noise squashed along one axis
                mp = nt.nodes.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = stretch
                nt.links.new(vec, mp.inputs['Vector']); vec = mp.outputs['Vector']
            nt.links.new(vec, tx.inputs['Vector'])
            bn = nt.nodes.new('ShaderNodeBump'); bn.inputs['Strength'].default_value = strength * a.surface
            bn.inputs['Distance'].default_value = scale_m * 0.2
            nt.links.new(tx.outputs['Fac'], bn.inputs['Height'])
            if normal_in is not None: nt.links.new(normal_in, bn.inputs['Normal'])
            return bn.outputs['Normal']
        if name.startswith(('finish', 'bronze', 'board', 'print', 'standpaint')) and not bsdf.inputs['Normal'].is_linked:
            # Eased edges: a lacquered cabinet's arrises are not razor sharp. A shader-space bevel of 2 mm, no geometry change.
            bev = nt.nodes.new('ShaderNodeBevel'); bev.inputs['Radius'].default_value = a.bevel / 1000; bev.samples = 6
            nrm = bev.outputs['Normal']
            if name.startswith('finish'):
                # Sprayed lacquer is never glass: a faint orange peel, about a millimetre across, that breaks long reflections up.
                nrm = noise_bump(0.0011, 0.025, nrm)
            elif name.startswith('bronze'):
                # A brushed plate: fine grain along its width, so the reflector reads as a sheen across metal, not a flat swatch.
                nrm = noise_bump(0.0004, 0.06, nrm, 0.0, 4.0, (1.0, 10.0, 10.0))
            nt.links.new(nrm, bsdf.inputs['Normal'])
        elif name.startswith('cone'):
            nt.links.new(noise_bump(0.0004, 0.12), bsdf.inputs['Normal']); bsdf.inputs['Roughness'].default_value = 0.8   # pressed paper
        elif name.startswith('surround'):
            bsdf.inputs['Roughness'].default_value = 0.45
            if 'Sheen Weight' in bsdf.inputs: bsdf.inputs['Sheen Weight'].default_value = 0.3                             # rubber
        elif name.startswith('crate'):
            nt.links.new(noise_bump(0.0005, 0.06), bsdf.inputs['Normal'])                                                # moulded HDPE
            if 'Subsurface Weight' in bsdf.inputs:
                bsdf.inputs['Subsurface Weight'].default_value = 0.06; bsdf.inputs['Subsurface Scale'].default_value = 0.002
        elif name.startswith(('floor', 'desk')):
            nt.links.new(noise_bump(0.003, 0.05, None, 2.0, 4.0, (6.0, 1.0, 1.0)), bsdf.inputs['Normal'])                 # grain along the planks
        elif name.startswith('wall'):
            nt.links.new(noise_bump(0.004, 0.035), bsdf.inputs['Normal'])                                                # plaster
        elif name.startswith('chairwood'):
            nt.links.new(noise_bump(0.002, 0.05, None, 1.5, 4.0, (1.0, 1.0, 5.0)), bsdf.inputs['Normal'])
        if m.blend_method == 'BLEND' or m.surface_render_method == 'BLENDED':
            m.surface_render_method = 'DITHERED'  # alpha-tested decals in Cycles stay crisp

    # Eased edges need each cabinet's finish in one object: the Bevel node only sees its own object's geometry, and the model
    # builds every panel of the finish (front, back, sides, plinth faces, gable) as its own mesh, so the corners where front
    # meets side stayed knife-sharp however large the radius (every critic round said so). Join them before rendering.
    fin = [o for o in scene.objects if o.type == 'MESH' and o.material_slots
           and all(sl.material and sl.material.name.lower().startswith('finish') for sl in o.material_slots)]
    if len(fin) > 1:
        for o in scene.objects: o.select_set(False)
        for o in fin: o.select_set(True)
        bpy.context.view_layer.objects.active = fin[0]
        bpy.ops.object.join()
    # The glowing sky planes stand just outside the windows; they must not shadow the sun.
    for o in scene.objects:
        if o.type == 'MESH' and any(sl.material and sl.material.name in emissive for sl in o.material_slots):
            o.visible_shadow = False

    # Cycles on the CPU, denoised, AgX.
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = a.samples
    scene.cycles.use_adaptive_sampling = True; scene.cycles.adaptive_threshold = 0.02
    if a.time_limit: scene.cycles.time_limit = a.time_limit
    scene.cycles.use_denoising = True
    scene.cycles.denoiser = 'OPENIMAGEDENOISE'; scene.cycles.denoising_input_passes = 'RGB_ALBEDO_NORMAL'
    scene.cycles.max_bounces = 8; scene.cycles.transparent_max_bounces = 16; scene.cycles.caustics_reflective = False; scene.cycles.caustics_refractive = False
    scene.cycles.film_exposure = side.get('exposure', 1.0)
    scene.view_settings.view_transform = 'AgX'; scene.view_settings.look = 'AgX - Medium High Contrast'
    scene.render.resolution_x = int(side['size'][0] * a.scale); scene.render.resolution_y = int(side['size'][1] * a.scale)
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'; scene.render.image_settings.color_mode = 'RGB'
    scene.render.filepath = str(Path(a.out).resolve()); Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    scene.render.film_transparent = False
    if side.get('background') and not hemi:
        pass
    t0 = time.time()
    bpy.ops.render.render(write_still=True)
    print(f'{a.out}  {time.time() - t0:.0f}s  {scene.render.resolution_x}x{scene.render.resolution_y}  {a.samples} spp', flush=True)

if __name__ == '__main__':
    main()
