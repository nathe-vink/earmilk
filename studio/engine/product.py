"""The product in the engine: its CAD (a GLB with one named mesh per part, from the product's own CAD script), materials
assigned by part name, colour zones, prints applied as decals under the finish, and as many copies as the shot asks for.

A product definition (studio/products/NAME.json) says:

    model        the GLB, written by the CAD in millimetres in the CAD's frame (build123d: x across, y back from
                 the front face, z up); glTF's Y-up turns that into Blender's (x, -z, y), which is undone here
    origin_mm    the CAD point that stands at the shot's origin (the footprint's centre on the floor)
    flavours     named colourways: {"whole": {"body": "#FFFFFF", "accent": "#C62828", ...}}; a material's value
                 "$body" takes the flavour's colour
    materials    named materials: {"body": {"preset": "paint", "color": "$body"}, ...}
    assign       [{"match": "front-baffle|side-*", "material": "body"}], first match wins (fnmatch, | for or)
    zones        [{"match": "...", "below_z_mm": 110, "material": "accent"}]: faces of matching parts whose centre is
                 below (or above, with above_z_mm) a height take another material (a painted band on one panel)
    decals       [{"name", "image", "center_mm", "normal", "up", "size_mm", "ink": "$facts_ink", "mode": "ink"|"alpha",
                   "material": "body"}]: a print inside that material's colour coat, under its clear

Instances share mesh data, so five flavours cost one import; each flavour gets its own material copies.
"""
import fnmatch, json, math, re
from pathlib import Path

from mathutils import Matrix, Vector

try:
    from . import materials as M
except ImportError:
    import materials as M

# build123d's export_gltf with unit=MM writes glTF's Y-up itself and Blender's importer turns it back, so the CAD's frame
# arrives as it was. A GLB written without that conversion arrives as (x, -z, y): set "axes": "raw" in the product file.
FIX_RAW = Matrix.Rotation(-math.pi / 2, 4, 'X')


def _match(name, pattern):
    return any(fnmatch.fnmatchcase(name, p.strip()) for p in pattern.split('|'))


def load_def(path, root):
    d = json.loads(Path(root, path).read_text())
    d['_root'] = str(root)
    return d


def smooth_parts(bpy, parts, rules):
    """Shade faceted CAD surfaces smooth: a lofted or ruled surface (a waveguide's wall) arrives from the CAD as
    hundreds of flat facets, each with its own normals, and a gloss coat mirrors them as stair-steps. For each part a
    rule matches, weld its vertices and mark only edges sharper than `angle_deg` as hard, so the reflection follows the
    surface's true curve. Shading only: the geometry, and anything measured from it, stays as the CAD made it.

        "smooth": [{"match": "waveguide-insert", "angle_deg": 20}]
    """
    import bmesh
    for name, ob in parts.items():
        r = next((r for r in rules if _match(name, r['match'])), None)
        if r is None:
            continue
        me = ob.data
        bm = bmesh.new(); bm.from_mesh(me)
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
        bm.to_mesh(me); bm.free()
        # the CAD's per-facet normals ride along as custom normals and would override the smoothing: drop them
        if 'custom_normal' in me.attributes:
            me.attributes.remove(me.attributes['custom_normal'])
        for p in me.polygons:
            p.use_smooth = True
        me.set_sharp_from_angle(angle=math.radians(r.get('angle_deg', 20)))


