"""
Demo 23: Model Upgrade Simulator
=================================
Safely test model upgrades before deploying to production.

Features demonstrated:
    - simulate_upgrade() with baseline + candidate functions
    - safe_to_upgrade property
    - format_simulation_report() console output
    - Custom model names
"""
from phylax import (
    Dataset,
    DatasetCase,
    simulate_upgrade,
    format_simulation_report,
)


def gpt4_handler(input_text: str) -> str:
    """Simulated GPT-4 handler (baseline)."""
    return (
        f"Based on your question about '{input_text}', here is a comprehensive "
        f"response. This topic involves several important considerations that "
        f"I'll outline for you with supporting details."
    )


def gpt45_handler(input_text: str) -> str:
    """Simulated GPT-4.5 handler (candidate) — improved responses."""
    return (
        f"Regarding '{input_text}': After thorough analysis, here are the key "
        f"insights. This is a nuanced topic that requires careful consideration "
        f"of multiple factors. I've structured my response to address each "
        f"aspect comprehensively."
    )


def main():
    print("=" * 60)
    print("Demo 23: Model Upgrade Simulator")
    print("=" * 60)

    # Define behavior contracts
    ds = Dataset(dataset="model_comparison", cases=[
        DatasetCase(
            input="Explain quantum computing",
            name="quantum",
            expectations={"min_tokens": 15, "must_include": ["question", "response"]},
        ),
        DatasetCase(
            input="What is machine learning?",
            name="ml_basics",
            expectations={"min_tokens": 15, "must_include": ["question"]},
        ),
        DatasetCase(
            input="How do neural networks work?",
            name="neural_nets",
            expectations={"min_tokens": 15},
        ),
    ])

    # Simulate the upgrade
    sim = simulate_upgrade(
        dataset=ds,
        baseline_func=gpt4_handler,
        candidate_func=gpt45_handler,
        baseline_name="GPT-4",
        candidate_name="GPT-4.5",
    )

    # Show results
    print(format_simulation_report(sim))

    # Programmatic access
    print(f"Baseline pass rate: {sim.baseline_result.passed_cases}/{sim.baseline_result.total_cases}")
    print(f"Candidate pass rate: {sim.candidate_result.passed_cases}/{sim.candidate_result.total_cases}")
    print(f"Safe to upgrade: {sim.safe_to_upgrade}")


if __name__ == "__main__":
    main()
