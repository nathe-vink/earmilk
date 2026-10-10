"""What a part mirrors into the camera: the reflection probe.

    python3 studio/engine/render.py SHOT --out IMG --probe 'woofer-cone' [--probe 'roof-*'] --scale 0.75

A glossy part shows whatever lies along its mirror direction, and a critic who wants a highlight, a sheen or a dark
edge on it is guessing where to put a lamp until that is known. This casts the camera's rays through the frame, keeps
the hits on the part, reflects each about the surface's own normal, and follows the reflected ray to the first thing
it meets: a surface of the set or the product, the face of an area lamp (or a panel), or the world (the sky). It
reports, for each thing seen, its share of the part's pixels, where those pixels are in the frame (in the image's own
pixels at the scale rendered, 0.75 for a critic), and the band of directions they look along (azimuth and elevation
in the engine's convention, from the part outward), so a card or a lamp can be sized and placed to cover exactly the
pixels that should light up. Nothing is rendered.
"""
import math, re

from mathutils import Vector


def _clean(name):
    return re.sub(r'(#\d+)?(\.\d+)?$', '', name)


def _az_el(d):
    return math.degrees(math.atan2(d.x, -d.y)), math.degrees(math.asin(max(-1.0, min(1.0, d.z))))


def _lamp_hit(lob, o, d):
    """Distance along the ray (o, d) to an area lamp's emitting face, or None."""
    L = lob.data
    Mi = lob.matrix_world.inverted()
    ol, dl = Mi @ o, (Mi.to_3x3() @ d)
    if abs(dl.z) < 1e-9:
        return None
    t = -ol.z / dl.z
    if t <= 1e-6 or ol.z >= 0:            # an area lamp emits along its -Z: the ray must come from that side
        return None
    p = ol + dl * t
    sx = L.size / 2; sy = (L.size_y if L.shape in ('RECTANGLE', 'ELLIPSE') else L.size) / 2
    if L.shape in ('DISK', 'ELLIPSE'):
        inside = (p.x / sx) ** 2 + (p.y / sy) ** 2 <= 1
    else:
        inside = abs(p.x) <= sx and abs(p.y) <= sy
    return t * (lob.matrix_world.to_3x3() @ dl).length if inside else None


def _cast(scene, dg, o, d, through_panels, receiver=None):
    """The first surface along a ray, by the render's ray visibility. A camera ray (through_panels) passes what the
    camera does not see (panels, flags, hidden helpers); a reflected ray passes what gloss does not see (flags by
    default), a panel's or a one-sided card's back, and a panel linked to other parts than `receiver`."""
    dist = 1e4
    while True:
        hit, loc, nrm, _, hob, _ = scene.ray_cast(dg, o, d, distance=dist)
        if not hit:
            return hit, loc, nrm, hob
        if through_panels:
            skip = hob.hide_render or not hob.visible_camera or bool(hob.get('engine_light'))
        else:
            skip = hob.hide_render or not hob.visible_glossy or \
                   bool((hob.get('engine_light') or hob.get('one_sided')) and nrm.dot(d) > 0)
            if not skip and hob.get('engine_light'):
                col = hob.light_linking.receiver_collection
                skip = col is not None and receiver not in col.objects
        if not skip:
            return hit, loc, nrm, hob
        dist -= (loc - o).length + 1e-4; o = loc + d * 1e-4
        if dist <= 0:
            return False, loc, nrm, None


