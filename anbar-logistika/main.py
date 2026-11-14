"""
ANBAR VƏ LOGİSTİKA İDARƏETMƏ SİSTEMİ
Kurs layihəsi: "Müasir data strukturları və alqoritmləri"

İşə salmaq:  python main.py
"""

import sys

from src.benchmarks import performance
from src.services.warehouse import Warehouse, WarehouseError
from src.utils.table import new_rows, print_table

LINE = "=" * 66


class ExitApp(Exception):
    """İstifadəçi proqramdan çıxır (Ctrl+C / Ctrl+D)."""


# ====================================================================== #
# Daxiletmə köməkçiləri
# ====================================================================== #
def ask(prompt):
    try:
        return input(prompt).strip()
    except (EOFError, KeyboardInterrupt):
        raise ExitApp()


def ask_required(prompt):
    while True:
        value = ask(prompt)
        if value:
            return value
        print("  ! Bu sahə boş ola bilməz.")


def ask_int(prompt, minimum=None, maximum=None, allow_empty=False, default=None):
    while True:
        raw = ask(prompt)
        if raw == "":
            if default is not None:
                return default
            if allow_empty:
                return None
        try:
            value = int(raw)
        except ValueError:
            print("  ! Tam ədəd daxil edin.")
            continue
        if minimum is not None and value < minimum:
            print("  ! Dəyər {0}-dən kiçik ola bilməz.".format(minimum))
            continue
        if maximum is not None and value > maximum:
            print("  ! Dəyər {0}-dən böyük ola bilməz.".format(maximum))
            continue
        return value


def ask_float(prompt, minimum=0.0, allow_empty=False):
    while True:
        raw = ask(prompt).replace(",", ".")
        if raw == "" and allow_empty:
            return None
        try:
            value = float(raw)
        except ValueError:
            print("  ! Ədəd daxil edin (məs. 49.90).")
            continue
        if value < minimum:
            print("  ! Dəyər {0}-dən kiçik ola bilməz.".format(minimum))
            continue
        return value


def ask_yes_no(prompt):
    return ask(prompt + " (b/x): ").lower() in ("b", "bəli", "beli", "h", "hə", "he", "y", "yes")


def pause():
    ask("\n  Davam etmək üçün Enter basın...")


def header(title):
    print("\n" + LINE)
    print("  " + title)
    print(LINE)


def menu(title, options):
    """``options`` — (açar, mətn) cütlərinin tuple-ı."""
    header(title)
    for key, text in options:
        print("  {0}. {1}".format(key, text))
    return ask("\n  Seçiminiz: ")


# ====================================================================== #
# Çap köməkçiləri
# ====================================================================== #
def print_products(products, title):
    rows = new_rows()
    number = 0
    for p in products:
        number += 1
        rows.append((str(number), p.sku, p.name, "{0:,.2f}".format(p.price),
                     str(p.quantity), "{0:,.2f}".format(p.total_value())))
    if number == 0:
        print("\n  (Heç bir məhsul tapılmadı.)")
        return
    print_table(("№", "SKU", "Ad", "Qiymət (AZN)", "Miqdar", "Dəyər (AZN)"), rows, title)


def print_orders(orders, title):
    rows = new_rows()
    number = 0
    for o in orders:
        number += 1
        rows.append((str(number), "#{0}".format(o.order_id), o.label(), o.customer,
                     o.sku, str(o.quantity), o.status))
    if number == 0:
        print("\n  {0}: boşdur.".format(title))
        return
    print_table(("Mövqe", "Sifariş", "Tip", "Müştəri", "SKU", "Miqdar", "Status"), rows, title)


