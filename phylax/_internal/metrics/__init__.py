"""
Phylax Metrics Package (Axis 3)

Provides observation memory for expectation health tracking.

Design rules:
- All metrics derive from raw ledger entries
- No qualitative labels, no scoring, no interpretation
- Append-only ledger, immutable entries
- All aggregations are computed, never stored
"""

from phylax._internal.metrics.identity import (
    ExpectationIdentity,
    compute_definition_hash,
)
from phylax._internal.metrics.ledger import (
    LedgerEntry,
    EvaluationLedger,
)
from phylax._internal.metrics.aggregator import (
    AggregateMetrics,
    aggregate,
    aggregate_all,
)

__all__ = [
    "ExpectationIdentity",
    "compute_definition_hash",
    "LedgerEntry",
    "EvaluationLedger",
    "AggregateMetrics",
    "aggregate",
    "aggregate_all",
]
