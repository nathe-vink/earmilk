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
    for i, p in enumerate(spec.get('props', [])):
        objs += prop(bpy, f'prop{i}-{p["kind"]}', p, mats)
    return objs


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
def prop(bpy, name, p, mats):
    """Simple, honest props: a rug, a low table, a chair, a book stack. Each at `position` [x, y] (its centre on the
    floor), turned `rotate_z` degrees."""
    kind = p['kind']; x, y = p['position']; rot = math.radians(p.get('rotate_z', 0))
    made = []
    if kind == 'rug':
        w, d = p.get('size', [2.0, 1.4])
        m = M.make(bpy, name, 'satin_paint', {'color': p.get('color', '#C9C1B4'), 'roughness': 0.95, 'specular': 0.05})
        made.append(box(bpy, name, -w / 2, -d / 2, 0.0, w / 2, d / 2, 0.008, m, bevel=0.003))
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
            made.append(box(bpy, f'{name}-{i}', -bw / 2, -bd / 2, z, bw / 2, bd / 2, z + bh, m, bevel=0.002)); z += bh
    for o in made:
        o.rotation_euler = (0, 0, rot); o.location = Vector((x, y, 0)) + o.location
    return made
