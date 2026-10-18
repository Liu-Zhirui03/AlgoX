"""Exercise the actual ASGI endpoint without network or extra dependencies."""

import json
import unittest
from unittest.mock import patch

from pydantic import BaseModel

from backend.registry import ALGORITHMS, AlgorithmDefinition
from backend.schemas import AlgorithmResult, VisualizationStep

from backend.main import app


async def request_api(path, method="GET", payload=None):
    body = json.dumps(payload).encode() if payload is not None else b""
    messages = []
    scope = {
        "type": "http", "asgi": {"version": "3.0"}, "http_version": "1.1",
        "method": method, "scheme": "http", "path": path,
        "raw_path": path.encode(), "query_string": b"",
        "headers": [(b"content-type", b"application/json")],
        "server": ("test", 80), "client": ("127.0.0.1", 1234), "root_path": "",
    }

    async def receive():
        return {"type": "http.request", "body": body, "more_body": False}

    async def send(message):
        messages.append(message)

    await app(scope, receive, send)
    status = next(message["status"] for message in messages if message["type"] == "http.response.start")
    payload = b"".join(message.get("body", b"") for message in messages if message["type"] == "http.response.body")
    return status, json.loads(payload)


async def request_example(values):
    return await request_api("/api/algorithms/bubble-sort", "POST", {"values": values})


class ExampleApiTests(unittest.IsolatedAsyncioTestCase):
    async def test_custom_inputs(self):
        for values in ([9, 3, 7, 1], [-3, 2, -3, 0], [5], list(range(20, 0, -1))):
            with self.subTest(values=values):
                status, result = await request_example(values)
                self.assertEqual(status, 200)
                self.assertEqual(result["input"], values)
                self.assertEqual(result["output"], sorted(values))
                self.assertEqual(result["language"], "python")
                self.assertIn("def bubble_sort", result["source"])
                self.assertEqual(result["steps"][0]["stateData"], values)
                self.assertEqual(result["steps"][-1]["stateData"], sorted(values))
                self.assertEqual(result["steps"][-1]["action"], "complete")

    async def test_invalid_inputs_are_rejected(self):
        for values in ([], list(range(21)), [True], [1.2], ["2"], [None], [9007199254740992], [-9007199254740992], "1,2"):
            with self.subTest(values=values):
                status, result = await request_example(values)
                self.assertEqual(status, 422)
                self.assertIn("detail", result)


class AlgorithmDispatchTests(unittest.IsolatedAsyncioTestCase):
    async def test_catalog_exposes_input_schema_and_renderer(self):
        status, catalog = await request_api("/api/algorithms")
        self.assertEqual(status, 200)
        self.assertEqual([entry["id"] for entry in catalog], ["bubble-sort", "quick-sort", "merge-sort", "binary-search", "hash-search", "dijkstra", "kruskal", "prim", "huffman", "activity-selection", "fractional-knapsack"])
        info = catalog[0]
        self.assertEqual(info["renderer"], "array-bars")
        self.assertEqual(info["playgroundUrl"], "/algorithms/bubble-sort")
        self.assertEqual(info["inputSchema"]["properties"]["values"]["maxItems"], 20)

    async def test_default_and_legacy_routes_preserve_playback_fields(self):
        _, expected = await request_example([5, 2, 8, 1])
        for path in ("/api/algorithms/bubble-sort", "/api/examples/bubble-sort"):
            status, result = await request_api(path)
            self.assertEqual(status, 200)
            self.assertEqual(result, expected)
            self.assertEqual(result["algorithmId"], "bubble-sort")
            self.assertEqual(result["renderer"], "array-bars")
            self.assertIn("sortedIndices", result["steps"][0])
            status, result = await request_api(path, "POST", {"values": [-2, 1, 0]})
            self.assertEqual(status, 200)
            self.assertEqual(result["output"], [-2, 0, 1])

    async def test_unknown_algorithms_return_404(self):
        for path in ("/api/algorithms/not-supported", "/api/examples/not-supported", "/algorithms/not-supported"):
            status, result = await request_api(path)
            self.assertEqual(status, 404)
            self.assertIn("not supported", result["detail"])
        status, _ = await request_api("/api/algorithms/not-supported", "POST", {"values": [1]})
        self.assertEqual(status, 404)

    async def test_validation_errors_include_body_location(self):
        status, result = await request_example([True])
        self.assertEqual(status, 422)
        self.assertEqual(result["detail"][0]["loc"], ["body", "values", 0])
        for payload in ({}, [], None):
            status, _ = await request_api("/api/algorithms/bubble-sort", "POST", payload)
            self.assertEqual(status, 422)

    async def test_new_module_can_use_non_array_input_and_steps_without_route_changes(self):
        # A test-only adapter proves the dispatcher does not assume sorting or arrays.
        class GraphInput(BaseModel):
            start: str

        def run_graph(payload):
            state = {"visited": [payload.start]}
            return AlgorithmResult(
                algorithmId="test-graph", title="Test Graph", renderer="graph",
                source="def visit(start):\n    return [start]\n",
                input={"start": payload.start}, output=state,
                steps=[VisualizationStep(stepIndex=0, explanation="Visit the start node.",
                                         stateData=state, highlights=[payload.start])],
            )

        adapter = AlgorithmDefinition(
            id="test-graph", title="Test Graph", category="Test only", renderer="graph",
            playground_file="unused.html", input_model=GraphInput,
            default_input={"start": "A"}, run=run_graph,
        )
        with patch.dict(ALGORITHMS, {"test-graph": adapter}):
            status, result = await request_api("/api/algorithms/test-graph", "POST", {"start": "B"})
            self.assertEqual(status, 200)
            self.assertEqual(result["output"], {"visited": ["B"]})
            self.assertEqual(result["steps"][0]["highlights"], ["B"])
            self.assertEqual(result["renderer"], "graph")
            status, result = await request_api("/api/algorithms/test-graph")
            self.assertEqual(status, 200)
            self.assertEqual(result["input"], {"start": "A"})
            status, _ = await request_api("/api/algorithms/test-graph", "POST", {"values": [1]})
            self.assertEqual(status, 422)


