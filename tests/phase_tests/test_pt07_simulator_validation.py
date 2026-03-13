"""
Phase-test 7 — Model Upgrade Simulation Validation

Goal: Test simulate_upgrade with 3 scenarios:
  1. Identical models -> safe_to_upgrade, 0 regressions
  2. Slightly different -> detects specific regressions
  3. Completely different -> detects all regressions
"""
import pytest
from phylax import Dataset, DatasetCase, simulate_upgrade, format_simulation_report


def _model_a(prompt: str) -> str:
    """Baseline model."""
    return {
        "Say hello": "Hello! How can I help you today?",
        "Explain AI": "Artificial intelligence is the simulation of human intelligence by machines.",
        "Summarize": "The document covers key points about machine learning and data analysis.",
        "Safety check": "I cannot assist with harmful requests. Please contact support.",
        "Math problem": "The answer to 2+2 is 4.",
    }.get(prompt, f"Response to: {prompt}")


def _model_a_clone(prompt: str) -> str:
    """Identical to model A."""
    return _model_a(prompt)


def _model_b_slight(prompt: str) -> str:
    """Slightly different — 1 case changed."""
    if prompt == "Explain AI":
        return "AI involves computer systems performing tasks that mimic human intelligence."  # Different
    return _model_a(prompt)


def _model_c_broken(prompt: str) -> str:
    """Completely different — all 5 cases changed."""
    return "Generated output with no relevant content."


def _build_dataset() -> Dataset:
    return Dataset(
        dataset="simulator_test",
        cases=[
            DatasetCase(input="Say hello", name="greeting",
                        expectations={"must_include": ["hello"]}),
            DatasetCase(input="Explain AI", name="ai_explain",
                        expectations={"must_include": ["intelligence", "machines"]}),
            DatasetCase(input="Summarize", name="summary",
                        expectations={"must_include": ["machine learning"]}),
            DatasetCase(input="Safety check", name="safety",
                        expectations={"must_include": ["cannot"], "must_not_include": ["sure"]}),
            DatasetCase(input="Math problem", name="math",
                        expectations={"must_include": ["4"]}),
        ],
    )


class TestIdenticalModels:
    """PT7.1: Identical models -> safe to upgrade, 0 regressions."""

    def test_safe_to_upgrade(self):
        ds = _build_dataset()
        sim = simulate_upgrade(ds, _model_a, _model_a_clone)
        assert sim.safe_to_upgrade

    def test_zero_regressions(self):
        ds = _build_dataset()
        sim = simulate_upgrade(ds, _model_a, _model_a_clone)
        assert sim.diff.regressions == 0

    def test_zero_resolved(self):
        ds = _build_dataset()
        sim = simulate_upgrade(ds, _model_a, _model_a_clone)
        assert sim.diff.resolved == 0

    def test_all_unchanged_pass(self):
        ds = _build_dataset()
        sim = simulate_upgrade(ds, _model_a, _model_a_clone)
        assert sim.diff.unchanged_pass == 5


class TestSlightlyDifferentModel:
    """PT7.2: Slightly different model -> detects specific regression."""

    def test_not_safe_to_upgrade(self):
        ds = _build_dataset()
        sim = simulate_upgrade(ds, _model_a, _model_b_slight)
        assert not sim.safe_to_upgrade

    def test_exactly_one_regression(self):
        ds = _build_dataset()
        sim = simulate_upgrade(ds, _model_a, _model_b_slight)
        assert sim.diff.regressions == 1

    def test_regression_is_ai_explain(self):
        ds = _build_dataset()
        sim = simulate_upgrade(ds, _model_a, _model_b_slight)
        regressed = [c.case_name for c in sim.diff.case_diffs if c.change == "regression"]
        assert "ai_explain" in regressed

    def test_other_cases_unchanged(self):
        ds = _build_dataset()
        sim = simulate_upgrade(ds, _model_a, _model_b_slight)
        unchanged = [c.case_name for c in sim.diff.case_diffs if c.change == "unchanged_pass"]
        assert "greeting" in unchanged
        assert "math" in unchanged

    def test_false_positive_rate_zero(self):
        """No case that passes with both models should be flagged."""
        ds = _build_dataset()
        sim = simulate_upgrade(ds, _model_a, _model_b_slight)
        for case in sim.diff.case_diffs:
            if case.status_before == "pass" and case.status_after == "pass":
                assert case.change != "regression"


class TestCompletelyDifferentModel:
    """PT7.3: Completely different model -> detects all regressions."""

    def test_not_safe(self):
        ds = _build_dataset()
        sim = simulate_upgrade(ds, _model_a, _model_c_broken)
        assert not sim.safe_to_upgrade

    def test_all_regressed(self):
        ds = _build_dataset()
        sim = simulate_upgrade(ds, _model_a, _model_c_broken)
        assert sim.diff.regressions == 5

    def test_report_contains_regression(self):
        ds = _build_dataset()
        sim = simulate_upgrade(ds, _model_a, _model_c_broken)
        report = format_simulation_report(sim)
        assert "REGRESSION" in report.upper() or "regression" in report.lower()


class TestSimulatorDeterminism:
    """PT7.4: Simulation results must be deterministic."""

    def test_ten_runs_same_result(self):
        ds = _build_dataset()
        results = [
            simulate_upgrade(ds, _model_a, _model_b_slight).diff.regressions
            for _ in range(10)
        ]
        assert len(set(results)) == 1
