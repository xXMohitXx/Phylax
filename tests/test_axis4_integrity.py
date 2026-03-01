"""
PHASE 4.2 — ANTI-INTEGRATION GUARANTEES
PHASE 4.3 — GOVERNANCE ENFORCEMENT
PHASE 4.4 — ECOSYSTEM FIT VALIDATION

Proves Phylax resists platformization.
"""

import ast
import importlib
import inspect
import json
import os
import sys

import pytest

from phylax import (
    VerdictArtifact,
    generate_verdict_artifact,
    FailureArtifact,
    generate_failure_artifact,
    TraceDiffArtifact,
    generate_trace_diff,
    EXIT_PASS,
    EXIT_FAIL,
    EXIT_SYSTEM_ERROR,
    resolve_exit_code,
    compute_definition_hash,
    __version__,
)


# ╔═══════════════════════════════════════════════════════════════════╗
# ║  PHASE 4.2 — ANTI-INTEGRATION GUARANTEES                        ║
# ╚═══════════════════════════════════════════════════════════════════╝

class TestAntiIntegration_NoDashboards:
    """4.2.1 — No embedded dashboard code in Axis 3/4 modules."""

    def test_no_chart_libraries(self):
        """No matplotlib, plotly, chart.js, or visualization imports."""
        from phylax._internal import artifacts
        from phylax._internal.metrics import identity, ledger, aggregator, health
        from phylax._internal.modes import handler
        from phylax._internal.meta import rules
        mods = [artifacts, identity, ledger, aggregator, health, handler, rules]
        viz_libs = ["matplotlib", "plotly", "bokeh", "seaborn", "chart", "d3"]
        for mod in mods:
            src = inspect.getsource(mod)
            for lib in viz_libs:
                assert lib not in src.lower(), f"{mod.__name__} imports {lib}"


class TestAntiIntegration_NoAlerting:
    """4.2.2 — No built-in alerting in ANY Axis 3/4 module."""

    def test_no_network_calls(self):
        """No requests, urllib, httpx, smtp, slack, webhook imports."""
        from phylax._internal.artifacts import verdict, failures, trace_diff, exit_codes
        from phylax._internal.metrics import identity, ledger, aggregator, health
        from phylax._internal.modes import handler
        from phylax._internal.meta import rules
        mods = [verdict, failures, trace_diff, exit_codes,
                identity, ledger, aggregator, health, handler, rules]
        network = ["requests", "urllib", "httpx", "smtp", "slack",
                    "webhook", "socket", "aiohttp"]
        for mod in mods:
            src = inspect.getsource(mod)
            for lib in network:
                assert f"import {lib}" not in src, f"{mod.__name__} imports {lib}"


class TestAntiIntegration_NoBackgroundServices:
    """4.2.3 — No daemon, scheduler, or background thread in Axis 3/4."""

    def test_no_daemon_code(self):
        from phylax._internal.artifacts import verdict, failures, trace_diff, exit_codes
        from phylax._internal.metrics import identity, ledger, aggregator, health
        mods = [verdict, failures, trace_diff, exit_codes,
                identity, ledger, aggregator, health]
        daemon_keywords = ["daemon", "scheduler", "crontab", "background",
                           "asyncio.run", "threading.Timer"]
        for mod in mods:
            src = inspect.getsource(mod)
            for kw in daemon_keywords:
                assert kw not in src, f"{mod.__name__} contains '{kw}'"


class TestAntiIntegration_NoPluginSystem:
    """4.2.4 — No plugin loading, extension marketplace, or runtime injection."""

    def test_no_plugin_infrastructure(self):
        from phylax._internal.artifacts import verdict, failures, trace_diff, exit_codes
        from phylax._internal.metrics import identity, ledger, aggregator, health
        mods = [verdict, failures, trace_diff, exit_codes,
                identity, ledger, aggregator, health]
        plugin_keywords = ["plugin", "extension", "marketplace", "load_module",
                           "importlib.import_module", "exec("]
        for mod in mods:
            src = inspect.getsource(mod)
            for kw in plugin_keywords:
                assert kw not in src.lower(), f"{mod.__name__} contains '{kw}'"


