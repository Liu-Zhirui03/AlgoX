"""Verify search results and exact bound/table transitions."""

from itertools import combinations_with_replacement, product
import unittest

from examples.binary_search import binary_search
from examples.hash_search import hash_search
from backend.algorithms.binary_search import binary_search_steps
from backend.algorithms.hash_search import hash_search_steps


class SearchTests(unittest.TestCase):
    def test_binary_bounds_and_first_occurrences(self):
        for length in range(6):
            for sequence in combinations_with_replacement((-2, -1, 0, 1, 2), length):
                values = list(sequence)
                for target in (-3, -1, 0, 1, 3):
                    expected = values.index(target) if target in values else -1
                    original = values.copy()
                    self.assertEqual(binary_search(values, target), expected)
                    steps = binary_search_steps(values, target)
                    self.assertEqual(values, original)
                    self.assertEqual(steps[-1].stateData.foundIndex, expected)
                    for index, step in enumerate(steps):
                        state = step.stateData
                        self.assertEqual(step.stepIndex, index)
                        self.assertEqual(state.values, values)
                        if step.action == "compare":
                            self.assertLessEqual(state.low, state.high)
                            self.assertEqual(state.middle, (state.low + state.high) // 2)
                            self.assertEqual(step.highlights, [state.middle])
                        if step.action == "discard":
                            previous = steps[index - 1].stateData
                            self.assertEqual(steps[index - 1].action, "compare")
                            if values[previous.middle] < target:
                                self.assertEqual(state.low, previous.middle + 1)
                                self.assertEqual(state.high, previous.high)
                            else:
                                self.assertEqual(state.high, previous.middle - 1)
                                self.assertEqual(state.low, previous.low)
                            if state.candidate is not None:
                                self.assertEqual(values[state.candidate], target)
                    self.assertGreater(steps[-1].stateData.low, steps[-1].stateData.high)

    def test_hash_table_build_and_lookup_chains(self):
        for length in range(5):
            for sequence in product((-3, 0, 3), repeat=length):
                values = list(sequence)
                original = values.copy()
                for count in (3, 7, 16):
                    for target in (-3, 0, 2, 3):
                        expected = values.index(target) if target in values else -1
                        self.assertEqual(hash_search(values, target, count), expected)
                        steps = hash_search_steps(values, target, count)
                        self.assertEqual(values, original)
                        self.assertEqual(steps[-1].stateData.foundIndex, expected)
                        expected_table = [[] for _ in range(count)]
                        for index, step in enumerate(steps):
                            state = step.stateData
                            self.assertEqual(step.stepIndex, index)
                            self.assertEqual(state.values, values)
                            if step.action == "insert":
                                source = state.inputIndex
                                bucket = values[source] % count
                                self.assertEqual(state.bucketIndex, bucket)
                                expected_table[bucket].append({"value": values[source], "index": source})
                            actual = [[item.model_dump() for item in chain] for chain in state.buckets]
                            self.assertEqual(actual, expected_table)
                            if step.action == "compare":
                                self.assertEqual(state.bucketIndex, target % count)
                                entry = state.buckets[state.bucketIndex][state.entryIndex]
                                self.assertEqual(entry.value, values[entry.index])
                            if step.action == "collision":
                                self.assertTrue(state.buckets[state.bucketIndex])
                        self.assertEqual(sum(step.action == "insert" for step in steps), len(values))

    def test_search_snapshots_are_independent(self):
        binary = binary_search_steps([1, 2, 2, 4], 2)
        binary[0].stateData.values[0] = 99
        self.assertEqual(binary[1].stateData.values, [1, 2, 2, 4])
        hashed = hash_search_steps([10, 17, 24], 24)
        inserted = [step for step in hashed if step.action == "insert"]
        inserted[0].stateData.buckets[3][0].value = 99
        self.assertEqual(inserted[1].stateData.buckets[3][0].value, 10)
