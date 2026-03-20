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
  Cpu,
  Database,
  GitPullRequest
} from 'lucide-react';

const navigation = [
  {
    name: 'Getting Started',
    items: [
      { name: 'Introduction', href: '/docs', icon: BookOpen },
      { name: 'Why Phylax?', href: '/why-phylax', icon: ShieldCheck },
      { name: 'Installation', href: '/docs/getting-started/installation', icon: Terminal },
      { name: 'Quickstart', href: '/docs/getting-started/quickstart', icon: Activity },
      { name: 'Providers', href: '/docs/getting-started/providers', icon: Layers },
    ],
  },
  {
    name: 'Core Concepts',
    items: [
      { name: 'Traces & Expectations', href: '/docs/concepts/traces-expectations', icon: ShieldCheck },
      { name: 'Execution Context', href: '/docs/concepts/execution-context', icon: Workflow },
      { name: 'Graph Model', href: '/docs/concepts/graph-model', icon: Layout },
    ],
  },
  {
    name: 'Axis 1: Advanced Expectations',
    items: [
      { name: 'Composition', href: '/docs/axis-1/composition', icon: Layers },
      { name: 'Conditionals', href: '/docs/axis-1/conditionals', icon: FileJson },
      { name: 'Scoping', href: '/docs/axis-1/scoping', icon: Search },
      { name: 'Templates', href: '/docs/axis-1/templates', icon: Layout },
    ],
  },
  {
    name: 'Axis 2: Surface Abstraction',
    items: [
      { name: 'Structured Output', href: '/docs/axis-2/structured-output', icon: FileJson },
      { name: 'Tool Calling', href: '/docs/axis-2/tool-calling', icon: Settings },
      { name: 'Execution Traces', href: '/docs/axis-2/execution-traces', icon: Workflow },
      { name: 'Cross-Run Stability', href: '/docs/axis-2/cross-run-stability', icon: Database },
    ],
  },
  {
    name: 'Axis 3: Scale & Health',
    items: [
      { name: 'Metrics Foundation', href: '/docs/axis-3/metrics-foundation', icon: Activity },
      { name: 'Health API', href: '/docs/axis-3/health-api', icon: ShieldCheck },
      { name: 'Enforcement Modes', href: '/docs/axis-3/enforcement-modes', icon: Settings },
      { name: 'Meta-Enforcement', href: '/docs/axis-3/meta-enforcement', icon: Layout },
    ],
  },
  {
    name: 'Axis 4: Artifact Contracts',
    items: [
      { name: 'Verdicts', href: '/docs/axis-4/verdicts', icon: FileJson },
      { name: 'Anti-Integration', href: '/docs/axis-4/anti-integration', icon: ShieldCheck },
    ],
  },
  {
    name: 'Evaluation & Datasets',
    items: [
      { name: 'Contracts', href: '/docs/datasets/contracts', icon: FileJson },
      { name: 'Behavioral Diffs', href: '/docs/datasets/behavioral-diffs', icon: GitPullRequest },
      { name: 'Model Upgrades', href: '/docs/datasets/model-upgrades', icon: Cpu },
    ],
  },
  {
    name: 'Applied Guides',
    items: [
      { name: 'Guardrail Packs', href: '/docs/guides/guardrail-packs', icon: ShieldCheck },
      { name: 'Multi-Agent', href: '/docs/guides/multi-agent', icon: Workflow },
      { name: 'RAG Enforcement', href: '/docs/guides/rag-enforcement', icon: BookOpen },
    ],
  },
  {
    name: 'CI/CD Integration',
    items: [
      { name: 'GitHub Actions', href: '/docs/ci/github-actions', icon: Settings },
      { name: 'GitLab CI', href: '/docs/ci/gitlab-ci', icon: Settings },
      { name: 'Jenkins', href: '/docs/ci/jenkins', icon: Settings },
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
                        className={`flex items-center gap-3 px-2 py-1.5 rounded-md text-sm transition-colors ${isActive
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
    </aside >
  );
}
