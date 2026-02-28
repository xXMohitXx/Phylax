"""
Meta-Enforcement Rules (Axis 3 - Phase 3.4)

Four structural guards against expectation dilution:
- MinExpectationCountRule: minimum declared expectation count
- ZeroSignalRule: fail if expectation never failed (user opt-in)
- DefinitionChangeGuard: hash-based definition change detection
- ExpectationRemovalGuard: track IDs across versions

Design rules:
- No evaluation of complexity or usefulness
- No semantic diff — only hash comparison
- No judgment on removal reason
- No scoring, no ranking, no advisory language
- User declares rules, engine enforces them deterministically
"""

from typing import Literal, Optional

from pydantic import BaseModel, Field

from phylax._internal.metrics.identity import compute_definition_hash


class MetaRuleResult(BaseModel):
    """
    Result of a meta-enforcement rule evaluation.
    
    Binary: PASS or FAIL. No interpretation.
    """
    
    rule_name: str = Field(
        description="Name of the meta-enforcement rule"
    )
    passed: bool = Field(
        description="True = PASS, False = FAIL"
    )
    detail: str = Field(
        default="",
        description="Factual detail — never qualitative"
    )
    
    class Config:
        frozen = True


class MinExpectationCountRule:
    """
    3.4.1 — Minimum Expectation Count Rule
    
    Checks: len(declared_expectations) >= N
    
    Nothing more.
    No evaluation of complexity or usefulness.
    """
    
    def __init__(self, min_count: int):
        """
        Args:
            min_count: Minimum number of expectations required.
        """
        if min_count < 0:
            raise ValueError(f"min_count must be >= 0, got {min_count}")
        self._min_count = min_count
    
    def evaluate(self, declared_count: int) -> MetaRuleResult:
        """
        Check: declared_count >= min_count
        
        Pure arithmetic. No complexity evaluation.
        """
        passed = declared_count >= self._min_count
        detail = (
            f"declared={declared_count}, required={self._min_count}"
        )
        return MetaRuleResult(
            rule_name="min_expectation_count",
            passed=passed,
            detail=detail,
        )


class ZeroSignalRule:
    """
    3.4.2 — Zero-Signal Rule (Explicit Only)
    
    User may declare: fail_if_never_failed == true
    
    Engine checks: never_failed == true → FAIL
    
    It does NOT decide triviality.
    User chooses rule.
    """
    
    def evaluate(self, never_failed: bool) -> MetaRuleResult:
        """
        Check: if never_failed → FAIL
        
        No judgment. No triviality assessment.
        """
        passed = not never_failed
        detail = (
            "expectation has never failed"
            if never_failed
            else "expectation has failed at least once"
        )
        return MetaRuleResult(
            rule_name="zero_signal",
            passed=passed,
            detail=detail,
        )


class DefinitionChangeGuard:
    """
    3.4.3 — Definition Change Guard
    
    Store previous definition_hash.
    If hash mismatch → FAIL.
    
    No semantic diff.
    Only hash comparison.
    """
    
    def evaluate(
        self,
        previous_hash: str,
        current_hash: str,
    ) -> MetaRuleResult:
        """
        Check: previous_hash == current_hash
        
        No semantic diff. Only hash comparison.
        """
        passed = previous_hash == current_hash
        detail = (
            "definition unchanged"
            if passed
            else f"definition changed: {previous_hash[:12]}... → {current_hash[:12]}..."
        )
        return MetaRuleResult(
            rule_name="definition_change_guard",
            passed=passed,
            detail=detail,
        )


class ExpectationRemovalGuard:
    """
    3.4.4 — Expectation Removal Guard
    
    Track expectation IDs across versions.
    If previously declared expectation missing → FAIL.
    
    No judgment on removal reason.
    """
    
    def evaluate(
        self,
        previous_ids: set[str],
        current_ids: set[str],
    ) -> MetaRuleResult:
        """
        Check: all previous IDs still present in current.
        
        No judgment on why IDs were removed.
        """
        removed = previous_ids - current_ids
        passed = len(removed) == 0
        detail = (
            "no expectations removed"
            if passed
            else f"removed expectations: {sorted(removed)}"
        )
        return MetaRuleResult(
            rule_name="expectation_removal_guard",
            passed=passed,
            detail=detail,
        )