# ====================================================================== #
# 1. MƏHSUL KATALOQU
# ====================================================================== #
def catalog_menu(wh):
    while True:
        choice = menu("MƏHSUL KATALOQU  [DynamicArray + HashTable + BST]", (
            ("1", "Bütün məhsullar (kataloq ardıcıllığı — DynamicArray)"),
            ("2", "SKU ilə axtarış (HashTable, orta O(1))"),
            ("3", "Yeni məhsul əlavə et"),
            ("4", "Qiyməti / miqdarı yenilə"),
            ("5", "Məhsulu sil"),
            ("6", "Kataloq massivinin vəziyyəti (ölçü / tutum)"),
            ("0", "Geri"),
        ))
        try:
            if choice == "1":
                print_products(wh.catalog, "Məhsul kataloqu ({0} məhsul, ümumi dəyər: {1:,.2f} AZN)".format(
                    len(wh.catalog), wh.total_inventory_value()))
            elif choice == "2":
                sku = ask_required("  SKU kodu: ")
                product = wh.get_product(sku)
                if product is None:
                    print("  ✘ '{0}' tapılmadı.".format(sku.upper()))
                else:
                    print("  ✔ Tapıldı (kova #{0}): {1}".format(
                        wh.sku_index.bucket_index_of(product.sku), product))
            elif choice == "3":
                sku = ask_required("  SKU (məs. ELK-1010): ")
                name = ask_required("  Ad: ")
                price = ask_float("  Qiymət (AZN): ")
                qty = ask_int("  Miqdar: ", minimum=0)
                product = wh.add_product(sku, name, price, qty)
                print("  ✔ Əlavə edildi: {0}".format(product))
            elif choice == "4":
                product = wh.require_product(ask_required("  SKU kodu: "))
                print("  Cari: {0}".format(product))
                price = ask_float("  Yeni qiymət (boş = dəyişmə): ", allow_empty=True)
                qty = ask_int("  Yeni miqdar (boş = dəyişmə): ", minimum=0, allow_empty=True)
                if price is None and qty is None:
                    print("  Heç nə dəyişdirilmədi.")
                else:
                    print("  ✔ Yeniləndi: {0}".format(wh.update_product(product.sku, price, qty)))
            elif choice == "5":
                product = wh.require_product(ask_required("  Silinəcək SKU: "))
                if ask_yes_no("  '{0}' silinsin?".format(product.name)):
                    wh.remove_product(product.sku)
                    print("  ✔ Silindi. (Geri qaytarmaq üçün əsas menyuda 3-ü seçin.)")
            elif choice == "6":
                print("  Elementlər: {0} | Tutum: {1} | Genişlənmə sayı: {2} | Doluluq: {3:.0f}%".format(
                    len(wh.catalog), wh.catalog.capacity, wh.catalog.resize_count,
                    100.0 * len(wh.catalog) / wh.catalog.capacity))
            elif choice == "0":
                return
            else:
                print("  ! Yanlış seçim.")
                continue
        except WarehouseError as exc:
            print("  ✘ " + str(exc))
        pause()


