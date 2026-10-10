#!/usr/bin/env python3
"""
DESIGN-STEP2B — اصلاح سلکتور D-10 (زبان واحد دکمه‌های اصلی)

مشکل: در گام ۲ سلکتور D-10 «مرکب» نوشته نشده بود؛ سه بخش :is(...) با فاصله/خط جدید
پشت هم آمده بودند و هر خط جدید در CSS یعنی ترکیب‌کنندهٔ «فرزند». نتیجه: قاعده روی
فرزندِ دکمه (مثلاً <span id="aiBtnText">) اعمال می‌شد، نه روی خود دکمه — پس هاور
۱٫۰۲ هیچ‌وقت روی دکمه دیده نمی‌شد (اودیت: scale 1.000→1.000).

اصلاح: هر سه سلکتور در یک خط و به‌صورت مرکب نوشته می‌شوند:
    :is(a, button):is([class^="bg-brand-blue"], …):is([class^="text-white"], …):not(…)
یعنی همهٔ شرط‌ها باید روی خودِ عنصر برقرار باشند (چیزی که کارفرما خواسته بود).

دامنهٔ پوشش (اندازه‌گیری‌شده روی بیلد): ۲۰ عنصر اصلی (دکمه‌های هدر، هیرو، پنل هوش،
ریموت، رزروِ ادامه/ذخیره، دراور چت…) — و ردیف‌های انتخابیِ دراپ‌داون/چیپ‌ها درست حذف می‌شوند.
اجرا:  python3 tools/patches/patch_design_step2b.py   (یک‌بار — نشانگر محافظت می‌کند)
"""
import io, sys

P = '/home/user/پشتیبان_رایانه.html'
MARK = 'DESIGN-STEP2B'
s = io.open(P, encoding='utf-8').read()
if MARK in s:
    sys.exit('این پچ قبلاً اجرا شده است — دوباره اجرا نمی‌شود.')
assert 'DESIGN-STEP2' in s, 'گام ۲ باید اول اجرا شده باشد.'

done = []

def rep(old, new, label, count=1):
    global s
    n = s.count(old)
    assert n == count, f'✗ {label}: {n} مورد پیدا شد (انتظار {count})\n{old[:200]}'
    s = s.replace(old, new, count)
    done.append(label)

# ------------------------------------------------------------------ سلکتور قدیمی (فرزندی — اشتباه)
OLD_SEL = """      :is(a, button):is([class^="bg-brand-blue"], [class*=" bg-brand-blue"],
                        [class^="bg-gradient-to-r"], [class*=" bg-gradient-to-r"])
                     :is([class^="text-white"], [class*=" text-white"])
                     :not(#aiFloatingLauncherBtn):not([class*="book-submit-btn"])"""

# ------------------------------------------------------------------ سلکتور جدید (مرکب — درست، یک خط)
SEL = (':is(a, button):is([class^="bg-brand-blue"], [class*=" bg-brand-blue"], '
       '[class^="bg-gradient-to-r"], [class*=" bg-gradient-to-r"])'
       ':is([class^="text-white"], [class*=" text-white"])'
       ':not(#aiFloatingLauncherBtn):not([class*="book-submit-btn"])')

# ۱) بلوک transition
rep(OLD_SEL + """ {
        transition: transform .18s cubic-bezier(.16,1,.3,1), box-shadow .18s cubic-bezier(.16,1,.3,1),
                    background-color .2s ease, color .2s ease, border-color .2s ease, opacity .2s ease;
      }""",
    "      " + SEL + """ {
        transition: transform .18s cubic-bezier(.16,1,.3,1), box-shadow .18s cubic-bezier(.16,1,.3,1),
                    background-color .2s ease, color .2s ease, border-color .2s ease, opacity .2s ease;
      }""",
    'سلکتور مرکب — بلوک transition')

# ۲) بلوک هاور
rep(OLD_SEL + """:hover { transform: scale(1.02); }""",
    "      " + SEL + """:hover { transform: scale(1.02); }""",
    'سلکتور مرکب — هاور ۱٫۰۲')

# ۳) بلوک فشردن
rep(OLD_SEL + """:active { transform: scale(.98); }""",
    "      " + SEL + """:active { transform: scale(.98); }""",
    'سلکتور مرکب — فشردن ۰٫۹۸')

# ------------------------------------------------------------------ یادداشت توضیحی + نشانگر
rep("""    /* D-10 — زبان واحد دکمه‌های اصلی: هاور ۱٫۰۲ · فشردن ۰٫۹۸.
       با سلکتور ویژگی پیاده می‌شود تا دکمه‌های ساخته‌شده در جاوااسکریپت هم خودکار پوشش بگیرند.
       (لانچر شناور و دکمه‌های رزرو استثنا هستند — رفتار خودشان را دارند.) */""",
    """    /* D-10 — زبان واحد دکمه‌های اصلی: هاور ۱٫۰۲ · فشردن ۰٫۹۸.   [DESIGN-STEP2B]
       سلکتور «مرکب» است: همهٔ شرط‌ها روی خودِ دکمه بررسی می‌شوند (نه فرزندش)، پس
       دکمه‌های ساخته‌شده در جاوااسکریپت هم خودکار پوشش می‌گیرند.
       (لانچر شناور و دکمه‌های رزرو استثنا هستند — رفتار خودشان را دارند.) */""",
    'یادداشت D-10 + نشانگر')

io.open(P, 'w', encoding='utf-8').write(s)
print('\n'.join(f'  ✓ {d}' for d in done))
print(f'\nDone — {len(s)} chars written')
print(f"  · scale(1.02): {s.count('scale(1.02)')} · نشانگرهای DESIGN-STEP2B: {s.count(MARK)}")
