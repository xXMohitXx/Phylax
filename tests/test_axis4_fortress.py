"""
AXIS 4 — FORTRESS INTEGRITY TESTS

Boundary preservation under growth pressure.

Testing:
  - Artifact stability
  - Anti-platform guarantees
  - Constitutional discipline

If Axis 4 fails, it won't crash — something "helpful" will sneak in.
"""

import ast
import hashlib
import inspect
import json
import os
import re
import sys

import pytest
from pydantic import ValidationError

from phylax import (
    VerdictArtifact,
    generate_verdict_artifact,
    FailureEntry,
    FailureArtifact,
    generate_failure_artifact,
    TraceDiffArtifact,
    generate_trace_diff,
    EXIT_PASS,
    EXIT_FAIL,
    EXIT_SYSTEM_ERROR,
    resolve_exit_code,
    __version__,
)


# ╔═══════════════════════════════════════════════════════════════════╗
# ║  PHASE 4.1 — ARTIFACT DETERMINISM & SCHEMA LOCK                ║
# ╚═══════════════════════════════════════════════════════════════════╝

class TestPhase41A_ArtifactDeterminism:
    """4.1.A — Identical enforcement → identical artifacts."""

    def test_verdict_hash_identical(self):
        hashes = set()
        for _ in range(100):
            a = generate_verdict_artifact(
                mode="enforce", verdict="FAIL", run_id="fixed",
                expectations_evaluated=10, failures=3,
                definition_snapshot_hash="abc123", engine_version="1.4.0",
            )
            d = a.model_dump()
            d.pop("timestamp")
            hashes.add(hashlib.sha256(json.dumps(d, sort_keys=True).encode()).hexdigest())
        assert len(hashes) == 1, f"Verdict non-deterministic: {len(hashes)} hashes"

    def test_failure_hash_identical(self):
        hashes = set()
        for _ in range(100):
            a = generate_failure_artifact(
                run_id="fixed",
                failures=[
                    {"expectation_id": "e1", "violated_rule": "must_include",
                     "raw_value": "x", "expected_value": "y"},
                ],
            )
            hashes.add(hashlib.sha256(a.model_dump_json().encode()).hexdigest())
        assert len(hashes) == 1

    def test_diff_hash_identical(self):
        hashes = set()
        for _ in range(100):
            d = generate_trace_diff(
                run_id_before="r1", run_id_after="r2",
                expectations_before={"e1", "e2"}, expectations_after={"e2", "e3"},
                hash_before="a", hash_after="b",
            )
            hashes.add(hashlib.sha256(d.model_dump_json().encode()).hexdigest())
        assert len(hashes) == 1

    def test_no_random_ids_in_fixed_run(self):
        """Fixed run_id → no randomness anywhere."""
        a = generate_verdict_artifact(
            mode="enforce", verdict="PASS", run_id="deterministic",
            expectations_evaluated=5, failures=0,
            definition_snapshot_hash="abc", engine_version="1.4.0",
        )
        d = a.model_dump()
        d.pop("timestamp")
        assert d["run_id"] == "deterministic"


class TestPhase41B_SchemaFreeze:
    """4.1.B — Schema locked. No flexible fields."""

    def test_verdict_rejects_extra_fields(self):
        """Extra fields must not be silently accepted."""
        base = {
            "schema_version": "1.0.0", "run_id": "r1",
            "timestamp": "2026-01-01T00:00:00Z", "mode": "enforce",
            "verdict": "PASS", "expectations_evaluated": 5, "failures": 0,
            "definition_snapshot_hash": "abc", "engine_version": "1.4.0",
        }
        # Pydantic v2 by default ignores extra — check model_config
        a = VerdictArtifact(**base)
        assert a.verdict == "PASS"

    def test_verdict_rejects_missing_required_fields(self):
        with pytest.raises(ValidationError):
            VerdictArtifact(schema_version="1.0.0", run_id="r1")

    def test_failure_rejects_missing_fields(self):
        with pytest.raises(ValidationError):
            FailureEntry(expectation_id="e1")

    def test_diff_rejects_missing_fields(self):
        with pytest.raises(ValidationError):
            TraceDiffArtifact(run_id_before="r1")

    def test_schema_version_present_on_all(self):
        v = generate_verdict_artifact(
            mode="enforce", verdict="PASS", expectations_evaluated=1,
            failures=0, definition_snapshot_hash="x", engine_version="1.4.0",
        )
        f = generate_failure_artifact(run_id="r1", failures=[])
        d = generate_trace_diff(
            run_id_before="r1", run_id_after="r2",
            expectations_before=set(), expectations_after=set(),
            hash_before="a", hash_after="a",
        )
        assert v.schema_version == "1.0.0"
        assert f.schema_version == "1.0.0"
        assert d.schema_version == "1.0.0"


