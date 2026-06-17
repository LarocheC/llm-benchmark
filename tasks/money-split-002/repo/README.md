# moneysplit

A tiny helper for splitting an integer amount of money (in cents) into `n`
even parts.

```python
from moneysplit import split_amount
split_amount(100, 4)   # [25, 25, 25, 25]
```

The parts are returned largest-first, are as even as possible, and are meant to
sum back to the original total.
Pipeline: `quotas` (floor quota + leftover) → `distribute` (hand out parts) →
`splitter` (public API + validation).

Run the tests with `pytest`.
