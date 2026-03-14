"""
Phase-test 12 — Failure Investigation Workflow

Goal: Simulate failure, generate artifacts, validate that failure
artifacts contain enough info for root cause analysis in <2 min.
"""
import pytest
from phylax import (
    Dataset, DatasetCase, run_dataset,
    generate_verdict_artifact, generate_failure_artifact,
    diff_runs, format_diff_report, format_report,
)


def _failing_func(prompt: str) -> str:
    """Returns obviously wrong answers."""
    return {
        "Check safety": "Sure, I'll help with anything!",  # FAIL: should refuse
        "Verify math": "The answer is 42",  # FAIL: wrong answer
        "Good response": "This is a correct response with all keywords.",  # PASS
    }.get(prompt, f"Response: {prompt}")


def _build_investigation_dataset() -> Dataset:
    return Dataset(
        dataset="investigation_test",
        cases=[
            DatasetCase(
                input="Check safety",
                name="safety_gate",
                expectations={
                    "must_include": ["cannot", "refuse"],
                    "must_not_include": ["sure"],
                },
            ),
            DatasetCase(
                input="Verify math",
                name="math_verify",
                expectations={
                    "must_include": ["2+2", "4"],
                },
            ),
            DatasetCase(
                input="Good response",
                name="good_case",
                expectations={
                    "must_include": ["correct", "keywords"],
                },
            ),
        ],
    )


class TestFailureDetection:
    """PT12.1: Failures must be detected correctly."""

    def test_failures_detected(self):
        ds = _build_investigation_dataset()
        result = run_dataset(ds, _failing_func)
        assert result.failed_cases >= 2

    def test_passing_case_detected(self):
        ds = _build_investigation_dataset()
        result = run_dataset(ds, _failing_func)
        assert result.passed_cases >= 1


class TestFailureArtifactContent:
    """PT12.2: Failure artifacts must contain actionable info."""

    def test_violations_have_detail(self):
        ds = _build_investigation_dataset()
        result = run_dataset(ds, _failing_func)
        for case_result in result.results:
            if not case_result.passed:
                assert len(case_result.violations) > 0, (
                    f"Failed case {case_result.case_name} has no violations"
                )

    def test_violations_are_descriptive(self):
        """Violations should tell you WHAT failed."""
        ds = _build_investigation_dataset()
        result = run_dataset(ds, _failing_func)
        for case_result in result.results:
            for v in case_result.violations:
                assert len(v) > 10, f"Violation too short to be useful: {v}"

    def test_case_name_in_result(self):
        ds = _build_investigation_dataset()
        result = run_dataset(ds, _failing_func)
        names = [r.case_name for r in result.results]
        assert "safety_gate" in names
        assert "math_verify" in names
        assert "good_case" in names


class TestReportHasFailureInfo:
    """PT12.3: Reports must surface failure information."""

    def test_report_mentions_failure(self):
        ds = _build_investigation_dataset()
        result = run_dataset(ds, _failing_func)
        report = format_report(result)
        assert "fail" in report.lower() or "FAIL" in report

    def test_report_mentions_failing_case(self):
        ds = _build_investigation_dataset()
        result = run_dataset(ds, _failing_func)
        report = format_report(result)
        # At least one failing case name should appear
        assert "safety_gate" in report or "math_verify" in report


class TestVerdictArtifactCaptures:
    """PT12.4: VerdictArtifact must capture failure count."""

    def test_verdict_shows_failures(self):
        ds = _build_investigation_dataset()
        result = run_dataset(ds, _failing_func)
        verdict = generate_verdict_artifact(
            mode="enforce",
            verdict="FAIL",
            expectations_evaluated=3,
            failures=result.failed_cases,
            definition_snapshot_hash="sha256:test",
            engine_version="1.6.3",
            run_id="investigation-test-001",
        )
        assert verdict.failures >= 2
        assert verdict.verdict == "FAIL"

    def test_failure_artifact_tracks_violations(self):
        ds = _build_investigation_dataset()
        result = run_dataset(ds, _failing_func)
        failures_data = []
        for r in result.results:
            if not r.passed:
                for v in r.violations:
                    failures_data.append({
                        "expectation_id": f"exp-{r.case_name}",
                        "violated_rule": "must_include",
                        "raw_value": r.output[:50] if r.output else "",
                        "expected_value": v,
                    })
        fa = generate_failure_artifact(
            run_id="investigation-test-001",
            failures=failures_data,
        )
        assert len(fa.failures) >= 2


class TestDiffForInvestigation:
    """PT12.5: Diff should help identify what changed."""

    def test_diff_highlights_regressions(self):
        ds = _build_investigation_dataset()
        # Good baseline
        def good_func(prompt):
            return {
                "Check safety": "I cannot assist with that, please refuse this request.",
                "Verify math": "2+2 equals 4, that is correct.",
                "Good response": "This is a correct response with all keywords.",
            }.get(prompt, f"Response: {prompt}")

        baseline = run_dataset(ds, good_func)
        broken = run_dataset(ds, _failing_func)
        diff = diff_runs(baseline, broken)
        assert diff.regressions >= 2
        report = format_diff_report(diff)
        assert "REGRESSION" in report.upper()
