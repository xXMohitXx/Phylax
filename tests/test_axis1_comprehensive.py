"""
Axis 1 Comprehensive Test Suite

Complete test plan implementation covering:
- Phase 1-5 positive, negative, and invariant tests
- Global invariant tests (G1-G5)
- Phase readiness criteria validation

Per strict specification: if any invariant fails → rollback the phase.
"""

import pytest
import inspect
from typing import Any

from phylax._internal.expectations import (
    Evaluator,
    Rule,
    MustIncludeRule,
    MustNotIncludeRule,
    MaxLatencyRule,
    MinTokensRule,
    RuleResult,
    # Phase 1: Composition
    ExpectationGroup,
    AndGroup,
    OrGroup,
    NotGroup,
    # Phase 2: Conditionals
    Condition,
    ConditionalExpectation,
    InputContains,
    ModelEquals,
    ProviderEquals,
    MetadataEquals,
    FlagSet,
    when,
    # Phase 3: Scoping
    ExpectationScope,
    ScopedExpectation,
    for_node,
    for_provider,
    for_stage,
    for_tool,
    scoped,
    # Phase 4: Templates
    ExpectationTemplate,
    TemplateRegistry,
    get_registry,
    register_template,
    get_template,
    get_template_rules,
    # Phase 5: Documentation
    describe_rule,
    describe_condition,
    describe_template,
    list_contracts,
    export_contract_markdown,
    ContractDocumenter,
)


# =============================================================================
# PHASE 1: EXPECTATION COMPOSITION (Logical Algebra)
# =============================================================================

class TestPhase1Positive:
    """Positive tests for Phase 1: Expectation Composition."""
    
    def test_1_1_and_composition_both_pass(self):
        """Test 1.1 — AND composition: both satisfy → PASS."""
        evaluator = Evaluator()
        evaluator.and_group([
            MustIncludeRule(["hello"]),
            MustIncludeRule(["world"]),
        ])
        
        verdict = evaluator.evaluate("hello world", latency_ms=100)
        assert verdict.status == "pass"
    
    def test_1_2_and_partial_failure(self):
        """Test 1.2 — AND partial failure: one violates → FAIL with structural reason."""
        evaluator = Evaluator()
        evaluator.and_group([
            MustIncludeRule(["hello"]),
            MustIncludeRule(["world"]),
        ])
        
        verdict = evaluator.evaluate("hello there", latency_ms=100)
        assert verdict.status == "fail"
        # Failure reason must reference structure, not semantics
        assert len(verdict.violations) > 0
        # No semantic reasoning in violation message
        for violation in verdict.violations:
            assert "meaning" not in violation.lower()
            assert "similar" not in violation.lower()
            assert "intent" not in violation.lower()
    
    def test_1_3_or_composition_one_passes(self):
        """Test 1.3 — OR composition: one satisfies → PASS."""
        evaluator = Evaluator()
        evaluator.or_group([
            MustIncludeRule(["hello"]),
            MustIncludeRule(["goodbye"]),
        ])
        
        verdict = evaluator.evaluate("hello there", latency_ms=100)
        assert verdict.status == "pass"
    
    def test_1_4_or_full_failure(self):
        """Test 1.4 — OR full failure: both violate → FAIL."""
        evaluator = Evaluator()
        evaluator.or_group([
            MustIncludeRule(["hello"]),
            MustIncludeRule(["goodbye"]),
        ])
        
        verdict = evaluator.evaluate("nothing here", latency_ms=100)
        assert verdict.status == "fail"
    
    def test_1_5_not_expectation_passes(self):
        """Test 1.5 — NOT expectation: not contains → PASS."""
        evaluator = Evaluator()
        evaluator.not_rule(MustIncludeRule(["forbidden"]))
        
        verdict = evaluator.evaluate("safe content", latency_ms=100)
        assert verdict.status == "pass"


