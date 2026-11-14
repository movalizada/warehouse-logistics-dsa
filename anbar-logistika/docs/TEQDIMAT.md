# Təqdimat Mətni və İzahlar

**Layihə:** Anbar və Logistika İdarəetmə Sistemi
**Fənn:** Müasir data strukturları və alqoritmləri

---

## 0. Təqdimatın planı (təxminən 10–12 dəqiqə)

| # | Slayd / Bölmə | Vaxt | Əsas fikir |
|---|---|---|---|
| 1 | Problem və tətbiqin təsviri | 1 dəq | Anbarda ani axtarış, sıralı hesabat, sifariş növbəsi, marşrut və naviqasiya lazımdır |
| 2 | Arxitektura: 9 struktur, 9 funksiya | 1.5 dəq | Hər struktur konkret biznes probleminə uyğun seçilib |
| 3 | Canlı demo | 3 dəq | Bölmə 5-dəki ssenari |
| 4 | Massivlər: statik vs. dinamik | 1.5 dəq | Amortizasiyalı O(1) |
| 5 | Əlaqəli siyahılar | 1 dəq | `prev` göstəricisinin qiyməti və faydası |
| 6 | Hash cədvəli | 1.5 dəq | Zəncirləmə, yük əmsalı |
| 7 | BST eksperimenti | 1.5 dəq | Sıralı giriş: hündürlük O(log n)-dən O(n)-ə |
| 8 | Nəticə | 0.5 dəq | Doğru struktur performansı onlarla, hətta minlərlə dəfə dəyişir |

**Giriş üçün nümunə mətn:**
> «Hörmətli müəllim, bizim layihəmiz anbar və logistika şirkəti üçün konsol tətbiqidir. Biz kursda
> öyrəndiyimiz bütün əsas data strukturlarını Python-un hazır `list` və `dict` tiplərindən istifadə
> etmədən, sıfırdan yazdıq. Hər strukturu da real bir problemi həll etmək üçün tətbiqə yerləşdirdik.
> Məqsədimiz təkcə strukturları yazmaq deyildi. Hər seçimin niyə doğru olduğunu ölçmələrlə sübut
> etmək istədik.»

---

## 1. Data strukturu seçimlərinin əsaslandırılması

### 1.1 Dinamik massiv: məhsul kataloqu
Kataloqa məhsullar daim əlavə olunur və onların sayı əvvəlcədən məlum deyil. Dinamik massiv
amortizasiyalı O(1) ilə sona əlavə edir, indeksə görə isə O(1) giriş verir. Elementlər yaddaşda
ardıcıl yerləşir. Bu, bütün kataloqu çap etmək və ümumi dəyəri hesablamaq kimi tam keçidləri
keş baxımından səmərəli edir.
Kataloqda axtarış xəttidir (O(n)). Ona görə SKU ilə axtarış hash cədvəlinə həvalə olunub.

### 1.2 Statik massiv: yükləmə rampaları
Anbarın fiziki olaraq 6 rampası var. Bu say proqram işləyərkən dəyişə bilməz. Statik massiv bu
real məhdudiyyəti dəqiq modelləşdirir. Yeddinci maşın gəldikdə struktur `ArrayOverflowError`
qaldırır və sistem «bütün rampalar doludur» mesajını göstərir. Dinamik massiv səhvən yeddinci
«virtual» rampa yaradardı.

### 1.3 Hash cədvəli (zəncirləmə): SKU indeksi
Anbarın ən tez-tez etdiyi əməliyyat budur: «bu kodlu məhsul hardadır, neçə ədəd var?» Hash cədvəli
axtarış, yeniləmə və silməni orta halda O(1)-də edir. Məhsul sayı 20-dən 20 000-ə qalxsa belə,
axtarış vaxtı praktik olaraq dəyişmir. Toqquşmaları zəncirləmə ilə həll edirik. Kova dolsa belə
cədvəl sıradan çıxmır, sadəcə zəncir uzanır. Yük əmsalı 0.75-i keçəndə cədvəl avtomatik genişlənir.

