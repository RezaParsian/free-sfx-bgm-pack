"""build_html.py — ساخت راهنمای HTML تک‌فایله (RTL، بدون منبع خارجی)"""
import os, csv, glob, wave

ROOT = os.environ.get("PACKDIR", "../audio-pack")
OUT = os.environ.get("OUTFILE", "../guides/guide.html")

# خواندن مدت زمان واقعی از فایل‌های WAV
DUR = {}
for f in glob.glob(os.path.join(ROOT, "sfx", "*.wav")) + glob.glob(os.path.join(ROOT, "bgm", "*.wav")):
    w = wave.open(f)
    DUR[os.path.basename(f)[:-4]] = w.getnframes() / w.getframerate()


def d(name):
    v = DUR.get(name, 0)
    return f"{v:.2f}s"


CATS = [
    ("ترنزیشن و کات", "#6366F1", "🔀", [
        ("whoosh_transition", "ووش نرم با پن چپ‌به‌راست", "کات بزرگ، تغییر بخش، ورود به اسکرین‌رکوردر",
         "۳–۵ فریم <b>قبل از</b> کات", "−۸ تا −۶ dB"),
        ("whoosh_short", "ووش کوتاه و سریع", "جامپ‌کات، حذف تپق، کات ریتمیک", "دقیقاً روی کات", "−۱۲ تا −۱۰ dB"),
        ("cut_tick", "تیک خیلی کوتاه و ظریف", "هر کات ساده، تعویض اسلاید، تغییر زاویه", "روی فریم کات", "−۱۴ dB"),
        ("riser_tension", "ریزر صعودی", "قبل از رونمایی قیمت، نتیجه‌ی بنچمارک، «اما یه مشکل هست»",
         "۲.۶ ثانیه قبل از لحظه‌ی اوج", "−۱۰ dB"),
        ("rewind_sweep", "افکت ریوایند / فلش‌بک", "بازگشت به عقب، «بریم عقب‌تر ببینیم»",
         "هم‌زمان با افکت تصویری Reverse", "−۱۰ dB"),
    ]),
    ("UI و نرم‌افزار", "#0EA5E9", "🖱️", [
        ("ui_click", "کلیک نرم رابط کاربری", "کلیک روی دکمه/منو در اسکرین‌رکوردر", "دقیقاً روی فریم کلیک موس", "−۱۲ dB"),
        ("ui_double_click", "دو کلیک پشت‌سرهم", "دابل‌کلیک، بازکردن فایل/اپ", "روی فریم کلیک دوم", "−۱۲ dB"),
        ("ui_hover_soft", "صدای خیلی ظریف هاور", "حرکت نشانگر روی منو، تولتیپ", "روی فریم ورود نشانگر", "−۱۸ تا −۱۶ dB"),
        ("typing_keyboard", "تایپ کردن", "تایپ در ترمینال، سرچ‌بار، کدنویسی، پرامپت AI",
         "با Rate Stretch با سرعت تایپ واقعی هماهنگ کن", "−۱۶ dB"),
        ("text_reveal_soft", "سوییچ نرم با پن", "ظهور زیرنویس، بولت‌پوینت، عنوان، آیکون", "روی شروع انیمیشن متن", "−۱۴ dB"),
        ("swipe_paper", "ورق‌زدن / سوایپ", "تعویض اسلاید، سوایپ گالری گوشی، تغییر تب", "روی فریم شروع حرکت", "−۱۳ dB"),
        ("camera_shutter", "شاتر دوربین", "اسکرین‌شات، نمایش عکس", "هم‌زمان با یک فریم فلش سفید", "−۱۰ dB"),
    ]),
    ("اعلان، موفقیت و خطا", "#10B981", "✅", [
        ("notification_ding", "دینگ اعلان", "نوتیفیکیشن، نکته‌ی مهم، ایده‌ی جدید 💡", "روی فریم ظهور متن نکته", "−۱۲ dB"),
        ("success_chime", "چایم موفقیت سه‌نتی", "موفقیت تست، نصب کامل، تیک چک‌لیست", "روی فریم موفقیت", "−۱۰ dB"),
        ("error_buzz", "بازر خطا", "باگ، شکست تست، «این کار رو نکن»", "روی فریم خطا + لرزش/رنگ قرمز", "−۱۲ dB"),
        ("coin_ping", "پینگ سکه / امتیاز", "امتیاز، لایک، آنباکس آیتم، شمارش آمار", "روی هر واحد شمارش", "−۱۴ dB"),
        ("sparkle_magic", "درخشش جادویی", "قابلیت AI، Before/After، تغییر چشمگیر", "زیر نمایش مقایسه", "−۱۴ dB"),
    ]),
    ("ضربه و تاکید", "#F43F5E", "💥", [
        ("impact_deep", "ضربه‌ی عمیق با ساب", "عدد نهایی، نتیجه‌ی بنچمارک، تیتر بزرگ", "روی فریمی که عدد کامل ظاهر شده", "−۸ dB"),
        ("impact_bright", "ضربه‌ی روشن و کوتاه‌تر", "تاکید سبک، پاپ‌آپ آیکون، «دقت کن!»", "روی فریم تاکید", "−۱۱ dB"),
        ("boom_cinematic", "بوم سینمایی", "شروع ویدیو بعد از هوک، ورود لوگو، رونمایی", "بعدش ۰.۵ ثانیه سکوت بگذار", "−۶ dB"),
        ("pop_bubble", "پاپ حبابی بامزه", "ظهور آیکون/ایموجی/برچسب قیمت", "روی فریم ظهور", "−۱۳ dB"),
        ("gong_section", "گنگ عمیق", "شروع بخش/فصل جدید، تغییر موضوع، Q&A", "هم‌زمان با Chapter Marker یوتیوب", "−۱۰ dB"),
        ("heartbeat_tension", "ضربان قلب تنشی", "لحظه‌ی حساس، تست دوام، انتظار برای نتیجه", "حجم پایین؛ زیر ۴.۶ ثانیه", "−۱۴ dB"),
    ]),
    ("ابزار تولید محتوا", "#F59E0B", "🎬", [
        ("countdown_beeps", "۴ بیپ شمارش معکوس", "قبل از شروع تست/چالش، «۳…۲…۱…»", "بیپ آخر = لحظه‌ی شروع", "−۱۲ dB"),
        ("countdown_tick_single", "تک‌تیک تایمر", "هر ثانیه‌ی چالش، تیک چک‌لیست", "با فاصله‌ی دقیق ۱ ثانیه Duplicate کن", "−۱۴ dB"),
        ("air_horn_meme", "ایرهورن میم", "لحظه‌ی شوخی، «باورت میشه؟!»", "در محتوای برند/اسپانسری نه", "−۱۲ dB"),
        ("vinyl_stop", "توقف وینیل (پیچ نزولی)", "پانچ‌لاین، «…ولی صبر کن»", "موزیک را دقیقاً در همان فریم قطع کن", "−۱۰ dB"),
        ("laser_pew", "لیزر رترو", "طنز، اشاره‌ی سریع، «اشتباه رایج»", "فقط محتوای طنز", "−۱۴ dB"),
        ("logo_sting", "استینگ لوگوی سه‌نتی", "اینترو، اوترو، امضای پایان ویدیو", "همیشه در یک نقطه‌ی ثابت", "−۸ dB"),
    ]),
    ("فضاسازی و لوپ", "#8B5CF6", "🌫️", [
        ("room_tone_loop", "نویز اتاق + هوم + فن", "زیر <b>کل</b> ویدیو برای پرکردن سکوت مطلق",
         "Loop از ابتدا تا انتها، بدون قطع", "−۳۴ تا −۳۰ dB"),
        ("vinyl_crackle_loop", "کرکل صفحه‌ی گرامافون", "حال‌وهوای لوفای/نوستالژیک", "Loop؛ حجم خیلی کم", "−۲۴ dB"),
    ]),
]

