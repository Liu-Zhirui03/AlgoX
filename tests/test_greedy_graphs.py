"""Compare graph results with independent shortest-path and exhaustive forest oracles."""

from itertools import combinations, product
import unittest

from backend.algorithms.graphs import GraphInput, StartGraphInput
from backend.algorithms.dijkstra import DijkstraInput, run as run_dijkstra
from backend.algorithms.kruskal import run as run_kruskal
from backend.algorithms.prim import run as run_prim


def component_groups(nodes, edges):
    remaining = set(nodes)
    groups = []
    while remaining:
        pending = [next(node for node in nodes if node in remaining)]
        group = set()
        while pending:
            node = pending.pop()
            if node in group: continue
            group.add(node)
            for edge in edges:
                if edge[0] == node: pending.append(edge[1])
                if edge[1] == node: pending.append(edge[0])
        remaining -= group
        groups.append(group)
    return groups


def minimum_forest_weight(nodes, edges):
    count = len(component_groups(nodes, edges))
    needed = len(nodes) - count
    best = None
    for indexes in combinations(range(len(edges)), needed):
        subset = [edges[index] for index in indexes]
        if len(component_groups(nodes, subset)) == count:
            weight = sum(edge[2] for edge in subset)
            best = weight if best is None else min(best, weight)
    return best


def shortest_oracle(nodes, edges, start):
    distance = {left: {right: (0 if left == right else float("inf")) for right in nodes} for left in nodes}
    for source, target, weight in edges:
        distance[source][target] = distance[target][source] = weight
    for middle in nodes:
        for left in nodes:
            for right in nodes:
                distance[left][right] = min(distance[left][right], distance[left][middle] + distance[middle][right])
    return {node: None if distance[start][node] == float("inf") else distance[start][node] for node in nodes}


class GreedyGraphTests(unittest.TestCase):
    def graphs(self):
        nodes = ["A", "B", "C", "D"]
        pairs = list(combinations(nodes, 2))
        for choices in product((None, -1, 2), repeat=len(pairs)):
            edges = [(source, target, weight) for (source, target), weight in zip(pairs, choices) if weight is not None]
            yield nodes, edges

    def payload(self, nodes, edges):
        return {"nodes": nodes, "edges": [{"source": source, "target": target, "weight": weight} for source, target, weight in edges]}

    def test_forests_match_exhaustive_optimum_and_each_greedy_cut(self):
        for nodes, edges in self.graphs():
            payload = self.payload(nodes, edges)
            expected = minimum_forest_weight(nodes, edges)
            groups = component_groups(nodes, edges)
            for name, run, model in (("kruskal", run_kruskal, GraphInput), ("prim", run_prim, StartGraphInput)):
                args = dict(payload)
                if name == "prim": args["start"] = "C"
                result = run(model.model_validate(args))
                self.assertEqual(result.output["totalWeight"], expected)
                self.assertEqual(len(result.output["edges"]), len(nodes) - len(groups))
                self.assertEqual({frozenset(group) for group in result.output["components"]}, {frozenset(group) for group in groups})
                self.assertEqual(result.steps[-1].stateData.selectedEdges, result.output["edges"])
                self.assertEqual(result.steps[-1].stateData.totalWeight, expected)
                for index, step in enumerate(result.steps):
                    self.assertEqual(step.stepIndex, index)
                    if step.action not in ("accept", "reject", "inspect"): continue
                    state = step.stateData
                    current = state.currentEdge
                    if step.action == "accept":
                        previous = result.steps[index - 1].stateData
                        self.assertEqual(state.selectedEdges, previous.selectedEdges + [current])
                        self.assertEqual(state.totalWeight, previous.totalWeight + edges[current][2])
                        old = [edges[item] for item in previous.selectedEdges]
                        source, target, _ = edges[current]
                        self.assertFalse(any(source in group and target in group for group in component_groups(nodes, old)))
                    if name == "prim" and step.action in ("inspect", "accept"):
                        crossing = [item for item, edge in enumerate(edges) if (edge[0] in state.visited) != (edge[1] in state.visited)]
                        self.assertEqual(state.edgeOrder, sorted(crossing, key=lambda item: (edges[item][2], item)))
                    if name == "prim" and step.action == "inspect":
                        candidates = [item for item, edge in enumerate(edges) if (edge[0] in state.visited) != (edge[1] in state.visited)]
                        self.assertEqual(current, min(candidates, key=lambda item: (edges[item][2], item)))
                    if name == "kruskal" and step.action == "reject":
                        selected = [edges[item] for item in state.selectedEdges]
                        source, target, _ = edges[current]
                        self.assertTrue(any(source in group and target in group for group in component_groups(nodes, selected)))

    def test_dijkstra_distances_paths_and_settled_values_match_floyd_warshall(self):
        for nodes, signed_edges in self.graphs():
            edges = [(source, target, abs(weight)) for source, target, weight in signed_edges]
            payload = self.payload(nodes, edges)
            result = run_dijkstra(DijkstraInput.model_validate({**payload, "start": "B"}))
            expected = shortest_oracle(nodes, edges, "B")
            self.assertEqual(result.output["distances"], expected)
            self.assertEqual(result.steps[-1].stateData.distances, expected)
            for node, path in result.output["paths"].items():
                if expected[node] is None:
                    self.assertIsNone(path)
                    continue
                self.assertEqual(path[0], "B")
                self.assertEqual(path[-1], node)
                self.assertEqual(len(path), len(set(path)))
                weight = sum(next(edge[2] for edge in edges if {edge[0], edge[1]} == {left, right}) for left, right in zip(path, path[1:]))
                self.assertEqual(weight, expected[node])
            for index, step in enumerate(result.steps):
                self.assertEqual(step.stepIndex, index)
                for node in step.stateData.visited:
                    self.assertEqual(step.stateData.distances[node], expected[node])
                if step.action == "relax":
                    previous = result.steps[index - 1].stateData
                    source, target, weight = edges[step.stateData.currentEdge]
                    current = step.stateData.currentNode
                    neighbor = target if source == current else source
                    self.assertEqual(step.stateData.distances[neighbor], previous.distances[current] + weight)

    def test_zero_weights_isolated_nodes_ties_and_snapshot_independence(self):
        payload = self.payload(["A", "B", "C", "D"], [("A", "B", 0), ("B", "C", 0), ("A", "C", 0)])
        for run, model, args in ((run_dijkstra, DijkstraInput, {**payload, "start": "A"}),
                                 (run_kruskal, GraphInput, payload),
                                 (run_prim, StartGraphInput, {**payload, "start": "B"})):
            validated = model.model_validate(args)
            before = validated.model_dump()
            result = run(validated)
            self.assertEqual(validated.model_dump(), before)
            result.steps[0].stateData.edges[0].weight = 123
            self.assertEqual(result.steps[1].stateData.edges[0].weight, 0)
            self.assertEqual(validated.edges[0].weight, 0)
