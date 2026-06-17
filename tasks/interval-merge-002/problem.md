# Touching / adjacent intervals are left unmerged

The `intervals` package merges a list of integer intervals into the minimal set
of non-overlapping intervals, sorted by start. Intervals are written
`[start, end]` and are **inclusive** of both endpoints, so `[1, 3]` denotes the
integers `{1, 2, 3}`.

Clearly-overlapping intervals merge fine, and intervals separated by a real gap
are correctly kept apart. The problem is at the boundary: intervals that **touch
at a shared endpoint** or are **immediately adjacent** (with no integer between
them) are being left as separate intervals, even though under inclusive
semantics they describe one contiguous run.

Example of the bug:

```python
>>> from intervals import merge_pairs
>>> merge_pairs([[1, 2], [3, 4]])
[[1, 2], [3, 4]]      # WRONG — 1, 2, 3, 4 are contiguous integers
```

Expected:

```python
>>> merge_pairs([[1, 2], [3, 4]])
[[1, 4]]              # the two intervals together cover 1..4
```

The covered integers `1, 2, 3, 4` form an unbroken run, so the result should be
the single interval `[1, 4]`. The same goes for intervals that share an
endpoint, e.g. `[1, 2]` and `[2, 3]` should collapse to `[1, 3]`.

Two intervals should be combined whenever the integers they cover form one
contiguous block — that is, when the later one starts no more than one unit past
where the earlier one ends. Intervals separated by at least one missing integer
must still be reported separately, and the existing behaviour for overlapping
and clearly-disjoint intervals must not change.

Please fix the merger so that touching and adjacent inclusive intervals are
merged.