### 1.4 İkili axtarış ağacı: qiymət və stok indeksləri
Hash cədvəli sıranı saxlamır. «50–200 AZN arası məhsullar» və ya «stoku 10-dan az olanlar» kimi
suallara cavab vermək üçün hash cədvəlində bütün elementləri yoxlamaq lazımdır (O(n)). BST-nin
in-order gəzintisi isə elementləri avtomatik sıralı verir. Aralıq sorğusu lazımsız alt ağacları
budayır və O(h + k) zamanda işləyir. Burada h ağacın hündürlüyü, k isə nəticədəki element
sayıdır. Açar kimi `(qiymət, SKU)` cütü götürülüb. Bu, eyni qiymətli məhsulların itməsinin
qarşısını alır.

### 1.5 Stack: undo sistemi
«Geri qaytar» əməliyyatı təbiətən LIFO-dur. Həmişə ən son edilən dəyişiklik birinci ləğv olunur.
Stack-in `push` və `pop` əməliyyatları O(1)-dir. LIFO ardıcıllığı tarixçənin ziddiyyətsiz qalmasını
da təmin edir. Məsələn, məhsul əvvəl yenilənib, sonra silinibsə, əvvəl silmə, sonra yeniləmə geri
qaytarılır.

### 1.6 Queue: adi sifariş növbəsi
Ədalətli xidmət prinsipi «ilk gələn, ilk xidmət alır» (FIFO) deməkdir. Növbə `head` və `tail`
göstəriciləri ilə həm əlavəni, həm çıxarmanı O(1)-də edir. Python `list.pop(0)` istifadə etsəydik,
bu O(n) olardı.

### 1.7 Deque: VIP və təcili göndəriş xətti
Göndəriş xəttinə iki tərəfdən daxil olmaq lazımdır. Təcili VIP sifariş öndən (`add_front`), adi
sifariş arxadan (`add_rear`) əlavə olunur. Ləğv edilən sifariş də istənilən ucdan çıxarıla bilər.
Deque bütün bu əməliyyatları O(1)-də edən yeganə xətti strukturdur. Prioritet növbəsi (heap)
burada artıq olardı, çünki cəmi iki prioritet səviyyəmiz var.

### 1.8 Tək əlaqəli siyahı: çatdırılma marşrutu
Yük maşını nəzarət nöqtələrini yalnız bir istiqamətdə keçir. Hər çatılan nöqtə siyahının başından
çıxarılır (`pop_front`, O(1)). Yeni nöqtə sona (`push_back`, O(1)) və ya təcili hallarda başa
əlavə olunur. Geri hərəkət tələb olunmadığı üçün `prev` göstəricisinə ehtiyac yoxdur və hər
düyündə 8 bayt qənaət olunur.

### 1.9 İki əlaqəli siyahı: rəf yoxlaması naviqasiyası
Yoxlama zamanı operator rəflər arasında həm irəli, həm geri gedir. Kursor bir düyünə işarə edir
və `next`/`prev` ilə hər addım O(1)-dir. Cari rəfi silmək də O(1)-dir. Tək əlaqəli siyahıda isə
əvvəlki düyünü tapmaq üçün başdan gəzmək (O(n)) lazım olardı.

---

## 2. Mürəkkəblik müqayisə cədvəli

**İşarələr:** n — element sayı, m — kova sayı, α = n/m — yük əmsalı, h — ağacın hündürlüyü,
k — nəticədəki element sayı.

### 2.1 Zaman mürəkkəbliyi

