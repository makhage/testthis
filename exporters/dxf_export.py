"""DXF export utilities."""
from __future__ import annotations

from typing import Iterable, Tuple

try:
    import ezdxf
except Exception as exc:  # pragma: no cover - handled at runtime
    ezdxf = None  # type: ignore[assignment]
    _import_error = exc
else:
    _import_error = None


Point = Tuple[float, float]


def write_dxf(points: Iterable[Point], path: str) -> None:
    """Write a DXF file containing the given *points*.

    Each point is a tuple ``(x, y)``. The DXF is saved to ``path``.
    """
    if ezdxf is None:  # pragma: no cover - requires ezdxf
        raise RuntimeError("ezdxf is required for DXF export") from _import_error

    doc = ezdxf.new()  # type: ignore[call-arg]
    msp = doc.modelspace()
    for x, y in points:
        msp.add_point((x, y))
    doc.saveas(path)
