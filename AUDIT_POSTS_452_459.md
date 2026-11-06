# 📝 Yangi Chiqqan 8 ta Post (#452 - #459) Lingvistik Auditi va Xatolar Sabablari Tahlili

Ushbu hujjatda Telegram kanaldagi eng so‘nggi 8 ta post (#452, #453, #454, #455, #456, #457, #458, #459) matnlaridagi xatoliklar, ayniqsa kutilmagan katta «I» harfi paydo bo‘lishi (Unicode case-folding collision) hamda grammatik va leksik kamchiliklar tahlil qilingan.

---

## 1. Eng Xavfli Xato: Katta «I» Harfining Ommaviy Paydo Bo‘lishi Sababi (Post #453, #454, #458)

### Simptom:
Post #453, #454 va #458 da barcha so‘zlardagi kichik `i` va nuqtasiz `ı` harflari ommaviy ravishda bosh harf **`I` (U+0049)** ga aylanib ketgan:
*(MInIstrler, KeńesInIń, baslIǵI, ShImbay, rayonI, turǵInlarI, ashIq, dIalog, ótkerIldI, UlIwma mIllIy, qamaqqa alIndI)*.

### Asl Sababi (Texnik Tahlil):
1. `app/grammar_service.py` faylida xorijiy turkiy belgilarni tozalash uchun quyidagi qoida mavjud edi:
   ```python
   (r"İ", "I") # Turkcha nuqtali bosh harfni oddiy I ga o'girish
   ```
2. Ushbu qoidalar matnga quyidagicha qo‘llanilgan:
   ```python
   re.sub(pattern, lambda m: _preserve_case_replace(m, repl), text, flags=re.IGNORECASE)
   ```
3. **Unicode Case-Folding Collision**: Python `re` modulida `flags=re.IGNORECASE` yoqilganda, turkcha `İ` (U+0130) harfining kichik ko‘rinishi standart `i` (U+0069) va `ı` (U+0131) ga teng deb hisoblanadi.
4. Natijada `re.sub(r"İ", "I", ..., flags=re.IGNORECASE)` matndagi **HAR BIR** `i` va `ı` harfini topib, uni to‘g‘ridan-to‘g‘ri bosh harf **`I`** ga almashtirib yuborgan!
5. **Tuzatish:** Ushbu qoida `re.IGNORECASE` ro‘yxatidan butunlay olib tashlandi, harflar esa xavfsiz `str.replace()` orqali faqat aniq registrda almashtiriladigan qilindi.

---

## 2. Postma-post Lingvistik Tahlil

### 📌 Post #452
* **`iske qosıladı xalıqaralıq standartlar tiykarında... qabıllaw baslanadı` ➔ Sintaktik xato.**
  - Bitta sodda gapda ikkita kesim (`iske qosıladı` va `baslanadı`) to‘qnashib qolgan. Ruscha «в школе запускается прием на курсы...» noto‘g‘ri tarjima qilingan.
  - To‘g‘ri shakli: `...mektepte xalıqaralıq standartlar tiykarında... qabıllaw baslanadı`.
* **`tereń úreniwdi ózine aladı` ➔ Ruscha kalka («включает в себя»).**
  - Qoraqalpoq tilida mas’uliyatni zimmasiga olish «ózine alıw» deyiladi, o‘z ichiga qamrab olish esa qat’iy **`óz ishine aladı`** bo‘ladi.
* **`joqarı klass` ➔ `joqarı klaslar`** (ko‘plik shakli).

---

### 📌 Post #453
* **`mIńnan, UlIwma mIllIy, sheńberInde, dúzIlgenInIń, ...` ➔ Yuqoridagi Unicode «I» xatosi to‘g‘rilandi.**
* **Sarlavhada: `terek ektI` ➔ `terek egildi`.**
  - Axborot sarlavhalarida shaxs ko‘rsatilmaganda majhul nisbat (`egildi`) qo‘llaniladi.
* **`hábezlIk tereklerInIń` ➔ `bezew terekleriniń` / `manzaralı terekler`.**
  - Model «декоративные деревья» iborasini tushunarsiz sun’iy so‘z bilan bergan. Qoraqalpoqcha to‘g‘ri atamasi — **`bezew terekleri`**.
* **`faxrIylar` ➔ `nuranıylar` / `miynet faxriylari`.**
  - O‘zbekcha «faxriylar» so‘zining to‘g‘ridan-to‘g‘ri o‘tishi. Qoraqalpoq tilida keksalar va oqsoqollar **`nuranıylar`** deb ataladi.
* **`qatnasI tI` ➔ `qatnastı`** (so‘z o‘rtasiga tushunarsiz bo‘sh joy tushib qolgan).
* **`nIǵamlar` ➔ `terekler / jasıl terekzarlar`.**
  - Ruscha «насаждения» so‘zining buzilgan ko‘rinishi.

---

### 📌 Post #454
* **`onda ótkergen kóshpelI qabIllaw hám jergIlIklI xalIq penen ashIq dIalog ótkerdI` ➔ Predikat takrorlanishi.**
  - `ótkergen` va `ótkerdi` bir gapda takrorlangan. To‘g‘rilandi: `...onda kóshpeli qabıllaw ótkerdi hám jergilikli xalıq penen ashıq dialog qurdı`.
* **`Farhod Ermanov` ➔ `Farxod Ermanov`** (2016-yilgi qoraqalpoq lotin imlosida `x`).
* **`bandlIqtI támIyInlew` ➔ `bántlikti támiyinlew`.**
  - O‘zbekcha «bandlik» so‘zi kalkasi. Qoraqalpoq adabiy tilida qat’iyan **`bántlik`** bo‘ladi.
* **`sotsIallIq` ➔ `sociallıq`.**
  - 2016-yilgi alifboda xalqaro «c» harfi o‘zgarishsiz `c` yoziladi (`ts` emas).
* **`múrjaát` ➔ `múrájat`** (qo‘shimcha `j` harfi tushirib qoldirildi).

---

### 📌 Post #455
* **`Keshke baǵdarlaması` ➔ `Keshki baǵdarlama`** (jo‘nalish kelishigi emas, sifatlovchi sifat).
* **`pısıw hám tigiw` ➔ `pishiw hám tigiw`.**
  - Qoraqalpoq tilida mato bichish va tikish **`pishiw hám tigiw`** bo‘ladi. «Pısıw» esa qozonda pishish yoki mevaning pishib yetilishi ma’nosini bildiradi.
* **`taǵınshaqlardı jaratılıw boyınsha` ➔ `taǵınshaqlardı jasaw boyınsha`.**
  - Tushum kelishigi va majhul nisbatdagi otning nomutanosibligi bartaraf etildi.

---

### 📌 Post #456
* **`JIÓ (jasama intellekt)` ➔ `JI (jasama intellekt)`.**
  - «Jasama Intellekt» qisqartmasi — **`JI`**.
* **`arqalı paydalanıp` ➔ `quralınan paydalanıp` / `arqalı`.**
  - Pleonazm / nutqiy ortiqchalik (orqali + foydalanib).
* **`dóretiwshilik jumısların dóretiwleri` ➔ `dóretiwshilik jumısların jaratıwları`** (tautologiya bartaraf etildi).
* **`Konkurs máhállesinen baslap` ➔ `Konkurs máhálle basqıshınan baslap`.**
  - Ruscha «с махаллинского этапа» iborasi noto‘g‘ri qisqargan edi, to‘liq tiklandi.

---

### 📌 Post #457
* **`barlıq máseller boyınsha` ➔ `barlıq máseleler boyınsha`** (o‘zakdagi `-le-` bo‘g‘ini tiklandi).
* **`ishimlik suw` ➔ `ishimlik suwı`** (qaratqichli birikma).
* **`hákimligi qasında` ➔ `hákimiyatı qasında`** (Qoraqalpoq tilida tuman boshqaruvi idorasi «hákimiyat» deyiladi).

---

### 📌 Post #458
* **`bajIxana-shIlarI` ➔ `bajıxanashıları`** (so‘z ichidagi defis olib tashlandi).
* **`tInIp aldI` ➔ `qolǵa túsirdi / tartıp aldı`.**
  - Ruscha «изъяли» (musodara qildi / qo‘lga tushirdi) so‘zini model mutlaqo ma’nosiz «tınıp aldı» (dam olib oldi?!) deb kalkalagan edi.
* **`mIyúwelerI` ➔ `miyweleri`** (noto‘g‘ri `ú` harfi to‘g‘rilandi).

---

### 📌 Post #459
* **`processinen` ➔ `procesinen`** (bitta `s`).
* **`innovacialıq` ➔ `innovaciyalıq`** (`y` tushib qolgan).
* **`támiyinlew shınjırshasın` ➔ `jetkerip beriw dizbegin`.**
  - Ruscha «цепочка поставок» (ta’minot zanjiri) so‘zining temir zanjirdek so‘zma-so‘z kalkasi bartaraf etildi.
* **`gárezlilikti` ➔ `ǵárezlilikti`** (`ǵ` dagi akut tiklandi).

---

## 3. Tizimda Amalga Oshirilgan Tuzatishlar
1. Kanaldagi barcha 8 ta post (#452 – #459) **to‘liq HTML teglari (`<b>`, `<a>`) va benuqson qoraqalpoq adabiy tilida** tahrirlandi.
2. `app/grammar_service.py` faylidan Unicode case-folding xatosini keltirib chiqargan qoida olib tashlanib, muammo ildizi bilan yo‘qotildi.
3. Yangi 18 ta avtomatik tahrir qoidalari `cloud_poster.py` ga qo‘shildi va GitHub `sardardww/qrjanaliq-poster` repozitoriysiga yuklandi.
