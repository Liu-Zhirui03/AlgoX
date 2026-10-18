"""Prim adapter with cheapest cut-edge selection and component restarts."""

from inspect import getsource
from backend.algorithms.graphs import DEFAULT_GRAPH, Recorder, StartGraphInput
from backend.schemas import AlgorithmResult
from examples.prim import prim

ALGORITHM_ID = "prim"
TITLE = "Prim's Algorithm"
CATEGORY = "Greedy Algorithms"
RENDERER = "weighted-graph"
DEFAULT_INPUT = {**DEFAULT_GRAPH, "start": "A"}
PLAYGROUND_FILE = "minimum-spanning-tree.html"


def prim_steps(payload: StartGraphInput):
    recorder = Recorder(payload)
    state = recorder.state
    recorder.record("initial", f"Grow a minimum spanning forest from {payload.start}. Always choose the lightest edge crossing the visited cut.")
    for root in [payload.start] + [node for node in payload.nodes if node != payload.start]:
        if root in state.visited:
            continue
        state.visited.append(root)
        component = [root]
        state.components.append(component)
        state.currentNode = root
        state.currentEdge = None
        recorder.record("start_component", f"Start a new component at {root}. This also handles isolated nodes.")
        while True:
            candidates = [index for index, edge in enumerate(payload.edges) if (edge.source in state.visited) != (edge.target in state.visited)]
            state.edgeOrder = sorted(candidates, key=lambda index: (payload.edges[index].weight, index))
            if not candidates:
                break
            index = state.edgeOrder[0]
            edge = payload.edges[index]
            state.currentEdge = index
            recorder.record("inspect", f"Choose the lightest crossing edge {edge.source}-{edge.target}, weight {edge.weight}; ties keep input order.")
            new_node = edge.target if edge.source in state.visited else edge.source
            state.visited.append(new_node)
            component.append(new_node)
            state.currentNode = new_node
            state.selectedEdges.append(index)
            state.totalWeight += edge.weight
            state.edgeOrder = sorted(
                [item for item, candidate in enumerate(payload.edges)
                 if (candidate.source in state.visited) != (candidate.target in state.visited)],
                key=lambda item: (payload.edges[item].weight, item),
            )
            recorder.record("accept", f"Accept {edge.source}-{edge.target}, add node {new_node}, and grow this component. Total weight: {state.totalWeight}.")
    state.currentEdge = None
    state.currentNode = None
    state.edgeOrder = []
    recorder.record("complete", f"Minimum spanning {'tree' if len(state.components) == 1 else 'forest'} complete: total weight {state.totalWeight}, {len(state.components)} component(s).")
    return recorder.steps


def run(payload: StartGraphInput) -> AlgorithmResult:
    steps = prim_steps(payload)
    output = prim(payload.nodes, [(edge.source, edge.target, edge.weight) for edge in payload.edges], payload.start)
    components = steps[-1].stateData.components
    return AlgorithmResult(algorithmId=ALGORITHM_ID, title=TITLE, renderer=RENDERER,
        source=getsource(prim), input=payload.model_dump(),
        output={**output, "components": components, "connected": len(components) == 1}, steps=steps)
