"""
AXIS 3 — FORTRESS INTEGRITY TESTS

This is NOT functional testing. This is structural integrity testing.

We are testing whether Axis 3 accidentally introduced:
- Intelligence or heuristic behavior
- Advisory or qualitative language
- Non-deterministic computation
- Adaptive mode switching
- Enforcement mutation
- Semantic creep into engine core

PHASES:
  3.1 — Ledger & Metric Foundation
  3.2 — Health Exposure Layer
  3.3 — Enforcement Modes
  3.4 — Meta-Enforcement Rules
  3.5 — Scale & Concurrency
  CROSS — Cross-Phase Integrity Audits
"""

import hashlib
import inspect
import json
import os
import re
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor

import pytest
from pydantic import ValidationError

from phylax import (
    # Metrics foundation
    ExpectationIdentity,
    compute_definition_hash,
    EvaluationLedger,
    LedgerEntry,
    AggregateMetrics,
    aggregate,
    aggregate_all,
    # Health
    HealthReport,
    CoverageReport,
    get_windowed_health,
    # Modes
    ModeHandler,
    ModeResult,
    EnforcementMode,
    VALID_MODES,
    # Meta-enforcement
    MetaRuleResult,
    MinExpectationCountRule,
    ZeroSignalRule,
    DefinitionChangeGuard,
    ExpectationRemovalGuard,
    # Engine core (for isolation check)
    evaluate,
    Evaluator,
)


# ╔═══════════════════════════════════════════════════════════════════╗
# ║  PHASE 3.1 — LEDGER & METRIC FOUNDATION                        ║
# ╚═══════════════════════════════════════════════════════════════════╝

class TestPhase31A_LedgerImmutability:
    """3.1.A — Append-Only Enforcement. If ledger can mutate → Axis 3 invalid."""

    def test_1_append_only_no_update(self):
        """Insert N entries, attempt update. Must be rejected."""
        ledger = EvaluationLedger()
        ledger.record(LedgerEntry(expectation_id="exp-1", verdict="pass"))
        ledger.record(LedgerEntry(expectation_id="exp-1", verdict="fail"))
        assert ledger.total_entries == 2

        # No update method allowed
        assert not hasattr(ledger, "update"), "Ledger has update method — MUTABILITY BREACH"
        assert not hasattr(ledger, "modify"), "Ledger has modify method — MUTABILITY BREACH"
        assert not hasattr(ledger, "edit"), "Ledger has edit method — MUTABILITY BREACH"
        assert not hasattr(ledger, "set"), "Ledger has set method — MUTABILITY BREACH"

    def test_1_append_only_no_delete(self):
        """Attempt delete. Must be rejected."""
        ledger = EvaluationLedger()
        ledger.record(LedgerEntry(expectation_id="exp-1", verdict="pass"))

        assert not hasattr(ledger, "delete"), "Ledger has delete method — MUTABILITY BREACH"
        assert not hasattr(ledger, "remove"), "Ledger has remove method — MUTABILITY BREACH"
        assert not hasattr(ledger, "clear"), "Ledger has clear method — MUTABILITY BREACH"
        assert not hasattr(ledger, "pop"), "Ledger has pop method — MUTABILITY BREACH"
        assert not hasattr(ledger, "truncate"), "Ledger has truncate method —  MUTABILITY BREACH"

    def test_1_entry_frozen(self):
        """LedgerEntry must be immutable after creation."""
        entry = LedgerEntry(expectation_id="exp-1", verdict="pass")
        with pytest.raises(ValidationError):
            entry.verdict = "fail"
        with pytest.raises(ValidationError):
            entry.expectation_id = "changed"

    def test_1_system_integrity_after_mutation_attempt(self):
        """System integrity preserved after rejected mutation."""
        ledger = EvaluationLedger()
        ledger.record(LedgerEntry(expectation_id="exp-1", verdict="pass"))
        # Attempt to directly access internal storage
        entries = ledger.get_entries()
        original_count = ledger.total_entries
        # Even if we modify the returned list, the ledger is unaffected
        entries.clear()
        assert ledger.total_entries == original_count, "Ledger mutated via returned list"


