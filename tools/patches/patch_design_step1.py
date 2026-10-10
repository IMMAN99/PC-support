#!/usr/bin/env python3
"""
DESIGN-STEP1 — گام ۱ جلای طراحی (تأییدشده توسط کارفرما ۲۰۲۶-۱۰-۰۷)

بر پایهٔ سند docs/بازبینی_طراحی_سه_نمونه.md:
  D-01  پرتو محیطی هیرو — دو گرادیان نرم آبی/بنفش، بدون فیلتر سنگین، صفر درخواست بیرونی
  D-02  ورود نرم اسکرولی — fade + بالا آمدن ۱۲px، یک‌جهته، پله‌ای، یک‌بار اجرا
  D-03  بلندشدن ملایم کارت‌ها در هاور (فقط دسکتاپ با اشاره‌گر دقیق)
  D-05  درز گرادیانی روی باندهای خاکستری (نرم‌کردن پرش رنگ، خصوصاً تم تیره)

قواعد رعایت‌شده:
  • هیچ تغییر چیدمان/متن/قیمت/قاعدهٔ کسب‌وکار — فقط لایهٔ تزئینی
  • صفر منبع بیرونی (همه‌چیز CSS/SVG/JS درون‌خطی)
  • احترام کامل به prefers-reduced-motion؛ اگر JS نباشد هیچ محتوایی پنهان نمی‌شود
  • هیچ کلاس Tailwind تازه‌ای اضافه نمی‌شود (نیاز به بازسازی CSS منجمد نیست)

اجرا:  python3 tools/patches/patch_design_step1.py     (یک‌بار — نشانگر محافظت می‌کند)
"""
import io, sys

P = '/home/user/پشتیبان_رایانه.html'
MARK = 'DESIGN-STEP1'
s = io.open(P, encoding='utf-8').read()
if MARK in s:
    sys.exit('این پچ قبلاً اجرا شده است — دوباره اجرا نمی‌شود.')

done = []

# ------------------------------------------------------------------ helpers
def rep(old, new, label, count=1):
    global s
    n = s.count(old)
    assert n == count, f'✗ {label}: {n} مورد پیدا شد (انتظار {count})\n{old[:160]}'
    s = s.replace(old, new, count)
    done.append(label)


def tag_header(section_id, label):
    """کلاس rise را به بلوک عنوان همان سکشن (والد h2) اضافه می‌کند."""
    global s
    i = s.index(f'<section id="{section_id}"')
    h2 = s.index('<h2', i)
    d = s.rindex('<div class="text-center', i, h2)
    q = s.index('class="', d)
    e = s.index('"', q + 7)
    s = s[:e] + ' rise' + s[e:]
    done.append(label)


def tag_in_section(section_id, prefix, extra, label):
    """extra را داخل کلاسِ عنصری که با prefix شروع می‌شود (داخل همان سکشن) اضافه می‌کند."""
    global s
    i = s.index(f'<section id="{section_id}"')
    j = s.index('</section>', i)
    seg = s[i:j]
    n = seg.count(prefix)
    assert n == 1, f'✗ {label}: {n} بار در سکشن {section_id} پیدا شد'
    seg = seg.replace(prefix, prefix + ' ' + extra, 1)
    s = s[:i] + seg + s[j:]
    done.append(label)


def add_class_to_id(eid, extra, label):
    """extra را انتهای صفت class عنصری با شناسهٔ eid اضافه می‌کند."""
    global s
    i = s.index(f'id="{eid}"')
    q = s.index('class="', i)
    e = s.index('"', q + 7)
    s = s[:e] + ' ' + extra + s[e:]
    done.append(label)

