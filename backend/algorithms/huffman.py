"""Huffman tree construction and code-assignment trace."""

from heapq import heapify, heappop, heappush
from inspect import getsource
from pydantic import BaseModel, Field, model_validator
from backend.algorithms.greedy import Label, Positive, Recorder
from backend.schemas import AlgorithmResult
from examples.huffman import huffman

ALGORITHM_ID = "huffman"
TITLE = "Huffman Coding"
CATEGORY = "Greedy Algorithms"
RENDERER = "huffman-tree"
PLAYGROUND_FILE = "huffman.html"
DEFAULT_INPUT = {"symbols": [{"symbol": symbol, "frequency": frequency} for symbol, frequency in [("A", 5), ("B", 9), ("C", 12), ("D", 13), ("E", 16), ("F", 45)]]}


class Symbol(BaseModel):
    symbol: Label
    frequency: Positive


class HuffmanInput(BaseModel):
    symbols: list[Symbol] = Field(min_length=1, max_length=10)

    @model_validator(mode="after")
    def unique_symbols(self):
        if len({item.symbol for item in self.symbols}) != len(self.symbols):
            raise ValueError("Symbols must be unique.")
        return self


def huffman_steps(payload: HuffmanInput):
    nodes = [{"id": index, "symbol": item.symbol, "frequency": item.frequency, "left": None, "right": None} for index, item in enumerate(payload.symbols)]
    heap = [(node["frequency"], node["id"]) for node in nodes]
    heapify(heap)
    recorder = Recorder({"nodes": nodes, "roots": [index for _, index in sorted(heap)], "codes": {}, "selected": [], "weightedCost": 0})
    state = recorder.state
    recorder.record("initial", "Create a leaf for every symbol. Order the forest by frequency, breaking ties by creation order.")
    while len(heap) > 1:
        left_weight, left = heappop(heap)
        right_weight, right = heappop(heap)
        state["selected"] = [left, right]
        recorder.record("select", f"Select the two smallest roots: {left_weight} and {right_weight}.", [left, right])
        index = len(state["nodes"])
        state["nodes"].append({"id": index, "symbol": None, "frequency": left_weight + right_weight, "left": left, "right": right})
        heappush(heap, (left_weight + right_weight, index))
        state["roots"] = [node for _, node in sorted(heap)]
        state["selected"] = [index]
        recorder.record("merge", f"Merge them into a parent of frequency {left_weight + right_weight}. Left edges encode 0 and right edges encode 1.", [index])
    root = heap[0][1]
    stack = [(root, "")]
    while stack:
        index, code = stack.pop()
        node = state["nodes"][index]
        if node["symbol"] is not None:
            state["codes"][node["symbol"]] = code or "0"
            state["weightedCost"] += node["frequency"] * len(code or "0")
            state["selected"] = [index]
            recorder.record("assign", f"Assign {node['symbol']} code {code or '0'}." + (" A single-symbol alphabet uses one bit per occurrence." if len(payload.symbols) == 1 else ""), [index])
        else:
            stack.append((node["right"], code + "1"))
            stack.append((node["left"], code + "0"))
    state["selected"] = []
    recorder.record("complete", f"Prefix codes are complete. Weighted bit cost: {state['weightedCost']}.")
    return recorder.steps


def run(payload: HuffmanInput) -> AlgorithmResult:
    return AlgorithmResult(algorithmId=ALGORITHM_ID, title=TITLE, renderer=RENDERER,
        source=getsource(huffman), input=payload.model_dump(),
        output=huffman([(item.symbol, item.frequency) for item in payload.symbols]), steps=huffman_steps(payload))
