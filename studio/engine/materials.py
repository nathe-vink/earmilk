"""The engine's material library: physically plausible presets built as Blender node trees.

Every preset takes overrides from the shot file (`materials` in a shot, by preset name), so the critic can prescribe
`materials.paint.clear_roughness` or `materials.oak.plank_contrast` and the next render uses it. Colours are sRGB hex;
albedos are scaled so that a "white" paint reflects about 85 % (a real white lacquer), never the 100 % a hex #FFFFFF
would imply and no surface on earth has.

Lessons from earmilk's path-traced rounds that live here:
- Paint under a full clear has no gloss of its own: the colour coat is matte (Specular IOR Level 0) and the clear
  (Coat) carries all the reflection, with a faint orange peel in the clear's normal only.
- A polished clear (roughness about 0.05) draws a light as a line; a satin clear (0.15 to 0.25) as a soft gradient. The
  peel is visible inside sharp highlights, so it is kept small.
- Floors read as real wood only with per-plank colour, long grain, and bevelled seams; walls need a faint plaster
  bump and a slight colour drift, or they read as a flat fill.
"""
import math

PRESET_DEFAULTS = {
    'paint':      dict(color='#FFFFFF', albedo=0.85, coat_roughness=0.08, peel=0.010, peel_scale_mm=1.1, coat_ior=1.5, base_roughness=0.6),
    'satin_paint': dict(color='#202020', albedo=1.0, roughness=0.45, specular=0.4),
    'metal':      dict(color='#C8C8C8', roughness=0.25, anisotropic=0.0),
    'gunmetal':   dict(color='#3A3A3C', roughness=0.32, metallic=0.85, coat=0.3, coat_roughness=0.15),
    'rubber':     dict(color='#1A1A1A', roughness=0.7, sheen=0.25),
    'paper_cone': dict(color='#2A2A2A', roughness=0.85, fibre_strength=0.12, ribs=0.0, ribs_count=14),
    'coated_cone': dict(color='#1C1C1C', roughness=0.45, coat=0.4, coat_roughness=0.3),
    'dome':       dict(color='#151515', roughness=0.4, sheen=0.3),
    'plastic':    dict(color='#202020', roughness=0.45, specular=0.5),
    'gloss_plastic': dict(color='#101010', roughness=0.15, coat=0.6, coat_roughness=0.05),
    'birch':      dict(color='#EAD8B0', roughness=0.55),
    'oak':        dict(base='#B8905F', dark='#9C7448', light='#C9A273', plank_w=0.18, plank_l=1.6, roughness=0.42, grain=0.6, seam=0.0015, plank_contrast=0.5),
    'plaster':    dict(color='#DDD6CA', roughness=0.92, bump=0.025, drift=0.03),
    'sweep':      dict(color='#A9A59E', roughness=0.55),
    'glass':      dict(color='#FFFFFF', roughness=0.0, ior=1.5),
    'emit':       dict(color='#FFFFFF', strength=1.0),
    'print':      dict(color='#1E1A17', roughness=0.6),
}


def hex_lin(h, scale=1.0):
    h = h.lstrip('#'); c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    lin = [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in c]
    return (*[min(1.0, v * scale) for v in lin], 1.0)


def _bump_noise(nt, scale_m, strength, distance_scale=0.2, detail=6.0, stretch=None, normal_in=None):
    geo = nt.nodes.new('ShaderNodeNewGeometry'); tx = nt.nodes.new('ShaderNodeTexNoise')
    tx.inputs['Scale'].default_value = 1.0 / scale_m; tx.inputs['Detail'].default_value = detail
    vec = geo.outputs['Position']
    if stretch:
        mp = nt.nodes.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = stretch
        nt.links.new(vec, mp.inputs['Vector']); vec = mp.outputs['Vector']
    nt.links.new(vec, tx.inputs['Vector'])
    bn = nt.nodes.new('ShaderNodeBump'); bn.inputs['Strength'].default_value = strength
    bn.inputs['Distance'].default_value = scale_m * distance_scale
    nt.links.new(tx.outputs['Fac'], bn.inputs['Height'])
    if normal_in is not None: nt.links.new(normal_in, bn.inputs['Normal'])
    return bn.outputs['Normal']


