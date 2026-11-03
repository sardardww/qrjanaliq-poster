#!/usr/bin/env python3
"""
QARAQALPAQSTAN JAN'ALIQLARI (@qrjanaliq) — 24/7 Cloud Automated News Poster
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
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
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

CRITICAL ORTHOGRAPHY & GRAMMAR RULES:
- Letter #32 `Cc` represents Cyrillic `ц`: ALWAYS write `Shveycariya` (NEVER `Shveysariya` or `Shveyariya`), `kompensaciya`, `konstituciya`, `delegaciya`, `associaciya`, `korrupciya`, `informaciya`, `akciya`, `policiya`.
- Letter #19 `Ńń` represents `ң`: Genitive case suffixes `-nıń / -niń / -dıń / -diń / -tıń / -tiń` and 2nd-person `-ńız / -ńiz` MUST ALWAYS use `ń` (e.g. `qıstıń kúnleri`, `Ministrler Keńesiniń`, `oqıwshılardıń` — NEVER `-tın` or `-nın`!).
- Letter #11 `Íı` (back vowel `ы`) vs #12 `Ii` (front vowel `и`): Follow strict vowel harmony! E.g. `gazlastırılmaǵan` (NEVER `gazlespegen`), `qıstıń`, `jılıtıw`, `jaratılǵan`, `xızmetker`.
- Letter #29 `Ww` (`ў`): Write `oqıw`, `saylaw`, `aǵza bolıw`, `áwmet`, `máwsim`, `wálayat`, `qáwipsizlik`.
- ZERO Turkish/old-Uzbek letters (`Ş, ş, Ç, ç, Ğ, ğ, Ö, ö, Ü, ü, o', g', ʻ`).
- ZERO Kazakhisms: NEVER write `joba/jobalar` -> write `joybar/joybarlar`; NEVER write `baǵıtlanǵan` -> write `baǵdarlanǵan` or `qaratılǵan`.
- ZERO Uzbekisms:
  * `ulanbaǵan / ulanǵan` -> `jalǵanbaǵan / jalǵanǵan`
  * `Favqulodda va Muxtor elshi / Muxtar elshi` -> `Ayrıqsha hám Tolıq huqıqlı elshi`
  * `bo'ldi` -> `boldı`, `uchun` -> `ushın`, `bilan` -> `menen`, `ham` -> `hám`
  * `so'm` -> `sum`, `tuman` -> `rayon`, `viloyat` -> `wálayat`, `xodim` -> `xızmetker`, `o'rinbosari` -> `orınbasarı`
- Number & grammar accuracy: Never pluralize a single city (`Nókis qalasındaǵı`, NEVER `Nókis qalalarındaǵı`). Distinguish "from X to Y" (`200 kVt·saattan 350 kVt·saatqa arttırıldı`, NEVER `200 kVt·saatqa asırılıp`).
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
    "Ğ": "Ǵ", "ğ": "ǵ",
    "Ö": "Ó", "ö": "ó",
    "Ü": "Ú", "ü": "ú",
}

AUTO_WORD_FIXES = [
    (r"\bShveysariya", "Shveycariya"),
    (r"\bshveysariya", "shveycariya"),
    (r"\bShveyariya", "Shveycariya"),
    (r"\bMuxtar elshi", "Tolıq huqıqlı elshi"),
    (r"\bmuxtar elshi", "tolıq huqıqlı elshi"),
    (r"\bjobalar", "joybarlar"),
    (r"\bJobalar", "Joybarlar"),
    (r"\bjobası", "joybarı"),
    (r"\bbaǵıtlanǵan\b", "baǵdarlanǵan"),
    (r"\bulanbaǵan\b", "jalǵanbaǵan"),
    (r"\bGazlespegen\b", "Gazlastırılmaǵan"),
    (r"\bgazlespegen\b", "gazlastırılmaǵan"),
    (r"\bNókis qalalarındaǵı\b", "Nókis qalasındaǵı"),
    (r"\bqıstın\b", "qıstıń"),
]

TELEGRAM_SOURCES = [
    # Karakalpakstan official & high-signal sector channels
    ("karakalpakstan", "joqargikenes", 14),
    ("karakalpakstan", "QResMinistrlerKenesi", 14),
    ("karakalpakstan", "krbajixana", 14),
    ("karakalpakstan", "kkeduuz", 14),
    ("karakalpakstan", "jaslar_isleri_agentligi", 14),
    ("karakalpakstan", "KarPressa", 8),
    # Citizen legal, subsidies, safety & Uzbekistan official channels
    ("citizen_uzbekistan", "xaliq_ushin", 18),
    ("citizen_uzbekistan", "karinform", 18),
    ("citizen_uzbekistan", "Press_Secretary_Uz", 10),
    ("citizen_uzbekistan", "uzbprokuratura", 10),
    ("citizen_uzbekistan", "RaqobatGovUz", 12),
    ("citizen_uzbekistan", "iivuz", 10),
    ("citizen_uzbekistan", "FAUzbekistan", 12),
]

RSS_AND_GLOBAL_FEEDS = [
    ("world", "bbc.com", "https://feeds.bbci.co.uk/news/world/rss.xml"),
    ("world_tech", "bbc.com", "https://feeds.bbci.co.uk/news/technology/rss.xml"),
    ("world", "bbc.com/uzbek", "https://feeds.bbci.co.uk/uzbek/rss.xml"),
    ("world", "theguardian.com", "https://www.theguardian.com/world/rss"),
    ("world_tech", "theguardian.com", "https://www.theguardian.com/uk/technology/rss"),
    ("world", "aljazeera.com", "https://www.aljazeera.com/xml/rss/all.xml"),
    ("citizen_uzbekistan", "gazeta.uz", "https://www.gazeta.uz/oz/rss/"),
    ("karakalpakstan", "Google News", "https://news.google.com/rss/search?q=when:12h+(Qoraqalpog%CA%BBiston+OR+Nukus+OR+Qaraqalpaqstan+OR+Karakalpakstan)&hl=uz&gl=UZ&ceid=UZ:uz"),
    ("world", "Google News", "https://news.google.com/rss/search?q=when:3h+(site:reuters.com+OR+site:apnews.com)&hl=en-US&gl=US&ceid=US:en"),
]

# ALWAYS prioritize flagship unlocked models first (verified from AI Studio: no Paid lock!)
TEXT_MODELS = [
    "gemini-3.8-flash",
    "gemini-3.8-flash",  # Retry once on transient 503/429 before falling back
    "gemini-3.1-pro-preview",
    "gemini-pro-latest",
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
]
VISION_MODELS = [
    "gemini-3.8-flash",
    "gemini-3.1-pro-preview",
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
]


def normalize_url(u: str) -> str:
    return u.strip().split("?")[0].rstrip("/")


def load_config() -> tuple[str, str, str, int]:
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    gemini_key = os.environ.get("GEMINI_API_KEY", "").strip()
    max_posts = int(os.environ.get("MAX_POSTS", "2"))

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
    """Scrape @qrjanaliq public feed + local cache to prevent duplicate stories & topics."""
    recent_summaries: list[str] = []
    seen_urls: set[str] = set()

    if HISTORY_FILE.exists():
        try:
            cached = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
            seen_urls.update(cached.get("urls", []))
            recent_summaries.extend(cached.get("titles", [])[-35:])
        except Exception:
            pass

    resp = http_get("https://t.me/s/qrjanaliq")
    if resp:
        soup = BeautifulSoup(resp.text, "html.parser")
        for msg in soup.select(".tgme_widget_message")[-28:]:
            txt_el = msg.select_one(".tgme_widget_message_text")
            if txt_el:
                txt = txt_el.get_text(" ", strip=True)
                recent_summaries.append(txt[:420])
                for a_tag in txt_el.select("a[href]"):
                    href = a_tag.get("href", "").strip()
                    if href and "t.me/qrjanaliq" not in href:
                        seen_urls.add(normalize_url(href))
    return recent_summaries[-40:], seen_urls


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


def scrape_rss_and_global_feeds() -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    ns = {"media": "http://search.yahoo.com/mrss/"}
    for cat, default_src, rss_url in RSS_AND_GLOBAL_FEEDS:
        resp = http_get(rss_url)
        if not resp:
            continue
        try:
            root = ET.fromstring(resp.content)
        except Exception:
            continue
        for item in root.findall("./channel/item")[:7]:
            title = (item.findtext("title") or "").strip()
            raw_desc = (item.findtext("description") or "").strip()
            desc = BeautifulSoup(raw_desc, "html.parser").get_text(" ", strip=True)
            link = (item.findtext("link") or "").strip()
            if "bbc.co.uk" in link:
                link = link.split("?")[0].replace("bbc.co.uk", "bbc.com")
            pub = (item.findtext("pubDate") or "").strip()
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
                items.append(
                    {
                        "category": cat,
                        "source_name": src_name,
                        "url": link,
                        "published_at": pub,
                        "text": f"{title}\n{desc}"[:1200],
                        "photo_urls": photos[:3],
                    }
                )
    return items


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


def curate_and_write_posts(
    client: genai.Client,
    candidates: list[dict[str, Any]],
    existing_posts: list[str],
    ask_count: int,
) -> list[dict[str, Any]]:
    playbook = Path("TASK_INSTRUCTIONS.md").read_text(encoding="utf-8") if Path("TASK_INSTRUCTIONS.md").exists() else ""

    prompt = f"""
