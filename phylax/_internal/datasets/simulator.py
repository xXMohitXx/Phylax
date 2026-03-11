"""
Model Upgrade Simulator — Run dataset contracts against multiple model configs.

Given a dataset contract and two model configurations, runs the same test cases
through both models and produces a behavioral diff showing regressions.

This enables safe model upgrades:
    1. Define behavior contracts in YAML
    2. Run contracts against current model (baseline)
    3. Run contracts against candidate model
    4. Diff results to detect regressions before deploying

Usage:
    from phylax import simulate_upgrade

    result = simulate_upgrade(
        dataset=my_dataset,
        baseline_func=gpt4_handler,
        candidate_func=gpt45_handler,
    )
"""
from typing import Callable, Optional

from phylax._internal.datasets.schema import Dataset, DatasetResult
from phylax._internal.datasets.executor import run_dataset
from phylax._internal.datasets.diff import DatasetDiff, diff_runs, format_diff_report


class SimulationConfig:
    """Configuration for a simulation run.

    Attributes:
        name: Human-readable name for this config (e.g., "gpt-4", "gpt-4.5").
        func: Callable that processes input strings.
    """
    def __init__(self, name: str, func: Callable[[str], str]):
        self.name = name
        self.func = func


class SimulationResult:
    """Result of a model upgrade simulation.

    Attributes:
        baseline_name: Name of the baseline model.
        candidate_name: Name of the candidate model.
        baseline_result: DatasetResult from baseline run.
        candidate_result: DatasetResult from candidate run.
        diff: DatasetDiff comparing baseline vs candidate.
    """
    def __init__(
        self,
        baseline_name: str,
        candidate_name: str,
        baseline_result: DatasetResult,
        candidate_result: DatasetResult,
        diff: DatasetDiff,
    ):
        self.baseline_name = baseline_name
        self.candidate_name = candidate_name
        self.baseline_result = baseline_result
        self.candidate_result = candidate_result
        self.diff = diff

    @property
    def safe_to_upgrade(self) -> bool:
        """True if no regressions detected — safe to deploy candidate."""
        return not self.diff.has_regressions

    @property
    def regressions(self) -> int:
        return self.diff.regressions

    @property
    def resolved(self) -> int:
        return self.diff.resolved


def simulate_upgrade(
    dataset: Dataset,
    baseline_func: Callable[[str], str],
    candidate_func: Callable[[str], str],
    baseline_name: str = "baseline",
    candidate_name: str = "candidate",
) -> SimulationResult:
    """Run a dataset against two functions and compare results.

    Args:
        dataset: The dataset contract to test both models against.
        baseline_func: The baseline (current) model handler.
        candidate_func: The candidate (new) model handler.
        baseline_name: Human-readable name for the baseline.
        candidate_name: Human-readable name for the candidate.

    Returns:
        A SimulationResult with both runs and a behavioral diff.
    """
    # Run baseline
    baseline_result = run_dataset(dataset, baseline_func)

    # Run candidate
    candidate_result = run_dataset(dataset, candidate_func)

    # Diff
    diff = diff_runs(baseline_result, candidate_result)

    return SimulationResult(
        baseline_name=baseline_name,
        candidate_name=candidate_name,
        baseline_result=baseline_result,
        candidate_result=candidate_result,
        diff=diff,
    )


def format_simulation_report(sim: SimulationResult) -> str:
    """Format a SimulationResult as a human-readable console report."""
    lines = []
    lines.append("")
    lines.append("=" * 60)
    lines.append("🔬 MODEL UPGRADE SIMULATION")
    lines.append("=" * 60)
    lines.append(f"Baseline:  {sim.baseline_name}")
    lines.append(f"Candidate: {sim.candidate_name}")
    lines.append(f"Dataset:   {sim.diff.dataset_name}")
    lines.append("")
    lines.append(f"Baseline:  {sim.baseline_result.passed_cases}/{sim.baseline_result.total_cases} passed")
    lines.append(f"Candidate: {sim.candidate_result.passed_cases}/{sim.candidate_result.total_cases} passed")
    lines.append("")

    if sim.regressions > 0:
        lines.append(f"🔴 {sim.regressions} REGRESSION(S) detected")
        for cd in sim.diff.case_diffs:
            if cd.change == "regression":
                lines.append(f"  ❌ [{cd.case_name}] PASS → FAIL")
                for v in cd.violations_after:
                    lines.append(f"     ⚠ {v}")

    if sim.resolved > 0:
        lines.append(f"🟢 {sim.resolved} issue(s) RESOLVED")

    lines.append("")
    lines.append("=" * 60)
    if sim.safe_to_upgrade:
        lines.append("✅ SAFE TO UPGRADE — no regressions detected")
    else:
        lines.append("❌ UPGRADE BLOCKED — regressions detected")
    lines.append("=" * 60)
    lines.append("")
    return "\n".join(lines)
