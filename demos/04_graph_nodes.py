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

from phylax._internal.graph import (
    ExecutionGraph,
    NodeRole,
    GraphStage,
)
from phylax._internal.schema import Verdict
import phylax


def create_sample_graph():
    """Create a sample execution graph for demonstration."""
    graph = ExecutionGraph(execution_id="demo-execution-001")
    
    # Add root node (first call in execution)
    graph.add_node(
        node_id="node-1",
        parent_id=None,
        verdict=Verdict(status="pass", violations=[], severity="none"),
    )
    
    # Add child nodes
    graph.add_node(
        node_id="node-2",
        parent_id="node-1",
        verdict=Verdict(status="pass", violations=[], severity="none"),
    )
    
    graph.add_node(
        node_id="node-3",
        parent_id="node-1",
        verdict=Verdict(status="fail", violations=["latency exceeded 1000ms"], severity="high"),
    )
    
    # Add leaf node
    graph.add_node(
        node_id="node-4",
        parent_id="node-2",
        verdict=Verdict(status="pass", violations=[], severity="none"),
    )
    
    return graph


def main():
    print("=" * 60)
    print("🧪 DEMO 04: Graph Nodes")
    print("=" * 60)
    print(f"📦 Phylax version: {phylax.__version__}")
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
            role = "ROOT" if node.parent_id is None else "CHILD"
            children = graph.get_children(node_id)
            if not children:
                role = "LEAF"
            status = "✅" if node.verdict.status == "pass" else "❌"
            print(f"   {node_id}: {role} {status}")
    print()
    
    # Compute overall verdict
    verdict = graph.compute_verdict()
    print("📍 Graph Verdict:")
    print(f"   Status: {verdict.status.upper()}")
    print(f"   Failed nodes: {verdict.failed_count}")
    print(f"   Tainted nodes: {verdict.tainted_count}")
    if verdict.root_cause_node:
        print(f"   Root cause: {verdict.root_cause_node}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