# ╔═══════════════════════════════════════════════════════════════════╗
# ║  PHASE 4.3 — GOVERNANCE ENFORCEMENT                             ║
# ╚═══════════════════════════════════════════════════════════════════╝

class TestGovernance_Constitution:
    """4.3.2 — CONSTITUTION.md must exist and contain key promises."""

    def test_constitution_exists(self):
        path = os.path.join(os.path.dirname(__file__), "..", "CONSTITUTION.md")
        assert os.path.exists(path), "CONSTITUTION.md missing"

    def test_constitution_contains_key_promises(self):
        path = os.path.join(os.path.dirname(__file__), "..", "CONSTITUTION.md")
        with open(path, encoding="utf-8") as f:
            content = f.read().lower()

        promises = [
            "explain failures",
            "rank expectations",
            "suggest improvements",
            "add ai inference",
            "embed dashboards",
            "send alerts",
            "auto-adjust",
            "plugin system",
            "daemon",
        ]
        for p in promises:
            assert p in content, f"Constitution missing promise: '{p}'"


class TestGovernance_AntiFeatures:
    """4.3.2 — ANTI_FEATURES.md must exist."""

    def test_anti_features_exists(self):
        path = os.path.join(os.path.dirname(__file__), "..", "ANTI_FEATURES.md")
        assert os.path.exists(path), "ANTI_FEATURES.md missing"


class TestGovernance_VersioningDiscipline:
    """4.3.1 — Version must follow semantic versioning."""

    def test_version_is_semver(self):
        parts = __version__.split(".")
        assert len(parts) == 3, f"Version not semver: {__version__}"
        for p in parts:
            assert p.isdigit(), f"Version part not numeric: {p}"


class TestGovernance_ArtifactSchemaVersioned:
    """4.3.4 — All artifacts must have schema_version field."""

    def test_verdict_has_schema_version(self):
        a = generate_verdict_artifact(
            mode="enforce", verdict="PASS",
            expectations_evaluated=1, failures=0,
            definition_snapshot_hash="x", engine_version="1.4.0",
        )
        assert hasattr(a, "schema_version")

    def test_failure_has_schema_version(self):
        a = generate_failure_artifact(run_id="r1", failures=[])
        assert hasattr(a, "schema_version")

    def test_diff_has_schema_version(self):
        a = generate_trace_diff(
            run_id_before="r1", run_id_after="r2",
            expectations_before=set(), expectations_after=set(),
            hash_before="a", hash_after="a",
        )
        assert hasattr(a, "schema_version")


# ╔═══════════════════════════════════════════════════════════════════╗
# ║  PHASE 4.4 — ECOSYSTEM FIT VALIDATION                           ║
# ╚═══════════════════════════════════════════════════════════════════╝

class TestEcosystemFit_ExternalConsumerSimulation:
    """4.4.1 — Prove external tools can parse Phylax artifacts."""

    def test_verdict_parseable_by_external_json(self):
        """External tool can parse verdict.json without Phylax SDK."""
        a = generate_verdict_artifact(
            mode="enforce", verdict="FAIL",
            expectations_evaluated=10, failures=3,
            definition_snapshot_hash="abc123", engine_version="1.4.0",
        )
        raw_json = a.model_dump_json()
        # Simulate external consumer — raw JSON parsing, no Phylax import
        parsed = json.loads(raw_json)
        assert parsed["verdict"] == "FAIL"
        assert parsed["failures"] == 3
        assert parsed["mode"] == "enforce"
        assert "schema_version" in parsed

    def test_failure_parseable_by_external_json(self):
        a = generate_failure_artifact(
            run_id="run-1",
            failures=[
                {"expectation_id": "e1", "violated_rule": "must_include",
                 "raw_value": "Hello", "expected_value": "refund"},
            ],
        )
        parsed = json.loads(a.model_dump_json())
        assert len(parsed["failures"]) == 1
        assert parsed["failures"][0]["expectation_id"] == "e1"

    def test_diff_parseable_by_external_json(self):
        d = generate_trace_diff(
            run_id_before="r1", run_id_after="r2",
            expectations_before={"e1", "e2"}, expectations_after={"e2", "e3"},
            hash_before="a", hash_after="b",
        )
        parsed = json.loads(d.model_dump_json())
        assert "e1" in parsed["removed_expectations"]
        assert "e3" in parsed["added_expectations"]

    def test_exit_code_consumable_by_ci(self):
        """CI systems only need exit code — no SDK required."""
        assert resolve_exit_code(verdict="PASS", mode="enforce") == 0
        assert resolve_exit_code(verdict="FAIL", mode="enforce") == 1
        # CI script: `phylax check; if ($LASTEXITCODE -eq 1) { fail }`


