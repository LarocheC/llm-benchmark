"""intervals: merge closed integer intervals into a minimal disjoint set."""
from .interval import Interval
from .merge import merge_intervals, merge_pairs

__all__ = ["Interval", "merge_intervals", "merge_pairs"]
