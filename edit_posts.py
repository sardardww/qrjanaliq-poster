import sys
import os
import requests

sys.stdout.reconfigure(encoding='utf-8')

BOT_TOKEN = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
CHAT_ID = sys.argv[2] if len(sys.argv) > 2 else os.environ.get("TELEGRAM_CHAT_ID", "@qaraqalpaqshajanaliqlar").strip()

if not BOT_TOKEN:
    print("ERROR: BOT_TOKEN is missing! Pass it as: python edit_posts.py <BOT_TOKEN> [CHAT_ID]")
    sys.exit(1)

EDITS = [
    {
        "id": 68,
        "caption": """⚡️ <b>Ekstremistlik shólkemlerde qatnasqanlar 10 jılǵa shekem azatlıǵınan ayırılıwı múmkin</b>

Ózbekstan Prezidenti ekstremizmge qarsı gúresiw nátiyjeliligin arttırıwǵa qaratılǵan jańa nızamǵa qol qoydı.

<a href="https://t.me/kknews_uz/94722">Nızamǵa muwapıq</a>, ekstremistlik shólkemlerdiń jumısında qatnasqan yamasa olardıń materialların saqlap tarqatqan shaxslarǵa qatań shara kórilip, 10 jılǵa shekem azatlıǵınan ayırıw jazası belgilenedi.

👉 <a href="https://t.me/qaraqalpaqshajanaliqlar">@qaraqalpaqshajanaliqlar — aǵza bolıw</a>"""
    },
    {
        "id": 69,
        "caption": """🚛 <b>Túrkmenstan menen shegaradaǵı Alat postında jańa kópir qurıladı</b>

Ózbekstan hám Túrkmenstan shegarasındaǵı «Alat» baqlaw-ótkeriw punktinde jol infrastrukturasın jaqsılaw hám júk qatnawın ańsatlastırıw maqsetinde jańa kópir qurıw rejelestirilmekte.

<a href="https://www.spot.uz/ru/2026/11/04/olot-modernization/">Xalıqaralıq tasıwlar sheńberinde</a> júk mashinaları arasında tirkemelerdi almastırıw májbúriyatın biykarlaw usınıs etilmekte. Bul jańalıq tasıwshılardıń shegaradan ótiw waqtın sezilerli dárejede qısqartadı.

👉 <a href="https://t.me/qaraqalpaqshajanaliqlar">@qaraqalpaqshajanaliqlar — aǵza bolıw</a>"""
    },
    {
        "id": 70,
        "caption": """🚨 <b>Sadır Japarov «Gazprom»nan gaz tarmaǵın mámleket baqlawına qaytarıwı múmkinligin eskertti</b>

Qırǵızstan Prezidenti Sadır Japarov eger Rossiyanıń «Gazprom» kompaniyası aymaqlardı tolıq gazlastırıw minnetlemelerin orınlamasa, mámlekettiń gaz sistemasın keri qaytarıw sharaları kóriletuǵının málim etti.

<a href="https://kun.uz/news/2026/11/04/sadir-japarov-gazpromga-gaz-tarmogini-milliylashtirish-bilan-tahdid-qildi-59349">Talas rayonı xalqı menen ushırasıwda</a> Prezident 2013-jılı gaz tarmaǵı 1 dollarǵa satılǵanın hám házirgi waqıtta mámleket óz aymaǵın ǵárezsiz gazlastıra almay atırǵanın atap ótti.

👉 <a href="https://t.me/qaraqalpaqshajanaliqlar">@qaraqalpaqshajanaliqlar — aǵza bolıw</a>"""
    },
    {
        "id": 71,
        "caption": """💻 <b>Ilimpazlar bakteriyalardı joq etetuǵın jańa tis shetkasın jarattı</b>

Izertlewshiler tis qabatındaǵı karies hám qızıl iyek keselliklerin keltirip shıǵaratuǵın bakteriyalarǵa qarsı gúresiwshi ózi quwatlanıwshı tis shetkasın sınaqtan ótkerdi.

<a href="https://www.livescience.com/health/this-self-powered-toothbrush-makes-electricity-to-kill-cavity-causing-bacteria">Ilimiy izertlewlerge qaraǵanda</a>, tazalaw waqtında shetka kishkene elektr zaryadların payda etip, tis tasları hám mikroblardı nátiyjeli joq etedi hám awız quwıslıǵı qáwipsizligin támiyinleydi.

👉 <a href="https://t.me/qaraqalpaqshajanaliqlar">@qaraqalpaqshajanaliqlar — aǵza bolıw</a>"""
    }
]

url = f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageCaption"

for item in EDITS:
    pid = item["id"]
    payload = {
        "chat_id": CHAT_ID,
        "message_id": pid,
        "caption": item["caption"],
        "parse_mode": "HTML"
    }
    r = requests.post(url, json=payload, timeout=15)
    resp = r.json()
    if resp.get("ok"):
        print(f"[SUCCESS] Post #{pid} successfully edited in channel {CHAT_ID}!")
    else:
        print(f"[FAIL] Post #{pid} edit failed: {resp}")
