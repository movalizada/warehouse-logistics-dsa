"""
Xətti Abstrakt Məlumat Tipləri: Stack, Queue, Deque
==================================================

Hamısı xüsusi düyün (node) göstəriciləri ilə sıfırdan qurulub —
``list`` və ya ``collections.deque`` istifadə OLUNMUR.

+--------------------------+---------+---------+---------+
| Əməliyyat                | Stack   | Queue   | Deque   |
+==========================+=========+=========+=========+
| push / enqueue / add_*   | O(1)    | O(1)    | O(1)    |
| pop / dequeue / remove_* | O(1)    | O(1)    | O(1)    |
| peek                     | O(1)    | O(1)    | O(1)    |
| remove_where (şərtlə)    |   —     |   —     | O(n)    |
| Yaddaş                   | O(n)    | O(n)    | O(n)    |
+--------------------------+---------+---------+---------+
"""


class EmptyStructureError(Exception):
    """Boş strukturdan element götürmək cəhdində qaldırılır."""


class _Node:
    """Tək istiqamətli düyün (Stack və Queue üçün)."""

    __slots__ = ("data", "next")

    def __init__(self, data, next_node=None):
        self.data = data
        self.next = next_node


class _DNode:
    """İki istiqamətli düyün (Deque üçün)."""

    __slots__ = ("data", "next", "prev")

    def __init__(self, data):
        self.data = data
        self.next = None
        self.prev = None


# ====================================================================== #
# STACK (LIFO)
# ====================================================================== #
class Stack:
    """LIFO yığın. Zirvə (top) — əlaqəli siyahının başıdır.

    Tətbiqdəki rolu: **Əməliyyatı geri qaytarmaq (Undo)** — son inventar
    dəyişikliyi həmişə zirvədədir və ilk olaraq ləğv olunur.
    """

    __slots__ = ("_top", "_size")

    def __init__(self):
        self._top = None
        self._size = 0

    def push(self, item):
        """Zirvəyə əlavə. O(1)."""
        self._top = _Node(item, self._top)
        self._size += 1

    def pop(self):
        """Zirvədəki elementi silir və qaytarır. O(1)."""
        if self._top is None:
            raise EmptyStructureError("Stack boşdur.")
        node = self._top
        self._top = node.next
        self._size -= 1
        return node.data

    def peek(self):
        """Zirvəyə baxış (silmədən). O(1)."""
        if self._top is None:
            raise EmptyStructureError("Stack boşdur.")
        return self._top.data

    def is_empty(self):
        return self._top is None

    def clear(self):
        self._top = None
        self._size = 0

    def __len__(self):
        return self._size

    def __iter__(self):
        """Zirvədən dibə doğru gəzir. O(n)."""
        node = self._top
        while node is not None:
            yield node.data
            node = node.next


# ====================================================================== #
# QUEUE (FIFO)
# ====================================================================== #
class Queue:
    """FIFO növbə: ``head`` göstəricisindən çıxarılır, ``tail``-a əlavə edilir.

    Tətbiqdəki rolu: **Adi sifariş növbəsi** — sifarişlər daxil olma
    ardıcıllığı ilə ciddi şəkildə emal olunur.
    """

    __slots__ = ("_head", "_tail", "_size")

    def __init__(self):
        self._head = None
        self._tail = None
        self._size = 0

    def enqueue(self, item):
        """Sona əlavə. O(1)."""
        node = _Node(item)
        if self._tail is None:
            self._head = node
        else:
            self._tail.next = node
        self._tail = node
        self._size += 1

    def dequeue(self):
        """Başdan çıxarma. O(1)."""
        if self._head is None:
            raise EmptyStructureError("Növbə boşdur.")
        node = self._head
        self._head = node.next
        if self._head is None:
            self._tail = None
        self._size -= 1
        return node.data

    def peek(self):
        if self._head is None:
            raise EmptyStructureError("Növbə boşdur.")
        return self._head.data

    def is_empty(self):
        return self._head is None

    def __len__(self):
        return self._size

    def __iter__(self):
        """Başdan sona gəzir. O(n)."""
        node = self._head
        while node is not None:
            yield node.data
            node = node.next


# ====================================================================== #
# DEQUE (iki tərəfli növbə)
# ====================================================================== #
class Deque:
    """İki uclu növbə — iki istiqamətli əlaqəli siyahı üzərində.

    Tətbiqdəki rolu: **Təcili/VIP göndəriş xətti** — VIP sifarişlər öndən
    (``add_front``), adi sifarişlər arxadan (``add_rear``) daxil olur; ləğv
    edilən sifarişlər istənilən ucdan çıxarıla bilər.
    """

    __slots__ = ("_front", "_rear", "_size")

    def __init__(self):
        self._front = None
        self._rear = None
        self._size = 0

    def add_front(self, item):
        """Önə əlavə. O(1)."""
        node = _DNode(item)
        if self._front is None:
            self._front = self._rear = node
        else:
            node.next = self._front
            self._front.prev = node
            self._front = node
        self._size += 1

    def add_rear(self, item):
        """Arxaya əlavə. O(1)."""
        node = _DNode(item)
        if self._rear is None:
            self._front = self._rear = node
        else:
            node.prev = self._rear
            self._rear.next = node
            self._rear = node
        self._size += 1

    def _unlink(self, node):
        """Verilmiş düyünü O(1) zamanda ayırır."""
        if node.prev is None:
            self._front = node.next
        else:
            node.prev.next = node.next
        if node.next is None:
            self._rear = node.prev
        else:
            node.next.prev = node.prev
        node.next = node.prev = None
        self._size -= 1
        return node.data

    def remove_front(self):
        """Öndən çıxarma. O(1)."""
        if self._front is None:
            raise EmptyStructureError("Deque boşdur.")
        return self._unlink(self._front)

    def remove_rear(self):
        """Arxadan çıxarma. O(1)."""
        if self._rear is None:
            raise EmptyStructureError("Deque boşdur.")
        return self._unlink(self._rear)

    def remove_where(self, predicate):
        """Şərti ödəyən ilk elementi çıxarır (yoxdursa ``None``). O(n)."""
        node = self._front
        while node is not None:
            if predicate(node.data):
                return self._unlink(node)
            node = node.next
        return None

    def peek_front(self):
        if self._front is None:
            raise EmptyStructureError("Deque boşdur.")
        return self._front.data

    def peek_rear(self):
        if self._rear is None:
            raise EmptyStructureError("Deque boşdur.")
        return self._rear.data

    def is_empty(self):
        return self._front is None

    def __len__(self):
        return self._size

    def __iter__(self):
        node = self._front
        while node is not None:
            yield node.data
            node = node.next
