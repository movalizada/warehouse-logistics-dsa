"""Sifariş məlumat modeli."""


class Order:
    """Müştəri sifarişi.

    Statuslar: ``Növbədə`` → ``Göndəriş xəttində`` → ``Göndərildi``
    və ya ``Ləğv edildi``.
    """

    __slots__ = ("order_id", "customer", "sku", "quantity", "vip", "status")

    def __init__(self, order_id, customer, sku, quantity, vip=False):
        if quantity <= 0:
            raise ValueError("Sifariş miqdarı müsbət olmalıdır.")
        self.order_id = order_id
        self.customer = customer
        self.sku = sku
        self.quantity = quantity
        self.vip = vip
        self.status = "Növbədə"

    def label(self):
        return "VIP" if self.vip else "Adi"

    def __str__(self):
        return "#{0} [{1}] {2} — {3} x{4} ({5})".format(
            self.order_id, self.label(), self.customer, self.sku,
            self.quantity, self.status)