| Struktur | Əməliyyat | Ən yaxşı | Orta | Ən pis |
|---|---|---|---|---|
| **StaticArray** | get / set | O(1) | O(1) | O(1) |
| | append | O(1) | O(1) | O(1) (dolu: xəta) |
| | insert(i) / delete(i) | O(1) (son) | O(n) | O(n) |
| | search | O(1) | O(n) | O(n) |
| **DynamicArray** | get / set | O(1) | O(1) | O(1) |
| | append | O(1) | O(1) amortizasiyalı | O(n) (resize) |
| | insert(i) / delete(i) | O(1) (son) | O(n) | O(n) |
| | search | O(1) | O(n) | O(n) |
| **SinglyLinkedList** | push_front / push_back | O(1) | O(1) | O(1) |
| | pop_front | O(1) | O(1) | O(1) |
| | pop_back | O(n) | O(n) | O(n) |
| | find / remove | O(1) | O(n) | O(n) |
| | geri gəzinti | O(n) | O(n) | O(n) (+O(n) yaddaş) |
| **DoublyLinkedList** | push / pop (hər iki uc) | O(1) | O(1) | O(1) |
| | remove_node | O(1) | O(1) | O(1) |
| | find | O(1) | O(n) | O(n) |
| | geri gəzinti | O(n) | O(n) | O(n) |
| **Stack** | push / pop / peek | O(1) | O(1) | O(1) |
| **Queue** | enqueue / dequeue / peek | O(1) | O(1) | O(1) |
| **Deque** | add/remove front/rear | O(1) | O(1) | O(1) |
| | remove_where (ID ilə ləğv) | O(1) | O(n) | O(n) |
| **HashTable** | put / get / remove | O(1) | O(1 + α) | O(n) |
| | rehash | O(n + m) | O(n + m) | O(n + m) |
| **BST** | insert / search / delete | O(1) | O(log n) | O(n) |
| | min / max | O(1) | O(log n) | O(n) |
| | in_order | O(n) | O(n) | O(n) |
| | range_query | O(h + k) | O(log n + k) | O(n) |
| | get_height | O(n) | O(n) | O(n) |

### 2.2 Yaddaş mürəkkəbliyi

| Struktur | Yaddaş | Qeyd |
|---|---|---|
| StaticArray | O(capacity) | Yaradılan anda tam ayrılır |
| DynamicArray | O(n) | Tutum ≤ 2n, yəni boş yer ən çox 50 % |
| SinglyLinkedList | O(n) | Düyün: data + next (48 B) |
| DoublyLinkedList | O(n) | Düyün: data + next + prev (56 B, +16.7 %) |
| Stack / Queue | O(n) | Tək göstəricili düyünlər |
| Deque | O(n) | İki göstəricili düyünlər |
| HashTable | O(n + m) | m kova + n zəncir düyünü |
| BST | O(n) | Düyün: key, value, left, right |

---

## 3. Əsas analitik nəticələr

### 3.1 Dinamik massiv: niyə append amortizasiyalı O(1)-dir?

Massiv dolduqda yeni blok (`capacity * 2`) ayrılır və bütün elementlər köçürülür. Bu bir
əməliyyat O(n)-dir. Lakin belə hallar çox nadir baş verir.

**Cəmləmə (aggregate) metodu.** Boş massivə n element əlavə edək (başlanğıc tutum 1):

* Hər elementin öz yazılışı: **n** əməliyyat.
* Genişlənmə köçürmələri 1, 2, 4, 8, …, 2^k ölçülərində baş verir, burada 2^k < n.
  Cəmi: 1 + 2 + 4 + … + 2^k = 2^(k+1) − 1 < **2n**.
* Ümumi xərc < n + 2n = **3n**, yəni bir əməliyyat üçün ortalama xərc < 3. Bu, O(1) deməkdir.

**Hesab (accounting) metodu ilə intuisiya.** Hər `append`-ə 3 «sikkə» ödəyirik. Bir sikkə
elementin öz yazılışına, ikisi isə «əmanətə» gedir. Massiv ikiqat böyüyəndə köçürmə xərcini son
yarıda yığılan əmanət tam ödəyir.

**Ölçmə ilə sübut (Cədvəl 1–2).** 50 000 element üçün cəmi 16 genişlənmə baş verdi (≈ log₂ n).
Bir `append`-in orta vaxtı n = 1 000, 10 000 və 50 000 üçün təxminən eyni qaldı (~0.4–0.6 µs).
Statik massivlə fərq sabit əmsaldır (~2×) və n-dən asılı deyil.

**Niyə məhz ikiqat artırırıq?** Tutumu sabit miqdarda (məs. +10) artırsaq, köçürmələrin cəmi
n²/20 olar. Onda append O(n)-ə çevrilər. Həndəsi artım (×2) isə köçürmə cəmini həndəsi sıraya
çevirir və bu cəm 2n ilə məhdudlaşır.

### 3.2 Tək vs. iki əlaqəli siyahı: qarşılıqlı güzəşt

