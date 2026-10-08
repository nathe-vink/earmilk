"""Light for the engine: the sun, the sky, area lamps placed by orbit or by position, window portals and glints.

Units are Cycles' own. A sun's strength is an irradiance (W/m2 on a surface facing it); an area lamp's power is in
watts, so the light it puts on the subject falls with the square of its distance; the sky is a radiance multiplier.
Colours are a temperature in kelvin (Blender's own blackbody, so 3000 is golden-hour amber and 6500 neutral) or an sRGB
hex.

A glint is a small area lamp placed where a curved surface would mirror it into the camera (R = 2(N.V)N - V), with no
diffuse share and invisible to the camera: a highlight on an edge or a rim exactly where it should be, lighting
nothing else. `receivers` limits it to some parts (light linking).
"""
import math

from mathutils import Vector


def _hex_lin(h):
    h = h.lstrip('#'); c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in c)


def set_color(light, spec):
    """spec: kelvin (number) or sRGB hex."""
    if spec is None:
        return
    if isinstance(spec, (int, float)):
        light.use_temperature = True; light.temperature = float(spec); light.color = (1, 1, 1)
    else:
        light.use_temperature = False; light.color = _hex_lin(spec)


def orbit_point(orbit, centre):
    az, el = math.radians(orbit.get('azimuth_deg', 0)), math.radians(orbit.get('elevation_deg', 30))
    d = orbit.get('distance_m', 2.0)
    # azimuth 0 is in front of the product (-y), +90 toward +x
    return Vector(centre) + d * Vector((math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el)))


def aim(obj, target):
    d = Vector(target) - obj.location
    obj.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()


def _visibility(obj, camera=False):
    obj.visible_camera = bool(camera)


def area(bpy, name, spec, centre):
    """An area lamp from a shot's `lights.NAME` entry."""
    L = bpy.data.lights.new(name, 'AREA')
    L.shape = spec.get('shape', 'RECTANGLE')
    size = spec.get('size_m', [1.0, 1.0])
    if isinstance(size, (int, float)): size = [size, size]
    L.size = size[0]; L.size_y = size[1]
    L.spread = math.radians(spec.get('spread_deg', 180))
    L.diffuse_factor = spec.get('diffuse', 1.0); L.specular_factor = spec.get('specular', 1.0)
    set_color(L, spec.get('color', 5600))
    if spec.get('portal'):
        L.cycles.is_portal = True
    ob = bpy.data.objects.new(name, L); bpy.context.scene.collection.objects.link(ob)
    if 'position' in spec:
        ob.location = Vector(spec['position'])
    else:
        ob.location = orbit_point(spec.get('orbit', {}), centre)
    target = Vector(spec.get('target', centre))
    aim(ob, target)
    L.energy = area_power(spec, (target - ob.location).length)
    if spec.get('roll_deg'):
        ob.rotation_euler.rotate_axis('Z', math.radians(spec['roll_deg']))
    _visibility(ob, spec.get('camera', False))
    return ob


def area_power(spec, distance):
    """An area lamp's watts from `power_w`, or from `irradiance` (W/m2 on a surface facing it at its target): a
    Lambertian emitter of power P has an on-axis intensity of P / pi, so E = P / (pi d^2). About 3 W/m2 renders a white
    lacquer (albedo 0.85) near 230 of 255 at exposure 0 under the neutral view."""
    if 'irradiance' in spec:
        return spec['irradiance'] * math.pi * distance ** 2
    return spec.get('power_w', 100.0)


def spot(bpy, name, spec, centre):
    L = bpy.data.lights.new(name, 'SPOT')
    L.energy = spec.get('power_w', 100.0); L.spot_size = math.radians(spec.get('cone_deg', 40))
    L.spot_blend = spec.get('blend', 0.3); L.shadow_soft_size = spec.get('radius_m', 0.05)
    L.diffuse_factor = spec.get('diffuse', 1.0); L.specular_factor = spec.get('specular', 1.0)
    set_color(L, spec.get('color', 5600))
    ob = bpy.data.objects.new(name, L); bpy.context.scene.collection.objects.link(ob)
    ob.location = Vector(spec['position']) if 'position' in spec else orbit_point(spec.get('orbit', {}), centre)
    aim(ob, spec.get('target', centre))
    return ob


def point(bpy, name, spec, centre):
    L = bpy.data.lights.new(name, 'POINT')
    L.energy = spec.get('power_w', 50.0); L.shadow_soft_size = spec.get('radius_m', 0.05)
    L.diffuse_factor = spec.get('diffuse', 1.0); L.specular_factor = spec.get('specular', 1.0)
    set_color(L, spec.get('color', 3000))
    ob = bpy.data.objects.new(name, L); bpy.context.scene.collection.objects.link(ob)
    ob.location = Vector(spec['position']) if 'position' in spec else orbit_point(spec.get('orbit', {}), centre)
    return ob


def sun_direction(spec):
    """Unit vector FROM the scene TOWARD the sun."""
    az, el = math.radians(spec.get('azimuth_deg', 0)), math.radians(spec.get('elevation_deg', 30))
    return Vector((math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el)))


