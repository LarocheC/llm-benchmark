# Reads don't count as "use" — the cache evicts keys it just returned

The `lrucache` package provides a fixed-capacity `LRUCache` with `get(key)`,
`put(key, value)`, and a capacity fixed in the constructor. The intent is a
standard **Least-Recently-Used** policy: when the cache is full and a *new*
key is inserted, the entry that has gone the longest without being **used**
is evicted — and *using* an entry means **either reading it with `get` or
writing it with `put`**.

The bug: a successful `get` does **not** count as using the entry. Only `put`
refreshes recency. So under a read-heavy access pattern, a key that was just
read is treated as stale and gets evicted, even though it is actually the
most-recently-touched entry.

Example of the bug:

```python
>>> from lrucache import LRUCache, MISS
>>> c = LRUCache(2)
>>> c.put("a", 1)
>>> c.put("b", 2)
>>> c.get("a")            # we just used "a", so "b" is now the least-recently-used
1
>>> c.put("c", 3)         # cache full -> should evict the least-recently-used entry
>>> c.get("a")
<object ...>              # WRONG — "a" was evicted (returns the MISS sentinel)
>>> c.get("b")
2                         # WRONG — stale "b" survived
```

Expected:

```python
>>> c.get("a")
1                         # "a" was read most recently, so it must survive
>>> c.get("b") is MISS
True                      # "b" is the genuine least-recently-used entry and is evicted
```

Insertion, value updates, the miss sentinel, and eviction driven purely by
writes all behave correctly and must stay that way. Only the recency bookkeeping
for **reads** is wrong. Please fix it so that a successful `get` marks its entry
as the most-recently-used, exactly like `put` already does.
