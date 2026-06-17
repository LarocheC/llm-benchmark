"""Public entry point: split a single CSV line into a list of fields."""

from .dialect import DEFAULT_DIALECT, Dialect
from .scanner import Scanner, ScanError

__all__ = ["parse_csv_line", "ScanError"]


def parse_csv_line(s, dialect=None):
    """Split a single CSV line ``s`` into a list of field strings.

    Fields are separated by the dialect's delimiter (``,`` by default).
    A field may be wrapped in double quotes, in which case the delimiter
    loses its special meaning inside it; a literal quote is written by
    doubling it (``""``). Surrounding quotes are not part of the returned
    field value.

    >>> parse_csv_line('a,b,c')
    ['a', 'b', 'c']
    >>> parse_csv_line('"x,y",z')
    ['x,y', 'z']

    An empty string yields a single empty field, matching the behaviour of
    spreadsheet importers (one empty cell).
    """
    if not isinstance(s, str):
        raise TypeError("parse_csv_line expects a string")
    if dialect is None:
        dialect = DEFAULT_DIALECT
    elif not isinstance(dialect, Dialect):
        raise TypeError("dialect must be a Dialect instance")

    scanner = Scanner(s, dialect)
    fields = []

    while True:
        field = scanner.scan_field()
        fields.append(field)
        if scanner.at_end():
            break
        # The scanner stopped on a delimiter; step over it and read the
        # next field. A trailing delimiter therefore produces a final
        # empty field, which is the expected CSV behaviour.
        if dialect.is_delimiter(scanner.current()):
            scanner.pos += 1
            if scanner.at_end():
                fields.append("")
                break
            continue
        # Anything else right after a field is malformed (e.g. stray text
        # following a closing quote).
        raise ScanError(
            "unexpected character %r after field" % scanner.current()
        )

    return fields
