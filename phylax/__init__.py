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
    TraceMessage,
    TraceParameters,
    Verdict,
)
from phylax._internal.decorator import trace, expect
from phylax._internal.context import (
    execution,
    get_execution_id,
    get_parent_node_id,
    push_node,
    pop_node,
    in_execution_context,
)
from phylax._internal.graph import ExecutionGraph, NodeRole, GraphStage, GraphDiff, NodeDiff

# Expectations engine
from phylax._internal.expectations import (
    evaluate,
    Evaluator,
    Rule,
    RuleResult,
    MustIncludeRule,
    MustNotIncludeRule,
    MaxLatencyRule,
    MinTokensRule,
    # Axis 1 Phase 1: Composition
    ExpectationGroup,
    AndGroup,
    OrGroup,
    NotGroup,
    # Axis 1 Phase 2: Conditionals
    Condition,
    ConditionalExpectation,
    InputContains,
    ModelEquals,
    ProviderEquals,
    MetadataEquals,
    FlagSet,
    when,
    # Axis 1 Phase 3: Scoping
    ExpectationScope,
    ScopedExpectation,
    for_node,
    for_provider,
    for_stage,
    for_tool,
    scoped,
    # Axis 1 Phase 4: Templates
    ExpectationTemplate,
    TemplateRegistry,
    register_template,
    get_template,
    get_template_rules,
)
from phylax._internal.expectations.templates import get_registry as get_template_registry
from phylax._internal.expectations.documentation import (
    describe_rule,
    describe_condition,
    describe_template,
    list_contracts,
    export_contract_markdown,
    ContractDocumenter,
)

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
    HealthReport,
    CoverageReport,
    get_windowed_health,
)

# Axis 3: Modes (Phase 3.3)
from phylax._internal.modes.handler import ModeHandler, ModeResult
from phylax._internal.modes.definitions import EnforcementMode, VALID_MODES

# Axis 3: Meta-Enforcement Rules (Phase 3.4)
from phylax._internal.meta.rules import (
    MetaRuleResult,
    MinExpectationCountRule,
    ZeroSignalRule,
    DefinitionChangeGuard,
    ExpectationRemovalGuard,
)

# Axis 4: Artifact Contracts (Phase 4.1)
from phylax._internal.artifacts.verdict import VerdictArtifact, generate_verdict_artifact
from phylax._internal.artifacts.failures import FailureEntry, FailureArtifact, generate_failure_artifact
from phylax._internal.artifacts.trace_diff import TraceDiffArtifact, generate_trace_diff
from phylax._internal.artifacts.exit_codes import (
    EXIT_PASS, EXIT_FAIL, EXIT_SYSTEM_ERROR, resolve_exit_code,
)

# Dataset Contracts
from phylax._internal.datasets import (
    Dataset,
    DatasetCase,
    DatasetResult,
    CaseResult,
    load_dataset,
    run_dataset,
    format_report,
    format_json_report,
    # Behavioral Diff Engine
    CaseDiff,
    DatasetDiff,
    diff_runs,
    format_diff_report,
    format_diff_json,
)

__version__ = "1.5.0"
__all__ = [
    # Core decorators
    "trace",
    "expect",
    # Context manager
    "execution",
    "get_execution_id",
    "get_parent_node_id",
    "push_node",
    "pop_node",
    "in_execution_context",
    # Data models
    "Trace",
    "TraceRequest",
    "TraceResponse",
    "TraceRuntime",
    "TraceMessage",
    "TraceParameters",
    "Verdict",
    # Graph (advanced)
    "ExecutionGraph",
    "NodeRole",
    "GraphStage",
    "GraphDiff",
    "NodeDiff",
    # Expectations engine
    "evaluate",
    "Evaluator",
    "Rule",
    "RuleResult",
    "MustIncludeRule",
    "MustNotIncludeRule",
    "MaxLatencyRule",
    "MinTokensRule",
    # Axis 1 Phase 1: Composition
    "ExpectationGroup",
    "AndGroup",
    "OrGroup",
    "NotGroup",
    # Axis 1 Phase 2: Conditionals
    "Condition",
    "ConditionalExpectation",
    "InputContains",
    "ModelEquals",
    "ProviderEquals",
    "MetadataEquals",
    "FlagSet",
    "when",
    # Axis 1 Phase 3: Scoping
    "ExpectationScope",
    "ScopedExpectation",
    "for_node",
    "for_provider",
    "for_stage",
    "for_tool",
    "scoped",
    # Axis 1 Phase 4: Templates
    "ExpectationTemplate",
    "TemplateRegistry",
    "get_template_registry",
    "register_template",
    "get_template",
    "get_template_rules",
    # Axis 1 Phase 5: Documentation
    "describe_rule",
    "describe_condition",
    "describe_template",
    "list_contracts",
    "export_contract_markdown",
    "ContractDocumenter",
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
    "HealthReport",
    "CoverageReport",
    "get_windowed_health",
    # Axis 3: Modes (Phase 3.3)
    "ModeHandler",
    "ModeResult",
    "EnforcementMode",
    "VALID_MODES",
    # Axis 3: Meta-Enforcement Rules (Phase 3.4)
    "MetaRuleResult",
    "MinExpectationCountRule",
    "ZeroSignalRule",
    "DefinitionChangeGuard",
    "ExpectationRemovalGuard",
    # Axis 4: Artifact Contracts (Phase 4.1)
    "VerdictArtifact",
    "generate_verdict_artifact",
    "FailureEntry",
    "FailureArtifact",
    "generate_failure_artifact",
    "TraceDiffArtifact",
    "generate_trace_diff",
    "EXIT_PASS",
    "EXIT_FAIL",
    "EXIT_SYSTEM_ERROR",
    "resolve_exit_code",
    # Dataset Contracts
    "Dataset",
    "DatasetCase",
    "DatasetResult",
    "CaseResult",
    "load_dataset",
    "run_dataset",
    "format_report",
    "format_json_report",
    # Behavioral Diff Engine
    "CaseDiff",
    "DatasetDiff",
    "diff_runs",
    "format_diff_report",
    "format_diff_json",
    # Version
    "__version__",
]
