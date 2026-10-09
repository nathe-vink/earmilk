"""The knobs: every setting a shot file exposes, with its unit, range and meaning. The critic prescribes changes in this
vocabulary only (critic/card.py prints it with the shot's current values), and the engine reads nothing else.

A pattern's `*` matches one path segment (a light's or a material's name). Ranges are what a change may set; outside
them the engine still renders, but the card marks the value.
"""
import fnmatch

KNOBS = [
    # pattern, unit, range or choices, meaning
    ('size', 'px [w, h]', None, 'output size'),
    # camera
    ('camera.position', 'm [x, y, z]', None, 'camera position; the product stands at the origin, its front toward -y, z up'),
    ('camera.target', 'm [x, y, z]', None, 'the point the camera aims at'),
    ('camera.lens_mm', 'mm', (14, 300), 'focal length on a 36 mm sensor (50 normal, 85 to 135 product portrait)'),
    ('camera.level', 'bool', None, 'true: the camera looks level and lens shift frames the target, so verticals stay vertical'),
    ('camera.shift_x', 'frame widths', (-0.5, 0.5), 'extra horizontal lens shift (composition), after any level shift'),
    ('camera.shift_y', 'frame heights', (-0.5, 0.5), 'extra vertical lens shift'),
    ('camera.roll_deg', 'deg', (-10, 10), 'roll about the view axis'),
    ('camera.fstop', 'f-number', (0, 32), 'depth of field; 0 for none (all sharp)'),
    ('camera.focus', 'm [x, y, z] or "target"', None, 'the plane of focus passes through this point'),
    ('camera.polariser.strength', '0 to 1', (0, 1), 'a polarising filter on the lens: 1 removes the glare a dielectric (the lacquer, a plastic, a waxed floor) reflects across the pass axis, completely at Brewster\'s angle (56 degrees off the surface\'s normal), not at all head-on or at grazing angles; colour under the glare comes back, highlights there dim with it; exposure is made good'),
    ('camera.polariser.angle_deg', 'deg', (0, 180), 'the filter\'s pass axis in the frame, from horizontal: 90 cuts the glare on faces tilted toward or away from the camera (a roof slope, a floor, a top), 0 on faces turned to the side (a side face, a plinth\'s side); one angle cannot clear both'),
    # exposure and colour
    ('render.exposure', 'EV', (-5, 5), 'exposure; +1 doubles every pixel\'s light'),
    ('render.view', 'choice', ('Khronos PBR Neutral', 'AgX', 'Filmic', 'Standard'), 'view transform (tone mapping)'),
    ('render.look', 'choice', None, 'the view transform\'s look (AgX: "AgX - Base Contrast", "AgX - Punchy", ...)'),
    ('render.white_balance_k', 'K', (2500, 12000), 'the white point: the colour temperature that renders neutral'),
    ('render.white_balance_tint', 'tint', (-50, 50), 'the white point\'s tint: 10 is neutral daylight; lower turns the image greener (takes out magenta: 02b\'s pink white went from dE 10.7 at 16 to 4.6 at 1.9 against warm white), higher more magenta'),
    ('render.samples', 'samples', (16, 4096), 'path samples per pixel'),
    ('render.adaptive', 'noise threshold', (0, 0.1), 'adaptive sampling; 0 samples every pixel fully'),
    ('render.clamp', 'radiance', (0, 100), 'indirect clamp against fireflies; 0 for none'),
    ('render.bounces', 'count', (4, 32), 'light bounces'),
    ('render.denoise', 'bool', None, 'OpenImageDenoise'),
    # sun and sky
    ('sun.azimuth_deg', 'deg', (-180, 180), 'compass direction the sun shines FROM, 0 = from in front of the product (-y), +90 = from +x'),
    ('sun.elevation_deg', 'deg', (0, 90), 'the sun\'s height above the horizon'),
    ('sun.irradiance', 'W/m2', (0, 1000), 'the sun\'s strength on a surface facing it (clear midday about 1000; 1 to 10 reads well in Cycles units here)'),
    ('sun.angle_deg', 'deg', (0.1, 10), 'the sun\'s angular diameter: 0.53 is the real sun, larger softens shadow edges'),
    ('sun.color', 'K or hex', None, 'colour temperature (3000 golden hour, 5500 midday) or an sRGB hex'),
    ('sun.aim', '{at: [x, y, z], window: index, through: [u, v]}', None, 'room: place the sun by where its light lands: the azimuth and elevation that send it through window `window` at (u across its width, v up from its sill; 0.5, 0.5 its centre) onto the point `at` (replaces azimuth_deg and elevation_deg)'),
    ('sun.aim.at', 'm [x, y, z]', None, 'where the sun\'s light should land (e.g. the product\'s front)'),
    ('sun.aim.through', '[u, v] 0 to 1', None, 'the point of the window the light passes through'),
    ('sky.kind', 'choice', ('gradient', 'physical', 'hdri', 'none'), 'the world: a gradient dome, a physical sky matched to the sun, a photographed environment (hdri), or black'),
    ('sky.file', 'choice', ('studio_small_03_1k', 'lebombo_1k', 'st_fagans_interior_1k', 'empty_warehouse_01_1k'),
     'hdri: the environment (studio/assets/hdri, Poly Haven CC0): a small photo studio with softboxes; a sunlit apartment; a museum interior with windows; an empty warehouse'),
    ('sky.rotation_deg', 'deg', (0, 360), 'hdri: turns the environment about the vertical, so its brightest part (a window, a softbox) faces where it should'),
    ('sky.strength', 'x', (0, 20), 'the sky\'s brightness'),
    ('sky.zenith', 'hex', None, 'gradient sky: colour overhead'),
    ('sky.horizon', 'hex', None, 'gradient sky: colour at the horizon'),
    ('sky.ground', 'hex', None, 'gradient sky: colour below the horizon'),
    ('sky.visible', 'bool', None, 'whether the camera sees the sky (false keeps its light, hides it)'),
    # lights
    ('lights.*.type', 'choice', ('area', 'spot', 'point', 'panel', 'flag'), 'kind of lamp; a panel is a graduated emissive rectangle the camera cannot see, mirrored by gloss as a smooth ramp; a flag is a matte black plane the camera cannot see that shades what lies behind it from each lamp (a light colour makes it a bounce card)'),
    ('lights.*.strength', 'radiance', (0, 200), 'panel: peak radiance (white at 1 reads scene-linear 1.0 head-on; a clear coat mirrors about 0.05 of it)'),
    ('lights.*.ramp', '{axis, at_m: [a, b], values: [va, vb]}', None, 'panel: strength fraction va at world coordinate a along axis ("x", "y", "z" or a vector), vb at b, linear between'),
    ('lights.*.shape', 'choice', ('RECTANGLE', 'ELLIPSE', 'DISK', 'SQUARE'), 'area lamp shape'),
    ('lights.*.size_m', 'm [w, h]', None, 'area lamp size: a softbox 0.6 to 1.5, a strip 0.2 x 1.5'),
    ('lights.*.position', 'm [x, y, z]', None, 'placed explicitly (else by orbit)'),
    ('lights.*.orbit', '{azimuth_deg, elevation_deg, distance_m}', None, 'placed round the product\'s centre (not round the target): azimuth from its front (-y), + toward +x; use position for a lamp anywhere else'),
    ('lights.*.orbit.azimuth_deg', 'deg', (-180, 180), 'see orbit'),
    ('lights.*.orbit.elevation_deg', 'deg', (-30, 90), 'see orbit'),
    ('lights.*.orbit.distance_m', 'm', (0.2, 20), 'see orbit'),
    ('lights.*.target', 'm [x, y, z]', None, 'the point the lamp faces (default the product\'s centre)'),
    ('lights.*.receivers', '[part names, * wildcards]', None, 'light linking: the lamp lights only these parts (a kick for a face that must not light the floor beside it); absent, it lights everything'),
    ('lights.*.power_w', 'W', (0, 50000), 'lamp power (Cycles watts); light on the subject falls with distance squared'),
    ('lights.*.irradiance', 'W/m2', (0, 50), 'area lamp: the light it puts on a surface facing it at its target (replaces power_w; about 3 renders a white near 230 at exposure 0)'),
    ('lights.*.color', 'K or hex', None, 'colour temperature or sRGB hex'),
    ('lights.*.spread_deg', 'deg', (1, 180), 'area lamp beam spread: 180 a bare softbox, 30 to 60 a gridded one'),
    ('lights.*.camera', 'bool', None, 'whether the lamp\'s face is visible to the camera'),
    ('lights.*.diffuse', '0 to 1', (0, 1), 'the lamp\'s share in diffuse light'),
    ('lights.*.specular', '0 to 1', (0, 1), 'the lamp\'s share in reflections (0: lights without a highlight; with diffuse 0: a glint only)'),
    ('lights.*.portal', 'bool', None, 'a window portal: guides the sky\'s light through an opening, adds none'),
    ('glints.*.distance_m', 'm', (0.05, 3), 'how far along the mirror ray the glint\'s lamp sits (0.6 by default); nearer keeps it clear of a floor or wall the ray meets'),
    ('glints.*.occlusion_ignore', 'list of part names (prefixes)', None, 'parts left out of the test for whether anything hides the lamp from the glint (a hit within 2 mm, or on a face seen from behind, is already taken as the surface itself)'),
    ('glints.*.size_m', 'm', (0.005, 1), 'the glint lamp\'s diameter: larger is a softer, wider highlight'),
    ('glints.*.power_w', 'W', (0, 200), 'the glint lamp\'s power'),
    # set
    ('set.kind', 'choice', ('room', 'sweep', 'none'), 'what surrounds the product'),
    ('set.*', 'see the set\'s own keys', None, 'room: floor, walls, window, skirting, props; sweep: color, radius, depth, width'),
    ('set.color', 'hex', None, 'sweep: its colour (the paper\'s)'),
    ('set.width', 'm', (2, 30), 'sweep: width across'),
    ('set.front', 'm', (1, 30), 'sweep: floor in front of the product'),
    ('set.depth', 'm', (0.3, 10), 'sweep: floor behind the product, to the start of the curve'),
    ('set.radius', 'm', (0.1, 4), 'sweep: the curve\'s radius (larger: a softer horizon)'),
    ('set.contact.strength', '0 to 0.8', (0, 0.8), 'sweep: a contact shadow where something stands on it, its colour multiplied down to 1 - strength in a corner (ambient occlusion); 0 off'),
    ('set.contact.distance_m', 'm', (0.005, 0.3), 'sweep: how far the contact shadow reaches from what stands on it (0.05: a few centimetres)'),
    ('set.height', 'm', (1, 10), 'sweep: the back wall\'s height'),
    ('set.size', 'm [w, d, h]', None, 'room: width (x), depth (y), height'),
    ('set.center', 'm [x, y]', None, 'room: the floor\'s centre'),
    ('set.floor.*', 'see materials oak', None, 'room: the floor\'s material overrides'),
    ('set.wall.*', 'see materials plaster', None, 'room: the walls\' material overrides'),
    ('set.windows.*.wall', 'choice', ('left', 'right', 'back', 'front'), 'room: which wall the window is in'),
    ('set.windows.*.along', 'm', (-5, 5), 'room: the window\'s centre from the wall\'s centre, positive the way the wall runs: back wall toward +x, front wall toward -x, left wall toward +y (to the back), right wall toward -y (to the front)'),
    ('set.windows.*.sill', 'm', (0, 2), 'room: sill height'),
    ('set.windows.*.size', 'm [w, h]', None, 'room: opening size'),
    ('set.windows.*.mullions', '[cols, rows]', None, 'room: glazing bars'),
    ('set.skirting.h', 'm', (0, 0.3), 'room: skirting height'),
    ('set.wainscot.height', 'm', (0.5, 1.5), 'room: the panelling\'s height, to the top of its rail'),
    ('set.wainscot.color', 'hex', None, 'room: the panelling\'s paint'),
    ('set.wainscot.panel_w', 'm', (0.3, 6), 'room: the raised panels\' width (the joints between them fall where it puts them)'),
    ('set.wainscot.roughness', '0 to 1', (0.2, 0.9), 'room: the panelling\'s paint sheen: 0.38 satin mirrors a lamp as a soft halo, 0.7 eggshell blurs it into the shade'),
    ('set.props.*.position', 'm [x, y]', None, 'room: a prop\'s place on the floor'),
    ('set.props.*.kind', 'choice', ('rug', 'table', 'books', 'sideboard', 'vase', 'lamp', 'sofa', 'curtain', 'frame'), 'room: what the prop is'),
    ('set.props.*.size', 'm [w, d] or [w, d, h]', None, 'room: a prop\'s size (a rug [w, d]; a table, sideboard or sofa [w, d, h]; a curtain or frame [w, h])'),
    ('set.props.*.color', 'hex', None, 'room: a prop\'s colour'),
    ('set.props.*.off', 'true/false', None, 'room: take the prop out of the set'),
    ('set.flags', 'list of {center_m: [x, y, z], size_m: [w, h], normal: [x, y, z]}', None, 'black cards the camera cannot see: they cast shadows (a flag to cut sun off a wall) and soak up bounce light; out of reflections unless "glossy": true; with "reflect_only": true, seen only in reflections (no shadow, no bounce), "color" its shade, and one-sided ("one_sided", true by default for these): seen only from the side its normal faces, so a card on the floor shows in the product\'s lacquer and not in the floor\'s own gloss'),
    ('set.bounces', 'list of {center_m, size_m, normal}', None, 'white cards the camera cannot see: bounce fill, and seen in reflections'),
    ('set.props.*.rotate_z', 'deg', (-180, 180), 'room: a prop\'s turn'),
    ('set.props.*.artwork', '{bands: [[hex, share], ...], ground: hex, seed: n}', None, 'frame: a colour-field painting in the print (bands top to bottom, soft-edged, canvas grain) instead of the flat art colour'),
    ('set.props.*.z', 'm', (0.3, 3), 'frame: the print\'s centre height'),
    # product
    ('product.flavour', 'choice', ('whole', 'two', 'skim', 'matcha', 'chocolate', 'oat'), 'colourway (fixed colours per flavour)'),
    ('product.instances', 'list of {position, rotate_z}', None, 'copies of the product: position m, rotation deg about z'),
    ('product.normals_refine', 'true/false', None, 'the waveguide\'s facets refined onto its true surface (true); false for a frame where the waveguides are a few dozen pixels across, where it only costs memory'),
    ('product.instances.*.position', 'm [x, y, z]', None, 'where this copy stands: x and y on the floor; z is its base\'s height (0 on the floor, the top of the furniture it stands on)'),
    ('product.instances.*.rotate_z', 'deg', (-360, 360), 'its turn about z: 0 faces -y; + turns its front toward +x'),
    ('products.*.instances.*.position', 'm [x, y, z]', None, 'where this copy stands: x and y on the floor; z is its base\'s height (0 on the floor, the top of the furniture it stands on)'),
    ('products.*.instances.*.rotate_z', 'deg', (-360, 360), 'its turn about z: 0 faces -y; + turns its front toward +x'),
    ('product.explode.*.offset_m', 'm [x, y, z]', None, 'how far the matched parts are drawn out along their own fixing axis: change the length, keep the direction'),
    # materials
    ('materials.*.*', 'see the preset', None, 'material preset overrides (studio/engine/materials.py PRESET_DEFAULTS)'),
]

