"""The Interval value type and the relational helpers used by the merger.

Intervals are CLOSED / INCLUSIVE: ``Interval(1, 3)`` denotes the integer set
``{1, 2, 3}``. Because the endpoints are inclusive, two intervals already form a
single contiguous run when the later one starts no more than one unit past the
end of the earlier one (e.g. ``[1, 2]`` and ``[3, 4]`` together cover ``1..4``).
"""
from __future__ import annotations


class Interval:
    """A closed integer interval ``[start, end]`` with ``start <= end``."""

    __slots__ = ("start", "end")

    def __init__(self, start, end):
        if not isinstance(start, int) or not isinstance(end, int):
            raise TypeError("interval endpoints must be ints")
        if start > end:
            raise ValueError(f"start {start} must be <= end {end}")
        self.start = start
        self.end = end

    # --- construction -----------------------------------------------------
    @classmethod
    def from_pair(cls, pair):
        """Build an Interval from a 2-element ``[start, end]`` sequence."""
        start, end = pair
        return cls(start, end)

    def as_pair(self):
        """Return the interval as a plain ``[start, end]`` list."""
        return [self.start, self.end]

    # --- relations --------------------------------------------------------
    def reaches(self, other):
        """How far ``other.start`` sits past the end of ``self``.

        Assumes ``self`` starts no later than ``other``. The result is the
        signed distance from this interval's end to the other's start:

        * ``< 0``  -> the intervals physically overlap,
        * ``== 0`` -> they touch at a shared endpoint (e.g. ``[1,2]`` & ``[2,3]``),
        * ``== 1`` -> they are immediately adjacent with no integer between them
          (e.g. ``[1,2]`` & ``[3,4]``, which together cover ``1..4``),
        * ``> 1``  -> a genuine gap separates them.
        """
        return other.start - self.end

    def connects(self, other):
        """True if ``self`` and ``other`` belong to the same merged run.

        ``self`` is assumed to start no later than ``other`` (the merger feeds
        intervals in sorted order). Two inclusive intervals form one run when
        they overlap *or* sit flush against each other.
        """
        return self.reaches(other) < 0

    def union(self, other):
        """Combine two connected intervals into the interval that covers both."""
        return Interval(min(self.start, other.start), max(self.end, other.end))

    # --- dunders ----------------------------------------------------------
    def __eq__(self, other):
        if not isinstance(other, Interval):
            return NotImplemented
        return self.start == other.start and self.end == other.end

    def __repr__(self):
        return f"Interval({self.start}, {self.end})"
