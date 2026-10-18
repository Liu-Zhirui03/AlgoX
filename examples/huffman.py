"""Huffman coding from positive symbol frequencies, with deterministic ties."""


def huffman(symbols):
    """Return prefix codes and weighted bit cost. O(n log n) tree construction.

    symbols is a list of (symbol, positive frequency) pairs with unique symbols.
    Equal frequencies use creation order. A single symbol receives code 0.
    """
    from heapq import heapify, heappop, heappush

    heap = [(frequency, index, (symbol, None, None))
            for index, (symbol, frequency) in enumerate(symbols)]
    heapify(heap)
    serial = len(symbols)
    while len(heap) > 1:
        left_weight, _, left = heappop(heap)
        right_weight, _, right = heappop(heap)
        heappush(heap, (left_weight + right_weight, serial, (None, left, right)))
        serial += 1
    codes = {}
    stack = [(heap[0][2], "")]
    while stack:
        (symbol, left, right), code = stack.pop()
        if symbol is not None:
            codes[symbol] = code or "0"
        else:
            stack.append((right, code + "1"))
            stack.append((left, code + "0"))
    return {"codes": codes, "weightedCost": sum(frequency * len(codes[symbol]) for symbol, frequency in symbols)}
