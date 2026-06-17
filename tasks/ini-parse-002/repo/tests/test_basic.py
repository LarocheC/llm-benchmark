from iniparse import parse_ini


def test_single_section_single_pair():
    assert parse_ini("[server]\nhost = localhost\n") == {
        "server": {"host": "localhost"}
    }


def test_multiple_pairs_in_section():
    text = "[server]\nhost = localhost\nport = 8080\n"
    assert parse_ini(text) == {"server": {"host": "localhost", "port": "8080"}}


def test_multiple_sections():
    text = (
        "[server]\n"
        "host = localhost\n"
        "\n"
        "[client]\n"
        "retries = 3\n"
    )
    assert parse_ini(text) == {
        "server": {"host": "localhost"},
        "client": {"retries": "3"},
    }


def test_comments_and_blank_lines_ignored():
    text = (
        "# global config\n"
        "\n"
        "[server]\n"
        "; the bind address\n"
        "host = localhost\n"
    )
    assert parse_ini(text) == {"server": {"host": "localhost"}}


def test_whitespace_around_key_and_value_trimmed():
    assert parse_ini("[a]\n   name   =    value   \n") == {"a": {"name": "value"}}


def test_keys_before_section_go_to_default():
    text = "name = global\n[a]\nname = local\n"
    assert parse_ini(text) == {
        "DEFAULT": {"name": "global"},
        "a": {"name": "local"},
    }


def test_empty_value():
    assert parse_ini("[a]\nkey =\n") == {"a": {"key": ""}}


def test_later_key_overrides_earlier():
    text = "[a]\nx = 1\nx = 2\n"
    assert parse_ini(text) == {"a": {"x": "2"}}
