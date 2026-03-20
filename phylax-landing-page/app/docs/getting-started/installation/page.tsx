import React from 'react';
import { CodeBlock } from '@/components/code-block';

const MINIMAL_CODE = `# Core engine only (no providers, no UI server)
pip install phylax

# Core + specific provider
pip install "phylax[openai]"
pip install "phylax[google]"
pip install "phylax[groq]"
pip install "phylax[mistral]"
pip install "phylax[huggingface]"
pip install "phylax[ollama]"

# Core + UI Server
pip install "phylax[server]"`;

export default function InstallationPage() {
    return (
        <div className="flex flex-col gap-6 w-full">
            <h1 className="text-4xl font-extrabold tracking-tight lg:text-5xl mb-2 text-coffee-bean">Installation</h1>
            <p className="text-xl text-coffee-bean/80">
                Phylax requires Python 3.10+ and supports all major operating systems.
            </p>

            <hr className="my-6 border-black/10" />

            <h2 className="text-2xl font-semibold text-coffee-bean mt-4 mb-4">Install via pip</h2>
            <p className="text-coffee-bean/80 mb-4">
                Install Phylax with all optional dependencies — all model providers and the UI server:
            </p>
            <CodeBlock language="bash" title="Terminal" code={`pip install phylax[all]`} />

            <h2 className="text-xl font-semibold text-coffee-bean mt-8 mb-4">Minimal Installation</h2>
            <p className="text-coffee-bean/80 mb-4">
                For lightweight CI environments or Docker containers, install the core engine and select only the adapters you need:
            </p>
            <CodeBlock language="bash" title="Terminal" code={MINIMAL_CODE} />

            <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Verify Installation</h2>
            <p className="text-coffee-bean/80 mb-4">
                Ensure the CLI is accessible. You should see the current version (v1.6.4).
            </p>
            <CodeBlock language="bash" title="Terminal" code={`phylax --version`} />

            <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Next Steps</h2>
            <p className="text-coffee-bean/80 mb-4">
                Phylax is installed — head to the Quickstart to run your first expectation.
            </p>
            <a href="/docs/getting-started/quickstart" className="inline-block mt-2 px-4 py-2 bg-coffee-bean text-lime-cream rounded-md font-medium w-max hover:bg-coffee-bean/90 transition-colors">
                Go to Quickstart →
            </a>
        </div>
    );
}
