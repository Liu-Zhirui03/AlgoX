"""Independent optimality and transition tests for coding, scheduling, and packing."""

from fractions import Fraction
from functools import lru_cache
from itertools import combinations, product
import random
import unittest

from backend.algorithms.huffman import HuffmanInput, run as run_huffman
from backend.algorithms.activity_selection import ActivityInput, run as run_activity
from backend.algorithms.fractional_knapsack import KnapsackInput, run as run_knapsack


@lru_cache(None)
def optimal_merge_cost(weights):
    if len(weights) <= 1: return 0
    return min(weights[left] + weights[right] + optimal_merge_cost(tuple(sorted(
        [value for index, value in enumerate(weights) if index not in (left, right)] + [weights[left] + weights[right]])))
        for left, right in combinations(range(len(weights)), 2))


def optimal_schedule(activities):
    best = 0
    for mask in range(1 << len(activities)):
        subset = sorted([item for index, item in enumerate(activities) if mask & (1 << index)], key=lambda item: (item["start"], item["finish"]))
        if all(left["finish"] <= right["start"] for left, right in zip(subset, subset[1:])):
            best = max(best, len(subset))
    return best


def optimal_fractional(items, capacity):
    best = Fraction(0)
    for mask in range(1 << len(items)):
        weight = sum(item["weight"] for index, item in enumerate(items) if mask & (1 << index))
        if weight > capacity: continue
        value = sum(item["value"] for index, item in enumerate(items) if mask & (1 << index))
        best = max(best, value)
        for index, item in enumerate(items):
            if mask & (1 << index): continue
            extra = min(item["weight"], capacity - weight)
            best = max(best, value + Fraction(extra * item["value"], item["weight"]))
    return best


