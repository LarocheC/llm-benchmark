# lrucache

A tiny fixed-capacity LRU (Least-Recently-Used) cache.

```python
from lrucache import LRUCache, MISS

c = LRUCache(2)
c.put("a", 1)
c.put("b", 2)
c.get("a")          # 1
c.put("c", 3)       # evicts the least-recently-used entry
c.get("missing")    # MISS sentinel
```

Backed by a dict for O(1) lookup and an intrusive doubly-linked list
(`_dll.py`) for O(1) recency reordering. The front of the list is the
most-recently-used entry; the back is the least-recently-used one and is the
first to be evicted when the cache is full.

Run the tests with `pytest`.
