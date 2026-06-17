"""Build a nested dict from classified INI lines.

The parser walks the classified lines produced by :mod:`iniparse.lexer`,
tracking the current section and recording each key/value pair under it.
Keys and values are whitespace-trimmed.
"""
from .lexer import lex

# Keys defined before any [section] header land in this implicit section.
DEFAULT_SECTION = "DEFAULT"


def _split_pair(raw):
    """Split a raw ``key = value`` line into a (key, value) tuple.

    Only the first ``=`` separates the key from the value; any further ``=``
    characters belong to the value. Keys and the value are trimmed of
    surrounding whitespace.
    """
    key_part, value_part = raw.split("=", 1)
    key = key_part.strip()
    value = value_part.strip()
    if key == "":
        raise ValueError(f"Missing key in line: {raw!r}")
    return key, value


def parse_ini(text):
    """Parse INI ``text`` into ``dict[str, dict[str, str]]``.

    Section headers look like ``[name]``. Inside a section, ``key = value``
    lines define string entries. Lines beginning with ``#`` or ``;`` are
    comments and blank lines are ignored. Keys appearing before the first
    section header are placed in the ``"DEFAULT"`` section.
    """
    result = {}
    current = DEFAULT_SECTION

    for line in lex(text):
        if line.kind in ("blank", "comment"):
            continue
        if line.kind == "section":
            current = line.text
            result.setdefault(current, {})
            continue
        if line.kind == "pair":
            key, value = _split_pair(line.text)
            result.setdefault(current, {})[key] = value
            continue
        raise ValueError(f"Unhandled line kind: {line.kind!r}")

    return result
