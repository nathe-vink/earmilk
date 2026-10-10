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
    zones        [{"match": "...", "below_z_mm": 110, "material": "accent", "part": "plinth"}]: faces of matching parts
                 whose centre is below (or above, with above_z_mm) a height take another material (a painted band on
                 one panel). A shot with `product.zone_parts` true splits a zone that names a `part` off as its own
                 part, "back-panel.plinth": a lamp can then be linked to the band alone. A part's patterns match its
                 zone parts too ("back-panel" takes "back-panel.plinth"; "*.plinth" only the bands).
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
    # a zone part ("back-panel.plinth") answers to its own name and to its part's
    names = (name, name.split('.', 1)[0]) if '.' in name else (name,)
    return any(fnmatch.fnmatchcase(n, p.strip()) for n in names for p in pattern.split('|'))


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


def _upsample(A, f, axis=0, closed=False):
    """A sampled surface (S, T, 3) made f times finer along `axis` by Catmull-Rom between its samples (closed: the
    axis wraps round)."""
    import numpy as np
    A = np.moveaxis(A, axis, 0)
    n = A.shape[0]
    idx = lambda k: (k % n) if closed else min(max(k, 0), n - 1)
    out = []
    segs = n if closed else n - 1
    for k in range(segs):
        p0, p1, p2, p3 = A[idx(k - 1)], A[idx(k)], A[idx(k + 1)], A[idx(k + 2)]
        for s in range(f):
            t = s / f
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    if not closed:
        out.append(A[-1])
    return np.moveaxis(np.array(out), 0, axis)


def _grid_normal(p, quad, V, NV):
    """The grid's normal at p, linear across the triangle of the quad p lies on (a, b, c or a, c, d): continuous
    across the grid, where weighting the four corners by distance spikes at each one and a mirrored edge saw-tooths
    at the grid's spacing."""
    a, b, c, d = (Vector(V[k]) for k in quad)
    na, nb, nc, nd = (Vector(NV[k]) for k in quad)
    for (t0, t1, t2), (m0, m1, m2) in (((a, b, c), (na, nb, nc)), ((a, c, d), (na, nc, nd))):
        v0, v1, v2 = t1 - t0, t2 - t0, p - t0
        d00, d01, d11, d20, d21 = v0.dot(v0), v0.dot(v1), v1.dot(v1), v2.dot(v0), v2.dot(v1)
        den = d00 * d11 - d01 * d01
        if abs(den) < 1e-18:
            continue
        w1 = (d11 * d20 - d01 * d21) / den; w2 = (d00 * d21 - d01 * d20) / den; w0 = 1.0 - w1 - w2
        if min(w0, w1, w2) >= -1e-3:
            w0, w1, w2 = max(w0, 0.0), max(w1, 0.0), max(w2, 0.0)
            return (m0 * w0 + m1 * w1 + m2 * w2).normalized()
    return min(((a, na), (b, nb), (c, nc), (d, nd)), key=lambda tm: (p - tm[0]).length)[1].normalized()


