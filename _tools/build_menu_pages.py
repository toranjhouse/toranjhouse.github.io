# -*- coding: utf-8 -*-
"""v22: منوی چندصفحه‌ای — جزئیات و قیمت‌ها از صفحهٔ اصلی به menu.html می‌روند."""
import io, re, sys

ROOT = "/home/user/orsi/"
idx = io.open(ROOT + "index.html", encoding="utf-8").read()

# ---------- استخراج بخش‌ها ----------
head = idx[: idx.index("</head>") + len("</head>")]
header = idx[idx.index('<header class="site-head"'): idx.index("</header>") + len("</header>")]
foot_start = idx.index('<footer class="site-foot">')
footer = idx[foot_start: idx.index("</footer>", foot_start) + len("</footer>")]
totop_start = idx.index('<button id="toTop"')
totop = idx[totop_start: idx.index("</button>", totop_start) + len("</button>")]

tiles_s = idx.index('<div class="wrap menu-cats" id="menuCats"')
tabs_s = idx.index('<div class="wrap menu-tabs reveal"')
grid_s = idx.index('<div class="wrap menu-grid" id="menuGrid">')
book_s = idx.index('<div class="wrap menu-book reveal" id="prices">')
more_s = idx.index('<div class="wrap menu-more reveal">')
sec_end = idx.index("</section>", more_s)

tiles_block = idx[tiles_s:tabs_s]
tabs_block = idx[tabs_s:grid_s]
grid_block = idx[grid_s:book_s]
book_block = idx[book_s:more_s]
more_block = idx[more_s:sec_end]

articles = re.findall(r'<article class="dish reveal" data-cat="(\w+)">.*?</article>', grid_block, re.S)
cats = {}
for m in re.finditer(r'<article class="dish reveal" data-cat="(\w+)">(.*?)</article>', grid_block, re.S):
    cats.setdefault(m.group(1), []).append(m.group(0))
print("categories:", {k: len(v) for k, v in cats.items()})

# ---------- دادهٔ کنار سفره ----------
KENAR = [
    ("نان سنگک تنوری", "از تنورِ حیاط، داغ و معطر؛ با سبزیِ تازه و پنیر لیقوان.", "۴۵۰۰۰"),
    ("سالاد شیرازی", "خیار و گوجهٔ خردشده با آبغوره و نعنا؛ همسفرهٔ خنکِ کباب‌ها.", "۹۵۰۰۰"),
    ("ماست و موسیر", "ماستِ چکیدهٔ محلی با موسیرِ کوهستان؛ ترشِ ملایم و خوش‌عطر.", "۱۱۰۰۰۰"),
    ("زیتون پرورده", "زیتونِ شمال با ربِ انار، گلپر و سیر؛ مهرِ گیلان بر سفره.", "۱۳۵٬۰۰۰"),
    ("دوغ محلی با نعنا", "دوغِ زده‌شده با نعنا و پونه؛ خنک در کاسهٔ مسی.", "۷۰٬۰۰۰"),
    ("ترشیِ فصلِ خانه", "ترشیِ دست‌سازِ پاییز؛ از هویج و گل‌کلم تا سیر و بادمجان.", "۱۲۰٬۰۰"),
    ("آش رشته‌ی پنجشنبه‌ها", "آشِ جاافتاده با رشتهٔ دستی، نعناداغ و کشکِ دودی؛ هر پنجشنبه.", "۲۹۰٬۰۰۰"),
    ("حلوااردشیر یزد", "وردهٔ نرمِ اردشیر با پسته و بادام؛ شیرینیِ خاطرهِ یزد.", "۸۵٬۰۰۰"),
]
FRAME = ('<img class="frame" src="assets/img/window-frame-650.webp"\n'
         '             srcset="assets/img/window-frame-420.webp 420w, assets/img/window-frame-650.webp 650w"\n'
         '             sizes="(max-width: 700px) 80vw, 300px" alt="" aria-hidden="true" decoding="async">')
kenar_cards = []
for name, desc, price in KENAR:
    kenar_cards.append(
        f'''    <article class="dish reveal kenar" data-cat="kenar">
      <div class="dish-media">
        <div class="window"><div class="glass">
          <b class="g-name">{name}</b>
        </div>
        {FRAME}
        </div>
      </div>
      <div class="dish-body">
        <header><h3>{name}</h3><span class="dots" aria-hidden="true"></span><b class="price">{price} <i>تومان</i></b></header>
        <p>{desc}</p>
      </div>
    </article>'''
    )
kenar_group = ('      <div class="mb-group">\n        <h4>کنارِ سفره: نان و ترشی و مخلفات</h4>\n        <ul role="list">\n'
               + "\n".join(f'          <li><b>{n}</b><span class="dots" aria-hidden="true"></span><i>{p}</i></li>' for n, d, p in KENAR)
               + "\n        </ul>\n      </div>\n")

