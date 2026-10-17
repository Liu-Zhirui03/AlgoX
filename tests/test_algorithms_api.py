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
        self.assertEqual([entry["id"] for entry in catalog], ["bubble-sort", "quick-sort", "merge-sort"])
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
