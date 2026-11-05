#!/usr/bin/env python3
"""
Qaraqalpaqsha jan'aliqlar (@qaraqalpaqshajanaliqlar) — 24/7 Cloud Automated News Poster
Official 34-Letter Karakalpak Alphabet + Two-Pass Literary Grammar Proofreading + Exact Photo Matching.
"""

from __future__ import annotations

import io
import json
import os
import re
import sys
import time
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any
import urllib.request
from urllib.parse import quote_plus, urljoin

import requests
from bs4 import BeautifulSoup
from google import genai
from google.genai import types
from PIL import Image

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)
HEADERS = {"User-Agent": USER_AGENT, "Accept-Language": "uz,ru;q=0.9,en;q=0.8"}
HISTORY_FILE = Path("posted_history.json")
CYRILLIC_RE = re.compile(r"[\u0400-\u04FF]")
BG_URL_RE = re.compile(r"background-image:url\('([^']+)'\)")

OFFICIAL_KARAKALPAK_ALPHABET_RULES = """
OFFICIAL 34-LETTER KARAKALPAK LATIN ALPHABET (2016 Law — STRICTLY MANDATORY):
1. Aa (а)   | 10. Xx (х)  | 19. Ńń (ң)  | 28. Vv (в)
2. Áá (ә)   | 11. Íı (ы)  | 20. Oo (о)  | 29. Ww (ў)
3. Bb (б)   | 12. Ii (и)  | 21. Óó (ө)  | 30. Yy (й)
4. Dd (д)   | 13. Jj (ж)  | 22. Pp (п)  | 31. Zz (з)
5. Ee (е,э) | 14. Kk (к)  | 23. Rr (р)  | 32. Cc (ц)
6. Ff (ф)   | 15. Qq (қ)  | 24. Ss (с)  | 33. Ch ch (ч)
7. Gg (г)   | 16. Ll (л)  | 25. Tt (т)  | 34. Sh sh (ш, щ)
8. Ǵǵ (ғ)   | 17. Mm (м)  | 26. Uu (у)
9. Hh (ҳ)   | 18. Nn (н)  | 27. Úú (ү)

CRITICAL ORTHOGRAPHY & KARAKALPAK GRAMMAR ENGINE:

1. STRICT MORPHOLOGY & SUFFIX HARMONY:
- ADJECTIVE SUFFIX: In Karakalpak, noun-to-adjective suffix is ALWAYS `-lı / -li`!
  * Write `qáwipli` (NEVER Kazakh `qáwipti`!), `tártipli` (NEVER `tártipti`), `quwatlı` (NEVER `quwattı`), `tájiriybeli`, `tásirli`, `paydalı`, `qolaylı`.
  * Negative adjective: `-sız / -siz` (`qáwipsiz`, `nızamsız`, `paydasız`).
  * Attributive from noun: `-lıq / -lik` (`turmıslıq gaz`, `balalıq`, `jaslıq`).
- CASE SYSTEM (SEPTIKLER):
  * Ataw (Nom): stem
  * Ilik (Gen): `-nıń / -niń` (vowels), `-dıń / -diń` (sonorants: l, r, z, j, w, y), `-tıń / -tiń` (voiceless: p, t, s, k, q, sh, x). ALWAYS ending in `ń`! (e.g. `Prezidenttiń`, `Ministrler Keńesiniń`, `qıstıń`, `respublikanıń`).
  * Barıw (Dat): `-ǵa / -ge` (vowels, voiced), `-qa / -ke` (voiceless: p, t, s, k, q, sh, x). (e.g. `toltırıwǵa`, `shaxslarǵa`, `rayonǵa`, `mektepke`, `támiyinlewge`).
  * Tabıs (Acc): `-nı / -ni` (vowels), `-dı / -di` (voiced), `-tı / -ti` (voiceless). (e.g. `qáwipsizlikti`, `ómirin`, `gazdı`).
  * Orın (Loc): `-da / -de` (vowels, voiced), `-ta / -te` (voiceless). (e.g. `qalasında`, `stanciyalarda`, `mektepte`).
  * Shıǵıs (Abl): `-dan / -den` (vowels, voiced), `-tan / -ten` (voiceless). (e.g. `jolawshılardan`, `qáwip-qáterden`).
  * Kómekshi (Inst): `-menen / -benen / -penen` (e.g. `mashina menen`, `qural menen` — NEVER Uzbek `bilan`!).
- VERBAL FORMS (FEYILLER):
  * Masdar (Infinitive): `-ıw / -iw` (`toltırıw`, `islew`, `engiziw`, `belgilew`, `kóriw` — NEVER Uzbek `-ish / -moq`, NEVER Kazakh `-u / -ü` like `істеу/толтыру`).
  * Passive: `-ıl / -il / -l-` (`belgilendi`, `engizildi`, `tartıldı`, `járiyalandı`).
  * Written/Journalistic Aspect: `-maqta / -mekte` (`ámelge asırılmaqta`, `ótkizilmekte`) or past `-dı / -di` (`júz berdi`, `qaytıs boldı`, `jaratıldı`).
  * Verbal negative: `-baydı / -beydi`, `-paydı / -peydi`, `-maydı / -meydi` (e.g. `ruqsat etilmeydi`, `toltırmaydı`).

2. ZERO KAZAKHISMS (Strictly Forbidden Kazakh Roots & Morphemes):
- Kazakh `qáwipti` -> Karakalpak `qáwipli`
- Kazakh `joba / jobalar` -> Karakalpak `joybar / joybarlar` (project) or `reje` (plan)
- Kazakh `baǵıt / baǵıttalǵan` -> Karakalpak `baǵdar / baǵdarlanǵan` (or `qaratılǵan`)
- Kazakh `orın aldı` -> Karakalpak `júz berdi` or `bolıp ótti`
- Kazakh `múmkindik` -> Karakalpak `múmkinshilik`
- Kazakh `jıynalıs` -> Karakalpak `májilis`
- Kazakh `úkimat` -> Karakalpak `húkimet`
- Kazakh `arıza` -> Karakalpak `arza`
- Kazakh `quwattı` -> Karakalpak `quwatlı`

3. ZERO UZBEKISMS:
- `chunki` -> `sebebi` / `óytkeni`; `uchun` -> `ushın`; `bilan` -> `menen`
- `lekin / ammo` -> `biraq`; `faqat` -> `tek` / `tek ǵana`; `juda` -> `júdá`
- `ham` -> `hám`; `har` -> `hár`; `kerak` -> `kerek` / `tiyis`
- `bo'yicha` -> `boyınsha`; `haqida / to'g'risida` -> `haqqında` / `tuwralı`
- `avto-gaz` -> `avtogaz`; `turmis gaz` -> `turmıslıq gaz`
- `zilzila` -> `jer silkiniwi`; `jonivor / jánivor` -> `janzat / haywan`
- `sayyora` -> `planeta`; `tezyurar` -> `tez júrer`; `ulkan` -> `úlken`
- `iqtidarlı` -> `uqıplı`; `moslasqan` -> `maslasqan`; `ommalastırıw` -> `ǵalabalastırıw`
- `taqdimatı` -> `tanıstırıw máresimi`; `sóxbat` -> `sáwbetlesiw`; `tunda` -> `túnde`
- `ulanbaǵan / ulanǵan` -> `jalǵanbaǵan / jalǵanǵan`
- `dástúr` (when program/initiative) -> `baǵdarlama / baǵdarlaması`
- `so'm` -> `sum`; `tuman` -> `rayon`; `viloyat` -> `wálayat`; `xodim` -> `xızmetker`
- `o'rinbosari` -> `orınbasarı`; `tadbir` -> `ilaj`
- `tanaffus` -> `tánepis`; `saroy` -> `saray`; `bezorilik / bizarılıq` -> `buzaqılıq`
- `kambag'al / kambaǵal` -> `kámbaǵal` (or `jarlı`); `hakam` -> `tóreshi`; `hakamlik` -> `tóreshilik`
- `nazariy` -> `teoriyalıq`; `turar joy` -> `turaq jay`; `jarohat` -> `jaraqat`
- `do'kon` -> `dúkan`; `chuvalchang` -> `shuwalshań`; `uzunlik` -> `uzınlıq`
- `qoida` -> `qaǵıyda` (`qáde` means traditional customs, NOT traffic rules!)
- Suffix `-tadan` with numbers is FORBIDDEN: write `22-den 45-ke` (NEVER `22 tadan 45 tadan`)!
- Infinitive `-moq / -mek` is FORBIDDEN: write `támiyinlew` (NEVER `támiyinlemek`)!
- Suffix harmony: `JIÓ-degi` (NEVER `JIÓ-daǵı`), `uzınlıǵı` (NEVER `uzunlıǵı`), `shiyrinlik` (NEVER `shıyrinlik`).

4. ALPHABET ACCURACY (Official 2016 Latin):
- Letter #32 `Cc` represents `ц`: ALWAYS `Shveycariya` (NEVER `Shveysariya` or `Shveyariya`), `investiciya`, `kompensaciya`, `konstituciya`, `delegaciya`, `associaciya`, `korrupciya`, `informaciya`, `akciya`, `policiya`, `epicentr` (NEVER `epitsentr`), `Savickiy` (NEVER `Savitskiy`).
- Letter #19 `Ńń` represents `ң`: Genitive `-nıń / -niń / -dıń / -diń / -tıń / -tiń` and 2nd-person `-ńız / -ńiz` MUST ALWAYS use `ń`.
- Letter #11 `Íı` (back vowel `ы`) vs #12 `Ii` (front vowel `и`): follow strict vowel harmony! E.g. `gazlastırılmaǵan` (NEVER `gazlespegen`), `qıstıń`, `jılıtıw`, `jaratılǵan`, `xızmetker`, `seksewil` (NEVER `saqsewil`), `puqara` (NEVER `puxara`).
- Letter #29 `Ww` (`ў`): Write `oqıw`, `saylaw`, `paydalanıw`, `qollap-quwatlawǵa`, `aǵza bolıw`, `áwmet`, `máwsim`, `wálayat`, `Awǵanstan`, `qáwipsizlik`.
- ZERO Turkish/old-Uzbek letters (`Ş, ş, Ç, ç, Ğ, ğ, Ö, ö, Ü, ü, İ, o', g', ʻ`). Chinese/foreign `ч` is ALWAYS `#33 Ch ch` (e.g. `Yunchjou`, NEVER `Yunçjou`).
"""

CYR_TO_QQ_LATIN = {
    "А": "A", "а": "a",
    "Ә": "Á", "ә": "á", "Ӓ": "Á", "ӓ": "á",
    "Б": "B", "б": "b",
    "В": "V", "в": "v",
    "Г": "G", "г": "g",
    "Ғ": "Ǵ", "ғ": "ǵ",
    "Д": "D", "д": "d",
    "Е": "E", "е": "e",
    "Ё": "Yo", "ё": "yo",
    "Ж": "J", "ж": "j", "Җ": "J", "җ": "j",
    "З": "Z", "з": "z",
    "И": "I", "и": "i", "І": "Í", "і": "ı",
    "Й": "Y", "й": "y",
    "К": "K", "к": "k",
    "Қ": "Q", "қ": "q",
    "Л": "L", "л": "l",
    "М": "M", "м": "m",
    "Н": "N", "н": "n",
    "Ң": "Ń", "ң": "ń",
    "О": "O", "о": "o",
    "Ө": "Ó", "ө": "ó",
    "П": "P", "п": "p",
    "Р": "R", "р": "r",
    "С": "S", "с": "s",
    "Т": "T", "т": "t",
    "У": "U", "у": "u",
    "Ү": "Ú", "ү": "ú",
    "Ў": "W", "ў": "w",
    "Ф": "F", "ф": "f",
    "Х": "X", "х": "x",
    "Ҳ": "H", "ҳ": "h",
    "Ц": "C", "ц": "c",
    "Ч": "Ch", "ч": "ch",
    "Ш": "Sh", "ш": "sh",
    "Щ": "Sh", "щ": "sh",
    "Ъ": "", "ъ": "", "Ь": "", "ь": "",
    "Ы": "Í", "ы": "ı",
    "Э": "E", "э": "e",
    "Ю": "Yu", "ю": "yu",
    "Я": "Ya", "я": "ya",
    # Non-Karakalpak Turkish diacritics sometimes copied from source channels
    "Ş": "Sh", "ş": "sh",
    "Ç": "Ch", "ç": "ch",
    "Ğ": "Ǵ", "ğ": "ǵ",
    "Ö": "Ó", "ö": "ó",
    "Ü": "Ú", "ü": "ú",
    "İ": "I",
}

