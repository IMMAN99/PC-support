#!/usr/bin/env python3
"""
DESIGN-STEP3C — اصلاح خوانایی باندهای تصویری (RTL).

یافتهٔ شواهد تصویری: پنل متن در چیدمان راست‌به‌چپ سمت راست می‌نشیند، ولی سایهٔ تصویر
(scrim) از چپ تیره می‌شد؛ نتیجه: متن روی بخش روشنِ عکس می‌افتاد. اصلاح:
  · گرادیان سایه آینه شد (تیره از سمت راست)
  · سایهٔ متن ظریف برای اطمینان روی هر عکسی
اجرا:  python3 tools/patches/patch_design_step3c.py
"""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P = os.path.join(ROOT, 'پشتیبان_رایانه.html')
if 'DESIGN-STEP3C' in io.open(P, encoding='utf-8').read():
    sys.exit('این پچ قبلاً اجرا شده است.')
s = io.open(P, encoding='utf-8').read()
assert 'DESIGN-STEP3B' in s, 'بخش ب باید اول اجرا شده باشد.'

old = """    .al-band .al-scrim { background: linear-gradient(90deg, rgba(0,0,0,.64) 0%, rgba(0,0,0,.16) 56%, rgba(0,0,0,0) 100%); }"""
new = """    /* RTL: پنل متنِ باند سمت راست می‌نشیند، پس سایه هم از راست تیره می‌شود */
    .al-band .al-scrim { background: linear-gradient(270deg, rgba(0,0,0,.72) 0%, rgba(0,0,0,.28) 50%, rgba(0,0,0,0) 100%); }"""
assert s.count(old) == 1
s = s.replace(old, new)

old2 = """    .al-row span { display: block; font-size: 11px; color: rgba(255,255,255,.78); margin-top: 2px; line-height: 1.65; }"""
new2 = """    .al-row span { display: block; font-size: 11px; color: rgba(255,255,255,.80); margin-top: 2px; line-height: 1.65; }
    .al-panel { text-shadow: 0 1px 10px rgba(0,0,0,.6); }   /* خوانایی روی هر عکسی */"""
assert s.count(old2) == 1
s = s.replace(old2, new2)

s = s.replace('DESIGN-STEP3B: باندهای تصویری سکشن‌ها ---  [DESIGN-STEP3B]',
              'DESIGN-STEP3B: باندهای تصویری سکشن‌ها ---  [DESIGN-STEP3B] [DESIGN-STEP3C]')
io.open(P, 'w', encoding='utf-8').write(s)
print('  ✓ سایهٔ باندها آینه شد (تیره از راست) + سایهٔ متن پنل')
