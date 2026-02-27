"""
Health Report Schema (Axis 3 - Phase 3.2)

Structured health data with ZERO qualitative language.

Design rules:
- Pure data, no opinions
- No strings like "weak", "strong", "bad", "risky"
- No threshold-based auto-fails
- Coverage is arithmetic only — it must NOT imply adequacy
- Windowed queries require explicit N
"""

from typing import Optional

from pydantic import BaseModel, Field

from phylax._internal.metrics.aggregator import AggregateMetrics


class HealthReport(BaseModel):
    """
    Health report for a single expectation.
    
    Contains ONLY facts. No interpretation.
    No qualitative language. No recommendations.
    
    Invariants:
    - All fields are data or arithmetic derivations
    - Immutable after creation
    """
    
    expectation_id: str = Field(
        description="ID of the expectation"
    )
    definition_hash: str = Field(
        description="SHA256 hash of current rule definition"
    )
    total_evaluations: int = Field(
        description="Total evaluation count"
    )
    total_failures: int = Field(
        description="Total failure count"
    )
    failure_rate: float = Field(
        description="Arithmetic: total_failures / total_evaluations"
    )
    never_failed: bool = Field(
        description="True if total_failures == 0 and total_evaluations > 0"
    )
    never_passed: bool = Field(
        description="True if total_passes == 0 and total_evaluations > 0"
    )
    
    class Config:
        frozen = True

    @classmethod
    def from_aggregate(
        cls,
        metrics: AggregateMetrics,
        definition_hash: str,
    ) -> "HealthReport":
        """
        Create a HealthReport from AggregateMetrics.
        
        Pure mapping — no additional computation or interpretation.
        """
        return cls(
            expectation_id=metrics.expectation_id,
            definition_hash=definition_hash,
            total_evaluations=metrics.total_evaluations,
            total_failures=metrics.total_failures,
            failure_rate=metrics.failure_rate,
            never_failed=metrics.never_failed,
            never_passed=metrics.never_passed,
        )


class CoverageReport(BaseModel):
    """
    Coverage metrics.
    
    Purely arithmetic. Coverage must NOT imply adequacy.
    
    Invariants:
    - coverage_ratio = expectations_evaluated / expectations_declared
    - No "sufficient" / "insufficient" labels
    - Immutable after creation
    """
    
    expectations_declared: int = Field(
        description="Total expectations declared"
    )
    expectations_evaluated: int = Field(
        description="Total expectations that have been evaluated at least once"
    )
    coverage_ratio: float = Field(
        description="Arithmetic: expectations_evaluated / expectations_declared"
    )
    
    class Config:
        frozen = True

    @classmethod
    def compute(
        cls,
        declared_count: int,
        evaluated_ids: set[str],
    ) -> "CoverageReport":
        """
        Compute coverage from declaration and evaluation data.
        
        Pure arithmetic. No adequacy judgment.
        """
        evaluated_count = len(evaluated_ids)
        ratio = evaluated_count / declared_count if declared_count > 0 else 0.0
        return cls(
            expectations_declared=declared_count,
            expectations_evaluated=evaluated_count,
            coverage_ratio=ratio,
        )


def get_windowed_health(
    metrics: AggregateMetrics,
    definition_hash: str,
) -> HealthReport:
    """
    Get health report (windowed metrics use pre-filtered entries).
    
    N must be explicitly provided upstream. No auto-window here.
    No rolling window. No statistical smoothing.
    """
    return HealthReport.from_aggregate(metrics, definition_hash)
