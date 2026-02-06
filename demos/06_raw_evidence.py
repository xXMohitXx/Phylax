"""
Demo 06: Raw Evidence

Demonstrates Phase 3: Raw Evidence Disclosure
- Hash evidence
- Latency evidence
- Path evidence
- Non-interpretation principle

Requirements:
- pip install phylax[all]
"""

import sys

from phylax import __version__
from phylax._internal.evidence import (
    compare_outputs,
    compare_latency,
    compare_paths,
)


def main():
    print("=" * 60)
    print("🧪 DEMO 06: Raw Evidence")
    print("=" * 60)
    print(f"📦 Phylax version: {__version__}")
    print()
    
    # Hash Evidence
    print("📍 Hash Evidence")
    original_text = "The answer is 42."
    new_text = "The answer is 42."
    evidence = compare_outputs(original_text, new_text)
    print(f"   Original hash: {evidence.original_hash}")
    print(f"   New hash: {evidence.new_hash}")
    print(f"   Match: {evidence.match}")
    print()
    
    # Different output
    different_text = "The answer is 43."
    evidence2 = compare_outputs(original_text, different_text)
    print(f"   Different text hash: {evidence2.new_hash}")
    print(f"   Match: {evidence2.match}")
    print()
    
    # Latency Evidence
    print("📍 Latency Evidence")
    latency = compare_latency(original_ms=150, new_ms=200)
    print(f"   Original: {latency.original_ms}ms")
    print(f"   New: {latency.new_ms}ms")
    print(f"   Delta: {latency.delta_ms}ms")
    print()
    
    # Path Evidence
    print("📍 Path Evidence")
    path1 = ["step_a", "step_b", "step_c"]
    path2 = ["step_a", "step_b", "step_d"]  # Diverged at step_c
    path_evidence = compare_paths(path1, path2)
    print(f"   Original: {path_evidence.original_path}")
    print(f"   New: {path_evidence.new_path}")
    print(f"   Diverged: {path_evidence.diverged}")
    print(f"   Point: {path_evidence.divergence_point}")
    print()
    
    # Disclaimer
    print("═" * 60)
    print("⚠️  Phylax reports evidence. Interpretation is external.")
    print("═" * 60)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
