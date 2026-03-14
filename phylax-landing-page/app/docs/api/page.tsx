import React from 'react';

export default function ApiReferencePage() {
  return (
    <div className="flex flex-col gap-6 w-full">
      <h1 className="text-4xl font-extrabold tracking-tight lg:text-5xl mb-2 text-coffee-bean">API Reference</h1>
      <p className="text-xl text-coffee-bean/80">
        The Phylax server provides a REST API for trace storage, execution graph management, golden baselines, and CI verdict enforcement. Base URL: <code className="px-1.5 py-0.5 rounded-md bg-beige text-coffee-bean text-sm">http://127.0.0.1:8000</code>
      </p>
      <hr className="my-6 border-black/10" />

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Traces</h2>
      <div className="overflow-x-auto">
        <table className="w-full text-sm border-collapse">
          <thead><tr className="border-b border-black/10">
            <th className="text-left py-3 pr-4 font-semibold text-coffee-bean">Method</th>
            <th className="text-left py-3 pr-4 font-semibold text-coffee-bean">Endpoint</th>
            <th className="text-left py-3 font-semibold text-coffee-bean">Description</th>
          </tr></thead>
          <tbody className="text-coffee-bean/80">
            <tr className="border-b border-black/5"><td className="py-3 pr-4 text-lime-cream font-mono text-xs">GET</td><td className="py-3 pr-4 font-mono text-xs">/v1/traces</td><td className="py-3">List all traces</td></tr>
            <tr className="border-b border-black/5"><td className="py-3 pr-4 text-lime-cream font-mono text-xs">GET</td><td className="py-3 pr-4 font-mono text-xs">/v1/traces/{'{id}'}</td><td className="py-3">Get a specific trace</td></tr>
            <tr className="border-b border-black/5"><td className="py-3 pr-4 text-lime-cream font-mono text-xs">POST</td><td className="py-3 pr-4 font-mono text-xs">/v1/traces</td><td className="py-3">Create a new trace</td></tr>
            <tr><td className="py-3 pr-4 text-fail-red font-mono text-xs">DELETE</td><td className="py-3 pr-4 font-mono text-xs">/v1/traces/{'{id}'}</td><td className="py-3">Delete a trace</td></tr>
          </tbody>
        </table>
      </div>

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Executions &amp; Graphs</h2>
      <div className="overflow-x-auto">
        <table className="w-full text-sm border-collapse">
          <thead><tr className="border-b border-black/10">
            <th className="text-left py-3 pr-4 font-semibold text-coffee-bean">Method</th>
            <th className="text-left py-3 pr-4 font-semibold text-coffee-bean">Endpoint</th>
            <th className="text-left py-3 font-semibold text-coffee-bean">Description</th>
          </tr></thead>
          <tbody className="text-coffee-bean/80">
            <tr className="border-b border-black/5"><td className="py-3 pr-4 text-lime-cream font-mono text-xs">GET</td><td className="py-3 pr-4 font-mono text-xs">/v1/executions</td><td className="py-3">List all executions</td></tr>
            <tr className="border-b border-black/5"><td className="py-3 pr-4 text-lime-cream font-mono text-xs">GET</td><td className="py-3 pr-4 font-mono text-xs">/v1/executions/{'{id}'}</td><td className="py-3">Get execution traces</td></tr>
            <tr className="border-b border-black/5"><td className="py-3 pr-4 text-lime-cream font-mono text-xs">GET</td><td className="py-3 pr-4 font-mono text-xs">/v1/executions/{'{id}'}/graph</td><td className="py-3">Get execution DAG</td></tr>
            <tr className="border-b border-black/5"><td className="py-3 pr-4 text-lime-cream font-mono text-xs">GET</td><td className="py-3 pr-4 font-mono text-xs">/v1/executions/{'{id}'}/analysis</td><td className="py-3">Performance analysis</td></tr>
            <tr className="border-b border-black/5"><td className="py-3 pr-4 text-lime-cream font-mono text-xs">GET</td><td className="py-3 pr-4 font-mono text-xs">/v1/executions/{'{a}'}/diff/{'{b}'}</td><td className="py-3">Compare two executions</td></tr>
            <tr className="border-b border-black/5"><td className="py-3 pr-4 text-lime-cream font-mono text-xs">GET</td><td className="py-3 pr-4 font-mono text-xs">/v1/executions/{'{id}'}/investigate</td><td className="py-3">Failure localization path</td></tr>
            <tr className="border-b border-black/5"><td className="py-3 pr-4 text-lime-cream font-mono text-xs">GET</td><td className="py-3 pr-4 font-mono text-xs">/v1/executions/{'{id}'}/snapshot</td><td className="py-3">Immutable snapshot</td></tr>
            <tr className="border-b border-black/5"><td className="py-3 pr-4 text-lime-cream font-mono text-xs">GET</td><td className="py-3 pr-4 font-mono text-xs">/v1/executions/{'{id}'}/export</td><td className="py-3">Export artifact</td></tr>
            <tr><td className="py-3 pr-4 text-lime-cream font-mono text-xs">GET</td><td className="py-3 pr-4 font-mono text-xs">/v1/executions/{'{id}'}/verify</td><td className="py-3">Verify integrity hash</td></tr>
          </tbody>
        </table>
      </div>

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Golden References</h2>
      <div className="overflow-x-auto">
        <table className="w-full text-sm border-collapse">
          <thead><tr className="border-b border-black/10">
            <th className="text-left py-3 pr-4 font-semibold text-coffee-bean">Method</th>
            <th className="text-left py-3 pr-4 font-semibold text-coffee-bean">Endpoint</th>
            <th className="text-left py-3 font-semibold text-coffee-bean">Description</th>
          </tr></thead>
          <tbody className="text-coffee-bean/80">
            <tr className="border-b border-black/5"><td className="py-3 pr-4 text-lime-cream font-mono text-xs">POST</td><td className="py-3 pr-4 font-mono text-xs">/v1/traces/{'{id}'}/bless</td><td className="py-3">Mark trace as golden</td></tr>
            <tr className="border-b border-black/5"><td className="py-3 pr-4 text-fail-red font-mono text-xs">DELETE</td><td className="py-3 pr-4 font-mono text-xs">/v1/traces/{'{id}'}/bless</td><td className="py-3">Remove golden status</td></tr>
            <tr><td className="py-3 pr-4 text-lime-cream font-mono text-xs">GET</td><td className="py-3 pr-4 font-mono text-xs">/v1/goldens</td><td className="py-3">List all golden traces</td></tr>
          </tbody>
        </table>
      </div>

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Replay</h2>
      <div className="overflow-x-auto">
        <table className="w-full text-sm border-collapse">
          <thead><tr className="border-b border-black/10">
            <th className="text-left py-3 pr-4 font-semibold text-coffee-bean">Method</th>
            <th className="text-left py-3 pr-4 font-semibold text-coffee-bean">Endpoint</th>
            <th className="text-left py-3 font-semibold text-coffee-bean">Description</th>
          </tr></thead>
          <tbody className="text-coffee-bean/80">
            <tr className="border-b border-black/5"><td className="py-3 pr-4 text-lime-cream font-mono text-xs">POST</td><td className="py-3 pr-4 font-mono text-xs">/v1/replay/{'{id}'}</td><td className="py-3">Re-run a trace</td></tr>
            <tr><td className="py-3 pr-4 text-lime-cream font-mono text-xs">GET</td><td className="py-3 pr-4 font-mono text-xs">/v1/replay/{'{id}'}/preview</td><td className="py-3">Preview replay</td></tr>
          </tbody>
        </table>
      </div>

      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Health &amp; Metrics</h2>
      <div className="overflow-x-auto">
        <table className="w-full text-sm border-collapse">
          <thead><tr className="border-b border-black/10">
            <th className="text-left py-3 pr-4 font-semibold text-coffee-bean">Method</th>
            <th className="text-left py-3 pr-4 font-semibold text-coffee-bean">Endpoint</th>
            <th className="text-left py-3 font-semibold text-coffee-bean">Description</th>
          </tr></thead>
          <tbody className="text-coffee-bean/80">
            <tr className="border-b border-black/5"><td className="py-3 pr-4 text-lime-cream font-mono text-xs">GET</td><td className="py-3 pr-4 font-mono text-xs">/health</td><td className="py-3">Server health check</td></tr>
            <tr className="border-b border-black/5"><td className="py-3 pr-4 text-lime-cream font-mono text-xs">GET</td><td className="py-3 pr-4 font-mono text-xs">/v1/health/{'{expectation_id}'}</td><td className="py-3">Expectation health report</td></tr>
            <tr className="border-b border-black/5"><td className="py-3 pr-4 text-lime-cream font-mono text-xs">GET</td><td className="py-3 pr-4 font-mono text-xs">/v1/coverage</td><td className="py-3">Coverage report</td></tr>
            <tr><td className="py-3 pr-4 text-lime-cream font-mono text-xs">POST</td><td className="py-3 pr-4 font-mono text-xs">/v1/chat/completions</td><td className="py-3">OpenAI-compatible proxy</td></tr>
          </tbody>
        </table>
      </div>

      <div className="bg-beige/40 border border-coffee-bean/10 rounded-lg p-6 mt-4">
        <p className="text-coffee-bean/80 text-sm"><strong>Note:</strong> The API server exists to support Phylax operations (trace storage, golden management, CI verdicts). It is not an extensibility platform. Start it with <code className="px-1 py-0.5 rounded bg-porcelain text-xs">phylax server</code>.</p>
      </div>
    </div>
  );
}
