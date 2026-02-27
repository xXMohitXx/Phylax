"""
Phylax Metrics Package (Axis 3)

Provides observation memory for expectation health tracking.

Design rules:
- All metrics derive from raw ledger entries
- No qualitative labels, no scoring, no interpretation
- Append-only ledger, immutable entries
- All aggregations are computed, never stored
"""
