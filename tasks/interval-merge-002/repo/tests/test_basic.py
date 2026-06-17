"""Baseline behaviour: clearly-overlapping intervals merge, clearly-disjoint
intervals (separated by a real gap) stay apart."""
from intervals import Interval, merge_intervals, merge_pairs


def test_empty():
    assert merge_pairs([]) == []


def test_single_interval():
    assert merge_pairs([[1, 5]]) == [[1, 5]]


def test_two_overlapping():
    assert merge_pairs([[1, 4], [2, 6]]) == [[1, 6]]


def test_contained_interval():
    # [3, 4] is fully inside [1, 10]
    assert merge_pairs([[1, 10], [3, 4]]) == [[1, 10]]


def test_clearly_disjoint_kept_apart():
    # gap of several integers between them (5..9 missing), must NOT merge
    assert merge_pairs([[1, 4], [10, 12]]) == [[1, 4], [10, 12]]


def test_disjoint_with_two_unit_gap():
    # [1, 3] then [5, 7]: integer 4 separates them, must stay apart
    assert merge_pairs([[1, 3], [5, 7]]) == [[1, 3], [5, 7]]


def test_unsorted_input_is_sorted():
    assert merge_pairs([[10, 12], [1, 4]]) == [[1, 4], [10, 12]]


def test_overlapping_chain_collapses():
    assert merge_pairs([[1, 5], [4, 9], [8, 12]]) == [[1, 12]]


def test_mixed_overlap_and_gap():
    assert merge_pairs([[1, 4], [2, 5], [20, 25], [22, 30]]) == [[1, 5], [20, 30]]


def test_accepts_interval_objects():
    out = merge_intervals([Interval(1, 4), Interval(2, 8)])
    assert out == [Interval(1, 8)]


def test_input_not_mutated():
    data = [[5, 9], [1, 6]]
    merge_pairs(data)
    assert data == [[5, 9], [1, 6]]


def test_negative_coordinates_overlap():
    assert merge_pairs([[-10, -3], [-5, 0]]) == [[-10, 0]]
