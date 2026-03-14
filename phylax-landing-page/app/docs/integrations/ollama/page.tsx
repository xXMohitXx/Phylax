import React from 'react';
import { CodeBlock } from '@/components/code-block';

export default function OllamaPage() {
  return (
    <div className="flex flex-col gap-6 w-full">
      <h1 className="text-4xl font-extrabold tracking-tight lg:text-5xl mb-2 text-coffee-bean">Ollama Integration</h1>
      <p className="text-xl text-coffee-bean/80">Run Phylax against local models using Ollama. Zero API costs, full offline support, perfect for development and edge deployments.</p>
      <hr className="my-6 border-black/10" />
      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Installation</h2>
      <CodeBlock language="bash" title="Terminal" code={`pip install phylax[ollama]

# Make sure Ollama is running:
# https://ollama.ai
ollama serve`} />
      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Environment</h2>
      <CodeBlock language="bash" title="Environment Variable" code={`# Default: http://localhost:11434
export OLLAMA_HOST="http://localhost:11434"`} />
      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Usage</h2>
      <CodeBlock language="python" title="ollama_usage.py" code={`from phylax import OllamaAdapter

adapter = OllamaAdapter()  # Uses OLLAMA_HOST env var

response, trace = adapter.generate(
    prompt="Hello!",
    model="llama3"
)

# List available local models
models = adapter.list_models()`} />
      <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Supported Models</h2>
      <div className="overflow-x-auto"><table className="w-full text-sm border-collapse">
        <thead><tr className="border-b border-black/10"><th className="text-left py-3 pr-4 font-semibold text-coffee-bean">Model</th><th className="text-left py-3 font-semibold text-coffee-bean">Description</th></tr></thead>
        <tbody className="text-coffee-bean/80">
          <tr className="border-b border-black/5"><td className="py-3 pr-4">llama3</td><td className="py-3">Meta Llama 3</td></tr>
          <tr className="border-b border-black/5"><td className="py-3 pr-4">mistral</td><td className="py-3">Mistral 7B</td></tr>
          <tr className="border-b border-black/5"><td className="py-3 pr-4">codellama</td><td className="py-3">Code Llama</td></tr>
          <tr><td className="py-3 pr-4">phi3</td><td className="py-3">Microsoft Phi-3</td></tr>
        </tbody>
      </table></div>
    </div>
  );
}