| | Singly | Doubly |
|---|---|---|
| Düyün başına yaddaş | 48 B | 56 B (**+8 B, +16.7 %**) |
| Sondan silmə | **O(n)**: `tail`-dən əvvəlki düyünü tapmaq üçün başdan gəzmək lazımdır | **O(1)**: `tail.prev` birbaşa məlumdur |
| Məlum düyünü silmək | O(n) | O(1) |
| Geri gəzinti | O(n) vaxt + O(n) köməkçi Stack | O(n) vaxt, O(1) əlavə yaddaş |
| Kodun sadəliyi | Daha sadə, hər əməliyyatda 1 göstərici | 2 göstərici, səhv ehtimalı daha yüksək |

**Ölçmə (Cədvəl 3–4).** n = 50 000 olduqda sondan silmə singly-də ~1.1 ms, doubly-də ~0.4 µs
çəkdi. Bu, təxminən **2900 dəfə** fərq deməkdir. Fərq n ilə xətti böyüyür: n = 1 000-də 70×,
n = 10 000-də 700×. Bunun qarşılığında 50 000 düyünlük siyahıda doubly cəmi ~390 KB əlavə yaddaş
istifadə edir.

**Nəticə.** Yalnız bir istiqamətdə hərəkət varsa (marşrut, FIFO), singly kifayətdir və yaddaşa
qənaət edir. İki istiqamətli hərəkət və ya ixtiyari düyünün tez silinməsi lazımdırsa (rəf
naviqasiyası, Deque, LRU keş), `prev` göstəricisinə sərf olunan yaddaş özünü doğruldur.

### 3.3 Zəncirləmə toqquşmaları necə həll edir, yük əmsalı nəyə təsir edir?

**Toqquşma** iki fərqli açarın eyni kova indeksinə düşməsidir. m kova və n > m açar olduqda
göyərçin yuvası prinsipinə görə toqquşma qaçılmazdır.

**Zəncirləmə.** Hər kova bir əlaqəli siyahıdır. Eyni indeksə düşən açarlar həmin siyahıya
əlavə olunur. Axtarış zamanı əvvəl kova O(1)-də tapılır, sonra yalnız həmin qısa zəncir gəzilir.
Açıq ünvanlamadan fərqli olaraq, burada cədvəl heç vaxt «dolmur». Silmə də sadədir, çünki xüsusi
«silinib» işarəsi (tombstone) lazım deyil.

**Hash funksiyamız.** Funksiya iki addımdan ibarətdir:
1. Polinomial (Horner) hash: `h = (h·31 + kod) mod (2³¹ − 1)`. Bu addım simvolların sırasını
   nəzərə alır, ona görə «AB» ≠ «BA».
2. `fmix32` qarışdırma addımı (XOR və vurma). Bu addım ardıcıl SKU-ların
   (`SKU-000001`, `SKU-000002`, …) klasterləşməsini aradan qaldırır.

Cədvəl 6-da ölçülən toqquşma sayları ideal təsadüfi hash-in nəzəri gözləntisi
`n − m·(1 − e^(−n/m))` ilə praktik olaraq üst-üstə düşür (məs. α = 1 üçün 3 697 və 3 677).

**Yük əmsalı α = n/m.** Bu, bir kovaya düşən orta element sayıdır.
* Uğursuz axtarış (açar yoxdur) orta hesabla bütün zənciri gəzir: **1 + α** addım.
* Uğurlu axtarış zəncirin təxminən yarısını gəzir: **1 + α/2** addım.
* α sabit saxlanılarsa, axtarış O(1) qalır. α → n olarsa (m = 1), cədvəl əlaqəli siyahıya
  çevrilir və axtarış O(n) olur.

**Ölçmə (Cədvəl 6).** α = 0.5–1 olduqda ən uzun zəncir cəmi 6–8 element idi. α = 99 olduqda bu
rəqəm 124-ə çatdı və axtarış yavaşladı. Ona görə tətbiqdəki cədvəl α > 0.75 olduqda kova sayını
ikiqat artırır və bütün açarları yenidən hash-ləyir (rehash). Bu, dinamik massivdəki kimi
amortizasiyalı O(1) xərcdir.

### 3.4 Sıralı verilənlər BST-ni niyə məhv edir?

