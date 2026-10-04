#!/usr/bin/env python3
"""Path-traces a product scene described in JSON with Blender's Cycles. Any product: earmilk, earworm, earwig, the next.

    python3 studio/pathtrace.py spinoffs/earworm/shots.json --shot hero [--out x.png] [--samples 128] [--scale 1]

Runs on the system Python with `bpy` (studio/setup.sh installs it). Geometry comes from the product's CAD (build123d
exports STL, STEP or GLB in millimetres); cables and tubes are generated here; anything else (hair, say) comes from a
small Python hook next to the scene file.

Scene file (all lengths in millimetres, colours as sRGB hex):

    {
      "materials": { "shell": {"preset": "satin_plastic", "color": "#1d1d1f"}, ... },
      "objects": [
        {"id": "cup", "type": "mesh", "file": "out/stl/cup.stl", "material": "shell", "translate": [0,0,0], "rotate": [0,0,0]},
        {"id": "cable", "type": "tube", "points": [[x,y,z], ...], "radius": 2.6, "material": "worm",
         "profile": [[0, 1.0], [0.4, 1.6], [1, 0.5]], "rings": {"pitch": 2.2, "depth": 0.18}},
        {"type": "python", "file": "hair.py", "args": {...}}
      ],
      "shots": {
        "hero": {"size": [1800, 1200], "rig": {"type": "sweep", "color": "#efece6"},
                 "camera": {"position": [x,y,z], "target": [x,y,z], "lens": 85, "fstop": 4},
                 "hide": ["id", ...]}
      }
    }

Rigs size themselves to the subject's bounding box, so a 20 mm earbud and a 1 m speaker light the same way:
  sweep   a seamless cove in `color` (`cove_depth`, `cove_radius` in subject sizes; `wall_color` and `wall_range` darken
          it behind the subject), a softbox key (`key`: azimuth from the camera, elevation, size, power), a fill, a
          rim, and a dome that is white overhead and the cove's tone at the horizon
  table   a tabletop (`surface`: oak, walnut, marble, linen, slate or a hex colour) under a large window light
  any rig takes `lights`: extra area lights by azimuth from the camera, elevation, distance and size (a number, or
          [w, h] for a strip) in subject sizes, power as irradiance at the subject: strips for edges, a pin for glints

Tubes also take `flatten` (a soft tube lying on a floor), `attrs` (a float along the tube for a material's
`attr_color`, e.g. a saddle that fades into the body), rings with `jitter`, `skip_mm`, `skip_fade`, `skip_depth`, and
`bands` (a stretch in another material). Materials take `top_color`, `attr_color`, `bump` and `wrinkle`.
Lessons carried from earmilk's path-traced rounds: light in physical units scaled to the subject, AgX view, the key
on the camera's side of the subject, a dome at fill strength only, no coplanar faces (they render black).
"""
import argparse, importlib.util, json, math, os, sys
from pathlib import Path

MM = 0.001

PRESETS = {
    'satin_plastic':  {'roughness': 0.42},
    'matte_plastic':  {'roughness': 0.72},
    'gloss_plastic':  {'roughness': 0.12, 'coat': 0.5, 'coat_roughness': 0.04},
    'soft_touch':     {'roughness': 0.6, 'sheen': 0.25, 'sheen_roughness': 0.6},
    'rubber':         {'roughness': 0.85},
    'silicone':       {'roughness': 0.38, 'sss': 0.25, 'sss_radius': [1.0, 0.45, 0.3], 'sss_scale': 1.0},
    'gummy':          {'roughness': 0.3, 'sss': 1.0, 'sss_radius': [1.0, 0.6, 0.4], 'sss_scale': 3.0, 'coat': 0.3, 'coat_roughness': 0.25},
    'skin':           {'roughness': 0.45, 'sss': 0.8, 'sss_radius': [1.0, 0.35, 0.2], 'sss_scale': 1.5, 'coat': 0.35, 'coat_roughness': 0.15},
    'lacquer':        {'roughness': 0.3, 'coat': 0.8, 'coat_roughness': 0.06},
    'metal_polished': {'metallic': 1.0, 'roughness': 0.06},
    'metal_satin':    {'metallic': 1.0, 'roughness': 0.28},
    'metal_brushed':  {'metallic': 1.0, 'roughness': 0.32, 'anisotropic': 0.7},
    'anodized':       {'metallic': 1.0, 'roughness': 0.35},
    'leather':        {'roughness': 0.55, 'bump': {'type': 'noise', 'scale': 0.6, 'strength': 0.25}},
    'protein_leather': {'roughness': 0.45, 'coat': 0.15, 'coat_roughness': 0.4, 'bump': {'type': 'noise', 'scale': 0.5, 'strength': 0.15}},
    'fabric':         {'roughness': 0.95, 'sheen': 0.8, 'sheen_roughness': 0.4, 'bump': {'type': 'noise', 'scale': 0.25, 'strength': 0.3}},
    'glass':          {'roughness': 0.02, 'transmission': 1.0, 'ior': 1.5},
    'smoked_glass':   {'roughness': 0.05, 'transmission': 0.85, 'ior': 1.5},
    'emissive':       {'roughness': 0.5, 'emission': 6.0},
    'paper':          {'roughness': 0.85, 'sheen': 0.2},
    'wood':           {'roughness': 0.5, 'bump': {'type': 'wave', 'scale': 3.0, 'strength': 0.08}},
}
SURFACES = {'oak': '#b48a5a', 'walnut': '#5b3d2a', 'marble': '#e9e6e0', 'linen': '#d9d2c3', 'slate': '#3b3e42', 'concrete': '#a9a7a2'}


