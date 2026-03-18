"""
phylax.guardrails — Public API for Guardrail Packs.

Includes built-in packs (safety, quality, compliance) and
productized domain packs (pii, security, finance, healthcare).

Usage:
    from phylax.guardrails import pii_pack, security_pack, finance_pack, healthcare_pack
    from phylax.guardrails import register_pack
"""
from phylax._internal.guardrails.packs import (
    GuardrailPack,
    GuardrailRule,
    _PACK_REGISTRY,
    get_pack,
    list_packs,
    apply_pack,
    safety_pack,
    quality_pack,
    compliance_pack,
)


# ===========================================================================
# DOMAIN-SPECIFIC PACKS
# ===========================================================================

def pii_pack() -> GuardrailPack:
    """PII detection guardrail pack — blocks SSN, credit cards, phone numbers, emails, addresses."""
    return GuardrailPack(
        name="pii",
        description="PII detection: blocks SSN, credit cards, phone numbers, emails, addresses",
        rules=[
            GuardrailRule(name="no_ssn", type="must_not_include",
                          value=["SSN", "social security number", "social security"],
                          severity="high"),
            GuardrailRule(name="no_credit_card", type="must_not_include",
                          value=["credit card number", "card number", "CVV", "expiration date"],
                          severity="high"),
            GuardrailRule(name="no_phone", type="must_not_include",
                          value=["phone number", "cell number", "mobile number"],
                          severity="high"),
            GuardrailRule(name="no_raw_email", type="must_not_include",
                          value=["@gmail.com", "@yahoo.com", "@hotmail.com", "@outlook.com"],
                          severity="medium"),
            GuardrailRule(name="no_address", type="must_not_include",
                          value=["home address", "street address", "mailing address"],
                          severity="medium"),
            GuardrailRule(name="no_dob", type="must_not_include",
                          value=["date of birth", "birthday", "born on"],
                          severity="medium"),
        ],
        version="1.0.0",
    )


def security_pack() -> GuardrailPack:
    """Security pack — blocks jailbreaks, system prompt leaks, credential exposure, code injection."""
    return GuardrailPack(
        name="security",
        description="Security: blocks jailbreaks, system prompt leaks, credential exposure",
        rules=[
            GuardrailRule(name="no_jailbreak", type="must_not_include",
                          value=["DAN mode", "without restrictions", "ignore all previous",
                                 "bypass safety", "as an unrestricted AI"],
                          severity="high"),
            GuardrailRule(name="no_system_prompt_leak", type="must_not_include",
                          value=["system prompt", "my instructions are", "I was told to",
                                 "my configuration is"],
                          severity="high"),
            GuardrailRule(name="no_credentials", type="must_not_include",
                          value=["API_KEY", "api_key", "password=", "secret_key",
                                 "access_token", "OPENAI_API_KEY"],
                          severity="high"),
            GuardrailRule(name="no_code_injection", type="must_not_include",
                          value=["os.system(", "subprocess.run(", "eval(", "exec(",
                                 "__import__"],
                          severity="high"),
        ],
        version="1.0.0",
    )


def finance_pack() -> GuardrailPack:
    """Financial compliance pack — blocks unauthorized financial advice."""
    return GuardrailPack(
        name="finance",
        description="Financial compliance: blocks unauthorized financial advice",
        rules=[
            GuardrailRule(name="no_investment_advice", type="must_not_include",
                          value=["you should invest", "guaranteed returns", "buy this stock",
                                 "sell your shares", "best investment"],
                          severity="high"),
            GuardrailRule(name="no_tax_advice", type="must_not_include",
                          value=["tax advice", "you can deduct", "file your taxes as",
                                 "tax-exempt"],
                          severity="high"),
            GuardrailRule(name="no_insurance_advice", type="must_not_include",
                          value=["you should get this insurance", "best policy for you",
                                 "cancel your insurance"],
                          severity="high"),
            GuardrailRule(name="no_profit_guarantees", type="must_not_include",
                          value=["guaranteed profit", "risk-free", "can't lose money",
                                 "100% returns"],
                          severity="high"),
        ],
        version="1.0.0",
    )


def healthcare_pack() -> GuardrailPack:
    """Healthcare compliance pack (HIPAA-aligned) — blocks medical diagnosis, medication advice, PHI."""
    return GuardrailPack(
        name="healthcare",
        description="Healthcare compliance: blocks medical diagnosis, medication advice, PHI",
        rules=[
            GuardrailRule(name="no_diagnosis", type="must_not_include",
                          value=["your diagnosis is", "you have cancer", "you are diabetic",
                                 "based on your symptoms you have"],
                          severity="high"),
            GuardrailRule(name="no_medication_advice", type="must_not_include",
                          value=["take this medication", "prescribe", "recommended dosage",
                                 "you should take"],
                          severity="high"),
            GuardrailRule(name="no_treatment_plans", type="must_not_include",
                          value=["your treatment plan", "you need surgery",
                                 "the procedure involves"],
                          severity="high"),
            GuardrailRule(name="no_phi_disclosure", type="must_not_include",
                          value=["patient record", "medical record number",
                                 "health insurance number"],
                          severity="high"),
        ],
        version="1.0.0",
    )


def register_pack(name: str, pack_factory) -> None:
    """Register a custom guardrail pack in the global registry."""
    _PACK_REGISTRY[name] = pack_factory


# Register domain packs
register_pack("pii", pii_pack)
register_pack("security", security_pack)
register_pack("finance", finance_pack)
register_pack("healthcare", healthcare_pack)

__all__ = [
    "GuardrailPack", "GuardrailRule",
    "get_pack", "list_packs", "apply_pack", "register_pack",
    "safety_pack", "quality_pack", "compliance_pack",
    "pii_pack", "security_pack", "finance_pack", "healthcare_pack",
]
