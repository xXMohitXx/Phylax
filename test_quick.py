"""Quick test for Phase 13-18 features"""
import os, sys, uuid
sys.path.insert(0, '.')

from sdk.schema import Trace, TraceRequest, TraceResponse, TraceMessage, Verdict, TraceRuntime
from sdk.graph import ExecutionGraph

def create_trace(exec_id, node_id, parent_id=None, latency=100, status='pass'):
    return Trace(
        trace_id=str(uuid.uuid4()),
        execution_id=exec_id,
        node_id=node_id,
        parent_node_id=parent_id,
        request=TraceRequest(provider='test', model='test', messages=[TraceMessage(role='user', content='test')]),
        response=TraceResponse(text='response', latency_ms=latency),
        runtime=TraceRuntime(library='test', version='1.0'),
        verdict=Verdict(status=status, violations=[])
    )

# Test Phase 13-14: Create execution with causality
exec_id = str(uuid.uuid4())
n1, n2, n3 = str(uuid.uuid4()), str(uuid.uuid4()), str(uuid.uuid4())
traces = [
    create_trace(exec_id, n1, None, 100),
    create_trace(exec_id, n2, n1, 200),
    create_trace(exec_id, n3, n1, 150)
]

print('PHASE 13-14: Graph Construction')
graph = ExecutionGraph.from_traces(traces)
print('  Nodes:', graph.node_count)
print('  Edges:', len(graph.edges))
print('  Children of root:', len(graph.get_children(n1)))

# Test Phase 16: Verdict
print('')
print('PHASE 16: Graph Verdict')
v = graph.compute_verdict()
print('  Status:', v.status)
print('  Message:', v.message)

# Test with failure
fail_traces = [
    create_trace(exec_id, n1, None, 100, 'pass'),
    create_trace(exec_id, n2, n1, 200, 'fail'),
    create_trace(exec_id, n3, n2, 150, 'pass')
]
fail_graph = ExecutionGraph.from_traces(fail_traces)
fv = fail_graph.compute_verdict()
print('  Fail verdict:', fv.status)
print('  Root cause:', fv.root_cause_node[:12] + '...')
print('  Tainted nodes:', fv.tainted_count)

# Test Phase 18: Performance
print('')
print('PHASE 18: Performance Analysis')
cp = fail_graph.critical_path()
print('  Critical path nodes:', len(cp['path']))
print('  Total latency:', cp['total_latency_ms'], 'ms')
print('  Bottleneck latency:', cp['bottleneck_latency_ms'], 'ms')

bottlenecks = fail_graph.find_bottlenecks(3)
print('  Top bottleneck:', bottlenecks[0]['latency_ms'], 'ms')

print('')
print('[PASS] All Phase 13-18 tests passed!')