def import_model(bpy, glb, origin_mm, axes='gltf'):
    """Import the GLB once; return {part name: object} with the transforms baked into the meshes, in metres, in the
    CAD's frame shifted so origin_mm sits at (0, 0, 0). The objects are unlinked templates (not in the scene)."""
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(glb))
    new = [o for o in bpy.data.objects if o not in before]
    shift = Matrix.Translation(-Vector(origin_mm) / 1000.0)
    parts = {}
    for o in new:
        if o.type != 'MESH':
            continue
        mw = o.matrix_world.copy()
        o.parent = None
        o.data.transform(shift @ (FIX_RAW if axes == 'raw' else Matrix.Identity(4)) @ mw)
        o.matrix_world = Matrix.Identity(4)
        for p in o.data.polygons:
            p.use_smooth = True
        o.data.materials.clear(); o.data.materials.append(None)   # one empty slot; each copy links its own material
        # a second product in the same shot arrives with Blender's ".001" on names it shares with the first
        parts[re.sub(r'\.\d{3,}$', '', o.name)] = o
    for o in new:
        if o.type != 'MESH':
            bpy.data.objects.remove(o, do_unlink=True)
    for o in parts.values():
        for c in list(o.users_collection):
            c.objects.unlink(o)
    return parts


def _resolve(v, flavour):
    if isinstance(v, str) and v.startswith('$'):
        return flavour[v[1:]]
    return v


def build_materials(bpy, pdef, flavour_name, shot_mats, tag):
    """The product's materials for one flavour, with the shot's overrides: by preset name (all paints) and by
    material name (one), the name winning."""
    fl = pdef['flavours'][flavour_name]
    out = {}
    for name, spec in pdef['materials'].items():
        spec = {k: _resolve(v, fl) for k, v in spec.items()}
        preset = spec.pop('preset')
        bevel = spec.pop('bevel_mm', 0.0)
        ov = {**spec, **shot_mats.get(preset, {}), **shot_mats.get(name, {})}
        ov = {k: v for k, v in ov.items() if k in M.PRESET_DEFAULTS[preset]}
        out[name] = M.make(bpy, f'{name}@{tag}', preset, ov, bevel_mm=bevel)
    return out


