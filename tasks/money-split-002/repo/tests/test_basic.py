from moneysplit import split_amount


def test_divisible_by_4():
    assert split_amount(100, 4) == [25, 25, 25, 25]


def test_divisible_by_2():
    assert split_amount(10, 2) == [5, 5]


def test_divisible_by_5():
    assert split_amount(50, 5) == [10, 10, 10, 10, 10]


def test_single_part_gets_everything():
    assert split_amount(137, 1) == [137]


def test_divisible_sum_matches():
    parts = split_amount(60, 3)
    assert sum(parts) == 60
    assert parts == [20, 20, 20]


def test_zero_total_is_all_zeros():
    assert split_amount(0, 4) == [0, 0, 0, 0]


def test_length_is_n():
    assert len(split_amount(99, 3)) == 3


def test_parts_within_one_cent():
    # max - min <= 1 holds even for the buggy (all-equal) output.
    parts = split_amount(100, 3)
    assert max(parts) - min(parts) <= 1


def test_rejects_zero_parts():
    try:
        split_amount(100, 0)
    except ValueError:
        return
    raise AssertionError("expected ValueError for n == 0")


def test_rejects_negative_total():
    try:
        split_amount(-5, 2)
    except ValueError:
        return
    raise AssertionError("expected ValueError for negative total")
