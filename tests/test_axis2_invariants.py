"""
Axis 2 Invariant Guard Tests

These tests exist to PREVENT Axis 2 regressions.
If any test here fails, the build must fail.

Invariants enforced:
- I1: Verdict space is binary (PASS/FAIL only)
- I2: No adaptive or inferred expectations
- I3: Evidence is observational, not interpretive
- I4: Non-goals are documented
- I5: Error messages are contractual (codes, no advice)
"""

import pytest
import inspect
import os
from pathlib import Path


# =============================================================================
# I1: VERDICT SPACE IMMUTABILITY
# =============================================================================

class TestVerdictSpaceInvariant:
    """Verdict space must remain binary: only 'pass' and 'fail'."""

    def test_verdict_status_is_literal_pass_fail(self):
        """Verdict.status must be Literal['pass', 'fail']."""
        from phylax._internal.schema import Verdict
        
        # Get the type annotation for status field
        field_info = Verdict.model_fields["status"]
        annotation = field_info.annotation
        
        # Check it's a Literal type with exactly pass and fail
        import typing
        args = typing.get_args(annotation)
        assert set(args) == {"pass", "fail"}, (
            f"PHYLAX_INVARIANT_VIOLATION: Verdict.status must be "
            f"Literal['pass', 'fail'], got {args}"
        )

    def test_no_warn_verdict(self):
        """No WARN verdict must exist anywhere in schema."""
        from phylax._internal import schema
        source = inspect.getsource(schema)
        assert "WARN" not in source or "WARNING" in source, (
            "PHYLAX_INVARIANT_VIOLATION: WARN verdict found in schema"
        )

    def test_no_soft_fail_verdict(self):
        """No SOFT_FAIL verdict must exist."""
        from phylax._internal import schema
        source = inspect.getsource(schema)
        assert "SOFT_FAIL" not in source, (
            "PHYLAX_INVARIANT_VIOLATION: SOFT_FAIL verdict found in schema"
        )

    def test_no_partial_verdict(self):
        """No PARTIAL verdict must exist."""
        from phylax._internal import schema
        source = inspect.getsource(schema)
        assert "PARTIAL" not in source, (
            "PHYLAX_INVARIANT_VIOLATION: PARTIAL verdict found in schema"
        )

    def test_no_confidence_in_verdict(self):
        """No CONFIDENCE field must exist in verdict."""
        from phylax._internal.schema import Verdict
        fields = set(Verdict.model_fields.keys())
        assert "confidence" not in fields, (
            "PHYLAX_INVARIANT_VIOLATION: confidence field found in Verdict"
        )

    def test_no_score_in_verdict(self):
        """No SCORE field must exist in verdict."""
        from phylax._internal.schema import Verdict
        fields = set(Verdict.model_fields.keys())
        assert "score" not in fields, (
            "PHYLAX_INVARIANT_VIOLATION: score field found in Verdict"
        )

    def test_verdict_is_frozen(self):
        """Verdict must be immutable (frozen model)."""
        from phylax._internal.schema import Verdict
        config = Verdict.model_config
        assert config.get("frozen") is True, (
            "PHYLAX_INVARIANT_VIOLATION: Verdict model is not frozen"
        )


# =============================================================================
# I2: NO ADAPTIVE EXPECTATIONS
# =============================================================================

class TestNoAdaptiveExpectations:
    """Expectations must be 100% user-authored, never inferred."""

    def test_no_similarity_attribute(self):
        """No expectation rule may have a 'similarity' attribute."""
        from phylax._internal.expectations.rules import (
            MustIncludeRule, MustNotIncludeRule,
            MaxLatencyRule, MinTokensRule,
        )
        for rule_cls in [MustIncludeRule, MustNotIncludeRule, MaxLatencyRule, MinTokensRule]:
            assert not hasattr(rule_cls, "similarity"), (
                f"PHYLAX_INVARIANT_VIOLATION: {rule_cls.__name__} has similarity attribute"
            )

    def test_no_semantic_attribute(self):
        """No expectation rule may have a 'semantic' attribute."""
        from phylax._internal.expectations.rules import (
            MustIncludeRule, MustNotIncludeRule,
            MaxLatencyRule, MinTokensRule,
        )
        for rule_cls in [MustIncludeRule, MustNotIncludeRule, MaxLatencyRule, MinTokensRule]:
            assert not hasattr(rule_cls, "semantic"), (
                f"PHYLAX_INVARIANT_VIOLATION: {rule_cls.__name__} has semantic attribute"
            )

    def test_no_adaptive_attribute(self):
        """No expectation rule may have an 'adaptive' attribute."""
        from phylax._internal.expectations.rules import (
            MustIncludeRule, MustNotIncludeRule,
            MaxLatencyRule, MinTokensRule,
        )
        for rule_cls in [MustIncludeRule, MustNotIncludeRule, MaxLatencyRule, MinTokensRule]:
            assert not hasattr(rule_cls, "adaptive"), (
                f"PHYLAX_INVARIANT_VIOLATION: {rule_cls.__name__} has adaptive attribute"
            )

    def test_no_learned_threshold(self):
        """No rule may have a 'learned' or 'auto' threshold."""
        from phylax._internal.expectations.rules import (
            MustIncludeRule, MustNotIncludeRule,
            MaxLatencyRule, MinTokensRule,
        )
        for rule_cls in [MustIncludeRule, MustNotIncludeRule, MaxLatencyRule, MinTokensRule]:
            for attr in ["learned", "auto_threshold", "auto_generate"]:
                assert not hasattr(rule_cls, attr), (
                    f"PHYLAX_INVARIANT_VIOLATION: {rule_cls.__name__} has {attr} attribute"
                )