def normals_from(bpy, parts, rules, origin_mm, root):
    """Shading normals from the true surface: a CAD surface tessellated into flat facets (a waveguide made as a ruled
    loft through polygon rings) mirrors a light as stair-steps however its vertices are smoothed, because its long
    thin triangles bend the interpolated normal. For each part a rule matches, every face corner within `within_mm` of
    the rule's grid (the surface sampled finely: meridians x stations x 3 in the CAD's mm, with its unit normals into
    the air) takes the grid's normal there, interpolated across the grid's quad; the rest keep their own. The geometry
    stays the CAD's.

        "normals_from": [{"match": "waveguide-insert", "grid": "fab/out/render/earmilk-floorstander-horn.npy",
                          "normals": "fab/out/render/earmilk-floorstander-horn-normals.npy", "within_mm": 0.3}]
    """
    import numpy as np
    from mathutils.bvhtree import BVHTree
    for name, ob in parts.items():
        r = next((r for r in rules if _match(name, r['match'])), None)
        if r is None:
            continue
        G = np.load(Path(root, r['grid'])); NG = np.load(Path(root, r['normals']))
        S, T = G.shape[:2]
        V = ((G - np.array(origin_mm, dtype=float)) / 1000.0).reshape(-1, 3)
        NV = NG.reshape(-1, 3)
        quads = [((i % S) * T + j, ((i + 1) % S) * T + j, ((i + 1) % S) * T + j + 1, (i % S) * T + j + 1)
                 for i in range(S) for j in range(T - 1)]
        bvh = BVHTree.FromPolygons(V.tolist(), quads)
        me = ob.data
        skin_normals = {}
        within = r.get('within_mm', 0.3) / 1000.0
        if r.get('refine'):
            # normals alone cannot fix a long thin facet: the normal interpolated across it still kinks at its edges,
            # and a mirrored light's edge saw-tooths along them. Cut each facet on the surface into refine+1 a side
            # and set the new corners on the true surface (each one's nearest point on the grid)
            import bmesh
            bm = bmesh.new(); bm.from_mesh(me)
            on = {v: bvh.find_nearest(v.co, within)[0] is not None for v in bm.verts}
            faces = [f for f in bm.faces if all(on[v] for v in f.verts)]
            edges = list({e for f in faces for e in f.edges})
            res = bmesh.ops.subdivide_edges(bm, edges=edges, cuts=int(r['refine']), use_grid_fill=True)
            moved = 0
            for v in (g for g in res['geom'] if isinstance(g, bmesh.types.BMVert)):
                if v in on:
                    continue
                loc = bvh.find_nearest(v.co, 4 * within)[0]
                if loc is not None:
                    v.co = loc; moved += 1
            n0 = len(me.polygons)
            bm.to_mesh(me); bm.free(); me.update()
            for poly in me.polygons:
                poly.use_smooth = True
            print(f'normals: {name}: {len(faces)} facets on the surface refined x{int(r["refine"]) + 1} a side, '
                  f'{n0} to {len(me.polygons)} faces, {moved} new corners set on it')
        if r.get('skin'):
            # the true surface itself, as fine as the grid, a hair into the air over the CAD's facets (refined first:
            # on a concave bowl a flat facet bulges into the air by its sagitta, 0.16 mm on the ruled loft's coarsest,
            # and pokes through a skin laid closer than that)
            import bmesh
            off = r.get('skin_offset_mm', 0.05) / 1000.0
            up = int(r['skin']) if not isinstance(r['skin'], bool) else 1
            SV, SN = G.astype(float), NG.astype(float)
            if up > 1:
                # Catmull-Rom between the grid's samples, round the axis (closed) and along the wall (open): a skin up
                # times finer, since Cycles keeps a grazing reflection above each flat triangle and the correction
                # steps at the triangles' size
                SV, SN = _upsample(SV, up, closed=True), _upsample(SN, up, closed=True)
                SV, SN = _upsample(SV, up, axis=1), _upsample(SN, up, axis=1)
                SN /= np.linalg.norm(SN, axis=2, keepdims=True)
            S2, T2 = SV.shape[:2]
            SVf = ((SV - np.array(origin_mm, dtype=float)) / 1000.0).reshape(-1, 3); SNf = SN.reshape(-1, 3)
            squads = [((i % S2) * T2 + j, ((i + 1) % S2) * T2 + j, ((i + 1) % S2) * T2 + j + 1, (i % S2) * T2 + j + 1)
                      for i in range(S2) for j in range(T2 - 1)]
            bm = bmesh.new(); bm.from_mesh(me)
            n_before = len(bm.verts)
            vs = [bm.verts.new(Vector(SVf[k]) + Vector(SNf[k]) * off) for k in range(len(SVf))]
            bm.verts.ensure_lookup_table()
            nf = 0
            for q in squads:
                try:
                    # wound so the face's normal points into the air, as the grid's normals do
                    f = bm.faces.new([vs[k] for k in q])
                except ValueError:
                    continue
                f.normal_update()                          # a new face's normal is not computed until asked
                if f.normal.dot(Vector(SNf[q[0]])) < 0:
                    f.normal_flip()
                f.smooth = True; f.material_index = 0; nf += 1
            bm.to_mesh(me); bm.free(); me.update()
            print(f'normals: {name}: a skin of {nf} faces from {r["grid"]} (x{up}), {off * 1000:g} mm over the facets')
            if up > 1:
                # the skin's own corners take its interpolated normals directly; the facets beneath go through the BVH
                skin_normals = {n_before + k: Vector(SNf[k]) for k in range(len(SNf))}
        corner = [Vector(c.vector) for c in me.corner_normals]
        at_vertex, changed = {}, 0
        for li, loop in enumerate(me.loops):
            vi = loop.vertex_index
            if vi in skin_normals:
                corner[li] = skin_normals[vi]; changed += 1
                continue
            if vi not in at_vertex:
                loc, _, fi, _ = bvh.find_nearest(me.vertices[vi].co, within)
                if loc is None:
                    at_vertex[vi] = None
                else:
                    at_vertex[vi] = _grid_normal(loc, quads[fi], V, NV)
            n = at_vertex[vi]
            if n is not None and n.dot(corner[li]) > 0.5:
                corner[li] = n; changed += 1
        me.normals_split_custom_set([tuple(c) for c in corner])
        print(f'normals: {name}: {changed} of {len(me.loops)} corners from {r["grid"]}')


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
        # a smooth-shaded facet at a grazing angle to a lamp shadows its neighbours in steps along the terminator (the
        # waveguide's saw-tooth: the shadow map showed it on the key's and fill's terminators, not in a reflection);
        # Cycles offsets such shadow rays to the smooth surface the normals describe
        o.shadow_terminator_geometry_offset = 1.0
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
        # a colour the flavour sets on a paint (body, accent, insert) is a swatch the retouch matches (retouch.py)
        raw = pdef['materials'][name].get('color', '')
        if isinstance(raw, str) and raw.startswith('$') and preset not in ('metal', 'gunmetal', 'emit') \
                and isinstance(ov.get('color'), str) and ov['color'].startswith('#'):
            out[name]['swatch'] = ov['color']; out[name]['swatch_name'] = name
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


