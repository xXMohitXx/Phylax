"""
Phase-test 1 — Deterministic Verdict Stability

Goal: Ensure identical inputs ALWAYS produce identical PASS/FAIL results.
Run same dataset 10 times. Verify:
  - Same verdicts
  - Same violations
  - Same pass/fail counts
  - No random ordering
  - No nondeterministic hashing
  - No timestamp-based verdict differences
"""
import pytest
from phylax import Dataset, DatasetCase, run_dataset


# ---------------------------------------------------------------------------
# Fixtures — deterministic function and dataset
# ---------------------------------------------------------------------------

def _deterministic_func(prompt: str) -> str:
    """Deterministic function: always returns the same output for same input."""
    responses = {
        "Say hello": "Hello there! How can I help you today?",
        "What is 2+2?": "The answer is 4.",
        "Explain refund policy": "Our refund policy allows returns within 30 days.",
        "Tell me a joke": "Why did the chicken cross the road? To get to the other side.",
        "Summarize AI": "Artificial intelligence is the simulation of human intelligence by machines.",
    }
    return responses.get(prompt, f"Default response to: {prompt}")


def _build_dataset() -> Dataset:
    """Build a fixed dataset with known expectations."""
    return Dataset(
        dataset="stability_test",
        cases=[
            DatasetCase(
                input="Say hello",
                name="greeting",
                expectations={
                    "must_include": ["hello"],
                    "must_not_include": ["error"],
                    "max_latency_ms": 5000,
                    "min_tokens": 3,
                },
            ),
            DatasetCase(
                input="What is 2+2?",
                name="math_check",
                expectations={
                    "must_include": ["4"],
                    "must_not_include": ["wrong"],
                    "min_tokens": 2,
                },
            ),
            DatasetCase(
                input="Explain refund policy",
                name="refund_check",
                expectations={
                    "must_include": ["refund", "30 days"],
                    "must_not_include": ["lawsuit", "denied"],
                },
            ),
            DatasetCase(
                input="Tell me a joke",
                name="joke_check",
                expectations={
                    "must_include": ["chicken"],
                    "must_not_include": ["offensive"],
                    "min_tokens": 5,
                },
            ),
            DatasetCase(
                input="Summarize AI",
                name="summary_check",
                expectations={
                    "must_include": ["intelligence", "machines"],
                    "must_not_include": ["sentient"],
                    "min_tokens": 5,
                },
            ),
        ],
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestVerdictStability:
    """PT1: Run same dataset 10 times, verify identical results."""

    def test_ten_runs_produce_identical_verdicts(self):
        """Core test: 10 runs must yield identical verdicts."""
        dataset = _build_dataset()
        runs = [run_dataset(dataset, _deterministic_func) for _ in range(10)]

        # All runs must have same pass/fail counts
        pass_counts = [r.passed_cases for r in runs]
        fail_counts = [r.failed_cases for r in runs]
        assert len(set(pass_counts)) == 1, f"Pass counts vary: {pass_counts}"
        assert len(set(fail_counts)) == 1, f"Fail counts vary: {fail_counts}"

    def test_ten_runs_produce_identical_per_case_verdicts(self):
        """Each case must have the same pass/fail across all runs."""
        dataset = _build_dataset()
        runs = [run_dataset(dataset, _deterministic_func) for _ in range(10)]

        for case_idx in range(len(dataset.cases)):
            case_verdicts = [r.results[case_idx].passed for r in runs]
            assert len(set(case_verdicts)) == 1, (
                f"Case {case_idx} has inconsistent verdicts: {case_verdicts}"
            )

    def test_ten_runs_produce_identical_violations(self):
        """Violation messages must be identical across runs."""
        dataset = _build_dataset()
        runs = [run_dataset(dataset, _deterministic_func) for _ in range(10)]

        for case_idx in range(len(dataset.cases)):
            all_violations = [
                tuple(r.results[case_idx].violations) for r in runs
            ]
            assert len(set(all_violations)) == 1, (
                f"Case {case_idx} has inconsistent violations: {all_violations}"
            )

    def test_case_ordering_is_stable(self):
        """Cases must always appear in the same order."""
        dataset = _build_dataset()
        runs = [run_dataset(dataset, _deterministic_func) for _ in range(10)]

        for run in runs:
            case_names = [r.case_name for r in run.results]
            assert case_names == [
                "greeting", "math_check", "refund_check",
                "joke_check", "summary_check",
            ], f"Case ordering changed: {case_names}"

    def test_outputs_are_identical(self):
        """Function outputs must be identical across runs."""
        dataset = _build_dataset()
        runs = [run_dataset(dataset, _deterministic_func) for _ in range(10)]

        for case_idx in range(len(dataset.cases)):
            outputs = [r.results[case_idx].output for r in runs]
            assert len(set(outputs)) == 1, (
                f"Case {case_idx} has inconsistent outputs: {outputs}"
            )

    def test_all_cases_pass(self):
        """With our deterministic func, all 5 cases should pass."""
        dataset = _build_dataset()
        result = run_dataset(dataset, _deterministic_func)
        assert result.all_passed, (
            f"Expected all passed but got {result.failed_cases} failures: "
            f"{[r.violations for r in result.results if not r.passed]}"
        )

    def test_dataset_name_is_stable(self):
        """Dataset name must be preserved across runs."""
        dataset = _build_dataset()
        runs = [run_dataset(dataset, _deterministic_func) for _ in range(10)]
        names = [r.dataset_name for r in runs]
        assert all(n == "stability_test" for n in names)

    def test_total_counts_are_stable(self):
        """Total case count must be the same."""
        dataset = _build_dataset()
        runs = [run_dataset(dataset, _deterministic_func) for _ in range(10)]
        totals = [r.total_cases for r in runs]
        assert all(t == 5 for t in totals)


class TestVerdictWithFailures:
    """PT1 extension: Verify stability when some cases FAIL."""

    def _failing_func(self, prompt: str) -> str:
        """Returns wrong outputs for some cases to trigger failures."""
        if prompt == "Say hello":
            return "Goodbye!"  # FAIL: missing "hello"
        if prompt == "What is 2+2?":
            return "The answer is 5."  # FAIL: missing "4"
        return _deterministic_func(prompt)

    def test_failures_are_deterministic(self):
        """Same failures must occur every run."""
        dataset = _build_dataset()
        runs = [run_dataset(dataset, self._failing_func) for _ in range(10)]

        for run in runs:
            assert run.failed_cases == 2, f"Expected 2 failures, got {run.failed_cases}"
            assert run.passed_cases == 3, f"Expected 3 passes, got {run.passed_cases}"

    def test_failing_case_indices_are_stable(self):
        """Same cases must fail every time."""
        dataset = _build_dataset()
        runs = [run_dataset(dataset, self._failing_func) for _ in range(10)]

        for run in runs:
            failed_indices = [r.case_index for r in run.results if not r.passed]
            assert failed_indices == [0, 1], f"Failed indices changed: {failed_indices}"

    def test_violation_messages_are_deterministic(self):
        """Violation text must be identical across runs."""
        dataset = _build_dataset()
        runs = [run_dataset(dataset, self._failing_func) for _ in range(10)]

        for case_idx in [0, 1]:  # the failing cases
            violation_sets = [
                tuple(r.results[case_idx].violations) for r in runs
            ]
            assert len(set(violation_sets)) == 1, (
                f"Case {case_idx} violations vary: {violation_sets}"
            )