def reflections(bpy, scene, cam, objs, part_of, pattern, match, step=2):
    """The probe for parts matching `pattern`: {seen: {share, box_px, az, el, pixels}}, over pixels every `step`."""
    dg = bpy.context.evaluated_depsgraph_get()
    W, H = scene.render.resolution_x, scene.render.resolution_y
    M = cam.matrix_world; origin = M.translation
    tr, br, bl, tl = [M @ v for v in cam.data.view_frame(scene=scene)]
    targets = {o.name for o in objs if match(part_of[o.name], pattern)}
    if not targets:
        return {'error': f'no part matches {pattern!r}'}
    # Cycles ignores a lamp's specular factor; what a reflection sees is set by its glossy ray visibility
    lamps = [o for o in scene.objects if o.type == 'LIGHT' and o.data.type == 'AREA' and o.visible_glossy and not o.hide_render]
    def lit_by(lob, ob_name):
        col = lob.light_linking.receiver_collection
        return col is None or ob_name in col.objects
    seen, total = {}, 0
    for py in range(0, H, step):
        for px in range(0, W, step):
            u, v = (px + 0.5) / W, (py + 0.5) / H
            p = tl + (tr - tl) * u + (bl - tl) * v
            d = (p - origin).normalized()
            hit, loc, nrm, hob = _cast(scene, dg, origin, d, through_panels=True)
            if not hit or hob.name not in targets:
                continue
            n = nrm if nrm.dot(d) < 0 else -nrm
            r = (d - 2 * d.dot(n) * n).normalized()
            o2 = loc + n * 1e-4
            hit2, loc2, _, hob2 = _cast(scene, dg, o2, r, through_panels=False, receiver=hob.name)
            best, what = ((loc2 - o2).length, ('panel ' if hob2.get('engine_light') else '') + _clean(hob2.name)) if hit2 \
                else (math.inf, 'world (sky)')
            for lob in lamps:
                if not lit_by(lob, hob.name):
                    continue
                t = _lamp_hit(lob, o2, r)
                if t is not None and t < best:
                    best, what = t, f'lamp {lob.name}'
            total += 1
            s = seen.setdefault(what, {'n': 0, 'x0': W, 'y0': H, 'x1': 0, 'y1': 0, 'az': [], 'el': []})
            s['n'] += 1
            s['x0'], s['y0'] = min(s['x0'], px), min(s['y0'], py); s['x1'], s['y1'] = max(s['x1'], px + step), max(s['y1'], py + step)
            az, el = _az_el(r); s['az'].append(az); s['el'].append(el)
    out = {}
    for what, s in sorted(seen.items(), key=lambda kv: -kv[1]['n']):
        az, el = sorted(s['az']), sorted(s['el'])
        q = lambda a, f: round(a[min(len(a) - 1, int(f * len(a)))], 1)
        out[what] = {'share': round(s['n'] / total, 3), 'box_px': [s['x0'], s['y0'], s['x1'], s['y1']],
                     'az_deg': [q(az, 0.05), q(az, 0.5), q(az, 0.95)], 'el_deg': [q(el, 0.05), q(el, 0.5), q(el, 0.95)]}
    return {'part': pattern, 'pixels_sampled': total, 'step': step, 'seen': out}


def reflection_map(bpy, scene, cam, objs, part_of, pattern, match, box, out_png):
    """Every pixel of `box` [x0, y0, x1, y1] (the frame's pixels) on parts matching `pattern`, coloured by what its
    reflected ray meets first (the shading normal's mirror, as the render's): a map of which object draws which part
    of a reflection, to find the one behind an artefact. Writes out_png and returns {label: [pixels, colour]}."""
    import numpy as np
    from PIL import Image
    dg = bpy.context.evaluated_depsgraph_get()
    W, H = scene.render.resolution_x, scene.render.resolution_y
    M = cam.matrix_world; origin = M.translation
    tr, br, bl, tl = [M @ v for v in cam.data.view_frame(scene=scene)]
    targets = {o.name for o in objs if match(part_of[o.name], pattern)}
    x0, y0, x1, y1 = box
    img = np.zeros((y1 - y0, x1 - x0, 3), np.uint8)
    pal, counts = {}, {}
    colours = [(230, 60, 60), (60, 160, 230), (250, 200, 40), (90, 200, 90), (200, 90, 220), (240, 140, 40), (40, 40, 40), (255, 255, 255), (120, 120, 120)]
    for py in range(y0, y1):
        for px in range(x0, x1):
            u, v = (px + 0.5) / W, (py + 0.5) / H
            d = ((tl + (tr - tl) * u + (bl - tl) * v) - origin).normalized()
            hit, loc, nrm, hob = _cast(scene, dg, origin, d, through_panels=True)
            if not hit or hob.name not in targets:
                continue
            n = nrm if nrm.dot(d) < 0 else -nrm
            r = (d - 2 * d.dot(n) * n).normalized()
            o2 = loc + n * 1e-4
            hit2, loc2, _, hob2 = _cast(scene, dg, o2, r, through_panels=False, receiver=hob.name)
            what = (('panel ' if hob2.get('engine_light') else '') + _clean(hob2.name)) if hit2 else 'world (sky)'
            if what not in pal:
                pal[what] = colours[len(pal) % len(colours)]
            img[py - y0, px - x0] = pal[what]; counts[what] = counts.get(what, 0) + 1
    Image.fromarray(img).save(out_png)
    return {k: [counts[k], pal[k]] for k in counts}