class AdditionalSortApiTests(unittest.IsolatedAsyncioTestCase):
    async def test_registered_sorts_defaults_custom_inputs_and_validation(self):
        for algorithm_id in ("quick-sort", "merge-sort"):
            for prefix in ("/api/algorithms/", "/api/examples/"):
                status, result = await request_api(prefix + algorithm_id)
                self.assertEqual(status, 200)
                self.assertEqual(result["algorithmId"], algorithm_id)
                self.assertEqual(result["output"], [1, 2, 5, 8])
                self.assertIn("def " + algorithm_id.replace("-", "_"), result["source"])
                compile(result["source"], "sample.py", "exec")
            for values in ([1], [-2, 3, -2, 0], [0] * 20, list(range(20, 0, -1)),
                           [-9007199254740991, 9007199254740991, 0]):
                status, result = await request_api("/api/algorithms/" + algorithm_id, "POST", {"values": values})
                self.assertEqual(status, 200)
                self.assertEqual(result["input"], values)
                self.assertEqual(result["output"], sorted(values))
                self.assertEqual(result["steps"][0]["stateData"], values)
                self.assertEqual(result["steps"][-1]["stateData"], sorted(values))
                self.assertEqual(result["steps"][-1]["action"], "complete")
            for values in ([], [1] * 21, [True], [1.1], ["1"], [None], [9007199254740992], [-9007199254740992]):
                status, _ = await request_api("/api/algorithms/" + algorithm_id, "POST", {"values": values})
                self.assertEqual(status, 422)


class SearchApiTests(unittest.IsolatedAsyncioTestCase):
    async def test_defaults_and_original_index_results(self):
        for slug, index in (("binary-search", 3), ("hash-search", 2)):
            for prefix in ("/api/algorithms/", "/api/examples/"):
                status, result = await request_api(prefix + slug)
                self.assertEqual(status, 200)
                self.assertEqual(result["algorithmId"], slug)
                self.assertEqual(result["renderer"], slug)
                self.assertEqual(result["output"], {"found": True, "index": index})
                self.assertEqual(result["steps"][-1]["stateData"]["foundIndex"], index)
                compile(result["source"], slug + ".py", "exec")

    async def test_found_missing_duplicates_and_boundaries(self):
        for slug in ("binary-search", "hash-search"):
            for values, target in (([1], 1), ([1], 0), ([-3, -3, 0, 4], -3),
                                   (list(range(20)), 19), (list(range(20)), 22),
                                   ([-9007199254740991, 0, 9007199254740991], 9007199254740991)):
                status, result = await request_api("/api/algorithms/" + slug, "POST", {"values": values, "target": target})
                self.assertEqual(status, 200)
                expected = values.index(target) if target in values else -1
                self.assertEqual(result["output"], {"found": expected >= 0, "index": expected})
                self.assertEqual(result["input"]["values"], values)
                self.assertEqual(result["steps"][-1]["action"], "complete")
        status, result = await request_api("/api/algorithms/hash-search", "POST", {"values": [17, -4, 10, 17], "target": 17, "bucketCount": 7})
        self.assertEqual(status, 200)
        self.assertEqual(result["output"]["index"], 0)
        self.assertTrue(any(step["action"] == "collision" for step in result["steps"]))

    async def test_invalid_search_requests_return_422(self):
        for slug in ("binary-search", "hash-search"):
            for body in ({"values": [1]}, {"values": [1], "target": True},
                         {"values": [1], "target": "1"}, {"values": [1], "target": 1.5},
                         {"values": [], "target": 1}, {"values": [1] * 21, "target": 1},
                         {"values": [True], "target": 1}, {"values": [1], "target": 9007199254740992}):
                status, _ = await request_api("/api/algorithms/" + slug, "POST", body)
                self.assertEqual(status, 422)
        status, result = await request_api("/api/algorithms/binary-search", "POST", {"values": [3, 1, 2], "target": 1})
        self.assertEqual(status, 422)
        self.assertIn("ascending", str(result))
        for count in (0, 2, 17, True, 3.5, "7"):
            status, _ = await request_api("/api/algorithms/hash-search", "POST", {"values": [1], "target": 1, "bucketCount": count})
            self.assertEqual(status, 422)


