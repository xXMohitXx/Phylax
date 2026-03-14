"""
Phase-test 14 — Server & Infrastructure Stability

Goal: Verify internal modules import without errors, key internal
infrastructure is accessible, and graph/artifact modules work.
"""
import pytest


class TestInternalModuleImports:
    """PT14.1: Core internal modules must import without errors."""

    def test_context_module(self):
        from phylax._internal import context
        assert context is not None

    def test_capture_module(self):
        from phylax._internal import capture
        assert capture is not None

    def test_graph_module(self):
        from phylax._internal import graph
        assert graph is not None

    def test_errors_module(self):
        from phylax._internal import errors
        assert errors is not None

    def test_evidence_module(self):
        from phylax._internal import evidence
        assert evidence is not None

    def test_decorator_module(self):
        from phylax._internal import decorator
        assert decorator is not None

    def test_schema_module(self):
        from phylax._internal import schema
        assert schema is not None


class TestSubpackageImports:
    """PT14.2: Sub-packages must import cleanly."""

    def test_adapters_package(self):
        from phylax._internal import adapters
        assert adapters is not None

    def test_artifacts_package(self):
        from phylax._internal import artifacts
        assert artifacts is not None

    def test_datasets_package(self):
        from phylax._internal import datasets
        assert datasets is not None

    def test_guardrails_package(self):
        from phylax._internal import guardrails
        assert guardrails is not None

    def test_expectations_package(self):
        from phylax._internal import expectations
        assert expectations is not None


class TestGraphInfrastructure:
    """PT14.3: Graph infrastructure smoke test."""

    def test_execution_graph_creates(self):
        from phylax import ExecutionGraph
        g = ExecutionGraph(execution_id="test-exec")
        assert g.execution_id == "test-exec"
        assert g.node_count == 0

    def test_node_role_enum(self):
        from phylax import NodeRole
        assert NodeRole.LLM is not None
        assert NodeRole.INPUT is not None
        assert NodeRole.OUTPUT is not None
