"""Boundary-element model of the tweeter in its waveguide in the gable, for the polar response (fab/waveguide.py).

    .venv-fab/bin/python fab/bem.py --throat 125 903.5 --freqs 2000 4000 8000 --out out/acoustics/wg-125

What is modelled: the gable block (front slope with the waveguide cut into it, back slope, gable ends, the fin) on a stub
of the cabinet (`--stub` mm of the body below the gable, closed at the bottom), every surface rigid except a flat disc
at the throat moving as a piston (the dome, a standard approximation up to where the dome breaks up). The air outside is
solved for with bempp-cl: the exterior Neumann problem in the Burton-Miller form, which stays well conditioned at the
closed body's interior resonances (checked on a pulsating sphere at ka = pi: -0.0921-0.2890i against -0.0920-0.2890i).
The stub's bottom is an artificial edge: it colours the result below about 1.5 kHz, where the mid takes over.

Out: polar responses (dB, horizontal and vertical, 0 to 90 degrees in 5 degree steps; positive vertical angles are
up), each normalised to its own on-axis value and also absolute, the -6 dB beamwidths, the directivity index (on-axis
power against the average over a sphere of 600 directions), the vertical angle of the loudest direction, and a JSON file.

Speed: the operators are assembled with OpenCL (pyopencl and pocl-binary-distribution, a CPU OpenCL), about five times
faster than numba on four cores: about a minute a frequency for 8000 triangles. Without pyopencl it falls back to numba.
"""
import argparse, json, time
from math import cos, sin, radians
from pathlib import Path

import numpy as np

try:
    from waveguide import Waveguide
    from params import PLAN, BODY, RISE, RUN, FIN_H, FIN_T
except ImportError:
    from fab.waveguide import Waveguide
    from fab.params import PLAN, BODY, RISE, RUN, FIN_H, FIN_T

C_AIR = 343.0


def roof_z(y):
    return BODY + (RISE / RUN) * y


