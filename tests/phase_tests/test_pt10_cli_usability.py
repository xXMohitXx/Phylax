"""
Phase-test 10 — API Usability & Interface Verification

Goal: Verify the public API is clean, imports work correctly,
version is accurate, and core interfaces are stable.

Note: Phylax does not have a CLI entry point (no console_scripts).
This test validates the programmatic API usability instead.
"""
import pytest
import phylax


class TestPublicImports:
    """PT10.1: All documented public API symbols must import cleanly."""

    def test_core_symbols_importable(self):
        """Core dataset symbols must import from top-level."""
        from phylax import Dataset, DatasetCase, run_dataset
        assert Dataset is not None
        assert DatasetCase is not None
        assert run_dataset is not None

    def test_diff_symbols_importable(self):
        from phylax import diff_runs, format_diff_report, format_diff_json
        assert diff_runs is not None
        assert format_diff_report is not None

    def test_simulator_symbols_importable(self):
        from phylax import simulate_upgrade, format_simulation_report
        assert simulate_upgrade is not None

    def test_artifact_symbols_importable(self):
        from phylax import (
            generate_verdict_artifact,
            generate_failure_artifact,
            generate_trace_diff,
        )
        assert generate_verdict_artifact is not None

    def test_guardrail_symbols_importable(self):
        from phylax import (
            safety_pack, quality_pack, compliance_pack,
            list_packs, get_pack, apply_pack,
        )
        assert safety_pack is not None
        assert list_packs is not None

    def test_graph_symbols_importable(self):
        from phylax import ExecutionGraph, NodeRole
        assert ExecutionGraph is not None
        assert NodeRole is not None

    def test_report_symbols_importable(self):
        from phylax import format_report, format_json_report
        assert format_report is not None
        assert format_json_report is not None


class TestVersion:
    """PT10.2: Version must be correct and well-formatted."""

    def test_version_exists(self):
        assert hasattr(phylax, "__version__")

    def test_version_current(self):
        assert phylax.__version__ == "1.6.5"

    def test_version_is_semver(self):
        parts = phylax.__version__.split(".")
        assert len(parts) == 3
        assert all(p.isdigit() for p in parts)


class TestModuleStructure:
    """PT10.3: Package structure must be coherent."""

    def test_no_private_leakage(self):
        """Public attributes should not include internal helpers."""
        public = [x for x in dir(phylax) if not x.startswith("_")]
        # Should have meaningful names, not internal implementation details
        for name in public:
            assert len(name) > 1, f"Suspicious short public name: {name}"

    def test_all_public_callables_have_docstrings(self):
        """All public functions should have docstrings."""
        import types
        public = [x for x in dir(phylax) if not x.startswith("_")]
        for name in public:
            obj = getattr(phylax, name)
            # Only check actual functions, not classes/types/enums
            if isinstance(obj, types.FunctionType):
                assert obj.__doc__ is not None, f"{name} missing docstring"


class TestDatasetCreation:
    """PT10.4: Dataset creation interface must be intuitive."""

    def test_minimal_dataset(self):
        """Minimal dataset should work with just input and expectations."""
        ds = phylax.Dataset(
            dataset="test",
            cases=[
                phylax.DatasetCase(
                    input="hello",
                    expectations={"must_include": ["hello"]},
                ),
            ],
        )
        assert len(ds.cases) == 1

    def test_dataset_with_name(self):
        ds = phylax.Dataset(
            dataset="named_test",
            cases=[
                phylax.DatasetCase(
                    input="hello",
                    name="greeting",
                    expectations={"must_include": ["hello"]},
                ),
            ],
        )
        assert ds.cases[0].name == "greeting"

    def test_run_returns_result(self):
        ds = phylax.Dataset(
            dataset="result_test",
            cases=[
                phylax.DatasetCase(
                    input="hello",
                    expectations={"must_include": ["hello"]},
                ),
            ],
        )
        result = phylax.run_dataset(ds, lambda x: f"hello from {x}")
        assert hasattr(result, "all_passed")
        assert hasattr(result, "total_cases")
        assert hasattr(result, "passed_cases")
        assert hasattr(result, "failed_cases")