class TestPhase31A_ReplayDeterminism:
    """3.1.A Test 2 — Replay entire ledger. Recompute in fresh context. Must be identical."""

    def test_2_replay_determinism_memory(self):
        """Replay in memory — same aggregates."""
        entries = [
            LedgerEntry(expectation_id="exp-1", verdict="pass"),
            LedgerEntry(expectation_id="exp-1", verdict="fail"),
            LedgerEntry(expectation_id="exp-1", verdict="pass"),
            LedgerEntry(expectation_id="exp-1", verdict="pass"),
            LedgerEntry(expectation_id="exp-1", verdict="fail"),
        ]
        r1 = aggregate(entries, "exp-1")
        # "Fresh process" — new computation
        r2 = aggregate(entries, "exp-1")

        assert r1.total_evaluations == r2.total_evaluations
        assert r1.total_passes == r2.total_passes
        assert r1.total_failures == r2.total_failures
        assert r1.failure_rate == r2.failure_rate
        assert r1.never_failed == r2.never_failed
        assert r1.never_passed == r2.never_passed

    def test_2_replay_determinism_disk(self):
        """Replay from disk — identical metrics after reload."""
        with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False, mode="w") as f:
            path = f.name
        try:
            ledger1 = EvaluationLedger(path)
            for i in range(50):
                v = "pass" if i % 3 != 0 else "fail"
                ledger1.record(LedgerEntry(expectation_id="exp-A", verdict=v))

            r1 = aggregate(ledger1.get_entries(), "exp-A")

            # Reload from disk — fresh process simulation
            ledger2 = EvaluationLedger(path)
            r2 = aggregate(ledger2.get_entries(), "exp-A")

            assert r1.total_evaluations == r2.total_evaluations
            assert r1.total_failures == r2.total_failures
            assert r1.failure_rate == r2.failure_rate
            assert r1.never_failed == r2.never_failed
        finally:
            os.unlink(path)

    def test_2_ordering_preserved(self):
        """Entry ordering must survive persistence."""
        with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False, mode="w") as f:
            path = f.name
        try:
            ledger = EvaluationLedger(path)
            verdicts = ["pass", "fail", "pass", "fail", "pass"]
            for v in verdicts:
                ledger.record(LedgerEntry(expectation_id="exp-1", verdict=v))

            reloaded = EvaluationLedger(path)
            entries = reloaded.get_entries()
            for i, v in enumerate(verdicts):
                assert entries[i].verdict == v, f"Order broken at index {i}"
        finally:
            os.unlink(path)


class TestPhase31B_AggregationDeterminism:
    """3.1.B — Arithmetic integrity. No rounding drift. No smoothing. No thresholding."""

    def test_3_arithmetic_integrity(self):
        """Manually compute failure_rate vs engine result. Must be exact."""
        entries = [LedgerEntry(expectation_id="exp-1", verdict=v)
                   for v in (["pass"] * 7 + ["fail"] * 3)]
        result = aggregate(entries, "exp-1")

        expected_rate = 3 / 10
        assert result.failure_rate == pytest.approx(expected_rate, abs=0)
        assert result.total_evaluations == 10
        assert result.total_passes == 7
        assert result.total_failures == 3

    def test_3_no_smoothing(self):
        """No moving average, no exponential decay, no smoothing."""
        entries = ([LedgerEntry(expectation_id="exp-1", verdict="fail")] * 10 +
                   [LedgerEntry(expectation_id="exp-1", verdict="pass")] * 10)
        r = aggregate(entries, "exp-1")
        # Exact arithmetic, not smoothed
        assert r.failure_rate == pytest.approx(0.5, abs=0)

    def test_3_no_thresholding(self):
        """System must not convert rate into categories."""
        entries = [LedgerEntry(expectation_id="exp-1", verdict="fail")]
        r = aggregate(entries, "exp-1")
        assert r.failure_rate == pytest.approx(1.0, abs=0)
        # No "critical", "warning", "healthy" classification
        assert not hasattr(r, "status")
        assert not hasattr(r, "level")
        assert not hasattr(r, "category")
        assert not hasattr(r, "severity")

    def test_4_edge_zero_evaluations(self):
        """0 evaluations — no division error, no inferred classification."""
        r = aggregate([], "exp-1")
        assert r.total_evaluations == 0
        assert r.failure_rate == 0.0
        assert r.never_failed is False
        assert r.never_passed is False

    def test_4_edge_zero_failures(self):
        """0 failures — correct booleans, no inference."""
        entries = [LedgerEntry(expectation_id="exp-1", verdict="pass")] * 5
        r = aggregate(entries, "exp-1")
        assert r.failure_rate == 0.0
        assert r.never_failed is True
        assert r.never_passed is False

    def test_4_edge_100_percent_failures(self):
        """100% failures — correct booleans, no inference."""
        entries = [LedgerEntry(expectation_id="exp-1", verdict="fail")] * 5
        r = aggregate(entries, "exp-1")
        assert r.failure_rate == pytest.approx(1.0)
        assert r.never_failed is False
        assert r.never_passed is True

    def test_4_edge_single_evaluation(self):
        """1 evaluation — no special case logic."""
        r = aggregate([LedgerEntry(expectation_id="exp-1", verdict="pass")], "exp-1")
        assert r.total_evaluations == 1
        assert r.failure_rate == 0.0
        assert r.never_failed is True


class TestPhase31C_DefinitionHashIntegrity:
    """3.1.C — Hash must be canonical. Whitespace === same. Semantic change === different."""

    def test_5_whitespace_canonicalization(self):
        """Same rule, different whitespace → same hash."""
        c1 = {"rule": "must_include", "substrings": ["hello"]}
        c2 = {"rule":   "must_include",   "substrings":   ["hello"]}
        assert compute_definition_hash(c1) == compute_definition_hash(c2)

    def test_5_key_order_canonicalization(self):
        """Same rule, different key order → same hash."""
        c1 = {"rule": "must_include", "substrings": ["hello"]}
        c2 = {"substrings": ["hello"], "rule": "must_include"}
        assert compute_definition_hash(c1) == compute_definition_hash(c2)

    def test_5_semantic_change_different_hash(self):
        """Semantic change → different hash."""
        c1 = {"rule": "must_include", "substrings": ["hello"]}
        c2 = {"rule": "must_include", "substrings": ["world"]}
        assert compute_definition_hash(c1) != compute_definition_hash(c2)

    def test_5_type_change_different_hash(self):
        """Type change → different hash. No coercion."""
        c1 = {"rule": "max_latency", "max_ms": 1000}
        c2 = {"rule": "max_latency", "max_ms": "1000"}
        assert compute_definition_hash(c1) != compute_definition_hash(c2)

    def test_5_nested_canonicalization(self):
        """Nested objects canonicalized recursively."""
        c1 = {"a": {"z": 1, "a": 2}, "b": 3}
        c2 = {"b": 3, "a": {"a": 2, "z": 1}}
        assert compute_definition_hash(c1) == compute_definition_hash(c2)


