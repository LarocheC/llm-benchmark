"""Classify raw INI lines into typed records.

The lexer is intentionally dumb: it only decides *what kind* of line it is
looking at and strips surrounding whitespace. It does not interpret the
contents of a key/value line beyond noticing that one exists. Splitting a
key/value line into its parts is the parser's job.
"""

# A line is a comment when its first non-space character is one of these.
COMMENT_PREFIXES = ("#", ";")


class Line:
    """A single classified source line.

    kind is one of: "blank", "comment", "section", "pair".
    For a "section" line, ``text`` holds the section name.
    For a "pair" line, ``text`` holds the raw line (still containing the
    separator); the parser is responsible for splitting it.
    """

    def __init__(self, kind, text, number):
        self.kind = kind
        self.text = text
        self.number = number

    def __repr__(self):
        return f"Line({self.kind!r}, {self.text!r}, line={self.number})"


def classify(raw, number):
    stripped = raw.strip()
    if stripped == "":
        return Line("blank", "", number)
    if stripped.startswith(COMMENT_PREFIXES):
        return Line("comment", stripped, number)
    if stripped.startswith("[") and stripped.endswith("]"):
        name = stripped[1:-1].strip()
        if name == "":
            raise ValueError(f"Empty section header on line {number}")
        return Line("section", name, number)
    if "=" in stripped:
        return Line("pair", stripped, number)
    raise ValueError(f"Malformed line {number}: {raw!r}")


def lex(text):
    """Turn source text into a list of classified Line records."""
    return [classify(raw, i) for i, raw in enumerate(text.splitlines(), start=1)]
