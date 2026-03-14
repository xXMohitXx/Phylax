'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { 
  BookOpen, 
  Terminal, 
  Settings, 
  ShieldCheck, 
  Layout, 
  FileJson, 
  Workflow, 
  Search,
  Activity,
  Layers,
  Cpu
} from 'lucide-react';

const navigation = [
  {
    name: 'Overview',
    items: [
      { name: 'Introduction', href: '/docs', icon: BookOpen },
      { name: 'Getting Started', href: '/docs/getting-started', icon: Terminal },
      { name: 'Quickstart', href: '/docs/quickstart', icon: Activity },
      { name: 'Dataset Contracts', href: '/docs/dataset-contracts', icon: FileJson },
      { name: 'CI Integration', href: '/docs/ci-integration', icon: Settings },
      { name: 'Model Upgrade Testing', href: '/docs/model-upgrade-testing', icon: Cpu },
    ],
  },
  {
    name: 'Concepts',
    items: [
      { name: 'Traces', href: '/docs/concepts/traces', icon: FileJson },
      { name: 'Expectations', href: '/docs/concepts/expectations', icon: ShieldCheck },
      { name: 'Execution Graphs', href: '/docs/concepts/execution-graphs', icon: Workflow },
      { name: 'Surfaces', href: '/docs/concepts/surfaces', icon: Layout },
    ],
  },
  {
    name: 'Guides',
    items: [
      { name: 'Testing AI Systems', href: '/docs/guides/testing-ai-systems', icon: Layout },
      { name: 'Debugging Failures', href: '/docs/guides/debugging-failures', icon: Terminal },
      { name: 'Agent Workflows', href: '/docs/guides/agent-testing', icon: Workflow },
      { name: 'CI Pipelines', href: '/docs/guides/ci-pipelines', icon: Settings },
    ],
  },
  {
    name: 'Integrations',
    items: [
      { name: 'OpenAI', href: '/docs/integrations/openai', icon: Layers },
      { name: 'Gemini', href: '/docs/integrations/gemini', icon: Layers },
      { name: 'Ollama', href: '/docs/integrations/ollama', icon: Layers },
      { name: 'LangChain', href: '/docs/integrations/langchain', icon: Layers },
    ],
  },
  {
    name: 'Architecture',
    items: [
      { name: 'Axis 1 - Expectations', href: '/docs/architecture/axis1-expectations', icon: ShieldCheck },
      { name: 'Axis 2 - Surfaces', href: '/docs/architecture/axis2-surfaces', icon: Layout },
      { name: 'Axis 3 - Metrics', href: '/docs/architecture/axis3-metrics', icon: Activity },
      { name: 'Axis 4 - Artifacts', href: '/docs/architecture/axis4-artifacts', icon: FileJson },
    ],
  },
  {
    name: 'Reference',
    items: [
      { name: 'API Reference', href: '/docs/api', icon: Terminal },
    ],
  },
];

export function Sidebar() {
  const pathname = usePathname();
  const [searchQuery, setSearchQuery] = React.useState('');

  const filteredNavigation = navigation.map(section => ({
    ...section,
    items: section.items.filter(item => 
      item.name.toLowerCase().includes(searchQuery.toLowerCase())
    )
  })).filter(section => section.items.length > 0);

  return (
    <aside className="w-64 lg:w-72 flex-shrink-0 border-r border-black/10 bg-porcelain h-[calc(100vh-4rem)] sticky top-16 overflow-y-auto hidden md:block no-scrollbar py-6">
      
      {/* Search Placeholder */}
      <div className="px-5 mb-6">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-coffee-bean/40" />
          <input 
            type="text" 
            placeholder="Search docs..." 
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-white/60 border border-black/10 rounded-md py-1.5 pl-9 pr-4 text-sm text-coffee-bean focus:outline-none focus:border-coffee-bean/30 focus:ring-1 focus:ring-coffee-bean/30 transition-colors placeholder:text-coffee-bean/40 shadow-sm"
          />
        </div>
      </div>

      <nav className="px-3 pb-8 space-y-6">
        {filteredNavigation.length === 0 ? (
          <div className="text-sm text-coffee-bean/40 text-center py-4">No results found</div>
        ) : (
          filteredNavigation.map((section) => (
            <div key={section.name}>
              <h4 className="px-2 mb-2 text-xs font-semibold text-coffee-bean/50 uppercase tracking-wider">
                {section.name}
              </h4>
              <ul className="space-y-0.5">
                {section.items.map((item) => {
                  const isActive = pathname === item.href;
                  const Icon = item.icon;
                  return (
                    <li key={item.name}>
                      <Link
                        href={item.href}
                        className={`flex items-center gap-3 px-2 py-1.5 rounded-md text-sm transition-colors ${
                          isActive 
                            ? 'bg-beige border border-black/5 text-coffee-bean font-semibold shadow-sm' 
                            : 'text-coffee-bean/70 hover:text-coffee-bean hover:bg-black/5'
                        }`}
                      >
                        <Icon className="w-4 h-4" />
                        {item.name}
                      </Link>
                    </li>
                  );
                })}
              </ul>
            </div>
          ))
        )}
      </nav>
    </aside>
  );
}
