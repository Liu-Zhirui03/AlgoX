"""Build a chained integer hash table, then look up the first matching index."""


def hash_search(values: list[int], target: int, bucket_count: int = 7) -> int:
    """Return the original index of target, or -1, using separate chaining.

    bucket_count must be positive. Build: O(n). Lookup: expected O(1 + n/m),
    worst O(n), for m buckets. Space: O(n + m). Input is not modified.
    """
    buckets = [[] for _ in range(bucket_count)]
    for index, value in enumerate(values):
        buckets[value % bucket_count].append((value, index))
    for value, index in buckets[target % bucket_count]:
        if value == target:
            return index
    return -1


if __name__ == "__main__":
    print(hash_search([10, 17, 24, 3, 10], 24))
