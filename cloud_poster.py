#!/usr/bin/env python3

"""

Qaraqalpaqsha jan'aliqlar (@qaraqalpaqshajanaliqlar) — 24/7 Cloud Automated News Poster

Official 34-Letter Karakalpak Alphabet + Two-Pass Literary Grammar Proofreading + Exact Photo Matching.

"""



from __future__ import annotations



import io
import base64
import json
import os
import re
import shutil
import subprocess
import sys
sys.stdout.reconfigure(line_buffering=True)
import tempfile
import time
import xml.etree.ElementTree as ET

import json

import os

import re

import sys
sys.stdout.reconfigure(line_buffering=True)

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

NICHE_ESOTERIC_TOPIC_RE = re.compile(
    r"\b("
    r"метеорн(?:ый|ого|ом|ые|ых|ому)|"
    r"звездопад\w*|"
    r"метеоритн(?:ый|ого|ые)\s+дожд|"
    r"леонид\w*|"
    r"персеид\w*|"
    r"геминид\w*|"
    r"лирид\w*|"
    r"астероид\s+(?:пролетит|сблизится)|"
    r"комет[аые]\s+[0-9]+[A-Za-z]|"
    r"звездн(?:ое|ого)\s+неб[оа]|"
    r"астрономическ(?:ие|их)\s+наблюден|"
    r"meteor\s+shower|"
    r"leonids?|"
    r"perseids?|"
    r"drobny[ye]\s+zaryad|"
    r"kvantov(?:aya|oy)\s+zaputannost|"
    r"mikrobiom\s+myshey|"
    r"genom\s+mukh|"
    r"iskopayem(?:yye|ogo)\s+mollyusk|"
    r"paleontolog\w*\s+opisali"
    r")\b",
    re.IGNORECASE
)




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

    # Non-Karakalpak foreign Latin diacritics (Tatar, Turkmen, Turkish, German, Finnish, etc.)
    "Ä": "Á", "ä": "á",
    "Ö": "Ó", "ö": "ó",
    "Ü": "Ú", "ü": "ú",
    "Ğ": "Ǵ", "ğ": "ǵ",
    "Ş": "Sh", "ş": "sh",
    "Ç": "Ch", "ç": "ch",
    "Ñ": "Ń", "ñ": "ń",
    "İ": "I",
    "Â": "A", "â": "a",
    "Ê": "E", "ê": "e",
    "Î": "I", "î": "i",
    "Ô": "O", "ô": "o",
    "Û": "U", "û": "u",
    "Ë": "E", "ë": "e",
    "Ï": "I", "ï": "i",
    "Ÿ": "Y", "ÿ": "y",
    "À": "A", "à": "a",
    "È": "E", "è": "e",
    "Ì": "I", "ì": "i",
    "Ò": "O", "ò": "o",
    "Ù": "U", "ù": "u",
}



AUTO_WORD_FIXES = [

    # 1. Official 2016 Acute Vowels & Consonants (Strict normalization from typewriter apostrophes)

    (r"G['’ʻʼ]", "Ǵ"),

    (r"g['’ʻʼ]", "ǵ"),

    (r"O['’ʻʼ]", "Ó"),

    (r"o['’ʻʼ]", "ó"),

    (r"N['’ʻʼ]", "Ń"),

    (r"n['’ʻʼ]", "ń"),



    # 2. Foreign Latin letters with diacritics (Tatar, Turkmen, Turkish, German, etc.)
    (r"Ä", "Á"), (r"ä", "á"),
    (r"Ö", "Ó"), (r"ö", "ó"),
    (r"Ü", "Ú"), (r"ü", "ú"),
    (r"Ğ", "Ǵ"), (r"ğ", "ǵ"),
    (r"Ş", "Sh"), (r"ş", "sh"),
    (r"Ç", "Ch"), (r"ç", "ch"),
    (r"Ñ", "Ń"), (r"ñ", "ń"),
    (r"İ", "I"), (r"ı", "ı"),
    (r"Ë", "E"), (r"ë", "e"),
    (r"Ï", "I"), (r"ï", "i"),



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

    (r"\bTórtkúl\b", "Tórtkól"),

    (r"\btórtkúl\b", "tórtkól"),

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

        (r"\bJÁ\b", "JI"),

    (r"\bJÁ([a-zıóúáǵń]*)\b", r"JI\1"),

    (r"\bjastar([a-zıóúáǵń]*)\b", r"jaslar\1"),

    (r"\bJastar([a-zıóúáǵń]*)\b", r"Jaslar\1"),

    (r"\bjasand([ıi])\b", "jasama"),

    (r"\bJasand([ıi])\b", "Jasama"),

    (r"\bjasandıq\b", "jasamalıq"),

    (r"\bJasandıq\b", "Jasamalıq"),

    (r"\bjasalma\b", "jasama"),

    (r"\bJasalma\b", "Jasama"),

    (r"\bkrah([a-zıóúáǵń]*)\b", r"bankrotlıq\1"),

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

    # Additional critical slips & anti-Uzbekisms audited from posts 97-139

    (r"\bprezidendi\b", "prezidenti"),

    (r"\bPrezidendi\b", "Prezidenti"),

    (r"\bShavqat\b", "Shavkat"),

    (r"\bbazıxana\b", "bajıxana"),

    (r"\bBazıxana\b", "Bajıxana"),

    (r"\btamoxana\b", "bajıxana"),

    (r"\bTamoxana\b", "Bajıxana"),

    (r"\bdvigatil([a-zıóúáǵń]*)\b", r"dvigatel\1"),

    (r"\bDvigatil([a-zıóúáǵń]*)\b", r"Dvigatel\1"),

    (r"\bpanelil([a-zıóúáǵń]*)\b", r"panell\1"),

    (r"\bpanelgel([a-zıóúáǵń]*)\b", r"panellerg\1"),

    (r"\bBizinsiz\b", "Biziń"),

    (r"\bbizinsiz\b", "biziń"),

    (r"\bobyektst([a-zıóúáǵń]*)\b", r"obyekt\1"),

    (r"\basteroyid([a-zıóúáǵń]*)\b", r"asteroid\1"),

    (r"\bátirindegi\b", "átirapındaǵı"),

    (r"\b(x|X)alıq aralıq\b", r"\1alıqaralıq"),

    (r"\bjumısqar sapar([a-zıóúáǵń]*)\b", r"jumıs sapar\1"),

    (r"\bÁdministraciya([a-zıóúáǵń]*)\b", r"Administraciya\1"),

    (r"\bádministraciya([a-zıóúáǵń]*)\b", r"administraciya\1"),

    (r"\bmenedjerdiler\b", "menedjerler"),

    (r"\btop-menedjerdiler\b", "top-menedjerler"),

    (r"\bnapaqá\b", "napaqa"),

    (r"\bNapaqá\b", "Napaqa"),

    (r"\btirishilik\b", "tirshilik"),

    (r"\bTirishilik\b", "Tirshilik"),

    (r"\btábiyǵiy\b", "tábiyiy"),

    (r"\bTábiyǵiy\b", "Tábiyiy"),

    (r"\bkútew([a-zıóúáǵń]*)\b", r"kútiw\1"),

    (r"\bKútew([a-zıóúáǵń]*)\b", r"Kútiw\1"),

    (r"\bkonkurenciya\b", "báseki"),

    (r"\bKonkurenciya\b", "Báseki"),

    (r"\bKonkurenciya komiteti\b", "Báseki komiteti"),

    (r"\bjáriyalad([ıi])\b", r"jariylad\1"),

    (r"\bJáriyalad([ıi])\b", r"Jariylad\1"),

    (r"\bUsırasıw\b", "Ushırasıw"),

    (r"\busırasıw\b", "ushırasıw"),

    (r"\b(r|R)ayon turıwshı([a-zıóúáǵń]*)\b", r"\1ayon turǵın\2"),

    (r"\b(b|B)untan aldın\b", r"\1unnan aldın"),

    (r"\b(s|S)ebepti\b", r"\1ebepli"),

    (r"\bBunga\b", "Buǵan"),

    (r"\bbunga\b", "buǵan"),

    (r"\b(f|F)aktni\b", r"\1aktti"),

    (r"\b(b|B)olama\?", r"\1ola ma?"),

    (r"\b(i|I)mkaniyat bereme\?", r"\1mkaniyat bere me?"),

    (r"\b(m|M)úmkinshilik bereme\?", r"\1úmkinshilik bere me?"),

    (r"\b(d|D)odalawda\b", r"\1alqılamaqta"),

    (r"\b(p|P)akistanlı\b", r"\1akistanlıq"),

    (r"\b(s|S)tantsiya([a-zıóúáǵń]*)\b", r"\1tanciya\2"),

    (r"\b(a|A)ktsiya([a-zıóúáǵń]*)\b", r"\1kciya\2"),

    (r"\bhámde\b", "hám de"),

    (r"\bHámde\b", "Hám de"),

    # Audited from posts 140-141

    (r"\bdepartamendi\b", "departamenti"),

    (r"\bDepartamendi\b", "Departamenti"),

    (r"\bparlamendi\b", "parlamenti"),

    (r"\bParlamendi\b", "Parlamenti"),

    (r"\bwáqıya([a-zıóúáǵń]*)\b", r"waqıya\1"),

    (r"\bWáqıya([a-zıóúáǵń]*)\b", r"Waqıya\1"),

    (r"\bkitniń\b", "kittiń"),

    (r"\balımlar\b", "ilimpazlar"),

    (r"\bAlımlar\b", "Ilimpazlar"),

    (r"\babıroylı\b", "abıraylı"),

    (r"\bAbıroylı\b", "Abıraylı"),

    (r"\bmoyındap\b", "moyınlap"),

    (r"\bmoyındaw\b", "moyınlaw"),

    (r"\bmártebe\b", "márte"),

    # Critical audited slips from posts 142-143

    (r"\bbaslı qalaq\b", ""),

    (r"\bkinoqumar([a-zıóúáǵń]*)\b", r"kinosúyiwshi\1"),

    (r"\bKinoqumar([a-zıóúáǵń]*)\b", r"Kinosúyiwshi\1"),

    (r"\bdereklar\b", "derekler"),

    (r"\bDereklar\b", "Derekler"),

    (r"\boqsham([a-zıóúáǵń]*)\b", r"kesh\1"),

    (r"\bOqsham([a-zıóúáǵń]*)\b", r"Kesh\1"),

    (r"\bxizmet([a-zıóúáǵń]*)\b", r"xızmet\1"),

    (r"\bXizmet([a-zıóúáǵń]*)\b", r"Xızmet\1"),

    (r"\bBıqıńǵı\b", "Kúshli"),

    (r"\bjasawshı([a-zıóúáǵń]*)\b", r"turǵın\1"),

    (r"\bJasawshı([a-zıóúáǵń]*)\b", r"Turǵın\1"),

    # Critical audited slips from posts 146-215 (Highlighted)

    (r"\baksiy([a-zıóúáǵń]*)\b", r"akciy\1"),

    (r"\bAksiy([a-zıóúáǵń]*)\b", r"Akciy\1"),

    (r"\bádeyir\b", "ádeywir"),

    (r"\bÁdeyir\b", "Ádeywir"),

    (r"\bderek-oray([a-zıóúáǵń]*)\b", r"maǵlıwmatlar oray\1"),

    (r"\bderek oray([a-zıóúáǵń]*)\b", r"maǵlıwmatlar oray\1"),

    (r"\bshamamen\b", "shama menen"),

    (r"\bShamamen\b", "Shama menen"),

    (r"\bshıntlap\b", "shınında da"),

    (r"\bShıntlap\b", "Shınında da"),

    (r"\btopılıs([a-zıóúáǵń]*)\b", r"hújim\1"),

    (r"\bTopılıs([a-zıóúáǵń]*)\b", r"Hújim\1"),

    (r"\bjas basqan adamlard([ıi])\b", "kekselerdi"),

    # Critical audited slips from posts 290-294
    (r"\b(t|T)ınıq toq[ıi]malar\b", r"\1iri toqımalar"),
    (r"\bJabıńqı\b", "Qaplama"),
    (r"\bjabıńqı\b", "qaplama"),
    (r"\bkletqa([a-zıóúáǵń]*)\b", r"kletka\1"),
    (r"\bKletqa([a-zıóúáǵń]*)\b", r"Kletka\1"),
    (r"\bkútik([a-zıóúáǵń]*)\b", r"kúyik\1"),
    (r"\bKútik([a-zıóúáǵń]*)\b", r"Kúyik\1"),
    (r"\bdıyqan([a-zıóúáǵń]*)\b", r"diyqan\1"),
    (r"\bDıyqan([a-zıóúáǵń]*)\b", r"Diyqan\1"),
    (r"\btaldap shıǵ([a-zıóúáǵń]*)\b", r"tallap shıǵ\1"),
    (r"\bTaldap shıǵ([a-zıóúáǵń]*)\b", r"Tallap shıǵ\1"),
    (r"\bshıń saatlar([a-zıóúáǵń]*)\b", r"eń tıǵız saatlar\1"),
    (r"\bShıń saatlar([a-zıóúáǵń]*)\b", r"Eń tıǵız saatlar\1"),
    (r"\b([A-Za-zÁáÓóÚúǴǵŃńıI]+)lerinin'\b", r"\1leriniń"),
    (r"\btarix\b", "tariyx"),
    (r"\bTarix\b", "Tariyx"),
    (r"\bashildi\b", "ashıldı"),
    (r"\bAshildi\b", "Ashıldı"),
    (r"\bzıyanlan([a-zıóúáǵń]*)\b", r"zaqımlan\1"),
    (r"\bZıyanlan([a-zıóúáǵń]*)\b", r"Zaqımlan\1"),
    (r"\bbarlıǵı tórt saat\b", "barı-joǵı tórt saat"),

    # Audited slips from latest 50 posts (#113-#294)
    (r"\bp'edestal([a-zıóúáǵń]*)\b", r"pedestal\1"),
    (r"\bP'edestal([a-zıóúáǵń]*)\b", r"Pedestal\1"),
    (r"\bjelelik arza\b", "elektronlıq arza"),
    (r"\bkadastrdi\b", "kadastrdı"),
    (r"\bKadastrdi\b", "Kadastrdı"),
    (r"\bsignaldi\b", "signaldı"),
    (r"\bSignaldi\b", "Signaldı"),
    (r"\bjırtqıshdı\b", "jırtqıshtı"),
    (r"\bıytı menen\b", "iyti menen"),
    (r"\baqsha jıliwda\b", "aqsha jıllawda"),
    (r"\bcirkumbinnıń ekzoplaneta\b", "cirkumbinar ekzoplaneta"),
    (r"\bretsenziy([a-zıóúáǵń]*)\b", r"recenziy\1"),
    (r"\bRetsenziy([a-zıóúáǵń]*)\b", r"Recenziy\1"),
    (r"\btastiyıqlaw([a-zıóúáǵń]*)\b", r"tastıyıqlaw\1"),
    (r"\bTastiyıqlaw([a-zıóúáǵń]*)\b", r"Tastıyıqlaw\1"),

    # Audited slips from posts #294-#386
    (r"\bUllı milletlik\b", "Ulıwma milliy"),
    (r"\bullı milletlik\b", "ulıwma milliy"),
    (r"\b(t|T)erek eguw\b", r"\1erek egiw"),
    (r"\b(k|K)ólem taraw boyınsha\b", r"\1óklemzarlastırıw boyınsha"),
    (r"\bmáhällä([a-zıóúáǵń]*)\b", r"máhálle\1"),
    (r"\bmáhállá([a-zıóúáǵń]*)\b", r"máhálle\1"),
    (r"\bMáhällä([a-zıóúáǵń]*)\b", r"Máhálle\1"),
    (r"\bMáhállá([a-zıóúáǵń]*)\b", r"Máhálle\1"),
    (r"\bKeniya sudi\b", "Keniya sudı"),
    (r"\bjasy tolmaǵan\b", "jası tolmaǵan"),
    (r"\bkómılgen\b", "kómilgen"),
    (r"\bKorolylıq\b", "Korolligi"),
    (r"\b(t|T)arafdar([a-zıóúáǵń]*)\b", r"\1árepdar\2"),
    (r"\bgúres sistemaları\b", "jawıngerlik sistemalar"),
    (r"\bkóp jıllardan berli\b", "kóp jıllardan beri"),
    (r"\bnarkobuzaqılıq([a-zıóúáǵń]*)\b", r"narkojınayatshılıq\1"),
    (r"\bnarkotikalıq qurallard([ıi])\b", "narkotikalıq zatlardı"),
    (r"\bbayraqdarlar\b", "sawrınlı orın iyeleri"),
    (r"\bmars tuqımı([a-zıóúáǵń]*)\b", r"mars jınısı\1"),
    (r"\b(m|M)eteorittıń\b", r"\1eteorittiń"),
    (r"\btereń erte dáwirler([a-zıóúáǵń]*)\b", r"áyyemgi dáwirler\1"),
    (r"\bshártterin\b", "shártlerin"),
    (r"\b(t|T)ibbiyot([a-zıóúáǵń]*)\b", r"\1edicina\2"),
    (r"\b(t|T)ezlestir([a-zıóúáǵń]*)\b", r"\1ezlet\2"),
    (r"\bintellekten paydalan([a-zıóúáǵń]*)\b", r"intellektten paydalan\1"),
    (r"\baqsha juwıw\b", "aqsha jıllaw"),
    # New audited slips from posts #381 - #399
    (r"\bengiziwdıń\b", "engiziwdiń"),
    (r"\b(t|T)echnologiya([a-zıóúáǵń]*)\b", r"\1exnologiya\2"),
    (r"\bmáselerin\b", "máselelerin"),
    (r"\bÁstanalıq\b", "Astanalıq"),
    (r"\bÁstana\b", "Astana"),
    (r"\b(p|P)rocess\b", r"\1roces"),
    (r"\bjúze keliw([a-zıóúáǵń]*)\b", r"júzege keliw\1"),
    (r"\b(q|Q)adaǵalaw ólshemler([a-zıóúáǵń]*)\b", r"\1adaǵalaw ilajlar\2"),
    (r"\bIshki isler uyımları\b", "Ishki isler organları"),
    (r"\btájiriybeli sapar([a-zıóúáǵń]*)\b", r"jumıs sapar\1"),
    (r"\bkútip barıw([a-zıóúáǵń]*)\b", r"kútip-baplaw\1"),
    (r"\b(j|J)asıl makan\b", r"\1asıl mákan"),
    (r"\b(u|U)lıwma milliy\b", r"\1lıwmamilliy"),
    (r"\b(q|Q)arıydarlardıń huqıqlar([a-zıóúáǵń]*)\b", r"\1utınıwshılardıń huqıqlar\2"),
    (r"\b(q|Q)ádemler taslamaqta\b", r"ilajlar kórmekte"),
    (r"\bqupıya orın([a-zıóúáǵń]*)\b", r"jasırın orın\1"),
    (r"\bǵalabalıq sport([a-zıóúáǵń]*)\b", r"ǵalaba sport\1"),
    # New audited slips from posts #452 - #459
    (r"\bJIÓ\b", "JI"),
    (r"\bbandlıq([a-zıóúáǵń]*)\b", r"bántlik\1"),
    (r"\bBandlıq([a-zıóúáǵń]*)\b", r"Bántlik\1"),
    (r"\bsotsial([a-zıóúáǵń]*)\b", r"social\1"),
    (r"\bSotsial([a-zıóúáǵń]*)\b", r"Social\1"),
    (r"\bhábezlik\b", "bezew"),
    (r"\bfaxriy([a-zıóúáǵń]*)\b", r"nuranıy\1"),
    (r"\bFaxriy([a-zıóúáǵń]*)\b", r"Nuranıy\1"),
    (r"\btınıp ald([ıi])\b", "qolǵa túsirdi"),
    (r"\bmıyúwe([a-zıóúáǵń]*)\b", r"miywe\1"),
    (r"\b(t|T)aǵınshaqlardı jaratılıw\b", r"\1aǵınshaqlardı jasaw"),
    (r"\b(p|P)ısıw hám tigiw\b", r"\1ishiw hám tigiw"),
    (r"\bkeshke baǵdarlaması\b", "keshki baǵdarlama"),
    (r"\bterek ekti\b", "terek egildi"),
    (r"\bhákimligi qasında\b", "hákimiyatı qasında"),
    (r"\bshınjırshasın\b", "jetkerip beriw dizbegin"),
    (r"\bgárezlilikti\b", "ǵárezlilikti"),
    (r"\binnovacialıq\b", "innovaciyalıq"),
    # New audited slips from posts #460 - #465
    (r"\bis gazınen\b", "is gazınan"),
    (r"\b(z|Z)áhárleniw([a-zıóúáǵń]*)\b", r"\1eherleniw\2"),
    (r"\bIslom Yusupov\b", "Islam Yusupov"),
    (r"\bmorylar\b", "morilar"),
    (r"\bsaz isleywshiligin\b", "durıs islewin"),
    (r"\búshinshi dáwiri\b", "úshinshi basqıshı"),
    (r"\brayonlıq administraciya\b", "rayon hákimiyatı"),
    (r"\brayonınıń\b", "rayonnıń"),
    (r"\bjámiyetshilik keńlikler([a-zıóúáǵń]*)\b", r"jámiyetlik orınlar\1"),
    (r"\bTórtkól\b", "Tórtkúl"),
    (r"\bkitabxan([a-zıóúáǵń]*)\b", r"kitapxan\1"),
    (r"\bKitabxan([a-zıóúáǵń]*)\b", r"Kitapxan\1"),
    (r"\bRespublıkas([ıi])\b", r"Respublikas\1"),
    (r"\bdelegacıya\b", "delegaciya"),
    (r"\bmásseleler([a-zıóúáǵń]*)\b", r"máseleler\1"),
    (r"\b([e|E])ksport qiliw\b", r"\1ksport qılıw"),
    (r"\btexnologıya([a-zıóúáǵń]*)\b", r"texnologiya\1"),
    # New audited slips from post #466
    (r"\bmáhalle([a-zıóúáǵń]*)\b", r"máhálle\1"),
    (r"\bMáhalle([a-zıóúáǵń]*)\b", r"Máhálle\1"),
    (r"\b№?\s*(PP|ПП)-(\d+)\b", r"PQ-\2-sanlı"),
    (r"\bkesispepleri([a-zıóúáǵń]*)\b", r"kesispeleri\1"),
    (r"\bjolawshılardı tashıw\b", "jolawshılardı tasıw"),
    (r"\badministrativlik tártipte\b", "hákimshilik tártipte"),
]



