"""Fractional knapsack with exact density comparisons and visible capacity changes."""

from fractions import Fraction
from inspect import getsource
from pydantic import BaseModel, Field, model_validator
from backend.algorithms.greedy import Label, Nonnegative, Positive, Recorder
from backend.schemas import AlgorithmResult
from examples.fractional_knapsack import fractional_knapsack

ALGORITHM_ID = "fractional-knapsack"
TITLE = "Fractional Knapsack Algorithm"
CATEGORY = "Greedy Algorithms"
RENDERER = "fractional-knapsack"
PLAYGROUND_FILE = "fractional-knapsack.html"
DEFAULT_INPUT = {"items": [{"name": name, "weight": weight, "value": value} for name, weight, value in [("A", 10, 60), ("B", 20, 100), ("C", 30, 120)]], "capacity": 50}


class Item(BaseModel):
    name: Label
    weight: Positive
    value: Nonnegative


class KnapsackInput(BaseModel):
    items: list[Item] = Field(min_length=1, max_length=12)
    capacity: Nonnegative

    @model_validator(mode="after")
    def unique_names(self):
        if len({item.name for item in self.items}) != len(self.items):
            raise ValueError("Item names must be unique.")
        return self


def knapsack_steps(payload: KnapsackInput):
    count = len(payload.items)
    recorder = Recorder({"items": [item.model_dump() for item in payload.items], "capacity": payload.capacity, "remaining": payload.capacity, "totalWeight": 0, "totalValue": 0.0, "fractions": [0.0] * count, "takenWeights": [0] * count, "order": list(range(count)), "current": None, "skipped": []})
    state = recorder.state
    total = Fraction(0)
    recorder.record("initial", "Fill the knapsack with the most valuable weight first. Partial items are allowed.")
    state["order"] = sorted(state["order"], key=lambda index: (-Fraction(payload.items[index].value, payload.items[index].weight), index))
    recorder.record("sort", "Order items by descending value-to-weight ratio. Equal ratios keep input order.")
    for index in state["order"]:
        item = payload.items[index]
        state["current"] = index
        recorder.record("consider", f"Consider {item.name}: value {item.value}, weight {item.weight}, ratio {float(Fraction(item.value, item.weight)):.6g}; remaining capacity {state['remaining']}.", [index])
        if state["remaining"] == 0 or item.value == 0:
            state["skipped"].append(index)
            recorder.record("skip", f"Skip {item.name}: " + ("the knapsack is full." if state["remaining"] == 0 else "its value is zero."), [index])
            continue
        amount = min(item.weight, state["remaining"])
        fraction = Fraction(amount, item.weight)
        state["fractions"][index] = float(fraction)
        state["takenWeights"][index] = amount
        state["remaining"] -= amount
        state["totalWeight"] += amount
        total += fraction * item.value
        state["totalValue"] = float(total)
        recorder.record("take", f"Take {float(fraction) * 100:.6g}% of {item.name}: weight {amount}, value {float(fraction * item.value):.6g}. Remaining capacity: {state['remaining']}.", [index])
    state["current"] = None
    recorder.record("complete", f"Optimal fractional value: {state['totalValue']:.6g}; used weight {state['totalWeight']} of {payload.capacity}.")
    return recorder.steps


def run(payload: KnapsackInput) -> AlgorithmResult:
    return AlgorithmResult(algorithmId=ALGORITHM_ID, title=TITLE, renderer=RENDERER,
        source=getsource(fractional_knapsack), input=payload.model_dump(),
        output=fractional_knapsack([(item.name, item.weight, item.value) for item in payload.items], payload.capacity), steps=knapsack_steps(payload))
