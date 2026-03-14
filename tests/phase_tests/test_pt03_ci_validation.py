"""
Phase-test 3 — CI Pipeline Validation

Goal: Verify Phylax exit code conventions work correctly for CI integration.
  exit 0 = all PASS
  exit 1 = any FAIL
  exit 2 = SYSTEM ERROR

Note: Actual CI environments (GitHub Actions, GitLab CI, Docker) are documented
as manual checklists. This test validates the underlying logic programmatically.
"""
import pytest
from phylax import Dataset, DatasetCase, run_dataset, diff_runs


class TestExitCodeConventions:
    """PT3.1: Dataset results translate to correct exit code semantics."""

    def test_all_pass_means_exit_0(self):
        """When all cases pass, CI should get exit 0."""
        ds = Dataset(
            dataset="ci_pass_test",
            cases=[
                DatasetCase(input="hello", expectations={"must_include": ["hello"]}),
                DatasetCase(input="world", expectations={"must_include": ["world"]}),
            ],
        )
        result = run_dataset(ds, lambda x: f"Response: {x}")
        assert result.all_passed
        # Exit code 0 semantic: all_passed == True
        exit_code = 0 if result.all_passed else 1
        assert exit_code == 0

    def test_any_fail_means_exit_1(self):
        """When any case fails, CI should get exit 1."""
        ds = Dataset(
            dataset="ci_fail_test",
            cases=[
                DatasetCase(input="hello", expectations={"must_include": ["goodbye"]}),
            ],
        )
        result = run_dataset(ds, lambda x: f"Response: {x}")
        assert not result.all_passed
        exit_code = 0 if result.all_passed else 1
        assert exit_code == 1

    def test_mixed_results_exit_1(self):
        """Even one failure in a batch means CI fails."""
        ds = Dataset(
            dataset="ci_mixed_test",
            cases=[
                DatasetCase(input="pass_case", expectations={"must_include": ["pass_case"]}),
                DatasetCase(input="fail_case", expectations={"must_include": ["nonexistent"]}),
            ],
        )
        result = run_dataset(ds, lambda x: f"Response: {x}")
        assert not result.all_passed
        assert result.passed_cases == 1
        assert result.failed_cases == 1


class TestCIReporting:
    """PT3.2: Reports must be CI-friendly."""

    def test_report_has_pass_fail_counts(self):
        from phylax import format_report
        ds = Dataset(
            dataset="ci_report_test",
            cases=[
                DatasetCase(input="a", expectations={"must_include": ["a"]}),
                DatasetCase(input="b", expectations={"must_include": ["z"]}),
            ],
        )
        result = run_dataset(ds, lambda x: f"Response: {x}")
        report = format_report(result)
        assert "pass" in report.lower() or "PASS" in report
        assert "fail" in report.lower() or "FAIL" in report

    def test_json_report_machine_parseable(self):
        import json
        from phylax import format_json_report
        ds = Dataset(
            dataset="ci_json_test",
            cases=[
                DatasetCase(input="a", expectations={"must_include": ["a"]}),
            ],
        )
        result = run_dataset(ds, lambda x: f"Response: {x}")
        j = json.loads(format_json_report(result))
        assert "passed_cases" in j
        assert "failed_cases" in j
        assert "passed_cases" in j
        assert "failed_cases" in j


class TestCIDiffRegression:
    """PT3.3: Diff results must be CI-compatible."""

    def test_diff_regressions_exits_1(self):
        """If diff shows regressions, CI should fail."""
        ds = Dataset(
            dataset="ci_diff_test",
            cases=[
                DatasetCase(input="hello", expectations={"must_include": ["hello"]}),
            ],
        )
        r_pass = run_dataset(ds, lambda x: f"hello from system")
        r_fail = run_dataset(ds, lambda x: f"goodbye from system")
        diff = diff_runs(r_pass, r_fail)
        exit_code = 0 if not diff.has_regressions else 1
        assert exit_code == 1

    def test_diff_no_regressions_exits_0(self):
        ds = Dataset(
            dataset="ci_diff_ok_test",
            cases=[
                DatasetCase(input="hello", expectations={"must_include": ["hello"]}),
            ],
        )
        r1 = run_dataset(ds, lambda x: f"hello from {x}")
        r2 = run_dataset(ds, lambda x: f"hello from {x}")
        diff = diff_runs(r1, r2)
        exit_code = 0 if not diff.has_regressions else 1
        assert exit_code == 0
