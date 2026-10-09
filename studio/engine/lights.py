"""Light for the engine: the sun, the sky, area lamps placed by orbit or by position, window portals and glints.

Units are Cycles' own. A sun's strength is an irradiance (W/m2 on a surface facing it); an area lamp's power is in
watts, so the light it puts on the subject falls with the square of its distance; the sky is a radiance multiplier.
Colours are a temperature in kelvin (Blender's own blackbody, so 3000 is golden-hour amber and 6500 neutral) or an sRGB
hex.

A panel is a graduated light: an emissive rectangle the camera cannot see, lighting from one side, its brightness ramped
along a world axis (a softbox behind a graduated scrim). A gloss surface mirrors it as a smooth ramp of light instead of
one flat patch, the way a lacquered roof or a car's bonnet is lit in a studio.

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


def panel(bpy, name, spec, centre):
    """A graduated panel from a shot's `lights.NAME` entry with type "panel":
    size_m [w, h], position (or orbit) and target as an area lamp's; `strength`, the peak radiance (a white panel of
    strength 1 reads scene-linear 1.0 seen head-on, its mirror image in a clear coat about 0.05 of that); `ramp`
    {"axis": "x"|"y"|"z" or [x, y, z] (world), "at_m": [a, b, ...], "values": [va, vb, ...]}: the strength's fraction
    is va where the world coordinate along the axis is a, vb where it is b, and so on, linear between the stops and
    held beyond them; without a ramp the panel is even. `diffuse` false: seen only in reflections (a reflector card), lighting nothing diffusely.
    The panel's face looks at its target; its back emits nothing; it casts no shadow."""
    import bmesh
    w, h = spec.get('size_m', [1.0, 0.25])
    me = bpy.data.meshes.new(name)
    # vertices clockwise seen from +z, so the face's normal is local -z: the direction aim() turns toward the target
    me.from_pydata([(-w / 2, -h / 2, 0), (-w / 2, h / 2, 0), (w / 2, h / 2, 0), (w / 2, -h / 2, 0)], [], [(0, 1, 2, 3)])
    me.update()
    ob = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(ob)
    ob.location = Vector(spec['position']) if 'position' in spec else orbit_point(spec.get('orbit', {}), centre)
    target = Vector(spec.get('target', centre))
    d = target - ob.location
    # a panel facing straight up or down has no up direction to keep; it then keeps world +y as its local +y
    up = 'Y' if abs(d.normalized().z) < 0.999 else None
    if up:
        aim(ob, target)
    else:
        from mathutils import Matrix
        z = -d.normalized(); y = Vector((0, 1, 0)); x = y.cross(z)
        ob.rotation_euler = Matrix((x, y, z)).transposed().to_euler()
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial'); em = nt.nodes.new('ShaderNodeEmission')
    col = spec.get('color', 5600)
    if isinstance(col, (int, float)):
        bb = nt.nodes.new('ShaderNodeBlackbody'); bb.inputs['Temperature'].default_value = float(col)
        nt.links.new(bb.outputs['Color'], em.inputs['Color'])
    else:
        em.inputs['Color'].default_value = (*_hex_lin(col), 1)
    peak = float(spec.get('strength', 1.0))
    ramp = spec.get('ramp')
    if ramp:
        ax = ramp.get('axis', 'y')
        ax = {'x': (1, 0, 0), 'y': (0, 1, 0), 'z': (0, 0, 1)}[ax] if isinstance(ax, str) else ax
        geo = nt.nodes.new('ShaderNodeNewGeometry'); dot = nt.nodes.new('ShaderNodeVectorMath'); dot.operation = 'DOT_PRODUCT'
        dot.inputs[1].default_value = Vector(ax).normalized()
        nt.links.new(geo.outputs['Position'], dot.inputs[0])
        at = ramp.get('at_m', [-h / 2, h / 2]); vals = ramp.get('values', [0.0, 1.0])
        if len(at) == 2:
            mr = nt.nodes.new('ShaderNodeMapRange'); mr.clamp = True
            mr.inputs['From Min'].default_value = at[0]; mr.inputs['From Max'].default_value = at[1]
            mr.inputs['To Min'].default_value = vals[0] * peak; mr.inputs['To Max'].default_value = vals[1] * peak
            nt.links.new(dot.outputs['Value'], mr.inputs['Value']); nt.links.new(mr.outputs['Result'], em.inputs['Strength'])
        else:
            # several stops: the coordinate mapped onto 0..1 across them, a linear colour ramp of the values (as greys)
            lo, hi = min(at), max(at)
            mr = nt.nodes.new('ShaderNodeMapRange'); mr.clamp = True
            mr.inputs['From Min'].default_value = lo; mr.inputs['From Max'].default_value = hi
            nt.links.new(dot.outputs['Value'], mr.inputs['Value'])
            cr_ = nt.nodes.new('ShaderNodeValToRGB'); cr = cr_.color_ramp; cr.interpolation = 'LINEAR'
            stops = sorted(zip(at, vals))
            els = list(cr.elements)
            while len(els) < len(stops):
                els.append(cr.elements.new(0.5))
            for e, (x, v) in zip(cr.elements, stops):
                e.position = (x - lo) / (hi - lo); e.color = (v, v, v, 1.0)
            bw = nt.nodes.new('ShaderNodeRGBToBW'); mul = nt.nodes.new('ShaderNodeMath'); mul.operation = 'MULTIPLY'
            mul.inputs[1].default_value = peak
            nt.links.new(mr.outputs['Result'], cr_.inputs['Fac']); nt.links.new(cr_.outputs['Color'], bw.inputs['Color'])
            nt.links.new(bw.outputs['Val'], mul.inputs[0]); nt.links.new(mul.outputs['Value'], em.inputs['Strength'])
    else:
        em.inputs['Strength'].default_value = peak
    # one-sided: the back face is transparent
    gm = nt.nodes.new('ShaderNodeNewGeometry'); tr = nt.nodes.new('ShaderNodeBsdfTransparent'); mix = nt.nodes.new('ShaderNodeMixShader')
    nt.links.new(gm.outputs['Backfacing'], mix.inputs['Fac'])
    nt.links.new(em.outputs['Emission'], mix.inputs[1]); nt.links.new(tr.outputs['BSDF'], mix.inputs[2])
    nt.links.new(mix.outputs['Shader'], out.inputs['Surface'])
    me.materials.append(m)
    ob.visible_camera = bool(spec.get('camera', False)); ob.visible_shadow = False
    ob.visible_diffuse = bool(spec.get('diffuse', True)); ob.visible_glossy = bool(spec.get('specular', True))
    ob['engine_light'] = True
    return ob


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


