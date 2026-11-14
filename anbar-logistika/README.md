# Anbar və Logistika İdarəetmə Sistemi

**Kurs layihəsi:** «Müasir data strukturları və alqoritmləri»
**Dil:** Python 3.8+ (yalnız standart kitabxana: `ctypes`, `time`, `random`, `math`, `sys`)

Bu layihə anbar və logistika şirkəti üçün konsol tətbiqidir. Tətbiqdəki hər funksiya
**sıfırdan yazılmış** bir data strukturu ilə işləyir. Əsas strukturlarda Python-un hazır
`list`, `dict` və `collections.deque` tipləri **istifadə olunmur**. Massivlər
`ctypes.py_object` ilə ayrılan ardıcıl yaddaş blokları üzərində qurulub. Digər strukturlar
xüsusi düyün (node) göstəriciləri ilə yazılıb.

---

## 1. Tez başlanğıc

```bash
git clone <repo-url>
cd anbar-logistika
python main.py                                  # interaktiv menyu
python -m src.benchmarks.performance            # bütün benchmark-lar (~4–8 s)
python -m unittest discover -s tests -v         # 22 vahid test
```

Heç bir xarici paket tələb olunmur. Proqram açılan kimi 20 məhsul, 8 rəf, 5 marşrut nöqtəsi,
2 yük maşını və bir neçə sifarişlə doldurulur, ona görə hər funksiyanı dərhal yoxlamaq olar.

---

## 2. Layihənin quruluşu

```
anbar-logistika/
├── main.py                        # Azərbaycan dilində interaktiv CLI
├── README.md
├── docs/
│   └── TEQDIMAT.md                # Təqdimat mətni və nəzəri izahlar
├── src/
│   ├── models/
│   │   ├── product.py             # Product (sku, name, price, quantity)
│   │   ├── order.py               # Order (sifariş)
│   │   └── shelf.py               # Shelf (rəf)
│   ├── structures/
│   │   ├── arrays.py              # StaticArray, DynamicArray (ctypes)
│   │   ├── linked_lists.py        # SinglyLinkedList, DoublyLinkedList
│   │   ├── linear_adts.py         # Stack, Queue, Deque
│   │   ├── hash_table.py          # HashTable (zəncirləmə)
│   │   └── bst.py                 # BinarySearchTree
│   ├── services/
│   │   └── warehouse.py           # Biznes məntiqi: strukturların inteqrasiyası
│   ├── benchmarks/
│   │   └── performance.py         # Avtomatlaşdırılmış performans testləri
│   └── utils/
│       └── table.py               # ASCII cədvəl çapı
└── tests/
    └── test_structures.py         # unittest
```

---

## 3. Arxitektura: hansı struktur nə iş görür

| Struktur | Fayl | Tətbiqdəki rolu | Menyu |
|---|---|---|---|
| `DynamicArray` | `arrays.py` | Əsas məhsul kataloqu (daxil olma sırası ilə) | 1 |
| `StaticArray` | `arrays.py` | 6 fiziki yükləmə rampası (sabit tutum, daşma xətası) | 6 |
| `HashTable` | `hash_table.py` | SKU → məhsul: ani axtarış, yeniləmə, silmə | 1, 8 |
| `BinarySearchTree` ×2 | `bst.py` | Qiymət və stok indeksləri: sıralı hesabat, aralıq sorğuları | 7 |
| `Stack` | `linear_adts.py` | Undo: son inventar dəyişikliyini geri qaytarmaq | 3 |
| `Queue` | `linear_adts.py` | Adi sifarişlərin FIFO növbəsi | 2 |
| `Deque` | `linear_adts.py` | Göndəriş xətti: VIP öndən, adi sifarişlər arxadan; hər iki ucdan ləğv | 2 |
| `SinglyLinkedList` | `linked_lists.py` | Birtərəfli çatdırılma marşrutu | 4 |
| `DoublyLinkedList` | `linked_lists.py` | Rəf yoxlaması: irəli/geri naviqasiya, cari rəfi O(1)-də silmə | 5 |

**Məlumat axını (sifariş):**
`Yeni adi sifariş → Queue (enqueue) → emal → Deque (add_rear) → yola salma (remove_front) → stok azalır → Undo Stack-ə yazılır`
VIP sifariş birbaşa `Deque.add_front` ilə xəttin önünə düşür.

**Məhsul əməliyyatı** bir anda dörd strukturu yeniləyir: `DynamicArray` (kataloq),
`HashTable` (SKU indeksi), qiymət `BST`-si və stok `BST`-si. BST açarı `(qiymət, SKU)`
cütüdür. Bu, eyni qiymətli məhsulların bir-birini əvəz etməsinin qarşısını alır.

