"""
Tək və İki Əlaqəli Siyahılar (Singly vs. Doubly Linked List)
============================================================

+------------------------------+-----------------+-----------------+
| Əməliyyat                    | SinglyLinkedList| DoublyLinkedList|
+==============================+=================+=================+
| push_front (başa əlavə)      | O(1)            | O(1)            |
| push_back (sona əlavə)*      | O(1)            | O(1)            |
| pop_front (başdan silmə)     | O(1)            | O(1)            |
| pop_back (sondan silmə)      | **O(n)**        | **O(1)**        |
| remove_node (düyünü silmə)   | O(n) (əvvəlkini tapmaq lazımdır) | O(1) |
| find / remove (dəyərə görə)  | O(n)            | O(n)            |
| İrəli gəzinti                | O(n)            | O(n)            |
| Geri gəzinti                 | O(n) vaxt + O(n) əlavə yaddaş (Stack) | O(n), O(1) əlavə yaddaş |
| Düyün başına yaddaş          | data + next     | data + next + prev |
+------------------------------+-----------------+-----------------+

* Hər iki siyahı ``tail`` göstəricisi saxlayır, ona görə sona əlavə O(1)-dir.
Tək əlaqəli siyahıda sondan silmə isə ``tail``-dən əvvəlki düyünü tapmaq üçün
başdan gəzməyi tələb edir — O(n).
"""

import sys

from src.structures.linear_adts import EmptyStructureError, Stack


class SinglyNode:
    """Yalnız ``next`` göstəricisi olan düyün."""

    __slots__ = ("data", "next")

    def __init__(self, data):
        self.data = data
        self.next = None


class DoublyNode:
    """``next`` və ``prev`` göstəriciləri olan düyün."""

    __slots__ = ("data", "next", "prev")

    def __init__(self, data):
        self.data = data
        self.next = None
        self.prev = None


# ====================================================================== #
# TƏK ƏLAQƏLİ SİYAHI
# ====================================================================== #
class SinglyLinkedList:
    """Tək istiqamətli əlaqəli siyahı.

    Tətbiqdəki rolu: **Çatdırılma marşrutu** — yük maşını nəzarət nöqtələrini
    yalnız bir istiqamətdə (irəli) keçir, geri qayıtmaq tələb olunmur.
    """

    __slots__ = ("head", "tail", "_size")

    def __init__(self):
        self.head = None
        self.tail = None
        self._size = 0

    def __len__(self):
        return self._size

    def is_empty(self):
        return self.head is None

    def push_front(self, data):
        """Başa əlavə. O(1)."""
        node = SinglyNode(data)
        node.next = self.head
        self.head = node
        if self.tail is None:
            self.tail = node
        self._size += 1

    def push_back(self, data):
        """Sona əlavə (tail sayəsində). O(1)."""
        node = SinglyNode(data)
        if self.tail is None:
            self.head = self.tail = node
        else:
            self.tail.next = node
            self.tail = node
        self._size += 1

    def insert_at(self, index, data):
        """``index`` mövqeyinə əlavə. O(n)."""
        if index < 0 or index > self._size:
            raise IndexError("Mövqe {0} yanlışdır.".format(index))
        if index == 0:
            self.push_front(data)
            return
        if index == self._size:
            self.push_back(data)
            return
        prev = self.head
        i = 0
        while i < index - 1:
            prev = prev.next
            i += 1
        node = SinglyNode(data)
        node.next = prev.next
        prev.next = node
        self._size += 1

    def pop_front(self):
        """Başdan silmə. O(1)."""
        if self.head is None:
            raise EmptyStructureError("Siyahı boşdur.")
        node = self.head
        self.head = node.next
        if self.head is None:
            self.tail = None
        self._size -= 1
        return node.data

    def pop_back(self):
        """Sondan silmə. O(n) — sondan əvvəlki düyünü tapmaq üçün gəzinti lazımdır."""
        if self.head is None:
            raise EmptyStructureError("Siyahı boşdur.")
        if self.head is self.tail:
            data = self.head.data
            self.head = self.tail = None
            self._size = 0
            return data
        prev = self.head
        while prev.next is not self.tail:
            prev = prev.next
        data = self.tail.data
        prev.next = None
        self.tail = prev
        self._size -= 1
        return data

    def find(self, predicate):
        """Şərti ödəyən ilk dəyəri qaytarır (yoxdursa ``None``). O(n)."""
        node = self.head
        while node is not None:
            if predicate(node.data):
                return node.data
            node = node.next
        return None

    def remove_where(self, predicate):
        """Şərti ödəyən ilk düyünü silir. Silinən dəyəri və ya ``None`` qaytarır. O(n)."""
        prev = None
        node = self.head
        while node is not None:
            if predicate(node.data):
                if prev is None:
                    self.head = node.next
                else:
                    prev.next = node.next
                if node is self.tail:
                    self.tail = prev
                self._size -= 1
                return node.data
            prev = node
            node = node.next
        return None

    def peek_front(self):
        if self.head is None:
            raise EmptyStructureError("Siyahı boşdur.")
        return self.head.data

    def __iter__(self):
        """İrəli gəzinti. O(n)."""
        node = self.head
        while node is not None:
            yield node.data
            node = node.next

    def traverse_backward(self):
        """Geri gəzinti. ``prev`` olmadığı üçün köməkçi Stack lazımdır:
        O(n) vaxt + O(n) ƏLAVƏ yaddaş."""
        stack = Stack()
        node = self.head
        while node is not None:
            stack.push(node.data)
            node = node.next
        while not stack.is_empty():
            yield stack.pop()

    @staticmethod
    def node_size_bytes():
        """Bir düyünün obyekt ölçüsü (bayt) — ``sys.getsizeof`` ilə."""
        return sys.getsizeof(SinglyNode(None))