class GreedyGraphApiTests(unittest.IsolatedAsyncioTestCase):
    async def test_registered_graph_defaults_and_aliases(self):
        for slug in ("dijkstra", "kruskal", "prim"):
            for prefix in ("/api/algorithms/", "/api/examples/"):
                status, result = await request_api(prefix + slug)
                self.assertEqual(status, 200)
                self.assertEqual(result["algorithmId"], slug)
                self.assertEqual(result["renderer"], "weighted-graph")
                compile(result["source"], slug + ".py", "exec")
                self.assertEqual(result["steps"][-1]["action"], "complete")
                if slug == "dijkstra":
                    self.assertEqual(result["output"]["distances"], {"A": 0, "B": 3, "C": 2, "D": 8, "E": 10})
                    self.assertEqual(result["output"]["paths"]["E"], ["A", "C", "B", "D", "E"])
                else:
                    self.assertEqual(result["output"]["totalWeight"], 10)
                    self.assertTrue(result["output"]["connected"])

    async def test_disconnected_zero_and_negative_graphs(self):
        for slug in ("dijkstra", "kruskal", "prim"):
            body = {"nodes": ["A", "B", "C"], "edges": [{"source": "A", "target": "B", "weight": 0}]}
            if slug != "kruskal": body["start"] = "A"
            status, result = await request_api("/api/algorithms/" + slug, "POST", body)
            self.assertEqual(status, 200)
            if slug == "dijkstra":
                self.assertIsNone(result["output"]["distances"]["C"])
                self.assertIsNone(result["output"]["paths"]["C"])
            else:
                self.assertFalse(result["output"]["connected"])
                self.assertEqual(len(result["output"]["components"]), 2)
            body["edges"][0]["weight"] = -5
            status, result = await request_api("/api/algorithms/" + slug, "POST", body)
            self.assertEqual(status, 422 if slug == "dijkstra" else 200)
            if status == 200: self.assertEqual(result["output"]["totalWeight"], -5)
            singleton = {"nodes": ["A"], "edges": []}
            if slug != "kruskal": singleton["start"] = "A"
            status, result = await request_api("/api/algorithms/" + slug, "POST", singleton)
            self.assertEqual(status, 200)

    async def test_maximum_supported_graph(self):
        from itertools import combinations
        nodes = ["N" + str(index) for index in range(10)]
        edges = [{"source": source, "target": target, "weight": index % 7}
                 for index, (source, target) in enumerate(list(combinations(nodes, 2))[:30])]
        for slug in ("dijkstra", "kruskal", "prim"):
            body = {"nodes": nodes, "edges": edges}
            if slug != "kruskal": body["start"] = nodes[0]
            status, result = await request_api("/api/algorithms/" + slug, "POST", body)
            self.assertEqual(status, 200)
            self.assertEqual(len(result["steps"][-1]["stateData"]["edges"]), 30)
            if slug == "dijkstra":
                self.assertTrue(all(distance is not None for distance in result["output"]["distances"].values()))
            else:
                self.assertEqual(len(result["output"]["edges"]), 9)
                self.assertTrue(result["output"]["connected"])

    async def test_graph_validation_rejects_invalid_shapes(self):
        from copy import deepcopy
        base = {"nodes": ["A", "B"], "edges": [{"source": "A", "target": "B", "weight": 1}]}
        invalid = [
            {"nodes": []}, {"nodes": ["A", "A"]}, {"nodes": ["A", "bad label"]},
            {"nodes": ["A"] * 11},
            {"edges": [{"source": "A", "target": "Z", "weight": 1}]},
            {"edges": [{"source": "A", "target": "A", "weight": 1}]},
            {"edges": base["edges"] + [{"source": "B", "target": "A", "weight": 2}]},
            {"edges": base["edges"] * 31},
        ]
        invalid += [{"edges": [{"source": "A", "target": "B", "weight": value}]} for value in (True, 1.5, "1", 1000001, -1000001)]
        for slug in ("dijkstra", "kruskal", "prim"):
            for changes in invalid:
                body = {**deepcopy(base), **changes}
                if slug != "kruskal": body["start"] = "A"
                status, _ = await request_api("/api/algorithms/" + slug, "POST", body)
                self.assertEqual(status, 422, (slug, body))
            if slug != "kruskal":
                for start in (None, "Z", 1):
                    status, _ = await request_api("/api/algorithms/" + slug, "POST", {**base, "start": start})
                    self.assertEqual(status, 422)