def build_mesh(wg, stub=250.0, h_near=6.0, h_far=28.0):
    """A closed triangle mesh (mm) of the gable and a stub of the body, the waveguide cut into the front slope.
    Returns vertices (N, 3), triangles (M, 3), domain (M,): 1 on the throat's disc (the radiator), 0 elsewhere."""
    import gmsh
    G, _ = wg.grid()                            # (sections, stations, 3); the last ring lies on the roof
    S, T = G.shape[0], G.shape[1]
    mouth = G[:, -1, :]
    y_fin0, y_fin1 = RUN - FIN_T / 2, RUN + FIN_T / 2
    z_fin = roof_z(y_fin0); z_top = BODY + RISE + FIN_H; z0 = BODY - stub

    gmsh.initialize(); gmsh.option.setNumber('General.Terminal', 0)
    gmsh.model.add('gable')
    geo = gmsh.model.geo
    P = {}
    def pt(name, xyz, h):
        P[name] = geo.addPoint(*xyz, h); return P[name]
    # corners
    c = dict(
        Ef0=(0, 0, BODY), Ef1=(PLAN, 0, BODY), Ff0=(0, y_fin0, z_fin), Ff1=(PLAN, y_fin0, z_fin),
        Ft0=(0, y_fin0, z_top), Ft1=(PLAN, y_fin0, z_top), Fb0=(0, y_fin1, z_top), Fb1=(PLAN, y_fin1, z_top),
        Bf0=(0, y_fin1, z_fin), Bf1=(PLAN, y_fin1, z_fin), Eb0=(0, PLAN, BODY), Eb1=(PLAN, PLAN, BODY),
        Sf0=(0, 0, z0), Sf1=(PLAN, 0, z0), Sb0=(0, PLAN, z0), Sb1=(PLAN, PLAN, z0))
    for k, v in c.items():
        near = k.startswith(('Ef', 'Ff'))
        pt(k, v, h_far * (0.6 if near else 1.0))
    L = {}
    def line(a, b):
        key = tuple(sorted((a, b)))
        if key not in L: L[key] = (geo.addLine(P[a], P[b]), a, b)
        tag, a0, b0 = L[key]
        return tag if (a0, b0) == (a, b) else -tag
    def loop(names):
        return geo.addCurveLoop([line(names[i], names[(i + 1) % len(names)]) for i in range(len(names))])
    faces = {}
    # the mouth: one point per meridian, joined by straight segments of exactly two nodes each
    mp = [geo.addPoint(*m, h_near) for m in mouth]
    ml = [geo.addLine(mp[i], mp[(i + 1) % S]) for i in range(S)]
    for t in ml: geo.mesh.setTransfiniteCurve(t, 2)
    hole = geo.addCurveLoop(ml)
    faces['front_slope'] = geo.addPlaneSurface([loop(['Ef0', 'Ef1', 'Ff1', 'Ff0']), hole])
    faces['fin_front'] = geo.addPlaneSurface([loop(['Ff0', 'Ff1', 'Ft1', 'Ft0'])])
    faces['fin_top'] = geo.addPlaneSurface([loop(['Ft0', 'Ft1', 'Fb1', 'Fb0'])])
    faces['fin_back'] = geo.addPlaneSurface([loop(['Fb0', 'Fb1', 'Bf1', 'Bf0'])])
    faces['back_slope'] = geo.addPlaneSurface([loop(['Bf0', 'Bf1', 'Eb1', 'Eb0'])])
    faces['left'] = geo.addPlaneSurface([loop(['Sf0', 'Ef0', 'Ff0', 'Ft0', 'Fb0', 'Bf0', 'Eb0', 'Sb0'])])
    faces['right'] = geo.addPlaneSurface([loop(['Sf1', 'Sb1', 'Eb1', 'Bf1', 'Fb1', 'Ft1', 'Ff1', 'Ef1'])])
    faces['front'] = geo.addPlaneSurface([loop(['Sf0', 'Sf1', 'Ef1', 'Ef0'])])
    faces['back'] = geo.addPlaneSurface([loop(['Sb0', 'Eb0', 'Eb1', 'Sb1'])])
    faces['bottom'] = geo.addPlaneSurface([loop(['Sf0', 'Sb0', 'Sb1', 'Sf1'])])
    geo.synchronize()
    # grade the mesh: fine near the mouth, coarse far from it
    f = gmsh.model.mesh.field
    d = f.add('Distance'); f.setNumbers(d, 'CurvesList', ml); f.setNumber(d, 'Sampling', 20)
    th = f.add('Threshold'); f.setNumber(th, 'InField', d); f.setNumber(th, 'SizeMin', h_near); f.setNumber(th, 'SizeMax', h_far)
    f.setNumber(th, 'DistMin', 10.0); f.setNumber(th, 'DistMax', 180.0)
    f.setAsBackgroundMesh(th)
    gmsh.option.setNumber('Mesh.MeshSizeExtendFromBoundary', 0); gmsh.option.setNumber('Mesh.MeshSizeFromPoints', 0)
    gmsh.option.setNumber('Mesh.Algorithm', 6)
    gmsh.model.mesh.generate(2)
    tags, coords, _ = gmsh.model.mesh.getNodes()
    xyz = coords.reshape(-1, 3); idx = {int(t): i for i, t in enumerate(tags)}
    tris = []
    for name, surf in faces.items():
        et, _, en = gmsh.model.mesh.getElements(2, surf)
        for typ, nodes in zip(et, en):
            if typ != 2: continue
            for tri in np.asarray(nodes).reshape(-1, 3):
                tris.append([idx[int(n)] for n in tri])
    gmsh.finalize()
    V = [tuple(v) for v in xyz]
    tris = np.array(tris)
    # orient the planar faces outward: away from a point inside the body (a body without the cavity is convex enough
    # for this; the faces meeting the cavity are handled with the waveguide below)
    inside = np.array([PLAN / 2, PLAN / 2, (z0 + BODY) / 2])
    Vn = np.array(V)
    def orient(tri_list, ref_out):
        out = []
        for t in tri_list:
            a, b, cc = Vn[t[0]], Vn[t[1]], Vn[t[2]]
            n = np.cross(b - a, cc - a)
            out.append(t if ref_out(n, (a + b + cc) / 3) else [t[0], t[2], t[1]])
        return out
    tris = orient(tris, lambda n, m: n @ (m - inside) > 0)
    # the waveguide wall and the throat's disc, from the grid; join to the mesh by exact coordinates
    key = lambda p: (round(float(p[0]), 6), round(float(p[1]), 6), round(float(p[2]), 6))
    vid = {key(v): i for i, v in enumerate(V)}
    Vl = [np.array(v) for v in V]
    def vertex(p):
        k = key(p)
        if k not in vid: vid[k] = len(Vl); Vl.append(np.array(p, float))
        return vid[k]
    gid = np.array([[vertex(G[i, j]) for j in range(T)] for i in range(S)])
    axis_pt = np.array([RUN, wg.throat_y, wg.throat_z])
    wall = []
    for i in range(S):
        i1 = (i + 1) % S
        for j in range(T - 1):
            a, b, cc, dd = gid[i, j], gid[i1, j], gid[i1, j + 1], gid[i, j + 1]
            wall += [[a, b, cc], [a, cc, dd]]
    Vn = np.array(Vl)
    def toward_axis(n, m):      # the wall's outward normal (into the air) points toward the axis
        q = m - axis_pt; ax = np.array([0, -1.0, 0]); radial = q - (q @ ax) * ax
        return n @ radial < 0
    wall = orient(wall, toward_axis)
    centre = vertex(axis_pt)
    Vn = np.array(Vl)
    disc = [[centre, gid[i, 0], gid[(i + 1) % S, 0]] for i in range(S)]
    disc = orient(disc, lambda n, m: n[1] < 0)        # the dome faces forward (-y)
    allt = np.array(list(tris) + wall + disc)
    dom = np.array([0] * (len(tris) + len(wall)) + [1] * len(disc), dtype=np.uint32)
    V = np.array(Vl)
    return V, consistent_orientation(V, allt), dom