# ====================================================================== #
# 2. SİFARİŞLƏR
# ====================================================================== #
def orders_menu(wh):
    while True:
        print_orders(wh.order_queue, "Adi sifariş növbəsi (Queue — FIFO)")
        print_orders(wh.dispatch_line, "Göndəriş xətti (Deque — ön: VIP, arxa: adi)")
        choice = menu("SİFARİŞLƏR  [Queue + Deque]", (
            ("1", "Yeni adi sifariş (növbənin sonuna — enqueue)"),
            ("2", "Təcili VIP sifariş (göndəriş xəttinin önünə — add_front)"),
            ("3", "Növbədəki ilk sifarişi emal et (dequeue → add_rear)"),
            ("4", "Öndəki sifarişi yola sal (remove_front, stok azalır)"),
            ("5", "Öndəki sifarişi ləğv et (remove_front)"),
            ("6", "Arxadakı sifarişi ləğv et (remove_rear)"),
            ("7", "Nömrəyə görə ləğv et"),
            ("0", "Geri"),
        ))
        try:
            if choice in ("1", "2"):
                customer = ask_required("  Müştəri: ")
                product = wh.require_product(ask_required("  SKU: "))
                print("  Məhsul: {0}".format(product))
                qty = ask_int("  Miqdar: ", minimum=1)
                order = wh.create_order(customer, product.sku, qty, vip=(choice == "2"))
                print("  ✔ Yaradıldı: {0}".format(order))
            elif choice == "3":
                print("  ✔ Göndəriş xəttinə keçirildi: {0}".format(wh.process_next_order()))
            elif choice == "4":
                order, ok = wh.dispatch_next()
                if ok:
                    print("  ✔ {0}. Qalan stok: {1} əd.".format(order, wh.get_product(order.sku).quantity))
                else:
                    print("  ✘ {0}".format(order))
            elif choice == "5":
                print("  ✔ " + str(wh.cancel_front()))
            elif choice == "6":
                print("  ✔ " + str(wh.cancel_rear()))
            elif choice == "7":
                print("  ✔ " + str(wh.cancel_by_id(ask_int("  Sifariş nömrəsi: ", minimum=1))))
            elif choice == "0":
                return
            else:
                print("  ! Yanlış seçim.")
                continue
        except WarehouseError as exc:
            print("  ✘ " + str(exc))
        pause()


# ====================================================================== #
# 3. UNDO
# ====================================================================== #
def undo_menu(wh):
    header("ƏMƏLİYYATI GERİ QAYTARMAQ  [Stack — LIFO]")
    if wh.undo_stack.is_empty():
        print("  Tarixçə boşdur — geri qaytarılacaq əməliyyat yoxdur.")
        pause()
        return
    print("  Son əməliyyatlar (zirvədən başlayaraq):")
    shown = 0
    for action in wh.undo_stack:
        shown += 1
        marker = "→" if shown == 1 else " "
        print("   {0} {1}. {2}".format(marker, shown, action))
        if shown == 10:
            break
    if ask_yes_no("\n  Ən son əməliyyat geri qaytarılsın?"):
        try:
            print("  ✔ Geri qaytarıldı: {0}".format(wh.undo()))
        except WarehouseError as exc:
            print("  ✘ " + str(exc))
    pause()


# ====================================================================== #
# 4. ÇATDIRILMA MARŞRUTU
# ====================================================================== #
def route_menu(wh):
    while True:
        header("ÇATDIRILMA MARŞRUTU  [SinglyLinkedList]")
        if wh.route.is_empty():
            print("  Marşrut boşdur.")
        else:
            print("  " + "  →  ".join(wh.route) + "  → ∅")
        choice = menu("Əməliyyatlar", (
            ("1", "Sona nöqtə əlavə et (push_back, O(1))"),
            ("2", "Başa nöqtə əlavə et (push_front, O(1))"),
            ("3", "Növbəti nöqtəyə çat (pop_front, O(1))"),
            ("4", "Nöqtəni adına görə sil (O(n))"),
            ("0", "Geri"),
        ))
        try:
            if choice == "1":
                wh.add_checkpoint(ask_required("  Nöqtənin adı: "))
                print("  ✔ Əlavə edildi.")
            elif choice == "2":
                wh.add_checkpoint(ask_required("  Nöqtənin adı: "), at_start=True)
                print("  ✔ Əlavə edildi.")
            elif choice == "3":
                point = wh.arrive_next_checkpoint()
                print("  🚚 '{0}' nöqtəsinə çatıldı. Qalan nöqtə: {1}".format(point, len(wh.route)))
            elif choice == "4":
                print("  ✔ Silindi: " + wh.remove_checkpoint(ask_required("  Nöqtənin adı: ")))
            elif choice == "0":
                return
            else:
                print("  ! Yanlış seçim.")
                continue
        except WarehouseError as exc:
            print("  ✘ " + str(exc))
        pause()


