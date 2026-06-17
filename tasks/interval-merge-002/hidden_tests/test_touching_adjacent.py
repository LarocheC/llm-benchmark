"""Hidden tests: under inclusive [start, end] semantics, intervals that merely
touch at a shared endpoint OR are immediately adjacent (no integer between
them) must collapse into a single interval."""
from intervals import Interval, merge_intervals, merge_pairs


def test_touching_shared_endpoint():
    # [1, 2] and [2, 3] share the point 2 -> one run covering 1..3
    assert merge_pairs([[1, 2], [2, 3]]) == [[1, 3]]


def test_adjacent_no_gap():
    # [1, 2] and [3, 4]: integers 1,2,3,4 are contiguous -> covers 1..4
    assert merge_pairs([[1, 2], [3, 4]]) == [[1, 4]]


def test_adjacent_unsorted():
    assert merge_pairs([[3, 4], [1, 2]]) == [[1, 4]]


def test_chain_of_adjacent():
    # [1,1],[2,2],[3,3],[4,4] are all contiguous integers -> 1..4
    assert merge_pairs([[1, 1], [2, 2], [3, 3], [4, 4]]) == [[1, 4]]


def test_chain_of_touching():
    assert merge_pairs([[1, 3], [3, 5], [5, 7]]) == [[1, 7]]


def test_touching_then_real_gap():
    # first two touch -> [1,4]; then a gap (6 missing) before [7,9]
    assert merge_pairs([[1, 2], [2, 4], [7, 9]]) == [[1, 4], [7, 9]]


def test_adjacent_then_gap():
    # [1,2]+[3,4] -> [1,4]; 5 missing; [6,7] separate
    assert merge_pairs([[1, 2], [3, 4], [6, 7]]) == [[1, 4], [6, 7]]


def test_adjacent_interval_objects():
    assert merge_intervals([Interval(10, 12), Interval(13, 15)]) == [Interval(10, 15)]


def test_singletons_touching():
    # identical single points and an adjacent one
    assert merge_pairs([[5, 5], [5, 5], [6, 6]]) == [[5, 6]]


def test_negative_adjacent():
    # [-3, -2] and [-1, 0] are contiguous integers -> -3..0
    assert merge_pairs([[-3, -2], [-1, 0]]) == [[-3, 0]]
