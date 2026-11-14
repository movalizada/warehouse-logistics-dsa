"""
Anbar və Logistika xidmət qatı (biznes məntiqi).

Hər data strukturu konkret bir problemi həll edir:

* ``DynamicArray``      — əsas məhsul kataloqu (daxil olma ardıcıllığı ilə)
* ``StaticArray``       — sabit sayda fiziki yükləmə rampası
* ``HashTable``         — SKU → Product ani axtarış indeksi
* ``BinarySearchTree``  — qiymət və stok miqdarı indeksləri (sıralı hesabat, aralıq sorğu)
* ``Stack``             — Undo (əməliyyatı geri qaytarma) tarixçəsi
* ``Queue``             — adi sifarişlərin qəbul növbəsi (FIFO)
* ``Deque``             — VIP/təcili göndəriş xətti (öndən VIP, arxadan adi)
* ``SinglyLinkedList``  — birtərəfli çatdırılma marşrutu
* ``DoublyLinkedList``  — irəli/geri rəf yoxlaması naviqasiyası
"""

from src.models.order import Order
from src.models.product import Product
from src.models.shelf import Shelf
from src.structures.arrays import ArrayOverflowError, DynamicArray, StaticArray
from src.structures.bst import BinarySearchTree
from src.structures.hash_table import HashTable
from src.structures.linear_adts import Deque, EmptyStructureError, Queue, Stack
from src.structures.linked_lists import DoublyLinkedList, SinglyLinkedList

_MAX_STR = "\U0010ffff"


class WarehouseError(Exception):
    """İstifadəçiyə göstəriləcək biznes xətası."""


class Action:
    """Undo stack-də saxlanılan bir inventar əməliyyatı."""

    __slots__ = ("kind", "sku", "product", "old_price", "old_quantity", "description")

    ADD = "ƏLAVƏ"
    DELETE = "SİLMƏ"
    UPDATE = "YENİLƏMƏ"

    def __init__(self, kind, sku, description, product=None, old_price=None, old_quantity=None):
        self.kind = kind
        self.sku = sku
        self.description = description
        self.product = product
        self.old_price = old_price
        self.old_quantity = old_quantity

    def __str__(self):
        return "[{0}] {1}".format(self.kind, self.description)


