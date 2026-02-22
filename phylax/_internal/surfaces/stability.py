"""
Cross-Run Stability Enforcement (Axis 2 Phase 2.4)

Enforce invariants across executions for deterministic regression detection.

Surface: Snapshot comparison:
    current: { version_id, structured_output, tool_trace, metadata }
    baseline: { version_id, structured_output, tool_trace, metadata }

Enforcement types:
1. Exact Stability — field must not change / hash must match
2. Allowed Drift — user-whitelisted fields may change, all others must be stable

What is forbidden:
- Trend detection
- Statistical comparison
- Drift scoring
- Auto-updating baselines
- Probabilistic tolerance
"""

import hashlib
import json
from typing import Any, Literal, Optional

from phylax._internal.surfaces.surface import (
    Surface,
    SurfaceAdapter,
    SurfaceRule,
    SurfaceRuleResult,
)
from phylax._internal.surfaces.structured import _resolve_path


# ─── Utility ─────────────────────────────────────────────────────────────────

def _deterministic_hash(data: Any) -> str:
    """
    Compute a deterministic hash of any JSON-serializable data.

    Uses sorted keys and no indentation for canonical form.
    """
    serialized = json.dumps(data, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def _get_nested_value(data: Any, path: str) -> tuple[bool, Any]:
    """Resolve a dot-notation path. Reuses the structured path resolver."""
    return _resolve_path(data, path)


def _set_nested_value(data: dict, path: str, value: Any) -> dict:
    """
    Set a value at a dot-notation path in a dict (returns a copy).
    Used for masking drift fields before comparison.
    """
    import copy
    result = copy.deepcopy(data)
    parts = path.split(".")
    current = result
    for part in parts[:-1]:
        if isinstance(current, dict) and part in current:
            current = current[part]
        elif isinstance(current, list):
            try:
                idx = int(part)
                current = current[idx]
            except (ValueError, IndexError):
                return result
        else:
            return result

    last_part = parts[-1]
    if isinstance(current, dict):
        current[last_part] = value
    elif isinstance(current, list):
        try:
            idx = int(last_part)
            current[idx] = value
        except (ValueError, IndexError):
            pass

    return result


# ─── Rules ───────────────────────────────────────────────────────────────────

class ExactStabilityRule(SurfaceRule):
    """
    A specific field must not change between baseline and current.

    Or: the entire payload hash must match (if path is None).

    No tolerance. No probabilistic matching. Exact only.
    """

    name = "exact_stability"

    def __init__(self, path: Optional[str] = None):
        """
        Args:
            path: Dot-notation path to check for stability.
                  If None, compare entire payload hash.
        """
        self.path = path

    def evaluate(self, surface: Surface) -> SurfaceRuleResult:
        payload = surface.raw_payload
        if not isinstance(payload, dict):
            return SurfaceRuleResult(
                passed=False,
                rule_name=self.name,
                violation_message="raw_payload must be a dict with 'baseline' and 'current'",
            )

        baseline = payload.get("baseline")
        current = payload.get("current")

        if baseline is None or current is None:
            return SurfaceRuleResult(
                passed=False,
                rule_name=self.name,
                violation_message="payload must contain 'baseline' and 'current'",
            )

        if self.path is None:
            # Compare entire hash
            baseline_hash = _deterministic_hash(baseline)
            current_hash = _deterministic_hash(current)
            if baseline_hash != current_hash:
                return SurfaceRuleResult(
                    passed=False,
                    rule_name=self.name,
                    violation_message=(
                        f"payload hash changed: baseline={baseline_hash[:16]}… "
                        f"current={current_hash[:16]}…"
                    ),
                )
        else:
            # Compare specific field
            b_exists, b_val = _get_nested_value(baseline, self.path)
            c_exists, c_val = _get_nested_value(current, self.path)

            if not b_exists and not c_exists:
                return SurfaceRuleResult(passed=True, rule_name=self.name)

            if b_exists != c_exists:
                return SurfaceRuleResult(
                    passed=False,
                    rule_name=self.name,
                    violation_message=(
                        f"path '{self.path}': field existence changed "
                        f"(baseline={'exists' if b_exists else 'missing'}, "
                        f"current={'exists' if c_exists else 'missing'})"
                    ),
                )

            if type(b_val) != type(c_val) or b_val != c_val:
                return SurfaceRuleResult(
                    passed=False,
                    rule_name=self.name,
                    violation_message=(
                        f"path '{self.path}': value changed from "
                        f"{b_val!r} to {c_val!r}"
                    ),
                )

        return SurfaceRuleResult(passed=True, rule_name=self.name)


class AllowedDriftRule(SurfaceRule):
    """
    Only user-whitelisted fields may change between runs.
    All other fields must remain stable.

    No auto-updating baselines. No tolerance. Explicit whitelist only.
    """

    name = "allowed_drift"

    def __init__(self, allowed_fields: list[str]):
        """
        Args:
            allowed_fields: List of dot-notation paths that are allowed to change
                           (e.g. ["timestamp", "metadata.execution_id"])
        """
        self.allowed_fields = allowed_fields

    def evaluate(self, surface: Surface) -> SurfaceRuleResult:
        payload = surface.raw_payload
        if not isinstance(payload, dict):
            return SurfaceRuleResult(
                passed=False,
                rule_name=self.name,
                violation_message="raw_payload must be a dict with 'baseline' and 'current'",
            )

        baseline = payload.get("baseline")
        current = payload.get("current")

        if baseline is None or current is None:
            return SurfaceRuleResult(
                passed=False,
                rule_name=self.name,
                violation_message="payload must contain 'baseline' and 'current'",
            )

        # Mask allowed drift fields with a sentinel before comparison
        sentinel = "__DRIFT_ALLOWED__"
        masked_baseline = baseline
        masked_current = current

        if isinstance(baseline, dict) and isinstance(current, dict):
            import copy
            masked_baseline = copy.deepcopy(baseline)
            masked_current = copy.deepcopy(current)

            for field in self.allowed_fields:
                masked_baseline = _set_nested_value(masked_baseline, field, sentinel)
                masked_current = _set_nested_value(masked_current, field, sentinel)

        baseline_hash = _deterministic_hash(masked_baseline)
        current_hash = _deterministic_hash(masked_current)

        if baseline_hash != current_hash:
            return SurfaceRuleResult(
                passed=False,
                rule_name=self.name,
                violation_message=(
                    f"non-whitelisted fields changed "
                    f"(allowed drift: {self.allowed_fields})"
                ),
            )

        return SurfaceRuleResult(passed=True, rule_name=self.name)


# ─── Stability Surface Adapter ──────────────────────────────────────────────

class StabilitySurfaceAdapter(SurfaceAdapter):
    """
    Adapter for cross-run stability snapshots.

    Produces a Surface with type="cross_run_snapshot" containing:
        { "baseline": <snapshot>, "current": <snapshot> }

    Each snapshot should be: { version_id, structured_output, tool_trace, metadata }

    No auto-updating. Baselines are explicit and immutable.

    Usage:
        adapter = StabilitySurfaceAdapter()
        surface = adapter.adapt(
            baseline={"version_id": "v1", "structured_output": {...}, ...},
            current={"version_id": "v2", "structured_output": {...}, ...},
        )
    """

    surface_type = "cross_run_snapshot"

    def adapt(self, raw_data: Any = None, **kwargs) -> Surface:
        """
        Convert baseline+current snapshots into a Surface.

        Args:
            raw_data: Not used (use baseline/current kwargs instead).
                      If a dict with 'baseline'+'current', used directly.
            **kwargs: baseline (dict), current (dict), metadata (dict)

        Returns:
            Surface with type="cross_run_snapshot"
        """
        metadata = kwargs.get("metadata", {})

        if isinstance(raw_data, dict) and "baseline" in raw_data and "current" in raw_data:
            payload = raw_data
        else:
            baseline = kwargs.get("baseline", raw_data)
            current = kwargs.get("current", {})
            payload = {"baseline": baseline, "current": current}

        return Surface(
            type="cross_run_snapshot",
            raw_payload=payload,
            metadata=metadata,
        )
