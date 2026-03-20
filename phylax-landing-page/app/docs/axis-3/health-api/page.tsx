import React from 'react';
import { CodeBlock } from '@/components/code-block';

const HEALTH_CODE = `from phylax import HealthReport, aggregate

# Load entries from the ledger and aggregate
metrics = aggregate(entries, "exp-custom-1")
report = HealthReport.from_aggregate(metrics, "definition_sha256...")

print(report.total_evaluations)  # e.g. 50
print(report.total_failures)     # e.g. 3
print(report.failure_rate)       # e.g. 0.06
print(report.never_failed)       # True if failure_rate == 0.0
print(report.never_passed)       # True if failure_rate == 1.0`;

const COVERAGE_CODE = `from phylax import CoverageReport

# 100 expectations declared in code, only 45 were evaluated during this CI run
report = CoverageReport.compute(
    total_declared=100,
    evaluated_ids={"exp-1", "exp-2", ...},  # Set of 45 IDs
)

print(report.coverage_ratio)  # 0.45`;

export default function HealthApiPage() {
    return (
        <div className="flex flex-col gap-6 w-full">
            <h1 className="text-4xl font-extrabold tracking-tight lg:text-5xl mb-2 text-coffee-bean">Health API</h1>
            <p className="text-xl text-coffee-bean/80">
                Factual, objective reporting of failure rates and system coverage.
            </p>

            <hr className="my-6 border-black/10" />

            <h2 className="text-2xl font-semibold text-coffee-bean mt-4 mb-4">Health Reports</h2>
            <p className="text-coffee-bean/80 mb-4">
                A <code>HealthReport</code> is derived from <code>AggregateMetrics</code>. It provides the exact mathematical reality of an expectation&apos;s performance over time.
            </p>

            <CodeBlock language="python" title="health_report.py" code={HEALTH_CODE} />

            <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Coverage Reporting</h2>
            <p className="text-coffee-bean/80 mb-4">
                <code>CoverageReport</code> calculates what percentage of your declared test suite was actually evaluated during a run. This is critical for verifying that conditional scopes didn&apos;t accidentally bypass all tests.
            </p>

            <CodeBlock language="python" title="coverage.py" code={COVERAGE_CODE} />

            <div className="bg-beige/40 border border-coffee-bean/10 rounded-lg p-6 mt-6 mb-6">
                <h3 className="text-lg font-semibold text-coffee-bean mb-2">No Smoothing Allowed</h3>
                <p className="text-coffee-bean/80">
                    By design, the Health API does not perform statistical smoothing, moving averages, or confidence interval calculations. If an expectation failed 3 out of 10 times, the <code>failure_rate</code> is exactly <code>0.3</code>.
                </p>
            </div>
        </div>
    );
}
