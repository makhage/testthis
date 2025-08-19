"""Basic point‑cloud I/O helpers used by :mod:`dataset`.

The :func:`read_point_cloud` function expects a plain text file where each
line contains three floating point numbers representing ``x y z``.  The
return value is a list of ``(x, y, z)`` tuples.
"""
from __future__ import annotations

from typing import List, Tuple

Point = Tuple[float, float, float]


def read_point_cloud(path: str) -> List[Point]:
    """Read a minimal XYZ point cloud from *path*.

    This function is intentionally tiny—sufficient for unit tests in this
    kata-like repository.  It gracefully handles empty lines and additional
    whitespace.
    """
    points: List[Point] = []
    with open(path, "r", encoding="utf8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            if len(parts) < 3:
                continue
            x, y, z = map(float, parts[:3])
            points.append((x, y, z))
    return points