# ------------------------------------------------------------------ ۱) CSS (D-01 · D-05 · D-03 · D-02)
CSS = """
    /* ===== DESIGN-STEP1 — لایهٔ جلای نهایی (گام ۱) =====
       D-01 پرتو محیطی هیرو · D-02 ورود نرم اسکرولی · D-03 بلندشدن کارت · D-05 درز گرادیانی
       همه درون‌خطی (صفر درخواست بیرونی)، سبک، و با احترام به prefers-reduced-motion. */

    /* D-01 — پرتو محیطی: گرادیانِ نرم، بدون filter: blur و بدون انیمیشن دائمی */
    #overview { position: relative; z-index: 0; }
    #overview::before,
    #overview::after { content: ""; position: absolute; z-index: -1; border-radius: 50%; pointer-events: none; }
    #overview::before { top: -22%; right: -12%; width: min(780px, 66vw); aspect-ratio: 1 / 1;
      background: radial-gradient(circle, rgba(0,113,227,.10) 0%, rgba(0,113,227,.04) 44%, rgba(0,113,227,0) 72%); }
    #overview::after { top: -8%; left: -14%; width: min(640px, 58vw); aspect-ratio: 1 / 1;
      background: radial-gradient(circle, rgba(168,85,247,.09) 0%, rgba(168,85,247,.035) 46%, rgba(168,85,247,0) 74%); }
    .dark #overview::before { background: radial-gradient(circle, rgba(0,113,227,.22) 0%, rgba(0,113,227,.09) 46%, rgba(0,113,227,0) 74%); }
    .dark #overview::after { background: radial-gradient(circle, rgba(168,85,247,.18) 0%, rgba(168,85,247,.075) 48%, rgba(168,85,247,0) 76%); }

    /* D-05 — درز گرادیانی روی باندهای خاکستری: مرزها نرم می‌شوند (بیشترین اثر در تم تیره) */
    section[class*="bg-brand-lightGray"] { position: relative; }
    section[class*="bg-brand-lightGray"]::before,
    section[class*="bg-brand-lightGray"]::after { content: ""; position: absolute; left: 0; right: 0; height: 40px; pointer-events: none; }
    section[class*="bg-brand-lightGray"]::before { top: 0; background: linear-gradient(to bottom, #fbfbfd 0%, rgba(251,251,253,0) 100%); }
    #ai-diagnostic::after, #bottleneck::after { bottom: 0; background: linear-gradient(to top, #fbfbfd 0%, rgba(251,251,253,0) 100%); }
    .dark section[class*="bg-brand-lightGray"]::before { background: linear-gradient(to bottom, #000 0%, rgba(0,0,0,0) 100%); }
    .dark #ai-diagnostic::after, .dark #bottleneck::after { background: linear-gradient(to top, #000 0%, rgba(0,0,0,0) 100%); }

    /* D-03 — بلندشدن ملایم کارت‌ها؛ فقط دستگاه‌های اشاره‌گر دقیق و بدون کاهش حرکت */
    @media (hover: hover) and (pointer: fine) and (prefers-reduced-motion: no-preference) {
      section [class*="rounded-[28px]"] { transition: transform .22s cubic-bezier(.16,1,.3,1), box-shadow .22s cubic-bezier(.16,1,.3,1); }
      section [class*="rounded-[28px]"]:hover { transform: translateY(-4px); box-shadow: 0 18px 40px -16px rgba(0,0,0,.22); }
      .dark section [class*="rounded-[28px]"]:hover { box-shadow: 0 20px 44px -18px rgba(0,0,0,.8); }
    }

    /* D-02 — ورود نرم اسکرولی: پنهان‌سازی فقط وقتی JS فعال است و حرکت مجاز است */
    @media (prefers-reduced-motion: no-preference) {
      html.js .rise { opacity: 0; transform: translateY(12px); }
      html.js .rise.in { opacity: 1; transform: none;
        transition: opacity .6s cubic-bezier(.16,1,.3,1), transform .6s cubic-bezier(.16,1,.3,1); }
      html.js .rise.in[data-rise="1"] { transition-delay: .07s; }
      html.js .rise.in[data-rise="2"] { transition-delay: .14s; }
      html.js .rise.in[data-rise="3"] { transition-delay: .21s; }
      html.js .rise.in[data-rise="4"] { transition-delay: .28s; }

      html.js .rise-stagger > * { opacity: 0; transform: translateY(12px); }
      html.js .rise-stagger.in > * { opacity: 1; transform: none;
        transition: opacity .55s cubic-bezier(.16,1,.3,1), transform .55s cubic-bezier(.16,1,.3,1); }
      html.js .rise-stagger.in > *:nth-child(1) { transition-delay: .05s; }
      html.js .rise-stagger.in > *:nth-child(2) { transition-delay: .12s; }
      html.js .rise-stagger.in > *:nth-child(3) { transition-delay: .19s; }
      html.js .rise-stagger.in > *:nth-child(4) { transition-delay: .26s; }
      html.js .rise-stagger.in > *:nth-child(5) { transition-delay: .33s; }
      html.js .rise-stagger.in > *:nth-child(6) { transition-delay: .40s; }
      html.js .rise-stagger.in > *:nth-child(n+7) { transition-delay: .45s; }
    }
"""
rep('\n  </style>\n</head>', CSS + '\n  </style>\n</head>', 'CSS گام ۱ (پرتو · درز · لبه‌ها · ورود نرم)')

