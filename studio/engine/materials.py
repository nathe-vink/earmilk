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
    'eucalyptus_bark': dict(palette=[['#E3DACA', 0.26], ['#C7C2B6', 0.22], ['#EDE6D8', 0.12], ['#CFAA98', 0.12], ['#C5B28F', 0.1],
                                     ['#A3AA95', 0.11], ['#B3B6B2', 0.07]],
                            roughness=0.55, patch_m=0.12, stretch=1.9, edge=0.45, mottle=0.07, scale=1.0, bump=0.3),
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
    """A smooth-barked eucalyptus (a spotted or snow gum): the bark sheds in irregular patches, each its own colour from
    the palette (weighted: mostly creams and greys, fewer salmon, ochre and sage), taller than wide (`stretch`), their
    edges wavy (a strong noise bends the plane) and softly blended (smooth Voronoi), a smaller layer of patches over
    the larger in places, a mottle inside each and a faint lip where a newer layer meets the old. World space, metres."""
    node, math_, mix, smooth = _nodes(nt)
    uv, geo = _face_uv(nt, node, math_)
    pos = geo.outputs['Position']
    k = p['scale']
    pm = p['patch_m']

    def warp(vec, scale, amount, seed):
        wn = node('ShaderNodeTexNoise'); wn.inputs['Scale'].default_value = scale * k; wn.inputs['Detail'].default_value = 4.0
        wn.inputs['Roughness'].default_value = 0.55
        ad = node('ShaderNodeVectorMath', operation='ADD'); nt.links.new(pos, ad.inputs[0]); ad.inputs[1].default_value = seed
        nt.links.new(ad.outputs['Vector'], wn.inputs['Vector'])
        cen = node('ShaderNodeVectorMath', operation='SUBTRACT'); nt.links.new(wn.outputs['Color'], cen.inputs[0]); cen.inputs[1].default_value = (0.5, 0.5, 0.5)
        sc = node('ShaderNodeVectorMath', operation='SCALE'); nt.links.new(cen.outputs['Vector'], sc.inputs[0]); sc.inputs['Scale'].default_value = amount
        out = node('ShaderNodeVectorMath', operation='ADD'); nt.links.new(vec, out.inputs[0]); nt.links.new(sc.outputs['Vector'], out.inputs[1])
        return out.outputs['Vector']

    ramp = node('ShaderNodeValToRGB')
    cr = ramp.color_ramp; cr.interpolation = 'CONSTANT'
    pal = [c if isinstance(c, (list, tuple)) else [c, 1.0] for c in p['palette']]       # [colour, share of the bark]
    tot = sum(w for _, w in pal)
    while len(cr.elements) < len(pal):
        cr.elements.new(0.0)
    acc = 0.0
    for el, (hx, w) in zip(cr.elements, pal):
        el.position = acc / tot; el.color = hex_lin(hx); acc += w

    def patches(size, seed):
        """Smooth-F1 cells `size` across (taller by `stretch`): a colour from the ramp each, blended at the edges."""
        v = warp(warp(uv, 3.0 / size * 0.12, 1.1 * size, seed), 1.0 / size * 0.5, 0.35 * size, (seed[1], seed[0], 0.0))
        mp = node('ShaderNodeMapping'); s_ = k / size
        mp.inputs['Scale'].default_value = (s_, s_ / p['stretch'], 1.0)
        nt.links.new(v, mp.inputs['Vector'])
        vo = node('ShaderNodeTexVoronoi', feature='SMOOTH_F1', voronoi_dimensions='2D')
        vo.inputs['Scale'].default_value = 1.0; vo.inputs['Randomness'].default_value = 1.0; vo.inputs['Smoothness'].default_value = 0.25
        nt.links.new(mp.outputs['Vector'], vo.inputs['Vector'])
        sep = node('ShaderNodeSeparateColor'); nt.links.new(vo.outputs['Color'], sep.inputs['Color'])
        rr = node('ShaderNodeValToRGB'); rr.color_ramp.interpolation = 'CONSTANT'
        while len(rr.color_ramp.elements) < len(cr.elements):
            rr.color_ramp.elements.new(0.0)
        for e_src, e_dst in zip(cr.elements, rr.color_ramp.elements):
            e_dst.position = e_src.position; e_dst.color = e_src.color
        nt.links.new(sep.outputs['Red'], rr.inputs['Fac'])
        ed = node('ShaderNodeTexVoronoi', feature='DISTANCE_TO_EDGE', voronoi_dimensions='2D')
        ed.inputs['Scale'].default_value = 1.0; ed.inputs['Randomness'].default_value = 1.0
        nt.links.new(mp.outputs['Vector'], ed.inputs['Vector'])
        return rr.outputs['Color'], sep.outputs['Green'], ed.outputs['Distance']

    c1, g1, e1 = patches(pm, (0.0, 0.0, 0.0))
    c2, g2, e2 = patches(pm * 0.55, (13.7, 5.3, 0.0))
    # the smaller, newer layer over the larger where a slow noise says so
    ln = node('ShaderNodeTexNoise'); ln.inputs['Scale'].default_value = 1.4 / pm * 0.12 * k; ln.inputs['Detail'].default_value = 3.0
    nt.links.new(pos, ln.inputs['Vector'])
    top = smooth(ln.outputs['Fac'], 0.52, 0.56)
    col = mix(top, c1, c2)
    # a mottle inside each patch at two scales, and the faint lip where the layers meet
    def mottle(scale, amount, seed):
        mo = node('ShaderNodeTexNoise'); mo.inputs['Scale'].default_value = scale * k; mo.inputs['Detail'].default_value = 5.0
        ad = node('ShaderNodeVectorMath', operation='ADD'); nt.links.new(pos, ad.inputs[0]); ad.inputs[1].default_value = seed
        nt.links.new(ad.outputs['Vector'], mo.inputs['Vector'])
        mr = node('ShaderNodeMapRange'); nt.links.new(mo.outputs['Fac'], mr.inputs['Value'])
        mr.inputs['To Min'].default_value = 1 - amount; mr.inputs['To Max'].default_value = 1 + amount
        comb = node('ShaderNodeCombineColor')
        for ch in ('Red', 'Green', 'Blue'):
            nt.links.new(mr.outputs['Result'], comb.inputs[ch])
        return comb.outputs['Color'], mo.outputs['Fac']
    m1, f1 = mottle(9.0, p['mottle'], (2.0, 7.0, 1.0))
    m2, _ = mottle(60.0, p['mottle'] * 0.5, (5.0, 1.0, 3.0))
    col = mix(1.0, mix(1.0, col, m1, 'MULTIPLY'), m2, 'MULTIPLY')
    lip = math_('MULTIPLY', math_('SUBTRACT', 1.0, smooth(e2, 0.0, 0.05)), top)
    lip = math_('MAXIMUM', lip, math_('MULTIPLY', math_('SUBTRACT', 1.0, smooth(e1, 0.0, 0.03)), math_('SUBTRACT', 1.0, top)))
    col = mix(math_('MULTIPLY', lip, 0.18 * p['edge']), col, hex_lin('#6E6352'))
    nt.links.new(col, b.inputs['Base Color'])
    b.inputs['Roughness'].default_value = p['roughness']
    # relief: the newer layer's edge stands a little proud of the one under it
    h = math_('ADD', math_('MULTIPLY', lip, p['edge']), math_('MULTIPLY', f1, 0.12))
    bn = node('ShaderNodeBump'); bn.inputs['Strength'].default_value = p['bump']; bn.inputs['Distance'].default_value = 0.0008
    nt.links.new(h, bn.inputs['Height'])
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
