"""Graph normalization and bookkeeping helpers used by the sorter.

These helpers turn a user-supplied ``dict node -> [successors]`` into the
structures Kahn's algorithm needs: the full set of nodes, an adjacency view,
and an in-degree table.
"""


def successors(graph, node):
    """Return the list of successors of ``node`` (empty list if unknown)."""
    return graph.get(node, [])


def node_universe(graph):
    """Return every node that participates in the graph.

    A node participates if it is declared as a key *or* if it appears as a
    successor of some other node. The result is ordered: declared keys first
    (in insertion order), then any successor-only nodes in first-seen order.
    """
    seen = {}
    for src in graph:
        seen.setdefault(src, None)
    for src in graph:
        for dst in graph[src]:
            seen.setdefault(dst, None)
    return list(seen)


def in_degrees(graph):
    """Return ``{node: number_of_incoming_edges}`` for every node.

    Every node in the universe is present in the result, even sources (which
    map to ``0``).
    """
    degree = {node: 0 for node in graph}
    for src in graph:
        for dst in graph[src]:
            # Count an incoming edge for dst. Sources keep their initial 0.
            degree[dst] = degree.get(dst, 0) + 1
    return degree