BGMS = [
    ("bgm_hook_loop_8s", 124, "پرانرژی و لوپ‌شونده", "۳ ثانیه‌ی اول ریلز/شورتس + اینترو کوتاه", "−۱۴ dB", "hot"),
    ("bgm_tech_explainer", 118, "پیش‌رونده و مدرن (پلد + آرپژ + درام)", "پیش‌فرض تو: بررسی محصول، ویدیوی ۵–۱۵ دقیقه‌ای", "−۲۰ dB", "main"),
    ("bgm_upbeat_vlog", 112, "روشن و مثبت", "اینترو، ولاگ، آنباکسینگ", "−۲۰ dB", ""),
    ("bgm_playful_marimba", 104, "بامزه و جهشی (ماریمبا)", "نکات طنز، اشتباهات رایج، ترفندها", "−۲۲ dB", ""),
    ("bgm_cinematic_tension", 80, "تیره و پرتنش + ریزر و ضربه‌ی پایانی", "مقایسه‌ی حساس، تست دوام، «مشکل اینجاست»", "−۲۰ dB", ""),
    ("bgm_lofi_focus", 74, "لوفای/چیل + کرکل وینیل", "آموزش طولانی، کدنویسی، Study-with-me", "−۲۲ dB", ""),
    ("bgm_screen_bed", 60, "خیلی خلوت، بدون درام", "زیر اسکرین‌رکوردر و آموزش نرم‌افزار", "−۲۴ dB", "main"),
    ("bgm_ambient_underscore", 60, "خنثی و اتمسفریک", "توضیح مفاهیم، زیر دیاگرام و اسلاید", "−۲۲ dB", ""),
]

