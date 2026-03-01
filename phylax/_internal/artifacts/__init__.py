"""
Phylax Artifacts — __init__.py

Machine-consumable output contracts.
Phylax produces artifacts. Other systems consume them.
"""

from phylax._internal.artifacts.verdict import VerdictArtifact, generate_verdict_artifact
from phylax._internal.artifacts.failures import FailureEntry, FailureArtifact, generate_failure_artifact
from phylax._internal.artifacts.trace_diff import (
    TraceDiffArtifact,
    generate_trace_diff,
)
from phylax._internal.artifacts.exit_codes import (
    EXIT_PASS,
    EXIT_FAIL,
    EXIT_SYSTEM_ERROR,
    resolve_exit_code,
)

__all__ = [
    "VerdictArtifact",
    "generate_verdict_artifact",
    "FailureEntry",
    "FailureArtifact",
    "generate_failure_artifact",
    "TraceDiffArtifact",
    "generate_trace_diff",
    "EXIT_PASS",
    "EXIT_FAIL",
    "EXIT_SYSTEM_ERROR",
    "resolve_exit_code",
]
