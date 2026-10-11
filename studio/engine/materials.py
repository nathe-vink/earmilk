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
    'veneer':     dict(color='#8A6548', roughness=0.42, grain=0.2, figure_m=0.022, leaf_m=0.4, arch_m=0.06, streak=0.8, coat=0.5),
    'oak':        dict(base='#B8905F', dark='#9C7448', light='#C9A273', plank_w=0.18, plank_l=1.6, roughness=0.42, grain=0.6, seam=0.0015, plank_contrast=0.5,
                       figure=0.22, rings=60.0, arch=4.0, flat_sawn=0.6, gloss_vary=0.3),
    'plaster':    dict(color='#DDD6CA', roughness=0.92, bump=0.025, drift=0.03),
    'sweep':      dict(color='#A9A59E', roughness=0.55, contact=0.0, contact_m=0.05, core=0.0, core_m=0.025),
    'glass':      dict(color='#FFFFFF', roughness=0.0, ior=1.5),
    # frosted translucent resin or glass (a cast waveguide): a milky body that light crosses (subsurface scattering
    # `radius` metres deep, so a thin wall glows and a thick one deepens to `absorb`), a frosted surface over it
    # (`roughness`), and a little clear transmission (`clear`) so it reads as cast resin and not as paint
    'frosted':    dict(color='#F2EEE6', absorb='#E9DFC9', roughness=0.45, ior=1.5, radius=0.025, clear=0.15),
    'emit':       dict(color='#FFFFFF', strength=1.0),
    'print':      dict(color='#1E1A17', roughness=0.6),
    # bark finishes, procedural (no texture download): paper birch's chalky white with dark horizontal lenticels, a few
    # dark scars and apricot where the outer layer has peeled; a eucalyptus's smooth bark shed in patches of cream,
    # grey, salmon, ochre and sage, each patch its own colour, its edges a little proud
    'birch_bark': dict(color='#ECE7DC', warm='#E6D6C4', lenticel='#2B2724', peel='#C9976E', roughness=0.72, lenticels=1.0,
                       scars=0.6, peel_amount=0.5, scale=1.0, bump=0.35),
    # a eucalyptus after rain: fresh underbark streaked green, olive, yellow and orange, under older layers left in
    # long strips (straw, rust, grey, brown; fresh to old), each layer's share and strip size its own, their edges
    # lifting; wet (`wet` 0..1): deep, saturated and glossy
    'eucalyptus_bark': dict(base=['#3F5E1C', '#6E8427', '#A99B35', '#C9772C'],
                            layers=[dict(color=['#B8955A', '#CDB27C'], cover=0.30, w=0.12, l=0.8),
                                    dict(color=['#9E3F22', '#C8683A'], cover=0.30, w=0.10, l=0.9),
                                    dict(color=['#6C6863', '#8C8478'], cover=0.40, w=0.20, l=1.2),
                                    dict(color=['#3E2C22', '#57402F'], cover=0.10, w=0.05, l=0.6)],
                            wander=1.0, torn=0.3, edge=0.8, streak=0.12, wet=0.8, scale=1.0, bump=0.4),
    # a grille's acoustically transparent knit: the yarn's colour, heathered (each yarn a little lighter or darker), a
    # fine weave about `pitch_mm` (its relief only reads close to), matt with a fabric's sheen
    'cloth': dict(color='#DCD6C8', pitch_mm=1.2, heather=0.08, roughness=0.88, sheen=0.6, bump=0.2),
    # agglomerated cork: granules about `granule_mm` across, each its own shade of the colour (`variation`), darker
    # gaps between them, matt; expanded (smoked) cork is dark brown, natural cork tan
    'cork': dict(color='#3B2F28', granule_mm=3.0, variation=0.35, gaps=0.5, roughness=0.9, bump=0.5),
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


def add_relief(m, strength, scale_m=0.012, stretch=(1.0, 1.0, 0.08)):
    """A brushed paint's relief on material `m`: a bump of noise drawn out along `stretch` (by default upright, as a
    brush runs down a panel or a stile), `scale_m` its feature size, so a low sun rakes something across a painted
    board instead of a dead-flat field (02b's round 12: the sunlit wainscot 2.8 levels across a 60 px square)."""
    nt = m.node_tree; b = nt.nodes['Principled BSDF']
    prev = b.inputs['Normal'].links[0].from_socket if b.inputs['Normal'].is_linked else None
    nt.links.new(_bump_noise(nt, scale_m, strength, stretch=stretch, normal_in=prev), b.inputs['Normal'])


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
    elif preset == 'veneer':
        _veneer(nt, b, p)
    elif preset == 'birch_bark':
        _birch_bark(nt, b, p, normal)
    elif preset == 'eucalyptus_bark':
        _eucalyptus_bark(nt, b, p, normal)
    elif preset == 'cloth':
        _cloth(nt, b, p, normal)
    elif preset == 'cork':
        _cork(nt, b, p, normal)
    elif preset in ('plaster', 'sweep'):
        setin('Base Color', hex_lin(p['color'])); setin('Roughness', p['roughness'])
        if preset == 'sweep' and (p.get('contact', 0) > 0 or p.get('core', 0) > 0):
            _contact(nt, I, hex_lin(p['color']), p['contact'], p['contact_m'], p.get('core', 0.0), p.get('core_m', 0.025))
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
    elif preset == 'frosted':
        setin('Base Color', hex_lin(p['color'])); setin('Roughness', p['roughness']); setin('IOR', p['ior'])
        setin('Subsurface Weight', 1.0); setin('Subsurface Scale', p['radius'])
        dc = hex_lin(p['absorb'])
        setin('Subsurface Radius', (max(dc[0], 0.05), max(dc[1], 0.05), max(dc[2], 0.05)))   # deeper where the tint lets light through
        setin('Transmission Weight', p['clear'])
        if normal is not None: nt.links.new(normal, I['Normal'])
    elif preset == 'emit':
        out = nt.nodes['Material Output']; nt.nodes.remove(b)
        em = nt.nodes.new('ShaderNodeEmission'); em.inputs['Color'].default_value = hex_lin(p['color']); em.inputs['Strength'].default_value = p['strength']
        nt.links.new(em.outputs['Emission'], out.inputs['Surface'])
    return m


