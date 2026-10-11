"""What the kit checks on every build, so a product cannot ship drawings for parts that do not fit:

- **clashes**: every pair of parts whose solids share volume (boxes tested first, then the solids' intersection),
  except pairs the product lists in `touching` (a press fit, a gasket squeezed in its groove) and pairs from two
  different options (never fitted together); glue joints are faces that touch and share no volume, so they pass;
- **sheet parts**: each is a prism of its stock's thickness (flats.analyse raises if not), and its stock comes in that
  thickness;
- **printed parts**: a wall thinner than the material allows, found by casting rays inward from points spread over the
  part's surface (each ray's run inside the solid is the wall there, where it leaves through a face that faces it);
- **bought parts**: their library entries exist.

Returns a dict the build writes as checks.json; `ok` is False if any clash or missing entry was found.
"""
import fnmatch, math

import numpy as np

from model import SHEETS, PRINTS, Sheet, Printed, Bought


def _bb(s):
    b = s.bounding_box()
    return np.array([b.min.X, b.min.Y, b.min.Z]), np.array([b.max.X, b.max.Y, b.max.Z])


def _allowed(a, b, touching):
    for x, y in touching:
        if (fnmatch.fnmatch(a, x) and fnmatch.fnmatch(b, y)) or (fnmatch.fnmatch(a, y) and fnmatch.fnmatch(b, x)):
            return True
    return False


def clashes(parts, touching=(), tol_mm3=1.0):
    out = []
    bbs = [_bb(p.solid) for p in parts]
    for i in range(len(parts)):
        for j in range(i + 1, len(parts)):
            (a0, a1), (b0, b1) = bbs[i], bbs[j]
            if np.any(a1 <= b0 + 1e-6) or np.any(b1 <= a0 + 1e-6):
                continue
            pi, pj = parts[i], parts[j]
            if _allowed(pi.name, pj.name, touching):
                continue
            if pi.option and pj.option and pi.option != pj.option:
                continue                               # two options are never fitted together
            try:
                common = pi.solid & pj.solid
                v = common.volume if common is not None else 0.0     # None: nothing in common
            except Exception as e:                     # a boolean that fails is reported, not passed
                out.append(dict(a=pi.name, b=pj.name, volume_mm3=None, error=str(e)[:120]))
                continue
            if v > tol_mm3:
                out.append(dict(a=pi.name, b=pj.name, volume_mm3=round(v, 1)))
    return out


def walls(part, min_wall, n=400):
    """The thinnest walls found by inward rays from n points over the surface: [(mm, (x, y, z))], thinnest first."""
    from build123d import Axis, Vector
    s = part.solid
    faces = s.faces()
    areas = np.array([f.area for f in faces]); areas = areas / areas.sum()
    rng = np.random.default_rng(7)
    found = []
    for fi in rng.choice(len(faces), size=n, p=areas):
        f = faces[fi]
        u, v = rng.random(), rng.random()
        try:
            p = f.position_at(u, v)
            if not f.is_inside(p, 1e-3):        # (u, v) spans the untrimmed surface: a hole's or a cut's area is off
                continue                        # the face
            nrm = f.normal_at(p)
        except Exception:
            continue
        d = Vector(-nrm.X, -nrm.Y, -nrm.Z)
        start = p + d * 0.01
        try:
            hits = s.find_intersection_points(Axis(start, d))     # the whole line: keep the hits ahead of the start
        except Exception:
            hits = []
        ahead = sorted((((h[0] - start).dot(d), h[1]) for h in hits if (h[0] - start).dot(d) > 0.02), key=lambda t: t[0])
        if ahead:
            t, n_hit = ahead[0]
            t += 0.01
            # a wall is thin where the ray leaves through a face that looks back at it; one it only grazes is a corner
            # (the ray running along the next face round an edge), which is no wall
            if t < min_wall and abs(n_hit.normalized().dot(d)) > 0.5:
                found.append((round(t, 2), (round(p.X, 1), round(p.Y, 1), round(p.Z, 1))))
    return sorted(found)[:8]


def run(product, parts, library):
    rep = dict(clashes=clashes([p for p in parts if p.solid is not None], product.touching), sheets=[], prints=[], bought=[])
    for p in parts:
        if isinstance(p.make, Sheet):
            st = SHEETS.get(p.make.material)
            if st is None:
                rep['sheets'].append(dict(part=p.name, problem=f'no stock called {p.make.material!r}'))
            elif p.make.thickness not in st['thicknesses']:
                rep['sheets'].append(dict(part=p.name, problem=f'{p.make.material} is not sold {p.make.thickness:g} mm thick '
                                                                 f'(stock: {", ".join(f"{t:g}" for t in st["thicknesses"])})'))
        elif isinstance(p.make, Printed):
            m = PRINTS.get(p.make.material)
            if m is None:
                rep['prints'].append(dict(part=p.name, problem=f'no print material called {p.make.material!r}'))
                continue
            mw = p.make.min_wall or m['min_wall']
            thin = walls(p, mw)
            if thin:
                rep['prints'].append(dict(part=p.name, problem=f'walls under {mw:g} mm', where=thin))
        elif isinstance(p.make, Bought):
            if p.make.ref not in library:
                rep['bought'].append(dict(part=p.name, problem=f'{p.make.ref!r} is not in the component library'))
    rep['ok'] = not rep['clashes'] and not rep['bought'] and not any('no stock' in x['problem'] for x in rep['sheets'])
    return rep
