"""A standalone ascending Bubble Sort example, independent of Ollama."""


def bubble_sort(values: list[int]) -> list[int]:
    """Return a sorted copy of values, leaving the original list unchanged.

    Compare adjacent elements and swap them when they are out of order.
    Each pass moves the largest remaining element to the end of the range.
    Stop early when a pass makes no swaps.

    Time: O(n squared) in the worst case, O(n) for already sorted input.
    Space: O(n) for the copy; the sorting loop uses O(1) extra space.
    """
    result = list(values)
    for end in range(len(result) - 1, 0, -1):
        swapped = False
        for index in range(end):
            if result[index] > result[index + 1]:
                result[index], result[index + 1] = result[index + 1], result[index]
                swapped = True
        if not swapped:
            break
    return result


if __name__ == "__main__":
    numbers = [5, 2, 8, 1]
    print("Input: ", numbers)
    print("Sorted:", bubble_sort(numbers))
