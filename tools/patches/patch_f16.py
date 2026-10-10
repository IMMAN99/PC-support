#!/usr/bin/env python3
"""
ROUND-3-F16 — بستن یافتهٔ پولیش F-16:
  ۱) همهٔ ایموجی‌هایی که به‌عنوان «آیکون رابط» استفاده شده‌اند با آیکون‌های خطی SVG جایگزین می‌شوند
     (🌙 ☀️ 📸 📷 ⚙️ 💬 ✈️ 🟢 🏛️ 🛡️ 🔒 📅 ⚠️ ⏳) تا با بقیهٔ آیکون‌های سایت هم‌خانواده باشند و
     با رنگ متن/حالت شب هم‌رنگ شوند.
  ۲) شکستن خط واحد قیمت در کارت‌های طرح Care: whitespace-nowrap روی گروه «مبلغ + واحد».

اجرا:  python3 tools/patches/patch_f16.py      (یک‌بار — با نشانگر محافظت می‌شود)
"""
import io, sys

P = '/home/user/پشتیبان_رایانه.html'
MARK = 'ROUND-3-F16'
s = io.open(P, encoding='utf-8').read()
if MARK in s:
    sys.exit('این پچ قبلاً اجرا شده است — دوباره اجرا نمی‌شود.')

done = []
def rep(old, new, label, count=1):
    global s
    n = s.count(old)
    assert n == count, f'✗ {label}: {n} مورد پیدا شد (انتظار {count})\n{old[:140]}'
    s = s.replace(old, new, 1)
    done.append(label)

