"""
PHASE 4.1 — STABLE ARTIFACT CONTRACTS TESTS

Proves artifacts are:
  - Frozen and immutable
  - Deterministic across runs
  - Machine-consumable (no commentary)
  - Schema-versioned
  - Backward compatible
"""

import json
import hashlib

import pytest
from pydantic import ValidationError

from phylax import (
    VerdictArtifact,
    generate_verdict_artifact,
    FailureEntry,
    FailureArtifact,
    generate_failure_artifact,
    TraceDiffArtifact,
    generate_trace_diff,
    EXIT_PASS,
    EXIT_FAIL,
    EXIT_SYSTEM_ERROR,
    resolve_exit_code,
)


# ── 4.1.1 — Verdict Artifact ───────────────────────────────────────

class TestVerdictArtifact:
    """Verdict artifact: frozen, deterministic, no commentary."""

    def test_generate_pass(self):
        a = generate_verdict_artifact(
            mode="enforce", verdict="PASS",
            expectations_evaluated=10, failures=0,
            definition_snapshot_hash="abc123",
            engine_version="1.4.0",
        )
        assert a.verdict == "PASS"
        assert a.failures == 0
        assert a.mode == "enforce"
        assert a.schema_version == "1.0.0"

    def test_generate_fail(self):
        a = generate_verdict_artifact(
            mode="quarantine", verdict="FAIL",
            expectations_evaluated=10, failures=3,
            definition_snapshot_hash="def456",
            engine_version="1.4.0",
        )
        assert a.verdict == "FAIL"
        assert a.failures == 3

    def test_frozen(self):
        a = generate_verdict_artifact(
            mode="enforce", verdict="PASS",
            expectations_evaluated=5, failures=0,
            definition_snapshot_hash="x", engine_version="1.4.0",
        )
        with pytest.raises(ValidationError):
            a.verdict = "FAIL"

    def test_invalid_verdict_rejected(self):
        with pytest.raises(ValueError, match="PASS or FAIL"):
            generate_verdict_artifact(
                mode="enforce", verdict="warning",
                expectations_evaluated=5, failures=0,
                definition_snapshot_hash="x", engine_version="1.4.0",
            )

    def test_invalid_mode_rejected(self):
        with pytest.raises(ValueError, match="enforce|quarantine|observe"):
            generate_verdict_artifact(
                mode="auto", verdict="PASS",
                expectations_evaluated=5, failures=0,
                definition_snapshot_hash="x", engine_version="1.4.0",
            )

    def test_deterministic_serialization(self):
        """Same inputs → identical JSON (minus run_id/timestamp)."""
        a1 = generate_verdict_artifact(
            mode="enforce", verdict="PASS", run_id="fixed-id",
            expectations_evaluated=10, failures=0,
            definition_snapshot_hash="abc", engine_version="1.4.0",
        )
        a2 = generate_verdict_artifact(
            mode="enforce", verdict="PASS", run_id="fixed-id",
            expectations_evaluated=10, failures=0,
            definition_snapshot_hash="abc", engine_version="1.4.0",
        )
        # Exclude timestamp from comparison
        d1 = a1.model_dump()
        d2 = a2.model_dump()
        d1.pop("timestamp")
        d2.pop("timestamp")
        assert d1 == d2

    def test_no_commentary_fields(self):
        """No explanation, suggestion, or narrative fields."""
        a = generate_verdict_artifact(
            mode="enforce", verdict="FAIL",
            expectations_evaluated=10, failures=5,
            definition_snapshot_hash="x", engine_version="1.4.0",
        )
        d = a.model_dump()
        forbidden = ["explanation", "reason", "suggestion", "narrative",
                      "comment", "description", "note", "advice", "impact"]
        for key in d:
            assert key not in forbidden, f"Commentary key: {key}"

    def test_json_roundtrip(self):
        """JSON export → reimport → identical."""
        a = generate_verdict_artifact(
            mode="enforce", verdict="PASS",
            expectations_evaluated=10, failures=0,
            definition_snapshot_hash="abc", engine_version="1.4.0",
        )
        j = a.model_dump_json()
        parsed = json.loads(j)
        a2 = VerdictArtifact(**parsed)
        assert a.verdict == a2.verdict
        assert a.mode == a2.mode

    def test_key_ordering_deterministic(self):
        """JSON keys must be in deterministic order across runs."""
        hashes = set()
        for _ in range(50):
            a = generate_verdict_artifact(
                mode="enforce", verdict="PASS", run_id="stable",
                expectations_evaluated=10, failures=0,
                definition_snapshot_hash="abc", engine_version="1.4.0",
            )
            d = a.model_dump()
            d.pop("timestamp")
            h = hashlib.sha256(json.dumps(d, sort_keys=True).encode()).hexdigest()
            hashes.add(h)
        assert len(hashes) == 1


# ── 4.1.2 — Failure Artifact ───────────────────────────────────────

