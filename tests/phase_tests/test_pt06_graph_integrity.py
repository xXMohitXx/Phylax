"""
Phase-test 6 — Execution Graph Integrity

Goal: Verify complex execution graphs (10-20 nodes) with nested contexts,
parent-child relationships, critical path, verdict computation, and diff.
"""
import pytest
from phylax import ExecutionGraph, GraphStage, NodeRole
from phylax._internal.graph import GraphNode, GraphEdge, GraphVerdict


# ---------------------------------------------------------------------------
# Helpers — build graph directly (no traces needed for graph tests)
# ---------------------------------------------------------------------------

def _build_linear_graph(n: int) -> ExecutionGraph:
    """Build a linear graph: node_0 -> node_1 -> ... -> node_(n-1)."""
    nodes = []
    edges = []
    for i in range(n):
        role = NodeRole.INPUT if i == 0 else (NodeRole.OUTPUT if i == n-1 else NodeRole.LLM)
        nodes.append(GraphNode(
            node_id=f"node_{i}",
            trace_id=f"trace_{i}",
            role=role,
            human_label=f"Step {i}",
            node_type="llm",
            model="test-model",
            provider="test",
            latency_ms=(i + 1) * 100,
            verdict_status="pass",
        ))
        if i > 0:
            edges.append(GraphEdge(from_node=f"node_{i-1}", to_node=f"node_{i}"))

    total_latency = sum(n.latency_ms for n in nodes)
    return ExecutionGraph(
        execution_id="exec-linear",
        nodes=nodes,
        edges=edges,
        root_node_id="node_0",
        total_latency_ms=total_latency,
        node_count=len(nodes),
    )


def _build_diamond_graph() -> ExecutionGraph:
    """Build a diamond graph: A -> B, A -> C, B -> D, C -> D."""
    nodes = [
        GraphNode(node_id="A", trace_id="t-A", role=NodeRole.INPUT,
                  human_label="Start", latency_ms=100, verdict_status="pass"),
        GraphNode(node_id="B", trace_id="t-B", role=NodeRole.LLM,
                  human_label="Path B", latency_ms=300, verdict_status="pass"),
        GraphNode(node_id="C", trace_id="t-C", role=NodeRole.LLM,
                  human_label="Path C", latency_ms=200, verdict_status="pass"),
        GraphNode(node_id="D", trace_id="t-D", role=NodeRole.OUTPUT,
                  human_label="End", latency_ms=100, verdict_status="pass"),
    ]
    edges = [
        GraphEdge(from_node="A", to_node="B"),
        GraphEdge(from_node="A", to_node="C"),
        GraphEdge(from_node="B", to_node="D"),
        GraphEdge(from_node="C", to_node="D"),
    ]
    return ExecutionGraph(
        execution_id="exec-diamond",
        nodes=nodes,
        edges=edges,
        root_node_id="A",
        total_latency_ms=700,
        node_count=4,
    )