def interior_marker(templates, min_gap_mm=10.0, ignore=None):
    """Which faces of a part are inside the product, the faces a build leaves unfinished: from each face's centre, a
    ray along its normal and four tilted 30 degrees round it, against the whole assembled product; a face whose rays
    all meet the product again, the straight one further than min_gap_mm away (so a 3 mm shadow line stays painted),
    is inside. Returns mark(mesh, index): sets those faces' material index on a mesh in the product's frame. It is
    run on the assembled product, before an explode or a cut opens it."""
    from mathutils.bvhtree import BVHTree
    verts, polys = [], []
    for pname, tpl in templates.items():
        if ignore and _match(pname, ignore):
            continue                                  # loose things in a cavity (a cable, a plug) do not make its walls
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
            # a face another part covers (a pocket's wall under its insert): closed even at 60 degrees, within 12 mm;
            # a shadow line's walls fail both, its opening letting the steep rays out
            covered = not cavity and hit[3] <= gap and all(bvh.ray_cast(o, d, 0.012)[0] is not None for d in tilted(n, 60))
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
    mark = interior_marker(templates, ignore=pdef.get('interior_ignore')) if inner_rules else None
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
            # the zones that name a part, split off as parts of their own when the shot asks (04b's red plinth, to be
            # lit without the white above it)
            pieces = [(pname, me)]
            if zones and prod.get('zone_parts') and any(z.get('part') for z in zones):
                # in a cutaway or an exploded view the inside's faces (the last material) stay with the panel; only its
                # outside's zone goes to the zone part (07 e12: skipped there, '*.plinth' matched nothing)
                pieces = _split_zones(bpy, me, pname, zones, inner_idx=len(me.materials) - 1 if inner else None)
            for pn, me_ in pieces:
                ob = bpy.data.objects.new(f'{pn}#{i}', me_)
                bpy.context.scene.collection.objects.link(ob)
                ob['instance'] = i
                if not zones:
                    # the mesh is shared by every copy: the material lives on the object, so flavours can differ
                    ob.material_slots[0].link = 'OBJECT'; ob.material_slots[0].material = mats[mat_name]
                # an exploded view: the first rule that matches moves the part, in the product's frame (metres)
                off = next((r['offset_m'] for r in prod.get('explode', []) if _match(pname, r['match'])), None)
                ob.matrix_world = T @ Matrix.Translation(Vector(off)) if off else T
                objs.append(ob); part_of[ob.name] = pn
    if prod.get('cutaway'):
        cutaway(bpy, prod['cutaway'], instances, objs, pdef.get('laminated', {}))
    return objs, part_of