# ------------------------------------------------------------------ ۲) اسکریپت فعال‌سازی (قبل از رندر محتوا)
BODY_TAG = ('<body class="bg-brand-canvas dark:bg-brand-darkCanvas text-brand-dark dark:text-white '
            'transition-colors duration-300 selection:bg-brand-blue selection:text-white min-h-screen pt-12">')
SCRIPT_A = BODY_TAG + """
  <!-- DESIGN-STEP1 — ورود نرم اسکرولی: اگر حرکت مجاز نباشد یا IntersectionObserver نباشد،
       هیچ محتوایی پنهان نمی‌شود (محافظه‌کارانه‌ترین حالت = بدون جلوه). -->
  <script>
    (function () { try {
      var ok = ('IntersectionObserver' in window) &&
               !(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches);
      if (ok) document.documentElement.classList.add('js');
    } catch (e) {} })();
  </script>"""
rep(BODY_TAG, SCRIPT_A, 'اسکریپت فعال‌سازی (بدون پنهان‌سازی در حالت کاهش حرکت)')

# ------------------------------------------------------------------ ۳) ناظر IntersectionObserver (انتهای بدنه)
SCRIPT_B = """  <script>
    /* DESIGN-STEP1 — ناظر ورود نرم: هر عنصر یک‌بار و برای همیشه نمایان می‌شود. */
    (function () { try {
      var d = document.documentElement;
      if (!d.classList.contains('js')) return;
      var io = new IntersectionObserver(function (entries) {
        for (var i = 0; i < entries.length; i++) {
          if (entries[i].isIntersecting) { entries[i].target.classList.add('in'); io.unobserve(entries[i].target); }
        }
      }, { threshold: 0.12, rootMargin: '0px 0px -36px 0px' });
      var els = document.querySelectorAll('.rise, .rise-stagger');
      for (var j = 0; j < els.length; j++) io.observe(els[j]);
    } catch (e) { document.documentElement.classList.remove('js'); } })();
  </script>
</body>"""
rep('</body>', SCRIPT_B, 'ناظر IntersectionObserver')

# ------------------------------------------------------------------ ۴) تگ‌گذاری هیرو
rep('<div class="inline-flex items-center gap-2 mb-6 px-3.5 py-1.5 rounded-full bg-brand-lightGray dark:bg-brand-darkCard border border-black/[0.08] dark:border-white/[0.08] shadow-sm">',
    '<div class="rise inline-flex items-center gap-2 mb-6 px-3.5 py-1.5 rounded-full bg-brand-lightGray dark:bg-brand-darkCard border border-black/[0.08] dark:border-white/[0.08] shadow-sm">',
    'ریزال هیرو ۱/۶ — قرص بالای عنوان')

rep('<h1 class="hero-headline text-4xl sm:text-6xl md:text-7xl font-extrabold text-brand-dark dark:text-white max-w-4xl mx-auto md:leading-[1.45]">',
    '<h1 data-rise="1" class="hero-headline rise text-4xl sm:text-6xl md:text-7xl font-extrabold text-brand-dark dark:text-white max-w-4xl mx-auto md:leading-[1.45]">',
    'ریزال هیرو ۲/۶ — عنوان')

rep('<p class="mt-6 text-base sm:text-xl text-brand-gray max-w-2xl mx-auto font-normal leading-relaxed">',
    '<p data-rise="2" class="rise mt-6 text-base sm:text-xl text-brand-gray max-w-2xl mx-auto font-normal leading-relaxed">',
    'ریزال هیرو ۳/۶ — توضیح')