SRC = [
    ("YouTube Audio Library", "https://studio.youtube.com/", "رایگان؛ بخشی CC BY", "بعضی‌ها بله",
     "مطمئن‌ترین گزینه برای یوتیوب — فیلتر «Attribution not required» را بزن"),
    ("Pixabay Music", "https://pixabay.com/music/", "Pixabay Content License", "خیر",
     "بزرگ‌ترین کتابخانه‌ی رایگان؛ فروش/توزیع مجدد خود فایل‌ها ممنوع"),
    ("Pixabay SFX", "https://pixabay.com/sound-effects/", "Pixabay Content License", "خیر", "۱۳۰ هزار افکت"),
    ("Freesound", "https://freesound.org/", "هر فایل متفاوت: CC0 / CC BY / CC BY-NC", "CC BY → بله",
     "فقط <b>CC0</b> را فیلتر کن؛ CC BY-NC برای ویدیوی درآمدزا ممنوع"),
    ("Mixkit", "https://mixkit.co/free-sound-effects/", "رایگان تجاری", "خیر", "بدون ثبت‌نام دانلود می‌شود"),
    ("Uppbeat", "https://uppbeat.io/", "رایگان با سقف ماهانه", "بله — اجباری", "Safelist برای رفع ادعای Content ID"),
    ("Bensound", "https://www.bensound.com/", "بخشی رایگان", "بله", "نسخه‌ی رایگان معمولاً فقط آنلاین"),
    ("Chosic", "https://www.chosic.com/free-music/all/", "عمدتاً CC0", "خیر", "موزیک خنثی و آرشیوی"),
    ("FreePD", "https://freepd.com/", "Public Domain", "خیر", "کاملاً آزاد"),
    ("ZapSplat", "https://www.zapsplat.com/", "رایگان با ثبت‌نام", "بله", "دسته‌بندی افکت‌ها عالی است"),
    ("Mubert AI", "https://mubert.com/", "اشتراکی (AI)", "خیر", "برای حجم تولید بالا"),
]

MIX = [
    ("صدای خودت (Voice-over)", "0 dB (مرجع)", "−۱۶ تا −۱۴ LUFS", "همیشه پادشاه میکس"),
    ("موسیقی زیر ویس", "−۲۰ تا −۱۶ dB", "—", "با Ducking خودکار یا Keyframe دستی"),
    ("موسیقی اینترو/اوترو (بدون ویس)", "−۱۴ تا −۱۲ dB", "—", "می‌تواند بلندتر باشد"),
    ("افکت تاکید (impact / boom / gong)", "−۸ تا −۶ dB", "—", "بیش از ۲ بار در دقیقه نه"),
    ("افکت ترنزیشن (whoosh / riser)", "−۱۰ تا −۸ dB", "—", "—"),
    ("افکت UI (click / pop / tick)", "−۱۴ تا −۱۰ dB", "—", "روی فریم دقیق"),
    ("Ambience (room tone / crackle)", "−۳۴ تا −۲۸ dB", "—", "زیر کل ویدیو، لوپ"),
    ("خروجی نهایی یوتیوب و اینستاگرام", "—", "<b>−۱۴ LUFS</b>", "True Peak حداکثر <b>−۱ dBTP</b>"),
    ("خروجی پادکست", "—", "−۱۶ تا −۱۴ LUFS", "True Peak حداکثر −۱ dBTP"),
]

TL = [
    ("0:00 – 0:03", "هوک", "bgm_hook_loop_8s (بلند) + impact_deep روی کلمه‌ی کلیدی"),
    ("0:03 – 0:08", "اینترو / لوگو", "logo_sting — بدون موزیک"),
    ("0:12 – 2:30", "معرفی محصول", "bgm_tech_explainer @ −۲۰ dB"),
    ("2:30 – 4:00", "مشخصات / اسلاید", "bgm_screen_bed @ −۲۴ dB"),
    ("4:00 – 5:00", "بنچمارک و تست", "bgm_cinematic_tension + riser_tension قبل از نتیجه"),
    ("5:00 – 6:30", "نکات و ترفندها", "bgm_playful_marimba @ −۲۲ dB"),
    ("6:30 – 7:30", "جمع‌بندی", "bgm_tech_explainer (بازگشت به تم اصلی)"),
    ("7:30 – 8:00", "CTA / سابسکرایب", "logo_sting + success_chime"),
    ("کل ویدیو", "ترک زیرین", "room_tone_loop @ −۳۲ dB"),
]

