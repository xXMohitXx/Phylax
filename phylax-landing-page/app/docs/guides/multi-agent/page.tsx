import React from 'react';
import { CodeBlock } from '@/components/code-block';

const MULTI_AGENT_CODE = `from phylax import trace, expect, execution

@trace(provider="openai")
@expect(must_include=["intent"])
def classify_intent(message: str) -> str:
    """Root agent — identifies user intent."""
    return llm_call(f"Classify the intent of: {message}")

@trace(provider="openai")
@expect(must_include=["refund"], must_not_include=["lawsuit"])
def handle_refund(intent: str) -> str:
    """Child agent — handles refund intents."""
    return llm_call(f"Handle refund request: {intent}")

@trace(provider="openai")
@expect(must_include=["ticket"])
def escalate_issue(intent: str) -> str:
    """Child agent — escalates unresolved issues."""
    return llm_call(f"Escalate: {intent}")

# All three agents share the same execution context
with execution() as exec_id:
    intent = classify_intent("Where is my refund?")

    if "refund" in intent:
        response = handle_refund(intent)
    else:
        response = escalate_issue(intent)`;

const SCOPE_CODE = `from phylax.expectations import scoped, for_node, MinTokensRule

# Only fire this rule for the escalation agent
scoped(for_node("escalate_issue"), MinTokensRule(50))`;

export default function MultiAgentPage() {
    return (
        <div className="flex flex-col gap-6 w-full">
            <h1 className="text-4xl font-extrabold tracking-tight lg:text-5xl mb-2 text-coffee-bean">Multi-Agent Verification</h1>
            <p className="text-xl text-coffee-bean/80">
                Test entire agent pipelines — not just individual LLM calls — with shared execution contexts and node-scoped rules.
            </p>

            <hr className="my-6 border-black/10" />

            <h2 className="text-2xl font-semibold text-coffee-bean mt-4 mb-4">Shared Execution Context</h2>
            <p className="text-coffee-bean/80 mb-4">
                Use the <code>execution()</code> context manager to group all agents in a pipeline under one shared <code>exec_id</code>. Phylax tracks parent-child relationships automatically through the call stack.
            </p>

            <CodeBlock language="python" title="multi_agent.py" code={MULTI_AGENT_CODE} />

            <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Node-Scoped Rules</h2>
            <p className="text-coffee-bean/80 mb-4">
                Use <code>for_node()</code> to apply rules only to a specific agent by its function name. This prevents rules meant for one agent from incorrectly failing another.
            </p>

            <CodeBlock language="python" title="node_scoping.py" code={SCOPE_CODE} />

            <div className="bg-beige/40 border border-coffee-bean/10 rounded-lg p-6 mt-6">
                <h3 className="text-lg font-semibold text-coffee-bean mb-2">Graph Hierarchy</h3>
                <ul className="space-y-2 text-coffee-bean/80">
                    <li><strong>ROOT</strong> — The first traced function in the context (<code>classify_intent</code> above).</li>
                    <li><strong>CHILD</strong> — Functions called inside the context that are also traced.</li>
                    <li><strong>First Failing Node</strong> — Phylax isolates which agent caused the failure, not just the final output.</li>
                </ul>
            </div>
        </div>
    );
}