AUTO_WORD_FIXES = [
    # 1. Official 2016 Acute Vowels & Consonants (Strict normalization from typewriter apostrophes)
    (r"G['’ʻʼ]", "Ǵ"),
    (r"g['’ʻʼ]", "ǵ"),
    (r"O['’ʻʼ]", "Ó"),
    (r"o['’ʻʼ]", "ó"),
    (r"N['’ʻʼ]", "Ń"),
    (r"n['’ʻʼ]", "ń"),

    # 2. Turkish/foreign letters sometimes output by OCR/translators
    (r"Ş", "Sh"), (r"ş", "sh"),
    (r"Ç", "Ch"), (r"ç", "ch"),
    (r"Ğ", "Ǵ"), (r"ğ", "ǵ"),
    (r"Ö", "Ó"), (r"ö", "ó"),
    (r"Ü", "Ú"), (r"ü", "ú"),
    (r"İ", "I"), (r"ı", "ı"),

    # 3. 2016 Standard Latin: 'c' in international loanwords (replaces obsolete 'ts')
    (r"\bepitsentr", "epicentr"),
    (r"\bEpitsentr", "Epicentr"),
    (r"\bpolitsiya\b", "policiya"),
    (r"\bPolitsiya\b", "Policiya"),
    (r"\bkonstitutsiya\b", "konstituciya"),
    (r"\bKonstitutsiya\b", "Konstituciya"),
    (r"\binvestitsiya\b", "investiciya"),
    (r"\bInvestitsiya\b", "Investiciya"),
    (r"\bkompensatsiya\b", "kompensaciya"),
    (r"\bKompensatsiya\b", "Kompensaciya"),
    (r"\bdelegatsiya\b", "delegaciya"),
    (r"\bDelegatsiya\b", "Delegaciya"),
    (r"\bkorruptsiya\b", "korrupciya"),
    (r"\bKorruptsiya\b", "Korrupciya"),
    (r"\binformatsiya\b", "informaciya"),
    (r"\bInformatsiya\b", "Informaciya"),
    (r"\baktsiya\b", "akciya"),
    (r"\bAktsiya\b", "Akciya"),
    (r"\boperatsiya\b", "operaciya"),
    (r"\bOperatsiya\b", "Operaciya"),
    (r"\borganizatsiya\b", "organizaciya"),
    (r"\bOrganizatsiya\b", "Organizaciya"),
    (r"\bvaksina\b", "vakcina"),
    (r"\bVaksina\b", "Vakcina"),
    (r"\bfederatsiya\b", "federaciya"),
    (r"\bFederatsiya\b", "Federaciya"),
    (r"\baviatsiya\b", "aviaciya"),
    (r"\bAviatsiya\b", "Aviaciya"),
    (r"\bsotsiallıq\b", "sociallıq"),
    (r"\bSotsiallıq\b", "Sociallıq"),
    (r"\bShveysariya\b", "Shveycariya"),
    (r"\bshveysariya\b", "shveycariya"),
    (r"\bSavitskiy\b", "Savickiy"),
    (r"\bYunçjou\b", "Yunchjou"),

    # 4. Standard 2016 Karakalpak Orthography & Spelling normalizations
    (r"\bbuzyw\b", "buzıw"),
    (r"\bBuzyw\b", "Buzıw"),
    (r"\bshirinlikler\b", "shiyrinlikler"),
    (r"\bShirinlikler\b", "Shiyrinlikler"),
    (r"\bshirinlik\b", "shiyrinlik"),
    (r"\bShirinlik\b", "Shiyrinlik"),
    (r"\bshıyrinlikler\b", "shiyrinlikler"),
    (r"\bshıyrinlik\b", "shiyrinlik"),
    (r"\bpuqara\b", "puqara"),
    (r"\bpuxara\b", "puqara"),
    (r"\bPuxara\b", "Puqara"),
    (r"\bpuxaralar\b", "puqaralar"),
    (r"\bPuxaralar\b", "Puqaralar"),
    (r"\bseksewil\b", "seksewil"),
    (r"\bsaqsewil\b", "seksewil"),
    (r"\bSaqsewil\b", "Seksewil"),
    (r"\bturaq jay\b", "turaq jay"),
    (r"\bturar jay\b", "turaq jay"),
    (r"\bTurar jay\b", "Turaq jay"),
    (r"\bnarkodúkon\b", "narkodúkan"),
    (r"\bsıyqırshı\b", "sıyqırshı"),
    (r"\bsıyıqshı\b", "sıyqırshı"),
    (r"\bSıyıqshı\b", "Sıyqırshı"),
    (r"\buzunlıǵı\b", "uzınlıǵı"),
    (r"\bUzunlıǵı\b", "Uzınlıǵı"),
    (r"\bAfǵanstan\b", "Awǵanstan"),
    (r"\bafǵanstan\b", "awǵanstan"),
    (r"\bFárǵona\b", "Ferǵana"),
    (r"\bfárǵona\b", "ferǵana"),
    (r"\bAlat\b", "Álot"),
    (r"\b(m|M)ínnetleme\b", r"\1innetleme"),
    (r"\bpricep\b", "tirkeme"),
    (r"\bPricep\b", "Tirkeme"),
    (r"\bpriceplar\b", "tirkemeler"),
    (r"\bPriceplar\b", "Tirkemeler"),
    (r"\btanaffus\b", "tánepis"),
    (r"\bTanaffus\b", "Tánepis"),
    (r"\btexnogeniyalıq\b", "texnogen"),
    (r"\bTexnogeniyalıq\b", "Texnogen"),

    # 5. Strict Uzbekisms & Kazakhisms (Unambiguous words that are NEVER Karakalpak)
        (r"\bjasand([ıi])\b", "jasama"),
    (r"\bJasand([ıi])\b", "Jasama"),
    (r"\bjasandıq\b", "jasamalıq"),
    (r"\bJasandıq\b", "Jasamalıq"),
    (r"\bjasalma\b", "jasama"),
    (r"\bJasalma\b", "Jasama"),
    (r"\bmayda bezorılıq\b", "mayda buzaqılıq"),
    (r"\bMayda bezorılıq\b", "Mayda buzaqılıq"),
    (r"\bkishi buzaqılıq\b", "mayda buzaqılıq"),
    (r"\bKishi buzaqılıq\b", "Mayda buzaqılıq"),
    (r"\bkishi xuliganlıq\b", "mayda buzaqılıq"),
    (r"\búsaq xuliganlıq\b", "mayda buzaqılıq"),
    (r"\bbezorılıq\b", "buzaqılıq"),
    (r"\bBezorılıq\b", "Buzaqılıq"),
    (r"\bjamoat tártibin\b", "jámiyetlik tártipti"),
    (r"\bJamoat tártibin\b", "Jámiyetlik tártipti"),
    (r"\bjamoat\b", "jámiyetlik"),
    (r"\bJamoat\b", "Jámiyetlik"),
    (r"\b(m|M)ádeniyat saroyı\b", r"\1ádeniyat sarayı"),
    (r"\b(s|S)aroyında\b", r"\1arayında"),
    (r"\b(s|S)aroyda\b", r"\1arayda"),
    (r"\b(s|S)aroyǵa\b", r"\1arayǵa"),
    (r"\b(s|S)aroydıń\b", r"\1araydıń"),
    (r"\b(s|S)aroy\b", r"\1aray"),
    (r"\bmilliy saylandı komanda\b", "terme komanda"),
    (r"\bMilliy saylandı komanda\b", "Terme komanda"),
    (r"\bsaylandı komanda\b", "terme komanda"),
    (r"\bSaylandı komanda\b", "Terme komanda"),
    (r"\btalonshılıq\b", "basqınshılıq"),
    (r"\bTalonshılıq\b", "Basqınshılıq"),
    (r"\bchunki\b", "sebebi"),
    (r"\bChunki\b", "Sebebi"),
    (r"\bammo\b", "biraq"),
    (r"\bAmmo\b", "Biraq"),
    (r"\blekin\b", "biraq"),
    (r"\bLekin\b", "Biraq"),
    (r"\btuman\b", "rayon"),
    (r"\bTuman\b", "Rayon"),
    (r"\bviloyat\b", "wálayat"),
    (r"\bViloyat\b", "Wálayat"),
    (r"\bxodim\b", "xızmetker"),
    (r"\bXodim\b", "Xızmetker"),
    (r"\bo'rinbosari\b", "orınbasarı"),
    (r"\bto'g'risida\b", "tuwralı"),
    (r"\bhaqida\b", "haqqında"),
    (r"\bbo'yicha\b", "boyınsha"),
    (r"\bboʻyicha\b", "boyınsha"),
    (r"\bkambaǵal\b", "kámbaǵal"),
    (r"\bKambaǵal\b", "Kámbaǵal"),
    (r"\bMuxtar elshi\b", "Tolıq huqıqlı elshi"),
    (r"\bmuxtar elshi\b", "tolıq huqıqlı elshi"),
    (r"\borın aldı\b", "júz berdi"),
    (r"\bOrın aldı\b", "Júz berdi"),
    (r"\bteledidar\b", "televizor"),
    (r"\bTeledidar\b", "Televizor"),
    (r"\búkimat\b", "húkimet"),
    (r"\bÚkimat\b", "Húkimet"),
    (r"\bjıynalıs\b", "májilis"),
    (r"\bJıynalıs\b", "Májilis"),
    (r"\bso'm\b", "sum"),
    (r"\bsoʻm\b", "sum"),
]

TELEGRAM_SOURCES = [
    # --- KARAKALPAKSTAN (primary: local official + media + active districts) ---
    ("karakalpakstan", "KarPressa", 24),
    ("karakalpakstan", "kknews_uz", 24),
    ("karakalpakstan", "kkeduuz", 24),
    ("karakalpakstan", "krbajixana", 24),
    ("karakalpakstan", "jaslar_isleri_agentligi", 24),
    ("karakalpakstan", "joqargikenes", 24),
    ("karakalpakstan", "QResMinistrlerKenesi", 24),
    ("karakalpakstan", "karinform", 24),
    ("karakalpakstan", "xaliq_ushin", 24),
    ("karakalpakstan", "xodjeyli_rk", 24),
    ("karakalpakstan", "turtkulhokim_uz", 24),
    ("karakalpakstan", "pressTaqiyatas", 24),
    ("karakalpakstan", "kanlikulnews", 24),
    # --- UZBEKISTAN (primary: news media + official bodies) ---
    ("citizen_uzbekistan", "kunuz", 10),
    ("citizen_uzbekistan", "kunuzru", 10),
    ("citizen_uzbekistan", "gazetauz", 10),
    ("citizen_uzbekistan", "daryo", 10),
    ("citizen_uzbekistan", "repostuz", 10),
    ("citizen_uzbekistan", "qalampir", 10),
    ("citizen_uzbekistan", "uznews", 10),
    ("citizen_uzbekistan", "uzdaily", 10),
    ("citizen_uzbekistan", "zaminuz", 12),
    ("citizen_uzbekistan", "spotuz", 12),
    ("citizen_uzbekistan", "uzbekistan24", 10),
    ("citizen_uzbekistan", "bbcuzbek", 24),
    ("citizen_uzbekistan", "terabaytuz", 24),
    ("citizen_uzbekistan", "itpark_uz", 24),
    ("citizen_uzbekistan", "Press_Secretary_Uz", 10),
    ("citizen_uzbekistan", "uzbprokuratura", 12),
    ("citizen_uzbekistan", "RaqobatGovUz", 12),
    ("citizen_uzbekistan", "iivuz", 10),
    ("citizen_uzbekistan", "mygovuz", 24),
    ("citizen_uzbekistan", "yoshlaragentligi", 24),
    ("citizen_uzbekistan", "uzedu", 24),
    ("citizen_uzbekistan", "uzreport", 12),
    ("citizen_uzbekistan", "sportuz", 12),
    ("citizen_uzbekistan", "fauzbekistan", 12),
    # --- WORLD (primary: international wires, quality media, science & tech) ---
    ("world", "bbcrussian", 8),
    ("world", "dwrussian", 12),
    ("world", "tass_agency", 8),
    ("world", "rian_ru", 8),
    ("world", "rbc_news", 8),
    ("world", "kommersant", 8),
    ("world", "vedomosti", 12),
    ("world", "forbesrussia", 12),
    ("world", "meduzalive", 12),
    ("world", "currenttime", 10),
    ("world", "nexta_live", 8),
    ("world", "ukrainenow", 8),
    ("world", "ukr_pravda", 12),
    ("world", "bbcukrainian", 12),
    ("world", "trtworld", 10),
    ("world", "hindustantimes", 8),
    ("world", "guardian", 10),
    ("world", "france24_en", 10),
    ("world", "nhkworld", 12),
    ("world", "koreatimes", 12),
    ("world", "allafrica", 10),
    ("world_tech", "nature", 24),
    ("world_tech", "nplus1", 24),
    ("world_tech", "scientificrussia", 24),
    ("world_tech", "spacenews", 24),
    ("world_tech", "futurism", 24),
    ("world_tech", "smithsonianmag", 24),
    ("world_tech", "nvidia", 24),
    ("world_tech", "hitech", 12),
    ("world_tech", "nasa_news", 24),
]