def make(bpy, name, preset, overrides=None, bevel_mm=0.0):
    """A Blender material from a preset plus overrides. bevel_mm > 0 adds a shader bevel (eases edges the mesh keeps
    sharp; the CAD's own fillets need none)."""
    p = {**PRESET_DEFAULTS[preset], **(overrides or {})}
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; b = nt.nodes['Principled BSDF']
    I = b.inputs
    def setin(k, v):
        if k in I: I[k].default_value = v
    normal = None
    if bevel_mm > 0:
        bev = nt.nodes.new('ShaderNodeBevel'); bev.inputs['Radius'].default_value = bevel_mm / 1000; bev.samples = 6
        normal = bev.outputs['Normal']
    if preset == 'paint':
        setin('Base Color', hex_lin(p['color'], p['albedo'])); setin('Roughness', p['base_roughness']); setin('Specular IOR Level', 0.0)
        setin('Coat Weight', 1.0); setin('Coat Roughness', p['coat_roughness']); setin('Coat IOR', p['coat_ior'])
        coat_n = _bump_noise(nt, p['peel_scale_mm'] / 1000, p['peel'], normal_in=normal) if p['peel'] > 0 else normal
        if normal is not None: nt.links.new(normal, I['Normal'])
        if coat_n is not None: nt.links.new(coat_n, I['Coat Normal'])
    elif preset in ('satin_paint', 'plastic', 'print'):
        setin('Base Color', hex_lin(p['color'], p.get('albedo', 1.0))); setin('Roughness', p['roughness'])
        if 'specular' in p: setin('Specular IOR Level', p['specular'])
        if normal is not None: nt.links.new(normal, I['Normal'])
    elif preset == 'gloss_plastic':
        setin('Base Color', hex_lin(p['color'])); setin('Roughness', p['roughness']); setin('Coat Weight', p['coat']); setin('Coat Roughness', p['coat_roughness'])
    elif preset == 'metal':
        setin('Base Color', hex_lin(p['color'])); setin('Metallic', 1.0); setin('Roughness', p['roughness']); setin('Anisotropic', p['anisotropic'])
    elif preset == 'gunmetal':
        setin('Base Color', hex_lin(p['color'])); setin('Metallic', p['metallic']); setin('Roughness', p['roughness'])
        setin('Coat Weight', p['coat']); setin('Coat Roughness', p['coat_roughness'])
    elif preset == 'rubber':
        setin('Base Color', hex_lin(p['color'])); setin('Roughness', p['roughness']); setin('Sheen Weight', p['sheen']); setin('Sheen Roughness', 0.5)
    elif preset == 'paper_cone':
        setin('Base Color', hex_lin(p['color'])); setin('Roughness', p['roughness'])
        n = _bump_noise(nt, 0.0004, p['fibre_strength'])
        nt.links.new(n, I['Normal'])
    elif preset == 'coated_cone':
        setin('Base Color', hex_lin(p['color'])); setin('Roughness', p['roughness']); setin('Coat Weight', p['coat']); setin('Coat Roughness', p['coat_roughness'])
    elif preset == 'dome':
        setin('Base Color', hex_lin(p['color'])); setin('Roughness', p['roughness']); setin('Sheen Weight', p['sheen'])
    elif preset == 'birch':
        _wood(nt, b, p['color'], p['roughness'], grain=0.35, stretch=(1.0, 1.0, 12.0))
    elif preset == 'oak':
        _planks(nt, b, p)
    elif preset in ('plaster', 'sweep'):
        setin('Base Color', hex_lin(p['color'])); setin('Roughness', p['roughness'])
        if preset == 'plaster':
            # a faint plaster bump and a slow colour drift, so a wall is a surface and not a flat fill
            nt.links.new(_bump_noise(nt, 0.004, p['bump']), I['Normal'])
            geo = nt.nodes.new('ShaderNodeNewGeometry'); nz = nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 0.7
            nt.links.new(geo.outputs['Position'], nz.inputs['Vector'])
            mr = nt.nodes.new('ShaderNodeMapRange'); mr.inputs['To Min'].default_value = 1 - p['drift']; mr.inputs['To Max'].default_value = 1 + p['drift']
            nt.links.new(nz.outputs['Fac'], mr.inputs['Value'])
            mix = nt.nodes.new('ShaderNodeMix'); mix.data_type = 'RGBA'; mix.blend_type = 'MULTIPLY'; mix.inputs['Factor'].default_value = 1.0
            ins = [x for x in mix.inputs if x.type == 'RGBA']; outs = [x for x in mix.outputs if x.type == 'RGBA']
            ins[0].default_value = hex_lin(p['color'])
            comb = nt.nodes.new('ShaderNodeCombineColor')
            for ch in ('Red', 'Green', 'Blue'): nt.links.new(mr.outputs['Result'], comb.inputs[ch])
            nt.links.new(comb.outputs['Color'], ins[1]); nt.links.new(outs[0], I['Base Color'])
    elif preset == 'glass':
        setin('Base Color', hex_lin(p['color'])); setin('Roughness', p['roughness']); setin('Transmission Weight', 1.0); setin('IOR', p['ior'])
    elif preset == 'emit':
        out = nt.nodes['Material Output']; nt.nodes.remove(b)
        em = nt.nodes.new('ShaderNodeEmission'); em.inputs['Color'].default_value = hex_lin(p['color']); em.inputs['Strength'].default_value = p['strength']
        nt.links.new(em.outputs['Emission'], out.inputs['Surface'])
    return m


