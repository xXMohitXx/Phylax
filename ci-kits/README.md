# CI Integration Kits

Ready-made CI/CD configurations for Phylax. Copy the appropriate config into your project.

## Available Kits

| Platform | File | Setup |
|----------|------|-------|
| **GitHub Actions** | [`github-actions/phylax.yml`](github-actions/phylax.yml) | Copy to `.github/workflows/phylax.yml` |
| **GitLab CI** | [`gitlab-ci/phylax.yml`](gitlab-ci/phylax.yml) | Include in `.gitlab-ci.yml` |
| **Jenkins** | [`jenkins/Jenkinsfile`](jenkins/Jenkinsfile) | Copy to project root |

## Quick Start

### GitHub Actions
```bash
mkdir -p .github/workflows
cp ci-kits/github-actions/phylax.yml .github/workflows/phylax.yml
```

### GitLab CI
```bash
cp ci-kits/gitlab-ci/phylax.yml .gitlab-ci.yml
```

### Jenkins
```bash
cp ci-kits/jenkins/Jenkinsfile Jenkinsfile
```

## Usage

All kits:
1. Install Phylax
2. Run `phylax check` for golden trace enforcement
3. Optionally run `phylax dataset run` for contract testing
4. Exit code `0` = all pass, `1` = failure (blocks merge/deploy)

## Required Secrets

| Secret | Purpose |
|--------|---------|
| `GOOGLE_API_KEY` | Gemini adapter |
| `OPENAI_API_KEY` | OpenAI adapter |
| `GROQ_API_KEY` | Groq adapter |

Set only the secrets for adapters you use.