def _decal_nodes(mat, dec, img, ink_rgb, origin_mm=(0, 0, 0)):
    """Mix a print into a material's base colour: the image projected along the decal's normal in object space, only
    on faces facing that way and within 2 mm of its plane."""
    nt = mat.node_tree; b = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
    # the parts' meshes are in metres with origin_mm at (0, 0, 0) (import_model), so the decal's centre moves the same way
    c = (Vector(dec['center_mm']) - Vector(origin_mm)) / 1000.0; N = Vector(dec['normal']).normalized(); U0 = Vector(dec.get('up', (0, 0, 1)))
    R = U0.cross(N).normalized(); U = N.cross(R).normalized()      # R: the print's right as seen facing it
    w, h = [v / 1000.0 for v in dec['size_mm']]
    tc = nt.nodes.new('ShaderNodeTexCoord')
    sub = nt.nodes.new('ShaderNodeVectorMath'); sub.operation = 'SUBTRACT'; sub.inputs[1].default_value = c
    nt.links.new(tc.outputs['Object'], sub.inputs[0])
    def dot(vec):
        n_ = nt.nodes.new('ShaderNodeVectorMath'); n_.operation = 'DOT_PRODUCT'; n_.inputs[1].default_value = vec
        nt.links.new(sub.outputs['Vector'], n_.inputs[0]); return n_.outputs['Value']
    def affine(val, scale, add):
        m = nt.nodes.new('ShaderNodeMath'); m.operation = 'MULTIPLY_ADD'
        nt.links.new(val, m.inputs[0]); m.inputs[1].default_value = scale; m.inputs[2].default_value = add
        return m.outputs['Value']
    u = affine(dot(R), 1.0 / w, 0.5); v = affine(dot(U), 1.0 / h, 0.5)
    comb = nt.nodes.new('ShaderNodeCombineXYZ'); nt.links.new(u, comb.inputs['X']); nt.links.new(v, comb.inputs['Y'])
    tex = nt.nodes.new('ShaderNodeTexImage'); tex.image = img; tex.extension = 'CLIP'; tex.interpolation = 'Cubic'
    nt.links.new(comb.outputs['Vector'], tex.inputs['Vector'])
    if dec.get('mode', 'ink') == 'alpha':
        mask = tex.outputs['Alpha']
    else:
        # an opaque raster of dark ink on white: the ink's coverage is one minus its brightness
        # (outside the image CLIP returns transparent black, so the coverage is also multiplied by the alpha)
        bw = nt.nodes.new('ShaderNodeRGBToBW'); nt.links.new(tex.outputs['Color'], bw.inputs['Color'])
        inv = nt.nodes.new('ShaderNodeMath'); inv.operation = 'SUBTRACT'; inv.inputs[0].default_value = 1.0
        nt.links.new(bw.outputs['Val'], inv.inputs[1])
        ia = nt.nodes.new('ShaderNodeMath'); ia.operation = 'MULTIPLY'
        nt.links.new(inv.outputs['Value'], ia.inputs[0]); nt.links.new(tex.outputs['Alpha'], ia.inputs[1]); mask = ia.outputs['Value']
    # on the decal's plane only: |depth| < 2 mm and the face turned toward the decal's normal
    dep = nt.nodes.new('ShaderNodeMath'); dep.operation = 'ABSOLUTE'; nt.links.new(dot(N), dep.inputs[0])
    near = nt.nodes.new('ShaderNodeMath'); near.operation = 'LESS_THAN'; near.inputs[1].default_value = 0.002
    nt.links.new(dep.outputs['Value'], near.inputs[0])
    fdot = nt.nodes.new('ShaderNodeVectorMath'); fdot.operation = 'DOT_PRODUCT'; fdot.inputs[1].default_value = N
    nt.links.new(tc.outputs['Normal'], fdot.inputs[0])
    facing = nt.nodes.new('ShaderNodeMath'); facing.operation = 'GREATER_THAN'; facing.inputs[1].default_value = 0.7
    nt.links.new(fdot.outputs['Value'], facing.inputs[0])
    m1 = nt.nodes.new('ShaderNodeMath'); m1.operation = 'MULTIPLY'; nt.links.new(mask, m1.inputs[0]); nt.links.new(near.outputs['Value'], m1.inputs[1])
    m2 = nt.nodes.new('ShaderNodeMath'); m2.operation = 'MULTIPLY'; nt.links.new(m1.outputs['Value'], m2.inputs[0]); nt.links.new(facing.outputs['Value'], m2.inputs[1])
    mix = nt.nodes.new('ShaderNodeMix'); mix.data_type = 'RGBA'
    ins = [x for x in mix.inputs if x.type == 'RGBA']; outs = [x for x in mix.outputs if x.type == 'RGBA']
    base = b.inputs['Base Color']
    if base.links:
        nt.links.new(base.links[0].from_socket, ins[0])
    else:
        ins[0].default_value = base.default_value
    ins[1].default_value = (*ink_rgb, 1.0)
    nt.links.new(m2.outputs['Value'], mix.inputs['Factor']); nt.links.new(outs[0], base)


