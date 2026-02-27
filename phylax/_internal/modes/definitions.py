"""
Mode Definitions (Axis 3 - Phase 3.3.2)

Three enforcement modes:
- enforce: FAIL → exit 1
- quarantine: FAIL → log, exit 0
- observe: Always exit 0, record only

Design rules:
- Mode is explicit and configuration-driven
- NEVER auto-switchable
- No dynamic escalation
- Same input across all modes → identical verdict
"""

from typing import Literal

EnforcementMode = Literal["enforce", "quarantine", "observe"]

# Valid modes — exhaustive, explicit
VALID_MODES = {"enforce", "quarantine", "observe"}