rep('<div class="mt-8 sm:mt-10 flex flex-wrap items-center justify-center gap-3">',
    '<div data-rise="3" class="rise mt-8 sm:mt-10 flex flex-wrap items-center justify-center gap-3">',
    'ریزال هیرو ۴/۶ — دکمه‌های اقدام')

rep('<div id="heroStatusStrip" class="mt-8 flex flex-wrap items-stretch justify-center gap-3">',
    '<div data-rise="4" id="heroStatusStrip" class="rise mt-8 flex flex-wrap items-stretch justify-center gap-3">',
    'ریزال هیرو ۵/۶ — نوار وضعیت')

rep('<div class="mt-16 sm:mt-20 grid grid-cols-1 md:grid-cols-3 gap-6 text-right">',
    '<div class="rise-stagger mt-16 sm:mt-20 grid grid-cols-1 md:grid-cols-3 gap-6 text-right">',
    'ریزال هیرو ۶/۶ — سه کارت بنتو (پله‌ای)')

# ------------------------------------------------------------------ ۵) عنوان سکشن‌ها
tag_header('ai-diagnostic',  'ریزال عنوان — عیب‌یاب هوشمند')
tag_header('remote-support', 'ریزال عنوان — پشتیبانی ریموت')
tag_header('speed-booster',  'ریزال عنوان — تست سرعت')
tag_header('bottleneck',     'ریزال عنوان — تحلیل گلوگاه')
tag_header('plans',          'ریزال عنوان — طرح‌های Care')
tag_header('faq',            'ریزال عنوان — پرسش‌های متداول')

# ------------------------------------------------------------------ ۶) کارت‌ها و گروه‌ها
add_class_to_id('aiTextDiagnosticCard', 'rise', 'ریزال کارت عیب‌یاب')

tag_in_section('remote-support', '<div class="grid grid-cols-1 lg:grid-cols-3 gap-6', 'rise-stagger',
               'ریزال گروه اصلی ریموت (پله‌ای)')
tag_in_section('remote-support', '<div class="lg:col-span-2 grid grid-cols-1 sm:grid-cols-3 gap-6 items-start', 'rise-stagger',
               'ریزال سه‌مرحلهٔ ریموت (پله‌ای)')
tag_in_section('remote-support', '<div class="mt-6 grid grid-cols-1 md:grid-cols-2 gap-6', 'rise-stagger',
               'ریزال دو کارت مرز ریموت/کارگاه (پله‌ای)')
tag_in_section('remote-support', '<div class="mt-6 bg-white dark:bg-brand-darkCard rounded-[28px] p-6 border border-black/[0.08] dark:border-white/[0.08] shadow-sm flex flex-col', 'rise',
               'ریزال نوار امنیت اتصال')

tag_in_section('speed-booster', '<div class="bg-white dark:bg-brand-darkCard rounded-[28px] p-6 sm:p-8 border border-black/[0.08] dark:border-white/[0.08] shadow-sm', 'rise',
               'ریزال کارت تست سرعت')
tag_in_section('bottleneck', '<div class="bg-white dark:bg-brand-darkCard rounded-[28px] p-6 sm:p-8 border border-black/[0.08] dark:border-white/[0.08] shadow-sm', 'rise',
               'ریزال کارت تحلیل گلوگاه')

tag_in_section('plans', '<div class="grid grid-cols-1 md:grid-cols-3 gap-6', 'rise-stagger',
               'ریزال سه طرح Care (پله‌ای)')
tag_in_section('faq', '<div class="space-y-4', 'rise-stagger',
               'ریزال فهرست پرسش‌ها (پله‌ای)')

rep('<div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-center mb-10">',
    '<div class="rise-stagger grid grid-cols-2 md:grid-cols-4 gap-4 text-center mb-10">',
    'ریزال نشان‌های اعتماد (پله‌ای)')

# ------------------------------------------------------------------ نوشتن + گزارش
io.open(P, 'w', encoding='utf-8').write(s)
print('\n'.join(f'  ✓ {d}' for d in done))
print(f'\nDone — {len(s)} chars written')
print(f"  · rise: {s.count('class=\"rise') + s.count(' rise ')} جای‌گذاری‌شده · rise-stagger: {s.count('rise-stagger') - 2} گروه")
print(f"  · کلیدواژه‌های CSS برای پوشش بیلد: .rise ✓ .rise-stagger ✓ .js ✓ .in ✓")