TELEGRAM_SOURCES = [

    # --- KARAKALPAKSTAN (Exclusive Primary Sources: Supreme Council, Ministers, Akimiyats, Law Enforcement, Ministries) ---

    ("karakalpakstan", "joqargikenes", 24),           # QR Joqarǵı Keńesi

    ("karakalpakstan", "QResMinistrlerKenesi", 24),   # QR Ministrler Keńesi

    ("karakalpakstan", "qrprokuratura", 24),          # QR Prokuraturası

    ("karakalpakstan", "qrsudlari", 24),              # QR Sudları

    ("karakalpakstan", "nukus_press", 24),            # Nókis qalası hákimligi

    ("karakalpakstan", "qonirat_press", 24),          # Qońırat rayonı hákimligi

    ("karakalpakstan", "moynaq_press", 24),           # Moynaq rayonı hákimligi

    ("karakalpakstan", "shimbayrk", 24),              # Shimbay rayonı hákimligi

    ("karakalpakstan", "turtkulhokim_uz", 24),        # Tórtkúl rayonı hákimligi

    ("karakalpakstan", "xodjeyli_rk", 24),            # Xojeli rayonı hákimligi

    ("karakalpakstan", "pressTaqiyatas", 24),         # Taqıyatas rayonı hákimligi

    ("karakalpakstan", "kanlikulnews", 24),           # Qanlıkól rayonı hákimligi

    ("karakalpakstan", "beruniy_press", 24),          # Beruniy rayonı hákimligi

    ("karakalpakstan", "kegeyli_press", 24),          # Kegeyli rayonı hákimligi

    ("karakalpakstan", "taxtakopir_press", 24),       # Taxtakópir rayonı hákimligi

    ("karakalpakstan", "ellikqala_press", 24),        # Ellikqala rayonı hákimligi

    ("karakalpakstan", "qaraozek_press", 24),         # Qaraózek rayonı hákimligi

    ("karakalpakstan", "shomanay_press", 24),         # Shomanay rayonı hákimligi

    ("karakalpakstan", "bozataw_press", 24),          # Bozataw rayonı hákimligi

    ("karakalpakstan", "krbajixana", 24),             # QR Bajıxana basqarması

    ("karakalpakstan", "kkeduuz", 24),                # QR Mektep hám mektepke shekemgi bilimlendiriw

    ("karakalpakstan", "jaslar_isleri_agentligi", 24),# QR Jaslar isleri agentligi

    ("karakalpakstan", "xaliq_ushin", 24),            # Rásmiy jurnalistika / axborot xizmati

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





def load_config() -> tuple[str, str, str, int, str, bool]:
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    gemini_key = os.environ.get("GEMINI_API_KEY", "").strip()
    max_posts = max(5, int(os.environ.get("MAX_POSTS", "5")))
    admin_chat_id = os.environ.get("ADMIN_CHAT_ID", "5649102659").strip()
    auto_publish = os.environ.get("AUTO_PUBLISH_TO_CHANNEL", "false").lower() in ("true", "1", "yes")

    local_cfg = Path("telegram_config.json")
    if (not bot_token or not chat_id) and local_cfg.exists():
        data = json.loads(local_cfg.read_text(encoding="utf-8"))
        bot_token = bot_token or data.get("bot_token", "")
        chat_id = chat_id or data.get("chat_id") or data.get("channel_id", "")
        admin_chat_id = admin_chat_id or data.get("admin_chat_id", "5649102659")

    if not bot_token or not chat_id:
        raise RuntimeError("Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID.")
    if not gemini_key:
        raise RuntimeError("Missing GEMINI_API_KEY secret.")
    return bot_token, chat_id, gemini_key, max(5, max_posts), admin_chat_id, auto_publish

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
            recent_summaries.extend(cached.get("titles", [])[-80:])
        except Exception:
            pass
    else:
        try:
            gh_raw = requests.get("https://raw.githubusercontent.com/sardardww/qrjanaliq-poster/main/posted_history.json", timeout=6)
            if gh_raw.status_code == 200:
                cached = gh_raw.json()
                seen_urls.update(cached.get("urls", []))
                recent_summaries.extend(cached.get("titles", [])[-80:])
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

                    if href and "t.me/janaliqjanaliq" not in href and "t.me/qaraqalpaqshajanaliqlar" not in href:

                        seen_urls.add(normalize_url(href))

        return page_summaries, oldest_id



    # Scrape public channel @janaliqjanaliq for real-time live posts and URLs
    for ch_name in ["janaliqjanaliq", "qaraqalpaqshajanaliqlar"]:
        resp = http_get(f"https://t.me/s/{ch_name}")
        if resp:
            soup1 = BeautifulSoup(resp.text, "html.parser")
            page1_summaries, oldest = _extract_from_soup(soup1)
            if oldest and oldest > 1:
                prev_resp = http_get(f"https://t.me/s/{ch_name}?before={oldest}")
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



    # Also sync seen/blacklisted URLs from Render Moderation Queue
    try:
        r_seen = requests.get("https://karakalpak-translator-api.onrender.com/drafts/seen_urls", timeout=8)
        if r_seen.status_code == 200:
            for u in r_seen.json().get("urls", []):
                seen_urls.add(normalize_url(u))
    except Exception:
        pass

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

        external_links = []

        for a_tag in txt_el.select("a[href]"):

            href = a_tag.get("href", "").strip()

            if (

                href.startswith("http")

                and channel.lower() not in href.lower()

                and not any(s in href.lower() for s in ("instagram.com", "facebook.com", "fb.com", "youtube.com", "x.com"))

            ):

                external_links.append(href)

        # Minimum substantive text threshold: 1-line stubs or bare hashtags without an external article have insufficient facts and cause AI hallucinations
        if len(text) < 110 and not external_links:

            continue



        video_urls = []

        for v_el in msg.select("video.tgme_widget_message_video, video, .tgme_widget_message_roundvideo, .tgme_widget_message_video_player video"):
            if v_el.find_parent(class_=["tgme_widget_message_reply", "tgme_widget_message_link_preview"]):
                continue
            src = v_el.get("src", "").strip()
            if not src:
                for s_el in v_el.select("source"):
                    s_src = s_el.get("src", "").strip()
                    if s_src:
                        src = s_src
                        break
            if src and src.startswith("http") and src not in video_urls:
                video_urls.append(src)

        # If post has a video player (not inside a reply/link preview) but video tag wasn't inlined, fetch embed page
        own_video_players = [
            vp for vp in msg.select(".tgme_widget_message_video_player")
            if not vp.find_parent(class_=["tgme_widget_message_reply", "tgme_widget_message_link_preview"])
        ]
        if not video_urls and own_video_players:
            post_data_id = msg.get("data-post") or ""
            if post_data_id:
                try:
                    embed_resp = http_get(f"https://t.me/{post_data_id}?embed=1")
                    if embed_resp and embed_resp.text:
                        esoup = BeautifulSoup(embed_resp.text, "html.parser")
                        for ev in esoup.select("video"):
                            if ev.find_parent(class_=["tgme_widget_message_reply", "tgme_widget_message_link_preview"]):
                                continue
                            esrc = ev.get("src", "").strip()
                            if esrc and esrc.startswith("http") and esrc not in video_urls:
                                video_urls.append(esrc)
                except Exception:
                    pass

        photo_urls = []
        for wrap in msg.select(".tgme_widget_message_photo_wrap"):
            if "tgme_widget_message_video_thumb" in wrap.get("class", []):
                continue
            if wrap.find_parent(class_=["tgme_widget_message_reply", "tgme_widget_message_link_preview"]):
                continue
            m = BG_URL_RE.search(wrap.get("style", ""))
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
            videos: list[str] = []

            for m_content in item.findall("media:content", ns):

                u = (m_content.get("url") or "").strip()
                m_type = (m_content.get("type") or "").lower()
                m_med = (m_content.get("medium") or "").lower()

                if u:
                    if "video" in m_type or m_med == "video" or any(u.lower().endswith(ext) for ext in (".mp4", ".mov", ".m4v", ".webm")):
                        if u not in videos:
                            videos.append(u)
                    elif u not in photos:
                        photos.append(u)

            thumb = item.find("media:thumbnail", ns)

            if thumb is not None and thumb.get("url"):

                u = thumb.get("url", "").replace("/standard/240/", "/standard/976/")

                if u not in photos:

                    photos.append(u)

            enc = item.find("enclosure")

            if enc is not None and enc.get("url"):

                u = enc.get("url", "").strip()
                enc_type = (enc.get("type") or "").lower()

                if "video" in enc_type or any(u.lower().endswith(ext) for ext in (".mp4", ".mov", ".m4v", ".webm")):
                    if u not in videos:
                        videos.append(u)
                elif "image" in enc_type or not enc_type:
                    if u not in photos:
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
                        "video_urls": videos[:2],

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

        "karakalpakstan": 25,

        "citizen_uzbekistan": 20,

        "world": 20,

        "world_tech": 15

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

        if src in DISCOURAGED_SOURCES or any(d in src for d in ["kun.uz"]):

            score -= 100000.0  # Heavily penalize overused aggregators

        elif src in AUTHENTIC_SOURCES or any(a in src for a in ["nasa", "nature", "reuters", "bbc", "guardian", "techcrunch", "uza.uz", "xaliq_ushin", "joqargikenes", "qresministrlerkenesi", "qrprokuratura", "qrsudlari", "nukus_press"]):

            score += 50000.0   # Heavily boost primary authentic sources

        # Priority boost for verified videos to maximize channel interactivity & forward rates!
        if c.get("video_urls"):
            score += 40000.0

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

            is_discouraged = src in DISCOURAGED_SOURCES or any(d in src for d in ["kun.uz"])

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

    "kknews.uz", "kknews_uz", "kknews",

    "karpressa", "karpress",

    "karinform"

}