**Mexanizm.** BST-də hər yeni açar kökdən başlayaraq «kiçikdirsə sola, böyükdürsə sağa» qaydası
ilə yerləşdirilir. Açarlar artan sıra ilə (1, 2, 3, …, n) gəlirsə:
* 1 kök olur.
* 2 > 1, ona görə 1-in sağ uşağı olur.
* 3 > 1 və 3 > 2, ona görə 2-nin sağ uşağı olur.
* …
* Hər yeni açar indiyə qədərki ən böyük açardan böyükdür və həmişə **ən sağdakı düyünün sağına**
  düşür.

Nəticədə heç bir düyünün sol uşağı olmur. Ağac sağa əyilmiş **xətti zəncirə**, yəni mahiyyətcə
əlaqəli siyahıya çevrilir:

```
Təsadüfi sıra (balansa yaxın)        Sıralı sıra (əyilmiş)
            50                        1
          /    \                       \
        25      75                      2
       /  \    /  \                      \
     12   37  62   88                     3
                                           \
   hündürlük ≈ log₂ n                       ...   hündürlük = n
```

**Riyazi təhlil.**
* Ən pis halda hündürlük **h = n**. Axtarış, əlavə və silmə əməliyyatları O(h) olduğu üçün
  hamısı **O(n)**-ə pisləşir.
* Ağacı qurmaq üçün i-ci açar i − 1 müqayisə tələb edir. Cəmi n(n − 1)/2 müqayisə lazımdır, yəni
  qurulma O(n log n)-dən **O(n²)**-ə pisləşir.
* Sıralı ağacda uğurlu axtarışın orta müqayisə sayı (n + 1)/2-dir. n = 2000 üçün bu **1000.5**
  edir. Eksperimentdə dəqiq bu rəqəm alındı.
* Təsadüfi sıra ilə qurulan ağacda orta müqayisə sayı nəzəri olaraq 2(1 + 1/n)·Hₙ − 3 ≈ 1.39·log₂ n
  düsturu ilə hesablanır (Hₙ harmonik ədəddir). n = 2000 üçün bu ≈ 13.4 edir. Ölçmədə **13.1**
  alındı.

**Eksperimentin nəticəsi (Cədvəl 5, n = 2000).**

| | Təsadüfi | Sıralı |
|---|---|---|
| Hündürlük | 24 | 2000 (83 dəfə hündür) |
| Orta müqayisə | 13.1 | 1000.5 |
| Orta axtarış vaxtı | ~0.7 µs | ~46 µs (~65 dəfə yavaş) |
| Qurulma vaxtı | ~1.7 ms | ~81 ms (~48 dəfə yavaş) |

**Praktik əhəmiyyəti.** Real anbarda məhsullar çox vaxt artan SKU nömrəsi və ya artan qiymətlə
idxal olunur. Belə verilənlər sadə BST üçün ən pis haldır.

**Həll yolları:**
1. **Özünü balanslaşdıran ağaclar.** AVL və ya Qırmızı-Qara ağac fırlanmalar (rotation)
   vasitəsilə hündürlüyü həmişə O(log n) saxlayır.
2. **Daxil etmədən əvvəl qarışdırmaq.** Fisher–Yates qarışdırması gözlənilən hündürlüyü O(log n)
   edir.
3. **Treap və ya Splay ağacı.** Bunlar ehtimal və ya amortizasiyalı balans təmin edir.

Layihədə BST əməliyyatları **iterativ** yazılıb. Rekursiv versiya 2000 hündürlüklü əyilmiş ağacda
Python-un rekursiya limitini (≈1000) aşaraq `RecursionError` ilə çökərdi. Bu, ən pis halın
praktikada nə qədər real olduğunu göstərən əlavə nümunədir.

---

## 4. Ümumi nəticə

> «Eyni məsələ fərqli data strukturları ilə həll olunanda performans onlarla, hətta minlərlə dəfə
> fərqlənə bilər: sondan silmədə 2900×, sıralı BST-də 65×. Ona görə struktur seçimi
> optimallaşdırma detalı deyil, arxitektura qərarıdır. Layihəmizdə hər strukturu tətbiqin konkret
> əməliyyat profilinə görə seçdik və hər seçimi ölçmələrlə təsdiqlədik.»

