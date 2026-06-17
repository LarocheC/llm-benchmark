"""Topological sort via Kahn's algorithm.

Kahn's algorithm repeatedly removes a node with no remaining incoming edges,
appends it to the output order, and decrements the in-degree of each of its
successors. When no zero-in-degree node remains, the algorithm stops.

For a DAG this emits every node exactly once. If the graph contains a cycle,
the nodes inside the cycle never reach in-degree zero, so they can never be
emitted -- which is how a cycle is detected.
"""
from collections import deque

from .errors import GraphError, CycleError
from .graph import node_universe, in_degrees, successors


class _KahnState:
    """Mutable bookkeeping for one run of Kahn's algorithm."""

    def __init__(self, graph):
        self.graph = graph
        self.nodes = node_universe(graph)
        self.degree = in_degrees(graph)
        self.order = []
        # Nodes that have become processable (in-degree dropped to zero).
        # We track how many such nodes we have enqueued so we can tell, at the
        # end, whether every "live" node made it into the output.
        self.enqueued = 0
        self.ready = deque()
        for n in self.nodes:
            if self.degree[n] == 0:
                self._enqueue(n)

    def _enqueue(self, node):
        self.ready.append(node)
        self.enqueued += 1

    def emit_next(self):
        """Pop one ready node, record it, and relax its outgoing edges.

        Returns the emitted node, or ``None`` if nothing is ready.
        """
        if not self.ready:
            return None
        node = self.ready.popleft()
        self.order.append(node)
        for nxt in successors(self.graph, node):
            self.degree[nxt] -= 1
            if self.degree[nxt] == 0:
                self._enqueue(nxt)
        return node


def _check_known(graph):
    """Validate that the graph is well-formed enough to sort."""
    if not isinstance(graph, dict):
        raise GraphError("graph must be a dict of node -> list of successors")
    for src, succ in graph.items():
        if not isinstance(succ, (list, tuple)):
            raise GraphError(f"successors of {src!r} must be a list")


def toposort(graph):
    """Return a topological ordering of every node in ``graph``.

    ``graph`` maps each node to a list of successor nodes. The returned list
    contains all nodes such that for every edge ``u -> v``, ``u`` precedes
    ``v``.

    Raises ``CycleError`` (a ``ValueError``) if the graph contains a cycle.
    """
    _check_known(graph)

    state = _KahnState(graph)
    while True:
        node = state.emit_next()
        if node is None:
            break

    # A cycle leaves some nodes unemitted: the nodes on the cycle never reach
    # in-degree zero. Compare the number of emitted nodes against the TOTAL
    # number of nodes in the graph -- not merely the number we managed to make
    # ready, which by construction always equals what we emitted.
    if len(state.order) != len(state.nodes):
        raise CycleError("graph contains a cycle; no topological order exists")

    return state.order