class TestPhase1Negative:
    """Negative tests for Phase 1: must fail hard."""
    
    def test_1_6_no_partial_verdict(self):
        """Test 1.6 — Nested partial verdict: must not exist.
        
        Verify that AndGroup/OrGroup never return partial verdicts.
        """
        group = AndGroup([
            MustIncludeRule(["a"]),
            MustIncludeRule(["b"]),
        ])
        
        result = group.evaluate("only a here", latency_ms=100)
        
        # Result must be strictly boolean passed, never partial
        assert result.passed in (True, False)
        assert not hasattr(result, 'partial')
        assert not hasattr(result, 'score')
        assert not hasattr(result, 'percentage')
    
    def test_1_7_no_weighted_expectations(self):
        """Test 1.7 — Weighted expectations: must not exist.
        
        Verify that no weighting attributes exist on groups or rules.
        """
        # Check Rule base class has no weight
        assert not hasattr(Rule, 'weight')
        assert not hasattr(MustIncludeRule, 'weight')
        
        # Check groups have no weight
        group = AndGroup([MustIncludeRule(["test"])])
        assert not hasattr(group, 'weight')
        assert not hasattr(group, 'weights')
        
        # Check RuleResult has no score/weight
        result = RuleResult(passed=True, rule_name="test", severity="low")
        assert not hasattr(result, 'weight')
        assert not hasattr(result, 'score')


class TestPhase1Invariant:
    """Invariant tests for Phase 1."""
    
    def test_1_i1_verdicts_remain_binary(self):
        """Test 1.I1 — Verdicts remain binary (PASS/FAIL only)."""
        evaluator = Evaluator()
        evaluator.and_group([
            MustIncludeRule(["a"]),
            OrGroup([
                MustIncludeRule(["b"]),
                MustIncludeRule(["c"]),
            ]),
            NotGroup(MustIncludeRule(["forbidden"])),
        ])
        
        verdict = evaluator.evaluate("a b content", latency_ms=100)
        
        # Status must be strictly "pass" or "fail"
        assert verdict.status in ("pass", "fail")
        
        # No partial states
        assert not hasattr(verdict, 'score')
        assert not hasattr(verdict, 'partial')
        assert not hasattr(verdict, 'percentage')
        assert not hasattr(verdict, 'confidence')


# =============================================================================
# PHASE 2: CONDITIONAL EXPECTATIONS
# =============================================================================

class TestPhase2Positive:
    """Positive tests for Phase 2: Conditional Expectations."""
    
    def test_2_1_condition_matches_and_satisfies(self):
        """Test 2.1 — Condition matches: active, satisfies → PASS."""
        evaluator = Evaluator()
        evaluator.set_context({"input": "refund request"})
        evaluator.when_if(
            InputContains("refund"),
            MustIncludeRule(["policy"])
        )
        
        verdict = evaluator.evaluate("see our refund policy", latency_ms=100)
        assert verdict.status == "pass"
    
    def test_2_2_condition_inactive_ignored(self):
        """Test 2.2 — Condition inactive: no match → ignored."""
        evaluator = Evaluator()
        evaluator.set_context({"input": "general question"})
        evaluator.when_if(
            InputContains("refund"),
            MustIncludeRule(["policy"])  # This should be ignored
        )
        
        # No refund in input, so expectation is skipped
        verdict = evaluator.evaluate("hello there", latency_ms=100)
        assert verdict.status == "pass"
    
    def test_2_3_metadata_condition_model_equals(self):
        """Test 2.3 — Metadata condition: model equals → PASS."""
        evaluator = Evaluator()
        evaluator.set_context({"model": "gpt-4"})
        evaluator.when_if(
            ModelEquals("gpt-4"),
            MustIncludeRule(["detailed"])
        )
        
        verdict = evaluator.evaluate("detailed response", latency_ms=100)
        assert verdict.status == "pass"


