"""moneysplit: divide an integer number of cents into even parts.

The public entry point is :func:`split_amount`, which returns a list of ``n``
integer parts that should sum back to the original total while staying as even
as possible.
"""
from .splitter import split_amount

__all__ = ["split_amount"]
