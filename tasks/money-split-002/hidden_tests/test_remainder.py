"""Hidden tests: non-divisible totals must still sum to total_cents exactly,
while parts stay within one cent of each other."""
from moneysplit import split_amount


def test_100_into_3_sums_exactly():
    parts = split_amount(100, 3)
    assert sum(parts) == 100
    assert sorted(parts) == [33, 33, 34]


def test_10_into_4_sums_exactly():
    parts = split_amount(10, 4)
    assert sum(parts) == 10
    assert sorted(parts) == [2, 2, 3, 3]


def test_20_into_6_sums_exactly():
    parts = split_amount(20, 6)
    assert sum(parts) == 20
    assert sorted(parts) == [3, 3, 3, 3, 4, 4]


def test_remainder_parts_are_within_one_cent():
    parts = split_amount(101, 7)
    assert sum(parts) == 101
    assert max(parts) - min(parts) <= 1


def test_exactly_remainder_parts_are_larger():
    # 100 % 3 == 1, so exactly one part should be the larger value.
    parts = split_amount(100, 3)
    assert parts.count(max(parts)) == 1


def test_many_non_divisible_cases_sum_exactly():
    for total in range(0, 40):
        for n in range(1, 9):
            parts = split_amount(total, n)
            assert sum(parts) == total, (total, n, parts)
            assert len(parts) == n
            assert max(parts) - min(parts) <= 1


def test_large_total_sums_exactly():
    parts = split_amount(1_000_003, 7)
    assert sum(parts) == 1_000_003
    assert max(parts) - min(parts) <= 1
