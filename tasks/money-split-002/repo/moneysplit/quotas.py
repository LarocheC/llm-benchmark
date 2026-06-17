"""Low-level integer arithmetic for an even split.

A split of ``total`` cents across ``n`` parts is described by two numbers:

* ``base``      -- the floor quota every part receives, ``total // n``
* ``remainder`` -- the cents left over, ``total % n`` (always ``0 <= r < n``)

Because ``remainder`` cents could not be handed out evenly, exactly
``remainder`` of the parts must receive ``base + 1`` cents and the rest receive
``base``; that is the only way the parts can both sum to ``total`` and differ by
at most one cent.
"""


class Quota:
    """The result of dividing ``total`` cents into ``n`` parts."""

    __slots__ = ("total", "n", "base", "remainder")

    def __init__(self, total, n):
        self.total = total
        self.n = n
        self.base = total // n
        self.remainder = total % n

    def is_clean(self):
        """True when the total divides evenly (no leftover cents)."""
        return self.remainder == 0

    def __repr__(self):
        return (
            f"Quota(total={self.total}, n={self.n}, "
            f"base={self.base}, remainder={self.remainder})"
        )


def compute_quota(total, n):
    """Compute the :class:`Quota` for splitting ``total`` cents into ``n`` parts."""
    return Quota(total, n)