def shadow_map(bpy, scene, cam, objs, part_of, pattern, match, box, out_png):
    """Every pixel of `box` on parts matching `pattern`, coloured by what blocks the ray from its surface to each area
    lamp's centre (one band of the map per lamp, left to right): which object casts which shadow edge."""
    import numpy as np
    from PIL import Image
    dg = bpy.context.evaluated_depsgraph_get()
    W, H = scene.render.resolution_x, scene.render.resolution_y
    M = cam.matrix_world; origin = M.translation
    tr, br, bl, tl = [M @ v for v in cam.data.view_frame(scene=scene)]
    targets = {o.name for o in objs if match(part_of[o.name], pattern)}
    lamps = [o for o in scene.objects if o.type == 'LIGHT' and o.data.type == 'AREA' and o.data.energy > 0]
    x0, y0, x1, y1 = box
    bw = x1 - x0
    img = np.zeros((y1 - y0, bw * max(1, len(lamps)), 3), np.uint8)
    pal, counts = {'lit': (255, 255, 255)}, {}
    colours = [(230, 60, 60), (60, 160, 230), (250, 200, 40), (90, 200, 90), (200, 90, 220), (240, 140, 40), (40, 40, 40)]
    for py in range(y0, y1):
        for px in range(x0, x1):
            u, v = (px + 0.5) / W, (py + 0.5) / H
            d = ((tl + (tr - tl) * u + (bl - tl) * v) - origin).normalized()
            hit, loc, nrm, hob = _cast(scene, dg, origin, d, through_panels=True)
            if not hit or hob.name not in targets:
                continue
            n = nrm if nrm.dot(d) < 0 else -nrm
            for li, lob in enumerate(lamps):
                to = lob.matrix_world.translation - loc
                dist = to.length; dl = to / dist
                if dl.dot(n) <= 0:
                    what = 'facing away'
                else:
                    h2, l2, _, o2 = _cast(scene, dg, loc + n * 1e-4, dl, through_panels=True)
                    what = 'lit' if not h2 or (l2 - loc).length >= dist else 'shadow of ' + _clean(o2.name)
                key = f'{lob.name}: {what}'
                if what not in pal:
                    pal[what] = colours[(len(pal) - 1) % len(colours)]
                img[py - y0, li * bw + px - x0] = pal[what]; counts[key] = counts.get(key, 0) + 1
    Image.fromarray(img).save(out_png)
    return {'lamps': [l.name for l in lamps], 'counts': counts, 'colours': {k: list(v) for k, v in pal.items()}}


class _Normals:
    """The render's shading normal at a ray's hit: the corner normals of the hit face's triangle, interpolated at the
    hit (smooth parts mirror as the render shades them, not facet by facet). Per object, cached."""
    def __init__(self, dg):
        self.dg, self.cache = dg, {}

    def _mesh(self, ob):
        import numpy as np
        c = self.cache.get(ob.name)
        if c is None:
            me = ob.evaluated_get(self.dg).data
            nt = len(me.loop_triangles)
            poly = np.empty(nt, np.int64); me.loop_triangles.foreach_get('polygon_index', poly)
            loops = np.empty(nt * 3, np.int64); me.loop_triangles.foreach_get('loops', loops)
            verts = np.empty(nt * 3, np.int64); me.loop_triangles.foreach_get('vertices', verts)
            co = np.empty(len(me.vertices) * 3); me.vertices.foreach_get('co', co)
            cn = np.empty(len(me.corner_normals) * 3); me.corner_normals.foreach_get('vector', cn)
            order = np.argsort(poly, kind='stable')
            c = self.cache[ob.name] = {'poly': poly[order], 'tri': order, 'loops': loops.reshape(-1, 3),
                                       'verts': verts.reshape(-1, 3), 'co': co.reshape(-1, 3), 'cn': cn.reshape(-1, 3)}
        return c

    def at(self, ob, index, loc, geo):
        """The world-space shading normal of `ob` at `loc` on face `index`; `geo` (the face's normal) where the face
        cannot be read or the two disagree by more than 40 degrees (a stale index)."""
        import numpy as np
        try:
            c = self._mesh(ob)
        except Exception:
            return geo
        lo, hi = np.searchsorted(c['poly'], [index, index + 1])
        if hi <= lo:
            return geo
        Mi = ob.matrix_world.inverted(); p = Mi @ loc
        best = None
        for t in c['tri'][lo:hi]:
            a, b, d = (Vector(c['co'][v]) for v in c['verts'][t])
            v0, v1, v2 = b - a, d - a, p - a
            d00, d01, d11, d20, d21 = v0.dot(v0), v0.dot(v1), v1.dot(v1), v2.dot(v0), v2.dot(v1)
            den = d00 * d11 - d01 * d01
            if abs(den) < 1e-18:
                continue
            w1 = (d11 * d20 - d01 * d21) / den; w2 = (d00 * d21 - d01 * d20) / den; w0 = 1 - w1 - w2
            score = min(w0, w1, w2)
            if best is None or score > best[0]:
                best = (score, t, (w0, w1, w2))
        if best is None:
            return geo
        _, t, w = best
        n = sum((Vector(c['cn'][l]) * wi for l, wi in zip(c['loops'][t], w)), Vector())
        n = (Mi.transposed().to_3x3() @ n)
        if n.length < 1e-9:
            return geo
        n.normalize()
        return n if math.degrees(n.angle(geo if n.dot(geo) >= 0 else -geo)) <= 40 else geo


