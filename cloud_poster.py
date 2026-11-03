#!/usr/bin/env python3
"""
QARAQALPAQSTAN JAN'ALIQLARI (@qrjanaliq) — 24/7 Cloud Automated News Poster
Runs unattended on GitHub Actions (or any Linux/Windows server) even when PC is off.
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
}

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
    # Direct global & national feeds with high-res watermark-free article photos
    ("world", "bbc.com", "https://feeds.bbci.co.uk/news/world/rss.xml"),
    ("world_tech", "bbc.com", "https://feeds.bbci.co.uk/news/technology/rss.xml"),
    ("world", "bbc.com/uzbek", "https://feeds.bbci.co.uk/uzbek/rss.xml"),
    ("world", "theguardian.com", "https://www.theguardian.com/world/rss"),
    ("world_tech", "theguardian.com", "https://www.theguardian.com/uk/technology/rss"),
    ("world", "aljazeera.com", "https://www.aljazeera.com/xml/rss/all.xml"),
    ("citizen_uzbekistan", "gazeta.uz", "https://www.gazeta.uz/oz/rss/"),
    # Open-web Google News live search across all regional & global sites (0 API quota!)
    ("karakalpakstan", "Google News", "https://news.google.com/rss/search?q=when:12h+(Qoraqalpog%CA%BBiston+OR+Nukus+OR+Qaraqalpaqstan+OR+Karakalpakstan)&hl=uz&gl=UZ&ceid=UZ:uz"),
    ("world", "Google News", "https://news.google.com/rss/search?q=when:3h+(site:reuters.com+OR+site:apnews.com)&hl=en-US&gl=US&ceid=US:en"),
]

# Fast, Free-Tier friendly Gemini 3.5 / 3.1 models first (avoids 503 preview delays)
TEXT_MODELS = [
    "gemini-3.5-flash-lite",
    "gemini-3.5-flash",
    "gemini-3.1-flash-lite",
    "gemini-flash-lite-latest",
    "gemini-flash-latest",
]
VISION_MODELS = [
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
    "gemini-3.5-flash",
]


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
    """Scrape @qrjanaliq public feed + local cache to prevent duplicate stories."""
    recent_summaries: list[str] = []
    seen_urls: set[str] = set()

    if HISTORY_FILE.exists():
        try:
            cached = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
            seen_urls.update(cached.get("urls", []))
            recent_summaries.extend(cached.get("titles", [])[-30:])
        except Exception:
            pass

    resp = http_get("https://t.me/s/qrjanaliq")
    if resp:
        soup = BeautifulSoup(resp.text, "html.parser")
        for msg in soup.select(".tgme_widget_message")[-25:]:
            txt_el = msg.select_one(".tgme_widget_message_text")
            if txt_el:
                txt = txt_el.get_text(" ", strip=True)
                recent_summaries.append(txt[:220])
                for a_tag in txt_el.select("a[href]"):
                    href = a_tag.get("href", "").strip()
                    if href and "t.me/qrjanaliq" not in href:
                        seen_urls.add(href.split("?")[0].rstrip("/"))
    return recent_summaries[-35:], seen_urls


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

        txt_el = msg.select_one(".tgme_widget_message_text")
        if not txt_el:
            continue
        text = txt_el.get_text("\n", strip=True)
        if len(text) < 60:
            continue

        external_links = []
        for a_tag in txt_el.select("a[href]"):
            href = a_tag.get("href", "").strip()
            if href.startswith("http") and channel.lower() not in href.lower():
                external_links.append(href)

        photo_urls = []
        for wrap in msg.select(".tgme_widget_message_photo_wrap"):
            m = BG_URL_RE.search(wrap.get("style", ""))
            if m:
                photo_urls.append(m.group(1))

        items.append(
            {
                "category": category,
                "source_name": channel,
                "url": external_links[0] if any("lex.uz" in u or "my.gov.uz" in u for u in external_links) else post_url,
                "fallback_post_url": post_url,
                "external_links": external_links[:3],
                "published_at": pub_dt.isoformat() if pub_dt else "",
                "text": text[:1500],
                "photo_urls": photo_urls,
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
        body_text = " ".join(p.get_text(" ", strip=True) for p in asoup.select("article p, .entry-content p, .post-content p"))
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
    for model_name in models:
        try:
            return client.models.generate_content(
                model=model_name,
                contents=contents,
                config=config,
            )
        except Exception as exc:
            last_err = exc
            print(f"[WARN] Model {model_name} unavailable ({exc}), trying next fallback...")
            time.sleep(1.0)
    raise RuntimeError(f"All fallback models failed: {last_err}")


def curate_and_write_posts(
    client: genai.Client,
    candidates: list[dict[str, Any]],
    existing_posts: list[str],
    ask_count: int,
) -> list[dict[str, Any]]:
    playbook = Path("TASK_INSTRUCTIONS.md").read_text(encoding="utf-8") if Path("TASK_INSTRUCTIONS.md").exists() else ""

    prompt = f"""