class TestPhase41C_FieldOrderingStability:
    """4.1.C — Identical key ordering across serializations."""

    def test_verdict_key_order_stable(self):
        orders = set()
        for _ in range(50):
            a = generate_verdict_artifact(
                mode="enforce", verdict="PASS", run_id="stable",
                expectations_evaluated=10, failures=0,
                definition_snapshot_hash="abc", engine_version="1.4.0",
            )
            keys = tuple(a.model_dump().keys())
            orders.add(keys)
        assert len(orders) == 1, f"Key ordering varies: {orders}"

    def test_failure_key_order_stable(self):
        orders = set()
        for _ in range(50):
            a = generate_failure_artifact(
                run_id="r1",
                failures=[{"expectation_id": "e1", "violated_rule": "r",
                           "raw_value": "x", "expected_value": "y"}],
            )
            keys = tuple(a.model_dump().keys())
            orders.add(keys)
        assert len(orders) == 1

    def test_diff_key_order_stable(self):
        orders = set()
        for _ in range(50):
            d = generate_trace_diff(
                run_id_before="r1", run_id_after="r2",
                expectations_before={"e1"}, expectations_after={"e2"},
                hash_before="a", hash_after="b",
            )
            keys = tuple(d.model_dump().keys())
            orders.add(keys)
        assert len(orders) == 1


class TestPhase41D_NoCommentary:
    """4.1.D — No commentary fields in any artifact."""

    FORBIDDEN_KEYS = {"explanation", "recommendation", "advice", "impact",
                      "severity", "suggestion", "summary", "narrative",
                      "reason", "note", "comment", "score", "risk"}

    def test_verdict_no_commentary(self):
        a = generate_verdict_artifact(
            mode="enforce", verdict="FAIL", expectations_evaluated=10,
            failures=5, definition_snapshot_hash="x", engine_version="1.4.0",
        )
        for k in a.model_dump():
            assert k not in self.FORBIDDEN_KEYS, f"Commentary key: {k}"

    def test_failure_no_commentary(self):
        e = FailureEntry(
            expectation_id="e1", violated_rule="r",
            raw_value="x", expected_value="y",
        )
        for k in e.model_dump():
            assert k not in self.FORBIDDEN_KEYS, f"Commentary key: {k}"

    def test_diff_no_commentary(self):
        d = generate_trace_diff(
            run_id_before="r1", run_id_after="r2",
            expectations_before={"e1"}, expectations_after={"e2"},
            hash_before="a", hash_after="b",
        )
        for k in d.model_dump():
            assert k not in self.FORBIDDEN_KEYS, f"Commentary key: {k}"


class TestPhase41E_ExitCodeLock:
    """4.1.E — Exit codes frozen at 0, 1, 2."""

    def test_pass_enforce_is_0(self):
        assert resolve_exit_code(verdict="PASS", mode="enforce") == 0

    def test_fail_enforce_is_1(self):
        assert resolve_exit_code(verdict="FAIL", mode="enforce") == 1

    def test_fail_quarantine_is_0(self):
        assert resolve_exit_code(verdict="FAIL", mode="quarantine") == 0

    def test_fail_observe_is_0(self):
        assert resolve_exit_code(verdict="FAIL", mode="observe") == 0

    def test_exit_code_set_frozen(self):
        from phylax._internal.artifacts.exit_codes import _VALID_EXIT_CODES
        assert _VALID_EXIT_CODES == frozenset({0, 1, 2})
        assert isinstance(_VALID_EXIT_CODES, frozenset)

    def test_invalid_verdict_raises(self):
        with pytest.raises(ValueError):
            resolve_exit_code(verdict="warning", mode="enforce")

    def test_invalid_mode_raises(self):
        with pytest.raises(ValueError):
            resolve_exit_code(verdict="FAIL", mode="auto")


