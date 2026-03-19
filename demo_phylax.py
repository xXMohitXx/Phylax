"""
demo_phylax.py

A root-level staging ground for testing out Phylax features.
"""

from phylax import trace, expect, execution, Dataset, DatasetCase

# Guardrail Setup
_rules = {"must_include": ["safe", "authorized"], "min_tokens": 5}

@trace(provider="mock")
@expect(**_rules)
def test_agent_call(prompt: str) -> str:
    """Mock agent call with validation."""
    return f"This is a safe and authorized response to '{prompt}'."

def main():
    print("=== Phylax Validation Demo ===")
    
    with execution():
        result = test_agent_call("Hello World")
        print(f"Result: {result}")

if __name__ == "__main__":
    main()