class Warehouse:
    DOCK_COUNT = 6

    def __init__(self):
        self.catalog = DynamicArray()
        self.sku_index = HashTable(capacity=16, max_load_factor=0.75)
        self.price_index = BinarySearchTree()
        self.stock_index = BinarySearchTree()
        self.undo_stack = Stack()
        self.order_queue = Queue()
        self.dispatch_line = Deque()
        self.route = SinglyLinkedList()
        self.shelves = DoublyLinkedList()
        self.shelf_cursor = None
        self.docks = StaticArray(self.DOCK_COUNT)
        self.dispatched_count = 0
        self._next_order_id = 1001

    # ================================================================== #
    # MƏHSULLAR (DynamicArray + HashTable + BST)
    # ================================================================== #
    def _index_product(self, product):
        self.price_index.insert((product.price, product.sku), product)
        self.stock_index.insert((product.quantity, product.sku), product)

    def _unindex_product(self, product):
        self.price_index.delete((product.price, product.sku))
        self.stock_index.delete((product.quantity, product.sku))

    def add_product(self, sku, name, price, quantity, record=True):
        sku = sku.strip().upper()
        if self.sku_index.contains(sku):
            raise WarehouseError("SKU '{0}' artıq mövcuddur.".format(sku))
        try:
            product = Product(sku, name.strip(), price, quantity)
        except ValueError as exc:
            raise WarehouseError(str(exc))
        self._insert_product(product)
        if record:
            self.undo_stack.push(Action(Action.ADD, sku, "'{0}' ({1}) əlavə edildi".format(product.name, sku)))
        return product

    def _insert_product(self, product):
        self.catalog.append(product)
        self.sku_index.put(product.sku, product)
        self._index_product(product)

    def get_product(self, sku):
        return self.sku_index.get(sku.strip().upper())

    def require_product(self, sku):
        product = self.get_product(sku)
        if product is None:
            raise WarehouseError("SKU '{0}' tapılmadı.".format(sku.strip().upper()))
        return product

    def remove_product(self, sku, record=True):
        product = self.require_product(sku)
        self.sku_index.remove(product.sku)
        index = self.catalog.index_where(lambda p: p.sku == product.sku)
        self.catalog.delete(index)
        self._unindex_product(product)
        if record:
            self.undo_stack.push(Action(Action.DELETE, product.sku,
                                        "'{0}' ({1}) silindi".format(product.name, product.sku),
                                        product=product))
        return product

    def update_product(self, sku, price=None, quantity=None, record=True, reason=None):
        product = self.require_product(sku)
        if price is not None and price < 0:
            raise WarehouseError("Qiymət mənfi ola bilməz.")
        if quantity is not None and quantity < 0:
            raise WarehouseError("Miqdar mənfi ola bilməz.")
        old_price, old_qty = product.price, product.quantity
        if price is not None and float(price) != old_price:
            self.price_index.delete((old_price, product.sku))
            product.price = float(price)
            self.price_index.insert((product.price, product.sku), product)
        if quantity is not None and int(quantity) != old_qty:
            self.stock_index.delete((old_qty, product.sku))
            product.quantity = int(quantity)
            self.stock_index.insert((product.quantity, product.sku), product)
        if record:
            text = reason or "{0}: qiymət {1:.2f}→{2:.2f}, miqdar {3}→{4}".format(
                product.sku, old_price, product.price, old_qty, product.quantity)
            self.undo_stack.push(Action(Action.UPDATE, product.sku, text,
                                        old_price=old_price, old_quantity=old_qty))
        return product

    def products_by_price(self):
        for _, product in self.price_index.in_order():
            yield product

    def products_in_price_range(self, low, high):
        for _, product in self.price_index.range_query((low, ""), (high, _MAX_STR)):
            yield product

    def products_in_stock_range(self, low, high):
        for _, product in self.stock_index.range_query((low, ""), (high, _MAX_STR)):
            yield product

    def total_inventory_value(self):
        total = 0.0
        for product in self.catalog:
            total += product.total_value()
        return total

    # ================================================================== #
    # UNDO (Stack)
    # ================================================================== #
    def undo(self):
        """Son inventar əməliyyatını geri qaytarır. O(1) + əməliyyatın öz qiyməti."""
        try:
            action = self.undo_stack.pop()
        except EmptyStructureError:
            raise WarehouseError("Geri qaytarılacaq əməliyyat yoxdur.")
        if action.kind == Action.ADD:
            self.remove_product(action.sku, record=False)
        elif action.kind == Action.DELETE:
            self._insert_product(action.product)
        else:
            self.update_product(action.sku, price=action.old_price,
                                quantity=action.old_quantity, record=False)
        return action

    # ================================================================== #
    # SİFARİŞLƏR (Queue + Deque)
    # ================================================================== #
    def create_order(self, customer, sku, quantity, vip=False):
        product = self.require_product(sku)
        if quantity <= 0:
            raise WarehouseError("Sifariş miqdarı müsbət olmalıdır.")
        order = Order(self._next_order_id, customer.strip() or "Naməlum", product.sku, quantity, vip)
        self._next_order_id += 1
        if vip:
            order.status = "Göndəriş xəttində"
            self.dispatch_line.add_front(order)  # VIP — öndən
        else:
            self.order_queue.enqueue(order)      # adi — FIFO növbəyə
        return order

    def process_next_order(self):
        """Növbədəki ilk adi sifarişi göndəriş xəttinin sonuna keçirir."""
        try:
            order = self.order_queue.dequeue()
        except EmptyStructureError:
            raise WarehouseError("Adi sifariş növbəsi boşdur.")
        order.status = "Göndəriş xəttində"
        self.dispatch_line.add_rear(order)
        return order

    def dispatch_next(self):
        """Göndəriş xəttinin önündəki sifarişi yola salır və stoku azaldır.

        Qaytarır: ``(order, uğurlu_mu)``.
        """
        try:
            order = self.dispatch_line.remove_front()
        except EmptyStructureError:
            raise WarehouseError("Göndəriş xətti boşdur.")
        product = self.get_product(order.sku)
        if product is None or product.quantity < order.quantity:
            order.status = "Ləğv edildi (stok çatışmır)"
            return order, False
        self.update_product(order.sku, quantity=product.quantity - order.quantity,
                            reason="Sifariş #{0} göndərildi: {1} −{2} əd.".format(
                                order.order_id, order.sku, order.quantity))
        order.status = "Göndərildi"
        self.dispatched_count += 1
        return order, True

    def cancel_front(self):
        try:
            order = self.dispatch_line.remove_front()
        except EmptyStructureError:
            raise WarehouseError("Göndəriş xətti boşdur.")
        order.status = "Ləğv edildi"
        return order

    def cancel_rear(self):
        try:
            order = self.dispatch_line.remove_rear()
        except EmptyStructureError:
            raise WarehouseError("Göndəriş xətti boşdur.")
        order.status = "Ləğv edildi"
        return order

    def cancel_by_id(self, order_id):
        order = self.dispatch_line.remove_where(lambda o: o.order_id == order_id)
        if order is None:
            raise WarehouseError("#{0} nömrəli sifariş göndəriş xəttində tapılmadı.".format(order_id))
        order.status = "Ləğv edildi"
        return order

    # ================================================================== #
    # ÇATDIRILMA MARŞRUTU (SinglyLinkedList)
    # ================================================================== #
    def add_checkpoint(self, name, at_start=False):
        name = name.strip()
        if not name:
            raise WarehouseError("Nöqtənin adı boş ola bilməz.")
        if at_start:
            self.route.push_front(name)
        else:
            self.route.push_back(name)

    def arrive_next_checkpoint(self):
        try:
            return self.route.pop_front()
        except EmptyStructureError:
            raise WarehouseError("Marşrut tamamlanıb — nöqtə qalmayıb.")

    def remove_checkpoint(self, name):
        target = name.strip().lower()
        removed = self.route.remove_where(lambda n: n.lower() == target)
        if removed is None:
            raise WarehouseError("'{0}' marşrutda tapılmadı.".format(name.strip()))
        return removed

    # ================================================================== #
    # RƏF NAVİQASİYASI (DoublyLinkedList)
    # ================================================================== #
    def add_shelf(self, code, category):
        code = code.strip().upper()
        if not code:
            raise WarehouseError("Rəf kodu boş ola bilməz.")
        if self.shelves.find_node(lambda s: s.code == code) is not None:
            raise WarehouseError("'{0}' rəfi artıq mövcuddur.".format(code))
        node = self.shelves.push_back(Shelf(code, category.strip() or "Ümumi"))
        if self.shelf_cursor is None:
            self.shelf_cursor = node
        return node.data

    def current_shelf(self):
        if self.shelf_cursor is None:
            raise WarehouseError("Rəf siyahısı boşdur.")
        return self.shelf_cursor.data

    def move_forward(self):
        self.current_shelf()
        if self.shelf_cursor.next is None:
            raise WarehouseError("Siz artıq sonuncu rəfdəsiniz.")
        self.shelf_cursor = self.shelf_cursor.next
        return self.shelf_cursor.data

    def move_backward(self):
        self.current_shelf()
        if self.shelf_cursor.prev is None:
            raise WarehouseError("Siz artıq birinci rəfdəsiniz.")
        self.shelf_cursor = self.shelf_cursor.prev
        return self.shelf_cursor.data

    def go_first_shelf(self):
        self.current_shelf()
        self.shelf_cursor = self.shelves.head
        return self.shelf_cursor.data

    def go_last_shelf(self):
        self.current_shelf()
        self.shelf_cursor = self.shelves.tail
        return self.shelf_cursor.data

    def inspect_current(self, note=""):
        shelf = self.current_shelf()
        shelf.inspected = True
        shelf.note = note.strip()
        return shelf

    def remove_current_shelf(self):
        """Cari rəfi O(1)-də silir; kursor növbəti (yoxdursa əvvəlki) rəfə keçir."""
        node = self.shelf_cursor
        if node is None:
            raise WarehouseError("Rəf siyahısı boşdur.")
        new_cursor = node.next if node.next is not None else node.prev
        removed = self.shelves.remove_node(node)
        self.shelf_cursor = new_cursor
        return removed

    def shelf_position(self):
        """Kursorun 1-dən başlayan mövqeyi."""
        position = 0
        node = self.shelves.head
        while node is not None:
            position += 1
            if node is self.shelf_cursor:
                return position
            node = node.next
        return 0

    # ================================================================== #
    # YÜKLƏMƏ RAMPALARI (StaticArray)
    # ================================================================== #
    def dock_truck(self, plate):
        plate = plate.strip().upper()
        if not plate:
            raise WarehouseError("Nömrə nişanı boş ola bilməz.")
        if self.docks.search(plate) != -1:
            raise WarehouseError("{0} artıq rampadadır.".format(plate))
        try:
            self.docks.append(plate)
        except ArrayOverflowError:
            raise WarehouseError(
                "Bütün {0} rampa doludur! Statik massiv genişlənə bilmir — "
                "əvvəlcə bir maşını yola salın.".format(self.DOCK_COUNT))
        return len(self.docks)

    def release_truck(self, dock_number):
        if dock_number < 1 or dock_number > len(self.docks):
            raise WarehouseError("Rampa nömrəsi 1..{0} aralığında olmalıdır.".format(len(self.docks)))
        return self.docks.delete(dock_number - 1)

    # ================================================================== #
    # NÜMUNƏ MƏLUMATLAR
    # ================================================================== #
    def seed_sample_data(self):
        products = (
            ("ELK-1001", "Noutbuk Lenovo IdeaPad 5", 1450.00, 24),
            ("ELK-1002", "Smartfon Samsung Galaxy A55", 899.00, 40),
            ("ELK-1003", "Simsiz qulaqlıq JBL Tune", 129.90, 75),
            ("ELK-1004", "Monitor Dell 27\" 4K", 780.00, 12),
            ("ELK-1005", "USB-C şarj cihazı 65W", 45.50, 150),
            ("MEB-2001", "Ofis kreslosu ergonomik", 320.00, 18),
            ("MEB-2002", "Yazı masası (palıd)", 410.00, 9),
            ("MEB-2003", "Kitab rəfi 5 qatlı", 155.00, 22),
            ("MƏT-3001", "Düyü Basmati 5 kq", 18.40, 300),
            ("MƏT-3002", "Azərçay qara çay 500 q", 7.20, 520),
            ("MƏT-3003", "Zeytun yağı 1 L", 21.90, 140),
            ("MƏT-3004", "Qəhvə dənələri 1 kq", 34.00, 65),
            ("TİK-4001", "Sement M500 50 kq", 9.80, 800),
            ("TİK-4002", "Laminat döşəmə (m²)", 16.50, 1200),
            ("TİK-4003", "Elektrik dreli Bosch", 189.00, 30),
            ("MƏİ-5001", "Paltaryuyan maşın LG 8 kq", 1120.00, 7),
            ("MƏİ-5002", "Soyuducu Beko No-Frost", 1340.00, 5),
            ("MƏİ-5003", "Tozsoran Philips", 265.00, 16),
            ("GEY-6001", "Qış gödəkçəsi (kişi)", 145.00, 48),
            ("GEY-6002", "İdman ayaqqabısı", 98.00, 3),
        )
        for sku, name, price, qty in products:
            self.add_product(sku, name, price, qty, record=False)

        for code, category in (("A-01", "Elektronika"), ("A-02", "Elektronika"),
                               ("B-01", "Mebel"), ("C-01", "Ərzaq"),
                               ("C-02", "Ərzaq"), ("D-01", "Tikinti materialları"),
                               ("E-01", "Məişət texnikası"), ("F-01", "Geyim")):
            self.add_shelf(code, category)

        for point in ("Mərkəzi anbar (Bakı, Binəqədi)", "Sumqayıt paylama mərkəzi",
                      "Quba filialı", "Qusar mağazası", "Xaçmaz təhvil məntəqəsi"):
            self.add_checkpoint(point)

        for plate in ("10-AB-123", "90-KL-456"):
            self.dock_truck(plate)

        self.create_order("Bravo Supermarket", "MƏT-3002", 100)
        self.create_order("Kontakt Home", "ELK-1002", 5)
        self.create_order("Ali & Nino", "MEB-2003", 2)
        self.create_order("Baku Electronics", "ELK-1001", 3)
        self.process_next_order()
        self.create_order("ADA Universiteti", "ELK-1004", 4, vip=True)

        self.undo_stack.clear()  # başlanğıc məlumatlar geri qaytarılmamalıdır
