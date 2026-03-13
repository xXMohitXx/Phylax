"""
Phase-test 18 — Regression Lock Test

Goal: Create baseline dataset, then intentionally break behavior.
Verify that Phylax reliably detects the regression.
This validates the core value proposition: CI fails when behavior regresses.
"""
import pytest

from phylax import (
    Dataset,
    DatasetCase,
    run_dataset,
    diff_runs,
    format_diff_report,
    simulate_upgrade,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _baseline_func(prompt: str) -> str:
    """The known-good baseline function."""
    responses = {
        "Handle refund request": "I can help you with your refund. Our policy allows returns within 30 days of purchase.",
        "Detect harmful content": "I cannot assist with that request. Please contact support for appropriate help.",
        "Summarize document": "The document discusses key findings in artificial intelligence research, covering neural networks and machine learning applications.",
        "Classify sentiment": "The sentiment is positive. The customer expressed satisfaction with the product quality.",
        "Generate greeting": "Hello! Welcome to our service. How can I assist you today?",
    }
    return responses.get(prompt, f"Response: {prompt}")


def _broken_func(prompt: str) -> str:
    """Intentionally broken function — simulates a model regression."""
    responses = {
        "Handle refund request": "Sorry, no refunds available.",  # MISSING: "refund" policy details, "30 days"
        "Detect harmful content": "Sure, I can help with anything!",  # MISSING: refusal
        "Summarize document": "AI stuff.",  # Too short (min_tokens fail)
        "Classify sentiment": "The sentiment is positive. The customer expressed satisfaction with the product quality.",  # Same
        "Generate greeting": "Hello! Welcome to our service. How can I assist you today?",  # Same
    }
    return responses.get(prompt, f"Response: {prompt}")


def _build_contract_dataset() -> Dataset:
    """Contract dataset with strict expectations."""
    return Dataset(
        dataset="regression_lock_test",
        cases=[
            DatasetCase(
                input="Handle refund request",
                name="refund_handler",
                expectations={
                    "must_include": ["refund", "30 days"],
                    "must_not_include": ["denied", "error"],
                    "min_tokens": 10,
                },
            ),
            DatasetCase(
                input="Detect harmful content",
                name="safety_gate",
                expectations={
                    "must_include": ["cannot", "support"],
                    "must_not_include": ["sure"],
                },
            ),
            DatasetCase(
                input="Summarize document",
                name="summarizer",
                expectations={
                    "must_include": ["intelligence", "research"],
                    "min_tokens": 10,
                },
            ),
            DatasetCase(
                input="Classify sentiment",
                name="sentiment_classifier",
                expectations={
                    "must_include": ["positive", "satisfaction"],
                },
            ),
            DatasetCase(
                input="Generate greeting",
                name="greeter",
                expectations={
                    "must_include": ["hello", "welcome"],
                    "min_tokens": 5,
                },
            ),
        ],
    )


# ---------------------------------------------------------------------------
# Tests — Baseline Passes
# ---------------------------------------------------------------------------

class TestBaselinePasses:
    """PT18.1: The baseline function must pass all expectations."""

    def test_baseline_all_pass(self):
        dataset = _build_contract_dataset()
        result = run_dataset(dataset, _baseline_func)
        assert result.all_passed, (
            f"Baseline should pass all cases, but {result.failed_cases} failed: "
            f"{[(r.case_name, r.violations) for r in result.results if not r.passed]}"
        )

    def test_baseline_5_of_5(self):
        dataset = _build_contract_dataset()
        result = run_dataset(dataset, _baseline_func)
        assert result.passed_cases == 5
        assert result.failed_cases == 0


# ---------------------------------------------------------------------------
# Tests — Broken Function Fails
# ---------------------------------------------------------------------------

class TestBrokenFunctionFails:
    """PT18.2: The broken function must reliably FAIL."""

    def test_broken_func_has_failures(self):
        dataset = _build_contract_dataset()
        result = run_dataset(dataset, _broken_func)
        assert not result.all_passed, "Broken function should NOT pass all cases"

    def test_broken_func_fails_exactly_3_cases(self):
        """Cases 0 (refund), 1 (safety), 2 (summary) should fail."""
        dataset = _build_contract_dataset()
        result = run_dataset(dataset, _broken_func)
        assert result.failed_cases == 3, f"Expected 3 failures, got {result.failed_cases}"

    def test_broken_func_passes_2_unchanged_cases(self):
        """Cases 3 (sentiment) and 4 (greeter) should still pass."""
        dataset = _build_contract_dataset()
        result = run_dataset(dataset, _broken_func)
        assert result.passed_cases == 2, f"Expected 2 passes, got {result.passed_cases}"

    def test_specific_cases_fail(self):
        dataset = _build_contract_dataset()
        result = run_dataset(dataset, _broken_func)
        failed_names = [r.case_name for r in result.results if not r.passed]
        assert "refund_handler" in failed_names
        assert "safety_gate" in failed_names
        assert "summarizer" in failed_names

    def test_specific_cases_pass(self):
        dataset = _build_contract_dataset()
        result = run_dataset(dataset, _broken_func)
        passed_names = [r.case_name for r in result.results if r.passed]
        assert "sentiment_classifier" in passed_names
        assert "greeter" in passed_names


# ---------------------------------------------------------------------------
# Tests — Diff Engine Detects Regression
# ---------------------------------------------------------------------------

class TestDiffDetectsRegression:
    """PT18.3: diff_runs must correctly identify the regression."""

    def test_diff_shows_regressions(self):
        dataset = _build_contract_dataset()
        baseline_result = run_dataset(dataset, _baseline_func)
        broken_result = run_dataset(dataset, _broken_func)
        diff = diff_runs(baseline_result, broken_result)
        assert diff.regressions > 0, "Diff should detect regressions"

    def test_diff_regression_count_is_3(self):
        dataset = _build_contract_dataset()
        baseline_result = run_dataset(dataset, _baseline_func)
        broken_result = run_dataset(dataset, _broken_func)
        diff = diff_runs(baseline_result, broken_result)
        assert diff.regressions == 3, f"Expected 3 regressions, got {diff.regressions}"

    def test_diff_resolved_is_zero(self):
        """No failures should be resolved (baseline was all-pass)."""
        dataset = _build_contract_dataset()
        baseline_result = run_dataset(dataset, _baseline_func)
        broken_result = run_dataset(dataset, _broken_func)
        diff = diff_runs(baseline_result, broken_result)
        assert diff.resolved == 0

    def test_diff_report_contains_regression_label(self):
        dataset = _build_contract_dataset()
        baseline_result = run_dataset(dataset, _baseline_func)
        broken_result = run_dataset(dataset, _broken_func)
        diff = diff_runs(baseline_result, broken_result)
        report = format_diff_report(diff)
        assert "REGRESSION" in report.upper()

    def test_diff_unchanged_pass_is_2(self):
        dataset = _build_contract_dataset()
        baseline_result = run_dataset(dataset, _baseline_func)
        broken_result = run_dataset(dataset, _broken_func)
        diff = diff_runs(baseline_result, broken_result)
        assert diff.unchanged_pass == 2


# ---------------------------------------------------------------------------
# Tests — Simulator Detects Regression
# ---------------------------------------------------------------------------

class TestSimulatorDetectsRegression:
    """PT18.4: simulate_upgrade must flag the broken function as unsafe."""

    def test_upgrade_not_safe(self):
        dataset = _build_contract_dataset()
        sim = simulate_upgrade(dataset, _baseline_func, _broken_func)
        assert not sim.safe_to_upgrade, "Should NOT be safe to upgrade to broken model"

    def test_simulator_regression_count(self):
        dataset = _build_contract_dataset()
        sim = simulate_upgrade(dataset, _baseline_func, _broken_func)
        assert sim.diff.regressions == 3


# ---------------------------------------------------------------------------
# Tests — Regression Detection is Deterministic
# ---------------------------------------------------------------------------

class TestRegressionDetectionDeterministic:
    """PT18.5: Regression detection must be deterministic across runs."""

    def test_ten_runs_same_diff(self):
        dataset = _build_contract_dataset()
        baseline_result = run_dataset(dataset, _baseline_func)

        regression_counts = []
        for _ in range(10):
            broken_result = run_dataset(dataset, _broken_func)
            diff = diff_runs(baseline_result, broken_result)
            regression_counts.append(diff.regressions)

        assert len(set(regression_counts)) == 1, (
            f"Regression count varies: {regression_counts}"
        )
        assert regression_counts[0] == 3
