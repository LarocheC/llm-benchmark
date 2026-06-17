from csvkit import parse_csv_line


def test_plain_fields():
    assert parse_csv_line("a,b,c") == ["a", "b", "c"]


def test_single_field():
    assert parse_csv_line("hello") == ["hello"]


def test_empty_string_is_one_empty_field():
    assert parse_csv_line("") == [""]


def test_empty_fields_between_delimiters():
    assert parse_csv_line("a,,c") == ["a", "", "c"]


def test_trailing_delimiter_yields_empty_field():
    assert parse_csv_line("a,b,") == ["a", "b", ""]


def test_leading_delimiter_yields_empty_field():
    assert parse_csv_line(",a") == ["", "a"]


def test_quoted_field_with_comma_inside():
    # The comma is data, not a separator, because the field is quoted.
    assert parse_csv_line('"x,y",z') == ["x,y", "z"]


def test_quoted_field_alone():
    assert parse_csv_line('"just one field"') == ["just one field"]


def test_quoted_empty_field():
    assert parse_csv_line('"",a') == ["", "a"]


def test_mixed_quoted_and_plain():
    assert parse_csv_line('name,"city, state",zip') == [
        "name",
        "city, state",
        "zip",
    ]