# ---------------------------------------------------------------- ۱) اسپرایت آیکون
def sym(name, body):
    return (f'<symbol id="ic-{name}" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            f'stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">{body}</symbol>')

SPRITE = """
  <!-- ROUND-3-F16: اسپرایت آیکون‌های خطی سایت — جایگزین ایموجی‌های سیستمی -->
  <svg width="0" height="0" aria-hidden="true" focusable="false" style="position:absolute">""" + "".join([
    sym('moon', '<path d="M20.6 14.4A8.6 8.6 0 0 1 9.6 3.4a8.6 8.6 0 1 0 11 11z"/>'),
    sym('sun', '<circle cx="12" cy="12" r="4"/><path d="M12 2.4v2.2M12 19.4v2.2M2.4 12h2.2M19.4 12h2.2M5 5l1.6 1.6M17.4 17.4 19 19M19 5l-1.6 1.6M6.6 17.4 5 19"/>'),
    sym('image', '<rect x="3" y="4.5" width="18" height="15" rx="3"/><circle cx="8.6" cy="10" r="1.6"/><path d="M3.6 17.6 9 12.4l4 3.8 2.9-2.4 4.5 3.8"/>'),
    sym('camera', '<path d="M4.2 8.6h2.5l1.4-2.1h7.8l1.4 2.1h2.5A1.7 1.7 0 0 1 21.5 10.3v7.5a1.7 1.7 0 0 1-1.7 1.7H4.2a1.7 1.7 0 0 1-1.7-1.7v-7.5A1.7 1.7 0 0 1 4.2 8.6z"/><circle cx="12" cy="13.7" r="3.2"/>'),
    sym('sliders', '<path d="M4 7h9M19 7h1M4 12h3M13 12h7M4 17h8M18 17h2"/><circle cx="16" cy="7" r="1.9"/><circle cx="10" cy="12" r="1.9"/><circle cx="15" cy="17" r="1.9"/>'),
    sym('message', '<path d="M20.6 11.6a8 8 0 0 1-8.3 8 8.7 8.7 0 0 1-3.7-.8L3.4 20.2l1.5-4.9a8 8 0 0 1-.9-3.7 8 8 0 0 1 8.3-8 8 8 0 0 1 8.3 8z"/>'),
    sym('alert', '<path d="M12 3.4 21.2 19.6H2.8z"/><path d="M12 9.4v4.2M12 16.7v.2"/>'),
    sym('building', '<path d="M3.6 20.4h16.8M5.4 20.4V9.4L12 4.2l6.6 5.2v11"/><path d="M9.6 20.4v-4.8h4.8v4.8"/>'),
    sym('shield', '<path d="M12 3.2 5.2 5.9v5.3c0 4.5 2.9 8.3 6.8 9.6 3.9-1.3 6.8-5.1 6.8-9.6V5.9z"/><path d="M9.3 12.1l2 2 3.5-3.8"/>'),
    sym('lock', '<rect x="5" y="10.4" width="14" height="10" rx="2.6"/><path d="M8.6 10.4V8a3.4 3.4 0 0 1 6.8 0v2.4M12 14.6v1.9"/>'),
    sym('send', '<path d="M21.4 2.6 2.9 9.7l5.8 2.4 2.4 5.8z"/><path d="M8.7 12.1 21.4 2.6"/>'),
    sym('chat', '<path d="M20.6 11.6a8 8 0 0 1-8.3 8 8.7 8.7 0 0 1-3.7-.8L3.4 20.2l1.5-4.9a8 8 0 0 1-.9-3.7 8 8 0 0 1 8.3-8 8 8 0 0 1 8.3 8z"/><path d="M9.6 8.5c.3 0 .5.2.6.5l.4.9c.1.3 0 .5-.1.7l-.4.4c-.1.2-.1.4 0 .6.3.5.8 1 1.4 1.3.2.1.4.1.6-.1l.4-.4c.2-.2.4-.2.6-.1l.9.4c.3.1.5.4.5.6 0 .7-.6 1.2-1.3 1.2-1.9 0-4.5-2.7-4.5-4.5 0-.7.5-1.2 1-1.2z"/>'),
    sym('calendar', '<rect x="3.6" y="5.2" width="16.8" height="15" rx="2.6"/><path d="M3.6 10.1h16.8M8.2 3.4v3.6M15.8 3.4v3.6"/>'),
    sym('clock', '<circle cx="12" cy="12" r="8.4"/><path d="M12 7.4v4.9l3.2 1.9"/>'),
]) + "</svg>\n"

anchor = '<body class="bg-brand-canvas dark:bg-brand-darkCanvas text-brand-dark dark:text-white transition-colors duration-300 selection:bg-brand-blue selection:text-white min-h-screen pt-12">'
assert s.count(anchor) == 1
rep(anchor, anchor + SPRITE, 'اسپرایت آیکون‌های خطی SVG')

def ic(name, cls='w-4 h-4', extra=''):
    return (f'<svg class="{cls} shrink-0{extra}" viewBox="0 0 24 24" aria-hidden="true" '
            f'focusable="false"><use href="#ic-{name}"/></svg>')

def ic_span(name, cls='w-4 h-4', span_cls='inline-flex shrink-0'):
    return f'<span class="{span_cls}">{ic(name, cls)}</span>'

# ---------------------------------------------------------------- تم شب/روز
rep('<span id="themeToggleIcon" class="text-xs">🌙</span>',
    f'<span id="themeToggleIcon" class="inline-flex" data-theme-icon="moon">{ic("moon")}</span>',
    'آیکون تم (هدر)')

rep('<span id="drawerThemeText">تغییر به تم تیره 🌙</span>',
    '<span id="drawerThemeText">تغییر به تم تیره</span>',
    'متن تم (منوی موبایل) بدون ایموجی')

rep('showToast(isDark ? "حالت تیره فعال شد 🌙" : "حالت روشن فعال شد ☀️");',
    'showToast(isDark ? "حالت تیره فعال شد." : "حالت روشن فعال شد.");',
    'پیام‌های تم بدون ایموجی')

rep("""      if (themeIcon) themeIcon.textContent = isDark ? "☀️" : "🌙";
      if (drawerThemeText) drawerThemeText.textContent = isDark ? "تغییر به تم روشن ☀️" : "تغییر به تم تیره 🌙";""",
"""      if (themeIcon) {
        themeIcon.innerHTML = poshIcon(isDark ? 'sun' : 'moon', 'w-4 h-4');
        themeIcon.setAttribute('data-theme-icon', isDark ? 'sun' : 'moon');
      }
      if (drawerThemeText) drawerThemeText.textContent = isDark ? "تغییر به تم روشن" : "تغییر به تم تیره";""",
    'به‌روزرسانی آیکون تم با SVG')

# ---------------------------------------------------------------- کمک‌تابع آیکون برای JS
rep("""    function creditFa(n) { return Number(n || 0).toLocaleString('fa-IR'); }""",
"""    /* ROUND-3-F16: آیکون خطی به‌صورت رشتهٔ HTML — برای متن‌هایی که جاوااسکریپت می‌سازد */
    function poshIcon(name, cls) {
      return `<svg class="${cls || 'w-4 h-4'} shrink-0" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><use href="#ic-${name}"/></svg>`;
    }

    function creditFa(n) { return Number(n || 0).toLocaleString('fa-IR'); }""",
    'کمک‌تابع poshIcon')

rep('        if (btnText) btnText.textContent = "تحلیل تصویر با هوش مصنوعی 📸";',
    """        if (btnText) btnText.innerHTML = poshIcon('camera', 'w-3.5 h-3.5') + 'تحلیل تصویر با هوش مصنوعی';""",
    'دکمهٔ تحلیل تصویر (بازگشت حالت)')

# ---------------------------------------------------------------- هوش مصنوعی / بارگذاری
rep('<span>📸 تحلیل تصویر ارور / BSOD</span>',
    '<span class="inline-flex items-center gap-1.5">' + ic('image', 'w-3.5 h-3.5') + 'تحلیل تصویر ارور / BSOD</span>',
    'تب تحلیل تصویر')

rep('<span>⚙️ نشانه‌های متداول پیش‌فرض</span>',
    '<span class="inline-flex items-center gap-1.5">' + ic('sliders', 'w-3.5 h-3.5') + 'نشانه‌های متداول پیش‌فرض</span>',
    'تب نشانه‌های متداول')

rep('<span id="aiVisionBtnText">تحلیل تصویر با هوش مصنوعی 📸</span>',
    '<span id="aiVisionBtnText" class="inline-flex items-center gap-1.5">' + ic('camera', 'w-3.5 h-3.5') + 'تحلیل تصویر با هوش مصنوعی</span>',
    'دکمهٔ تحلیل تصویر')

rep("""            <div class="w-12 h-12 rounded-2xl bg-purple-500/10 text-purple-500 flex items-center justify-center mx-auto text-xl">
              📷
            </div>""",
"""            <div class="w-12 h-12 rounded-2xl bg-purple-500/10 text-purple-500 flex items-center justify-center mx-auto">
              """ + ic('camera', 'w-6 h-6') + """
            </div>""",
    'کادر بارگذاری تصویر')

rep("""class="w-7 h-7 rounded-full bg-black/5 dark:bg-white/10 flex items-center justify-center text-xs hover:opacity-75 transition">
          ⚙️
        </button>""",
    """class="w-7 h-7 rounded-full bg-black/5 dark:bg-white/10 flex items-center justify-center hover:opacity-75 transition">
          """ + ic('sliders') + """
        </button>""",
    'دکمهٔ تنظیمات چت')

# ---------------------------------------------------------------- اعتماد و پیام‌رسان‌ها
rep('<span class="text-xl block mb-1">🏛️</span>',
    ic_span('building', 'w-6 h-6 mx-auto', 'block mb-1 text-brand-blue'), 'نشان اتحادیه')
rep('<span class="text-xl block mb-1">🛡️</span>',
    ic_span('shield', 'w-6 h-6 mx-auto', 'block mb-1 text-brand-blue'), 'نشان نظام صنفی')
rep('<span class="text-xl block mb-1">🔒</span>',
    ic_span('lock', 'w-6 h-6 mx-auto', 'block mb-1 text-brand-blue'), 'نشان محرمانگی')

rep('<span>💬</span>', ic('message', 'w-3.5 h-3.5'), 'آیکون پیام‌رسان (بله/ایتا)', count=2)
rep('<span>✈️</span>', ic('send', 'w-3.5 h-3.5'), 'آیکون تلگرام')
rep('<span>🟢</span>', ic('chat', 'w-3.5 h-3.5'), 'آیکون واتساپ')

# ---------------------------------------------------------------- تقویم و شیفت‌ها
rep('<span class="text-base">📅</span>',
    ic_span('calendar', 'w-4 h-4', 'inline-flex text-brand-blue'), 'آیکون تاریخ انتخابی')

rep("""<span class="text-base leading-none" style="font-family:  'Segoe UI Emoji', 'Noto Color Emoji', sans-serif;">☀️</span>""",
    ic_span('sun', 'w-4 h-4', 'inline-flex leading-none text-amber-500'), 'آیکون شیفت صبح')
rep("""<span class="text-base leading-none" style="font-family:  'Segoe UI Emoji', 'Noto Color Emoji', sans-serif;">🌙</span>""",
    ic_span('moon', 'w-4 h-4', 'inline-flex leading-none text-indigo-400'), 'آیکون شیفت بعدازظهر')

# ---------------------------------------------------------------- هشدار و انقضا
rep('                <span>⚠️</span>',
    '                ' + ic('alert'), 'آیکون هشدار تاییدیه')
rep('        <span class="text-xs">⏳</span>',
    ic_span('clock', 'w-4 h-4', 'inline-flex text-emerald-600 dark:text-emerald-400'), 'آیکون مهلت اعتبار')

# ---------------------------------------------------------------- ۲) الآن‌رپ قیمت طرح‌ها
rep("""<div class="mt-6 font-mono text-2xl font-black text-brand-dark dark:text-white">
            ۲۹۰,۰۰۰ <span class="text-xs font-normal text-brand-gray">تومان / ماهانه</span>""",
    """<div class="mt-6 font-mono text-2xl font-black text-brand-dark dark:text-white whitespace-nowrap">
            ۲۹۰,۰۰۰ <span class="text-xs font-normal text-brand-gray">تومان / ماهانه</span>""",
    'قیمت Care شخصی: بدون شکستن خط')
rep("""<div class="mt-6 font-mono text-2xl font-black text-brand-dark dark:text-white">
            ۵۹۰,۰۰۰ <span class="text-xs font-normal text-brand-gray">تومان / ماهانه</span>""",
    """<div class="mt-6 font-mono text-2xl font-black text-brand-dark dark:text-white whitespace-nowrap">
            ۵۹۰,۰۰۰ <span class="text-xs font-normal text-brand-gray">تومان / ماهانه</span>""",
    'قیمت Care Pro: بدون شکستن خط')
rep("""<div class="mt-6 font-mono text-2xl font-black text-brand-dark dark:text-white">
            قرارداد SLA <span class="text-xs font-normal text-brand-gray">ماهانه اختصاصی</span>""",
    """<div class="mt-6 font-mono text-2xl font-black text-brand-dark dark:text-white whitespace-nowrap">
            قرارداد SLA <span class="text-xs font-normal text-brand-gray">ماهانه اختصاصی</span>""",
    'برچسب Care Business: بدون شکستن خط')

# ---------------------------------------------------------------- نشانگر
rep('<svg width="0" height="0" aria-hidden="true" focusable="false" style="position:absolute">',
    '<svg width="0" height="0" aria-hidden="true" focusable="false" data-sprite="ROUND-3-F16" style="position:absolute">',
    'نشانگر پچ')

io.open(P, 'w', encoding='utf-8').write(s)
print('\n'.join(f'  ✓ {d}' for d in done))
print(f'\nDone — {len(s)} chars written · آیکون‌ها: {s.count("<use href=")}')
