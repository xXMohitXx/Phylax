import React from 'react';
import { CodeBlock } from '@/components/code-block';

export default function SurfacesPage() {
  return (
    <div className="flex flex-col gap-6 w-full">
      <h1 className="text-4xl font-extrabold tracking-tight lg:text-5xl mb-2 text-coffee-bean">Surfaces</h1>
      <p className="text-xl text-coffee-bean/80">
        The Surface Abstraction Layer lets you enforce contracts on <em>any</em> LLM output type — not just raw text. Parse and validate structured JSON, tool calls, execution traces, and cross-run stability.
      </p>
      <hr className="my-6 border-black/10" />

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Surface Types</h2>
      <div className="overflow-x-auto">
        <table className="w-full text-sm border-collapse">
          <thead><tr className="border-b border-black/10">
            <th className="text-left py-3 pr-4 font-semibold text-coffee-bean">Surface Type</th>
            <th className="text-left py-3 pr-4 font-semibold text-coffee-bean">Rules</th>
            <th className="text-left py-3 font-semibold text-coffee-bean">Use Case</th>
          </tr></thead>
          <tbody className="text-coffee-bean/80">
            <tr className="border-b border-black/5"><td className="py-3 pr-4 font-medium">Structured Output</td><td className="py-3 pr-4">FieldExists, TypeEnforcement, ExactValue, Enum, ArrayBounds</td><td className="py-3">JSON API responses</td></tr>
            <tr className="border-b border-black/5"><td className="py-3 pr-4 font-medium">Tool Calls</td><td className="py-3 pr-4">ToolPresence, ToolCount, ToolArgument, ToolOrdering</td><td className="py-3">Agent tool usage</td></tr>
            <tr className="border-b border-black/5"><td className="py-3 pr-4 font-medium">Execution Traces</td><td className="py-3 pr-4">StepCount, ForbiddenTransition, RequiredStage</td><td className="py-3">Multi-step workflows</td></tr>
            <tr><td className="py-3 pr-4 font-medium">Cross-Run Stability</td><td className="py-3 pr-4">ExactStability, AllowedDrift</td><td className="py-3">Regression detection</td></tr>
          </tbody>
        </table>
      </div>

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Structured Output Enforcement</h2>
      <p className="text-coffee-bean/80 mb-4">Validate JSON API responses with strict schema rules:</p>
      <CodeBlock language="python" title="structured_output.py" code={`from phylax import (
    Surface, SurfaceEvaluator,
    FieldExistsRule,        # JSON field must exist
    FieldNotExistsRule,     # JSON field must NOT exist
    TypeEnforcementRule,    # Strict type checking
    ExactValueRule,         # Field must have exact value
    EnumEnforcementRule,    # Field must be one of allowed values
    ArrayBoundsRule,        # Array length constraints
)

evaluator = SurfaceEvaluator()

# Ensure a JSON response has required fields
evaluator.add_rule(FieldExistsRule("data.user.email"))
evaluator.add_rule(TypeEnforcementRule("data.user.age", int))
evaluator.add_rule(EnumEnforcementRule("data.status", ["active", "pending"]))
evaluator.add_rule(ArrayBoundsRule("data.items", min_length=1, max_length=50))

verdict = evaluator.evaluate(llm_output)`} />

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Tool Call Enforcement</h2>
      <p className="text-coffee-bean/80 mb-4">Validate that agents call the right tools in the right order:</p>
      <CodeBlock language="python" title="tool_enforcement.py" code={`from phylax import (
    ToolPresenceRule,    # Tool must be called
    ToolCountRule,       # Tool called N times
    ToolArgumentRule,    # Tool argument validation
    ToolOrderingRule,    # Tools called in correct order
)

evaluator = SurfaceEvaluator()
evaluator.add_rule(ToolPresenceRule("fetch_database"))
evaluator.add_rule(ToolCountRule("search_api", exact=1))
evaluator.add_rule(ToolArgumentRule("fetch_database", "query", required=True))
evaluator.add_rule(ToolOrderingRule(["search_api", "fetch_database", "format_response"]))`} />

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Execution Trace Enforcement</h2>
      <CodeBlock language="python" title="execution_enforcement.py" code={`from phylax import (
    StepCountRule,            # Execution must have N steps
    ForbiddenTransitionRule,  # Certain step sequences are forbidden
    RequiredStageRule,        # Execution must include these stages
)

evaluator = SurfaceEvaluator()
evaluator.add_rule(StepCountRule(min_steps=3, max_steps=10))
evaluator.add_rule(ForbiddenTransitionRule("classify", "output"))  # Must not skip research
evaluator.add_rule(RequiredStageRule(["validation", "safety_check"]))`} />

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Cross-Run Stability</h2>
      <p className="text-coffee-bean/80 mb-4">Detect when outputs change between runs (regression detection):</p>
      <CodeBlock language="python" title="stability.py" code={`from phylax import (
    ExactStabilityRule,  # Output must not change between runs
    AllowedDriftRule,    # Output may change within bounds
)

evaluator = SurfaceEvaluator()
evaluator.add_rule(ExactStabilityRule())        # Must match exactly
evaluator.add_rule(AllowedDriftRule(max_delta=0.05))  # Up to 5% drift`} />

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Public API Imports</h2>
      <CodeBlock language="python" title="imports.py" code={`from phylax import (
    # Core
    Surface, SurfaceType, SurfaceEvaluator, SurfaceRegistry,
    SurfaceRule, SurfaceRuleResult, SurfaceVerdict,
    SurfaceAdapter, TextSurfaceAdapter,
    
    # Structured Output
    FieldExistsRule, FieldNotExistsRule, TypeEnforcementRule,
    ExactValueRule, EnumEnforcementRule, ArrayBoundsRule,
    StructuredSurfaceAdapter,
    
    # Tool Calls
    ToolPresenceRule, ToolCountRule, ToolArgumentRule,
    ToolOrderingRule, ToolSurfaceAdapter,
    
    # Execution Traces
    StepCountRule, ForbiddenTransitionRule, RequiredStageRule,
    ExecutionTraceSurfaceAdapter,
    
    # Cross-Run Stability
    ExactStabilityRule, AllowedDriftRule, StabilitySurfaceAdapter,
)`} />
    </div>
  );
}
