"""
Behavioral Diff Engine — Compare two dataset runs to detect regressions.

Given two DatasetResult objects (run A and run B), produces a diff showing:
    - Cases that changed from PASS -> FAIL (new failures / regressions)
    - Cases that changed from FAIL -> PASS (resolved failures)
    - Cases that remained the same
    - Summary statistics

Usage:
    from phylax import diff_runs, format_diff_report

    diff = diff_runs(result_a, result_b)
    print(format_diff_report(diff))

CLI:
    phylax dataset diff runA.json runB.json
"""
from pydantic import BaseModel, Field
from typing import Optional

from phylax._internal.datasets.schema import DatasetResult, CaseResult


class CaseDiff(BaseModel):
    """Diff for a single test case between two runs.

    Attributes:
        case_index: Index of the case.
        case_name: Name of the case.
        input: The test input.
        status_before: "pass" or "fail" in run A.
        status_after: "pass" or "fail" in run B.
        change: "regression", "resolved", "unchanged_pass", "unchanged_fail".
        violations_before: Violations in run A.
        violations_after: Violations in run B.
        latency_before_ms: Latency in run A.
        latency_after_ms: Latency in run B.
    """
    case_index: int
    case_name: str
    input: str
    status_before: str
    status_after: str
    change: str  # "regression", "resolved", "unchanged_pass", "unchanged_fail"
    violations_before: list[str] = Field(default_factory=list)
    violations_after: list[str] = Field(default_factory=list)
    latency_before_ms: float = 0.0
    latency_after_ms: float = 0.0

    model_config = {"frozen": True}


class DatasetDiff(BaseModel):
    """Aggregate diff between two dataset runs.

    Attributes:
        dataset_name: Name of the dataset.
        run_id_before: Run ID of run A.
        run_id_after: Run ID of run B.
        total_cases: Total cases compared.
        regressions: Number of PASS -> FAIL cases.
        resolved: Number of FAIL -> PASS cases.
        unchanged_pass: Cases that stayed PASS.
        unchanged_fail: Cases that stayed FAIL.
        case_diffs: Per-case diffs.
    """
    dataset_name: str
    run_id_before: str
    run_id_after: str
    total_cases: int
    regressions: int
    resolved: int
    unchanged_pass: int
    unchanged_fail: int
    case_diffs: list[CaseDiff]

    model_config = {"frozen": True}

    @property
    def has_regressions(self) -> bool:
        """True if any case regressed (PASS -> FAIL)."""
        return self.regressions > 0


def diff_runs(run_a: DatasetResult, run_b: DatasetResult) -> DatasetDiff:
    """Compare two dataset runs and produce a behavioral diff.

    Args:
        run_a: The baseline run (before).
        run_b: The new run (after).

    Returns:
        A DatasetDiff with per-case change analysis.

    Raises:
        ValueError: If the datasets have different names or case counts.
    """
    if run_a.dataset_name != run_b.dataset_name:
        raise ValueError(
            f"Cannot diff datasets with different names: "
            f"'{run_a.dataset_name}' vs '{run_b.dataset_name}'"
        )

    if run_a.total_cases != run_b.total_cases:
        raise ValueError(
            f"Cannot diff datasets with different case counts: "
            f"{run_a.total_cases} vs {run_b.total_cases}"
        )

    case_diffs = []
    regressions = 0
    resolved = 0
    unchanged_pass = 0
    unchanged_fail = 0

    for a, b in zip(run_a.results, run_b.results):
        passed_a = a.passed
        passed_b = b.passed

        if passed_a and not passed_b:
            change = "regression"
            regressions += 1
        elif not passed_a and passed_b:
            change = "resolved"
            resolved += 1
        elif passed_a and passed_b:
            change = "unchanged_pass"
            unchanged_pass += 1
        else:
            change = "unchanged_fail"
            unchanged_fail += 1

        case_diffs.append(CaseDiff(
            case_index=a.case_index,
            case_name=a.case_name,
            input=a.input,
            status_before="pass" if passed_a else "fail",
            status_after="pass" if passed_b else "fail",
            change=change,
            violations_before=list(a.violations),
            violations_after=list(b.violations),
            latency_before_ms=a.latency_ms,
            latency_after_ms=b.latency_ms,
        ))

    return DatasetDiff(
        dataset_name=run_a.dataset_name,
        run_id_before=run_a.run_id,
        run_id_after=run_b.run_id,
        total_cases=len(case_diffs),
        regressions=regressions,
        resolved=resolved,
        unchanged_pass=unchanged_pass,
        unchanged_fail=unchanged_fail,
        case_diffs=case_diffs,
    )


def format_diff_report(diff: DatasetDiff) -> str:
    """Format a DatasetDiff as a human-readable console report."""
    lines = []
    lines.append("")
    lines.append(f"Dataset Diff: {diff.dataset_name}")
    lines.append(f"Before: {diff.run_id_before[:12]}...")
    lines.append(f"After:  {diff.run_id_after[:12]}...")
    lines.append("=" * 60)

    # Show regressions first
    regressions = [d for d in diff.case_diffs if d.change == "regression"]
    if regressions:
        lines.append("")
        lines.append(f"[!!] REGRESSIONS ({len(regressions)}):")
        for d in regressions:
            lines.append(f"  [FAIL] [{d.case_name}] PASS -> FAIL")
            lines.append(f"     Input: {d.input[:50]}")
            for v in d.violations_after:
                lines.append(f"     [!] {v}")

    # Show resolved
    resolved = [d for d in diff.case_diffs if d.change == "resolved"]
    if resolved:
        lines.append("")
        lines.append(f"[OK] RESOLVED ({len(resolved)}):")
        for d in resolved:
            lines.append(f"  [PASS] [{d.case_name}] FAIL -> PASS")

    # Summary
    lines.append("")
    lines.append("=" * 60)
    lines.append(f"Total: {diff.total_cases} cases")
    lines.append(f"  Regressions:    {diff.regressions}")
    lines.append(f"  Resolved:       {diff.resolved}")
    lines.append(f"  Unchanged pass: {diff.unchanged_pass}")
    lines.append(f"  Unchanged fail: {diff.unchanged_fail}")

    if diff.has_regressions:
        lines.append("")
        lines.append("[FAIL] REGRESSIONS DETECTED")
    else:
        lines.append("")
        lines.append("[PASS] NO REGRESSIONS")

    lines.append("")
    return "\n".join(lines)


def format_diff_json(diff: DatasetDiff) -> str:
    """Format a DatasetDiff as JSON."""
    return diff.model_dump_json(indent=2)
