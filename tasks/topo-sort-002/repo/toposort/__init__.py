"""Topological sorting for directed graphs.

A graph is a ``dict`` mapping each node to a list of its successor nodes
(i.e. ``graph[u]`` is the list of ``v`` such that there is an edge ``u -> v``).

The public entry point is :func:`toposort`, which returns a linear ordering of
all nodes such that every edge ``u -> v`` has ``u`` appearing before ``v``.
"""
from .sorter import toposort
from .errors import GraphError, CycleError

__all__ = ["toposort", "GraphError", "CycleError"]