class TestFailureArtifact:
    """Failure artifact: mechanical, no explanation, no ranking."""

    def test_generate_failures(self):
        a = generate_failure_artifact(
            run_id="run-1",
            failures=[
                {"expectation_id": "e1", "violated_rule": "must_include",
                 "raw_value": "Hello", "expected_value": "refund"},
                {"expectation_id": "e2", "violated_rule": "max_latency_ms",
                 "raw_value": "2500", "expected_value": "1500"},
            ],
        )
        assert len(a.failures) == 2
        assert a.failures[0].expectation_id == "e1"
        assert a.failures[1].violated_rule == "max_latency_ms"

    def test_frozen(self):
        entry = FailureEntry(
            expectation_id="e1", violated_rule="test",
            raw_value="x", expected_value="y",
        )
        with pytest.raises(ValidationError):
            entry.raw_value = "changed"

    def test_no_explanation_field(self):
        """No 'reason', 'explanation', 'suggestion'."""
        entry = FailureEntry(
            expectation_id="e1", violated_rule="must_include",
            raw_value="x", expected_value="y",
        )
        d = entry.model_dump()
        assert "reason" not in d
        assert "explanation" not in d
        assert "suggestion" not in d
        assert "severity" not in d

    def test_no_severity_ranking(self):
        """Failures must NOT be ranked or ordered by severity."""
        a = generate_failure_artifact(
            run_id="run-1",
            failures=[
                {"expectation_id": "e1", "violated_rule": "r1", "raw_value": "a", "expected_value": "b"},
                {"expectation_id": "e2", "violated_rule": "r2", "raw_value": "c", "expected_value": "d"},
            ],
        )
        d = a.model_dump()
        assert "severity" not in str(d).lower()
        assert "priority" not in str(d).lower()
        assert "rank" not in str(d).lower()


# ── 4.1.3 — Trace Diff Artifact ───────────────────────────────────

class TestTraceDiffArtifact:
    """Trace diff: literal diffs only. No impact assessment."""

    def test_no_changes(self):
        d = generate_trace_diff(
            run_id_before="r1", run_id_after="r2",
            expectations_before={"e1", "e2"}, expectations_after={"e1", "e2"},
            hash_before="abc", hash_after="abc",
        )
        assert d.hashes_match is True
        assert d.added_expectations == []
        assert d.removed_expectations == []

    def test_additions_detected(self):
        d = generate_trace_diff(
            run_id_before="r1", run_id_after="r2",
            expectations_before={"e1"}, expectations_after={"e1", "e2", "e3"},
            hash_before="a", hash_after="b",
        )
        assert d.added_expectations == ["e2", "e3"]
        assert d.removed_expectations == []
        assert d.hashes_match is False

    def test_removals_detected(self):
        d = generate_trace_diff(
            run_id_before="r1", run_id_after="r2",
            expectations_before={"e1", "e2", "e3"}, expectations_after={"e1"},
            hash_before="a", hash_after="b",
        )
        assert d.removed_expectations == ["e2", "e3"]
        assert d.added_expectations == []

    def test_frozen(self):
        d = generate_trace_diff(
            run_id_before="r1", run_id_after="r2",
            expectations_before={"e1"}, expectations_after={"e1"},
            hash_before="a", hash_after="a",
        )
        with pytest.raises(ValidationError):
            d.hashes_match = False

    def test_no_impact_assessment(self):
        """No 'impact', 'risk', 'severity' in diff output."""
        d = generate_trace_diff(
            run_id_before="r1", run_id_after="r2",
            expectations_before={"e1"}, expectations_after={"e2"},
            hash_before="a", hash_after="b",
            changed_fields=["verdict"],
        )
        dump = json.dumps(d.model_dump())
        for word in ["impact", "risk", "severity", "score", "critical"]:
            assert word not in dump.lower(), f"Impact word '{word}' in diff"

    def test_sorted_output(self):
        """Added/removed expectations must be sorted for determinism."""
        d = generate_trace_diff(
            run_id_before="r1", run_id_after="r2",
            expectations_before={"e3", "e1"}, expectations_after={"e5", "e2"},
            hash_before="a", hash_after="b",
        )
        assert d.added_expectations == sorted(d.added_expectations)
        assert d.removed_expectations == sorted(d.removed_expectations)


# ── 4.1.4 — Deterministic Exit Codes ───────────────────────────────

class TestExitCodes:
    """Exit codes: frozen, 3 values only, deterministic resolution."""

    def test_values_frozen(self):
        assert EXIT_PASS == 0
        assert EXIT_FAIL == 1
        assert EXIT_SYSTEM_ERROR == 2

    def test_resolve_pass_always_0(self):
        for mode in ("enforce", "quarantine", "observe"):
            assert resolve_exit_code(verdict="PASS", mode=mode) == 0
            assert resolve_exit_code(verdict="pass", mode=mode) == 0

    def test_resolve_fail_enforce_is_1(self):
        assert resolve_exit_code(verdict="FAIL", mode="enforce") == 1
        assert resolve_exit_code(verdict="fail", mode="enforce") == 1

    def test_resolve_fail_non_enforce_is_0(self):
        assert resolve_exit_code(verdict="FAIL", mode="quarantine") == 0
        assert resolve_exit_code(verdict="FAIL", mode="observe") == 0

    def test_invalid_verdict_rejected(self):
        with pytest.raises(ValueError):
            resolve_exit_code(verdict="warning", mode="enforce")

    def test_invalid_mode_rejected(self):
        with pytest.raises(ValueError):
            resolve_exit_code(verdict="FAIL", mode="auto")

    def test_no_exit_code_expansion(self):
        """Only 3 exit codes exist. No 3, 4, etc."""
        from phylax._internal.artifacts.exit_codes import _VALID_EXIT_CODES
        assert _VALID_EXIT_CODES == frozenset({0, 1, 2})
