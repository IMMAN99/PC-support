#!/usr/bin/env python3
"""
DESIGN-STEP2 — گام ۲ جلای طراحی (تأییدشده توسط کارفرما ۲۰۲۶-۱۰-۰۷)

بر پایهٔ docs/بازبینی_طراحی_سه_نمونه.md:
  D-04  هالهٔ گوشهٔ کارت — فقط دو نقطه: کارت عیب‌یاب (آبی، پایین‌راست) و کارت Care Pro (بنفش، بالا‌راست)
        پیاده‌سازی با background-image رادیال + بزرگ‌شدن نرم در هاور (بدون شبه‌عنصر، بدون گیر افتادن زیر متن)
  D-08  نوارهای سنجش سرعت — پر شدن از صفر در اولین دیدن سکشن (scaleX)، تعامل بعدی دست‌نخورده (پهنای نوار)
  D-09  تثبیت قاعدهٔ نقطهٔ وضعیت — سبزِ پالس‌دار = آنلاین · کهرباییِ ثابت = در صف/بسته.
        یک شکاف واقعی بسته شد: نقطهٔ منوی موبایل همیشه سبزِ پالس‌دار بود و به وضعیت حضور گره نخورده بود.
  D-10  زبان واحد دکمه‌های اصلی: هاور = بزرگ‌نمایی ۱٫۰۲ · فشردن = ۰٫۹۸ (بدون تغییر مارک‌آپ — با سلکتور CSS)

قواعد: صفر منبع بیرونی · احترام کامل به prefers-reduced-motion · بدون تغییر چیدمان/متن/قیمت/قواعد کسب‌وکار
اجرا:  python3 tools/patches/patch_design_step2.py     (یک‌بار — نشانگر محافظت می‌کند)
"""
import io, sys

P = '/home/user/پشتیبان_رایانه.html'
MARK = 'DESIGN-STEP2'
s = io.open(P, encoding='utf-8').read()
if MARK in s:
    sys.exit('این پچ قبلاً اجرا شده است — دوباره اجرا نمی‌شود.')
assert 'DESIGN-STEP1' in s, 'گام ۱ باید اول اجرا شده باشد.'

done = []

def rep_in_section(section_id, old, new, label, count=1):
    """جای‌گذاری محدود به یک سکشن — برای رشته‌هایی که در چند سکشن تکرار می‌شوند."""
    global s
    i = s.index(f'<section id="{section_id}"')
    j = s.index('</section>', i)
    seg = s[i:j]
    n = seg.count(old)
    assert n == count, f'✗ {label}: {n} مورد در سکشن {section_id} (انتظار {count})'
    seg = seg.replace(old, new, count)
    s = s[:i] + seg + s[j:]
    done.append(label)




def rep(old, new, label, count=1):
    global s
    n = s.count(old)
    assert n == count, f'✗ {label}: {n} مورد پیدا شد (انتظار {count})\n{old[:160]}'
    s = s.replace(old, new, count)
    done.append(label)

