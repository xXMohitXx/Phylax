"""
Phylax Evidence - Public API

Clean imports for evidence comparison utilities.
"""

from phylax._internal.evidence import (
    compare_outputs,
    compare_latency,
    compare_paths,
)

__all__ = [
    "compare_outputs",
    "compare_latency",
    "compare_paths",
]
