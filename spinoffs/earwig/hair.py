"""earwig's wig: grows a bob on the case's lid for studio/pathtrace.py. A "python" object in shots.json:

    {"type": "python", "file": "hair.py", "args": {"w": 62, "d": 26, "h": 48, "r": 10, "split_z": 29.76, ...}}

Roots are scattered on the lid's crown (its top and the upper half of its rounded edges). Each strand is combed away
from a centre part, follows the lid at its own small height (that spread is the wig's volume), falls over the edges
under gravity, and is cut level a little below the lid's split, the way a bob is cut. Vectorised in numpy: 30,000
strands grow in about two seconds. Rendered as Cycles curves with the Principled Hair BSDF (`"preset": "hair"`).
"""


def build(ctx, w, d, h, r, split_z, count=30000, radius=0.035, volume=(0.3, 3.2), cut_below=1.8, seed=7,
          material='hair', points=16, step=0.45, translate=(0, 0, 0), frizz=0.08, clump=0.5, tuck=0.45):
    np, bpy, MM = ctx.np, ctx.bpy, ctx.MM
    rng = np.random.default_rng(seed)
    c = np.array([0.0, 0.0, h / 2]); inner = np.array([w / 2, d / 2, h / 2]) - r

    def sdf(p):
        q = np.abs(p - c) - inner
        return np.linalg.norm(np.maximum(q, 0), axis=1) + np.minimum(q.max(axis=1), 0) - r

    def normal(p, e=1e-3):
        g = np.stack([sdf(p + np.array(v) * e) - sdf(p - np.array(v) * e) for v in ((1, 0, 0), (0, 1, 0), (0, 0, 1))], axis=1)
        return g / np.linalg.norm(g, axis=1, keepdims=True)

    # roots on the crown: the flat top and the upper rounded band (dx^2 + dy^2 < (0.75 r)^2 past the flat)
    n = count
    x = rng.uniform(-w / 2, w / 2, n * 2); y = rng.uniform(-d / 2, d / 2, n * 2)
    dx = np.maximum(np.abs(x) - inner[0], 0); dy = np.maximum(np.abs(y) - inner[1], 0)
    ok = dx ** 2 + dy ** 2 < (0.75 * r) ** 2
    x, y, dx, dy = x[ok][:n], y[ok][:n], dx[ok][:n], dy[ok][:n]
    n = len(x)
    z = c[2] + inner[2] + np.sqrt(np.maximum(r ** 2 - dx ** 2 - dy ** 2, 0))
    p = np.column_stack([x, y, z])
    hs = rng.uniform(volume[0], volume[1], n) ** 1.0                       # each strand's height off the lid
    half_part = w / 2 - d / 2                                              # the part runs along x, as long as the top is flat
    cut = split_z - cut_below + rng.normal(0, 0.18, n)                     # a level cut, not a ruler's
    # clumps: strands near each other share a small offset, so the surface breaks into locks instead of felt
    cell = 2.2                                                             # clump size, mm
    gx = np.floor((x + w) / cell).astype(int); gy = np.floor((y + d) / cell).astype(int)
    near = gx * 1000 + gy
    _, near = np.unique(near, return_inverse=True)
    cl_off = rng.normal(0, 1, (near.max() + 1, 3)) * 0.35
    track = [p.copy()]
    alive = np.ones(n, bool); travelled = np.zeros(n)
    wob_phase = rng.uniform(0, 2 * np.pi, n); wob_k = rng.uniform(0.6, 1.4, n)
    for it in range(400):
        if not alive.any():
            break
        nn = normal(p)
        # comb: away from the part (a segment along x), and down
        out = p.copy(); out[:, 0] = p[:, 0] - np.clip(p[:, 0], -half_part, half_part); out[:, 2] = 0
        out /= np.maximum(np.linalg.norm(out, axis=1, keepdims=True), 1e-6)
        v = out * 0.7 + np.array([0, 0, -1.0])
        v = v - (v * nn).sum(1, keepdims=True) * nn
        v /= np.maximum(np.linalg.norm(v, axis=1, keepdims=True), 1e-9)
        # a little wave and frizz
        side = np.cross(nn, v)
        v = v + side * (frizz * np.sin(travelled * wob_k * 0.9 + wob_phase))[:, None]
        q = p + v * step
        # hold each strand at its own height: rise from the root over 2.5 mm, tuck under over the last 3 mm before the cut
        rise = np.clip(travelled / 2.5, 0, 1)
        to_cut = q[:, 2] - cut
        tuck_k = np.where(to_cut < 3.0, 1 - tuck * (1 - np.clip(to_cut / 3.0, 0, 1)), 1.0)
        target = hs * (rise * (2 - rise)) * tuck_k
        target = target + (cl_off[near] * nn).sum(1) * clump * rise
        q = q - ((sdf(q) - np.maximum(target, 0.05)))[:, None] * normal(q)
        p = np.where(alive[:, None], q, p)
        travelled = travelled + alive * step
        alive &= p[:, 2] > cut
        track.append(p.copy())
    T = np.stack(track, axis=1)                                            # (n, steps, 3)
    seg = np.linalg.norm(np.diff(T, axis=1), axis=2)
    s = np.concatenate([np.zeros((n, 1)), np.cumsum(seg, axis=1)], axis=1)
    L = s[:, -1]
    out_pts = np.empty((n, points, 3))
    for i in range(n):
        tt = np.linspace(0, L[i], points)
        for k in range(3):
            out_pts[i, :, k] = np.interp(tt, s[i], T[i, :, k])
    out_pts += np.array(translate)
    cv = bpy.data.hair_curves.new('wig')
    cv.add_curves([points] * n)
    cv.attributes['position'].data.foreach_set('vector', (out_pts * MM).astype(np.float32).ravel())
    rad = np.tile(np.linspace(1.0, 0.45, points), n) * radius * MM
    if 'radius' not in cv.attributes:
        cv.attributes.new('radius', 'FLOAT', 'POINT')
    cv.attributes['radius'].data.foreach_set('value', rad.astype(np.float32))
    cv.materials.append(ctx.material(material))
    ob = bpy.data.objects.new('wig', cv); ctx.scene.collection.objects.link(ob)
    print(f'wig: {n} strands, {points} points each, mean length {L.mean():.1f} mm', flush=True)
    return [ob]
