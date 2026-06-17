# iniparse

A tiny INI configuration parser.

```python
from iniparse import parse_ini

parse_ini("[server]\nhost = localhost\nport = 8080\n")
# {"server": {"host": "localhost", "port": "8080"}}
```

Supports `[section]` headers, `key = value` lines, `#`/`;` comments, and blank
lines. Keys before the first section land in the `"DEFAULT"` section.
Pipeline: `lexer` (classifies each line) -> `parser` (builds the nested dict).

Run the tests with `pytest`.
