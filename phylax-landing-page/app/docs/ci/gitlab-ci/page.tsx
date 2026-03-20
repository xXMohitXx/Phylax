import React from 'react';
import { CodeBlock } from '@/components/code-block';

const GITLAB_YAML = `stages:
  - test
  - evaluate_ai

evaluate_llm_models:
  stage: evaluate_ai
  image: python:3.11

  before_script:
    - pip install -r requirements.txt
    - pip install phylax[all]

  script:
    - export PHYLAX_MODE="enforce"
    - python run_ai_evals.py

  artifacts:
    when: always
    paths:
      - phylax_artifacts/*.json
      - phylax_ledger.jsonl
    expire_in: 30 days`;

const ENV_CODE = `# .env (never commit this)
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=AIza...

# Set enforcement mode per environment
PHYLAX_MODE=enforce        # blocks CI on failure
# PHYLAX_MODE=observe      # logs but never blocks
# PHYLAX_MODE=quarantine   # isolates failures from production`;

export default function GitlabCiPage() {
    return (
        <div className="flex flex-col gap-6 w-full">
            <h1 className="text-4xl font-extrabold tracking-tight lg:text-5xl mb-2 text-coffee-bean">GitLab CI</h1>
            <p className="text-xl text-coffee-bean/80">
                Integrate Phylax evaluation gates into your GitLab pipelines.
            </p>

            <hr className="my-6 border-black/10" />

            <h2 className="text-2xl font-semibold text-coffee-bean mt-4 mb-4">Pipeline Configuration</h2>
            <p className="text-coffee-bean/80 mb-4">
                GitLab CI runners natively respect POSIX exit codes. When Phylax exits with code <code>1</code> (enforcement mode failure), the pipeline job registers as failed and blocks the merge.
            </p>

            <CodeBlock language="yaml" title=".gitlab-ci.yml" code={GITLAB_YAML} />

            <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Environment Variables</h2>
            <CodeBlock language="bash" title=".env" code={ENV_CODE} />

            <div className="bg-beige/40 border border-coffee-bean/10 rounded-lg p-6 mt-6 mb-6">
                <h3 className="text-lg font-semibold text-coffee-bean mb-2">Managing Ledgers</h3>
                <p className="text-coffee-bean/80">
                    The evaluation ledger (Axis 3) is append-only. Use GitLab&apos;s artifact caching to continuously build a ledger file across commits, accumulating historical failure rate data over time.
                </p>
            </div>
        </div>
    );
}