def consistent_orientation(V, T):
    """Orient every triangle consistently with its neighbours (a breadth-first walk over shared edges), then make the
    normals point out of the body (positive signed volume). The per-face guesses above are only a start."""
    from collections import defaultdict, deque
    T = T.copy(); edges = defaultdict(list)
    for i, t in enumerate(T):
        for a, b in ((t[0], t[1]), (t[1], t[2]), (t[2], t[0])):
            edges[(min(a, b), max(a, b))].append(i)
    seen = np.zeros(len(T), bool)
    def directed(t):
        return {(t[0], t[1]), (t[1], t[2]), (t[2], t[0])}
    for seed in range(len(T)):
        if seen[seed]: continue
        seen[seed] = True; q = deque([seed])
        while q:
            i = q.popleft(); di = directed(T[i])
            for a, b in di:
                for j in edges[(min(a, b), max(a, b))]:
                    if j == i or seen[j]: continue
                    if (a, b) in directed(T[j]):          # same direction on a shared edge: flip the neighbour
                        T[j] = [T[j][0], T[j][2], T[j][1]]
                    seen[j] = True; q.append(j)
    vol = np.sum(np.einsum('ij,ij->i', V[T[:, 0]], np.cross(V[T[:, 1]], V[T[:, 2]]))) / 6
    if vol < 0: T = T[:, [0, 2, 1]]
    return T


