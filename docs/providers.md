# Supported Providers

Phylax supports multiple LLM providers via adapters.

## Installation

```bash
# All providers
pip install phylax[all]

# Individual providers
pip install phylax[openai]
pip install phylax[google]
pip install phylax[groq]
pip install phylax[mistral]
pip install phylax[huggingface]
pip install phylax[ollama]
```

---

## OpenAI

```python
from phylax import OpenAIAdapter

adapter = OpenAIAdapter()  # Uses OPENAI_API_KEY
response, trace = adapter.chat_completion(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

| Env Variable | Models |
|--------------|--------|
| `OPENAI_API_KEY` | gpt-4o, gpt-4-turbo, gpt-3.5-turbo |

---

## Google Gemini

```python
from phylax import GeminiAdapter

adapter = GeminiAdapter()  # Uses GOOGLE_API_KEY
response, trace = adapter.generate(
    prompt="Hello!",
    model="gemini-2.5-flash"
)
```

| Env Variable | Models |
|--------------|--------|
| `GOOGLE_API_KEY` | gemini-2.5-flash, gemini-2.5-pro |

> **Note**: Uses `google-genai` SDK (v0.5.0+)

---

## Groq

```python
from phylax import GroqAdapter

adapter = GroqAdapter()  # Uses GROQ_API_KEY
response, trace = adapter.chat_completion(
    model="llama3-70b-8192",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

| Env Variable | Models |
|--------------|--------|
| `GROQ_API_KEY` | llama3-70b-8192, llama3-8b-8192, mixtral-8x7b-32768 |

---

## Mistral

```python
from phylax import MistralAdapter

adapter = MistralAdapter()  # Uses MISTRAL_API_KEY
response, trace = adapter.generate(
    prompt="Hello!",
    model="mistral-large-latest"
)
```

| Env Variable | Models |
|--------------|--------|
| `MISTRAL_API_KEY` | mistral-large-latest, mistral-small-latest, codestral-latest |

---

## HuggingFace

```python
from phylax import HuggingFaceAdapter

adapter = HuggingFaceAdapter()  # Uses HF_TOKEN
response, trace = adapter.generate(
    prompt="Hello!",
    model="meta-llama/Llama-3.1-8B-Instruct"
)
```

| Env Variable | Models |
|--------------|--------|
| `HF_TOKEN` | Any HuggingFace Inference API compatible model |

---

## Ollama (Local)

```python
from phylax import OllamaAdapter

adapter = OllamaAdapter()  # Uses OLLAMA_HOST (default: localhost:11434)
response, trace = adapter.generate(
    prompt="Hello!",
    model="llama3"
)

# List available local models
models = adapter.list_models()
```

| Env Variable | Default |
|--------------|---------|
| `OLLAMA_HOST` | `http://localhost:11434` |

| Models | Description |
|--------|-------------|
| llama3 | Meta Llama 3 |
| mistral | Mistral 7B |
| codellama | Code Llama |
| phi3 | Microsoft Phi-3 |

---

## Common Pattern

All adapters share the same interface:

```python
# chat_completion - standard chat format
response, trace = adapter.chat_completion(
    model="model-name",
    messages=[
        {"role": "system", "content": "You are helpful."},
        {"role": "user", "content": "Hello!"}
    ],
    temperature=0.7,
    max_tokens=256,
)

# generate - simple prompt
response, trace = adapter.generate(
    prompt="Hello!",
    model="model-name"
)
```
