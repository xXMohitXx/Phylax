import React from 'react';
import { CodeBlock } from '@/components/code-block';

const CODE_BLOCK_0 = `
phylax/_internal/surfaces/
├── __init__.py                # Public exports
├── base.py                    # Surface, SurfaceRule, SurfaceEvaluator
├── registry.py                # SurfaceRegistry
├── structured.py              # Phase 2.1: JSON enforcement
├── tools.py                   # Phase 2.2: Tool call invariants
├── execution_trace.py         # Phase 2.3: Execution trace rules
└── stability.py               # Phase 2.4: Cross-run stability
`;
const CODE_BLOCK_1 = `
FieldExistsRule("data.user.email")          # Field must exist
FieldNotExistsRule("data.internal_id")      # Field must NOT exist
TypeEnforcementRule("data.age", int)         # Type must match
ExactValueRule("data.status", "active")      # Exact value match
EnumEnforcementRule("data.role", ["admin", "user"])  # Enum values
ArrayBoundsRule("data.items", min_length=1, max_length=50)
`;
const CODE_BLOCK_2 = `
ToolPresenceRule("fetch_database")           # Tool must be called
ToolCountRule("search_api", exact=1)         # Called exactly once
ToolArgumentRule("fetch_db", "query", required=True)  # Arg validation
ToolOrderingRule(["search", "fetch", "format"])  # Call order
`;
const CODE_BLOCK_3 = `
StepCountRule(min_steps=3, max_steps=10)     # Step count bounds
ForbiddenTransitionRule("classify", "output") # Forbidden transitions
RequiredStageRule(["validation", "safety"])    # Required stages
`;
const CODE_BLOCK_4 = `
ExactStabilityRule()           # Output must be identical across runs
AllowedDriftRule(max_delta=0.05)  # Up to 5% drift allowed
`;

export default function Axis2Page() {
  return (
    <div className="flex flex-col gap-6 w-full">
      <h1 className="text-4xl font-extrabold tracking-tight lg:text-5xl mb-2 text-coffee-bean">Axis 2 — Surface Abstraction Layer</h1>
      <p className="text-xl text-coffee-bean/80">Enforce contracts on any LLM output type — structured JSON, tool calls, execution traces, and cross-run stability.</p>
      <hr className="my-6 border-black/10" />

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Architecture Overview</h2>
      <CodeBlock language="bash" title="Directory Structure" code={CODE_BLOCK_0} />

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Phase 2.1: Structured Output</h2>
      <p className="text-coffee-bean/80 mb-4">6 rules for JSON response validation:</p>
      <CodeBlock language="python" title="Structured Rules" code={CODE_BLOCK_1} />

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Phase 2.2: Tool Call Invariants</h2>
      <p className="text-coffee-bean/80 mb-4">4 rules for agent tool usage validation:</p>
      <CodeBlock language="python" title="Tool Rules" code={CODE_BLOCK_2} />

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Phase 2.3: Execution Trace</h2>
      <CodeBlock language="python" title="Execution Rules" code={CODE_BLOCK_3} />

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Phase 2.4: Cross-Run Stability</h2>
      <CodeBlock language="python" title="Stability Rules" code={CODE_BLOCK_4} />
    </div>
  );
}
