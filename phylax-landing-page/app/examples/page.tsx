import React from 'react';
import Link from 'next/link';
import { ArrowRight, Bot, Database, Workflow, ShieldCheck } from 'lucide-react';
import { Footer } from '@/components/Footer';

export default function ExamplesIndex() {
  const examples = [
    {
      title: "Support Bot Testing",
      description: "Asserting refund policies, tool usages, and formatting for a multi-turn support agent. Demonstrates @trace, @expect, and Dataset Contracts.",
      icon: Bot,
      href: "/examples/support-bot",
      color: "text-lime-cream"
    },
    {
      title: "RAG Pipeline Validation",
      description: "Testing that generated answers strictly synthesize retrieved context without hallucination. Uses Surface Enforcement for structured output validation.",
      icon: Database,
      href: "#",
      color: "text-lime-cream"
    },
    {
      title: "Multi-Agent Workflows",
      description: "Tracing Execution Graphs across multi-step agent pipelines to pinpoint exact node failures with Evidence Purity first-failing-node detection.",
      icon: Workflow,
      href: "#",
      color: "text-lime-cream"
    },
    {
      title: "Guardrail Packs",
      description: "Apply pre-built safety, quality, and compliance packs to automatically enforce content policies across your entire LLM application.",
      icon: ShieldCheck,
      href: "#",
      color: "text-lime-cream"
    }
  ];

  return (
    <>
      <div className="max-w-7xl mx-auto px-6 py-24">
        <div className="max-w-3xl mb-16">
          <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight text-coffee-bean mb-6">
            Real-World Examples
          </h1>
          <p className="text-xl text-coffee-bean/70">
            See how teams use Phylax to enforce contracts on complex, multi-modal, and agentic workflows.
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {examples.map((example) => (
            <Link key={example.title} href={example.href}>
              <div className={`p-6 rounded-2xl border bg-porcelain hover:bg-white transition-all h-full flex flex-col ${example.href === '#' ? 'opacity-50 cursor-not-allowed border-black/10' : 'border-black/10 hover:border-coffee-bean/20 hover:shadow-[0_8px_30px_rgba(38,28,21,0.08)]'}`}>
                <example.icon className={`w-8 h-8 mb-4 ${example.color}`} />
                <h3 className="text-xl font-bold text-coffee-bean mb-2">{example.title}</h3>
                <p className="text-coffee-bean/70 text-sm leading-relaxed flex-1 mb-6">
                  {example.description}
                </p>
                <div className="text-sm font-medium text-coffee-bean/60 flex items-center gap-2 mt-auto">
                  {example.href === '#' ? 'Coming Soon' : 'View Implementation'} <ArrowRight className="w-4 h-4" />
                </div>
              </div>
            </Link>
          ))}
        </div>
      </div>
      <Footer />
    </>
  );
}