CHK = [
    "در هر ۱۰ ثانیه بیشتر از ۲ افکت نگذار (مگر ریلز تند).",
    "از یک افکت بیش از ۵ بار در دقیقه استفاده نکن؛ گوش عادت می‌کند و اثرش صفر می‌شود.",
    "افکت UI باید دقیقاً روی فریم رخداد باشد — ۲ فریم خطا یعنی «غیرحرفه‌ای».",
    "اگر ویس و موزیک تضاد دارند، موزیک را کم کن؛ ویس را تقویت نکن.",
    "قبل از نکته‌ی مهم: ۰.۵ ثانیه سکوت + impact_deep → قوی‌تر از هر افکت پرصدا.",
    "هیچ‌وقت سکوت دیجیتال مطلق نگذار؛ room_tone زیر همه‌چیز باشد.",
    "بیسِ boom روی اسپیکر گوشی شنیده نمی‌شود → یک لایه impact_bright هم رویش بگذار.",
    "خروجی: −۱۴ LUFS و True Peak زیر −۱ dB.",
    "سه بار مرور کن: بار اول تصویر، بار دوم با چشم بسته فقط صدا، بار سوم با گوشی.",
    "لایسنس هر فایل خارجی را بخوان و رسید/اسکرین‌شاتش را نگه دار.",
]

CSS = """
:root{--bg:#0b1020;--card:#151b30;--card2:#1c2440;--tx:#e6e9f2;--mut:#9aa3bd;--line:#2a3352;--acc:#6366f1}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--tx);font-family:'Vazirmatn','IRANSans','Segoe UI',Tahoma,'Noto Naskh Arabic',sans-serif;line-height:1.85;font-size:15px}
.wrap{max-width:1120px;margin:0 auto;padding:0 20px 80px}
header{padding:52px 20px 40px;text-align:center;background:radial-gradient(1200px 400px at 50% -80px,#2b3a8f55,transparent),linear-gradient(180deg,#101736,#0b1020);border-bottom:1px solid var(--line)}
header h1{margin:0 0 10px;font-size:31px;letter-spacing:-.4px}
header p{margin:6px auto;max-width:760px;color:var(--mut);font-size:15px}
.badges{display:flex;flex-wrap:wrap;gap:8px;justify-content:center;margin-top:18px}
.b{background:#1e2749;border:1px solid var(--line);color:#cdd5ee;border-radius:999px;padding:5px 13px;font-size:12.5px}
.b.g{background:#0f3d2e;border-color:#1d6f52;color:#8ff0c8}
h2{font-size:23px;margin:52px 0 6px;padding-top:14px;border-top:1px solid var(--line)}
h2 .n{color:var(--acc);font-size:15px;margin-left:8px;font-weight:700}
.sub{color:var(--mut);margin:0 0 20px;font-size:14px}
h3{font-size:17px;margin:30px 0 10px}
table{width:100%;border-collapse:collapse;margin:12px 0 8px;font-size:13.6px;background:var(--card);border-radius:12px;overflow:hidden}
th{background:#232c4d;color:#dbe2ff;text-align:right;padding:11px 12px;font-weight:700;border-bottom:1px solid var(--line);white-space:nowrap}
td{padding:10px 12px;border-bottom:1px solid #202945;vertical-align:top;color:#dfe4f4}
tr:last-child td{border-bottom:none}
tr:hover td{background:#1a2240}
code{background:#0f1730;border:1px solid var(--line);border-radius:6px;padding:1.5px 7px;font-family:'SFMono-Regular',Consolas,monospace;font-size:12.4px;color:#8fe3c8;direction:ltr;display:inline-block}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:18px 20px;margin:14px 0}
.card h4{margin:0 0 8px;font-size:16px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(258px,1fr));gap:14px;margin:16px 0}
.pill{display:inline-block;background:#252f55;border:1px solid var(--line);border-radius:999px;padding:2px 11px;font-size:12px;color:#c6cdec;margin-left:6px}
.lvl{font-family:Consolas,monospace;direction:ltr;display:inline-block;background:#0f1730;border:1px solid var(--line);border-radius:6px;padding:1px 8px;font-size:12px;color:#ffd28f}
.dur{color:var(--mut);font-size:12px;font-family:Consolas,monospace;direction:ltr}
.cat{display:inline-flex;align-items:center;gap:8px;font-size:18px;font-weight:700;margin:34px 0 4px}
.dot{width:11px;height:11px;border-radius:50%}
.tip{background:linear-gradient(90deg,#132b45,#12203a);border-right:3px solid #38bdf8;border-radius:10px;padding:13px 17px;margin:14px 0;font-size:14px}
.warn{background:linear-gradient(90deg,#3a1f22,#2a1719);border-right:3px solid #f87171;border-radius:10px;padding:13px 17px;margin:14px 0;font-size:14px}
.ok{background:linear-gradient(90deg,#123126,#10241d);border-right:3px solid #34d399;border-radius:10px;padding:13px 17px;margin:14px 0;font-size:14px}
.timeline{font-family:Consolas,monospace;direction:ltr;background:#0f1730;border:1px solid var(--line);border-radius:12px;padding:16px 18px;overflow-x:auto;font-size:12.6px;color:#c8d0ea;line-height:1.95}
ul.chk{list-style:none;padding:0;margin:10px 0}
ul.chk li{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:10px 14px 10px 44px;margin:7px 0;position:relative;font-size:14px}
ul.chk li:before{content:"☐";position:absolute;right:14px;top:8px;color:#7dd3fc;font-size:17px}
.toc{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:16px 20px;margin:26px 0}
.toc a{color:#a5b4fc;text-decoration:none;display:inline-block;margin:3px 4px 3px 16px;font-size:14px}
a{color:#93c5fd}
.hot{background:#3a1e2c !important}
.main{background:#16324a !important}
footer{margin-top:60px;padding-top:20px;border-top:1px solid var(--line);color:var(--mut);font-size:13px;text-align:center}
@media print{body{background:#fff;color:#000}.card,table,.tip,.warn,.ok,ul.chk li{background:#fff!important;color:#000!important;border-color:#bbb}header{background:#fff}}
"""

