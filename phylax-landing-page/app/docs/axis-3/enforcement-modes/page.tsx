import React from 'react';
import { CodeBlock } from '@/components/code-block';

const MODE_CODE = `from phylax import ModeHandler

# Set via PHYLAX_MODE env variable, or passed explicitly
handler = ModeHandler("quarantine")

result = handler.apply("fail")
print(result.verdict)    # "fail"
print(result.exit_code)  # 0 — quarantine mode never blocks CI`;

export default function EnforcementModesPage() {
    return (
        <div className="flex flex-col gap-6 w-full">
            <h1 className="text-4xl font-extrabold tracking-tight lg:text-5xl mb-2 text-coffee-bean">Enforcement Modes</h1>
            <p className="text-xl text-coffee-bean/80">
                Safely onboard Phylax to existing systems using observe, quarantine, and enforce modes.
            </p>

            <hr className="my-6 border-black/10" />

            <h2 className="text-2xl font-semibold text-coffee-bean mt-4 mb-4">The Three Modes</h2>
            <p className="text-coffee-bean/80 mb-4">
                Phylax has exactly three valid execution modes. There are no &quot;auto-escalating&quot; or &quot;smart&quot; modes.
            </p>

            <div className="overflow-x-auto mb-6">
                <table className="w-full text-sm border-collapse">
                    <thead><tr className="border-b border-black/10">
                        <th className="text-left py-3 pr-4 font-semibold text-coffee-bean">Mode</th>
                        <th className="text-left py-3 pr-4 font-semibold text-coffee-bean">Exit Code on Fail</th>
                        <th className="text-left py-3 font-semibold text-coffee-bean">Use Case</th>
                    </tr></thead>
                    <tbody className="text-coffee-bean/80">
                        <tr className="border-b border-black/5"><td className="py-3 pr-4"><code>observe</code></td><td className="py-3 pr-4"><code>0</code></td><td className="py-3">Safe integration — traces without blocking CI</td></tr>
                        <tr className="border-b border-black/5"><td className="py-3 pr-4"><code>quarantine</code></td><td className="py-3 pr-4"><code>0</code></td><td className="py-3">Logs violations & writes artifacts, never blocks</td></tr>
                        <tr><td className="py-3 pr-4"><code>enforce</code></td><td className="py-3 pr-4"><code>1</code></td><td className="py-3">Production gate — blocks PRs and deployments on fail</td></tr>
                    </tbody>
                </table>
            </div>

            <CodeBlock language="python" title="mode_handler.py" code={MODE_CODE} />

            <div className="bg-beige/40 border border-coffee-bean/10 rounded-lg p-6 mt-6 mb-6">
                <h3 className="text-lg font-semibold text-coffee-bean mb-2">The Mode Invariant</h3>
                <p className="text-coffee-bean/80">
                    The exact same LLM output evaluated under <code>observe</code> and <code>enforce</code> produces identical trace hashes, identical metrics, and identical <code>pass/fail</code> verdicts. The <strong>only</strong> difference is the final OS exit code behavior.
                </p>
            </div>
        </div>
    );
}
