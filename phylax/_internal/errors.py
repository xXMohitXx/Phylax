"""
Phylax Error Classes

Canonical error codes for machine-readable failures.
No explanations. No diagnostics. No suggestions.

Error code format: PHYLAX_Exxx
"""


class PhylaxError(Exception):
    """Base class for all Phylax errors."""
    
    code: str = "PHYLAX_E000"
    
    def __init__(self, message: str = ""):
        self.message = message
        super().__init__(f"[{self.code}] {message}")


# =============================================================================
# E1xx: Expectation Errors
# =============================================================================

class MissingExpectationsError(PhylaxError):
    """Execution has no expectations. Meaningless run."""
    
    code = "PHYLAX_E101"
    
    def __init__(self, func_name: str = ""):
        super().__init__(
            f"Function '{func_name}' has no expectations. "
            "Add @expect decorator or Phylax cannot produce a verdict."
        )


class EmptyExecutionGraphError(PhylaxError):
    """Execution graph contains no nodes."""
    
    code = "PHYLAX_E102"
    
    def __init__(self, execution_id: str = ""):
        super().__init__(
            f"Execution '{execution_id}' has no traced calls. "
            "An empty graph cannot be evaluated."
        )


class NoVerdictPathError(PhylaxError):
    """Execution has no verdict path."""
    
    code = "PHYLAX_E103"
    
    def __init__(self):
        super().__init__(
            "Execution completed without any verdict-producing nodes."
        )


# =============================================================================
# E2xx: Golden Trace Errors
# =============================================================================

class NonDeterministicGoldenError(PhylaxError):
    """Attempted to bless a non-deterministic trace."""
    
    code = "PHYLAX_E201"
    
    def __init__(self, trace_id: str = "", reason: str = ""):
        msg = f"Cannot bless trace '{trace_id}'. "
        if reason:
            msg += f"Instability detected: {reason}"
        else:
            msg += "Non-deterministic behavior detected."
        super().__init__(msg)


class ReplayWithoutGoldenError(PhylaxError):
    """Replay requested but no golden reference exists."""
    
    code = "PHYLAX_E202"
    
    def __init__(self, model: str = "", provider: str = ""):
        super().__init__(
            f"No golden trace exists for {provider}/{model}. "
            "Bless a trace first with 'phylax bless <trace_id>'."
        )


class GoldenHashMismatchError(PhylaxError):
    """Output hash differs from golden reference."""
    
    code = "PHYLAX_E203"
    
    def __init__(self, expected: str = "", actual: str = ""):
        super().__init__(
            f"Output hash mismatch. Expected: {expected}, Got: {actual}"
        )


# =============================================================================
# E3xx: Configuration Errors
# =============================================================================

class MeaninglessConfigurationError(PhylaxError):
    """Configuration is meaningless - cannot produce verdicts."""
    
    code = "PHYLAX_E301"
    
    def __init__(self, reason: str = ""):
        super().__init__(reason or "Configuration cannot produce verdicts.")