def cutaway(bpy, spec, instances, objs, laminated=None):
    """Cut every part that crosses a box away (a boolean difference per part, the product's frame, metres), and paint
    the cut faces with one section material, the way a technical illustration shows the inside:

        "cutaway": {"box_m": [x0, y0, z0, x1, y1, z1], "skip": "pattern",
                    "sections": [{"match": "pattern", "color": "#D9C29B"}, ...]}

    A part wholly inside the box is hidden; parts matching "skip" are left whole (a cable drawn whole in front of
    the cut reads better than half a cable). A cut face takes the colour of the first "sections" rule its part
    matches (wood shows wood, a printed part its resin), else the part's own material, as a bought part's would.
    A plywood panel's cut face shows its veneers; a block the product file lists under `laminated` ({part pattern:
    sheet thickness, mm}) shows the plies of the sheets it was glued up from, stacked up the vertical."""
    laminated = laminated or {}
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
            rule = next((r for r in rules if _match(pname, r['match'])), None)
            if sec is not None and rule.get('preset', 'birch') == 'birch' and rule.get('plies', True):
                plate = _plate(ob)
                lay = next((v for k_, v in laminated.items() if _match(pname, k_)), None)
                if plate:          # a plywood panel's cut face shows its veneers
                    axis, plo_, th_local, th_mm = plate
                    sec = M.ply_section(bpy, f'section plies {pname}', rule['color'], rule.get('roughness', 0.7), axis, plo_,
                                        th_local, max(3, int(round(th_mm / 1.4)) | 1))
                elif lay:          # a block glued up from plywood sheets: each sheet's 13 plies, stacked up the vertical
                    Rm = ob.matrix_world.to_3x3()
                    k_ = max(range(3), key=lambda j: abs(Rm.col[j].normalized().z))
                    bb = [Vector(c) for c in ob.bound_box]
                    lo_k = min(c[k_] for c in bb); d_k = max(c[k_] for c in bb) - lo_k
                    th_mm = d_k * Rm.col[k_].length * 1000.0
                    sec = M.ply_section(bpy, f'section layers {pname}', rule['color'], rule.get('roughness', 0.7), k_, lo_k,
                                        d_k, max(13, int(round(th_mm / lay * 13))), per_layer=13)
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
            cut = []
            for p in new.polygons:
                c = W @ p.center; n = (R @ p.normal).normalized()
                for k in range(3):
                    if (abs(c[k] - lo[k]) < 2e-5 and n[k] > 0.99) or (abs(c[k] - hi[k]) < 2e-5 and n[k] < -0.99):
                        if all(lo[j] - 2e-5 <= c[j] <= hi[j] + 2e-5 for j in range(3) if j != k):
                            p.material_index = si; cut.append(p.index)
                            break
            if cut:
                # a cut face is a plane: its own normal at every corner and flat shaded. The boolean's caps otherwise take
                # normals blended from the part's sides, a soft dark smudge across the section (08b's tweeter frame)
                ln = [tuple(cn.vector) for cn in new.corner_normals]
                for pi in cut:
                    p = new.polygons[pi]; nn = tuple(p.normal)
                    for li in p.loop_indices:
                        ln[li] = nn
                    p.use_smooth = False
                new.normals_split_custom_set(ln)
            ob.data = new
            for sl in ob.material_slots:
                sl.link = 'DATA'



def _plate(ob):
    """A panel's thin axis in its own coordinates: (axis, low end, thickness in its units, thickness in mm), or None
    for a part that is not a plate (thicker than 40 mm, or not thin against its other sides)."""
    cs = [Vector(c) for c in ob.bound_box]
    lo = [min(c[k] for c in cs) for k in range(3)]; dims = [max(c[k] for c in cs) - lo[k] for k in range(3)]
    order = sorted(range(3), key=lambda k: dims[k])
    thin = order[0]
    if dims[thin] <= 0 or dims[thin] / max(dims[order[1]], 1e-9) > 0.2:
        return None
    th_mm = dims[thin] * ob.matrix_world.to_scale()[thin] * 1000.0
    if th_mm > 40:
        return None
    return thin, lo[thin], dims[thin], th_mm


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


def _zone_of(zones, cz):
    """The zone a face whose centre is at height cz (mm) falls in: the last that holds it, as _zoned_mesh assigns."""
    hit = None
    for z in zones:
        if z.get('above_z_mm', -1e9) <= cz <= z.get('below_z_mm', 1e9):
            hit = z
    return hit


def _split_zones(bpy, me, pname, zones, inner_idx=None):
    """A zoned mesh in pieces: [(part name, mesh)], the faces outside every named zone under the part's own name, each
    named zone's as "part.zone" (its faces, materials and normals as they were; one mesh per flavour, as the zoned mesh).
    Faces with material `inner_idx` (the inside of a cut or exploded panel) stay with the part."""
    import bmesh
    named = [z for z in zones if z.get('part')]
    out = []
    for target in [None] + named:
        pn = f'{pname}.{target["part"]}' if target else pname
        key = f'{me.name}|{pn}'
        m2 = bpy.data.meshes.get(key)
        if m2 is None:
            m2 = me.copy(); m2.name = key
            bm = bmesh.new(); bm.from_mesh(m2)
            kill = []
            for f in bm.faces:
                z = _zone_of(zones, f.calc_center_median().z * 1000.0)
                z = z if (z is not None and z.get('part')) else None
                if inner_idx is not None and f.material_index == inner_idx:
                    z = None
                if z is not target:
                    kill.append(f)
            bmesh.ops.delete(bm, geom=kill, context='FACES')
            bm.to_mesh(m2); bm.free()
        if len(m2.polygons):
            out.append((pn, m2))
    return out


def bounds(objs):
    lo = Vector((1e9, 1e9, 1e9)); hi = -lo
    for o in objs:
        for c in o.bound_box:
            w = o.matrix_world @ Vector(c)
            lo = Vector((min(lo.x, w.x), min(lo.y, w.y), min(lo.z, w.z))); hi = Vector((max(hi.x, w.x), max(hi.y, w.y), max(hi.z, w.z)))
    return lo, hi
