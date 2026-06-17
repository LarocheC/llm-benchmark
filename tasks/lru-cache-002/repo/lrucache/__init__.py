"""A tiny, fixed-capacity LRU cache.

    >>> from lrucache import LRUCache, MISS
    >>> c = LRUCache(2)
    >>> c.put("a", 1)
    >>> c.get("a")
    1
    >>> c.get("missing") is MISS
    True
"""

from .cache import LRUCache, MISS

__all__ = ["LRUCache", "MISS"]
