# intervals

A tiny library for merging closed integer intervals.

```python
from intervals import merge_pairs
merge_pairs([[1, 4], [2, 6], [8, 10]])   # [[1, 6], [8, 10]]
```

Intervals are `[start, end]` and **inclusive** of both endpoints.
`merge_intervals` / `merge_pairs` normalise the input, sort it, and fold
connected runs into the minimal set of non-overlapping intervals.

Pipeline: `interval` (the `Interval` value type + relational helpers) →
`merge` (sort and fold).

Run the tests with `pytest`.
