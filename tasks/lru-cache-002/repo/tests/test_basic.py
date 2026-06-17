"""Basic behaviour that must hold regardless of the recency-tracking detail.

None of these tests exercise a read-then-evict ordering, so they pass on the
current (buggy) implementation as well as the fixed one.
"""
import pytest

from lrucache import LRUCache, MISS


def test_put_then_get():
    c = LRUCache(2)
    c.put("a", 1)
    assert c.get("a") == 1


def test_get_missing_returns_sentinel():
    c = LRUCache(2)
    assert c.get("nope") is MISS


def test_get_missing_returns_explicit_default():
    c = LRUCache(2)
    assert c.get("nope", default=-1) == -1


def test_none_is_a_valid_stored_value():
    c = LRUCache(2)
    c.put("a", None)
    assert c.get("a") is None
    assert c.get("a") is not MISS


def test_update_existing_key_overwrites_value():
    c = LRUCache(2)
    c.put("a", 1)
    c.put("a", 99)
    assert c.get("a") == 99
    assert len(c) == 1


def test_len_and_contains():
    c = LRUCache(3)
    assert len(c) == 0
    c.put("a", 1)
    c.put("b", 2)
    assert len(c) == 2
    assert "a" in c
    assert "z" not in c


def test_capacity_must_be_positive():
    with pytest.raises(ValueError):
        LRUCache(0)


def test_eviction_on_overflow_drops_oldest_insert():
    # Pure insert sequence (no reads in between): once over capacity, the
    # earliest-inserted key is evicted.
    c = LRUCache(2)
    c.put("a", 1)
    c.put("b", 2)
    c.put("c", 3)          # capacity 2 -> "a" (oldest) is evicted
    assert c.get("a") is MISS
    assert c.get("b") == 2
    assert c.get("c") == 3


def test_update_does_not_count_against_capacity():
    c = LRUCache(2)
    c.put("a", 1)
    c.put("b", 2)
    c.put("b", 22)         # update, not insert -> nothing evicted
    assert len(c) == 2
    assert c.get("a") == 1
    assert c.get("b") == 22


def test_put_refresh_protects_updated_key_from_eviction():
    # Recency driven entirely by puts: re-putting "a" makes it MRU, so the
    # next insert evicts "b" instead. This works on buggy code because put()
    # *does* update recency.
    c = LRUCache(2)
    c.put("a", 1)
    c.put("b", 2)
    c.put("a", 11)         # "a" becomes most-recently-used
    c.put("c", 3)          # evicts least-recently-used, which is "b"
    assert c.get("b") is MISS
    assert c.get("a") == 11
    assert c.get("c") == 3
