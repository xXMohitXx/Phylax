"""
RAG Pipeline Enforcement Rules — Deterministic validation for RAG outputs.

Rules:
    ContextUsedRule — Response must use content from the provided context.
    NoHallucinationRule — Response must not contain claims absent from context (deterministic).
    CitationRequiredRule — Response must include source citations.
"""
from typing import Optional
from pydantic import BaseModel, Field


class RAGRuleResult(BaseModel):
    """Result of evaluating a RAG enforcement rule."""
    passed: bool
    rule_name: str
    violations: list[str] = Field(default_factory=list)

    model_config = {"frozen": True}


class ContextUsedRule:
    """Response must reference content from the provided context.

    Checks that the response contains at least N key terms from the context.
    This is deterministic: exact substring matching, no LLM judgment.

    Args:
        min_overlap_terms: Minimum number of context terms that must appear in response.
        term_min_length: Minimum word length to consider as a "key term" (filters stop words).
    """
    name = "context_used"
    severity = "high"

    def __init__(self, min_overlap_terms: int = 3, term_min_length: int = 4):
        self.min_overlap_terms = min_overlap_terms
        self.term_min_length = term_min_length

    def evaluate(self, response_text: str, context: str) -> RAGRuleResult:
        """Check that response uses terms from the provided context."""
        context_terms = set(
            word.lower().strip(".,;:!?\"'()[]{}") 
            for word in context.split() 
            if len(word.strip(".,;:!?\"'()[]{}")) >= self.term_min_length
        )
        response_lower = response_text.lower()
        
        found_terms = [term for term in context_terms if term in response_lower]
        
        if len(found_terms) >= self.min_overlap_terms:
            return RAGRuleResult(passed=True, rule_name=self.name)
        
        return RAGRuleResult(
            passed=False,
            rule_name=self.name,
            violations=[
                f"context_used: found {len(found_terms)} terms from context "
                f"(minimum: {self.min_overlap_terms}). "
                f"Terms found: {found_terms[:5]}"
            ],
        )


class NoHallucinationRule:
    """Response must not contain specific forbidden claims absent from context.

    This is the DETERMINISTIC version — it checks that the response does not
    contain specific forbidden phrases that contradict or add to the context.
    This is NOT LLM-based judgment. It is substring matching against a deny list.

    Args:
        forbidden_claims: List of phrases that should NOT appear in the response.
    """
    name = "no_hallucination"
    severity = "high"

    def __init__(self, forbidden_claims: Optional[list[str]] = None):
        self.forbidden_claims = forbidden_claims or []

    def evaluate(self, response_text: str, context: str) -> RAGRuleResult:
        """Check that response doesn't contain forbidden claims."""
        response_lower = response_text.lower()
        found_forbidden = []
        
        for claim in self.forbidden_claims:
            if claim.lower() in response_lower:
                found_forbidden.append(claim)
        
        if not found_forbidden:
            return RAGRuleResult(passed=True, rule_name=self.name)
        
        return RAGRuleResult(
            passed=False,
            rule_name=self.name,
            violations=[
                f"no_hallucination: response contains forbidden claims: {found_forbidden}"
            ],
        )


class CitationRequiredRule:
    """Response must include source citations.

    Checks that the response contains citation markers (e.g., [1], [Source:], etc.).

    Args:
        citation_patterns: List of substrings that count as valid citations.
        min_citations: Minimum number of citations required.
    """
    name = "citation_required"
    severity = "medium"

    def __init__(
        self,
        citation_patterns: Optional[list[str]] = None,
        min_citations: int = 1,
    ):
        self.citation_patterns = citation_patterns or [
            "[1]", "[2]", "[3]", "[source:", "[ref:", "source:", "according to",
        ]
        self.min_citations = min_citations

    def evaluate(self, response_text: str, context: str) -> RAGRuleResult:
        """Check that response includes citations."""
        response_lower = response_text.lower()
        found_citations = sum(
            1 for pattern in self.citation_patterns
            if pattern.lower() in response_lower
        )
        
        if found_citations >= self.min_citations:
            return RAGRuleResult(passed=True, rule_name=self.name)
        
        return RAGRuleResult(
            passed=False,
            rule_name=self.name,
            violations=[
                f"citation_required: found {found_citations} citation(s) "
                f"(minimum: {self.min_citations})"
            ],
        )


def evaluate_rag(
    response_text: str,
    context: str,
    rules: Optional[list] = None,
) -> list[RAGRuleResult]:
    """Evaluate a RAG response against a list of rules.

    Args:
        response_text: The generated response.
        context: The retrieved context used for generation.
        rules: List of rule instances. Defaults to all three rules.

    Returns:
        List of RAGRuleResult for each rule.
    """
    if rules is None:
        rules = [
            ContextUsedRule(),
            NoHallucinationRule(),
            CitationRequiredRule(),
        ]
    
    return [rule.evaluate(response_text, context) for rule in rules]
