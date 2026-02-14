"""
Phylax - Deterministic regression enforcement for LLM systems.

Public API:
    trace       - Decorator to trace LLM calls
    expect      - Decorator to add expectations
    execution   - Context manager for grouping traces
    Trace       - Trace data model
    Verdict     - Verdict model (PASS, FAIL)
    
Adapters:
    OpenAIAdapter       - OpenAI integration
    GeminiAdapter       - Google Gemini integration
    GroqAdapter         - Groq LPU integration
    MistralAdapter      - Mistral AI integration
    HuggingFaceAdapter  - HuggingFace Inference API
    OllamaAdapter       - Ollama local models
"""

from phylax._internal.schema import (
    Trace,
    TraceRequest,
    TraceResponse,
    TraceRuntime,
    Verdict,
)
from phylax._internal.decorator import trace, expect
from phylax._internal.context import execution
from phylax._internal.graph import ExecutionGraph, NodeRole, GraphStage, GraphDiff, NodeDiff

# Adapters - lazy import to avoid requiring all dependencies
from phylax._internal.adapters import (
    OpenAIAdapter,
    GeminiAdapter,
    GroqAdapter,
    MistralAdapter,
    HuggingFaceAdapter,
    OllamaAdapter,
)

__version__ = "1.2.6"
__all__ = [
    # Core decorators
    "trace",
    "expect",
    # Context manager
    "execution",
    # Data models
    "Trace",
    "TraceRequest",
    "TraceResponse",
    "TraceRuntime",
    "Verdict",
    # Graph (advanced)
    "ExecutionGraph",
    "NodeRole",
    "GraphStage",
    "GraphDiff",
    "NodeDiff",
    # Adapters
    "OpenAIAdapter",
    "GeminiAdapter",
    "GroqAdapter",
    "MistralAdapter",
    "HuggingFaceAdapter",
    "OllamaAdapter",
    # Version
    "__version__",
]
