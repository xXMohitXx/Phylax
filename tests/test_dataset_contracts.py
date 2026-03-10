"""
Test suite for Phylax Dataset Contracts.

Tests:
    - Schema validation (DatasetCase, Dataset, CaseResult, DatasetResult)
    - YAML loader (valid/invalid files, edge cases)
    - Executor (pass/fail cases, all expectation types)
    - Reporter (console and JSON output)
    - Public API imports (no _internal usage)
"""
import pytest
import json
import tempfile
import os
from pathlib import Path


# ===========================================================================
# PUBLIC API IMPORT TESTS
# ===========================================================================

class TestPublicAPIImports:
    """All dataset symbols must be importable from `phylax` directly."""

    def test_import_dataset(self):
        from phylax import Dataset
        assert Dataset is not None

    def test_import_dataset_case(self):
        from phylax import DatasetCase
        assert DatasetCase is not None

    def test_import_dataset_result(self):
        from phylax import DatasetResult
        assert DatasetResult is not None

    def test_import_case_result(self):
        from phylax import CaseResult
        assert CaseResult is not None

    def test_import_load_dataset(self):
        from phylax import load_dataset
        assert callable(load_dataset)

    def test_import_run_dataset(self):
        from phylax import run_dataset
        assert callable(run_dataset)

    def test_import_format_report(self):
        from phylax import format_report
        assert callable(format_report)

    def test_import_format_json_report(self):
        from phylax import format_json_report
        assert callable(format_json_report)


# ===========================================================================
# SCHEMA TESTS
# ===========================================================================

class TestDatasetCase:
    """DatasetCase model tests."""

    def test_basic_case(self):
        from phylax import DatasetCase
        case = DatasetCase(input="hello", expectations={"must_include": ["hello"]})
        assert case.input == "hello"
        assert case.expectations == {"must_include": ["hello"]}

    def test_case_is_frozen(self):
        from phylax import DatasetCase
        case = DatasetCase(input="hello")
        with pytest.raises(Exception):
            case.input = "changed"

    def test_case_with_name(self):
        from phylax import DatasetCase
        case = DatasetCase(input="hello", name="test_case_1")
        assert case.name == "test_case_1"

    def test_case_defaults(self):
        from phylax import DatasetCase
        case = DatasetCase(input="hello")
        assert case.expectations == {}
        assert case.name is None
        assert case.metadata is None


class TestDataset:
    """Dataset model tests."""

    def test_basic_dataset(self):
        from phylax import Dataset, DatasetCase
        ds = Dataset(
            dataset="test",
            cases=[DatasetCase(input="hello")]
        )
        assert ds.dataset == "test"
        assert len(ds.cases) == 1

    def test_dataset_is_frozen(self):
        from phylax import Dataset, DatasetCase
        ds = Dataset(dataset="test", cases=[DatasetCase(input="hello")])
        with pytest.raises(Exception):
            ds.dataset = "changed"


class TestCaseResult:
    """CaseResult model tests."""

    def test_passing_result(self):
        from phylax import CaseResult
        result = CaseResult(
            case_index=0, case_name="test", input="hello",
            output="hello world", passed=True
        )
        assert result.passed is True
        assert result.violations == []

    def test_failing_result(self):
        from phylax import CaseResult
        result = CaseResult(
            case_index=0, case_name="test", input="hello",
            output="goodbye", passed=False,
            violations=["must_include: expected \"hello\""]
        )
        assert result.passed is False
        assert len(result.violations) == 1


class TestDatasetResult:
    """DatasetResult model tests."""

    def test_all_passed(self):
        from phylax import DatasetResult, CaseResult
        result = DatasetResult(
            dataset_name="test", total_cases=2, passed_cases=2,
            failed_cases=0, results=[
                CaseResult(case_index=0, case_name="a", input="x", output="y", passed=True),
                CaseResult(case_index=1, case_name="b", input="x", output="y", passed=True),
            ]
        )
        assert result.all_passed is True

    def test_some_failed(self):
        from phylax import DatasetResult, CaseResult
        result = DatasetResult(
            dataset_name="test", total_cases=2, passed_cases=1,
            failed_cases=1, results=[
                CaseResult(case_index=0, case_name="a", input="x", output="y", passed=True),
                CaseResult(case_index=1, case_name="b", input="x", output="y", passed=False, violations=["fail"]),
            ]
        )
        assert result.all_passed is False

    def test_run_id_auto_generated(self):
        from phylax import DatasetResult
        r1 = DatasetResult(dataset_name="test", total_cases=0, passed_cases=0, failed_cases=0, results=[])
        r2 = DatasetResult(dataset_name="test", total_cases=0, passed_cases=0, failed_cases=0, results=[])
        assert r1.run_id != r2.run_id


# ===========================================================================
# LOADER TESTS
# ===========================================================================