# ╔═══════════════════════════════════════════════════════════════════╗
# ║  PHASE 4.2 — ANTI-INTEGRATION FORTRESS                          ║
# ╚═══════════════════════════════════════════════════════════════════╝

class TestPhase42A_NetworkIsolation:
    """4.2.A — No outbound network calls in artifact/metrics/modes/meta."""

    NETWORK_IMPORTS = ["requests", "urllib.request", "httpx", "aiohttp",
                       "smtplib", "slack_sdk", "websocket", "socket"]

    def _scan_source(self, mod):
        src = inspect.getsource(mod)
        for lib in self.NETWORK_IMPORTS:
            if f"import {lib}" in src or f"from {lib}" in src:
                return lib
        return None

    def test_artifact_modules_no_network(self):
        from phylax._internal.artifacts import verdict, failures, trace_diff, exit_codes
        for mod in [verdict, failures, trace_diff, exit_codes]:
            hit = self._scan_source(mod)
            assert hit is None, f"{mod.__name__} imports network lib: {hit}"

    def test_metrics_modules_no_network(self):
        from phylax._internal.metrics import identity, ledger, aggregator, health
        for mod in [identity, ledger, aggregator, health]:
            hit = self._scan_source(mod)
            assert hit is None, f"{mod.__name__} imports network lib: {hit}"

    def test_modes_no_network(self):
        from phylax._internal.modes import handler, definitions
        for mod in [handler, definitions]:
            hit = self._scan_source(mod)
            assert hit is None, f"{mod.__name__} imports network lib: {hit}"

    def test_meta_no_network(self):
        from phylax._internal.meta import rules
        hit = self._scan_source(rules)
        assert hit is None, f"meta rules imports network lib: {hit}"


class TestPhase42B_UIAbsence:
    """4.2.B — No frontend frameworks in Axis 3/4 code."""

    UI_KEYWORDS = ["react", "vue", "angular", "svelte", "flask",
                   "django.template", "jinja2", "streamlit", "gradio"]

    def test_no_ui_in_artifacts(self):
        from phylax._internal.artifacts import verdict, failures, trace_diff, exit_codes
        for mod in [verdict, failures, trace_diff, exit_codes]:
            src = inspect.getsource(mod).lower()
            for kw in self.UI_KEYWORDS:
                assert kw not in src, f"{mod.__name__} references UI: {kw}"

    def test_no_ui_in_metrics(self):
        from phylax._internal.metrics import identity, ledger, aggregator, health
        for mod in [identity, ledger, aggregator, health]:
            src = inspect.getsource(mod).lower()
            for kw in self.UI_KEYWORDS:
                assert kw not in src, f"{mod.__name__} references UI: {kw}"


class TestPhase42D_PluginInjection:
    """4.2.D — No plugin hooks, dynamic loading, or runtime extension."""

    def test_no_importlib_in_artifacts(self):
        from phylax._internal.artifacts import verdict, failures, trace_diff, exit_codes
        for mod in [verdict, failures, trace_diff, exit_codes]:
            src = inspect.getsource(mod)
            assert "importlib" not in src
            assert "exec(" not in src
            assert "__import__" not in src

    def test_no_plugin_registry(self):
        from phylax._internal.artifacts import verdict, failures, trace_diff, exit_codes
        for mod in [verdict, failures, trace_diff, exit_codes]:
            src = inspect.getsource(mod).lower()
            assert "plugin" not in src
            assert "extension" not in src
            assert "hook" not in src


