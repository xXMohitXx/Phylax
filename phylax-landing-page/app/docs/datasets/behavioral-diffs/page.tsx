import React from 'react';
import { CodeBlock } from '@/components/code-block';

const DIFF_CODE = `from phylax import diff_runs, format_diff_report

# Two dataset results (before and after a model change or prompt edit)
diff = diff_runs(result_before, result_after)

print(f"New failures:  {diff.new_failures}")
print(f"Fixed cases:   {diff.new_passes}")
print(f"Regressions:   {diff.has_regressions}")

# Human-readable diff report
print(format_diff_report(diff))`;

const JSON_DIFF_CODE = `from phylax import format_diff_json

# Machine-consumable JSON diff for dashboards or CI artifact storage
json_diff = format_diff_json(diff)
# {
#   "new_failures": [...],
#   "new_passes": [...],
#   "has_regressions": true
# }`;

export default function BehavioralDiffsPage() {
    return (
        <div className="flex flex-col gap-6 w-full">
            <h1 className="text-4xl font-extrabold tracking-tight lg:text-5xl mb-2 text-coffee-bean">Behavioral Diffs</h1>
            <p className="text-xl text-coffee-bean/80">
                Compare two dataset runs to detect behavioral changes between model versions, prompt edits, or config changes.
            </p>

            <hr className="my-6 border-black/10" />

            <h2 className="text-2xl font-semibold text-coffee-bean mt-4 mb-4">The Diff Engine</h2>
            <p className="text-coffee-bean/80 mb-4">
                <code>diff_runs()</code> takes two <code>DatasetResult</code> objects and compares them case-by-case. It produces a <code>DatasetDiff</code> object — a strict, deterministic accounting of what changed.
            </p>

            <div className="bg-beige/40 border border-coffee-bean/10 rounded-lg p-6 mb-6">
                <ul className="space-y-3 text-coffee-bean/80">
                    <li><strong><code>new_failures</code></strong> — Cases that passed before but fail now (regressions).</li>
                    <li><strong><code>new_passes</code></strong> — Cases that failed before but now pass (fixes).</li>
                    <li><strong><code>has_regressions</code></strong> — Boolean: <code>True</code> if any new failures were introduced.</li>
                    <li><strong><code>stable_failures</code></strong> — Cases that failed in both runs (known issues).</li>
                    <li><strong><code>stable_passes</code></strong> — Cases that passed in both runs (unchanged behavior).</li>
                </ul>
            </div>

            <CodeBlock language="python" title="diff_engine.py" code={DIFF_CODE} />

            <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Machine-Consumable Output</h2>
            <CodeBlock language="python" title="diff_json.py" code={JSON_DIFF_CODE} />

            <div className="bg-beige/40 border border-coffee-bean/10 rounded-lg p-6 mt-6">
                <h3 className="text-lg font-semibold text-coffee-bean mb-2">Zero-Tolerance Rule</h3>
                <p className="text-coffee-bean/80">
                    Phylax does not perform &quot;directional improvement&quot; balancing. Even if 10 cases improved, a single new regression causes <code>has_regressions</code> to be <code>True</code> and CI to block the merge.
                </p>
            </div>
        </div>
    );
}
