"""
İkili Axtarış Ağacı (Binary Search Tree — BST)
==============================================

Bütün əməliyyatlar **iterativ** yazılıb (rekursiya yoxdur). Səbəb: sıralanmış
verilənlər BST-ni uzunluğu n olan xətti zəncirə çevirir və rekursiv həll
Python-un rekursiya limitini (≈1000) aşaraq çökərdi. Gəzinti üçün xüsusi
``Stack``, hündürlük üçün isə xüsusi ``Queue`` istifadə olunur.

Hündürlük tərifi: ağacdakı səviyyələrin sayı (boş ağac = 0, tək düyün = 1).

+------------------------+-------------+-------------+-------------------+
| Əməliyyat              | Ən yaxşı    | Orta hal    | Ən pis (əyilmiş)  |
+========================+=============+=============+===================+
| insert / search / delete | O(1)      | O(log n)    | O(n)              |
| min / max              | O(1)        | O(log n)    | O(n)              |
| in_order               | O(n)        | O(n)        | O(n)              |
| range_query            | O(log n + k)| O(log n + k)| O(n)              |
| get_height             | O(n)        | O(n)        | O(n)              |
| Yaddaş                 | O(n)        |             |                   |
+------------------------+-------------+-------------+-------------------+
"""

from src.structures.linear_adts import Queue, Stack


class BSTNode:
    __slots__ = ("key", "value", "left", "right")

    def __init__(self, key, value=None):
        self.key = key
        self.value = value
        self.left = None
        self.right = None


class BinarySearchTree:
    """Açarlar müqayisə oluna bilən istənilən tip ola bilər (ədəd, tuple və s.).

    Tətbiqdəki rolu: məhsulları **qiymətə** və **stok miqdarına** görə
    indeksləmək — sıralı hesabatlar və aralıq (range) sorğuları üçün.
    Təkrarlanan qiymətlərin qarşısını almaq üçün açar ``(qiymət, SKU)`` cütüdür.
    """

    __slots__ = ("root", "_size")

    def __init__(self):
        self.root = None
        self._size = 0

    def __len__(self):
        return self._size

    def is_empty(self):
        return self.root is None

    # ------------------------------------------------------------------ #
    # Əlavə etmə
    # ------------------------------------------------------------------ #
    def insert(self, key, value=None):
        """Açar yoxdursa əlavə edir (True), varsa dəyəri yeniləyir (False)."""
        new = BSTNode(key, value)
        if self.root is None:
            self.root = new
            self._size = 1
            return True
        node = self.root
        while True:
            if key < node.key:
                if node.left is None:
                    node.left = new
                    break
                node = node.left
            elif key > node.key:
                if node.right is None:
                    node.right = new
                    break
                node = node.right
            else:
                node.value = value
                return False
        self._size += 1
        return True

    # ------------------------------------------------------------------ #
    # Axtarış
    # ------------------------------------------------------------------ #
    def find_node(self, key):
        node = self.root
        while node is not None:
            if key < node.key:
                node = node.left
            elif key > node.key:
                node = node.right
            else:
                return node
        return None

    def search(self, key, default=None):
        """Açara görə dəyəri qaytarır. Orta O(log n), ən pis O(n)."""
        node = self.find_node(key)
        return default if node is None else node.value

    def contains(self, key):
        return self.find_node(key) is not None

    def search_with_comparisons(self, key):
        """``(tapıldı, müqayisə_sayı)`` — eksperiment üçün addım sayğacı."""
        comparisons = 0
        node = self.root
        while node is not None:
            comparisons += 1
            if key < node.key:
                node = node.left
            elif key > node.key:
                node = node.right
            else:
                return True, comparisons
        return False, comparisons

    # ------------------------------------------------------------------ #
    # Silmə (3 hal)
    # ------------------------------------------------------------------ #
    def delete(self, key):
        """Açarı silir. Silindisə True, tapılmadısa False.

        Hal 1 — yarpaq düyün: valideyndən sadəcə ayrılır.
        Hal 2 — bir uşaqlı düyün: uşaq düyünün yerini tutur.
        Hal 3 — iki uşaqlı düyün: in-order varisi (sağ alt ağacın ən kiçiyi)
                 tapılır, onun açar/dəyəri düyünə köçürülür, sonra varis
                 silinir (varisin sol uşağı olmur — Hal 1 və ya Hal 2).
        """
        parent = None
        node = self.root
        while node is not None and node.key != key:
            parent = node
            node = node.left if key < node.key else node.right
        if node is None:
            return False

        # Hal 3: iki uşaq
        if node.left is not None and node.right is not None:
            succ_parent = node
            succ = node.right
            while succ.left is not None:
                succ_parent = succ
                succ = succ.left
            node.key = succ.key
            node.value = succ.value
            # indi varisi silirik (onun ən çox sağ uşağı var)
            parent = succ_parent
            node = succ

        # Hal 1 və Hal 2: ən çox bir uşaq
        child = node.left if node.left is not None else node.right
        if parent is None:
            self.root = child
        elif parent.left is node:
            parent.left = child
        else:
            parent.right = child
        self._size -= 1
        return True

    # ------------------------------------------------------------------ #
    # Gəzinti və sorğular
    # ------------------------------------------------------------------ #
    def in_order(self):
        """Açarların artan sırası ilə ``(key, value)`` qaytarır. O(n)."""
        stack = Stack()
        node = self.root
        while node is not None or not stack.is_empty():
            while node is not None:
                stack.push(node)
                node = node.left
            node = stack.pop()
            yield node.key, node.value
            node = node.right

    def range_query(self, low, high):
        """``low <= key <= high`` olan cütlər, artan sıra ilə. O(h + k).

        ``low``-dan kiçik alt ağaclar tamamilə budanır, ``high``-dan böyük
        ilk açarda gəzinti dayanır.
        """
        stack = Stack()
        node = self.root
        while True:
            while node is not None:
                if node.key < low:
                    node = node.right  # sol alt ağacın hamısı < low
                else:
                    stack.push(node)
                    node = node.left
            if stack.is_empty():
                return
            node = stack.pop()
            if node.key > high:
                return
            yield node.key, node.value
            node = node.right

    def min_key(self):
        if self.root is None:
            return None
        node = self.root
        while node.left is not None:
            node = node.left
        return node.key

    def max_key(self):
        if self.root is None:
            return None
        node = self.root
        while node.right is not None:
            node = node.right
        return node.key

    def get_height(self):
        """Səviyyə-səviyyə (BFS) gəzinti ilə hündürlük. O(n)."""
        if self.root is None:
            return 0
        queue = Queue()
        queue.enqueue(self.root)
        height = 0
        while not queue.is_empty():
            level_count = len(queue)
            height += 1
            while level_count > 0:
                node = queue.dequeue()
                if node.left is not None:
                    queue.enqueue(node.left)
                if node.right is not None:
                    queue.enqueue(node.right)
                level_count -= 1
        return height
