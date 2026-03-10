"""
AI Agent Template — Ready-to-use Phylax starter for multi-step agents.

This template includes:
    - Multi-step agent with execution graph tracking
    - Per-step safety contracts
    - GitHub Actions CI configuration

Usage:
    1. Copy this template to your project
    2. Set your API key
    3. Run: python app.py
    4. CI: phylax check
"""
from phylax import trace, expect, execution

@trace(provider="openai")
@expect(must_include=["intent"], max_latency_ms=2000)
def plan(user_input: str) -> str:
    """Step 1: Plan the agent's action."""
    return f"intent: help_user — Analyzing request: {user_input}"

@trace(provider="openai")
@expect(must_include=["result"], max_latency_ms=5000)
def execute_action(plan: str) -> str:
    """Step 2: Execute the planned action."""
    return f"result: Action completed successfully for plan: {plan[:30]}"

@trace(provider="openai")
@expect(must_not_include=["error", "failed"], max_latency_ms=3000, min_tokens=20)
def format_response(action_result: str) -> str:
    """Step 3: Format the final response."""
    return (
        "I've completed your request. Here's a summary of what was done: "
        "your query was analyzed, the appropriate action was taken, and "
        "the task has been completed successfully."
    )

def run_agent(user_input: str) -> str:
    """Run the full agent pipeline with execution tracking."""
    with execution() as exec_id:
        step1 = plan(user_input)
        step2 = execute_action(step1)
        step3 = format_response(step2)
        return step3

if __name__ == "__main__":
    response = run_agent("Help me write a report")
    print(f"Agent: {response}")
    print("\n✅ Run 'phylax check' to enforce all agent steps in CI.")