class TestLoader:
    """YAML dataset loader tests."""

    def _write_yaml(self, content: str) -> Path:
        """Write YAML content to a temp file and return path."""
        fd, path = tempfile.mkstemp(suffix=".yaml")
        os.write(fd, content.encode())
        os.close(fd)
        return Path(path)

    def test_load_valid_dataset(self):
        from phylax import load_dataset
        path = self._write_yaml("""
dataset: support_bot
cases:
  - input: "I want a refund"
    expectations:
      must_include: ["refund"]
  - input: "My package is late"
    expectations:
      must_not_include: ["lawsuit"]
""")
        try:
            ds = load_dataset(path)
            assert ds.dataset == "support_bot"
            assert len(ds.cases) == 2
            assert ds.cases[0].input == "I want a refund"
        finally:
            os.unlink(path)

    def test_load_file_not_found(self):
        from phylax import load_dataset
        with pytest.raises(FileNotFoundError):
            load_dataset("nonexistent.yaml")

    def test_load_wrong_extension(self):
        from phylax import load_dataset
        fd, path = tempfile.mkstemp(suffix=".txt")
        os.close(fd)
        try:
            with pytest.raises(ValueError, match="must be .yaml or .yml"):
                load_dataset(path)
        finally:
            os.unlink(path)

    def test_load_missing_dataset_field(self):
        from phylax import load_dataset
        path = self._write_yaml("cases:\n  - input: hello\n")
        try:
            with pytest.raises(ValueError, match="'dataset' field"):
                load_dataset(path)
        finally:
            os.unlink(path)

    def test_load_missing_cases_field(self):
        from phylax import load_dataset
        path = self._write_yaml("dataset: test\n")
        try:
            with pytest.raises(ValueError, match="'cases' field"):
                load_dataset(path)
        finally:
            os.unlink(path)

    def test_load_empty_cases(self):
        from phylax import load_dataset
        path = self._write_yaml("dataset: test\ncases: []\n")
        try:
            with pytest.raises(ValueError, match="at least one test case"):
                load_dataset(path)
        finally:
            os.unlink(path)

    def test_load_case_missing_input(self):
        from phylax import load_dataset
        path = self._write_yaml("dataset: test\ncases:\n  - expectations: {}\n")
        try:
            with pytest.raises(ValueError, match="'input' field"):
                load_dataset(path)
        finally:
            os.unlink(path)

    def test_load_yml_extension(self):
        from phylax import load_dataset
        fd, path = tempfile.mkstemp(suffix=".yml")
        os.write(fd, b"dataset: test\ncases:\n  - input: hello\n")
        os.close(fd)
        try:
            ds = load_dataset(path)
            assert ds.dataset == "test"
        finally:
            os.unlink(path)


# ===========================================================================
# EXECUTOR TESTS
# ===========================================================================

