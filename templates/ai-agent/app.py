"""
AI Agent Template — Multi-step agent with compliance enforcement.

Features:
    - Compliance guardrails (no financial/medical/legal advice)
    - Execution context tracking
    - Model upgrade simulation

Usage:
    pip install phylax
    python app.py
"""
from phylax import (
    trace, expect, execution,
    compliance_pack,
    Dataset, DatasetCase, simulate_upgrade,
    format_simulation_report,
)


_compliance = compliance_pack().to_expectations()


@trace(provider="mock")
@expect(**_compliance)
def agent_think(query: str) -> str:
    """Agent reasoning step with compliance enforcement."""
    return (
        f"Analyzing the query about '{query}'. Based on available "
        f"information, I can provide general guidance. For specific "
        f"professional advice, please consult a qualified expert."
    )


@trace(provider="mock")
@expect(**_compliance)
def agent_respond(thought: str) -> str:
    """Agent response step with compliance enforcement."""
    return (
        f"Based on my analysis: {thought[:30]}... "
        f"Here are the key considerations for this topic. "
        f"Please review and let me know if you need more details."
    )


def main():
    print("=== AI Agent with Compliance Enforcement ===\n")

    with execution():
        thought = agent_think("help with my project")
        response = agent_respond(thought)
        print(f"Response: {response[:80]}...\n")

    print("✅ Agent passed compliance checks!")


if __name__ == "__main__":
    main()