# Website / RSS sources (all live-tested 2026-11-04). Format: (category, source_name, rss_url)
RSS_AND_GLOBAL_FEEDS = [
    # --- KARAKALPAKSTAN ---
    ("karakalpakstan", "kknews.uz", "https://kknews.uz/qq/feed"),
    ("karakalpakstan", "Google News", "https://news.google.com/rss/search?q=when:12h+(Qoraqalpog%CA%BBiston+OR+Nukus+OR+Qaraqalpaqstan+OR+Karakalpakstan)&hl=uz&gl=UZ&ceid=UZ:uz"),
    # --- UZBEKISTAN ---
    ("citizen_uzbekistan", "kun.uz", "https://kun.uz/news/rss"),
    ("citizen_uzbekistan", "gazeta.uz", "https://www.gazeta.uz/oz/rss/"),
    ("citizen_uzbekistan", "gazeta.uz", "https://www.gazeta.uz/ru/rss/"),
    ("citizen_uzbekistan", "daryo.uz", "https://daryo.uz/feed"),
    ("citizen_uzbekistan", "uzdaily.uz", "https://uzdaily.uz/rss"),
    ("citizen_uzbekistan", "uza.uz", "https://uza.uz/rss"),
    ("citizen_uzbekistan", "nuz.uz", "https://nuz.uz/feed"),
    ("citizen_uzbekistan", "xabar.uz", "https://xabar.uz/rss"),
    ("citizen_uzbekistan", "spot.uz", "https://spot.uz/rss"),
    ("citizen_uzbekistan", "aniq.uz", "https://aniq.uz/rss"),
    ("citizen_uzbekistan", "zamin.uz", "https://zamin.uz/rss"),
    ("citizen_uzbekistan", "kapital.uz", "https://kapital.uz/feed"),
    ("citizen_uzbekistan", "bbc.com/uzbek", "https://feeds.bbci.co.uk/uzbek/rss.xml"),
    # --- WORLD: BBC ---
    ("world", "bbc.com", "https://feeds.bbci.co.uk/news/world/rss.xml"),
    ("world", "Google News", "https://news.google.com/rss/search?q=when:3h+(site:reuters.com+OR+site:apnews.com)&hl=en-US&gl=US&ceid=US:en"),
    ("world", "bbc.com", "https://feeds.bbci.co.uk/news/world/asia/rss.xml"),
    ("world", "bbc.com", "https://feeds.bbci.co.uk/news/world/europe/rss.xml"),
    ("world", "bbc.com", "https://feeds.bbci.co.uk/news/world/middle_east/rss.xml"),
    ("world", "bbc.com", "https://feeds.bbci.co.uk/news/world/africa/rss.xml"),
    ("world", "bbc.com", "https://feeds.bbci.co.uk/news/world/us_and_canada/rss.xml"),
    ("world", "bbc.com", "https://feeds.bbci.co.uk/news/world/latin_america/rss.xml"),
    ("world", "bbc.com", "https://feeds.bbci.co.uk/news/health/rss.xml"),
    ("world", "bbc.com", "https://feeds.bbci.co.uk/news/business/rss.xml"),
    ("world", "bbc.com/russian", "https://feeds.bbci.co.uk/russian/rss.xml"),
    ("world", "bbc.com/ukrainian", "https://feeds.bbci.co.uk/ukrainian/rss.xml"),
    ("world", "bbc.com/turkce", "https://feeds.bbci.co.uk/turkce/rss.xml"),
    ("world_tech", "bbc.com", "https://feeds.bbci.co.uk/news/technology/rss.xml"),
    ("world_tech", "bbc.com", "https://feeds.bbci.co.uk/news/science_and_environment/rss.xml"),
    # --- WORLD: Guardian ---
    ("world", "theguardian.com", "https://www.theguardian.com/world/rss"),
    ("world", "theguardian.com", "https://www.theguardian.com/environment/rss"),
    ("world", "theguardian.com", "https://www.theguardian.com/world/europe-news/rss"),
    ("world", "theguardian.com", "https://www.theguardian.com/world/asia-pacific/rss"),
    ("world", "theguardian.com", "https://www.theguardian.com/world/middleeast/rss"),
    ("world", "theguardian.com", "https://www.theguardian.com/world/africa/rss"),
    ("world_tech", "theguardian.com", "https://www.theguardian.com/uk/technology/rss"),
    ("world_tech", "theguardian.com", "https://www.theguardian.com/science/rss"),
    # --- WORLD: international broadcasters & wires ---
    ("world", "aljazeera.com", "https://www.aljazeera.com/xml/rss/all.xml"),
    ("world", "france24.com", "https://www.france24.com/en/rss"),
    ("world", "euronews.com", "https://www.euronews.com/rss"),
    ("world", "npr.org", "https://feeds.npr.org/1001/rss.xml"),
    ("world", "npr.org", "https://feeds.npr.org/1004/rss.xml"),
    ("world", "nbcnews.com", "https://feeds.nbcnews.com/nbcnews/public/world"),
    ("world", "abcnews.go.com", "https://abcnews.go.com/abcnews/internationalheadlines"),
    ("world", "abc.net.au", "https://www.abc.net.au/news/feed/51120/rss.xml"),
    ("world", "abc.net.au", "https://www.abc.net.au/news/feed/2942460/rss.xml"),
    ("world", "japantimes.co.jp", "https://www.japantimes.co.jp/feed/"),
    ("world", "scmp.com", "https://www.scmp.com/rss/91/feed"),
    ("world", "scmp.com", "https://www.scmp.com/rss/4/feed"),
    ("world", "straitstimes.com", "https://www.straitstimes.com/news/world/rss.xml"),
    ("world", "straitstimes.com", "https://www.straitstimes.com/news/asia/rss.xml"),
    ("world", "channelnewsasia.com", "https://www.channelnewsasia.com/rssfeeds/8395986"),
    ("world", "thehindu.com", "https://www.thehindu.com/news/international/feeder/default.rss"),
    ("world", "hindustantimes.com", "https://www.hindustantimes.com/feeds/rss/world-news/rssfeed.xml"),
    ("world", "timesofindia.com", "https://timesofindia.indiatimes.com/rssfeeds/296589292.cms"),
    ("world", "indianexpress.com", "https://indianexpress.com/section/world/feed/"),
    ("world", "ndtv.com", "https://feeds.feedburner.com/ndtvnews-world-news"),
    ("world", "dawn.com", "https://www.dawn.com/feeds/home"),
    ("world", "koreatimes.co.kr", "http://www.koreatimes.co.kr/www/rss/world.xml"),
    ("world", "rte.ie", "https://www.rte.ie/news/rss/news-headlines.xml"),
    ("world", "nytimes.com", "https://rss.nytimes.com/services/xml/rss/nyt/World.xml"),
    ("world", "nytimes.com", "https://rss.nytimes.com/services/xml/rss/nyt/Health.xml"),
    ("world", "nytimes.com", "https://rss.nytimes.com/services/xml/rss/nyt/Business.xml"),
    ("world", "latimes.com", "https://www.latimes.com/world-nation/rss2.0.xml"),
    ("world", "foxnews.com", "https://moxie.foxnews.com/google-publisher/world.xml"),
    ("world", "politico.eu", "https://www.politico.eu/feed/"),
    ("world", "ft.com", "https://www.ft.com/world?format=rss"),
    ("world", "bloomberg.com", "https://feeds.bloomberg.com/markets/news.rss"),
    ("world", "meduza.io", "https://meduza.io/rss/all"),
    ("world", "meduza.io/en", "https://meduza.io/rss/en/all"),
    ("world", "kommersant.ru", "https://www.kommersant.ru/RSS/news.xml"),
    ("world", "vedomosti.ru", "https://www.vedomosti.ru/rss/news"),
    ("world", "tass.com", "https://tass.com/rss/v2.xml"),
    ("world", "ria.ru", "https://ria.ru/export/rss2/archive/index.xml"),
    ("world", "interfax.ru", "https://www.interfax.ru/rss.asp"),
    ("world", "themoscowtimes.com", "https://www.themoscowtimes.com/rss/news"),
    ("world", "kyivindependent.com", "https://kyivindependent.com/news-archive/rss/"),
    ("world", "ukrinform.net", "https://www.ukrinform.net/rss/block-lastnews"),
    ("world", "pravda.com.ua", "https://www.pravda.com.ua/rss/"),
    ("world", "unian.net", "https://www.unian.net/rss"),
    ("world", "trthaber.com", "https://www.trthaber.com/sondakika.rss"),
    ("world", "dailysabah.com", "https://www.dailysabah.com/rssFeed/world"),
    ("world", "thenationalnews.com", "https://www.thenationalnews.com/arc/outboundfeeds/rss/?outputType=xml"),
    ("world", "haaretz.com", "https://www.haaretz.com/srv/haaretz-latest-headlines"),
    ("world", "middleeasteye.net", "https://www.middleeasteye.net/rss"),
    ("world", "allafrica.com", "https://allafrica.com/tools/headlines/rdf/latest/headlines.rdf"),
    ("world", "africanews.com", "https://www.africanews.com/feed/rss"),
    ("world", "cgtn.com", "https://www.cgtn.com/subscribe/rss/section/world.xml"),
    ("world", "bangkokpost.com", "https://www.bangkokpost.com/rss/data/topstories.xml"),
    ("world", "rappler.com", "https://www.rappler.com/feed/"),
    ("world", "smh.com.au", "https://www.smh.com.au/rss/world.xml"),
    ("world", "nzherald.co.nz", "https://www.nzherald.co.nz/arc/outboundfeeds/rss/section/world/?outputType=xml"),
    ("world", "stuff.co.nz", "https://www.stuff.co.nz/rss"),
    ("world", "globalnews.ca", "https://globalnews.ca/world/feed/"),
    ("world", "cbc.ca", "https://www.cbc.ca/webfeed/rss/rss-world"),
    ("world", "batimes.com.ar", "https://www.batimes.com.ar/feed"),
    ("world", "lemonde.fr", "https://www.lemonde.fr/en/rss/une.xml"),
    ("world", "spiegel.de", "https://www.spiegel.de/international/index.rss"),
    ("world", "euractiv.com", "https://www.euractiv.com/feed/"),
    ("world", "axios.com", "https://www.axios.com/feeds/feed.rss"),
    ("world", "vox.com", "https://www.vox.com/rss/index.xml"),
    ("world", "theatlantic.com", "https://www.theatlantic.com/feed/all/"),
    ("world", "newyorker.com", "https://www.newyorker.com/feed/everything"),
    ("world", "time.com", "https://time.com/feed/"),
    ("world", "fortune.com", "https://fortune.com/feed/"),
    ("world", "businessinsider.com", "https://www.businessinsider.com/rss"),
    ("world", "cnbc.com", "https://www.cnbc.com/id/100727362/device/rss/rss.html"),
    ("world", "marketwatch.com", "https://www.marketwatch.com/rss/topstories"),
    ("world", "skysports.com", "https://www.skysports.com/rss/12040"),
    ("world", "un.org", "https://news.un.org/feed/subscribe/en/news/all/rss.xml"),
    # --- WORLD: science, space, health & technology (the "wow" stories) ---
    ("world_tech", "sciencedaily.com", "https://www.sciencedaily.com/rss/all.xml"),
    ("world_tech", "phys.org", "https://phys.org/rss-feed/"),
    ("world_tech", "space.com", "https://www.space.com/feeds/all"),
    ("world_tech", "nasa.gov", "https://www.nasa.gov/feed/"),
    ("world_tech", "esa.int", "https://www.esa.int/rssfeed/Our_Activities/Space_News"),
    ("world_tech", "spacenews.com", "https://spacenews.com/feed/"),
    ("world_tech", "sciencealert.com", "https://www.sciencealert.com/feed"),
    ("world_tech", "livescience.com", "https://www.livescience.com/feeds/all"),
    ("world_tech", "popsci.com", "https://www.popsci.com/feed/"),
    ("world_tech", "scientificamerican.com", "https://www.scientificamerican.com/platform/syndication/rss/"),
    ("world_tech", "smithsonianmag.com", "https://www.smithsonianmag.com/rss/latest_articles/"),
    ("world_tech", "interestingengineering.com", "https://interestingengineering.com/feed"),
    ("world_tech", "futurism.com", "https://futurism.com/feed"),
    ("world_tech", "technologyreview.com", "https://www.technologyreview.com/feed/"),
    ("world_tech", "techcrunch.com", "https://techcrunch.com/feed/"),
    ("world_tech", "theverge.com", "https://www.theverge.com/rss/index.xml"),
    ("world_tech", "wired.com", "https://www.wired.com/feed/rss"),
    ("world_tech", "arstechnica.com", "https://arstechnica.com/feed/"),
    ("world_tech", "engadget.com", "https://www.engadget.com/rss.xml"),
    ("world_tech", "cnet.com", "https://www.cnet.com/rss/news/"),
    ("world_tech", "zdnet.com", "https://www.zdnet.com/news/rss.xml"),
    ("world_tech", "techradar.com", "https://www.techradar.com/rss"),
    ("world_tech", "gizmodo.com", "https://gizmodo.com/rss"),
    ("world_tech", "mashable.com", "https://mashable.com/feeds/rss/all"),
    ("world_tech", "theregister.com", "https://www.theregister.com/headlines.atom"),
    ("world_tech", "bleepingcomputer.com", "https://www.bleepingcomputer.com/feed/"),
    ("world_tech", "thehackernews.com", "https://thehackernews.com/feeds/posts/default"),
    ("world_tech", "nytimes.com", "https://rss.nytimes.com/services/xml/rss/nyt/Science.xml"),
    ("world_tech", "nytimes.com", "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml"),
    ("world_tech", "nbcnews.com", "https://feeds.nbcnews.com/nbcnews/public/tech"),
    ("world_tech", "bloomberg.com", "https://feeds.bloomberg.com/technology/news.rss"),
    ("world_tech", "forbes.com", "https://www.forbes.com/innovation/feed2/"),
]

# OPEN-WEB DISCOVERY (NOT a limit — these roam the wider internet for stories the fixed
# lists above may miss). Each query is a Google News search over the last hours.
# Format: (category, label, search_query)
OPEN_WEB_QUERIES = [
    ("karakalpakstan", "open-web", "Qoraqalpog'iston OR Nukus OR Qaraqalpaqstan"),
    ("karakalpakstan", "open-web", "Karakalpakstan OR Каракалпакстан OR Нукус"),
    ("citizen_uzbekistan", "open-web", "O'zbekiston yangi qonun OR qaror OR narx OR jarima"),
    ("citizen_uzbekistan", "open-web", "Узбекистан постановление OR тариф OR штраф OR пособие"),
    ("citizen_uzbekistan", "open-web", "Uzbekistan accident OR fire OR flood OR earthquake"),
    ("citizen_uzbekistan", "open-web", "Узбекистан ДТП OR пожар OR отравление OR задержан"),
    ("world", "open-web", "scientists discover OR \"for the first time\" OR record-breaking"),
    ("world", "open-web", "plane crash OR earthquake OR explosion OR wildfire"),
    ("world", "open-web", "health warning OR outbreak OR recall OR study finds"),
    ("world", "open-web", "company announces OR price hike OR ban OR new rule"),
    ("world", "open-web", "sports tragedy OR record OR transfer OR final"),
    ("world_tech", "open-web", "AI breakthrough OR new chip OR robot OR launch"),
    ("world_tech", "open-web", "scholarship OR grant OR remote job OR free course"),
    ("world_tech", "open-web", "space mission OR rocket OR asteroid OR telescope"),
]


def open_web_feeds() -> list[tuple[str, str, str]]:
    feeds: list[tuple[str, str, str]] = []
    for cat, label, query in OPEN_WEB_QUERIES:
        q = quote_plus(f"when:12h ({query})")
        feeds.append((cat, label, f"https://news.google.com/rss/search?q={q}&hl=en-US&gl=US&ceid=US:en"))
    return feeds

# Smart Free-Tier Quota Routing (Live-Tested against GEMINI_API_KEY):
# - gemini-3.8-flash: 20 req/day Free Tier cap -> reserve STRICTLY 1 call/hour for primary drafting!
# - gemini-3.6-flash / gemini-3.5-flash: High all-day Free Tier quota (10x better Karakalpak than -lite)
# - gemini-3.1-pro-preview / gemini-3-flash-preview / gemini-4-argon: Blocked (limit: 0 / Paid) on Free Tier
DRAFT_MODELS = [
    "gemini-3.8-flash",
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
]
PROOFREAD_MODELS = [
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
]
VISION_MODELS = [
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
]


def normalize_url(u: str) -> str:
    return u.strip().split("?")[0].rstrip("/")


def load_config() -> tuple[str, str, str, int]:
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    gemini_key = os.environ.get("GEMINI_API_KEY", "").strip()
    max_posts = int(os.environ.get("MAX_POSTS", "1"))

    local_cfg = Path("telegram_config.json")
    if (not bot_token or not chat_id) and local_cfg.exists():
        data = json.loads(local_cfg.read_text(encoding="utf-8"))
        bot_token = bot_token or data.get("bot_token", "")
        chat_id = chat_id or data.get("chat_id") or data.get("channel_id", "")

    if not bot_token or not chat_id:
        raise RuntimeError("Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID.")
    if not gemini_key:
        raise RuntimeError("Missing GEMINI_API_KEY secret.")
    return bot_token, chat_id, gemini_key, max(1, min(max_posts, 4))


