'use client';

import React, { useState } from 'react';
import { ArrowRight, Loader2, CheckCircle2, Sparkles } from 'lucide-react';

export function BetaSignup() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
  const [errorMsg, setErrorMsg] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setStatus('loading');
    setErrorMsg('');

    try {
      const response = await fetch('/api/beta-signup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, email }),
      });

      const data = await response.json();

      if (response.ok) {
        setStatus('success');
        setName('');
        setEmail('');
      } else {
        setStatus('error');
        setErrorMsg(data.error || 'Something went wrong');
      }
    } catch {
      setStatus('error');
      setErrorMsg('Network error. Please try again.');
    }
  };

  return (
    <section className="py-24 relative bg-coffee-bean overflow-hidden">
      {/* Subtle grid pattern */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#ffffff08_1px,transparent_1px),linear-gradient(to_bottom,#ffffff08_1px,transparent_1px)] bg-[size:4rem_4rem] pointer-events-none" />
      
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="text-center mb-12">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-lime-cream/10 border border-lime-cream/20 text-lime-cream text-sm font-medium mb-6">
            <Sparkles className="w-4 h-4" />
            Coming Soon
          </div>
          <h2 className="text-3xl md:text-4xl font-bold text-porcelain mb-4">
            Phylax Cloud — Zero Infrastructure CI
          </h2>
          <p className="text-lg text-beige max-w-2xl mx-auto">
            Managed CI enforcement for teams. No server setup, no config, no maintenance. 
            Push your contracts, we enforce them. Join the private beta waitlist.
          </p>
        </div>

        {status === 'success' ? (
          <div className="max-w-md mx-auto bg-lime-cream/10 border border-lime-cream/20 rounded-xl p-8 text-center">
            <CheckCircle2 className="w-12 h-12 text-lime-cream mx-auto mb-4" />
            <h3 className="text-xl font-bold text-porcelain mb-2">You&apos;re on the list!</h3>
            <p className="text-beige text-sm">We&apos;ll reach out when Phylax Cloud is ready for you.</p>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="max-w-md mx-auto space-y-4">
            <div>
              <input
                type="text"
                placeholder="Your name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
                className="w-full bg-black/20 border border-black/30 rounded-lg px-4 py-3 text-sm text-porcelain placeholder:text-beige/50 focus:outline-none focus:border-lime-cream/50 focus:ring-1 focus:ring-lime-cream/30 transition-colors"
              />
            </div>
            <div>
              <input
                type="email"
                placeholder="you@company.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full bg-black/20 border border-black/30 rounded-lg px-4 py-3 text-sm text-porcelain placeholder:text-beige/50 focus:outline-none focus:border-lime-cream/50 focus:ring-1 focus:ring-lime-cream/30 transition-colors"
              />
            </div>
            <button
              type="submit"
              disabled={status === 'loading'}
              className="w-full flex items-center justify-center gap-2 px-6 py-3 bg-lime-cream hover:bg-lime-cream/90 text-coffee-bean rounded-lg text-sm font-bold transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {status === 'loading' ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Signing up...
                </>
              ) : (
                <>
                  Join the Cloud Beta <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
            {status === 'error' && (
              <p className="text-fail-red text-sm text-center">{errorMsg}</p>
            )}
            <p className="text-beige/50 text-xs text-center">
              No spam. We&apos;ll only email you about Phylax Cloud availability.
            </p>
          </form>
        )}
      </div>
    </section>
  );
}