H = []
A = H.append
A(f"<!doctype html><html lang='fa' dir='rtl'><head><meta charset='utf-8'>")
A(f"<meta name='viewport' content='width=device-width,initial-scale=1'>")
A("<title>پک افکت صوتی و BGM — محتوای تکنولوژی و آموزشی</title>")
A(f"<style>{CSS}</style></head><body>")

A("<header><h1>🎧 پک افکت صوتی + موسیقی پس‌زمینه</h1>")
A("<p>راهنمای کامل صداگذاری برای محتوای <b>تکنولوژی و آموزشی</b> در یوتیوب و اینستاگرام — همراه با اینکه هر افکت <b>دقیقاً کجا و با چه سطحی</b> استفاده شود.</p>")
A("<div class='badges'>")
A("<span class='b g'>✔ ۱۰۰٪ اورجینال و بدون کپی‌رایت</span>")
A(f"<span class='b'>{len(DUR) - len(BGMS)} افکت صوتی</span>")
A(f"<span class='b'>{len(BGMS)} ترک موسیقی</span>")
A("<span class='b'>WAV + MP3</span><span class='b'>نرمالایز شده: SFX −۱۸ / BGM −۲۰ LUFS</span>")
A("<span class='b'>بدون نیاز به ذکر منبع</span><span class='b'>قابل استفاده‌ی تجاری</span></div></header>")

A("<div class='wrap'>")

A("<div class='toc'><b>فهرست:</b><br>")
for i, t in enumerate(["چطور شروع کنم", "کتابخانه‌ی افکت‌ها", "موسیقی پس‌زمینه (BGM)",
                       "نقشه‌ی موزیک در یک ویدیو", "منابع رایگان BGM", "تنظیم سطح صدا",
                       "قوانین طلایی و چک‌لیست", "کپی‌رایت و امنیت کانال", "ساخت فایل جدید"], 1):
    A(f"<a href='#s{i}'>{i}. {t}</a>")
A("</div>")

# ── ۱ شروع
A("<h2 id='s1'><span class='n'>۰۱</span>چطور شروع کنم</h2>")
A("<div class='grid'>")
A("<div class='card'><h4>🎞️ ادیت در پریمیر / داوینچی / فاینال‌کات</h4>"
  "<p>از پوشه‌ی <code>audio-pack/sfx</code> و <code>audio-pack/bgm</code> فایل‌های <b>WAV</b> را بردار. "
  "کیفیت اصلی است و برای تغییر سرعت (Rate Stretch) و کش‌دان بدون افت مناسب است.</p></div>")
A("<div class='card'><h4>📱 ادیت در CapCut / InShot / موبایل</h4>"
  "<p>از <code>audio-pack/mp3</code> استفاده کن. حجمش یک‌دهم است و همه‌جا باز می‌شود.</p></div>")
A("<div class='card'><h4>🎚️ سه قدم راه‌اندازی</h4>"
  "<p>۱) افکت‌ها را روی یک <b>ترک صوتی جدا</b> زیر صدای خودت بگذار.<br>"
  "۲) موزیک را روی ترک دیگر و <b>−۲۰ dB</b> زیر ویس.<br>"
  "۳) <code>room_tone_loop</code> را از ابتدا تا انتها لوپ کن.</p></div>")
