"""Sets for the engine: a studio sweep and a room with a real window. Built from the shot's `set` entry; lengths in
metres, the floor at z = 0, the product standing at the origin with its front toward -y (the camera's side).

sweep: a seamless cove (floor, a curve of `radius`, a back wall) in one colour, wide and deep enough that the frame never
       finds its edge; optional `flags` (black cards for negative fill) and `bounces` (white cards).
room:  a closed box (floor, four walls, ceiling) so light bounces as it does indoors: oak boards, plaster walls with a
       skirting, and windows cut through a wall, each with a frame, mullions and a sill, a sky outside (the world) and a
       portal in the opening so the sky's light through it converges. The sun comes through the windows by itself.
       `props`: simple furniture and a rug, placed in metres.
"""
import math

import bmesh
from mathutils import Vector

try:
    from . import materials as M
except ImportError:
    import materials as M


def _obj(bpy, name, me, mat=None):
    ob = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(ob)
    if mat is not None:
        ob.data.materials.append(mat)
    return ob


def box(bpy, name, x0, y0, z0, x1, y1, z1, mat=None, bevel=0.0):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = Vector(((x0 + x1) / 2 + v.co.x * (x1 - x0), (y0 + y1) / 2 + v.co.y * (y1 - y0), (z0 + z1) / 2 + v.co.z * (z1 - z0)))
    if bevel > 0:
        bmesh.ops.bevel(bm, geom=bm.edges[:], offset=bevel, segments=2, affect='EDGES')
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    return _obj(bpy, name, me, mat)


def plane(bpy, name, corners, mat=None, uv=True):
    me = bpy.data.meshes.new(name)
    me.from_pydata([Vector(c) for c in corners], [], [(0, 1, 2, 3)])
    if uv:
        me.uv_layers.new()
    return _obj(bpy, name, me, mat)


# --- sweep ---------------------------------------------------------------------------------------------------------
def sweep(bpy, spec, mats):
    """A cove: floor from y = -front to the curve, the curve of `radius`, the wall up to `height`, `width` across."""
    W, front, back = spec.get('width', 8.0), spec.get('front', 6.0), spec.get('depth', 2.0)
    R, H = spec.get('radius', 1.0), spec.get('height', 5.0)
    prof = [(-front, 0.0)]
    n = 24
    for i in range(n + 1):
        a = -math.pi / 2 + (math.pi / 2) * i / n
        prof.append((back - R + R * math.cos(a), R + R * math.sin(a)))
    prof.append((back, H))
    xs = [-W / 2, W / 2]
    verts = [(x, y, z) for (y, z) in prof for x in xs]
    faces = [(2 * i, 2 * i + 1, 2 * i + 3, 2 * i + 2) for i in range(len(prof) - 1)]
    me = bpy.data.meshes.new('sweep'); me.from_pydata(verts, [], faces)
    for p in me.polygons: p.use_smooth = True
    mat = M.make(bpy, 'sweep', 'sweep', {'color': spec.get('color', '#B9B5AE'), **mats.get('sweep', {})})
    ob = _obj(bpy, 'sweep', me, mat)
    for i, f in enumerate(spec.get('flags', [])):
        _card(bpy, f'flag{i}', f, '#050505')
    for i, f in enumerate(spec.get('bounces', [])):
        _card(bpy, f'bounce{i}', f, '#F2F2F2')
    return [ob]


def _card(bpy, name, f, color):
    """A vertical card `size` [w, h] at `position` (its bottom centre), facing `target`; unseen by the camera."""
    w, h = f.get('size', [1.0, 2.0])
    p = Vector(f['position']); t = Vector(f.get('target', (0, 0, p.z + h / 2)))
    d = Vector((t.x - p.x, t.y - p.y, 0)).normalized(); side = Vector((-d.y, d.x, 0))
    c = [p - side * w / 2, p + side * w / 2, p + side * w / 2 + Vector((0, 0, h)), p - side * w / 2 + Vector((0, 0, h))]
    m = M.make(bpy, name, 'satin_paint', {'color': color, 'roughness': 0.9, 'specular': 0.1})
    ob = plane(bpy, name, c, m)
    ob.visible_camera = f.get('camera', False)
    return ob