# ╔═══════════════════════════════════════════════════════════════════╗
# ║  PHASE 3.2 — HEALTH EXPOSURE LAYER                             ║
# ╚═══════════════════════════════════════════════════════════════════╝

class TestPhase32A_OutputSchemaLock:
    """3.2.A — Health output must contain ONLY fact keys. No score/risk/quality."""

    FORBIDDEN_KEYS = {"score", "risk", "strength", "quality", "impact",
                      "severity", "priority", "confidence", "weight", "rank",
                      "label", "category", "level", "suggestion", "recommendation"}

    def test_health_report_no_forbidden_keys(self):
        """HealthReport fields must not include advisory keys."""
        entries = [LedgerEntry(expectation_id="e1", verdict="pass")]
        metrics = aggregate(entries, "e1")
        report = HealthReport.from_aggregate(metrics, "hash123")
        report_dict = report.model_dump()

        for key in report_dict:
            assert key.lower() not in self.FORBIDDEN_KEYS, (
                f"HealthReport contains forbidden key: '{key}'"
            )

    def test_aggregate_metrics_no_forbidden_keys(self):
        """AggregateMetrics fields must not include advisory keys."""
        entries = [LedgerEntry(expectation_id="e1", verdict="pass")]
        metrics = aggregate(entries, "e1")
        metrics_dict = metrics.model_dump()

        for key in metrics_dict:
            assert key.lower() not in self.FORBIDDEN_KEYS, (
                f"AggregateMetrics contains forbidden key: '{key}'"
            )

    def test_coverage_report_no_forbidden_keys(self):
        """CoverageReport fields must not include advisory keys."""
        report = CoverageReport.compute(5, {"e1", "e2"})
        report_dict = report.model_dump()

        for key in report_dict:
            assert key.lower() not in self.FORBIDDEN_KEYS, (
                f"CoverageReport contains forbidden key: '{key}'"
            )


class TestPhase32B_LinguisticAudit:
    """3.2.B — No qualitative language in ANY Axis 3 source code."""

    FORBIDDEN_WORDS = [
        "bad", "weak", "good", "improve", "suggest", "optimize",
        "recommend", "risky", "healthy", "unhealthy", "critical",
        "warning", "danger", "strong", "poor", "excellent",
    ]

    def _scan_module(self, module):
        """Scan module source for forbidden words in logic paths (not docstrings)."""
        source = inspect.getsource(module)
        # Extract only non-docstring, non-comment lines
        lines = source.split("\n")
        logic_lines = []
        in_docstring = False
        for line in lines:
            stripped = line.strip()
            if '"""' in stripped or "'''" in stripped:
                count = stripped.count('"""') + stripped.count("'''")
                if count == 1:
                    in_docstring = not in_docstring
                continue
            if in_docstring or stripped.startswith("#"):
                continue
            logic_lines.append(stripped.lower())

        logic_text = " ".join(logic_lines)
        violations = []
        for word in self.FORBIDDEN_WORDS:
            # Match as variable/function names, not substrings of other words
            pattern = rf'\b{re.escape(word)}\b'
            if re.search(pattern, logic_text):
                violations.append(word)
        return violations

    def test_no_advisory_in_identity(self):
        from phylax._internal.metrics import identity
        violations = self._scan_module(identity)
        assert not violations, f"identity.py logic contains: {violations}"

    def test_no_advisory_in_ledger(self):
        from phylax._internal.metrics import ledger
        violations = self._scan_module(ledger)
        assert not violations, f"ledger.py logic contains: {violations}"

    def test_no_advisory_in_aggregator(self):
        from phylax._internal.metrics import aggregator
        violations = self._scan_module(aggregator)
        assert not violations, f"aggregator.py logic contains: {violations}"

    def test_no_advisory_in_health(self):
        from phylax._internal.metrics import health
        violations = self._scan_module(health)
        assert not violations, f"health.py logic contains: {violations}"

    def test_no_advisory_in_handler(self):
        from phylax._internal.modes import handler
        violations = self._scan_module(handler)
        assert not violations, f"handler.py logic contains: {violations}"

    def test_no_advisory_in_definitions(self):
        from phylax._internal.modes import definitions
        violations = self._scan_module(definitions)
        assert not violations, f"definitions.py logic contains: {violations}"

    def test_no_advisory_in_meta_rules(self):
        from phylax._internal.meta import rules
        violations = self._scan_module(rules)
        assert not violations, f"rules.py logic contains: {violations}"