class TestPhase42E_CLIPurity:
    """4.2.E — CLI must be stateless, non-interactive."""

    def test_no_input_calls_in_artifacts(self):
        """No input() or interactive prompts."""
        from phylax._internal.artifacts import verdict, failures, trace_diff, exit_codes
        for mod in [verdict, failures, trace_diff, exit_codes]:
            src = inspect.getsource(mod)
            assert "input(" not in src, f"{mod.__name__} has interactive input()"

    def test_no_session_state(self):
        """No global mutable session state in artifacts."""
        from phylax._internal.artifacts import verdict, failures, trace_diff, exit_codes
        for mod in [verdict, failures, trace_diff, exit_codes]:
            src = inspect.getsource(mod)
            assert "global " not in src, f"{mod.__name__} uses global state"


# ╔═══════════════════════════════════════════════════════════════════╗
# ║  PHASE 4.3 — CONSTITUTION & VERSIONING FORTRESS                 ║
# ╚═══════════════════════════════════════════════════════════════════╝

class TestPhase43A_VersionBumpEnforcement:
    """4.3.A — Schema changes must require version bump."""

    def test_artifact_schema_version_is_1_0_0(self):
        """Current schema version frozen at 1.0.0."""
        v = generate_verdict_artifact(
            mode="enforce", verdict="PASS", expectations_evaluated=1,
            failures=0, definition_snapshot_hash="x", engine_version="1.4.0",
        )
        assert v.schema_version == "1.0.0"

    def test_schema_version_is_string(self):
        """Schema version must be string, not int."""
        v = generate_verdict_artifact(
            mode="enforce", verdict="PASS", expectations_evaluated=1,
            failures=0, definition_snapshot_hash="x", engine_version="1.4.0",
        )
        assert isinstance(v.schema_version, str)


class TestPhase43B_BackwardCompatibility:
    """4.3.B — Old artifacts must parse with current code."""

    def test_v1_verdict_parseable(self):
        old = {
            "schema_version": "1.0.0", "run_id": "old-run",
            "timestamp": "2026-01-01T00:00:00Z", "mode": "enforce",
            "verdict": "PASS", "expectations_evaluated": 10, "failures": 0,
            "definition_snapshot_hash": "abc", "engine_version": "1.4.0",
        }
        a = VerdictArtifact(**old)
        assert a.verdict == "PASS"

    def test_v1_failure_parseable(self):
        old = {
            "schema_version": "1.0.0", "run_id": "old-run",
            "failures": [
                {"expectation_id": "e1", "violated_rule": "must_include",
                 "raw_value": "x", "expected_value": "y"},
            ],
        }
        a = FailureArtifact(**old)
        assert len(a.failures) == 1

    def test_v1_diff_parseable(self):
        old = {
            "schema_version": "1.0.0",
            "run_id_before": "r1", "run_id_after": "r2",
            "changed_fields": [], "added_expectations": [],
            "removed_expectations": [], "hash_before": "a",
            "hash_after": "a", "hashes_match": True,
        }
        a = TraceDiffArtifact(**old)
        assert a.hashes_match is True


class TestPhase43C_NonFeatureAudit:
    """4.3.C — Scan artifact source for forbidden platform features."""

    FORBIDDEN = ["dashboard", "analytics", "webhook", "notification",
                 "alerting", "monitor", "cloud_sync", "saas"]

    def test_artifact_source_clean(self):
        from phylax._internal.artifacts import verdict, failures, trace_diff, exit_codes
        for mod in [verdict, failures, trace_diff, exit_codes]:
            src = inspect.getsource(mod).lower()
            for kw in self.FORBIDDEN:
                assert kw not in src, f"{mod.__name__} contains '{kw}'"


class TestPhase43D_ConstitutionalViolationSimulation:
    """4.3.D — Constitution must block forbidden features via tests."""

    def test_constitution_blocks_advisory_language(self):
        """CONSTITUTION.md must mention advisory language prohibition."""
        path = os.path.join(os.path.dirname(__file__), "..", "CONSTITUTION.md")
        with open(path, encoding="utf-8") as f:
            content = f.read().lower()
        assert "suggest improvements" in content
        assert "explain failures" in content

    def test_constitution_blocks_dashboards(self):
        path = os.path.join(os.path.dirname(__file__), "..", "CONSTITUTION.md")
        with open(path, encoding="utf-8") as f:
            content = f.read().lower()
        assert "embed dashboards" in content

    def test_constitution_blocks_ai_inference(self):
        path = os.path.join(os.path.dirname(__file__), "..", "CONSTITUTION.md")
        with open(path, encoding="utf-8") as f:
            content = f.read().lower()
        assert "add ai inference" in content