# --- room ----------------------------------------------------------------------------------------------------------
def room(bpy, spec, mats):
    """A closed room. spec: size [w (x), d (y), h], origin of the room's floor centre `center` [x, y], `floor`
    (oak overrides), `wall` (plaster overrides), `skirting` {h, color}, `windows` [{wall: left|right|back|front,
    along: m from the wall's centre, sill: m, size: [w, h], mullions: [cols, rows], frame: hex}], `props`."""
    w, d, h = spec.get('size', [6.0, 6.0, 2.8])
    cx, cy = spec.get('center', [0.0, 1.0])
    x0, x1, y0, y1 = cx - w / 2, cx + w / 2, cy - d / 2, cy + d / 2
    objs = []
    oak = M.make(bpy, 'floor', 'oak', mats.get('oak', {}) | spec.get('floor', {}))
    objs.append(plane(bpy, 'floor', [(x0, y0, 0), (x1, y0, 0), (x1, y1, 0), (x0, y1, 0)], oak))
    plaster = M.make(bpy, 'wall', 'plaster', mats.get('plaster', {}) | spec.get('wall', {}))
    ceil = M.make(bpy, 'ceiling', 'plaster', {'color': spec.get('ceiling', '#F1EEE8'), 'bump': 0.0})
    objs.append(plane(bpy, 'ceiling', [(x0, y0, h), (x0, y1, h), (x1, y1, h), (x1, y0, h)], ceil))
    walls = {
        'back':  ((x0, y1), (x1, y1)),
        'front': ((x1, y0), (x0, y0)),
        'left':  ((x0, y0), (x0, y1)),
        'right': ((x1, y1), (x1, y0)),
    }
    wins = spec.get('windows', [])
    frame_mat = M.make(bpy, 'window-frame', 'satin_paint', {'color': spec.get('frame', '#EDEBE6'), 'roughness': 0.35, 'specular': 0.5})
    sill_mat = frame_mat
    for name, (a, b) in walls.items():
        holes = [wi for wi in wins if wi.get('wall') == name]
        objs += _wall(bpy, f'wall-{name}', Vector((*a, 0)), Vector((*b, 0)), h, holes, plaster, frame_mat, sill_mat)
    sk = spec.get('skirting', {'h': 0.1, 'color': '#EEECE7'})
    if sk:
        skm = M.make(bpy, 'skirting', 'satin_paint', {'color': sk.get('color', '#EEECE7'), 'roughness': 0.3, 'specular': 0.5})
        t, hh = sk.get('t', 0.016), sk.get('h', 0.1)
        for name, (a, b) in walls.items():
            if name == 'front' and not sk.get('front', False):
                continue
            objs += _skirting(bpy, f'skirting-{name}', Vector((*a, 0)), Vector((*b, 0)), t, hh, skm,
                              [wi for wi in wins if wi.get('wall') == name and wi.get('sill', 1) < hh])
    wa = spec.get('wainscot')
    if wa:
        objs += _wainscot(bpy, walls, wins, wa)
    for i, p in enumerate(spec.get('props', [])):
        objs += prop(bpy, f'prop{i}-{p["kind"]}', p, mats)
    return objs


