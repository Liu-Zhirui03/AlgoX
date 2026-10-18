"""Maximum-cardinality activity selection using earliest finishing time."""


def activity_selection(activities):
    """Return input indexes of a maximum-size non-overlapping schedule.

    activities contains (name, start, finish) with 0 <= start < finish.
    Intervals are half-open: [start, finish), so touching endpoints are allowed.
    Sort by finish time, breaking ties by input order. O(n log n) time.
    """
    order = sorted(range(len(activities)), key=lambda index: (activities[index][2], index))
    selected = []
    last_finish = None
    for index in order:
        name, start, finish = activities[index]
        if last_finish is None or start >= last_finish:
            selected.append(index)
            last_finish = finish
    return {"selected": selected, "count": len(selected)}
