"""
AI Chatbot Template — Ready-to-use Phylax starter.

This template includes:
    - A chatbot with safety contracts
    - Dataset contract YAML for batch testing
    - GitHub Actions CI configuration

Usage:
    1. Copy this template to your project
    2. Set your API key
    3. Run: python app.py
    4. CI: phylax check
"""
from phylax import trace, expect

@trace(provider="openai")
@expect(
    must_not_include=["I cannot", "as an AI"],
    max_latency_ms=5000,
)
def chat(user_message: str) -> str:
    """Process a chat message with enforced contracts."""
    # Replace with your LLM call:
    #   from phylax import OpenAIAdapter
    #   adapter = OpenAIAdapter()
    #   response, _ = adapter.generate(prompt=user_message)
    #   return response
    return f"Thanks for your message! I'll help you with: {user_message}"

if __name__ == "__main__":
    response = chat("How do I reset my password?")
    print(f"Bot: {response}")
    print("\n✅ Run 'phylax check' to enforce this in CI.")
