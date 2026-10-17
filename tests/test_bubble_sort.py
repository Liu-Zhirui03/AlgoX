"""Check reference sorting results and preservation of caller input."""

from itertools import product
import unittest

from examples.bubble_sort import bubble_sort


class BubbleSortTests(unittest.TestCase):
    def test_example(self):
        self.assertEqual(bubble_sort([5, 2, 8, 1]), [1, 2, 5, 8])

    def test_short_lists_match_python_sort_without_mutating_input(self):
        # Covers empty/single lists, duplicates, negative values, and all orders.
        for length in range(6):
            for values in product((-1, 0, 1), repeat=length):
                with self.subTest(values=values):
                    original = list(values)
                    result = bubble_sort(original)
                    self.assertEqual(result, sorted(values))
                    self.assertEqual(original, list(values))
                    self.assertIsNot(result, original)


if __name__ == "__main__":
    unittest.main()
