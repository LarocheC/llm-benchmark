"""Configuration for how a CSV line is structured.

A :class:`Dialect` bundles the three characters that control parsing:
the field delimiter, the quote character, and the escape style. Only the
"doubled quote" escape style is supported here (the most common one, used
by RFC 4180 and by spreadsheet exports), where a literal quote inside a
quoted field is written by doubling it (``""``).
"""


class Dialect:
    def __init__(self, delimiter=",", quotechar='"'):
        if len(delimiter) != 1:
            raise ValueError("delimiter must be a single character")
        if len(quotechar) != 1:
            raise ValueError("quotechar must be a single character")
        if delimiter == quotechar:
            raise ValueError("delimiter and quotechar must differ")
        self.delimiter = delimiter
        self.quotechar = quotechar

    def is_delimiter(self, ch):
        return ch == self.delimiter

    def is_quote(self, ch):
        return ch == self.quotechar


DEFAULT_DIALECT = Dialect()
