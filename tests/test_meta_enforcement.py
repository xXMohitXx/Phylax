"""
Phase 3.4 — Meta-Enforcement Rules Tests

Tests for:
- 3.4.1 MinExpectationCountRule
- 3.4.2 ZeroSignalRule
- 3.4.3 DefinitionChangeGuard
- 3.4.4 ExpectationRemovalGuard

Critical invariant:
No evaluation of complexity or usefulness.
No semantic diff. Only hash comparison.
No judgment on removal reason.
"""

import inspect

import pytest
from pydantic import ValidationError

from phylax._internal.meta.rules import (
    MetaRuleResult,
    MinExpectationCountRule,
    ZeroSignalRule,
    DefinitionChangeGuard,
    ExpectationRemovalGuard,
)
from phylax._internal.metrics.identity import compute_definition_hash


# ═══════════════════════════════════════════════════════════════════
# 3.4.1 — MINIMUM EXPECTATION COUNT RULE
# ═══════════════════════════════════════════════════════════════════

class TestMinExpectationCount:
    """len(declared) >= N. Nothing more."""

    def test_sufficient_count(self):
        rule = MinExpectationCountRule(3)
        result = rule.evaluate(5)
        assert result.passed is True

    def test_exact_count(self):
        rule = MinExpectationCountRule(3)
        result = rule.evaluate(3)
        assert result.passed is True

    def test_insufficient_count(self):
        rule = MinExpectationCountRule(3)
        result = rule.evaluate(2)
        assert result.passed is False

    def test_zero_required(self):
        rule = MinExpectationCountRule(0)
        result = rule.evaluate(0)
        assert result.passed is True

    def test_negative_min_rejected(self):
        with pytest.raises(ValueError):
            MinExpectationCountRule(-1)

    def test_no_complexity_evaluation(self):
        """Must not evaluate expectation complexity."""
        source = inspect.getsource(MinExpectationCountRule)
        for forbidden in ["compute_complexity", "assess_usefulness",
                          "quality_score", "is_trivial", "is_meaningful"]:
            assert forbidden not in source.lower()


# ═══════════════════════════════════════════════════════════════════
# 3.4.2 — ZERO-SIGNAL RULE
# ═══════════════════════════════════════════════════════════════════

class TestZeroSignalRule:
    """Fail if never_failed. No triviality judgment."""

    def test_never_failed_fails(self):
        rule = ZeroSignalRule()
        result = rule.evaluate(never_failed=True)
        assert result.passed is False

    def test_has_failed_passes(self):
        rule = ZeroSignalRule()
        result = rule.evaluate(never_failed=False)
        assert result.passed is True

    def test_no_triviality_assessment(self):
        """Must not assess triviality."""
        source = inspect.getsource(ZeroSignalRule)
        for forbidden in ["assess_trivial", "is_useless", "is_unnecessary",
                          "compute_importance", "assess_value"]:
            assert forbidden not in source.lower()


# ═══════════════════════════════════════════════════════════════════
# 3.4.3 — DEFINITION CHANGE GUARD
# ═══════════════════════════════════════════════════════════════════

class TestDefinitionChangeGuard:
    """Hash comparison only. No semantic diff."""

    def test_unchanged(self):
        guard = DefinitionChangeGuard()
        h = compute_definition_hash({"rule": "must_include", "substrings": ["hello"]})
        result = guard.evaluate(h, h)
        assert result.passed is True

    def test_changed(self):
        guard = DefinitionChangeGuard()
        h1 = compute_definition_hash({"rule": "must_include", "substrings": ["hello"]})
        h2 = compute_definition_hash({"rule": "must_include", "substrings": ["world"]})
        result = guard.evaluate(h1, h2)
        assert result.passed is False

    def test_no_semantic_diff(self):
        """Must not contain semantic diff logic."""
        source = inspect.getsource(DefinitionChangeGuard)
        for forbidden in ["semantic_diff", "meaning_changed",
                          "structural_diff", "deep_compare"]:
            assert forbidden not in source.lower()


# ═══════════════════════════════════════════════════════════════════
# 3.4.4 — EXPECTATION REMOVAL GUARD
# ═══════════════════════════════════════════════════════════════════

class TestExpectationRemovalGuard:
    """Track IDs. No reason judgment."""

    def test_no_removal(self):
        guard = ExpectationRemovalGuard()
        result = guard.evaluate(
            previous_ids={"exp-1", "exp-2"},
            current_ids={"exp-1", "exp-2", "exp-3"},
        )
        assert result.passed is True

    def test_removal_detected(self):
        guard = ExpectationRemovalGuard()
        result = guard.evaluate(
            previous_ids={"exp-1", "exp-2", "exp-3"},
            current_ids={"exp-1", "exp-3"},
        )
        assert result.passed is False
        assert "exp-2" in result.detail

    def test_empty_previous(self):
        guard = ExpectationRemovalGuard()
        result = guard.evaluate(
            previous_ids=set(),
            current_ids={"exp-1"},
        )
        assert result.passed is True

    def test_all_removed(self):
        guard = ExpectationRemovalGuard()
        result = guard.evaluate(
            previous_ids={"exp-1", "exp-2"},
            current_ids=set(),
        )
        assert result.passed is False

    def test_no_removal_reason_judgment(self):
        """Must not judge why expectations were removed."""
        source = inspect.getsource(ExpectationRemovalGuard)
        for forbidden in ["removal_reason", "justify_removal",
                          "is_acceptable", "is_legitimate"]:
            assert forbidden not in source.lower()


# ═══════════════════════════════════════════════════════════════════
# CROSS-CUTTING: IMMUTABILITY & PURITY
# ═══════════════════════════════════════════════════════════════════

class TestMetaRuleImmutability:
    """MetaRuleResult is frozen."""

    def test_frozen(self):
        result = MetaRuleResult(rule_name="test", passed=True)
        with pytest.raises(ValidationError):
            result.passed = False


class TestNoScoringInMeta:
    """No scoring, ranking, or advisory language."""

    def test_no_scoring_in_source(self):
        from phylax._internal.meta import rules
        source = inspect.getsource(rules)
        for forbidden in ["compute_score", "assign_rank", "set_priority",
                          "confidence_level", "compute_weight"]:
            assert forbidden not in source.lower(), (
                f"meta/rules.py contains scoring: {forbidden}"
            )

    def test_no_advisory_language(self):
        from phylax._internal.meta import rules
        source = inspect.getsource(rules)
        for forbidden in ["recommend", "suggest", "advise",
                          "should_consider", "best_practice"]:
            assert forbidden not in source.lower()


class TestEngineIsolationMeta:
    """Engine must not know about meta-enforcement."""

    def test_engine_no_meta_imports(self):
        from phylax._internal.expectations import rules, evaluator
        for mod in [rules, evaluator]:
            source = inspect.getsource(mod)
            assert "meta" not in source.replace("metadata", ""), (
                f"{mod.__name__} imports meta — engine contamination"
            )
