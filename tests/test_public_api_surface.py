"""
Public API Surface Test (v1.4.0)

This test validates that EVERY feature of Phylax is accessible
through `from phylax import ...` — no _internal imports needed.

If this test fails, users are forced to use private imports.
"""

import pytest

# ═══════════════════════════════════════════════════════════════════
# IMPORT EVERYTHING FROM PUBLIC API
# ═══════════════════════════════════════════════════════════════════

from phylax import (
    # Core
    trace, expect, execution, __version__,
    # Schema
    Trace, TraceRequest, TraceResponse, TraceRuntime, TraceMessage,
    TraceParameters, Verdict,
    # Context
    get_execution_id, get_parent_node_id, push_node, pop_node,
    in_execution_context,
    # Graph
    ExecutionGraph, NodeRole, GraphStage, GraphDiff, NodeDiff,
    # Expectations engine
    evaluate, Evaluator, Rule, RuleResult,
    MustIncludeRule, MustNotIncludeRule, MaxLatencyRule, MinTokensRule,
    # Composition
    ExpectationGroup, AndGroup, OrGroup, NotGroup,
    # Conditionals
    Condition, ConditionalExpectation, InputContains, ModelEquals,
    ProviderEquals, MetadataEquals, FlagSet, when,
    # Scoping
    ExpectationScope, ScopedExpectation, for_node, for_provider,
    for_stage, for_tool, scoped,
    # Templates
    ExpectationTemplate, TemplateRegistry, get_template_registry,
    register_template, get_template, get_template_rules,
    # Documentation
    describe_rule, describe_condition, describe_template,
    list_contracts, export_contract_markdown, ContractDocumenter,
    # Adapters
    OpenAIAdapter, GeminiAdapter, GroqAdapter,
    MistralAdapter, HuggingFaceAdapter, OllamaAdapter,
    # Surfaces
    Surface, SurfaceType, SurfaceRuleResult, SurfaceVerdict,
    SurfaceRule, SurfaceAdapter, SurfaceEvaluator, SurfaceRegistry,
    get_registry, TextSurfaceAdapter,
    FieldExistsRule, FieldNotExistsRule, TypeEnforcementRule,
    ExactValueRule, EnumEnforcementRule, ArrayBoundsRule,
    StructuredSurfaceAdapter,
    ToolPresenceRule, ToolCountRule, ToolArgumentRule, ToolOrderingRule,
    ToolSurfaceAdapter,
    StepCountRule, ForbiddenTransitionRule, RequiredStageRule,
    ExecutionTraceSurfaceAdapter,
    ExactStabilityRule, AllowedDriftRule, StabilitySurfaceAdapter,
    # Metrics
    ExpectationIdentity, compute_definition_hash,
    LedgerEntry, EvaluationLedger, AggregateMetrics,
    aggregate, aggregate_all,
    HealthReport, CoverageReport, get_windowed_health,
    # Modes
    ModeHandler, ModeResult, EnforcementMode, VALID_MODES,
    # Meta-Enforcement
    MetaRuleResult, MinExpectationCountRule, ZeroSignalRule,
    DefinitionChangeGuard, ExpectationRemovalGuard,
)


# ═══════════════════════════════════════════════════════════════════
# TESTS — Every feature works from public import
# ═══════════════════════════════════════════════════════════════════

class TestVersion:
    def test_version_is_1_4_0(self):
        assert __version__ == "1.4.0"


class TestExpectationsPublicAPI:
    """Core expectations work from public import."""

    def test_evaluate_pass(self):
        v = evaluate(response_text="Your refund is approved.", latency_ms=100,
                     must_include=["refund"])
        assert v.status == "pass"

    def test_evaluate_fail(self):
        v = evaluate(response_text="No help.", latency_ms=100,
                     must_include=["refund"])
        assert v.status == "fail"

    def test_evaluator_class(self):
        e = Evaluator()
        e.must_include(["test"])
        v = e.evaluate("This is a test.", 100)
        assert v.status == "pass"

    def test_rules(self):
        r = MustIncludeRule(["hello"])
        assert r.evaluate("hello world", 100).passed is True

        r2 = MustNotIncludeRule(["forbidden"])
        assert r2.evaluate("safe text", 100).passed is True

        r3 = MaxLatencyRule(1000)
        assert r3.evaluate("ok", 500).passed is True

        r4 = MinTokensRule(3)
        assert r4.evaluate("one two three four", 100).passed is True


class TestCompositionPublicAPI:
    """Groups and conditionals work from public import."""

    def test_and_group(self):
        group = AndGroup([MustIncludeRule(["a"]), MustIncludeRule(["b"])])
        result = group.evaluate("a and b", 100)
        assert result.passed is True

    def test_or_group(self):
        group = OrGroup([MustIncludeRule(["x"]), MustIncludeRule(["a"])])
        result = group.evaluate("a only", 100)
        assert result.passed is True

    def test_not_group(self):
        group = NotGroup(MustIncludeRule(["forbidden"]))
        result = group.evaluate("safe text", 100)
        assert result.passed is True

    def test_conditional(self):
        cond = InputContains("refund")
        assert isinstance(cond, Condition)


class TestScopingPublicAPI:
    def test_scope_creation(self):
        scope = ExpectationScope(node_id="test_node")
        assert scope.node_id == "test_node"


