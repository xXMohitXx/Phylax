"""
Dataset executor — Run dataset cases against a callable and enforce expectations.

The executor:
    1. Calls the function under test for each case
    2. Measures latency
    3. Evaluates expectations (must_include, must_not_include, max_latency_ms, min_tokens)
    4. Returns a DatasetResult with per-case verdicts
"""
import time
from typing import Callable

from phylax._internal.datasets.schema import (
    Dataset,
    DatasetResult,
    CaseResult,
)


def _evaluate_expectations(
    output: str,
    expectations: dict,
    latency_ms: float,
) -> list[str]:
    """Evaluate expectations against an output. Returns list of violation messages."""
    violations = []

    # must_include: all substrings must appear in output
    must_include = expectations.get("must_include", [])
    if isinstance(must_include, list):
        for substring in must_include:
            if str(substring).lower() not in output.lower():
                violations.append(
                    f"must_include: expected \"{substring}\" in output"
                )

    # must_not_include: no forbidden substrings in output
    must_not_include = expectations.get("must_not_include", [])
    if isinstance(must_not_include, list):
        for substring in must_not_include:
            if str(substring).lower() in output.lower():
                violations.append(
                    f"must_not_include: found forbidden \"{substring}\" in output"
                )

    # max_latency_ms: response time limit
    max_latency = expectations.get("max_latency_ms")
    if max_latency is not None:
        if latency_ms > float(max_latency):
            violations.append(
                f"max_latency_ms: {latency_ms:.1f}ms exceeded limit of {max_latency}ms"
            )

    # min_tokens: minimum response length (approximate: split by whitespace)
    min_tokens = expectations.get("min_tokens")
    if min_tokens is not None:
        token_count = len(output.split())
        if token_count < int(min_tokens):
            violations.append(
                f"min_tokens: {token_count} tokens below minimum of {min_tokens}"
            )

    return violations


def run_dataset(
    dataset: Dataset,
    func: Callable[[str], str],
) -> DatasetResult:
    """Execute all cases in a dataset against a callable.

    Args:
        dataset: The Dataset to run.
        func: A callable that takes a string input and returns a string output.

    Returns:
        A DatasetResult with per-case verdicts.
    """
    results = []

    for i, case in enumerate(dataset.cases):
        case_name = case.name or f"case_{i}"

        # Execute the function and measure latency
        start = time.perf_counter()
        try:
            output = str(func(case.input))
        except Exception as e:
            output = f"ERROR: {type(e).__name__}: {e}"
        elapsed_ms = (time.perf_counter() - start) * 1000

        # Evaluate expectations
        violations = _evaluate_expectations(output, case.expectations, elapsed_ms)

        results.append(CaseResult(
            case_index=i,
            case_name=case_name,
            input=case.input,
            output=output,
            passed=(len(violations) == 0),
            violations=violations,
            latency_ms=round(elapsed_ms, 2),
        ))

    passed = sum(1 for r in results if r.passed)
    failed = sum(1 for r in results if not r.passed)

    return DatasetResult(
        dataset_name=dataset.dataset,
        total_cases=len(results),
        passed_cases=passed,
        failed_cases=failed,
        results=results,
    )
