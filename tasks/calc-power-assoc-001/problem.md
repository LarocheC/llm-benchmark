# Exponentiation is left-associative; it should be right-associative

The `calc` package evaluates arithmetic expression strings. Exponentiation (`**`) is
currently evaluated **left-to-right**, but by mathematical convention (and to match Python)
it must be **right-associative**.

Example of the bug:

```python
>>> from calc import evaluate
>>> evaluate("2 ** 3 ** 2")
64            # WRONG — currently evaluates as (2 ** 3) ** 2
```

Expected:

```python
>>> evaluate("2 ** 3 ** 2")
512           # 2 ** (3 ** 2)
```

Only the **associativity of `**`** is wrong. Operator precedence relative to `+ - * /`,
parentheses, and single `**` operations are all correct and must stay that way.

Please fix the evaluator so that chained exponentiation is right-associative.
