# QARAQALPAQSHA JAN'ALIQLAR (@qaraqalpaqshajanaliqlar) — Editorial & Technical Playbook

## Channel & Schedule Overview
- **Channel:** `@qaraqalpaqshajanaliqlar` (`https://t.me/qaraqalpaqshajanaliqlar`)
- **Active Posting Schedule:** Strictly every 15 minutes (:02, :17, :32, :47) from **04:00 AM to 00:00 AM (Midnight)** Tashkent time (`Asia/Tashkent`, UTC+5).
- **Quiet Sleep Hours:** **00:00 AM to 04:00 AM** (No posts while the audience is sleeping). Both GitHub Actions self-chaining and `cloud_poster.py` automatically enter quiet sleep mode during these hours.
- **Language:** 100% pure **Karakalpak Latin** (`Qaraqalpaq ádebiy tili` under the official 2016 Law: `Á á, Ó ó, Ú ú, Í ı, Ǵ ǵ, Ń ń`).
- **Translation Engine:** Render Tilmoch Translation API. Strict rule: If Tilmoch translation fails or errors, the post is SKIPPED (never post arbitrary or unverified text).

---

## 1. Editorial Format & Structure (Professional Multi-Paragraph Journalistic Style)

Every post MUST follow a clean, balanced narrative structure without artificial exaggeration:

```html
{OPTIONAL_FLAG_OR_EMOJI} <b>{Hook Headline}</b>

{Paragraph 1: Core news event with concrete details — exact names, ages, clubs/organizations, quotes in «...», dates, and exact statistics. Seamlessly embed the direct source link onto ONE focus action verb or keyword before the period, e.g. <a href="EXACT_URL">málim etti</a>.}

{Paragraph 2: Context, background facts, significance, or past milestones. SPARINGLY and only when genuinely organic (consumer polls, lifestyle debate), a natural question may be included. For standard formal news, keep it purely informative and factual without forced questions.}

👉 <a href="https://t.me/qaraqalpaqshajanaliqlar">Qaraqalpaqsha jańalıqlar — aǵza bolıw</a>
```

### Strict Editorial Rules (No Exaggeration):
1. **Headline:** Use Country Flag only when directly related to that country (e.g. 🇵🇹, 🇺🇿, 🇰🇿, 🇨🇳). Use a topical icon only when truly fitting, or leave clean without emoji for serious news. Do NOT spam or force emojis.
2. **Double Newlines (`\n\n`):** Cleanly separate Headline, Paragraph 1, Paragraph 2, and Footer.
3. **NO BULLET LISTS:** Strictly NEVER use bullet points (`🔹`, `▪️`, `➖`, •). Posts must read as high-level journalistic narratives.
4. **Interactive Questions — Selective & Natural:** Do NOT add questions to every post! In most posts (economic data, laws, science, accidents, official decisions), Paragraph 2 is a purely factual conclusion. Reserve questions only for occasions where public discussion is natural (~20% of posts).
5. **Single Embedded Source Link:** Wrap exactly ONE natural focus action verb or keyword in Paragraph 1 with `<a href="{exact_url}">...</a>`.
6. **NO Redundant Trailing Source Lines:** Strictly NEVER append "Derek:", "Tolıq maǵlıwmatlar bul jerde", or "Manba:".
7. **Strict Factual Grounding & Zero Hallucination:** Every single fact, quote, number, name, reason, and official statement MUST be 100% grounded in the source text. Strictly NEVER invent quotes from officials ("dep málim etti basqarma wákilleri", "mutasaddilar bildirdi"), reasons ("dıyqanlardıń miyneti arqasında"), or speculative claims not in the source. If a source is short (e.g. video headline), keep the summary concise and strictly true to what is actually stated. Factual truth strictly overrides length!
8. **Character Length:** Typically between 300 and 750 characters. For brief official notices, concise factual brevity is strongly preferred over invented fluff. Never pad with fake quotes or filler text.
9. **ZERO FORWARD ARTIFACTS (Strict Prohibition of forwardMessage into Channel):** NEVER use `forwardMessage` into the channel to inspect, read, or scan post captions. Standard Telegram Bot API lacks `getMessage`, which previously led to unsafe scripts forwarding messages into the channel to read the caption and then calling `deleteMessage`. If the delete failed or lagged, this left unsightly "Переслано из Qaraqalpaqsha jan'aliqlar" duplicates in the public feed! Always inspect channel messages safely using Telethon MTProto (`client.get_messages(chat, ids=...)`) or web previews. The channel feed must strictly contain ONLY direct, native publications!

---

## 2. Topic Mix & Content Balance

1. **Strict 3-Category Dynamic Rotation (QR / UZ / WORLD):** AI Studio analyzes the last 3 published posts on the channel. Whichever category is missing among the last 3 posts is strictly mandated for the next publication:
   - **QR (Qaraqalpaqstan):** Nukus, districts (Qońırat, Moynaq, Xojeli, Shimbay, etc.), Joqarǵı Keńes, local events, infrastructure, and ecology. Karakalpakstan regional news must NEVER be omitted!
   - **UZ (Ózbekstan):** National reforms, laws, citizen benefits, social protection, economy, and official ministries.
   - **WORLD (Dúnya / Tech):** High-impact global events, viral incidents, consumer AI, humanoid robotics, extreme engineering demos, and breakthrough technology.
   - **STRICT BAN on Niche Astronomy & Esoteric Science:** Absolutely NEVER select routine astronomy (meteor showers like Leonids/Perseids, comet dust trails, asteroid flybys, amateur stargazing tips) or narrow academic laboratory micro-research (mice genetics, cellular proteins, theoretical physics formulas). The audience consists of ordinary everyday readers who want interesting, exciting, relatable news — NOT professional astronomers or university professors!
2. **Zero Advertising:** Strictly NEVER post commercial ads, retail discounts, shop promos, or real estate listings.
3. **Zero Violence/Rape:** Strictly prohibited from covering sexual crimes, rape, or pedophilia.
4. **Sourcing Integrity & Karakalpakstan Exclusivity (Strict):** For Karakalpakstan news, NEVER choose from generic news aggregator channels (kknews, KarPressa, karinform). Select EXCLUSIVELY from official government systems, district administrations/akimiyats (@joqargikenes, @QResMinistrlerKenesi, @qrprokuratura, @qrsudlari, @nukus_press, @qonirat_press, @moynaq_press, @shimbayrk, @turtkulhokim_uz, @xodjeyli_rk, @pressTaqiyatas, @kanlikulnews, @beruniy_press, @kegeyli_press, @taxtakopir_press, @ellikqala_press, @qaraozek_press, @shomanay_press, @bozataw_press), state agencies (@krbajixana, @kkeduuz, @jaslar_isleri_agentligi), and official journalism (@xaliq_ushin). This keeps all Karakalpak news 100% exclusive and prevents advertising competitor channels. Disfavor repetitive generic aggregators (kun.uz).
5. **Interactive Video & Photo Priority:** When a candidate story contains verified video (`has_video: true`), strongly prioritize it when relevant to the target category. Videos drive 2x to 3x higher subscriber retention, watch time, and forwards. If video download/upload exceeds 40MB, is unsupported, or fails, automatically extract a clean frame directly from the video (or use its video thumbnail) and publish it as a photo post, so no visual content is lost and the post never skips.
