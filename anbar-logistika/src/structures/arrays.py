"""
Statik və Dinamik Massivlər (Static Array vs. Dynamic Array)
============================================================

Hər iki massiv ``ctypes.py_object`` əsasında qurulub. ``(N * ctypes.py_object)()``
ifadəsi yaddaşda N ardıcıl (contiguous) göstərici yeri ayırır — bu, C dilindəki
``PyObject* arr[N]`` massivinin birbaşa analoqudur. Python ``list`` istifadə OLUNMUR.

Mürəkkəblik (n — elementlərin sayı):

+---------------------+-------------------+-----------------------------+
| Əməliyyat           | StaticArray       | DynamicArray                |
+=====================+===================+=============================+
| get / set (indeks)  | O(1)              | O(1)                        |
| append (sona)       | O(1) / Overflow   | O(1) amortizasiyalı, O(n) ən pis |
| insert (əvvələ/orta)| O(n)              | O(n)                        |
| delete (indeks)     | O(n) (sondan O(1))| O(n) (sondan O(1))          |
| search (xətti)      | O(n)              | O(n)                        |
| Yaddaş              | O(capacity)       | O(capacity), capacity <= 2n |
+---------------------+-------------------+-----------------------------+
"""

import ctypes


class ArrayOverflowError(Exception):
    """Statik massiv dolu olduqda yeni element əlavə etmək cəhdində qaldırılır."""


def _allocate(capacity):
    """``capacity`` ölçülü ardıcıl ``py_object`` blokunu ayırır. O(capacity)."""
    return (capacity * ctypes.py_object)()


class _BaseArray:
    """Statik və dinamik massivlərin ortaq məntiqi.

    Alt siniflər yalnız ``_ensure_space`` metodunu fərqli həyata keçirir:
    statik massiv xəta qaldırır, dinamik massiv tutumu ikiqat artırır.
    """

    __slots__ = ("_capacity", "_size", "_data")

    def __init__(self, capacity):
        if capacity <= 0:
            raise ValueError("Massivin tutumu müsbət tam ədəd olmalıdır.")
        self._capacity = capacity
        self._size = 0
        self._data = _allocate(capacity)

    # ------------------------------------------------------------------ #
    # Köməkçi metodlar
    # ------------------------------------------------------------------ #
    def _ensure_space(self):  # pragma: no cover - alt siniflərdə təyin olunur
        raise NotImplementedError

    def _check_index(self, index):
        if index < 0 or index >= self._size:
            raise IndexError(
                "İndeks {0} hüduddan kənardır (ölçü: {1}).".format(index, self._size)
            )

    # ------------------------------------------------------------------ #
    # Əsas xüsusiyyətlər
    # ------------------------------------------------------------------ #
    def __len__(self):
        return self._size

    @property
    def capacity(self):
        """Ayrılmış yaddaş yerlərinin sayı."""
        return self._capacity

    def is_empty(self):
        return self._size == 0

    def is_full(self):
        return self._size == self._capacity

    # ------------------------------------------------------------------ #
    # Giriş — O(1)
    # ------------------------------------------------------------------ #
    def get(self, index):
        """İndeksə görə element. Zaman: O(1)."""
        self._check_index(index)
        return self._data[index]

    def set(self, index, value):
        """İndeksdəki elementi əvəz edir. Zaman: O(1)."""
        self._check_index(index)
        self._data[index] = value

    def __getitem__(self, index):
        return self.get(index)

    def __setitem__(self, index, value):
        self.set(index, value)

    # ------------------------------------------------------------------ #
    # Əlavə etmə
    # ------------------------------------------------------------------ #
    def append(self, value):
        """Sona əlavə. Statik: O(1); Dinamik: amortizasiyalı O(1)."""
        self._ensure_space()
        self._data[self._size] = value
        self._size += 1

    def insert(self, index, value):
        """``index`` mövqeyinə əlavə edir, sağdakı elementləri sürüşdürür. Zaman: O(n)."""
        if index < 0 or index > self._size:
            raise IndexError(
                "Əlavə üçün indeks {0} yanlışdır (ölçü: {1}).".format(index, self._size)
            )
        self._ensure_space()
        i = self._size
        while i > index:  # sağa sürüşdürmə
            self._data[i] = self._data[i - 1]
            i -= 1
        self._data[index] = value
        self._size += 1

    # ------------------------------------------------------------------ #
    # Silmə
    # ------------------------------------------------------------------ #
    def delete(self, index):
        """``index`` mövqeyindəki elementi silir və qaytarır. Zaman: O(n - index)."""
        self._check_index(index)
        value = self._data[index]
        i = index
        last = self._size - 1
        while i < last:  # sola sürüşdürmə
            self._data[i] = self._data[i + 1]
            i += 1
        self._data[last] = None  # köhnə istinadı burax (yaddaş sızmasının qarşısı)
        self._size -= 1
        return value

    def pop(self):
        """Son elementi silir. Zaman: O(1)."""
        if self._size == 0:
            raise IndexError("Boş massivdən element silmək olmaz.")
        return self.delete(self._size - 1)

    def clear(self):
        """Bütün elementləri silir. Zaman: O(n)."""
        i = 0
        while i < self._size:
            self._data[i] = None
            i += 1
        self._size = 0

    # ------------------------------------------------------------------ #
    # Axtarış — O(n)
    # ------------------------------------------------------------------ #
    def search(self, value):
        """Xətti axtarış: tapılarsa indeks, əks halda -1. Zaman: O(n)."""
        i = 0
        while i < self._size:
            if self._data[i] == value:
                return i
            i += 1
        return -1

    def index_where(self, predicate):
        """Şərti ödəyən ilk elementin indeksi (yoxdursa -1). Zaman: O(n)."""
        i = 0
        while i < self._size:
            if predicate(self._data[i]):
                return i
            i += 1
        return -1

    def __iter__(self):
        i = 0
        while i < self._size:
            yield self._data[i]
            i += 1

    def __repr__(self):
        return "{0}([{1}], ölçü={2}, tutum={3})".format(
            type(self).__name__,
            ", ".join(repr(x) for x in self),
            self._size,
            self._capacity,
        )


