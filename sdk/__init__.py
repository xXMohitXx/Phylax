"""
Sentinel SDK - LLM Tracing & Debugging

This package provides the core capture layer for tracing LLM calls.
"""

from sdk.schema import Trace, TraceRequest, TraceResponse, TraceRuntime, Verdict
from sdk.decorator import trace, expect
from sdk.capture import CaptureLayer
from sdk.context import execution  # Phase 13: Execution context

__version__ = "0.2.0"
__all__ = [
    "Trace",
    "TraceRequest",
    "TraceResponse",
    "TraceRuntime",
    "Verdict",
    "trace",
    "expect",
    "CaptureLayer",
    "execution",  # Phase 13
]
