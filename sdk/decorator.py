"""
Decorator - Function Decorator for Tracing

Provides a clean decorator interface for tracing LLM calls.
No reflection, no AST tricks — explicit, debuggable Python.

Decorators:
- @trace: Capture LLM calls automatically
- @expect: Define expectations for validation
"""

import functools
from typing import Any, Callable, Optional, TypeVar, ParamSpec

from sdk.capture import get_capture_layer, CaptureLayer
from sdk.context import get_execution_id, get_parent_node_id, push_node, pop_node

P = ParamSpec("P")
T = TypeVar("T")

# Store expectations per function (set by @expect decorator)
_function_expectations: dict[Callable, dict[str, Any]] = {}


def expect(
    must_include: Optional[list[str]] = None,
    must_not_include: Optional[list[str]] = None,
    max_latency_ms: Optional[int] = None,
    min_tokens: Optional[int] = None,
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """
    Decorator to define expectations for LLM calls.
    
    Use with @trace to automatically validate responses.
    
    Usage:
        @trace(provider="gemini")
        @expect(must_include=["refund"], max_latency_ms=1500)
        def reply(prompt):
            ...
    
    Args:
        must_include: Substrings that must appear in response
        must_not_include: Substrings that must NOT appear
        max_latency_ms: Maximum latency threshold
        min_tokens: Minimum token count
        
    Returns:
        Decorated function with attached expectations
    """
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        # Store expectations for this function
        _function_expectations[func] = {
            "must_include": must_include,
            "must_not_include": must_not_include,
            "max_latency_ms": max_latency_ms,
            "min_tokens": min_tokens,
        }
        return func
    return decorator


def trace(
    provider: str = "openai",
    model: Optional[str] = None,
    capture_layer: Optional[CaptureLayer] = None,
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """
    Decorator to trace LLM calls.
    
    Usage:
        @trace(provider="openai", model="gpt-4")
        def my_llm_call(messages):
            return openai.chat.completions.create(
                model="gpt-4",
                messages=messages
            )
    
    Args:
        provider: The LLM provider name
        model: Optional model name (can be extracted from response)
        capture_layer: Optional custom capture layer instance
        
    Returns:
        Decorated function that traces calls
    """
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            layer = capture_layer or get_capture_layer()
            
            # Phase 13: Get execution context
            execution_id = get_execution_id()
            parent_node_id = get_parent_node_id()
            
            # Try to extract messages from args/kwargs
            messages = _extract_messages(args, kwargs)
            parameters = _extract_parameters(kwargs)
            
            # Execute the function
            import time
            start_time = time.perf_counter()
            result = func(*args, **kwargs)
            latency_ms = int((time.perf_counter() - start_time) * 1000)
            
            # Determine the model
            actual_model = model or _extract_model(kwargs, result)
            
            # Get expectations if any
            expectations = _function_expectations.get(func)
            
            # Create and store the trace (with verdict if expectations exist)
            node_id = _create_trace(
                layer=layer,
                provider=provider,
                model=actual_model,
                messages=messages,
                parameters=parameters,
                result=result,
                latency_ms=latency_ms,
                expectations=expectations,
                execution_id=execution_id,
                parent_node_id=parent_node_id,
            )
            
            # Phase 13: Push this node for child tracking, then pop after
            push_node(node_id)
            pop_node()
            
            return result
        
        return wrapper
    return decorator


def _extract_messages(args: tuple, kwargs: dict) -> list[dict[str, str]]:
    """Extract messages from function arguments."""
    # Check kwargs first
    if "messages" in kwargs:
        return kwargs["messages"]
    
    # Check first positional argument
    if args and isinstance(args[0], list):
        first = args[0]
        if first and isinstance(first[0], dict) and "role" in first[0]:
            return first
    
    return []


def _extract_parameters(kwargs: dict) -> dict[str, Any]:
    """Extract LLM parameters from kwargs."""
    param_keys = [
        "temperature",
        "max_tokens",
        "top_p",
        "frequency_penalty",
        "presence_penalty",
        "stop",
    ]
    return {k: kwargs[k] for k in param_keys if k in kwargs}


def _extract_model(kwargs: dict, result: Any) -> str:
    """Extract model name from kwargs or result."""
    if "model" in kwargs:
        return kwargs["model"]
    
    if hasattr(result, "model"):
        return result.model
    
    return "unknown"


def _create_trace(
    layer: CaptureLayer,
    provider: str,
    model: str,
    messages: list[dict[str, str]],
    parameters: dict[str, Any],
    result: Any,
    latency_ms: int,
    expectations: Optional[dict[str, Any]] = None,
    execution_id: Optional[str] = None,
    parent_node_id: Optional[str] = None,
) -> str:
    """Create and store a trace from the captured data. Returns node_id."""
    from sdk.schema import (
        Trace,
        TraceRequest,
        TraceResponse,
        TraceRuntime,
        TraceMessage,
        TraceParameters,
        Verdict,
    )
    
    # Build request
    trace_messages = [TraceMessage(**msg) for msg in messages] if messages else []
    trace_params = TraceParameters(**parameters) if parameters else TraceParameters()
    
    request = TraceRequest(
        provider=provider,
        model=model,
        messages=trace_messages,
        parameters=trace_params,
    )
    
    # Build response
    response_text = layer._extract_response_text(result)
    response = TraceResponse(
        text=response_text,
        latency_ms=latency_ms,
        usage=layer._extract_usage(result),
    )
    
    # Build runtime
    runtime = TraceRuntime(
        library=layer._detect_library(provider),
        version=layer._get_library_version(provider),
    )
    
    # Evaluate expectations and create verdict (computed at trace creation time)
    verdict = None
    if expectations:
        from sdk.expectations import evaluate
        verdict = evaluate(
            response_text=response_text,
            latency_ms=latency_ms,
            must_include=expectations.get("must_include"),
            must_not_include=expectations.get("must_not_include"),
            max_latency_ms=expectations.get("max_latency_ms"),
            min_tokens=expectations.get("min_tokens"),
        )
    
    # Create and store trace with execution context
    from uuid import uuid4
    node_id = str(uuid4())
    
    trace = Trace(
        request=request,
        response=response,
        runtime=runtime,
        verdict=verdict,
        execution_id=execution_id or str(uuid4()),
        node_id=node_id,
        parent_node_id=parent_node_id,
    )
    
    layer._store_trace(trace)
    return node_id

