"""
4.1.1 — Verdict Artifact Specification

Frozen, deterministic, machine-consumable verdict output.

Constraints:
  - No optional fields without version bump.
  - No semantic additions.
  - Deterministic ordering of keys.
  - No human commentary.
"""

import json
import uuid
from datetime import datetime, timezone

from pydantic import BaseModel, Field


class VerdictArtifact(BaseModel):
    """
    Frozen verdict output contract.
    
    Every field is mechanical fact. No commentary. No interpretation.
    Schema changes require a MAJOR version bump.
    """
    model_config = {"frozen": True}

    schema_version: str = Field(default="1.0.0", description="Artifact schema version")
    run_id: str = Field(description="Unique run identifier")
    timestamp: str = Field(description="ISO-8601 UTC timestamp")
    mode: str = Field(description="Enforcement mode: enforce|quarantine|observe")
    verdict: str = Field(description="PASS or FAIL — only two values, ever")
    expectations_evaluated: int = Field(description="Total expectations evaluated")
    failures: int = Field(description="Total failures")
    definition_snapshot_hash: str = Field(description="SHA-256 hash of all expectation definitions")
    engine_version: str = Field(description="Phylax engine version that produced this")


def generate_verdict_artifact(
    *,
    mode: str,
    verdict: str,
    expectations_evaluated: int,
    failures: int,
    definition_snapshot_hash: str,
    engine_version: str,
    run_id: str | None = None,
) -> VerdictArtifact:
    """
    Generate a frozen verdict artifact.
    
    Pure factory function. No side effects. No network calls.
    """
    if verdict not in ("PASS", "FAIL"):
        raise ValueError(f"Verdict must be PASS or FAIL, got: {verdict}")
    if mode not in ("enforce", "quarantine", "observe"):
        raise ValueError(f"Mode must be enforce|quarantine|observe, got: {mode}")

    return VerdictArtifact(
        run_id=run_id or str(uuid.uuid4()),
        timestamp=datetime.now(timezone.utc).isoformat(),
        mode=mode,
        verdict=verdict,
        expectations_evaluated=expectations_evaluated,
        failures=failures,
        definition_snapshot_hash=definition_snapshot_hash,
        engine_version=engine_version,
    )
