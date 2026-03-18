import React from 'react';
import Link from 'next/link';
import { ArrowRight, Check } from 'lucide-react';
import { Footer } from '@/components/Footer';

const tiers = [
    {
        name: 'Open Source',
        price: 'Free',
        description: 'Everything you need for local CI enforcement. No limits, no catches — MIT licensed.',
        features: [
            'All deterministic rules',
            'Dataset contracts',
            'Surface enforcement',
            'Execution graphs (local UI)',
            'Community support on GitHub',
        ],
        cta: 'pip install phylax',
        href: '/docs/quickstart',
        highlighted: false,
    },
    {
        name: 'Pro',
        price: '$29',
        interval: '/month',
        description: 'For developers who want cloud-hosted dataset runs and trace history.',
        features: [
            'Everything in Open Source',
            'Cloud dataset replay (up to 500 cases)',
            '14-day trace storage',
            'Basic analytics dashboard',
            'Email support',
        ],
        cta: 'Join Waitlist',
        href: '#waitlist',
        highlighted: true,
    },
    {
        name: 'Team',
        price: '$149',
        interval: '/month',
        description: 'For teams that share datasets, baselines, and collaborate on contracts.',
        features: [
            'Everything in Pro',
            'Up to 10 team members',
            '90-day trace storage',
            'Shared datasets & baselines',
            'Priority support',
        ],
        cta: 'Join Waitlist',
        href: '#waitlist',
        highlighted: false,
    },
    {
        name: 'Enterprise',
        price: 'Custom',
        description: 'For organizations with compliance requirements or custom deployment needs.',
        features: [
            'Everything in Team',
            'Unlimited team members & storage',
            'Self-hosted / VPC deployment',
            'Compliance packs (SOC2, HIPAA)',
            'Dedicated support channel',
        ],
        cta: "Let's Talk",
        href: 'mailto:mohit@phylax.dev',
        highlighted: false,
    },
];

export default function PricingPage() {
    return (
        <>
            <div className="max-w-7xl mx-auto px-6 py-24">
                <div className="text-center max-w-3xl mx-auto mb-20">
                    <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight text-coffee-bean mb-6">
                        Simple, Transparent Pricing
                    </h1>
                    <p className="text-xl text-coffee-bean/70">
                        Start for free with local CI enforcement. Upgrade to Phylax Cloud when your team needs shared datasets, replays, and collaboration.
                    </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
                    {tiers.map((tier) => (
                        <div
                            key={tier.name}
                            className={`flex flex-col p-8 rounded-3xl border ${tier.highlighted
                                ? 'border-lime-cream bg-coffee-bean text-white shadow-2xl relative'
                                : 'border-black/10 bg-white text-coffee-bean hover:border-coffee-bean/20'
                                } transition-all`}
                        >
                            {tier.highlighted && (
                                <div className="absolute -top-4 left-1/2 -translate-x-1/2 bg-lime-cream text-coffee-bean px-4 py-1 rounded-full text-xs font-bold tracking-wider uppercase">
                                    Most Popular
                                </div>
                            )}

                            <h3 className={`text-xl font-bold mb-2 ${tier.highlighted ? 'text-white' : 'text-coffee-bean'}`}>
                                {tier.name}
                            </h3>
                            <div className="flex items-baseline gap-1 mb-4">
                                <span className={`text-4xl font-extrabold ${tier.highlighted ? 'text-lime-cream' : 'text-coffee-bean'}`}>
                                    {tier.price}
                                </span>
                                {tier.interval && (
                                    <span className={`text-sm ${tier.highlighted ? 'text-white/70' : 'text-coffee-bean/60'}`}>
                                        {tier.interval}
                                    </span>
                                )}
                            </div>
                            <p className={`text-sm mb-8 flex-grow ${tier.highlighted ? 'text-white/80' : 'text-coffee-bean/70'}`}>
                                {tier.description}
                            </p>

                            <Link
                                href={tier.href}
                                className={`w-full py-3 rounded-xl font-bold text-sm flex items-center justify-center gap-2 transition-all mb-8 ${tier.highlighted
                                    ? 'bg-lime-cream text-coffee-bean hover:bg-white'
                                    : 'bg-coffee-bean/5 text-coffee-bean hover:bg-coffee-bean hover:text-white'
                                    }`}
                            >
                                {tier.name === 'Open Source' ? (
                                    <span className="font-mono text-xs">{tier.cta}</span>
                                ) : (
                                    <>
                                        {tier.cta} <ArrowRight className="w-4 h-4" />
                                    </>
                                )}
                            </Link>

                            <div className="space-y-4">
                                <p className={`text-sm font-semibold ${tier.highlighted ? 'text-white' : 'text-coffee-bean'}`}>
                                    Includes:
                                </p>
                                <ul className="space-y-3">
                                    {tier.features.map((feature, i) => (
                                        <li key={i} className="flex items-start gap-3">
                                            <Check className={`w-5 h-5 flex-shrink-0 ${tier.highlighted ? 'text-lime-cream' : 'text-coffee-bean/40'}`} />
                                            <span className={`text-sm ${tier.highlighted ? 'text-white/80' : 'text-coffee-bean/80'}`}>
                                                {feature}
                                            </span>
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        </div>
                    ))}
                </div>

                <div className="mt-24 max-w-4xl mx-auto bg-beige/30 rounded-3xl p-8 md:p-12 border border-black/10">
                    <h2 className="text-2xl font-bold text-coffee-bean mb-4">Frequently Asked Questions</h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mt-8">
                        <div>
                            <h4 className="font-bold text-coffee-bean mb-2">Can I use Phylax Open Source in commercial projects?</h4>
                            <p className="text-sm text-coffee-bean/70">Yes. Phylax is licensed under the permissive MIT License. You can use it in any commercial or private project without restrictions.</p>
                        </div>
                        <div>
                            <h4 className="font-bold text-coffee-bean mb-2">What is the Cloud Dataset Replay Engine?</h4>
                            <p className="text-sm text-coffee-bean/70">Our cloud infrastructure allows you to run massive dataset contracts (1,000+ cases) asynchronously in parallel across multiple models, offloading the compute from your CI runners.</p>
                        </div>
                        <div>
                            <h4 className="font-bold text-coffee-bean mb-2">Do you see my API keys?</h4>
                            <p className="text-sm text-coffee-bean/70">No. When using the open-source version, everything runs locally on your machine or CI runner. We never see your API keys or data.</p>
                        </div>
                        <div>
                            <h4 className="font-bold text-coffee-bean mb-2">How stable is the API?</h4>
                            <p className="text-sm text-coffee-bean/70">Phylax hit stable 1.0.0 in January 2026. The core primitives (@trace, @expect, Dataset Contracts) are subject to strict semantic versioning backward compatibility guarantees.</p>
                        </div>
                    </div>
                </div>
            </div>
            <Footer />
        </>
    );
}
