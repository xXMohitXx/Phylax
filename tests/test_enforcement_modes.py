"""
Phase 3.3 — Enforcement Modes Tests

Tests for:
- 3.3.1 Mode Abstraction Layer
- 3.3.2 Mode Definitions
- 3.3.3 Mode Invariance Tests

Critical invariant:
Same input across ALL modes must produce:
- IDENTICAL verdict
- IDENTICAL metrics
- DIFFERENT exit behavior only

If verdict differs → semantic contamination.
"""

import inspect

import pytest

from phylax import ModeHandler, ModeResult
from phylax import EnforcementMode, VALID_MODES


# ═══════════════════════════════════════════════════════════════════
# 3.3.1 — MODE ABSTRACTION LAYER
# ═══════════════════════════════════════════════════════════════════

class TestModeHandler:
    """Mode handler wraps verdicts without modifying them."""

    def test_enforce_pass(self):
        handler = ModeHandler("enforce")
        result = handler.apply("pass")
        assert result.verdict == "pass"
        assert result.exit_code == 0
        assert result.mode == "enforce"

    def test_enforce_fail(self):
        handler = ModeHandler("enforce")
        result = handler.apply("fail")
        assert result.verdict == "fail"
        assert result.exit_code == 1
        assert result.mode == "enforce"

    def test_quarantine_pass(self):
        handler = ModeHandler("quarantine")
        result = handler.apply("pass")
        assert result.verdict == "pass"
        assert result.exit_code == 0

    def test_quarantine_fail(self):
        handler = ModeHandler("quarantine")
        result = handler.apply("fail")
        assert result.verdict == "fail"
        assert result.exit_code == 0  # Quarantine always exits 0

    def test_observe_pass(self):
        handler = ModeHandler("observe")
        result = handler.apply("pass")
        assert result.verdict == "pass"
        assert result.exit_code == 0

    def test_observe_fail(self):
        handler = ModeHandler("observe")
        result = handler.apply("fail")
        assert result.verdict == "fail"
        assert result.exit_code == 0  # Observe always exits 0

    def test_invalid_mode(self):
        with pytest.raises(ValueError):
            ModeHandler("auto")
        with pytest.raises(ValueError):
            ModeHandler("smart")

    def test_invalid_verdict(self):
        handler = ModeHandler("enforce")
        with pytest.raises(ValueError):
            handler.apply("warning")
        with pytest.raises(ValueError):
            handler.apply("skip")

    def test_mode_read_only(self):
        handler = ModeHandler("enforce")
        assert handler.mode == "enforce"


# ═══════════════════════════════════════════════════════════════════
# 3.3.2 — MODE DEFINITIONS
# ═══════════════════════════════════════════════════════════════════

class TestModeDefinitions:
    """Exactly three modes. No more."""

    def test_exactly_three_modes(self):
        assert VALID_MODES == {"enforce", "quarantine", "observe"}

    def test_no_auto_mode(self):
        assert "auto" not in VALID_MODES

    def test_no_smart_mode(self):
        assert "smart" not in VALID_MODES


class TestModeResultImmutability:
    """ModeResult is frozen."""

    def test_frozen(self):
        handler = ModeHandler("enforce")
        result = handler.apply("pass")
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            result.exit_code = 1


# ═══════════════════════════════════════════════════════════════════
# 3.3.3 — MODE INVARIANCE TESTS (Critical)
# ═══════════════════════════════════════════════════════════════════

class TestModeInvariance:
    """
    Same input across ALL modes must produce identical verdict.
    Only exit behavior changes.
    
    If verdict differs across modes → SEMANTIC CONTAMINATION.
    """

    def test_pass_verdict_identical_across_modes(self):
        """PASS verdict must be identical in all modes."""
        verdicts = set()
        for mode in VALID_MODES:
            handler = ModeHandler(mode)
            result = handler.apply("pass")
            verdicts.add(result.verdict)
        assert verdicts == {"pass"}, "Verdict differs across modes — CONTAMINATION"

    def test_fail_verdict_identical_across_modes(self):
        """FAIL verdict must be identical in all modes."""
        verdicts = set()
        for mode in VALID_MODES:
            handler = ModeHandler(mode)
            result = handler.apply("fail")
            verdicts.add(result.verdict)
        assert verdicts == {"fail"}, "Verdict differs across modes — CONTAMINATION"

    def test_only_exit_code_differs(self):
        """
        For a FAIL verdict:
        - enforce: exit 1
        - quarantine: exit 0
        - observe: exit 0
        """
        results = {}
        for mode in VALID_MODES:
            handler = ModeHandler(mode)
            results[mode] = handler.apply("fail")
        
        assert results["enforce"].exit_code == 1
        assert results["quarantine"].exit_code == 0
        assert results["observe"].exit_code == 0
        
        # But verdicts are ALL the same
        assert all(r.verdict == "fail" for r in results.values())

    def test_100_runs_invariant(self):
        """100-run sweep: verdict must not drift."""
        for _ in range(100):
            for verdict in ("pass", "fail"):
                results = {}
                for mode in VALID_MODES:
                    handler = ModeHandler(mode)
                    results[mode] = handler.apply(verdict)
                
                verdicts = set(r.verdict for r in results.values())
                assert len(verdicts) == 1, f"Verdict drifted on run for {verdict}"


class TestNoAutoEscalation:
    """No dynamic escalation or auto-switching."""

    def test_no_escalation_in_source(self):
        from phylax._internal.modes import handler
        source = inspect.getsource(handler)
        for forbidden in ["escalate", "auto_switch", "promote", "upgrade_mode",
                          "dynamic_mode", "adaptive"]:
            assert forbidden not in source.lower()

    def test_no_escalation_in_definitions(self):
        from phylax._internal.modes import definitions
        source = inspect.getsource(definitions)
        for forbidden in ["escalate", "auto_switch", "promote", "smart",
                          "adaptive"]:
            assert forbidden not in source.lower()


class TestEngineIsolation:
    """Engine must not know about modes."""

    def test_engine_no_mode_imports(self):
        from phylax._internal.expectations import rules, evaluator
        for mod in [rules, evaluator]:
            source = inspect.getsource(mod)
            assert "modes" not in source, (
                f"{mod.__name__} imports modes — engine contamination"
            )
