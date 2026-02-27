"""
Health API Routes (Axis 3 - Phase 3.2)

Exposes health data via HTTP endpoints.

Design rules:
- Pure JSON data only
- No qualitative strings in responses
- Coverage does NOT imply adequacy
- Windowed queries require explicit N parameter
"""

from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from phylax._internal.metrics.ledger import EvaluationLedger
from phylax._internal.metrics.aggregator import aggregate
from phylax._internal.metrics.identity import ExpectationIdentity
from phylax._internal.metrics.health import (
    HealthReport,
    CoverageReport,
    get_windowed_health,
)


router = APIRouter()

# Shared state — injected at server startup
_ledger: Optional[EvaluationLedger] = None
_identities: dict[str, ExpectationIdentity] = {}


def configure_health(
    ledger: EvaluationLedger,
    identities: dict[str, ExpectationIdentity],
) -> None:
    """Configure the health API with shared state."""
    global _ledger, _identities
    _ledger = ledger
    _identities = identities


@router.get("/health/expectations/{expectation_id}")
async def get_expectation_health(
    expectation_id: str,
    window: Optional[int] = Query(
        None,
        description="Last N runs. Must be explicitly provided. No auto-window.",
        ge=1,
    ),
):
    """
    Get health report for a single expectation.
    
    Returns pure data. No qualitative labels.
    """
    if _ledger is None:
        raise HTTPException(status_code=503, detail="Health API not configured")
    
    identity = _identities.get(expectation_id)
    if identity is None:
        raise HTTPException(status_code=404, detail="Expectation not found")
    
    if window is not None:
        # Explicit windowed query
        entries = _ledger.get_entries_windowed(expectation_id, window)
    else:
        entries = _ledger.get_entries(expectation_id)
    
    metrics = aggregate(entries, expectation_id)
    report = get_windowed_health(metrics, identity.definition_hash)
    
    return report.model_dump()


@router.get("/health/coverage")
async def get_coverage():
    """
    Get coverage metrics.
    
    Purely arithmetic. Coverage does NOT imply adequacy.
    """
    if _ledger is None:
        raise HTTPException(status_code=503, detail="Health API not configured")
    
    all_entries = _ledger.get_entries()
    evaluated_ids = set(e.expectation_id for e in all_entries)
    declared_count = len(_identities)
    
    report = CoverageReport.compute(declared_count, evaluated_ids)
    return report.model_dump()
