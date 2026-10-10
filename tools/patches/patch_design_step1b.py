#!/usr/bin/env python3
"""
DESIGN-STEP1B — اصلاح تداخل transform در گام ۱ (یافتهٔ آزمون D-03)

مشکل: قاعدهٔ ورود نرم (D-02) روی فرزندان گروه‌ها `transform: none` می‌گذارد و
با ویژگیِ بالاتر، قاعدهٔ بلندشدن کارت (D-03) را که با `transform` کار می‌کرد خنثی می‌کند.

راه‌حل استاندارد و بدون !important: بلندشدن کارت با ویژگی مستقل `translate` انجام می‌شود
(دو ویژگی جدا، پس هیچ‌کدام دیگری را بازنویسی نمی‌کند)، و فهرست transition هر دو حالت
به‌روز می‌شود تا حرکت نرم بماند. تأخیرِ پله‌ای فقط به opacity/transform می‌خورد تا
هاورِ کاربر هرگز معطل نماند.

اجرا:  python3 tools/patches/patch_design_step1b.py     (یک‌بار — نشانگر محافظت می‌کند)
"""
import io, sys

P = '/home/user/پشتیبان_رایانه.html'
MARK = 'DESIGN-STEP1B'
s = io.open(P, encoding='utf-8').read()
if MARK in s:
    sys.exit('این پچ قبلاً اجرا شده است — دوباره اجرا نمی‌شود.')
assert 'DESIGN-STEP1' in s, 'پچ گام ۱ هنوز اجرا نشده است.'

done = []


def rep(old, new, label, count=1):
    global s
    n = s.count(old)
    assert n == count, f'✗ {label}: {n} مورد پیدا شد (انتظار {count})\n{old[:160]}'
    s = s.replace(old, new, count)
    done.append(label)


# ------------------------------------------------------------------ D-03: transform → translate
rep('''    /* D-03 — بلندشدن ملایم کارت‌ها؛ فقط دستگاه‌های اشاره‌گر دقیق و بدون کاهش حرکت */
    @media (hover: hover) and (pointer: fine) and (prefers-reduced-motion: no-preference) {
      section [class*="rounded-[28px]"] { transition: transform .22s cubic-bezier(.16,1,.3,1), box-shadow .22s cubic-bezier(.16,1,.3,1); }
      section [class*="rounded-[28px]"]:hover { transform: translateY(-4px); box-shadow: 0 18px 40px -16px rgba(0,0,0,.22); }
      .dark section [class*="rounded-[28px]"]:hover { box-shadow: 0 20px 44px -18px rgba(0,0,0,.8); }
    }''',
'''    /* D-03 — بلندشدن ملایم کارت‌ها؛ فقط دستگاه‌های اشاره‌گر دقیق و بدون کاهش حرکت.
       از ویژگی مستقل «translate» استفاده می‌شود تا با transformِ ورود نرم (D-02) تداخل نکند. */
    @media (hover: hover) and (pointer: fine) and (prefers-reduced-motion: no-preference) {
      section [class*="rounded-[28px]"] { transition: translate .22s cubic-bezier(.16,1,.3,1), box-shadow .22s cubic-bezier(.16,1,.3,1); }
      section [class*="rounded-[28px]"]:hover { translate: 0 -4px; box-shadow: 0 18px 40px -16px rgba(0,0,0,.22); }
      .dark section [class*="rounded-[28px]"]:hover { box-shadow: 0 20px 44px -18px rgba(0,0,0,.8); }
    }''',
    'D-03 با ویژگی translate (بدون تداخل با ورود نرم)')

# ------------------------------------------------------------------ انتقال‌ها: افزودن translate/box-shadow
rep('''      html.js .rise.in { opacity: 1; transform: none;
        transition: opacity .6s cubic-bezier(.16,1,.3,1), transform .6s cubic-bezier(.16,1,.3,1); }''',
'''      html.js .rise.in { opacity: 1; transform: none;
        transition: opacity .6s cubic-bezier(.16,1,.3,1), transform .6s cubic-bezier(.16,1,.3,1),
                    translate .22s cubic-bezier(.16,1,.3,1), box-shadow .22s cubic-bezier(.16,1,.3,1); }''',
    'انتقال translate/box-shadow برای عناصر rise')

rep('''      html.js .rise-stagger.in > * { opacity: 1; transform: none;
        transition: opacity .55s cubic-bezier(.16,1,.3,1), transform .55s cubic-bezier(.16,1,.3,1); }''',
'''      html.js .rise-stagger.in > * { opacity: 1; transform: none;
        transition: opacity .55s cubic-bezier(.16,1,.3,1), transform .55s cubic-bezier(.16,1,.3,1),
                    translate .22s cubic-bezier(.16,1,.3,1), box-shadow .22s cubic-bezier(.16,1,.3,1); }''',
    'انتقال translate/box-shadow برای فرزندان گروه‌ها')

# ------------------------------------------------------------------ تأخیر فقط روی opacity/transform
for i, d in enumerate(('.07s', '.14s', '.21s', '.28s'), start=1):
    rep(f'      html.js .rise.in[data-rise="{i}"] {{ transition-delay: {d}; }}',
        f'      html.js .rise.in[data-rise="{i}"] {{ transition-delay: {d}, {d}, 0s, 0s; }}',
        f'تأخیر داده‌ریزال {i} فقط برای opacity/transform')

for i, d in enumerate(('.05s', '.12s', '.19s', '.26s', '.33s', '.40s'), start=1):
    rep(f'      html.js .rise-stagger.in > *:nth-child({i}) {{ transition-delay: {d}; }}',
        f'      html.js .rise-stagger.in > *:nth-child({i}) {{ transition-delay: {d}, {d}, 0s, 0s; }}',
        f'تأخیر پله‌ای فرزند {i} فقط برای opacity/transform')

rep('      html.js .rise-stagger.in > *:nth-child(n+7) { transition-delay: .45s; }',
    '      html.js .rise-stagger.in > *:nth-child(n+7) { transition-delay: .45s, .45s, 0s, 0s; }',
    'تأخیر پله‌ای فرزندان ۷+ فقط برای opacity/transform')

rep('       همه درون‌خطی (صفر درخواست بیرونی)، سبک، و با احترام به prefers-reduced-motion. */',
    '       همه درون‌خطی (صفر درخواست بیرونی)، سبک، و با احترام به prefers-reduced-motion.\n       (DESIGN-STEP1B: بلندشدن کارت با ویژگی مستقل translate — بدون تداخل با transformِ ورود نرم) */',
    'نشانگر DESIGN-STEP1B در توضیح بلوک')

io.open(P, 'w', encoding='utf-8').write(s)
print('\n'.join(f'  ✓ {d}' for d in done))
print(f'\nDone — {len(s)} chars written')
