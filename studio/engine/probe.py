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
    """The first surface along a ray. A panel (an engine light) is passed through by camera rays, which do not see
    it; a reflected ray sees it only where its light linking lets it light the part reflecting it."""
    dist = 1e4
    while True:
        hit, loc, nrm, _, hob, _ = scene.ray_cast(dg, o, d, distance=dist)
        if hit and hob.hide_render:
            dist -= (loc - o).length; o = loc + d * 1e-4      # a hidden helper (a cutaway's cutter)
            continue
        if not hit or not hob.get('engine_light'):
            return hit, loc, nrm, hob
        col = hob.light_linking.receiver_collection
        if not through_panels and (col is None or receiver in col.objects):
            return hit, loc, nrm, hob
        dist -= (loc - o).length; o = loc + d * 1e-4


def reflections(bpy, scene, cam, objs, part_of, pattern, match, step=2):
    """The probe for parts matching `pattern`: {seen: {share, box_px, az, el, pixels}}, over pixels every `step`."""
    dg = bpy.context.evaluated_depsgraph_get()
    W, H = scene.render.resolution_x, scene.render.resolution_y
    M = cam.matrix_world; origin = M.translation
    tr, br, bl, tl = [M @ v for v in cam.data.view_frame(scene=scene)]
    targets = {o.name for o in objs if match(part_of[o.name], pattern)}
    if not targets:
        return {'error': f'no part matches {pattern!r}'}
    lamps = [o for o in scene.objects if o.type == 'LIGHT' and o.data.type == 'AREA' and o.data.specular_factor > 0]
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
