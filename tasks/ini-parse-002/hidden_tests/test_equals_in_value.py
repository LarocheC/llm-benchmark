"""Hidden tests: a value may itself contain '=' characters.

Only the FIRST '=' separates the key from the value; everything after it
(verbatim, aside from outer whitespace) is the value.
"""
from iniparse import parse_ini


def test_query_string_value():
    text = "[http]\nurl = a=1&b=2\n"
    assert parse_ini(text) == {"http": {"url": "a=1&b=2"}}


def test_base64_padding_value():
    text = "[auth]\ntoken = YWJjZA==\n"
    assert parse_ini(text) == {"auth": {"token": "YWJjZA=="}}


def test_equation_value():
    text = "[math]\nformula = e = m*c=2\n"
    assert parse_ini(text) == {"math": {"formula": "e = m*c=2"}}


def test_only_first_equals_is_separator():
    text = "[a]\nkey = =leading\n"
    assert parse_ini(text) == {"a": {"key": "=leading"}}


def test_connection_string_in_default_section():
    text = "dsn = host=localhost;port=5432\n"
    assert parse_ini(text) == {"DEFAULT": {"dsn": "host=localhost;port=5432"}}
