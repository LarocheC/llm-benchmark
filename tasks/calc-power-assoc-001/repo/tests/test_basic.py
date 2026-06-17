from calc import evaluate


def test_addition():
    assert evaluate("1 + 2") == 3


def test_precedence_mul_over_add():
    assert evaluate("2 + 3 * 4") == 14


def test_parentheses():
    assert evaluate("(2 + 3) * 4") == 20


def test_subtraction_left_associative():
    assert evaluate("10 - 3 - 2") == 5


def test_division():
    assert evaluate("8 / 2") == 4


def test_single_power():
    assert evaluate("2 ** 3") == 8


def test_unary_minus():
    assert evaluate("-5 + 2") == -3


def test_nested_expression():
    assert evaluate("2 * (3 + 4) - 1") == 13
