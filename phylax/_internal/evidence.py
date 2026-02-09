"""
Phylax Raw Evidence Module

Exposes raw facts, NOT analysis.
Evidence artifacts for machine consumption.

Design principle:
- Observations, not explanations
- Data, not insights
- Phylax reports evidence. Interpretation is external.
"""

import hashlib
from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime


@dataclass
class HashEvidence:
    """
    Evidence: output hash changed.
    
    Phylax reports evidence. Interpretation is external.
    """
    original_hash: str
    new_hash: str
    match: bool
    
    def to_dict(self) -> dict:
        return {
            "type": "hash_evidence",
            "original_hash": self.original_hash,
            "new_hash": self.new_hash,
            "match": self.match,
            "_disclaimer": "Phylax reports evidence. Interpretation is external.",
        }


@dataclass
class LatencyEvidence:
    """
    Evidence: latency measurement.
    
    Phylax reports evidence. Interpretation is external.
    """
    original_ms: int
    new_ms: int
    delta_ms: int
    
    def to_dict(self) -> dict:
        return {
            "type": "latency_evidence",
            "original_ms": self.original_ms,
            "new_ms": self.new_ms,
            "delta_ms": self.delta_ms,
            "_disclaimer": "Phylax reports evidence. Interpretation is external.",
        }


@dataclass
class PathEvidence:
    """
    Evidence: execution path divergence.
    
    Phylax reports evidence. Interpretation is external.
    """
    original_path: List[str]
    new_path: List[str]
    diverged: bool
    divergence_point: Optional[str]
    
    def to_dict(self) -> dict:
        return {
            "type": "path_evidence",
            "original_path": self.original_path,
            "new_path": self.new_path,
            "diverged": self.diverged,
            "divergence_point": self.divergence_point,
            "_disclaimer": "Phylax reports evidence. Interpretation is external.",
        }


@dataclass
class TimestampEvidence:
    """
    Evidence: timestamp delta.
    
    Phylax reports evidence. Interpretation is external.
    """
    original_timestamp: str
    new_timestamp: str
    
    def to_dict(self) -> dict:
        return {
            "type": "timestamp_evidence",
            "original_timestamp": self.original_timestamp,
            "new_timestamp": self.new_timestamp,
            "_disclaimer": "Phylax reports evidence. Interpretation is external.",
        }


def compute_hash(text: str) -> str:
    """Compute hash of text for comparison."""
    return hashlib.sha256(text.encode()).hexdigest()[:16]


def compare_outputs(original_text: str, new_text: str) -> HashEvidence:
    """
    Compare two outputs and return hash evidence.
    
    Phylax reports evidence. Interpretation is external.
    """
    original_hash = compute_hash(original_text)
    new_hash = compute_hash(new_text)
    return HashEvidence(
        original_hash=original_hash,
        new_hash=new_hash,
        match=(original_hash == new_hash),
    )


def compare_latency(original_ms: int, new_ms: int) -> LatencyEvidence:
    """
    Compare latencies and return evidence.
    
    Phylax reports evidence. Interpretation is external.
    """
    return LatencyEvidence(
        original_ms=original_ms,
        new_ms=new_ms,
        delta_ms=(new_ms - original_ms),
    )


def compare_paths(original_path: List[str], new_path: List[str]) -> PathEvidence:
    """
    Compare execution paths and return evidence.
    
    Phylax reports evidence. Interpretation is external.
    """
    diverged = (original_path != new_path)
    divergence_point = None
    
    if diverged:
        for i, (orig, new) in enumerate(zip(original_path, new_path)):
            if orig != new:
                divergence_point = f"index_{i}"
                break
        else:
            divergence_point = f"length_mismatch"
    
    return PathEvidence(
        original_path=original_path,
        new_path=new_path,
        diverged=diverged,
        divergence_point=divergence_point,
    )
