"""Stable Merge Sort with a temporary buffer for each merge."""


def merge_sort(values: list[int]) -> list[int]:
    """Return a sorted copy in O(n log n) time and O(n) auxiliary space."""
    result = list(values)

    def sort(low, high):
        if low >= high:
            return
        middle = (low + high) // 2
        sort(low, middle)
        sort(middle + 1, high)
        left, right = low, middle + 1
        buffer = []
        while left <= middle and right <= high:
            if result[left] <= result[right]:
                buffer.append(result[left])
                left += 1
            else:
                buffer.append(result[right])
                right += 1
        buffer.extend(result[left:middle + 1])
        buffer.extend(result[right:high + 1])
        result[low:high + 1] = buffer

    sort(0, len(result) - 1)
    return result


if __name__ == "__main__":
    numbers = [5, 2, 8, 1]
    print("Input: ", numbers)
    print("Sorted:", merge_sort(numbers))