A("</div>")
A("<div class='ok'><b>خبر خوب:</b> همه‌ی فایل‌ها از قبل نرمالایز شده‌اند "
  "(افکت‌ها −۱۸ LUFS، موزیک‌ها −۲۰ LUFS). یعنی اگر بدون تغییر سطح روی تایم‌لاین بگذاری، "
  "<b>نسبت افکت‌ها به هم از قبل درست است</b> — فقط کل ترک موزیک را پایین بده تا زیر حرفت گم شود.</div>")

# ── ۲ افکت‌ها
A("<h2 id='s2'><span class='n'>۰۲</span>کتابخانه‌ی افکت‌ها — کجا استفاده شود</h2>")
A("<p class='sub'>«سطح پیشنهادی» نسبت به صدای اصلی خودت (Voice-over = 0 dB) است.</p>")
for title, color, emoji, items in CATS:
    A(f"<div class='cat'><span class='dot' style='background:{color}'></span>{emoji} {title}"
      f"<span class='pill'>{len(items)} فایل</span></div>")
    A("<table><tr><th>فایل</th><th>مدت</th><th>چیست</th><th>کجا استفاده شود</th><th>زمان‌بندی دقیق</th><th>سطح</th></tr>")
    for name, what, where, when, lvl in items:
        A(f"<tr><td><code>{name}</code></td><td class='dur'>{d(name)}</td><td>{what}</td>"
          f"<td>{where}</td><td>{when}</td><td><span class='lvl'>{lvl}</span></td></tr>")
    A("</table>")

A("<div class='tip'><b>فرمول طلایی ترنزیشن:</b> <code>riser_tension</code> → (کات) → "
  "<code>impact_deep</code> یا <code>boom_cinematic</code>. ریزر را ۲.۶ ثانیه قبل از لحظه‌ی اوج شروع کن.</div>")
A("<div class='tip'><b>تکنیک حرفه‌ای:</b> <code>room_tone_loop</code> را روی یک ترک جدا از ابتدا تا انتهای ویدیو بینداز و Loop کن. "
  "بعد هیچ کاتی «سکوت ناگهانی» ندارد. همین یک کار، ویدیوی آماتور را از حرفه‌ای جدا می‌کند.</div>")

# ── ۳ BGM
A("<h2 id='s3'><span class='n'>۰۳</span>موسیقی پس‌زمینه (BGM)</h2>")
A("<p class='sub'>همه‌ی این ترک‌ها با کد سنتز شده‌اند — هیچ نمونه‌ی صوتی خارجی در آن‌ها نیست، پس هیچ ادعای Content ID روی ویدیویت نمی‌نشیند.</p>")
A("<table><tr><th>فایل</th><th>مدت</th><th>BPM</th><th>حال‌وهوا</th><th>بهترین کاربرد</th><th>سطح زیر ویس</th></tr>")
for name, bpm, mood, use, lvl, tag in BGMS:
    cls = " class='hot'" if tag == "hot" else (" class='main'" if tag == "main" else "")
    A(f"<tr{cls}><td><code>{name}</code></td><td class='dur'>{d(name)}</td><td>{bpm}</td>"
      f"<td>{mood}</td><td>{use}</td><td><span class='lvl'>{lvl}</span></td></tr>")
A("</table>")
A("<div class='tip'><b>دو ترک کلیدی:</b> ردیف <span style='color:#f9a8d4'>صورتی</span> = <code>bgm_hook_loop_8s</code> "
  "برای ۳ ثانیه‌ی اول ریلز؛ ردیف <span style='color:#7dd3fc'>آبی</span> = دو ترک پیش‌فرض برای ویدیوی بلند "
  "(<code>bgm_tech_explainer</code> برای صحبت و <code>bgm_screen_bed</code> برای زیر اسکرین‌رکوردر).</div>")
A("<div class='warn'><b>نکته‌ی مهم برای موزیک زیر ویس:</b> جای فرکانس صدای انسان ۱ تا ۴ kHz است. "
  "اگر موزیکت مزاحم حرف‌زدنت شد، به‌جای کم‌کردن حجم، یک <b>EQ</b> روی ترک موزیک بزن و "
  "فرکانس ۱.۲ تا ۳ kHz را ۴ تا ۶ dB کاهش بده. نتیجه بسیار طبیعی‌تر از کم‌کردن صداست.</div>")

# ── ۴ نقشه تایم‌لاین
A("<h2 id='s4'><span class='n'>۰۴</span>نقشه‌ی موزیک در یک ویدیوی ۸ دقیقه‌ای</h2>")
A("<table><tr><th>بازه</th><th>بخش</th><th>صدا</th></tr>")
for a, b, c in TL:
    A(f"<tr><td class='dur' style='white-space:nowrap'>{a}</td><td>{b}</td><td><code>{c}</code></td></tr>")