You are the Editor-in-Chief and Doctor of Karakalpak Philology for the Telegram channel QARAQALPAQSTAN JAN'ALIQLARI (@qrjanaliq).

{OFFICIAL_KARAKALPAK_ALPHABET_RULES}

STRICT EDITORIAL PLAYBOOK:
{playbook[:5000]}

ALREADY PUBLISHED ON @qrjanaliq (STRICT SEMANTIC DEDUPLICATION — NEVER repeat ANY topic, law, number, person, or event already covered below, even if the URL or source channel is different!):
{json.dumps(existing_posts, ensure_ascii=False, indent=2)}

CANDIDATE STORIES FROM LIVE OFFICIAL & GLOBAL FEEDS:
{json.dumps([{ "idx": i, "url": c["url"], "category": c["category"], "source_name": c["source_name"], "has_photo": bool(c.get("photo_urls")), "text": c["text"][:1000] } for i, c in enumerate(candidates)], ensure_ascii=False, indent=2)}

YOUR TASK:
1. Select the TOP {ask_count} completely NEW, non-duplicate, high-interest stories (aiming for a strong mix across Karakalpakstan, Citizen Legal/Utility or Uzbekistan important news, and World/Tech exclusive stories).
   - Double-check against ALREADY PUBLISHED ON @qrjanaliq: if a story is about the same event/law (e.g. 350 kVt electricity limit, 4-day parent school holiday leave, Nukus Chemistry Olympiad, Cannavaro, Asian Cup 2027, Swiss Ambassador at School #34, China Eastern Airlines), SKIP IT!
   - Strongly prefer candidates where `has_photo` is true or whose `url` is a direct web article (not `news.google.com`).
2. Write each caption in 100% pure, natural, literary KARAKALPAK LATIN following the Official 34-Letter Alphabet above.
   - Keep visible text between 360 and 820 characters.
   - Use ONLY valid Telegram HTML tags: `<b>...</b>`, `<blockquote>...</blockquote>`, `<a href="...">...</a>`.
   - Lead with ONE fitting emoji (`⚡️`, `🚨`, `❓`, `🔰`, `🚀`, `🏆`, `🚛`, `💻`) + `<b>Headline</b>`.
   - End EVERY caption with these exact two lines (using the EXACT `url` of THAT SAME `idx` candidate!):
Deregi: <a href="EXACT_CANDIDATE_URL">SHORT_SOURCE_LABEL</a>
👉 <a href="https://t.me/qrjanaliq">@qrjanaliq — aǵza bolıw</a>

Return ONLY a JSON array of objects with keys:
- "candidate_idx": integer (MUST match the exact `idx` of the story you wrote about!)
- "source_url": string (MUST equal `candidates[candidate_idx]["url"]`!)
- "caption_html": string
- "wikimedia_search_keywords": string (2-3 simple English nouns for backup photo search)
"""

    resp = generate_content_with_fallback(
        client,
        TEXT_MODELS,
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
                return v
        return [parsed]
    return parsed


def proofread_karakalpak_captions(client: genai.Client, items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Dedicated 2nd-pass literary Karakalpak proofreader using the Official 34-Letter Alphabet."""
    if not items:
        return items
    try:
        proof_prompt = f"""
You are a strict Karakalpak language proofreader verifying Telegram HTML captions against the Official 34-Letter Karakalpak Alphabet.

{OFFICIAL_KARAKALPAK_ALPHABET_RULES}

Inspect each caption_html in the JSON array below and fix ANY:
1. Alphabet/spelling errors (`Shveysariya/Shveyariya` -> `Shveycariya`, missing `c` in `-ciya` words, missing `ń` in `-nıń/-niń/-dıń/-diń/-tıń/-tiń`, wrong `ı` vs `i`, wrong `ǵ/ń/á/ó/ú/w`).
2. Kazakhisms (`joba/jobalar` -> `joybar/joybarlar`, `baǵıtlanǵan` -> `baǵdarlanǵan`) or Uzbekisms (`ulanbaǵan` -> `jalǵanbaǵan`, `Muxtar elshi` -> `Tolıq huqıqlı elshi`, `tuman` -> `rayon`, `viloyat` -> `wálayat`).
3. Vowel harmony errors (`gazlespegen` -> `gazlastırılmaǵan`) or singular/plural mistakes (`Nókis qalalarındaǵı` -> `Nókis qalasındaǵı`).
4. Preserve all HTML tags (`<b>`, `<blockquote>`, `<a href="...">`), URLs, numbers, and the `Deregi:` + `@qrjanaliq` footer intact!

INPUT JSON:
{json.dumps([{"i": idx, "caption_html": it.get("caption_html", "")} for idx, it in enumerate(items)], ensure_ascii=False, indent=2)}

Return ONLY a JSON array of objects `[{{"i": 0, "caption_html": "..."}}, ...]`.
"""
        resp = generate_content_with_fallback(
            client,
            TEXT_MODELS,
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
        if isinstance(fixed_list, list):
            for entry in fixed_list:
                pos = entry.get("i")
                new_cap = entry.get("caption_html")
                if isinstance(pos, int) and 0 <= pos < len(items) and isinstance(new_cap, str) and len(new_cap) > 120:
                    items[pos]["caption_html"] = new_cap
        time.sleep(1.5)
    except Exception as exc:
        print(f"[WARN] Second-pass proofreader skipped ({exc}); relying on deterministic fixes.")
    return items


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
    if "@qrjanaliq" not in caption:
        caption = caption.rstrip() + '\n👉 <a href="https://t.me/qrjanaliq">@qrjanaliq — aǵza bolıw</a>'
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
        if "t.me/qrjanaliq" in nm:
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

    print("[1/5] Checking @qrjanaliq live feed for deduplication...")
    existing_posts, seen_urls = fetch_existing_channel_posts()
    print(f"      Found {len(existing_posts)} recent channel posts & {len(seen_urls)} seen URLs.")

    print("[2/5] Scanning global & official Karakalpak/Uzbek feeds...")
    raw_candidates: list[dict[str, Any]] = []
    raw_candidates.extend(scrape_kknews())
    for cat, ch, hrs in TELEGRAM_SOURCES:
        raw_candidates.extend(scrape_telegram_channel(cat, ch, hrs))
    raw_candidates.extend(scrape_kun_uz())
    raw_candidates.extend(scrape_rss_and_global_feeds())

    candidates = [
        c
        for c in raw_candidates
        if normalize_url(c["url"]) not in seen_urls
        and normalize_url(c.get("fallback_post_url", "")) not in seen_urls
    ][:45]
    print(f"      Collected {len(candidates)} fresh unseen candidate stories.")
    if not candidates:
        print("[DONE] No unseen stories right now.")
        return 0

    ask_count = min(max_posts + 2, 5)
    print(f"[3/5] Curating & drafting Karakalpak Latin posts with Gemini 3.8 Flash (target={max_posts}, pool={ask_count})...")
    selected = curate_and_write_posts(client, candidates, existing_posts, ask_count)
    time.sleep(1.5)

    print("[4/5] Proofreading captions against Official 34-Letter Karakalpak Alphabet & literary grammar...")
    selected = proofread_karakalpak_captions(client, selected)

    published_count = 0
    new_urls = list(seen_urls)
    new_titles = list(existing_posts)

    print("[5/5] Verifying exact photo match & publishing to @qrjanaliq...")
    for item in selected:
        if published_count >= max_posts:
            break
        cand = resolve_candidate_for_item(item, candidates)
        if not cand:
            print("[WARN] Could not resolve candidate for item, skipping.")
            continue
        caption = sanitize_and_validate_caption(item.get("caption_html", ""))
        if not caption:
            continue

        photo_bytes = get_clean_photo_for_post(
            client, cand, caption, item.get("wikimedia_search_keywords", "")
        )
        if not photo_bytes:
            print(f"[SKIP] Could not obtain clean related photo for {cand['url']}; trying backup story.")
            continue

        res = send_telegram_photo(bot_token, chat_id, photo_bytes, caption)
        if res.get("ok"):
            msg_id = res["result"]["message_id"]
            print(f"[OK] Published https://t.me/qrjanaliq/{msg_id} -> {cand['url']}")
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