You are the chief Karakalpak-language editor for the Telegram channel QARAQALPAQSTAN JAN'ALIQLARI (@qrjanaliq).

STRICT EDITORIAL PLAYBOOK:
{playbook[:6000]}

ALREADY PUBLISHED ON @qrjanaliq (NEVER repeat any of these stories, topics, or URLs):
{json.dumps(existing_posts, ensure_ascii=False, indent=2)}

CANDIDATE STORIES FROM LIVE OFFICIAL & GLOBAL FEEDS (each has an index `idx`):
{json.dumps([{ "idx": i, **{k: v for k, v in c.items() if k != "photo_urls"}, "has_photo": bool(c.get("photo_urls")) } for i, c in enumerate(candidates)], ensure_ascii=False, indent=2)}

YOUR TASK:
Select the TOP {ask_count} completely non-duplicate, high-interest stories in priority order (aiming for a strong mix across Karakalpakstan, Citizen Legal/Utility or Uzbekistan important news, and World/Tech exclusive stories).
Strongly prefer candidates where `has_photo` is true or whose `url` is a direct news article (not `news.google.com`), so every post has an authentic real photo.
Skip minor appointments, bureaucratic meetings without concrete citizen impact, greetings, or ads.

CRITICAL LANGUAGE & HTML RULES FOR EACH CAPTION:
1. Write 100% pure literary KARAKALPAK LATIN (`Á á, Ó ó, Ú ú, Í ı, Ǵ ǵ, Ń ń`).
   - ZERO Cyrillic letters anywhere! Double-check every word so no Russian/Cyrillic lookalike letters (`а`, `е`, `о`, `с`, `т`, `н`, `и`, `В`) slip in.
   - NEVER use Uzbek `o'`, `g'` or Uzbek words (`bo'ldi` -> `boldı`, `uchun` -> `ushın`, `bilan` -> `menen`, `ham` -> `hám`, `so'm` -> `sum`, `o'rinbosari` -> `orınbasarı`, `tuman` -> `rayon`, `viloyat` -> `wálayat`, `xodim` -> `xızmetker`).
2. Keep visible text concise: between 350 and 820 characters (strictly < 900 visible chars).
3. Use ONLY valid Telegram HTML tags: `<b>...</b>`, `<blockquote>...</blockquote>`, `<a href="...">...</a>`. Every opened tag MUST be closed. Do NOT use `<br>`, `<p>`, or Markdown `**`.
4. Lead with ONE fitting emoji (`⚡️`, `🚨`, `❓`, `🔰`, `🚀`, `🏆`, `🚛`, `💻`) + `<b>Headline</b>`.
5. End EVERY caption with these exact two lines:
Deregi: <a href="EXACT_SOURCE_URL">SHORT_SOURCE_LABEL</a>
👉 <a href="https://t.me/qrjanaliq">@qrjanaliq — aǵza bolıw</a>

