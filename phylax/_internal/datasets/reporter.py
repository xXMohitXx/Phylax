"""
Dataset reporter — Format DatasetResult for console and JSON output.
"""
import json
from phylax._internal.datasets.schema import DatasetResult


def format_report(result: DatasetResult) -> str:
    """Format a DatasetResult as a human-readable console report.

    Args:
        result: The DatasetResult to format.

    Returns:
        A multi-line string suitable for console output.
    """
    lines = []
    lines.append("")
    lines.append(f"Dataset: {result.dataset_name}")
    lines.append(f"Run ID:  {result.run_id}")
    lines.append("=" * 60)

    for r in result.results:
        icon = "✅" if r.passed else "❌"
        lines.append(f"  {icon} [{r.case_name}] {r.input[:50]}")
        if not r.passed:
            for v in r.violations:
                lines.append(f"     ⚠ {v}")
        lines.append(f"     ⏱ {r.latency_ms:.1f}ms")

    lines.append("=" * 60)
    lines.append(
        f"{result.total_cases} cases executed — "
        f"{result.passed_cases} passed, {result.failed_cases} failed"
    )

    if result.all_passed:
        lines.append("✅ ALL CASES PASSED")
    else:
        lines.append("❌ FAILURES DETECTED")

    lines.append("")
    return "\n".join(lines)


def format_json_report(result: DatasetResult) -> str:
    """Format a DatasetResult as a JSON string for CI consumption.

    Args:
        result: The DatasetResult to format.

    Returns:
        A JSON string.
    """
    return result.model_dump_json(indent=2)