def _wainscot(bpy, walls, wins, wa):
    """Panelling below a dado rail on each wall but the front: a painted board, raised panels and the rail, broken
    where a window's sill comes lower than the rail."""
    H = wa.get('height', 0.9); col = wa.get('color', '#CFC3AE')
    paint = M.make(bpy, 'wainscot', 'satin_paint', {'color': col, 'roughness': 0.38, 'specular': 0.5})
    out = []
    for name, (a, b) in walls.items():
        if name == 'front' and not wa.get('front', False):
            continue
        a = Vector((*a, 0)); b = Vector((*b, 0)); L = (b - a).length; u = (b - a).normalized(); n_in = Vector((u.y, -u.x, 0))
        segs = [(0.0, L)]
        for wi in wins:
            if wi.get('wall') != name or wi.get('sill', 1) >= H: continue
            ww = wi['size'][0]; c = L / 2 + wi.get('along', 0.0)
            new = []
            for s0, s1 in segs:
                if c - ww / 2 - 0.05 > s0: new.append((s0, min(s1, c - ww / 2 - 0.05)))
                if c + ww / 2 + 0.05 < s1: new.append((max(s0, c + ww / 2 + 0.05), s1))
            segs = new
        for k, (s0, s1) in enumerate(segs):
            def bx(nm, t0, t1, z0, z1, d0, d1):
                p0 = a + u * t0 + n_in * d0; p1 = a + u * t1 + n_in * d1
                lo = Vector((min(p0.x, p1.x), min(p0.y, p1.y), z0)); hi = Vector((max(p0.x, p1.x), max(p0.y, p1.y), z1))
                return box(bpy, nm, lo.x, lo.y, lo.z, hi.x, hi.y, hi.z, paint, bevel=0.002)
            out.append(bx(f'wainscot-{name}{k}', s0, s1, 0.0, H, 0.0, 0.012))
            out.append(bx(f'dado-{name}{k}', s0, s1, H - 0.02, H + 0.03, 0.0, 0.03))
            pw = wa.get('panel_w', 0.6); n = max(1, int((s1 - s0 - 0.1) / pw))
            step = (s1 - s0) / n
            for i in range(n):
                t0 = s0 + i * step + 0.07; t1 = s0 + (i + 1) * step - 0.07
                if t1 - t0 < 0.15: continue
                out.append(bx(f'panel-{name}{k}-{i}', t0, t1, 0.2, H - 0.1, 0.012, 0.02))
    return out


