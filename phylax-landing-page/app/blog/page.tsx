import React from 'react';
import Link from 'next/link';
import { ArrowRight } from 'lucide-react';
import { Footer } from '@/components/Footer';

export default function BlogIndex() {
  return (
    <>
      <div className="max-w-4xl mx-auto px-6 py-24">
        <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight text-coffee-bean mb-6">
          The Phylax Blog
        </h1>
        <p className="text-xl text-coffee-bean/70 mb-16">
          Thoughts on deterministic AI engineering, CI pipelines, and ending &quot;vibes-based&quot; testing.
        </p>

        <div className="space-y-12">
          
          <article className="group cursor-pointer">
            <Link href="/blog/ai-regressions">
              <div className="flex flex-col md:flex-row gap-8 items-start md:items-center p-6 rounded-2xl border border-black/10 hover:border-coffee-bean/20 hover:bg-beige/30 transition-all">
                <div className="flex-shrink-0 w-full md:w-64 h-40 bg-gradient-to-br from-beige to-porcelain rounded-xl flex items-center justify-center border border-black/10">
                  <span className="text-coffee-bean/50 font-mono text-sm group-hover:text-lime-cream transition-colors">model.generate()</span>
                </div>
                <div>
                  <div className="flex items-center gap-3 mb-3">
                    <span className="text-lime-cream bg-coffee-bean/10 px-2 py-0.5 rounded text-sm font-medium">Engineering</span>
                    <span className="text-coffee-bean/50 text-sm">March 14, 2026</span>
                  </div>
                  <h2 className="text-2xl font-bold text-coffee-bean mb-3 group-hover:text-lime-cream transition-colors">
                    Why AI Systems Regress
                  </h2>
                  <p className="text-coffee-bean/70 leading-relaxed max-w-2xl">
                    Model weight updates, prompt drift, and non-deterministic outputs. Why monitoring in production isn&apos;t enough, and why we built Phylax.
                  </p>
                  <div className="text-lime-cream text-sm font-medium mt-4 flex items-center gap-2">
                    Read Article <ArrowRight className="w-4 h-4" />
                  </div>
                </div>
              </div>
            </Link>
          </article>

        </div>
      </div>
      <Footer />
    </>
  );
}
