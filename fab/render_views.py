#!/usr/bin/env python3
"""Renders the fabrication parts from fab/out/stl as raw birch: an exploded view and a section on the centreline.
Uses Blender's Python module (the same `bpy` the path tracer uses; system Python, not the CAD venv).

    python3 fab/render_views.py [--samples 64] [--scale 1]

Writes fab/out/views/exploded.png and fab/out/views/section.png.
"""
import argparse, math, os, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
STL = HERE / 'out' / 'stl'
OUT = HERE / 'out' / 'views'

WOOD = ['front-baffle', 'back-panel', 'side-left', 'side-right', 'top-panel', 'bottom-panel', 'window-brace',
        'mid-shelf', 'mid-divider', 'gable-block']
OTHER = {'port-tube-with-flange': 'pla', 'port-flare-collar': 'pla', 'terminal-cup': 'dark'}
# Exploded offsets in mm (spec frame: x right, y back, z up).
EXPLODE = {
    'front-baffle': (0, -260, 0), 'back-panel': (0, 300, 0), 'side-left': (-260, 0, 0), 'side-right': (260, 0, 0),
    'top-panel': (0, 0, 120), 'bottom-panel': (0, 0, -160), 'window-brace': (0, 0, 0), 'mid-shelf': (0, -60, 0),
    'mid-divider': (0, -60, 40), 'gable-block': (0, 0, 300), 'port-tube-with-flange': (0, 420, 0),
    'port-flare-collar': (0, 180, 0), 'terminal-cup': (0, 360, 0),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--samples', type=int, default=64)
    ap.add_argument('--scale', type=float, default=1.0)
    ap.add_argument('--only', default='')
    a = ap.parse_args()
    import bpy
    from mathutils import Vector
    OUT.mkdir(parents=True, exist_ok=True)

    def reset():
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.preferences.addon_enable(module='cycles')
        sc = bpy.context.scene
        sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = a.samples
        sc.cycles.use_denoising = True; sc.cycles.denoiser = 'OPENIMAGEDENOISE'
        sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = 'AgX - Base Contrast'
        sc.render.film_transparent = False
        w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True
        bg = w.node_tree.nodes['Background']; bg.inputs['Color'].default_value = (0.93, 0.93, 0.92, 1); bg.inputs['Strength'].default_value = 0.25
        return sc

    def mat(name, color, rough=0.6, metal=0.0):
        m = bpy.data.materials.new(name); m.use_nodes = True
        b = m.node_tree.nodes['Principled BSDF']
        b.inputs['Base Color'].default_value = (*color, 1); b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = metal
        return m

    def load(name, material, offset=(0, 0, 0), scale_explode=1.0):
        bpy.ops.wm.stl_import(filepath=str(STL / f'{name}.stl'))
        o = bpy.context.selected_objects[0]; o.name = name
        o.data.materials.clear(); o.data.materials.append(material)
        o.scale = (0.001, 0.001, 0.001)
        o.location = (offset[0] * 0.001 * scale_explode, offset[1] * 0.001 * scale_explode, offset[2] * 0.001 * scale_explode)
        for p in o.data.polygons: p.use_smooth = False
        return o

    def lights(sc):
        s = bpy.data.lights.new('key', 'AREA'); s.energy = 260; s.size = 2.5
        o = bpy.data.objects.new('key', s); sc.collection.objects.link(o); o.location = (-2.2, -2.6, 3.0)
        o.rotation_euler = (Vector((0.2, 0.2, 0.6)) - o.location).to_track_quat('-Z', 'Y').to_euler()
        f = bpy.data.lights.new('fill', 'AREA'); f.energy = 70; f.size = 3
        o2 = bpy.data.objects.new('fill', f); sc.collection.objects.link(o2); o2.location = (2.6, -1.0, 1.4)
        o2.rotation_euler = (Vector((0.2, 0.2, 0.5)) - o2.location).to_track_quat('-Z', 'Y').to_euler()

    def ground(sc, z=-0.2):
        bpy.ops.mesh.primitive_plane_add(size=20, location=(0.2, 0.2, z))
        g = bpy.context.active_object; g.data.materials.append(mat('ground', (0.93, 0.93, 0.92), 0.9))
        g.is_shadow_catcher = False

    def camera(sc, loc, target, lens=50, ortho=None):
        c = bpy.data.cameras.new('cam'); c.lens = lens
        if ortho: c.type = 'ORTHO'; c.ortho_scale = ortho
        o = bpy.data.objects.new('cam', c); sc.collection.objects.link(o); o.location = loc
        o.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler(); sc.camera = o

    def render(sc, path, w, h):
        sc.render.resolution_x = int(w * a.scale); sc.render.resolution_y = int(h * a.scale); sc.render.resolution_percentage = 100
        sc.render.filepath = str(path); bpy.ops.render.render(write_still=True); print(path, flush=True)

    birch = None
    if a.only in ('', 'exploded'):
        sc = reset(); birch = mat('birch', (0.78, 0.62, 0.42), 0.55)
        mats = {'pla': mat('pla', (0.08, 0.08, 0.09), 0.4), 'bronze': mat('bronze', (0.62, 0.42, 0.2), 0.35, 1.0),
                'dark': mat('dark', (0.05, 0.05, 0.05), 0.4, 0.6)}
        for n in WOOD: load(n, birch, EXPLODE[n])
        for n, m in OTHER.items(): load(n, mats[m], EXPLODE[n])
        ground(sc, -0.32); lights(sc)
        camera(sc, (-1.55, -2.0, 1.55), (0.2, 0.25, 0.52), lens=38)
        render(sc, OUT / 'exploded.png', 1800, 1500)
        # The same parts from behind and to the right, to show the port and the terminal cup.
        camera(sc, (2.05, 2.75, 1.35), (0.2, 0.3, 0.5), lens=38)
        render(sc, OUT / 'exploded-back.png', 1800, 1500)

    if a.only in ('', 'section'):
        sc = reset(); birch = mat('birch', (0.78, 0.62, 0.42), 0.55)
        cutm = mat('cut', (0.55, 0.36, 0.18), 0.9)
        mats = {'pla': mat('pla', (0.08, 0.08, 0.09), 0.4), 'bronze': mat('bronze', (0.62, 0.42, 0.2), 0.35, 1.0),
                'dark': mat('dark', (0.05, 0.05, 0.05), 0.4, 0.6)}
        objs = [load(n, birch) for n in WOOD] + [load(n, mats[m]) for n, m in OTHER.items()]
        # Cut everything at the centreline x = 195 and keep the half x < 195, so the camera at +x sees the section.
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0.195 + 0.5, 0.195, 0.55)); cutter = bpy.context.active_object
        cutter.scale = (1.0, 1.0, 1.4); cutter.hide_render = True; cutter.display_type = 'WIRE'
        for o in objs:
            m = o.modifiers.new('cut', 'BOOLEAN'); m.operation = 'DIFFERENCE'; m.object = cutter; m.solver = 'EXACT'
            o.data.materials.append(cutm)
            bpy.context.view_layer.objects.active = o
            bpy.ops.object.modifier_apply(modifier='cut')
            # faces lying on the cut plane get the lighter cut-face material
            for p in o.data.polygons:
                cx = (o.matrix_world @ p.center).x
                if abs(cx - 0.195) < 1e-4 and abs(p.normal.x) > 0.99: p.material_index = 1
        ground(sc, -0.002); lights(sc)
        camera(sc, (3.2, 0.195, 0.53), (0.195, 0.195, 0.53), ortho=1.25)
        render(sc, OUT / 'section.png', 1400, 1500)


if __name__ == '__main__':
    main()