# ------------------------------------------------------------------ ۱) CSS — D-04 · D-08 · D-10
CSS = """
    /* ===== DESIGN-STEP2 — گام ۲ جلای نهایی =====
       D-04 هالهٔ گوشهٔ کارت · D-08 پر شدن نوارهای سنجش · D-10 زبان واحد دکمه‌ها */

    /* D-04 — هالهٔ گوشه: یک لایهٔ گرادیانِ نرم روی بدنهٔ کارت (زیر محتوا، چون background است نه شبه‌عنصر).
       نقطهٔ هاله: پایین‌راست آبی برای عیب‌یاب، بالا‌راست بنفش برای Care Pro. */
    .halo-corner { background-repeat: no-repeat; background-size: 112% 112%; }
    .halo-br { background-image: radial-gradient(620px circle at 100% 100%, rgba(0,113,227,.085), rgba(0,113,227,0) 62%); background-position: 100% 100%; }
    .halo-tr { background-image: radial-gradient(620px circle at 100% 0%, rgba(168,85,247,.095), rgba(168,85,247,0) 62%); background-position: 100% 0%; }
    .dark .halo-br { background-image: radial-gradient(620px circle at 100% 100%, rgba(0,113,227,.17), rgba(0,113,227,0) 64%); }
    .dark .halo-tr { background-image: radial-gradient(620px circle at 100% 0%, rgba(168,85,247,.16), rgba(168,85,247,0) 64%); }

    /* D-08 — نوارهای سنجش: پر شدن از سمت شروع (راست) در اولین ورود کارت.
       پهنای نوار و تعامل بعدی (تغییر HDD/SATA/NVMe) دست‌نخورده می‌ماند. */
    @media (prefers-reduced-motion: no-preference) {
      html.js .bench-card .bench-bar { transform: scaleX(0); transform-origin: 100% 50%;
        transition: transform .7s cubic-bezier(.16,1,.3,1) .12s, width .5s ease-out; }
      html.js .bench-card.in .bench-bar { transform: scaleX(1); }
    }

    /* D-10 — زبان واحد دکمه‌های اصلی: هاور ۱٫۰۲ · فشردن ۰٫۹۸.
       با سلکتور ویژگی پیاده می‌شود تا دکمه‌های ساخته‌شده در جاوااسکریپت هم خودکار پوشش بگیرند.
       (لانچر شناور و دکمه‌های رزرو استثنا هستند — رفتار خودشان را دارند.) */
    @media (hover: hover) and (pointer: fine) and (prefers-reduced-motion: no-preference) {
      :is(a, button):is([class^="bg-brand-blue"], [class*=" bg-brand-blue"],
                        [class^="bg-gradient-to-r"], [class*=" bg-gradient-to-r"])
                     :is([class^="text-white"], [class*=" text-white"])
                     :not(#aiFloatingLauncherBtn):not([class*="book-submit-btn"]) {
        transition: transform .18s cubic-bezier(.16,1,.3,1), box-shadow .18s cubic-bezier(.16,1,.3,1),
                    background-color .2s ease, color .2s ease, border-color .2s ease, opacity .2s ease;
      }
      :is(a, button):is([class^="bg-brand-blue"], [class*=" bg-brand-blue"],
                        [class^="bg-gradient-to-r"], [class*=" bg-gradient-to-r"])
                     :is([class^="text-white"], [class*=" text-white"])
                     :not(#aiFloatingLauncherBtn):not([class*="book-submit-btn"]):hover { transform: scale(1.02); }
      :is(a, button):is([class^="bg-brand-blue"], [class*=" bg-brand-blue"],
                        [class^="bg-gradient-to-r"], [class*=" bg-gradient-to-r"])
                     :is([class^="text-white"], [class*=" text-white"])
                     :not(#aiFloatingLauncherBtn):not([class*="book-submit-btn"]):active { transform: scale(.98); }
    }

    /* هاله در هاور کمی بازتر می‌شود؛ انتقالِ ترکیبی تا با لبهٔ D-03 تعارض نکند */
    @media (hover: hover) and (pointer: fine) and (prefers-reduced-motion: no-preference) {
      section .halo-corner { transition: translate .22s cubic-bezier(.16,1,.3,1),
                             box-shadow .22s cubic-bezier(.16,1,.3,1),
                             background-size .35s cubic-bezier(.16,1,.3,1); }
      section .halo-corner:hover { background-size: 142% 142%; }
    }
"""
rep('\n  </style>\n</head>', CSS + '\n  </style>\n</head>', 'CSS گام ۲ (هاله · نوارها · دکمه‌ها)')

# ------------------------------------------------------------------ ۲) مارک‌آپ — D-04
rep('<div id="aiTextDiagnosticCard" class="bg-white dark:bg-brand-darkCard rounded-[28px] p-6 sm:p-8 border border-black/[0.08] dark:border-white/[0.08] shadow-sm mb-6 rise"',
    '<div id="aiTextDiagnosticCard" class="bg-white dark:bg-brand-darkCard rounded-[28px] p-6 sm:p-8 border border-black/[0.08] dark:border-white/[0.08] shadow-sm mb-6 rise halo-corner halo-br"',
    'هالهٔ کارت عیب‌یاب (آبی، پایین‌راست)')

