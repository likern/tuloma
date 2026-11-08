"""Immediate Rust operations over shared NumPy arrays.

Only storage construction/validation and bindings are implemented. All geometric
queries raise NotImplementedError until their Rust algorithms are supplied.
There is deliberately no fallback to the separate tuloma_reference package.
"""
from .._los import (
    ALGORITHMS_IMPLEMENTED, ClearanceExtrema, ClearanceProfile, ContactKind,
    Contacts, Location, Scene1D, Visibility, lerp, line_height, segment_points,
)

__all__ = [
    "ALGORITHMS_IMPLEMENTED", "ClearanceExtrema", "ClearanceProfile",
    "ContactKind", "Contacts", "Location", "Scene1D", "Visibility",
    "lerp", "line_height", "segment_points",
]