def _contact(nt, I, col_lin, strength, distance, core=0.0, core_distance=0.025):
    """A contact shadow painted into a surface: where something stands on it or close to it, an ambient-occlusion term
    `distance` deep multiplies its base colour down to 1 - strength (in a corner), and leaves it alone farther out. A
    sweep under a box lit by large sources keeps little of its own (every lamp reaches the floor beside the plinth, and
    04b's base read pasted on); a photographer paints one in, and this is that. `core`: a second term, `core_distance`
    deep, multiplied with the first, for the dark line right at the base that a wide term spreads into a halo (04b's
    round 11: the floor 2 to 11 px from the plinth at 0.76 of the open floor, with the wide term at its ceiling)."""
    def term(s, d):
        ao = nt.nodes.new('ShaderNodeAmbientOcclusion'); ao.samples = 16; ao.only_local = False
        ao.inputs['Distance'].default_value = d
        mr = nt.nodes.new('ShaderNodeMapRange'); mr.clamp = True
        mr.inputs['To Min'].default_value = 1.0 - s; mr.inputs['To Max'].default_value = 1.0
        nt.links.new(ao.outputs['AO'], mr.inputs['Value'])
        return mr.outputs['Result']
    f = term(strength, distance) if strength > 0 else None
    if core > 0:
        c = term(core, core_distance)
        if f is None:
            f = c
        else:
            mul = nt.nodes.new('ShaderNodeMath'); mul.operation = 'MULTIPLY'
            nt.links.new(f, mul.inputs[0]); nt.links.new(c, mul.inputs[1]); f = mul.outputs['Value']
    mix = nt.nodes.new('ShaderNodeMix'); mix.data_type = 'RGBA'; mix.blend_type = 'MULTIPLY'; mix.inputs['Factor'].default_value = 1.0
    ins = [x for x in mix.inputs if x.type == 'RGBA']; outs = [x for x in mix.outputs if x.type == 'RGBA']
    ins[0].default_value = col_lin
    comb = nt.nodes.new('ShaderNodeCombineColor')
    for ch in ('Red', 'Green', 'Blue'):
        nt.links.new(f, comb.inputs[ch])
    nt.links.new(comb.outputs['Color'], ins[1]); nt.links.new(outs[0], I['Base Color'])


def ply_section(bpy, name, color, roughness, axis, lo, thickness, plies, per_layer=None):
    """The cut face of a plywood panel: `plies` veneers across its `thickness` along object axis `axis` (0, 1, 2,
    from `lo`, in the object's own units), alternating long grain (the colour) and end grain (darker, warmer), a
    thin dark glue line between each, and a faint grain noise. Baltic birch is about 1.4 mm a ply (13 in 18 mm).
    `per_layer`: a block glued up from sheets of that many plies each, every sheet starting on long grain again."""
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
    ply = math('FLOOR', t)
    if per_layer:
        ply = math('MODULO', ply, float(per_layer))                     # the ply's place in its own sheet
    parity = math('MODULO', ply, 2.0)                                   # 0 long grain, 1 end grain
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


def _nodes(nt):
    """Node and math shorthands for the procedural finishes."""
    def node(t, **kw):
        n = nt.nodes.new(t)
        for k, v in kw.items():
            setattr(n, k, v)
        return n

    def math_(op, a, b_=None, c=None):
        m = node('ShaderNodeMath', operation=op)
        for i, v in enumerate((a, b_, c)):
            if v is None:
                continue
            if isinstance(v, (int, float)):
                m.inputs[i].default_value = v
            else:
                nt.links.new(v, m.inputs[i])
        return m.outputs['Value']

    def mix(fac, a, b_, blend='MIX'):
        m = node('ShaderNodeMix', data_type='RGBA', blend_type=blend)
        ins = [x for x in m.inputs if x.type == 'RGBA']; out = [x for x in m.outputs if x.type == 'RGBA'][0]
        if isinstance(fac, (int, float)):
            m.inputs['Factor'].default_value = fac
        else:
            nt.links.new(fac, m.inputs['Factor'])
        for slot, v in zip(ins, (a, b_)):
            if isinstance(v, tuple):
                slot.default_value = v
            else:
                nt.links.new(v, slot)
        return out

    def smooth(x, lo, hi):
        mr = node('ShaderNodeMapRange', interpolation_type='SMOOTHSTEP')
        nt.links.new(x, mr.inputs['Value']); mr.inputs['From Min'].default_value = lo; mr.inputs['From Max'].default_value = hi
        return mr.outputs['Result']
    return node, math_, mix, smooth


def _face_uv(nt, node, math_):
    """Coordinates in the face's own plane, metres: (along, up, 0) on an upright face (along is x on a front or back,
    y on a side), (x, y, 0) on a level one. A pattern of 2D cells read here keeps its size on every face; a 3D one
    sliced by a face shows many small cells, the slices of those near the plane."""
    geo = node('ShaderNodeNewGeometry')
    sep = node('ShaderNodeSeparateXYZ'); nt.links.new(geo.outputs['Position'], sep.inputs['Vector'])
    nrm = node('ShaderNodeSeparateXYZ'); nt.links.new(geo.outputs['Normal'], nrm.inputs['Vector'])
    ax, ay, up = (math_('ABSOLUTE', nrm.outputs[c]) for c in ('X', 'Y', 'Z'))
    h = math_('ADD', math_('MULTIPLY', sep.outputs['X'], math_('ADD', ay, up)), math_('MULTIPLY', sep.outputs['Y'], ax))
    v = math_('ADD', math_('MULTIPLY', sep.outputs['Z'], math_('SUBTRACT', 1.0, up)), math_('MULTIPLY', sep.outputs['Y'], up))
    co = node('ShaderNodeCombineXYZ'); nt.links.new(h, co.inputs['X']); nt.links.new(v, co.inputs['Y'])
    return co.outputs['Vector'], geo


