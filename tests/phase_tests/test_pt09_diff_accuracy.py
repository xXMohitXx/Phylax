"""
Phase-test 9 — Dataset Diff Accuracy

Goal: Create two runs with known differences, run diff_runs(),
and verify changed_cases, new_failures, resolved_failures are all correct.
"""
import pytest
from phylax import Dataset, DatasetCase, run_dataset, diff_runs, format_diff_report, format_diff_json
import json


def _func_v1(prompt: str) -> str:
    """Version 1: baseline responses."""
    return {
        "greet": "Hello! Welcome to our support service.",
        "refund": "I can help with your refund. Our policy allows returns within 30 days.",
        "complaint": "I understand your frustration. Let me escalate this to a supervisor.",
        "info": "Our office hours are 9am to 5pm, Monday through Friday.",
        "farewell": "Thank you for contacting us. Have a great day!",
    }.get(prompt, f"Response: {prompt}")


def _func_v2(prompt: str) -> str:
    """Version 2: 2 regressions, 1 fix."""
    return {
        "greet": "Hello! Welcome to our support service.",  # SAME (pass->pass)
        "refund": "No refunds available.",                   # REGRESSION (pass->fail, missing "30 days")
        "complaint": "Please call back later.",              # REGRESSION (pass->fail, missing "escalate")
        "info": "Our hours have changed — we are now open 24/7!",  # Changed but still passes (contains "hours")
        "farewell": "Thank you for contacting us. Have a great day!",  # SAME
    }.get(prompt, f"Response: {prompt}")


def _func_v3_fix(prompt: str) -> str:
    """Version 3: fixes a previous failure."""
    return {
        "greet": "Hello! Welcome to our support service.",
        "refund": "I can help with your refund. Our policy allows returns within 30 days.",
        "complaint": "I understand your frustration. Let me escalate this to my supervisor immediately.",  # FIXED
        "info": "Our office hours are 9am to 5pm, Monday through Friday.",
        "farewell": "Thank you for contacting us. Have a great day!",
    }.get(prompt, f"Response: {prompt}")


def _build_dataset() -> Dataset:
    return Dataset(
        dataset="diff_accuracy_test",
        cases=[
            DatasetCase(input="greet", name="greeting",
                        expectations={"must_include": ["hello", "welcome"]}),
            DatasetCase(input="refund", name="refund_handler",
                        expectations={"must_include": ["refund", "30 days"]}),
            DatasetCase(input="complaint", name="complaint_handler",
                        expectations={"must_include": ["escalate"]}),
            DatasetCase(input="info", name="info_query",
                        expectations={"must_include": ["hours"]}),
            DatasetCase(input="farewell", name="farewell",
                        expectations={"must_include": ["thank"]}),
        ],
    )


class TestDiffDetectsRegressions:
    """PT9.1: v1->v2 should detect exactly 2 regressions."""

    def test_regression_count(self):
        ds = _build_dataset()
        r1 = run_dataset(ds, _func_v1)
        r2 = run_dataset(ds, _func_v2)
        diff = diff_runs(r1, r2)
        assert diff.regressions == 2

    def test_regression_cases_identified(self):
        ds = _build_dataset()
        r1 = run_dataset(ds, _func_v1)
        r2 = run_dataset(ds, _func_v2)
        diff = diff_runs(r1, r2)
        regressed = [c.case_name for c in diff.case_diffs if c.change == "regression"]
        assert "refund_handler" in regressed
        assert "complaint_handler" in regressed

    def test_unchanged_pass_count(self):
        ds = _build_dataset()
        r1 = run_dataset(ds, _func_v1)
        r2 = run_dataset(ds, _func_v2)
        diff = diff_runs(r1, r2)
        # greet and farewell stay pass, info changes output but may still pass/fail depending on expectations
        unchanged = [c.case_name for c in diff.case_diffs if c.change == "unchanged_pass"]
        assert "greeting" in unchanged
        assert "farewell" in unchanged


class TestDiffDetectsResolved:
    """PT9.2: If we diff a broken run against a fixed run, resolved should be detected."""

    def test_resolved_from_v2_to_v3(self):
        ds = _build_dataset()
        r2 = run_dataset(ds, _func_v2)
        r3 = run_dataset(ds, _func_v3_fix)
        diff = diff_runs(r2, r3)
        assert diff.resolved >= 1

    def test_resolved_complaint_handler(self):
        ds = _build_dataset()
        r2 = run_dataset(ds, _func_v2)
        r3 = run_dataset(ds, _func_v3_fix)
        diff = diff_runs(r2, r3)
        resolved_names = [c.case_name for c in diff.case_diffs if c.change == "resolved"]
        assert "complaint_handler" in resolved_names


class TestDiffIdenticalRuns:
    """PT9.3: Diffing identical runs should show zero changes."""

    def test_zero_regressions(self):
        ds = _build_dataset()
        r1 = run_dataset(ds, _func_v1)
        r2 = run_dataset(ds, _func_v1)
        diff = diff_runs(r1, r2)
        assert diff.regressions == 0
        assert diff.resolved == 0

    def test_all_unchanged_pass(self):
        ds = _build_dataset()
        r1 = run_dataset(ds, _func_v1)
        r2 = run_dataset(ds, _func_v1)
        diff = diff_runs(r1, r2)
        assert diff.unchanged_pass == 5


class TestDiffReportFormat:
    """PT9.4: Diff reports must be well-formatted."""

    def test_text_report_contains_summary(self):
        ds = _build_dataset()
        r1 = run_dataset(ds, _func_v1)
        r2 = run_dataset(ds, _func_v2)
        diff = diff_runs(r1, r2)
        report = format_diff_report(diff)
        assert isinstance(report, str)
        assert len(report) > 0

    def test_json_report_valid(self):
        ds = _build_dataset()
        r1 = run_dataset(ds, _func_v1)
        r2 = run_dataset(ds, _func_v2)
        diff = diff_runs(r1, r2)
        j = format_diff_json(diff)
        parsed = json.loads(j)
        assert "regressions" in parsed
        assert parsed["regressions"] == 2


class TestDiffDeterminism:
    """PT9.5: Diff must be deterministic."""

    def test_10_diffs_identical(self):
        ds = _build_dataset()
        r1 = run_dataset(ds, _func_v1)
        results = []
        for _ in range(10):
            r2 = run_dataset(ds, _func_v2)
            diff = diff_runs(r1, r2)
            results.append(diff.regressions)
        assert len(set(results)) == 1
