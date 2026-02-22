"""
Phylax Surface Abstraction Layer (Axis 2)

Provides a generic enforcement surface so the engine can enforce
contracts over any payload type — text, JSON, tool calls, execution traces,
or cross-run snapshots — without knowing or caring about the surface type.

Design rules:
- All surfaces preserve raw payloads (no normalization, no transformation)
- Verdicts remain binary: PASS / FAIL
- No inference, no scoring, no interpretation
"""

from phylax._internal.surfaces.surface import (
    Surface,
    SurfaceType,
    SurfaceRuleResult,
    SurfaceVerdict,
    SurfaceRule,
    SurfaceAdapter,
    SurfaceEvaluator,
    SurfaceRegistry,
    get_registry,
)
from phylax._internal.surfaces.text import TextSurfaceAdapter

__all__ = [
    # Core models
    "Surface",
    "SurfaceType",
    "SurfaceRuleResult",
    "SurfaceVerdict",
    # Base classes
    "SurfaceRule",
    "SurfaceAdapter",
    # Evaluator
    "SurfaceEvaluator",
    # Registry
    "SurfaceRegistry",
    "get_registry",
    # Adapters
    "TextSurfaceAdapter",
]