Bütün BST əməliyyatları **iterativdir**. Rekursiv yazılsaydı, sıralı verilənlərlə qurulan
2000 hündürlüklü ağac Python-un rekursiya limitini aşardı.

---

## 4. Nəticələrin xülasəsi

Aşağıdakı rəqəmlər bir ölçmə nümunəsidir (Python 3.13, Linux). Vaxtlar maşından asılı olaraq
dəyişir, amma nisbətlər və asimptotik meyllər sabit qalır.

### 4.1 Statik vs. Dinamik massiv (bir əməliyyatın orta vaxtı)

| n | Əməliyyat | StaticArray | DynamicArray |
|---|---|---|---|
| 50 000 | Sona əlavə (append) | ~0.34 µs | ~0.64 µs (16 genişlənmə daxil) |
| 50 000 | Əvvələ əlavə (insert 0) | ~11.5 ms | ~14.6 ms |
| 50 000 | Əvvəldən silmə | ~11.2 ms | ~11.5 ms |
| 50 000 | Sondan silmə (pop) | < 1 µs | < 1 µs |
| 50 000 | Xətti axtarış | ~2.8 ms | ~2.6 ms |

* `append` n-dən asılı deyil: dinamik massivdə də amortizasiyalı O(1)-dir.
* Əvvələ əlavə və silmə n 10 dəfə artdıqda təxminən 10 dəfə yavaşlayır: O(n).

### 4.2 Tək vs. İki əlaqəli siyahı

| n | Əməliyyat | Singly | Doubly |
|---|---|---|---|
| 50 000 | Sondan silmə | ~1.1 ms (O(n)) | ~0.38 µs (O(1)), **~2900× sürətli** |
| 50 000 | Geri gəzinti | ~15.8 ms (köməkçi Stack) | ~2.0 ms |
| — | Düyün ölçüsü | 48 B | 56 B (**+16.7 %** yaddaş) |

### 4.3 BST: təsadüfi vs. sıralı (n = 2000)

| Metrik | Təsadüfi | Sıralı | İdeal |
|---|---|---|---|
| Hündürlük | 24 | **2000** | 11 |
| Orta müqayisə sayı | 13.1 | **1000.5** | ≈ 10 |
| Orta axtarış vaxtı | ~0.7 µs | ~46 µs (**~65× yavaş**) | — |

### 4.4 Hash cədvəli (n = 10 000, sabit kova sayı)

| α | Ölçülən toqquşma | Nəzəri gözlənti | Ən uzun zəncir |
|---|---|---|---|
| 0.5 | 2 129 | 2 130 | 6 |
| 1.0 | 3 697 | 3 677 | 8 |
| 5.0 | 8 015 | 8 011 | 15 |
| 99 | 9 899 | 9 899 | 124 |

Ölçülən toqquşma sayları ideal hash düsturu `n − m·(1 − e^(−n/m))` ilə üst-üstə düşür.
Deməli, xüsusi hash funksiyası açarları kovalara bərabər paylayır.

Kiçik α qiymətlərində axtarış vaxtını əsasən sətir hash-inin hesablanması müəyyən edir
(10 simvol). Ona görə α = 0.5 ilə α = 5 arasında vaxt fərqi azdır. Böyük α qiymətlərində
(≈ 100) isə zəncir boyunca gəzmək üstünlük təşkil edir və axtarış nəzərəçarpacaq dərəcədə
yavaşlayır.

Ətraflı nəzəri izahlar və təqdimat mətni: **[`docs/TEQDIMAT.md`](docs/TEQDIMAT.md)**.

---

## 5. Mürəkkəblik cədvəli (qısa)

| Struktur | Giriş | Axtarış | Əlavə | Silmə | Yaddaş |
|---|---|---|---|---|---|
| StaticArray | O(1) | O(n) | O(1) son / O(n) orta | O(1) son / O(n) | O(capacity) |
| DynamicArray | O(1) | O(n) | O(1)* son / O(n) | O(1) son / O(n) | O(n) |
| SinglyLinkedList | O(n) | O(n) | O(1) baş/son | O(1) baş, **O(n) son** | O(n) |
| DoublyLinkedList | O(n) | O(n) | O(1) baş/son | **O(1) baş/son/düyün** | O(n) (+prev) |
| Stack / Queue / Deque | — | — | O(1) | O(1) | O(n) |
| HashTable | — | O(1)** | O(1)** | O(1)** | O(n + m) |
| BST | — | O(log n)*** | O(log n)*** | O(log n)*** | O(n) |

\* amortizasiyalı; \*\* orta hal, ən pis O(n); \*\*\* orta hal, ən pis (sıralı giriş) O(n).
