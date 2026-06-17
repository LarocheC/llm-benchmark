"""A small character-level state machine that walks one CSV line.

The scanner reads the line left to right and emits the field boundaries.
It distinguishes three states:

* ``FIELD_START``  -- at the very beginning of a field, before any character
  has been consumed. A quote here opens a quoted field; anything else starts
  an unquoted field.
* ``UNQUOTED``     -- inside a bare field; characters are taken literally until
  a delimiter ends the field.
* ``QUOTED``       -- inside a quoted field; the delimiter is treated as data,
  and the field ends only at the closing quote.

The escape convention is the doubled quote: inside a quoted field, two quote
characters in a row (``""``) represent a single literal quote and parsing
stays inside the field.
"""

FIELD_START = "field_start"
UNQUOTED = "unquoted"
QUOTED = "quoted"


class ScanError(ValueError):
    """Raised when the line cannot be tokenised under the dialect."""


class Scanner:
    def __init__(self, line, dialect):
        self.line = line
        self.dialect = dialect
        self.pos = 0
        self.n = len(line)

    def at_end(self):
        return self.pos >= self.n

    def current(self):
        return self.line[self.pos]

    def lookahead(self):
        """The character one past the cursor, or None at end of line."""
        nxt = self.pos + 1
        if nxt < self.n:
            return self.line[nxt]
        return None

    def scan_field(self):
        """Consume one field starting at the cursor and return its text.

        On return, the cursor sits either at the delimiter that ends the
        field or just past the end of the line.
        """
        d = self.dialect
        chars = []
        state = FIELD_START

        while not self.at_end():
            ch = self.current()

            if state == FIELD_START:
                if d.is_quote(ch):
                    state = QUOTED
                    self.pos += 1
                    continue
                state = UNQUOTED
                # fall through to UNQUOTED handling without advancing

            if state == UNQUOTED:
                if d.is_delimiter(ch):
                    return "".join(chars)
                chars.append(ch)
                self.pos += 1
                continue

            if state == QUOTED:
                if d.is_quote(ch):
                    # A quote inside a quoted field closes the field. The
                    # caller is responsible for what follows (a delimiter or
                    # end of line).
                    self.pos += 1
                    return "".join(chars)
                chars.append(ch)
                self.pos += 1
                continue

        if state == QUOTED:
            raise ScanError("unterminated quoted field")
        return "".join(chars)
