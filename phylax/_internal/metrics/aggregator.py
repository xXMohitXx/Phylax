"""
Deterministic Aggregator (Axis 3 - Phase 3.1.3)

Pure aggregation layer deriving metrics from raw ledger entries.

Design rules:
- COMPUTED, not stored
- DETERMINISTIC — same entries → same result
- RECOMPUTABLE from ledger at any time
- No cached heuristics
- No qualitative labels
- No scoring
"""

from typing import Any

from pydantic import BaseModel, Field

from phylax._internal.metrics.ledger import LedgerEntry


class AggregateMetrics(BaseModel):
    """
    Aggregated metrics for a single expectation.
    
    All fields are computed from raw ledger entries.
    Nothing is stored or cached.
    
    Invariants:
    - Pure arithmetic derivation
    - No qualitative labels (no "weak", "strong", "risky")
    - No scoring or ranking
    - Immutable after computation
    """
    
    expectation_id: str = Field(
        description="Expectation this aggregate belongs to"
    )
    total_evaluations: int = Field(
        description="Total number of evaluation runs"
    )
    total_passes: int = Field(
        description="Number of PASS verdicts"
    )
    total_failures: int = Field(
        description="Number of FAIL verdicts"
    )
    failure_rate: float = Field(
        description="total_failures / total_evaluations (0.0 if no evaluations)"
    )
    never_failed: bool = Field(
        description="True if total_failures == 0 and total_evaluations > 0"
    )
    never_passed: bool = Field(
        description="True if total_passes == 0 and total_evaluations > 0"
    )
    
    class Config:
        frozen = True  # Immutable after computation


def aggregate(
    entries: list[LedgerEntry],
    expectation_id: str,
) -> AggregateMetrics:
    """
    Compute aggregate metrics from raw ledger entries.
    
    This is a PURE FUNCTION.
    Same entries → same result. Always.
    No side effects. No caching. No stored state.
    
    Args:
        entries: Raw ledger entries (pre-filtered or unfiltered).
        expectation_id: Expectation to aggregate for.
        
    Returns:
        Frozen AggregateMetrics instance.
    """
    filtered = [e for e in entries if e.expectation_id == expectation_id]
    
    total = len(filtered)
    passes = sum(1 for e in filtered if e.verdict == "pass")
    failures = sum(1 for e in filtered if e.verdict == "fail")
    
    return AggregateMetrics(
        expectation_id=expectation_id,
        total_evaluations=total,
        total_passes=passes,
        total_failures=failures,
        failure_rate=failures / total if total > 0 else 0.0,
        never_failed=failures == 0 and total > 0,
        never_passed=passes == 0 and total > 0,
    )


def aggregate_all(
    entries: list[LedgerEntry],
) -> list[AggregateMetrics]:
    """
    Compute aggregates for ALL expectations in the ledger.
    
    Pure function. Deterministic.
    
    Args:
        entries: All ledger entries.
        
    Returns:
        List of AggregateMetrics, one per unique expectation_id.
    """
    unique_ids = sorted(set(e.expectation_id for e in entries))
    return [aggregate(entries, eid) for eid in unique_ids]