def _wall(bpy, name, a, b, h, holes, mat, frame_mat, sill_mat):
    """A wall from a to b (its inner face; the room on the right as you walk a->b), with rectangular openings. Built as a
    thick slab with boolean-free geometry: the face is split round each hole, and each hole gets reveals, a frame,
    mullions and a sill."""
    along = (b - a); L = along.length; u = along.normalized()
    n_out = Vector((-u.y, u.x, 0)); n_in = -n_out      # the walls run with the room on their right: left is outside
    T = 0.2   # wall thickness
    # rectangles of the wall face not covered by holes: split by the holes' x-extents into columns
    hs = []
    for wi in holes:
        ww, wh = wi['size']; c = L / 2 + wi.get('along', 0.0); s0 = wi.get('sill', 0.9)
        hs.append((c - ww / 2, c + ww / 2, s0, s0 + wh, wi))
    xs = sorted({0.0, L, *[v for hh in hs for v in hh[:2]]})
    quads = []
    for i in range(len(xs) - 1):
        xa, xb = xs[i], xs[i + 1]; xm = (xa + xb) / 2
        inside = [hh for hh in hs if hh[0] <= xm <= hh[1]]
        zs = [0.0, h]
        for hh in inside: zs += [hh[2], hh[3]]
        zs = sorted(set(zs))
        for j in range(len(zs) - 1):
            za, zb = zs[j], zs[j + 1]; zm = (za + zb) / 2
            if any(hh[2] <= zm <= hh[3] for hh in inside):
                continue
            quads.append((xa, xb, za, zb))
    verts, faces = [], []
    def P(x, z, off=0.0): return a + u * x + Vector((0, 0, z)) + n_out * off   # off > 0: into the wall, toward outside
    for (xa, xb, za, zb) in quads:
        k = len(verts); verts += [P(xa, za), P(xb, za), P(xb, zb), P(xa, zb)]; faces.append((k, k + 1, k + 2, k + 3))
    objs = []
    me = bpy.data.meshes.new(name); me.from_pydata(verts, [], faces); me.uv_layers.new()
    objs.append(_obj(bpy, name, me, mat))
    # each opening: four reveals through the wall's thickness, a frame, mullions, a sill; a portal outside
    for (xa, xb, za, zb, wi) in hs:
        rv, rf = [], []
        for (p0, p1) in (((xa, za), (xb, za)), ((xb, za), (xb, zb)), ((xb, zb), (xa, zb)), ((xa, zb), (xa, za))):
            k = len(rv); rv += [P(*p0), P(*p1), P(*p1, T), P(*p0, T)]; rf.append((k, k + 1, k + 2, k + 3))
        rme = bpy.data.meshes.new(name + '-reveal'); rme.from_pydata(rv, [], rf); rme.uv_layers.new()
        objs.append(_obj(bpy, name + '-reveal', rme, mat))
        fw = wi.get('frame_w', 0.05); fd = wi.get('frame_d', 0.06); inset = wi.get('inset', 0.12)
        cols, rows = wi.get('mullions', [2, 2])
        def frame_bar(nm, x0_, x1_, z0_, z1_):
            c0 = P(x0_, z0_, inset); c1 = P(x1_, z1_, inset + fd)
            lo = Vector((min(c0.x, c1.x), min(c0.y, c1.y), min(c0.z, c1.z))); hi = Vector((max(c0.x, c1.x), max(c0.y, c1.y), max(c0.z, c1.z)))
            return box(bpy, nm, lo.x, lo.y, lo.z, hi.x, hi.y, hi.z, frame_mat, bevel=0.003)
        objs.append(frame_bar(name + '-frame-b', xa, xb, za, za + fw)); objs.append(frame_bar(name + '-frame-t', xa, xb, zb - fw, zb))
        objs.append(frame_bar(name + '-frame-l', xa, xa + fw, za, zb)); objs.append(frame_bar(name + '-frame-r', xb - fw, xb, za, zb))
        mw = wi.get('mullion_w', 0.03)
        for c in range(1, cols):
            x = xa + (xb - xa) * c / cols
            objs.append(frame_bar(f'{name}-mullion-v{c}', x - mw / 2, x + mw / 2, za, zb))
        for r in range(1, rows):
            z = za + (zb - za) * r / rows
            objs.append(frame_bar(f'{name}-mullion-h{r}', xa, xb, z - mw / 2, z + mw / 2))
        if wi.get('sill_board', True):
            s0 = P(xa - 0.04, za - 0.03, -0.04); s1 = P(xb + 0.04, za, T * 0.6)
            lo = Vector((min(s0.x, s1.x), min(s0.y, s1.y), min(s0.z, s1.z))); hi = Vector((max(s0.x, s1.x), max(s0.y, s1.y), max(s0.z, s1.z)))
            objs.append(box(bpy, name + '-sill', lo.x, lo.y, lo.z, hi.x, hi.y, hi.z, sill_mat, bevel=0.004))
        # the portal: an area lamp in the opening's outer face, facing in, adding no light of its own
        L = bpy.data.lights.new(name + '-portal', 'AREA'); L.shape = 'RECTANGLE'; L.size = xb - xa; L.size_y = zb - za
        L.cycles.is_portal = True
        po = bpy.data.objects.new(name + '-portal', L); bpy.context.scene.collection.objects.link(po)
        po.location = P((xa + xb) / 2, (za + zb) / 2, T + 0.01)
        po.rotation_euler = n_in.to_track_quat('-Z', 'Y').to_euler()   # a portal faces into the room along its -Z
        objs.append(po)
    return objs


def _skirting(bpy, name, a, b, t, h, mat, gaps):
    along = (b - a); L = along.length; u = along.normalized(); n_in = Vector((u.y, -u.x, 0))
    segs = [(0.0, L)]
    for wi in gaps:
        ww = wi['size'][0]; c = L / 2 + wi.get('along', 0.0)
        new = []
        for s0, s1 in segs:
            if c - ww / 2 > s0: new.append((s0, min(s1, c - ww / 2)))
            if c + ww / 2 < s1: new.append((max(s0, c + ww / 2), s1))
        segs = new
    out = []
    for i, (s0, s1) in enumerate(segs):
        p0 = a + u * s0; p1 = a + u * s1 + n_in * t
        lo = Vector((min(p0.x, p1.x), min(p0.y, p1.y), 0)); hi = Vector((max(p0.x, p1.x), max(p0.y, p1.y), h))
        out.append(box(bpy, f'{name}{i}', lo.x, lo.y, lo.z, hi.x, hi.y, hi.z, mat, bevel=0.002))
    return out


