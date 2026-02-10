"""
Traces Routes

Endpoints for trace CRUD operations.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import datetime

from phylax._internal.schema import Trace
from phylax.server.storage.files import FileStorage

router = APIRouter()
storage = FileStorage()


@router.get("/traces")
async def list_traces(
    limit: int = Query(default=50, le=100),
    offset: int = Query(default=0, ge=0),
    model: Optional[str] = None,
    provider: Optional[str] = None,
    date: Optional[str] = None,
) -> dict:
    """
    List all traces with optional filtering.
    
    Args:
        limit: Maximum number of traces to return
        offset: Number of traces to skip
        model: Filter by model name
        provider: Filter by provider
        date: Filter by date (YYYY-MM-DD format)
    """
    traces = storage.list_traces(
        limit=limit,
        offset=offset,
        model=model,
        provider=provider,
        date=date,
    )
    
    total = storage.count_traces(model=model, provider=provider, date=date)
    
    return {
        "traces": [t.model_dump() for t in traces],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get("/traces/{trace_id}")
async def get_trace(trace_id: str) -> dict:
    """Get a specific trace by ID."""
    trace = storage.get_trace(trace_id)
    
    if trace is None:
        raise HTTPException(status_code=404, detail=f"Trace {trace_id} not found")
    
    return trace.model_dump()


@router.post("/traces")
async def create_trace(trace: Trace) -> dict:
    """Create a new trace."""
    storage.save_trace(trace)
    return {"status": "created", "trace_id": trace.trace_id}


@router.delete("/traces/{trace_id}")
async def delete_trace(trace_id: str) -> dict:
    """Delete a trace by ID."""
    success = storage.delete_trace(trace_id)
    
    if not success:
        raise HTTPException(status_code=404, detail=f"Trace {trace_id} not found")
    
    return {"status": "deleted", "trace_id": trace_id}


@router.get("/traces/{trace_id}/lineage")
async def get_trace_lineage(trace_id: str) -> dict:
    """Get the lineage chain for a trace (original → replays)."""
    trace = storage.get_trace(trace_id)
    
    if trace is None:
        raise HTTPException(status_code=404, detail=f"Trace {trace_id} not found")
    
    lineage = storage.get_lineage(trace_id)
    
    return {
        "trace_id": trace_id,
        "lineage": [t.model_dump() for t in lineage],
    }


# =============================================================================
# Golden Reference Endpoints (Bless/Unbless)
# =============================================================================

@router.post("/traces/{trace_id}/bless")
async def bless_trace(trace_id: str) -> dict:
    """
    Mark a trace as a golden reference.
    
    Requirements:
    - Trace must exist
    - Trace must have a passing verdict
    
    Returns:
        Blessed trace data with metadata
    """
    trace = storage.get_trace(trace_id)
    
    if trace is None:
        raise HTTPException(status_code=404, detail=f"Trace {trace_id} not found")
    
    # Validate trace has passing verdict
    if not trace.verdict:
        raise HTTPException(
            status_code=400, 
            detail="PHYLAX_E201: Cannot bless trace without verdict"
        )
    
    if trace.verdict.status != "pass":
        raise HTTPException(
            status_code=400, 
            detail="PHYLAX_E201: Cannot bless a failing trace"
        )
    
    # Bless the trace
    blessed = storage.bless_trace(trace_id)
    
    if blessed is None:
        raise HTTPException(status_code=500, detail="Failed to bless trace")
    
    return {
        "status": "blessed",
        "trace_id": trace_id,
        "blessed_at": blessed.metadata.get("blessed_at"),
        "output_hash": blessed.metadata.get("output_hash"),
    }


@router.delete("/traces/{trace_id}/bless")
async def unbless_trace(trace_id: str) -> dict:
    """Remove golden status from a trace."""
    trace = storage.get_trace(trace_id)
    
    if trace is None:
        raise HTTPException(status_code=404, detail=f"Trace {trace_id} not found")
    
    if not trace.blessed:
        raise HTTPException(status_code=400, detail="Trace is not blessed")
    
    success = storage.unbless_trace(trace_id)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to unbless trace")
    
    return {"status": "unblessed", "trace_id": trace_id}


@router.get("/goldens")
async def list_golden_traces() -> dict:
    """List all blessed (golden) traces."""
    goldens = storage.list_blessed_traces()
    
    return {
        "goldens": [t.model_dump() for t in goldens],
        "count": len(goldens),
    }


# =============================================================================
# Phase 14: Graph Endpoints
# =============================================================================

@router.get("/executions")
async def list_executions() -> dict:
    """List all unique execution IDs."""
    executions = storage.list_executions()
    return {"executions": executions, "count": len(executions)}


@router.get("/executions/{execution_id}")
async def get_execution(execution_id: str) -> dict:
    """Get all traces for an execution."""
    traces = storage.get_traces_by_execution(execution_id)
    
    if not traces:
        raise HTTPException(status_code=404, detail=f"Execution {execution_id} not found")
    
    return {
        "execution_id": execution_id,
        "traces": [t.model_dump() for t in traces],
        "count": len(traces),
    }


@router.get("/executions/{execution_id}/graph")
async def get_execution_graph(execution_id: str) -> dict:
    """Get the execution graph for a specific execution."""
    graph = storage.get_execution_graph(execution_id)
    
    if graph is None:
        raise HTTPException(status_code=404, detail=f"Execution {execution_id} not found")
    
    return graph.model_dump()


# =============================================================================
# Phase 18: Performance Analysis Endpoints
# =============================================================================

@router.get("/executions/{execution_id}/analysis")
async def analyze_execution(execution_id: str) -> dict:
    """
    Phase 18: Complete performance analysis for an execution.
    
    Returns:
    - Critical path (longest latency chain)
    - Bottleneck nodes
    - Graph verdict
    """
    graph = storage.get_execution_graph(execution_id)
    
    if graph is None:
        raise HTTPException(status_code=404, detail=f"Execution {execution_id} not found")
    
    return {
        "execution_id": execution_id,
        "node_count": graph.node_count,
        "total_latency_ms": graph.total_latency_ms,
        "critical_path": graph.critical_path(),
        "bottlenecks": graph.find_bottlenecks(top_n=3),
        "verdict": graph.compute_verdict().model_dump(),
    }


# =============================================================================
# Phase 23: Graph Diff Endpoints
# =============================================================================

@router.get("/executions/{exec_a}/diff/{exec_b}")
async def diff_executions(exec_a: str, exec_b: str) -> dict:
    """
    Phase 23: Compare two execution graphs.
    
    Returns differences in:
    - Added/removed nodes
    - Latency changes
    - Verdict changes
    """
    graph_a = storage.get_execution_graph(exec_a)
    if graph_a is None:
        raise HTTPException(status_code=404, detail=f"Execution {exec_a} not found")
    
    graph_b = storage.get_execution_graph(exec_b)
    if graph_b is None:
        raise HTTPException(status_code=404, detail=f"Execution {exec_b} not found")
    
    diff = graph_a.diff_with(graph_b)
    
    return diff.model_dump()


# =============================================================================
# Phase 24: Investigation Path Endpoints
# =============================================================================

@router.get("/executions/{execution_id}/investigate")
async def get_investigation_path(execution_id: str) -> dict:
    """
    Phase 24: Get suggested investigation path for failure localization.
    
    Returns deterministic graph traversal (not AI) for localizing failures:
    1. First failure identification
    2. Input review
    3. Validation check
    4. Blast radius analysis
    """
    graph = storage.get_execution_graph(execution_id)
    
    if graph is None:
        raise HTTPException(status_code=404, detail=f"Execution {execution_id} not found")
    
    steps = graph.investigation_path()
    verdict = graph.compute_verdict()
    
    return {
        "execution_id": execution_id,
        "verdict": verdict.status,
        "steps": steps,
    }


# =============================================================================
# Phase 25: Enterprise Hardening Endpoints
# =============================================================================

@router.get("/executions/{execution_id}/snapshot")
async def create_snapshot(execution_id: str) -> dict:
    """
    Phase 25: Create an immutable snapshot with integrity hash.
    
    Returns the graph with:
    - integrity_hash (SHA256)
    - snapshot_at timestamp
    """
    graph = storage.get_execution_graph(execution_id)
    
    if graph is None:
        raise HTTPException(status_code=404, detail=f"Execution {execution_id} not found")
    
    snapshot = graph.to_snapshot()
    
    return snapshot.model_dump()


@router.get("/executions/{execution_id}/export")
async def export_graph(execution_id: str, format: str = "json") -> dict:
    """
    Phase 25: Export graph as artifact for auditing.
    
    Args:
        format: Export format (json only for now)
        
    Returns:
        Graph data with integrity metadata
    """
    graph = storage.get_execution_graph(execution_id)
    
    if graph is None:
        raise HTTPException(status_code=404, detail=f"Execution {execution_id} not found")
    
    snapshot = graph.to_snapshot()
    
    return {
        "execution_id": execution_id,
        "format": format,
        "integrity_hash": snapshot.integrity_hash,
        "snapshot_at": snapshot.snapshot_at,
        "data": snapshot.model_dump(),
    }


@router.get("/executions/{execution_id}/verify")
async def verify_graph(execution_id: str, expected_hash: Optional[str] = None) -> dict:
    """
    Phase 25: Verify graph integrity.
    
    Args:
        expected_hash: Optional hash to compare against
        
    Returns:
        Verification result
    """
    graph = storage.get_execution_graph(execution_id)
    
    if graph is None:
        raise HTTPException(status_code=404, detail=f"Execution {execution_id} not found")
    
    computed_hash = graph.compute_hash()
    
    if expected_hash:
        matches = computed_hash == expected_hash
    else:
        matches = graph.verify_integrity() if graph.integrity_hash else None
    
    return {
        "execution_id": execution_id,
        "computed_hash": computed_hash,
        "expected_hash": expected_hash or graph.integrity_hash,
        "verified": matches,
    }
