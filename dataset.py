"""Dataset utilities integrating point clouds and orthophotos.

Only the small subset needed for the unit tests is implemented here.  The
class accepts a sequence of paths to point‑cloud files.  When a path ends
with ``.dgn`` it delegates to :func:`dgn_reader.load_points` to extract
geometry; otherwise it uses :func:`point_cloud_io.read_point_cloud`.
"""
from __future__ import annotations

from typing import Iterable, List

import dgn_reader
from point_cloud_io import read_point_cloud


class PointCloudOrthoDataset:
    """Very small dataset wrapper used in tests."""

    def __init__(self, point_paths: Iterable[str]):
        self.point_paths = list(point_paths)

    def _load_points(self, path: str):
        if path.lower().endswith(".dgn"):
            return dgn_reader.load_points(path)
        return read_point_cloud(path)

    def load_all(self) -> List:
        """Load points for all configured paths."""
        return [self._load_points(p) for p in self.point_paths]
