"""Anbar rəfi modeli (rəf yoxlaması naviqasiyası üçün)."""


class Shelf:
    __slots__ = ("code", "category", "inspected", "note")

    def __init__(self, code, category):
        self.code = code
        self.category = category
        self.inspected = False
        self.note = ""

    def __str__(self):
        status = "✔ yoxlanılıb" if self.inspected else "✘ yoxlanılmayıb"
        text = "{0} ({1}) — {2}".format(self.code, self.category, status)
        if self.note:
            text += " | Qeyd: " + self.note
        return text