# ====================================================================== #
# 5. RƏF YOXLAMASI
# ====================================================================== #
def shelves_menu(wh):
    while True:
        header("RƏF YOXLAMASI NAVİQASİYASI  [DoublyLinkedList]")
        if wh.shelves.is_empty():
            print("  Rəf yoxdur.")
        else:
            parts = new_rows()
            for shelf in wh.shelves:
                text = shelf.code
                if wh.shelf_cursor is not None and shelf is wh.shelf_cursor.data:
                    text = "[" + text + "]"
                parts.append(text)
            print("  ∅ ⇄ " + " ⇄ ".join(parts) + " ⇄ ∅")
            print("  Cari rəf ({0}/{1}): {2}".format(wh.shelf_position(), len(wh.shelves), wh.current_shelf()))
        choice = menu("Əməliyyatlar", (
            ("i", "İrəli (next)"),
            ("g", "Geri (prev)"),
            ("1", "Birinci rəfə keç (head)"),
            ("2", "Sonuncu rəfə keç (tail)"),
            ("3", "Cari rəfi yoxlanılmış kimi qeyd et"),
            ("4", "Yeni rəf əlavə et (sona)"),
            ("5", "Cari rəfi sil (O(1), prev göstəricisi sayəsində)"),
            ("6", "Bütün rəfləri tərsinə göstər (geri gəzinti)"),
            ("0", "Geri"),
        )).lower()
        try:
            if choice in ("i", "irəli", "ireli"):
                print("  → " + str(wh.move_forward()))
                continue
            elif choice in ("g", "geri"):
                print("  ← " + str(wh.move_backward()))
                continue
            elif choice == "1":
                wh.go_first_shelf()
                continue
            elif choice == "2":
                wh.go_last_shelf()
                continue
            elif choice == "3":
                print("  ✔ " + str(wh.inspect_current(ask("  Qeyd (boş ola bilər): "))))
            elif choice == "4":
                print("  ✔ Əlavə edildi: " + str(wh.add_shelf(ask_required("  Rəf kodu: "), ask("  Kateqoriya: "))))
            elif choice == "5":
                shelf = wh.current_shelf()
                if ask_yes_no("  '{0}' rəfi silinsin?".format(shelf.code)):
                    print("  ✔ Silindi: " + str(wh.remove_current_shelf()))
            elif choice == "6":
                for shelf in wh.shelves.traverse_backward():
                    print("   ← " + str(shelf))
            elif choice == "0":
                return
            else:
                print("  ! Yanlış seçim.")
                continue
        except WarehouseError as exc:
            print("  ✘ " + str(exc))
        pause()


# ====================================================================== #
# 6. YÜKLƏMƏ RAMPALARI
# ====================================================================== #
def docks_menu(wh):
    while True:
        header("YÜKLƏMƏ RAMPALARI  [StaticArray — tutum {0}]".format(wh.DOCK_COUNT))
        i = 0
        while i < wh.DOCK_COUNT:
            occupant = wh.docks[i] if i < len(wh.docks) else "— boş —"
            print("  Rampa {0}: {1}".format(i + 1, occupant))
            i += 1
        choice = menu("Əməliyyatlar", (
            ("1", "Yük maşını yerləşdir (append — dolu olduqda Overflow)"),
            ("2", "Yük maşınını yola sal (delete — sonrakılar sürüşür)"),
            ("0", "Geri"),
        ))
        try:
            if choice == "1":
                number = wh.dock_truck(ask_required("  Nömrə nişanı (məs. 10-AA-777): "))
                print("  ✔ Rampa {0}-ə yerləşdirildi.".format(number))
            elif choice == "2":
                plate = wh.release_truck(ask_int("  Rampa nömrəsi: ", minimum=1))
                print("  ✔ {0} yola salındı.".format(plate))
            elif choice == "0":
                return
            else:
                print("  ! Yanlış seçim.")
                continue
        except WarehouseError as exc:
            print("  ✘ " + str(exc))
        pause()


