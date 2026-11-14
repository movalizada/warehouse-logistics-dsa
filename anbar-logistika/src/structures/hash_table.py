"""
Zəncirləmə (Chaining) ilə Hash Cədvəli
======================================

Python ``dict`` istifadə OLUNMUR. Kovalar (bucket) ``StaticArray`` daxilində
saxlanılır, hər kova isə ``(key, value)`` düyünlərindən ibarət xüsusi
tək əlaqəli siyahıdır (``ChainList``).

Hash funksiyası:
  * Sətir açarları — polinomial (Horner) hash + qarışdırma (finalizer) addımı:
        h = (h * 31 + ord(simvol)) mod (2^31 - 1)
        h = fmix32(h)   — MurmurHash3 tipli XOR/vurma qarışdırması
    Son addım ardıcıl SKU-ların (SKU-000001, SKU-000002, ...) eyni nümunə ilə
    kovalara düşməsinin (klasterləşmənin) qarşısını alır; ölçmələrdə toqquşma
    sayı ideal təsadüfi hash-in nəzəri gözləntisi ilə üst-üstə düşür.
  * Tam ədəd açarları — Knuth-un multiplikativ hash-i:
        h = (key * 2654435761) mod 2^32
  Nəticə kova sayına görə modul alınır: ``index = h mod m``.

Yük əmsalı (load factor) α = n / m. Avtomatik genişlənmə aktivdirsə,
α > ``max_load_factor`` olduqda kova sayı ikiqat artırılır və bütün
elementlər yenidən hash-lənir (rehash).

+----------------------+-----------------+-------------+
| Əməliyyat            | Orta hal        | Ən pis hal  |
+======================+=================+=============+
| put / get / remove   | O(1 + α)        | O(n)        |
| rehash               | O(n + m)        | O(n + m)    |
| Yaddaş               | O(n + m)        |             |
+----------------------+-----------------+-------------+
"""

from src.structures.arrays import StaticArray

_STRING_MOD = 2147483647  # 2^31 - 1 (Mersenne sadə ədədi)
_KNUTH = 2654435761
_TWO_32 = 4294967296


def _fmix32(h):
    """32-bitlik qarışdırma (avalanche): hər giriş biti çıxışın bütün bitlərinə təsir edir."""
    h ^= h >> 16
    h = (h * 0x85EBCA6B) % _TWO_32
    h ^= h >> 13
    h = (h * 0xC2B2AE35) % _TWO_32
    h ^= h >> 16
    return h


class _ChainNode:
    __slots__ = ("key", "value", "next")

    def __init__(self, key, value, next_node=None):
        self.key = key
        self.value = value
        self.next = next_node


class ChainList:
    """Bir kovanın zənciri: ``(key, value)`` düyünlərinin tək əlaqəli siyahısı."""

    __slots__ = ("head", "length")

    def __init__(self):
        self.head = None
        self.length = 0

    def find_node(self, key):
        node = self.head
        while node is not None:
            if node.key == key:
                return node
            node = node.next
        return None

    def put(self, key, value):
        """Açar varsa dəyəri yeniləyir (False), yoxdursa başa əlavə edir (True)."""
        node = self.find_node(key)
        if node is not None:
            node.value = value
            return False
        self.head = _ChainNode(key, value, self.head)
        self.length += 1
        return True

    def remove(self, key):
        prev = None
        node = self.head
        while node is not None:
            if node.key == key:
                if prev is None:
                    self.head = node.next
                else:
                    prev.next = node.next
                self.length -= 1
                return node
            prev = node
            node = node.next
        return None

    def __iter__(self):
        node = self.head
        while node is not None:
            yield node.key, node.value
            node = node.next


class HashTableStats:
    """Hash cədvəlinin toqquşma metrikləri."""

    __slots__ = (
        "total_items",
        "bucket_count",
        "load_factor",
        "collisions",
        "collision_events",
        "longest_chain",
        "empty_buckets",
        "rehash_count",
    )

    def __init__(self, total_items, bucket_count, load_factor, collisions,
                 collision_events, longest_chain, empty_buckets, rehash_count):
        self.total_items = total_items
        self.bucket_count = bucket_count
        self.load_factor = load_factor
        self.collisions = collisions
        self.collision_events = collision_events
        self.longest_chain = longest_chain
        self.empty_buckets = empty_buckets
        self.rehash_count = rehash_count


