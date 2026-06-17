# Values that contain `=` get truncated

The `iniparse` package parses a tiny INI format into a nested dict:

```python
>>> from iniparse import parse_ini
>>> parse_ini("[server]\nhost = localhost\nport = 8080\n")
{'server': {'host': 'localhost', 'port': '8080'}}
```

It handles `[section]` headers, `key = value` lines, `#`/`;` comment lines and
blank lines. Simple configs come out fine, but values that themselves contain an
`=` sign are mangled — only a fragment of the value survives.

Example of the bug:

```python
>>> parse_ini("[http]\nurl = a=1&b=2\n")
{'http': {'url': 'a'}}        # WRONG — the rest of the value was dropped
```

Expected:

```python
>>> parse_ini("[http]\nurl = a=1&b=2\n")
{'http': {'url': 'a=1&b=2'}}  # only the FIRST '=' separates key from value
```

The convention for INI files is that the **first** `=` on a line splits the key
from the value; every later `=` is just part of the value (query strings,
base64 padding like `YWJjZA==`, connection strings, and so on are common).

Keys and values should still be trimmed of surrounding whitespace, and all the
existing behavior (sections, comments, blank lines, simple pairs) must keep
working. Please fix the parser so values keep everything after the first `=`.