class RemainingGreedyApiTests(unittest.IsolatedAsyncioTestCase):
    async def test_defaults_aliases_and_reference_syntax(self):
        for slug in ("huffman", "activity-selection", "fractional-knapsack"):
            for prefix in ("/api/algorithms/", "/api/examples/"):
                status, result = await request_api(prefix + slug)
                self.assertEqual(status, 200)
                self.assertEqual(result["algorithmId"], slug)
                compile(result["source"], slug + ".py", "exec")
                self.assertEqual(result["steps"][-1]["action"], "complete")
                if slug == "huffman":
                    self.assertEqual(result["output"]["weightedCost"], 224)
                elif slug == "activity-selection":
                    self.assertEqual(result["output"]["names"], ["A", "D", "F", "G"])
                else:
                    self.assertAlmostEqual(result["output"]["totalValue"], 240)
                    self.assertAlmostEqual(result["output"]["fractions"][2], 2 / 3)

    async def test_singletons_maximum_rows_and_zero_capacity(self):
        cases = [
            ("huffman", {"symbols": [{"symbol": "A", "frequency": 7}]}),
            ("huffman", {"symbols": [{"symbol": "S" + str(index), "frequency": 1000000} for index in range(10)]}),
            ("activity-selection", {"activities": [{"name": "A" + str(index), "start": index, "finish": index + 1} for index in range(12)]}),
            ("fractional-knapsack", {"items": [{"name": "I" + str(index), "weight": 1000000, "value": 1000000} for index in range(12)], "capacity": 1000000}),
            ("fractional-knapsack", {"items": [{"name": "A", "weight": 5, "value": 8}], "capacity": 0}),
        ]
        for slug, payload in cases:
            status, result = await request_api("/api/algorithms/" + slug, "POST", payload)
            self.assertEqual(status, 200)
            if slug == "huffman" and len(payload["symbols"]) == 1:
                self.assertEqual(result["output"], {"codes": {"A": "0"}, "weightedCost": 7})
            if slug == "activity-selection": self.assertEqual(result["output"]["count"], 12)
            if payload.get("capacity") == 0: self.assertEqual(result["output"]["totalValue"], 0)

    async def test_invalid_greedy_inputs_return_422(self):
        invalid = {
            "huffman": [
                {"symbols": []}, {"symbols": [{"symbol": "A", "frequency": 1}] * 11},
                {"symbols": [{"symbol": "A", "frequency": 1}, {"symbol": "A", "frequency": 2}]},
                *[{"symbols": [{"symbol": "A", "frequency": frequency}]} for frequency in (0, -1, True, 1.5, "2", 1000001)],
            ],
            "activity-selection": [
                {"activities": []}, {"activities": [{"name": "A", "start": 0, "finish": 1}] * 13},
                *[{"activities": [{"name": "A", "start": start, "finish": finish}]} for start, finish in ((1, 1), (2, 1), (-1, 2), (True, 2), (0, "2"), (0, 1.5), (0, 1000001))],
                {"activities": [{"name": "A", "start": 0, "finish": 1}, {"name": "A", "start": 1, "finish": 2}]},
            ],
            "fractional-knapsack": [
                {"items": [], "capacity": 5},
                {"items": [{"name": "A", "weight": 1, "value": 1}] * 13, "capacity": 5},
                *[{"items": [{"name": "A", "weight": weight, "value": 1}], "capacity": 5} for weight in (0, -1, True, 1.5, "2", 1000001)],
                *[{"items": [{"name": "A", "weight": 1, "value": 1}], "capacity": capacity} for capacity in (-1, True, 1.5, "2", 1000001)],
                {"items": [{"name": "A", "weight": 1, "value": -1}], "capacity": 5},
                {"items": [{"name": "A", "weight": 1, "value": 1}, {"name": "A", "weight": 2, "value": 2}], "capacity": 5},
            ],
        }
        for slug, cases in invalid.items():
            for payload in cases:
                status, _ = await request_api("/api/algorithms/" + slug, "POST", payload)
                self.assertEqual(status, 422, (slug, payload))