def sun(bpy, spec):
    L = bpy.data.lights.new('sun', 'SUN')
    L.energy = spec.get('irradiance', 3.0)
    L.angle = math.radians(spec.get('angle_deg', 0.53))
    set_color(L, spec.get('color', 5200))
    ob = bpy.data.objects.new('sun', L); bpy.context.scene.collection.objects.link(ob)
    d = sun_direction(spec)
    ob.rotation_euler = (-d).to_track_quat('-Z', 'Y').to_euler()   # a sun lamp shines along its -Z
    return ob


def world(bpy, sky, sun_spec=None):
    """The world: a gradient dome (zenith, horizon, ground), a physical sky matched to the sun, or black."""
    W = bpy.data.worlds.new('world'); bpy.context.scene.world = W
    W.use_nodes = True; nt = W.node_tree; nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputWorld'); bg = nt.nodes.new('ShaderNodeBackground')
    nt.links.new(bg.outputs['Background'], out.inputs['Surface'])
    kind = (sky or {}).get('kind', 'gradient'); strength = (sky or {}).get('strength', 1.0)
    bg.inputs['Strength'].default_value = strength
    if kind == 'none':
        bg.inputs['Color'].default_value = (0, 0, 0, 1)
    elif kind == 'physical':
        tx = nt.nodes.new('ShaderNodeTexSky'); tx.sky_type = 'MULTIPLE_SCATTERING'; tx.sun_disc = False
        s = sun_spec or {}
        tx.sun_elevation = math.radians(s.get('elevation_deg', 30))
        # the sky's sun rotation is checked against the sun lamp in the engine's tests (sun.azimuth_deg 0: from -y)
        tx.sun_rotation = math.radians(180 - s.get('azimuth_deg', 0))
        tx.air_density = sky.get('air', 1.0); tx.aerosol_density = sky.get('dust', 1.0)
        nt.links.new(tx.outputs['Color'], bg.inputs['Color'])
    else:
        # gradient on the view direction's z: ground below the horizon, horizon to zenith above
        tc = nt.nodes.new('ShaderNodeTexCoord'); sep = nt.nodes.new('ShaderNodeSeparateXYZ')
        nt.links.new(tc.outputs['Generated'], sep.inputs['Vector'])
        ramp = nt.nodes.new('ShaderNodeValToRGB'); cr = ramp.color_ramp
        cr.elements[0].position = 0.0; cr.elements[0].color = (*_hex_lin(sky.get('ground', '#5A5650')), 1)
        cr.elements[1].position = 1.0; cr.elements[1].color = (*_hex_lin(sky.get('zenith', '#9DB6D8')), 1)
        e = cr.elements.new(0.5); e.color = (*_hex_lin(sky.get('horizon', '#DCE3EA')), 1)
        e2 = cr.elements.new(0.49); e2.color = (*_hex_lin(sky.get('ground', '#5A5650')), 1)
        # on the world, Generated is the ray's direction: z runs -1 (straight down) to 1 (overhead); map it to 0..1
        mr = nt.nodes.new('ShaderNodeMapRange'); mr.inputs['From Min'].default_value = -1.0; mr.inputs['From Max'].default_value = 1.0
        nt.links.new(sep.outputs['Z'], mr.inputs['Value'])
        nt.links.new(mr.outputs['Result'], ramp.inputs['Fac']); nt.links.new(ramp.outputs['Color'], bg.inputs['Color'])
    if sky and sky.get('visible') is False:
        # light from the sky, but the camera sees a neutral colour instead
        lp = nt.nodes.new('ShaderNodeLightPath'); mix = nt.nodes.new('ShaderNodeMixShader'); bg2 = nt.nodes.new('ShaderNodeBackground')
        bg2.inputs['Color'].default_value = (*_hex_lin(sky.get('backdrop', '#808080')), 1)
        nt.links.remove(bg.outputs['Background'].links[0])
        nt.links.new(lp.outputs['Is Camera Ray'], mix.inputs['Fac'])
        nt.links.new(bg.outputs['Background'], mix.inputs[1]); nt.links.new(bg2.outputs['Background'], mix.inputs[2])
        nt.links.new(mix.outputs['Shader'], out.inputs['Surface'])
    return W


def glint(bpy, name, spec, cam_pos):
    """A specular-only lamp where the surface at `at` with normal `normal` mirrors it into the camera."""
    P = Vector(spec['at']); N = Vector(spec['normal']).normalized()
    V = (Vector(cam_pos) - P).normalized()
    R = 2 * N.dot(V) * N - V
    L = bpy.data.lights.new(name, 'AREA'); L.shape = 'DISK'
    L.size = spec.get('size_m', 0.05); L.energy = spec.get('power_w', 2.0)
    L.diffuse_factor = 0.0; L.specular_factor = 1.0
    set_color(L, spec.get('color', 6000))
    ob = bpy.data.objects.new(name, L); bpy.context.scene.collection.objects.link(ob)
    ob.location = P + R * spec.get('distance_m', 0.6)
    aim(ob, P)
    ob.visible_camera = False
    return ob


def link_receivers(bpy, light_ob, objects):
    """Light linking: the lamp lights only `objects`."""
    col = bpy.data.collections.new(light_ob.name + '-receivers')
    for o in objects:
        col.objects.link(o)
    light_ob.light_linking.receiver_collection = col
