#!/usr/bin/env python3
"""DESIGN-STEP4B — refine consistent glow + stronger translucency, based on screenshots."""
import io, os, sys
ROOT=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P=os.path.join(ROOT,'پشتیبان_رایانه.html')
s=io.open(P,encoding='utf-8').read()
if 'DESIGN-STEP4B' in s: sys.exit('DESIGN-STEP4B already applied.')
assert 'DESIGN-STEP4' in s and 'halo-br' in s, 'Apply Step 4 first.'
CSS=r'''

    /* ===== DESIGN-STEP4B — نور یکپارچه و شیشهٔ شفاف‌تر (بازبینی بصری) ===== */
    /* هاله‌های موضعی D-04 دیگر آبیِ یک‌طرفه/بنفشِ جدا نیستند: هر دو از همان دو نورِ
       آبیِ بالا-راست + بنفشِ بالا-چپِ هدر پیروی می‌کنند؛ فقط با شدت کمتر از نور محیط. */
    .halo-br, .halo-tr { background-image:
      radial-gradient(560px circle at 91% 4%, rgba(0,113,227,.045), rgba(0,113,227,0) 70%),
      radial-gradient(520px circle at 8% 7%, rgba(168,85,247,.032), rgba(168,85,247,0) 72%);
      background-position: 0 0, 0 0; }
    .dark .halo-br, .dark .halo-tr { background-image:
      radial-gradient(560px circle at 91% 4%, rgba(0,113,227,.095), rgba(0,113,227,0) 70%),
      radial-gradient(520px circle at 8% 7%, rgba(168,85,247,.070), rgba(168,85,247,0) 72%); }

    /* نور محیط از سطوح کمی بیشتر دیده شود؛ هنوز مات و خوانا می‌مانند، اما دیگر خاکستریِ تخت نیستند. */
    body div[class*="rounded-[28px]"][class*="bg-white"],
    body div[class*="rounded-3xl"][class*="bg-white"],
    body div[class*="rounded-2xl"][class*="bg-white"][class*="border-black"] {
      background-color: rgba(255,255,255,.52) !important;
      -webkit-backdrop-filter: blur(22px) saturate(155%); backdrop-filter: blur(22px) saturate(155%);
      box-shadow: 0 16px 40px -29px rgba(21,35,61,.25), inset 0 1px 0 rgba(255,255,255,.78); }
    body div[class*="rounded-2xl"][class*="bg-brand-lightGray"][class*="border-black"]:not([class*="border-dashed"]) {
      background-color: rgba(236,240,248,.38) !important;
      -webkit-backdrop-filter: blur(22px) saturate(150%); backdrop-filter: blur(22px) saturate(150%); }
    html.dark body div[class*="rounded-[28px]"][class*="bg-white"],
    html.dark body div[class*="rounded-3xl"][class*="bg-white"],
    html.dark body div[class*="rounded-2xl"][class*="bg-white"][class*="border-black"] {
      background-color: rgba(19,20,25,.56) !important;
      -webkit-backdrop-filter: blur(22px) saturate(145%); backdrop-filter: blur(22px) saturate(145%);
      box-shadow: 0 18px 44px -30px rgba(0,0,0,.78), inset 0 1px 0 rgba(255,255,255,.09); }
    html.dark body div[class*="rounded-2xl"][class*="bg-brand-lightGray"][class*="border-black"]:not([class*="border-dashed"]) {
      background-color: rgba(25,26,32,.48) !important;
      -webkit-backdrop-filter: blur(22px) saturate(140%); backdrop-filter: blur(22px) saturate(140%); }
    /* ===== END DESIGN-STEP4B ===== */
'''
assert s.count('</style>')==1
s=s.replace('</style>',CSS+'\n  </style>',1)
io.open(P,'w',encoding='utf-8').write(s)
print('✓ D-04 آبی/بنفش یکپارچه شد · شفافیت کارت‌ها بیشتر شد · blur 22px · [DESIGN-STEP4B]')
