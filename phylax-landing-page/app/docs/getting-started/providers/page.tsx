import React from 'react';
import { CodeBlock } from '@/components/code-block';

const INTERFACE_CODE = `# 1. generate() — string in, string out
response, trace = adapter.generate(
    prompt="Hello!",
    model="model-name",
)

# 2. chat_completion() — standardized messages payload
response, trace = adapter.chat_completion(
    model="model-name",
    messages=[
        {"role": "system", "content": "You are helpful."},
        {"role": "user",   "content": "Hello!"},
    ],
    temperature=0.7,
    max_tokens=256,
)`;

const OPENAI_CODE = `from phylax import OpenAIAdapter

adapter = OpenAIAdapter()  # reads OPENAI_API_KEY from env
response, trace = adapter.chat_completion(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Hello!"}],
)`;

const GEMINI_CODE = `from phylax import GeminiAdapter

adapter = GeminiAdapter()  # reads GOOGLE_API_KEY from env
response, trace = adapter.generate(
    prompt="Hello!",
    model="gemini-2.5-flash",
)`;

const GROQ_CODE = `from phylax import GroqAdapter

adapter = GroqAdapter()  # reads GROQ_API_KEY from env
response, trace = adapter.chat_completion(
    model="llama3-70b-8192",
    messages=[{"role": "user", "content": "Hello!"}],
)`;

const MISTRAL_CODE = `from phylax import MistralAdapter

adapter = MistralAdapter()  # reads MISTRAL_API_KEY from env
response, trace = adapter.generate(
    prompt="Hello!",
    model="mistral-large-latest",
)`;

const OLLAMA_CODE = `from phylax import OllamaAdapter

# Default host: http://localhost:11434
# Set OLLAMA_HOST to override
adapter = OllamaAdapter()

response, trace = adapter.generate(
    prompt="Hello!",
    model="llama3",
)

# List locally installed models
models = adapter.list_models()`;

const HFACE_CODE = `from phylax import HuggingFaceAdapter

adapter = HuggingFaceAdapter()  # reads HF_TOKEN from env
response, trace = adapter.generate(
    prompt="Hello!",
    model="mistralai/Mistral-7B-Instruct-v0.2",
)`;

export default function ProvidersPage() {
    return (
        <div className="flex flex-col gap-6 w-full">
            <h1 className="text-4xl font-extrabold tracking-tight lg:text-5xl mb-2 text-coffee-bean">Providers</h1>
            <p className="text-xl text-coffee-bean/80">
                Phylax supports all major LLM providers out of the box. All adapters share the same standardized interface.
            </p>

            <hr className="my-6 border-black/10" />

            <h2 className="text-2xl font-semibold text-coffee-bean mt-4 mb-4">The Standard Adapter Interface</h2>
            <p className="text-coffee-bean/80 mb-4">
                Every adapter implements two methods: <code>generate()</code> for simple string prompts and <code>chat_completion()</code> for message arrays.
            </p>
            <CodeBlock language="python" title="interface.py" code={INTERFACE_CODE} />

            <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">OpenAI</h2>
            <CodeBlock language="python" title="openai_example.py" code={OPENAI_CODE} />
            <ul className="list-disc ml-6 mt-2 text-coffee-bean/80">
                <li><strong>Install:</strong> <code>pip install phylax[openai]</code></li>
                <li><strong>Env:</strong> <code>OPENAI_API_KEY</code></li>
                <li><strong>Models:</strong> gpt-4o, gpt-4-turbo, gpt-3.5-turbo</li>
            </ul>

            <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Google Gemini</h2>
            <p className="text-coffee-bean/80 text-sm mb-3">Uses the <code>google-genai</code> SDK v0.5.0+</p>
            <CodeBlock language="python" title="gemini_example.py" code={GEMINI_CODE} />
            <ul className="list-disc ml-6 mt-2 text-coffee-bean/80">
                <li><strong>Install:</strong> <code>pip install phylax[google]</code></li>
                <li><strong>Env:</strong> <code>GOOGLE_API_KEY</code></li>
                <li><strong>Models:</strong> gemini-2.5-flash, gemini-2.5-pro</li>
            </ul>

            <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Groq</h2>
            <CodeBlock language="python" title="groq_example.py" code={GROQ_CODE} />
            <ul className="list-disc ml-6 mt-2 text-coffee-bean/80">
                <li><strong>Install:</strong> <code>pip install phylax[groq]</code></li>
                <li><strong>Env:</strong> <code>GROQ_API_KEY</code></li>
            </ul>

            <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Mistral</h2>
            <CodeBlock language="python" title="mistral_example.py" code={MISTRAL_CODE} />
            <ul className="list-disc ml-6 mt-2 text-coffee-bean/80">
                <li><strong>Install:</strong> <code>pip install phylax[mistral]</code></li>
                <li><strong>Env:</strong> <code>MISTRAL_API_KEY</code></li>
            </ul>

            <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">Ollama (Local)</h2>
            <CodeBlock language="python" title="ollama_example.py" code={OLLAMA_CODE} />
            <ul className="list-disc ml-6 mt-2 text-coffee-bean/80 mb-4">
                <li><strong>Install:</strong> <code>pip install phylax[ollama]</code></li>
                <li><strong>Env:</strong> <code>OLLAMA_HOST=http://localhost:11434</code></li>
            </ul>

            <h2 className="text-2xl font-semibold text-coffee-bean mt-8 mb-4">HuggingFace</h2>
            <CodeBlock language="python" title="huggingface_example.py" code={HFACE_CODE} />
            <ul className="list-disc ml-6 mt-2 text-coffee-bean/80">
                <li><strong>Install:</strong> <code>pip install phylax[huggingface]</code></li>
                <li><strong>Env:</strong> <code>HF_TOKEN</code></li>
            </ul>
        </div>
    );
}
