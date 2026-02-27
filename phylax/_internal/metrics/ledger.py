"""
Evaluation Ledger (Axis 3 - Phase 3.1.2)

Append-only ledger for evaluation results.

Design rules:
- Entries are immutable once written (frozen=True)
- No summarization during write — raw storage only
- No overwrite, no delete capability
- Backed by JSON Lines (.jsonl) for append-only semantics
- If entries can be overwritten → misuse risk

This is the single source of truth for all metrics.
"""

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal, Optional

from pydantic import BaseModel, Field


class LedgerEntry(BaseModel):
    """
    Single evaluation record.
    
    Immutable. Once written, never modified.
    """
    
    run_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique run identifier"
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO timestamp of evaluation"
    )
    expectation_id: str = Field(
        description="ID of the expectation evaluated"
    )
    verdict: Literal["pass", "fail"] = Field(
        description="Binary verdict — PASS or FAIL only"
    )
    
    class Config:
        frozen = True  # Immutable after creation


class EvaluationLedger:
    """
    Append-only evaluation ledger.
    
    Invariants:
    - Entries cannot be modified after recording
    - Entries cannot be deleted
    - Recording is append-only
    - Reading returns all entries in insertion order
    
    Storage: JSON Lines file (.jsonl)
    Each line is one JSON-serialized LedgerEntry.
    """
    
    def __init__(self, ledger_path: Optional[str] = None):
        """
        Args:
            ledger_path: Path to .jsonl file. If None, uses in-memory storage.
        """
        self._path = Path(ledger_path) if ledger_path else None
        self._memory: list[LedgerEntry] = []
        
        # Load existing entries if file exists
        if self._path and self._path.exists():
            self._load_from_disk()
    
    def _load_from_disk(self) -> None:
        """Load existing ledger entries from disk."""
        with open(self._path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    entry = LedgerEntry.model_validate_json(line)
                    self._memory.append(entry)
    
    def record(self, entry: LedgerEntry) -> None:
        """
        Append a single entry to the ledger.
        
        This is the ONLY write operation.
        No update. No delete. No overwrite.
        
        Args:
            entry: Frozen LedgerEntry to record.
        """
        self._memory.append(entry)
        
        if self._path:
            # Append-only: open in 'a' mode
            self._path.parent.mkdir(parents=True, exist_ok=True)
            with open(self._path, "a", encoding="utf-8") as f:
                f.write(entry.model_dump_json() + "\n")
    
    def get_entries(
        self,
        expectation_id: Optional[str] = None,
    ) -> list[LedgerEntry]:
        """
        Read entries from the ledger.
        
        Args:
            expectation_id: Filter by expectation ID. None = all entries.
            
        Returns:
            List of LedgerEntry in insertion order.
        """
        if expectation_id is None:
            return list(self._memory)
        return [e for e in self._memory if e.expectation_id == expectation_id]
    
    def get_entries_windowed(
        self,
        expectation_id: str,
        last_n: int,
    ) -> list[LedgerEntry]:
        """
        Get the last N entries for a given expectation.
        
        N must be explicitly provided. No auto-window.
        No rolling window. No statistical smoothing.
        
        Args:
            expectation_id: Expectation to query.
            last_n: Exactly how many recent entries to return.
            
        Returns:
            Last N entries for this expectation, in insertion order.
        """
        filtered = [e for e in self._memory if e.expectation_id == expectation_id]
        return filtered[-last_n:] if last_n < len(filtered) else filtered
    
    @property
    def total_entries(self) -> int:
        """Total number of ledger entries."""
        return len(self._memory)
