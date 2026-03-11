"""
Test suite for Phylax Model Upgrade Simulator (Phase 4).

Tests:
    - Public API imports
    - simulate_upgrade() with various scenarios
    - safe_to_upgrade property
    - Report formatting
"""
import pytest


# ===========================================================================
# PUBLIC API IMPORT TESTS
# ===========================================================================

class TestSimulatorPublicAPI:
    """All simulator symbols must be importable from phylax directly."""

    def test_import_simulation_result(self):
        from phylax import SimulationResult
        assert SimulationResult is not None

    def test_import_simulate_upgrade(self):
        from phylax import simulate_upgrade
        assert callable(simulate_upgrade)

    def test_import_format_simulation_report(self):
        from phylax import format_simulation_report
        assert callable(format_simulation_report)


# ===========================================================================
# SIMULATOR TESTS
# ===========================================================================

class TestSimulateUpgrade:
    """Core simulate_upgrade() function tests."""

    def test_safe_upgrade(self):
        """Both models produce identical results — safe to upgrade."""
        from phylax import Dataset, DatasetCase, simulate_upgrade
        ds = Dataset(dataset="test", cases=[
            DatasetCase(input="hello", expectations={"must_include": ["hello"]}),
        ])
        result = simulate_upgrade(
            dataset=ds,
            baseline_func=lambda x: f"hello from baseline: {x}",
            candidate_func=lambda x: f"hello from candidate: {x}",
        )
        assert result.safe_to_upgrade is True
        assert result.regressions == 0

    def test_regression_detected(self):
        """Candidate fails a case that baseline passes — regression."""
        from phylax import Dataset, DatasetCase, simulate_upgrade
        ds = Dataset(dataset="test", cases=[
            DatasetCase(input="hello", expectations={"must_include": ["hello"]}),
        ])
        result = simulate_upgrade(
            dataset=ds,
            baseline_func=lambda x: f"hello from baseline",
            candidate_func=lambda x: f"goodbye from candidate",
        )
        assert result.safe_to_upgrade is False
        assert result.regressions == 1

    def test_resolved_detected(self):
        """Candidate passes a case that baseline fails — resolved."""
        from phylax import Dataset, DatasetCase, simulate_upgrade
        ds = Dataset(dataset="test", cases=[
            DatasetCase(input="hello", expectations={"must_include": ["specific_word"]}),
        ])
        result = simulate_upgrade(
            dataset=ds,
            baseline_func=lambda x: "no match here",
            candidate_func=lambda x: "has specific_word in response",
        )
        assert result.safe_to_upgrade is True
        assert result.resolved == 1

    def test_multiple_cases_mixed(self):
        """Multiple cases with mixed results."""
        from phylax import Dataset, DatasetCase, simulate_upgrade
        ds = Dataset(dataset="test", cases=[
            DatasetCase(input="a", expectations={"must_include": ["a"]}),
            DatasetCase(input="b", expectations={"must_include": ["b"]}),
            DatasetCase(input="c", expectations={"must_include": ["c"]}),
        ])

        def baseline(x):
            return f"response with a and b and c"

        def candidate(x):
            if x == "b":
                return "no match here"  # regression
            return f"response with a and b and c"

        result = simulate_upgrade(
            dataset=ds,
            baseline_func=baseline,
            candidate_func=candidate,
        )
        assert result.safe_to_upgrade is False
        assert result.regressions == 1

    def test_custom_names(self):
        """Custom model names appear in result."""
        from phylax import Dataset, DatasetCase, simulate_upgrade
        ds = Dataset(dataset="test", cases=[
            DatasetCase(input="hello"),
        ])
        result = simulate_upgrade(
            dataset=ds,
            baseline_func=lambda x: x,
            candidate_func=lambda x: x,
            baseline_name="gpt-4",
            candidate_name="gpt-4.5",
        )
        assert result.baseline_name == "gpt-4"
        assert result.candidate_name == "gpt-4.5"

    def test_both_fail_safe(self):
        """If both models fail the same case, it's not a regression."""
        from phylax import Dataset, DatasetCase, simulate_upgrade
        ds = Dataset(dataset="test", cases=[
            DatasetCase(input="hello", expectations={"must_include": ["impossible"]}),
        ])
        result = simulate_upgrade(
            dataset=ds,
            baseline_func=lambda x: "no match",
            candidate_func=lambda x: "no match either",
        )
        assert result.safe_to_upgrade is True
        assert result.regressions == 0

    def test_result_has_both_runs(self):
        """SimulationResult should contain both DatasetResult objects."""
        from phylax import Dataset, DatasetCase, simulate_upgrade
        ds = Dataset(dataset="test", cases=[
            DatasetCase(input="hello"),
        ])
        result = simulate_upgrade(
            dataset=ds,
            baseline_func=lambda x: x,
            candidate_func=lambda x: x,
        )
        assert result.baseline_result is not None
        assert result.candidate_result is not None
        assert result.diff is not None


# ===========================================================================
# REPORT TESTS
# ===========================================================================

class TestSimulationReport:
    """Simulation report formatting tests."""

    def test_safe_upgrade_report(self):
        from phylax import Dataset, DatasetCase, simulate_upgrade, format_simulation_report
        ds = Dataset(dataset="test", cases=[
            DatasetCase(input="hello", expectations={"must_include": ["hello"]}),
        ])
        result = simulate_upgrade(
            dataset=ds,
            baseline_func=lambda x: f"hello",
            candidate_func=lambda x: f"hello",
        )
        report = format_simulation_report(result)
        assert "SAFE TO UPGRADE" in report
        assert "MODEL UPGRADE SIMULATION" in report

    def test_blocked_upgrade_report(self):
        from phylax import Dataset, DatasetCase, simulate_upgrade, format_simulation_report
        ds = Dataset(dataset="test", cases=[
            DatasetCase(input="hello", expectations={"must_include": ["hello"]}),
        ])
        result = simulate_upgrade(
            dataset=ds,
            baseline_func=lambda x: "hello",
            candidate_func=lambda x: "goodbye",
        )
        report = format_simulation_report(result)
        assert "UPGRADE BLOCKED" in report
        assert "REGRESSION" in report

    def test_report_shows_model_names(self):
        from phylax import Dataset, DatasetCase, simulate_upgrade, format_simulation_report
        ds = Dataset(dataset="test", cases=[DatasetCase(input="x")])
        result = simulate_upgrade(
            dataset=ds,
            baseline_func=lambda x: x,
            candidate_func=lambda x: x,
            baseline_name="gpt-4",
            candidate_name="gpt-4.5",
        )
        report = format_simulation_report(result)
        assert "gpt-4" in report
        assert "gpt-4.5" in report
