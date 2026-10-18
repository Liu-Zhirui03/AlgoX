"""Dijkstra's shortest paths for an undirected, nonnegative weighted graph."""


def dijkstra(nodes, edges, start):
    """Return distances (None means unreachable) and predecessor nodes.

    edges contains (source, target, weight) tuples; weights must be nonnegative.
    With a linear minimum scan: O(V squared + E) time, O(V + E) space.
    """
    adjacency = {node: [] for node in nodes}
    for source, target, weight in edges:
        adjacency[source].append((target, weight))
        adjacency[target].append((source, weight))
    distances = {node: None for node in nodes}
    parents = {node: None for node in nodes}
    distances[start] = 0
    visited = set()
    while True:
        reachable = [node for node in nodes if node not in visited and distances[node] is not None]
        if not reachable:
            break
        current = min(reachable, key=lambda node: distances[node])
        visited.add(current)
        for neighbor, weight in adjacency[current]:
            if neighbor in visited:
                continue
            candidate = distances[current] + weight
            if distances[neighbor] is None or candidate < distances[neighbor]:
                distances[neighbor] = candidate
                parents[neighbor] = current
    return {"distances": distances, "parents": parents}
