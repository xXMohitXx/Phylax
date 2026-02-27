"""
Mode Handler (Axis 3 - Phase 3.3.1)

Enforcement wrapper that decides exit behavior based on mode.

Design rules:
- Engine returns verdict (PASS/FAIL) always
- Mode handler decides: exit code, logging behavior
- Engine is NEVER aware of mode
- Mode changes behavior OUTSIDE engine, not inside
- No dynamic escalation
- No auto-switching
"""

from typing import Literal, Optional

from pydantic import BaseModel, Field

from phylax._internal.modes.definitions import EnforcementMode, VALID_MODES


class ModeResult(BaseModel):
    """
    Result of applying a mode to a verdict.
    
    Invariants:
    - verdict is ALWAYS the raw engine verdict (never modified)
    - exit_code and log_action are the only mode-affected fields
    - Immutable after creation
    """
    
    verdict: Literal["pass", "fail"] = Field(
        description="Raw engine verdict — NEVER modified by mode"
    )
    exit_code: int = Field(
        description="Exit code for CI: 0 = success, 1 = failure"
    )
    log_action: str = Field(
        description="What the mode does: 'enforce', 'quarantine', 'observe'"
    )
    mode: EnforcementMode = Field(
        description="Mode that was applied"
    )
    
    class Config:
        frozen = True


class ModeHandler:
    """
    Applies enforcement mode to engine verdicts.
    
    The engine is NEVER aware of the mode.
    Mode only affects what happens AFTER the verdict.
    
    Invariants:
    - Same verdict for same input across all modes
    - Mode is explicit (set at construction, not auto-detected)
    - No escalation logic
    - No auto-switching between modes
    """
    
    def __init__(self, mode: EnforcementMode):
        """
        Args:
            mode: One of 'enforce', 'quarantine', 'observe'.
        """
        if mode not in VALID_MODES:
            raise ValueError(
                f"Invalid mode: {mode!r}. Must be one of: {sorted(VALID_MODES)}"
            )
        self._mode = mode
    
    @property
    def mode(self) -> EnforcementMode:
        """Current mode (read-only)."""
        return self._mode
    
    def apply(self, verdict: Literal["pass", "fail"]) -> ModeResult:
        """
        Apply mode to a verdict.
        
        The verdict is NEVER modified.
        Only exit_code and log_action change based on mode.
        
        Args:
            verdict: Raw engine verdict ("pass" or "fail").
            
        Returns:
            ModeResult with exit_code and log_action.
        """
        if verdict not in ("pass", "fail"):
            raise ValueError(
                f"Invalid verdict: {verdict!r}. Must be 'pass' or 'fail'."
            )
        
        if self._mode == "enforce":
            return ModeResult(
                verdict=verdict,
                exit_code=1 if verdict == "fail" else 0,
                log_action="enforce",
                mode=self._mode,
            )
        
        elif self._mode == "quarantine":
            return ModeResult(
                verdict=verdict,
                exit_code=0,  # Always exit 0 in quarantine
                log_action="quarantine",
                mode=self._mode,
            )
        
        elif self._mode == "observe":
            return ModeResult(
                verdict=verdict,
                exit_code=0,  # Always exit 0 in observe
                log_action="observe",
                mode=self._mode,
            )
        
        # Should never reach here — VALID_MODES check at init
        raise ValueError(f"Unknown mode: {self._mode!r}")
