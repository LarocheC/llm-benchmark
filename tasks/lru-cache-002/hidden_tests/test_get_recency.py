"""Hidden tests: a successful get() must count as a use.

After reading a key, that key becomes most-recently-used, so it must outlive
keys that were inserted earlier and not touched since. The buggy version only
updates recency on put(), so it wrongly evicts the just-read key.
"""
from lrucache import LRUCache, MISS


def test_get_protects_key_from_eviction():
    c = LRUCache(2)
    c.put("a", 1)
    c.put("b", 2)
    assert c.get("a") == 1     # "a" is now most-recently-used
    c.put("c", 3)              # must evict the LRU entry, which is now "b"
    assert c.get("a") == 1
    assert c.get("b") is MISS
    assert c.get("c") == 3


def test_repeated_gets_keep_key_alive():
    c = LRUCache(2)
    c.put("x", 10)
    c.put("y", 20)
    for _ in range(5):
        assert c.get("x") == 10   # keep refreshing "x"
    c.put("z", 30)                # evicts "y", the genuinely least-recently-used
    assert c.get("x") == 10
    assert c.get("y") is MISS
    assert c.get("z") == 30


def test_get_updates_recency_order_listing():
    c = LRUCache(3)
    c.put("a", 1)
    c.put("b", 2)
    c.put("c", 3)              # MRU->LRU: c, b, a
    c.get("a")                 # reading "a" promotes it to MRU
    assert c.keys_mru_to_lru() == ["a", "c", "b"]


def test_interleaved_gets_drive_eviction_order():
    c = LRUCache(3)
    c.put("a", 1)
    c.put("b", 2)
    c.put("c", 3)
    # Touch a and b via reads; c is now the least-recently-used.
    assert c.get("a") == 1
    assert c.get("b") == 2
    c.put("d", 4)              # evicts "c"
    assert c.get("c") is MISS
    assert c.get("a") == 1
    assert c.get("b") == 2
    assert c.get("d") == 4


def test_get_then_lru_chain():
    c = LRUCache(3)
    for k, v in [("k1", 1), ("k2", 2), ("k3", 3)]:
        c.put(k, v)
    assert c.get("k1") == 1    # promote k1; LRU is now k2
    c.put("k4", 4)             # evicts k2
    assert c.get("k2") is MISS
    assert c.get("k3") == 3    # promote k3; LRU is now k1
    c.put("k5", 5)             # evicts k1 (k4 and k3 are more recent)
    assert c.get("k1") is MISS
    assert c.get("k3") == 3
    assert c.get("k4") == 4
    assert c.get("k5") == 5