PRESET_UNITS = {
    'coat_roughness': ('0 to 1', (0.0, 0.6), 'the clear coat\'s roughness: 0.03 mirror, 0.08 polished, 0.2 satin'),
    'peel': ('bump', (0.0, 0.05), 'orange peel in the clear'),
    'albedo': ('0 to 1', (0.5, 0.95), 'the colour coat\'s reflectance scale (a white lacquer is about 0.85)'),
    'roughness': ('0 to 1', (0.0, 1.0), 'surface roughness'),
    'color': ('hex', None, 'sRGB colour'),
}


def describe(path):
    """(unit, range, meaning) for a path, or None if no pattern covers it."""
    best = None
    for pat, unit, rng, meaning in KNOBS:
        if fnmatch.fnmatchcase(path, pat) and (best is None or len(pat) > len(best[0])):
            best = (pat, unit, rng, meaning)
    if path.startswith('materials.'):
        leaf = path.split('.')[-1]
        if leaf in PRESET_UNITS:
            u, r, m = PRESET_UNITS[leaf]
            return u, r, m
    return best[1:] if best else None


def in_range(value, rng):
    if rng is None:
        return True
    if isinstance(rng, tuple) and len(rng) == 2 and all(isinstance(v, (int, float)) for v in rng):
        return isinstance(value, (int, float)) and rng[0] <= value <= rng[1]
    return value in rng