class TestEcosystemFit_ArtifactStability:
    """4.4.2 — Artifacts from this version are forward-parseable."""

    def test_verdict_schema_v1_parseable(self):
        """v1.0.0 schema artifacts must remain parseable."""
        v1_json = {
            "schema_version": "1.0.0",
            "run_id": "test-run",
            "timestamp": "2026-03-01T00:00:00Z",
            "mode": "enforce",
            "verdict": "PASS",
            "expectations_evaluated": 10,
            "failures": 0,
            "definition_snapshot_hash": "abc123",
            "engine_version": "1.4.0",
        }
        a = VerdictArtifact(**v1_json)
        assert a.verdict == "PASS"

    def test_failure_schema_v1_parseable(self):
        v1_json = {
            "schema_version": "1.0.0",
            "run_id": "test-run",
            "failures": [
                {"expectation_id": "e1", "violated_rule": "must_include",
                 "raw_value": "x", "expected_value": "y"},
            ],
        }
        a = FailureArtifact(**v1_json)
        assert len(a.failures) == 1

    def test_diff_schema_v1_parseable(self):
        v1_json = {
            "schema_version": "1.0.0",
            "run_id_before": "r1",
            "run_id_after": "r2",
            "changed_fields": ["verdict"],
            "added_expectations": ["e3"],
            "removed_expectations": ["e1"],
            "hash_before": "a",
            "hash_after": "b",
            "hashes_match": False,
        }
        a = TraceDiffArtifact(**v1_json)
        assert a.hashes_match is False


class TestEcosystemFit_MinimalFootprint:
    """4.4.3 — Minimal binary footprint audit."""

    def test_no_heavy_dependencies_in_artifacts(self):
        """Artifact modules must not import heavy libraries."""
        from phylax._internal.artifacts import verdict, failures, trace_diff, exit_codes
        mods = [verdict, failures, trace_diff, exit_codes]
        heavy = ["numpy", "pandas", "scipy", "tensorflow", "torch",
                 "sklearn", "transformers", "pillow", "opencv"]
        for mod in mods:
            src = inspect.getsource(mod)
            for lib in heavy:
                assert lib not in src, f"{mod.__name__} imports heavy lib: {lib}"

    def test_artifact_modules_import_only_stdlib_and_pydantic(self):
        """Artifact modules must only depend on stdlib + pydantic."""
        from phylax._internal.artifacts import verdict, failures, trace_diff, exit_codes
        mods = [verdict, failures, trace_diff, exit_codes]
        allowed_third_party = {"pydantic"}
        for mod in mods:
            src = inspect.getsource(mod)
            tree = ast.parse(src)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        top = alias.name.split(".")[0]
                        if top not in dir(__builtins__) and top not in sys.stdlib_module_names:
                            assert top in allowed_third_party, \
                                f"{mod.__name__} imports non-allowed: {top}"
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        top = node.module.split(".")[0]
                        if top not in sys.stdlib_module_names and top != "phylax":
                            assert top in allowed_third_party, \
                                f"{mod.__name__} imports non-allowed: {top}"
