"""Exception types raised by the toposort package.

``CycleError`` is a subclass of the built-in ``ValueError`` so that callers may
catch either the specific type or the broad ``ValueError`` contract.
"""


class GraphError(ValueError):
    """Base class for malformed-graph problems (e.g. a node referenced as a
    successor but missing from the graph definition)."""


class CycleError(ValueError):
    """Raised when the graph contains at least one directed cycle and therefore
    has no valid topological ordering."""
