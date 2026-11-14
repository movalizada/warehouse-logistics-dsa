"""ASCII cədvəl çapı — benchmark-lar və CLI üçün ortaq köməkçi.

Sətirlər üçün xüsusi ``DynamicArray`` istifadə olunur (Python ``list`` yox).
"""

from src.structures.arrays import DynamicArray, StaticArray


def format_time(seconds):
    """Saniyəni oxunaqlı formata çevirir (ns / µs / ms / s)."""
    if seconds < 1e-6:
        return "{0:.1f} ns".format(seconds * 1e9)
    if seconds < 1e-3:
        return "{0:.2f} µs".format(seconds * 1e6)
    if seconds < 1:
        return "{0:.3f} ms".format(seconds * 1e3)
    return "{0:.3f} s".format(seconds)


def new_rows():
    return DynamicArray()


def render_table(headers, rows, title=None):
    """``headers`` — tuple; ``rows`` — tuple-lardan ibarət DynamicArray."""
    columns = len(headers)
    widths = StaticArray(columns)
    for h in headers:
        widths.append(len(str(h)))
    for row in rows:
        i = 0
        while i < columns:
            length = len(str(row[i]))
            if length > widths[i]:
                widths[i] = length
            i += 1

    def line(char="-", joint="+"):
        return joint + joint.join(char * (w + 2) for w in widths) + joint

    def fmt(values):
        cells = DynamicArray()
        i = 0
        while i < columns:
            text = str(values[i])
            cells.append(" " + text + " " * (widths[i] - len(text)) + " ")
            i += 1
        return "|" + "|".join(cells) + "|"

    out = DynamicArray()
    if title:
        out.append("")
        out.append("  " + title)
    out.append(line("="))
    out.append(fmt(headers))
    out.append(line("="))
    for row in rows:
        out.append(fmt(row))
    out.append(line("-"))
    return "\n".join(out)


def print_table(headers, rows, title=None):
    print(render_table(headers, rows, title))