def ply_section(bpy, name, color, roughness, axis, lo, thickness, plies):
    """The cut face of a plywood panel: `plies` veneers across its `thickness` along object axis `axis` (0, 1, 2,
    from `lo`, in the object's own units), alternating long grain (the colour) and end grain (darker, warmer), a
    thin dark glue line between each, and a faint grain noise. Baltic birch is about 1.4 mm a ply (13 in 18 mm)."""
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; b = nt.nodes['Principled BSDF']; L = nt.links
    b.inputs['Roughness'].default_value = roughness
    tc = nt.nodes.new('ShaderNodeTexCoord'); sep = nt.nodes.new('ShaderNodeSeparateXYZ')
    L.new(tc.outputs['Object'], sep.inputs['Vector'])
    def math(op, a, bval=None):
        n = nt.nodes.new('ShaderNodeMath'); n.operation = op
        for k, v in enumerate((a, bval)):
            if v is None: continue
            if isinstance(v, (int, float)): n.inputs[k].default_value = v
            else: L.new(v, n.inputs[k])
        return n.outputs['Value']
    # t runs 0 to plies across the panel's thickness
    t = math('MULTIPLY', math('SUBTRACT', sep.outputs['XYZ'[axis]], lo), plies / thickness)
    parity = math('MODULO', math('FLOOR', t), 2.0)                     # 0 long grain, 1 end grain
    f = math('FRACT', t)
    edge = math('MINIMUM', f, math('SUBTRACT', 1.0, f))                 # distance to the nearest glue line, in plies
    glue = math('SUBTRACT', 1.0, math('MINIMUM', math('DIVIDE', edge, 0.07), 1.0))
    # colour: the long grain, the end grain 14 % darker and a little warmer, the glue line darker still
    lin = hex_lin(color)
    endg = (lin[0] * 0.84, lin[1] * 0.80, lin[2] * 0.72, 1.0)
    mix = nt.nodes.new('ShaderNodeMix'); mix.data_type = 'RGBA'
    ins = [x for x in mix.inputs if x.type == 'RGBA']; outs = [x for x in mix.outputs if x.type == 'RGBA']
    ins[0].default_value = lin; ins[1].default_value = endg
    L.new(parity, mix.inputs['Factor'])
    dark = nt.nodes.new('ShaderNodeMix'); dark.data_type = 'RGBA'; dark.blend_type = 'MULTIPLY'
    dins = [x for x in dark.inputs if x.type == 'RGBA']; douts = [x for x in dark.outputs if x.type == 'RGBA']
    L.new(outs[0], dins[0]); dins[1].default_value = (0.45, 0.38, 0.30, 1.0)
    L.new(math('MULTIPLY', glue, 0.8), dark.inputs['Factor'])
    # a faint grain noise so each veneer is wood and not a flat band
    nz = nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 900.0; nz.inputs['Detail'].default_value = 3.0
    L.new(tc.outputs['Object'], nz.inputs['Vector'])
    mr = nt.nodes.new('ShaderNodeMapRange'); mr.inputs['To Min'].default_value = 0.93; mr.inputs['To Max'].default_value = 1.05
    L.new(nz.outputs['Fac'], mr.inputs['Value'])
    tone = nt.nodes.new('ShaderNodeMix'); tone.data_type = 'RGBA'; tone.blend_type = 'MULTIPLY'; tone.inputs['Factor'].default_value = 1.0
    tins = [x for x in tone.inputs if x.type == 'RGBA']; touts = [x for x in tone.outputs if x.type == 'RGBA']
    comb = nt.nodes.new('ShaderNodeCombineColor')
    for ch in ('Red', 'Green', 'Blue'): L.new(mr.outputs['Result'], comb.inputs[ch])
    L.new(douts[0], tins[0]); L.new(comb.outputs['Color'], tins[1])
    L.new(touts[0], b.inputs['Base Color'])
    return m


