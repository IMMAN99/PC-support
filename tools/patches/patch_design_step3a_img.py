#!/usr/bin/env python3
"""
DESIGN-STEP3A-IMG — جاسازی واقعی تصویر هیرو (اصلاح جاافتادگی).

در پچ «۳A» جای‌گذارِ تصویر (`data_uri('hero-bench')`) محاسبه شد ولی در متن قالب
جایگزین نشد؛ نتیجه: `src="__HERO__"` و کادر مشکی در هیرو. این پچ همان جای‌گذاری را
انجام می‌دهد. (فایل پچ ۳A هم برای بازسازی از صفر اصلاح شد.)
اجرا:  python3 tools/patches/patch_design_step3a_img.py
"""
import base64, io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P = os.path.join(ROOT, 'پشتیبان_رایانه.html')
if 'DESIGN-STEP3A-IMG' in io.open(P, encoding='utf-8').read():
    sys.exit('این پچ قبلاً اجرا شده است.')
s = io.open(P, encoding='utf-8').read()
assert 'DESIGN-STEP3A' in s, 'گام ۳ الف باید اول اجرا شده باشد.'
assert s.count('src="__HERO__"') == 1, 'جای‌گذار تصویر هیرو پیدا نشد.'

raw = io.open(os.path.join(ROOT, 'assets', 'img', 'hero-bench.webp'), 'rb').read()
uri = 'data:image/webp;base64,' + base64.b64encode(raw).decode()
s = s.replace('src="__HERO__"', 'src="' + uri + '"')
s = s.replace('DESIGN-STEP3A — «زنده‌شدن» صفحه: تصویر + پنل زنده + ساعت + شمارنده + پارالاکس =====  [DESIGN-STEP3A]',
              'DESIGN-STEP3A — «زنده‌شدن» صفحه: تصویر + پنل زنده + ساعت + شمارنده + پارالاکس =====  [DESIGN-STEP3A] [DESIGN-STEP3A-IMG]')
io.open(P, 'w', encoding='utf-8').write(s)
print(f'  ✓ تصویر هیرو جاسازی شد — {len(uri)/1024:.0f} KB base64 · فایل {len(s)} کاراکتر')