def http_get(url: str, timeout: int = 20) -> requests.Response | None:
    try:
        resp = requests.get(url, headers=HEADERS, timeout=timeout)
        if resp.status_code == 200:
            return resp
    except Exception as exc:
        print(f"[WARN] GET failed for {url}: {exc}")
    return None


def fetch_existing_channel_posts() -> tuple[list[str], set[str]]:
    """Layer 1: Scrape 2 full pages of @qaraqalpaqshajanaliqlar (~40 live posts = 2+ days) + local cache."""
    recent_summaries: list[str] = []
    seen_urls: set[str] = set()

    if HISTORY_FILE.exists():
        try:
            cached = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
            seen_urls.update(cached.get("urls", []))
            recent_summaries.extend(cached.get("titles", [])[-40:])
        except Exception:
            pass

    def _extract_from_soup(soup: BeautifulSoup) -> tuple[list[str], int | None]:
        page_summaries: list[str] = []
        oldest_id: int | None = None
        for msg in soup.select(".tgme_widget_message"):
            post_attr = msg.get("data-post", "")
            if "/" in post_attr:
                try:
                    pid = int(post_attr.split("/")[-1])
                    if oldest_id is None or pid < oldest_id:
                        oldest_id = pid
                except ValueError:
                    pass
            txt_el = msg.select_one(".tgme_widget_message_text")
            if txt_el:
                txt = txt_el.get_text(" ", strip=True)
                if len(txt) > 30:
                    page_summaries.append(txt[:420])
                for a_tag in txt_el.select("a[href]"):
                    href = a_tag.get("href", "").strip()
                    if href and "t.me/qaraqalpaqshajanaliqlar" not in href:
                        seen_urls.add(normalize_url(href))
        return page_summaries, oldest_id

    resp = http_get("https://t.me/s/qaraqalpaqshajanaliqlar")
    if resp:
        soup1 = BeautifulSoup(resp.text, "html.parser")
        page1_summaries, oldest = _extract_from_soup(soup1)
        if oldest and oldest > 1:
            prev_resp = http_get(f"https://t.me/s/qaraqalpaqshajanaliqlar?before={oldest}")
            if prev_resp:
                prev_summaries, _ = _extract_from_soup(BeautifulSoup(prev_resp.text, "html.parser"))
                recent_summaries.extend(prev_summaries)
        recent_summaries.extend(page1_summaries)

    # Deduplicate summaries while preserving order
    deduped_summaries: list[str] = []
    seen_txt: set[str] = set()
    for s in recent_summaries:
        key = s[:120].lower()
        if key not in seen_txt:
            seen_txt.add(key)
            deduped_summaries.append(s)

    return deduped_summaries[-45:], seen_urls


def scrape_telegram_channel(category: str, channel: str, max_age_hours: int) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    resp = http_get(f"https://t.me/s/{channel}")
    if not resp:
        return items

    cutoff = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)
    soup = BeautifulSoup(resp.text, "html.parser")

    for msg in soup.select(".tgme_widget_message")[-12:]:
        post_id = msg.get("data-post", "")
        if not post_id:
            continue
        post_url = f"https://t.me/{post_id}"

        time_el = msg.select_one("time[datetime]")
        pub_dt = None
        if time_el and time_el.get("datetime"):
            try:
                pub_dt = datetime.fromisoformat(time_el["datetime"].replace("Z", "+00:00"))
            except Exception:
                pub_dt = None
        if pub_dt and pub_dt < cutoff:
            continue

        # Select only the top-level message text (avoid nested duplicate text divs)
        txt_el = msg.select_one(".tgme_widget_message_bubble > .tgme_widget_message_text") or msg.select_one(
            ".tgme_widget_message_text"
        )
        if not txt_el:
            continue
        text = txt_el.get_text("\n", strip=True)
        if len(text) < 60:
            continue

        external_links = []
        for a_tag in txt_el.select("a[href]"):
            href = a_tag.get("href", "").strip()
            if (
                href.startswith("http")
                and channel.lower() not in href.lower()
                and not any(s in href.lower() for s in ("instagram.com", "facebook.com", "fb.com", "youtube.com", "x.com"))
            ):
                external_links.append(href)

        photo_urls = []
        for wrap in msg.select(".tgme_widget_message_photo_wrap"):
            m = BG_URL_RE.search(wrap.get("style", ""))
            if m and m.group(1) not in photo_urls:
                photo_urls.append(m.group(1))

        video_urls = []
        for v_el in msg.select("video.tgme_widget_message_video, video"):
            src = v_el.get("src", "").strip()
            if src and src.startswith("http") and src not in video_urls:
                video_urls.append(src)
        for v_wrap in msg.select(".tgme_widget_message_video_player .tgme_widget_message_video_thumb"):
            m = BG_URL_RE.search(v_wrap.get("style", ""))
            if m and m.group(1) not in photo_urls:
                photo_urls.append(m.group(1))

        primary_doc = next((u for u in external_links if "lex.uz/docs/" in u or "my.gov.uz/" in u), None)
        items.append(
            {
                "category": category,
                "source_name": channel,
                "url": primary_doc or post_url,
                "fallback_post_url": post_url,
                "external_links": external_links[:3],
                "published_at": pub_dt.isoformat() if pub_dt else "",
                "text": text[:1500],
                "photo_urls": photo_urls[:4],
                "video_urls": video_urls[:2],
            }
        )
    return items


def scrape_kknews() -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    resp = http_get("https://kknews.uz/qq/")
    if not resp:
        return items
    soup = BeautifulSoup(resp.text, "html.parser")
    links: list[str] = []
    for a_tag in soup.select("a[href*='/qq/']"):
        href = urljoin("https://kknews.uz", a_tag.get("href", ""))
        if re.search(r"/qq/\d+\.html$", href) and href not in links:
            links.append(href)
        if len(links) >= 5:
            break

    for url in links:
        art = http_get(url)
        if not art:
            continue
        asoup = BeautifulSoup(art.text, "html.parser")
        title_el = asoup.select_one("meta[property='og:title']") or asoup.select_one("h1")
        desc_el = asoup.select_one("meta[property='og:description']")
        img_el = asoup.select_one("meta[property='og:image']")
        body_text = " ".join(
            p.get_text(" ", strip=True) for p in asoup.select("article p, .entry-content p, .post-content p")
        )
        title = (
            title_el.get("content", "").strip()
            if title_el and title_el.has_attr("content")
            else (title_el.get_text(strip=True) if title_el else "")
        )
        desc = desc_el.get("content", "").strip() if desc_el else ""
        full_txt = f"{title}\n{desc}\n{body_text}".strip()
        if len(full_txt) < 80:
            continue
        photos = [img_el["content"].strip()] if img_el and img_el.get("content") else []
        items.append(
            {
                "category": "karakalpakstan",
                "source_name": "kknews.uz",
                "url": url,
                "published_at": datetime.now(timezone.utc).isoformat(),
                "text": full_txt[:1500],
                "photo_urls": photos,
            }
        )
    return items


def scrape_kun_uz() -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for cat, url in [
        ("citizen_uzbekistan", "https://kun.uz/news/list"),
        ("world", "https://kun.uz/news/category/jahon"),
        ("world_tech", "https://kun.uz/news/category/texnologiya"),
    ]:
        resp = http_get(url)
        if not resp:
            continue
        soup = BeautifulSoup(resp.text, "html.parser")
        article_urls: list[str] = []
        for a_tag in soup.select("a[href^='/news/20']"):
            full_url = urljoin("https://kun.uz", a_tag.get("href", ""))
            if full_url not in article_urls:
                article_urls.append(full_url)
            if len(article_urls) >= 4:
                break

        for art_url in article_urls:
            art = http_get(art_url)
            if not art:
                continue
            asoup = BeautifulSoup(art.text, "html.parser")
            t_el = asoup.select_one("meta[property='og:title']")
            d_el = asoup.select_one("meta[property='og:description']")
            i_el = asoup.select_one("meta[property='og:image']")
            p_el = asoup.select_one("meta[property='article:published_time']")
            paragraphs = " ".join(p.get_text(" ", strip=True) for p in asoup.select(".article-body p"))
            title = t_el.get("content", "").strip() if t_el else ""
            desc = d_el.get("content", "").strip() if d_el else ""
            if not title:
                continue
            photos = [i_el["content"].strip()] if i_el and i_el.get("content") else []
            items.append(
                {
                    "category": cat,
                    "source_name": "kun.uz",
                    "url": art_url,
                    "published_at": p_el.get("content", "") if p_el else "",
                    "text": f"{title}\n{desc}\n{paragraphs}"[:1500],
                    "photo_urls": photos,
                }
            )
    return items


def parse_pub_datetime(raw: str) -> datetime | None:
    """Parse RSS/ISO publication dates into aware UTC datetimes (None if unparseable)."""
    raw = (raw or "").strip()
    if not raw:
        return None
    dt: datetime | None = None
    try:
        dt = parsedate_to_datetime(raw)
    except Exception:
        try:
            dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        except Exception:
            return None
    if dt is not None and dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


RSS_MAX_AGE_HOURS = 18
RSS_ITEMS_PER_FEED = 3


def scrape_rss_and_global_feeds(
    feeds: list[tuple[str, str, str]] | None = None,
) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    ns = {"media": "http://search.yahoo.com/mrss/"}
    rss_cutoff = datetime.now(timezone.utc) - timedelta(hours=RSS_MAX_AGE_HOURS)
    for cat, default_src, rss_url in (feeds if feeds is not None else RSS_AND_GLOBAL_FEEDS):
        resp = http_get(rss_url)
        if not resp:
            continue
        try:
            root = ET.fromstring(resp.content)
        except Exception:
            continue
        taken = 0
        entries = root.findall("./channel/item") or root.findall(".//{http://www.w3.org/2005/Atom}entry")
        for item in entries:
            if taken >= RSS_ITEMS_PER_FEED:
                break
            title = (item.findtext("title") or item.findtext("{http://www.w3.org/2005/Atom}title") or "").strip()
            raw_desc = (item.findtext("description") or item.findtext("{http://www.w3.org/2005/Atom}summary") or "").strip()
            desc = BeautifulSoup(raw_desc, "html.parser").get_text(" ", strip=True)
            link = (item.findtext("link") or "").strip()
            if not link:
                atom_link = item.find("{http://www.w3.org/2005/Atom}link")
                link = (atom_link.get("href") if atom_link is not None else "") or ""
            if "bbc.co.uk" in link:
                link = link.split("?")[0].replace("bbc.co.uk", "bbc.com")
            pub = (item.findtext("pubDate") or item.findtext("{http://www.w3.org/2005/Atom}updated") or "").strip()
            pub_dt = parse_pub_datetime(pub)
            if pub_dt and pub_dt < rss_cutoff:
                continue
            src_el = item.find("source")
            src_name = src_el.text.strip() if src_el is not None and src_el.text else default_src

            photos: list[str] = []
            for m_content in item.findall("media:content", ns):
                u = (m_content.get("url") or "").strip()
                if u and u not in photos:
                    photos.append(u)
            thumb = item.find("media:thumbnail", ns)
            if thumb is not None and thumb.get("url"):
                u = thumb.get("url", "").replace("/standard/240/", "/standard/976/")
                if u not in photos:
                    photos.append(u)
            enc = item.find("enclosure")
            if enc is not None and enc.get("url") and "image" in (enc.get("type") or "image"):
                u = enc.get("url", "").strip()
                if u and u not in photos:
                    photos.append(u)

            if title and link:
                taken += 1
                items.append(
                    {
                        "category": cat,
                        "source_name": src_name,
                        "url": link,
                        "published_at": pub_dt.isoformat() if pub_dt else pub,
                        "text": f"{title}\n{desc}"[:1200],
                        "photo_urls": photos[:3],
                    }
                )
    return items


def scrape_all_sources_parallel() -> list[dict[str, Any]]:
    """Scan every Telegram channel + RSS website + open-web query concurrently (fast & fault-tolerant)."""
    tasks: list[Any] = []
    out: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=16) as pool:
        for cat, ch, hrs in TELEGRAM_SOURCES:
            tasks.append(pool.submit(scrape_telegram_channel, cat, ch, hrs))
        for feed in RSS_AND_GLOBAL_FEEDS + open_web_feeds():
            tasks.append(pool.submit(scrape_rss_and_global_feeds, [feed]))
        for t in tasks:
            try:
                out.extend(t.result(timeout=240))
            except Exception as exc:
                print(f"[WARN] A source task failed and was skipped: {exc}")
    return out


def build_balanced_candidate_pool(
    candidates: list[dict[str, Any]], limit: int = 64
) -> list[dict[str, Any]]:
    """Round-robin by category with heavy discouragement of repetitive aggregators (kun.uz, KarPressa, kknews),
    strict commercial ad filtering, and strong boost for authentic primary world, tech, and official gazettes."""
    quotas = {
        "world": 25,
        "world_tech": 18,
        "karakalpakstan": 10,
        "citizen_uzbekistan": 10
    }
    
    # Filter out commercial advertisements
    filtered: list[dict[str, Any]] = []
    for c in candidates:
        txt = c.get("text", "")
        if COMMERCIAL_AD_REGEX.search(txt):
            continue
        filtered.append(c)

    by_cat: dict[str, list[dict[str, Any]]] = {}
    for c in filtered:
        by_cat.setdefault(c.get("category", "world"), []).append(c)

    def sort_key(c: dict[str, Any]) -> float:
        dt = parse_pub_datetime(c.get("published_at", ""))
        score = dt.timestamp() if dt else 0.0
        src = c.get("source_name", "").lower()
        if src in DISCOURAGED_SOURCES or any(d in src for d in ["kun.uz", "kknews", "karpress"]):
            score -= 100000.0  # Heavily penalize overused aggregators
        elif src in AUTHENTIC_SOURCES or any(a in src for a in ["nasa", "nature", "reuters", "bbc", "guardian", "techcrunch", "uza.uz", "xaliq_ushin", "joqargikenes"]):
            score += 50000.0   # Heavily boost primary authentic sources
        return score

    pool: list[dict[str, Any]] = []
    seen_urls: set[str] = set()
    total_discouraged_taken = 0
    MAX_DISCOURAGED_TOTAL = 1  # At most 1 item from discouraged aggregators in the whole pool!

    for cat in ["world", "world_tech", "karakalpakstan", "citizen_uzbekistan"]:
        items = by_cat.get(cat, [])
        items.sort(key=sort_key, reverse=True)
        per_source: dict[str, int] = {}
        taken = 0
        for c in items:
            key = normalize_url(c["url"])
            if key in seen_urls:
                continue
            src = c.get("source_name", "").lower()
            is_discouraged = src in DISCOURAGED_SOURCES or any(d in src for d in ["kun.uz", "kknews", "karpress"])
            if is_discouraged:
                if total_discouraged_taken >= MAX_DISCOURAGED_TOTAL:
                    continue
                if per_source.get(src, 0) >= 1:
                    continue
            else:
                if per_source.get(src, 0) >= 2:
                    continue
            
            seen_urls.add(key)
            per_source[src] = per_source.get(src, 0) + 1
            if is_discouraged:
                total_discouraged_taken += 1
            pool.append(c)
            taken += 1
            if taken >= quotas.get(cat, 10):
                break

    return pool[:limit]