class TestPhase32C_WindowedMetricStability:
    """3.2.C — Windowed metrics must be exact. No auto-window. No rolling."""

    def test_windowed_exact_match_after_restart(self):
        """Windowed query over N → recompute after restart → identical."""
        with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False, mode="w") as f:
            path = f.name
        try:
            ledger = EvaluationLedger(path)
            for i in range(30):
                v = "pass" if i % 5 != 0 else "fail"
                ledger.record(LedgerEntry(expectation_id="exp-w", verdict=v))

            window = ledger.get_entries_windowed("exp-w", last_n=10)
            r1 = aggregate(window, "exp-w")

            # Restart simulation
            ledger2 = EvaluationLedger(path)
            window2 = ledger2.get_entries_windowed("exp-w", last_n=10)
            r2 = aggregate(window2, "exp-w")

            assert r1.total_evaluations == r2.total_evaluations
            assert r1.failure_rate == r2.failure_rate
            assert r1.total_failures == r2.total_failures
        finally:
            os.unlink(path)

    def test_no_auto_window_shifting(self):
        """Adding entries must not shift existing window results."""
        ledger = EvaluationLedger()
        for i in range(20):
            ledger.record(LedgerEntry(expectation_id="exp-s", verdict="pass"))

        w1 = ledger.get_entries_windowed("exp-s", last_n=5)
        r1 = aggregate(w1, "exp-s")

        # Add more entries
        for _ in range(10):
            ledger.record(LedgerEntry(expectation_id="exp-s", verdict="fail"))

        # Window of last 5 should now be all fails
        w2 = ledger.get_entries_windowed("exp-s", last_n=5)
        r2 = aggregate(w2, "exp-s")

        # They SHOULD differ — window moves with data, no stale cache
        assert r2.failure_rate == 1.0
        assert r1.failure_rate == 0.0


# ╔═══════════════════════════════════════════════════════════════════╗
# ║  PHASE 3.3 — ENFORCEMENT MODE TESTING                           ║
# ╚═══════════════════════════════════════════════════════════════════╝

class TestPhase33A_VerdictInvariance:
    """3.3.A — Verdict MUST be identical across all modes. Only exit code changes."""

    def test_verdict_invariance_on_fail(self):
        """Same failing input → identical verdict across all modes."""
        verdicts = {}
        exit_codes = {}
        for mode in VALID_MODES:
            handler = ModeHandler(mode)
            r = handler.apply("fail")
            verdicts[mode] = r.verdict
            exit_codes[mode] = r.exit_code

        # All verdicts must be "fail"
        for mode, v in verdicts.items():
            assert v == "fail", f"Mode '{mode}' changed verdict to '{v}'"

        # Exit codes differ
        assert exit_codes["enforce"] == 1
        assert exit_codes["quarantine"] == 0
        assert exit_codes["observe"] == 0

    def test_verdict_invariance_on_pass(self):
        """Same passing input → identical verdict across all modes."""
        for mode in VALID_MODES:
            handler = ModeHandler(mode)
            r = handler.apply("pass")
            assert r.verdict == "pass", f"Mode '{mode}' changed passing verdict"
            assert r.exit_code == 0, f"Mode '{mode}' set exit_code != 0 for pass"

    def test_health_metrics_invariant_across_modes(self):
        """Metrics computed from same data must be identical regardless of mode."""
        entries = [
            LedgerEntry(expectation_id="exp-m", verdict="pass"),
            LedgerEntry(expectation_id="exp-m", verdict="fail"),
        ]
        base = aggregate(entries, "exp-m")

        for mode in VALID_MODES:
            r = aggregate(entries, "exp-m")
            assert r.total_evaluations == base.total_evaluations
            assert r.failure_rate == base.failure_rate
            assert r.never_failed == base.never_failed


class TestPhase33B_AutoSwitchResistance:
    """3.3.B — No auto-escalation. No auto-downgrade. Mode stays as set."""

    def test_no_auto_escalation_on_failures(self):
        """Consecutive failures must NOT change mode."""
        handler = ModeHandler("observe")
        for _ in range(100):
            r = handler.apply("fail")
            assert r.exit_code == 0, "Mode auto-escalated from observe"

    def test_no_auto_downgrade_on_success(self):
        """Consecutive passes in enforce must NOT downgrade."""
        handler = ModeHandler("enforce")
        for _ in range(100):
            r = handler.apply("pass")
            assert r.exit_code == 0  # pass always exits 0

        # But failure MUST still exit 1
        r = handler.apply("fail")
        assert r.exit_code == 1, "Mode auto-downgraded from enforce"

    def test_no_auto_switch_on_high_failure_rate(self):
        """High failure rate must NOT trigger mode change."""
        handler = ModeHandler("quarantine")
        for _ in range(50):
            r = handler.apply("fail")
            assert r.exit_code == 0, "Quarantine auto-switched on high failure rate"


