# `toposort` silently drops nodes instead of rejecting cyclic graphs

The `toposort` package orders the nodes of a directed graph so that every edge
points "forward". A graph is given as a `dict` mapping each node to a list of
its successor nodes:

```python
>>> from toposort import toposort
>>> toposort({"a": ["b"], "b": ["c"], "c": []})
['a', 'b', 'c']
```

A directed graph that contains a **cycle** has *no* valid topological ordering,
so `toposort` is documented to raise `ValueError` in that case (the package's
`CycleError` is a subclass of `ValueError`).

That contract is currently broken. On a cyclic graph, `toposort` does **not**
raise — it just returns whatever prefix of nodes it happened to be able to
order, swallowing the rest:

```python
>>> toposort({"a": ["b"], "b": ["c"], "c": ["b"]})
['a']          # WRONG — b and c form a cycle, but no error is raised
```

Expected:

```python
>>> toposort({"a": ["b"], "b": ["c"], "c": ["b"]})
ValueError: graph contains a cycle; no topological order exists
```

A pure cycle is even worse — it comes back empty:

```python
>>> toposort({"a": ["b"], "b": ["a"]})
[]             # WRONG — should raise ValueError
```

Ordering of genuinely acyclic graphs (DAGs) is correct and must stay that way;
the only problem is that cycles are not being detected, so impossible inputs are
accepted and reported as if they had succeeded.

Please fix the sorter so that any graph containing a directed cycle raises
`ValueError`, while valid DAGs continue to produce a correct ordering of all
their nodes.