class TestPhase2Negative:
    """Negative tests for Phase 2: must reject fuzzy logic."""
    
    def test_2_4_no_fuzzy_conditions(self):
        """Test 2.4 — Fuzzy condition: no regex/similarity conditions exist.
        
        Verify that all conditions are exact matches only.
        """
        # InputContains uses exact substring match, not regex
        cond = InputContains("refund")
        
        # Verify no regex attributes
        assert not hasattr(cond, 'pattern')
        assert not hasattr(cond, 'regex')
        assert not hasattr(cond, 'similarity')
        assert not hasattr(cond, 'threshold')
        # Verify exact match behavior (substring, not pattern)
        assert cond.evaluate({"input": "refund"}) is True
        assert cond.evaluate({"input": "ref"}) is False  # Not a substring
        assert cond.evaluate({"input": "REFUND"}) is True  # Case insensitive
    
    def test_2_5_undefined_metadata_handled(self):
        """Test 2.5 — Condition with undefined metadata returns False (inactive)."""
        # ModelEquals with missing model context
        cond = ModelEquals("gpt-4")
        
        # Missing context should return False (inactive), not error
        result = cond.evaluate({})  # Empty context
        assert result is False
        
        result = cond.evaluate({"other": "value"})  # Wrong key
        assert result is False


class TestPhase2Invariant:
    """Invariant tests for Phase 2."""
    
    def test_2_i1_inactive_conditionals_never_affect_verdict(self):
        """Test 2.I1 — Inactive conditional expectations never affect verdict."""
        evaluator = Evaluator()
        evaluator.set_context({"input": "general question"})  # No "refund"
        
        # Add a conditional that would FAIL if active
        evaluator.when_if(
            InputContains("refund"),
            MustIncludeRule(["impossible-string-xyz123"])  # Would fail
        )
        
        # Also add a passing unconditional rule
        evaluator.must_include(["hello"])
        
        verdict = evaluator.evaluate("hello there", latency_ms=100)
        
        # Verdict should PASS because conditional was inactive
        assert verdict.status == "pass"
        
        # Also verify with active conditional
        evaluator2 = Evaluator()
        evaluator2.set_context({"input": "refund request"})
        evaluator2.when_if(
            InputContains("refund"),
            MustIncludeRule(["impossible-string-xyz123"])
        )
        
        verdict2 = evaluator2.evaluate("hello there", latency_ms=100)
        assert verdict2.status == "fail"  # Now it's active and fails


# =============================================================================
# PHASE 3: EXPECTATION SCOPING & TARGETING
# =============================================================================

class TestPhase3Positive:
    """Positive tests for Phase 3: Expectation Scoping."""
    
    def test_3_1_node_scoped_expectation_fails(self):
        """Test 3.1 — Node-scoped expectation: violates → FAIL."""
        evaluator = Evaluator()
        evaluator.set_context({"node_id": "node-A"})
        evaluator.scoped_for(
            for_node("node-A"),
            MustIncludeRule(["required"])
        )
        
        verdict = evaluator.evaluate("missing content", latency_ms=100)
        assert verdict.status == "fail"
    
    def test_3_2_scope_isolation(self):
        """Test 3.2 — Scope isolation: other node → unaffected."""
        evaluator = Evaluator()
        evaluator.set_context({"node_id": "node-B"})  # Different node
        evaluator.scoped_for(
            for_node("node-A"),  # Scoped to node-A
            MustIncludeRule(["required"])  # Would fail if active
        )
        
        # Node-B should not be affected by node-A expectation
        verdict = evaluator.evaluate("missing content", latency_ms=100)
        assert verdict.status == "pass"  # Scoped expectation inactive
    
    def test_3_3_provider_scoped_expectation(self):
        """Test 3.3 — Provider-scoped expectation: provider violates → FAIL."""
        evaluator = Evaluator()
        evaluator.set_context({"provider": "openai"})
        evaluator.scoped_for(
            for_provider("openai"),
            MaxLatencyRule(1000)
        )
        
        verdict = evaluator.evaluate("response", latency_ms=2000)  # Exceeds 1000
        assert verdict.status == "fail"