A("</table>")
A("<div class='tip'><b>قانون تغییر موزیک:</b> موزیک را فقط در مرز «بخش‌ها» عوض کن، نه وسط جمله — "
  "و همیشه یک <b>Crossfade نیم‌ثانیه‌ای</b> بین دو ترک بگذار.</div>")

A("<h3>الگوی ریلز / شورتس (۱۵ تا ۶۰ ثانیه)</h3>")
A("<table><tr><th>ثانیه</th><th>چه اتفاقی</th><th>صدا</th></tr>")
for a, b, c in [("0.0 – 0.5", "<b>ضربه‌ی اول</b> — ۷۰٪ ری‌تنشن این‌جا تعیین می‌شود", "impact_deep یا boom_cinematic"),
                ("0.5 – 3", "بستر و ریتم", "bgm_hook_loop_8s (لوپ) + cut_tick روی هر کات"),
                ("هر متن", "ظهور متن روی تصویر", "text_reveal_soft یا pop_bubble"),
                ("لحظه‌ی «واو»", "اوج محتوا", "sparkle_magic یا success_chime"),
                ("شوخی", "میم", "air_horn_meme یا laser_pew"),
                ("پایان / CTA", "خاتمه", "vinyl_stop + logo_sting کوتاه")]:
    A(f"<tr><td class='dur'>{a}</td><td>{b}</td><td><code>{c}</code></td></tr>")
A("</table>")
A("<div class='warn'><b>تفاوت مهم ریلز و یوتیوب:</b> در اینستاگرام صدای <b>Trending Audio</b> الگوریتمی کمک می‌کند. "
  "استراتژی درست: موزیک ترند را روی حجم خیلی کم (−۲۴ dB) زیر کار بگذار و افکت‌های خودت را رویش بچین. "
  "در یوتیوب برعکس — موزیک باید کاملاً بی‌کپی‌رایت باشد.</div>")

# ── ۵ منابع
A("<h2 id='s5'><span class='n'>۰۵</span>منابع رایگان BGM و افکت (برای تنوع بیشتر)</h2>")
A("<table><tr><th>منبع</th><th>لایسنس</th><th>ذکر منبع</th><th>نکته</th></tr>")
for name, url, lic, att, note in SRC:
    A(f"<tr><td><a href='{url}'>{name}</a></td><td>{lic}</td><td>{att}</td><td>{note}</td></tr>")
A("</table>")
A("<h3>کلمات کلیدی جستجو برای محتوای تکنولوژی</h3><div class='card'>")
A("<p style='margin:4px 0'><code>corporate tech</code> <code>minimal technology</code> <code>product review background</code> "
  "<code>tutorial underscore</code> <code>ambient explainer</code> <code>upbeat digital</code> <code>clean corporate</code></p>")
A("<p style='margin:4px 0'><code>lofi study</code> <code>synthwave chill</code> <code>documentary pulse</code> "
  "<code>marimba playful</code> <code>tension riser</code> <code>logo sting</code> <code>ui sounds pack</code> "
  "<code>whoosh transition</code> <code>notification pop</code></p></div>")

# ── ۶ میکس
A("<h2 id='s6'><span class='n'>۰۶</span>تنظیم سطح صدا (Gain Staging)</h2>")
A("<table><tr><th>عنصر</th><th>سطح روی تایم‌لاین</th><th>بلندی هدف خروجی</th><th>نکته</th></tr>")
for a, b, c, e in MIX:
    A(f"<tr><td>{a}</td><td><span class='lvl'>{b}</span></td><td>{c}</td><td>{e}</td></tr>")
A("</table>")
A("<div class='card'><h4>Ducking (کم‌شدن خودکار موزیک زیر حرف)</h4>"
  "<p><b>CapCut:</b> ترک موزیک → <code>Audio</code> → <code>Ducking</code> را روشن کن.<br>"
  "<b>Premiere:</b> <code>Essential Sound</code> → موزیک را <i>Music</i> و ویس را <i>Dialogue</i> علامت بزن → "
  "<code>Ducking</code> → <code>Generate Keyframes</code>. تنظیم پیشنهادی: Duck Amount = <b>−۱۸ dB</b>، Ramp = <b>300ms</b>.<br>"
  "<b>DaVinci Resolve:</b> تب <code>Fairlight</code> → <code>Music Ducking</code> (یا Sidechain روی کمپرسور ترک موزیک).</p>"
  "<p style='color:#9aa3bd'>دستی: هر جا حرف می‌زنی موزیک −۲۰ dB، هر جا ساکتی −۱۲ dB، با رمپ ۲۵۰ تا ۳۵۰ میلی‌ثانیه.</p></div>")
A("<div class='card'><h4>اندازه‌گیری بلندی خروجی</h4><div class='timeline'>ffmpeg -i video.mp4 -af ebur128=peak=true -f null -</div>"
  "<p style='margin:10px 0 0'>در خروجی، <code>I:</code> = بلندی یکپارچه (باید حدود −۱۴ باشد) و <code>Peak:</code> نباید از −۱ dBTP بالاتر برود.</p></div>")

