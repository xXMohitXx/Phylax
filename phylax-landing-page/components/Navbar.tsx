'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { ArrowRight, Shield, Github, Menu, X } from 'lucide-react';

export function Navbar() {
  const [isOpen, setIsOpen] = useState(false);

  // Close menu on route change or resize past md
  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth >= 768) setIsOpen(false);
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Prevent body scroll when menu is open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => { document.body.style.overflow = ''; };
  }, [isOpen]);

  return (
    <header className="sticky top-0 z-50 w-full border-b border-black/20 bg-porcelain backdrop-blur-md">
      <div className="flex h-14 items-center px-4 md:px-8 mx-auto w-full max-w-[1536px]">
        <Link href="/" className="flex items-center gap-2.5 group">
          <img src="/favicon.png" alt="Phylax Logo" className="w-7 h-7 rounded-md shadow-[0_0_10px_rgba(197,216,109,0.1)] group-hover:shadow-[0_0_15px_rgba(197,216,109,0.4)] transition-all" />
          <span className="text-lg font-bold tracking-tight text-coffee-bean">Phylax</span>
        </Link>

        {/* Desktop nav */}
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

          {/* Mobile hamburger */}
          <button
            className="md:hidden flex items-center justify-center w-9 h-9 rounded-md border border-coffee-bean/10 text-coffee-bean hover:bg-beige/50 transition-colors"
            onClick={() => setIsOpen(!isOpen)}
            aria-label="Toggle menu"
          >
            {isOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>
      </div>

      {/* Mobile drawer */}
      <div
        className={`md:hidden overflow-hidden transition-all duration-300 ease-in-out border-t border-black/10 bg-porcelain ${isOpen ? 'max-h-[400px] opacity-100' : 'max-h-0 opacity-0 border-t-0'
          }`}
      >
        <nav className="flex flex-col px-6 py-4 gap-1">
          <Link href="/docs" onClick={() => setIsOpen(false)} className="py-3 text-[15px] font-medium text-coffee-bean/80 hover:text-lime-cream transition-colors border-b border-black/5">Documentation</Link>
          <Link href="/blog" onClick={() => setIsOpen(false)} className="py-3 text-[15px] font-medium text-coffee-bean/80 hover:text-lime-cream transition-colors border-b border-black/5">Blog</Link>
          <Link href="/examples" onClick={() => setIsOpen(false)} className="py-3 text-[15px] font-medium text-coffee-bean/80 hover:text-lime-cream transition-colors border-b border-black/5">Examples</Link>
          <Link href="/why-phylax" onClick={() => setIsOpen(false)} className="py-3 text-[15px] font-medium text-coffee-bean/80 hover:text-lime-cream transition-colors border-b border-black/5">Why Phylax?</Link>

          <div className="flex flex-col gap-3 pt-4">
            <a href="https://github.com/xXMohitXx/phylax" target="_blank" rel="noreferrer" className="flex items-center justify-center gap-2 px-4 py-2.5 rounded-md border border-coffee-bean/10 bg-black/5 text-coffee-bean text-sm font-medium hover:bg-black/10 transition-colors">
              <Github className="w-4 h-4" />
              Star on GitHub
            </a>
            <Link href="/docs/quickstart" onClick={() => setIsOpen(false)}>
              <button className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-lime-cream hover:bg-lime-cream/90 text-coffee-bean rounded-md text-sm font-bold transition-all">
                Sign Up <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </Link>
          </div>
        </nav>
      </div>
    </header>
  );
}
