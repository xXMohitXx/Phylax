"""
Phase-test 4 — Multi-Provider Compatibility

Goal: Verify adapter classes for all supported providers load correctly
and the adapter layer has proper structure.
"""
import pytest


class TestAdapterImports:
    """PT4.1: All adapter classes must be importable."""

    def test_openai_adapter(self):
        from phylax._internal.adapters import OpenAIAdapter
        assert OpenAIAdapter is not None

    def test_ollama_adapter(self):
        import phylax._internal.adapters as adapters
        assert hasattr(adapters, 'ollama') or 'ollama' in str(dir(adapters))

    def test_gemini_adapter(self):
        from phylax._internal.adapters import GeminiAdapter
        assert GeminiAdapter is not None

    def test_groq_adapter(self):
        from phylax._internal.adapters import GroqAdapter
        assert GroqAdapter is not None


class TestAdapterPackage:
    """PT4.2: Adapter package must have proper structure."""

    def test_adapters_package_importable(self):
        import phylax._internal.adapters
        assert phylax._internal.adapters is not None

    def test_multiple_adapters_available(self):
        import phylax._internal.adapters as adapters
        public = [x for x in dir(adapters) if not x.startswith("_")]
        adapter_classes = [x for x in public if "Adapter" in x]
        assert len(adapter_classes) >= 4, f"Only {len(adapter_classes)} adapters found"


class TestTracingInfra:
    """PT4.3: Tracing infrastructure must work."""

    def test_context_module(self):
        from phylax._internal import context
        assert context is not None

    def test_capture_module(self):
        from phylax._internal import capture
        assert capture is not None

    def test_schema_module(self):
        from phylax._internal import schema
        assert schema is not None

    def test_graph_module(self):
        from phylax._internal import graph
        assert graph is not None