def generate_content_with_fallback(
    client: genai.Client,
    models: list[str],
    contents: Any,
    config: types.GenerateContentConfig,
) -> Any:
    last_err: Exception | None = None
    for idx, model_name in enumerate(models):
        try:
            resp = client.models.generate_content(
                model=model_name,
                contents=contents,
                config=config,
            )
            if not (resp.text or "").strip():
                raise ValueError(f"Empty text response from {model_name}")
            print(f"[INFO] Generated content using model: {model_name}")
            return resp
        except Exception as exc:
            last_err = exc
            print(f"[WARN] Model {model_name} attempt {idx + 1} unavailable ({exc}), trying next...")
            time.sleep(2.5)
    raise RuntimeError(f"All fallback models failed: {last_err}")



DICTIONARY_FILE = Path("qq_dictionary.json")
_QQ_DICT_CACHE: dict[str, dict[str, str]] | None = None


def load_qq_dictionary() -> dict[str, dict[str, str]]:
    global _QQ_DICT_CACHE
    if _QQ_DICT_CACHE is not None:
        return _QQ_DICT_CACHE
    if DICTIONARY_FILE.exists():
        try:
            _QQ_DICT_CACHE = json.loads(DICTIONARY_FILE.read_text(encoding="utf-8"))
            print(f"[DICT] Loaded {len(_QQ_DICT_CACHE)} verified dictionary entries from {DICTIONARY_FILE}")
            return _QQ_DICT_CACHE
        except Exception as exc:
            print(f"[WARN] Failed to load {DICTIONARY_FILE}: {exc}")
    _QQ_DICT_CACHE = {}
    return _QQ_DICT_CACHE



# ======================================================================================
# UZBEK -> KARAKALPAK NEWS TERMINOLOGY BRIDGE (Prevents Uzbekism/Kazakhism leaks)
# ======================================================================================
UZ_TO_QQ_NEWS_BRIDGE: dict[str, str] = {
    # Crime & Law Enforcement
    "talonchilik": "basqınshılıq, tonawshılıq (NEVER talonshılıq)",
    "bosqinchilik": "basqınshılıq",
    "qidiruv": "izlestiriw, qıdırıw (NEVER izertlew)",
    "tezkor-qidiruv": "jedel-qıdırıw, jedel-izlestiriw",
    "tezkor": "jedel",
    "tergov": "tergew",
    "tergovchi": "tergewshi",
    "surishtiruv": "suristiriw",
    "qo'lga olindi": "qolǵa alındı",
    "ushlandi": "ushalandı, qolǵa alındı",
    "qamoqqa olindi": "qamaqqa alındı",
    "hukm": "húkim",
    "sudlandi": "sudlandı",
    "sud": "sud",
    "jinoyat": "jinayat",
    "jinoyatchi": "jinayatshı",
    "jinoiy": "jinayatlıq",
    "jazoga tortildi": "jazaǵa tartıldı",
    "jarima": "járiyma",
    "jarimaga tortildi": "járiyma salındı (NEVER járiymaǵa tartıw)",
    "jarima belgilandi": "járiyma belgilendi",
    "javobgarlik": "juwapkershilik",
    "javobgarlikka tortildi": "juwapkershilikke tartıldı",
    "ma'muriy": "hákimshilik",
    "bezorilik": "bizarılıq (NEVER bezorılıq)",
    "mayda bezorilik": "mayda bizarılıq",
    "tartibbuzarlik": "tártipbuzarlıq",
    "jamoat": "jámiyetlik (NEVER jamoat)",
    "jamoat tartibi": "jámiyetlik tártip",
    "jamoat joylarida": "jámiyetlik orınlarda",
    "deportatsiya": "deportaciya",
    "deportatsiya qilindi": "deportaciya etildi (NEVER deportaciya qılındı)",
    "mamlakatdan chiqarib yuborildi": "mámleketten shıǵarıp jiberildi",
    "qonunbuzarlik": "nızambuzarlıq",
    "qonuniy": "nızamlı",
    "noqonuniy": "nızamsız",
    "taqiqlandi": "qadaǵan etildi",
    "taqiq": "qadaǵan etiw",
    "kamsituvchi": "kemsitiwshi",
    "ramz": "belgi",
    "ramzlar": "belgiler",
    "tashviqot": "úgit-násiyat",

    # Emergencies, Accidents, Disasters
    "favqulodda": "ayrıqsha",
    "favqulodda vaziyat": "ayrıqsha jaǵday",
    "halokat": "halakat",
    "yol-transport hodisasi": "jol-transport hádıysi",
    "avariya": "avariya, hádiyse",
    "hodisa": "hádiyse",
    "yuz berdi": "júz berdi, bolıp ótti (NEVER orın aldı)",
    "vafot etdi": "qaytıs boldı, kóz jumdı (NEVER opat boldı)",
    "halok bo'ldi": "halak boldı",
    "jarohat": "jarahat",
    "jarohatlandi": "jarahatlandı",
    "jarohat olgan": "jarahat alǵan",
    "yong'in": "órt (NEVER pojar)",
    "yong'in xavfsizligi": "órt qáwipsizligi",
    "qutqaruvchi": "qutqarıwshı",
    "qutqarildi": "qutqarıldı",
    "zilzila": "jer silkiniwi (NEVER zilzila)",
    "texnogen": "texnogen (NEVER texnogeniyalıq)",
    "kompensatsiya": "kompensaciya",
    "zarar": "zıyan",
    "xavf": "qáwip",
    "xavfli": "qáwipli (NEVER qáwipti)",
    "xavfsizlik": "qáwipsizlik",
    "gaz balloni": "turmıslıq gaz ballonı (NEVER turmıs gaz)",
    "avtogaz": "avtogaz (NEVER avto-gaz)",

    # Government, Politics & Administration
    "prezident": "Prezident",
    "qaror": "qarar",
    "farmon": "párman",
    "vazirlik": "ministrlik",
    "vazir": "ministr",
    "boshqarma": "basqarma",
    "tashkilot": "shólkem",
    "hokimiyat": "hákimiyat",
    "viloyat": "wálayat (NEVER viloyat)",
    "tuman": "rayon (NEVER tuman)",
    "shahar": "qala",
    "amaldor": "ámeldar",
    "xodim": "xızmetker (NEVER xodim)",
    "orinbosar": "orınbasar (NEVER o'rinbosari)",
    "rahbar": "basshı",
    "bosh vazir": "Bas ministr",
    "tashrif": "sapar",
    "tashrif buyurdi": "sapar etti, keldi (NEVER tashrif buyırdı)",
    "uchrashuv": "ushırasıw",
    "uchrashdi": "ushırastı",
    "muzokara": "kelisiwler, sóylesiwler",
    "kelishuv": "kelisim",
    "shartnoma": "shártnama",
    "yig'ilish": "májilis (NEVER jıynalıs)",
    "majlis": "májilis",
    "tadbir": "ilaj (NEVER tadbir)",
    "tadbirlar": "ilajlar",
    "chora-tadbirlar": "ilajlar",
    "loyiha": "joybar (NEVER joba)",
    "reja": "joybar (loyiha mánisinde), reje (reje mánisinde)",
    "dastur": "baǵdarlama (NEVER dástúr - dástúr degen ádet degeni)",
    "yo'naltirilgan": "baǵdarlanǵan, qaratılǵan (NEVER baǵıtlanǵan)",
    "joriy etildi": "engizildi",
    "qabul qilindi": "qabıl etildi",
    "amalga oshirildi": "ámelge asırıldı",
    "amalga oshirilmoqda": "ámelge asırılmaqta",
    "tashkil etildi": "shólkemlestirildi",
    "belgilandi": "belgilendi",
    "e'lon qilindi": "járiyalandı",

    # Society, Education, Culture & Health
    "shirinliklar": "shıyrinlikler, tatlılıqlar (NEVER shirinlikler)",
    "shirinlik": "shıyrinlik, tatlılıq",
    "folbin": "palker, palshı",
    "sehrgar": "sıyqırshı (NEVER sıyıqshı)",
    "jodugar": "duwaxan, sıyqırshı hayal",
    "psixolog": "psixolog",
    "shifokor": "shıpaker",
    "kasallik": "kesellik",
    "bemor": "nawqas",
    "salomatlik": "densawlıq",
    "talaba": "student",
    "o'quvchi": "oqıwshı",
    "maktab": "mektep",
    "universitet": "universitet",
    "malaka": "mamanlıq",
    "mutaxassis": "qánige",
    "kasb": "kásip",
    "kasbiy": "kásiplik",
    "faoliyat": "is-háreket, jumıs (NEVER iskerlik)",
    "ishchi": "jumısshı",
    "ishsiz": "jumıssız",
    "ish o'rni": "jumıs ornı",
    "yarmarka": "yarmarka",
    "yordam": "járdem",
    "nafaqa": "pension, napaqa",
    "imtiyoz": "jeńillik",

    # Economics & Finance
    "moliya": "finans (NEVER qarjılay)",
    "moliyaviy": "finanslıq",
    "mablag'": "qarjı",
    "narx": "baha",
    "narxlar": "bahalar",
    "qimmat": "qımbat",
    "arzon": "arzan",
    "oshdi": "arttı, ósti",
    "pasaydi": "páseyedi, arzanladı",
    "kamaydi": "azaydı",
    "soliq": "salıq",
    "bojxona": "bajixana",
    "qarz": "qarz, kredit",
    "jamg'arma": "qor",
    "korxona": "kárxana",
    "tadbirkor": "isbilermen",
    "savdo": "sawda",
    "ishlab chiqarish": "islep shıǵarıw",
    "eksport": "eksport",
    "import": "import",
    "yetkazib berish": "jetkerip beriw",
    "ta'minlash": "támiyinlew",
    "sarflandi": "sarplap etildi, jumsaldı",

    # Tech, Science & World
    "sayyora": "planeta (NEVER sayyora)",
    "kosmos": "kosmos",
    "olimlar": "ilimpazlar",
    "tadqiqot": "izertlew, ilimiy jumıs",
    "kashfiyot": "jańalıq, oylap tabıw",
    "sun'iy intellekt": "jasalma intellekt",
    "dron": "dron, ushıwshısız apparat",
    "jonivor": "janzat, haywan (NEVER jonivor, jánivor)",

    # Conjunctions, Particles & Common Words
    "chunki": "sebebi, óytkeni (NEVER chunki)",
    "uchun": "ushın (NEVER uchun)",
    "bilan": "menen (NEVER bilan)",
    "lekin": "biraq (NEVER lekin, ammo)",
    "ammo": "biraq",
    "faqat": "tek, tek ǵana (NEVER faqat)",
    "juda": "júdá (NEVER juda)",
    "ham": "hám (NEVER ham)",
    "har": "hár (NEVER har)",
    "kerak": "kerek, tiyis (NEVER kerak, lozim)",
    "bo'yicha": "boyınsha (NEVER bo'yicha)",
    "haqida": "haqqında, tuwralı (NEVER haqida)",
    "to'g'risida": "tuwralı, haqqında (NEVER to'g'risida)",
    "muhim": "áhmiyetli (NEVER muhim)",
    "asosiy": "tiykarǵı (NEVER asosiy)",
    "umumiy": "ulıwma",
    "birgalikda": "birgelikte",
    "hamkorlikda": "birge islesiwde",
    "natijasida": "nátiyjesinde",
    "sababli": "sebepli",
    "to'g'ri": "durıs, tuwrı",
    "noto'g'ri": "nadurıs, qáte",
    "yangilik": "jańalıq",
    "xabar": "xabar",
    "ma'lumot": "maǵlıwmat",
    "hujjat": "hújjet",
    "dastlabki": "dáslepki",
    "yakuniy": "juwmaqlawshı",
    "hozirgi": "házirgi",
    "kelgusi": "kelesi",
}


def extract_dictionary_glossary_for_text(text: str, limit: int = 50) -> str:
    """Find words in candidate story matching Russian dictionary OR Uzbek-QQ Bridge."""
    text_lower = text.lower()
    found: list[str] = []
    seen = set()

    # 1. Match Uzbek news terminology bridge
    for uz_word, qq_trans in UZ_TO_QQ_NEWS_BRIDGE.items():
        if uz_word in text_lower and uz_word not in seen:
            seen.add(uz_word)
            found.append(f"- [UZ] {uz_word} => [QQ] {qq_trans}")
        if len(found) >= 25:
            break

    # 2. Match Russian Turabaev dictionary
    d = load_qq_dictionary()
    if d:
        ru_words = re.findall(r"[а-яё]{4,}", text_lower)
        for w in ru_words:
            if w in d and w not in seen:
                seen.add(w)
                lat_trans = d[w].get("qq_lat", "")
                if lat_trans and not lat_trans.startswith("sm."):
                    found.append(f"- [RU] {w} => [QQ] {lat_trans}")
            if len(found) >= limit:
                break

    if not found:
        return ""
    joined = "\n".join(found)
    return f"MANDATORY DICTIONARY & TERMINOLOGY GLOSSARY (YOU MUST USE THESE EXACT KARAKALPAK TERMS):\n{joined}"


# ======================================================================================
# STRICT CONTENT SAFETY FILTER: ZERO TOLERANCE FOR RAPE / SEXUAL VIOLENCE
# ======================================================================================
COMMERCIAL_AD_REGEX = re.compile(
    r"(?i)\b(reklama|reklamasi|aksiya|chegirma|skidka|homiylik|hamkorlik\s+asosida|narxi\s+\d+|sotuvda|buyurtma\s+berish|promokod|manzilimiz|telefon:\s*\+?\d|shoshiling|cheklangan\s+miqdorda|arzon\s+narx|dokonimiz|dúkanımız|murojaat\s+uchun)\b"
)