# ---------- ساخت menu.html ----------
CATS_FA = [("kabab", "کباب‌ها", "کباب‌های زغالی خانه؛ از سلطانی تا شیشلیک."),
           ("khoresh", "خورش‌ها", "خورش‌های جاافتاده با سبزیِ معطر و ربِ انار."),
           ("polo", "پلوها و چلوها", "پلوهای دمی و زعفرانی با ته‌دیگِ طلایی."),
           ("sonnati", "سنتی و آش", "دیزی، کشک بادمجان و آش‌های خانگی."),
           ("kenar", "کنارِ سفره", "نان تنوری، ترشی، دوغ و مخلفاتِ سفره.")]

def fix_nav(block, prices_same_page=True):
    b = block
    for a in ["story", "menu", "spaces", "tea", "reserve"]:
        b = b.replace(f'href="#{a}"', f'href="index.html#{a}"')
    b = b.replace('href="#hero"', 'href="index.html"')
    b = b.replace('href="#"', 'href="index.html"')
    if not prices_same_page:
        b = b.replace('href="#prices"', 'href="menu.html#prices"')
    return b

m_header = fix_nav(header, prices_same_page=True)
m_footer = fix_nav(footer, prices_same_page=True)

views = []
for key, fa, sub in CATS_FA:
    cards = "\n".join(cats[key]) if key in cats else "\n".join(kenar_cards)
    views.append(f'''  <section class="view" id="view-{key}">
    <header class="wrap sec-head view-head">
      <p class="eyebrow">منوی ترنج</p>
      <h2>{fa}</h2>
      <p class="sec-sub">{sub} قیمت‌ها به تومان است.</p>
    </header>
    <div class="wrap menu-grid">
{cards}
    </div>
  </section>''')

book_inner = book_block.replace('class="wrap menu-book reveal" id="prices"', 'class="wrap menu-book"')
book_inner = book_inner.replace("    </div>\n  </div>", "    </div>\n" + kenar_group + "  </div>", 1) if False else book_inner
# افزودن گروه کنار سفره به انتهای mb-grid
mb_end = book_inner.rindex("</div>\n  </div>")
book_inner = book_inner[:mb_end] + kenar_group + book_inner[mb_end:]

views.append(f'''  <section class="view" id="view-prices">
    <header class="wrap sec-head view-head">
      <p class="eyebrow">منوی ترنج</p>
      <h2>دفترچه‌ی کاملِ قیمت‌ها</h2>
      <p class="sec-sub">همهٔ گروه‌های سفره‌ی خانه، به‌همراه کنارِ سفره؛ قیمت‌ها به تومان.</p>
    </header>
{book_inner}  </section>''')

tabs_html = '    <div class="wrap menu-tabs m-tabs" role="group" aria-label="دسته‌های منو">\n' + "\n".join(
    f'      <button class="tab" type="button" data-view="{k}" aria-pressed="false">{fa}</button>' for k, fa, _ in CATS_FA) + \
    '\n      <button class="tab" type="button" data-view="prices" aria-pressed="false">لیست قیمت کامل</button>\n    </div>'

m_head = head.replace("<title>ترنج | رستوران و چای‌خانه‌ی سنتی ایرانی</title>",
                      "<title>منوی غذا و قیمت‌ها | ترنج</title>")
m_head = m_head.replace('css/style.css?v=7', 'css/style.css?v=8')

menu_html = f'''<!DOCTYPE html>
<html lang="fa" dir="rtl">
{m_head}
<body class="is-night">
{m_header}

<main id="main">
  <div class="back-bar">
    <div class="wrap">
      <a class="back-btn" href="index.html#menu">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>
        بازگشت به منوی اصلی
      </a>
    </div>
  </div>
  <div class="m-tabs-wrap">
{tabs_html}
  </div>

  <section class="menu menu-page">
{chr(10).join(views)}
  </section>
</main>

{m_footer}
{totop}
<script src="js/main.js?v=6"></script>
<script src="js/menu.js?v=1"></script>
</body>
</html>
'''
io.open(ROOT + "menu.html", "w", encoding="utf-8").write(menu_html)
print("menu.html written:", len(menu_html), "bytes")

# ---------- پیرایش index.html ----------
# 1) کاشی‌ها به پیوند تبدیل شوند + کاشی کنار سفره + جعبهٔ قیمت
new_tiles = tiles_block
new_tiles = new_tiles.replace('<button class="cat-tile reveal" type="button" data-cat="kabab">',
                              '<a class="cat-tile reveal" href="menu.html#kabab">')
new_tiles = new_tiles.replace('<button class="cat-tile reveal" type="button" data-cat="khoresh">',
                              '<a class="cat-tile reveal" href="menu.html#khoresh">')
new_tiles = new_tiles.replace('<button class="cat-tile reveal" type="button" data-cat="polo">',
                              '<a class="cat-tile reveal" href="menu.html#polo">')
