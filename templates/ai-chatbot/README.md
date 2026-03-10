# AI Chatbot Template

A ready-to-use Phylax starter template for AI chatbots.

## What's Included

| File | Purpose |
|------|---------|
| `app.py` | Chatbot with safety contracts |
| `contracts.yaml` | Dataset contract for batch testing |
| `.github/workflows/phylax.yml` | CI configuration |

## Quick Start

```bash
# 1. Copy this template
cp -r templates/ai-chatbot my-chatbot
cd my-chatbot

# 2. Install Phylax
pip install phylax[openai]

# 3. Set your API key
export OPENAI_API_KEY="your-key"

# 4. Run
python app.py

# 5. Enforce in CI
phylax check
```
