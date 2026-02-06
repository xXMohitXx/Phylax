"""
Demo 07: Error Contracts

Demonstrates PHYLAX error codes (Phase 2):
- PHYLAX_E101: Missing expectations
- PHYLAX_E102: Empty execution graph
- PHYLAX_E201: Non-deterministic golden
- PHYLAX_E202: Check without goldens

Requirements:
- pip install phylax[all]
"""

import sys

from phylax import __version__
from phylax._internal.errors import (
    MissingExpectationsError,
    EmptyExecutionGraphError,
    NonDeterministicGoldenError,
    ReplayWithoutGoldenError,
)


def demo_e101_missing_expectations():
    """PHYLAX_E101: Function with @trace but no @expect."""
    print("📍 PHYLAX_E101: Missing Expectations")
    print("   When @trace is used without @expect:")
    print()
    print("   @trace(provider='gemini')  # ❌ No @expect!")
    print("   def my_func():")
    print("       ...")
    print()
    
    # Show the error
    try:
        raise MissingExpectationsError("my_func")
    except MissingExpectationsError as e:
        print(f"   Error: {e}")
    print()


def demo_e102_empty_graph():
    """PHYLAX_E102: Empty execution context."""
    print("📍 PHYLAX_E102: Empty Execution Graph")
    print("   When execution() contains no traced calls:")
    print()
    print("   with execution() as exec_id:")
    print("       pass  # ❌ No traces!")
    print()
    
    try:
        raise EmptyExecutionGraphError("abc-123")
    except EmptyExecutionGraphError as e:
        print(f"   Error: {e}")
    print()


def demo_e201_non_deterministic():
    """PHYLAX_E201: Cannot bless non-deterministic trace."""
    print("📍 PHYLAX_E201: Non-Deterministic Golden")
    print("   When trying to bless a trace without verdict:")
    print()
    print("   phylax bless <trace_without_verdict>")
    print()
    
    try:
        raise NonDeterministicGoldenError("trace-xyz", "no verdict attached")
    except NonDeterministicGoldenError as e:
        print(f"   Error: {e}")
    print()


def demo_e202_no_golden():
    """PHYLAX_E202: Check without golden references."""
    print("📍 PHYLAX_E202: Replay Without Golden")
    print("   When running check without blessed traces:")
    print()
    print("   phylax check  # ❌ No golden traces!")
    print()
    
    try:
        raise ReplayWithoutGoldenError("gemini", "gemini-2.5-flash")
    except ReplayWithoutGoldenError as e:
        print(f"   Error: {e}")
    print()


def main():
    print("=" * 60)
    print("🧪 DEMO 07: Error Contracts")
    print("=" * 60)
    print(f"📦 Phylax version: {__version__}")
    print()
    
    demo_e101_missing_expectations()
    demo_e102_empty_graph()
    demo_e201_non_deterministic()
    demo_e202_no_golden()
    
    print("═" * 60)
    print("📝 Error Contract Summary")
    print("═" * 60)
    print()
    print("| Code         | Invariant Violated              |")
    print("|--------------|----------------------------------|")
    print("| PHYLAX_E101  | @trace without @expect           |")
    print("| PHYLAX_E102  | Empty execution context          |")
    print("| PHYLAX_E201  | Bless trace without verdict      |")
    print("| PHYLAX_E202  | Check without golden traces      |")
    print()
    print("These are hard failures, not warnings.")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
