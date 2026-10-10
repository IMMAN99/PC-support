#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Package 1 patch — applies the four correctness fixes to پشتیبان_رایانه.html:

  F-01  word-boundary matching + correct priority in runLocalIntelligentEngine()
        («آب» must not match inside «آبی»; blue-screen must win over liquid damage)
  F-03  single source of truth for opening hours (SHOP_HOURS):
        intake Sat–Wed until 17:00, remote support until 20:30
  F-04  Persian digits in booking counters + consistent thousands separator
  F-14  wording: «شیفت عصر» → «بعدازظهر», «نوبت پشتیبانی» → «جلسه»

Idempotent: refuses to run if the fixes are already present.
"""
import io, re, sys

PATH = "/home/user/پشتیبان_رایانه.html"
s = io.open(PATH, encoding="utf-8").read()
orig = s
applied = []

# ------------------------------------------------------------------ F-01 ----
if "F-01:" in s:
    print("F-01 already applied, skipping")
else:
    # every report template of the local engine, in current (wrong) order
    templates = re.findall(r"return `(### [^`]*?)`;", s, re.S)
    # keep only the 7 symptom reports (the vision branch has 3, then 6 + generic)
    assert len(templates) >= 9, f"unexpected template count: {len(templates)}"
    by_head = {}
    for t in templates:
        by_head[t.split("\n", 1)[0]] = t
    get = lambda kw: next(t for h, t in by_head.items() if kw in h)
    t_water   = get("نفوذ مایعات")
    t_burned  = get("سوختن ماسفت")
    t_thermal = get("Thermal Throttling")
    t_bsod    = get("آدرس‌دهی حافظه")
    t_disk    = get("استهلاک مکانیکی هارد")
    t_power   = get("افت ولتاژ مدار تغذیه")
    t_generic = get("عیب‌یابی هوشمند سیستم")

    start = s.index('      if (q.includes("آب")')
    end_marker = "\n      }\n    }\n\n    /**\n     * AI Free-text Diagnosis"
    end = s.index(end_marker, start) + len("\n      }\n")

    new_chain = '''      /* --- F-01: تطبیق روی مرز کلمه + ترتیب اولویت درست ---
         «آب» نباید داخل «آبی» پیدا شود، و «صفحه آبی»/کرش باید قبل از مایعات بررسی شود.
         فقط مرز چپِ کلمه لازم است تا پسوندهای فارسی (فنش، رمم، هاردش) هم پوشش داده شوند. */
      const rxL = (t) => new RegExp('(^|[^\\\\p{L}])' + t, 'u');
      const hit = (...terms) => terms.some(t => rxL(t).test(q));
      const TERMS = {
        bsod:    ['صفحه\\\\s*آبی', 'صفحهآبی', 'بلواسکرین', 'bsod', 'blue\\\\s*screen', 'استاپ\\\\s*کد', 'stop\\\\s*code', 'کرش', 'crash', 'ریستارت', 'restart', 'حافظه', 'مموری', 'memory', 'رم', 'ram'],
        liquid:  ['آب(?!ی)', 'مایع', 'خیس', 'چای', 'قهوه', 'نوشیدنی', 'ریخته'],
        burned:  ['بو(?!د)', 'سوخت', 'دود', 'جرقه', 'ماسفت', 'خازن'],
        thermal: ['فن(?!ا|ل)', 'داغ', 'حرارت', 'خاموش', 'گوشت', 'تهویه'],
        disk:    ['هارد', 'دیسک', 'کندی', 'درایو', 'اس\\\\s*اس\\\\s*دی', 'ssd', 'تیک', '۱۰۰'],
        power:   ['تصویر', 'روشن\\\\s*نمی', 'بوت\\\\s*نمی', 'بالا\\\\s*نمی', 'بوق', 'شارژ', 'برق']
      };

      if (hit(...TERMS.bsod)) {
        return `@@BSOD@@`;
      } else if (hit(...TERMS.liquid)) {
        return `@@WATER@@`;
      } else if (hit(...TERMS.burned)) {
        return `@@BURNED@@`;
      } else if (hit(...TERMS.thermal)) {
        return `@@THERMAL@@`;
      } else if (hit(...TERMS.disk)) {
        return `@@DISK@@`;
      } else if (hit(...TERMS.power)) {
        return `@@POWER@@`;
      } else {
        return `@@GENERIC@@`;
      }
'''
    for token, tmpl in [("BSOD", t_bsod), ("WATER", t_water), ("BURNED", t_burned),
                        ("THERMAL", t_thermal), ("DISK", t_disk), ("POWER", t_power),
                        ("GENERIC", t_generic)]:
        assert "@@" + token + "@@" in new_chain
        new_chain = new_chain.replace("@@" + token + "@@", tmpl)

    s = s[:start] + new_chain + s[end:]
    applied.append("F-01 diagnostic engine (boundary matching + priority)")

# ------------------------------------------------------------------ F-03 ----
if "SHOP_HOURS" in s:
    print("F-03 already applied, skipping")
else:
    old_fn_start = s.index("    function initShopHours() {")
    old_fn_end = s.index("\n    }\n", old_fn_start) + len("\n    }\n")
    new_fn = '''    /* --- F-03: منبع حقیقت واحد ساعت کاری ---
       پذیرش حضوری: شنبه تا چهارشنبه تا ۱۷:۰۰ | پشتیبانی ریموت و تلفنی: تا ۲۰:۳۰
       همهٔ جاهایی که ساعت کاری را نشان می‌دهند (نشان هدر، متن مودال رزرو، تقویم) از همین منبع می‌خوانند. */
    const SHOP_HOURS = {
      weekdays: [0, 1, 2, 3, 4],            // 0=شنبه … 4=چهارشنبه (پنجشنبه و جمعه تعطیل)
      intake:  { from: 9.5, to: 17 },       // پذیرش حضوری دستگاه
      support: { from: 9.5, to: 20.5 }      // پاسخگویی ریموت/تلفنی
    };

    function initShopHours() {
      const badge = document.getElementById("liveWorkStatusBadge");
      const text = document.getElementById("shopHoursStatusText");
      const dot = document.getElementById("shopHoursStatusDot");
      if (!badge || !text) return;

      const now = new Date();
      const utcTime = now.getTime() + now.getTimezoneOffset() * 60000;
      const tehranDate = new Date(utcTime + 3.5 * 3600000);
      const tehranIdx = (tehranDate.getDay() + 1) % 7;   // 0=شنبه … 6=جمعه
      const hour = tehranDate.getHours() + tehranDate.getMinutes() / 60;

      const faClock = (h) => `${Number(Math.floor(h)).toLocaleString("fa-IR").padStart(2, "۰")}:${h % 1 ? "۳۰" : "۰۰"}`;
      const isWorkday = SHOP_HOURS.weekdays.includes(tehranIdx);
      const intakeOpen = isWorkday && hour >= SHOP_HOURS.intake.from && hour < SHOP_HOURS.intake.to;
      const supportOpen = isWorkday && hour >= SHOP_HOURS.support.from && hour < SHOP_HOURS.support.to;

      const GREEN = "hidden xl:flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-medium bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20 shrink-0 whitespace-nowrap transition-colors";
      const AMBER = "hidden xl:flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-medium bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20 shrink-0 whitespace-nowrap transition-colors";

      if (intakeOpen) {
        text.textContent = "پذیرش حضوری باز است";
        badge.className = GREEN;
        if (dot) dot.className = "w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse shrink-0";
      } else if (supportOpen) {
        text.textContent = `پشتیبانی ریموت فعال — پذیرش حضوری تا ${faClock(SHOP_HOURS.intake.to)}`;
        badge.className = AMBER;
        if (dot) dot.className = "w-1.5 h-1.5 rounded-full bg-amber-500 animate-pulse shrink-0";
      } else {
        text.textContent = "خارج از ساعت کاری — رزرو آنلاین فعال";
        badge.className = AMBER;
        if (dot) dot.className = "w-1.5 h-1.5 rounded-full bg-amber-500 shrink-0";
      }
    }
'''
    s = s[:old_fn_start] + new_fn + s[old_fn_end:]
    applied.append("F-03 opening hours single source of truth")

# ------------------------------------------------------------------ F-04 ----
reps_f04 = [
    ('<b id="bookSelectedCountText" class="text-brand-blue">۱ خدمت انتخابی</b>',
     '<b id="bookSelectedCountText" class="text-brand-blue">۱ خدمت</b>'),
    ('if (countText) countText.textContent = `${selectedBookingServiceIds.size} خدمت انتخابی`;',
     'if (countText) countText.textContent = selectedBookingServiceIds.size === 0\n        ? "بدون خدمت"\n        : `${selectedBookingServiceIds.size.toLocaleString("fa-IR")} خدمت`;'),
    ('if (countSummary) countSummary.textContent = `${selectedBookingServiceIds.size} مورد`;',
     'if (countSummary) countSummary.textContent = `${selectedBookingServiceIds.size.toLocaleString("fa-IR")} مورد`;'),
    ('۲۵۰,۰۰۰ تومان', '۲۵۰٬۰۰۰ تومان'), ('۱۸۰,۰۰۰ تومان', '۱۸۰٬۰۰۰ تومان'),
    ('۱۲۰,۰۰۰ تومان', '۱۲۰٬۰۰۰ تومان'), ('۳۰۰,۰۰۰ تومان', '۳۰۰٬۰۰۰ تومان'),
]
n04 = 0
for a, b in reps_f04:
    if a in s:
        s = s.replace(a, b)
        n04 += 1
if n04:
    applied.append(f"F-04 Persian digits + separators ({n04} replacements)")

# ------------------------------------------------------------------ F-14 ----
reps_f14 = [
    ('✓ ۲ نوبت پشتیبانی ریموت فوری ماهانه', '✓ ۲ جلسه پشتیبانی ریموت فوری در ماه'),
    ('(شیفت عصر)', '(بعدازظهر)'),
]
n14 = 0
for a, b in reps_f14:
    if a in s:
        s = s.replace(a, b)
        n14 += 1
if n14:
    applied.append(f"F-14 wording ({n14} replacements)")

# ------------------------------------------------------------------ write ---
if s == orig:
    print("Nothing to do — all fixes already present.")
    sys.exit(0)

io.open(PATH, "w", encoding="utf-8").write(s)
print("Applied:")
for a in applied:
    print("  ✓", a)
print(f"\nFile: {len(orig)} → {len(s)} chars")