class TestTemplatesPublicAPI:
    def test_registry_access(self):
        reg = get_template_registry()
        assert isinstance(reg, TemplateRegistry)

    def test_get_template(self):
        t = get_template("safe-response")
        assert isinstance(t, ExpectationTemplate)


class TestDocumentationPublicAPI:
    def test_describe_rule(self):
        desc = describe_rule(MustIncludeRule(["hello"]))
        assert isinstance(desc, str)

    def test_list_contracts(self):
        rules = [MustIncludeRule(["test"])]
        contracts = list_contracts(rules)
        assert isinstance(contracts, str)
        assert "test" in contracts


class TestSurfacesPublicAPI:
    """All surface types work from public import."""

    def test_text_surface(self):
        adapter = TextSurfaceAdapter()
        assert isinstance(adapter, SurfaceAdapter)

    def test_structured_surface(self):
        adapter = StructuredSurfaceAdapter()
        assert isinstance(adapter, SurfaceAdapter)

    def test_tool_surface(self):
        adapter = ToolSurfaceAdapter()
        assert isinstance(adapter, SurfaceAdapter)

    def test_execution_trace_surface(self):
        adapter = ExecutionTraceSurfaceAdapter()
        assert isinstance(adapter, SurfaceAdapter)

    def test_stability_surface(self):
        adapter = StabilitySurfaceAdapter()
        assert isinstance(adapter, SurfaceAdapter)

    def test_field_exists_rule(self):
        rule = FieldExistsRule(path="name")
        assert isinstance(rule, SurfaceRule)

    def test_tool_presence_rule(self):
        rule = ToolPresenceRule(tool_name="search")
        assert isinstance(rule, SurfaceRule)


class TestMetricsPublicAPI:
    """Axis 3 metrics work from public import."""

    def test_identity_creation(self):
        identity = ExpectationIdentity.create({"rule": "test"})
        assert identity.expectation_id.startswith("exp-")

    def test_hash_determinism(self):
        h1 = compute_definition_hash({"rule": "test"})
        h2 = compute_definition_hash({"rule": "test"})
        assert h1 == h2

    def test_ledger_and_aggregate(self):
        ledger = EvaluationLedger()
        ledger.record(LedgerEntry(expectation_id="e1", verdict="pass"))
        ledger.record(LedgerEntry(expectation_id="e1", verdict="fail"))
        result = aggregate(ledger.get_entries(), "e1")
        assert result.total_evaluations == 2
        assert result.total_failures == 1

    def test_health_report(self):
        entries = [LedgerEntry(expectation_id="e1", verdict="pass")]
        metrics = aggregate(entries, "e1")
        report = HealthReport.from_aggregate(metrics, "hash123")
        assert report.total_evaluations == 1

    def test_coverage_report(self):
        report = CoverageReport.compute(3, {"e1", "e2"})
        assert report.coverage_ratio == pytest.approx(2/3)


class TestModesPublicAPI:
    """Enforcement modes work from public import."""

    def test_enforce_mode(self):
        h = ModeHandler("enforce")
        r = h.apply("fail")
        assert r.verdict == "fail"
        assert r.exit_code == 1

    def test_quarantine_mode(self):
        h = ModeHandler("quarantine")
        r = h.apply("fail")
        assert r.verdict == "fail"
        assert r.exit_code == 0

    def test_observe_mode(self):
        h = ModeHandler("observe")
        r = h.apply("fail")
        assert r.verdict == "fail"
        assert r.exit_code == 0

    def test_valid_modes(self):
        assert VALID_MODES == {"enforce", "quarantine", "observe"}


class TestMetaEnforcementPublicAPI:
    """Meta-enforcement rules work from public import."""

    def test_min_count(self):
        rule = MinExpectationCountRule(3)
        assert rule.evaluate(5).passed is True
        assert rule.evaluate(2).passed is False

    def test_zero_signal(self):
        rule = ZeroSignalRule()
        assert rule.evaluate(never_failed=True).passed is False
        assert rule.evaluate(never_failed=False).passed is True

    def test_definition_change_guard(self):
        guard = DefinitionChangeGuard()
        h = compute_definition_hash({"rule": "test"})
        assert guard.evaluate(h, h).passed is True

    def test_removal_guard(self):
        guard = ExpectationRemovalGuard()
        r = guard.evaluate({"e1", "e2"}, {"e1"})
        assert r.passed is False


class TestContextPublicAPI:
    """Context functions work from public import."""

    def test_execution_context(self):
        assert not in_execution_context()
        with execution() as exec_id:
            assert in_execution_context()
            assert get_execution_id() == exec_id
        assert not in_execution_context()


class TestSchemaPublicAPI:
    """Schema models work from public import."""

    def test_trace_creation(self):
        t = Trace(
            request=TraceRequest(
                provider="test", model="m1",
                messages=[TraceMessage(role="user", content="hi")],
            ),
            response=TraceResponse(text="hello", latency_ms=100),
            runtime=TraceRuntime(library="test", version="1.0"),
        )
        assert t.trace_id is not None

    def test_verdict_immutable(self):
        v = Verdict(status="pass")
        with pytest.raises(Exception):
            v.status = "fail"