def directions(angles_deg):
    """Unit vectors for the horizontal arc (x, toward the speaker's right as seen from the front... seen by the
    listener) and the vertical arc (positive up), measured from the axis (-y)."""
    a = np.radians(angles_deg)
    hor = np.stack([np.sin(a), -np.cos(a), np.zeros_like(a)])
    ver = np.stack([np.zeros_like(a), -np.cos(a), np.sin(a)])
    return hor, ver


def sphere(n=600):
    """n nearly uniform unit vectors (a Fibonacci lattice), shape (3, n)."""
    i = np.arange(n) + 0.5
    z = 1 - 2 * i / n; r = np.sqrt(1 - z * z); t = np.pi * (1 + 5 ** 0.5) * i
    return np.stack([r * np.cos(t), r * np.sin(t), z])


def device():
    try:
        import pyopencl  # noqa: F401
        return 'opencl'
    except ImportError:
        return 'numba'


def solve(V, Tr, dom, freqs, angles=np.arange(0, 91, 5)):
    import bempp_cl.api as bempp
    bempp.DEFAULT_PRECISION = 'single'
    bempp.DEFAULT_DEVICE_INTERFACE = device()
    grid = bempp.Grid(V.T / 1000.0, Tr.T.astype(np.uint32), dom)          # metres
    P1 = bempp.function_space(grid, 'P', 1)
    # the radiator's velocity lives only on the throat's disc (domain 1): a space on that segment alone keeps the
    # right-hand side's operators a few dozen columns wide instead of one per triangle
    DP0 = bempp.function_space(grid, 'DP', 0, segments=[1])
    g = bempp.GridFunction(DP0, coefficients=np.ones(DP0.global_dof_count, dtype=np.complex128))
    hor, ver = directions(angles)
    hor_neg, ver_neg = directions(-angles)
    out = []
    for f in freqs:
        t0 = time.time(); k = 2 * np.pi * f / C_AIR
        I = bempp.operators.boundary.sparse.identity(P1, P1, P1)
        Ig = bempp.operators.boundary.sparse.identity(DP0, P1, P1)
        D = bempp.operators.boundary.helmholtz.double_layer(P1, P1, P1, k)
        H = bempp.operators.boundary.helmholtz.hypersingular(P1, P1, P1, k)
        Sg = bempp.operators.boundary.helmholtz.single_layer(DP0, P1, P1, k)
        Dpg = bempp.operators.boundary.helmholtz.adjoint_double_layer(DP0, P1, P1, k)
        eta = 1j / k
        lhs = D - 0.5 * I + eta * H
        rhs = (Sg - eta * (0.5 * Ig + Dpg)) * g
        # a direct solve of the assembled system: a few thousand unknowns, so LU takes seconds and cannot stall
        A = np.asarray(lhs.weak_form().to_dense()); b = rhs.projections(P1)
        coeffs = np.linalg.solve(A, b)
        p = bempp.GridFunction(P1, coefficients=coeffs)
        resid = float(np.linalg.norm(A @ coeffs - b) / np.linalg.norm(b))
        res = {'f': f, 'residual': resid}
        info = f'residual {resid:.1e}'
        for name, pts in (('h_right', hor), ('h_left', hor_neg), ('v_up', ver), ('v_down', ver_neg), ('sphere', sphere())):
            DLf = bempp.operators.far_field.helmholtz.double_layer(P1, pts, k)
            SLf = bempp.operators.far_field.helmholtz.single_layer(DP0, pts, k)
            pf = (DLf * p - SLf * g).ravel()
            if name == 'sphere':
                res['di'] = float(10 * np.log10(np.abs(on_axis) ** 2 / np.mean(np.abs(pf) ** 2)))
            else:
                if name == 'h_right': on_axis = pf[0]
                res[name] = (20 * np.log10(np.abs(pf) + 1e-30)).tolist()
        vert = np.array(res['v_down'][::-1] + res['v_up'][1:]); va = np.concatenate([-angles[::-1], angles[1:]])
        res['vertical_peak'] = float(va[int(np.argmax(vert))])
        res['seconds'] = round(time.time() - t0, 1)
        out.append(res); print(f'{f:7.0f} Hz  {res["seconds"]:6.1f}s  {info}', flush=True)
    return out


