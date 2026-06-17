# calc

A tiny arithmetic expression evaluator.

```python
from calc import evaluate
evaluate("2 + 3 * 4")   # 14
```

Supports `+ - * /`, unary minus, parentheses, and `**` (exponentiation).
Pipeline: `tokenizer` → `parser` (builds an AST) → `evaluator`.

Run the tests with `pytest`.