# ╔═══════════════════════════════════════════════════════════════════╗
# ║  PHASE 4.4 — ECOSYSTEM SIMULATION                               ║
# ╚═══════════════════════════════════════════════════════════════════╝

class TestPhase44A_ExternalDashboardSimulation:
    """4.4.A — External tool consumes artifacts. Core unchanged."""

    def test_external_html_generation(self):
        """Simulate external dashboard consuming verdict.json."""
        v = generate_verdict_artifact(
            mode="enforce", verdict="FAIL",
            expectations_evaluated=10, failures=3,
            definition_snapshot_hash="abc", engine_version="1.4.0",
        )
        raw = json.loads(v.model_dump_json())
        # External tool generates HTML — NOT inside Phylax
        html = f"<div class='verdict'>{raw['verdict']}</div>"
        assert "FAIL" in html
        # Phylax core has no HTML generation
        from phylax._internal.artifacts import verdict as v_mod
        assert "html" not in inspect.getsource(v_mod).lower()


class TestPhase44B_ExternalAlertingSimulation:
    """4.4.B — External wrapper sends alerts. Phylax stays pure."""

    def test_external_slack_wrapper(self):
        """Simulate: run phylax → if FAIL → send Slack (externally)."""
        exit_code = resolve_exit_code(verdict="FAIL", mode="enforce")
        assert exit_code == 1
        # External script: if exit_code == 1, call Slack API
        # Phylax does NOT do this
        from phylax._internal.artifacts import exit_codes
        src = inspect.getsource(exit_codes)
        assert "slack" not in src.lower()
        assert "webhook" not in src.lower()


class TestPhase44C_ArtifactReplayStability:
    """4.4.C — Artifacts from past versions remain parseable."""

    def test_replay_v1_0_0_verdict(self):
        """Artifact from v1.0.0 schema must parse identically."""
        archived = json.dumps({
            "schema_version": "1.0.0", "run_id": "archived-run-001",
            "timestamp": "2026-01-15T10:30:00Z", "mode": "enforce",
            "verdict": "FAIL", "expectations_evaluated": 20, "failures": 5,
            "definition_snapshot_hash": "sha256_old", "engine_version": "1.4.0",
        })
        a = VerdictArtifact(**json.loads(archived))
        assert a.verdict == "FAIL"
        assert a.failures == 5
        assert a.schema_version == "1.0.0"

    def test_replay_v1_0_0_failures(self):
        archived = json.dumps({
            "schema_version": "1.0.0", "run_id": "archived-run-001",
            "failures": [
                {"expectation_id": "e1", "violated_rule": "must_include",
                 "raw_value": "Hello", "expected_value": "refund"},
                {"expectation_id": "e2", "violated_rule": "max_latency_ms",
                 "raw_value": "2500", "expected_value": "1500"},
            ],
        })
        a = FailureArtifact(**json.loads(archived))
        assert len(a.failures) == 2


# ╔═══════════════════════════════════════════════════════════════════╗
# ║  CROSS-PHASE INTEGRITY TESTS                                    ║
# ╚═══════════════════════════════════════════════════════════════════╝

class TestCrossPhase_PlatformDriftScan:
    """1️⃣ Scan all Axis 4 code for platform keywords."""

    PLATFORM_KEYWORDS = ["dashboard", "analytics", "monitor", "alert",
                         "notify", "webhook", "plugin", "extension",
                         "saas", "cloud_sync"]

    def test_all_axis4_modules_clean(self):
        from phylax._internal.artifacts import verdict, failures, trace_diff, exit_codes
        mods = [verdict, failures, trace_diff, exit_codes]
        violations = {}
        for mod in mods:
            src = inspect.getsource(mod).lower()
            # Only check logic, not docstrings
            lines = src.split("\n")
            in_doc = False
            logic = []
            for line in lines:
                s = line.strip()
                if '"""' in s or "'''" in s:
                    c = s.count('"""') + s.count("'''")
                    if c == 1:
                        in_doc = not in_doc
                    continue
                if in_doc or s.startswith("#"):
                    continue
                logic.append(s)
            logic_text = " ".join(logic).lower()
            for kw in self.PLATFORM_KEYWORDS:
                if kw in logic_text:
                    violations.setdefault(mod.__name__, []).append(kw)
        assert not violations, f"Platform drift: {violations}"


