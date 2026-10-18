"""Prim's minimum spanning forest, restarting at unvisited components."""


def prim(nodes, edges, start):
    """Return selected input edge indexes and total weight.

    edges contains undirected (source, target, weight) tuples.
    This simple cut-edge scan takes O(VE + V squared) time and O(V + E) space.
    """
    visited = set()
    selected = []
    for root in [start] + [node for node in nodes if node != start]:
        if root in visited:
            continue
        visited.add(root)
        while True:
            candidates = [index for index, (source, target, _) in enumerate(edges)
                          if (source in visited) != (target in visited)]
            if not candidates:
                break
            index = min(candidates, key=lambda index: (edges[index][2], index))
            source, target, weight = edges[index]
            selected.append(index)
            visited.update((source, target))
    return {"edges": selected, "totalWeight": sum(edges[index][2] for index in selected)}
