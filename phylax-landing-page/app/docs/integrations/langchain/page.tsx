import React from 'react';
import { CodeBlock } from '@/components/code-block';

export default function LangChainPage() {
  return (
    <div className="flex flex-col gap-6 w-full">
      <h1 className="text-4xl font-extrabold tracking-tight lg:text-5xl mb-2 text-coffee-bean">LangChain Integration</h1>
      <p className="text-xl text-coffee-bean/80">Use Phylax with LangChain and LangGraph to enforce behavioral contracts on chain outputs and agent workflows.</p>
      <hr className="my-6 border-black/10" />

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">How It Works</h2>
      <p className="text-coffee-bean/80 mb-4">
        Phylax wraps your LangChain calls with the <code className="px-1.5 py-0.5 rounded-md bg-beige text-coffee-bean text-sm">@trace</code> decorator. Any LangChain chain, agent, or LangGraph node can be traced and enforced — Phylax is framework-agnostic.
      </p>

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Basic Chain</h2>
      <CodeBlock language="python" title="langchain_basic.py" code={`from phylax import trace, expect
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

llm = ChatOpenAI(model="gpt-4")
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a customer support agent."),
    ("user", "{message}")
])
chain = prompt | llm

@trace(provider="openai")
@expect(must_include=["refund"], must_not_include=["lawsuit"])
def support(message: str) -> str:
    response = chain.invoke({"message": message})
    return response.content`} />

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Multi-Agent Workflow (LangGraph)</h2>
      <CodeBlock language="python" title="langgraph_agents.py" code={`from phylax import trace, expect, execution

@trace(provider="openai")
@expect(must_include=["intent"])
def classifier_node(state):
    # LangGraph node: classify user intent
    return classify(state["message"])

@trace(provider="openai")
@expect(must_include=["response"])
def responder_node(state):
    # LangGraph node: generate response
    return respond(state["intent"])

# Track as an execution graph
with execution() as exec_id:
    intent = classifier_node({"message": "I need a refund"})
    response = responder_node({"intent": intent})
    # Phylax builds a DAG:
    # [classifier] → [responder]`} />

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Best Practices</h2>
      <ul className="space-y-3 text-coffee-bean/80 list-disc pl-6 marker:text-lime-cream">
        <li>Wrap each LangGraph <strong>node</strong> individually with <code className="px-1 py-0.5 rounded bg-beige text-xs">@trace</code> for granular failure localization</li>
        <li>Use <code className="px-1 py-0.5 rounded bg-beige text-xs">execution()</code> context to group all nodes into a single DAG</li>
        <li>Add <code className="px-1 py-0.5 rounded bg-beige text-xs">@expect</code> to each node — Phylax identifies the first failing node in the chain</li>
        <li>Use Surface Enforcement for nodes that output structured data or tool calls</li>
      </ul>
    </div>
  );
}