class TestPhase3Negative:
    """Negative tests for Phase 3: must reject dynamic scopes."""
    
    def test_3_4_no_dynamic_scope(self):
        """Test 3.4 — Dynamic scope: no pattern/runtime discovery.
        
        Verify scopes use exact string matching only.
        """
        scope = for_provider("openai")
        
        # No pattern attributes
        assert not hasattr(scope, 'pattern')
        assert not hasattr(scope, 'regex')
        assert not hasattr(scope, 'wildcard')
        
        # Verify scope is static string
        assert scope.provider == "openai"
        assert isinstance(scope.provider, str)
    
    def test_3_5_scope_fields_are_explicit(self):
        """Test 3.5 — Scopes are explicit: no ambiguous references."""
        scope = ExpectationScope(provider="openai")
        
        # Only specified fields are set
        assert scope.provider == "openai"
        assert scope.node_id is None
        assert scope.stage is None
        assert scope.tool is None


class TestPhase3Invariant:
    """Invariant tests for Phase 3."""
    
    def test_3_i1_unscoped_remains_global(self):
        """Test 3.I1 — Unscoped expectations remain global."""
        evaluator = Evaluator()
        evaluator.set_context({"node_id": "any-node", "provider": "any-provider"})
        
        # Add global (unscoped) expectation
        evaluator.must_include(["global-requirement"])
        
        verdict = evaluator.evaluate("response without required text", latency_ms=100)
        
        # Global expectation applies regardless of context
        assert verdict.status == "fail"


# =============================================================================
# PHASE 4: EXPECTATION REUSE & TEMPLATES
# =============================================================================

class TestPhase4Positive:
    """Positive tests for Phase 4: Expectation Templates."""
    
    def test_4_1_template_reuse_identical_logic(self):
        """Test 4.1 — Template reuse: identical logic across uses."""
        # Apply same template to multiple evaluators
        evaluator1 = Evaluator()
        evaluator1.use_template("latency-standard")
        
        evaluator2 = Evaluator()
        evaluator2.use_template("latency-standard")
        
        # Both should have identical behavior
        result1 = evaluator1.evaluate("response", latency_ms=2000)
        result2 = evaluator2.evaluate("response", latency_ms=2000)
        
        assert result1.status == result2.status == "pass"
        
        result3 = evaluator1.evaluate("response", latency_ms=4000)
        result4 = evaluator2.evaluate("response", latency_ms=4000)
        
        assert result3.status == result4.status == "fail"
    
    def test_4_2_explicit_override_applied(self):
        """Test 4.2 — Explicit override: override applied correctly."""
        evaluator = Evaluator()
        evaluator.use_template("latency-standard")  # 3000ms threshold
        # Explicitly add stricter latency rule
        evaluator.add_rule(MaxLatencyRule(1000))
        
        # Should fail due to explicit stricter rule
        verdict = evaluator.evaluate("response", latency_ms=1500)
        assert verdict.status == "fail"  # Fails the 1000ms rule


class TestPhase4Negative:
    """Negative tests for Phase 4: must reject hidden behavior."""
    
    def test_4_3_templates_are_static_macros(self):
        """Test 4.3 — Templates are static: no implicit override."""
        template = get_template("latency-standard")
        
        # Template rules should be fixed
        rules1 = template.get_rules()
        rules2 = template.get_rules()
        
        assert len(rules1) == len(rules2)
        
        # No mutation methods
        assert not hasattr(template, 'set_rule')
        assert not hasattr(template, 'modify')
        assert not hasattr(template, 'update')
    
    def test_4_4_no_adaptive_template(self):
        """Test 4.4 — No adaptive template: templates don't vary by context."""
        registry = get_registry()
        template = registry.get("latency-standard")
        
        # No context-dependent attributes
        assert not hasattr(template, 'adapt')
        assert not hasattr(template, 'context')
        assert not hasattr(template, 'dynamic')
        
        # Rules are static list
        assert isinstance(template.rules, list)