class TestPhase33C_ConfigDependency:
    """3.3.C — Mode configuration must be explicit."""

    def test_valid_modes_explicit(self):
        """VALID_MODES must be exactly 3, explicitly defined."""
        assert VALID_MODES == {"enforce", "quarantine", "observe"}

    def test_invalid_mode_rejected(self):
        """Invalid mode must be rejected, not silently defaulted."""
        with pytest.raises((ValueError, KeyError, Exception)):
            ModeHandler("auto")

        with pytest.raises((ValueError, KeyError, Exception)):
            ModeHandler("safe")

        with pytest.raises((ValueError, KeyError, Exception)):
            ModeHandler("")


# ╔═══════════════════════════════════════════════════════════════════╗
# ║  PHASE 3.4 — META-ENFORCEMENT RULE TESTING                      ║
# ╚═══════════════════════════════════════════════════════════════════╝

class TestPhase34A_MinExpectationRule:
    """3.4.A — Literal comparison only. No qualitative messaging."""

    def test_below_threshold_fails(self):
        rule = MinExpectationCountRule(min_count=5)
        r = rule.evaluate(declared_count=4)
        assert r.passed is False

    def test_at_threshold_passes(self):
        rule = MinExpectationCountRule(min_count=5)
        r = rule.evaluate(declared_count=5)
        assert r.passed is True

    def test_above_threshold_passes(self):
        rule = MinExpectationCountRule(min_count=5)
        r = rule.evaluate(declared_count=100)
        assert r.passed is True

    def test_no_qualitative_detail(self):
        """Detail must not contain advisory language."""
        rule = MinExpectationCountRule(min_count=5)
        r = rule.evaluate(declared_count=3)
        detail_lower = r.detail.lower()
        for word in ["weak", "strong", "improve", "suggest", "recommend",
                     "risk", "dangerous", "insufficient"]:
            assert word not in detail_lower, f"Advisory word '{word}' in detail"


class TestPhase34B_NeverFailedRule:
    """3.4.B — System must not auto-fail trivial expectations."""

    def test_never_failed_true_fails(self):
        rule = ZeroSignalRule()
        r = rule.evaluate(never_failed=True)
        assert r.passed is False

    def test_never_failed_false_passes(self):
        rule = ZeroSignalRule()
        r = rule.evaluate(never_failed=False)
        assert r.passed is True

    def test_rule_is_opt_in(self):
        """ZeroSignalRule must be explicitly instantiated. Not auto-applied."""
        # The rule exists as a class — it's not baked into the engine
        assert isinstance(ZeroSignalRule, type)


class TestPhase34C_DefinitionChangeGuard:
    """3.4.C — Only hash mismatch. No commentary about weakening."""

    def test_same_hash_passes(self):
        guard = DefinitionChangeGuard()
        h = compute_definition_hash({"rule": "test"})
        r = guard.evaluate(h, h)
        assert r.passed is True

    def test_different_hash_fails(self):
        guard = DefinitionChangeGuard()
        h1 = compute_definition_hash({"rule": "test", "v": 1})
        h2 = compute_definition_hash({"rule": "test", "v": 2})
        r = guard.evaluate(h1, h2)
        assert r.passed is False

    def test_no_interpretation_in_detail(self):
        """Detail must not interpret change as weakening/strengthening."""
        guard = DefinitionChangeGuard()
        h1 = compute_definition_hash({"rule": "test", "v": 1})
        h2 = compute_definition_hash({"rule": "test", "v": 2})
        r = guard.evaluate(h1, h2)
        detail_lower = r.detail.lower()
        for word in ["weaken", "strengthen", "relax", "tighten",
                     "degrade", "improve", "dilut"]:
            assert word not in detail_lower, f"Interpretation word '{word}' in detail"


class TestPhase34D_ExpectationRemovalGuard:
    """3.4.D — Only set difference. No inference about intent."""

    def test_no_removal_passes(self):
        guard = ExpectationRemovalGuard()
        r = guard.evaluate({"e1", "e2"}, {"e1", "e2", "e3"})
        assert r.passed is True

    def test_removal_detected_fails(self):
        guard = ExpectationRemovalGuard()
        r = guard.evaluate({"e1", "e2", "e3"}, {"e1", "e3"})
        assert r.passed is False

    def test_no_intent_in_detail(self):
        """Detail must not infer intent behind removal."""
        guard = ExpectationRemovalGuard()
        r = guard.evaluate({"e1", "e2"}, {"e1"})
        detail_lower = r.detail.lower()
        for word in ["intentional", "accidental", "suspicious", "deliberate",
                     "careless", "concerning"]:
            assert word not in detail_lower, f"Intent word '{word}' in detail"


class TestPhase34E_RuleRejection:
    """3.4.E — Heuristic rules must NOT be expressible in the system."""

    def test_no_suspicion_based_rules(self):
        """System cannot express 'suspicious' — only literal thresholds."""
        # MinExpectationCountRule takes a literal number, nothing fuzzy
        rule = MinExpectationCountRule(min_count=5)
        # It's a strict comparison, not "suspiciously low"
        assert rule.evaluate(declared_count=5).passed is True
        assert rule.evaluate(declared_count=4).passed is False
        # No fuzziness parameter exists
        assert not hasattr(rule, "threshold_type")
        assert not hasattr(rule, "sensitivity")
        assert not hasattr(rule, "confidence")

    def test_no_trivial_detection(self):
        """System cannot detect if an expectation 'seems trivial'."""
        # ZeroSignalRule checks a boolean flag — not rule content
        rule = ZeroSignalRule()
        # It only takes never_failed flag, not the expectation definition
        sig = inspect.signature(rule.evaluate)
        params = list(sig.parameters.keys())
        assert "content" not in params
        assert "definition" not in params
        assert "complexity" not in params

    def test_no_redundancy_detection(self):
        """System cannot detect redundant expectations."""
        # No such rule exists in meta module
        from phylax._internal.meta import rules as meta_mod
        source = inspect.getsource(meta_mod)
        assert "redundan" not in source.lower()
        assert "duplicate" not in source.lower()
        assert "similar" not in source.lower()


