"""
Phase-test 16 — Installation & Package Verification

Goal: Verify package metadata, public API completeness, and
that all documented imports work from a fresh import.
"""
import pytest
import importlib


class TestPackageMetadata:
    """PT16.1: Package metadata must be correct."""

    def test_version_in_init(self):
        import phylax
        assert hasattr(phylax, "__version__")
        assert phylax.__version__ == "1.6.5"

    def test_package_name(self):
        import phylax
        assert phylax.__name__ == "phylax"

    def test_pyproject_version_matches(self):
        """pyproject.toml version must match __version__."""
        import phylax
        try:
            import tomllib
        except ImportError:
            import tomli as tomllib
        with open("pyproject.toml", "rb") as f:
            pyproject = tomllib.load(f)
        assert pyproject["project"]["version"] == phylax.__version__


class TestPublicAPICompleteness:
    """PT16.2: All expected public symbols must exist."""

    EXPECTED_SYMBOLS = [
        # Core dataset
        "Dataset", "DatasetCase", "run_dataset",
        # Diff engine
        "diff_runs", "format_diff_report", "format_diff_json",
        # Simulator
        "simulate_upgrade", "format_simulation_report",
        # Artifacts
        "generate_verdict_artifact",
        "generate_failure_artifact",
        "generate_trace_diff",
        # Reports
        "format_report", "format_json_report",
        # Guardrail Packs
        "safety_pack", "quality_pack", "compliance_pack",
        "list_packs", "get_pack", "apply_pack",
        # Graph
        "ExecutionGraph", "NodeRole",
        # Version
        "__version__",
    ]

    def test_all_expected_symbols_exist(self):
        import phylax
        missing = []
        for sym in self.EXPECTED_SYMBOLS:
            if not hasattr(phylax, sym):
                missing.append(sym)
        assert missing == [], f"Missing public symbols: {missing}"

    def test_all_symbols_are_not_none(self):
        import phylax
        for sym in self.EXPECTED_SYMBOLS:
            obj = getattr(phylax, sym, None)
            assert obj is not None, f"Symbol {sym} is None"


class TestFreshImport:
    """PT16.3: Fresh import must succeed without side effects."""

    def test_reimport_works(self):
        """Re-importing phylax must not crash."""
        importlib.reload(importlib.import_module("phylax"))

    def test_import_does_not_print(self, capsys):
        """Importing phylax should not print anything to stdout."""
        importlib.reload(importlib.import_module("phylax"))
        captured = capsys.readouterr()
        assert captured.out == "", f"Import printed: {captured.out[:100]}"


class TestDependencies:
    """PT16.4: Required dependencies must be installed."""

    def test_pydantic_available(self):
        import pydantic
        assert pydantic is not None

    def test_pyyaml_available(self):
        import yaml
        assert yaml is not None
