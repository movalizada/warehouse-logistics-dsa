"""
Avtomatlaşdırılmış Performans Testləri (Benchmark)
=================================================

1. StaticArray vs. DynamicArray — sona/əvvələ/ortaya əlavə, silmə, axtarış
2. SinglyLinkedList vs. DoublyLinkedList — baş/son əməliyyatları, iki istiqamətli gəzinti, yaddaş
3. BST — təsadüfi vs. sıralı verilənlər (hündürlük və axtarış vaxtı)
4. HashTable — yük əmsalının axtarış vaxtına və zəncir uzunluğuna təsiri

Vaxt ``time.perf_counter()`` ilə ölçülür. Hər əməliyyat üçün strukturu
hazırlamaq (doldurmaq) vaxta daxil EDİLMİR — yalnız ölçülən əməliyyatlar.
Nəticələr bir əməliyyat üçün orta vaxt kimi göstərilir.
"""

import math
import random
import time

from src.structures.arrays import ArrayOverflowError, DynamicArray, StaticArray
from src.structures.bst import BinarySearchTree
from src.structures.hash_table import HashTable
from src.structures.linked_lists import DoublyLinkedList, SinglyLinkedList
from src.utils.table import format_time, new_rows, print_table

DEFAULT_SIZES = (1000, 10000, 50000)


def _sizes_label(sizes):
    return ", ".join("{0:,}".format(s) for s in sizes)


def _ratio(a, b):
    if b == 0:
        return "—"
    return "{0:.2f}x".format(a / b)


def shuffle(array, seed=None):
    """``DynamicArray`` üzərində Fisher–Yates qarışdırması. O(n)."""
    rng = random.Random(seed)
    i = len(array) - 1
    while i > 0:
        j = rng.randint(0, i)
        tmp = array[i]
        array[i] = array[j]
        array[j] = tmp
        i -= 1
    return array


# ====================================================================== #
# 1. MASSİVLƏR
# ====================================================================== #
def _build_static(n, extra):
    arr = StaticArray(n + extra)
    i = 0
    while i < n:
        arr.append(i)
        i += 1
    return arr


def _build_dynamic(n):
    arr = DynamicArray()
    i = 0
    while i < n:
        arr.append(i)
        i += 1
    return arr


def _time_ops(structure, operation, count):
    start = time.perf_counter()
    i = 0
    while i < count:
        operation(structure, i)
        i += 1
    return (time.perf_counter() - start) / count


