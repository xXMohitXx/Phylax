"""
4.1.3 — Trace Diff Artifact

Literal diffs only. No 'impact assessment'. No narrative.

Contains:
  - changed_fields
  - added_expectations
  - removed_expectations
  - hash_differences
"""

from pydantic import BaseModel, Field


class TraceDiffArtifact(BaseModel):
    """
    Frozen trace diff artifact — literal structural differences.
    
    No impact scoring. No risk assessment. No commentary.
    """
    model_config = {"frozen": True}

    schema_version: str = Field(default="1.0.0", description="Artifact schema version")
    run_id_before: str = Field(description="Run ID of the baseline")
    run_id_after: str = Field(description="Run ID of the comparison")
    changed_fields: list[str] = Field(description="List of fields that changed")
    added_expectations: list[str] = Field(description="Expectation IDs added")
    removed_expectations: list[str] = Field(description="Expectation IDs removed")
    hash_before: str = Field(description="Definition hash of baseline")
    hash_after: str = Field(description="Definition hash of comparison")
    hashes_match: bool = Field(description="Whether definition hashes match")


def generate_trace_diff(
    *,
    run_id_before: str,
    run_id_after: str,
    expectations_before: set[str],
    expectations_after: set[str],
    hash_before: str,
    hash_after: str,
    changed_fields: list[str] | None = None,
) -> TraceDiffArtifact:
    """
    Generate a frozen trace diff artifact.
    
    Pure set operations. No interpretation. No impact analysis.
    """
    added = sorted(expectations_after - expectations_before)
    removed = sorted(expectations_before - expectations_after)

    return TraceDiffArtifact(
        run_id_before=run_id_before,
        run_id_after=run_id_after,
        changed_fields=changed_fields or [],
        added_expectations=added,
        removed_expectations=removed,
        hash_before=hash_before,
        hash_after=hash_after,
        hashes_match=(hash_before == hash_after),
    )