def _panel_radiance(ob, loc):
    """A panel's radiance where a ray meets it (its strength times its ramp there), from what lights.panel recorded."""
    import json as _j
    e = ob.get('emit')
    if not e:
        return None
    e = _j.loads(e)
    if not e.get('axis'):
        return round(e['peak'], 4)
    c = Vector(loc).dot(Vector(e['axis']))
    st = sorted(zip(e['at'], e['values']))
    if c <= st[0][0]:
        f = st[0][1]
    elif c >= st[-1][0]:
        f = st[-1][1]
    else:
        f = next(v0 + (v1 - v0) * (c - a0) / (a1 - a0) for (a0, v0), (a1, v1) in zip(st, st[1:]) if a0 <= c <= a1)
    return round(e['peak'] * f, 4)


def _follow(scene, dg, o, d, receiver, lamps):
    """A reflected ray from `receiver`, as the render follows it: past what gloss does not see (`visible_glossy` off:
    flags, hidden helpers), past a panel's or a one-sided card's back, and through a panel linked to its receivers
    (see-through: they see its light added to what lies behind it); stopped by the first surface or unlinked panel
    face. Area lamps are crossed, not stopped at, as the render's are. Returns (layers, terminal): layers [(t, label,
    radiance, world point)] of every emitter met that lights `receiver`, terminal (t, label, radiance or None, point)."""
    layers = []; o0 = o; dist = 1e4
    while True:
        hit, loc, nrm, _, hob, _ = scene.ray_cast(dg, o, d, distance=dist)
        if not hit:
            terminal = (math.inf, 'world (sky)', None, None); break
        t = (loc - o0).length
        through = hob.hide_render or not hob.visible_glossy
        if not through and (hob.get('engine_light') or hob.get('one_sided')) and nrm.dot(d) > 0:
            through = True                                   # a one-sided face seen from behind
        if not through and hob.get('engine_light'):
            col = hob.light_linking.receiver_collection
            if col is not None:
                if receiver in col.objects:
                    layers.append((t, 'panel ' + _clean(hob.name), _panel_radiance(hob, loc), tuple(loc)))
                through = True
        if through:
            dist -= (loc - o).length + 1e-4; o = loc + d * 1e-4
            if dist <= 0:
                terminal = (math.inf, 'world (sky)', None, None); break
            continue
        terminal = (t, ('panel ' if hob.get('engine_light') else '') + _clean(hob.name),
                    _panel_radiance(hob, loc) if hob.get('engine_light') else None, tuple(loc))
        break
    for name, Mi, M3, round_, sx, sy, recv, rad in lamps:
        if recv is not None and receiver not in recv:
            continue
        ol, dl = Mi @ o0, Mi.to_3x3() @ d
        if abs(dl.z) < 1e-9 or ol.z >= 0:
            continue
        tl = -ol.z / dl.z
        if tl <= 1e-6:
            continue
        q = ol + dl * tl
        if (round_ and (q.x / sx) ** 2 + (q.y / sy) ** 2 <= 1) or (not round_ and abs(q.x) <= sx and abs(q.y) <= sy):
            tw = tl * (M3 @ dl).length
            if tw < terminal[0]:
                layers.append((tw, 'lamp ' + name, rad, tuple(o0 + d * tw)))
    layers.sort(key=lambda x: -(x[2] or 0))
    return layers, terminal