---

## 5. Canlı demo ssenarisi (≈ 3 dəqiqə)

1. `python main.py` əmrini işlədin. Başlanğıc panelində sayğaclar görünür.
2. **1 → 2** seçin və `ELK-1001` yazın. SKU hash cədvəlində tapılır və kova nömrəsi göstərilir.
3. **1 → 4** seçin və `ELK-1001`-in qiymətini dəyişin. Sonra **3** seçin və undo ilə dəyişikliyi
   geri qaytarın (Stack).
4. **2** seçin: növbə (Queue) və göndəriş xətti (Deque) göstərilir. **2** ilə VIP sifariş verin
   və onun xəttin önünə düşdüyünü göstərin. **4** ilə sifarişi yola salın və stokun azaldığını
   göstərin. **6** ilə arxadakı sifarişi ləğv edin.
5. **5** seçin. `i`, `i`, `g` daxil edərək rəflər arasında irəli və geri hərəkət edin. **5** ilə
   cari rəfi O(1)-də silin.
6. **6** seçin və ardıcıl 5 maşın əlavə edin. 2 maşın artıq rampadadır, ona görə beşinci əlavədə
   (yeddinci maşın) statik massivin daşma xətası görünür.
7. **7 → 2** seçin və 10–50 AZN aralığını daxil edin (BST range query). **7 → 3** ilə az qalan
   stok hesabatını göstərin.
8. **8** seçin: toqquşmalar, yük əmsalı və kovaların vizual paylanması görünür.
9. **9 → 3** seçin: BST eksperimentində hündürlüklər 24 və 2000 alınır. Vaxt imkan verirsə,
   **9 → 1** ilə massiv testini də göstərin.

---

## 6. Ehtimal olunan suallar və cavablar

**S: Niyə Python `list` istifadə etmədiniz?**
C: `list` özü dinamik massivdir. Onu istifadə etsəydik, öyrənməli olduğumuz mexanizm (yaddaş
ayırma, köçürmə, genişlənmə) gizli qalardı. `ctypes.py_object` massivi C səviyyəsində sabit ölçülü
ardıcıl göstərici bloku ayırır və heç vaxt özbaşına böyümür. Bu, statik massivin dəqiq modelidir.

**S: Statik massivdə `pop` bəzən dinamikdən yavaş görünür. Niyə?**
C: Hər iki əməliyyat O(1)-dir və eyni kodla işləyir. Nanosaniyələr səviyyəsindəki fərq ölçmə
küyüdür (keş, zibil yığan, ölçmə ardıcıllığı). Asimptotik meyl, yəni n-dən asılı olmaması, hər iki
massivdə eynidir.

**S: Hash cədvəlində ən pis hal nə vaxt baş verir?**
C: Bütün açarlar eyni kovaya düşəndə. Bu, ya pis hash funksiyası, ya da məqsədli hücum
(hash flooding) nəticəsində olur. Onda axtarış O(n)-dir. Yaxşı qarışdırma funksiyası və
genişlənmə bunun ehtimalını praktik olaraq sıfıra endirir.

**S: BST əvəzinə məhsulları dinamik massivdə sıralayıb binar axtarış etmək olmazdımı?**
C: Axtarış O(log n) olardı. Lakin hər yeni məhsul və ya qiymət dəyişikliyi sıranı qorumaq üçün
elementləri sürüşdürməyi tələb edərdi (O(n)). BST əlavə və silməni orta halda O(log n)-də edir.

**S: Niyə Deque-də prioritet növbəsi (heap) yox?**
C: Cəmi iki prioritet səviyyəmiz var: VIP və adi. Deque hər ikisini O(1)-də idarə edir. Heap isə
O(log n) xərc tələb edərdi və eyni prioritetli sifarişlərin FIFO sırasını qorumazdı.

**S: Undo stack-in ölçüsü məhduddurmu?**
C: Hazırda məhdud deyil, yaddaş O(k)-dır (k əməliyyat sayıdır). Real sistemdə son N əməliyyatı
saxlamaq üçün dairəvi bufer (ring buffer) və ya Deque istifadə olunardı. Köhnə əməliyyatlar
`remove_rear` ilə atılardı.