# ====================================================================== #
# İKİ ƏLAQƏLİ SİYAHI
# ====================================================================== #
class DoublyLinkedList:
    """İki istiqamətli əlaqəli siyahı.

    Tətbiqdəki rolu: **Rəf yoxlaması naviqasiyası** — operator rəflər arasında
    həm irəli, həm geri hərəkət edir; cari rəfi O(1)-də silmək mümkündür.
    """

    __slots__ = ("head", "tail", "_size")

    def __init__(self):
        self.head = None
        self.tail = None
        self._size = 0

    def __len__(self):
        return self._size

    def is_empty(self):
        return self.head is None

    def push_front(self, data):
        """Başa əlavə. O(1)."""
        node = DoublyNode(data)
        if self.head is None:
            self.head = self.tail = node
        else:
            node.next = self.head
            self.head.prev = node
            self.head = node
        self._size += 1
        return node

    def push_back(self, data):
        """Sona əlavə. O(1)."""
        node = DoublyNode(data)
        if self.tail is None:
            self.head = self.tail = node
        else:
            node.prev = self.tail
            self.tail.next = node
            self.tail = node
        self._size += 1
        return node

    def insert_after(self, node, data):
        """Verilmiş düyündən sonra əlavə. O(1)."""
        if node is self.tail:
            return self.push_back(data)
        new = DoublyNode(data)
        new.prev = node
        new.next = node.next
        node.next.prev = new
        node.next = new
        self._size += 1
        return new

    def remove_node(self, node):
        """Düyünü birbaşa silir — ``prev`` sayəsində O(1)."""
        if node.prev is None:
            self.head = node.next
        else:
            node.prev.next = node.next
        if node.next is None:
            self.tail = node.prev
        else:
            node.next.prev = node.prev
        node.next = node.prev = None
        self._size -= 1
        return node.data

    def pop_front(self):
        """Başdan silmə. O(1)."""
        if self.head is None:
            raise EmptyStructureError("Siyahı boşdur.")
        return self.remove_node(self.head)

    def pop_back(self):
        """Sondan silmə. O(1) — ``tail.prev`` birbaşa məlumdur."""
        if self.tail is None:
            raise EmptyStructureError("Siyahı boşdur.")
        return self.remove_node(self.tail)

    def find_node(self, predicate):
        """Şərti ödəyən ilk düyünü qaytarır. O(n)."""
        node = self.head
        while node is not None:
            if predicate(node.data):
                return node
            node = node.next
        return None

    def remove_where(self, predicate):
        node = self.find_node(predicate)
        if node is None:
            return None
        return self.remove_node(node)

    def __iter__(self):
        """İrəli gəzinti. O(n)."""
        node = self.head
        while node is not None:
            yield node.data
            node = node.next

    def traverse_backward(self):
        """Geri gəzinti — ``prev`` göstəriciləri ilə, əlavə yaddaş O(1)."""
        node = self.tail
        while node is not None:
            yield node.data
            node = node.prev

    @staticmethod
    def node_size_bytes():
        return sys.getsizeof(DoublyNode(None))
