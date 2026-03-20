import React from 'react';
import { CodeBlock } from '@/components/code-block';

const CODE_BLOCK_0 = `
from phylax import (
    SurfaceEvaluator,
    ToolPresenceRule,
    ToolCountRule,
    ToolOrderingRule,
    ToolSurfaceAdapter
)

evaluator = SurfaceEvaluator()

# The agent MUST look up information before responding
evaluator.add_rule(ToolOrderingRule("search_db", "send_email", "before"))

# The agent should never retry search more than 3 times
evaluator.add_rule(ToolCountRule("search_db", "<=", 3))

# The agent is forbidden from deleting records
evaluator.add_rule(ToolPresenceRule("delete_record", must_exist=False))

adapter = ToolSurfaceAdapter()
surface = adapter.adapt([
    {"name": "search_db", "args": {"query": "test"}},
    {"name": "send_email", "args": {"body": "hello"}}
])

verdict = evaluator.evaluate(surface)
print(verdict.passed) # True
`;

export default function ToolCallingPage() {
  return (
    <div className="flex flex-col gap-6 w-full">
      <h1 className="text-4xl font-extrabold tracking-tight lg:text-5xl mb-2 text-coffee-bean">Tool Calling</h1>
      <p className="text-xl text-coffee-bean/80">
        Enforce which tools an agent calls, how often they call them, and with what exact arguments.
      </p>

      <hr className="my-6 border-black/10" />

      <h2 className="text-2xl font-semibold text-coffee-bean mt-4 mb-4">Tool Call Rules</h2>
      <p className="text-coffee-bean/80 mb-4">
        Validating agent tool selection is critical to ensuring your system won't execute dangerous functions or waste cycles on hallucinated tools.
      </p>

      <div className="bg-beige/40 border border-coffee-bean/10 rounded-lg p-6 mb-6">
        <ul className="space-y-4 text-coffee-bean/80">
          <li><strong><code>ToolPresenceRule(tool_name, must_exist=True)</code></strong>: Asserts whether a specific tool was used in the payload stream.</li>
          <li><strong><code>ToolCountRule(tool_name, operator, count)</code></strong>: Controls tool usage limits (e.g. <code>"==", 2</code> or <code>"&lt;=", 3</code>).</li>
          <li><strong><code>ToolArgumentRule(tool_name, arg_path, expected_value, occurrence=1)</code></strong>: Strictly checks the exact value of an argument passed to a tool.</li>
          <li><strong><code>ToolOrderingRule(tool_a, tool_b, mode)</code></strong>: Asserts tool execution sequence (e.g., <code>"search" "before" "write"</code>).</li>
        </ul>
      </div>

      <CodeBlock language="python" title="agent_tool_enforcement.py" code={CODE_BLOCK_0} />

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Argument Inspection</h2>
      <p className="text-coffee-bean/80 mb-4">
        <code>ToolArgumentRule</code> allows you to inspect deep into tool JSON schemas. For example, ensuring that an agent executing an SQL query tool always includes a <code>LIMIT 10</code> constraint.
      </p>

    </div>
  );
}
