"""Public, high-level split API.

``split_amount`` wires the pieces together:

    compute_quota  ->  even_parts  ->  (hand out leftover cents)  ->  validate

and returns the final list of integer parts. Parts are returned largest-first so
that, when some parts are a cent bigger than others, the bigger ones come first.
"""
from .quotas import compute_quota
from .distribute import even_parts


def _validate(parts, n):
    """Sanity-check the shape of a split before returning it.

    Guards against obviously malformed splits: wrong length, non-integer parts,
    or parts that are not within one cent of each other.
    """
    if len(parts) != n:
        raise ValueError(f"expected {n} parts, produced {len(parts)}")
    if any(not isinstance(p, int) for p in parts):
        raise TypeError("parts must be integers")
    if parts and (max(parts) - min(parts)) > 1:
        raise ValueError("parts differ by more than one cent")
    return parts


def split_amount(total_cents, n):
    """Split ``total_cents`` into ``n`` even integer parts.

    The parts are as equal as possible and are ordered largest-first.

    :raises ValueError: if ``n`` is not a positive integer or ``total_cents`` is
        negative.
    """
    if not isinstance(n, int) or n <= 0:
        raise ValueError("n must be a positive integer")
    if not isinstance(total_cents, int) or total_cents < 0:
        raise ValueError("total_cents must be a non-negative integer")

    quota = compute_quota(total_cents, n)
    parts = even_parts(quota)

    parts.sort(reverse=True)
    return _validate(parts, n)
