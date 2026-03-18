"""
Tests for RAG Pipeline Enforcement Rules.

Tests cover:
    - ContextUsedRule: term overlap detection
    - NoHallucinationRule: forbidden claim detection
    - CitationRequiredRule: citation pattern matching
    - evaluate_rag: combined evaluation
"""
import pytest
from phylax.rag import (
    ContextUsedRule,
    NoHallucinationRule,
    CitationRequiredRule,
    evaluate_rag,
)


class TestContextUsedRule:
    """Tests for ContextUsedRule — response must use terms from context."""

    def test_passes_when_context_terms_present(self):
        rule = ContextUsedRule(min_overlap_terms=2)
        context = "GDPR is a European regulation about data privacy"
        response = "According to GDPR, the European regulation covers data privacy rights."
        result = rule.evaluate(response, context)
        assert result.passed is True

    def test_fails_when_context_terms_missing(self):
        rule = ContextUsedRule(min_overlap_terms=5)
        context = "GDPR is a European regulation about data privacy"
        response = "The weather is nice today."
        result = rule.evaluate(response, context)
        assert result.passed is False
        assert len(result.violations) > 0

    def test_filters_short_words(self):
        rule = ContextUsedRule(min_overlap_terms=1, term_min_length=6)
        context = "A an the is regulation"
        response = "This regulation applies."
        result = rule.evaluate(response, context)
        assert result.passed is True

    def test_case_insensitive(self):
        rule = ContextUsedRule(min_overlap_terms=1)
        context = "IMPORTANT REGULATION"
        response = "this important regulation applies"
        result = rule.evaluate(response, context)
        assert result.passed is True


class TestNoHallucinationRule:
    """Tests for NoHallucinationRule — forbidden claims must not appear."""

    def test_passes_when_no_forbidden_claims(self):
        rule = NoHallucinationRule(forbidden_claims=["US law", "American regulation"])
        response = "GDPR is a European regulation about data privacy."
        result = rule.evaluate(response, "")
        assert result.passed is True

    def test_fails_when_forbidden_claim_present(self):
        rule = NoHallucinationRule(forbidden_claims=["US law"])
        response = "GDPR is a US law about data."
        result = rule.evaluate(response, "")
        assert result.passed is False
        assert "US law" in result.violations[0]

    def test_case_insensitive_matching(self):
        rule = NoHallucinationRule(forbidden_claims=["us law"])
        response = "This is a US LAW about data."
        result = rule.evaluate(response, "")
        assert result.passed is False

    def test_empty_forbidden_list_always_passes(self):
        rule = NoHallucinationRule(forbidden_claims=[])
        response = "Anything goes here."
        result = rule.evaluate(response, "")
        assert result.passed is True


class TestCitationRequiredRule:
    """Tests for CitationRequiredRule — response must include citations."""

    def test_passes_with_bracket_citation(self):
        rule = CitationRequiredRule(min_citations=1)
        response = "GDPR protects personal data [1]."
        result = rule.evaluate(response, "")
        assert result.passed is True

    def test_passes_with_source_citation(self):
        rule = CitationRequiredRule(min_citations=1)
        response = "According to the regulation, data must be protected."
        result = rule.evaluate(response, "")
        assert result.passed is True

    def test_fails_without_citations(self):
        rule = CitationRequiredRule(min_citations=1)
        response = "GDPR protects personal data."
        result = rule.evaluate(response, "")
        assert result.passed is False

    def test_custom_citation_patterns(self):
        rule = CitationRequiredRule(
            citation_patterns=["(Source:", "(Ref:"],
            min_citations=1,
        )
        response = "GDPR applies to all EU members (Source: EU Commission)."
        result = rule.evaluate(response, "")
        assert result.passed is True


class TestEvaluateRAG:
    """Tests for the combined evaluate_rag function."""

    def test_all_rules_pass(self):
        context = "GDPR is a European regulation about data privacy protection"
        response = (
            "According to GDPR, the European regulation ensures data privacy "
            "protection for all citizens [1]."
        )
        results = evaluate_rag(response, context)
        assert all(r.passed for r in results)

    def test_mixed_results(self):
        context = "GDPR is a European regulation about data privacy"
        response = "The weather is nice today."
        results = evaluate_rag(response, context)
        assert not all(r.passed for r in results)

    def test_custom_rules(self):
        rules = [ContextUsedRule(min_overlap_terms=1)]
        context = "GDPR regulation"
        response = "The GDPR applies."
        results = evaluate_rag(response, context, rules=rules)
        assert len(results) == 1
        assert results[0].passed is True
