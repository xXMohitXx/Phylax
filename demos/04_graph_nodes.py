"""
Demo 04: Graph Nodes

Demonstrates:
- ExecutionGraph construction
- Node roles (ROOT, CHILD, LEAF)
- Graph traversal and verdict computation

Requirements:
- pip install phylax[all]
"""

import sys

from phylax import __version__
from phylax.graph import (
    ExecutionGraph,
    NodeRole,
    GraphStage,
    GraphNode,
    GraphEdge,
    GraphVerdict,
)


def create_sample_graph():
    """Create a sample execution graph for demonstration."""
    # Create nodes manually (normally done via from_traces)
    nodes = [
        GraphNode(
            node_id="node-1",
            trace_id="trace-1",
            role=NodeRole.INPUT,
            human_label="Root node",
            verdict_status="pass",
        ),
        GraphNode(
            node_id="node-2",
            trace_id="trace-2",
            role=NodeRole.LLM,
            human_label="Child 1",
            verdict_status="pass",
        ),
        GraphNode(
            node_id="node-3",
            trace_id="trace-3",
            role=NodeRole.LLM,
            human_label="Child 2 (failed)",
            verdict_status="fail",
        ),
        GraphNode(
            node_id="node-4",
            trace_id="trace-4",
            role=NodeRole.OUTPUT,
            human_label="Leaf node",
            verdict_status="pass",
        ),
    ]
    
    # Create edges (parent -> child)
    edges = [
        GraphEdge(from_node="node-1", to_node="node-2"),
        GraphEdge(from_node="node-1", to_node="node-3"),
        GraphEdge(from_node="node-2", to_node="node-4"),
    ]
    
    # Construct immutable graph
    graph = ExecutionGraph(
        execution_id="demo-execution-001",
        nodes=nodes,
        edges=edges,
        root_node_id="node-1",
        node_count=4,
    )
    
    return graph


def main():
    print("=" * 60)
    print("🧪 DEMO 04: Graph Nodes")
    print("=" * 60)
    print(f"📦 Phylax version: {__version__}")
    print()
    
    # Create graph
    graph = create_sample_graph()
    
    print(f"📊 Graph: {graph.execution_id}")
    print(f"   Nodes: {graph.node_count}")
    print()
    
    # Show node structure
    print("📍 Node Structure:")
    print("   node-1 (ROOT)")
    print("   ├── node-2 (CHILD)")
    print("   │   └── node-4 (LEAF)")
    print("   └── node-3 (CHILD, FAILED)")
    print()
    
    # Get node roles
    print("📍 Node Roles:")
    for node_id in ["node-1", "node-2", "node-3", "node-4"]:
        node = graph.get_node(node_id)
        if node:
            role = node.role.value.upper()
            children = graph.get_children(node_id)
            if not children:
                role = "LEAF"
            status = "✅" if node.verdict_status == "pass" else "❌"
            print(f"   {node_id}: {role} {status}")
    print()
    
    # Compute overall verdict
    verdict = graph.compute_verdict()
    print("📍 Graph Verdict:")
    print(f"   Status: {verdict.status.upper()}")
    print(f"   Failed nodes: {verdict.failed_count}")
    print(f"   Tainted nodes: {verdict.tainted_count}")
    if verdict.first_failing_node:
        print(f"   First failing node: {verdict.first_failing_node}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