def _build_complex_graph() -> ExecutionGraph:
    """Build a 15-node complex graph simulating real agent workflow."""
    nodes = [
        # Input layer
        GraphNode(node_id="input", trace_id="t-0", role=NodeRole.INPUT,
                  human_label="User Request", latency_ms=10, verdict_status="pass"),
        # Transform layer
        GraphNode(node_id="parse", trace_id="t-1", role=NodeRole.TRANSFORM,
                  human_label="Parse Input", latency_ms=20, verdict_status="pass"),
        # LLM reasoning layer (parallel branches)
        GraphNode(node_id="llm_classify", trace_id="t-2", role=NodeRole.LLM,
                  human_label="Classify Intent", model="gpt-4", latency_ms=500, verdict_status="pass"),
        GraphNode(node_id="llm_extract", trace_id="t-3", role=NodeRole.LLM,
                  human_label="Extract Entities", model="gpt-4", latency_ms=400, verdict_status="pass"),
        GraphNode(node_id="llm_sentiment", trace_id="t-4", role=NodeRole.LLM,
                  human_label="Sentiment Analysis", model="gpt-4", latency_ms=300, verdict_status="pass"),
        # Tool calls
        GraphNode(node_id="tool_db", trace_id="t-5", role=NodeRole.TOOL,
                  human_label="Database Lookup", latency_ms=150, verdict_status="pass"),
        GraphNode(node_id="tool_api", trace_id="t-6", role=NodeRole.TOOL,
                  human_label="External API", latency_ms=200, verdict_status="pass"),
        # Second LLM layer
        GraphNode(node_id="llm_reason", trace_id="t-7", role=NodeRole.LLM,
                  human_label="Reasoning Step", model="gpt-4", latency_ms=600, verdict_status="pass"),
        GraphNode(node_id="llm_draft", trace_id="t-8", role=NodeRole.LLM,
                  human_label="Draft Response", model="gpt-4", latency_ms=450, verdict_status="pass"),
        # Validation layer
        GraphNode(node_id="val_safety", trace_id="t-9", role=NodeRole.VALIDATION,
                  human_label="Safety Check", latency_ms=50, verdict_status="pass"),
        GraphNode(node_id="val_quality", trace_id="t-10", role=NodeRole.VALIDATION,
                  human_label="Quality Check", latency_ms=40, verdict_status="pass"),
        GraphNode(node_id="val_compliance", trace_id="t-11", role=NodeRole.VALIDATION,
                  human_label="Compliance Check", latency_ms=30, verdict_status="pass"),
        # Final LLM
        GraphNode(node_id="llm_refine", trace_id="t-12", role=NodeRole.LLM,
                  human_label="Refine Output", model="gpt-4", latency_ms=350, verdict_status="pass"),
        # Output
        GraphNode(node_id="format", trace_id="t-13", role=NodeRole.TRANSFORM,
                  human_label="Format Response", latency_ms=15, verdict_status="pass"),
        GraphNode(node_id="output", trace_id="t-14", role=NodeRole.OUTPUT,
                  human_label="Final Output", latency_ms=5, verdict_status="pass"),
    ]
    edges = [
        GraphEdge(from_node="input", to_node="parse"),
        GraphEdge(from_node="parse", to_node="llm_classify"),
        GraphEdge(from_node="parse", to_node="llm_extract"),
        GraphEdge(from_node="parse", to_node="llm_sentiment"),
        GraphEdge(from_node="llm_classify", to_node="tool_db"),
        GraphEdge(from_node="llm_extract", to_node="tool_api"),
        GraphEdge(from_node="tool_db", to_node="llm_reason"),
        GraphEdge(from_node="tool_api", to_node="llm_reason"),
        GraphEdge(from_node="llm_sentiment", to_node="llm_reason"),
        GraphEdge(from_node="llm_reason", to_node="llm_draft"),
        GraphEdge(from_node="llm_draft", to_node="val_safety"),
        GraphEdge(from_node="llm_draft", to_node="val_quality"),
        GraphEdge(from_node="llm_draft", to_node="val_compliance"),
        GraphEdge(from_node="val_safety", to_node="llm_refine"),
        GraphEdge(from_node="val_quality", to_node="llm_refine"),
        GraphEdge(from_node="val_compliance", to_node="llm_refine"),
        GraphEdge(from_node="llm_refine", to_node="format"),
        GraphEdge(from_node="format", to_node="output"),
    ]
    total = sum(n.latency_ms for n in nodes)
    return ExecutionGraph(
        execution_id="exec-complex",
        nodes=nodes,
        edges=edges,
        root_node_id="input",
        total_latency_ms=total,
        node_count=15,
    )


# ---------------------------------------------------------------------------
# Tests — Basic Graph Structure
# ---------------------------------------------------------------------------

class TestGraphStructure:
    """PT6.1: Graph structure integrity."""

    def test_linear_graph_10_nodes(self):
        g = _build_linear_graph(10)
        assert g.node_count == 10
        assert len(g.nodes) == 10
        assert len(g.edges) == 9

    def test_diamond_graph_structure(self):
        g = _build_diamond_graph()
        assert g.node_count == 4
        assert len(g.edges) == 4

    def test_complex_graph_15_nodes(self):
        g = _build_complex_graph()
        assert g.node_count == 15
        assert len(g.edges) == 18


# ---------------------------------------------------------------------------
# Tests — Parent/Child Relationships
# ---------------------------------------------------------------------------

class TestParentChild:
    """PT6.2: Parent-child relationships must be correct."""

    def test_linear_parent_child(self):
        g = _build_linear_graph(5)
        for i in range(1, 5):
            parent = g.get_parent(f"node_{i}")
            assert parent == f"node_{i-1}", f"node_{i} parent should be node_{i-1}"

    def test_root_has_no_parent(self):
        g = _build_linear_graph(5)
        assert g.get_parent("node_0") is None

    def test_diamond_children_of_a(self):
        g = _build_diamond_graph()
        children = g.get_children("A")
        assert set(children) == {"B", "C"}

    def test_diamond_d_has_two_parents(self):
        """D should have two edges pointing to it (from B and C)."""
        g = _build_diamond_graph()
        parents = [e.from_node for e in g.edges if e.to_node == "D"]
        assert set(parents) == {"B", "C"}

    def test_complex_graph_parse_has_3_children(self):
        g = _build_complex_graph()
        children = g.get_children("parse")
        assert set(children) == {"llm_classify", "llm_extract", "llm_sentiment"}

    def test_complex_graph_llm_reason_has_3_parents(self):
        g = _build_complex_graph()
        parents = [e.from_node for e in g.edges if e.to_node == "llm_reason"]
        assert set(parents) == {"tool_db", "tool_api", "llm_sentiment"}


# ---------------------------------------------------------------------------
# Tests — Topological Order
# ---------------------------------------------------------------------------

class TestTopologicalOrder:
    """PT6.3: Topological ordering must respect edges."""

    def test_linear_topo_order(self):
        g = _build_linear_graph(5)
        order = g.topological_order()
        assert order == [f"node_{i}" for i in range(5)]

    def test_diamond_topo_a_first_d_last(self):
        g = _build_diamond_graph()
        order = g.topological_order()
        assert order[0] == "A"
        assert order[-1] == "D"

    def test_complex_topo_input_before_output(self):
        g = _build_complex_graph()
        order = g.topological_order()
        assert order.index("input") < order.index("output")
        assert order.index("parse") < order.index("llm_classify")
        assert order.index("llm_draft") < order.index("val_safety")