class TestExecutor:
    """Dataset executor tests."""

    def test_all_pass(self):
        from phylax import Dataset, DatasetCase, run_dataset
        ds = Dataset(dataset="test", cases=[
            DatasetCase(input="say hello", expectations={"must_include": ["hello"]}),
        ])
        result = run_dataset(ds, lambda x: f"hello from {x}")
        assert result.all_passed is True
        assert result.passed_cases == 1
        assert result.failed_cases == 0

    def test_must_include_fail(self):
        from phylax import Dataset, DatasetCase, run_dataset
        ds = Dataset(dataset="test", cases=[
            DatasetCase(input="say hello", expectations={"must_include": ["refund"]}),
        ])
        result = run_dataset(ds, lambda x: f"hello from {x}")
        assert result.all_passed is False
        assert result.failed_cases == 1
        assert "must_include" in result.results[0].violations[0]

    def test_must_not_include_fail(self):
        from phylax import Dataset, DatasetCase, run_dataset
        ds = Dataset(dataset="test", cases=[
            DatasetCase(input="say hello", expectations={"must_not_include": ["hello"]}),
        ])
        result = run_dataset(ds, lambda x: f"hello from {x}")
        assert result.all_passed is False
        assert "must_not_include" in result.results[0].violations[0]

    def test_must_not_include_pass(self):
        from phylax import Dataset, DatasetCase, run_dataset
        ds = Dataset(dataset="test", cases=[
            DatasetCase(input="say hello", expectations={"must_not_include": ["lawsuit"]}),
        ])
        result = run_dataset(ds, lambda x: f"hello from {x}")
        assert result.all_passed is True

    def test_min_tokens_fail(self):
        from phylax import Dataset, DatasetCase, run_dataset
        ds = Dataset(dataset="test", cases=[
            DatasetCase(input="say hello", expectations={"min_tokens": 100}),
        ])
        result = run_dataset(ds, lambda x: "short")
        assert result.all_passed is False
        assert "min_tokens" in result.results[0].violations[0]

    def test_min_tokens_pass(self):
        from phylax import Dataset, DatasetCase, run_dataset
        ds = Dataset(dataset="test", cases=[
            DatasetCase(input="say hello", expectations={"min_tokens": 3}),
        ])
        result = run_dataset(ds, lambda x: "one two three four five")
        assert result.all_passed is True

    def test_max_latency_pass(self):
        from phylax import Dataset, DatasetCase, run_dataset
        ds = Dataset(dataset="test", cases=[
            DatasetCase(input="fast", expectations={"max_latency_ms": 5000}),
        ])
        result = run_dataset(ds, lambda x: "fast response")
        assert result.all_passed is True

    def test_multiple_expectations(self):
        from phylax import Dataset, DatasetCase, run_dataset
        ds = Dataset(dataset="test", cases=[
            DatasetCase(input="refund request", expectations={
                "must_include": ["refund"],
                "must_not_include": ["lawsuit"],
                "min_tokens": 5,
            }),
        ])
        result = run_dataset(ds, lambda x: "Your refund has been processed and will arrive in 5-7 days")
        assert result.all_passed is True

    def test_multiple_cases(self):
        from phylax import Dataset, DatasetCase, run_dataset
        ds = Dataset(dataset="test", cases=[
            DatasetCase(input="a", expectations={"must_include": ["a"]}),
            DatasetCase(input="b", expectations={"must_include": ["b"]}),
            DatasetCase(input="c", expectations={"must_include": ["MISSING"]}),
        ])
        result = run_dataset(ds, lambda x: f"response to {x}")
        assert result.total_cases == 3
        assert result.passed_cases == 2
        assert result.failed_cases == 1

    def test_function_exception_handled(self):
        from phylax import Dataset, DatasetCase, run_dataset
        ds = Dataset(dataset="test", cases=[
            DatasetCase(input="boom", expectations={}),
        ])
        def explode(x):
            raise ValueError("kaboom")
        result = run_dataset(ds, explode)
        assert "ERROR" in result.results[0].output

    def test_case_name_auto_generated(self):
        from phylax import Dataset, DatasetCase, run_dataset
        ds = Dataset(dataset="test", cases=[
            DatasetCase(input="hello"),
        ])
        result = run_dataset(ds, lambda x: x)
        assert result.results[0].case_name == "case_0"

    def test_case_name_from_yaml(self):
        from phylax import Dataset, DatasetCase, run_dataset
        ds = Dataset(dataset="test", cases=[
            DatasetCase(input="hello", name="my_test"),
        ])
        result = run_dataset(ds, lambda x: x)
        assert result.results[0].case_name == "my_test"

    def test_case_insensitive_matching(self):
        from phylax import Dataset, DatasetCase, run_dataset
        ds = Dataset(dataset="test", cases=[
            DatasetCase(input="x", expectations={"must_include": ["HELLO"]}),
        ])
        result = run_dataset(ds, lambda x: "hello world")
        assert result.all_passed is True

    def test_latency_recorded(self):
        from phylax import Dataset, DatasetCase, run_dataset
        ds = Dataset(dataset="test", cases=[
            DatasetCase(input="hello"),
        ])
        result = run_dataset(ds, lambda x: x)
        assert result.results[0].latency_ms >= 0


# ===========================================================================
# REPORTER TESTS
# ===========================================================================

class TestReporter:
    """Reporter output tests."""

    def test_console_report_pass(self):
        from phylax import DatasetResult, CaseResult, format_report
        result = DatasetResult(
            dataset_name="test", total_cases=1, passed_cases=1,
            failed_cases=0, results=[
                CaseResult(case_index=0, case_name="case_0", input="hi", output="hi", passed=True),
            ]
        )
        report = format_report(result)
        assert "ALL CASES PASSED" in report
        assert "1 cases executed" in report

    def test_console_report_fail(self):
        from phylax import DatasetResult, CaseResult, format_report
        result = DatasetResult(
            dataset_name="test", total_cases=1, passed_cases=0,
            failed_cases=1, results=[
                CaseResult(case_index=0, case_name="case_0", input="hi", output="bye",
                           passed=False, violations=["must_include: expected \"hello\""]),
            ]
        )
        report = format_report(result)
        assert "FAILURES DETECTED" in report
        assert "must_include" in report

    def test_json_report_valid_json(self):
        from phylax import DatasetResult, CaseResult, format_json_report
        result = DatasetResult(
            dataset_name="test", total_cases=1, passed_cases=1,
            failed_cases=0, results=[
                CaseResult(case_index=0, case_name="case_0", input="hi", output="hi", passed=True),
            ]
        )
        json_str = format_json_report(result)
        parsed = json.loads(json_str)
        assert parsed["dataset_name"] == "test"
        assert parsed["total_cases"] == 1
        assert parsed["failed_cases"] == 0

    def test_json_report_contains_violations(self):
        from phylax import DatasetResult, CaseResult, format_json_report
        result = DatasetResult(
            dataset_name="test", total_cases=1, passed_cases=0,
            failed_cases=1, results=[
                CaseResult(case_index=0, case_name="case_0", input="hi", output="bye",
                           passed=False, violations=["must_include: expected \"hello\""]),
            ]
        )
        json_str = format_json_report(result)
        parsed = json.loads(json_str)
        assert parsed["results"][0]["violations"][0] == 'must_include: expected "hello"'
