# Quoted fields containing escaped quotes are truncated

The `csvkit` package splits a single CSV line into fields with
`parse_csv_line(s) -> list[str]`. It already handles plain comma-separated
fields and double-quoted fields where a comma is part of the data:

```python
>>> from csvkit import parse_csv_line
>>> parse_csv_line('"x,y",z')
['x,y', 'z']
```

The trouble is fields that contain a quote character. By the usual CSV
convention (RFC 4180, and what spreadsheets export), a literal double-quote
inside a quoted field is written by **doubling it** — two quote characters in
a row (`""`) stand for a single `"` and parsing should stay inside the field
until the *real* closing quote.

Right now that escape is mishandled: the first inner quote is taken as the end
of the field, so anything that contains a doubled quote comes out wrong (and a
field can even be cut short or rejected as malformed).

Example of the bug:

```python
>>> parse_csv_line('"He said ""yes"""')
# WRONG — the field is cut off at the first inner quote (or raises an error)
```

Expected:

```python
>>> parse_csv_line('"He said ""yes"""')
['He said "yes"']        # the doubled quotes collapse to single quotes
```

Plain fields, empty fields, and quoted fields that hold a delimiter all behave
correctly and must keep working. Only the handling of the doubled-quote escape
inside a quoted field is wrong.

Please fix the parser so that a doubled quote inside a quoted field is treated
as one literal quote and does not prematurely end the field.
