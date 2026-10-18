"""Fractional knapsack, taking items by descending value-to-weight ratio."""


def fractional_knapsack(items, capacity):
    """Return fractions, used weight, and value. Items are (name, weight, value).

    Weights must be positive, values/capacity nonnegative. Fractions are allowed.
    Ratios and accumulated value are calculated exactly before conversion to
    floats for display. O(n log n) time; equal ratios keep input order.
    """
    from fractions import Fraction

    order = sorted(range(len(items)), key=lambda index: (-Fraction(items[index][2], items[index][1]), index))
    taken = [0.0] * len(items)
    remaining = capacity
    total = Fraction(0)
    for index in order:
        name, weight, value = items[index]
        if remaining == 0 or value == 0:
            continue
        amount = min(weight, remaining)
        taken[index] = float(Fraction(amount, weight))
        total += Fraction(amount * value, weight)
        remaining -= amount
    return {"fractions": taken, "totalWeight": capacity - remaining, "totalValue": float(total)}
