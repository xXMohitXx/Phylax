import React from 'react';
import { CodeBlock } from '@/components/code-block';

const JENKINSFILE = `pipeline {
  agent any

  environment {
    OPENAI_API_KEY = credentials('openai-prod-key')
    PHYLAX_MODE = 'enforce'
  }

  stages {
    stage('Unit Tests') {
      steps {
        sh 'pytest tests/'
      }
    }

    stage('AI Semantic Evaluation') {
      steps {
        sh """
          python3 -m venv venv
          . venv/bin/activate
          pip install phylax -r requirements.txt

          # Exits 1 if regressions are found, failing the build
          python evaluate_production_models.py
        """
      }
    }
  }

  post {
    always {
      archiveArtifacts artifacts: 'verdict.json, ledger.jsonl', allowEmptyArchive: true
    }
  }
}`;

export default function JenkinsPage() {
    return (
        <div className="flex flex-col gap-6 w-full">
            <h1 className="text-4xl font-extrabold tracking-tight lg:text-5xl mb-2 text-coffee-bean">Jenkins Integration</h1>
            <p className="text-xl text-coffee-bean/80">
                Add AI guardrail checks to your Jenkins automation pipelines.
            </p>

            <hr className="my-6 border-black/10" />

            <h2 className="text-2xl font-semibold text-coffee-bean mt-4 mb-4">Jenkinsfile Definition</h2>
            <p className="text-coffee-bean/80 mb-4">
                Jenkins stages halt on non-zero exit codes. Phylax is designed to integrate cleanly — a failure in <code>enforce</code> mode exits with code <code>1</code>, immediately blocking the stage and preventing deployment.
            </p>

            <CodeBlock language="groovy" title="Jenkinsfile" code={JENKINSFILE} />

            <div className="bg-beige/40 border border-coffee-bean/10 rounded-lg p-6 mt-6">
                <h3 className="text-lg font-semibold text-coffee-bean mb-2">Artifact Archiving</h3>
                <p className="text-coffee-bean/80">
                    The <code>post.always</code> block archives <code>verdict.json</code> and <code>ledger.jsonl</code> even on failed builds. This lets you inspect exactly which contracts were violated and ingest the ledger into dashboards.
                </p>
            </div>
        </div>
    );
}