# ── ۷ چک‌لیست
A("<h2 id='s7'><span class='n'>۰۷</span>قوانین طلایی — چک‌لیست قبل از اکسپورت</h2>")
A("<ul class='chk'>")
for c in CHK:
    A(f"<li>{c}</li>")
A("</ul>")

# ── ۸ کپی‌رایت
A("<h2 id='s8'><span class='n'>۰۸</span>کپی‌رایت و امنیت کانال</h2>")
A("<div class='ok'><b>این پک:</b> صفر ریسک. همه‌چیز از صفر سنتز شده و هیچ نمونه‌ی صوتیِ کسی در آن نیست — "
  "نه Content ID، نه Claim، نه Strike. حتی می‌توانی <code>logo_sting</code> را به امضای صوتی برندت تبدیل کنی.</div>")
A("<h3>۵ قانون برای منابع خارجی</h3><div class='card'><ol style='margin:0;padding-right:20px'>")
for x in ["قبل از دانلود، لایسنس <b>همان فایل</b> را بخوان — نه لایسنس کلی سایت.",
          "<code>CC0</code> = کاملاً آزاد · <code>CC BY</code> = آزاد با ذکر منبع در توضیحات · <code>CC BY-NC</code> = <b>برای ویدیوی درآمدزا ممنوع</b>.",
          "اگر سایتی «Credit» خواست، متن را <b>دقیقاً</b> کپی کن و در Description یوتیوب بگذار.",
          "رسید یا اسکرین‌شات لایسنس هر ترک را <b>ذخیره کن</b> — اگر روزی Claim بیاید، تنها مدرکت همین است.",
          "به کانال‌های «No Copyright Music» یوتیوب اعتماد کامل نکن؛ خیلی‌ها بعداً لایسنس را عوض می‌کنند و روی ویدیوهای <b>قدیمی</b>‌ات Claim می‌زنند."]:
    A(f"<li style='margin:8px 0'>{x}</li>")
A("</ol></div>")

# ── ۹ ساخت مجدد
A("<h2 id='s9'><span class='n'>۰۹</span>ساخت فایل جدید / شخصی‌سازی</h2>")
A("<p class='sub'>کد سازنده‌ی همه‌ی فایل‌ها در پوشه‌ی <code>sfx-lab/</code> هست و قابل تغییر است.</p>")
A("<div class='timeline'>"
  "cd sfx-lab\n"
  "OUTDIR=../audio-pack/sfx  python3 build_sfx_extra.py   # ساخت هر ۳۱ افکت\n"
  "OUTDIR=../audio-pack/bgm  python3 build_bgm.py         # ساخت هر ۸ ترک موسیقی\n"
  "PACKDIR=../audio-pack     python3 encode_mp3.py        # تبدیل MP3 + نرمالایز + گزارش LUFS\n"
  "</div>")
A("<div class='grid'>")
A("<div class='card'><h4>چه چیزی را کجا عوض کنی</h4><p>"
  "<code>build_sfx.py</code> → تابع هر افکت: <code>peak</code> بلندی، <code>d</code> طول، <code>width</code> پهنای استریو، <code>pan</code> مکان چپ/راست<br>"
  "<code>build_bgm.py</code> → <code>bpm</code>، <code>bars</code> تعداد میزان، <code>prog</code> توالی آکوردها، <code>master_lp</code> فرکانس قطع<br>"
  "<code>audio_engine.py</code> → سازها و فیلترها (karplus، bell، pad، reverb، sidechain)</p></div>")
A("<div class='card'><h4>سریع‌ترین ترفند</h4><p>برای موزیک زیر ویس، <code>master_lp</code> را روی <b>۴۵۰۰</b> بگذار → "
  "موزیک تیره می‌شود و جای فرکانس صدای انسان خالی می‌ماند.</p>"
  "<p>برای لوگوی صوتی برندت، در <code>logo_sting</code> نت‌ها را عوض کن: "
  "<code>523.25</code> = دو، <code>784.0</code> = سل، <code>1046.5</code> = دو اکتاو بالاتر.</p></div>")
A("</div>")

A("<footer>ساخته‌شده با سنتز DSP — همه‌ی فایل‌ها اورجینال و بدون کپی‌رایت هستند. "
  "راهنمای کامل متنی در <code>guides/README.md</code> و جدول فیلترشدنی در <code>guides/audio-library.xlsx</code>.</footer>")
A("</div></body></html>")

os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, "w", encoding="utf-8").write("".join(H))
print("saved:", OUT, os.path.getsize(OUT), "bytes")