rep('<div class="bg-white dark:bg-brand-darkCard rounded-[28px] p-6 sm:p-8 border-2 border-brand-blue shadow-lg relative flex flex-col justify-between">',
    '<div class="bg-white dark:bg-brand-darkCard rounded-[28px] p-6 sm:p-8 border-2 border-brand-blue shadow-lg relative flex flex-col justify-between halo-corner halo-tr">',
    'هالهٔ کارت Care Pro (بنفش، بالا‌راست)')

# ------------------------------------------------------------------ ۳) مارک‌آپ — D-08
rep_in_section('speed-booster',
    '<div class="bg-white dark:bg-brand-darkCard rounded-[28px] p-6 sm:p-8 border border-black/[0.08] dark:border-white/[0.08] shadow-sm rise">',
    '<div class="bg-white dark:bg-brand-darkCard rounded-[28px] p-6 sm:p-8 border border-black/[0.08] dark:border-white/[0.08] shadow-sm rise bench-card">',
    'کارت تست سرعت ← bench-card')

rep('<div id="benchBootBar" class="h-full bg-emerald-500 rounded-full transition-all duration-500" style="width: 92%">',
    '<div id="benchBootBar" class="h-full bg-emerald-500 rounded-full transition-all duration-500 bench-bar" style="width: 92%">',
    'نوار بوت ← bench-bar')
rep('<div id="benchAppBar" class="h-full bg-brand-blue rounded-full transition-all duration-500" style="width: 90%">',
    '<div id="benchAppBar" class="h-full bg-brand-blue rounded-full transition-all duration-500 bench-bar" style="width: 90%">',
    'نوار اجرای برنامه ← bench-bar')
rep('<div id="benchReadBar" class="h-full bg-purple-500 rounded-full transition-all duration-500" style="width: 95%">',
    '<div id="benchReadBar" class="h-full bg-purple-500 rounded-full transition-all duration-500 bench-bar" style="width: 95%">',
    'نوار خواندن متوالی ← bench-bar')

# ------------------------------------------------------------------ ۴) D-09 — نقطهٔ منوی موبایل به حضور گره می‌خورد
rep('<span class="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span><span id="drawerPresenceLine">',
    '<span id="drawerPresenceDot" class="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span><span id="drawerPresenceLine">',
    'شناسه برای نقطهٔ حضور منوی موبایل')

rep("""      const drawerCount = document.getElementById('drawerPresenceCount');
      if (drawerCount) drawerCount.textContent = online ? `${faNum(n)} کارشناس آنلاین` : 'ثبت درخواست و تماس بعدی';""",
    """      const drawerCount = document.getElementById('drawerPresenceCount');
      if (drawerCount) drawerCount.textContent = online ? `${faNum(n)} کارشناس آنلاین` : 'ثبت درخواست و تماس بعدی';

      /* D-09: نقطهٔ ردیف «پشتیبانی ریموت» در منوی موبایل هم مثل پیل هدر و پنل ریموت
         به وضعیت واقعی حضور گره می‌خورد — سبزِ پالس‌دار = آنلاین، کهرباییِ ثابت = در صف. */
      const drawerDot = document.getElementById('drawerPresenceDot');
      if (drawerDot) drawerDot.className = online
        ? 'w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse'
        : 'w-1.5 h-1.5 rounded-full bg-amber-500';""",
    'نقطهٔ منوی موبایل ← وضعیت حضور واقعی')

# ------------------------------------------------------------------ نشانگر
rep('       D-04 هالهٔ گوشهٔ کارت · D-08 پر شدن نوارهای سنجش · D-10 زبان واحد دکمه‌ها */',
    '       D-04 هالهٔ گوشهٔ کارت · D-08 پر شدن نوارهای سنجش · D-10 زبان واحد دکمه‌ها · DESIGN-STEP2 */',
    'نشانگر پچ (سرصفحهٔ CSS)')

io.open(P, 'w', encoding='utf-8').write(s)
print('\n'.join(f'  ✓ {d}' for d in done))
print(f'\nDone — {len(s)} chars written')
print(f"  · هاله: {s.count('halo-corner')} جای‌گذاری · نوارها: {s.count('bench-bar')} · کارت: {s.count('bench-card')}")
