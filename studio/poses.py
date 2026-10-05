"""Resting poses for small parts on a floor, for scene files (numpy only; any Python).

    from poses import stl_vertices, lying_pose
    pose = lying_pose(V, up=(1, 0, 0), axis=(0, 0, 1), heading=40, at=(4, -54), ends=(-9, -24))
    {"type": "mesh", "file": ..., **pose}       # translate (mm) and rotate (degrees, Blender XYZ)

A part lies with its local `up` vector facing the ceiling and its local `axis` (its length) pointing along `heading`
degrees on the floor; then it tilts about the floor line across its length until it rests on both ends: the vertices
whose coordinate along `axis` is above ends[0] and those below ends[1]. Earbuds lie like this on a table.
"""
import math, struct
import numpy as np


def stl_vertices(path):
    """Vertices of a binary STL (as build123d writes them), mm."""
    b = open(path, 'rb').read()
    n = struct.unpack('<I', b[80:84])[0]
    a = np.frombuffer(b[84:84 + 50 * n], dtype=np.dtype([('n', '<f4', 3), ('v', '<f4', (3, 3)), ('a', '<u2')]))
    return a['v'].reshape(-1, 3).astype(float)


def euler_xyz(R):
    """Blender's XYZ Euler (R = Rz Ry Rx), in degrees."""
    b = math.asin(max(-1.0, min(1.0, -R[2, 0])))
    return [math.degrees(math.atan2(R[2, 1], R[2, 2])), math.degrees(b), math.degrees(math.atan2(R[1, 0], R[0, 0]))]


def rot(axis, deg):
    a = np.asarray(axis, float); a = a / np.linalg.norm(a); t = math.radians(deg)
    K = np.array([[0, -a[2], a[1]], [a[2], 0, -a[0]], [-a[1], a[0], 0]])
    return np.eye(3) + math.sin(t) * K + (1 - math.cos(t)) * K @ K


def lying_pose(V, up, axis, heading, at, ends, roll=0.0, floor=0.0, gap=0.02):
    """Translate and rotate (for the scene) that lay vertices V down: `up` to the ceiling, `axis` along `heading`,
    tilted to rest on both ends, `gap` mm above `floor`, its rest point near `at` (x, y)."""
    up = np.asarray(up, float); up /= np.linalg.norm(up)
    ax = np.asarray(axis, float); ax -= up * (ax @ up); ax /= np.linalg.norm(ax)
    side = np.cross(ax, up)
    zg = np.array([math.cos(math.radians(heading)), math.sin(math.radians(heading)), 0.0])   # where `axis` goes
    xg = np.array([0, 0, 1.0])                                                                 # where `up` goes
    yg = np.cross(zg, xg)                                                                      # where `side` goes
    local = np.column_stack([up, side, ax])           # columns: the part's own basis (right-handed: up x side = axis)
    world = np.column_stack([xg, yg, zg])             # where each goes (right-handed too: xg x yg = zg)
    R0 = rot(zg, roll) @ world @ local.T
    t_along = V @ ax
    A = t_along > ends[0]; B = t_along < ends[1]
    tilt_axis = np.cross(zg, xg)
    lo, hi = -45.0, 45.0
    for _ in range(60):                               # tilt until both ends touch
        t = (lo + hi) / 2
        W = V @ (rot(tilt_axis, t) @ R0).T
        if W[A, 2].min() < W[B, 2].min():
            lo = t
        else:
            hi = t
    R = rot(tilt_axis, (lo + hi) / 2) @ R0
    W = V @ R.T
    T = [float(at[0]), float(at[1]), float(floor - W[:, 2].min() + gap)]
    return {'translate': T, 'rotate': euler_xyz(R), 'matrix': R.tolist()}


def to_world(pose, p):
    """A point in the part's own frame, where the pose puts it (mm)."""
    return (np.array(pose['matrix']) @ np.asarray(p, float) + np.array(pose['translate'])).tolist()


def dir_world(pose, d):
    return (np.array(pose['matrix']) @ np.asarray(d, float)).tolist()