def _wood(nt, b, color, roughness, grain=0.4, stretch=(1, 1, 10)):
    geo = nt.nodes.new('ShaderNodeNewGeometry'); mp = nt.nodes.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = stretch
    nt.links.new(geo.outputs['Position'], mp.inputs['Vector'])
    wv = nt.nodes.new('ShaderNodeTexWave'); wv.inputs['Scale'].default_value = 40.0; wv.inputs['Distortion'].default_value = 6.0; wv.inputs['Detail'].default_value = 4.0
    nt.links.new(mp.outputs['Vector'], wv.inputs['Vector'])
    mr = nt.nodes.new('ShaderNodeMapRange'); mr.inputs['To Min'].default_value = 1 - grain * 0.25; mr.inputs['To Max'].default_value = 1.0
    nt.links.new(wv.outputs['Fac'], mr.inputs['Value'])
    comb = nt.nodes.new('ShaderNodeCombineColor')
    c = hex_lin(color)
    mul = nt.nodes.new('ShaderNodeMix'); mul.data_type = 'RGBA'; mul.blend_type = 'MULTIPLY'; mul.inputs['Factor'].default_value = 1.0
    ins = [x for x in mul.inputs if x.type == 'RGBA']; outs = [x for x in mul.outputs if x.type == 'RGBA']
    ins[0].default_value = c
    for ch in ('Red', 'Green', 'Blue'): nt.links.new(mr.outputs['Result'], comb.inputs[ch])
    nt.links.new(comb.outputs['Color'], ins[1]); nt.links.new(outs[0], b.inputs['Base Color'])
    b.inputs['Roughness'].default_value = roughness


