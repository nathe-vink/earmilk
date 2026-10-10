"""Solid-building shorthands every product file reaches for, in the kit's frame (mm; x across, y back from the front
face, z up). Thin wrappers on build123d, so a product file reads as dimensions rather than API calls."""
import math

from build123d import (Align, Axis, Box, Cylinder, Plane, Polyline, Pos, Rot, Solid, Wire, extrude, make_face, revolve,
                       loft, Sketch, Vector, Compound)

MIN = (Align.MIN, Align.MIN, Align.MIN)


def box(x0, y0, z0, x1, y1, z1):
    """An axis-aligned block from corner (x0, y0, z0) to (x1, y1, z1)."""
    return Pos(min(x0, x1), min(y0, y1), min(z0, z1)) * Box(abs(x1 - x0), abs(y1 - y0), abs(z1 - z0), align=MIN)


def cyl(axis, c, d, a0, a1):
    """A cylinder of diameter d along `axis` ('x', 'y' or 'z') through the point c (the other two coordinates), from a0
    to a1 along the axis."""
    lo, L = min(a0, a1), abs(a1 - a0)
    if axis == 'z':
        return Pos(c[0], c[1], lo) * Cylinder(d / 2, L, align=(Align.CENTER, Align.CENTER, Align.MIN))
    if axis == 'y':
        return Pos(c[0], lo, c[1]) * Rot(-90, 0, 0) * Cylinder(d / 2, L, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return Pos(lo, c[0], c[1]) * Rot(0, 90, 0) * Cylinder(d / 2, L, align=(Align.CENTER, Align.CENTER, Align.MIN))


def prism(outline, axis, a0, a1):
    """A prism: a closed 2D outline [(u, v), ...] extruded along `axis` from a0 to a1. For axis 'y' the outline is in
    (x, z); for 'x' in (y, z); for 'z' in (x, y)."""
    pts = list(outline) + [outline[0]]
    if axis == 'z':
        P = [(u, v, a0) for u, v in pts]; d = (0, 0, a1 - a0)
    elif axis == 'y':
        P = [(u, a0, v) for u, v in pts]; d = (0, a1 - a0, 0)
    else:
        P = [(a0, u, v) for u, v in pts]; d = (a1 - a0, 0, 0)
    f = make_face(Polyline(*P))
    return extrude(f, amount=math.hypot(*d), dir=d)


def rounded_rect(w, h, r, n=8, cx=0.0, cy=0.0):
    """A rounded rectangle's outline, w x h centred on (cx, cy), corner radius r, n points per corner."""
    r = min(r, w / 2 - 1e-6, h / 2 - 1e-6)
    pts = []
    for (ox, oy, a0) in ((w / 2 - r, h / 2 - r, 0), (-w / 2 + r, h / 2 - r, 90), (-w / 2 + r, -h / 2 + r, 180), (w / 2 - r, -h / 2 + r, 270)):
        for k in range(n + 1):
            a = math.radians(a0 + 90 * k / n)
            pts.append((cx + ox + r * math.cos(a), cy + oy + r * math.sin(a)))
    return pts


def circle_pts(cx, cy, d, n=96):
    return [(cx + d / 2 * math.cos(2 * math.pi * k / n), cy + d / 2 * math.sin(2 * math.pi * k / n)) for k in range(n)]


def profile_face(pts, smooth=()):
    """A closed profile [(r, h), ...] as a face in the XZ plane (x = r, z = h): straight edges between the points,
    except each run of points in `smooth` ((first, last) index pairs), which is one spline through them. A curve made
    of many short lines draws as many rings and renders faceted; a spline is one smooth face."""
    from build123d import Edge, Wire
    P = [Vector(r, 0.0, h) for r, h in pts]
    n = len(P)
    runs = dict(smooth)
    edges, i = [], 0
    while i < n:
        if i in runs:
            j = runs[i]
            edges.append(Edge.make_spline(P[i:j + 1])); i = j
        else:
            j = (i + 1) % n
            if (P[j] - P[i]).length > 1e-6:
                edges.append(Edge.make_line(P[i], P[j]))
            i += 1
    return make_face(Wire(edges))


def revolve_profile(pts, axis='z', centre=(0, 0, 0), smooth=()):
    """A solid of revolution from a closed profile [(r, h), ...] in the half plane r >= 0, revolved about `axis`
    through `centre`: 'z' (up) or 'y' (facing back, so 'h' runs toward +y) or '-y' (facing out of the front). Runs of
    points listed in `smooth` ((first, last) index pairs) become splines (profile_face)."""
    if smooth:
        face = profile_face(pts, smooth)
    else:
        face = make_face(Polyline(*([(r, 0.0, h) for r, h in pts] + [(pts[0][0], 0.0, pts[0][1])])))
    s = revolve(face, Axis.Z, 360)
    cx, cy, cz = centre
    if axis == 'z':
        return Pos(cx, cy, cz) * s
    if axis == 'y':
        return Pos(cx, cy, cz) * Rot(-90, 0, 0) * s
    if axis == '-y':
        return Pos(cx, cy, cz) * Rot(90, 0, 0) * s
    raise ValueError(axis)


def union(*solids):
    out = None
    for s in solids:
        if s is None:
            continue
        out = s if out is None else out + s
    return out


def bbox(solid):
    b = solid.bounding_box()
    return (b.min.X, b.min.Y, b.min.Z), (b.max.X, b.max.Y, b.max.Z)
