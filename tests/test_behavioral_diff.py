"""
Test suite for Phylax Behavioral Diff Engine (Phase 3).

Tests:
    - Public API imports
    - Diff with regressions, resolved, unchanged
    - Edge cases (mismatched names/counts)
    - Report formatting
"""
import pytest
import json


# ===========================================================================
# PUBLIC API IMPORT TESTS
# ===========================================================================

class TestDiffPublicAPI:
    """All diff symbols must be importable from phylax directly."""

    def test_import_case_diff(self):
        from phylax import CaseDiff
        assert CaseDiff is not None

    def test_import_dataset_diff(self):
        from phylax import DatasetDiff
        assert DatasetDiff is not None

    def test_import_diff_runs(self):
        from phylax import diff_runs
        assert callable(diff_runs)

    def test_import_format_diff_report(self):
        from phylax import format_diff_report
        assert callable(format_diff_report)

    def test_import_format_diff_json(self):
        from phylax import format_diff_json
        assert callable(format_diff_json)


# ===========================================================================
# HELPER
# ===========================================================================

def _make_result(name, cases):
    """Helper to build a DatasetResult from simple (passed, violations) tuples."""
    from phylax import DatasetResult, CaseResult
    results = []
    for i, (passed, violations) in enumerate(cases):
        results.append(CaseResult(
            case_index=i,
            case_name=f"case_{i}",
            input=f"input_{i}",
            output=f"output_{i}",
            passed=passed,
            violations=violations,
        ))
    return DatasetResult(
        dataset_name=name,
        total_cases=len(results),
        passed_cases=sum(1 for r in results if r.passed),
        failed_cases=sum(1 for r in results if not r.passed),
        results=results,
    )


# ===========================================================================
# DIFF ENGINE TESTS
# ===========================================================================

class TestDiffRuns:
    """Core diff_runs() function tests."""

    def test_no_changes(self):
        from phylax import diff_runs
        a = _make_result("test", [(True, []), (True, [])])
        b = _make_result("test", [(True, []), (True, [])])
        diff = diff_runs(a, b)
        assert diff.regressions == 0
        assert diff.resolved == 0
        assert diff.unchanged_pass == 2
        assert diff.unchanged_fail == 0
        assert not diff.has_regressions

    def test_regression_detected(self):
        from phylax import diff_runs
        a = _make_result("test", [(True, []), (True, [])])
        b = _make_result("test", [(True, []), (False, ["must_include: fail"])])
        diff = diff_runs(a, b)
        assert diff.regressions == 1
        assert diff.unchanged_pass == 1
        assert diff.has_regressions

    def test_resolved_detected(self):
        from phylax import diff_runs
        a = _make_result("test", [(False, ["violation"]), (True, [])])
        b = _make_result("test", [(True, []), (True, [])])
        diff = diff_runs(a, b)
        assert diff.resolved == 1
        assert diff.regressions == 0
        assert not diff.has_regressions

    def test_mixed_changes(self):
        from phylax import diff_runs
        a = _make_result("test", [
            (True, []),       # will regress
            (False, ["v1"]),  # will resolve
            (True, []),       # stays pass
            (False, ["v2"]),  # stays fail
        ])
        b = _make_result("test", [
            (False, ["new_fail"]),  # regression
            (True, []),             # resolved
            (True, []),             # unchanged pass
            (False, ["v2"]),        # unchanged fail
        ])
        diff = diff_runs(a, b)
        assert diff.regressions == 1
        assert diff.resolved == 1
        assert diff.unchanged_pass == 1
        assert diff.unchanged_fail == 1
        assert diff.total_cases == 4

    def test_all_regressions(self):
        from phylax import diff_runs
        a = _make_result("test", [(True, []), (True, [])])
        b = _make_result("test", [(False, ["f1"]), (False, ["f2"])])
        diff = diff_runs(a, b)
        assert diff.regressions == 2
        assert diff.has_regressions

    def test_all_resolved(self):
        from phylax import diff_runs
        a = _make_result("test", [(False, ["v1"]), (False, ["v2"])])
        b = _make_result("test", [(True, []), (True, [])])
        diff = diff_runs(a, b)
        assert diff.resolved == 2
        assert not diff.has_regressions

    def test_mismatched_dataset_names(self):
        from phylax import diff_runs
        a = _make_result("dataset_a", [(True, [])])
        b = _make_result("dataset_b", [(True, [])])
        with pytest.raises(ValueError, match="different names"):
            diff_runs(a, b)

    def test_mismatched_case_counts(self):
        from phylax import diff_runs
        a = _make_result("test", [(True, [])])
        b = _make_result("test", [(True, []), (True, [])])
        with pytest.raises(ValueError, match="different case counts"):
            diff_runs(a, b)

    def test_case_diff_details(self):
        from phylax import diff_runs
        a = _make_result("test", [(True, [])])
        b = _make_result("test", [(False, ["must_include: expected 'hello'"])])
        diff = diff_runs(a, b)
        cd = diff.case_diffs[0]
        assert cd.change == "regression"
        assert cd.status_before == "pass"
        assert cd.status_after == "fail"
        assert cd.violations_before == []
        assert "must_include" in cd.violations_after[0]

    def test_single_case(self):
        from phylax import diff_runs
        a = _make_result("test", [(True, [])])
        b = _make_result("test", [(True, [])])
        diff = diff_runs(a, b)
        assert diff.total_cases == 1
        assert diff.unchanged_pass == 1


