"""Existing tests: valid DAGs produce an order that respects every edge."""
from toposort import toposort


def _respects_edges(graph, order):
    """True iff for every edge u -> v, u appears before v in `order`."""
    pos = {node: i for i, node in enumerate(order)}
    for src in graph:
        for dst in graph[src]:
            if pos[src] >= pos[dst]:
                return False
    return True


def test_linear_chain():
    graph = {"a": ["b"], "b": ["c"], "c": []}
    order = toposort(graph)
    assert order == ["a", "b", "c"]


def test_diamond_respects_edges():
    graph = {"a": ["b", "c"], "b": ["d"], "c": ["d"], "d": []}
    order = toposort(graph)
    assert _respects_edges(graph, order)
    assert order[0] == "a"
    assert order[-1] == "d"


def test_multiple_sources():
    graph = {"a": ["c"], "b": ["c"], "c": ["d"], "d": []}
    order = toposort(graph)
    assert _respects_edges(graph, order)


def test_successor_only_node_present():
    # 'd' never appears as a key, only as a successor.
    graph = {"a": ["b"], "b": ["d"], "c": ["d"]}
    order = toposort(graph)
    assert _respects_edges(graph, order)


def test_empty_graph():
    assert toposort({}) == []


def test_single_node():
    assert toposort({"x": []}) == ["x"]


def test_two_independent_edges():
    graph = {"a": ["b"], "c": ["d"]}
    order = toposort(graph)
    assert _respects_edges(graph, order)


def test_wide_fanout():
    graph = {"root": ["a", "b", "c"], "a": [], "b": [], "c": []}
    order = toposort(graph)
    assert order[0] == "root"
    assert _respects_edges(graph, order)
