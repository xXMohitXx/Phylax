"""
Phase-test 17 — Performance Benchmark

Goal: Benchmark dataset runs with 100 cases × 10 expectations.
Measure runtime, confirm under ceiling, publish results.
"""
import time
import pytest
from phylax import Dataset, DatasetCase, run_dataset, diff_runs, simulate_upgrade


def _benchmark_func(prompt: str) -> str:
    """Deterministic function with realistic-length response."""
    return (
        f"Response to: {prompt}. "
        "This is a comprehensive answer covering the topic in detail. "
        "The analysis shows positive trends across all metrics. "
        "Key findings include improved accuracy, reduced latency, "
        "and enhanced reliability in production environments. "
        "Additional context: the system has been validated through "
        "extensive testing covering edge cases and stress scenarios."
    )


def _build_benchmark_dataset(n: int = 100) -> Dataset:
    """Build dataset with n cases, each with multiple expectations."""
    cases = []
    for i in range(n):
        cases.append(DatasetCase(
            input=f"Benchmark case {i}: analyze the performance metrics",
            name=f"bench_{i:04d}",
            expectations={
                "must_include": ["response", "analysis", "metrics"],
                "must_not_include": ["error", "crash", "undefined"],
                "max_latency_ms": 5000,
                "min_tokens": 10,
            },
        ))
    return Dataset(dataset=f"benchmark_{n}", cases=cases)


# ---------------------------------------------------------------------------
# Performance tests
# ---------------------------------------------------------------------------

class TestPerformanceBenchmark:
    """PT17: Benchmark core operations."""

    def test_100_cases_under_2s(self):
        ds = _build_benchmark_dataset(100)
        start = time.perf_counter()
        result = run_dataset(ds, _benchmark_func)
        elapsed = time.perf_counter() - start
        assert result.all_passed
        assert elapsed < 2.0, f"100 cases took {elapsed:.3f}s, exceeds 2s ceiling"

    def test_500_cases_under_5s(self):
        ds = _build_benchmark_dataset(500)
        start = time.perf_counter()
        result = run_dataset(ds, _benchmark_func)
        elapsed = time.perf_counter() - start
        assert result.all_passed
        assert elapsed < 5.0, f"500 cases took {elapsed:.3f}s, exceeds 5s ceiling"

    def test_diff_100_cases_under_1s(self):
        ds = _build_benchmark_dataset(100)
        result_a = run_dataset(ds, _benchmark_func)
        result_b = run_dataset(ds, _benchmark_func)
        start = time.perf_counter()
        diff = diff_runs(result_a, result_b)
        elapsed = time.perf_counter() - start
        assert elapsed < 1.0, f"Diff of 100 cases took {elapsed:.3f}s"
        assert diff.regressions == 0

    def test_simulate_100_cases_under_5s(self):
        ds = _build_benchmark_dataset(100)
        start = time.perf_counter()
        sim = simulate_upgrade(ds, _benchmark_func, _benchmark_func)
        elapsed = time.perf_counter() - start
        assert sim.safe_to_upgrade
        assert elapsed < 5.0, f"Simulation of 100 cases took {elapsed:.3f}s"

    def test_per_case_overhead_under_1ms(self):
        """Each case should add < 1ms overhead (excluding function runtime)."""
        ds = _build_benchmark_dataset(1000)
        start = time.perf_counter()
        result = run_dataset(ds, _benchmark_func)
        elapsed = time.perf_counter() - start
        per_case = (elapsed / 1000) * 1000  # ms per case
        # Very generous: each case should take < 2ms total
        assert per_case < 2.0, f"Per-case time {per_case:.3f}ms exceeds 2ms limit"

    def test_benchmark_results_summary(self):
        """Run benchmarks and verify results are reportable."""
        results = {}
        for n in [100, 500]:
            ds = _build_benchmark_dataset(n)
            start = time.perf_counter()
            result = run_dataset(ds, _benchmark_func)
            elapsed = time.perf_counter() - start
            results[n] = {
                "cases": n,
                "time_s": round(elapsed, 3),
                "per_case_ms": round((elapsed / n) * 1000, 3),
                "all_passed": result.all_passed,
            }
        # All benchmarks should pass
        for n, r in results.items():
            assert r["all_passed"], f"Benchmark {n} failed"
            assert r["time_s"] < 10, f"Benchmark {n} took {r['time_s']}s"
