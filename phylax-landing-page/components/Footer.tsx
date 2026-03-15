import React from 'react';
import Link from 'next/link';

export function Footer() {
  return (
    <footer className="border-t border-black/20 bg-coffee-bean pt-16 pb-8 mt-auto">
      <div className="max-w-[1450px] w-full mx-auto px-6 md:px-8">
        <div className="flex flex-col md:flex-row items-center justify-between gap-8 mb-16 pb-12 border-b border-black/10">
          <div>
            <h2 className="text-2xl font-bold text-white mb-2">Subscribe to our newsletter</h2>
            <p className="text-beige/80 text-sm">Get the latest updates on AI regression testing and CI infrastructure.</p>
          </div>
          <div className="flex w-full md:w-auto max-w-sm gap-2">
            <input type="email" placeholder="Enter your email" className="flex-1 bg-black/20 border border-black/20 rounded-md px-4 py-2 text-sm text-white placeholder:text-beige/50 focus:outline-none focus:border-lime-cream outline-none" />
            <button className="px-4 py-2 bg-lime-cream text-coffee-bean rounded-md text-sm font-semibold hover:bg-lime-cream/90 transition-colors">Subscribe</button>
          </div>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-8 mb-12">
          
          <div className="col-span-2 lg:col-span-2">
            <Link href="/" className="flex items-center gap-2.5 mb-4 group">
              <img src="/favicon.png" alt="Phylax Logo" className="w-6 h-6 rounded-sm opacity-90 group-hover:opacity-100 transition-opacity" />
              <span className="text-base font-bold tracking-tight text-porcelain">Phylax</span>
            </Link>
            <p className="text-sm text-beige max-w-xs">
              CI enforcement for AI behavior. Stop LLM regressions before they reach production.
            </p>
          </div>

          <div>
            <h4 className="text-sm font-semibold text-white mb-4">Product</h4>
            <ul className="space-y-3 text-sm text-beige/80">
              <li><Link href="/docs/dataset-contracts" className="hover:text-lime-cream transition-colors">Dataset Contracts</Link></li>
              <li><Link href="/docs/concepts/execution-graphs" className="hover:text-lime-cream transition-colors">Execution Graphs</Link></li>
              <li><Link href="/docs/model-upgrade-testing" className="hover:text-lime-cream transition-colors">Model Upgrades</Link></li>
              <li><Link href="/why-phylax" className="hover:text-lime-cream transition-colors">Why Phylax?</Link></li>
            </ul>
          </div>

          <div>
            <h4 className="text-sm font-semibold text-white mb-4">Resources</h4>
            <ul className="space-y-3 text-sm text-beige/80">
              <li><Link href="/docs" className="hover:text-lime-cream transition-colors">Documentation</Link></li>
              <li><Link href="/examples" className="hover:text-lime-cream transition-colors">Examples</Link></li>
              <li><Link href="/blog" className="hover:text-lime-cream transition-colors">Blog</Link></li>
              <li><Link href="/docs/api" className="hover:text-lime-cream transition-colors">API Reference</Link></li>
            </ul>
          </div>

          <div>
            <h4 className="text-sm font-semibold text-white mb-4">Integrations</h4>
            <ul className="space-y-3 text-sm text-beige/80">
              <li><Link href="/docs/integrations/openai" className="hover:text-lime-cream transition-colors">OpenAI</Link></li>
              <li><Link href="/docs/integrations/gemini" className="hover:text-lime-cream transition-colors">Google Gemini</Link></li>
              <li><Link href="/docs/integrations/ollama" className="hover:text-lime-cream transition-colors">Ollama</Link></li>
              <li><Link href="/docs/integrations/langchain" className="hover:text-lime-cream transition-colors">LangChain</Link></li>
            </ul>
          </div>

        </div>

        <div className="border-t border-black/20 pt-8 flex flex-col md:flex-row items-center justify-between gap-4">
          <p className="text-[13px] text-beige">
            © {new Date().getFullYear()} Phylax. MIT License.
          </p>
          <div className="flex items-center gap-6 text-[13px] text-lime-cream font-medium">
            <a href="https://github.com/xXMohitXx/phylax" target="_blank" rel="noreferrer" className="hover:text-lime-cream/80 transition-colors">GitHub</a>
            <a href="https://pypi.org/project/phylax/" target="_blank" rel="noreferrer" className="hover:text-lime-cream/80 transition-colors">PyPI</a>
          </div>
        </div>
      </div>
    </footer>
  );
}