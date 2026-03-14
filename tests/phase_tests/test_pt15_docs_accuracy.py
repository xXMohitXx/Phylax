"""
Phase-test 15 — Documentation Accuracy

Goal: Verify key code examples from documentation actually work.
"""
import json
import pytest
from phylax import (
    Dataset, DatasetCase, run_dataset,
    diff_runs, format_diff_report, format_diff_json,
    simulate_upgrade, format_simulation_report,
    generate_verdict_artifact,
    safety_pack, apply_pack,
    format_report, format_json_report,
)


class TestDocExample_BasicDataset:
    """PT15.1: Basic dataset example from docs must work."""

    def test_create_and_run_dataset(self):
        dataset = Dataset(
            dataset="support_requests",
            cases=[
                DatasetCase(
                    input="How do I get a refund?",
                    name="refund_query",
                    expectations={
                        "must_include": ["refund"],
                        "must_not_include": ["lawsuit"],
                        "min_tokens": 5,
                    },
                ),
            ],
        )
        def my_handler(prompt):
            return "You can request a refund within 30 days of purchase."

        result = run_dataset(dataset, my_handler)
        assert result.total_cases == 1
        assert result.all_passed


class TestDocExample_DiffRuns:
    """PT15.2: Diff example from docs must work."""

    def test_diff_two_runs(self):
        dataset = Dataset(
            dataset="test",
            cases=[
                DatasetCase(input="hello", expectations={"must_include": ["hello"]}),
            ],
        )
        result_a = run_dataset(dataset, lambda x: f"hello {x}")
        result_b = run_dataset(dataset, lambda x: f"hello {x}")
        diff = diff_runs(result_a, result_b)
        report = format_diff_report(diff)
        assert isinstance(report, str)
        j = json.loads(format_diff_json(diff))
        assert "regressions" in j


class TestDocExample_Simulator:
    """PT15.3: Model upgrade simulator example."""

    def test_simulate_upgrade(self):
        dataset = Dataset(
            dataset="test",
            cases=[
                DatasetCase(input="hi", expectations={"must_include": ["hi"]}),
            ],
        )
        baseline = lambda x: f"hi from baseline: {x}"
        candidate = lambda x: f"hi from candidate: {x}"
        sim = simulate_upgrade(dataset, baseline, candidate)
        report = format_simulation_report(sim)
        assert sim.safe_to_upgrade
        assert isinstance(report, str)


class TestDocExample_VerdictArtifact:
    """PT15.4: Verdict artifact example."""

    def test_generate_verdict(self):
        verdict = generate_verdict_artifact(
            mode="enforce",
            verdict="PASS",
            expectations_evaluated=5,
            failures=0,
            definition_snapshot_hash="sha256:abc123",
            engine_version="1.6.3",
            run_id="test-run-001",
        )
        assert verdict.verdict == "PASS"
        assert verdict.failures == 0
        d = verdict.model_dump()
        assert "schema_version" in d


class TestDocExample_GuardrailPacks:
    """PT15.5: Guardrail pack example."""

    def test_apply_safety_pack(self):
        pack = safety_pack()
        custom_exp = {"must_include": ["helpful"]}
        merged = apply_pack(pack, custom_exp)
        assert isinstance(merged, dict)
        assert "helpful" in merged.get("must_include", [])


class TestDocExample_Reports:
    """PT15.6: Report formatting examples."""

    def test_text_report(self):
        ds = Dataset(
            dataset="report_test",
            cases=[
                DatasetCase(input="test", expectations={"must_include": ["test"]}),
            ],
        )
        result = run_dataset(ds, lambda x: f"test response: {x}")
        report = format_report(result)
        assert isinstance(report, str)
        assert len(report) > 0

    def test_json_report(self):
        ds = Dataset(
            dataset="json_test",
            cases=[
                DatasetCase(input="test", expectations={"must_include": ["test"]}),
            ],
        )
        result = run_dataset(ds, lambda x: f"test response: {x}")
        j = json.loads(format_json_report(result))
        assert "dataset_name" in j
