"""Kruskal adapter with sorted edges, component unions, and cycle rejection."""

from inspect import getsource
from backend.algorithms.graphs import DEFAULT_GRAPH, GraphInput, Recorder
from backend.schemas import AlgorithmResult
from examples.kruskal import kruskal

ALGORITHM_ID = "kruskal"
TITLE = "Kruskal's Algorithm"
CATEGORY = "Greedy Algorithms"
RENDERER = "weighted-graph"
DEFAULT_INPUT = DEFAULT_GRAPH
PLAYGROUND_FILE = "minimum-spanning-tree.html"


def kruskal_steps(payload: GraphInput):
    recorder = Recorder(payload)
    state = recorder.state
    parent = {node: node for node in payload.nodes}
    rank = {node: 0 for node in payload.nodes}

    def find(node):
        while parent[node] != node:
            parent[node] = parent[parent[node]]
            node = parent[node]
        return node

    def components():
        groups = {}
        for node in payload.nodes:
            groups.setdefault(find(node), []).append(node)
        return list(groups.values())

    state.components = components()
    state.edgeOrder = sorted(range(len(payload.edges)), key=lambda index: (payload.edges[index].weight, index))
    recorder.record("initial", "Sort all edges by weight. Start with each node in its own component; ties keep input order.")
    for index in state.edgeOrder.copy():
        edge = payload.edges[index]
        state.currentEdge = index
        recorder.record("inspect", f"Inspect {edge.source}-{edge.target}, weight {edge.weight}: test whether its endpoints are in different components.")
        state.edgeOrder.remove(index)
        left, right = find(edge.source), find(edge.target)
        if left == right:
            state.rejectedEdges.append(index)
            recorder.record("reject", f"Reject {edge.source}-{edge.target}: both endpoints are already connected, so it would create a cycle.")
        else:
            if rank[left] < rank[right]:
                left, right = right, left
            parent[right] = left
            if rank[left] == rank[right]:
                rank[left] += 1
            state.selectedEdges.append(index)
            state.totalWeight += edge.weight
            state.components = components()
            state.visited = [node for node in payload.nodes if any(node in (payload.edges[item].source, payload.edges[item].target) for item in state.selectedEdges)]
            recorder.record("accept", f"Accept {edge.source}-{edge.target}, join its components, and add {edge.weight}. Total weight: {state.totalWeight}.")
    state.currentEdge = None
    state.visited = payload.nodes.copy()
    recorder.record("complete", f"Minimum spanning {'tree' if len(state.components) == 1 else 'forest'} complete: total weight {state.totalWeight}, {len(state.components)} component(s).")
    return recorder.steps


def run(payload: GraphInput) -> AlgorithmResult:
    steps = kruskal_steps(payload)
    output = kruskal(payload.nodes, [(edge.source, edge.target, edge.weight) for edge in payload.edges])
    components = steps[-1].stateData.components
    return AlgorithmResult(algorithmId=ALGORITHM_ID, title=TITLE, renderer=RENDERER,
        source=getsource(kruskal), input=payload.model_dump(),
        output={**output, "components": components, "connected": len(components) == 1}, steps=steps)