DISCOURAGED_SOURCES = {
    "kun.uz", "kunuz", "kunuzru",
    "kknews.uz", "kknews_uz",
    "karpressa", "karpress"
}

AUTHENTIC_SOURCES = {
    "xaliq_ushin", "joqargikenes", "qresministrlerkenesi", "jaslar_isleri_agentligi",
    "krbajixana", "turtkulhokim_uz", "presstaqiyatas", "kanlikulnews", "xodjeyli_rk",
    "uza.uz", "press_secretary_uz", "uzbprokuratura", "raqobatgovuz", "mygovuz",
    "yoshlaragentligi", "uzedu", "itpark_uz", "spot.uz", "gazeta.uz", "bbc.com/uzbek",
    "reuters", "bbc", "bbc.com", "theguardian", "theguardian.com", "aljazeera", "france24",
    "dw", "euronews", "apnews", "nasa", "nasa.gov", "esa.int", "nature", "space.com",
    "spacenews", "sciencedaily", "phys.org", "sciencealert", "livescience", "techcrunch",
    "theverge", "wired", "arstechnica", "technologyreview", "futurism", "interestingengineering"
}

BANNED_VIOLENCE_REGEX = re.compile(
    r"\b(изнасилован\w*|изнасиловал\w*|педофил\w*|сексуальн\w+\s+насили\w*|развратн\w+\s+действи\w*|"
    r"zo['ʻʼ]?rlash\w*|nomusiga\s+teg\w*|pedofil\w*|jinsiy\s+zo['ʻʼ]?ravonlik\w*|"
    r"zorlaw\w*|nomısına\s+tiy\w*|jınsıy\s+zorlaw\w*)\b",
    re.IGNORECASE
)

KARAKALPAK_TRANSLATOR_API_URL = os.environ.get(
    "KARAKALPAK_TRANSLATOR_API_URL", 
    "https://karakalpak-translator-api.onrender.com/translate"
)


def ensure_render_service_warm(max_wait_seconds: int = 60) -> bool:
    """Proactively wakes up Render translation API if it's sleeping, waiting until it returns 200 OK."""
    health_url = "https://karakalpak-translator-api.onrender.com/health"
    print("[WARMUP] Checking if Render Translation API is awake...")
    start_time = time.time()
    attempts = 0
    while time.time() - start_time < max_wait_seconds:
        attempts += 1
        try:
            req = urllib.request.Request(health_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                if resp.status == 200:
                    elapsed = round(time.time() - start_time, 1)
                    print(f"[WARMUP] Render is AWAKE and READY (took {elapsed}s, attempt {attempts})!")
                    return True
        except Exception as e:
            elapsed = round(time.time() - start_time, 1)
            print(f"[WARMUP] Render waking up... ({e}, elapsed: {elapsed}s)")
            time.sleep(3)
    print(f"[WARMUP] Render did not respond within {max_wait_seconds}s.")
    return False


def translate_post_via_custom_api(text: str, timeout: int = 45, retries: int = 2) -> str | None:
    """Translates Russian news caption into Karakalpak Latin using user's dedicated Render API.
    STRICT POLICY: If Tilmoch translation fails, return None so the post is SKIPPED without arbitrary posting."""
    if not text or not text.strip():
        return None
    payload = {"text": text, "target_script": "latin", "model": "gemini-3.1-flash-lite"}
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        KARAKALPAK_TRANSLATOR_API_URL,
        data=data,
        headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
    )
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                res = json.loads(resp.read().decode("utf-8"))
                translated = res.get("translated_text", "")
                if translated and len(translated.strip()) > 30:
                    print(f"[TRANSLATE_API] Successfully translated caption via Tilmoch ({len(translated)} chars)")
                    return translated
        except Exception as e:
            print(f"[TRANSLATE_API] Attempt {attempt+1} failed: {e}")
            if attempt < retries:
                time.sleep(3)
    print("[TRANSLATE_API] Tilmoch API failed after retries. STRICT USER DIRECTIVE: Post will be SKIPPED, no arbitrary posting.")
    return None


def curate_and_write_posts(
    client: genai.Client,
    candidates: list[dict[str, Any]],
    existing_posts: list[str],
    ask_count: int,
    target_category_hint: str = "",
) -> list[dict[str, Any]]:
    playbook = Path("TASK_INSTRUCTIONS.md").read_text(encoding="utf-8") if Path("TASK_INSTRUCTIONS.md").exists() else ""

    rotation_mandate = ""
    if target_category_hint == "world_or_tech":
        rotation_mandate = """
*** CRITICAL TOPIC ROTATION (WORLD / SCIENCE & TECH MANDATE) ***:
The previous post on @qaraqalpaqshajanaliqlar covered a local/regional item.
For this batch, you MUST select an extraordinary, high-interest WORLD or SCIENCE/TECH story (categories 'world' or 'world_tech')!
Examples: space mission / James Webb discovery, AI / robotics milestone, unusual medical or scientific breakthrough, shocking global natural event, or high-stakes international news.
DO NOT pick a routine local repost for this batch!
"""
    elif target_category_hint == "local":
        rotation_mandate = """
*** CRITICAL TOPIC ROTATION (AUTHENTIC LOCAL / CITIZEN LIFE MANDATE) ***:
The previous post on @qaraqalpaqshajanaliqlar covered world/tech news.
For this batch, choose an authentic Karakalpakstan or Uzbekistan public/legal update (category 'karakalpakstan' or 'citizen_uzbekistan') from a primary official source (e.g. UzA, ministries, district councils).
"""

    prompt = f"""
You are the Editor-in-Chief and Doctor of Karakalpak Philology for the Telegram channel Qaraqalpaqsha jan'aliqlar (@qaraqalpaqshajanaliqlar).

{rotation_mandate}

AUTHENTIC SOURCES ONLY — STRICT DISCOURAGEMENT OF AGGREGATORS & ZERO ADS:
- Heavily DISCOURAGE selecting from kun.uz, KarPressa, or kknews.uz! They have been severely overused. Strongly favor primary authentic web portals, official gazettes, and international science/world wires (NASA, Nature, ScienceDaily, BBC, Reuters, Guardian, TechCrunch, UzA, etc.).
- ZERO ADVERTISING: Absolutely NEVER choose commercial advertisements, store discounts, product promos, or sponsored real estate announcements.

{OFFICIAL_KARAKALPAK_ALPHABET_RULES}

STRICT EDITORIAL PLAYBOOK:
{playbook[:5000]}

ALREADY PUBLISHED ON @qaraqalpaqshajanaliqlar (STRICT SEMANTIC DEDUPLICATION — NEVER repeat ANY topic, law, number, person, or event already covered below, even if the URL or source channel is different!):
{json.dumps(existing_posts, ensure_ascii=False, indent=2)}

CANDIDATE STORIES FROM LIVE OFFICIAL & GLOBAL FEEDS:
{json.dumps([{ "idx": i, "url": c["url"], "category": c["category"], "source_name": c["source_name"], "has_photo": bool(c.get("photo_urls")), "text": c["text"][:1000] } for i, c in enumerate(candidates)], ensure_ascii=False, indent=2)}


SOURCE POLICY:
- The candidate list comes from a PRIMARY list of Karakalpak, Uzbek and world Telegram channels + news websites, plus open-web discovery searches (`source_name` = "open-web"). These lists are NOT a limit: every candidate is equally eligible, and open-web items may be chosen when they are the most interesting AND come from a reliable outlet.
- Reliability: prefer official sources, wires and established media. For sensational or unverified claims (deaths, disasters, scandals, health scares) require a reputable source in `source_name`/`url`; never invent or "round up" facts, numbers, names or quotes. If a number is not in the candidate text, do not write it.

EDITORIAL STYLE — "interesting first" (the style of fast, curiosity-driven news channels, NOT of dry bureaucratic reposts):
- Choose stories people will want to read AND forward: accidents and disasters, world events, money and rules that change daily life (prices, fines, tariffs, benefits, deadlines), health and safety warnings, weather changes, science/tech/AI surprises, scholarships and remote jobs, sports tragedies and records, first-in-history facts, strange-but-true stories.
- Treat a weather change, a price/rule change or a safety warning with the SAME weight as a government event. Do NOT pick routine items such as "a meeting was held", ceremonies, delegations, awards/placings of one student or athlete in a minor contest — UNLESS there is a striking angle (first-ever, record, big prize, Karakalpakstan pride, large money, many people affected).
- HEADLINE = the concrete event with its strongest detail (who/what/how many), in correct Karakalpak. Good pattern (describe in Karakalpak, do not copy literally): "A business jet crashed in Florida, nine dead", "A Spanish footballer died after a collision with the goalkeeper", "The emergency ministry asked people to check their chimneys". Bad pattern: "A meeting was held", "A ceremony took place".
- BODY = 2–4 short sentences with the exact numbers/names/places from the candidate, then (when natural) ONE short human or safety line (what people should do / why it matters to them).
- Mix of topics across the batch: at most ONE routine-official story per batch; at least one story that touches daily life or safety; world/science/tech stories are welcome in every batch.
- MANDATORY SOURCE DIVERSITY: You MUST pick candidates from completely DIFFERENT sources! Diversify across Karakalpakstan district/regional channels (KarPressa, xaliq_ushin, Turtkul, Taqiyatash, kknews), Uzbekistan official ministries/legal portals (lex.uz, huquqiyaxborot, gov.uz), and World/Tech outlets. NEVER pick multiple stories from the same news outlet!

YOUR TASK:
1. Select the TOP {ask_count} completely NEW, non-duplicate, most interesting stories following the style above (mix of Karakalpakstan, Uzbekistan daily-life/legal/safety, and World/Tech).
   - Double-check against ALREADY PUBLISHED ON @qaraqalpaqshajanaliqlar: if a story is about the same event/law (e.g. 350 kVt electricity limit, 4-day parent school holiday leave, Nukus Chemistry Olympiad, Cannavaro, Asian Cup 2027, Swiss Ambassador at School #34, China Eastern Airlines), SKIP IT!
   - Strongly prefer candidates where `has_photo` is true or whose `url` is a direct web article (not `news.google.com`).
2. Write each caption in fluent, crystal-clear, factual RUSSIAN (it will be translated into 100% pure Karakalpak Latin via our dedicated neural translation API):
   - Keep visible text between 300 and 700 characters (short, concrete numbers, names, and scannable).
   - Use ONLY valid Telegram HTML tags: `<b>...</b>`, `<i>...</i>`, `<blockquote>...</blockquote>`, `<a href="...">...</a>`.
   - Lead with ONE fitting emoji (`⚡️`, `🚨`, `❓`, `🔰`, `🚀`, `🏆`, `🚛`, `💻`, `⚠️`, `🌍`) + `<b>Заголовок на русском</b>`.
   - Put the direct source link on ONE natural keyword inside the body text (e.g. `<a href="EXACT_CANDIDATE_URL">ключевое слово</a>`) using the EXACT `url` of THAT SAME `idx` candidate.
   - End EVERY caption with exactly this one line:
👉 <a href="https://t.me/qaraqalpaqshajanaliqlar">@qaraqalpaqshajanaliqlar — aǵza bolıw</a>

STRICT CONTENT BAN:
- NEVER select or write about rape, sexual violence, sexual assault, pedophilia, or sexual crimes! (Military wars, armed conflicts, and accidents are allowed, but ALL sexual violence/rape is STRICTLY FORBIDDEN).

Return ONLY a JSON array of objects with keys:
- "candidate_idx": integer (MUST match the exact `idx` of the story you wrote about!)
- "source_url": string (MUST equal `candidates[candidate_idx]["url"]`!)
- "caption_html": string (Russian formatted caption ready for translation)
- "wikimedia_search_keywords": string (2-3 simple English nouns for backup photo search)
"""

    resp = generate_content_with_fallback(
        client,
        DRAFT_MODELS,
        prompt,
        types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.2,
        ),
    )
    raw = (resp.text or "").strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw, flags=re.DOTALL).strip()
    parsed = json.loads(raw)
    if isinstance(parsed, dict):
        for v in parsed.values():
            if isinstance(v, list):
                parsed = v
                break
        else:
            parsed = [parsed]

    print(f"[TRANSLATOR] Translating {len(parsed)} curated posts into Karakalpak via {KARAKALPAK_TRANSLATOR_API_URL}...")
    valid_items = []
    for it in parsed:
        cap = it.get("caption_html", "")
        if cap:
            translated = translate_post_via_custom_api(cap, timeout=45, retries=2)
            if not translated:
                print(f"[SKIP] Post idx #{it.get('candidate_idx')} SKIPPED because Tilmoch translation failed.")
                continue
            it["caption_html"] = translated
            it["tilmoch_verified"] = True
            valid_items.append(it)
    return valid_items


def scan_suspicious_words(caption_html: str) -> list[str]:
    """Scan candidate caption for common Uzbekisms, Kazakhisms, or orthography traps."""
    plain = BeautifulSoup(caption_html, "html.parser").get_text(" ", strip=True).lower()
    flagged = set()
    for uz_word in UZ_TO_QQ_NEWS_BRIDGE.keys():
        if re.search(r"\b" + re.escape(uz_word) + r"\b", plain):
            flagged.add(uz_word)
    for pattern in [
        r"\b\w+tadan\b", r"\b\w+mek\b",
        r"[ğşçöüĞŞÇÖÜ]",
        r"\b(tanaffus|saroy|bizarılıq|janıwar|tezyurar|tunda|kunda|Olmazor|jarahat|turar jay|saqsewil|Savitskiy|puxara|shıyrinlik|erkinen ayır|Álot|pricep|bajarmasa|bajarıw|mínnetleme|tıs shetka|tıs qawat|ótkezdi)\b"
    ]:
        m = re.findall(pattern, plain, re.IGNORECASE)
        for w in m:
            if isinstance(w, str) and len(w) > 1:
                flagged.add(w)
    return sorted(list(flagged))[:15]


