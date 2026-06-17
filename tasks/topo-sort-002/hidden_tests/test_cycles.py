"""Hidden tests: cycles must raise ValueError, and DAG output must be complete.

A graph with any directed cycle has no topological ordering, so toposort must
raise ValueError (not return a partial/empty list). For a DAG, every node must
appear exactly once in the output.
"""
import pytest

from toposort import toposort


def _all_nodes(graph):
    nodes = set(graph)
    for succ in graph.values():
        nodes.update(succ)
    return nodes


# ---- cycles must raise ValueError -----------------------------------------

def test_self_loop_raises():
    with pytest.raises(ValueError):
        toposort({"a": ["a"]})


def test_two_node_cycle_raises():
    with pytest.raises(ValueError):
        toposort({"a": ["b"], "b": ["a"]})


def test_three_node_cycle_raises():
    with pytest.raises(ValueError):
        toposort({"a": ["b"], "b": ["c"], "c": ["a"]})


def test_cycle_with_tail_raises():
    # A clean DAG prefix that feeds into a cycle must still be rejected.
    graph = {"s": ["a"], "a": ["b"], "b": ["c"], "c": ["a"]}
    with pytest.raises(ValueError):
        toposort(graph)


def test_cycle_plus_separate_dag_raises():
    # Some nodes are perfectly sortable; the presence of any cycle still fails.
    graph = {"x": ["y"], "y": [], "p": ["q"], "q": ["p"]}
    with pytest.raises(ValueError):
        toposort(graph)


def test_does_not_silently_return_partial_on_cycle():
    # Regression guard against "silently emit what you can" behavior.
    graph = {"a": ["b"], "b": ["c"], "c": ["b"]}
    try:
        result = toposort(graph)
    except ValueError:
        return
    pytest.fail(f"expected ValueError on cyclic graph, got {result!r}")


# ---- DAG output must contain every node exactly once ----------------------

def test_every_node_exactly_once_diamond():
    graph = {"a": ["b", "c"], "b": ["d"], "c": ["d"], "d": []}
    order = toposort(graph)
    assert sorted(order) == sorted(_all_nodes(graph))
    assert len(order) == len(set(order))


def test_every_node_exactly_once_with_successor_only_nodes():
    # 'd' and 'e' appear only as successors, never as keys.
    graph = {"a": ["b", "d"], "b": ["e"], "c": ["e"]}
    order = toposort(graph)
    expected = _all_nodes(graph)
    assert set(order) == expected
    assert len(order) == len(expected)
