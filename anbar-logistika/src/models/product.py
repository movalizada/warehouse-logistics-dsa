"""Məhsul məlumat modeli."""


class Product:
    """Anbardakı bir məhsul.

    Atributlar:
        sku      — unikal stok kodu (məs. ``ELK-1001``)
        name     — məhsulun adı
        price    — vahid qiyməti (AZN)
        quantity — anbardakı miqdar (ədəd)
    """

    __slots__ = ("sku", "name", "price", "quantity")

    def __init__(self, sku, name, price, quantity):
        if not sku:
            raise ValueError("SKU boş ola bilməz.")
        if price < 0:
            raise ValueError("Qiymət mənfi ola bilməz.")
        if quantity < 0:
            raise ValueError("Miqdar mənfi ola bilməz.")
        self.sku = sku
        self.name = name
        self.price = float(price)
        self.quantity = int(quantity)

    def copy(self):
        return Product(self.sku, self.name, self.price, self.quantity)

    def total_value(self):
        return self.price * self.quantity

    def __eq__(self, other):
        return isinstance(other, Product) and self.sku == other.sku

    def __hash__(self):
        return hash(self.sku)

    def __repr__(self):
        return "Product({0!r}, {1!r}, {2:.2f}, {3})".format(
            self.sku, self.name, self.price, self.quantity)

    def __str__(self):
        return "{0} | {1} | {2:.2f} AZN | {3} əd.".format(
            self.sku, self.name, self.price, self.quantity)
