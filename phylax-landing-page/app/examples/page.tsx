import React from 'react';
import Link from 'next/link';
import { ArrowRight, Bot, Database, Workflow, ShieldCheck } from 'lucide-react';
import { Footer } from '@/components/Footer';

export default function ExamplesIndex() {
  const examples = [
    {
      title: "Support Bot Testing",
      description: "Enforce refund policies, safety guardrails, and response quality on a customer support agent using @trace, @expect, and Dataset Contracts.",
      icon: Bot,
      href: "/examples/support-bot",
      color: "text-lime-cream"
    },
    {
      title: "RAG Pipeline Validation",
      description: "Validate that generated answers use retrieved context, don't hallucinate, and include citations. Uses ContextUsedRule, NoHallucinationRule, and CitationRequiredRule.",
      icon: Database,
      href: "/examples/rag-pipeline",
      color: "text-lime-cream"
    },
    {
      title: "Multi-Agent Workflows",
      description: "Enforce tool call ordering, validate agent step structure, and detect the first failing node in multi-step pipelines with ToolSequenceRule and AgentStepValidator.",
      icon: Workflow,
      href: "/examples/multi-agent",
      color: "text-lime-cream"
    },
    {
      title: "Guardrail Packs",
      description: "Apply pre-built PII, security, finance, and healthcare guardrail packs to automatically enforce domain-specific policies on any LLM output.",
      icon: ShieldCheck,
      href: "/examples/guardrail-packs",
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
              <div className="p-6 rounded-2xl border border-black/10 bg-porcelain hover:bg-white hover:border-coffee-bean/20 hover:shadow-[0_8px_30px_rgba(38,28,21,0.08)] transition-all h-full flex flex-col">
                <example.icon className={`w-8 h-8 mb-4 ${example.color}`} />
                <h3 className="text-xl font-bold text-coffee-bean mb-2">{example.title}</h3>
                <p className="text-coffee-bean/70 text-sm leading-relaxed flex-1 mb-6">
                  {example.description}
                </p>
                <div className="text-sm font-medium text-lime-cream flex items-center gap-2 mt-auto">
                  View Implementation <ArrowRight className="w-4 h-4" />
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