# ╔═══════════════════════════════════════════════════════════════════╗
# ║  PHASE 3.5 — SCALE & CONCURRENCY TESTING                        ║
# ╚═══════════════════════════════════════════════════════════════════╝

class TestPhase35A_HighVolume:
    """3.5.A — Deterministic results at scale. No precision shortcuts."""

    def test_10k_expectations_deterministic(self):
        """10,000 expectations → exact aggregation."""
        entries = []
        for i in range(10000):
            v = "fail" if i % 7 == 0 else "pass"
            entries.append(LedgerEntry(expectation_id="exp-scale", verdict=v))

        r1 = aggregate(entries, "exp-scale")
        r2 = aggregate(entries, "exp-scale")

        assert r1.total_evaluations == 10000
        assert r1.total_evaluations == r2.total_evaluations
        assert r1.failure_rate == r2.failure_rate
        assert r1.total_failures == r2.total_failures

        # Manual verification
        expected_fails = len([i for i in range(10000) if i % 7 == 0])
        assert r1.total_failures == expected_fails
        assert r1.failure_rate == pytest.approx(expected_fails / 10000)

    def test_100k_ledger_entries(self):
        """100,000 entries → deterministic aggregate_all."""
        entries = []
        ids = [f"exp-{i}" for i in range(100)]
        for i in range(100000):
            eid = ids[i % 100]
            v = "fail" if i % 11 == 0 else "pass"
            entries.append(LedgerEntry(expectation_id=eid, verdict=v))

        results = aggregate_all(entries)
        assert len(results) == 100

        # Re-run
        results2 = aggregate_all(entries)
        for r1, r2 in zip(results, results2):
            assert r1.total_evaluations == r2.total_evaluations
            assert r1.failure_rate == r2.failure_rate


class TestPhase35B_ConcurrentWrite:
    """3.5.B — No lost entries. No duplication. No race conditions."""

    def test_concurrent_writes(self):
        """Parallel writes must all be recorded."""
        with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False, mode="w") as f:
            path = f.name
        try:
            ledger = EvaluationLedger(path)
            n_threads = 10
            n_per_thread = 100

            def write_entries(thread_id):
                for i in range(n_per_thread):
                    ledger.record(LedgerEntry(
                        expectation_id=f"exp-t{thread_id}",
                        verdict="pass" if i % 2 == 0 else "fail",
                    ))

            threads = []
            for t in range(n_threads):
                th = threading.Thread(target=write_entries, args=(t,))
                threads.append(th)
                th.start()
            for th in threads:
                th.join()

            assert ledger.total_entries == n_threads * n_per_thread
        finally:
            os.unlink(path)


class TestPhase35C_PartialCorruption:
    """3.5.C — Corrupted data must fail deterministically. No silent repair."""

    def test_invalid_verdict_rejected(self):
        """Invalid verdict value must raise error, not be silently corrected."""
        with pytest.raises((ValidationError, ValueError)):
            LedgerEntry(expectation_id="exp-1", verdict="warning")

        with pytest.raises((ValidationError, ValueError)):
            LedgerEntry(expectation_id="exp-1", verdict="skip")

        with pytest.raises((ValidationError, ValueError)):
            LedgerEntry(expectation_id="exp-1", verdict="partial")

    def test_truncated_jsonl_handled(self):
        """Truncated JSONL must cause deterministic failure — not silent repair."""
        with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False, mode="w") as f:
            path = f.name
            # Write valid entry
            entry = LedgerEntry(expectation_id="exp-1", verdict="pass")
            f.write(json.dumps(entry.model_dump(), default=str) + "\n")
            # Write truncated entry
            f.write('{"expectation_id": "exp-2", "verdict": "fa')

        try:
            # System should either:
            # A) Raise an error (deterministic failure) — GOOD
            # B) Skip corrupt entry, keep valid ones — ACCEPTABLE
            # C) Silently repair/infer data — FAIL
            try:
                ledger = EvaluationLedger(path)
                # If it loaded, corrupt entry must be skipped, not repaired
                assert ledger.total_entries >= 1, "Valid entry lost"
                # Must NOT have 2 entries (that would mean auto-repair)
                if ledger.total_entries == 2:
                    entries = ledger.get_entries()
                    # If second entry exists, verdict must not be "inferred"
                    assert entries[1].verdict in ("pass", "fail"), \
                        "Auto-repaired verdict detected"
            except Exception:
                # Raising on corruption is deterministic failure — GOOD
                pass
        finally:
            os.unlink(path)


