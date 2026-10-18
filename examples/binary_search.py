"""Binary Search over ascending data; return the first matching index."""


def binary_search(values: list[int], target: int) -> int:
    """Return the first index of target, or -1. O(log n) time, O(1) space.

    values must already be sorted in ascending order. Input is not modified.
    """
    low, high = 0, len(values) - 1
    found = -1
    while low <= high:
        middle = (low + high) // 2
        if values[middle] < target:
            low = middle + 1
        else:
            if values[middle] == target:
                found = middle
            high = middle - 1
    return found


if __name__ == "__main__":
    print(binary_search([1, 2, 5, 8, 12, 16, 23], 8))