def interior_marker(templates, min_gap_mm=10.0):
    """Which faces of a part are inside the product, the faces a build leaves unfinished: from each face's centre, a
    ray along its normal and four tilted 30 degrees round it, against the whole assembled product; a face whose rays
    all meet the product again, the straight one further than min_gap_mm away (so a 3 mm shadow line stays painted),
    is inside. Returns mark(mesh, index): sets those faces' material index on a mesh in the product's frame. It is
    run on the assembled product, before an explode or a cut opens it."""
    from mathutils.bvhtree import BVHTree
    verts, polys = [], []
    for tpl in templates.values():
        M = tpl.matrix_world; base = len(verts)
        verts += [M @ v.co for v in tpl.data.vertices]
        polys += [[base + i for i in p.vertices] for p in tpl.data.polygons]
    bvh = BVHTree.FromPolygons(verts, polys)
    gap = min_gap_mm / 1000.0
    def tilted(n, deg):
        t1 = n.orthogonal().normalized(); t2 = n.cross(t1)
        c, s_ = math.cos(math.radians(deg)), math.sin(math.radians(deg))
        return [(n * c + t * s_).normalized() for t in (t1, -t1, t2, -t2)]
    def mark(me, idx):
        n_in = 0
        for p in me.polygons:
            c, n = p.center, p.normal
            if n.length < 0.5:
                continue
            o = c + n * 1e-4
            hit = bvh.ray_cast(o, n, 2.0)
            if hit[0] is None:
                continue
            # a wall of a cavity: the product again more than min_gap away, and all round at 30 degrees
            cavity = hit[3] > gap and all(bvh.ray_cast(o, d, 2.0)[0] is not None for d in tilted(n, 30))
            # a face another part covers (a pocket's wall under its insert): closed even at 60 degrees, within 5 mm;
            # a shadow line's walls fail both, its opening letting the steep rays out
            covered = not cavity and hit[3] <= gap and all(bvh.ray_cast(o, d, 0.005)[0] is not None for d in tilted(n, 60))
            if cavity or covered:
                p.material_index = idx; n_in += 1
        return n_in
    return mark


def place(bpy, pdef, templates, shot, root):
    """Link one copy of every part per instance, with its flavour's materials. Returns (objects, part_of) where
    part_of maps each object to its part name (for the masks)."""
    prod = shot.get('product', {})
    instances = prod.get('instances', [{'position': [0, 0, 0], 'rotate_z': 0}])
    shot_mats = shot.get('materials', {})
    objs, part_of = [], {}
    mats_by_flavour = {}
    images = {}
    # the inside of the product is left unfinished in a build: when it can be seen (a cutaway, an exploded view),
    # its faces take the "interior" rules' materials (raw birch, bare resin) instead of the paint and its zones
    inner_rules = pdef.get('interior', []) if (prod.get('cutaway') or prod.get('explode')) else []
    mark = interior_marker(templates) if inner_rules else None
    for i, inst in enumerate(instances):
        fl = inst.get('flavour', prod.get('flavour', next(iter(pdef['flavours']))))
        if fl not in mats_by_flavour:
            mats = build_materials(bpy, pdef, fl, shot_mats, fl)
            for dec in pdef.get('decals', []):
                if dec.get('flavours') and fl not in dec['flavours']:
                    continue
                ip = str(Path(root, dec['image']))
                if ip not in images:
                    images[ip] = bpy.data.images.load(ip, check_existing=True)
                    images[ip].colorspace_settings.name = 'sRGB'
                ink = _resolve(dec.get('ink', '#000000'), pdef['flavours'][fl])
                _decal_nodes(mats[dec['material']], dec, images[ip], M.hex_lin(ink)[:3], pdef['origin_mm'])
            mats_by_flavour[fl] = mats
        mats = mats_by_flavour[fl]
        T = Matrix.Translation(Vector(inst.get('position', (0, 0, 0)))) @ Matrix.Rotation(math.radians(inst.get('rotate_z', 0)), 4, 'Z')
        for pname, tpl in templates.items():
            if any(_match(pname, h) for h in prod.get('hide', [])):
                continue
            mat_name = next((r['material'] for r in pdef.get('assign', []) if _match(pname, r['match'])), None)
            if mat_name is None:
                continue
            me = tpl.data
            zones = [z for z in pdef.get('zones', []) if _match(pname, z['match'])]
            if zones:
                # a zone splits faces between materials: that needs this part's own mesh per flavour
                key = f'{pname}@{fl}'
                me = bpy.data.meshes.get(key) or _zoned_mesh(bpy, tpl.data, key, mats[mat_name], zones, mats)
            inner = next((r for r in inner_rules if _match(pname, r['match'])), None)
            if inner:
                key = f'{pname}@{fl if zones else "all"}@inside'
                if key in bpy.data.meshes:
                    me = bpy.data.meshes[key]
                else:
                    me = me.copy(); me.name = key
                    if not zones:
                        me.materials.clear(); me.materials.append(mats[mat_name])
                    me.materials.append(mats[inner['material']])
                    n_in = mark(me, len(me.materials) - 1)
                    print(f'interior: {pname} {n_in} of {len(me.polygons)} faces take {inner["material"]}')
            ob = bpy.data.objects.new(f'{pname}#{i}', me)
            bpy.context.scene.collection.objects.link(ob)
            ob['instance'] = i
            if not zones:
                # the mesh is shared by every copy: the material lives on the object, so flavours can differ
                ob.material_slots[0].link = 'OBJECT'; ob.material_slots[0].material = mats[mat_name]
            # an exploded view: the first rule that matches moves the part, in the product's frame (metres)
            off = next((r['offset_m'] for r in prod.get('explode', []) if _match(pname, r['match'])), None)
            ob.matrix_world = T @ Matrix.Translation(Vector(off)) if off else T
            objs.append(ob); part_of[ob.name] = pname
    if prod.get('cutaway'):
        cutaway(bpy, prod['cutaway'], instances, objs)
    return objs, part_of


