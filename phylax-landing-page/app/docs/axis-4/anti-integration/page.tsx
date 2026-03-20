import React from 'react';
import { CodeBlock } from '@/components/code-block';

const BASH_CODE = `# Phylax outputs verdict.json and exits with the correct code
python run_evals.py > verdict.json
EXIT_CODE=$?

# You build the ecosystem around Phylax's clean output
if [ $EXIT_CODE -eq 1 ]; then
    ./notify_slack.sh "AI regression detected!"
    ./upload_to_datadog.sh verdict.json
    exit 1
fi`;

const BANNED_CODE = `# From tests/test_axis4_integrity.py — runs in Phylax's own CI
# This scan will FAIL THE BUILD if any of these are found in phylax source:

BANNED_IMPORTS = [
    "requests.post",   # No outbound telemetry
    "import flask",    # No embedded web servers
    "import jinja2",   # No UI rendering
    "smtplib",         # No email sending
    "import matplotlib",
    "import plotly",
]

BANNED_IDIOMS = [
    "daemon",           # No background services
    "threading.Timer",  # No scheduled tasks
    "asyncio.run",      # No autonomous event loops
]`;

const EXIT_CODE = `from phylax import resolve_exit_code, EXIT_PASS, EXIT_FAIL, EXIT_SYSTEM_ERROR

# In enforce mode: FAIL verdict → exit 1
code = resolve_exit_code(verdict="FAIL", mode="enforce")
print(code)   # 1  (== EXIT_FAIL)

# In observe or quarantine mode: always exit 0
code = resolve_exit_code(verdict="FAIL", mode="observe")
print(code)   # 0  (== EXIT_PASS)`;

export default function AntiIntegrationPage() {
    return (
        <div className="flex flex-col gap-6 w-full">
            <h1 className="text-4xl font-extrabold tracking-tight lg:text-5xl mb-2 text-coffee-bean">Anti-Integration Fortress</h1>
            <p className="text-xl text-coffee-bean/80">
                Phylax is a library, not a platform. The core engine has a strict constitutional boundary against ecosystem features.
            </p>

            <hr className="my-6 border-black/10" />

            <h2 className="text-2xl font-semibold text-coffee-bean mt-4 mb-4">The Constitutional Boundary</h2>
            <p className="text-coffee-bean/80 mb-4">
                Axis 4 represents Phylax&apos;s most intentional architectural decision: <strong>the core engine will never build ecosystem features.</strong>
            </p>
            <p className="text-coffee-bean/80 mb-4">
                Phylax&apos;s own CI suite programmatically scans the library&apos;s source code AST to forbid platform bloat. If a contributor adds network syncing or a webhook, the CI build crashes.
            </p>

            <div className="bg-beige/40 border border-coffee-bean/10 rounded-lg p-6 mb-6">
                <h3 className="text-lg font-semibold text-coffee-bean mb-2">Explicitly Banned Behaviors</h3>
                <ul className="space-y-4 text-coffee-bean/80">
                    <li><strong>Outbound Telemetry & Cloud Sync:</strong> No <code>requests.post</code> or API clients calling home.</li>
                    <li><strong>Dashboards & UI:</strong> No embedded Flask, React, or Jinja2 visualizers.</li>
                    <li><strong>Alerting:</strong> No Slack implementations, emailers, or webhooks inside the core.</li>
                    <li><strong>AI Inference:</strong> Phylax will never use an LLM to explain <em>why</em> an expectation failed.</li>
                </ul>
            </div>

            <CodeBlock language="python" title="anti_integration_test.py" code={BANNED_CODE} />

            <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Building Your Ecosystem</h2>
            <p className="text-coffee-bean/80 mb-4">
                Phylax&apos;s job ends when your evaluation script writes <code>verdict.json</code> and exits with a code. From there, you own the pipeline:
            </p>

            <CodeBlock language="bash" title="ci_pipeline.sh" code={BASH_CODE} />

            <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Exit Codes</h2>
            <p className="text-coffee-bean/80 mb-4">
                Use <code>resolve_exit_code(verdict, mode)</code> to map Phylax verdicts to OS exit codes in your scripts:
            </p>
            <CodeBlock language="python" title="exit_codes.py" code={EXIT_CODE} />

            <p className="text-coffee-bean/80 mt-4">
                Want Slack alerts? Write a shell script that checks <code>$EXIT_CODE</code>. Want a dashboard? Pipe the <code>.jsonl</code> ledger into Datadog, Grafana, or any telemetry system. The separation is intentional and permanent.
            </p>
        </div>
    );
}
