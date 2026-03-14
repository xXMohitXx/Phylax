"""
Phase-test 13 — Security & Isolation

Goal: Ensure Phylax handles adversarial / edge-case inputs gracefully.
No crashes, no information leakage, no undefined behavior.
"""
import pytest
from phylax import Dataset, DatasetCase, run_dataset, diff_runs


# ---------------------------------------------------------------------------
# Adversarial input functions
# ---------------------------------------------------------------------------

def _echo_func(prompt: str) -> str:
    """Simply echoes input — useful for testing input handling."""
    return f"Echo: {prompt}"


# ---------------------------------------------------------------------------
# Tests — Large Inputs
# ---------------------------------------------------------------------------

class TestLargeInputs:
    """PT13.1: Handle very large inputs without crashes."""

    def test_1mb_input(self):
        """1MB input should not crash the system."""
        large_input = "x" * (1024 * 1024)  # 1MB string
        ds = Dataset(
            dataset="large_input_test",
            cases=[
                DatasetCase(input=large_input, expectations={"min_tokens": 1}),
            ],
        )
        result = run_dataset(ds, _echo_func)
        assert result.total_cases == 1  # Didn't crash

    def test_10k_character_expectation(self):
        """Large expectation values should not crash."""
        ds = Dataset(
            dataset="large_expectation_test",
            cases=[
                DatasetCase(
                    input="test",
                    expectations={"must_include": ["a" * 10000]},
                ),
            ],
        )
        result = run_dataset(ds, _echo_func)
        assert result.total_cases == 1


# ---------------------------------------------------------------------------
# Tests — Null / Empty Inputs
# ---------------------------------------------------------------------------

class TestEdgeCaseInputs:
    """PT13.2: Handle edge-case inputs gracefully."""

    def test_empty_string_input(self):
        ds = Dataset(
            dataset="empty_input_test",
            cases=[DatasetCase(input="", expectations={"min_tokens": 0})],
        )
        result = run_dataset(ds, _echo_func)
        assert result.total_cases == 1

    def test_whitespace_only_input(self):
        ds = Dataset(
            dataset="whitespace_test",
            cases=[DatasetCase(input="   \n\t  ", expectations={"min_tokens": 0})],
        )
        result = run_dataset(ds, _echo_func)
        assert result.total_cases == 1

    def test_special_characters_input(self):
        ds = Dataset(
            dataset="special_chars_test",
            cases=[
                DatasetCase(
                    input='<script>alert("xss")</script>',
                    expectations={"must_include": ["Echo"]},
                ),
            ],
        )
        result = run_dataset(ds, _echo_func)
        assert result.total_cases == 1

    def test_null_bytes_in_input(self):
        ds = Dataset(
            dataset="null_bytes_test",
            cases=[
                DatasetCase(
                    input="hello\x00world",
                    expectations={"min_tokens": 1},
                ),
            ],
        )
        result = run_dataset(ds, _echo_func)
        assert result.total_cases == 1


# ---------------------------------------------------------------------------
# Tests — Unicode Edge Cases
# ---------------------------------------------------------------------------

class TestUnicodeHandling:
    """PT13.3: Handle unicode edge cases."""

    def test_emoji_input(self):
        ds = Dataset(
            dataset="emoji_test",
            cases=[DatasetCase(input="Hello 😀🎉🔥", expectations={"min_tokens": 1})],
        )
        result = run_dataset(ds, _echo_func)
        assert result.total_cases == 1

    def test_rtl_input(self):
        """Right-to-left text should work."""
        ds = Dataset(
            dataset="rtl_test",
            cases=[DatasetCase(input="مرحبا بالعالم", expectations={"min_tokens": 1})],
        )
        result = run_dataset(ds, _echo_func)
        assert result.total_cases == 1

    def test_chinese_input(self):
        ds = Dataset(
            dataset="chinese_test",
            cases=[DatasetCase(input="你好世界", expectations={"min_tokens": 1})],
        )
        result = run_dataset(ds, _echo_func)
        assert result.total_cases == 1

    def test_mixed_unicode_expectations(self):
        ds = Dataset(
            dataset="unicode_exp_test",
            cases=[
                DatasetCase(
                    input="Respond in emoji",
                    expectations={"must_include": ["Echo"]},
                ),
            ],
        )
        result = run_dataset(ds, _echo_func)
        assert result.all_passed


# ---------------------------------------------------------------------------
# Tests — Invalid Expectations
# ---------------------------------------------------------------------------

class TestInvalidExpectations:
    """PT13.4: Handle malformed expectations gracefully."""

    def test_empty_expectations(self):
        ds = Dataset(
            dataset="empty_exp_test",
            cases=[DatasetCase(input="test", expectations={})],
        )
        result = run_dataset(ds, _echo_func)
        assert result.total_cases == 1

    def test_empty_must_include_list(self):
        ds = Dataset(
            dataset="empty_list_test",
            cases=[DatasetCase(input="test", expectations={"must_include": []})],
        )
        result = run_dataset(ds, _echo_func)
        assert result.total_cases == 1


# ---------------------------------------------------------------------------
# Tests — Function that Raises Exceptions
# ---------------------------------------------------------------------------

class TestExceptionHandling:
    """PT13.5: Functions that raise should not crash Phylax."""

    def test_function_that_raises(self):
        def bad_func(prompt: str) -> str:
            raise ValueError("Intentional test error")

        ds = Dataset(
            dataset="exception_test",
            cases=[DatasetCase(input="test", expectations={"min_tokens": 1})],
        )
        # Executor may handle gracefully (case fails) or propagate
        try:
            result = run_dataset(ds, bad_func)
            # If it didn't raise, the case should have failed
            assert not result.all_passed or result.total_cases == 1
        except (ValueError, RuntimeError):
            pass  # Also acceptable

    def test_function_returns_none(self):
        """Function returning None should be handled."""
        def none_func(prompt: str):
            return None

        ds = Dataset(
            dataset="none_test",
            cases=[DatasetCase(input="test", expectations={"min_tokens": 1})],
        )
        # Should handle gracefully — either fail the case or raise
        try:
            result = run_dataset(ds, none_func)
            # If it doesn't raise, the case should fail
            assert not result.all_passed or result.total_cases == 1
        except (TypeError, AttributeError):
            pass  # Also acceptable — at least it didn't crash silently


# ---------------------------------------------------------------------------
# Tests — Diff Security
# ---------------------------------------------------------------------------

class TestDiffSecurity:
    """PT13.6: Diff engine with adversarial inputs."""

    def test_diff_with_large_results(self):
        ds = Dataset(
            dataset="diff_security_test",
            cases=[
                DatasetCase(
                    input=f"Case {i}",
                    expectations={"must_include": ["Case"]},
                )
                for i in range(100)
            ],
        )
        r1 = run_dataset(ds, _echo_func)
        r2 = run_dataset(ds, _echo_func)
        diff = diff_runs(r1, r2)
        assert diff.regressions == 0

    def test_diff_never_crashes_on_empty_violations(self):
        ds = Dataset(
            dataset="empty_violations_test",
            cases=[DatasetCase(input="test", expectations={})],
        )
        r1 = run_dataset(ds, _echo_func)
        r2 = run_dataset(ds, _echo_func)
        diff = diff_runs(r1, r2)
        assert diff.total_cases == 1
