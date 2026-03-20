import React from 'react';
import Link from 'next/link';

export default function DocsSidebar() {
  const sections = [
    {
      title: 'Getting Started',
      links: [
        { name: 'Overview', href: '/docs' },
        { name: 'Installation', href: '/docs/getting-started/installation' },
        { name: 'Quickstart', href: '/docs/getting-started/quickstart' },
        { name: 'Providers', href: '/docs/getting-started/providers' },
      ]
    },
    {
      title: 'Core Concepts',
      links: [
        { name: 'Traces & Expectations', href: '/docs/concepts/traces-expectations' },
        { name: 'Execution Context', href: '/docs/concepts/execution-context' },
        { name: 'Graph Model', href: '/docs/concepts/graph-model' },
      ]
    },
    {
      title: 'Axis 1: Advanced Expectations',
      links: [
        { name: 'Composition', href: '/docs/axis-1/composition' },
        { name: 'Conditionals', href: '/docs/axis-1/conditionals' },
        { name: 'Scoping', href: '/docs/axis-1/scoping' },
        { name: 'Templates', href: '/docs/axis-1/templates' },
      ]
    },
    {
      title: 'Axis 2: Surface Abstraction',
      links: [
        { name: 'Structured Output', href: '/docs/axis-2/structured-output' },
        { name: 'Tool Calling', href: '/docs/axis-2/tool-calling' },
        { name: 'Execution Traces', href: '/docs/axis-2/execution-traces' },
        { name: 'Cross-Run Stability', href: '/docs/axis-2/cross-run-stability' },
      ]
    },
    {
      title: 'Axis 3: Scale & Health',
      links: [
        { name: 'Metrics Foundation', href: '/docs/axis-3/metrics-foundation' },
        { name: 'Health API', href: '/docs/axis-3/health-api' },
        { name: 'Enforcement Modes', href: '/docs/axis-3/enforcement-modes' },
        { name: 'Meta-Enforcement', href: '/docs/axis-3/meta-enforcement' },
      ]
    },
    {
      title: 'Axis 4: Artifact Contracts',
      links: [
        { name: 'Verdicts', href: '/docs/axis-4/verdicts' },
        { name: 'Anti-Integration', href: '/docs/axis-4/anti-integration' },
      ]
    },
    {
      title: 'Evaluation & Datasets',
      links: [
        { name: 'Contracts', href: '/docs/datasets/contracts' },
        { name: 'Behavioral Diffs', href: '/docs/datasets/behavioral-diffs' },
        { name: 'Model Upgrades', href: '/docs/datasets/model-upgrades' },
      ]
    },
    {
      title: 'Applied Guides',
      links: [
        { name: 'Guardrail Packs', href: '/docs/guides/guardrail-packs' },
        { name: 'Multi-Agent', href: '/docs/guides/multi-agent' },
        { name: 'RAG Enforcement', href: '/docs/guides/rag-enforcement' },
      ]
    },
    {
      title: 'CI/CD Integration',
      links: [
        { name: 'GitHub Actions', href: '/docs/ci/github-actions' },
        { name: 'GitLab CI', href: '/docs/ci/gitlab-ci' },
        { name: 'Jenkins', href: '/docs/ci/jenkins' },
      ]
    }
  ];

  return (
    <aside className="w-64 border-r border-white/10 h-screen sticky top-0 overflow-y-auto bg-[#020202] p-6 text-sm flex-shrink-0 hide-scrollbar">
      <div className="mb-10 mt-2 flex items-center gap-2">
        <div className="w-6 h-6 rounded bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center font-bold text-xs text-white">
          P
        </div>
        <span className="font-bold tracking-wide text-white">Phylax Docs</span>
      </div>
      <nav className="space-y-8">
        {sections.map((section) => (
          <div key={section.title}>
            <h4 className="font-semibold text-white mb-3 tracking-wide">{section.title}</h4>
            <ul className="space-y-2.5">
              {section.links.map((link) => (
                <li key={link.name}>
                  <Link href={link.href} className="text-gray-400 hover:text-white transition-colors block">
                    {link.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </nav>
    </aside>
  );
}