def _planks(nt, b, p):
    """Oak floorboards in world space (x along the boards): a brick texture lays out boards of random length and
    shade, a stretched noise and a wave give each its grain, and the mortar lines become shallow bevelled seams."""
    geo = nt.nodes.new('ShaderNodeNewGeometry')
    br = nt.nodes.new('ShaderNodeTexBrick')
    # brick texture: rows are boards (height = board width), bricks are board lengths
    br.inputs['Scale'].default_value = 1.0
    br.inputs['Brick Width'].default_value = p['plank_l']; br.inputs['Row Height'].default_value = p['plank_w']
    br.inputs['Mortar Size'].default_value = p['seam']; br.inputs['Mortar Smooth'].default_value = 0.6
    br.offset = 0.37; br.squash = 1.0
    br.inputs['Color1'].default_value = hex_lin(p['light']); br.inputs['Color2'].default_value = hex_lin(p['dark'])
    br.inputs['Mortar'].default_value = hex_lin('#3A2A1C')
    sep = nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(geo.outputs['Position'], sep.inputs['Vector'])
    comb = nt.nodes.new('ShaderNodeCombineXYZ')
    nt.links.new(sep.outputs['X'], comb.inputs['X']); nt.links.new(sep.outputs['Y'], comb.inputs['Y'])
    nt.links.new(comb.outputs['Vector'], br.inputs['Vector'])
    # grain: noise stretched along the boards, and fine streaks
    mp = nt.nodes.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (1.0, 22.0, 1.0)
    nt.links.new(geo.outputs['Position'], mp.inputs['Vector'])
    nz = nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 3.0; nz.inputs['Detail'].default_value = 8.0; nz.inputs['Distortion'].default_value = 1.5
    nt.links.new(mp.outputs['Vector'], nz.inputs['Vector'])
    mr = nt.nodes.new('ShaderNodeMapRange'); mr.inputs['To Min'].default_value = 1 - 0.35 * p['grain']; mr.inputs['To Max'].default_value = 1 + 0.15 * p['grain']
    nt.links.new(nz.outputs['Fac'], mr.inputs['Value'])
    mul = nt.nodes.new('ShaderNodeMix'); mul.data_type = 'RGBA'; mul.blend_type = 'MULTIPLY'; mul.inputs['Factor'].default_value = 1.0
    ins = [x for x in mul.inputs if x.type == 'RGBA']; outs = [x for x in mul.outputs if x.type == 'RGBA']
    nt.links.new(br.outputs['Color'], ins[0])
    cc = nt.nodes.new('ShaderNodeCombineColor')
    for ch in ('Red', 'Green', 'Blue'): nt.links.new(mr.outputs['Result'], cc.inputs[ch])
    nt.links.new(cc.outputs['Color'], ins[1])
    # blend the per-board colour toward the base by plank_contrast
    mix = nt.nodes.new('ShaderNodeMix'); mix.data_type = 'RGBA'; mix.inputs['Factor'].default_value = 1 - p['plank_contrast']
    mins = [x for x in mix.inputs if x.type == 'RGBA']; mouts = [x for x in mix.outputs if x.type == 'RGBA']
    nt.links.new(outs[0], mins[0]); mins[1].default_value = hex_lin(p['base'])
    nt.links.new(mouts[0], b.inputs['Base Color'])
    b.inputs['Roughness'].default_value = p['roughness']
    # seams as a shallow bump from the brick's mortar factor, plus the grain's fine relief
    bn = nt.nodes.new('ShaderNodeBump'); bn.inputs['Strength'].default_value = 0.6; bn.inputs['Distance'].default_value = 0.0008
    inv = nt.nodes.new('ShaderNodeMath'); inv.operation = 'SUBTRACT'; inv.inputs[0].default_value = 1.0
    nt.links.new(br.outputs['Fac'], inv.inputs[1]); nt.links.new(inv.outputs['Value'], bn.inputs['Height'])
    bn2 = nt.nodes.new('ShaderNodeBump'); bn2.inputs['Strength'].default_value = 0.08; bn2.inputs['Distance'].default_value = 0.0005
    nt.links.new(nz.outputs['Fac'], bn2.inputs['Height']); nt.links.new(bn.outputs['Normal'], bn2.inputs['Normal'])
    nt.links.new(bn2.outputs['Normal'], b.inputs['Normal'])