def cutaway(bpy, spec, instances, objs):
    """Cut every part that crosses a box away (a boolean difference per part, the product's frame, metres), and paint
    the cut faces with one section material, the way a technical illustration shows the inside:

        "cutaway": {"box_m": [x0, y0, z0, x1, y1, z1], "skip": "pattern",
                    "sections": [{"match": "pattern", "color": "#D9C29B"}, ...]}

    A part wholly inside the box is hidden; parts matching "skip" are left whole (a cable drawn whole in front of
    the cut reads better than half a cable). A cut face takes the colour of the first "sections" rule its part
    matches (wood shows wood, a printed part its resin), else the part's own material, as a bought part's would."""
    import bmesh
    x0, y0, z0, x1, y1, z1 = spec['box_m']
    rules = spec.get('sections') or [{'match': '*', 'color': spec.get('color', '#D9C29B')}]
    secs = {}
    def section_for(pname):
        r = next((r for r in rules if _match(pname, r['match'])), None)
        if r is None:
            return None
        key = (r['color'], r.get('preset', 'birch'))
        if key not in secs:
            # wood sections take the birch shader (its grain); anything else a plain one ("preset": "plastic")
            ov = {'color': r['color'], 'roughness': r.get('roughness', 0.7)}
            secs[key] = M.make(bpy, f'section {r["color"]} {key[1]}', key[1], {k: v for k, v in ov.items() if k in M.PRESET_DEFAULTS[key[1]]})
        return secs[key]
    lo, hi = Vector((x0, y0, z0)), Vector((x1, y1, z1))
    by_inst = {}
    for ob in objs:
        by_inst.setdefault(ob['instance'], []).append(ob)
    for i, inst in enumerate(instances):
        T = Matrix.Translation(Vector(inst.get('position', (0, 0, 0)))) @ Matrix.Rotation(math.radians(inst.get('rotate_z', 0)), 4, 'Z')
        cme = bpy.data.meshes.new(f'cutter#{i}')
        bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0); bm.to_mesh(cme); bm.free()
        cutter = bpy.data.objects.new(f'cutter#{i}', cme)
        bpy.context.scene.collection.objects.link(cutter)
        cutter.matrix_world = T @ Matrix.Translation((lo + hi) / 2) @ Matrix.Diagonal((*(hi - lo), 1.0))
        cutter.hide_render = True; cutter.display_type = 'WIRE'
        Ti = T.inverted()
        for ob in by_inst.get(i, []):
            pname = re.sub(r'#\d+(\.\d+)?$', '', ob.name)
            if spec.get('skip') and _match(pname, spec['skip']):
                continue
            # the part's box in the product's frame (an exploded part is moved, so use its own matrix)
            cs = [Ti @ (ob.matrix_world @ Vector(c)) for c in ob.bound_box]
            plo = Vector((min(c.x for c in cs), min(c.y for c in cs), min(c.z for c in cs)))
            phi = Vector((max(c.x for c in cs), max(c.y for c in cs), max(c.z for c in cs)))
            if any(phi[k] <= lo[k] or plo[k] >= hi[k] for k in range(3)):
                continue                                   # clear of the box
            if all(plo[k] >= lo[k] and phi[k] <= hi[k] for k in range(3)):
                ob.hide_render = True; ob.hide_viewport = True
                continue                                   # wholly inside it
            mats = [sl.material for sl in ob.material_slots]
            me = ob.data.copy(); ob.data = me
            bm = bmesh.new(); bm.from_mesh(me)
            bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
            bm.to_mesh(me); bm.free()
            me.set_sharp_from_angle(angle=math.radians(35))
            mod = ob.modifiers.new('cut', 'BOOLEAN')
            mod.operation = 'DIFFERENCE'; mod.object = cutter; mod.solver = 'EXACT'; mod.use_hole_tolerant = True
            dg = bpy.context.evaluated_depsgraph_get()
            new = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
            ob.modifiers.remove(mod)
            # set the slots in place: clearing a mesh's materials resets every face's index to the first
            for k, m in enumerate(mats):
                if k < len(new.materials):
                    new.materials[k] = m
                else:
                    new.materials.append(m)
            sec = section_for(pname)
            if sec is None:
                ob.data = new
                for sl in ob.material_slots:
                    sl.link = 'DATA'
                continue
            si = len(new.materials)
            new.materials.append(sec)
            # the cut faces lie on the box's walls and face into it (toward what was cut away)
            W = Ti @ ob.matrix_world
            R = W.to_3x3()
            for p in new.polygons:
                c = W @ p.center; n = (R @ p.normal).normalized()
                for k in range(3):
                    if (abs(c[k] - lo[k]) < 2e-5 and n[k] > 0.99) or (abs(c[k] - hi[k]) < 2e-5 and n[k] < -0.99):
                        if all(lo[j] - 2e-5 <= c[j] <= hi[j] + 2e-5 for j in range(3) if j != k):
                            p.material_index = si
            ob.data = new
            for sl in ob.material_slots:
                sl.link = 'DATA'