AUTHENTIC_SOURCES = {

    "joqargikenes", "qresministrlerkenesi", "qrprokuratura", "qrsudlari",

    "nukus_press", "qonirat_press", "moynaq_press", "shimbayrk", "turtkulhokim_uz",

    "xodjeyli_rk", "presstaqiyatas", "kanlikulnews", "beruniy_press", "kegeyli_press",

    "taxtakopir_press", "ellikqala_press", "qaraozek_press", "shomanay_press", "bozataw_press",

    "krbajixana", "kkeduuz", "jaslar_isleri_agentligi", "xaliq_ushin",

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

    payload = {"text": text, "target_script": "latin", "model": "auto"}

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





QR_CATEGORY_REGEX = re.compile(

    r"(?i)\b(qaraqalpaq|qaraqalpaqstan|nókis|nokis|nukus|qońırat|qonirat|moynaq|xojeli|shimbay|"

    r"taqıyatas|beruniy|tórtkúl|tortkul|bozataw|qanlıkól|kegeyli|taxtakópir|ellikqala|qaraózek|"

    r"ámiwdárya|amiwdarya|joqarǵı keńes|joqargi kenes|ministrler keńesi|aral teńizi|aral|karpress|kknews)\w*"

)



UZ_CATEGORY_REGEX = re.compile(

    r"(?i)\b(ózbekstan|ozbekstan|tashkent|toshkent|húkimet|senat|parlament|samarqand|buxoro|"

    r"andijon|fergana|fargʻona|namangan|qashqadaryo|surxondaryo|jizzax|sirdaryo|navoiy|xorazm|"

    r"oraylıq bank|solıq|pensiya|kadastr|sud|mámleketlik|som|vazirlik)\w*"

)



def strip_post_footer(text: str) -> str:

    """Strips footer from text so channel handle does not falsely trigger QR category on every post."""

    lines = [

        ln for ln in text.split("\n")

        if not (ln.strip().startswith("👉") or "aǵza bolıw" in ln.lower() or "qaraqalpaqsha janaliqlar" in ln.lower() or "qaraqalpaqshajanaliqlar" in ln.lower() or "+ccz2kfdc8Fg1ZGYy" in ln)

    ]

    return "\n".join(lines)



def classify_channel_post(text: str) -> str:

    """Classifies a published post into QR, UZ, or WORLD based on content (excluding footer)."""

    body = strip_post_footer(text)

    if QR_CATEGORY_REGEX.search(body):

        return "QR"

    elif UZ_CATEGORY_REGEX.search(body):

        return "UZ"

    else:

        return "WORLD"



def analyze_last_3_posts_and_get_target(existing_posts: list[str]) -> tuple[str, list[dict[str, Any]], str]:

    """

    Analyzes the last 3 published posts on the channel.

    If QR, UZ, or WORLD is missing from the last 3 posts, returns that missing category as target.

    Priority if multiple missing: QR > UZ > WORLD.

    If all 3 are present, rotates to the oldest of the 3 to maintain smooth cyclic rotation.

    """

    last_3 = existing_posts[:3]

    analysis = []

    cats = []

    for i, p in enumerate(last_3):

        cat = classify_channel_post(p)

        cats.append(cat)

        first_line = p.strip().split("\n")[0] if p else "Post"

        analysis.append({"idx": i + 1, "category": cat, "headline": first_line[:75]})

    

    present = set(cats)

    if "QR" not in present:

        target = "QR"

        reason = "QARAQALPAQSTAN (QR) is missing in the last 3 posts! Mandatory selection."

    elif "UZ" not in present:

        target = "UZ"

        reason = "UZBEKISTAN (UZ) is missing in the last 3 posts! Mandatory selection."

    elif "WORLD" not in present:

        target = "WORLD"

        reason = "WORLD / TECH is missing in the last 3 posts! Mandatory selection."

    else:

        target = cats[-1] if cats else "QR"

        reason = f"All 3 categories present in last 3 posts. Oldest is {target}, continuing smooth rotation."



    return target, analysis, reason




def extract_json_safely(raw: str) -> list[dict[str, Any]]:
    """Robustly parse JSON array or objects from LLM response, with auto-repair for missing commas or markdown."""
    raw = (raw or "").strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw, flags=re.DOTALL).strip()
    
    # 1. Try standard json.loads
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, dict):
            for v in parsed.values():
                if isinstance(v, list):
                    return v
            return [parsed]
        elif isinstance(parsed, list):
            return parsed
    except Exception:
        pass

    # 2. Try regex extraction of outermost [ ... ]
    m = re.search(r'\[\s*\{.*\}\s*\]', raw, re.DOTALL)
    if m:
        try:
            cleaned = re.sub(r',\s*([\]\}])', r'\1', m.group(0))
            parsed = json.loads(cleaned)
            if isinstance(parsed, list):
                return parsed
        except Exception:
            pass

    # 3. Try parsing individual JSON objects { ... }
    objs = []
    for match in re.finditer(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', raw, re.DOTALL):
        try:
            cleaned = re.sub(r',\s*([\]\}])', r'\1', match.group(0))
            obj = json.loads(cleaned)
            if isinstance(obj, dict) and ("headline_ru" in obj or "paragraph1_ru" in obj or "caption_html" in obj or "candidate_idx" in obj):
                objs.append(obj)
        except Exception:
            continue
    if objs:
        return objs

    print("[WARN] extract_json_safely: Failed to parse LLM response. Snippet:", raw[:250])
    return []

def curate_and_write_posts(

    client: genai.Client,

    candidates: list[dict[str, Any]],

    existing_posts: list[str],

    ask_count: int,

    target_category: str = "QR",

    rotation_analysis: list[dict[str, Any]] | None = None,

    rotation_reason: str = "",

) -> list[dict[str, Any]]:

    playbook = Path("TASK_INSTRUCTIONS.md").read_text(encoding="utf-8") if Path("TASK_INSTRUCTIONS.md").exists() else ""



    analysis_json = json.dumps(rotation_analysis or [], ensure_ascii=False, indent=2)

    rotation_mandate = f"""
*** BALANCED 3-PILLAR CURATION MANDATE (QR / UZ / WORLD) ***
The channel @qaraqalpaqshajanaliqlar seeks a rich, balanced mix of:
1. QARAQALPAQSTAN (QR): Official Karakalpakstan news (Joqarg'i Kenes, ministries, agencies, district akimiyats, @xaliq_ushin).
2. O'ZBEKISTON (UZ): Citizen-focused national news covering laws, salaries, pensions, utilities, education, transport, economy.
3. DUNYO & TEXNOLOGIYA (WORLD): High-impact world events, shocking incidents, viral phenomena, consumer AI, smartphones, cars, space, extreme engineering.

PRIORITY DIRECTIVE:
Select the {ask_count} best stories across QR, UZ, and WORLD. If one category has few or no fresh stories at this hour (e.g. late evening/night hours for government press releases), freely fill the full quota of {ask_count} posts from the remaining categories (UZ and WORLD)! NEVER return an empty list or fewer than 5 items when fresh candidates are available!
"""



    prompt = f"""

You are the Editor-in-Chief and Doctor of Karakalpak Philology for the Telegram channel Qaraqalpaqsha jan'aliqlar (@qaraqalpaqshajanaliqlar).



{rotation_mandate}



AUTHENTIC SOURCES ONLY — STRICT DISCOURAGEMENT OF AGGREGATORS & ZERO ADS:

- SOURCING INTEGRITY: Strongly favor primary authentic web portals, official Karakalpakstan media (kknews.uz, KarPressa, xaliq_ushin, joqargikenes), Uzbekistan official gazettes (UzA, gov.uz, ministries), and international science/world wires (NASA, Nature, ScienceDaily, BBC, Reuters, Guardian, TechCrunch). Disfavor repetitive generic aggregators (kun.uz).

- ZERO ADVERTISING: Absolutely NEVER choose commercial advertisements, store discounts, product promos, or sponsored real estate announcements.



{OFFICIAL_KARAKALPAK_ALPHABET_RULES}



STRICT EDITORIAL PLAYBOOK:

{playbook[:5000]}



ALREADY PUBLISHED ON @qaraqalpaqshajanaliqlar (STRICT SEMANTIC DEDUPLICATION — NEVER repeat ANY topic, law, number, person, or event already covered below, even if the URL or source channel is different!):

{json.dumps(existing_posts, ensure_ascii=False, indent=2)}



CANDIDATE STORIES FROM LIVE OFFICIAL & GLOBAL FEEDS:

{json.dumps([{ "idx": i, "url": c["url"], "category": c["category"], "source_name": c["source_name"], "has_photo": bool(c.get("photo_urls")), "has_video": bool(c.get("video_urls")), "text": c["text"][:1000] } for i, c in enumerate(candidates)], ensure_ascii=False, indent=2)}





SOURCE POLICY:

- The candidate list comes from a PRIMARY list of Karakalpak, Uzbek and world Telegram channels + news websites, plus open-web discovery searches (`source_name` = "open-web"). These lists are NOT a limit: every candidate is equally eligible, and open-web items may be chosen when they are the most interesting AND come from a reliable outlet.

- Reliability: prefer official sources, wires and established media. For sensational or unverified claims (deaths, disasters, scandals, health scares) require a reputable source in `source_name`/`url`; never invent or "round up" facts, numbers, names or quotes. If a number is not in the candidate text, do not write it.



EDITORIAL STYLE — "interesting first" (the style of fast, curiosity-driven news channels, NOT of dry bureaucratic reposts):

- Choose stories people will want to read AND forward: accidents and disasters, world events, money and rules that change daily life (prices, fines, tariffs, benefits, deadlines), health and safety warnings, weather changes, science/tech/AI surprises, scholarships and remote jobs, sports tragedies and records, first-in-history facts, strange-but-true stories.

- Treat a weather change, a price/rule change or a safety warning with the SAME weight as a government event. Do NOT pick routine items such as "a meeting was held", ceremonies, delegations, awards/placings of one student or athlete in a minor contest — UNLESS there is a striking angle (first-ever, record, big prize, Karakalpakstan pride, large money, many people affected).

- Mix of topics across the batch: at most ONE routine-official story per batch; at least one story that touches daily life or safety; world/science/tech stories are welcome in every batch.

- MANDATORY SOURCE DIVERSITY: You MUST pick candidates from completely DIFFERENT sources! Diversify across Karakalpakstan district/regional channels, Uzbekistan official ministries/legal portals (lex.uz, huquqiyaxborot, gov.uz), and World/Tech outlets. NEVER pick multiple stories from the same news outlet!



MANDATORY JOURNALISTIC MULTI-PARAGRAPH HOOK & INTERACTIVE TEMPLATE (STRICTLY REQUIRED):

Every single post MUST be structured as a compelling multi-paragraph journalistic story with an interactive reader engagement question (like @EVENT24.uz / @quloqnews):



[Model Structure Example 1 — Tech/Business/Lifestyle]:

🛍 <b>Яндекс закрывает свой маркетплейс в Узбекистане, не продержавшись и двух лет</b>



С 10 ноября Market Yandex Go перестанет принимать заказы. Сервис запустился в апреле 2025 года, но компания решила сосредоточиться на Yandex Lavka и разделе «Магазины» с быстрой доставкой, <a href="EXACT_CANDIDATE_URL">сообщили</a> в пресс-службе.



А вы хоть раз заказывали что-нибудь через Market Yandex Go? Или даже не знали о его существовании?



👉 <a href="https://t.me/qaraqalpaqshajanaliqlar">Qaraqalpaqsha jańalıqlar — aǵza bolıw</a>



[Model Structure Example 2 — Sports/World/Discovery]:

🇵🇹 <b>Криштиану Роналду объявил о завершении карьеры в сборной Португалии</b>



41-летний нападающий саудовского «Аль-Насра» <a href="EXACT_CANDIDATE_URL">объявил</a> об уходе из национальной команды в Instagram, опубликовав большое видео. «Португалия навсегда останется во мне», — написал футболист. Роналду дебютировал за сборную 20 августа 2003 года в товарищеском матче против Казахстана и за 234 встречи забил 146 голов.



В составе сборной Роналду выиграл Евро-2016 и дважды Лигу наций УЕФА. Как думаете, сможет ли кто-нибудь в ближайшие десятилетия побить его рекорд?



👉 <a href="https://t.me/qaraqalpaqshajanaliqlar">Qaraqalpaqsha jańalıqlar — aǵza bolıw</a>



CRITICAL FORMATTING INSTRUCTIONS (MAINTAIN PROFESSIONAL BALANCE — DO NOT OVERDO EMOJIS OR QUESTIONS):

1. LEAD HEADLINE:

   - Use Country Flag ONLY if the story is directly related to a specific country (e.g. 🇵🇹, 🇺🇿, 🇰🇿, 🇨🇳, 🇺🇸).

   - If not a country story, use a single fitting icon ONLY when truly natural, or LEAVE EMPTY ("") for formal news. DO NOT force emojis on every post!

   - Headline in bold: <b>Заголовок на русском</b>. Followed by a blank line (\n\n).

2. PARAGRAPH 1 (Core News + Hook Details):

   - Rich factual storytelling with exact ages, dates, club/agency names, quotes in «...», and numbers/stats.

   - Embed the exact direct source link ONTO ONE natural action verb or keyword before the period: e.g. <a href="EXACT_CANDIDATE_URL">объявил</a> or <a href="EXACT_CANDIDATE_URL">сообщили</a>. Followed by a blank line (\n\n).

3. PARAGRAPH 2 (Context, Background & Significance):

   - Context, historical background, significance, or next steps.

   - INTERACTIVE QUESTIONS: USE VERY SPARINGLY (only in ~20% of posts where truly organic, e.g. consumer opinions on a new app). In standard news (official laws, economics, science, accidents, announcements), DO NOT force questions! A purely informative conclusion is often much better and more professional.

4. STRICT: ZERO BULLET POINTS! Absolutely NEVER use bullet lists (🔹, ▪️, ➖, •, etc.)! Everything must be fluent, engaging narrative prose.

5. STRICT: NO EXTERNAL MEDIA NAMES & NO SEPARATE SOURCE LINE!
   - Absolutely NEVER mention foreign or domestic media names (e.g. "Futurism", "The Guardian", "BBC", "Nexta", "Gazeta.uz", "Kun.uz", "сообщает издание...", "dep xabar beredi...")!
   - Report facts directly and authoritatively without crediting outside websites or publications.
   - All links must be embedded ONLY onto natural action verbs under the headline/spotlight (e.g. <a href="EXACT_CANDIDATE_URL">сообщил</a>, <a href="EXACT_CANDIDATE_URL">заявил</a>, <a href="EXACT_CANDIDATE_URL">разрабатывает</a>).
   - Absolutely NEVER output bare parenthetical homepages like `(https://lex.uz/)` or `(https://www.ramsar.org/)`!

6. CLOSING FOOTER:

👉 <a href="https://t.me/qaraqalpaqshajanaliqlar">Qaraqalpaqsha jańalıqlar — aǵza bolıw</a>

7. STRICT ZERO HALLUCINATION MANDATE (ABSOLUTE TRUTH & GROUNDING):
   - You must NEVER invent or hallucinate statements, quotes, official reactions ("представители ведомства сообщили", "dep málim etti basqarma wákilleri", "мутасаддилар билдирди"), reasons ("это стало возможным благодаря труду дехкан"), or background facts that DO NOT exist in the candidate's text!
   - Every single claim, quote, number, name, and cause MUST be 100% grounded in the candidate's provided text.
   - If a source candidate text is short, KEEP THE POST SHORT AND 100% FACTUAL! DO NOT artificially pad, fluff, or invent stories to inflate character count.
   - Factual truth and accuracy STRICTLY override length! A truthful 250-character post is infinitely better than a 500-character post with invented official statements.
   - Typical length: between 300 and 700 characters (or shorter if the original source is brief).



YOUR TASK:

1. Select EXACTLY {ask_count} completely NEW, non-duplicate, most interesting stories following the style above.
   - MANDATORY BACKUP CANDIDATES: Your JSON response array MUST contain AT LEAST 3 (ideally {ask_count}) distinct stories! Even if TARGET CATEGORY is QR, if there are only 1 or 2 QR stories available in candidates, fill the remaining slots with UZ and WORLD stories so there are ALWAYS healthy backup stories ready to publish! NEVER return an array with only 1 story!

   - Double-check against ALREADY PUBLISHED ON @qaraqalpaqshajanaliqlar: if a story is about the same event/law (e.g. 350 kVt electricity limit, 4-day parent school holiday leave, Nukus Chemistry Olympiad, Cannavaro, Asian Cup 2027, Swiss Ambassador at School #34, China Eastern Airlines), SKIP IT!

   - DYNAMIC VIDEO & PHOTO PRIORITY: If a candidate has `has_video: true`, STRONGLY FAVOR selecting it when relevant to the target category! Videos generate 2-3x higher user engagement, watch time, and forwards. Otherwise prefer candidates where `has_photo` is true.

2. Write each caption in fluent, crystal-clear, factual RUSSIAN following the exact 2-paragraph hook structure above (it will be translated into 100% pure Karakalpak Latin via our dedicated neural translation API).



STRICT FACTUAL INTEGRITY & CONTENT BAN:

- ABSOLUTE ZERO HALLUCINATION: You are FORBIDDEN from inventing facts, statistics, reasons, or quotes from officials/spokespeople that do not exist in the candidate text.
- DO NOT select candidates that are mere stubs or 1-line video tags lacking factual substance (less than ~100 chars of actual facts), because they lack sufficient information to write an accurate, non-hallucinated post.
- NEVER select or write about rape, sexual violence, sexual assault, pedophilia, or sexual crimes! (Military wars, armed conflicts, and accidents are allowed, but ALL sexual violence/rape is STRICTLY FORBIDDEN).
- STRICT BAN ON NICHE / DEEP SPECIALIZED ACADEMIC & ASTRONOMY TOPICS:
  * Absolutely NEVER select routine astronomy or amateur stargazing: meteor showers (Leonids, Perseids, Geminids, Lyrid meteor streams, "звездопад", "метеорный поток"), minor comet designations (55P/Tempel-Tuttle, etc.), routine asteroid passings, planetary alignments, or night-sky viewing calendars. The channel audience consists of general public readers, NOT professional astronomers!
  * Absolutely NEVER select narrow, esoteric laboratory micro-research: experiments on mice/rats, fruit fly genetics, cellular microbiology, abstract theoretical physics, quantum equations, or obscure fossil descriptions that only a narrow academic specialist would care about.
  * Science and tech MUST be globally impactful, viral, visually astonishing, or directly useful to everyday people (e.g., consumer AI products like ChatGPT, humanoid robots, Tesla/self-driving cars, smartphones, life-saving medical treatments, massive rocket launches like SpaceX Starship, extreme physical engineering demos). If a story requires a university degree in astrophysics or molecular biology to find interesting, REJECT IT IMMEDIATELY!



Return ONLY a JSON array of objects with keys:

- "candidate_idx": integer (MUST match the exact `idx` of the story you wrote about!)

- "source_url": string (MUST equal `candidates[candidate_idx]["url"]`!)

- "lead_emoji": string (Country flag if country-specific e.g. 🇺🇿, 🇵🇹, 🇰🇿, 🇨🇳, or single fitting icon, or empty string "" if formal/serious)

- "headline_ru": string (Engaging hook headline in Russian, plain text, NO emoji, NO tags)

- "paragraph1_ru": string (Paragraph 1 in Russian: core event details, ages, dates, quotes in «...», exact numbers)

- "paragraph2_ru": string (Paragraph 2 in Russian: context, background, and ONLY IF truly organic, a reader question; otherwise factual conclusion)

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
    parsed = extract_json_safely(raw)

    if not parsed:
        print("[FALLBACK CURATION] Model returned empty list. Retrying with permissive top-candidate fallback...")
        fallback_prompt = f"""You are the Editor of Telegram channel Qaraqalpaqsha jan'aliqlar.
Select the top {ask_count} most interesting, important, or viral stories from the candidate list below.
Return ONLY a valid JSON array of objects with keys:
- "candidate_idx": integer
- "source_url": string
- "lead_emoji": string
- "headline_ru": string
- "paragraph1_ru": string
- "paragraph2_ru": string
- "wikimedia_search_keywords": string

Candidates:
""" + "\n".join(f"[{c['idx']}] {c.get('source_name','')}: {c.get('title','')[:100]} | {c.get('text','')[:250]}" for c in candidates[:ask_count*2])
        try:
            resp_fb = generate_content_with_fallback(
                client,
                DRAFT_MODELS,
                fallback_prompt,
                types.GenerateContentConfig(response_mime_type="application/json", temperature=0.3),
            )
            parsed = extract_json_safely(resp_fb.text or "")
            print(f"[FALLBACK CURATION] Fallback successfully recovered {len(parsed)} curated posts!")
        except Exception as fb_exc:
            print(f"[FALLBACK CURATION] Fallback exception: {fb_exc}")

    print(f"[TRANSLATOR] Translating {len(parsed)} curated posts into Karakalpak via {KARAKALPAK_TRANSLATOR_API_URL}...")

    valid_items = []

    for it in parsed:

        lead_emoji = it.get("lead_emoji") or "⚡️"

        headline_ru = (it.get("headline_ru") or "").strip()

        p1_ru = (it.get("paragraph1_ru") or "").strip()

        p2_ru = (it.get("paragraph2_ru") or "").strip()



        # Backward compatibility fallback if model outputs caption_html

        if not headline_ru and it.get("caption_html"):

            raw_cap = it["caption_html"]

            parts = [p.strip() for p in raw_cap.split("\n\n") if p.strip()]

            if parts:

                headline_ru = re.sub(r'<[^>]+>', '', parts[0]).strip()

                p1_ru = parts[1] if len(parts) > 1 else ""

                p2_ru = parts[2] if len(parts) > 2 else ""



        if not headline_ru or not p1_ru:

            print(f"[SKIP] Post idx #{it.get('candidate_idx')} missing headline or paragraph1.")

            continue

        # Strip any raw HTML tags before sending to Tilmoch neural translator so tags are never mangled
        clean_headline_ru = re.sub(r"<[^>]+>", "", headline_ru).strip()
        clean_p1_ru = re.sub(r"<[^>]+>", "", p1_ru).strip()
        clean_p2_ru = re.sub(r"<[^>]+>", "", p2_ru).strip() if p2_ru else ""

        print(f"[TRANSLATE_API] Translating candidate #{it.get('candidate_idx')} components via Tilmoch...")

        tr_headline = translate_post_via_custom_api(clean_headline_ru, timeout=30, retries=2)

        if not tr_headline:

            print(f"[SKIP] Post idx #{it.get('candidate_idx')} SKIPPED because headline translation failed.")

            continue



        tr_p1 = translate_post_via_custom_api(clean_p1_ru, timeout=45, retries=2)

        if not tr_p1:

            print(f"[SKIP] Post idx #{it.get('candidate_idx')} SKIPPED because paragraph 1 translation failed.")

            continue



        tr_p2 = ""

        if clean_p2_ru:

            tr_p2 = translate_post_via_custom_api(clean_p2_ru, timeout=45, retries=2) or ""



        # Clean headline

        clean_headline = re.sub(r'^[^\w\s]+', '', tr_headline).strip().rstrip(".")

        clean_headline = re.sub(r'<[^>]+>', '', clean_headline).strip()



        lead_str = f"{lead_emoji} " if lead_emoji.strip() else ""

        body_parts = [

            f"{lead_str}<b>{clean_headline}</b>",

            tr_p1.strip()

        ]

        if tr_p2.strip():

            body_parts.append(tr_p2.strip())



        constructed_cap = "\n\n".join(body_parts)
        it["caption_html"] = constructed_cap

        # Verify and resolve exact candidate (auto-correcting any off-by-one candidate_idx/source_url)
        matched_cand = resolve_candidate_for_item(it, candidates)
        if matched_cand:
            exact_url = matched_cand.get("url") or matched_cand.get("fallback_post_url") or ""
            it["source_url"] = exact_url
        else:
            exact_url = it.get("source_url") or ""

        # Inject direct source link into paragraph 1 and append standardized footer
        constructed_cap = format_caption_with_direct_source_link(constructed_cap, exact_url)



        it["caption_html"] = constructed_cap

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

2. "fact_and_grounding_audit":
   Check if the text contains any fabricated official claims or padding (e.g. "dep málim etti basqarma wákilleri", "arqasında múmkin boldı") that were not substantiated by facts. Strip out invented quotes or fluff!

3. "linguistic_audit" (MANDATORY CHAIN-OF-THOUGHT):

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

   - PRESERVE exact numbers, dates, names, quotes «...», and embedded links intact!

   - PRESERVE the EXACT 2-paragraph narrative layout (\n\n between Headline, Paragraph 1, Paragraph 2, and Footer). NEVER collapse the paragraphs into a single text block!

   - PRESERVE the closing link intact: 👉 <a href="https://t.me/qaraqalpaqshajanaliqlar">Qaraqalpaqsha jańalıqlar — aǵza bolıw</a>



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

                    # Enforce that headline is bold and double newlines exist

                    if "<b>" not in new_cap:

                        lines = [ln.strip() for ln in new_cap.split("\n") if ln.strip()]

                        if lines:

                            first_line = lines[0]

                            m = re.match(r"^([^\w\s]+\s*)(.*)$", first_line)

                            if m:

                                lines[0] = f"{m.group(1)}<b>{m.group(2).rstrip('.')}</b>"

                            else:

                                lines[0] = f"<b>{first_line.rstrip('.')}</b>"

                            new_cap = "\n\n".join(lines)

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






def repair_rogue_capital_i(text: str) -> str:
    """
    Bulletproof defense: Repairs stray capital 'I' letters introduced by upstream translation APIs.
    - Preserves standard acronyms: IIV, IIO, AQSh, BMSh, GFR, ÓzA, etc.
    - Preserves valid word-initial 'I': Isa, Ilim, Iras, etc.
    - Converts mid/end-word 'I' to 'ı' (back vowel words) or 'i' (front vowel words).
    """
    FRONT_VOWELS = set('eióúáEÍÓÚÁ')
    BACK_VOWELS = set('aouıAOUÍ')

    def fix_word(match):
        word = match.group(0)
        if word.isupper() and len(word) <= 5:
            return word
        if 'I' not in word:
            return word

        has_front = any(ch in FRONT_VOWELS for ch in word.replace('I', ''))
        has_back = any(ch in BACK_VOWELS for ch in word.replace('I', ''))

        if has_front and not has_back:
            safe_vowel = 'i'
        elif has_back and not has_front:
            safe_vowel = 'ı'
        else:
            safe_vowel = None

        chars = list(word)
        for idx, ch in enumerate(chars):
            if ch == 'I':
                if idx == 0 and len(chars) > 1 and chars[1].islower():
                    continue
                target_v = safe_vowel
                if not target_v:
                    prev_v = None
                    for b_idx in range(idx - 1, -1, -1):
                        if chars[b_idx].lower() in 'eióúá':
                            prev_v = 'i'; break
                        elif chars[b_idx].lower() in 'aouı':
                            prev_v = 'ı'; break
                    next_v = None
                    for f_idx in range(idx + 1, len(chars)):
                        if chars[f_idx].lower() in 'eióúá':
                            next_v = 'i'; break
                        elif chars[f_idx].lower() in 'aouı':
                            next_v = 'ı'; break
                    target_v = prev_v or next_v or 'ı'
                chars[idx] = target_v

        return "".join(chars)

    parts = re.split(r"(<[^>]+>)", text)
    out = []
    for part in parts:
        if part.startswith("<") and part.endswith(">"):
            out.append(part)
        else:
            repaired = re.sub(r"[a-zA-ZáóúıǵńÁÓÚIǴŃ]+", fix_word, part)
            out.append(repaired)
    return "".join(out)


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

    joined = "".join(out)
    return repair_rogue_capital_i(joined)





STANDARD_FOOTER = '👉 <a href="https://t.me/qaraqalpaqshajanaliqlar">Qaraqalpaqsha jańalıqlar — aǵza bolıw</a>'



def ensure_single_footer(text: str) -> str:

    """Strips all duplicate footers and ensures strictly ONE footer at the end."""

    lines = text.split("\n")

    cleaned_lines = []

    for line in lines:

        stripped = line.strip()

        if stripped.startswith("👉") or "aǵza bolıw" in stripped.lower() or "t.me/qaraqalpaqshajanaliqlar" in stripped.lower() or "t.me/+ccz2kfdc8Fg1ZGYy" in stripped.lower():

            continue

        cleaned_lines.append(line)

    cleaned = "\n".join(cleaned_lines).rstrip()

    return cleaned + "\n\n" + STANDARD_FOOTER



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

    caption = ensure_single_footer(caption)

    return caption





# ======================================================================================

# PRE-PUBLISH PHILOLOGY & DIRECT URL AUDITOR (Zero-Tolerance Error Gate)

# ======================================================================================

FORBIDDEN_ROOTS_CHECK = [
    # Anti-Uzbekism & High Frequency News Fixes
    (r"\bhosil\b", "ónim"),
    (r"\byutug['’‘`]?i\b", "tabısı"),
    (r"\byutuq\b", "tabıs"),
    (r"\bloyih?a\b", "joybar"),
    (r"\btadbir\b", "ilaj"),
    (r"\btadbirkor\b", "isbilermen"),
    (r"\biqtisodiyot\b", "ekonomika"),
    (r"\biqtisodiy\b", "ekonomikalıq"),
    (r"\b(t|T)ibbiyot\b", "medicina"),
    (r"\b(t|T)ibbiyotta\b", "medicinada"),
    (r"\b(t|T)ibbiy\b", "medicinalıq"),
    (r"\bkeseliklerge\b", "keselliklerge"),
    (r"\bkeselik\b", "kesellik"),
    (r"\bnatija\b", "nátiyje"),
    (r"\bfuqaro\b", "puqara"),
    (r"\bpuxara\b", "puqara"),
    (r"\btunda\b", "túnde"),
    (r"\bkecha\b", "keshe"),
    (r"\bertaga\b", "erteń"),
    (r"\byordam\b", "járdem"),
    (r"\bshuningdek\b", "sonday-aq"),
    (r"\bmasala\b", "másele"),
    (r"\bqaror\b", "qarar"),
    (r"\bhukumat\b", "húkimet"),
    (r"\bshifokor\b", "shıpaker"),
    (r"\bkasalxona\b", "emlewxana"),
    (r"\bdorixona\b", "dárixana"),
    (r"\bqurilish\b", "qurılıs"),
    (r"\bta['’‘`]?lim\b", "bilimlendiriw"),
    (r"\bjarima\b", "járiyma"),
    (r"\bmatbuot xizmati\b", "málimleme xızmeti"),
    (r"\bqollanǵan\b", "paydalanǵan"),
    (r"\bqollanıp\b", "paydalanıp"),
    (r"\bkómeklesetuǵının\b", "járdem beretuǵının"),
    (r"\bsherik-tiykarlawshısı\b", "tiykarshılarınıń biri"),
    (r"\burlaw\b", "urlıq qılıw"),


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



    # Strip any bullet markers at line starts

    caption = re.sub(r'(?m)^[\s]*[🔹▪️➖•–—]\s*', '', caption)



    # Strip any redundant Derek/Tolıq maǵlıwmat lines

    caption = re.sub(r'(?i)\n*Tolıq\s+maǵlıwmat(?:lar)?(?:\s+(?:ushın|bul jerde))?[.:]?', '', caption)

    caption = re.sub(r'(?i)\n*🔗\s*(?:Derek|Tolıq maǵlıwmat)[^\n]*', '', caption)

    caption = re.sub(r'(?i)\n*Derek\s*:[^\n]*', '', caption)



    # Strip any broken bare parenthetical URLs (e.g. (https://lex.uz/) or (https://www.ramsar.org/))
    caption = re.sub(r'\s*\(\s*https?://[a-zA-Z0-9.\-_/]+\s*\)', '', caption)

    # If PQ-393 is mentioned, ensure it links to the exact Lex.uz document rather than home page
    if "393" in caption and "lex.uz/docs" not in caption:
        caption = re.sub(
            r'(?i)("?PQ-393-sanl[ıi]\s+qarar[ıi]nda"?|"?PQ-393-sanl[ıi]\s+qarar[ıi]"?)',
            r'<a href="https://lex.uz/docs/-8575723">\1</a>',
            caption,
            count=1
        )

    # 1. Unwrap any links previously attached to media or source names
    soup = BeautifulSoup(caption, "html.parser")
    for a in soup.find_all("a"):
        href = a.get("href", "")
        if "qaraqalpaqshajanaliqlar" not in href and "+ccz2kfdc8Fg1ZGYy" not in href:
            txt = a.get_text().strip().lower()
            if any(w in txt for w in ["basılımı", "baspası", "xızmeti", "jámiyetshilik", "guardian", "futurism", "bbc", "xızmetkerler"]):
                a.unwrap()
    caption = str(soup)

    # 2. Strip external media mentions like 'dep xabar beredi Futurism baspası' or ', dep xabar berdi The Guardian'
    media_pat = r'(?i),\s*dep\s+xabar\s+(?:beredi|berdi|berildi|berilmekte)\s+[a-zA-Z0-9áóúıǵńÁÓÚIǴŃ\s.\-_]+?(?:\s+(?:baspas[ıi]|bas[ıi]l[ıi]m[ıi]|x[ıi]zmeti|j[aá]miyetshilik|x[ıi]zmetkerler|sayt[ıi]|kanal[ıi]|agentligi))?(\.)'
    caption = re.sub(media_pat, r'\1', caption)
    media_pat2 = r'(?i)\s+dep\s+xabar\s+(?:beredi|berdi|berildi|berilmekte)\s+[a-zA-Z0-9áóúıǵńÁÓÚIǴŃ\s.\-_]+?(?:\s+(?:baspas[ıi]|bas[ıi]l[ıi]m[ıi]|x[ıi]zmeti|j[aá]miyetshilik|x[ıi]zmetkerler|sayt[ıi]|kanal[ıi]|agentligi))?(\.)'
    caption = re.sub(media_pat2, r'\1', caption)

    # 3. Ensure clean \n\n after </b> headline
    caption = re.sub(r'(</b>)\s*\n(?!\n)', r'\1\n\n', caption)

    # 4. Separate headline (Spotlight) from body so headline stays clean and links only go under spotlight
    if "</b>" in caption:
        head_part, sep, body_part = caption.partition("</b>")
    else:
        head_part, sep, body_part = "", "", caption

    # Clean any accidental link from headline
    head_part = re.sub(r'</?a[^>]*>', '', head_part)

    # Check if external link already exists in body
    soup_body = BeautifulSoup(body_part, "html.parser")
    has_external_link = False
    for a in soup_body.find_all("a"):
        href = a.get("href", "")
        if "qaraqalpaqshajanaliqlar" not in href and "+ccz2kfdc8Fg1ZGYy" not in href and "janaliqjanaliq" not in href:
            if not a.get_text().strip():
                a.unwrap()
                continue
            a["href"] = exact_url
            has_external_link = True
            break

    body_part = str(soup_body)

    if not has_external_link:
        # Try prominent focus verbs & announcements strictly under spotlight (in body)
        focus_verbs = [
            r"\b(juwmaqlaw múddetlerin|málim etti|málim qılındı|málimleme berdi|xabar berildi|xabar berilmekte|xabarladı|eskertti|kútilmekte|engiziledi|engizildi|tastıyıqlandı|belgilendi|aytıp ótti|iske qospaqshı|iske qosıldı|payda boladı|ashıldı|shólkemlestirildi|júzege asırıldı|start berildi|jolǵa qoyıldı|kórsetpekte|baqlay aladı|imkaniyatına iye boladı|satıp alıwǵa boladı)\b"
        ]
        wrapped_body = False
        for pat in focus_verbs:
            m = re.search(pat, body_part, flags=re.IGNORECASE)
            if m:
                target_word = m.group(1).rstrip(".,;:!?")
                body_part = body_part[:m.start()] + f'<a href="{exact_url}">{target_word}</a>' + body_part[m.start() + len(target_word):]
                wrapped_body = True
                break

        # If not matched, wrap the main verb of the first sentence before period
        if not wrapped_body:
            sentence_verb_match = re.search(r'([a-zA-ZáóúıǵńÁÓÚIǴŃ]{4,})(\s*\.)', body_part)
            if sentence_verb_match:
                verb = sentence_verb_match.group(1)
                body_part = body_part[:sentence_verb_match.start(1)] + f'<a href="{exact_url}">{verb}</a>' + body_part[sentence_verb_match.end(1):]
                wrapped_body = True

    caption = head_part + sep + body_part



    # Guarantee strictly ONE single footer

    caption = ensure_single_footer(caption)



    # Normalize excessive newlines (max 2)

    caption = re.sub(r'\n{3,}', '\n\n', caption)



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



    # 4.5 Ensure bold headline tag and multi-paragraph separation are NEVER lost

    if "<b>" not in caption:

        lines = [ln.strip() for ln in caption.split("\n") if ln.strip()]

        if lines:

            first_line = lines[0]

            m = re.match(r"^([^\w\s]+\s*)(.*)$", first_line)

            if m:

                lines[0] = f"{m.group(1)}<b>{m.group(2).rstrip('.')}</b>"

            else:

                lines[0] = f"<b>{first_line.rstrip('.')}</b>"

            caption = "\n\n".join(lines)



    # 5. STRICT URL & FOCUS LINK ENFORCER: Inject exact direct source link to focus keyword and footer

    exact_url = cand.get("url") or cand.get("fallback_post_url") or ""

    source_name = cand.get("source_name") or ""

    if exact_url:

        caption = format_caption_with_direct_source_link(caption, exact_url, source_name)



    # 6. Signature assurance (strictly ONE clean footer)

    caption = ensure_single_footer(caption)



    # 7. Length and alphabet validation

    visible_text = BeautifulSoup(caption, "html.parser").get_text()

    if len(visible_text) > 1015 or len(visible_text) < 120:

        print(f"[AUDIT] Visible caption length out of bounds ({len(visible_text)} chars)")

        return None

        

    if CYRILLIC_RE.search(visible_text):

        print(f"[AUDIT] Unmapped Cyrillic still present, rejecting: {CYRILLIC_RE.findall(visible_text)}")

        return None



    return caption





RU_STOP_STEMS = {
    "котор", "через", "после", "также", "будет", "время", "этого", "между",
    "очень", "более", "около", "из-за", "могут", "чтобы", "когда", "только",
    "своей", "своег", "новых", "новый", "новая", "стали", "стало",
}


def _score_candidate_content_match(item: dict[str, Any], cand: dict[str, Any]) -> float:
    """Compute lexical & numeric overlap score between drafted item and candidate text to prevent LLM index/URL shifts."""
    cand_raw = f"{cand.get('title', '')} {cand.get('text', '')} {cand.get('url', '')}"
    cand_lower = cand_raw.lower()
    cand_latin = transliterate_and_fix_outside_tags(cand_raw).lower()

    item_ru = f"{item.get('headline_ru', '')} {item.get('paragraph1_ru', '')} {item.get('paragraph2_ru', '')}".lower()
    item_cap = strip_post_footer(BeautifulSoup(item.get("caption_html", "") or "", "html.parser").get_text(" ", strip=True)).lower()
    kw_raw = item.get("wikimedia_search_keywords") or ""
    if isinstance(kw_raw, (list, tuple, set)):
        kw_raw = " ".join(str(x) for x in kw_raw)
    item_kw = str(kw_raw).lower()

    score = 0.0

    # 1. Exact numbers overlap (e.g., 38, 148, 362, 250, 191)
    item_nums = {n for n in re.findall(r"\b\d+\b", f"{item_ru} {item_cap}") if n not in ("2026", "2025", "1", "2", "3")}
    cand_nums = set(re.findall(r"\b\d+\b", cand_lower))
    shared_nums = item_nums & cand_nums
    score += len(shared_nums) * 3.0

    # 2. Cyrillic stem overlap (for Russian / Uzbek Cyrillic / Karakalpak Cyrillic candidates)
    ru_words = re.findall(r"[а-яёқғўҳәөүң]{4,}", item_ru)
    ru_stems = {w[:5] for w in ru_words if w[:5] not in RU_STOP_STEMS}
    for st in ru_stems:
        if st in cand_lower:
            score += 2.0

    # 3. Latin / English / Transliterated stem overlap
    lat_source = f"{item_cap} {transliterate_and_fix_outside_tags(item_ru).lower()} {item_kw}"
    lat_words = re.findall(r"[a-záóúıǵń]{4,}", lat_source)
    lat_stems = {w[:5] for w in lat_words if w[:5] not in STOP_STEMS and w[:6] not in STOP_STEMS}
    for st in lat_stems:
        if st in cand_latin or st in cand_lower:
            score += 1.5

    return score


def resolve_candidate_for_item(item: dict[str, Any], candidates: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Match candidate by source_url/candidate_idx AND verify content overlap so LLM off-by-one shifts NEVER attach the wrong video/photo!"""
    direct_cand: dict[str, Any] | None = None

    src_url = normalize_url(item.get("source_url") or "")
    if src_url:
        for c in candidates:
            if normalize_url(c["url"]) == src_url or normalize_url(c.get("fallback_post_url", "")) == src_url:
                direct_cand = c
                break

    if not direct_cand:
        cap = item.get("caption_html") or ""
        for m in re.findall(r'href="([^"]+)"', cap):
            nm = normalize_url(m)
            if "t.me/qaraqalpaqshajanaliqlar" in nm or "+ccz2kfdc8Fg1ZGYy" in m or "janaliqjanaliq" in nm:
                continue
            for c in candidates:
                if normalize_url(c["url"]) == nm or normalize_url(c.get("fallback_post_url", "")) == nm:
                    direct_cand = c
                    break
            if direct_cand:
                break

    if not direct_cand:
        idx = item.get("candidate_idx")
        if isinstance(idx, int) and 0 <= idx < len(candidates):
            direct_cand = candidates[idx]

    # Score all candidates against the drafted item's actual text/numbers/entities
    best_cand: dict[str, Any] | None = None
    best_score = -1.0
    for c in candidates:
        sc = _score_candidate_content_match(item, c)
        if sc > best_score:
            best_score = sc
            best_cand = c

    if direct_cand is not None:
        direct_score = _score_candidate_content_match(item, direct_cand)
        # If another candidate matches the story text much better (LLM shifted candidate_idx/source_url):
        if best_cand is not None and best_cand is not direct_cand:
            if (direct_score < 2.0 and best_score >= 4.0) or (best_score >= 6.0 and best_score > direct_score * 3.0):
                print(
                    f"[CAND-FIX] Corrected LLM candidate mismatch! "
                    f"Was {direct_cand.get('url')} (score={direct_score:.1f}) -> "
                    f"Fixed to {best_cand.get('url')} (score={best_score:.1f})"
                )
                item["source_url"] = best_cand.get("url") or ""
                return best_cand
        # If direct_cand has Cyrillic text (same script as headline_ru) yet has 0.0 overlap with the drafted story:
        if direct_score == 0.0 and re.search(r"[а-яА-ЯёЁ]", direct_cand.get("text", "")):
            print(f"[CAND-REJECT] Candidate {direct_cand.get('url')} has 0.0 content overlap with drafted text! Rejecting mismatch.")
            return best_cand if best_score >= 4.0 else None
        return direct_cand

    if best_cand is not None and best_score >= 4.0:
        item["source_url"] = best_cand.get("url") or ""
        return best_cand

    return None


def verify_photo_clean_and_relevant(
    client: genai.Client, img_bytes: bytes, story_summary: str
) -> bool:
    """Inspect candidate image via PIL + Gemini Vision to reject watermarks, channel logos, banners, document tables, or mismatched scenes."""
    try:
        with Image.open(io.BytesIO(img_bytes)) as im:
            w, h = im.size
            if w < 550 or h < 340:
                print(f"[INFO] Photo rejected by dimensions ({w}x{h} < 550x340)")
                return False
            ratio = w / float(h)
            if ratio < 0.65 or ratio > 2.4:
                print(f"[INFO] Photo rejected by aspect ratio ({ratio:.2f})")
                return False
    except Exception:
        return False

    try:
        check_prompt = (
            f"News post text:\n{story_summary[:500]}\n\n"
            "Inspect this image strictly as a senior photo editor and return JSON {\"ok\": true/false, \"reason\": \"...\"}.\n"
            "Set \"ok\": false if ANY of these apply:\n"
            "1) It contains ANY Telegram channel logo, watermark, handle (@...), website logo/url, or third-party media badge anywhere on the image (e.g. @KARAKALPAK24, @xaliq_ushin, @kunuzofficial, @KarPressa, @qalampir, @daryo, kun.uz, gazeta.uz, uza.uz, etc.).\n"
            "2) It has big promotional/template banner text or news headlines written on top of the image (e.g. 'SHOSHILINCH', 'RASMIY XABAR', 'TEZKOR', 'DIQQAT', 'MÚNÁSIBET', 'E\\'LON', 'RADDİYA').\n"
            "3) It is a screenshot of a text document, table, spreadsheet, decree/resolution table, PDF page, or chart with small text.\n"
            "4) It is a generic website logo, coat of arms/emblem only, map diagram, cartoon illustration, or blurry/low-resolution image.\n"
            "5) The visual scene/people/objects in the photo clearly belong to a DIFFERENT story or contradict the post text."
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
        time.sleep(1.0)
        if isinstance(verdict, dict) and not verdict.get("ok", False):
            print(f"[INFO] Vision rejected photo: {verdict.get('reason')}")
            return False
        return True
    except Exception as exc:
        print(f"[WARN] Vision photo check exception ({exc}); rejecting unverified photo so clean AI photo is generated.")
        return False


def verify_video_frame_matches_story(
    client: genai.Client, frame_bytes: bytes, story_summary: str
) -> bool:
    """Verify that a video's visual scene belongs to the same news story (while ALLOWING channel watermarks/logos on videos as requested by user)."""
    if not frame_bytes:
        return True
    try:
        check_prompt = (
            f"News post text:\n{story_summary[:500]}\n\n"
            "This image is a frame extracted from a video attached to the news post above.\n"
            "Return JSON {\"ok\": true/false, \"reason\": \"...\"}.\n"
            "CRITICAL RULES FOR VIDEOS:\n"
            "- DO NOT reject the video for having Telegram channel watermarks, logos, @handles, or text overlays! Watermarks on videos are ALLOWED because the admin reviews videos manually.\n"
            "- Set \"ok\": false ONLY if the visual scene, people, or event in the video frame clearly belong to a COMPLETELY DIFFERENT, unrelated news story that contradicts the post text (for example: a politician speaking at a podium in Congress when the text is about a drone delivering food to a chimpanzee in a flood).\n"
            "- If the video scene matches or is plausible for the news story, set \"ok\": true."
        )
        res = generate_content_with_fallback(
            client,
            VISION_MODELS,
            [
                types.Part.from_bytes(data=frame_bytes, mime_type="image/jpeg"),
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
        time.sleep(1.0)
        if isinstance(verdict, dict) and not verdict.get("ok", True):
            print(f"[INFO] Vision rejected mismatched video: {verdict.get('reason')}")
            return False
        return True
    except Exception as exc:
        print(f"[WARN] Video frame check warning: {exc}")
        return True


def search_wikimedia_fallback_photos(keywords: Any) -> list[str]:
    if isinstance(keywords, (list, tuple, set)):
        keywords = " ".join(str(k) for k in keywords if k)
    elif not isinstance(keywords, str):
        keywords = str(keywords or "")
    keywords = keywords.strip()
    if not keywords:
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


def generate_ai_news_photo(
    client: genai.Client, caption: str, wiki_keywords: Any = ""
) -> bytes | None:
    """Generate a clean, photorealistic editorial news image via AI Studio when source has no valid photo."""
    plain_story = BeautifulSoup(caption or "", "html.parser").get_text(" ", strip=True)[:500]
    kw_str = " ".join(wiki_keywords) if isinstance(wiki_keywords, (list, tuple, set)) else str(wiki_keywords or "")

    # Step 1: Craft a precise photorealistic editorial prompt using AI Studio
    img_prompt = (
        f"Photorealistic editorial news photography illustrating: {kw_str or plain_story[:140]}. "
        "Shot on Canon EOS R5 35mm lens, natural lighting, high detail, realistic environment, "
        "strictly no text, no letters, no numbers, no logos, no watermarks, no signs."
    )
    try:
        prompt_Instruction = (
            "Write a single concise English image-generation prompt (max 45 words) for a realistic editorial news photograph "
            "that visually illustrates the following news story.\n"
            "Rules:\n"
            "- Describe a concrete, realistic visual scene (buildings, infrastructure, nature, technology, transport, or objects).\n"
            "- Avoid close-up portraits of specific named politicians.\n"
            "- Explicitly end with: 'photorealistic editorial news photography, natural lighting, 4k DSLR, no text, no logos, no watermarks'.\n"
            "- Return ONLY the raw English prompt string, nothing else.\n\n"
            f"News text: {plain_story}"
        )
        p_res = generate_content_with_fallback(
            client,
            VISION_MODELS,
            prompt_Instruction,
            types.GenerateContentConfig(temperature=0.3),
        )
        if p_res and p_res.text and len(p_res.text.strip()) > 20:
            img_prompt = p_res.text.strip().replace("\n", " ").strip('"')
            print(f"[AI PHOTO] Crafted prompt: {img_prompt[:120]}...")
    except Exception as exc:
        print(f"[WARN] AI prompt crafting fallback: {exc}")

    # Step 2A: Try Google AI Studio native Imagen 3 endpoint
    for imagen_model in ("imagen-3.0-generate-002", "imagen-3.0-generate-001"):
        try:
            im_res = client.models.generate_images(
                model=imagen_model,
                prompt=img_prompt,
                config=types.GenerateImagesConfig(
                    number_of_images=1,
                    output_mime_type="image/jpeg",
                    aspect_ratio="16:9",
                ),
            )
            if im_res and getattr(im_res, "generated_images", None):
                raw_bytes = im_res.generated_images[0].image.image_bytes
                if raw_bytes and len(raw_bytes) > 15000:
                    with Image.open(io.BytesIO(raw_bytes)) as im:
                        rgb = im.convert("RGB")
                        buf = io.BytesIO()
                        rgb.save(buf, format="JPEG", quality=93)
                        print(f"[AI PHOTO] Generated via AI Studio {imagen_model}!")
                        return buf.getvalue()
        except Exception as exc:
            print(f"[INFO] AI Studio {imagen_model} unavailable on current key tier: {str(exc)[:90]}")

    # Step 2B: Try Google AI Studio Gemini native multimodal image generation models
    for gem_img_model in ("gemini-2.0-flash-preview-image-generation", "gemini-2.0-flash-exp-image-generation"):
        try:
            g_res = client.models.generate_content(
                model=gem_img_model,
                contents=f"Generate a photorealistic editorial news photo (16:9 horizontal, no text, no watermarks): {img_prompt}",
                config=types.GenerateContentConfig(
                    response_modalities=["TEXT", "IMAGE"],
                    temperature=0.4,
                ),
            )
            for cand_part in (g_res.candidates[0].content.parts if g_res and g_res.candidates else []):
                inline = getattr(cand_part, "inline_data", None)
                if inline and getattr(inline, "data", None) and len(inline.data) > 15000:
                    with Image.open(io.BytesIO(inline.data)) as im:
                        rgb = im.convert("RGB")
                        buf = io.BytesIO()
                        rgb.save(buf, format="JPEG", quality=93)
                        print(f"[AI PHOTO] Generated via AI Studio {gem_img_model}!")
                        return buf.getvalue()
        except Exception as exc:
            print(f"[INFO] AI Studio {gem_img_model} unavailable on current key tier: {str(exc)[:90]}")

    # Step 2C: Guaranteed photorealistic Flux generation driven by the AI Studio prompt (with clean crop & multi-attempt retry)
    for model_variant in ("flux", "turbo"):
        try:
            seed = random.randint(1000, 999999)
            flux_url = (
                f"https://image.pollinations.ai/prompt/{quote_plus(img_prompt)}"
                f"?width=1280&height=768&nologo=true&model={model_variant}&seed={seed}"
            )
            f_resp = http_get(flux_url, timeout=30)
            if f_resp and len(f_resp.content) > 15000:
                with Image.open(io.BytesIO(f_resp.content)) as im:
                    if im.width >= 600 and im.height >= 400:
                        # Crop bottom 48px to guarantee zero corner watermark
                        clean_im = im.crop((0, 0, im.width, im.height - 48)).convert("RGB")
                        buf = io.BytesIO()
                        clean_im.save(buf, format="JPEG", quality=93)
                        print(f"[AI PHOTO] Generated clean photorealistic image via {model_variant} ({clean_im.width}x{clean_im.height})!")
                        return buf.getvalue()
        except Exception as exc:
            print(f"[WARN] AI photo generation ({model_variant}) attempt warning: {exc}")

    return None


def get_clean_photo_for_post(
    client: genai.Client, candidate: dict[str, Any], caption: str, wiki_keywords: Any
) -> bytes | None:
    urls = list(candidate.get("photo_urls", []))

    # Check og:image on the candidate URL and any external article links
    check_links = [candidate.get("url", "")] + list(candidate.get("external_links", []))
    for art_url in check_links[:3]:
        if art_url and art_url.startswith("http") and "t.me/" not in art_url and "news.google.com" not in art_url and "lex.uz" not in art_url:
            art_resp = http_get(art_url, timeout=12)
            if art_resp:
                soup = BeautifulSoup(art_resp.text, "html.parser")
                og = soup.select_one("meta[property='og:image']")
                if og and og.get("content") and og["content"].strip() not in urls:
                    urls.append(og["content"].strip())

    # 1. First try genuine source photos — strictly verified by PIL + Gemini Vision
    for img_url in urls[:5]:
        resp = http_get(img_url)
        if not resp or len(resp.content) < 15000:
            continue
        try:
            with Image.open(io.BytesIO(resp.content)) as im:
                if im.width < 550 or im.height < 340:
                    continue
                rgb = im.convert("RGB")
                buf = io.BytesIO()
                rgb.save(buf, format="JPEG", quality=92)
                jpg_bytes = buf.getvalue()
        except Exception:
            continue

        if verify_photo_clean_and_relevant(client, jpg_bytes, caption):
            print(f"[MEDIA] Verified clean source photo: {img_url[:70]}")
            return jpg_bytes

    # 2. If source has no photo or source photo was rejected (watermark/table/blurry), generate with AI!
    print("[MEDIA] No clean source photo found; generating custom news photo via AI...")
    ai_jpg = generate_ai_news_photo(client, caption, wiki_keywords)
    if ai_jpg:
        return ai_jpg

    # 3. Last-resort fallback: Wikimedia Commons (strictly verified by Vision AI)
    for img_url in search_wikimedia_fallback_photos(wiki_keywords)[:4]:
        resp = http_get(img_url)
        if not resp or len(resp.content) < 15000:
            continue
        try:
            with Image.open(io.BytesIO(resp.content)) as im:
                if im.width < 550 or im.height < 340:
                    continue
                rgb = im.convert("RGB")
                buf = io.BytesIO()
                rgb.save(buf, format="JPEG", quality=92)
                jpg_bytes = buf.getvalue()
        except Exception:
            continue

        if verify_photo_clean_and_relevant(client, jpg_bytes, caption):
            return jpg_bytes

    return None


def extract_frame_from_video(video_url: str = "", video_bytes: bytes | None = None) -> bytes | None:
    """Extract a clean JPG frame from video using ffmpeg or direct stream."""
    ffmpeg_bin = shutil.which("ffmpeg")
    if not ffmpeg_bin:
        try:
            import imageio_ffmpeg
            ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
        except Exception:
            ffmpeg_bin = None

    if not ffmpeg_bin:
        return None

    try:
        if video_bytes and len(video_bytes) > 10000:
            with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tf:
                tf.write(video_bytes)
                temp_path = tf.name
            try:
                cmd = [
                    ffmpeg_bin, "-ss", "00:00:02", "-i", temp_path,
                    "-vframes", "1", "-f", "image2pipe", "-vcodec", "mjpeg", "-"
                ]
                proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=15)
                if proc.returncode == 0 and len(proc.stdout) > 2000:
                    print(f"[MEDIA] Extracted clean frame from video file ({len(proc.stdout)} bytes)")
                    return proc.stdout
            finally:
                if os.path.exists(temp_path):
                    try:
                        os.remove(temp_path)
                    except Exception:
                        pass
        elif video_url and video_url.startswith("http"):
            cmd = [
                ffmpeg_bin, "-ss", "00:00:02", "-i", video_url,
                "-vframes", "1", "-f", "image2pipe", "-vcodec", "mjpeg", "-"
            ]
            proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=20)
            if proc.returncode == 0 and len(proc.stdout) > 2000:
                print(f"[MEDIA] Extracted clean frame from video URL ({len(proc.stdout)} bytes)")
                return proc.stdout
    except Exception as exc:
        print(f"[WARN] Frame extraction from video failed: {exc}")

    return None

def enqueue_draft_to_render(
    cand_url: str,
    headline: str,
    caption_html: str,
    video_url: str = "",
    photo_bytes: bytes | None = None
) -> dict[str, Any] | None:
    enqueue_api = "https://karakalpak-translator-api.onrender.com/drafts/enqueue"
    payload = {
        "url": cand_url,
        "headline": headline,
        "caption_html": caption_html,
        "media_type": "video" if video_url else "photo",
        "media_url": video_url,
        "photo_base64": base64.b64encode(photo_bytes).decode("utf-8") if photo_bytes else None
    }
    try:
        resp = requests.post(enqueue_api, json=payload, timeout=4)
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return None

def send_telegram_video(bot_token: str, chat_id: str, video_url: str, caption_html: str, reply_markup: dict[str, Any] | None = None) -> dict[str, Any]:
    url = f"https://api.telegram.org/bot{bot_token}/sendVideo"
    try:
        # Download actual video bytes directly with streaming
        v_resp = requests.get(video_url, stream=True, timeout=30, headers={"User-Agent": USER_AGENT})
        if v_resp.status_code == 200:
            cl = int(v_resp.headers.get("content-length", 0))
            if cl > 50 * 1024 * 1024:
                print(f"[WARN] Video too large ({cl} bytes > 50MB), cannot upload directly via bot API.")
                return {"ok": False}
            chunks = []
            total = 0
            for chunk in v_resp.iter_content(chunk_size=1024 * 1024):
                total += len(chunk)
                if total > 50 * 1024 * 1024:
                    print(f"[WARN] Video exceeded 50MB during download, skipping.")
                    return {"ok": False}
                chunks.append(chunk)
            v_bytes = b"".join(chunks)
            if len(v_bytes) > 5000:
                post_data = {
                    "chat_id": chat_id,
                    "parse_mode": "HTML",
                    "caption": caption_html,
                    "supports_streaming": "true",
                }
                if reply_markup:
                    post_data["reply_markup"] = json.dumps(reply_markup)
                resp = requests.post(
                    url,
                    data=post_data,
                    files={"video": ("news_video.mp4", v_bytes, "video/mp4")},
                    timeout=120,
                )
                res_data = resp.json()
                if res_data.get("ok"):
                    return res_data
                else:
                    print(f"[WARN] Telegram sendVideo error: {res_data}")
    except Exception as exc:
        print(f"[WARN] send_telegram_video exception: {exc}")
    return {"ok": False}

def send_telegram_photo(bot_token: str, chat_id: str, photo_bytes: bytes, caption_html: str, reply_markup: dict[str, Any] | None = None) -> dict[str, Any]:
    url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
    data = {
        "chat_id": chat_id,
        "parse_mode": "HTML",
        "caption": caption_html,
    }
    if reply_markup:
        data["reply_markup"] = json.dumps(reply_markup)
    resp = requests.post(
        url,
        data=data,
        files={"photo": ("news.jpg", photo_bytes, "image/jpeg")},
        timeout=30,
    )
    return resp.json()

def is_within_active_posting_hours() -> bool:
    """Active 24/7 non-stop as requested by user."""
    return True


def main() -> int:
    tashkent_tz = timezone(timedelta(hours=5))
    now_uzt = datetime.now(tashkent_tz)
    print(f"[ACTIVE 24/7] Current Tashkent time is {now_uzt.strftime('%Y-%m-%d %H:%M:%S')}. Operating non-stop.")



    bot_token, chat_id, gemini_key, max_posts, admin_chat_id, auto_publish = load_config()

    client = genai.Client(api_key=gemini_key)



    ensure_render_service_warm(max_wait_seconds=45)

    # Check Moderation Queue status on Render to maintain steady 4-post buffer
    queue_status = {"pending_in_queue": 0, "has_active_waiting_admin": False}
    try:
        r_stat = requests.get("https://karakalpak-translator-api.onrender.com/drafts/status", timeout=10)
        if r_stat.status_code == 200:
            queue_status = r_stat.json()
    except Exception as exc:
        print(f"[WARN] Could not check Render queue status: {exc}")

    pending_in_q = queue_status.get("pending_in_queue", 0)
    has_active = 1 if queue_status.get("has_active_waiting_admin") else 0
    total_waiting = pending_in_q + has_active

    # Max reserve in moderation queue: 15 posts (+ 1 active in chat = 16 max total)
    max_reserve = 15
    if pending_in_q >= max_reserve:
        print(f"[QUEUE RESERVE FULL] Moderation queue already has {pending_in_q} posts in reserve (max: {max_reserve}) + {has_active} active in chat.")
        print("                     Skipping drafting this run to prevent backlog.")
        return 0

    posts_to_generate = max(5, max_posts)
    print(f"[QUEUE STATUS] Active in chat: {has_active}, In reserve: {pending_in_q}/{max_reserve}. Target to generate this run: {posts_to_generate} post(s).")

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
        and not NICHE_ESOTERIC_TOPIC_RE.search((c.get("text") or "") + " " + (c.get("url") or ""))

    ]

    candidates = build_balanced_candidate_pool(fresh_candidates, limit=60)

    print(f"      Collected {len(candidates)} fresh unseen candidate stories.")

    if not candidates:

        print("[DONE] No unseen stories right now.")

        return 0



    # 3-Category Rotation Analyzer: QR / UZ / WORLD

    target_category, rot_analysis, rot_reason = analyze_last_3_posts_and_get_target(existing_posts)

    print("      [ROTATION ENGINE] Last 3 posts analysis on @qaraqalpaqshajanaliqlar:")

    for a in rot_analysis:

        print(f"         Post #{a['idx']}: [{a['category']}] {a['headline']}")

    print(f"      [ROTATION ENGINE] Target category for this run: {target_category} ({rot_reason})")



    ask_count = max(posts_to_generate + 3, 6)

    print(f"[3/5] Curating & drafting Karakalpak Latin posts with flagship Gemini (target={posts_to_generate}, pool={ask_count})...")

    selected = curate_and_write_posts(client, candidates, existing_posts, ask_count, target_category, rot_analysis, rot_reason)

    time.sleep(1.5)



    print("[4/5] Proofreading captions & checking semantic duplicates against Official 34-Letter Alphabet...")

    selected = proofread_karakalpak_captions(client, selected, existing_posts)



    if not selected:

        print("[SKIP ALL] No posts available from Tilmoch translator. Skipping run cleanly as instructed by user.")

        return 0



    # Classify candidate items into QR, UZ, and WORLD pools
    def get_story_cat(it: dict[str, Any]) -> str:
        cand_temp = resolve_candidate_for_item(it, candidates)
        txt = (it.get("caption_html", "") + " " + (cand_temp.get("text", "") if cand_temp else ""))
        c_cat = cand_temp.get("category", "") if cand_temp else ""
        if c_cat == "karakalpakstan" or QR_CATEGORY_REGEX.search(txt):
            return "QR"
        elif c_cat == "citizen_uzbekistan" or UZ_CATEGORY_REGEX.search(txt):
            return "UZ"
        else:
            return "WORLD"

    qr_pool = [it for it in selected if get_story_cat(it) == "QR"]
    uz_pool = [it for it in selected if get_story_cat(it) == "UZ"]
    world_pool = [it for it in selected if get_story_cat(it) == "WORLD"]

    print(f"      [3-PILLAR CURATION POOL] QR: {len(qr_pool)}, UZ: {len(uz_pool)}, WORLD: {len(world_pool)}")

    # Interleave strictly: QR, UZ, WORLD, QR, UZ, WORLD...
    balanced_selected: list[dict[str, Any]] = []
    max_len = max(len(qr_pool), len(uz_pool), len(world_pool), 1)
    for i in range(max_len):
        if i < len(qr_pool):
            balanced_selected.append(qr_pool[i])
        if i < len(uz_pool):
            balanced_selected.append(uz_pool[i])
        if i < len(world_pool):
            balanced_selected.append(world_pool[i])

    selected = balanced_selected



    published_count = 0

    new_urls = list(seen_urls)

    new_titles = list(existing_posts)



    print("[5/5] Verifying exact photo match, overlap gate & publishing to @qaraqalpaqshajanaliqlar...")

    for item in selected:

        if published_count >= posts_to_generate:

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
        raw_video_urls = cand.get("video_urls", [])
        video_urls: list[str] = []
        for v_url in raw_video_urls:
            v_frame = extract_frame_from_video(video_url=v_url)
            if v_frame and not verify_video_frame_matches_story(client, v_frame, caption):
                print(f"[MEDIA] Video rejected (scene mismatch with story text): {v_url[:60]}")
                continue
            video_urls.append(v_url)

        # Deliver EVERY post DIRECTLY to checkjanaliq (-1003941073968) so admin always has at least 5 posts ready
        mod_chat_id = "-1003941073968"
        post_ts = int(time.time() * 1000) % 1000000000
        mod_markup = {
            "inline_keyboard": [
                [
                    {"text": "🚀 Kanalǵa shıǵarıw", "callback_data": f"pub:{post_ts}"},
                    {"text": "❌ Biykar etiw", "callback_data": f"del:{post_ts}"}
                ]
            ]
        }
        fb_res = None
        if video_urls:
            for v_url in video_urls:
                print(f"[MEDIA] Delivering verified video to checkjanaliq: {v_url[:60]}...")
                fb_res = send_telegram_video(
                    bot_token=bot_token,
                    chat_id=mod_chat_id,
                    video_url=v_url,
                    caption_html=caption,
                    reply_markup=mod_markup
                )
                if fb_res and fb_res.get("ok"):
                    print("[MEDIA] Video delivered successfully to checkjanaliq!")
                    break

        photo_bytes = None
        if not fb_res or not fb_res.get("ok"):
            # Obtain strictly verified clean photo (or AI-generated photo if source photo has logo/watermark/banner or is missing)
            photo_bytes = get_clean_photo_for_post(
                client, cand, caption, item.get("wikimedia_search_keywords", "")
            )
            if not photo_bytes:
                print(f"[SKIP] Could not obtain media for {cand['url']}; blacklisting to prevent loop.")
                new_urls.append(normalize_url(cand["url"]))
                continue
            print("[MEDIA] Delivering photo post to checkjanaliq...")
            fb_res = send_telegram_photo(
                bot_token=bot_token,
                chat_id=mod_chat_id,
                photo_bytes=photo_bytes,
                caption_html=caption,
                reply_markup=mod_markup
            )
        if fb_res and fb_res.get("ok"):
            deliv_mid = fb_res.get('result', {}).get('message_id')
            print(f"[DIRECT TO CHECKJANALIQ] Post #{published_count+1} delivered! (Message ID: {deliv_mid})")
            published_count += 1
            new_urls.append(normalize_url(cand["url"]))
            if cand.get("fallback_post_url"):
                new_urls.append(normalize_url(cand["fallback_post_url"]))
            new_titles.append(BeautifulSoup(caption, "html.parser").get_text(" ", strip=True)[:350])
            time.sleep(2)
        else:
            print(f"[FALLBACK] Render moderation queue returned: {q_res}. Delivering DIRECTLY to moderation channel (-1003941073968)...")
            mod_chat_id = "-1003941073968"
            mod_markup = {
                "inline_keyboard": [
                    [
                        {"text": "🚀 Kanalǵa shıǵarıw", "callback_data": f"pub:{int(time.time())}"},
                        {"text": "❌ Biykar etiw", "callback_data": f"del:{int(time.time())}"}
                    ]
                ]
            }
            fb_res = None
            if video_urls:
                for v_url in video_urls:
                    print(f"[MEDIA] Prioritizing actual video upload for post: {v_url[:60]}...")
                    fb_res = send_telegram_video(
                        bot_token=bot_token,
                        chat_id=mod_chat_id,
                        video_url=v_url,
                        caption_html=caption,
                        reply_markup=mod_markup
                    )
                    if fb_res and fb_res.get("ok"):
                        print("[MEDIA] Actual HD video successfully delivered to moderation channel!")
                        break
            if not fb_res or not fb_res.get("ok"):
                if photo_bytes:
                    print("[MEDIA] Delivering high-res photo fallback...")
                    fb_res = send_telegram_photo(
                        bot_token=bot_token,
                        chat_id=mod_chat_id,
                        photo_bytes=photo_bytes,
                        caption_html=caption,
                        reply_markup=mod_markup
                    )
            if fb_res and fb_res.get("ok"):
                print(f"[DIRECT DELIVERED] Post successfully delivered directly to moderation channel! (Message ID: {fb_res.get('result', {}).get('message_id')})")
                published_count += 1
                new_urls.append(normalize_url(cand["url"]))
                if cand.get("fallback_post_url"):
                    new_urls.append(normalize_url(cand["fallback_post_url"]))
                new_titles.append(BeautifulSoup(caption, "html.parser").get_text(" ", strip=True)[:350])
                time.sleep(2)
            else:
                print(f"[WARN] Direct fallback delivery error: {fb_res}")







    history_payload = {"urls": new_urls[-350:], "titles": new_titles[-100:]}
    HISTORY_FILE.write_text(
        json.dumps(history_payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    # Sync posted_history.json to GitHub repository so history is permanently preserved across runs
    try:
        gh_token = os.environ.get("GITHUB_TOKEN") or ""
        if gh_token:
            gh_url = "https://api.github.com/repos/sardardww/qrjanaliq-poster/contents/posted_history.json"
            gh_req = urllib.request.Request(gh_url, headers={"Authorization": f"Bearer {gh_token}", "User-Agent": "python"})
            gh_sha = json.loads(urllib.request.urlopen(gh_req, timeout=8).read().decode())["sha"]
            import base64
            gh_update = {
                "message": f"chore(history): persist {len(new_urls)} URLs and {len(new_titles)} titles",
                "content": base64.b64encode(HISTORY_FILE.read_bytes()).decode("utf-8"),
                "sha": gh_sha
            }
            gh_put = urllib.request.Request(gh_url, data=json.dumps(gh_update).encode("utf-8"), headers={"Authorization": f"Bearer {gh_token}", "User-Agent": "python", "Content-Type": "application/json"}, method="PUT")
            urllib.request.urlopen(gh_put, timeout=10)
            print("[HISTORY] Successfully synced posted_history.json to GitHub repo!")
    except Exception as exc:
        print(f"[HISTORY] Note: GitHub sync skipped or error: {exc}")

    print(f"[DONE] Successfully published {published_count} posts.")

    return 0





if __name__ == "__main__":

    sys.exit(main())

