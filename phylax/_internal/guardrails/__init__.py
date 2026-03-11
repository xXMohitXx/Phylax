"""
Phylax Guardrail Packs — Pre-built expectation rule sets for common use cases.

Packs:
    - safety: Content safety rules (no hate speech, PII, etc.)
    - quality: Response quality rules (min length, coherence markers)
    - compliance: Regulatory compliance (no financial advice, medical disclaimers)
"""
from phylax._internal.guardrails.packs import (
    GuardrailPack,
    get_pack,
    list_packs,
    apply_pack,
    # Built-in packs
    safety_pack,
    quality_pack,
    compliance_pack,
)

__all__ = [
    "GuardrailPack",
    "get_pack",
    "list_packs",
    "apply_pack",
    "safety_pack",
    "quality_pack",
    "compliance_pack",
]