# ---------------------------------------------------------------------------
# Tests — Critical Path
# ---------------------------------------------------------------------------

class TestCriticalPath:
    """PT6.4: Critical path must be accurate."""

    def test_linear_critical_path_is_full_chain(self):
        g = _build_linear_graph(5)
        cp = g.critical_path()
        assert len(cp["path"]) == 5
        assert cp["total_latency_ms"] == sum((i+1)*100 for i in range(5))

    def test_linear_bottleneck_is_last_node(self):
        g = _build_linear_graph(5)
        cp = g.critical_path()
        assert cp["bottleneck_node"] == "node_4"
        assert cp["bottleneck_latency_ms"] == 500

    def test_diamond_critical_path_through_b(self):
        """Path through B (300ms) is longer than through C (200ms)."""
        g = _build_diamond_graph()
        cp = g.critical_path()
        assert "B" in cp["path"], "Critical path should go through B (slower branch)"

    def test_complex_critical_path_exists(self):
        g = _build_complex_graph()
        cp = g.critical_path()
        assert len(cp["path"]) > 0
        assert cp["total_latency_ms"] > 0
        assert cp["bottleneck_node"] is not None


# ---------------------------------------------------------------------------
# Tests — Verdict Computation
# ---------------------------------------------------------------------------

class TestGraphVerdict:
    """PT6.5: Graph-level verdict computation."""

    def test_all_pass_graph(self):
        g = _build_complex_graph()
        v = g.compute_verdict()
        assert v.status == "pass"
        assert v.first_failing_node is None
        assert v.failed_count == 0

    def test_one_failure_detected(self):
        """Inject one failure and verify it's detected."""
        g = _build_complex_graph()
        # Replace one node with a failed version
        new_nodes = []
        for n in g.nodes:
            if n.node_id == "val_safety":
                new_nodes.append(GraphNode(
                    node_id=n.node_id, trace_id=n.trace_id, role=n.role,
                    human_label=n.human_label, latency_ms=n.latency_ms,
                    verdict_status="fail",
                ))
            else:
                new_nodes.append(n)
        g2 = ExecutionGraph(
            execution_id=g.execution_id, nodes=new_nodes, edges=g.edges,
            root_node_id=g.root_node_id, total_latency_ms=g.total_latency_ms,
            node_count=g.node_count,
        )
        v = g2.compute_verdict()
        assert v.status == "fail"
        assert v.failed_count == 1
        assert v.first_failing_node == "val_safety"

    def test_blast_radius(self):
        """Failing val_safety should taint llm_refine, format, output."""
        g = _build_complex_graph()
        tainted = g.get_tainted_nodes("val_safety")
        assert "val_safety" in tainted
        assert "llm_refine" in tainted
        assert "format" in tainted
        assert "output" in tainted


# ---------------------------------------------------------------------------
# Tests — Graph Diff
# ---------------------------------------------------------------------------

class TestGraphDiff:
    """PT6.6: Graph diff engine."""

    def test_identical_graphs_no_changes(self):
        g1 = _build_complex_graph()
        g2 = _build_complex_graph()
        diff = g1.diff_with(g2)
        assert diff.total_changes == 0
        assert diff.verdict_changed is False

    def test_diff_detects_latency_change(self):
        """If a node latency changes >50ms, it should be detected."""
        g1 = _build_diamond_graph()
        nodes2 = []
        for n in g1.nodes:
            if n.node_id == "B":
                nodes2.append(GraphNode(
                    node_id=n.node_id, trace_id=n.trace_id, role=n.role,
                    human_label=n.human_label, latency_ms=n.latency_ms + 100,
                    verdict_status=n.verdict_status,
                ))
            else:
                nodes2.append(n)
        g2 = ExecutionGraph(
            execution_id="exec-diamond-2", nodes=nodes2, edges=g1.edges,
            root_node_id=g1.root_node_id, total_latency_ms=g1.total_latency_ms + 100,
            node_count=g1.node_count,
        )
        diff = g1.diff_with(g2)
        assert diff.total_changes >= 1
        assert diff.latency_delta_ms == 100


# ---------------------------------------------------------------------------
# Tests — Integrity Hash
# ---------------------------------------------------------------------------

class TestGraphIntegrity:
    """PT6.7: Graph integrity hashing."""

    def test_hash_is_deterministic(self):
        g = _build_complex_graph()
        h1 = g.compute_hash()
        h2 = g.compute_hash()
        assert h1 == h2

    def test_snapshot_verifies(self):
        g = _build_complex_graph()
        snapshot = g.to_snapshot()
        assert snapshot.verify_integrity()

    def test_different_graphs_different_hash(self):
        g1 = _build_linear_graph(5)
        g2 = _build_linear_graph(10)
        assert g1.compute_hash() != g2.compute_hash()