def true_glint(bpy, spec, receivers, cam_pos, ray_m=0.05, snap_m=0.03, agree_deg=60):
    """A glint as the surface really is. Its `at` is moved onto the surface the critic pointed at and its normal
    replaced by that surface's own, so the lamp sits exactly where the surface mirrors it into the camera. The
    surface is, in order: the receiving part the camera's ray through `at` hits within ray_m of it; else the nearest
    receiving surface within snap_m that faces the camera and is within agree_deg of the normal given (a lip seen
    beside a hole); else whatever the camera's ray hits within ray_m (the orientation of the surface there).
    A glint whose lamp would be hidden from its point (behind the floor, inside the product) cannot exist: it is
    skipped, with the reason (what the surface mirrors into the camera instead). Returns (spec, note)."""
    from mathutils.bvhtree import BVHTree
    dg = bpy.context.evaluated_depsgraph_get(); scene = bpy.context.scene
    P0 = Vector(spec['at']); C = Vector(cam_pos); given = Vector(spec['normal']).normalized()
    names = {o.name for o in receivers}
    ignore = tuple(spec.get('occlusion_ignore', []))
    def cast(origin, d, dist, occluding=False):
        # occluding: the test for whether anything hides the lamp from the glint's point. A hit within 2 mm of where the
        # ray starts, or on a face seen from behind (the ray starting inside a solid that overlaps the surface, as a
        # connector's bezel sunk in its module), is the surface itself, not something in the way; so is a part named in
        # the glint's occlusion_ignore.
        start = origin
        hit, loc, nrm, _, hob, _ = scene.ray_cast(dg, origin, d, distance=dist)
        def skip(hit, loc, nrm, hob):
            if not hit or hob is None:
                return False
            if hob.get('engine_light') or hob.hide_render:
                return True
            return occluding and ((loc - start).length < 0.002 or nrm.dot(d) > 0 or (ignore and hob.name.startswith(ignore)))
        while skip(hit, loc, nrm, hob):
            dist -= (loc - origin).length + 1e-4; origin = loc + d * 1e-4
            if dist <= 0:
                return False, loc, nrm, None
            hit, loc, nrm, _, hob, _ = scene.ray_cast(dg, origin, d, distance=dist)
        return hit, loc, nrm, hob
    def facing(n, loc):
        return n if n.dot(C - loc) >= 0 else -n
    found, nearest = None, None
    hit, hloc, hnrm, hob = cast(C, (P0 - C).normalized(), (P0 - C).length + 1.0)
    seen = hit and (hloc - P0).length <= ray_m
    if seen and hob.name in names:
        found = (hloc, facing(hnrm, hloc), f'seen surface ({hob.name})')
    else:
        for o in receivers:
            if o.type != 'MESH':
                continue
            M = o.matrix_world; Mi = M.inverted()
            h = BVHTree.FromObject(o, dg).find_nearest(Mi @ P0)
            if h[0] is None:
                continue
            l, n = M @ h[0], (Mi.transposed().to_3x3() @ h[1]).normalized()
            dd = (l - P0).length
            if nearest is None or dd < nearest[0]:
                nearest = (dd, o.name)
            if n.dot(C - l) > 0 and math.degrees(n.angle(given)) <= agree_deg and dd <= snap_m and \
                    (found is None or dd < (found[0] - P0).length):
                found = (l, n, f'nearest facing surface ({o.name})')
        if found is None and seen:
            found = (hloc, facing(hnrm, hloc), f'seen surface ({hob.name}), not a receiver')
    spec = dict(spec)
    if found:
        loc, nrm, how = found
        note = {'on': how, 'moved_mm': round((loc - P0).length * 1000, 1),
                'normal_off_deg': round(math.degrees(given.angle(nrm)), 1)}
        spec['at'] = list(loc); spec['normal'] = list(nrm)
    else:
        note = {'on': 'no surface found; as given' + (f' (the nearest receiving surface, {nearest[1]}, is {nearest[0] * 1000:.0f} mm '
                                                      f'from `at`)' if nearest else '')}
    P = Vector(spec['at']); N = Vector(spec['normal']).normalized()
    V = (C - P).normalized(); R = 2 * N.dot(V) * N - V
    dist = spec.get('distance_m', 0.6)
    hit, loc, _, hob = cast(P + N * 1e-3, R, dist, occluding=True)
    if hit:
        note['skipped'] = (f'the surface there mirrors {hob.name} into the camera ({(loc - P).length:.2f} m away along '
                           f'the mirror direction), so no lamp can sit there')
    return spec, note


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