def hex_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def lin(c):
    return tuple(v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in c)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('scene')
    ap.add_argument('--shot', default=None)
    ap.add_argument('--out', default=None)
    ap.add_argument('--samples', type=int, default=None)
    ap.add_argument('--scale', type=float, default=1.0)
    ap.add_argument('--blend', default=None, help='also save the .blend file here (for opening in Blender)')
    a = ap.parse_args()
    import bpy, bmesh  # noqa: F401
    import numpy as np
    from mathutils import Vector, Matrix, Euler

    scene_path = Path(a.scene).resolve()
    base = scene_path.parent
    S = json.loads(scene_path.read_text())
    shots = S.get('shots', {'default': S})
    shot_name = a.shot or next(iter(shots))
    shot = {**{k: v for k, v in S.items() if k not in ('shots', 'objects', 'materials')}, **shots[shot_name]}
    out = Path(a.out) if a.out else base / 'renders' / f"{shot_name}.png"

    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.preferences.addon_enable(module='cycles')
    sc = bpy.context.scene

    # --- materials -------------------------------------------------------------------------------------------------
    mats = {}

    def make_material(name, spec):
        spec = {**PRESETS.get(spec.get('preset', 'satin_plastic'), {}), **spec}
        m = bpy.data.materials.new(name); m.use_nodes = True
        nt = m.node_tree; b = nt.nodes['Principled BSDF']
        if spec.get('preset') == 'hair':
            nt.nodes.remove(b)
            h = nt.nodes.new('ShaderNodeBsdfHairPrincipled')
            h.parametrization = 'MELANIN'
            h.inputs['Melanin'].default_value = spec.get('melanin', 0.6)
            h.inputs['Melanin Redness'].default_value = spec.get('redness', 0.4)
            h.inputs['Roughness'].default_value = spec.get('roughness', 0.3)
            h.inputs['Radial Roughness'].default_value = spec.get('radial_roughness', 0.4)
            h.inputs['Coat'].default_value = spec.get('coat', 0.1)
            if 'tint' in spec:
                h.inputs['Tint'].default_value = (*lin(hex_rgb(spec['tint'])), 1)
            nt.links.new(h.outputs[0], nt.nodes['Material Output'].inputs['Surface'])
            return m

        def setv(key, val):
            if key in b.inputs:
                b.inputs[key].default_value = val
        col = lin(hex_rgb(spec.get('color', '#808080')))
        setv('Base Color', (*col, 1))
        def two_tone(c_side, c_top):
            """A colour socket: c_side, turning to c_top on upward-facing surfaces (a worm's dorsal side)."""
            if c_top is None:
                rgb = nt.nodes.new('ShaderNodeRGB'); rgb.outputs[0].default_value = (*lin(hex_rgb(c_side)), 1)
                return rgb.outputs[0]
            geo = nt.nodes.new('ShaderNodeNewGeometry'); sep = nt.nodes.new('ShaderNodeSeparateXYZ')
            mr = nt.nodes.new('ShaderNodeMapRange'); mix = nt.nodes.new('ShaderNodeMix'); mix.data_type = 'RGBA'
            mr.inputs['From Min'].default_value, mr.inputs['From Max'].default_value = spec.get('top_range', [-0.3, 0.7])
            mix.inputs['A'].default_value = (*lin(hex_rgb(c_side)), 1); mix.inputs['B'].default_value = (*lin(hex_rgb(c_top)), 1)
            nt.links.new(geo.outputs['Normal'], sep.inputs['Vector']); nt.links.new(sep.outputs['Z'], mr.inputs['Value'])
            nt.links.new(mr.outputs['Result'], mix.inputs['Factor'])
            return mix.outputs['Result']
        if 'top_color' in spec or 'attr_color' in spec:
            base_sock = two_tone(spec.get('color', '#808080'), spec.get('top_color'))
            if 'attr_color' in spec:                  # blend toward another colour where a mesh attribute says so
                ac = spec['attr_color']
                an = nt.nodes.new('ShaderNodeAttribute'); an.attribute_name = ac['attr']
                mix2 = nt.nodes.new('ShaderNodeMix'); mix2.data_type = 'RGBA'
                nt.links.new(base_sock, mix2.inputs['A']); nt.links.new(two_tone(ac['color'], ac.get('top_color')), mix2.inputs['B'])
                nt.links.new(an.outputs['Fac'], mix2.inputs['Factor'])
                base_sock = mix2.outputs['Result']
            nt.links.new(base_sock, b.inputs['Base Color'])
        setv('Roughness', spec.get('roughness', 0.5)); setv('Metallic', spec.get('metallic', 0.0))
        setv('Coat Weight', spec.get('coat', 0.0)); setv('Coat Roughness', spec.get('coat_roughness', 0.03))
        setv('Sheen Weight', spec.get('sheen', 0.0)); setv('Sheen Roughness', spec.get('sheen_roughness', 0.5))
        setv('Anisotropic', spec.get('anisotropic', 0.0))
        setv('Transmission Weight', spec.get('transmission', 0.0)); setv('IOR', spec.get('ior', 1.5))
        if spec.get('sss'):
            setv('Subsurface Weight', spec['sss']); setv('Subsurface Radius', tuple(spec.get('sss_radius', [1, 0.4, 0.25])))
            setv('Subsurface Scale', spec.get('sss_scale', 1.0) * MM)
        if spec.get('emission'):
            setv('Emission Color', (*col, 1)); setv('Emission Strength', spec['emission'])
        bump = spec.get('bump')
        if bump:
            tc = nt.nodes.new('ShaderNodeTexCoord')
            if bump['type'] == 'wave':
                tx = nt.nodes.new('ShaderNodeTexWave'); tx.inputs['Scale'].default_value = bump.get('scale', 3.0)
                tx.inputs['Distortion'].default_value = 6.0
            else:
                tx = nt.nodes.new('ShaderNodeTexNoise'); tx.inputs['Detail'].default_value = 8.0
                tx.inputs['Scale'].default_value = 1.0 / (bump.get('scale', 0.5) * MM)
            nt.links.new(tc.outputs['Object'], tx.inputs['Vector'])
            bn = nt.nodes.new('ShaderNodeBump'); bn.inputs['Strength'].default_value = bump.get('strength', 0.2)
            bn.inputs['Distance'].default_value = bump.get('distance', 0.1) * MM
            nt.links.new(tx.outputs['Fac'], bn.inputs['Height']); nt.links.new(bn.outputs['Normal'], b.inputs['Normal'])
            wr = spec.get('wrinkle')
            if wr:                                    # leather that has been sat in: coarse creases over the grain
                tx2 = nt.nodes.new('ShaderNodeTexNoise'); tx2.inputs['Detail'].default_value = 3.0
                tx2.inputs['Scale'].default_value = 1.0 / (wr.get('scale', 4.0) * MM)
                if 'Distortion' in tx2.inputs:
                    tx2.inputs['Distortion'].default_value = wr.get('distortion', 0.6)
                nt.links.new(tc.outputs['Object'], tx2.inputs['Vector'])
                bn2 = nt.nodes.new('ShaderNodeBump'); bn2.inputs['Strength'].default_value = wr.get('strength', 0.2)
                bn2.inputs['Distance'].default_value = wr.get('distance', 0.4) * MM
                nt.links.new(tx2.outputs['Fac'], bn2.inputs['Height']); nt.links.new(bn.outputs['Normal'], bn2.inputs['Normal'])
                nt.links.new(bn2.outputs['Normal'], b.inputs['Normal'])
        return m

    for name, spec in S.get('materials', {}).items():
        mats[name] = make_material(name, spec)

    def material(name):
        if name not in mats:
            mats[name] = make_material(name, {'preset': 'satin_plastic', 'color': '#888888'})
        return mats[name]

    # --- objects ---------------------------------------------------------------------------------------------------
    objs = {}
    hidden = set(shot.get('hide', []))

    def place(o, spec):
        t = spec.get('translate', [0, 0, 0]); r = spec.get('rotate', [0, 0, 0])
        o.location = (o.location.x + t[0] * MM, o.location.y + t[1] * MM, o.location.z + t[2] * MM)
        o.rotation_euler = Euler([math.radians(v) for v in r], 'XYZ')

    def load_mesh(spec):
        f = (base / spec['file']).resolve()
        before = set(bpy.data.objects)
        ext = f.suffix.lower()
        if ext == '.stl':
            bpy.ops.wm.stl_import(filepath=str(f))
        elif ext in ('.glb', '.gltf'):
            bpy.ops.import_scene.gltf(filepath=str(f))
        elif ext == '.obj':
            bpy.ops.wm.obj_import(filepath=str(f))
        else:
            raise SystemExit(f'unsupported mesh file {f}')
        new = [o for o in bpy.data.objects if o not in before and o.type == 'MESH']
        for o in new:
            if ext == '.stl':
                o.scale = (MM, MM, MM)
            o.data.materials.clear(); o.data.materials.append(material(spec.get('material', 'default')))
            bpy.context.view_layer.objects.active = o; o.select_set(True)
            if spec.get('smooth', 30) is not False:
                bpy.ops.object.shade_smooth_by_angle(angle=math.radians(spec.get('smooth', 30)))
            o.select_set(False)
            place(o, spec)
        return new

    def make_tube(spec):
        """A cable or tube along a smooth path through `points`: parallel-transport frames, a radius profile along the
        length, optional rings (narrow grooves at `pitch`), optional caps."""
        P = np.array(spec['points'], float)
        # Catmull-Rom through the points, then resample evenly by arc length.
        def catmull(P, n=24):
            pts = [P[0]]
            Q = np.vstack([P[0] * 2 - P[1], P, P[-1] * 2 - P[-2]])
            for i in range(1, len(Q) - 2):
                p0, p1, p2, p3 = Q[i - 1], Q[i], Q[i + 1], Q[i + 2]
                for t in np.linspace(0, 1, n, endpoint=False)[1:]:
                    t2, t3 = t * t, t * t * t
                    pts.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
                pts.append(p2)
            return np.array(pts)
        C = catmull(P)
        seg = np.linalg.norm(np.diff(C, axis=0), axis=1); s = np.concatenate([[0], np.cumsum(seg)]); L = s[-1]
        rings = spec.get('rings')
        step = min(spec.get('step', 1.0), (rings['pitch'] / 8) if rings else 1e9)
        n = max(8, int(L / step))
        ss = np.linspace(0, L, n)
        C = np.column_stack([np.interp(ss, s, C[:, k]) for k in range(3)])
        T = np.gradient(C, axis=0); T /= np.linalg.norm(T, axis=1)[:, None]
        # rotation-minimising frames
        up = np.array([0, 0, 1.0]) if abs(T[0, 2]) < 0.9 else np.array([1.0, 0, 0])
        N = np.zeros_like(T); B = np.zeros_like(T)
        N[0] = np.cross(up, T[0]); N[0] /= np.linalg.norm(N[0]); B[0] = np.cross(T[0], N[0])
        for i in range(1, n):
            v = np.cross(T[i - 1], T[i]); sv = np.linalg.norm(v)
            if sv < 1e-9:
                N[i] = N[i - 1]
            else:
                ang = math.atan2(sv, float(np.dot(T[i - 1], T[i]))); k = v / sv
                Ni = N[i - 1]
                N[i] = Ni * math.cos(ang) + np.cross(k, Ni) * math.sin(ang) + k * np.dot(k, Ni) * (1 - math.cos(ang))
            B[i] = np.cross(T[i], N[i])
        u = ss / L
        at = lambda d: d / L if d >= 0 else (L + d) / L              # mm along the path; negative counts from the end
        prof = spec.get('profile', [[0, 1], [1, 1]])
        if 'profile_mm' in spec:                                     # [[mm, k], ...]: the profile by distance instead
            prof = sorted([at(d), k] for d, k in spec['profile_mm'])
        prof = np.array(prof, float)
        r = spec.get('radius', 2.0) * np.interp(u, prof[:, 0], prof[:, 1])
        if rings:
            if rings.get('jitter'):                                  # uneven annuli: the pitch wanders by +-jitter
                rs = np.random.default_rng(rings.get('seed', 3))
                wob = sum(np.sin(2 * np.pi * ss / wl + rs.uniform(0, 2 * np.pi)) for wl in (37.0, 13.0, 5.3)) / 2.2
                cyc = np.concatenate([[0], np.cumsum(np.diff(ss) / (rings['pitch'] * (1 + rings['jitter'] * wob[1:])))])
                phase = cyc % 1.0
            else:
                phase = (ss % rings['pitch']) / rings['pitch']
            groove = np.exp(-((phase - 0.5) / rings.get('width', 0.12)) ** 2)
            mask = np.ones_like(u)
            skips = [list(k) for k in rings.get('skip', [])] + [[at(a0), at(a1)] for a0, a1 in rings.get('skip_mm', [])]
            for (a0, a1) in skips:                                    # smooth bands (a worm's saddle, a plug) have no rings
                fade = rings.get('skip_fade', 0.0) / L                # ease the rings in and out over this many mm
                keep = rings.get('skip_depth', 0.0)                   # what is left of the rings inside (0: none)
                if fade > 0:
                    mask = np.minimum(mask, keep + (1 - keep) * np.clip(np.maximum(a0 - u, u - a1) / fade, 0, 1))
                else:
                    mask[(u >= a0) & (u <= a1)] = keep
            r = r * (1 - rings['depth'] * groove * mask)
        m = spec.get('segments', 20)
        th = np.linspace(0, 2 * np.pi, m, endpoint=False)
        if spec.get('flatten'):                                     # a soft tube resting on a floor: lower and wider
            f_ = spec['flatten']
            upv = np.array([0, 0, 1.0]) - T[:, 2:3] * T
            upv /= np.maximum(np.linalg.norm(upv, axis=1, keepdims=True), 1e-9)
            sdv = np.cross(T, upv)
            V = (C[:, None, :] + r[:, None, None] * (np.cos(th)[None, :, None] * sdv[:, None, :] * (1 + f_)
                                                     + np.sin(th)[None, :, None] * upv[:, None, :] * (1 - f_))).reshape(-1, 3)
        else:
            V = (C[:, None, :] + r[:, None, None] * (np.cos(th)[None, :, None] * N[:, None, :] + np.sin(th)[None, :, None] * B[:, None, :])).reshape(-1, 3)
        faces = []
        for i in range(n - 1):
            for j in range(m):
                a0, a1 = i * m + j, i * m + (j + 1) % m
                faces.append((a0, a1, a1 + m, a0 + m))
        verts = [tuple(v * MM) for v in V]
        if spec.get('caps', True):
            c0 = len(verts); verts.append(tuple(C[0] * MM)); c1 = len(verts); verts.append(tuple(C[-1] * MM))
            for j in range(m):
                faces.append((c0, (j + 1) % m, j))
                faces.append((c1, (n - 1) * m + j, (n - 1) * m + (j + 1) % m))
        me = bpy.data.meshes.new(spec.get('id', 'tube')); me.from_pydata(verts, [], faces); me.update()
        for p in me.polygons:
            p.use_smooth = True
        o = bpy.data.objects.new(spec.get('id', 'tube'), me); sc.collection.objects.link(o)
        o.data.materials.append(material(spec.get('material', 'default')))
        # attrs: a float along the tube that rises over `fade` mm into [from, to] and falls after it, for a material's
        # attr_color (a worm's saddle that blends into the body instead of a sleeve's hard edge)
        for at_spec in spec.get('attrs', []):
            s0, s1, fd = at(at_spec['from']) * L, at(at_spec['to']) * L, max(at_spec.get('fade', 0.0), 1e-6)
            k = np.clip(np.minimum(ss - s0, s1 - ss) / fd + 0.5, 0, 1)
            k = k * k * (3 - 2 * k)
            vals = np.repeat(k, m)
            if spec.get('caps', True):
                vals = np.concatenate([vals, [k[0], k[-1]]])
            att = me.attributes.new(at_spec['name'], 'FLOAT', 'POINT')
            att.data.foreach_set('value', vals.astype(np.float32))
        # bands: a stretch of the tube in another material, e.g. a worm's saddle ({"from": mm, "to": mm, "material": name})
        bands = spec.get('bands', [])
        if bands:
            idx = np.zeros(len(me.polygons), dtype=np.int32)
            ring_s = np.repeat(0.5 * (ss[:-1] + ss[1:]), m)            # one entry per side face, ring by ring
            for k, bd in enumerate(bands, start=1):
                o.data.materials.append(material(bd['material']))
                s0, s1 = at(bd['from']) * L, at(bd['to']) * L
                idx[:len(ring_s)][(ring_s >= s0) & (ring_s <= s1)] = k
            me.polygons.foreach_set('material_index', idx); me.update()
        place(o, spec)
        return [o]

    class Ctx:
        pass
    ctx = Ctx(); ctx.bpy = bpy; ctx.np = np; ctx.MM = MM; ctx.material = material; ctx.objects = objs; ctx.scene = sc
    ctx.base = base; ctx.lin = lin; ctx.hex_rgb = hex_rgb

    for spec in S.get('objects', []) + shot.get('objects_extra', []):
        oid = spec.get('id')
        if oid in hidden:
            continue
        t = spec.get('type', 'mesh')
        if t == 'mesh':
            new = load_mesh(spec)
        elif t == 'tube':
            new = make_tube(spec)
        elif t == 'python':
            f = (base / spec['file']).resolve()
            mod_spec = importlib.util.spec_from_file_location(f.stem, f); mod = importlib.util.module_from_spec(mod_spec)
            mod_spec.loader.exec_module(mod)
            new = mod.build(ctx, **spec.get('args', {})) or []
        else:
            raise SystemExit(f'unknown object type {t}')
        if oid:
            objs[oid] = new

    # Subject bounds (everything loaded), in metres.
    bpy.context.view_layer.update()
    pts = []
    for o in sc.objects:
        if o.type in ('MESH', 'CURVES') and not o.get('studio_set'):
            pts += [o.matrix_world @ Vector(c) for c in o.bound_box]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    centre = (lo + hi) / 2; size = (hi - lo).length
    floor_z = shot.get('floor_z', None)
    floor_z = lo.z if floor_z is None else floor_z * MM

    # --- rig ---------------------------------------------------------------------------------------------------------
    rig = shot.get('rig', {'type': 'sweep'})
    def area_light(name, azim, elev, dist, sz, irradiance, color='#ffffff', target=None):
        target = target or centre
        d = bpy.data.lights.new(name, 'AREA'); d.shape = 'SQUARE'; d.size = sz
        d.color = lin(hex_rgb(color)); d.energy = irradiance * math.pi * dist * dist
        o = bpy.data.objects.new(name, d); sc.collection.objects.link(o)
        az, el = math.radians(azim), math.radians(elev)
        o.location = target + Vector((math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el))) * dist
        o.rotation_euler = (target - o.location).to_track_quat('-Z', 'Y').to_euler()
        o['studio_set'] = True
        return o

    def set_mesh(name, verts, faces, mat):
        me = bpy.data.meshes.new(name); me.from_pydata(verts, [], faces); me.update()
        for p in me.polygons:
            p.use_smooth = True
        o = bpy.data.objects.new(name, me); sc.collection.objects.link(o); o.data.materials.append(mat); o['studio_set'] = True
        return o

    world = bpy.data.worlds.new('world'); sc.world = world; world.use_nodes = True
    wbg = world.node_tree.nodes['Background']
    rt = rig.get('type', 'sweep')
    D = max(size, 0.05)
    if rt == 'sweep':
        col = rig.get('color', '#efece6')
        m = make_material('cove', {'preset': 'matte_plastic', 'color': col, 'roughness': 0.9})
        cam_p = Vector(shot['camera']['position']) * MM if 'position' in shot.get('camera', {}) else centre + Vector((0, -3 * D, D))
        away_v = Vector((centre.x - cam_p.x, centre.y - cam_p.y, 0)); away_v = away_v.normalized() if away_v.length > 1e-6 else Vector((0, 1, 0))
        if rig.get('wall_color'):                     # a deliberate gradient: the set darkens behind the subject and up the wall
            nt_c = m.node_tree; bc = nt_c.nodes['Principled BSDF']
            tc_c = nt_c.nodes.new('ShaderNodeTexCoord'); sub = nt_c.nodes.new('ShaderNodeVectorMath'); sub.operation = 'SUBTRACT'
            sub.inputs[1].default_value = (centre.x, centre.y, floor_z)
            dot = nt_c.nodes.new('ShaderNodeVectorMath'); dot.operation = 'DOT_PRODUCT'
            dot.inputs[1].default_value = (away_v.x, away_v.y, 1.0)            # distance behind the subject, plus height
            mr_c = nt_c.nodes.new('ShaderNodeMapRange'); mx_c = nt_c.nodes.new('ShaderNodeMix'); mx_c.data_type = 'RGBA'
            g0, g1 = rig.get('wall_range', [0.4, 3.0])                          # in units of the subject's size
            mr_c.inputs['From Min'].default_value, mr_c.inputs['From Max'].default_value = g0 * D, g1 * D
            mx_c.inputs['A'].default_value = (*lin(hex_rgb(col)), 1); mx_c.inputs['B'].default_value = (*lin(hex_rgb(rig['wall_color'])), 1)
            nt_c.links.new(tc_c.outputs['Object'], sub.inputs[0]); nt_c.links.new(sub.outputs['Vector'], dot.inputs[0])
            nt_c.links.new(dot.outputs['Value'], mr_c.inputs['Value'])
            nt_c.links.new(mr_c.outputs['Result'], mx_c.inputs['Factor']); nt_c.links.new(mx_c.outputs['Result'], bc.inputs['Base Color'])
        # a cove behind the subject (away from the camera), sized to the subject
        cam_pos = Vector(shot['camera']['position']) * MM if 'position' in shot.get('camera', {}) else centre + Vector((0, -3 * D, D))
        away = Vector((centre.x - cam_pos.x, centre.y - cam_pos.y, 0)); away = away.normalized() if away.length > 1e-6 else Vector((0, 1, 0))
        side = Vector((-away.y, away.x, 0))
        W, depth, R, Hh = 14 * D, rig.get('cove_depth', 3.0) * D, rig.get('cove_radius', 1.6) * D, 8 * D
        Hh = max(Hh, R + 2 * D)
        prof = [(-depth * 2.5, 0.0)] + [(depth + R * math.sin(t * math.pi / 2 / 16), R - R * math.cos(t * math.pi / 2 / 16)) for t in range(17)] + [(depth + R, Hh)]
        verts, faces = [], []
        for (dd, zz) in prof:
            for sgn in (-1, 1):
                p = Vector((centre.x, centre.y, floor_z)) + away * dd + side * (sgn * W / 2) + Vector((0, 0, zz))
                verts.append(tuple(p))
        for i in range(len(prof) - 1):
            a0 = 2 * i
            faces.append((a0, a0 + 1, a0 + 3, a0 + 2))
        set_mesh('cove', verts, faces, m)
        k = rig.get('key', {}); f = rig.get('fill', {}); r = rig.get('rim', {})
        cam_az = math.degrees(math.atan2(cam_pos.x - centre.x, -(cam_pos.y - centre.y)))
        area_light('key', cam_az + k.get('azimuth', -45), k.get('elevation', 50), 2.2 * D, 1.4 * D * k.get('size', 1.0), 3.2 * k.get('power', 1.0), k.get('color', '#fff6ec'))
        area_light('fill', cam_az + f.get('azimuth', 60), f.get('elevation', 20), 3.0 * D, 2.2 * D, 0.9 * f.get('power', 1.0), f.get('color', '#eef3ff'))
        area_light('rim', cam_az + r.get('azimuth', 160), r.get('elevation', 35), 2.4 * D, 0.9 * D, 2.0 * r.get('power', 1.0), r.get('color', '#ffffff'))
        # dome: white overhead, the cove's tone at the horizon, at fill strength
        nt = world.node_tree
        tc = nt.nodes.new('ShaderNodeTexCoord'); sep = nt.nodes.new('ShaderNodeSeparateXYZ'); mr = nt.nodes.new('ShaderNodeMapRange'); ramp = nt.nodes.new('ShaderNodeValToRGB')
        mr.inputs['From Min'].default_value = -0.05; mr.inputs['From Max'].default_value = 0.9
        c = lin(hex_rgb(col)); ramp.color_ramp.elements[0].color = (*[v * 0.6 for v in c], 1); ramp.color_ramp.elements[1].color = (1, 1, 1, 1)
        nt.links.new(tc.outputs['Generated'], sep.inputs['Vector']); nt.links.new(sep.outputs['Z'], mr.inputs['Value'])
        nt.links.new(mr.outputs['Result'], ramp.inputs['Fac']); nt.links.new(ramp.outputs['Color'], wbg.inputs['Color'])
        wbg.inputs['Strength'].default_value = rig.get('dome', 0.35)
    elif rt == 'table':
        surf = rig.get('surface', 'oak')
        col = SURFACES.get(surf, surf if str(surf).startswith('#') else '#b48a5a')
        preset = 'wood' if surf in ('oak', 'walnut') else 'matte_plastic'
        mt = make_material('table', {'preset': preset, 'color': col, 'roughness': rig.get('roughness', 0.45 if preset == 'wood' else 0.7)})
        Wt = 12 * D
        set_mesh('table', [(centre.x - Wt, centre.y - Wt, floor_z), (centre.x + Wt, centre.y - Wt, floor_z), (centre.x + Wt, centre.y + Wt, floor_z), (centre.x - Wt, centre.y + Wt, floor_z)], [(0, 1, 2, 3)], mt)
        wallc = rig.get('wall', '#e9e5dd')
        mw = make_material('wall', {'preset': 'matte_plastic', 'color': wallc, 'roughness': 0.95})
        wy = centre.y + rig.get('wall_distance', 4.0) * D
        set_mesh('wall', [(centre.x - Wt, wy, floor_z), (centre.x + Wt, wy, floor_z), (centre.x + Wt, wy, floor_z + Wt), (centre.x - Wt, wy, floor_z + Wt)], [(0, 1, 2, 3)], mw)
        k = rig.get('key', {})
        area_light('window', k.get('azimuth', -70), k.get('elevation', 35), 3.0 * D, 3.0 * D, 3.6 * k.get('power', 1.0), k.get('color', '#fff3e4'))
        area_light('bounce', 110, 15, 4.0 * D, 4.0 * D, 0.5, '#f4f1ea')
        wbg.inputs['Color'].default_value = (*lin(hex_rgb(rig.get('sky', '#dfe6ee'))), 1); wbg.inputs['Strength'].default_value = rig.get('dome', 0.15)
    else:
        wbg.inputs['Color'].default_value = (*lin(hex_rgb(rig.get('color', '#ffffff'))), 1); wbg.inputs['Strength'].default_value = rig.get('dome', 1.0)

    # extra lights for any rig: strips for edges, kickers ({azimuth (from the camera), elevation, size: D or [w, h] in
    # units of the subject's size, distance in the same units, power as irradiance at the subject, color})
    cam_pos2 = Vector(shot['camera']['position']) * MM if 'position' in shot.get('camera', {}) else centre + Vector((0, -3 * D, D))
    cam_az2 = math.degrees(math.atan2(cam_pos2.x - centre.x, -(cam_pos2.y - centre.y)))
    for i, L_ in enumerate(rig.get('lights', [])):
        o = area_light(f'extra{i}', cam_az2 + L_.get('azimuth', 0), L_.get('elevation', 30), L_.get('distance', 2.2) * D,
                       1.0, L_.get('power', 1.0), L_.get('color', '#ffffff'))
        sz = L_.get('size', 0.6)
        if isinstance(sz, (list, tuple)):
            o.data.shape = 'RECTANGLE'; o.data.size = sz[0] * D; o.data.size_y = sz[1] * D
        else:
            o.data.size = sz * D

    # --- camera ------------------------------------------------------------------------------------------------------
    cs = shot.get('camera', {})
    cam = bpy.data.cameras.new('cam'); cam.lens = cs.get('lens', 85); cam.sensor_width = 36
    co = bpy.data.objects.new('cam', cam); sc.collection.objects.link(co); sc.camera = co
    tgt = Vector(cs['target']) * MM if 'target' in cs else centre
    if 'position' in cs:
        co.location = Vector(cs['position']) * MM
    else:  # auto: frame the subject's bounding sphere from azimuth/elevation
        az, el = math.radians(cs.get('azimuth', -30)), math.radians(cs.get('elevation', 20))
        fov = 2 * math.atan(18 / cam.lens)
        dist = (size / 2) / math.sin(fov / 2) / cs.get('fill', 0.8)
        co.location = tgt + Vector((math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el))) * dist
    co.rotation_euler = (tgt - co.location).to_track_quat('-Z', 'Y').to_euler()
    if cs.get('fstop'):
        cam.dof.use_dof = True; cam.dof.aperture_fstop = cs['fstop']
        fp = Vector(cs['focus']) * MM if 'focus' in cs else tgt
        cam.dof.focus_distance = (fp - co.location).length

    # --- render --------------------------------------------------------------------------------------------------------
    sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'
    sc.cycles.samples = a.samples or shot.get('samples', 128)
    sc.cycles.use_adaptive_sampling = True; sc.cycles.adaptive_threshold = 0.01
    sc.cycles.use_denoising = True; sc.cycles.denoiser = 'OPENIMAGEDENOISE'
    sc.cycles.max_bounces = 12; sc.cycles.transmission_bounces = 12; sc.cycles.transparent_max_bounces = 32
    sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = shot.get('look', 'AgX - Medium High Contrast')
    sc.cycles.film_exposure = 2 ** shot.get('exposure', 0.0)
    w, h = shot.get('size', [1800, 1200])
    sc.render.resolution_x = int(w * a.scale); sc.render.resolution_y = int(h * a.scale); sc.render.resolution_percentage = 100
    sc.render.image_settings.file_format = 'PNG'; sc.render.image_settings.color_mode = 'RGB'
    out.parent.mkdir(parents=True, exist_ok=True); sc.render.filepath = str(out.resolve())
    if a.blend:
        bpy.ops.wm.save_as_mainfile(filepath=str(Path(a.blend).resolve()))
    import time
    t0 = time.time()
    bpy.ops.render.render(write_still=True)
    print(f'{out}  {time.time() - t0:.0f}s  {sc.render.resolution_x}x{sc.render.resolution_y}  {sc.cycles.samples} spp', flush=True)


if __name__ == '__main__':
    main()