# ====================================================================== #
# 7. HESABATLAR (BST)
# ====================================================================== #
def reports_menu(wh):
    while True:
        choice = menu("HESABATLAR VƏ ARALIQ SORĞULARI  [BinarySearchTree]", (
            ("1", "Qiymətə görə sıralı hesabat (in-order gəzinti)"),
            ("2", "Qiymət aralığı sorğusu (range query)"),
            ("3", "Az qalan stok hesabatı (miqdar ≤ hədd)"),
            ("4", "Miqdar aralığı sorğusu"),
            ("5", "İndeks ağaclarının statistikası (hündürlük, min/maks)"),
            ("0", "Geri"),
        ))
        try:
            if choice == "1":
                print_products(wh.products_by_price(), "Qiymətə görə artan sıra")
            elif choice == "2":
                low = ask_float("  Minimum qiymət (AZN): ")
                high = ask_float("  Maksimum qiymət (AZN): ", minimum=low)
                print_products(wh.products_in_price_range(low, high),
                               "Qiyməti {0:.2f} – {1:.2f} AZN olan məhsullar".format(low, high))
            elif choice == "3":
                limit = ask_int("  Hədd (default 10): ", minimum=0, default=10)
                print_products(wh.products_in_stock_range(0, limit),
                               "Stoku ≤ {0} olan məhsullar (sifariş verilməlidir)".format(limit))
            elif choice == "4":
                low = ask_int("  Minimum miqdar: ", minimum=0)
                high = ask_int("  Maksimum miqdar: ", minimum=low)
                print_products(wh.products_in_stock_range(low, high),
                               "Miqdarı {0} – {1} olan məhsullar".format(low, high))
            elif choice == "5":
                rows = new_rows()
                for label, tree in (("Qiymət indeksi", wh.price_index), ("Stok indeksi", wh.stock_index)):
                    mn, mx = tree.min_key(), tree.max_key()
                    rows.append((label, str(len(tree)), str(tree.get_height()),
                                 "—" if mn is None else "{0} ({1})".format(mn[0], mn[1]),
                                 "—" if mx is None else "{0} ({1})".format(mx[0], mx[1])))
                print_table(("Ağac", "Düyün", "Hündürlük", "Min açar", "Maks açar"), rows,
                            "BST indekslərinin vəziyyəti")
            elif choice == "0":
                return
            else:
                print("  ! Yanlış seçim.")
                continue
        except WarehouseError as exc:
            print("  ✘ " + str(exc))
        pause()


# ====================================================================== #
# 8. HASH CƏDVƏLİ STATİSTİKASI
# ====================================================================== #
def hash_stats_menu(wh):
    header("HASH CƏDVƏLİ STATİSTİKASI  [Zəncirləmə — Chaining]")
    st = wh.sku_index.stats()
    rows = new_rows()
    rows.append(("Ümumi element sayı", str(st.total_items)))
    rows.append(("Kova sayı (m)", str(st.bucket_count)))
    rows.append(("Yük əmsalı α = n/m", "{0:.3f}".format(st.load_factor)))
    rows.append(("Toqquşma sayı (Σ zəncir − 1)", str(st.collisions)))
    rows.append(("Toqquşma hadisələri (son rehash-dən bəri)", str(st.collision_events)))
    rows.append(("Ən uzun zəncir", str(st.longest_chain)))
    rows.append(("Boş kovalar", str(st.empty_buckets)))
    rows.append(("Rehash sayı (genişlənmə)", str(st.rehash_count)))
    print_table(("Metrik", "Dəyər"), rows)
    print("\n  Kovaların paylanması (hər '■' bir element):")
    index = 0
    for length in wh.sku_index.bucket_lengths():
        if length > 0:
            keys = " → ".join(wh.sku_index.bucket_keys(index))
            print("   [{0:>3}] {1:<4} {2}".format(index, "■" * length, keys))
        index += 1
    pause()


