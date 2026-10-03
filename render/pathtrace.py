#!/usr/bin/env python3
"""Path-traced pass: render a GLB exported by `node render.mjs --glb` in Blender's Cycles, on the CPU, with real light.

    python3 render/pathtrace.py --glb render/out/glb/shot-01-v11.glb --out renders/2026-10-03/shot-01-v11-pt.png [--samples 128] [--scale 1]

The sidecar JSON beside the GLB carries the real-time rig (sun, area fills, hemisphere, points), the camera and the exposure;
this script rebuilds them as a sun lamp with a real disc, area lamps, a world of the room's sky colour, and AgX view transform.
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

    # Lights: three.js lamps are gone from the glTF (only punctual ones survive, and we rebuild those too), so clear and rebuild.
    for o in [o for o in scene.objects if o.type == 'LIGHT']:
        bpy.data.objects.remove(o, do_unlink=True)
    # three.js is Y-up, Z toward the camera; the glTF importer turns that into Blender's Z-up: (x, y, z) -> (x, -z, y)
    def P(v): return Vector((v[0], -v[2], v[1]))
    hemi = next((l for l in side['lights'] if l['type'] == 'hemi'), None)
    for l in side['lights']:
        if l['type'] == 'sun':
            d = bpy.data.lights.new('sun', 'SUN'); d.color = srgb_to_linear(hex_rgb(l['color']))
            d.energy = l['intensity'] * 1.1 * a.sun_strength
            d.angle = math.radians(1.6 if side['room'] in ('hero', 'apartmentBright', 'oldRoom') else 6.0)  # a real sun through a window; a broad soft key in the studio
            o = bpy.data.objects.new('sun', d); scene.collection.objects.link(o)
            o.location = P(l['position']); dirv = (P(l['target']) - P(l['position'])).normalized()
            o.rotation_euler = dirv.to_track_quat('-Z', 'Y').to_euler()
        elif l['type'] == 'area':
            d = bpy.data.lights.new('fill', 'AREA'); d.color = srgb_to_linear(hex_rgb(l['color'])); d.shape = 'RECTANGLE'
            d.size = l['width']; d.size_y = l['height']
            d.energy = l['intensity'] * l['width'] * l['height'] * 60 * a.area_strength  # nits-ish to watts, by eye
            o = bpy.data.objects.new('fill', d); scene.collection.objects.link(o)
            o.location = P(l['position']); dirv = P(l['direction']).normalized()
            o.rotation_euler = dirv.to_track_quat('-Z', 'Y').to_euler()
        elif l['type'] == 'point':
            d = bpy.data.lights.new('lamp', 'POINT'); d.color = srgb_to_linear(hex_rgb(l['color'])); d.energy = l['intensity'] * 25; d.shadow_soft_size = 0.08
            o = bpy.data.objects.new('lamp', d); scene.collection.objects.link(o); o.location = P(l['position'])

    # World: the hemisphere's sky colour as a soft dome, scaled by the real-time rig's ambient.
    world = bpy.data.worlds.new('world'); scene.world = world; world.use_nodes = True
    bg = world.node_tree.nodes['Background']
    sky = hex_rgb(side.get('background') or (hemi['sky'] if hemi else '#ffffff'))
    amb = (hemi['intensity'] if hemi else 0.3) + 0.5 * side.get('environmentIntensity', 0)
    bg.inputs['Color'].default_value = (*srgb_to_linear(sky), 1); bg.inputs['Strength'].default_value = amb * 1.6 * a.world_strength

    # Materials: glTF brought the colours, textures, roughness, metalness and clearcoat. Emissive planes (sky through windows) glow.
    emissive = set()
    for m in bpy.data.materials:
        if m.name and 'sky' in m.name.lower(): emissive.add(m.name)
        if not m.use_nodes: continue
        nt = m.node_tree; bsdf = next((n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED'), None)
        if bsdf is None: continue
        if m.name in emissive:
            bsdf.inputs['Emission Strength'].default_value = 1.0
            bsdf.inputs['Emission Color'].default_value = bsdf.inputs['Base Color'].default_value
            emissive.add(m.name)
        if m.blend_method == 'BLEND' or m.surface_render_method == 'BLENDED':
            m.surface_render_method = 'DITHERED'  # alpha-tested decals in Cycles stay crisp

    # The glowing sky planes stand just outside the windows; they must not shadow the sun or show up in reflections as walls.
    for o in scene.objects:
        if o.type == 'MESH' and any(sl.material and sl.material.name in emissive for sl in o.material_slots):
            o.visible_shadow = False
    # Any mesh the exporter marked as a plain unlit surface (MeshBasicMaterial) is a sky or a backdrop: no shadow from it either.

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
