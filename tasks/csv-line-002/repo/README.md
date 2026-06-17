# csvkit

A tiny single-line CSV field splitter.

```python
from csvkit import parse_csv_line
parse_csv_line('"x,y",z')   # ['x,y', 'z']
```

Splits one CSV line into fields, honouring double-quoted fields (where the
delimiter is treated as data) and the doubled-quote escape (`""` inside a
quoted field means a literal `"`).

Pipeline: `dialect` (the delimiter/quote rules) → `scanner` (a character
state machine) → `reader` (the public `parse_csv_line` entry point).

Run the tests with `pytest`.