class GreedyChoiceTests(unittest.TestCase):
    def test_huffman_prefix_codes_optimal_cost_and_smallest_merges(self):
        for length in range(1, 6):
            for weights in product((1, 2, 3), repeat=length):
                payload = HuffmanInput(symbols=[{"symbol": "S" + str(index), "frequency": weight} for index, weight in enumerate(weights)])
                result = run_huffman(payload)
                codes = result.output["codes"]
                self.assertEqual(set(codes), {item.symbol for item in payload.symbols})
                self.assertTrue(all(code and set(code) <= {"0", "1"} for code in codes.values()))
                self.assertFalse(any(right.startswith(left) for a, left in codes.items() for b, right in codes.items() if a != b))
                expected = weights[0] if length == 1 else optimal_merge_cost(tuple(sorted(weights)))
                self.assertEqual(result.output["weightedCost"], expected)
                final = result.steps[-1].stateData
                self.assertEqual(final["codes"], codes)
                self.assertEqual(final["weightedCost"], expected)
                self.assertEqual(len(final["nodes"]), 2 * length - 1)
                self.assertEqual(final["nodes"][final["roots"][0]]["frequency"], sum(weights))
                for index, step in enumerate(result.steps):
                    self.assertEqual(step.stepIndex, index)
                    state = step.stateData
                    if step.action == "select":
                        roots = sorted(state["roots"], key=lambda node: (state["nodes"][node]["frequency"], node))
                        self.assertEqual(state["selected"], roots[:2])
                    if step.action == "merge":
                        parent = state["nodes"][-1]
                        self.assertEqual(parent["frequency"], state["nodes"][parent["left"]]["frequency"] + state["nodes"][parent["right"]]["frequency"])
                    if step.action == "assign":
                        leaf = state["selected"][0]
                        path = ""
                        node = leaf
                        while True:
                            parent = next((item for item in state["nodes"] if item["left"] == node or item["right"] == node), None)
                            if parent is None: break
                            path = ("0" if parent["left"] == node else "1") + path
                            node = parent["id"]
                        self.assertEqual(state["codes"][state["nodes"][leaf]["symbol"]], path or "0")

    def test_activity_selection_matches_exhaustive_maximum_and_decisions(self):
        generator = random.Random(141)
        cases = [[{"name": "A", "start": 0, "finish": 1}, {"name": "B", "start": 1, "finish": 2}]]
        for _ in range(120):
            intervals = []
            for index in range(generator.randint(1, 8)):
                start = generator.randrange(9)
                intervals.append({"name": "A" + str(index), "start": start, "finish": generator.randrange(start + 1, 11)})
            cases.append(intervals)
        for activities in cases:
            result = run_activity(ActivityInput(activities=activities))
            self.assertEqual(result.output["count"], optimal_schedule(activities))
            self.assertEqual(result.output["selected"], result.steps[-1].stateData["selected"])
            self.assertEqual(result.steps[-1].stateData["order"], sorted(range(len(activities)), key=lambda index: (activities[index]["finish"], index)))
            for index, step in enumerate(result.steps):
                self.assertEqual(step.stepIndex, index)
                if step.action in ("accept", "reject"):
                    previous = result.steps[index - 1].stateData
                    item = activities[step.stateData["current"]]
                    compatible = previous["lastFinish"] is None or item["start"] >= previous["lastFinish"]
                    self.assertEqual(step.action == "accept", compatible)

    def test_fractional_knapsack_matches_independent_vertex_enumeration(self):
        generator = random.Random(916)
        cases = [([{"name": "A", "weight": 3, "value": 10}], 1),
                 ([{"name": "A", "weight": 1, "value": 0}], 5)]
        for _ in range(100):
            items = [{"name": "I" + str(index), "weight": generator.randrange(1, 10), "value": generator.randrange(21)} for index in range(generator.randrange(1, 7))]
            cases.append((items, generator.randrange(26)))
        for items, capacity in cases:
            result = run_knapsack(KnapsackInput(items=items, capacity=capacity))
            self.assertAlmostEqual(result.output["totalValue"], float(optimal_fractional(items, capacity)))
            final = result.steps[-1].stateData
            self.assertEqual(final["fractions"], result.output["fractions"])
            self.assertEqual(final["totalValue"], result.output["totalValue"])
            self.assertEqual(final["totalWeight"] + final["remaining"], capacity)
            self.assertEqual(sum(final["takenWeights"]), final["totalWeight"])
            self.assertLessEqual(sum(0 < fraction < 1 for fraction in final["fractions"]), 1)
            for fraction in final["fractions"]: self.assertTrue(0 <= fraction <= 1)
            for index, step in enumerate(result.steps):
                self.assertEqual(step.stepIndex, index)
                state = step.stateData
                self.assertEqual(state["totalWeight"] + state["remaining"], capacity)
                if step.action == "take":
                    previous = result.steps[index - 1].stateData
                    current = state["current"]
                    self.assertEqual(state["takenWeights"][current], min(items[current]["weight"], previous["remaining"]))
                order = state["order"]
                if step.action != "initial":
                    self.assertEqual(order, sorted(order, key=lambda item: (-Fraction(items[item]["value"], items[item]["weight"]), item)))

    def test_inputs_and_nested_snapshots_are_independent(self):
        from backend.algorithms.huffman import DEFAULT_INPUT as HUFFMAN
        from backend.algorithms.activity_selection import DEFAULT_INPUT as ACTIVITY
        from backend.algorithms.fractional_knapsack import DEFAULT_INPUT as KNAPSACK
        for model, run, payload, key in ((HuffmanInput, run_huffman, HUFFMAN, "nodes"),
                                         (ActivityInput, run_activity, ACTIVITY, "activities"),
                                         (KnapsackInput, run_knapsack, KNAPSACK, "items")):
            parsed = model.model_validate(payload)
            original = parsed.model_dump()
            result = run(parsed)
            self.assertEqual(parsed.model_dump(), original)
            result.steps[0].stateData[key][0]["testMutation"] = True
            self.assertNotIn("testMutation", result.steps[1].stateData[key][0])
