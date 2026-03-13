"""
Phase-test 2 — Artifact Determinism

Goal: Axis 4 artifacts must be fully reproducible.
Generate the same artifacts twice and compare — files must be byte-identical
(excluding known-variable fields like run_id and timestamp).
"""
import json
import pytest

from phylax import (
    generate_verdict_artifact,
    generate_failure_artifact,
    generate_trace_diff,
    Dataset,
    DatasetCase,
    run_dataset,
    diff_runs,
    format_diff_json,
    format_report,
    format_json_report,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fixed_verdict(**kwargs):
    """Generate verdict artifact with controlled inputs."""
    defaults = dict(
        mode="enforce",
        verdict="FAIL",
        expectations_evaluated=10,
        failures=3,
        definition_snapshot_hash="sha256:abc123def456",
        engine_version="1.6.3",
        run_id="fixed-run-id-001",
    )
    defaults.update(kwargs)
    return generate_verdict_artifact(**defaults)


def _deterministic_func(prompt: str) -> str:
    return f"Response to: {prompt}"


# ---------------------------------------------------------------------------
# Tests — Verdict Artifact
# ---------------------------------------------------------------------------

class TestVerdictArtifactDeterminism:
    """PT2.1: VerdictArtifact must serialize identically."""

    def test_same_inputs_produce_same_artifact(self):
        a = _fixed_verdict()
        b = _fixed_verdict()
        # Compare all fields except timestamp (generated at call time)
        assert a.schema_version == b.schema_version
        assert a.run_id == b.run_id
        assert a.mode == b.mode
        assert a.verdict == b.verdict
        assert a.expectations_evaluated == b.expectations_evaluated
        assert a.failures == b.failures
        assert a.definition_snapshot_hash == b.definition_snapshot_hash
        assert a.engine_version == b.engine_version

    def test_json_serialization_deterministic(self):
        a = _fixed_verdict()
        b = _fixed_verdict()
        # JSON keys should be in same order
        json_a = a.model_dump_json(indent=2)
        json_b = b.model_dump_json(indent=2)
        # Remove timestamp for comparison (it changes between calls)
        dict_a = json.loads(json_a)
        dict_b = json.loads(json_b)
        del dict_a["timestamp"]
        del dict_b["timestamp"]
        assert dict_a == dict_b

    def test_pass_verdict_deterministic(self):
        a = _fixed_verdict(verdict="PASS", failures=0)
        b = _fixed_verdict(verdict="PASS", failures=0)
        assert a.verdict == b.verdict == "PASS"
        assert a.failures == b.failures == 0

    def test_field_ordering_consistent(self):
        a = _fixed_verdict()
        keys_a = list(a.model_dump().keys())
        b = _fixed_verdict()
        keys_b = list(b.model_dump().keys())
        assert keys_a == keys_b, "Field ordering changed between generations"


# ---------------------------------------------------------------------------
# Tests — Failure Artifact
# ---------------------------------------------------------------------------

class TestFailureArtifactDeterminism:
    """PT2.2: FailureArtifact must be reproducible."""

    def test_failure_artifact_deterministic(self):
        failures_data = [
            {"expectation_id": "exp-001", "violated_rule": "must_include",
             "raw_value": "goodbye", "expected_value": "hello"},
            {"expectation_id": "exp-002", "violated_rule": "max_latency_ms",
             "raw_value": "6000", "expected_value": "5000"},
        ]
        a = generate_failure_artifact(run_id="fixed-001", failures=failures_data)
        b = generate_failure_artifact(run_id="fixed-001", failures=failures_data)
        assert a.model_dump() == b.model_dump()

    def test_multiple_failures_same_order(self):
        failures_data = [
            {"expectation_id": "exp-001", "violated_rule": "must_include",
             "raw_value": "goodbye", "expected_value": "hello"},
        ]
        artifacts = [
            generate_failure_artifact(run_id="fixed-001", failures=failures_data)
            for _ in range(5)
        ]
        for artifact in artifacts:
            assert artifact.failures[0].violated_rule == "must_include"

    def test_failure_field_ordering(self):
        failures_data = [
            {"expectation_id": "exp-001", "violated_rule": "must_include",
             "raw_value": "val", "expected_value": "exp"},
        ]
        a = generate_failure_artifact(run_id="fixed-001", failures=failures_data)
        b = generate_failure_artifact(run_id="fixed-001", failures=failures_data)
        keys_a = list(a.model_dump().keys())
        keys_b = list(b.model_dump().keys())
        assert keys_a == keys_b


# ---------------------------------------------------------------------------
# Tests — Trace Diff
# ---------------------------------------------------------------------------

class TestTraceDiffDeterminism:
    """PT2.3: TraceDiff must be reproducible."""

    def test_trace_diff_deterministic(self):
        a = generate_trace_diff(
            run_id_before="run-aaa",
            run_id_after="run-bbb",
            expectations_before={"exp-001", "exp-002"},
            expectations_after={"exp-002", "exp-003"},
            hash_before="sha256:111",
            hash_after="sha256:222",
        )
        b = generate_trace_diff(
            run_id_before="run-aaa",
            run_id_after="run-bbb",
            expectations_before={"exp-001", "exp-002"},
            expectations_after={"exp-002", "exp-003"},
            hash_before="sha256:111",
            hash_after="sha256:222",
        )
        assert a.model_dump() == b.model_dump()

    def test_trace_diff_added_removed_sorted(self):
        diff = generate_trace_diff(
            run_id_before="run-aaa",
            run_id_after="run-bbb",
            expectations_before={"c", "a"},
            expectations_after={"b", "d"},
            hash_before="sha256:111",
            hash_after="sha256:222",
        )
        # Added and removed should be sorted for determinism
        assert diff.added_expectations == sorted(diff.added_expectations)
        assert diff.removed_expectations == sorted(diff.removed_expectations)

    def test_trace_diff_hash_mismatch_detected(self):
        diff = generate_trace_diff(
            run_id_before="run-aaa",
            run_id_after="run-bbb",
            expectations_before=set(),
            expectations_after=set(),
            hash_before="sha256:111",
            hash_after="sha256:222",
        )
        assert diff.hashes_match is False


# ---------------------------------------------------------------------------
# Tests — Dataset Report Determinism
# ---------------------------------------------------------------------------

class TestDatasetReportDeterminism:
    """PT2.4: Dataset reports must be reproducible (excluding run_id)."""

    def test_format_report_deterministic(self):
        dataset = Dataset(
            dataset="artifact_test",
            cases=[
                DatasetCase(input="test", expectations={"must_include": ["test"]}),
            ],
        )
        a = run_dataset(dataset, _deterministic_func)
        b = run_dataset(dataset, _deterministic_func)

        report_a = format_report(a)
        report_b = format_report(b)
        # Reports differ by run_id and latency — filter those lines
        def _stable_lines(report):
            return [
                l for l in report.splitlines()
                if "run_id" not in l.lower()
                and "run id" not in l.lower()
                and "ms" not in l.lower()
            ]
        assert _stable_lines(report_a) == _stable_lines(report_b)

    def test_format_json_deterministic(self):
        dataset = Dataset(
            dataset="artifact_test",
            cases=[
                DatasetCase(input="test", expectations={"must_include": ["test"]}),
            ],
        )
        a = run_dataset(dataset, _deterministic_func)
        b = run_dataset(dataset, _deterministic_func)

        json_a = json.loads(format_json_report(a))
        json_b = json.loads(format_json_report(b))
        # Remove run_id (uuid) and latency (timing)
        del json_a["run_id"]
        del json_b["run_id"]
        for r in json_a["results"]:
            del r["latency_ms"]
        for r in json_b["results"]:
            del r["latency_ms"]
        assert json_a == json_b

    def test_diff_report_deterministic(self):
        dataset = Dataset(
            dataset="diff_test",
            cases=[
                DatasetCase(
                    input="hello",
                    name="case_a",
                    expectations={"must_include": ["hello"]},
                ),
            ],
        )
        result_a = run_dataset(dataset, _deterministic_func)
        result_b = run_dataset(dataset, _deterministic_func)
        diff1 = diff_runs(result_a, result_b)
        diff2 = diff_runs(result_a, result_b)

        json1 = json.loads(format_diff_json(diff1))
        json2 = json.loads(format_diff_json(diff2))
        # Remove variable fields
        for field in ["run_id_before", "run_id_after"]:
            json1.pop(field, None)
            json2.pop(field, None)
        assert json1 == json2
