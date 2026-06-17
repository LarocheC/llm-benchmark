"""Hidden tests: exponentiation must be right-associative, i.e. a ** b ** c == a ** (b ** c)."""
from calc import evaluate


def test_chain_2_3_2():
    assert evaluate("2 ** 3 ** 2") == 512        # 2 ** (3 ** 2); left-assoc would give 64


def test_chain_2_2_3():
    assert evaluate("2 ** 2 ** 3") == 256        # 2 ** (2 ** 3); left-assoc would give 64


def test_chain_4_3_2():
    assert evaluate("4 ** 3 ** 2") == 262144     # 4 ** (3 ** 2); left-assoc would give 4096


def test_chain_with_precedence():
    assert evaluate("2 ** 3 ** 2 + 1") == 513    # (2 ** (3 ** 2)) + 1; left-assoc would give 65