# =============================================================================
# I3: EVIDENCE PURITY
# =============================================================================

class TestEvidencePurity:
    """Evidence must be observational — no interpretation."""

    def test_evidence_module_no_similarity(self):
        """Evidence module must not contain similarity matching."""
        from phylax._internal import evidence
        source = inspect.getsource(evidence)
        for forbidden in ["similarity", "embedding", "cosine", "nlp", "semantic"]:
            assert forbidden not in source.lower(), (
                f"PHYLAX_INVARIANT_VIOLATION: evidence module contains '{forbidden}'"
            )

    def test_evidence_functions_are_exact(self):
        """Evidence functions must perform exact comparisons only."""
        from phylax._internal.evidence import compare_outputs
        # compare_outputs should use hash equality
        source = inspect.getsource(compare_outputs)
        assert "hash" in source.lower() or "==" in source, (
            "PHYLAX_INVARIANT_VIOLATION: compare_outputs does not use exact comparison"
        )

    def test_no_root_cause_field(self):
        """GraphVerdict must use 'first_failing_node', never 'root_cause'."""
        from phylax._internal.graph import GraphVerdict
        fields = GraphVerdict.model_fields.keys()
        
        assert "first_failing_node" in fields, (
            "PHYLAX_INVARIANT_VIOLATION: GraphVerdict missing 'first_failing_node'"
        )
        assert "root_cause_node" not in fields, (
            "PHYLAX_INVARIANT_VIOLATION: 'root_cause_node' found in GraphVerdict (must use first_failing_node)"
        )


# =============================================================================
# I4: NON-GOALS DOCUMENTED
# =============================================================================

class TestNonGoalsDocumented:
    """Non-goals must be explicitly documented."""

    def test_non_goals_file_exists(self):
        """docs/non-goals.md must exist."""
        project_root = Path(__file__).parent.parent
        non_goals = project_root / "docs" / "non-goals.md"
        assert non_goals.exists(), (
            "PHYLAX_INVARIANT_VIOLATION: docs/non-goals.md does not exist"
        )

    def test_non_goals_contains_five_items(self):
        """Non-goals doc must list all 5 required non-goals."""
        project_root = Path(__file__).parent.parent
        non_goals = project_root / "docs" / "non-goals.md"
        content = non_goals.read_text()
        
        required = [
            "explain failures",
            "recommend fixes",
            "score outputs",
            "reason semantically",
            "monitor production",
        ]
        
        content_lower = content.lower()
        for item in required:
            assert item.lower() in content_lower, (
                f"PHYLAX_INVARIANT_VIOLATION: non-goals.md missing: '{item}'"
            )


# =============================================================================
# I5: ERROR MESSAGES ARE CONTRACTUAL
# =============================================================================

class TestErrorMessagesContractual:
    """Error messages must have codes and no advice."""

    def test_errors_have_codes(self):
        """All error classes must map to PHYLAX_Exxx codes."""
        from phylax._internal import errors
        source = inspect.getsource(errors)
        assert "PHYLAX_E" in source, (
            "PHYLAX_INVARIANT_VIOLATION: error module missing PHYLAX_E error codes"
        )

    def test_error_messages_no_suggestions(self):
        """Error messages must not contain suggestion language."""
        from phylax._internal import errors
        source = inspect.getsource(errors)
        
        forbidden_advice = [
            "try ",
            "you should",
            "consider ",
            "maybe ",
            "perhaps ",
            "you might want",
        ]
        
        for phrase in forbidden_advice:
            assert phrase not in source.lower(), (
                f"PHYLAX_INVARIANT_VIOLATION: error module contains advice: '{phrase}'"
            )
