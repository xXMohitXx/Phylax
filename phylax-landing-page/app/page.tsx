import React from 'react';
import Link from 'next/link';
import { ArrowRight, Terminal, Shield, Workflow, Play, CheckCircle2, Copy, FileJson, Layers, Lock, Package, Gauge, Cog, BarChart3 } from 'lucide-react';
import { FeatureCard } from '@/components/feature-card';
import { CodeBlock } from '@/components/code-block';
import { BetaSignup } from '@/components/beta-signup';
import { Footer } from '@/components/Footer';

export default function LandingPage() {
  return (
    <div className="flex flex-col w-full">
      {/* 1. Hero Section */}
      <section className="relative pt-8 pb-12 md:pt-16 md:pb-20 overflow-hidden px-4 bg-porcelain">
        {/* Subtle grid pattern */}
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#e4e6c3_1px,transparent_1px),linear-gradient(to_bottom,#e4e6c3_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)] opacity-30 pointer-events-none" />
        
        <div className="max-w-7xl mx-auto relative z-10 flex flex-col items-center text-center" style={{marginTop: "3rem", marginBottom: "3rem"}}>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-beige border border-coffee-bean/10 text-sm text-coffee-bean mb-8">
            <span className="flex h-2 w-2 relative">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-lime-cream opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-lime-cream"></span>
            </span>
            Phylax v1.6.4 is now available
          </div>
          
          <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight text-coffee-bean mb-6 max-w-4xl space-y-2">
            <span className="block">CI for AI Behavior</span>
            <span className="block">
              Stop regressions before production.
            </span>
          </h1>
          
          <p className="text-xl text-coffee-bean/80 max-w-2xl mb-10 leading-relaxed">
            Phylax is an infrastructure system for enforcing deterministic behavioral contracts on LLM outputs. 
            No latency-heavy &quot;LLM-as-a-judge&quot;. Just predictable, binary test enforcement in your CI pipelines.
          </p>
          
          <div className="flex flex-col sm:flex-row items-center gap-4 w-full sm:w-auto">
            <Link href="/docs/quickstart">
              <button className="w-full sm:w-auto flex items-center justify-center gap-2 px-8 py-4 bg-lime-cream hover:bg-lime-cream/90 text-coffee-bean rounded-md text-lg font-bold transition-all shadow-sm">
                Read the Docs <ArrowRight className="w-5 h-5" />
              </button>
            </Link>
            
            <div className="w-full sm:w-auto flex items-center gap-3 px-6 py-4 bg-transparent border-2 border-coffee-bean rounded-md text-coffee-bean font-mono text-sm">
              <Terminal className="w-4 h-4 text-coffee-bean" />
              <span>pip install phylax</span>
              <button className="ml-2 hover:text-coffee-bean/70 transition-colors" title="Copy to clipboard">
                <Copy className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* 2. Dual Panel: Problem vs Solution */}
      <section className="py-20 bg-coffee-bean border-y border-black/10 relative">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          
          <div className="grid md:grid-cols-2 gap-12 lg:gap-24 items-center">
            {/* The Problem */}
            <div>
              <h2 className="text-3xl font-bold text-porcelain mb-4">The Problem with AI Testing</h2>
              <p className="text-beige mb-6 leading-relaxed">
                LLMs update their weights. Prompts drift. Developers push code. 
                Suddenly, your meticulously tuned support bot starts hallucinating or breaking its structured JSON formatting. 
                <br /><br />
                Monitoring catches this in production—<strong>after the damage is done.</strong>
              </p>
              <ul className="space-y-3">
                <li className="flex items-start gap-3 text-porcelain/90">
                  <div className="p-1 rounded bg-fail-red/10 border border-fail-red/20 mt-0.5"><div className="w-1.5 h-1.5 rounded-full bg-fail-red" /></div>
                  &quot;LLM-as-a-judge&quot; is too slow, expensive, and flaky for CI.
                </li>
                <li className="flex items-start gap-3 text-porcelain/90">
                  <div className="p-1 rounded bg-fail-red/10 border border-fail-red/20 mt-0.5"><div className="w-1.5 h-1.5 rounded-full bg-fail-red" /></div>
                  Model upgrades silently break multi-step agent logic.
                </li>
                <li className="flex items-start gap-3 text-porcelain/90">
                  <div className="p-1 rounded bg-fail-red/10 border border-fail-red/20 mt-0.5"><div className="w-1.5 h-1.5 rounded-full bg-fail-red" /></div>
                  Prompt drift causes cascading failures across your agent workflow.
                </li>
              </ul>
            </div>

            {/* The Solution */}
            <div className="relative">
              <CodeBlock 
                title="test_support_bot.py"
                language="python"
                highlightedLines={[4, 5]}
                code={`from phylax import trace, expect, OpenAIAdapter

@trace(provider="openai")
@expect(must_include=["refund_policy"])
@expect(max_latency_ms=2000)
def handle_refund(message: str) -> str:
    adapter = OpenAIAdapter()
    response, _ = adapter.chat_completion(
        model="gpt-4",
        messages=[{"role": "user", "content": message}]
    )
    return response`}
              />
            </div>
          </div>
        </div>
      </section>

      {/* 3. Core Capabilities Grid — All Features */}
      <section className="py-24 relative bg-beige">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-coffee-bean mb-6">Built for Serious Infrastructure</h2>
            <p className="text-lg text-coffee-bean/80">Everything you need to enforce behavioral contracts on LLM outputs across your entire stack.</p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            <FeatureCard 
              variant="glow"
              title="Deterministic Rules" 
              description="No probabilistic AI scoring. Enforce strict contracts via must_include, must_not_include, max_latency_ms, min_tokens — all producing binary PASS/FAIL verdicts."
              icon={Shield} 
            />
            <FeatureCard 
              variant="glow"
              title="Execution Graphs (DAG)" 
              description="Group traces across complex, multi-agent workflows. Automatically track parent-child cascades to pinpoint exactly which internal LLM thought failed first."
              icon={Workflow} 
            />
            <FeatureCard 
              variant="glow"
              title="Surface Enforcement" 
              description="Don't just test text. Parse and validate structured JSON outputs, tool calls, execution traces, and cross-run stability with the Surface Abstraction Layer."
              icon={FileJson} 
            />
            <FeatureCard 
              variant="glow"
              title="Enforcement Modes" 
              description="Three modes for every stage: enforce (block CI), quarantine (block + log), observe (log only). Gradually roll out contracts without breaking your pipeline."
              icon={Lock} 
            />
            <FeatureCard 
              variant="glow"
              title="Guardrail Packs" 
              description="Pre-built contract templates for common use cases: safety (blocks PII, hate speech), quality (min length, latency), and compliance (regulatory output constraints)."
              icon={Package} 
            />
            <FeatureCard 
              variant="glow"
              title="Dataset Contracts" 
              description="Define behavioral contracts in YAML. Batch-test hundreds of prompts against live models. Run in CI to catch regressions before they merge."
              icon={Layers} 
            />
          </div>
        </div>
      </section>

      {/* 4. How Phylax Works — Step by Step */}
      <section className="py-24 bg-porcelain relative">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-coffee-bean mb-6">How It Works</h2>
            <p className="text-lg text-coffee-bean/80">From instrumentation to CI enforcement in 4 steps.</p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {[
              { step: "01", title: "Trace", desc: "Wrap your LLM calls with @trace. Phylax records every input, output, latency, and token count.", icon: "📝" },
              { step: "02", title: "Expect", desc: "Declare behavioral contracts with @expect — must_include, must_not_include, latency bounds, token minimums.", icon: "✅" },
              { step: "03", title: "Bless", desc: "Mark known-good outputs as golden baselines. Future runs are hash-compared against these references.", icon: "⭐" },
              { step: "04", title: "Enforce", desc: "Run phylax check in CI. Exit code 0 = all pass. Exit code 1 = regression detected. PR blocked.", icon: "🚫" },
            ].map((item) => (
              <div key={item.step} className="relative group">
                <div className="bg-white rounded-xl border border-black/10 p-6 hover:shadow-[0_8px_30px_rgba(38,28,21,0.08)] transition-all h-full">
                  <div className="text-3xl mb-4">{item.icon}</div>
                  <div className="text-xs font-mono text-lime-cream mb-2">STEP {item.step}</div>
                  <h3 className="text-xl font-bold text-coffee-bean mb-2">{item.title}</h3>
                  <p className="text-coffee-bean/70 text-sm leading-relaxed">{item.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* 5. Dataset Contracts & Simulation Showcase */}
      <section className="py-24 bg-coffee-bean border-y border-black/20 relative overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            
            <div className="order-2 lg:order-1 space-y-6">
              <CodeBlock 
                title="Terminal"
                language="bash"
                code={`$ phylax simulate --from gpt-4 --to gpt-4.5 dataset.yaml

[Simulating 450 contract interactions...]

[gpt-4.5] PASS: Test 12 (Latency: 800ms)
[gpt-4.5] FAIL: Test 42 
   Violation: ToolPresenceRule failed
   Expected: 'fetch_db'
   Actual Payload: {}

CI Blocked. Model upgrade rejected.`}
              />
            </div>

            <div className="order-1 lg:order-2">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-md bg-lime-cream/10 border border-lime-cream/20 text-lime-cream text-sm mb-6 font-mono">
                <Play className="w-4 h-4" /> Simulation Engine
              </div>
              <h2 className="text-3xl md:text-4xl font-bold text-porcelain mb-6">Model Upgrade Simulation</h2>
              <p className="text-lg text-beige mb-6">
                OpenAI drops a new model variant. Is it safe to deploy? 
              </p>
              <p className="text-lg text-beige mb-8">
                Point Phylax at your Dataset Contracts YAML. It runs your thousands of prompts against the new remote model, maps it against your deterministic boundaries, and immediately flags behavioral drifts. 
              </p>
              <ul className="space-y-4">
                <li className="flex items-center gap-3 text-porcelain/90">
                  <CheckCircle2 className="w-5 h-5 text-lime-cream" /> Verify prompt boundary drift
                </li>
                <li className="flex items-center gap-3 text-porcelain/90">
                  <CheckCircle2 className="w-5 h-5 text-lime-cream" /> Measure systemic latency changes
                </li>
                <li className="flex items-center gap-3 text-porcelain/90">
                  <CheckCircle2 className="w-5 h-5 text-lime-cream" /> Ensure critical safety barriers hold
                </li>
              </ul>
            </div>

          </div>
        </div>
      </section>

      {/* 6. Supported Providers */}
      <section className="py-20 bg-beige">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-12">
            <h2 className="text-3xl md:text-4xl font-bold text-coffee-bean mb-4">Works with Every Provider</h2>
            <p className="text-lg text-coffee-bean/80">One interface, any model. All adapters share the same <code className="px-1.5 py-0.5 bg-porcelain rounded text-sm">generate()</code> and <code className="px-1.5 py-0.5 bg-porcelain rounded text-sm">chat_completion()</code> API.</p>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            {[
              { name: "OpenAI", models: "GPT-4o, GPT-4 Turbo", env: "OPENAI_API_KEY", install: "phylax[openai]" },
              { name: "Gemini", models: "Gemini 2.5 Flash/Pro", env: "GOOGLE_API_KEY", install: "phylax[google]" },
              { name: "Groq", models: "Llama 3, Mixtral", env: "GROQ_API_KEY", install: "phylax[groq]" },
              { name: "Mistral", models: "Large, Small, Codestral", env: "MISTRAL_API_KEY", install: "phylax[mistral]" },
              { name: "HuggingFace", models: "Any Inference API model", env: "HF_TOKEN", install: "phylax[huggingface]" },
              { name: "Ollama", models: "Llama 3, Phi-3, local", env: "OLLAMA_HOST", install: "phylax[ollama]" },
            ].map((p) => (
              <div key={p.name} className="bg-porcelain rounded-xl border border-black/10 p-5 text-center hover:shadow-[0_8px_30px_rgba(38,28,21,0.08)] transition-all group">
                <div className="text-lg font-bold text-coffee-bean mb-1 group-hover:text-lime-cream transition-colors">{p.name}</div>
                <div className="text-xs text-coffee-bean/60 mb-2">{p.models}</div>
                <div className="text-[10px] font-mono text-coffee-bean/40 bg-beige/50 rounded px-2 py-1">{p.install}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* 7. CLI Commands Reference */}
      <section className="py-20 bg-porcelain">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            <div>
              <h2 className="text-3xl md:text-4xl font-bold text-coffee-bean mb-6">Powerful CLI</h2>
              <p className="text-lg text-coffee-bean/80 mb-8">
                Everything you need from one command: trace management, golden baselines, CI enforcement, dataset execution, and model simulation.
              </p>
              <div className="space-y-3">
                {[
                  { cmd: "phylax check", desc: "CI enforcement — exits 1 on violation" },
                  { cmd: "phylax init", desc: "Initialize configuration" },
                  { cmd: "phylax server", desc: "Start API + Web UI inspector" },
                  { cmd: "phylax list --failed", desc: "List traces, filter by failures" },
                  { cmd: "phylax bless <id>", desc: "Mark trace as golden baseline" },
                  { cmd: "phylax dataset run", desc: "Execute dataset contracts" },
                  { cmd: "phylax simulate", desc: "Model upgrade simulation" },
                ].map((item) => (
                  <div key={item.cmd} className="flex items-center gap-4 p-3 bg-white rounded-lg border border-black/5">
                    <code className="text-sm font-mono text-lime-cream bg-code-bg px-3 py-1 rounded flex-shrink-0">{item.cmd}</code>
                    <span className="text-sm text-coffee-bean/70">{item.desc}</span>
                  </div>
                ))}
              </div>
            </div>
            <div>
              <CodeBlock 
                title="Terminal"
                language="bash"
                code={`$ phylax check

Evaluating 12 golden traces...

[1/12] trace-abc123 ✓ PASS (1204ms)
[2/12] trace-def456 ✓ PASS (890ms)
[3/12] trace-ghi789 ✗ FAIL
   Violation: must_include("refund_policy")
   Expected: substring "refund_policy"
   Actual: "We apologize for the inconvenience..."

❌ 1 contract violation detected.
Exit code: 1`}
              />
            </div>
          </div>
        </div>
      </section>

      {/* 8. Cloud Beta Signup */}
      <BetaSignup />

      {/* 9. Final CTA */}
      <section className="py-32 relative text-center bg-beige">
        <h2 className="text-4xl md:text-5xl font-bold text-coffee-bean mb-8">Stop testing AI with vibes.</h2>
        <p className="text-xl text-coffee-bean/80 mb-10 max-w-2xl mx-auto">
          Start enforcing deterministic software contracts on your LLMs today. Open source and ready for scale.
        </p>
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
          <Link href="/docs/quickstart">
            <button className="px-8 py-4 bg-coffee-bean hover:bg-coffee-bean/90 text-lime-cream rounded-md text-lg font-bold transition-all shadow-sm">
              Read the Documentation
            </button>
          </Link>
          <a href="https://github.com/xXMohitXx/Phylax" target="_blank" rel="noreferrer">
            <button className="px-8 py-4 bg-transparent border-2 border-coffee-bean hover:bg-coffee-bean/5 text-coffee-bean rounded-md text-lg font-bold transition-all">
              Star on GitHub
            </button>
          </a>
        </div>
      </section>

      <Footer />
    </div>
  );
}