def beamwidth(levels, angles):
    """-6 dB half-angle from a level list starting on axis (linear interpolation), or None if it never falls 6 dB."""
    l = np.asarray(levels) - levels[0]
    for i in range(1, len(l)):
        if l[i] <= -6:
            a0, a1, l0, l1 = angles[i - 1], angles[i], l[i - 1], l[i]
            return float(a0 + (a1 - a0) * (-6 - l0) / (l1 - l0))
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--throat', nargs=2, type=float, default=[125.0, 903.5], help='throat plane y and axis z, mm')
    ap.add_argument('--r0', type=float, default=15.0); ap.add_argument('--a0', type=float, default=12.0)
    ap.add_argument('--ah', type=float, default=45.0); ap.add_argument('--aup', type=float, default=35.0); ap.add_argument('--adown', type=float, default=30.0)
    ap.add_argument('--k', type=float, default=1.4); ap.add_argument('--lip', type=float, default=12.0)
    ap.add_argument('--tilt', type=float, default=0.0, help='degrees the axis is tipped down')
    ap.add_argument('--freqs', nargs='+', type=float, default=[1000, 1600, 2500, 4000, 6300, 10000])
    ap.add_argument('--stub', type=float, default=250.0)
    ap.add_argument('--h-near', type=float, default=None); ap.add_argument('--h-far', type=float, default=28.0)
    ap.add_argument('--sections', type=int, default=None); ap.add_argument('--steps', type=int, default=None)
    ap.add_argument('--out', default='out/acoustics/wg')
    a = ap.parse_args()
    fmax = max(a.freqs); lam = C_AIR / fmax * 1000
    h_near = a.h_near or max(3.5, lam / 6)
    wg = Waveguide(r0=a.r0, a0=a.a0, a_h=a.ah, a_up=a.aup, a_down=a.adown, k=a.k, throat_y=a.throat[0], throat_z=a.throat[1], lip_r=a.lip, tilt=a.tilt)
    circ = 2 * np.pi * 160
    wg.sections = a.sections or int(max(48, min(128, circ / h_near)) // 8 * 8)
    wg.steps = a.steps or int(max(16, min(48, 180 / h_near)))
    V, Tr, dom = build_mesh(wg, a.stub, h_near, a.h_far)
    print(f'mesh: {len(V)} vertices, {len(Tr)} triangles ({int(dom.sum())} on the radiator), h_near {h_near:.1f}, sections {wg.sections}, steps {wg.steps}', flush=True)
    angles = np.arange(0, 91, 5)
    res = solve(V, Tr, dom, a.freqs, angles)
    for r in res:
        r['beamwidth_h'] = beamwidth(r['h_right'], angles); r['beamwidth_up'] = beamwidth(r['v_up'], angles); r['beamwidth_down'] = beamwidth(r['v_down'], angles)
    out = Path(a.out); out.parent.mkdir(parents=True, exist_ok=True)
    meta = dict(waveguide=wg.summary(), mesh=dict(vertices=len(V), triangles=len(Tr), h_near=h_near, h_far=a.h_far, stub=a.stub), angles=angles.tolist())
    out.with_suffix('.json').write_text(json.dumps(dict(meta=meta, results=res), indent=1))
    for r in res:
        fmt = lambda v: '  -  ' if v is None else f'{v:5.1f}'
        print(f"{r['f']:7.0f} Hz  -6 dB half-angles: horizontal {fmt(r['beamwidth_h'])}, up {fmt(r['beamwidth_up'])}, "
              f"down {fmt(r['beamwidth_down'])}   DI {r['di']:4.1f} dB   loudest vertically at {r['vertical_peak']:+.0f} deg")


if __name__ == '__main__':
    main()
