"""Validate recorded execution transitions independently of rendering."""

from collections import Counter
from itertools import product
import unittest

from backend.algorithms.bubble_sort import bubble_sort_steps


class TraceTests(unittest.TestCase):
    def test_traces_preserve_values_and_follow_adjacent_swaps(self):
        for length in range(6):
            for values in product((-1, 0, 1), repeat=length):
                original = list(values)
                steps = bubble_sort_steps(original)
                self.assertEqual(original, list(values))
                self.assertEqual(steps[0].stateData, original)
                self.assertEqual(steps[-1].stateData, sorted(values))
                self.assertEqual(steps[-1].action, "complete")
                self.assertEqual(steps[-1].sortedIndices, list(range(length)))
                expected = sorted(values)
                for index, step in enumerate(steps):
                    self.assertEqual(step.stepIndex, index)
                    self.assertEqual(Counter(step.stateData), Counter(values))
                    for settled in step.sortedIndices:
                        self.assertEqual(step.stateData[settled], expected[settled])
                    for highlight in step.highlights:
                        self.assertTrue(0 <= highlight < length)
                    if step.action == "swap":
                        previous = steps[index - 1]
                        self.assertEqual(previous.action, "compare")
                        left, right = step.highlights
                        self.assertEqual(right, left + 1)
                        self.assertGreater(previous.stateData[left], previous.stateData[right])
                        changed = previous.stateData.copy()
                        changed[left], changed[right] = changed[right], changed[left]
                        self.assertEqual(step.stateData, changed)
                    elif index:
                        self.assertEqual(step.stateData, steps[index - 1].stateData)

    def test_twenty_reversed_values_record_all_comparisons_and_swaps(self):
        steps = bubble_sort_steps(list(range(20, 0, -1)))
        self.assertEqual(sum(step.action == "compare" for step in steps), 190)
        self.assertEqual(sum(step.action == "swap" for step in steps), 190)
        self.assertEqual(steps[-1].stateData, list(range(1, 21)))

    def test_sorted_input_exits_after_one_pass(self):
        steps = bubble_sort_steps(list(range(20)))
        self.assertEqual(sum(step.action == "compare" for step in steps), 19)
        self.assertFalse(any(step.action == "swap" for step in steps))

    def test_snapshots_do_not_share_mutable_lists(self):
        steps = bubble_sort_steps([3, 1, 2])
        steps[0].stateData[0] = 999
        self.assertEqual(steps[1].stateData, [3, 1, 2])