Return ONLY a JSON array of objects with keys:
- "candidate_idx": integer index into CANDIDATE STORIES
- "source_url": string (exact URL from that candidate)
- "caption_html": string (complete ready-to-post Telegram HTML caption)
- "wikimedia_search_keywords": string (2-3 simple English nouns for backup photo search, e.g. "Uzbekistan parliament" or "high speed train")
"""

    resp = generate_content_with_fallback(
        client,
        TEXT_MODELS,
        prompt,
        types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.25,
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


def transliterate_stray_cyrillic_outside_tags(html_text: str) -> str:
    """Convert any stray Cyrillic characters or homoglyphs in text nodes into pure Karakalpak Latin."""
    parts = re.split(r"(<[^>]+>)", html_text)
    out: list[str] = []
    for part in parts:
        if part.startswith("<") and part.endswith(">"):
            out.append(part)
        else:
            converted = "".join(CYR_TO_QQ_LATIN.get(ch, ch) for ch in part)
            out.append(converted)
    return "".join(out)


def sanitize_and_validate_caption(caption: str) -> str | None:
    caption = caption.lstrip("\ufeff").strip()
    caption = caption.replace("<br>", "\n").replace("<br/>", "\n").replace("<br />", "\n")

    if CYRILLIC_RE.search(caption):
        found_cyr = CYRILLIC_RE.findall(caption)
        print(f"[INFO] Auto-transliterating {len(found_cyr)} stray Cyrillic chars to Karakalpak Latin: {found_cyr[:10]}")
        caption = transliterate_stray_cyrillic_outside_tags(caption)

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


def verify_photo_clean_and_relevant(
    client: genai.Client, img_bytes: bytes, story_summary: str
) -> bool:
    """Inspect candidate image via PIL + Gemini Vision to reject competitor watermarks or off-topic photos."""
    try:
        with Image.open(io.BytesIO(img_bytes)) as im:
            w, h = im.size
            if w < 250 or h < 150:
                return False
    except Exception:
        return False

    try:
        check_prompt = (
            f"Story summary: {story_summary[:300]}\n"
            "Inspect this image carefully. Return JSON {\"ok\": true/false, \"reason\": \"...\"}. "
            "Set \"ok\": false if: (1) it contains a competitor Telegram channel watermark/handle like "
            "@KARAKALPAK24, @xaliq_ushin, @KarPressa, @qalampir, @kunuzofficial, OR "
            "(2) it is a generic website logo/icon (like a Google News 'G' icon or plain logo), OR "
            "(3) the image is completely unrelated to the story (e.g. a football player on a non-sports story). "
            "Official government emblems or official appointment cards without competitor @handles are OK."
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
        verdict = json.loads(res.text)
        time.sleep(1.2)
        if not verdict.get("ok", False):
            print(f"[INFO] Vision rejected photo: {verdict.get('reason')}")
            return False
        return True
    except Exception as exc:
        print(f"[WARN] Vision check warning (allowing valid PIL image): {exc}")
        return True


def search_wikimedia_fallback_photos(keywords: str) -> list[str]:
    """Free, watermark-free editorial photo fallback from Wikimedia Commons."""
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

    # Append Wikimedia Commons backup URLs in case source had no photo or had a competitor watermark
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

    print("[1/4] Checking @qrjanaliq live feed for deduplication...")
    existing_posts, seen_urls = fetch_existing_channel_posts()
    print(f"      Found {len(existing_posts)} recent channel posts & {len(seen_urls)} seen URLs.")

    print("[2/4] Scanning global & official Karakalpak/Uzbek feeds...")
    raw_candidates: list[dict[str, Any]] = []
    raw_candidates.extend(scrape_kknews())
    for cat, ch, hrs in TELEGRAM_SOURCES:
        raw_candidates.extend(scrape_telegram_channel(cat, ch, hrs))
    raw_candidates.extend(scrape_kun_uz())
    raw_candidates.extend(scrape_rss_and_global_feeds())

    candidates = [
        c
        for c in raw_candidates
        if c["url"].split("?")[0].rstrip("/") not in seen_urls
        and c.get("fallback_post_url", "").rstrip("/") not in seen_urls
    ][:45]
    print(f"      Collected {len(candidates)} fresh unseen candidate stories.")
    if not candidates:
        print("[DONE] No unseen stories right now.")
        return 0

    ask_count = min(max_posts + 2, 5)
    print(f"[3/4] Curating & writing Karakalpak Latin posts with Gemini (target={max_posts}, pool={ask_count})...")
    selected = curate_and_write_posts(client, candidates, existing_posts, ask_count)

    published_count = 0
    new_urls = list(seen_urls)
    new_titles = list(existing_posts)

    print("[4/4] Verifying photos & publishing to @qrjanaliq...")
    for item in selected:
        if published_count >= max_posts:
            break
        idx = item.get("candidate_idx")
        if idx is None or not (0 <= idx < len(candidates)):
            print(f"[WARN] Invalid candidate_idx={idx}, skipping.")
            continue
        cand = candidates[idx]
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
            new_urls.append(cand["url"].split("?")[0].rstrip("/"))
            if cand.get("fallback_post_url"):
                new_urls.append(cand["fallback_post_url"].rstrip("/"))
            new_titles.append(caption[:200])
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