# --- props ---------------------------------------------------------------------------------------------------------
def _mat_fabric(bpy, name, color, sheen=0.6, rough=0.95, bump=0.25, weave_mm=2.0, translucent=0.0):
    """Wool or linen: a matte base with sheen, a fine weave bump; `translucent` > 0 for sheers."""
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = M.hex_lin(color); b.inputs['Roughness'].default_value = rough
    b.inputs['Sheen Weight'].default_value = sheen; b.inputs['Sheen Roughness'].default_value = 0.5
    if 'Specular IOR Level' in b.inputs: b.inputs['Specular IOR Level'].default_value = 0.2
    tc = nt.nodes.new('ShaderNodeTexCoord')
    wv1 = nt.nodes.new('ShaderNodeTexWave'); wv1.wave_type = 'BANDS'; wv1.bands_direction = 'X'; wv1.inputs['Scale'].default_value = 1000.0 / weave_mm
    wv2 = nt.nodes.new('ShaderNodeTexWave'); wv2.wave_type = 'BANDS'; wv2.bands_direction = 'Y'; wv2.inputs['Scale'].default_value = 1000.0 / weave_mm
    for w in (wv1, wv2):
        w.inputs['Distortion'].default_value = 2.0; w.inputs['Detail'].default_value = 2.0
        nt.links.new(tc.outputs['Object'], w.inputs['Vector'])
    mx = nt.nodes.new('ShaderNodeMath'); mx.operation = 'MAXIMUM'
    nt.links.new(wv1.outputs['Fac'], mx.inputs[0]); nt.links.new(wv2.outputs['Fac'], mx.inputs[1])
    bn = nt.nodes.new('ShaderNodeBump'); bn.inputs['Strength'].default_value = bump; bn.inputs['Distance'].default_value = weave_mm / 4000
    nt.links.new(mx.outputs['Value'], bn.inputs['Height']); nt.links.new(bn.outputs['Normal'], b.inputs['Normal'])
    if translucent > 0:
        out = nt.nodes['Material Output']
        tr = nt.nodes.new('ShaderNodeBsdfTranslucent'); tr.inputs['Color'].default_value = M.hex_lin(color)
        mix = nt.nodes.new('ShaderNodeMixShader'); mix.inputs['Fac'].default_value = translucent
        tp = nt.nodes.new('ShaderNodeBsdfTransparent')
        mix2 = nt.nodes.new('ShaderNodeMixShader'); mix2.inputs['Fac'].default_value = 0.35
        nt.links.new(b.outputs['BSDF'], mix.inputs[1]); nt.links.new(tr.outputs['BSDF'], mix.inputs[2])
        nt.links.new(mix.outputs['Shader'], mix2.inputs[1]); nt.links.new(tp.outputs['BSDF'], mix2.inputs[2])
        nt.links.new(mix2.outputs['Shader'], out.inputs['Surface'])
    return m


def _mesh(bpy, name, verts, faces, mat, smooth=True):
    me = bpy.data.meshes.new(name); me.from_pydata(verts, [], faces); me.uv_layers.new()
    if smooth:
        for pg in me.polygons: pg.use_smooth = True
    return _obj(bpy, name, me, mat)


def _cyl(bpy, name, r, h, mat, n=48, z0=0.0, r_top=None, cap=True):
    rt = r if r_top is None else r_top
    verts = [(r * math.cos(2 * math.pi * i / n), r * math.sin(2 * math.pi * i / n), z0) for i in range(n)] + \
            [(rt * math.cos(2 * math.pi * i / n), rt * math.sin(2 * math.pi * i / n), z0 + h) for i in range(n)]
    faces = [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)]
    if cap:
        faces += [tuple(range(n))[::-1], tuple(range(n, 2 * n))]
    return _mesh(bpy, name, verts, faces, mat)


def _lathe(bpy, name, prof, mat, n=64):
    """A solid of revolution about z from (r, z) points."""
    verts, faces = [], []
    m = len(prof)
    for i in range(n):
        a = 2 * math.pi * i / n
        verts += [(r * math.cos(a), r * math.sin(a), z) for (r, z) in prof]
    for i in range(n):
        j = (i + 1) % n
        for k in range(m - 1):
            faces.append((i * m + k, j * m + k, j * m + k + 1, i * m + k + 1))
    return _mesh(bpy, name, verts, faces, mat)


