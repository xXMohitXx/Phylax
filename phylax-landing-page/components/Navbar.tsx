import React from 'react';
import Link from 'next/link';
import { ArrowRight, Shield, Github } from 'lucide-react';

export function Navbar() {
  return (
    <header className="sticky top-0 z-50 w-full border-b border-black/20 bg-porcelain backdrop-blur-md">
      <div className="flex h-14 items-center px-4 md:px-8 mx-auto w-full max-w-[1536px]">
        <Link href="/" className="flex items-center gap-2.5 group">
          <img src="/favicon.png" alt="Phylax Logo" className="w-7 h-7 rounded-md shadow-[0_0_10px_rgba(197,216,109,0.1)] group-hover:shadow-[0_0_15px_rgba(197,216,109,0.4)] transition-all" />
          <span className="text-lg font-bold tracking-tight text-coffee-bean">Phylax</span>
        </Link>
        
        <nav className="ml-10 hidden md:flex items-center gap-6">
          <Link href="/docs" className="text-[13px] font-medium text-coffee-bean/80 hover:text-lime-cream transition-colors">Documentation</Link>
          <Link href="/blog" className="text-[13px] font-medium text-coffee-bean/80 hover:text-lime-cream transition-colors">Blog</Link>
          <Link href="/examples" className="text-[13px] font-medium text-coffee-bean/80 hover:text-lime-cream transition-colors">Examples</Link>
          <Link href="/why-phylax" className="text-[13px] font-medium text-coffee-bean/80 hover:text-lime-cream transition-colors">Why Phylax?</Link>
        </nav>

        <div className="ml-auto flex items-center gap-4">
          <a href="https://github.com/xXMohitXx/phylax" target="_blank" rel="noreferrer" className="text-coffee-bean/80 hover:text-lime-cream transition-colors flex items-center gap-2 text-[13px] font-medium hidden sm:flex border border-coffee-bean/10 bg-black/20 hover:bg-black/40 px-3 py-1.5 rounded-md">
            <Github className="w-4 h-4" />
            <span>Star on GitHub</span>
          </a>
          <Link href="/docs/quickstart">
            <button className="hidden md:flex items-center gap-2 px-3 py-1.5 bg-lime-cream hover:bg-lime-cream/90 text-coffee-bean rounded-md text-[13px] font-bold transition-all">
              Sign Up <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </Link>
        </div>
      </div>
    </header>
  );
}
