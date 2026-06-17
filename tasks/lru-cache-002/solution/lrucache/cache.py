"""A fixed-capacity Least-Recently-Used (LRU) cache.

Backed by a dict (key -> Node) for O(1) lookup and an intrusive doubly-linked
list for O(1) recency reordering. The most-recently-used entry sits at the
front of the list; when the cache is full, the entry at the back (the
least-recently-used one) is evicted.

A read or a write counts as "using" an entry: after either, that entry should
become the most-recently-used and therefore the last to be evicted.
"""

from ._dll import DoublyLinkedList, Node

#: Returned by ``get`` when a key is absent (so ``None`` can be a real value).
MISS = object()


class LRUCache:
    def __init__(self, capacity):
        if capacity <= 0:
            raise ValueError("capacity must be a positive integer")
        self.capacity = capacity
        self._table = {}              # key -> Node
        self._order = DoublyLinkedList()

    def __len__(self):
        return len(self._table)

    def __contains__(self, key):
        return key in self._table

    def _touch(self, node):
        """Promote an existing node to most-recently-used."""
        self._order.move_to_front(node)

    def get(self, key, default=MISS):
        """Return the value for ``key``, or ``default`` if the key is absent.

        Looking a key up counts as accessing it.
        """
        node = self._table.get(key)
        if node is None:
            return default
        self._touch(node)
        return node.value

    def put(self, key, value):
        """Insert or update ``key`` with ``value``.

        On update, the existing entry's value is refreshed and the entry is
        promoted to most-recently-used. On insert into a full cache, the
        least-recently-used entry is evicted first.
        """
        existing = self._table.get(key)
        if existing is not None:
            existing.value = value
            self._touch(existing)
            return

        if len(self._table) >= self.capacity:
            self._evict()

        node = Node(key, value)
        self._table[key] = node
        self._order.add_to_front(node)

    def _evict(self):
        """Drop the least-recently-used entry, if any."""
        lru = self._order.pop_lru()
        if lru is not None:
            del self._table[lru.key]

    def keys_mru_to_lru(self):
        """Return current keys ordered most-recently-used first.

        Useful for inspection/debugging; reflects the recency list, not the
        dict insertion order.
        """
        result = []
        node = self._order.head.next
        while node is not self._order.tail:
            result.append(node.key)
            node = node.next
        return result