def _tube(bpy, name, pts, r, mat, n=8):
    """A thin tube along 3D points (a branch, a cable)."""
    verts, faces = [], []
    P = [Vector(p) for p in pts]
    for i, p in enumerate(P):
        t = (P[min(i + 1, len(P) - 1)] - P[max(i - 1, 0)]).normalized()
        a = t.orthogonal().normalized(); b = t.cross(a)
        rr = r * (1 - 0.7 * i / (len(P) - 1))
        verts += [p + rr * (math.cos(2 * math.pi * k / n) * a + math.sin(2 * math.pi * k / n) * b) for k in range(n)]
    for i in range(len(P) - 1):
        for k in range(n):
            faces.append((i * n + k, i * n + (k + 1) % n, (i + 1) * n + (k + 1) % n, (i + 1) * n + k))
    return _mesh(bpy, name, verts, faces, mat)


def prop(bpy, name, p, mats):
    """Props, each at `position` [x, y] (its centre on the floor), turned `rotate_z` degrees: rug, table, books,
    sideboard (with a turntable), vase (with branches), lamp, sofa, curtain, frame."""
    import random
    kind = p['kind']; x, y = p['position']; rot = math.radians(p.get('rotate_z', 0))
    rnd = random.Random(p.get('seed', 7))
    made = []
    if kind == 'rug':
        w, d = p.get('size', [2.0, 1.4])
        m = _mat_fabric(bpy, name, p.get('color', '#C9C1B4'), sheen=0.7, bump=0.35, weave_mm=3.5)
        made.append(box(bpy, name, -w / 2, -d / 2, 0.0, w / 2, d / 2, 0.009, m, bevel=0.004))
    elif kind == 'table':
        w, d, hh = p.get('size', [1.0, 0.5, 0.42])
        wood = M.make(bpy, name + '-wood', 'birch', {'color': p.get('color', '#9B7653'), 'roughness': 0.45})
        made.append(box(bpy, name + '-top', -w / 2, -d / 2, hh - 0.03, w / 2, d / 2, hh, wood, bevel=0.004))
        for sx in (-1, 1):
            for sy in (-1, 1):
                made.append(box(bpy, f'{name}-leg{sx}{sy}', sx * (w / 2 - 0.06) - 0.02, sy * (d / 2 - 0.06) - 0.02, 0,
                                sx * (w / 2 - 0.06) + 0.02, sy * (d / 2 - 0.06) + 0.02, hh - 0.03, wood, bevel=0.003))
    elif kind == 'books':
        cols = p.get('colors', ['#3C4A5A', '#B9A27A', '#7A2E2A'])
        z = p.get('z', 0.0)
        for i, c in enumerate(cols):
            m = M.make(bpy, f'{name}-{i}', 'satin_paint', {'color': c, 'roughness': 0.6, 'specular': 0.3})
            bw, bd, bh = 0.24 - 0.02 * i, 0.17 - 0.01 * i, 0.025 + 0.006 * (i % 2)
            b = box(bpy, f'{name}-{i}', -bw / 2, -bd / 2, z, bw / 2, bd / 2, z + bh, m, bevel=0.002)
            b.rotation_euler = (0, 0, math.radians(rnd.uniform(-6, 6))); made.append(b); z += bh
    elif kind == 'sideboard':
        w, d, hh = p.get('size', [1.6, 0.42, 0.56])
        leg = 0.14
        wood = M.make(bpy, name + '-oak', 'birch', {'color': p.get('color', '#A27B52'), 'roughness': 0.4})
        dark = M.make(bpy, name + '-dark', 'satin_paint', {'color': '#151413', 'roughness': 0.5, 'specular': 0.3})
        made.append(box(bpy, name + '-body', -w / 2, -d / 2, leg, w / 2, d / 2, hh, wood, bevel=0.005))
        for k in range(1, 3):   # door seams
            sx = -w / 2 + k * w / 3
            made.append(box(bpy, f'{name}-seam{k}', sx - 0.0015, -d / 2 - 0.0005, leg + 0.02, sx + 0.0015, -d / 2 + 0.002, hh - 0.02, dark))
        for sx in (-1, 1):
            for sy in (-1, 1):
                made.append(_cyl(bpy, f'{name}-leg{sx}{sy}', 0.016, leg, wood, n=16, r_top=0.02))
                made[-1].location = Vector((sx * (w / 2 - 0.08), sy * (d / 2 - 0.06), 0))
        if p.get('turntable', True):
            tz = hh
            ox = p.get('tt_x', -0.355) + 0.355          # the turntable's centre along the top (default left of centre)
            plinth = M.make(bpy, name + '-tt', 'satin_paint', {'color': p.get('tt_color', '#E9E6DF'), 'roughness': 0.35, 'specular': 0.5})
            made.append(box(bpy, name + '-tt', -0.58 + ox, -0.17, tz, -0.13 + ox, 0.17, tz + 0.09, plinth, bevel=0.006))
            rec = M.make(bpy, name + '-record', 'gloss_plastic', {'color': '#0B0B0B', 'roughness': 0.25})
            pl = _cyl(bpy, name + '-platter', 0.152, 0.012, dark, n=96); pl.location = Vector((-0.38 + ox, 0.0, tz + 0.09)); made.append(pl)
            rc = _cyl(bpy, name + '-record', 0.150, 0.002, rec, n=96); rc.location = Vector((-0.38 + ox, 0.0, tz + 0.102)); made.append(rc)
            lab = M.make(bpy, name + '-label', 'satin_paint', {'color': p.get('label', '#C62828'), 'roughness': 0.6})
            lb = _cyl(bpy, name + '-label', 0.045, 0.0006, lab, n=48); lb.location = Vector((-0.38 + ox, 0.0, tz + 0.104)); made.append(lb)
            metal = M.make(bpy, name + '-arm', 'metal', {'color': '#C9C9C6', 'roughness': 0.2})
            made.append(_tube(bpy, name + '-arm', [(-0.17 + ox, 0.12, tz + 0.12), (-0.24 + ox, 0.05, tz + 0.115), (-0.30 + ox, -0.06, tz + 0.11)], 0.004, metal))
    elif kind == 'vase':
        h = p.get('height', 0.32); z0 = p.get('z', 0.0)
        cer = M.make(bpy, name + '-ceramic', 'satin_paint', {'color': p.get('color', '#E8E2D6'), 'roughness': 0.55, 'specular': 0.5})
        prof = [(0.0, 0.0), (0.055, 0.0), (0.075, 0.08 * h / 0.32), (0.07, 0.2 * h / 0.32), (0.035, 0.29 * h / 0.32), (0.03, h), (0.026, h), (0.026, h - 0.01)]
        v = _lathe(bpy, name, prof, cer); v.location = Vector((0, 0, z0)); made.append(v)
        bark = M.make(bpy, name + '-branch', 'satin_paint', {'color': '#4B3A2B', 'roughness': 0.8, 'specular': 0.2})
        for i in range(p.get('branches', 5)):
            a = rnd.uniform(0, 2 * math.pi); lean = rnd.uniform(0.15, 0.45); L = rnd.uniform(0.5, 0.8)
            pts = []
            for k in range(9):
                t = k / 8
                pts.append((math.cos(a) * lean * L * t ** 1.4 + 0.01 * math.sin(7 * t + i), math.sin(a) * lean * L * t ** 1.4, z0 + h - 0.05 + L * t))
            made.append(_tube(bpy, f'{name}-b{i}', pts, 0.004, bark, n=6))
    elif kind == 'lamp':
        hh = p.get('height', 1.55)
        brass = M.make(bpy, name + '-brass', 'metal', {'color': '#B79A62', 'roughness': 0.28})
        made.append(_cyl(bpy, name + '-base', 0.13, 0.02, brass, n=64))
        made.append(_cyl(bpy, name + '-pole', 0.009, hh - 0.25, brass, n=16, z0=0.02))
        shade = _mat_fabric(bpy, name + '-shade', p.get('shade', '#EFE9DD'), sheen=0.3, bump=0.1, weave_mm=1.2, translucent=0.6)
        made.append(_cyl(bpy, name + '-shade', 0.2, 0.26, shade, n=64, z0=hh - 0.3, r_top=0.17, cap=False))
    elif kind == 'sofa':
        w, d, hh = p.get('size', [2.1, 0.92, 0.78])
        fab = _mat_fabric(bpy, name + '-fabric', p.get('color', '#9C9A92'), sheen=0.5, bump=0.3, weave_mm=2.5)
        legm = M.make(bpy, name + '-legs', 'birch', {'color': '#6B4A30', 'roughness': 0.45})
        made.append(box(bpy, name + '-base', -w / 2, -d / 2, 0.12, w / 2, d / 2, 0.4, fab, bevel=0.03))
        made.append(box(bpy, name + '-back', -w / 2, d / 2 - 0.2, 0.4, w / 2, d / 2, hh, fab, bevel=0.05))
        for sx in (-1, 1):
            made.append(box(bpy, f'{name}-arm{sx}', sx * w / 2 - (0.18 if sx > 0 else 0), -d / 2, 0.4, sx * w / 2 + (0.18 if sx < 0 else 0), d / 2, 0.62, fab, bevel=0.05))
        nseat = 2
        for k in range(nseat):
            x0_ = -w / 2 + 0.18 + k * (w - 0.36) / nseat; x1_ = x0_ + (w - 0.36) / nseat
            made.append(box(bpy, f'{name}-seat{k}', x0_ + 0.005, -d / 2 + 0.02, 0.4, x1_ - 0.005, d / 2 - 0.2, 0.52, fab, bevel=0.04))
        for sx in (-1, 1):
            for sy in (-1, 1):
                lg = _cyl(bpy, f'{name}-leg{sx}{sy}', 0.018, 0.12, legm, n=16, r_top=0.024)
                lg.location = Vector((sx * (w / 2 - 0.08), sy * (d / 2 - 0.08), 0)); made.append(lg)
    elif kind == 'curtain':
        # a sheer panel hanging in folds; position is its centre on the floor, it faces -y before rotate_z
        w, hh = p.get('size', [1.0, 2.6]); folds = p.get('folds', 9); amp = p.get('depth', 0.035)
        m = _mat_fabric(bpy, name, p.get('color', '#F4F1EA'), sheen=0.4, bump=0.08, weave_mm=0.8, translucent=p.get('translucent', 0.75))
        nx = folds * 8; verts, faces = [], []
        for j, z in enumerate((0.01, hh * 0.5, hh)):
            for i in range(nx + 1):
                t = i / nx; xx = -w / 2 + w * t
                verts.append((xx, amp * math.sin(2 * math.pi * folds * t) * (1.0 + 0.15 * j), z))
        for j in range(2):
            for i in range(nx):
                a0 = j * (nx + 1) + i
                faces.append((a0, a0 + 1, a0 + nx + 2, a0 + nx + 1))
        made.append(_mesh(bpy, name, verts, faces, m))
    elif kind == 'frame':
        # a framed print on a wall: position [x, y] is its centre, z its centre height, it faces -y before rotate_z
        w, hh = p.get('size', [0.6, 0.8]); z = p.get('z', 1.5)
        oak = M.make(bpy, name + '-oak', 'birch', {'color': p.get('frame', '#8C6A48'), 'roughness': 0.4})
        made.append(box(bpy, name + '-frame', -w / 2, -0.03, z - hh / 2, w / 2, 0.0, z + hh / 2, oak, bevel=0.003))
        pm = M.make(bpy, name + '-print', 'satin_paint', {'color': p.get('print', '#D8CFC0'), 'roughness': 0.85, 'specular': 0.2})
        made.append(box(bpy, name + '-print', -w / 2 + 0.05, -0.032, z - hh / 2 + 0.05, w / 2 - 0.05, -0.029, z + hh / 2 - 0.05, pm))
        art = M.make(bpy, name + '-art', 'satin_paint', {'color': p.get('art', '#3F5B6E'), 'roughness': 0.85, 'specular': 0.2})
        made.append(box(bpy, name + '-art', -w / 2 + 0.11, -0.0335, z - hh / 2 + 0.2, w / 2 - 0.11, -0.0325, z + hh / 2 - 0.12, art))
    for o in made:
        o.rotation_euler.z += rot
        o.location = Matrix_rot(rot) @ o.location + Vector((x, y, 0))
    return made


def Matrix_rot(a):
    from mathutils import Matrix
    return Matrix.Rotation(a, 3, 'Z')