def proofread_karakalpak_captions(
    client: genai.Client, items: list[dict[str, Any]], existing_posts: list[str]
) -> list[dict[str, Any]]:
    """Layer 3: 2nd-pass Chief Academic Editor & Critic (Chain-of-Thought Linguistic Proofreader)."""
    if not items:
        return items
    try:
        items_payload = []
        for idx, it in enumerate(items):
            cap = it.get("caption_html", "")
            suspicious = scan_suspicious_words(cap)
            items_payload.append({
                "i": idx,
                "flagged_suspicious_words": suspicious,
                "caption_html": cap
            })

        proof_prompt = f"""
You are the Chief Academic Editor and Linguistic Critic of the Karakalpak Language Academy for @qaraqalpaqshajanaliqlar.
Your task is to protect 100% clean, literary Karakalpak Latin (Qaraqalpaq ádebiy tili) and block semantic duplicates.

{OFFICIAL_KARAKALPAK_ALPHABET_RULES}

ALREADY PUBLISHED ON @qaraqalpaqshajanaliqlar:
{json.dumps(existing_posts[-40:], ensure_ascii=False, indent=2)}

INSTRUCTIONS FOR EACH ITEM:
1. "is_duplicate": set to true if the story covers the SAME event, law, incident, or topic already in ALREADY PUBLISHED.
2. "linguistic_audit" (MANDATORY CHAIN-OF-THOUGHT):
   Scan the caption word-by-word. You MUST check:
   - Any Uzbek roots or loanwords (tanaffus -> tánepis, saroy -> saray, bezorilik/bizarılıq -> buzaqılıq, kambag'al -> kámbaǵal, tezyurar -> tez júrer, janıwar -> janzat, tunda -> túnde, kunda -> kúnde, turar joy -> turaq jay, suhbat/sóxbat -> sáwbet, do'kon -> dúkan, qadr-qimmat -> qádir-qımbat, raqabat -> ráqabat, hakamlik -> tóreshilik, nazariy -> teoriyalıq, qoida -> qaǵıyda)
   - Any Kazakhisms (joba -> joybar, baǵıt -> baǵdar, múmkindik -> múmkinshilik, jıynalıs -> májilis, quwattı -> quwatlı, orın aldı -> júz berdi/bolıp ótti, saylandı komanda -> terme komanda)
   - Any forbidden Uzbek suffixes: NEVER use "-tadan" with numbers (use "22-den 45-ke"); NEVER use infinitive "-moq/-mek" (use "-ıw/-iw" like "támiyinlew").
   - Alphabet & Orthography (Savitskiy -> Savickiy, Yunçjou -> Yunchjou, Turkish ğ/ş/ç/ö/ü, Uzbek apostrophes o'/g').
   - Vowel harmony & morphology: seksewil (never saqsewil), puqara (never puxara), uzınlıǵı (never uzunlıǵı), shiyrinlik (never shıyrinlik), jaraqat (never jarahat), JIÓ-degi (never JIÓ-daǵı), júzege keletin (never júze keletin).
   List EVERY error you find in `linguistic_audit`: `[{{"found": "...", "fixed": "...", "reason": "..."}}]`.
3. "clean_caption_html":
   Apply all corrections from your linguistic audit to the text.
   - PRESERVE all HTML formatting tags (<b>, <i>, <blockquote>, <a href="...">) intact!
   - PRESERVE exact numbers, dates, names, and links intact!
   - PRESERVE the closing link intact: 👉 <a href="https://t.me/qaraqalpaqshajanaliqlar">@qaraqalpaqshajanaliqlar — aǵza bolıw</a>

INPUT ITEMS:
{json.dumps(items_payload, ensure_ascii=False, indent=2)}

Return ONLY a JSON array:
[
  {{
    "i": 0,
    "is_duplicate": false,
    "linguistic_audit": [
      {{"found": "tanaffustan", "fixed": "tánepisten", "reason": "Uzbekism"}}
    ],
    "clean_caption_html": "<b>...</b>..."
  }}
]
"""
        resp = generate_content_with_fallback(
            client,
            PROOFREAD_MODELS,
            proof_prompt,
            types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.1,
            ),
        )
        raw = (resp.text or "").strip()
        if raw.startswith("```"):
            raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw, flags=re.DOTALL).strip()
        fixed_list = json.loads(raw)
        duplicate_indices: set[int] = set()
        if isinstance(fixed_list, list):
            for entry in fixed_list:
                pos = entry.get("i")
                if not isinstance(pos, int) or not (0 <= pos < len(items)):
                    continue
                if entry.get("is_duplicate") is True:
                    print(f"[DEDUP] Layer 3 AI critic blocked semantic duplicate at index {pos}.")
                    duplicate_indices.add(pos)
                    continue
                audit = entry.get("linguistic_audit", [])
                if audit:
                    fixes_summary = ", ".join(f"{a.get('found')} -> {a.get('fixed')}" for a in audit if isinstance(a, dict))
                    print(f"[LIT-CRITIC] Post #{pos} applied {len(audit)} linguistic fixes: {fixes_summary}")
                new_cap = entry.get("clean_caption_html") or entry.get("caption_html")
                if isinstance(new_cap, str) and len(new_cap) > 120:
                    items[pos]["caption_html"] = new_cap
        if duplicate_indices:
            items = [it for idx, it in enumerate(items) if idx not in duplicate_indices]
        time.sleep(1.5)
    except Exception as exc:
        print(f"[WARN] Second-pass proofreader skipped ({exc}); relying on deterministic fixes.")
    return items


STOP_STEMS = {
    "qaraqa", "ózbek", "ozbeks", "respub", "deregi", "qrjana", "bolıw", "ushın",
    "menen", "boyın", "haqqın", "málim", "xabar", "tárepi", "sonday", "ekenin",
}


def _extract_stems_and_numbers(text: str) -> tuple[set[str], set[str]]:
    lower = text.lower()
    words = re.findall(r"[a-záóúıǵń]{5,}", lower)
    stems = {w[:6] for w in words if w[:6] not in STOP_STEMS}
    nums = {
        n for n in re.findall(r"\b\d{2,}\b", lower)
        if n not in {"2025", "2026", "2027", "103", "104", "1050", "1268"}
    }
    return stems, nums


def is_text_duplicate_of_existing(visible_text: str, existing_texts: list[str]) -> bool:
    """Layer 4: Deterministic Karakalpak word-stem + 2+ digit number overlap gate (>= 0.45)."""
    cand_stems, cand_nums = _extract_stems_and_numbers(visible_text)
    if len(cand_stems) < 5:
        return False
    for prev in existing_texts:
        prev_stems, prev_nums = _extract_stems_and_numbers(prev)
        if len(prev_stems) < 5:
            continue
        denom = min(len(cand_stems), len(prev_stems))
        stem_overlap = len(cand_stems & prev_stems) / max(denom, 1)
        shared_nums = cand_nums & prev_nums
        score = stem_overlap + (0.12 * min(len(shared_nums), 2))
        if score >= 0.45:
            print(f"[DEDUP] Layer 4 blocked overlap ({score:.2f}, shared_nums={shared_nums}): {prev[:90]}...")
            return True
    return False


def transliterate_and_fix_outside_tags(html_text: str) -> str:
    """Convert any stray Cyrillic/Turkish chars and common lexical slips outside HTML tags."""
    parts = re.split(r"(<[^>]+>)", html_text)
    out: list[str] = []
    for part in parts:
        if part.startswith("<") and part.endswith(">"):
            out.append(part)
        else:
            converted = "".join(CYR_TO_QQ_LATIN.get(ch, ch) for ch in part)
            for pattern, repl in AUTO_WORD_FIXES:
                converted = re.sub(pattern, repl, converted)
            out.append(converted)
    return "".join(out)


def sanitize_and_validate_caption(caption: str) -> str | None:
    caption = caption.lstrip("\ufeff").strip()
    caption = caption.replace("<br>", "\n").replace("<br/>", "\n").replace("<br />", "\n")
    caption = transliterate_and_fix_outside_tags(caption)

    # Escape any bare '&' not part of an HTML entity so Telegram HTML parser never fails
    caption = re.sub(r"&(?!(?:amp|lt|gt|quot|#\d+|#x[0-9a-fA-F]+);)", "&amp;", caption)

    visible_text = BeautifulSoup(caption, "html.parser").get_text()
    if len(visible_text) > 1015 or len(visible_text) < 120:
        print(f"[WARN] Visible caption length out of bounds ({len(visible_text)} chars)")
        return None
    if CYRILLIC_RE.search(visible_text):
        print(f"[WARN] Unmapped Cyrillic still present, rejecting: {CYRILLIC_RE.findall(visible_text)}")
        return None
    if "@qaraqalpaqshajanaliqlar" not in caption:
        caption = caption.rstrip() + '\n👉 <a href="https://t.me/qaraqalpaqshajanaliqlar">@qaraqalpaqshajanaliqlar — aǵza bolıw</a>'
    return caption


# ======================================================================================
# PRE-PUBLISH PHILOLOGY & DIRECT URL AUDITOR (Zero-Tolerance Error Gate)
# ======================================================================================
FORBIDDEN_ROOTS_CHECK = [
    (r"\bjamoat\b", "jámiyetlik"),
    (r"\bbezorilik\b", "buzaqılıq"),
    (r"\bbezorılıq\b", "buzaqılıq"),
    (r"\bbizarılıq\b", "buzaqılıq"),
    (r"\biskerligin\b", "jumısın"),
    (r"\biskerligi\b", "jumısı"),
    (r"\biskerlik\b", "jumıs"),
    (r"\bq[aá]wipti\b", "qáwipli"),
    (r"\bquwattı\b", "quwatlı"),
    (r"\bjoba\b", "joybar"),
    (r"\bjobalar\b", "joybarlar"),
    (r"\bjobası\b", "joybarı"),
    (r"\bsayyora\b", "planeta"),
    (r"\bzilzila\b", "jer silkiniwi"),
    (r"\bchunki\b", "sebebi"),
    (r"\bbilan\b", "menen"),
    (r"\buchun\b", "ushın"),
    (r"\bshirinlikler\b", "shiyrinlikler"),
    (r"\bshıyrinlikler\b", "shiyrinlikler"),
    (r"\bshirinlik\b", "shiyrinlik"),
    (r"\bshıyrinlik\b", "shiyrinlik"),
    (r"\btalonshılıq\b", "basqınshılıq"),
    (r"\bepitsentr\b", "epicentr"),
    (r"\bShveysariya\b", "Shveycariya"),
    (r"\bpolitsiya\b", "policiya"),
    (r"\bkonstitutsiya\b", "konstituciya"),
    (r"\bmuhim\b", "áhmiyetli"),
    (r"\bbo'yicha\b", "boyınsha"),
    (r"\bboʻyicha\b", "boyınsha"),
    (r"\bhaqida\b", "haqqında"),
    (r"\bto'g'risida\b", "tuwralı"),
    (r"\bqarjılay\b", "finanslıq"),
    (r"\bsıyıqshı\b", "sıyqırshı"),
    (r"\bTexnogeniyalıq\b", "Texnogen"),
    (r"\btexnogeniyalıq\b", "texnogen"),
    (r"\bjarahat(lan|qa|tıń|tı|ta|lar)?\b", r"jaraqat\1"),
    (r"\bJarahat(lan|qa|tıń|tı|ta|lar)?\b", r"Jaraqat\1"),
]

def format_caption_with_direct_source_link(caption: str, exact_url: str, source_name: str = "") -> str:
    """Enforces that the exact direct source link is wrapped on ONLY ONE prominent focus word/verb in the text."""
    if not exact_url:
        return caption

    caption = caption.strip()

    # Strip any redundant Derek/Tolıq maǵlıwmat lines
    caption = re.sub(r'(?i)\n*Tolıq\s+maǵlıwmat(?:lar)?(?:\s+(?:ushın|bul jerde))?[.:]?', '', caption)
    caption = re.sub(r'(?i)\n*🔗\s*(?:Derek|Tolıq maǵlıwmat)[^\n]*', '', caption)
    caption = re.sub(r'(?i)\n*Derek\s*:[^\n]*', '', caption)

    soup = BeautifulSoup(caption, "html.parser")
    
    # Check if external link already exists in body
    has_external_link = False
    for a in soup.find_all("a"):
        href = a.get("href", "")
        if "qaraqalpaqshajanaliqlar" not in href:
            a["href"] = exact_url
            has_external_link = True
            break
            
    if has_external_link:
        caption = str(soup)
    else:
        # 1. Try prominent focus verbs & announcements
        focus_verbs = [
            r"\b(juwmaqlaw múddetlerin|málim etti|málim qılındı|málimleme berdi|xabar berildi|xabar berilmekte|xabarladı|eskertti|kútilmekte|engiziledi|engizildi|tastıyıqlandı|belgilendi|aytıp ótti|iske qospaqshı|iske qosıldı|payda boladı|ashıldı|shólkemlestirildi|júzege asırıldı|start berildi|jolǵa qoyıldı|imkaniyatına iye boladı|satıp alıwǵa boladı)\b"
        ]
        wrapped_body = False
        for pat in focus_verbs:
            m = re.search(pat, caption, flags=re.IGNORECASE)
            if m:
                target_word = m.group(1).rstrip(".,;:!?")
                caption = caption[:m.start()] + f'<a href="{exact_url}">{target_word}</a>' + caption[m.start() + len(target_word):]
                wrapped_body = True
                break
        
        # 2. If not matched, wrap the main verb of the sentence before period
        if not wrapped_body:
            sentence_verb_match = re.search(r'([a-zA-ZáóúıǵńÁÓÚIǴŃ]{4,})(\s*\.)', caption)
            if sentence_verb_match:
                verb = sentence_verb_match.group(1)
                caption = caption[:sentence_verb_match.start(1)] + f'<a href="{exact_url}">{verb}</a>' + caption[sentence_verb_match.end(1):]
                wrapped_body = True

    if "@qaraqalpaqshajanaliqlar" not in caption:
        caption = caption.rstrip() + '\n👉 <a href="https://t.me/qaraqalpaqshajanaliqlar">@qaraqalpaqshajanaliqlar — aǵza bolıw</a>'

    return caption.strip()


