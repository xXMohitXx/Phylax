"""
Demo 20 â€” Deterministic Exit Codes

Shows Phylax's frozen exit code system:
  0 â†’ PASS or non-blocking mode
  1 â†’ FAIL in enforce mode
  2 â†’ System error

CI systems consume exit codes â€” no SDK required.

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
    print("â•â•â• Frozen Exit Codes â•â•â•")
    print(f"EXIT_PASS         = {EXIT_PASS}")
    print(f"EXIT_FAIL         = {EXIT_FAIL}")
    print(f"EXIT_SYSTEM_ERROR = {EXIT_SYSTEM_ERROR}")

    # â”€â”€ Resolution table â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    print("\nâ•â•â• Resolution Table â•â•â•")
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
        print(f"  {verdict:4s} + {mode:12s} â†’ exit {code}")

    # â”€â”€ CI usage example â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    print("\nâ•â•â• CI Usage â•â•â•")
    print("# In your CI pipeline (GitHub Actions, GitLab CI, etc.):")
    print("# ")
    print("#   - run: phylax check")
    print("#     # Exit 0 â†’ pipeline continues")
    print("#     # Exit 1 â†’ pipeline fails (enforce mode)")
    print("#     # Exit 2 â†’ system error, investigate")

    # â”€â”€ Key properties â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    print("\nâ•â•â• Properties â•â•â•")
    print("âœ“ Only 3 exit codes â€” frozen, no expansion without MAJOR bump")
    print("âœ“ Pure function â€” no side effects, no logging")
    print("âœ“ CI systems need only exit code, no Phylax SDK")
    print("âœ“ Invalid verdicts/modes raise ValueError")

    # â”€â”€ Error handling â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    print("\nâ•â•â• Error Handling â•â•â•")
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

