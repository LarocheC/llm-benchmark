"""A small intrusive doubly-linked list used to track recency order.

The list keeps two sentinel nodes, ``head`` and ``tail``. Real entries live
between them. The node right after ``head`` is the most-recently-used (MRU)
entry; the node right before ``tail`` is the least-recently-used (LRU) entry.

The cache stores its key/value payload directly on the nodes, so moving an
entry's recency is just a pointer splice -- no dict rebuild required.
"""


class Node:
    __slots__ = ("key", "value", "prev", "next")

    def __init__(self, key=None, value=None):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None


class DoublyLinkedList:
    def __init__(self):
        self.head = Node()  # sentinel; head.next is MRU
        self.tail = Node()  # sentinel; tail.prev is LRU
        self.head.next = self.tail
        self.tail.prev = self.head

    def add_to_front(self, node):
        """Insert ``node`` directly after the head sentinel (becomes MRU)."""
        first = self.head.next
        node.prev = self.head
        node.next = first
        self.head.next = node
        first.prev = node

    def unlink(self, node):
        """Detach ``node`` from the list, joining its neighbours."""
        prev_node = node.prev
        next_node = node.next
        prev_node.next = next_node
        next_node.prev = prev_node
        node.prev = None
        node.next = None

    def move_to_front(self, node):
        """Mark ``node`` as most-recently-used."""
        self.unlink(node)
        self.add_to_front(node)

    def pop_lru(self):
        """Remove and return the least-recently-used node (or None if empty)."""
        lru = self.tail.prev
        if lru is self.head:
            return None
        self.unlink(lru)
        return lru