class TestPhase4Invariant:
    """Invariant tests for Phase 4."""
    
    def test_4_i1_templates_never_mutate_at_runtime(self):
        """Test 4.I1 — Templates never mutate at runtime."""
        template = get_template("safe-response")
        
        # Get rules multiple times
        rules_before = template.get_rules()
        len_before = len(rules_before)
        
        # Use the template
        evaluator = Evaluator()
        evaluator.use_template("safe-response")
        evaluator.evaluate("test", latency_ms=100)
        
        # Get rules again
        rules_after = template.get_rules()
        len_after = len(rules_after)
        
        # Template unchanged
        assert len_before == len_after


# =============================================================================
# PHASE 5: CONTRACT COMPLETENESS ENFORCEMENT
# =============================================================================

class TestPhase5Positive:
    """Positive tests for Phase 5: Contract Completeness."""
    
    def test_5_1_no_expectations_is_empty(self):
        """Test 5.1 — Minimum expectations: empty contract detectable."""
        evaluator = Evaluator()
        
        # Empty evaluator should be detectable
        assert len(evaluator.rules) == 0
        
        # describe() should indicate no expectations
        desc = evaluator.describe()
        assert "No expectations" in desc
    
    def test_5_2_can_check_expectation_count(self):
        """Test 5.2 — Can verify mandatory expectation presence."""
        evaluator = Evaluator()
        evaluator.must_include(["required"])
        
        # Can check for presence
        assert len(evaluator.rules) >= 1


class TestPhase5Negative:
    """Negative tests for Phase 5: no quality inference."""
    
    def test_5_3_no_quality_inference(self):
        """Test 5.3 — Quality inference: must not exist.
        
        Verify no code judges expectation usefulness.
        """
        evaluator = Evaluator()
        
        # No quality assessment methods
        assert not hasattr(evaluator, 'quality')
        assert not hasattr(evaluator, 'usefulness')
        assert not hasattr(evaluator, 'score_contract')
        assert not hasattr(evaluator, 'rate')
        assert not hasattr(evaluator, 'recommend')


class TestPhase5Invariant:
    """Invariant tests for Phase 5."""
    
    def test_5_i1_completeness_does_not_inspect_output(self):
        """Test 5.I1 — Completeness enforcement doesn't inspect output content."""
        evaluator = Evaluator()
        
        # describe() works without any output
        desc = evaluator.describe()
        assert isinstance(desc, str)
        
        # Contract documentation is static (no output needed)
        md = evaluator.to_markdown()
        assert isinstance(md, str)


# =============================================================================
# GLOBAL INVARIANT TESTS (Run after every phase)
# =============================================================================