def _zoned_mesh(bpy, src, key, base_mat, zones, mats):
    import bmesh
    me = src.copy(); me.name = key
    # cut the faces at each zone's boundary first: a face that spans it (a tall rounded corner, one strip from the
    # floor to the eave) would otherwise take one material by its centre and leave a stripe of the wrong colour
    bm = bmesh.new(); bm.from_mesh(me)
    for z in zones:
        for k in ('above_z_mm', 'below_z_mm'):
            if k in z:
                geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
                bmesh.ops.bisect_plane(bm, geom=geom, dist=1e-7, plane_co=(0, 0, z[k] / 1000.0), plane_no=(0, 0, 1))
    bm.to_mesh(me); bm.free()
    me.materials.clear(); me.materials.append(base_mat)
    idx = {}
    for z in zones:
        m = mats[z['material']]
        if m.name not in idx:
            me.materials.append(m); idx[m.name] = len(me.materials) - 1
    for p in me.polygons:
        cz = p.center.z * 1000.0
        mi = 0
        for z in zones:
            lo, hi = z.get('above_z_mm', -1e9), z.get('below_z_mm', 1e9)
            if lo <= cz <= hi:
                mi = idx[mats[z['material']].name]
        p.material_index = mi
    return me


def bounds(objs):
    lo = Vector((1e9, 1e9, 1e9)); hi = -lo
    for o in objs:
        for c in o.bound_box:
            w = o.matrix_world @ Vector(c)
            lo = Vector((min(lo.x, w.x), min(lo.y, w.y), min(lo.z, w.z))); hi = Vector((max(hi.x, w.x), max(hi.y, w.y), max(hi.z, w.z)))
    return lo, hi
