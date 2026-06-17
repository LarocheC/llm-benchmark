"""Turn a :class:`~moneysplit.quotas.Quota` into a concrete list of parts.

The leftover cents recorded in ``quota.remainder`` have to be handed out so that
the parts still sum to the original total. We give one extra cent to the first
``remainder`` parts; this keeps the largest and smallest parts within one cent of
each other while accounting for every leftover cent.
"""


def even_parts(quota):
    """A list of ``quota.n`` parts that all equal the floor quota.

    These parts intentionally ignore the leftover cents; callers that care about
    the remainder must hand it out with :func:`distribute_remainder`.
    """
    return [quota.base] * quota.n


def distribute_remainder(parts, remainder):
    """Add the ``remainder`` leftover cents to ``parts``, one cent per part.

    The first ``remainder`` entries each gain a single cent. The list is modified
    in place and also returned for convenience.
    """
    for i in range(remainder):
        parts[i] += 1
    return parts
