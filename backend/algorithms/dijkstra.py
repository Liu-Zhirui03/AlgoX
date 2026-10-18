"""Dijkstra adapter showing minimum-distance selection and edge relaxation."""

from inspect import getsource
from pydantic import model_validator
from backend.algorithms.graphs import DEFAULT_GRAPH, Recorder, StartGraphInput
from backend.schemas import AlgorithmResult
from examples.dijkstra import dijkstra

ALGORITHM_ID = "dijkstra"
TITLE = "Dijkstra's Algorithm"
CATEGORY = "Greedy Algorithms"
RENDERER = "weighted-graph"
DEFAULT_INPUT = {**DEFAULT_GRAPH, "start": "A"}
PLAYGROUND_FILE = "dijkstra.html"


class DijkstraInput(StartGraphInput):
    @model_validator(mode="after")
    def nonnegative_weights(self):
        if any(edge.weight < 0 for edge in self.edges):
            raise ValueError("Dijkstra requires nonnegative edge weights.")
        return self


def dijkstra_steps(payload: DijkstraInput):
    recorder = Recorder(payload)
    state = recorder.state
    state.distances = {node: None for node in payload.nodes}
    state.parents = {node: None for node in payload.nodes}
    state.distances[payload.start] = 0
    adjacency = {node: [] for node in payload.nodes}
    for index, edge in enumerate(payload.edges):
        adjacency[edge.source].append((edge.target, edge.weight, index))
        adjacency[edge.target].append((edge.source, edge.weight, index))
    predecessor_edges = {}
    recorder.record("initial", f"Start at {payload.start} with distance 0. Other nodes are initially unreachable.")
    while True:
        candidates = [node for node in payload.nodes if node not in state.visited and state.distances[node] is not None]
        if not candidates:
            break
        current = min(candidates, key=lambda node: state.distances[node])
        state.currentNode = current
        state.currentEdge = None
        state.visited.append(current)
        recorder.record("settle", f"Settle {current}: it has the smallest tentative distance, {state.distances[current]}.")
        for neighbor, weight, index in adjacency[current]:
            if neighbor in state.visited:
                continue
            state.currentEdge = index
            candidate = state.distances[current] + weight
            recorder.record("inspect", f"Inspect {current}-{neighbor} (weight {weight}): candidate distance {state.distances[current]} + {weight} = {candidate}.")
            if state.distances[neighbor] is None or candidate < state.distances[neighbor]:
                state.distances[neighbor] = candidate
                state.parents[neighbor] = current
                predecessor_edges[neighbor] = index
                state.selectedEdges = sorted(predecessor_edges.values())
                recorder.record("relax", f"Improve distance to {neighbor} to {candidate}; its predecessor is now {current}.")
            else:
                recorder.record("skip", f"Keep {neighbor}'s existing distance {state.distances[neighbor]}; this edge gives no improvement.")
    state.currentNode = None
    state.currentEdge = None
    missing = [node for node in payload.nodes if state.distances[node] is None]
    recorder.record("complete", "Shortest paths are complete." + (f" Unreachable nodes: {', '.join(missing)}." if missing else " All nodes are reachable."))
    return recorder.steps


def run(payload: DijkstraInput) -> AlgorithmResult:
    edges = [(edge.source, edge.target, edge.weight) for edge in payload.edges]
    output = dijkstra(payload.nodes, edges, payload.start)
    paths = {}
    for node in payload.nodes:
        if output["distances"][node] is None:
            paths[node] = None
            continue
        path = []
        current = node
        while current is not None:
            path.append(current)
            current = output["parents"][current]
        paths[node] = list(reversed(path))
    return AlgorithmResult(algorithmId=ALGORITHM_ID, title=TITLE, renderer=RENDERER,
        source=getsource(dijkstra), input=payload.model_dump(), output={**output, "paths": paths},
        steps=dijkstra_steps(payload))
