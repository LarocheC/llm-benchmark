"""Fold a collection of intervals into the minimal sorted, non-overlapping set.

The public entry point is :func:`merge_intervals`. It accepts either
``Interval`` instances or plain ``[start, end]`` pairs, normalises them, sorts
by start (then end), and folds connected runs together.
"""
from __future__ import annotations

from .interval import Interval


def _coerce(item):
    if isinstance(item, Interval):
        return item
    return Interval.from_pair(item)


def merge_intervals(raw):
    """Merge ``raw`` intervals into a sorted list of disjoint ``Interval``s.

    ``raw`` is any iterable of ``Interval`` objects or ``[start, end]`` pairs.
    The result contains no two intervals that overlap or touch; it is sorted by
    start coordinate. The input is not mutated.
    """
    items = [_coerce(item) for item in raw]
    if not items:
        return []

    items.sort(key=lambda iv: (iv.start, iv.end))

    merged = [items[0]]
    for current in items[1:]:
        last = merged[-1]
        if last.connects(current):
            merged[-1] = last.union(current)
        else:
            merged.append(current)
    return merged


def merge_pairs(raw):
    """Convenience wrapper returning plain ``[start, end]`` lists."""
    return [iv.as_pair() for iv in merge_intervals(raw)]