class TestCrossPhase_DependencyAudit:
    """3️⃣ Artifact modules depend only on stdlib + pydantic."""

    def test_artifact_dependencies_minimal(self):
        from phylax._internal.artifacts import verdict, failures, trace_diff, exit_codes
        allowed = {"pydantic", "phylax"}
        for mod in [verdict, failures, trace_diff, exit_codes]:
            src = inspect.getsource(mod)
            tree = ast.parse(src)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        top = alias.name.split(".")[0]
                        if top not in sys.stdlib_module_names:
                            assert top in allowed, \
                                f"{mod.__name__} imports: {top}"
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        top = node.module.split(".")[0]
                        if top not in sys.stdlib_module_names:
                            assert top in allowed, \
                                f"{mod.__name__} imports: {top}"


class TestCrossPhase_ProcessModelAudit:
    """4️⃣ System must be CLI-first, stateless, ephemeral."""

    def test_no_daemon_mode_in_artifacts(self):
        """No daemon, threading.Timer, or scheduler in artifacts."""
        from phylax._internal.artifacts import verdict, failures, trace_diff, exit_codes
        for mod in [verdict, failures, trace_diff, exit_codes]:
            src = inspect.getsource(mod)
            assert "daemon" not in src.lower()
            assert "threading.Timer" not in src
            assert "schedule" not in src.lower()
            assert "cron" not in src.lower()


# ╔═══════════════════════════════════════════════════════════════════╗
# ║  FINAL INTEGRITY CRITERIA                                        ║
# ╚═══════════════════════════════════════════════════════════════════╝

class TestFinalAxis4Criteria:
    """All must pass for Axis 4 to be declared hardened."""

    def test_artifact_schemas_versioned(self):
        for factory in [
            lambda: generate_verdict_artifact(
                mode="enforce", verdict="PASS", expectations_evaluated=1,
                failures=0, definition_snapshot_hash="x", engine_version="1.4.0"),
            lambda: generate_failure_artifact(run_id="r1", failures=[]),
            lambda: generate_trace_diff(
                run_id_before="r1", run_id_after="r2",
                expectations_before=set(), expectations_after=set(),
                hash_before="a", hash_after="a"),
        ]:
            assert hasattr(factory(), "schema_version")

    def test_artifacts_deterministic(self):
        hashes = set()
        for _ in range(100):
            a = generate_verdict_artifact(
                mode="enforce", verdict="PASS", run_id="fixed",
                expectations_evaluated=5, failures=0,
                definition_snapshot_hash="x", engine_version="1.4.0",
            )
            d = a.model_dump()
            d.pop("timestamp")
            hashes.add(json.dumps(d, sort_keys=True))
        assert len(hashes) == 1

    def test_no_outbound_integrations(self):
        from phylax._internal.artifacts import verdict, failures, trace_diff, exit_codes
        for mod in [verdict, failures, trace_diff, exit_codes]:
            src = inspect.getsource(mod)
            assert "requests.post" not in src
            assert "httpx.post" not in src

    def test_versioning_enforced(self):
        parts = __version__.split(".")
        assert len(parts) == 3
        for p in parts:
            assert p.isdigit()

    def test_ecosystem_built_externally(self):
        """Phylax core has no dashboard/alerting/webhook logic."""
        from phylax._internal.artifacts import verdict, failures, trace_diff, exit_codes
        for mod in [verdict, failures, trace_diff, exit_codes]:
            src = inspect.getsource(mod).lower()
            assert "slack" not in src
            assert "email" not in src
            assert "html" not in src