def run_array_benchmark(sizes=DEFAULT_SIZES, shift_ops=30, search_ops=10):
    print("\n>>> Statik vs. Dinamik massiv testi işləyir (ölçülər: {0}). Gözləyin...".format(
        _sizes_label(sizes)))
    rows = new_rows()
    resize_rows = new_rows()

    for n in sizes:
        # --- Sona əlavə: boş strukturu n elementlə doldurmaq (amortizasiya) ---
        static = StaticArray(n)
        start = time.perf_counter()
        i = 0
        while i < n:
            static.append(i)
            i += 1
        t_static = (time.perf_counter() - start) / n

        dynamic = DynamicArray()
        start = time.perf_counter()
        i = 0
        while i < n:
            dynamic.append(i)
            i += 1
        t_dynamic = (time.perf_counter() - start) / n
        rows.append(("{0:,}".format(n), "Sona əlavə (append, n dəfə)",
                     format_time(t_static), format_time(t_dynamic), _ratio(t_dynamic, t_static)))
        resize_rows.append(("{0:,}".format(n), str(dynamic.resize_count),
                            "{0:,}".format(dynamic.capacity),
                            "{0:.1f}%".format(100.0 * len(dynamic) / dynamic.capacity)))

        # --- Statik massivdə daşma nümayişi ---
        try:
            static.append(-1)
            overflow_ok = False
        except ArrayOverflowError:
            overflow_ok = True

        cases = (
            ("Əvvələ əlavə (insert 0)", lambda a, i: a.insert(0, i), shift_ops),
            ("Ortaya əlavə (insert n/2)", lambda a, i: a.insert(len(a) // 2, i), shift_ops),
            ("Əvvəldən silmə (delete 0)", lambda a, i: a.delete(0), shift_ops),
            ("Ortadan silmə (delete n/2)", lambda a, i: a.delete(len(a) // 2), shift_ops),
            ("Sondan silmə (pop)", lambda a, i: a.pop(), shift_ops),
            ("Xətti axtarış (olmayan element)", lambda a, i: a.search(-7), search_ops),
        )
        for label, operation, count in cases:
            s = _build_static(n, count)
            d = _build_dynamic(n)
            t_s = _time_ops(s, operation, count)
            t_d = _time_ops(d, operation, count)
            rows.append(("{0:,}".format(n), label, format_time(t_s), format_time(t_d), _ratio(t_d, t_s)))

        if not overflow_ok:  # pragma: no cover - təhlükəsizlik yoxlaması
            print("XƏBƏRDARLIQ: StaticArray daşma xətası qaldırmadı!")

    print_table(("n", "Əməliyyat", "StaticArray (orta/əm.)", "DynamicArray (orta/əm.)", "Dinamik/Statik"),
                rows, "CƏDVƏL 1. Statik vs. Dinamik massiv — bir əməliyyatın orta vaxtı")
    print_table(("n", "Ölçü dəyişmə sayı", "Son tutum", "Doluluq"), resize_rows,
                "CƏDVƏL 2. DynamicArray-in genişlənmə statistikası (capacity * 2)")
    print("  ✔ StaticArray dolu olduqda ArrayOverflowError qaldırdı (avtomatik genişlənmə yoxdur).")
    print("  Nəticə: append hər iki massivdə O(1)-dir; dinamik massivdə nadir O(n) köçürmələr\n"
          "  log2(n) dəfə baş verir və amortizasiyalı qiymət sabit qalır. Əvvələ/ortaya əlavə və\n"
          "  silmə elementlərin sürüşdürülməsini tələb etdiyi üçün n ilə xətti böyüyür — O(n).")


# ====================================================================== #
# 2. ƏLAQƏLİ SİYAHILAR
# ====================================================================== #
def _build_list(cls, n):
    lst = cls()
    i = 0
    while i < n:
        lst.push_back(i)
        i += 1
    return lst


def _time_traversal(iterable_factory):
    start = time.perf_counter()
    count = 0
    for _ in iterable_factory():
        count += 1
    return time.perf_counter() - start


def run_linked_list_benchmark(sizes=DEFAULT_SIZES, head_ops=1000, tail_delete_ops=20):
    print("\n>>> Tək vs. İki əlaqəli siyahı testi işləyir (ölçülər: {0}). Gözləyin...".format(
        _sizes_label(sizes)))
    rows = new_rows()
    memory_rows = new_rows()
    s_node = SinglyLinkedList.node_size_bytes()
    d_node = DoublyLinkedList.node_size_bytes()

    for n in sizes:
        cases = (
            ("Başa əlavə (push_front)", lambda l, i: l.push_front(i), head_ops),
            ("Sona əlavə (push_back)", lambda l, i: l.push_back(i), head_ops),
            ("Başdan silmə (pop_front)", lambda l, i: l.pop_front(), head_ops),
            ("Sondan silmə (pop_back)", lambda l, i: l.pop_back(), tail_delete_ops),
        )
        for label, operation, count in cases:
            sl = _build_list(SinglyLinkedList, n + count)
            dl = _build_list(DoublyLinkedList, n + count)
            t_s = _time_ops(sl, operation, count)
            t_d = _time_ops(dl, operation, count)
            rows.append(("{0:,}".format(n), label, format_time(t_s), format_time(t_d), _ratio(t_s, t_d)))

        sl = _build_list(SinglyLinkedList, n)
        dl = _build_list(DoublyLinkedList, n)
        t_s = _time_traversal(lambda: iter(sl))
        t_d = _time_traversal(lambda: iter(dl))
        rows.append(("{0:,}".format(n), "İrəli gəzinti (bütün siyahı)", format_time(t_s), format_time(t_d), _ratio(t_s, t_d)))
        t_s = _time_traversal(sl.traverse_backward)
        t_d = _time_traversal(dl.traverse_backward)
        rows.append(("{0:,}".format(n), "Geri gəzinti (bütün siyahı)*", format_time(t_s), format_time(t_d), _ratio(t_s, t_d)))

        s_total = s_node * n
        d_total = d_node * n
        memory_rows.append(("{0:,}".format(n), "{0:,.1f} KB".format(s_total / 1024.0),
                            "{0:,.1f} KB".format(d_total / 1024.0),
                            "+{0:,.1f} KB".format((d_total - s_total) / 1024.0),
                            "+{0:.1f}%".format(100.0 * (d_total - s_total) / s_total)))

    print_table(("n", "Əməliyyat", "Singly (orta)", "Doubly (orta)", "Singly/Doubly"),
                rows, "CƏDVƏL 3. Tək vs. İki əlaqəli siyahı — vaxt müqayisəsi")
    print("  * Tək əlaqəli siyahıda geri gəzinti üçün köməkçi Stack-ə O(n) əlavə yaddaş lazımdır.")
    print_table(("n", "Singly (düyünlər)", "Doubly (düyünlər)", "Fərq (prev göstəricisi)", "Artım"),
                memory_rows,
                "CƏDVƏL 4. Nəzəri yaddaş yükü (düyün: Singly={0} B, Doubly={1} B; sys.getsizeof)".format(
                    s_node, d_node))
    print("  Nəticə: Doubly hər düyündə əlavə 'prev' göstəricisi saxlayır (+{0} bayt/düyün),\n"
          "  bunun müqabilində sondan silmə O(n) → O(1) olur və geri gəzinti əlavə yaddaşsız işləyir.".format(
              d_node - s_node))


# ====================================================================== #
# 3. BST: TƏSADÜFİ vs. SIRALI
# ====================================================================== #
class BSTResult:
    """BST eksperimentinin nəticələri (dict əvəzinə sadə sinif)."""

    __slots__ = ("height", "insert_total", "avg_search", "avg_comparisons",
                 "max_comparisons", "worst_search")

    def __init__(self, height, insert_total, avg_search, avg_comparisons,
                 max_comparisons, worst_search):
        self.height = height
        self.insert_total = insert_total
        self.avg_search = avg_search
        self.avg_comparisons = avg_comparisons
        self.max_comparisons = max_comparisons
        self.worst_search = worst_search


def _measure_bst(keys):
    tree = BinarySearchTree()
    start = time.perf_counter()
    for k in keys:
        tree.insert(k, k)
    insert_time = time.perf_counter() - start

    total_comparisons = 0
    max_comparisons = 0
    start = time.perf_counter()
    for k in keys:
        found, comps = tree.search_with_comparisons(k)
        total_comparisons += comps
        if comps > max_comparisons:
            max_comparisons = comps
    search_total = time.perf_counter() - start

    # ən pis hal: ən dərin açar (eyni müqayisə sayı ilə ən uzun yol)
    worst_key = None
    for k in keys:
        if tree.search_with_comparisons(k)[1] == max_comparisons:
            worst_key = k
            break
    repeats = 200
    start = time.perf_counter()
    i = 0
    while i < repeats:
        tree.search(worst_key)
        i += 1
    worst_time = (time.perf_counter() - start) / repeats

    n = len(keys)
    return BSTResult(tree.get_height(), insert_time, search_total / n,
                     total_comparisons / float(n), max_comparisons, worst_time)


def run_bst_experiment(n=2000, seed=42):
    print("\n>>> BST eksperimenti: {0:,} təsadüfi vs. {0:,} sıralı element...".format(n))
    sorted_keys = DynamicArray()
    i = 1
    while i <= n:
        sorted_keys.append(i)
        i += 1
    random_keys = DynamicArray()
    for k in sorted_keys:
        random_keys.append(k)
    shuffle(random_keys, seed)

    r = _measure_bst(random_keys)
    s = _measure_bst(sorted_keys)
    ideal = int(math.floor(math.log2(n))) + 1

    rows = new_rows()
    rows.append(("Ağacın hündürlüyü (səviyyələr)", str(r.height), str(s.height), str(ideal)))
    rows.append(("Orta müqayisə sayı (axtarış)", "{0:.1f}".format(r.avg_comparisons),
                 "{0:.1f}".format(s.avg_comparisons), "≈ {0}".format(ideal - 1)))
    rows.append(("Maks. müqayisə (ən pis axtarış)", str(r.max_comparisons), str(s.max_comparisons), str(ideal)))
    rows.append(("Orta axtarış vaxtı", format_time(r.avg_search), format_time(s.avg_search), "—"))
    rows.append(("Ən pis axtarış vaxtı (ən dərin açar)", format_time(r.worst_search), format_time(s.worst_search), "—"))
    rows.append(("Ümumi əlavə vaxtı ({0:,} insert)".format(n), format_time(r.insert_total), format_time(s.insert_total), "—"))

    print_table(("Metrik", "Təsadüfi sıra", "Sıralı sıra", "İdeal (balanslı)"), rows,
                "CƏDVƏL 5. BST — təsadüfi vs. sıralı daxiletmə (n = {0:,})".format(n))
    expected = 2.99 * math.log2(n)
    print("  Nəticə: təsadüfi daxiletmədə hündürlük = {0} (asimptotik hədd ≈ 2.99·log2 n ≈ {1:.0f},\n"
          "  yəni O(log n)); sıralı daxiletmədə isə hündürlük = n = {2} — ağac sağa əyilmiş xətti\n"
          "  zəncirə çevrilir. Axtarış O(log n) → O(n) pisləşir: orta axtarış ~{3:.0f} dəfə yavaşdır.".format(
              r.height, expected, s.height, s.avg_search / r.avg_search if r.avg_search else 0))
    return r, s


# ====================================================================== #
# 4. HASH CƏDVƏLİ: YÜK ƏMSALI
# ====================================================================== #
def run_hash_table_benchmark(n=10000, bucket_counts=(20011, 10007, 2003, 503, 101)):
    print("\n>>> Hash cədvəli testi: {0:,} SKU açarı, sabit kova sayları (rehash söndürülüb)...".format(n))
    keys = DynamicArray()
    i = 0
    while i < n:
        keys.append("SKU-{0:06d}".format(i))
        i += 1
    rows = new_rows()
    for m in bucket_counts:
        table = HashTable(capacity=m, auto_resize=False)
        for k in keys:
            table.put(k, k)
        start = time.perf_counter()
        for k in keys:
            table.get(k)
        avg = (time.perf_counter() - start) / n
        start = time.perf_counter()
        j = 0
        while j < 1000:
            table.get("YOX-{0}".format(j))
            j += 1
        miss = (time.perf_counter() - start) / 1000
        st = table.stats()
        expected = n - m * (1.0 - math.exp(-float(n) / m))
        rows.append(("{0:,}".format(m), "{0:.2f}".format(st.load_factor), "{0:,}".format(st.collisions),
                     "{0:,.0f}".format(expected),
                     str(st.longest_chain), "{0:,}".format(st.empty_buckets),
                     format_time(avg), format_time(miss)))
    print_table(("Kova (m)", "α = n/m", "Toqquşma", "Gözlənilən (ideal hash)", "Ən uzun zəncir", "Boş kova",
                 "Uğurlu axtarış", "Uğursuz axtarış"), rows,
                "CƏDVƏL 6. Yük əmsalının (load factor) performansa təsiri (n = {0:,})".format(n))
    print("  Gözlənilən toqquşma = n − m·(1 − e^(−n/m)) — ideal (vahid paylanan) hash üçün düstur.")
    print("  Nəticə: orta axtarış qiyməti O(1 + α)-dır. α ≤ 1 olduqda zəncirlər qısa qalır;\n"
          "  α böyüdükcə zəncirlər uzanır və axtarış xətti axtarışa yaxınlaşır. Buna görə\n"
          "  tətbiqdəki cədvəl α > 0.75 olduqda kova sayını avtomatik ikiqat artırır (rehash).")


def run_all(sizes=DEFAULT_SIZES, bst_n=2000):
    total_start = time.perf_counter()
    run_array_benchmark(sizes)
    run_linked_list_benchmark(sizes)
    run_bst_experiment(bst_n)
    run_hash_table_benchmark()
    print("\n  Bütün testlər {0} ərzində tamamlandı.".format(format_time(time.perf_counter() - total_start)))


if __name__ == "__main__":
    run_all()
