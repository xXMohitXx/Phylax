"""
phylax.rag — Public API for RAG Pipeline Enforcement.

Usage:
    from phylax.rag import ContextUsedRule, NoHallucinationRule, CitationRequiredRule, evaluate_rag
"""
from phylax._internal.surfaces.rag import (
    RAGRuleResult,
    ContextUsedRule,
    NoHallucinationRule,
    CitationRequiredRule,
    evaluate_rag,
)

__all__ = [
    "RAGRuleResult",
    "ContextUsedRule",
    "NoHallucinationRule",
    "CitationRequiredRule",
    "evaluate_rag",
]
