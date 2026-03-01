"""
Demo 20 - Deterministic Exit Codes

Shows Phylax's frozen exit code system:
  0 = PASS or non-blocking mode
  1 = FAIL in enforce mode
  2 = System error

CI systems consume exit codes - no SDK required.

Usage:
    python demos/20_exit_codes.py
"""

from phylax import (
    EXIT_PASS,
    EXIT_FAIL,
    EXIT_SYSTEM_ERROR,
    resolve_exit_code,
)


def main():
    print("--- Frozen Exit Codes ---")
    print(f"EXIT_PASS         = {EXIT_PASS}")
    print(f"EXIT_FAIL         = {EXIT_FAIL}")
    print(f"EXIT_SYSTEM_ERROR = {EXIT_SYSTEM_ERROR}")

    # -- Resolution table -------------------------------------------------
    print("\n--- Resolution Table ---")
    scenarios = [
        ("PASS", "enforce"),
        ("PASS", "quarantine"),
        ("PASS", "observe"),
        ("FAIL", "enforce"),
        ("FAIL", "quarantine"),
        ("FAIL", "observe"),
    ]
    for verdict, mode in scenarios:
        code = resolve_exit_code(verdict=verdict, mode=mode)
        print(f"  {verdict:4s} + {mode:12s} -> exit {code}")

    # -- CI usage example -------------------------------------------------
    print("\n--- CI Usage ---")
    print("# In your CI pipeline (GitHub Actions, GitLab CI, etc.):")
    print("# ")
    print("#   - run: phylax check")
    print("#     # Exit 0 -> pipeline continues")
    print("#     # Exit 1 -> pipeline fails (enforce mode)")
    print("#     # Exit 2 -> system error, investigate")

    # -- Key properties ---------------------------------------------------
    print("\n--- Properties ---")
    print("[OK] Only 3 exit codes - frozen, no expansion without MAJOR bump")
    print("[OK] Pure function - no side effects, no logging")
    print("[OK] CI systems need only exit code, no Phylax SDK")
    print("[OK] Invalid verdicts/modes raise ValueError")

    # -- Error handling ---------------------------------------------------
    print("\n--- Error Handling ---")
    try:
        resolve_exit_code(verdict="warning", mode="enforce")
    except ValueError as e:
        print(f"  Invalid verdict rejected: {e}")

    try:
        resolve_exit_code(verdict="FAIL", mode="auto")
    except ValueError as e:
        print(f"  Invalid mode rejected: {e}")


if __name__ == "__main__":
    main()
