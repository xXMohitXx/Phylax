"""
Expectation Identity Freezing (Axis 3 - Phase 3.1.1)

Every expectation gets a frozen identity:
- expectation_id: explicit or auto-generated deterministic hash
- definition_hash: SHA256 of canonical rule serialization
- created_at: ISO timestamp at creation
- last_modified_at: ISO timestamp at last modification

Design rules:
- definition_hash computed from CANONICAL serialization
- Whitespace must NOT change hash
- Semantic changes MUST change hash
- No interpretation of change — only detection
"""

import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from pydantic import BaseModel, Field


def _canonical_serialize(rule_config: dict[str, Any]) -> str:
    """
    Canonical JSON serialization for deterministic hashing.
    
    Rules:
    - Keys sorted recursively
    - No whitespace
    - Unicode escaped consistently
    - Deterministic across runs
    """
    return json.dumps(rule_config, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def compute_definition_hash(rule_config: dict[str, Any]) -> str:
    """
    Compute SHA256 hash of a rule definition.
    
    Whitespace-insensitive (canonical form used).
    Semantic-change-sensitive (any value change = new hash).
    
    Args:
        rule_config: Dictionary describing the rule configuration.
        
    Returns:
        64-character hex SHA256 hash string.
    """
    canonical = _canonical_serialize(rule_config)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _generate_deterministic_id(rule_config: dict[str, Any]) -> str:
    """
    Generate a deterministic expectation ID from rule config.
    
    Same config → same ID. Always.
    Uses first 16 chars of definition hash as namespace.
    """
    definition_hash = compute_definition_hash(rule_config)
    return f"exp-{definition_hash[:16]}"


class ExpectationIdentity(BaseModel):
    """
    Frozen identity for a single expectation.
    
    Once created, the expectation_id never changes.
    definition_hash changes only when rule semantics change.
    
    Invariants:
    - Immutable after creation (frozen=True)
    - expectation_id is permanent
    - definition_hash is deterministic
    """
    
    expectation_id: str = Field(
        description="Explicit or auto-generated deterministic ID"
    )
    definition_hash: str = Field(
        description="SHA256 of canonical rule serialization"
    )
    rule_config: dict[str, Any] = Field(
        description="Original rule configuration (preserved for auditability)"
    )
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO timestamp at creation"
    )
    last_modified_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO timestamp at last modification"
    )
    
    class Config:
        frozen = True  # Immutable after creation
    
    @classmethod
    def create(
        cls,
        rule_config: dict[str, Any],
        expectation_id: Optional[str] = None,
    ) -> "ExpectationIdentity":
        """
        Create a new ExpectationIdentity.
        
        Args:
            rule_config: Dictionary describing the rule.
            expectation_id: Explicit ID, or None for auto-generated.
            
        Returns:
            Frozen ExpectationIdentity instance.
        """
        definition_hash = compute_definition_hash(rule_config)
        eid = expectation_id or _generate_deterministic_id(rule_config)
        now = datetime.now(timezone.utc).isoformat()
        
        return cls(
            expectation_id=eid,
            definition_hash=definition_hash,
            rule_config=rule_config,
            created_at=now,
            last_modified_at=now,
        )
    
    def has_changed(self, new_config: dict[str, Any]) -> bool:
        """
        Check if rule definition has changed.
        
        No interpretation — only hash comparison.
        
        Returns:
            True if definition_hash differs.
        """
        new_hash = compute_definition_hash(new_config)
        return new_hash != self.definition_hash