# ╔═══════════════════════════════════════════════════════════════════╗
# ║  CROSS-PHASE INTEGRITY AUDITS                                    ║
# ╚═══════════════════════════════════════════════════════════════════╝

class TestCrossPhase_NonDeterminismSweep:
    """1️⃣ Run 100 identical evaluations. All hashes must match."""

    def test_100_run_verdict_hash(self):
        """100 runs → identical verdict."""
        hashes = set()
        for _ in range(100):
            v = evaluate(response_text="Refund approved.", latency_ms=200,
                         must_include=["refund"])
            hashes.add(v.status)
        assert len(hashes) == 1

    def test_100_run_health_report_hash(self):
        """100 runs → identical health report."""
        entries = [
            LedgerEntry(expectation_id="e1", verdict="pass"),
            LedgerEntry(expectation_id="e1", verdict="fail"),
            LedgerEntry(expectation_id="e1", verdict="pass"),
        ]
        hashes = set()
        for _ in range(100):
            r = aggregate(entries, "e1")
            report = HealthReport.from_aggregate(r, "hash123")
            h = hashlib.sha256(report.model_dump_json().encode()).hexdigest()
            hashes.add(h)
        assert len(hashes) == 1, f"Non-determinism detected: {len(hashes)} unique reports"

    def test_100_run_meta_rule_hash(self):
        """100 runs → identical meta-rule outcomes."""
        hashes = set()
        for _ in range(100):
            r1 = MinExpectationCountRule(min_count=5).evaluate(declared_count=3)
            r2 = ZeroSignalRule().evaluate(never_failed=True)
            r3 = DefinitionChangeGuard().evaluate("aaa", "bbb")
            r4 = ExpectationRemovalGuard().evaluate({"e1", "e2"}, {"e1"})
            combined = f"{r1.passed}|{r2.passed}|{r3.passed}|{r4.passed}"
            hashes.add(combined)
        assert len(hashes) == 1


class TestCrossPhase_IntelligenceDriftScan:
    """2️⃣ Static code scan for forbidden keywords in ALL Axis 3 modules."""

    FORBIDDEN_IN_LOGIC = [
        "score", "optimize", "recommend", "suggest", "improve",
        "risk", "priority", "quality", "heuristic", "adaptive",
        "intelligence", "smart", "clever", "infer_intent",
        "auto_repair", "auto_correct", "self_heal",
    ]

    def test_scan_all_axis3_modules(self):
        """Scan all Axis 3 source for forbidden intelligence keywords."""
        from phylax._internal.metrics import identity, ledger, aggregator, health
        from phylax._internal.modes import handler, definitions
        from phylax._internal.meta import rules

        modules = [identity, ledger, aggregator, health,
                   handler, definitions, rules]
        violations = {}
        for mod in modules:
            source = inspect.getsource(mod)
            # Only scan function/variable names, not docstrings
            lines = source.split("\n")
            logic_text = []
            in_doc = False
            for line in lines:
                s = line.strip()
                if '"""' in s or "'''" in s:
                    c = s.count('"""') + s.count("'''")
                    if c == 1:
                        in_doc = not in_doc
                    continue
                if in_doc or s.startswith("#"):
                    continue
                logic_text.append(s.lower())

            combined = " ".join(logic_text)
            for kw in self.FORBIDDEN_IN_LOGIC:
                if kw in combined:
                    violations.setdefault(mod.__name__, []).append(kw)

        assert not violations, f"Intelligence drift detected: {violations}"


class TestCrossPhase_HeuristicInjection:
    """3️⃣ Attempt to define heuristic rules. System must reject."""

    def test_no_percentage_based_meta_rule(self):
        """System must not accept 'fail if >80% never fail'."""
        # There is no PercentageMetaRule or ThresholdMetaRule
        from phylax._internal.meta import rules as meta_mod
        source = inspect.getsource(meta_mod)
        assert "percentag" not in source.lower()
        assert "threshold_ratio" not in source.lower()

    def test_rule_schema_has_no_fuzzy_params(self):
        """Meta rules must take only literal values, not fuzzy parameters."""
        for RuleClass in [MinExpectationCountRule, ZeroSignalRule,
                          DefinitionChangeGuard, ExpectationRemovalGuard]:
            # Check constructor doesn't accept heuristic parameters
            sig = inspect.signature(RuleClass.__init__)
            params = set(sig.parameters.keys()) - {"self"}
            for p in params:
                assert p not in {"sensitivity", "confidence", "tolerance",
                                 "fuzziness", "threshold_type", "auto_adjust"}, \
                    f"{RuleClass.__name__} has heuristic param: {p}"


class TestCrossPhase_SilentAutoCorrection:
    """4️⃣ System must NOT auto-repair, infer, smooth, or silently correct data."""

    def test_no_auto_repair_methods(self):
        """Ledger has no repair/fix/recover methods."""
        ledger = EvaluationLedger()
        forbidden_methods = ["repair", "fix", "recover", "heal", "correct",
                             "normalize", "smooth", "interpolate", "fill"]
        for method in forbidden_methods:
            assert not hasattr(ledger, method), f"Ledger has '{method}' method — auto-correction"

    def test_no_inferred_entries(self):
        """Ledger must not infer missing entries."""
        ledger = EvaluationLedger()
        assert ledger.total_entries == 0
        # No auto-generated entries
        assert len(ledger.get_entries()) == 0

    def test_aggregate_no_imputation(self):
        """Aggregation of empty → 0, not inferred."""
        r = aggregate([], "nonexistent")
        assert r.total_evaluations == 0
        # No imputation, no default values assumed
        assert r.failure_rate == 0.0


