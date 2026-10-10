"""The render model: every part the product shows, one named mesh each, from the same solids the cut files and
drawings come from, and the engine's product file that paints them (studio/engine reads both).

    render.write(product, parts, out)  ->  render/<name>.glb, render/<name>.json (part boxes), and the engine product
                                           file studio/products/<name>.json (materials by finish, assignments, origin)

A part's `finish` names its material: the product's `materials` maps finish names to the engine's presets
(paint, satin_paint, metal, rubber, birch, veneer, ... see studio/engine/materials.py). A product with colourways
lists them as `variants`, each a set of overrides the engine applies as a flavour.
"""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def write(product, parts, out):
    from build123d import Compound, Unit, export_gltf
    rd = os.path.join(out, 'render'); os.makedirs(rd, exist_ok=True)
    kids, boxes, finish = [], {}, {}
    for p in parts:
        if not p.render:
            continue
        for nm, (s, f) in ({f'{p.name}-{k}': v for k, v in p.pieces.items()} or {p.name: (p.solid, p.finish)}).items():
            s.label = nm
            kids.append(s)
            b = s.bounding_box()
            boxes[nm] = [round(v, 1) for v in (b.min.X, b.min.Y, b.min.Z, b.max.X, b.max.Y, b.max.Z)]
            finish[nm] = f
    asm = Compound(children=kids); asm.label = product.name
    glb = os.path.join(rd, f'{product.name}.glb')
    export_gltf(asm, glb + '.part.glb', unit=Unit.MM, binary=True, linear_deflection=0.0005, angular_deflection=0.08)
    os.replace(glb + '.part.glb', glb)
    json.dump({'parts': boxes, 'finishes': finish}, open(os.path.join(rd, f'{product.name}.json'), 'w'), indent=1)
    # the engine's product file: where the model is, where its origin sits, and how its finishes paint
    xs = [v for b in boxes.values() for v in (b[0], b[3])]; ys = [v for b in boxes.values() for v in (b[1], b[4])]
    zs = [b[2] for b in boxes.values()]
    origin = list(product.origin) if any(product.origin) else [round((min(xs) + max(xs)) / 2, 1), round((min(ys) + max(ys)) / 2, 1), round(min(zs), 1)]
    finishes = sorted({f for f in finish.values() if f})
    mats = {f: product.materials.get(f, {'preset': 'satin_paint', 'color': '#888888'}) for f in finishes}
    assign = [{'match': '|'.join(nm for nm, g in finish.items() if g == f), 'material': f} for f in finishes]
    eng = {'_note': f'{product.title} for the engine, written by studio/fabkit/render.py from the fabrication CAD; part names '
                    'are the parts\' names, materials the parts\' finishes.',
           'model': os.path.relpath(glb, ROOT), 'origin_mm': origin, 'materials': mats, 'assign': assign}
    eng['flavours'] = product.variants or {'default': {}}       # the engine always paints a flavour
    pf = os.path.join(ROOT, 'studio', 'products', f'{product.name}.json')
    json.dump(eng, open(pf, 'w'), indent=1)
    proof_shot(product, boxes, origin)
    return glb, pf


def proof_shot(product, boxes, origin):
    """A first shot for the engine, studio/shots/<name>/proof.json (left alone once it exists, so it can be tuned): the
    product on a grey sweep, three-quarter front, a soft key and fill, the camera framed on its bounding box.

        python3 studio/engine/render.py studio/shots/<name>/proof.json --out renders/<day>/<name>-proof.png"""
    import math
    sd = os.path.join(ROOT, 'studio', 'shots', product.name); os.makedirs(sd, exist_ok=True)
    path = os.path.join(sd, 'proof.json')
    if os.path.exists(path):
        return path
    lo = [min(b[i] for b in boxes.values()) - origin[i] for i in range(3)]
    hi = [max(b[i + 3] for b in boxes.values()) - origin[i] for i in range(3)]
    W, D, H = ((hi[i] - lo[i]) / 1000 for i in range(3))
    r = 0.5 * math.sqrt(W * W + D * D + H * H)
    tgt = [0.0, 0.0, round(H / 2, 3)]
    lens = 70.0
    vfov = 2 * math.atan(12.0 / lens)
    dist = r / math.sin(vfov / 2) * 1.15
    az, el = math.radians(-28), math.radians(12)
    cam = [round(dist * math.cos(el) * math.sin(az), 3), round(-dist * math.cos(el) * math.cos(az), 3), round(H / 2 + dist * math.sin(el), 3)]
    shot = {'_note': f'{product.title}: a first look, written by studio/fabkit/render.py (edit freely; a rebuild keeps it).',
            'title': f'{product.title}, proof', 'size': [1500, 1200],
            'product': {'def': f'studio/products/{product.name}.json', 'instances': [{'position': [0, 0, 0], 'rotate_z': 0}]},
            'set': {'kind': 'sweep', 'color': '#8C8A86', 'width': max(6.0, 8 * r), 'front': max(5.0, 6 * r), 'depth': 1.5, 'radius': 1.2,
                    'height': max(4.0, 5 * r)},
            'camera': {'position': cam, 'target': tgt, 'lens_mm': lens, 'level': True},
            'lights': {'key': {'type': 'area', 'size_m': [2.0, 1.5], 'orbit': {'azimuth_deg': -40, 'elevation_deg': 38, 'distance_m': round(3 + 6 * r, 2)},
                               'target': tgt, 'irradiance': 2.0, 'color': '#FFF3E1'},
                       'fill': {'type': 'area', 'size_m': [2.5, 2.5], 'orbit': {'azimuth_deg': 50, 'elevation_deg': 15, 'distance_m': round(3 + 6 * r, 2)},
                                'target': tgt, 'irradiance': 0.8, 'color': '#FFF7EA'}},
            'render': {'samples': 128, 'adaptive': 0.02, 'denoise': True, 'clamp': 8, 'bounces': 10, 'view': 'Khronos PBR Neutral', 'exposure': 0.0}}
    if product.variants:
        shot['product']['flavour'] = next(iter(product.variants))
    json.dump(shot, open(path, 'w'), indent=1)
    return path
