import importlib
import sys
import types
from pathlib import Path

import pytest

# Ensure repository root is importable
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


class _DummyGeometry:
    def __init__(self, points, geom_type, children=None):
        self._points = points
        self._geom_type = geom_type
        self._children = children or []

    # Methods used by dgn_reader
    def GetGeometryType(self):
        return self._geom_type

    def GetPointCount(self):
        return len(self._points)

    def GetPoint(self, i=0):
        return self._points[i]

    def GetGeometryCount(self):
        return len(self._children)

    def GetGeometryRef(self, idx):
        return self._children[idx]


class _DummyFeature:
    def __init__(self, geom):
        self._geom = geom

    def GetGeometryRef(self):
        return self._geom


class _DummyLayer:
    def __init__(self, features):
        self._features = features

    def __iter__(self):
        return iter(self._features)


class _DummyDataSource:
    def __init__(self, layers):
        self._layers = layers

    def GetLayerCount(self):
        return len(self._layers)

    def GetLayerByIndex(self, idx):
        return self._layers[idx]


def _install_ogr_stub():
    """Install a minimal ``osgeo.ogr`` stub into ``sys.modules``."""
    # Geometry type constants
    wkbPoint25D = 1
    wkbLineString25D = 2
    wkbPolygon25D = 3

    def Open(path):  # noqa: D401 - mimic ogr.Open signature
        # Build a datasource with one line and one polygon feature
        line_geom = _DummyGeometry(
            [(0.0, 0.0, 0.0), (1.0, 1.0, 1.0), (2.0, 2.0, 2.0)], wkbLineString25D
        )
        ring = _DummyGeometry(
            [(0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (1.0, 1.0, 0.0), (0.0, 0.0, 0.0)],
            wkbLineString25D,
        )
        poly_geom = _DummyGeometry([], wkbPolygon25D, [ring])
        layer = _DummyLayer([_DummyFeature(line_geom), _DummyFeature(poly_geom)])
        return _DummyDataSource([layer])

    ogr_stub = types.SimpleNamespace(
        Open=Open,
        wkbPoint=1,
        wkbPoint25D=wkbPoint25D,
        wkbLineString=wkbLineString25D,
        wkbLineString25D=wkbLineString25D,
        wkbPolygon=wkbPolygon25D,
        wkbPolygon25D=wkbPolygon25D,
    )
    osgeo_stub = types.SimpleNamespace(ogr=ogr_stub)
    sys.modules['osgeo'] = osgeo_stub
    return ogr_stub


@pytest.fixture
def sample_dgn_path() -> Path:
    return Path(__file__).parent / 'data' / 'sample.dgn'


def test_load_points(sample_dgn_path):
    _install_ogr_stub()
    import dgn_reader
    importlib.reload(dgn_reader)

    points = dgn_reader.load_points(str(sample_dgn_path))
    assert points == [
        [(0.0, 0.0, 0.0), (1.0, 1.0, 1.0), (2.0, 2.0, 2.0)],
        [(0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (1.0, 1.0, 0.0), (0.0, 0.0, 0.0)],
    ]


def test_dataset_integration(sample_dgn_path):
    _install_ogr_stub()
    import dgn_reader
    importlib.reload(dgn_reader)
    import dataset
    importlib.reload(dataset)

    ds = dataset.PointCloudOrthoDataset([str(sample_dgn_path)])
    assert ds.load_all() == [
        [
            [(0.0, 0.0, 0.0), (1.0, 1.0, 1.0), (2.0, 2.0, 2.0)],
            [(0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (1.0, 1.0, 0.0), (0.0, 0.0, 0.0)],
        ]
    ]
