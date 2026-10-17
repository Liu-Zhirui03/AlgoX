"""Check sorting results and each partition/buffer transition independently."""

from collections import Counter
from itertools import product
import unittest

from backend.algorithms.quick_sort import quick_sort_steps
from backend.algorithms.merge_sort import merge_sort_steps
from examples.quick_sort import quick_sort
from examples.merge_sort import merge_sort


class PartitionMergeTests(unittest.TestCase):
    def cases(self):
        for size in range(6):
            for values in product((-1, 0, 1), repeat=size):
                yield list(values)
        yield list(range(20))
        yield list(range(20, 0, -1))
        yield [0] * 20
        yield [-9007199254740991, 9007199254740991, 0]

    def assert_common(self, values, function, trace):
        original = values.copy()
        result = function(values)
        self.assertEqual(values, original)
        self.assertEqual(result, sorted(values))
        self.assertIsNot(result, values)
        steps = trace(values)
        self.assertEqual(values, original)
        self.assertEqual(steps[0].stateData, values)
        self.assertEqual(steps[-1].stateData, result)
        self.assertEqual(steps[-1].sortedIndices, list(range(len(values))))
        self.assertEqual(steps[-1].action, "complete")
        for index, step in enumerate(steps):
            self.assertEqual(step.stepIndex, index)
            self.assertTrue(step.explanation)
            self.assertEqual(Counter(step.stateData), Counter(values))
            for position in step.highlights + step.sortedIndices:
                self.assertTrue(0 <= position < len(values))
            for position in step.sortedIndices:
                self.assertEqual(step.stateData[position], result[position])
            if step.activeRange:
                low, high = step.activeRange
                self.assertTrue(0 <= low <= high < len(values))
                self.assertTrue(all(low <= position <= high for position in step.highlights))
        return steps

    def test_quick_sort_swaps_and_fixed_pivots(self):
        for values in self.cases():
            steps = self.assert_common(values, quick_sort, quick_sort_steps)
            for index, step in enumerate(steps):
                if step.pivotIndex is not None:
                    self.assertIn(step.pivotIndex, range(step.activeRange[0], step.activeRange[1] + 1))
                if index == 0:
                    continue
                previous = steps[index - 1]
                if step.action == "swap":
                    left, right = step.highlights
                    self.assertNotEqual(left, right)
                    expected = previous.stateData.copy()
                    expected[left], expected[right] = expected[right], expected[left]
                    self.assertEqual(step.stateData, expected)
                else:
                    self.assertEqual(step.stateData, previous.stateData)
                if step.action == "partition_complete" and len(step.sortedIndices) > len(previous.sortedIndices):
                    pivot = next(iter(set(step.sortedIndices) - set(previous.sortedIndices)))
                    low, high = step.activeRange
                    self.assertTrue(all(value <= step.stateData[pivot] for value in step.stateData[low:pivot]))
                    self.assertTrue(all(value > step.stateData[pivot] for value in step.stateData[pivot + 1:high + 1]))

    def test_merge_sort_buffer_appends_and_copy_back(self):
        for values in self.cases():
            steps = self.assert_common(values, merge_sort, merge_sort_steps)
            for index, step in enumerate(steps[1:], 1):
                previous = steps[index - 1]
                if step.action == "take":
                    source, = step.highlights
                    self.assertEqual(step.buffer, previous.buffer + [previous.stateData[source]])
                    self.assertEqual(step.stateData, previous.stateData)
                    self.assertEqual(step.buffer, sorted(step.buffer))
                    if previous.action == "compare":
                        left, right = previous.highlights
                        expected_source = left if previous.stateData[left] <= previous.stateData[right] else right
                        self.assertEqual(source, expected_source)
                elif step.action == "merge":
                    low, high = step.activeRange
                    self.assertEqual(step.buffer, sorted(previous.stateData[low:high + 1]))
                    expected = previous.stateData.copy()
                    expected[low:high + 1] = step.buffer
                    self.assertEqual(step.stateData, expected)
                else:
                    self.assertEqual(step.stateData, previous.stateData)

    def test_snapshots_have_independent_arrays_and_buffers(self):
        for trace in (quick_sort_steps, merge_sort_steps):
            steps = trace([4, 1, 3, 2])
            self.assertEqual(len({id(step.stateData) for step in steps}), len(steps))
            self.assertEqual(len({id(step.highlights) for step in steps}), len(steps))
            buffers = [step.buffer for step in steps if step.buffer is not None]
            self.assertEqual(len({id(buffer) for buffer in buffers}), len(buffers))
