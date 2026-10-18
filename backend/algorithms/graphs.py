"""Validated small undirected graphs and independent visualization snapshots."""

from typing import Annotated
from pydantic import BaseModel, Field, StrictInt, StringConstraints, model_validator
from backend.schemas import VisualizationStep

Node = Annotated[str, StringConstraints(strict=True, pattern=r"^[A-Za-z0-9_]{1,8}$")]
Weight = Annotated[StrictInt, Field(ge=-1000000, le=1000000)]


class Edge(BaseModel):
    source: Node
    target: Node
    weight: Weight


class GraphInput(BaseModel):
    nodes: list[Node] = Field(min_length=1, max_length=10)
    edges: list[Edge] = Field(max_length=30)

    @model_validator(mode="after")
    def validate_graph(self):
        if len(set(self.nodes)) != len(self.nodes):
            raise ValueError("Node labels must be unique.")
        seen = set()
        for edge in self.edges:
            if edge.source not in self.nodes or edge.target not in self.nodes:
                raise ValueError("Every edge endpoint must be a listed node.")
            if edge.source == edge.target:
                raise ValueError("Self-loops are not supported.")
            pair = frozenset((edge.source, edge.target))
            if pair in seen:
                raise ValueError("Duplicate undirected edges are not supported.")
            seen.add(pair)
        return self


class StartGraphInput(GraphInput):
    start: Node

    @model_validator(mode="after")
    def validate_start(self):
        if self.start not in self.nodes:
            raise ValueError("The start node must be listed in nodes.")
        return self


class GraphState(BaseModel):
    nodes: list[str]
    edges: list[Edge]
    visited: list[str] = Field(default_factory=list)
    currentNode: str | None = None
    currentEdge: int | None = None
    selectedEdges: list[int] = Field(default_factory=list)
    rejectedEdges: list[int] = Field(default_factory=list)
    distances: dict[str, int | None] = Field(default_factory=dict)
    parents: dict[str, str | None] = Field(default_factory=dict)
    components: list[list[str]] = Field(default_factory=list)
    totalWeight: int = 0
    edgeOrder: list[int] = Field(default_factory=list)


class GraphStep(VisualizationStep):
    action: str
    stateData: GraphState


class Recorder:
    def __init__(self, payload: GraphInput):
        self.state = GraphState(nodes=payload.nodes.copy(), edges=[edge.model_copy() for edge in payload.edges])
        self.steps = []

    def record(self, action, explanation):
        self.steps.append(GraphStep(
            stepIndex=len(self.steps), action=action, explanation=explanation,
            highlights=[] if self.state.currentEdge is None else [self.state.currentEdge],
            stateData=self.state.model_copy(deep=True),
        ))


DEFAULT_GRAPH = {
    "nodes": ["A", "B", "C", "D", "E"],
    "edges": [
        {"source": "A", "target": "B", "weight": 4},
        {"source": "A", "target": "C", "weight": 2},
        {"source": "B", "target": "C", "weight": 1},
        {"source": "B", "target": "D", "weight": 5},
        {"source": "C", "target": "D", "weight": 8},
        {"source": "C", "target": "E", "weight": 10},
        {"source": "D", "target": "E", "weight": 2},
    ],
}
