"""
Phylax Modes Package (Axis 3 - Phase 3.3)

Enforcement mode layer that operates OUTSIDE the engine.

Design rules:
- Mode affects CI behavior only (exit code, logging)
- Engine verdict is NEVER modified by mode
- No auto-escalation
- Mode is explicit, configuration-driven
"""
