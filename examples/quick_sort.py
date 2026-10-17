"""Quick Sort with a last-element pivot and Lomuto partitioning."""


def quick_sort(values: list[int]) -> list[int]:
    """Return a sorted copy. Average O(n log n), worst O(n squared) time.

    The copy takes O(n) space; recursion uses O(log n) average, O(n) worst.
    """
    result = list(values)

    def sort(low, high):
        if low >= high:
            return
        pivot = result[high]
        boundary = low
        for index in range(low, high):
            if result[index] <= pivot:
                result[boundary], result[index] = result[index], result[boundary]
                boundary += 1
        result[boundary], result[high] = result[high], result[boundary]
        sort(low, boundary - 1)
        sort(boundary + 1, high)

    sort(0, len(result) - 1)
    return result


if __name__ == "__main__":
    numbers = [5, 2, 8, 1]
    print("Input: ", numbers)
    print("Sorted:", quick_sort(numbers))
