# Splitting a bill loses cents when it does not divide evenly

The `moneysplit` package divides an integer amount of money (in cents) into `n`
parts. The contract for `split_amount(total_cents, n)` is:

- it returns a list of exactly `n` integer parts,
- the parts **sum back to `total_cents` exactly** (no money may be created or lost), and
- the parts are as even as possible, so any two parts differ by at most 1 cent.

When the total divides evenly everything is fine, but as soon as it does not, cents
go missing.

Example of the bug:

```python
>>> from moneysplit import split_amount
>>> split_amount(100, 3)
[33, 33, 33]          # WRONG — sums to 99, one cent vanished
```

Expected:

```python
>>> split_amount(100, 3)
[34, 33, 33]          # sums to 100; parts differ by at most 1
```

A few more of the intended results:

```python
>>> split_amount(10, 4)
[3, 3, 2, 2]          # sums to 10
>>> split_amount(20, 6)
[4, 4, 3, 3, 3, 3]    # sums to 20
```

Evenly divisible splits such as `split_amount(100, 4) == [25, 25, 25, 25]` already
work and must keep working. Please fix the splitter so that the parts always sum to
`total_cents` exactly while staying as even as possible.
