"""
Support Bot — Production Template with Phylax Enforcement

This is a production-ready support bot template that demonstrates:
    - @trace/@expect decorators for individual call tracing
    - Safety guardrail packs (blocks PII, hate speech, jailbreaks)
    - Dataset contracts for batch behavioral testing
    - Execution graphs for multi-step workflow tracking

Run:
    pip install phylax
    python app.py
"""
from phylax import (
    trace, expect, execution,
    safety_pack, quality_pack, apply_pack,
    Dataset, DatasetCase, run_dataset,
    format_report, load_dataset,
)


# Apply safety + quality guardrails
_safety = safety_pack()
_quality = quality_pack()
_safety_rules = _safety.to_expectations()
_quality_rules = _quality.to_expectations()
_combined_rules = apply_pack(_quality, _safety_rules)


# ============================================================
# HANDLERS — Each handler is traced with behavioral contracts
# ============================================================

@trace(provider="mock")
@expect(**_combined_rules, must_include=["refund"])
def handle_refund(message: str) -> str:
    """Handle refund requests. Must mention refund policy."""
    return (
        "I'd be happy to help with your refund request. Our refund_policy allows "
        "returns within 30_days of purchase. Please provide your order number and "
        "I'll process your refund within 24 hours."
    )


@trace(provider="mock")
@expect(**_combined_rules, must_include=["password"])
def handle_password_reset(message: str) -> str:
    """Handle password reset requests."""
    return (
        "To reset your password, click the 'Forgot password' link on the login page. "
        "You'll receive a password reset email within 5 minutes. If you don't see it, "
        "check your spam folder."
    )


@trace(provider="mock")
@expect(**_combined_rules, must_include=["cancel"])
def handle_cancellation(message: str) -> str:
    """Handle subscription cancellation requests."""
    return (
        "I can help you cancel your subscription. Please note that your cancel request "
        "will take effect at the end of your current billing period. You'll receive a "
        "confirmation email once the cancellation is processed."
    )


@trace(provider="mock")
@expect(**_combined_rules)
def handle_general(message: str) -> str:
    """Handle general inquiries with safety guardrails."""
    return (
        "Thank you for reaching out to our support team. A qualified agent will "
        "review your inquiry and respond within 24 hours. In the meantime, you "
        "can check our help center for common questions."
    )


def route_message(message: str) -> str:
    """Route messages to the appropriate handler."""
    msg_lower = message.lower()
    if any(word in msg_lower for word in ["refund", "money back", "return"]):
        return handle_refund(message)
    elif any(word in msg_lower for word in ["password", "login", "sign in"]):
        return handle_password_reset(message)
    elif any(word in msg_lower for word in ["cancel", "unsubscribe", "stop"]):
        return handle_cancellation(message)
    else:
        return handle_general(message)


# ============================================================
# MAIN — Demonstrates tracing + dataset contracts
# ============================================================

def main():
    print("=" * 60)
    print("SUPPORT BOT — Phylax Enforced Template")
    print("=" * 60)
    print(f"\nSafety rules: {len(_safety.rules)} | Quality rules: {len(_quality.rules)}\n")

    # 1. Live execution with tracing
    print("--- Live Execution ---")
    with execution() as exec_id:
        r1 = route_message("I want a refund for order #456")
        print(f"  Refund:   {r1[:70]}...")

        r2 = route_message("I forgot my password")
        print(f"  Password: {r2[:70]}...")

        r3 = route_message("Cancel my subscription")
        print(f"  Cancel:   {r3[:70]}...")

    # 2. Dataset contract execution
    print("\n--- Dataset Contract ---")
    try:
        ds = load_dataset("dataset.yaml")
        result = run_dataset(ds, route_message)
        print(format_report(result))
    except FileNotFoundError:
        print("  dataset.yaml not found. Run: phylax dataset run dataset.yaml")

    print("\nDone. Run 'phylax server' to inspect traces in the UI.")


if __name__ == "__main__":
    main()
