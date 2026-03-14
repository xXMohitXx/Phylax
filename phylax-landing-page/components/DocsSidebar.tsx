import React from 'react';
import Link from 'next/link';

export default function DocsSidebar() {
  const sections = [
    {
      title: 'Getting Started',
      links: [
        { name: 'Overview', href: '/docs' },
        { name: 'Quickstart', href: '/docs/quickstart' },
        { name: 'Dataset Contracts', href: '/docs/dataset-contracts' },
        { name: 'CI Integration', href: '/docs/ci-integration' },
        { name: 'Model Upgrade Testing', href: '/docs/model-upgrade-testing' }
      ]
    },
    {
      title: 'Concepts',
      links: [
        { name: 'Traces', href: '/docs/concepts/traces' },
        { name: 'Expectations', href: '/docs/concepts/expectations' },
        { name: 'Execution Graphs', href: '/docs/concepts/execution-graphs' },
        { name: 'Surfaces', href: '/docs/concepts/surfaces' }
      ]
    },
    {
      title: 'Guides',
      links: [
        { name: 'Testing AI Systems', href: '/docs/guides/testing-ai-systems' },
        { name: 'Debugging Failures', href: '/docs/guides/debugging-failures' },
        { name: 'Agent Testing', href: '/docs/guides/agent-testing' },
        { name: 'CI Pipelines', href: '/docs/guides/ci-pipelines' }
      ]
    },
    {
      title: 'Integrations',
      links: [
        { name: 'OpenAI', href: '/docs/integrations/openai' },
        { name: 'Gemini', href: '/docs/integrations/gemini' },
        { name: 'Ollama', href: '/docs/integrations/ollama' },
        { name: 'Langchain', href: '/docs/integrations/langchain' }
      ]
    },
    {
      title: 'Architecture',
      links: [
        { name: 'Axis 1 - Expectations', href: '/docs/architecture/axis1-expectations' },
        { name: 'Axis 2 - Surfaces', href: '/docs/architecture/axis2-surfaces' },
        { name: 'Axis 3 - Metrics', href: '/docs/architecture/axis3-metrics' },
        { name: 'Axis 4 - Artifacts', href: '/docs/architecture/axis4-artifacts' }
      ]
    },
    {
      title: 'Reference',
      links: [
        { name: 'API', href: '/docs/api' }
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