# ====================================================================== #
# 9. BENCHMARK-LAR
# ====================================================================== #
def benchmarks_menu():
    while True:
        choice = menu("PERFORMANS TESTLƏRİ (BENCHMARK)", (
            ("1", "Statik vs. Dinamik massiv (1 000 / 10 000 / 50 000)"),
            ("2", "Tək vs. İki əlaqəli siyahı (1 000 / 10 000 / 50 000)"),
            ("3", "BST: təsadüfi vs. sıralı verilənlər"),
            ("4", "Hash cədvəli: yük əmsalının təsiri"),
            ("5", "Hamısını işə sal"),
            ("6", "Sürətli rejim (kiçik ölçülər: 500 / 2 000 / 5 000)"),
            ("0", "Geri"),
        ))
        if choice == "1":
            performance.run_array_benchmark()
        elif choice == "2":
            performance.run_linked_list_benchmark()
        elif choice == "3":
            performance.run_bst_experiment(ask_int("  Element sayı N (default 2000): ", minimum=10,
                                                   maximum=20000, default=2000))
        elif choice == "4":
            performance.run_hash_table_benchmark()
        elif choice == "5":
            performance.run_all()
        elif choice == "6":
            performance.run_all(sizes=(500, 2000, 5000), bst_n=1000)
        elif choice == "0":
            return
        else:
            print("  ! Yanlış seçim.")
            continue
        pause()


# ====================================================================== #
# ƏSAS MENYU
# ====================================================================== #
def dashboard(wh):
    print("\n  Məhsul: {0} | Növbədə: {1} | Göndəriş xəttində: {2} | Marşrut nöqtəsi: {3} | "
          "Rampa: {4}/{5} | Undo: {6}".format(
              len(wh.catalog), len(wh.order_queue), len(wh.dispatch_line), len(wh.route),
              len(wh.docks), wh.DOCK_COUNT, len(wh.undo_stack)))


def main():
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except (ValueError, OSError):
            pass
    wh = Warehouse()
    wh.seed_sample_data()
    print(LINE)
    print("   ANBAR VƏ LOGİSTİKA İDARƏETMƏ SİSTEMİ")
    print("   Kurs layihəsi: «Müasir data strukturları və alqoritmləri»")
    print(LINE)
    print("  Sistem nümunə məlumatlarla yükləndi.")
    handlers = (
        ("1", "Məhsul kataloqu           [DynamicArray + HashTable]", lambda: catalog_menu(wh)),
        ("2", "Sifarişlər                [Queue + Deque]", lambda: orders_menu(wh)),
        ("3", "Əməliyyatı geri qaytar    [Stack]", lambda: undo_menu(wh)),
        ("4", "Çatdırılma marşrutu       [SinglyLinkedList]", lambda: route_menu(wh)),
        ("5", "Rəf yoxlaması             [DoublyLinkedList]", lambda: shelves_menu(wh)),
        ("6", "Yükləmə rampaları         [StaticArray]", lambda: docks_menu(wh)),
        ("7", "Hesabatlar və sorğular    [BST]", lambda: reports_menu(wh)),
        ("8", "Hash cədvəli statistikası [HashTable]", lambda: hash_stats_menu(wh)),
        ("9", "Performans testləri       [Benchmark]", benchmarks_menu),
    )
    try:
        while True:
            dashboard(wh)
            header("ƏSAS MENYU")
            for key, text, _ in handlers:
                print("  {0}. {1}".format(key, text))
            print("  0. Çıxış")
            choice = ask("\n  Seçiminiz: ")
            if choice == "0":
                break
            for key, _, handler in handlers:
                if key == choice:
                    handler()
                    break
            else:
                print("  ! Yanlış seçim, 0–9 arası rəqəm daxil edin.")
    except ExitApp:
        print()
    print("  Sağ olun! Proqram başa çatdı.")


if __name__ == "__main__":
    main()
