"""
Phase-test 5 — Large Dataset Stress Test

Goal: Verify Phylax scales to 100, 500, and 1000 cases without
crashes, memory errors, or incorrect results.
"""
import time
import pytest
from phylax import Dataset, DatasetCase, run_dataset, diff_runs


def _deterministic_func(prompt: str) -> str:
    return f"Response to: {prompt}. This is a deterministic output with enough tokens."


def _build_large_dataset(n: int) -> Dataset:
    """Build a dataset with n cases."""
    cases = []
    for i in range(n):
        cases.append(DatasetCase(
            input=f"Test case number {i}: please respond with a helpful answer",
            name=f"case_{i:04d}",
            expectations={
                "must_include": ["response"],
                "must_not_include": ["error", "crash"],
                "min_tokens": 3,
            },
        ))
    return Dataset(dataset=f"stress_test_{n}", cases=cases)


# ---------------------------------------------------------------------------
# 100 cases
# ---------------------------------------------------------------------------

class TestStress100:
    """PT5.1: 100 cases must work correctly."""

    def test_100_cases_all_pass(self):
        ds = _build_large_dataset(100)
        result = run_dataset(ds, _deterministic_func)
        assert result.total_cases == 100
        assert result.all_passed

    def test_100_cases_correct_counts(self):
        ds = _build_large_dataset(100)
        result = run_dataset(ds, _deterministic_func)
        assert result.passed_cases == 100
        assert result.failed_cases == 0

    def test_100_cases_all_results_present(self):
        ds = _build_large_dataset(100)
        result = run_dataset(ds, _deterministic_func)
        assert len(result.results) == 100
        indices = [r.case_index for r in result.results]
        assert indices == list(range(100))


# ---------------------------------------------------------------------------
# 500 cases
# ---------------------------------------------------------------------------

class TestStress500:
    """PT5.2: 500 cases must work correctly."""

    def test_500_cases_all_pass(self):
        ds = _build_large_dataset(500)
        result = run_dataset(ds, _deterministic_func)
        assert result.total_cases == 500
        assert result.all_passed

    def test_500_cases_results_ordered(self):
        ds = _build_large_dataset(500)
        result = run_dataset(ds, _deterministic_func)
        names = [r.case_name for r in result.results]
        assert names == [f"case_{i:04d}" for i in range(500)]


# ---------------------------------------------------------------------------
# 1000 cases
# ---------------------------------------------------------------------------

class TestStress1000:
    """PT5.3: 1000 cases must work correctly."""

    def test_1000_cases_all_pass(self):
        ds = _build_large_dataset(1000)
        result = run_dataset(ds, _deterministic_func)
        assert result.total_cases == 1000
        assert result.all_passed

    def test_1000_cases_no_duplicates(self):
        ds = _build_large_dataset(1000)
        result = run_dataset(ds, _deterministic_func)
        outputs = [r.output for r in result.results]
        assert len(set(outputs)) == 1000, "Each case should have unique output"

    def test_1000_cases_diff_works(self):
        """Diff engine must handle large results."""
        ds = _build_large_dataset(1000)
        result_a = run_dataset(ds, _deterministic_func)
        result_b = run_dataset(ds, _deterministic_func)
        diff = diff_runs(result_a, result_b)
        assert diff.regressions == 0
        assert diff.resolved == 0
        assert diff.unchanged_pass == 1000


# ---------------------------------------------------------------------------
# Timing validation
# ---------------------------------------------------------------------------

class TestStressTiming:
    """PT5.4: Execution time must scale linearly."""

    def test_execution_time_linear(self):
        """1000 cases should not take more than 10x of 100 cases."""
        ds_100 = _build_large_dataset(100)
        start = time.perf_counter()
        run_dataset(ds_100, _deterministic_func)
        time_100 = time.perf_counter() - start

        ds_1000 = _build_large_dataset(1000)
        start = time.perf_counter()
        run_dataset(ds_1000, _deterministic_func)
        time_1000 = time.perf_counter() - start

        # Generous: 1000 should take < 15x of 100 (accounting for overhead)
        ratio = time_1000 / max(time_100, 0.001)
        assert ratio < 15, f"Scaling ratio {ratio:.1f}x exceeds 15x limit"

    def test_1000_cases_under_5_seconds(self):
        """1000 deterministic cases should finish in well under 5s."""
        ds = _build_large_dataset(1000)
        start = time.perf_counter()
        run_dataset(ds, _deterministic_func)
        elapsed = time.perf_counter() - start
        assert elapsed < 5.0, f"1000 cases took {elapsed:.2f}s, exceeds 5s limit"
