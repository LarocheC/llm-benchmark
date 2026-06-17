"""Hidden tests: a doubled quote inside a quoted field is a literal quote.

Under RFC 4180 / spreadsheet rules, ``""`` inside a quoted field encodes a
single ``"`` and parsing stays inside the field. These exercise fields that
contain embedded quotes, which the buggy scanner truncates at the first
inner quote.
"""
from csvkit import parse_csv_line


def test_escaped_quote_in_middle():
    assert parse_csv_line('"a""b"') == ['a"b']


def test_field_that_is_just_a_quote():
    assert parse_csv_line('""""') == ['"']


def test_escaped_quotes_then_more_text():
    assert parse_csv_line('"she said ""hi"" today"') == ['she said "hi" today']


def test_escaped_quote_field_followed_by_another_field():
    assert parse_csv_line('"a""b",c') == ['a"b', "c"]


def test_escaped_quote_with_comma_inside():
    assert parse_csv_line('"x="",""y",z') == ['x=","y', "z"]


def test_two_quoted_fields_with_escapes():
    assert parse_csv_line('"p""q","r""s"') == ['p"q', 'r"s']


def test_trailing_escaped_quote():
    assert parse_csv_line('"end with quote """') == ['end with quote "']