def _birch_bark(nt, b, p, normal_in=None):
    """Paper birch: a chalky white skin, its lenticels the short dark dashes that run round the trunk (horizontal
    here, the trunk's axis taken as z), longer and fewer ones among them, a few dark scars, and apricot where the
    papery outer layer has peeled. World space, metres; `scale` > 1 makes every mark smaller."""
    node, math_, mix, smooth = _nodes(nt)
    uv, geo = _face_uv(nt, node, math_)
    pos = geo.outputs['Position']
    k = p['scale']

    def mapped(sh, sv, offset=(0.0, 0.0, 0.0)):
        mp = node('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (sh * k, sv * k, 1.0)
        mp.inputs['Location'].default_value = offset
        nt.links.new(uv, mp.inputs['Vector'])
        return mp.outputs['Vector']

    def voronoi(vec, feature='F1'):
        vo = node('ShaderNodeTexVoronoi', feature=feature, voronoi_dimensions='2D'); vo.inputs['Randomness'].default_value = 1.0
        vo.inputs['Scale'].default_value = 1.0              # the mapping sets the size (the node's own default is 5)
        nt.links.new(vec, vo.inputs['Vector'])
        return vo

    # the lenticels: 2D Voronoi cells drawn out round the trunk, the dark core of each a dash; a slow noise thins them
    # in places so they gather in bands as a real trunk's do
    def dashes(sh, sv, r, keep_lo, gate_scale, gate_lo, offset):
        vo = voronoi(mapped(sh, sv, offset))
        core = math_('SUBTRACT', 1.0, smooth(vo.outputs['Distance'], r * 0.6, r))
        # each dash its own: the cell's random colour keeps some and drops the rest
        sep = node('ShaderNodeSeparateColor'); nt.links.new(vo.outputs['Color'], sep.inputs['Color'])
        keep = smooth(sep.outputs['Red'], keep_lo, keep_lo + 0.05)
        # the gate is drawn out round the trunk too, so the dashes gather in horizontal bands
        gate = node('ShaderNodeTexNoise'); gate.inputs['Scale'].default_value = gate_scale; gate.inputs['Detail'].default_value = 2.0
        nt.links.new(mapped(0.7, 6.0, (offset[0] + 4.0, offset[1], 0.0)), gate.inputs['Vector'])
        band = smooth(gate.outputs['Fac'], gate_lo, gate_lo + 0.15)
        return math_('MULTIPLY', math_('MULTIPLY', core, keep), band)
    small = dashes(22.0, 170.0, 0.30, 0.48, 2.0, 0.40, (0.0, 0.0, 0.0))
    large = dashes(6.0, 85.0, 0.22, 0.5, 1.4, 0.42, (3.1, 1.7, 0.0))
    marks = math_('MINIMUM', math_('ADD', math_('MULTIPLY', small, 0.8 * p['lenticels']), large), 1.0)
    # scars: a few dark blots where branches were, sparse
    sv = voronoi(mapped(3.0, 9.0, (7.0, 2.0, 0.0)))
    ssep = node('ShaderNodeSeparateColor'); nt.links.new(sv.outputs['Color'], ssep.inputs['Color'])
    scar = math_('MULTIPLY', math_('SUBTRACT', 1.0, smooth(sv.outputs['Distance'], 0.09, 0.12)), smooth(ssep.outputs['Green'], 0.8, 0.82))
    marks = math_('MINIMUM', math_('ADD', marks, math_('MULTIPLY', scar, p['scars'])), 1.0)
    # the skin: chalk white drifting warm, and apricot inner bark where the outer layer has peeled
    drift = node('ShaderNodeTexNoise'); drift.inputs['Scale'].default_value = 2.2 * k; drift.inputs['Detail'].default_value = 4.0
    nt.links.new(pos, drift.inputs['Vector'])
    skin = mix(smooth(drift.outputs['Fac'], 0.35, 0.75), hex_lin(p['color']), hex_lin(p['warm']))
    pn = node('ShaderNodeTexNoise'); pn.inputs['Scale'].default_value = 5.0 * k; pn.inputs['Detail'].default_value = 6.0
    pn.inputs['Roughness'].default_value = 0.6
    nt.links.new(mapped(1.0, 3.0, (11.0, 5.0, 0.0)), pn.inputs['Vector'])
    peel = math_('MULTIPLY', smooth(pn.outputs['Fac'], 0.66 - 0.06 * p['peel_amount'], 0.70 - 0.06 * p['peel_amount']), p['peel_amount'])
    col = mix(peel, skin, hex_lin(p['peel']))
    col = mix(marks, col, hex_lin(p['lenticel']))
    nt.links.new(col, b.inputs['Base Color'])
    b.inputs['Roughness'].default_value = p['roughness']
    if 'Sheen Weight' in b.inputs:
        b.inputs['Sheen Weight'].default_value = 0.15
    # relief: the lenticels sit a little proud, the peel's edge is a step, the paper has a fine fibre
    fib = node('ShaderNodeTexNoise'); fib.inputs['Scale'].default_value = 500.0; fib.inputs['Detail'].default_value = 2.0
    nt.links.new(mapped(1.0, 4.0), fib.inputs['Vector'])
    h = math_('ADD', math_('ADD', math_('MULTIPLY', marks, 0.6), math_('MULTIPLY', peel, -0.5)), math_('MULTIPLY', fib.outputs['Fac'], 0.08))
    bn = node('ShaderNodeBump'); bn.inputs['Strength'].default_value = p['bump']; bn.inputs['Distance'].default_value = 0.0006
    nt.links.new(h, bn.inputs['Height'])
    if normal_in is not None:
        nt.links.new(normal_in, bn.inputs['Normal'])
    nt.links.new(bn.outputs['Normal'], b.inputs['Normal'])


def _eucalyptus_bark(nt, b, p, normal_in=None):
    """A smooth-barked gum after rain. Its bark sheds in layers. Under everything is the fresh underbark (`base`, a ramp
    streaked up the trunk: deep green, olive, yellow, orange). Over it lie the older layers (`layers`, fresh to old),
    each left in long patches drawn out up the trunk (`w` across, `l` along, metres; `cover`, the share of a face the
    layer would cover alone), so a layer reads as strips and the layers together as camouflage. Each patch's edge lifts:
    a dark shadow on the bark under it, a lit lip on the curled edge, its ends torn along the fibres (`torn`). Fine streaks run up
    every layer (`streak`); rain runs down in wetter streaks, and the water (`wet`, 0..1) deepens and saturates the
    colour and glosses it. World space, metres, read in each face's plane; `scale` > 1 makes everything smaller. Owner,
    2026-10-10: the first version was too pastel, \"not like the long strips of peely camo-ish bark. Like a eucalyptus
    after rain.\""""
    from statistics import NormalDist
    node, math_, mix, smooth = _nodes(nt)
    uv, geo = _face_uv(nt, node, math_)
    k = p['scale']
    sep = node('ShaderNodeSeparateXYZ'); nt.links.new(uv, sep.inputs['Vector'])
    y = sep.outputs['Y']

    def noise(x, w, l, seed, detail=2.0):
        """Perlin noise drawn out up the face: features about `w` across and `l` along (Fac: mean 0.5, sd 0.089 at
        detail 2, 0.083 at 3; measured)."""
        co = node('ShaderNodeCombineXYZ')
        nt.links.new(math_('DIVIDE', x, w / k), co.inputs['X'])
        nt.links.new(math_('DIVIDE', y, l / k), co.inputs['Y'])
        co.inputs['Z'].default_value = seed
        nz = node('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 1.0; nz.inputs['Detail'].default_value = detail
        nt.links.new(co.outputs['Vector'], nz.inputs['Vector'])
        return nz.outputs['Fac']

    def ramp(fac, colours, lo=0.36, hi=0.64):
        r = node('ShaderNodeValToRGB'); cr = r.color_ramp
        while len(cr.elements) < len(colours):
            cr.elements.new(0.0)
        for i, (el, hx) in enumerate(zip(cr.elements, colours)):
            el.position = i / (len(colours) - 1); el.color = hex_lin(hx)
        mr = node('ShaderNodeMapRange'); nt.links.new(fac, mr.inputs['Value'])
        mr.inputs['From Min'].default_value = lo; mr.inputs['From Max'].default_value = hi
        nt.links.new(mr.outputs['Result'], r.inputs['Fac'])
        return r.outputs['Color']

    def streaked(col, seed):
        """The fine streaks up a layer: its colour lifted and dropped a little along the fibres."""
        f = noise(sep.outputs['X'], 0.008, 0.3, seed, 3.0)
        mr = node('ShaderNodeMapRange'); nt.links.new(f, mr.inputs['Value'])
        mr.inputs['From Min'].default_value = 0.35; mr.inputs['From Max'].default_value = 0.65
        mr.inputs['To Min'].default_value = 1 - p['streak']; mr.inputs['To Max'].default_value = 1 + p['streak']
        g = node('ShaderNodeCombineColor')
        for ch in ('Red', 'Green', 'Blue'):
            nt.links.new(mr.outputs['Result'], g.inputs[ch])
        return mix(1.0, col, g.outputs['Color'], 'MULTIPLY'), f

    # the trunk's sway: every strip bends across with a slow noise read up the face
    x = math_('ADD', sep.outputs['X'], math_('MULTIPLY', math_('SUBTRACT', noise(sep.outputs['X'], 1.6, 1.1, 1.3), 0.5),
                                               p['wander'] * 0.25))
    # the fresh underbark: broad streaks through its ramp
    col, fibre = streaked(ramp(noise(x, 0.08, 0.9, 2.9), p['base']), 3.3)
    h = math_('MULTIPLY', fibre, 0.3)
    edge = p['edge']
    for i, L in enumerate(p['layers'], start=1):
        seed = 11.0 * i + 0.7
        # torn along the fibres: a fine noise drawn out up the face roughens the patch's edge
        torn = math_('MULTIPLY', math_('SUBTRACT', noise(x, L['w'] * 0.15, L['l'] * 0.25, seed + 5.0, 3.0), 0.5), p['torn'])
        n = math_('ADD', noise(x, L['w'], L['l'], seed), torn)
        t = 0.5 + (0.0887 ** 2 + (p['torn'] * 0.0833) ** 2) ** 0.5 * NormalDist().inv_cdf(1.0 - L['cover'])
        m = smooth(n, t - 0.002, t + 0.002)
        shadow = math_('MULTIPLY', smooth(n, t - 0.04, t), math_('SUBTRACT', 1.0, m))
        lip = math_('SUBTRACT', smooth(n, t, t + 0.006), smooth(n, t + 0.012, t + 0.03))
        c, _ = streaked(ramp(noise(x, L['w'] * 0.5, L['l'], seed + 2.0), L['color']), seed + 3.0)
        col = mix(math_('MULTIPLY', shadow, 0.7 * edge), col, hex_lin('#1E1712'))
        col = mix(m, col, c)
        col = mix(math_('MULTIPLY', lip, 0.35 * edge), col, hex_lin('#EDE3CF'))
        h = math_('SUBTRACT', h, math_('MULTIPLY', shadow, 0.4 * edge))
        hm = node('ShaderNodeMix', data_type='FLOAT'); nt.links.new(m, hm.inputs['Factor'])
        nt.links.new(h, hm.inputs['A']); nt.links.new(math_('ADD', float(i), math_('MULTIPLY', lip, 0.6 * edge)), hm.inputs['B'])
        h = hm.outputs['Result']
    # after rain: wetter streaks where it ran down; the water deepens and saturates (the colour multiplied by itself a
    # little), smooths and glosses
    wl = math_('MULTIPLY', math_('ADD', 0.7, math_('MULTIPLY', smooth(noise(x, 0.1, 1.4, 9.1), 0.38, 0.62), 0.6)), p['wet'])
    col = mix(math_('MULTIPLY', wl, 0.45), col, mix(1.0, col, col, 'MULTIPLY'))
    nt.links.new(col, b.inputs['Base Color'])
    nt.links.new(math_('MAXIMUM', math_('SUBTRACT', 0.55, math_('MULTIPLY', wl, 0.3)), 0.12), b.inputs['Roughness'])
    if 'Coat Weight' in b.inputs:
        nt.links.new(math_('MULTIPLY', wl, 0.5), b.inputs['Coat Weight']); b.inputs['Coat Roughness'].default_value = 0.08
    bn = node('ShaderNodeBump'); bn.inputs['Strength'].default_value = p['bump']; bn.inputs['Distance'].default_value = 0.0005
    nt.links.new(h, bn.inputs['Height'])
    if normal_in is not None:
        nt.links.new(normal_in, bn.inputs['Normal'])
    nt.links.new(bn.outputs['Normal'], b.inputs['Normal'])


def _cloth(nt, b, p, normal_in=None):
    """A knit stretched on a grille: threads crossing at `pitch_mm` in the face's plane, over and under in a checker
    (the relief, faint, reads only close to), each yarn's colour heathered by a noise drawn out along it, matt, with a
    fabric's sheen at grazing angles. World space, read in each face's plane."""
    node, math_, mix, smooth = _nodes(nt)
    uv, geo = _face_uv(nt, node, math_)
    sep = node('ShaderNodeSeparateXYZ'); nt.links.new(uv, sep.inputs['Vector'])
    pitch = p['pitch_mm'] / 1000.0
    u, v = (math_('DIVIDE', sep.outputs[c], pitch) for c in ('X', 'Y'))
    # a thread's cross-section: a raised sine across it; over and under by the checker of the cells
    wu = math_('ABSOLUTE', math_('SINE', math_('MULTIPLY', u, math.pi)))
    wv = math_('ABSOLUTE', math_('SINE', math_('MULTIPLY', v, math.pi)))
    chk = math_('MODULO', math_('ADD', math_('FLOOR', u), math_('FLOOR', v)), 2.0)
    h = math_('ADD', math_('MULTIPLY', wu, chk), math_('MULTIPLY', wv, math_('SUBTRACT', 1.0, chk)))
    # heather: each yarn a little lighter or darker, a noise drawn out along the threads
    co = node('ShaderNodeCombineXYZ'); nt.links.new(math_('MULTIPLY', u, 0.5), co.inputs['X']); nt.links.new(math_('MULTIPLY', v, 0.04), co.inputs['Y'])
    nz = node('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 1.0; nz.inputs['Detail'].default_value = 3.0
    nt.links.new(co.outputs['Vector'], nz.inputs['Vector'])
    mr = node('ShaderNodeMapRange'); nt.links.new(nz.outputs['Fac'], mr.inputs['Value'])
    mr.inputs['From Min'].default_value = 0.35; mr.inputs['From Max'].default_value = 0.65
    mr.inputs['To Min'].default_value = 1 - p['heather']; mr.inputs['To Max'].default_value = 1 + p['heather']
    g = node('ShaderNodeCombineColor')
    for ch in ('Red', 'Green', 'Blue'):
        nt.links.new(mr.outputs['Result'], g.inputs[ch])
    col = mix(1.0, hex_lin(p['color']), g.outputs['Color'], 'MULTIPLY')
    nt.links.new(col, b.inputs['Base Color'])
    b.inputs['Roughness'].default_value = p['roughness']
    if 'Sheen Weight' in b.inputs:
        b.inputs['Sheen Weight'].default_value = p['sheen']; b.inputs['Sheen Roughness'].default_value = 0.45
    bn = node('ShaderNodeBump'); bn.inputs['Strength'].default_value = p['bump']; bn.inputs['Distance'].default_value = pitch * 0.25
    nt.links.new(h, bn.inputs['Height'])
    if normal_in is not None:
        nt.links.new(normal_in, bn.inputs['Normal'])
    nt.links.new(bn.outputs['Normal'], b.inputs['Normal'])


def _cork(nt, b, p, normal_in=None):
    """Agglomerated cork: granules (2D cells about `granule_mm` across, read in each face's plane, with smaller ones
    among them), each its own shade of the colour, darker in the gaps between them, each granule a little domed; matt."""
    node, math_, mix, smooth = _nodes(nt)
    uv, geo = _face_uv(nt, node, math_)
    g = p['granule_mm'] / 1000.0

    def cells(size, seed):
        mp = node('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (1 / size, 1 / size, 1.0)
        mp.inputs['Location'].default_value = (seed, seed * 0.7, 0.0)
        nt.links.new(uv, mp.inputs['Vector'])
        vo = node('ShaderNodeTexVoronoi', feature='F1', voronoi_dimensions='2D'); vo.inputs['Scale'].default_value = 1.0
        vo.inputs['Randomness'].default_value = 1.0; nt.links.new(mp.outputs['Vector'], vo.inputs['Vector'])
        ed = node('ShaderNodeTexVoronoi', feature='DISTANCE_TO_EDGE', voronoi_dimensions='2D'); ed.inputs['Scale'].default_value = 1.0
        ed.inputs['Randomness'].default_value = 1.0; nt.links.new(mp.outputs['Vector'], ed.inputs['Vector'])
        cs = node('ShaderNodeSeparateColor'); nt.links.new(vo.outputs['Color'], cs.inputs['Color'])
        return cs.outputs['Red'], ed.outputs['Distance']

    s1, e1 = cells(g, 0.0)
    s2, e2 = cells(g * 0.45, 13.1)
    small = smooth(s2, 0.55, 0.56)                    # some places the smaller granules show instead
    val = math_('ADD', math_('MULTIPLY', s1, math_('SUBTRACT', 1.0, small)), math_('MULTIPLY', s2, small))
    e = math_('ADD', math_('MULTIPLY', e1, math_('SUBTRACT', 1.0, small)), math_('MULTIPLY', e2, small))
    mr = node('ShaderNodeMapRange'); nt.links.new(val, mr.inputs['Value'])
    mr.inputs['To Min'].default_value = 1 - p['variation']; mr.inputs['To Max'].default_value = 1 + p['variation']
    gc = node('ShaderNodeCombineColor')
    for ch in ('Red', 'Green', 'Blue'):
        nt.links.new(mr.outputs['Result'], gc.inputs[ch])
    col = mix(1.0, hex_lin(p['color']), gc.outputs['Color'], 'MULTIPLY')
    gap = math_('SUBTRACT', 1.0, smooth(e, 0.0, 0.12))
    col = mix(math_('MULTIPLY', gap, p['gaps']), col, hex_lin('#120D0A'))
    nt.links.new(col, b.inputs['Base Color'])
    b.inputs['Roughness'].default_value = p['roughness']
    bn = node('ShaderNodeBump'); bn.inputs['Strength'].default_value = p['bump']; bn.inputs['Distance'].default_value = g * 0.15
    nt.links.new(smooth(e, 0.0, 0.25), bn.inputs['Height'])
    if normal_in is not None:
        nt.links.new(normal_in, bn.inputs['Normal'])
    nt.links.new(bn.outputs['Normal'], b.inputs['Normal'])


def _veneer(nt, b, p):
    """A sliced-veneer panel (walnut, oak) under a satin lacquer, for furniture: the grain runs horizontally along the
    piece (world x) on its fronts and sides and along it on its top, as a cabinetmaker lays it. The growth rings are
    lines across the grain at about `figure_m` apart, warped by a slow noise so they wander, crowd and spread as a
    flat-sawn leaf's do (`grain`: how much darker the latewood line is), with long streaks of colour in the leaf
    (`streak`) and a clear coat (`coat`, its weight). 10's round 8: the birch shader's grain ran vertically on a
    sideboard's doors, a regular 4 px pinstripe that read as corrugated card."""
    def node(t, **kw):
        n = nt.nodes.new(t)
        for k, v in kw.items():
            setattr(n, k, v)
        return n
    def math_(op, a, b_=None, c=None):
        m = node('ShaderNodeMath', operation=op)
        for i, v in enumerate((a, b_, c)):
            if v is None:
                continue
            if isinstance(v, (int, float)):
                m.inputs[i].default_value = v
            else:
                nt.links.new(v, m.inputs[i])
        return m.outputs['Value']
    geo = node('ShaderNodeNewGeometry')
    sep = node('ShaderNodeSeparateXYZ'); nt.links.new(geo.outputs['Position'], sep.inputs['Vector'])
    nrm = node('ShaderNodeSeparateXYZ'); nt.links.new(geo.outputs['Normal'], nrm.inputs['Vector'])
    # across the grain: height on an upright face, depth on a level one (the face's normal decides)
    up = math_('ABSOLUTE', nrm.outputs['Z'])
    across = math_('ADD', math_('MULTIPLY', sep.outputs['Z'], math_('SUBTRACT', 1.0, up)), math_('MULTIPLY', sep.outputs['Y'], up))
    along = sep.outputs['X']
    # the leaf's figure: a slow noise over (along, across) bends the rings; a second, slower one sets their spacing
    co = node('ShaderNodeCombineXYZ'); nt.links.new(along, co.inputs['X']); nt.links.new(across, co.inputs['Y'])
    sc = node('ShaderNodeMapping'); sc.inputs['Scale'].default_value = (1.6, 5.0, 1.0)
    nt.links.new(co.outputs['Vector'], sc.inputs['Vector'])
    nz = node('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 1.0; nz.inputs['Detail'].default_value = 3.0
    nz.inputs['Roughness'].default_value = 0.55; nt.links.new(sc.outputs['Vector'], nz.inputs['Vector'])
    # the bend: a ring or two either way, so the lines wander as a leaf's do (10's round 9: nine rings either way drew
    # every door as a topographic map, the rings following the noise's contours)
    warp = math_('MULTIPLY', math_('SUBTRACT', nz.outputs['Fac'], 0.5), 2.5 * p['figure_m'])
    # cathedrals: each leaf (`leaf_m` wide along the grain, a door's width) bends its rings into nested arches about
    # its middle, so neighbouring leaves read as book-matched
    u = math_('SUBTRACT', math_('FRACT', math_('DIVIDE', along, p['leaf_m'])), 0.5)
    arch = math_('MULTIPLY', math_('POWER', math_('ABSOLUTE', u), 1.5), p['arch_m'] * 2.83)
    v0 = math_('ADD', math_('ADD', across, warp), arch)
    # the rings' spacing wanders too, closer and wider every few rings (a growth year's width is not a constant: an
    # even spacing printed as an inked chevron pattern, 01's and 10's round 10)
    sp = node('ShaderNodeCombineXYZ'); nt.links.new(math_('DIVIDE', v0, 3.0 * p['figure_m']), sp.inputs['X'])
    nt.links.new(math_('MULTIPLY', along, 0.7), sp.inputs['Y'])
    spn = node('ShaderNodeTexNoise'); spn.inputs['Scale'].default_value = 1.0; spn.inputs['Detail'].default_value = 1.0
    nt.links.new(sp.outputs['Vector'], spn.inputs['Vector'])
    v = math_('ADD', v0, math_('MULTIPLY', math_('SUBTRACT', spn.outputs['Fac'], 0.5), 1.4 * p['figure_m']))
    rings = math_('FRACT', math_('DIVIDE', v, p['figure_m']))
    # the latewood line: a soft dark band across the middle of each ring, as dense on both sides (a sawtooth, dark at
    # the ring's end and light the moment the next began, printed a 13-18 level step at every ring: 10's round 9)
    def band(f, half):
        d = math_('MULTIPLY', math_('ABSOLUTE', math_('SUBTRACT', f, 0.5)), 2.0)
        return math_('POWER', math_('MAXIMUM', math_('SUBTRACT', 1.0, math_('DIVIDE', d, half)), 0.0), 1.5)
    # each ring its own: how dark its latewood is varies ring to ring and slowly along it (a noise read at the ring's
    # index), so the lines do not print as one repeated stroke
    idx = math_('FLOOR', math_('DIVIDE', v, p['figure_m']))
    ri = node('ShaderNodeCombineXYZ'); nt.links.new(math_('MULTIPLY', idx, 0.731), ri.inputs['X'])
    nt.links.new(math_('MULTIPLY', along, 0.9), ri.inputs['Y'])
    rn = node('ShaderNodeTexNoise'); rn.inputs['Scale'].default_value = 2.0; rn.inputs['Detail'].default_value = 1.0
    nt.links.new(ri.outputs['Vector'], rn.inputs['Vector'])
    depth = math_('MINIMUM', math_('MAXIMUM', math_('MULTIPLY', math_('SUBTRACT', rn.outputs['Fac'], 0.28), 2.2), 0.12), 1.0)
    late = math_('MULTIPLY', band(rings, 0.42), depth)
    # and the fine grain between the rings, a fifth of their spacing, faint
    fine = math_('FRACT', math_('DIVIDE', v, p['figure_m'] * 0.2))
    fine_l = band(fine, 0.4)
    # pores: fine dark streaks drawn out along the grain, as an open-grained walnut's show under the lacquer
    pc = node('ShaderNodeCombineXYZ'); nt.links.new(math_('MULTIPLY', along, 30.0), pc.inputs['X'])
    nt.links.new(math_('MULTIPLY', v, 700.0), pc.inputs['Y'])
    pn = node('ShaderNodeTexNoise'); pn.inputs['Scale'].default_value = 1.0; pn.inputs['Detail'].default_value = 2.0
    nt.links.new(pc.outputs['Vector'], pn.inputs['Vector'])
    pores = math_('MULTIPLY', math_('MAXIMUM', math_('SUBTRACT', pn.outputs['Fac'], 0.58), 0.0), 2.4)
    shade = math_('SUBTRACT', math_('SUBTRACT', math_('SUBTRACT', 1.0, math_('MULTIPLY', late, p['grain'])),
                                          math_('MULTIPLY', fine_l, p['grain'] * 0.25)), math_('MULTIPLY', pores, p['grain'] * 0.35))
    # streaks: long, slow variations of the leaf's colour along the grain
    sc2 = node('ShaderNodeMapping'); sc2.inputs['Scale'].default_value = (0.25, 9.0, 1.0)
    nt.links.new(co.outputs['Vector'], sc2.inputs['Vector'])
    nz2 = node('ShaderNodeTexNoise'); nz2.inputs['Scale'].default_value = 1.0; nz2.inputs['Detail'].default_value = 2.0
    nt.links.new(sc2.outputs['Vector'], nz2.inputs['Vector'])
    streak = math_('ADD', 1.0, math_('MULTIPLY', math_('SUBTRACT', nz2.outputs['Fac'], 0.5), 0.35 * p['streak']))
    val = math_('MULTIPLY', shade, streak)
    tint = node('ShaderNodeMix', data_type='RGBA', blend_type='MULTIPLY'); tint.inputs['Factor'].default_value = 1.0
    ins = [x for x in tint.inputs if x.type == 'RGBA']; outs = [x for x in tint.outputs if x.type == 'RGBA']
    ins[0].default_value = hex_lin(p['color'])
    g = node('ShaderNodeCombineColor')
    for ch in ('Red', 'Green', 'Blue'): nt.links.new(val, g.inputs[ch])
    nt.links.new(g.outputs['Color'], ins[1]); nt.links.new(outs[0], b.inputs['Base Color'])
    b.inputs['Roughness'].default_value = p['roughness']
    b.inputs['Coat Weight'].default_value = p['coat']; b.inputs['Coat Roughness'].default_value = 0.25


def _planks(nt, b, p):
    """Oak floorboards in world space (x along the boards): a brick texture lays out boards of random length and
    shade, a stretched noise gives each its grain, and the mortar lines become shallow bevelled seams; each row is slid
    along by its own random amount, so the end joints fall at random.

    Each board is its own piece of wood: a second brick texture, laid out like the first, gives every board a random
    number r, which offsets its grain (so the grain stops at the seams instead of running on as laminate does), sets
    its sheen (`gloss_vary`) and its cut. A flat-sawn board (`flat_sawn`, the share of them) shows its growth rings as
    nested cathedral arches: rings at s = (v - c)^2 rings + u arch, v across the board from a pith offset c, u along it;
    a rift-sawn board shows them as straight lines. The latewood at the end of each ring is the dark line (`figure`,
    how much darker)."""
    geo = nt.nodes.new('ShaderNodeNewGeometry')
    br = nt.nodes.new('ShaderNodeTexBrick')
    # brick texture: rows are boards (height = board width), bricks are board lengths
    br.inputs['Scale'].default_value = 1.0
    br.inputs['Brick Width'].default_value = p['plank_l']; br.inputs['Row Height'].default_value = p['plank_w']
    br.inputs['Mortar Size'].default_value = p['seam']; br.inputs['Mortar Smooth'].default_value = 0.6
    br.offset = 0.0; br.squash = 1.0
    br.inputs['Color1'].default_value = hex_lin(p['light']); br.inputs['Color2'].default_value = hex_lin(p['dark'])
    br.inputs['Mortar'].default_value = hex_lin('#3A2A1C')
    sep = nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(geo.outputs['Position'], sep.inputs['Vector'])
    # each row of boards slid along by its own random amount, so the end joints fall at random as boards are laid
    # (a brick texture's regular offset lines them up in every other row: a column of joints across the floor)
    row = nt.nodes.new('ShaderNodeMath'); row.operation = 'FLOOR'
    rdiv = nt.nodes.new('ShaderNodeMath'); rdiv.operation = 'DIVIDE'; rdiv.inputs[1].default_value = p['plank_w']
    nt.links.new(sep.outputs['Y'], rdiv.inputs[0]); nt.links.new(rdiv.outputs['Value'], row.inputs[0])
    wn = nt.nodes.new('ShaderNodeTexWhiteNoise'); wn.noise_dimensions = '1D'
    nt.links.new(row.outputs['Value'], wn.inputs['W'])
    slide = nt.nodes.new('ShaderNodeMath'); slide.operation = 'MULTIPLY_ADD'
    nt.links.new(wn.outputs['Value'], slide.inputs[0]); slide.inputs[1].default_value = p['plank_l']
    nt.links.new(sep.outputs['X'], slide.inputs[2])
    comb = nt.nodes.new('ShaderNodeCombineXYZ')
    nt.links.new(slide.outputs['Value'], comb.inputs['X']); nt.links.new(sep.outputs['Y'], comb.inputs['Y'])
    nt.links.new(comb.outputs['Vector'], br.inputs['Vector'])
    # every board's own random number r, from a second brick texture laid out like the first, black to white
    br2 = nt.nodes.new('ShaderNodeTexBrick')
    for k in ('Scale', 'Brick Width', 'Row Height', 'Mortar Size', 'Mortar Smooth'):
        br2.inputs[k].default_value = br.inputs[k].default_value
    br2.offset = br.offset; br2.squash = br.squash
    br2.inputs['Color1'].default_value = (0, 0, 0, 1); br2.inputs['Color2'].default_value = (1, 1, 1, 1)
    br2.inputs['Mortar'].default_value = (0.5, 0.5, 0.5, 1)
    nt.links.new(comb.outputs['Vector'], br2.inputs['Vector'])
    rs = nt.nodes.new('ShaderNodeSeparateColor'); nt.links.new(br2.outputs['Color'], rs.inputs['Color'])
    r = rs.outputs['Red']
    def m(op, a, bb=None):
        n = nt.nodes.new('ShaderNodeMath'); n.operation = op
        for i, v in enumerate((a, bb)):
            if v is None:
                continue
            if isinstance(v, (int, float)): n.inputs[i].default_value = v
            else: nt.links.new(v, n.inputs[i])
        return n.outputs['Value']
    # the board's grain offset by r, so neighbouring boards do not share one grain
    off = nt.nodes.new('ShaderNodeCombineXYZ')
    nt.links.new(m('MULTIPLY', r, 7.3), off.inputs['X']); nt.links.new(m('MULTIPLY', r, 3.1), off.inputs['Z'])
    pos = nt.nodes.new('ShaderNodeVectorMath'); pos.operation = 'ADD'
    nt.links.new(geo.outputs['Position'], pos.inputs[0]); nt.links.new(off.outputs['Vector'], pos.inputs[1])
    # grain: noise stretched along the boards, and fine streaks
    mp = nt.nodes.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (1.0, 22.0, 1.0)
    nt.links.new(pos.outputs['Vector'], mp.inputs['Vector'])
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
    # growth rings: v across the board (-0.5 to 0.5 of its width), u along it; arches on a flat-sawn board, straight
    # lines on a rift-sawn one, wobbled by a slow noise; the latewood a thin dark line before each ring's end
    v = m('SUBTRACT', m('FRACT', m('DIVIDE', sep.outputs['Y'], p['plank_w'])), 0.5)
    d = m('SUBTRACT', v, m('MULTIPLY', m('SUBTRACT', r, 0.5), 0.6))
    u = m('ADD', sep.outputs['X'], m('MULTIPLY', r, 11.0))
    wob_map = nt.nodes.new('ShaderNodeMapping'); wob_map.inputs['Scale'].default_value = (1.5, 12.0, 1.0)
    nt.links.new(pos.outputs['Vector'], wob_map.inputs['Vector'])
    wob = nt.nodes.new('ShaderNodeTexNoise'); wob.inputs['Scale'].default_value = 1.0; wob.inputs['Detail'].default_value = 3.0
    nt.links.new(wob_map.outputs['Vector'], wob.inputs['Vector'])
    wobble = m('MULTIPLY', m('SUBTRACT', wob.outputs['Fac'], 0.5), 3.0)
    s_flat = m('ADD', m('ADD', m('MULTIPLY', m('MULTIPLY', d, d), p['rings']), m('MULTIPLY', u, p['arch'])), wobble)
    s_rift = m('ADD', m('MULTIPLY', v, p['rings'] * 0.2), wobble)
    flat = m('LESS_THAN', r, p['flat_sawn'])
    s_ring = m('ADD', m('MULTIPLY', s_flat, flat), m('MULTIPLY', s_rift, m('SUBTRACT', 1.0, flat)))
    late = m('POWER', m('FRACT', s_ring), 6.0)
    fig = m('SUBTRACT', 1.0, m('MULTIPLY', late, p['figure']))
    figc = nt.nodes.new('ShaderNodeCombineColor')
    for ch in ('Red', 'Green', 'Blue'): nt.links.new(fig, figc.inputs[ch])
    figmul = nt.nodes.new('ShaderNodeMix'); figmul.data_type = 'RGBA'; figmul.blend_type = 'MULTIPLY'; figmul.inputs['Factor'].default_value = 1.0
    fins = [x for x in figmul.inputs if x.type == 'RGBA']; fouts = [x for x in figmul.outputs if x.type == 'RGBA']
    nt.links.new(outs[0], fins[0]); nt.links.new(figc.outputs['Color'], fins[1])
    # blend the per-board colour toward the base by plank_contrast
    mix = nt.nodes.new('ShaderNodeMix'); mix.data_type = 'RGBA'; mix.inputs['Factor'].default_value = 1 - p['plank_contrast']
    mins = [x for x in mix.inputs if x.type == 'RGBA']; mouts = [x for x in mix.outputs if x.type == 'RGBA']
    nt.links.new(fouts[0], mins[0]); mins[1].default_value = hex_lin(p['base'])
    nt.links.new(mouts[0], b.inputs['Base Color'])
    # each board's sheen a little different, as boards finished together still are
    nt.links.new(m('MULTIPLY', m('ADD', 1.0 - p['gloss_vary'] / 2, m('MULTIPLY', r, p['gloss_vary'])), p['roughness']), b.inputs['Roughness'])
    # seams as a shallow bump from the brick's mortar factor, plus the grain's fine relief
    bn = nt.nodes.new('ShaderNodeBump'); bn.inputs['Strength'].default_value = 0.6; bn.inputs['Distance'].default_value = 0.0008
    inv = nt.nodes.new('ShaderNodeMath'); inv.operation = 'SUBTRACT'; inv.inputs[0].default_value = 1.0
    nt.links.new(br.outputs['Fac'], inv.inputs[1]); nt.links.new(inv.outputs['Value'], bn.inputs['Height'])
    bn2 = nt.nodes.new('ShaderNodeBump'); bn2.inputs['Strength'].default_value = 0.08; bn2.inputs['Distance'].default_value = 0.0005
    nt.links.new(nz.outputs['Fac'], bn2.inputs['Height']); nt.links.new(bn.outputs['Normal'], bn2.inputs['Normal'])
    nt.links.new(bn2.outputs['Normal'], b.inputs['Normal'])


def polarise(bpy, cam_rot, strength, angle_deg, ior=1.5):
    """A polarising filter on the lens. Light a dielectric (a clear coat, a plastic, a waxed floor) reflects is
    polarised: the component across the plane of incidence (s) reflects more than the one in it (p), and at Brewster's
    angle (56 degrees from the normal for n = 1.5) only s reflects; diffuse light is not polarised. A filter whose pass
    axis is at angle a to s passes s by cos2 a and p by sin2 a, and half the unpolarised light; with the exposure made
    good (x2), a camera ray's specular is scaled by 2 (Rs cos2 a + Rp sin2 a) / (Rs + Rp), from the Fresnel terms at its
    angle of incidence, and its diffuse is unchanged. Nothing changes head-on (Rs = Rp) or at grazing angles.

    Applied to every Principled BSDF that is not a metal or glass: the coat's weight and the specular level are
    multiplied by the factor for camera rays only, so what the surfaces light and mirror for each other is untouched.
    `angle_deg` is the pass axis in the frame from horizontal: 90 cuts the glare on faces tilted toward or away from the
    camera (a roof slope, a floor, a top), 0 on faces turned to the side."""
    from mathutils import Vector
    m = cam_rot.to_matrix()
    right, up = m @ Vector((1, 0, 0)), m @ Vector((0, 1, 0))
    a = math.cos(math.radians(angle_deg)) * right + math.sin(math.radians(angle_deg)) * up
    ng = bpy.data.node_groups.new('polariser', 'ShaderNodeTree')
    ng.interface.new_socket(name='Factor', in_out='OUTPUT', socket_type='NodeSocketFloat')
    N, L = ng.nodes, ng.links
    def mth(op, x, y=None, clamp=False):
        n = N.new('ShaderNodeMath'); n.operation = op; n.use_clamp = clamp
        for i, v in enumerate((x, y)):
            if v is None:
                continue
            if isinstance(v, (int, float)): n.inputs[i].default_value = v
            else: L.new(v, n.inputs[i])
        return n.outputs['Value']
    def vec(op, x, y=None):
        n = N.new('ShaderNodeVectorMath'); n.operation = op
        for i, v in enumerate((x, y)):
            if v is None:
                continue
            if isinstance(v, Vector): n.inputs[i].default_value = v
            else: L.new(v, n.inputs[i])
        return n.outputs['Value'] if op == 'DOT_PRODUCT' else n.outputs['Vector']
    geo = N.new('ShaderNodeNewGeometry'); lp = N.new('ShaderNodeLightPath')
    nrm, inc = geo.outputs['Normal'], geo.outputs['Incoming']
    c = mth('MINIMUM', mth('ABSOLUTE', vec('DOT_PRODUCT', nrm, inc)), 1.0)
    ct = mth('SQRT', mth('SUBTRACT', 1.0, mth('DIVIDE', mth('SUBTRACT', 1.0, mth('MULTIPLY', c, c)), ior * ior)))
    nct, nc = mth('MULTIPLY', ct, ior), mth('MULTIPLY', c, ior)
    rs = mth('POWER', mth('DIVIDE', mth('SUBTRACT', c, nct), mth('ADD', c, nct)), 2.0)
    rp = mth('POWER', mth('DIVIDE', mth('SUBTRACT', ct, nc), mth('ADD', ct, nc)), 2.0)
    q = mth('POWER', vec('DOT_PRODUCT', vec('NORMALIZE', vec('CROSS_PRODUCT', inc, nrm)), a), 2.0)   # cos2 between s and the pass axis
    num = mth('ADD', mth('MULTIPLY', rs, q), mth('MULTIPLY', rp, mth('SUBTRACT', 1.0, q)))
    fp = mth('DIVIDE', mth('MULTIPLY', num, 2.0), mth('ADD', rs, rp))
    f = mth('ADD', 1.0, mth('MULTIPLY', mth('SUBTRACT', fp, 1.0), strength))
    out = mth('ADD', 1.0, mth('MULTIPLY', mth('SUBTRACT', f, 1.0), lp.outputs['Is Camera Ray']))
    go = N.new('NodeGroupOutput'); L.new(out, go.inputs['Factor'])

    touched = 0
    for mat in bpy.data.materials:
        if not mat.use_nodes or not mat.node_tree:
            continue
        nt = mat.node_tree
        for b in [n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED']:
            I = b.inputs
            if (not I['Metallic'].is_linked and I['Metallic'].default_value > 0.5) or \
               (not I['Transmission Weight'].is_linked and I['Transmission Weight'].default_value > 0.5):
                continue
            g = None
            for k in ('Coat Weight', 'Specular IOR Level'):
                sock = I[k]
                if not sock.is_linked and sock.default_value <= 0:
                    continue
                if g is None:
                    g = nt.nodes.new('ShaderNodeGroup'); g.node_tree = ng
                mul = nt.nodes.new('ShaderNodeMath'); mul.operation = 'MULTIPLY'; mul.use_clamp = (k == 'Coat Weight')
                if sock.is_linked:
                    src = sock.links[0].from_socket; nt.links.remove(sock.links[0]); nt.links.new(src, mul.inputs[0])
                else:
                    mul.inputs[0].default_value = sock.default_value
                nt.links.new(g.outputs['Factor'], mul.inputs[1]); nt.links.new(mul.outputs['Value'], sock)
                touched += 1
    return touched