class StaticArray(_BaseArray):
    """Sabit tutumlu massiv. Dolduqda ``ArrayOverflowError`` qaldırır.

    Tətbiqdəki rolu: sabit sayda (fiziki) yükləmə rampalarının idarəsi və
    benchmark-da dinamik massivlə müqayisə.
    Yaddaş: O(capacity) — yaradılan anda tam ayrılır, heç vaxt dəyişmir.
    """

    __slots__ = ()

    def _ensure_space(self):
        if self._size == self._capacity:
            raise ArrayOverflowError(
                "Statik massiv doludur (tutum: {0}). Yeni element əlavə etmək mümkün deyil.".format(
                    self._capacity
                )
            )


class DynamicArray(_BaseArray):
    """Avtomatik böyüyən massiv: dolduqda tutum ``capacity * 2`` olur.

    Ölçü dəyişdirmə zamanı bütün elementlər yeni bloka ƏL İLƏ (dövrlə) köçürülür — O(n).
    Lakin bu nadir baş verdiyi üçün ``append`` amortizasiyalı O(1)-dir:
    n əlavə üçün ümumi köçürmə sayı 1 + 2 + 4 + ... + n/2 < n.

    Tətbiqdəki rolu: əsas məhsul kataloqu.
    """

    __slots__ = ("resize_count",)

    def __init__(self, initial_capacity=1):
        super().__init__(initial_capacity)
        self.resize_count = 0

    def _resize(self, new_capacity):
        """Yeni blok ayırır və elementləri bir-bir köçürür. Zaman: O(n)."""
        new_data = _allocate(new_capacity)
        i = 0
        while i < self._size:
            new_data[i] = self._data[i]
            i += 1
        self._data = new_data
        self._capacity = new_capacity
        self.resize_count += 1

    def _ensure_space(self):
        if self._size == self._capacity:
            self._resize(self._capacity * 2)
