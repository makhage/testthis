"""Utility for reading Microstation DGN files using GDAL/OGR.

This module provides :func:`load_points` which extracts XYZ point
coordinates from geometries stored in a DGN file.  The function iterates
through every layer and feature in the datasource, flattening common
geometry types into a list of ``(x, y, z)`` triples.  The return value is a
list of geometries where each geometry itself is represented by a list of
points.

The implementation relies on ``from osgeo import ogr``.  The module is
lightweight and avoids third‑party dependencies such as ``numpy`` so it can
operate in constrained environments.
"""
from __future__ import annotations

from typing import Iterable, List, Tuple

try:  # pragma: no cover - import is tested via unit tests with stubs
    from osgeo import ogr  # type: ignore
except Exception as exc:  # pragma: no cover - handled at runtime
    ogr = None  # type: ignore
    _IMPORT_ERROR = exc
else:
    _IMPORT_ERROR = None


Point = Tuple[float, float, float]
GeometryPoints = List[Point]


def _iter_geometries(geometry: "ogr.Geometry") -> Iterable["ogr.Geometry"]:
    """Yield child geometries recursively.

    OGR geometries can be single (e.g. ``wkbLineString``) or collections
    such as ``wkbMultiLineString``.  This helper flattens the hierarchy
    yielding each primitive geometry contained in ``geometry``.
    """
    stack = [geometry]
    while stack:
        geom = stack.pop()
        geom_type = geom.GetGeometryType()
        # If geometry has sub‑geometries, push them on the stack
        if geom.GetGeometryCount() > 0 and not _is_primitive(geom_type):
            for i in range(geom.GetGeometryCount()):
                stack.append(geom.GetGeometryRef(i))
        else:
            yield geom


def _is_primitive(ogr_type: int) -> bool:
    """Return True if *ogr_type* is a primitive point/line/polygon."""
    primitives = {
        ogr.wkbPoint,
        ogr.wkbPoint25D,
        ogr.wkbLineString,
        ogr.wkbLineString25D,
        ogr.wkbPolygon,
        ogr.wkbPolygon25D,
    }
    return ogr_type in primitives


def _geometry_to_points(geometry: "ogr.Geometry") -> GeometryPoints:
    """Convert a primitive geometry to a list of ``(x, y, z)`` points."""
    geom_type = geometry.GetGeometryType()
    points: GeometryPoints = []

    if geom_type in (ogr.wkbPoint, ogr.wkbPoint25D):
        x, y, z = geometry.GetPoint()  # single point
        points.append((x, y, z))
    elif geom_type in (ogr.wkbLineString, ogr.wkbLineString25D):
        for i in range(geometry.GetPointCount()):
            x, y, z = geometry.GetPoint(i)
            points.append((x, y, z))
    elif geom_type in (ogr.wkbPolygon, ogr.wkbPolygon25D):
        ring = geometry.GetGeometryRef(0)  # exterior ring
        for i in range(ring.GetPointCount()):
            x, y, z = ring.GetPoint(i)
            points.append((x, y, z))
    else:  # pragma: no cover - unexpected types
        for i in range(geometry.GetPointCount()):
            x, y, z = geometry.GetPoint(i)
            points.append((x, y, z))
    return points


def load_points(path: str) -> List[GeometryPoints]:
    """Load all point geometries from *path*.

    Parameters
    ----------
    path:
        Path to the ``.dgn`` file.

    Returns
    -------
    List[List[Tuple[float, float, float]]]
        A list containing one entry per feature.  Each entry is a list of
        ``(x, y, z)`` point triples describing the feature geometry.

    Raises
    ------
    ImportError
        If the ``osgeo`` package is not installed.
    RuntimeError
        If the file cannot be opened.
    """
    if ogr is None:  # pragma: no cover - exercised when GDAL missing
        raise ImportError(
            "GDAL/OGR library is required to read DGN files"  # noqa: TRY003
        ) from _IMPORT_ERROR

    ds = ogr.Open(path)
    if ds is None:
        raise RuntimeError(f"Unable to open DGN file: {path}")

    all_points: List[GeometryPoints] = []
    for layer_index in range(ds.GetLayerCount()):
        layer = ds.GetLayerByIndex(layer_index)
        for feature in layer:
            geom = feature.GetGeometryRef()
            if geom is None:
                continue
            for subgeom in _iter_geometries(geom):
                all_points.append(_geometry_to_points(subgeom))
    return all_points
