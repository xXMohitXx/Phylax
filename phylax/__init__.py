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

# Axis 2: Surface Abstraction Layer
from phylax._internal.surfaces import (
    Surface,
    SurfaceType,
    SurfaceRuleResult,
    SurfaceVerdict,
    SurfaceRule,
    SurfaceAdapter,
    SurfaceEvaluator,
    SurfaceRegistry,
    get_registry,
    TextSurfaceAdapter,
    # Axis 2 Phase 2.1: Structured Output Enforcement
    FieldExistsRule,
    FieldNotExistsRule,
    TypeEnforcementRule,
    ExactValueRule,
    EnumEnforcementRule,
    ArrayBoundsRule,
    StructuredSurfaceAdapter,
    # Axis 2 Phase 2.2: Tool & Function Call Invariants
    ToolPresenceRule,
    ToolCountRule,
    ToolArgumentRule,
    ToolOrderingRule,
    ToolSurfaceAdapter,
    # Axis 2 Phase 2.3: Execution Trace Enforcement
    StepCountRule,
    ForbiddenTransitionRule,
    RequiredStageRule,
    ExecutionTraceSurfaceAdapter,
    # Axis 2 Phase 2.4: Cross-Run Stability Enforcement
    ExactStabilityRule,
    AllowedDriftRule,
    StabilitySurfaceAdapter,
)

# Axis 3: Metrics Foundation Layer
from phylax._internal.metrics import (
    ExpectationIdentity,
    compute_definition_hash,
    LedgerEntry,
    EvaluationLedger,
    AggregateMetrics,
    aggregate,
    aggregate_all,
)

__version__ = "1.3.4"
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
    # Axis 2: Surface Abstraction Layer
    "Surface",
    "SurfaceType",
    "SurfaceRuleResult",
    "SurfaceVerdict",
    "SurfaceRule",
    "SurfaceAdapter",
    "SurfaceEvaluator",
    "SurfaceRegistry",
    "get_registry",
    "TextSurfaceAdapter",
    # Axis 2 Phase 2.1: Structured Output Enforcement
    "FieldExistsRule",
    "FieldNotExistsRule",
    "TypeEnforcementRule",
    "ExactValueRule",
    "EnumEnforcementRule",
    "ArrayBoundsRule",
    "StructuredSurfaceAdapter",
    # Axis 2 Phase 2.2: Tool & Function Call Invariants
    "ToolPresenceRule",
    "ToolCountRule",
    "ToolArgumentRule",
    "ToolOrderingRule",
    "ToolSurfaceAdapter",
    # Axis 2 Phase 2.3: Execution Trace Enforcement
    "StepCountRule",
    "ForbiddenTransitionRule",
    "RequiredStageRule",
    "ExecutionTraceSurfaceAdapter",
    # Axis 2 Phase 2.4: Cross-Run Stability Enforcement
    "ExactStabilityRule",
    "AllowedDriftRule",
    "StabilitySurfaceAdapter",
    # Axis 3: Metrics Foundation Layer
    "ExpectationIdentity",
    "compute_definition_hash",
    "LedgerEntry",
    "EvaluationLedger",
    "AggregateMetrics",
    "aggregate",
    "aggregate_all",
    # Version
    "__version__",
]
