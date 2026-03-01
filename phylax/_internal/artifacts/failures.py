"""
4.1.2 — Structured Failure Artifact

Strictly mechanical failure records. No explanation field. No narrative text.

Each failure entry contains:
  - expectation_id
  - violated_rule
  - raw_value
  - expected_value
"""

from pydantic import BaseModel, Field


class FailureEntry(BaseModel):
    """
    Single expectation failure — mechanical fact only.
    
    No 'reason', no 'explanation', no 'suggestion'.
    """
    model_config = {"frozen": True}

    expectation_id: str = Field(description="ID of the failed expectation")
    violated_rule: str = Field(description="Rule name that was violated")
    raw_value: str = Field(description="Actual value observed")
    expected_value: str = Field(description="Value that was expected")


class FailureArtifact(BaseModel):
    """
    Frozen failure artifact — list of mechanical failure entries.
    
    No commentary. No impact assessment. No severity ranking.
    """
    model_config = {"frozen": True}

    schema_version: str = Field(default="1.0.0", description="Artifact schema version")
    run_id: str = Field(description="Run that produced these failures")
    failures: list[FailureEntry] = Field(description="Ordered list of failures")


def generate_failure_artifact(
    *,
    run_id: str,
    failures: list[dict],
) -> FailureArtifact:
    """
    Generate a frozen failure artifact from raw failure data.
    
    Pure factory. No side effects. No ranking. No sorting by severity.
    """
    entries = [
        FailureEntry(
            expectation_id=f.get("expectation_id", "unknown"),
            violated_rule=f.get("violated_rule", "unknown"),
            raw_value=str(f.get("raw_value", "")),
            expected_value=str(f.get("expected_value", "")),
        )
        for f in failures
    ]
    return FailureArtifact(
        run_id=run_id,
        failures=entries,
    )
