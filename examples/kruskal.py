"""Kruskal's minimum spanning forest with a union-find structure."""


def kruskal(nodes, edges):
    """Return selected input edge indexes and total weight.

    edges contains undirected (source, target, weight) tuples.
    Sorting costs O(E log E); union-find uses path compression and rank.
    Disconnected inputs produce a minimum spanning forest.
    """
    parent = {node: node for node in nodes}
    rank = {node: 0 for node in nodes}

    def find(node):
        while parent[node] != node:
            parent[node] = parent[parent[node]]
            node = parent[node]
        return node

    selected = []
    for index in sorted(range(len(edges)), key=lambda index: (edges[index][2], index)):
        source, target, weight = edges[index]
        left, right = find(source), find(target)
        if left == right:
            continue
        if rank[left] < rank[right]:
            left, right = right, left
        parent[right] = left
        if rank[left] == rank[right]:
            rank[left] += 1
        selected.append(index)
    return {"edges": selected, "totalWeight": sum(edges[index][2] for index in selected)}