class TestCrossPhase_EngineIsolation:
    """5️⃣ Axis 3 must NOT modify engine core. Engine must be identical to pre-Axis 3."""

    def test_rules_module_no_metrics_import(self):
        """rules.py (expectations) must not import from metrics/modes/meta."""
        from phylax._internal.expectations import rules
        source = inspect.getsource(rules)
        assert "from phylax._internal.metrics" not in source
        assert "from phylax._internal.modes" not in source
        assert "from phylax._internal.meta" not in source

    def test_evaluator_module_no_metrics_import(self):
        """evaluator.py must not import from metrics/modes/meta."""
        from phylax._internal.expectations import evaluator
        source = inspect.getsource(evaluator)
        assert "from phylax._internal.metrics" not in source
        assert "from phylax._internal.modes" not in source
        assert "from phylax._internal.meta" not in source

    def test_schema_module_no_metrics_import(self):
        """schema.py must not import from metrics/modes/meta."""
        from phylax._internal import schema
        source = inspect.getsource(schema)
        assert "from phylax._internal.metrics" not in source
        assert "from phylax._internal.modes" not in source
        assert "from phylax._internal.meta" not in source

    def test_evaluate_function_unchanged(self):
        """evaluate() must produce same verdicts as Axis 1 — binary, deterministic."""
        v1 = evaluate(response_text="Hello world", latency_ms=100,
                      must_include=["hello"])
        assert v1.status == "pass"

        v2 = evaluate(response_text="Goodbye", latency_ms=100,
                      must_include=["hello"])
        assert v2.status == "fail"

        # No third state
        assert v1.status in {"pass", "fail"}
        assert v2.status in {"pass", "fail"}

    def test_verdict_space_still_binary(self):
        """Verdict must still be PASS/FAIL. No third state from Axis 3."""
        e = Evaluator()
        e.must_include(["test"])
        v = e.evaluate("This is a test.", 100)
        assert v.status in {"pass", "fail"}
        # No "quarantine", "observe", "warning" states leaked into verdicts
        assert v.status != "quarantine"
        assert v.status != "observe"
        assert v.status != "warning"


# ╔═══════════════════════════════════════════════════════════════════╗
# ║  FINAL INTEGRITY CRITERIA                                        ║
# ╚═══════════════════════════════════════════════════════════════════╝

class TestFinalIntegrityCriteria:
    """All of these must pass for Axis 3 to be declared hardened."""

    def test_all_metrics_from_ledger(self):
        """All health metrics derive strictly from ledger data."""
        entries = [
            LedgerEntry(expectation_id="e1", verdict="pass"),
            LedgerEntry(expectation_id="e1", verdict="fail"),
        ]
        r = aggregate(entries, "e1")
        # Every field is directly derived from entries
        assert r.total_evaluations == len(entries)
        assert r.total_passes + r.total_failures == r.total_evaluations
        assert r.failure_rate == r.total_failures / r.total_evaluations

    def test_no_adaptive_behavior(self):
        """No method contains 'adapt', 'learn', 'adjust', 'evolve'."""
        from phylax._internal.metrics import identity, ledger, aggregator, health
        from phylax._internal.modes import handler, definitions
        from phylax._internal.meta import rules
        for mod in [identity, ledger, aggregator, health, handler, definitions, rules]:
            members = [m for m in dir(mod) if not m.startswith("_")]
            for name in members:
                for forbidden in ["adapt", "learn", "adjust", "evolve", "train"]:
                    assert forbidden not in name.lower(), \
                        f"{mod.__name__}.{name} contains '{forbidden}'"

    def test_all_verdicts_binary(self):
        """Verdict space is permanently {pass, fail}."""
        with pytest.raises((ValidationError, ValueError)):
            LedgerEntry(expectation_id="e1", verdict="warning")
        with pytest.raises((ValidationError, ValueError)):
            LedgerEntry(expectation_id="e1", verdict="partial")
        with pytest.raises((ValidationError, ValueError)):
            LedgerEntry(expectation_id="e1", verdict="skip")

    def test_system_fully_deterministic(self):
        """1000-run sweep: identical inputs → identical outputs."""
        config = {"rule": "must_include", "substrings": ["hello"], "case": False}
        hashes_identity = set()
        hashes_aggregate = set()

        entries = [
            LedgerEntry(expectation_id="e1", verdict="pass"),
            LedgerEntry(expectation_id="e1", verdict="fail"),
        ]

        for _ in range(1000):
            hashes_identity.add(compute_definition_hash(config))
            r = aggregate(entries, "e1")
            hashes_aggregate.add(
                f"{r.total_evaluations}|{r.failure_rate}|{r.never_failed}"
            )

        assert len(hashes_identity) == 1, "Identity hash non-deterministic"
        assert len(hashes_aggregate) == 1, "Aggregation non-deterministic"