class HashTable:
    """Zəncirləmə ilə hash cədvəli.

    Tətbiqdəki rolu: SKU koduna görə ani (orta hal O(1)) məhsul axtarışı,
    yenilənməsi və silinməsi.
    """

    __slots__ = ("_buckets", "_capacity", "_size", "_max_load", "_auto_resize",
                 "_collision_events", "_rehash_count")

    def __init__(self, capacity=16, max_load_factor=0.75, auto_resize=True):
        if capacity <= 0:
            raise ValueError("Kova sayı müsbət olmalıdır.")
        self._capacity = capacity
        self._size = 0
        self._max_load = max_load_factor
        self._auto_resize = auto_resize
        self._collision_events = 0
        self._rehash_count = 0
        self._buckets = self._make_buckets(capacity)

    @staticmethod
    def _make_buckets(capacity):
        buckets = StaticArray(capacity)
        i = 0
        while i < capacity:
            buckets.append(ChainList())
            i += 1
        return buckets

    # ------------------------------------------------------------------ #
    # Hash funksiyası
    # ------------------------------------------------------------------ #
    @staticmethod
    def raw_hash(key):
        """Kova sayından asılı olmayan xam hash dəyəri. Sətir üçün O(L)."""
        if isinstance(key, bool):
            key = int(key)
        if isinstance(key, int):
            return (key * _KNUTH) % _TWO_32
        text = str(key)
        h = 0
        for ch in text:
            h = (h * 31 + ord(ch)) % _STRING_MOD
        return _fmix32(h)

    def _index(self, key):
        return self.raw_hash(key) % self._capacity

    # ------------------------------------------------------------------ #
    # Əsas əməliyyatlar
    # ------------------------------------------------------------------ #
    def put(self, key, value):
        """Əlavə və ya yeniləmə. Orta hal O(1)."""
        bucket = self._buckets.get(self._index(key))
        had_items = bucket.length > 0
        is_new = bucket.put(key, value)
        if is_new:
            if had_items:
                self._collision_events += 1
            self._size += 1
            if self._auto_resize and self.load_factor() > self._max_load:
                self._rehash(self._capacity * 2)
        return is_new

    def get(self, key, default=None):
        """Açara görə dəyər. Orta hal O(1)."""
        node = self._buckets.get(self._index(key)).find_node(key)
        return default if node is None else node.value

    def contains(self, key):
        return self._buckets.get(self._index(key)).find_node(key) is not None

    def __contains__(self, key):
        return self.contains(key)

    def remove(self, key):
        """Açarı silir və dəyərini qaytarır; yoxdursa ``KeyError``. Orta hal O(1)."""
        node = self._buckets.get(self._index(key)).remove(key)
        if node is None:
            raise KeyError(key)
        self._size -= 1
        return node.value

    def _rehash(self, new_capacity):
        """Bütün elementləri yeni kova massivinə köçürür. O(n + m)."""
        old = self._buckets
        self._capacity = new_capacity
        self._buckets = self._make_buckets(new_capacity)
        self._collision_events = 0
        for bucket in old:
            node = bucket.head
            while node is not None:
                target = self._buckets.get(self._index(node.key))
                if target.length > 0:
                    self._collision_events += 1
                target.put(node.key, node.value)
                node = node.next
        self._rehash_count += 1

    # ------------------------------------------------------------------ #
    # Gəzinti və metriklər
    # ------------------------------------------------------------------ #
    def __len__(self):
        return self._size

    @property
    def bucket_count(self):
        return self._capacity

    def load_factor(self):
        return self._size / self._capacity

    def keys(self):
        for bucket in self._buckets:
            for key, _ in bucket:
                yield key

    def values(self):
        for bucket in self._buckets:
            for _, value in bucket:
                yield value

    def items(self):
        for bucket in self._buckets:
            for pair in bucket:
                yield pair

    def bucket_lengths(self):
        """Hər kovanın zəncir uzunluğu (paylanmanı göstərmək üçün)."""
        for bucket in self._buckets:
            yield bucket.length

    def bucket_keys(self, index):
        """Verilmiş kovadakı açarlar (zəncir ardıcıllığı ilə)."""
        for key, _ in self._buckets.get(index):
            yield key

    def bucket_index_of(self, key):
        return self._index(key)

    def stats(self):
        """Toqquşma metriklərini hesablayır. O(m).

        ``collisions`` — cari vəziyyətdə öz kovasını başqası ilə bölüşən
        artıq elementlərin sayı: Σ max(0, zəncir_uzunluğu - 1).
        ``collision_events`` — boş olmayan kovaya əlavə hadisələrinin sayı
        (son rehash-dən bəri).
        """
        collisions = 0
        longest = 0
        empty = 0
        for bucket in self._buckets:
            length = bucket.length
            if length == 0:
                empty += 1
            else:
                collisions += length - 1
            if length > longest:
                longest = length
        return HashTableStats(self._size, self._capacity, self.load_factor(),
                              collisions, self._collision_events, longest, empty,
                              self._rehash_count)