def audit_and_enforce_karakalpak_quality(caption: str, cand: dict[str, Any]) -> str | None:
    """Final pre-publish inspection gate: enforces 0% error Karakalpak & exact post URL."""
    if not caption or len(caption.strip()) < 100:
        return None
    if BANNED_VIOLENCE_REGEX.search(caption):
        print("[AUDIT] Post rejected: contains banned sexual violence/rape topic.")
        return None
    
    caption = caption.lstrip("\ufeff").strip()
    caption = caption.replace("<br>", "\n").replace("<br/>", "\n").replace("<br />", "\n")
    
    # 1. Transliterate any stray Cyrillic/Turkish letters outside tags
    caption = transliterate_and_fix_outside_tags(caption)
    
    # 2. Apply all 100+ deterministic regex fixes
    for pattern, replacement in AUTO_WORD_FIXES:
        caption = re.sub(pattern, replacement, caption)
        
    # 3. Apply secondary forbidden roots sweep
    for pat, rep in FORBIDDEN_ROOTS_CHECK:
        caption = re.sub(pat, rep, caption, flags=re.IGNORECASE)

    # 4. Escape bare ampersands for Telegram HTML
    caption = re.sub(r"&(?!(?:amp|lt|gt|quot|#\d+|#x[0-9a-fA-F]+);)", "&amp;", caption)

    # 5. STRICT URL & FOCUS LINK ENFORCER: Inject exact direct source link to focus keyword and footer
    exact_url = cand.get("url") or cand.get("fallback_post_url") or ""
    source_name = cand.get("source_name") or ""
    if exact_url:
        caption = format_caption_with_direct_source_link(caption, exact_url, source_name)

    # 6. Signature assurance
    if "@qaraqalpaqshajanaliqlar" not in caption:
        caption = caption.rstrip() + '\n👉 <a href="https://t.me/qaraqalpaqshajanaliqlar">@qaraqalpaqshajanaliqlar — aǵza bolıw</a>'

    # 7. Length and alphabet validation
    visible_text = BeautifulSoup(caption, "html.parser").get_text()
    if len(visible_text) > 1015 or len(visible_text) < 120:
        print(f"[AUDIT] Visible caption length out of bounds ({len(visible_text)} chars)")
        return None
        
    if CYRILLIC_RE.search(visible_text):
        print(f"[AUDIT] Unmapped Cyrillic still present, rejecting: {CYRILLIC_RE.findall(visible_text)}")
        return None

    return caption


def resolve_candidate_for_item(item: dict[str, Any], candidates: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Match candidate by exact source_url FIRST so off-by-one candidate_idx can NEVER attach the wrong photo!"""
    src_url = normalize_url(item.get("source_url") or "")
    if src_url:
        for c in candidates:
            if normalize_url(c["url"]) == src_url or normalize_url(c.get("fallback_post_url", "")) == src_url:
                return c
    # Also check URL inside Deregi <a href="..."> in caption_html
    cap = item.get("caption_html") or ""
    for m in re.findall(r'href="([^"]+)"', cap):
        nm = normalize_url(m)
        if "t.me/qaraqalpaqshajanaliqlar" in nm:
            continue
        for c in candidates:
            if normalize_url(c["url"]) == nm or normalize_url(c.get("fallback_post_url", "")) == nm:
                return c

    idx = item.get("candidate_idx")
    if isinstance(idx, int) and 0 <= idx < len(candidates):
        return candidates[idx]
    return None


def verify_photo_clean_and_relevant(
    client: genai.Client, img_bytes: bytes, story_summary: str
) -> bool:
    """Inspect candidate image via PIL + Gemini Vision to reject watermarks OR mismatched scenes."""
    try:
        with Image.open(io.BytesIO(img_bytes)) as im:
            w, h = im.size
            if w < 250 or h < 150:
                return False
    except Exception:
        return False

    try:
        check_prompt = (
            f"News post text:\n{story_summary[:450]}\n\n"
            "Inspect this image strictly and return JSON {\"ok\": true/false, \"reason\": \"...\"}.\n"
            "Set \"ok\": false if ANY of these apply:\n"
            "1) It contains a competitor Telegram channel watermark/handle (@KARAKALPAK24, @xaliq_ushin, @KarPressa, @qalampir, @kunuzofficial).\n"
            "2) It is a generic website logo/icon (e.g. Google News icon).\n"
            "3) The scene/people/event in the photo clearly belong to a DIFFERENT news story than the post text "
            "(for example, an airport Olympiad flag ceremony on a post about a Swiss Ambassador visiting School #34, or a football photo on an economy story)."
        )
        res = generate_content_with_fallback(
            client,
            VISION_MODELS,
            [
                types.Part.from_bytes(data=img_bytes, mime_type="image/jpeg"),
                check_prompt,
            ],
            types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.0,
            ),
        )
        raw_verdict = (res.text or "").strip()
        if raw_verdict.startswith("```"):
            raw_verdict = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw_verdict, flags=re.DOTALL).strip()
        verdict = json.loads(raw_verdict)
        if isinstance(verdict, list) and verdict:
            verdict = verdict[0]
        time.sleep(1.2)
        if isinstance(verdict, dict) and not verdict.get("ok", False):
            print(f"[INFO] Vision rejected photo: {verdict.get('reason')}")
            return False
        return True
    except Exception as exc:
        print(f"[WARN] Vision check warning (allowing valid PIL image): {exc}")
        return True


def search_wikimedia_fallback_photos(keywords: str) -> list[str]:
    if not keywords.strip():
        return []
    api_url = (
        "https://commons.wikimedia.org/w/api.php?action=query&generator=search"
        f"&gsrnamespace=6&gsrsearch={quote_plus(keywords + ' filetype:bitmap')}&gsrlimit=4"
        "&prop=imageinfo&iiprop=url&iiurlwidth=1200&format=json"
    )
    resp = http_get(api_url, timeout=12)
    if not resp:
        return []
    urls: list[str] = []
    try:
        pages = resp.json().get("query", {}).get("pages", {})
        for page in pages.values():
            for ii in page.get("imageinfo", []):
                u = ii.get("thumburl") or ii.get("url")
                if u and u.lower().endswith((".jpg", ".jpeg", ".png")):
                    urls.append(u)
    except Exception:
        pass
    return urls


def get_clean_photo_for_post(
    client: genai.Client, candidate: dict[str, Any], caption: str, wiki_keywords: str
) -> bytes | None:
    urls = list(candidate.get("photo_urls", []))

    art_url = candidate.get("url", "")
    if art_url.startswith("http") and "t.me/" not in art_url and "news.google.com" not in art_url:
        art_resp = http_get(art_url)
        if art_resp:
            soup = BeautifulSoup(art_resp.text, "html.parser")
            og = soup.select_one("meta[property='og:image']")
            if og and og.get("content") and og["content"].strip() not in urls:
                urls.insert(0, og["content"].strip())

    urls.extend(search_wikimedia_fallback_photos(wiki_keywords))

    for img_url in urls[:6]:
        resp = http_get(img_url)
        if not resp or len(resp.content) < 5500:
            continue
        try:
            with Image.open(io.BytesIO(resp.content)) as im:
                rgb = im.convert("RGB")
                buf = io.BytesIO()
                rgb.save(buf, format="JPEG", quality=90)
                jpg_bytes = buf.getvalue()
        except Exception:
            continue

        if verify_photo_clean_and_relevant(client, jpg_bytes, caption):
            return jpg_bytes

    return None


def send_telegram_video(bot_token: str, chat_id: str, video_url: str, caption_html: str) -> dict[str, Any]:
    url = f"https://api.telegram.org/bot{bot_token}/sendVideo"
    try:
        # First try passing direct URL to Telegram Bot API
        resp = requests.post(
            url,
            data={
                "chat_id": chat_id,
                "parse_mode": "HTML",
                "caption": caption_html,
                "video": video_url,
            },
            timeout=40,
        )
        data = resp.json()
        if data.get("ok"):
            return data
        
        # Fallback: stream download and upload
        v_resp = requests.get(video_url, stream=True, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
        if v_resp.status_code == 200 and int(v_resp.headers.get("content-length", 0)) < 45 * 1024 * 1024:
            v_bytes = v_resp.content
            if len(v_bytes) > 10000:
                resp2 = requests.post(
                    url,
                    data={
                        "chat_id": chat_id,
                        "parse_mode": "HTML",
                        "caption": caption_html,
                    },
                    files={"video": ("news.mp4", v_bytes, "video/mp4")},
                    timeout=60,
                )
                return resp2.json()
    except Exception as exc:
        print(f"[WARN] send_telegram_video exception: {exc}")
    return {"ok": False}


def send_telegram_photo(bot_token: str, chat_id: str, photo_bytes: bytes, caption_html: str) -> dict[str, Any]:
    url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
    resp = requests.post(
        url,
        data={
            "chat_id": chat_id,
            "parse_mode": "HTML",
            "caption": caption_html,
        },
        files={"photo": ("news.jpg", photo_bytes, "image/jpeg")},
        timeout=30,
    )
    return resp.json()


def main() -> int:
    bot_token, chat_id, gemini_key, max_posts = load_config()
    client = genai.Client(api_key=gemini_key)

    ensure_render_service_warm(max_wait_seconds=45)

    print("[1/5] Checking @qaraqalpaqshajanaliqlar live feed for deduplication...")
    existing_posts, seen_urls = fetch_existing_channel_posts()
    print(f"      Found {len(existing_posts)} recent channel posts & {len(seen_urls)} seen URLs.")

    print(
        f"[2/5] Scanning {len(TELEGRAM_SOURCES)} Telegram channels + {len(RSS_AND_GLOBAL_FEEDS)} website feeds "
        f"+ {len(OPEN_WEB_QUERIES)} open-web discovery queries (primary lists, not a limit)..."
    )
    raw_candidates: list[dict[str, Any]] = scrape_all_sources_parallel()
    print(f"      Raw stories scanned: {len(raw_candidates)}")

    fresh_candidates = [
        c
        for c in raw_candidates
        if normalize_url(c["url"]) not in seen_urls
        and normalize_url(c.get("fallback_post_url", "")) not in seen_urls
        and not any(normalize_url(ext) in seen_urls for ext in c.get("external_links", []))
    ]
    candidates = build_balanced_candidate_pool(fresh_candidates, limit=60)
    print(f"      Collected {len(candidates)} fresh unseen candidate stories.")
    if not candidates:
        print("[DONE] No unseen stories right now.")
        return 0

    # Smart Dynamic Category Alternator: 50/50 balance between World/Tech and Local Authentic
    last_post_text = existing_posts[0] if existing_posts else ""
    is_last_local = bool(re.search(
        r"(?i)\b(ózbek|ozbek|qaraqalpaq|nókis|nokis|tashkent|toshkent|wálayat|walayat|hákim|hakim|ministr|respublika|samarqand|buxoro|andijon|qaraqalpaqstan|fergana|namangan|qashqadaryo|surxondaryo|jizzax|sirdaryo|navoiy|xorazm)\w*",
        last_post_text
    ))
    target_hint = "world_or_tech" if is_last_local else "local"
    print(f"      [ROTATION ENGINE] Last post was local={is_last_local} -> Target for this run: {target_hint.upper()}")

    ask_count = min(max_posts + 2, 5)
    print(f"[3/5] Curating & drafting Karakalpak Latin posts with flagship Gemini (target={max_posts}, pool={ask_count})...")
    selected = curate_and_write_posts(client, candidates, existing_posts, ask_count, target_hint)
    time.sleep(1.5)

    print("[4/5] Proofreading captions & checking semantic duplicates against Official 34-Letter Alphabet...")
    selected = proofread_karakalpak_captions(client, selected, existing_posts)

    if not selected:
        print("[SKIP ALL] No posts available from Tilmoch translator. Skipping run cleanly as instructed by user.")
        return 0

    # Prioritize items matching our target category
    def item_pref_key(it: dict[str, Any]) -> int:
        cand_temp = resolve_candidate_for_item(it, candidates)
        if not cand_temp:
            return 99
        c_cat = cand_temp.get("category", "")
        if target_hint == "world_or_tech":
            return 0 if c_cat in ("world", "world_tech") else 1
        else:
            return 0 if c_cat in ("karakalpakstan", "citizen_uzbekistan") else 1

    selected.sort(key=item_pref_key)

    published_count = 0
    new_urls = list(seen_urls)
    new_titles = list(existing_posts)

    print("[5/5] Verifying exact photo match, overlap gate & publishing to @qaraqalpaqshajanaliqlar...")
    for item in selected:
        if published_count >= max_posts:
            break
        if not item.get("tilmoch_verified"):
            print(f"[SKIP] Post rejected: not translated or verified by Tilmoch API.")
            continue
        cand = resolve_candidate_for_item(item, candidates)
        if not cand:
            print("[WARN] Could not resolve candidate for item, skipping.")
            continue
        # Run comprehensive pre-publish philology & exact direct URL audit
        caption = audit_and_enforce_karakalpak_quality(item.get("caption_html", ""), cand)
        if not caption:
            print(f"[AUDIT] Post rejected by pre-publish Philology Gate: {cand.get('url')}")
            continue

        plain_caption = BeautifulSoup(caption, "html.parser").get_text(" ", strip=True)
        if is_text_duplicate_of_existing(plain_caption, new_titles):
            continue

        res = None
        video_urls = cand.get("video_urls", [])
        if video_urls:
            print(f"[MEDIA] Found video for {cand['url']}, trying to post video...")
            res = send_telegram_video(bot_token, chat_id, video_urls[0], caption)
            if not res or not res.get("ok"):
                print(f"[WARN] Video send failed ({res}), falling back to verified photo.")
                res = None

        if not res or not res.get("ok"):
            photo_bytes = get_clean_photo_for_post(
                client, cand, caption, item.get("wikimedia_search_keywords", "")
            )
            if not photo_bytes:
                print(f"[SKIP] Could not obtain clean related photo for {cand['url']}; trying backup story.")
                continue
            res = send_telegram_photo(bot_token, chat_id, photo_bytes, caption)
        if res.get("ok"):
            msg_id = res["result"]["message_id"]
            print(f"[OK] Published https://t.me/qaraqalpaqshajanaliqlar/{msg_id} -> {cand['url']}")
            published_count += 1
            new_urls.append(normalize_url(cand["url"]))
            if cand.get("fallback_post_url"):
                new_urls.append(normalize_url(cand["fallback_post_url"]))
            new_titles.append(BeautifulSoup(caption, "html.parser").get_text(" ", strip=True)[:350])
            time.sleep(3)
        else:
            print(f"[ERR] Telegram API error: {res}")

    HISTORY_FILE.write_text(
        json.dumps({"urls": new_urls[-200:], "titles": new_titles[-60:]}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"[DONE] Successfully published {published_count} posts.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