def mirror_map(bpy, scene, cam, objs, part_of, out_png, step=2):
    """What every product pixel mirrors, for the critic: the camera's ray through each pixel (every `step`), past what
    the camera does not see, to its part; reflected about the render's shading normal there; followed as the render
    follows it (_follow). Each pixel's label is what it mirrors: the emitters met, brightest first, over the surface
    behind them ("panel glint5 + lamp fill over sweep"), or that surface alone. Writes `out_png` (red = the label's id,
    0 off the product, the frame's full size), beside it a .json (legend, per part shares) and a .npz (per sampled
    pixel: the label, the radiance of up to three emitters in the label's order, and where the nearest layer was met,
    world x, y, z: where on a panel a ramp has to change for a region). Returns the .json's content."""
    import numpy as np
    from PIL import Image
    dg = bpy.context.evaluated_depsgraph_get()
    W, H = scene.render.resolution_x, scene.render.resolution_y
    M = cam.matrix_world; origin = M.translation
    tr, br, bl, tl = [M @ v for v in cam.data.view_frame(scene=scene)]
    parts = {o.name: part_of[o.name] for o in objs if not o.hide_render}
    lamps = []
    for o in scene.objects:
        if o.type == 'LIGHT' and o.data.type == 'AREA' and not o.hide_render and o.visible_glossy:
            L = o.data
            col = o.light_linking.receiver_collection
            sy_ = (L.size_y if L.shape in ('RECTANGLE', 'ELLIPSE') else L.size)
            area = L.size * sy_ * (math.pi / 4 if L.shape in ('DISK', 'ELLIPSE') else 1.0)
            rad = round(L.energy / (math.pi * max(area, 1e-9)), 4)     # Cycles ignores specular_factor (lamp_shares)
            lamps.append((o.name, o.matrix_world.inverted(), o.matrix_world.to_3x3(), L.shape in ('DISK', 'ELLIPSE'), L.size / 2,
                          sy_ / 2, None if col is None else {x.name for x in col.objects}, rad))
    normals = _Normals(dg)
    h2, w2 = (H + step - 1) // step, (W + step - 1) // step
    ids = np.zeros((H, W), np.uint8)
    lab_s = np.zeros((h2, w2), np.uint8); rad_s = np.full((h2, w2, 3), np.nan, np.float32); xyz_s = np.full((h2, w2, 3), np.nan, np.float32)
    labels, counts = {}, {}
    for py in range(0, H, step):
        for px in range(0, W, step):
            u, v = (px + 0.5) / W, (py + 0.5) / H
            d = ((tl + (tr - tl) * u + (bl - tl) * v) - origin).normalized()
            dist = 1e4; o = origin
            while True:     # the camera's ray, past what the camera does not see
                hit, loc, nrm, idx, hob, _ = scene.ray_cast(dg, o, d, distance=dist)
                if hit and (hob.hide_render or not hob.visible_camera or
                            ((hob.get('engine_light') or hob.get('one_sided')) and nrm.dot(d) > 0)):
                    dist -= (loc - o).length + 1e-4; o = loc + d * 1e-4
                    continue
                break
            if not hit or hob.name not in parts:
                continue
            geo = nrm if nrm.dot(d) < 0 else -nrm
            n = normals.at(hob, idx, loc, geo)
            if n.dot(d) > 0:
                n = -n
            r = (d - 2 * d.dot(n) * n).normalized()
            layers, term = _follow(scene, dg, loc + geo * 1e-4, r, hob.name, lamps)
            what = (' + '.join(x[1] for x in layers) + ' over ' + term[1]) if layers else term[1]
            if what not in labels:
                if len(labels) >= 254:
                    what = 'other'
                labels.setdefault(what, len(labels) + 1)
            ids[py:py + step, px:px + step] = labels[what]
            j, i = py // step, px // step
            lab_s[j, i] = labels[what]
            comps = layers + ([term] if term[2] is not None else [])     # a panel behind the layers has a radiance too
            for k, x in enumerate(comps[:3]):
                rad_s[j, i, k] = np.nan if x[2] is None else x[2]
            near = min(layers + [term], key=lambda x: x[0])
            if near[3] is not None:
                xyz_s[j, i] = near[3]
            pc = counts.setdefault(parts[hob.name], {})
            pc[what] = pc.get(what, 0) + 1
    Image.fromarray(np.stack([ids, ids, ids], -1)).save(out_png)
    summary = {}
    for p, c in sorted(counts.items(), key=lambda kv: -sum(kv[1].values())):
        n = sum(c.values())
        summary[p] = {'pixels': n * step * step,
                      'seen': [[w, round(k / n, 3)] for w, k in sorted(c.items(), key=lambda kv: -kv[1])[:6]]}
    from pathlib import Path
    import json
    res = {'legend': {str(i): w for w, i in labels.items()}, 'step': step, 'parts': summary,
           'lamps': {l[0]: l[7] for l in lamps}}
    Path(out_png).with_suffix('.json').write_text(json.dumps(res, indent=1) + '\n')
    np.savez_compressed(Path(out_png).with_suffix('.npz'), label=lab_s, radiance=rad_s, xyz=xyz_s, step=step)
    return res