# ===========================================================================
# REPORT TESTS
# ===========================================================================

class TestDiffReport:
    """Diff report formatting tests."""

    def test_no_regressions_report(self):
        from phylax import diff_runs, format_diff_report
        a = _make_result("test", [(True, []), (True, [])])
        b = _make_result("test", [(True, []), (True, [])])
        diff = diff_runs(a, b)
        report = format_diff_report(diff)
        assert "NO REGRESSIONS" in report

    def test_regressions_report(self):
        from phylax import diff_runs, format_diff_report
        a = _make_result("test", [(True, [])])
        b = _make_result("test", [(False, ["must_include: fail"])])
        diff = diff_runs(a, b)
        report = format_diff_report(diff)
        assert "REGRESSIONS DETECTED" in report
        assert "PASS → FAIL" in report

    def test_resolved_in_report(self):
        from phylax import diff_runs, format_diff_report
        a = _make_result("test", [(False, ["v1"])])
        b = _make_result("test", [(True, [])])
        diff = diff_runs(a, b)
        report = format_diff_report(diff)
        assert "RESOLVED" in report
        assert "FAIL → PASS" in report

    def test_json_report_valid(self):
        from phylax import diff_runs, format_diff_json
        a = _make_result("test", [(True, [])])
        b = _make_result("test", [(False, ["fail"])])
        diff = diff_runs(a, b)
        json_str = format_diff_json(diff)
        parsed = json.loads(json_str)
        assert parsed["regressions"] == 1
        assert parsed["dataset_name"] == "test"


# ===========================================================================
# MODEL TESTS
# ===========================================================================

class TestDiffModels:
    """Model immutability and correctness tests."""

    def test_case_diff_frozen(self):
        from phylax import CaseDiff
        cd = CaseDiff(
            case_index=0, case_name="test", input="x",
            status_before="pass", status_after="fail", change="regression"
        )
        with pytest.raises(Exception):
            cd.change = "resolved"

    def test_dataset_diff_frozen(self):
        from phylax import DatasetDiff
        dd = DatasetDiff(
            dataset_name="test", run_id_before="a", run_id_after="b",
            total_cases=0, regressions=0, resolved=0,
            unchanged_pass=0, unchanged_fail=0, case_diffs=[]
        )
        with pytest.raises(Exception):
            dd.regressions = 5

    def test_has_regressions_property(self):
        from phylax import DatasetDiff
        dd = DatasetDiff(
            dataset_name="test", run_id_before="a", run_id_after="b",
            total_cases=1, regressions=1, resolved=0,
            unchanged_pass=0, unchanged_fail=0, case_diffs=[]
        )
        assert dd.has_regressions is True

    def test_no_regressions_property(self):
        from phylax import DatasetDiff
        dd = DatasetDiff(
            dataset_name="test", run_id_before="a", run_id_after="b",
            total_cases=1, regressions=0, resolved=0,
            unchanged_pass=1, unchanged_fail=0, case_diffs=[]
        )
        assert dd.has_regressions is False