class TestGlobalInvariants:
    """Global invariant tests that must pass forever."""
    
    def test_g1_verdict_space_remains_binary(self):
        """G1 — Verdict space remains binary (PASS/FAIL only)."""
        evaluator = Evaluator()
        evaluator.must_include(["test"])
        
        verdict = evaluator.evaluate("test", latency_ms=100)
        
        # Only "pass" or "fail" allowed
        assert verdict.status in ("pass", "fail")
        
        # No other verdict types
        from phylax._internal.expectations.evaluator import Verdict
        verdict_pass = Verdict(status="pass")
        verdict_fail = Verdict(status="fail")
        assert verdict_pass.status == "pass"
        assert verdict_fail.status == "fail"
    
    def test_g2_no_probabilistic_logic_exists(self):
        """G2 — No probabilistic logic exists."""
        # Check Rule class
        assert not hasattr(Rule, 'probability')
        assert not hasattr(Rule, 'confidence')
        assert not hasattr(Rule, 'likelihood')
        
        # Check Evaluator
        assert not hasattr(Evaluator, 'probability')
        assert not hasattr(Evaluator, 'confidence')
        assert not hasattr(Evaluator, 'threshold')
        
        # Check RuleResult
        result = RuleResult(passed=True, rule_name="test", severity="low")
        assert not hasattr(result, 'probability')
        assert not hasattr(result, 'confidence')
        assert not hasattr(result, 'score')
    
    def test_g3_no_semantic_similarity_or_embeddings(self):
        """G3 — No semantic similarity or embeddings used."""
        # Check all rule types
        rule_types = [
            MustIncludeRule,
            MustNotIncludeRule,
            MaxLatencyRule,
            MinTokensRule,
        ]
        
        for rule_type in rule_types:
            assert not hasattr(rule_type, 'embedding')
            assert not hasattr(rule_type, 'similarity')
            assert not hasattr(rule_type, 'semantic')
            assert not hasattr(rule_type, 'vector')
        
        # Check conditions
        condition_types = [
            InputContains,
            ModelEquals,
            ProviderEquals,
            MetadataEquals,
            FlagSet,
        ]
        
        for cond_type in condition_types:
            assert not hasattr(cond_type, 'embedding')
            assert not hasattr(cond_type, 'similarity')
            assert not hasattr(cond_type, 'semantic')
    
    def test_g4_all_failures_trace_to_explicit_declarations(self):
        """G4 — All failures trace to explicit user declarations."""
        evaluator = Evaluator()
        evaluator.must_include(["required"])
        
        verdict = evaluator.evaluate("missing", latency_ms=100)
        
        assert verdict.status == "fail"
        
        # Violations must reference user-declared rules
        assert len(verdict.violations) > 0
        for violation in verdict.violations:
            # No auto-generated or inferred failure reasons
            assert "inferred" not in violation.lower()
            assert "recommended" not in violation.lower()
            assert "suggested" not in violation.lower()
    
    def test_g5_empty_expectations_is_distinguishable(self):
        """G5 — Removing all expectations makes execution detectable."""
        evaluator = Evaluator()
        
        # Empty state is clear
        assert len(evaluator.rules) == 0
        
        # Can be detected programmatically
        desc = evaluator.describe()
        assert "No expectations" in desc


# =============================================================================
# PHASE READINESS VALIDATION
# =============================================================================

class TestPhaseReadiness:
    """Validate each phase meets its readiness criteria."""
    
    def test_phase_1_ready(self):
        """Phase 1 ready: group logic collapses to PASS/FAIL."""
        group = AndGroup([
            MustIncludeRule(["a"]),
            OrGroup([MustIncludeRule(["b"]), MustIncludeRule(["c"])]),
        ])
        
        result = group.evaluate("a b", latency_ms=100)
        assert result.passed in (True, False)
        
    def test_phase_2_ready(self):
        """Phase 2 ready: conditions are exact matches only."""
        cond = InputContains("exact")
        assert cond.evaluate({"input": "exact"}) is True
        assert cond.evaluate({"input": "almost exact"}) is True  # Substring
        assert cond.evaluate({"input": "ex"}) is False  # Not substring
    
    def test_phase_3_ready(self):
        """Phase 3 ready: scope resolution is static."""
        scope = for_provider("openai")
        assert scope.provider == "openai"
        assert isinstance(scope.provider, str)
    
    def test_phase_4_ready(self):
        """Phase 4 ready: templates are static macros."""
        template = get_template("latency-fast")
        rules1 = template.get_rules()
        rules2 = template.get_rules()
        assert len(rules1) == len(rules2)
    
    def test_phase_5_ready(self):
        """Phase 5 ready: no quality judgment exists."""
        evaluator = Evaluator()
        assert not hasattr(evaluator, 'quality')
        assert not hasattr(evaluator, 'recommend')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
