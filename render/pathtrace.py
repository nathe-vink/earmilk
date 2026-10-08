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
    ap.add_argument('--denoise', type=int, default=1, help='0 to skip the denoiser (for checking detail a pixel wide)')
    ap.add_argument('--denoise-guides', default='RGB_ALBEDO_NORMAL', choices=['RGB_ALBEDO_NORMAL', 'RGB_ALBEDO', 'RGB'], help='the passes the denoiser reads')
    ap.add_argument('--coat-normal', type=int, default=1, help='1: the finish\'s clear takes the eased edge and orange peel (v23 on); 0: as before')
    ap.add_argument('--coat-roughness', type=float, default=-1.0, help='the finish\'s clear coat roughness; below 0 keeps the glTF\'s (or the sidecar\'s coatRoughness)')
    ap.add_argument('--peel', type=float, default=1.0, help='multiplier on the finish\'s orange peel (also the sidecar\'s peel)')
    ap.add_argument('--trim-letters', type=int, default=1, help='0 keeps the cast letters\' planes whole (1: cut down to their glyphs, so the denoiser draws no halo round them)')
    ap.add_argument('--adaptive', type=float, default=0.02, help='adaptive sampling noise threshold; 0 samples every pixel fully')
    ap.add_argument('--hide', nargs='*', default=[], help='hide objects whose materials start with these names (for checks)')
    ap.add_argument('--crop', type=float, nargs=4, metavar=('X0', 'Y0', 'X1', 'Y1'), help='render only this part of the frame, as fractions from the top left (for checking a detail at full size)')
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
    if side['camera'].get('level'):
        # 2026-10-07: a level camera with lens shift, as a product photographer frames a tall object, so its verticals stay
        # vertical (tilted down, they converge: round 1 of the printed back). It looks horizontally toward the lookAt point and
        # the frame shifts to put that point where the tilted camera had it, at the centre. With a vertical sensor fit Blender's
        # shift is in units of the image height.
        from mathutils import Matrix
        C, T = side['camera']['position'], side['camera']['lookAt']
        tilt = math.atan2(T[1] - C[1], math.hypot(T[0] - C[0], T[2] - C[2]))
        dvec = Vector((T[0] - C[0], -(T[2] - C[2]), 0)).normalized()
        cam.matrix_world = Matrix.Translation(Vector((C[0], -C[2], C[1]))) @ dvec.to_track_quat('-Z', 'Y').to_matrix().to_4x4()   # (x, y, z) three.js -> (x, -z, y)
        cam.data.shift_y = math.tan(tilt) / (2 * math.tan(math.radians(side['camera']['fov']) / 2))

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
            sb = l.get('softbox')
            if sb:  # a shot that sizes its softbox: where the rig put it, at that size, for a harder key and a crisper shadow
                dist, size = min(max(span, 1.2), 6.0), (max(sb) if isinstance(sb, list) else sb)
            dirv = (tgt - pos).normalized()
            d, o = lamp('softbox' if i == 0 else 'fill', 'AREA', l['color']); d.shape = 'SQUARE'; d.size = size
            if isinstance(sb, list):  # a strip box [w, h]: w level across, h along the light's up, so lacquer mirrors it as a band
                d.shape = 'RECTANGLE'; d.size, d.size_y = sb[0], sb[1]
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
            ang = math.radians(sgn * side.get('stripAngle', 140))  # 140: behind the subject; a shot can bring them round to its sides
            dirv = Vector((fwd.x * math.cos(ang) - fwd.y * math.sin(ang), fwd.x * math.sin(ang) + fwd.y * math.cos(ang), 0))
            d, o = lamp(f'strip{k}', 'AREA', '#ffffff'); d.shape = 'RECTANGLE'; d.size = 0.35; d.size_y = 2.6
            dist = 3.2; d.energy = (1.6 if sgn < 0 else 1.3) * math.pi * dist * dist * strips
            o.location = Vector((lk.x, lk.y, 0.9)) - dirv * dist; aim(o, Vector((lk.x, lk.y, 0.6)) - o.location)
            o.visible_camera = False   # 2026-10-08: a light, not a prop (one stood at the line-up's edge as a clipped white strip)
    if side.get('reflector'):
        # A reflector card behind the camera that lights only the metal (light linking): the bronze plate and the posts mirror
        # it (the shot names the receivers by material), so the polished faces read bright against the dark engraving, while the
        # matte finish keeps the key's fall-off.
        r = side['reflector']
        cp, lk = P(side['camera']['position']), P(side['camera']['lookAt'])
        d, o = lamp('reflector', 'AREA', '#ffffff'); d.shape = 'RECTANGLE'; d.size = r['w']; d.size_y = r['h']
        d.energy = r['radiance'] * r['w'] * r['h'] * math.pi
        o.location = cp + (cp - lk).normalized() * r.get('behind', 1.0)
        if r.get('position'): o.location = P(r['position'])  # or where the shot puts it: where the metal mirrors it from the camera
        aim(o, (P(r['aim']) if r.get('aim') else lk) - o.location)
        rc = bpy.data.collections.new('reflector-receivers')
        for ob in scene.objects:
            if ob.type == 'MESH' and any(sl.material and sl.material.name.lower().startswith(tuple(r['receivers'])) for sl in ob.material_slots):
                rc.objects.link(ob)
        o.light_linking.receiver_collection = rc
    for k, gl in enumerate(side.get('glints') or []):
        # 2026-10-07: an edge light for one rounded edge. The strip goes where that edge's middle normal mirrors it into the
        # camera (R = 2(N.V)N - V), its long side along the edge, unseen by the camera, so the round draws a line of light.
        # `at` is a point on the edge and `normal` its middle normal (bisector of the two faces), both in metres; `irradiance`
        # in W/m2 at the edge; light linking keeps it to the receivers (the finish by default), so it adds no pool on the floor.
        cp = P(side['camera']['position']); at = P(gl['at']); n = P(gl.get('normal', [0, 0, 1])).normalized()
        v = (cp - at).normalized(); r = (2 * n.dot(v) * n - v).normalized()
        dist = gl.get('dist', 2.4); w, h = gl.get('size', [0.12, 1.6])
        d, o = lamp(f'glint{k}', 'AREA', gl.get('color', '#ffffff')); d.shape = 'RECTANGLE'; d.size = w; d.size_y = h
        if gl.get('position'):
            # 2026-10-08: or a small light where the shot puts it, aimed at `at` (a port's far wall, which no mirror direction
            # can reach from inside the tube); `dist` is then the distance from it
            o_loc = P(gl['position']); dist = (o_loc - at).length
        else:
            o_loc = at + r * dist
        d.energy = gl.get('irradiance', 4.0) * math.pi * dist * dist
        o.location = o_loc
        edge = P(gl.get('edge', [0, 1, 0])).normalized()          # the edge's direction: the strip's long side follows it
        z = (at - o.location).normalized(); y = (edge - edge.dot(z) * z).normalized(); x = y.cross(-z)   # local Z points away from the edge (a lamp emits along -Z); X = Y x Z
        from mathutils import Matrix
        o.matrix_world = Matrix(((x.x, y.x, -z.x, o.location.x), (x.y, y.y, -z.y, o.location.y), (x.z, y.z, -z.z, o.location.z), (0, 0, 0, 1)))
        o.visible_camera = False
        if gl.get('specularOnly'):
            # 2026-10-08: seen only in reflections, so a bright strip draws its line on a round a pixel or two wide without
            # lifting the faces beside it (a round that small reflects a thin sliver of the strip; diffuse spill grows with it)
            o.visible_diffuse = False; o.visible_transmission = False; o.visible_volume_scatter = False
        rcv = gl.get('receivers', ['finish'])
        gc = bpy.data.collections.new(f'glint{k}-receivers')
        for ob in scene.objects:
            if ob.type == 'MESH' and any(sl.material and sl.material.name.lower().startswith(tuple(rcv)) for sl in ob.material_slots):
                gc.objects.link(ob)
        o.light_linking.receiver_collection = gc
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
            # Eased edges: a lacquered cabinet's arrises are not razor sharp. A shader-space bevel, no geometry change; the shot's
            # bevelScale shrinks it with the cabinets (the pint is 100/390 of the floorstander: 6 mm rounded its 2 mm fin right through).
            bev = nt.nodes.new('ShaderNodeBevel'); bev.inputs['Radius'].default_value = a.bevel * side.get('bevelScale', 1) / 1000; bev.samples = 6
            nrm = bev.outputs['Normal']
            if name.startswith('finish'):
                # Sprayed lacquer is never glass: a faint orange peel, about a millimetre across, that breaks long reflections up.
                # v26: 0.015 (was 0.025), polished with the clear (at 0.025 it streaked a line of light into blotches)
                nrm = noise_bump(0.0011, 0.015 * a.peel * side.get('peel', 1.0), nrm)
            elif name.startswith('bronze'):
                # A brushed plate: fine grain along its width, so the reflector reads as a sheen across metal, not a flat swatch.
                nrm = noise_bump(0.0004, 0.06, nrm, 0.0, 4.0, (1.0, 10.0, 10.0))
            nt.links.new(nrm, bsdf.inputs['Normal'])
            if name.startswith('finish') and a.coat_normal and 'Coat Normal' in bsdf.inputs:
                # v23: the clear takes the same eased edge and orange peel (unlinked, it kept the flat-shaded normal: no glint where
                # the shader eased an arris, and a peel-free mirror over a peeled colour coat)
                nt.links.new(nrm, bsdf.inputs['Coat Normal'])
            cr = a.coat_roughness if a.coat_roughness >= 0 else side.get('coatRoughness', -1)
            if name.startswith('finish') and cr >= 0 and 'Coat Roughness' in bsdf.inputs:
                bsdf.inputs['Coat Roughness'].default_value = cr
            if name.startswith('finish') and 'Specular IOR Level' in bsdf.inputs and bsdf.inputs['Coat Weight'].default_value >= 0.99:
                # 2026-10-08: under a full clear the colour coat has no gloss of its own (paint against clear is no interface),
                # so the sheen is the clear's alone; its broad lobe also washed the sides wherever an edge light shone
                bsdf.inputs['Specular IOR Level'].default_value = 0.0
        elif name.startswith('cone'):
            # 2026-10-08: pressed concentric ribs, about a dozen from the rim to the cap (the lathe's v runs rim to centre), under
            # the paper's fibre, so a light draws rings across the cone (it was one flat black in every frame)
            tc = nt.nodes.new('ShaderNodeTexCoord'); sep = nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(tc.outputs['UV'], sep.inputs['Vector'])
            mul = nt.nodes.new('ShaderNodeMath'); mul.operation = 'MULTIPLY'; mul.inputs[1].default_value = 2 * math.pi * 14
            nt.links.new(sep.outputs['Y'], mul.inputs[0])
            sine = nt.nodes.new('ShaderNodeMath'); sine.operation = 'SINE'; nt.links.new(mul.outputs['Value'], sine.inputs[0])
            ribs = nt.nodes.new('ShaderNodeBump'); ribs.inputs['Strength'].default_value = 0.08 * a.surface; ribs.inputs['Distance'].default_value = 0.0005   # v25 a third as deep (at 0.4 they read as a stock grooved cone); v26 about half again (at 0.15, fine steps like faceted geometry)
            nt.links.new(sine.outputs['Value'], ribs.inputs['Height'])
            nt.links.new(noise_bump(0.0004, 0.12, ribs.outputs['Normal']), bsdf.inputs['Normal']); bsdf.inputs['Roughness'].default_value = 0.8   # pressed paper
        elif name.startswith('dustcap'):
            nt.links.new(noise_bump(0.0004, 0.08), bsdf.inputs['Normal'])                                                # 2026-10-08: the cap's paper, satin
        elif name.startswith('surround'):
            bsdf.inputs['Roughness'].default_value = 0.45
            if 'Sheen Weight' in bsdf.inputs: bsdf.inputs['Sheen Weight'].default_value = 0.3                             # rubber
        elif name.startswith('crate'):
            nt.links.new(noise_bump(0.0005, 0.06), bsdf.inputs['Normal'])                                                # moulded HDPE
            if 'Subsurface Weight' in bsdf.inputs:
                bsdf.inputs['Subsurface Weight'].default_value = 0.06; bsdf.inputs['Subsurface Scale'].default_value = 0.002
        elif name.startswith(('floor', 'desk')):
            nt.links.new(noise_bump(0.003, 0.05, None, 2.0, 4.0, (6.0, 1.0, 1.0)), bsdf.inputs['Normal'])                 # grain along the planks
            if bsdf.inputs['Base Color'].is_linked:
                # 2026-10-08: figure in the colour as well, broad enough to read from across a room (round 1 of the owner's answers:
                # "a procedural tile, every board one flat beige"): stretched noise along the boards, about 8 mm across and 6 cm
                # along, scaling each board's colour by 0.86 to 1.08
                src = bsdf.inputs['Base Color'].links[0].from_socket
                geo = nt.nodes.new('ShaderNodeNewGeometry'); mp = nt.nodes.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (8.0, 1.0, 1.0)
                nz = nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 16.0; nz.inputs['Detail'].default_value = 4.0
                if 'Distortion' in nz.inputs: nz.inputs['Distortion'].default_value = 1.5
                rng = nt.nodes.new('ShaderNodeMapRange'); rng.inputs['From Min'].default_value = 0.3; rng.inputs['From Max'].default_value = 0.7
                rng.inputs['To Min'].default_value = 0.86; rng.inputs['To Max'].default_value = 1.08
                mix = nt.nodes.new('ShaderNodeMix'); mix.data_type = 'RGBA'; mix.blend_type = 'MULTIPLY'; mix.inputs['Factor'].default_value = 1.0 * min(a.surface, 1.0)
                nt.links.new(geo.outputs['Position'], mp.inputs['Vector']); nt.links.new(mp.outputs['Vector'], nz.inputs['Vector'])
                nt.links.new(nz.outputs['Fac'], rng.inputs['Value'])
                sock = lambda coll, nm: next(x for x in coll if x.name == nm and x.type == 'RGBA')   # the Mix node has a float, a vector and a colour socket of each name
                nt.links.new(src, sock(mix.inputs, 'A')); nt.links.new(rng.outputs['Result'], sock(mix.inputs, 'B'))
                nt.links.new(sock(mix.outputs, 'Result'), bsdf.inputs['Base Color'])
        elif name.startswith('wall'):
            nt.links.new(noise_bump(0.004, 0.035), bsdf.inputs['Normal'])                                                # plaster
        elif name.startswith('chairwood'):
            nt.links.new(noise_bump(0.002, 0.05, None, 1.5, 4.0, (1.0, 1.0, 5.0)), bsdf.inputs['Normal'])
        if m.blend_method == 'BLEND' or m.surface_render_method == 'BLENDED':
            m.surface_render_method = 'DITHERED'  # alpha-tested decals in Cycles stay crisp

    # 2026-10-08: the cast letters are alpha-masked planes, a face over four more for the relief. Clear as they are outside the
    # glyphs, they still changed the noise behind them, and the denoiser drew each plane as a faint rectangle round the letters
    # on a dark plinth (round 2 of the owner's answers: "a visible rectangular decal patch" on Oat's). Each plane is rebuilt
    # as a grid of cells about a millimetre across, keeping only the cells a letter's pixels touch.
    import numpy as np
    alphas = {}
    for ob in [o for o in scene.objects if a.trim_letters and o.type == 'MESH' and len(o.data.polygons) <= 2 and o.material_slots and o.material_slots[0].material
               and o.material_slots[0].material.name.lower().startswith(('badgeletters', 'badgeside'))]:
        mat = ob.material_slots[0].material
        tex = next((n for n in mat.node_tree.nodes if n.type == 'TEX_IMAGE' and n.image), None)
        if tex is None or not ob.data.uv_layers: continue
        iw, ih = tex.image.size
        if tex.image.name not in alphas:   # rows from the bottom, as Blender's UVs
            buf = np.empty(iw * ih * 4, dtype=np.float32); tex.image.pixels.foreach_get(buf); alphas[tex.image.name] = buf.reshape(ih, iw, 4)[..., 3]
        alpha = alphas[tex.image.name]
        me = ob.data; uvl = me.uv_layers.active.data
        corner = {}
        for poly in me.polygons:
            for li in poly.loop_indices:
                u, v = uvl[li].uv; corner[(round(u), round(v))] = me.vertices[me.loops[li].vertex_index].co.copy()
        if not all(k in corner for k in ((0, 0), (1, 0), (0, 1))): continue
        p00, du, dv = corner[(0, 0)], corner[(1, 0)] - corner[(0, 0)], corner[(0, 1)] - corner[(0, 0)]
        m3 = ob.matrix_world.to_3x3()   # the model is in millimetres under a scaled group: size the cells in the world
        nu, nv = min(600, max(1, round((m3 @ du).length * 1000))), min(200, max(1, round((m3 @ dv).length * 1000)))   # cells about 1 mm
        keep = [(i, j) for j in range(nv) for i in range(nu)
                if alpha[int(j * ih / nv):max(int(j * ih / nv) + 1, int((j + 1) * ih / nv)), int(i * iw / nu):max(int(i * iw / nu) + 1, int((i + 1) * iw / nu))].max() > 0]
        verts, uvs, faces, index = [], [], [], {}
        def vid(i, j):
            if (i, j) not in index:
                index[(i, j)] = len(verts); verts.append(p00 + du * (i / nu) + dv * (j / nv)); uvs.append((i / nu, j / nv))
            return index[(i, j)]
        for i, j in keep:
            faces.append((vid(i, j), vid(i + 1, j), vid(i + 1, j + 1), vid(i, j + 1)))
        new = bpy.data.meshes.new(me.name + '-letters'); new.from_pydata([tuple(v) for v in verts], [], faces); new.update()
        uvnew = new.uv_layers.new(name=me.uv_layers.active.name)
        for poly in new.polygons:
            for li in poly.loop_indices: uvnew.data[li].uv = uvs[new.loops[li].vertex_index]
        if me.polygons and new.polygons and me.polygons[0].normal.dot(new.polygons[0].normal) < 0: new.flip_normals()
        new.materials.append(mat); ob.data = new
    for ob in scene.objects:
        if a.hide and ob.type == 'MESH' and any(sl.material and sl.material.name.lower().startswith(tuple(h.lower() for h in a.hide)) for sl in ob.material_slots):
            ob.hide_render = True
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
    scene.cycles.use_adaptive_sampling = a.adaptive > 0; scene.cycles.adaptive_threshold = a.adaptive or 0.02
    if a.time_limit: scene.cycles.time_limit = a.time_limit
    scene.cycles.use_denoising = bool(a.denoise)
    scene.cycles.denoiser = 'OPENIMAGEDENOISE'; scene.cycles.denoising_input_passes = a.denoise_guides
    scene.cycles.max_bounces = 8; scene.cycles.transparent_max_bounces = 16; scene.cycles.caustics_reflective = False; scene.cycles.caustics_refractive = False
    scene.cycles.sample_clamp_indirect = 10.0   # 2026-10-08: no fireflies (stray white sparkles on the scoop's edge, round 1 of the owner's answers)
    scene.cycles.film_exposure = side.get('exposure', 1.0)
    # v23: a shot can set its look; 2026-10-08: and its view transform ('Khronos PBR Neutral' keeps a base colour's hue up to the
    # highlights, where AgX turned a lit red to salmon)
    view = side.get('view') or 'AgX'
    scene.view_settings.view_transform = view; scene.view_settings.look = side.get('look') or ('AgX - Medium High Contrast' if view == 'AgX' else 'None')
    scene.render.resolution_x = int(side['size'][0] * a.scale); scene.render.resolution_y = int(side['size'][1] * a.scale)
    scene.render.resolution_percentage = 100
    if a.crop:
        x0, y0, x1, y1 = a.crop   # Blender's border runs from the bottom left
        scene.render.use_border = True; scene.render.use_crop_to_border = True
        scene.render.border_min_x, scene.render.border_max_x = x0, x1; scene.render.border_min_y, scene.render.border_max_y = 1 - y1, 1 - y0
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
