"""
4.1.4 — Deterministic Exit Codes

Frozen exit code definitions. No expansion without MAJOR version bump.

  0 → PASS or non-blocking mode
  1 → FAIL in enforce mode
  2 → System error (malformed config, etc.)
"""

# Frozen exit codes — do NOT add new values without major version bump.
EXIT_PASS: int = 0
EXIT_FAIL: int = 1
EXIT_SYSTEM_ERROR: int = 2

# Exhaustive set — anything else is a bug.
_VALID_EXIT_CODES = frozenset({EXIT_PASS, EXIT_FAIL, EXIT_SYSTEM_ERROR})


def resolve_exit_code(*, verdict: str, mode: str) -> int:
    """
    Resolve exit code from verdict and mode.
    
    Pure function. No side effects. No logging.
    
    Rules:
      - PASS always → 0
      - FAIL + enforce → 1
      - FAIL + quarantine → 0
      - FAIL + observe → 0
    """
    if verdict == "PASS" or verdict == "pass":
        return EXIT_PASS

    if verdict == "FAIL" or verdict == "fail":
        if mode == "enforce":
            return EXIT_FAIL
        elif mode in ("quarantine", "observe"):
            return EXIT_PASS
        else:
            raise ValueError(f"Unknown mode: {mode}")

    raise ValueError(f"Unknown verdict: {verdict}")