new_tiles = new_tiles.replace('<button class="cat-tile reveal" type="button" data-cat="sonnati">',
                              '<a class="cat-tile reveal" href="menu.html#sonnati">')
new_tiles = new_tiles.replace("</button>", "</a>")
extra = '''    <a class="cat-tile plain reveal" href="menu.html#kenar">
      <span class="plain-art" aria-hidden="true"></span>
      <span class="cat-txt"><b>کنارِ سفره</b><i>۸ قلم · نان و ترشی و دوغ</i><em>دیدن جزئیات و قیمت</em></span>
    </a>
    <a class="price-box reveal" href="menu.html#prices">
      <span class="pb-ic" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20V3H6.5A2.5 2.5 0 0 0 4 5.5v14Z"/><path d="M4 19.5A2.5 2.5 0 0 0 6.5 22H20v-5"/><path d="M9 7h7M9 11h7"/></svg></span>
      <b>دفترچه‌ی کاملِ قیمت‌ها</b>
      <span>همهٔ گروه‌های منو و کنارِ سفره، با قیمتِ به‌روز در یک صفحه.</span>
      <em class="pb-go">مشاهدهٔ لیست قیمت</em>
    </a>
'''
last_close = new_tiles.rindex("</div>")
new_tiles = new_tiles[:last_close] + extra + new_tiles[last_close:]

idx = idx[:tiles_s] + new_tiles + idx[tabs_s:]
# 2) حذف تب‌ها، گرید، دفترچه و بلوک کنار سفرهٔ قدیمی
idx = idx.replace(tabs_block, "", 1)
idx = idx.replace(grid_block, "", 1)
idx = idx.replace(book_block, "", 1)
idx = idx.replace(more_block, "", 1)
# 3) ناوبری و متن‌ها
idx = idx.replace('<a href="#prices">لیست قیمت</a>', '<a href="menu.html#prices">لیست قیمت</a>', 1)
idx = re.sub(r'(<section class="menu" id="menu" data-view="cats">.*?<p class="sec-sub">).*?(</p>)',
             r'\1قاب‌ها را لمس کنید: هر دسته صفحهٔ غذاهای خود را با جزئیات و قیمت باز می‌کند؛ دفترچه‌ی قیمت هم یک صفحهٔ جداست.\2',
             idx, count=1, flags=re.S)
idx = idx.replace('css/style.css?v=7', 'css/style.css?v=8')
idx = idx.replace('js/main.js?v=5', 'js/main.js?v=6')
io.open(ROOT + "index.html", "w", encoding="utf-8").write(idx)
print("index.html patched")

# ---------- main.js: حذف پالایش منو + گارد ----------
js = io.open(ROOT + "js/main.js", encoding="utf-8").read()
s = js.index("  /* --- پالایش منو --- */")
e = js.index("/* --- دکمه‌ی روز/شب")
js = js[:s] + js[e:]
old_dn = '''  dn.addEventListener("click", () => setNight(!hero.classList.contains("is-night")));
  hero.classList.toggle("is-night", document.body.classList.contains("is-night"));
  syncDn();'''
new_dn = '''  if (dn && hero) {
    dn.addEventListener("click", () => setNight(!hero.classList.contains("is-night")));
    hero.classList.toggle("is-night", document.body.classList.contains("is-night"));
    syncDn();
  }'''
assert js.count(old_dn) == 1
js = js.replace(old_dn, new_dn, 1)
fs = js.index('  const form = $("#resForm");')
fs_nl = js.index("\n", fs) + 1
fe = js.index("  });", js.index("form.reset();")) + len("  });")
js = js[:fs_nl] + "  if (form) {\n" + js[fs_nl:fe] + "\n  }" + js[fe:]
io.open(ROOT + "js/main.js", "w", encoding="utf-8").write(js)
print("main.js patched")

# ---------- menu.js ----------
menu_js = '''/* برگهٔ منو: مسیریابی با هش و جابه‌جایی دسته‌ها بدون بارگذاری دوباره */
(function () {
  const $ = (s) => document.querySelector(s);
  const $$ = (s) => [...document.querySelectorAll(s)];
  const tabs = $$(".m-tabs .tab");
  const views = $$(".view");
  const key = () => (location.hash || "#kabab").slice(1);
  const show = (k) => {
    if (!$("#view-" + k)) k = "kabab";
    views.forEach((v) => v.classList.toggle("is-on", v.id === "view-" + k));
    tabs.forEach((t) => {
      const on = t.dataset.view === k;
      t.classList.toggle("is-on", on);
      t.setAttribute("aria-pressed", String(on));
    });
  };
  tabs.forEach((t) => t.addEventListener("click", () => { location.hash = t.dataset.view; }));
  addEventListener("hashchange", () => { show(key()); scrollTo({ top: 0, behavior: "auto" }); });
  show(key());
})();
'''
io.open(ROOT + "js/menu.js", "w", encoding="utf-8").write(menu_js)
print("menu.js written")
