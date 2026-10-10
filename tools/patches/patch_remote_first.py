#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Remote-first repositioning patch for پشتیبان_رایانه.html

Policy change requested by the shop:
  * Remote support is the MAIN product and runs 24/7 (shift coverage).
  * Presence is shown live — «آنلاین» is never faked; when no technician is on
    shift the request is queued and the first free technician calls back.
  * In-person workshop intake stays as the escalation path for hardware:
    Sat–Wed, 09:30–17:00.

Changes
  R-01  REMOTE_SUPPORT config + live presence engine (header badge, hero strip,
        remote section, floating launcher, chat drawer, request modal)
  R-02  new «پشتیبانی ریموت شبانه‌روزی» section right after the hero, with
        how-it-works, security/privacy strip, remote-vs-workshop triage columns
  R-03  hero rewritten remote-first (headline, sub, CTAs, cards)
  R-04  real remote request form (validated, consent, request code, ticket saved
        into the existing tracking store, optional messenger hand-off)
  R-05  nav / header CTAs / mobile drawer / footer / Care plans / FAQ / meta /
        JSON-LD aligned with the new positioning

Idempotent: aborts if the patch marker is already present.
"""
import io, sys

PATH = "/home/user/پشتیبان_رایانه.html"
s = io.open(PATH, encoding="utf-8").read()

if "REMOTE_SUPPORT" in s:
    print("Patch already applied — aborting.")
    sys.exit(0)

def sub(old, new, label, count=1):
    global s
    n = s.count(old)
    if n < 1:
        raise SystemExit(f"ANCHOR NOT FOUND [{label}]:\n{old[:160]}")
    s = s.replace(old, new, count)
    print(f"  ✓ {label}" + (f" ({n} occurrences)" if n > 1 and count == n else ""))

# =============================================================== R-05 meta ===
sub('<title>پشتیبان پی‌سی | مرکز تخصصی عیب‌یابی، ارتقا و نگهداری رایانه</title>',
    '<title>پشتیبان پی‌سی | پشتیبانی ریموت شبانه‌روزی و عیب‌یابی هوشمند رایانه</title>', "title")

sub('content="مرکز فوق تخصصی عیب‌یابی سخت‌افزاری و نرم‌افزاری، ارتقای پرسرعت SSD، سرویس دوره‌ای و پشتیبانی ریموت فوری مجهز به هوش مصنوعی در تهران"',
    'content="پشتیبانی ریموت شبانه‌روزی برای ویندوز، مک و لینوکس؛ اتصال امن از راه دور، عیب‌یابی هوشمند با هوش مصنوعی، و کارگاه تخصصی سخت‌افزار در تهران"',
    "og:description")

sub('content="تحلیل هوشمند خطاهای صفحه آبی، تست گلوگاه قطعات و ارتقای پرسرعت SSD"',
    'content="پشتیبانی ریموت ۲۴ ساعته، تحلیل هوشمند خطاهای صفحه آبی و ارتقای پرسرعت SSD"',
    "twitter:description")

sub('"description": "مرکز فوق تخصصی عیب‌یابی سخت‌افزاری و نرم‌افزاری، ارتقای پرسرعت SSD و سرویس دوره‌ای رایانه‌ها مجهز به هوش مصنوعی"',
    '"description": "پشتیبانی ریموت شبانه‌روزی (شیفتی) برای ویندوز، مک و لینوکس؛ عیب‌یابی هوشمند با هوش مصنوعی و کارگاه تخصصی تعمیر و ارتقای سخت‌افزار در تهران"',
    "JSON-LD store description")

# store hours = in-person intake only (was Sat–Thu 09:30–20:30 — the stale third source)
sub('''        "openingHoursSpecification": [
          {
            "@type": "OpeningHoursSpecification",
            "dayOfWeek": ["Saturday", "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"],
            "opens": "09:30",
            "closes": "20:30"
          }
        ],''',
    '''        "openingHoursSpecification": [
          {
            "@type": "OpeningHoursSpecification",
            "dayOfWeek": ["Saturday", "Sunday", "Monday", "Tuesday", "Wednesday"],
            "opens": "09:30",
            "closes": "17:00",
            "description": "پذیرش حضوری دستگاه در کارگاه"
          }
        ],''',
    "JSON-LD store hours → intake only")

# add a Service node for 24/7 remote support + two FAQ entries
sub('''      {
        "@type": "FAQPage",''',
    '''      {
        "@type": "Service",
        "@id": "https://poshtibanpc.ir/#remote-support",
        "name": "پشتیبانی ریموت شبانه‌روزی پشتیبان پی‌سی",
        "description": "پشتیبانی از راه دور برای ویندوز، مک و لینوکس در تمام ساعات شبانه‌روز به‌صورت شیفتی؛ اتصال امن با اجازهٔ کاربر و رمز یک‌بارمصرف جلسه.",
        "serviceType": "Remote technical support",
        "hoursAvailable": {
          "@type": "OpeningHoursSpecification",
          "dayOfWeek": ["Saturday", "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
          "opens": "00:00",
          "closes": "23:59"
        },
        "availableChannel": {
          "@type": "ServiceChannel",
          "serviceUrl": "https://poshtibanpc.ir/#remote-support",
          "availableLanguage": ["fa"]
        },
        "provider": { "@id": "https://poshtibanpc.ir/#store" }
      },
      {
        "@type": "FAQPage",''',
    "JSON-LD remote service node")

sub('''          {
            "@type": "Question",
            "name": "مدت زمان عیب‌یابی و تحویل سیستم‌ها در کارگاه چقدر است؟",
            "acceptedAnswer": {
              "@type": "Answer",
              "text": "ارتقای SSD، نصب ویندوز و سرویس حرارتی فن در همان روز (۲ الی ۴ ساعت) انجام و تحویل داده می‌شوند."
            }
          }''',
    '''          {
            "@type": "Question",
            "name": "مدت زمان عیب‌یابی و تحویل سیستم‌ها در کارگاه چقدر است؟",
            "acceptedAnswer": {
              "@type": "Answer",
              "text": "ارتقای SSD، نصب ویندوز و سرویس حرارتی فن در همان روز (۲ الی ۴ ساعت) انجام و تحویل داده می‌شوند."
            }
          },
          {
            "@type": "Question",
            "name": "پشتیبانی ریموت شبانه‌روزی یعنی چه؟ اگر نیمه‌شب درخواست بدهم چه می‌شود؟",
            "acceptedAnswer": {
              "@type": "Answer",
              "text": "پوشش پشتیبانی ریموت ۲۴ ساعته و شیفتی است. درخواست شما در هر ساعتی ثبت می‌شود و اگر کارشناسی آنلاین باشد همان لحظه وصل می‌شود؛ در غیر این صورت درخواست در صف می‌ماند و اولین کارشناس آزاد با شما تماس می‌گیرد. کد پیگیری هم برایتان صادر می‌شود."
            }
          },
          {
            "@type": "Question",
            "name": "اتصال از راه دور امن است؟ کارشناس چه دسترسی‌ای دارد؟",
            "acceptedAnswer": {
              "@type": "Answer",
              "text": "اتصال فقط با اجازهٔ شما و صرفاً در طول همان جلسه برقرار می‌شود؛ رمز جلسه یک‌بارمصرف است، همهٔ کارها روی صفحهٔ شما دیده می‌شود و می‌توانید هر لحظه اتصال را قطع کنید. بدون هماهنگی هیچ فایلی کپی نمی‌شود."
            }
          }''',
    "JSON-LD FAQ entries")

# ================================================================ R-05 head ==
sub('''        <!-- Live Status Badge -->
        <div id="liveWorkStatusBadge" class="hidden xl:flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-medium bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20 shrink-0 whitespace-nowrap transition-colors">
          <span id="shopHoursStatusDot" class="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse shrink-0"></span>
          <span id="shopHoursStatusText" class="whitespace-nowrap">پذیرش حضوری باز است</span>
        </div>''',
    '''        <!-- Live remote-support presence (never faked — driven by REMOTE_SUPPORT shifts) -->
        <div id="liveWorkStatusBadge" class="hidden xl:flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-medium bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20 shrink-0 whitespace-nowrap transition-colors">
          <span id="shopHoursStatusDot" class="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse shrink-0"></span>
          <span id="shopHoursStatusText" class="whitespace-nowrap">کارشناس آنلاین</span>
        </div>''',
    "header presence badge")

sub('''        <!-- Booking CTA -->
        <button onclick="openBookingModal()" class="text-[11px] font-semibold px-2.5 sm:px-3.5 py-1 rounded-full bg-brand-blue hover:bg-brand-blueHover text-white shadow-sm transition shrink-0 whitespace-nowrap">
          رزرو نوبت
        </button>''',
    '''        <!-- Remote support = primary CTA -->
        <button onclick="openRemoteModal()" class="inline-flex items-center gap-1.5 text-[11px] font-semibold px-2.5 sm:px-3.5 py-1 rounded-full bg-brand-blue hover:bg-brand-blueHover text-white shadow-sm transition shrink-0 whitespace-nowrap">
          <span class="w-1.5 h-1.5 rounded-full bg-white/90 animate-pulse"></span>
          <span>پشتیبانی ریموت</span>
        </button>

        <!-- In-person booking = secondary (hidden on very small screens) -->
        <button onclick="openBookingModal()" class="hidden md:inline-flex text-[11px] font-semibold px-3 py-1 rounded-full text-brand-dark/80 dark:text-white/80 hover:bg-black/5 dark:hover:bg-white/10 transition shrink-0 whitespace-nowrap">
          رزرو حضوری
        </button>''',
    "header CTAs")

sub('''        <a href="#overview" class="hover:text-brand-blue transition-colors whitespace-nowrap">نگاه کلی</a>
        <a href="#ai-diagnostic" class="ai-gradient-text font-bold hover:opacity-80 transition-opacity flex items-center gap-1.5 whitespace-nowrap">''',
    '''        <a href="#remote-support" class="hover:text-brand-blue transition-colors whitespace-nowrap flex items-center gap-1.5">
          <span class="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span><span>پشتیبانی ریموت</span>
        </a>
        <a href="#ai-diagnostic" class="ai-gradient-text font-bold hover:opacity-80 transition-opacity flex items-center gap-1.5 whitespace-nowrap">''',
    "desktop nav")

sub('''    <a href="#overview" onclick="toggleMobileMenu()" class="block py-1.5 hover:text-brand-blue">نگاه کلی به خدمات</a>
    <a href="#ai-diagnostic" onclick="toggleMobileMenu()" class="block py-1.5 ai-gradient-text font-bold">✦ عیب‌یاب هوشمند سیستم</a>''',
    '''    <a href="#remote-support" onclick="toggleMobileMenu()" class="flex items-center gap-2 py-1.5 font-bold text-emerald-600 dark:text-emerald-400">
      <span class="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span><span id="drawerPresenceLine">پشتیبانی ریموت شبانه‌روزی</span>
    </a>
    <a href="#ai-diagnostic" onclick="toggleMobileMenu()" class="block py-1.5 ai-gradient-text font-bold">✦ عیب‌یاب هوشمند سیستم</a>''',
    "mobile drawer link")

sub('''      <button onclick="openRemoteModal(); toggleMobileMenu();" class="py-2 text-center rounded-xl bg-black/5 dark:bg-white/10 font-bold">
        درخواست ریموت فوری
      </button>''',
    '''      <button onclick="openRemoteModal(); toggleMobileMenu();" class="col-span-2 py-2.5 text-center rounded-xl bg-brand-blue text-white font-bold">
        درخواست پشتیبانی ریموت
      </button>''',
    "mobile drawer primary CTA")

sub('''      <button onclick="openBookingModal(); toggleMobileMenu();" class="col-span-2 py-2.5 text-center rounded-xl bg-brand-blue text-white font-bold">
        رزرو نوبت پذیرش
      </button>''',
    '''      <button onclick="openBookingModal(); toggleMobileMenu();" class="col-span-2 py-2 text-center rounded-xl bg-black/5 dark:bg-white/10 font-bold">
        رزرو نوبت حضوری (کارگاه)
      </button>''',
    "mobile drawer booking CTA")

# ============================================================== R-03 hero ====
sub('<span class="text-[11px] font-bold ai-gradient-text">مجهز به موتور هوش مصنوعی آنبرد و ابری</span>\n      <span class="px-2 py-0.5 rounded-full bg-brand-blue text-white text-[9px] font-bold">نسخه جدید</span>',
    '<span class="text-[11px] font-bold ai-gradient-text">پشتیبانی ریموت شبانه‌روزی + موتور هوش مصنوعی آنبرد</span>\n      <span class="px-2 py-0.5 rounded-full bg-emerald-500 text-white text-[9px] font-bold" id="heroPresenceChip">آنلاین</span>',
    "hero kicker")

sub('''      <span class="inline-block">تکنولوژی نو.</span>
      <span class="block mt-3.5 sm:mt-4 md:mt-5 text-transparent bg-clip-text bg-gradient-to-r from-brand-blue via-indigo-500 to-purple-600">
        استانداردهای فوق‌العاده.
      </span>''',
    '''      <span class="inline-block">هر ساعت شبانه‌روز،</span>
      <span class="block mt-3.5 sm:mt-4 md:mt-5 text-transparent bg-clip-text bg-gradient-to-r from-brand-blue via-indigo-500 to-purple-600">
        کارشناس آنلاین داری.
      </span>''',
    "hero headline")

sub('''      مرکز تخصصی عیب‌یابی رایانه‌ها، ارتقای پرسرعت و بهینه‌سازی حرارتی. ایرادات سیستم و خطاهای صفحه آبی را در چند ثانیه به صورت هوشمند تحلیل کنید.''',
    '''      مشکل ویندوز، شبکه، ایمیل یا نرم‌افزار سیستم‌تان را همین حالا به کارشناس آنلاین بسپارید؛ اتصال امن از راه دور، بدون جابه‌جایی دستگاه. اگر عیب سخت‌افزاری باشد، کارگاه تخصصی ما در تهران در خدمت شماست.''',
    "hero subtitle")

sub('''      <a href="#ai-diagnostic" class="px-6 py-3 rounded-full bg-brand-blue hover:bg-brand-blueHover text-white text-xs sm:text-sm font-semibold shadow-lg shadow-brand-blue/20 transition transform active:scale-95 flex items-center gap-2">
        <span>عیب‌یابی هوشمند سیستم</span>
        <span class="text-xs">✦</span>
      </a>
      <button onclick="toggleAiDrawer(true)" class="px-6 py-3 rounded-full bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white text-xs sm:text-sm font-semibold shadow-lg shadow-purple-500/20 transition transform active:scale-95 flex items-center gap-2">
        <span>گفتگو با مشاور فنی</span>
        <span>💬</span>
      </button>
      <button onclick="openRemoteModal()" class="px-5 py-3 rounded-full bg-brand-lightGray dark:bg-brand-darkCard hover:bg-neutral-200 dark:hover:bg-neutral-800 text-brand-dark dark:text-white text-xs sm:text-sm font-semibold transition border border-black/[0.08] dark:border-white/[0.08]">
        درخواست ریموت فوری
      </button>
    </div>''',
    '''      <button onclick="openRemoteModal()" class="px-6 py-3 rounded-full bg-brand-blue hover:bg-brand-blueHover text-white text-xs sm:text-sm font-semibold shadow-lg shadow-brand-blue/20 transition transform active:scale-95 flex items-center gap-2">
        <span class="w-2 h-2 rounded-full bg-white/90 animate-pulse"></span>
        <span>درخواست پشتیبانی ریموت</span>
      </button>
      <button onclick="toggleAiDrawer(true)" class="px-6 py-3 rounded-full bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white text-xs sm:text-sm font-semibold shadow-lg shadow-purple-500/20 transition transform active:scale-95 flex items-center gap-2">
        <span>مشاور هوشمند فنی</span>
        <span class="text-xs">✦</span>
      </button>
      <a href="#ai-diagnostic" class="px-5 py-3 rounded-full bg-brand-lightGray dark:bg-brand-darkCard hover:bg-neutral-200 dark:hover:bg-neutral-800 text-brand-dark dark:text-white text-xs sm:text-sm font-semibold transition border border-black/[0.08] dark:border-white/[0.08]">
        عیب‌یابی رایگان سیستم
      </a>
    </div>

    <!-- Live status strip: remote presence (live) + intake hours (static policy) -->
    <div class="mt-6 flex flex-wrap items-center justify-center gap-x-4 gap-y-2 text-[11px] text-brand-gray">
      <span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 font-semibold border border-emerald-500/20">
        <span id="heroPresenceDot" class="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
        <span id="heroPresenceText">کارشناس آنلاین</span>
      </span>
      <span class="inline-flex items-center gap-1.5">
        <span id="intakeHoursDot" class="w-1.5 h-1.5 rounded-full bg-neutral-400"></span>
        <span id="intakeHoursText">پذیرش حضوری: شنبه تا چهارشنبه ۹:۳۰ تا ۱۷:۰۰</span>
      </span>
      <span>پاسخ‌گویی ریموت: تمام ساعات شبانه‌روز</span>
    </div>''',
    "hero CTAs + status strip")

sub('''          <div class="w-10 h-10 rounded-2xl bg-gradient-to-br from-purple-500/20 to-blue-500/20 text-purple-600 dark:text-purple-400 flex items-center justify-center mb-5">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
            </svg>
          </div>
          <span class="text-xs text-purple-600 dark:text-purple-400 font-bold">هوش مصنوعی آنبرد و ابری</span>
          <h2 class="text-xl font-bold mt-1 text-brand-dark dark:text-white">تحلیل هوشمند و فوری</h2>
          <p class="text-xs text-brand-gray mt-2 leading-relaxed">
            از توصیف مشکل تا آپلود تصویر صفحه آبی و لاگ‌های خطا؛ موتور هوشمند ریشه نقص فنی را همراه با چک‌لیست قبل از تحویل مشخص می‌کند.
          </p>
        </div>
        <div class="mt-6 pt-4 border-t border-black/[0.06] dark:border-white/[0.06] text-xs font-semibold text-purple-600 dark:text-purple-400 flex items-center gap-1">
          <a href="#ai-diagnostic" class="hover:underline">تست آنلاین عیب‌یاب هوشمند ←</a>
        </div>''',
    '''          <div class="w-10 h-10 rounded-2xl bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 flex items-center justify-center mb-5">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
            </svg>
          </div>
          <span class="text-xs text-emerald-600 dark:text-emerald-400 font-bold">پشتیبانی ریموت شبانه‌روزی</span>
          <h2 class="text-xl font-bold mt-1 text-brand-dark dark:text-white">حل مشکل از راه دور</h2>
          <p class="text-xs text-brand-gray mt-2 leading-relaxed">
            کارشناس آنلاین با اتصال امن به سیستم شما وصل می‌شود و ویندوز، شبکه، ایمیل، نرم‌افزار و امنیت را همان جلسه حل می‌کند — بدون بردن دستگاه به کارگاه.
          </p>
        </div>
        <div class="mt-6 pt-4 border-t border-black/[0.06] dark:border-white/[0.06] text-xs font-semibold text-emerald-600 dark:text-emerald-400 flex items-center gap-1">
          <button onclick="openRemoteModal()" class="hover:underline">درخواست پشتیبانی ریموت ←</button>
        </div>''',
    "hero card 1 → remote")

sub('''          <span class="text-xs text-brand-gray font-medium">ضمانت رسمی قطعات</span>
          <h2 class="text-xl font-bold mt-1 text-brand-dark dark:text-white">قطعات اورجینال با گارانتی</h2>''',
    '''          <span class="text-xs text-brand-gray font-medium">اگر عیب سخت‌افزاری بود</span>
          <h2 class="text-xl font-bold mt-1 text-brand-dark dark:text-white">کارگاه ارتقا و تعمیر</h2>''',
    "hero card 2 → workshop escalation")

# ============================================================ R-02 section ===
REMOTE_SECTION = '''  <!-- Remote Support 24/7 — the main offering -->
  <section id="remote-support" class="py-20 max-w-6xl mx-auto px-4 sm:px-6 scroll-mt-20 border-t border-black/[0.06] dark:border-white/[0.06]">
    <div class="text-center max-w-2xl mx-auto mb-12">
      <span class="text-xs font-bold text-brand-blue uppercase tracking-wider">پشتیبانی از راه دور</span>
      <h2 class="text-2xl sm:text-3xl font-extrabold mt-1 text-brand-dark dark:text-white">پشتیبانی ریموت شبانه‌روزی — کارشناس، هر ساعتی که لازم داری</h2>
      <p class="text-xs sm:text-sm text-brand-gray mt-2">اتصال امن از راه دور برای ویندوز، مک و لینوکس؛ بدون جابه‌جایی سیستم و بدون معطلی تا نوبت حضوری.</p>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">

      <!-- Live presence + primary CTA -->
      <div class="bg-white dark:bg-brand-darkCard rounded-[28px] p-7 border border-black/[0.08] dark:border-white/[0.08] shadow-sm flex flex-col justify-between">
        <div>
          <div class="flex items-center justify-between">
            <span class="text-xs text-brand-gray font-medium">وضعیت کارشناسان</span>
            <span class="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">پوشش شبانه‌روزی</span>
          </div>

          <div class="mt-5 flex items-center gap-2">
            <span id="remoteSectionDot" class="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse shrink-0"></span>
            <span id="remoteSectionCount" class="text-3xl font-black text-emerald-500">۱</span>
            <span id="remoteSectionCountLabel" class="text-xs text-brand-gray">کارشناس آنلاین</span>
          </div>

          <ul id="remoteSectionRoles" class="mt-4 space-y-2 text-[11px] text-brand-gray"></ul>

          <div class="mt-5 pt-4 border-t border-black/[0.06] dark:border-white/[0.06] space-y-1.5 text-[11px] text-brand-gray">
            <p id="remoteSectionResponse" class="font-semibold text-brand-dark dark:text-white">هدف پاسخ‌گویی: تا ۱۵ دقیقه</p>
            <p class="leading-relaxed">درخواست در هر ساعتی ثبت می‌شود؛ اگر کارشناسی در شیفت نباشد، درخواست در صف می‌ماند و اولین کارشناس آزاد با شما تماس می‌گیرد.</p>
          </div>
        </div>

        <div class="mt-6 space-y-2">
          <button onclick="openRemoteModal()" class="w-full py-3 rounded-full bg-brand-blue hover:bg-brand-blueHover text-white text-xs font-bold transition shadow-sm">
            درخواست پشتیبانی ریموت
          </button>
          <button onclick="toggleAiDrawer(true)" class="w-full py-2.5 rounded-full bg-black/5 dark:bg-white/10 hover:bg-black/10 text-xs font-bold text-brand-dark dark:text-white transition">
            اول خودت امتحان کن: مشاور هوشمند ✦
          </button>
        </div>
      </div>

      <!-- How remote support works -->
      <div class="lg:col-span-2 grid grid-cols-1 sm:grid-cols-3 gap-6">
        <div class="bg-white dark:bg-brand-darkCard rounded-[28px] p-6 border border-black/[0.08] dark:border-white/[0.08] shadow-sm">
          <span class="w-8 h-8 rounded-xl bg-brand-blue/10 text-brand-blue flex items-center justify-center text-xs font-bold">۱</span>
          <h3 class="text-sm font-bold mt-4 text-brand-dark dark:text-white">درخواست بده</h3>
          <p class="text-[11px] text-brand-gray mt-2 leading-relaxed">نام، شماره تماس و شرح کوتاه مشکل. کد پیگیری همان لحظه صادر می‌شود و می‌توانی وضعیتش را ببینی.</p>
        </div>
        <div class="bg-white dark:bg-brand-darkCard rounded-[28px] p-6 border border-black/[0.08] dark:border-white/[0.08] shadow-sm">
          <span class="w-8 h-8 rounded-xl bg-brand-blue/10 text-brand-blue flex items-center justify-center text-xs font-bold">۲</span>
          <h3 class="text-sm font-bold mt-4 text-brand-dark dark:text-white">کارشناس وصل می‌شود</h3>
          <p class="text-[11px] text-brand-gray mt-2 leading-relaxed">با AnyDesk، RustDesk یا درسان‌دسک — با اجازهٔ تو و رمز یک‌بارمصرف جلسه. هر لحظه بخواهی، اتصال قطع می‌شود.</p>
        </div>
        <div class="bg-white dark:bg-brand-darkCard rounded-[28px] p-6 border border-black/[0.08] dark:border-white/[0.08] shadow-sm">
          <span class="w-8 h-8 rounded-xl bg-brand-blue/10 text-brand-blue flex items-center justify-center text-xs font-bold">۳</span>
          <h3 class="text-sm font-bold mt-4 text-brand-dark dark:text-white">حل و گزارش</h3>
          <p class="text-[11px] text-brand-gray mt-2 leading-relaxed">مشکل همان جلسه حل می‌شود و گزارش فارسی کارهای انجام‌شده برایت ارسال می‌گردد.</p>
        </div>
      </div>
    </div>

    <!-- Remote-fixable vs workshop escalation -->
    <div class="mt-6 grid grid-cols-1 md:grid-cols-2 gap-6">
      <div class="bg-white dark:bg-brand-darkCard rounded-[28px] p-7 border border-black/[0.08] dark:border-white/[0.08] shadow-sm">
        <div class="flex items-center gap-2">
          <span class="w-2 h-2 rounded-full bg-emerald-500"></span>
          <h3 class="text-sm font-bold text-brand-dark dark:text-white">از راه دور حل می‌شود</h3>
        </div>
        <ul class="mt-4 space-y-2 text-[11px] text-brand-gray leading-relaxed">
          <li>• ویندوز بالا نمی‌آید، بوت‌لوپ، صفحه آبی و خطاهای درایور</li>
          <li>• شبکه، اینترنت، وای‌فای، پرینتر و اشتراک فایل</li>
          <li>• آفیس، ایمیل، نرم‌افزارهای اداری و مشکلات لایسنس</li>
          <li>• ویروس، بدافزار، تبلیغ‌های پاپ‌آپ و کندی نرم‌افزاری</li>
          <li>• بازیابی فایل‌های پاک‌شده و راه‌اندازی بکاپ</li>
          <li>• تنظیمات بوت، پارتیشن‌بندی و بهینه‌سازی استارتاپ</li>
        </ul>
      </div>
      <div class="bg-white dark:bg-brand-darkCard rounded-[28px] p-7 border border-black/[0.08] dark:border-white/[0.08] shadow-sm">
        <div class="flex items-center gap-2">
          <span class="w-2 h-2 rounded-full bg-brand-blue"></span>
          <h3 class="text-sm font-bold text-brand-dark dark:text-white">مسیر کارگاه (عیب سخت‌افزاری)</h3>
        </div>
        <ul class="mt-4 space-y-2 text-[11px] text-brand-gray leading-relaxed">
          <li>• تعویض قطعه، مادربرد، مدار تغذیه و پاور</li>
          <li>• تعمیر صفحه، کیبورد، لولا و پورت‌های دستگاه</li>
          <li>• ارتقای SSD و رم همراه با کلون کامل اطلاعات</li>
          <li>• سرویس حرارتی، تعویض خمیر سیلیکون و فن</li>
          <li>• ریکاوری تخصصی هارد و آزمون‌های آزمایشگاهی</li>
        </ul>
        <button onclick="openBookingModal()" class="mt-5 w-full py-2.5 rounded-full bg-brand-lightGray dark:bg-white/10 hover:bg-neutral-200 dark:hover:bg-white/[0.15] text-brand-dark dark:text-white text-xs font-bold transition">
          رزرو نوبت حضوری در کارگاه
        </button>
      </div>
    </div>

    <!-- Security + tools strip -->
    <div class="mt-6 bg-white dark:bg-brand-darkCard rounded-[28px] p-6 border border-black/[0.08] dark:border-white/[0.08] shadow-sm flex flex-col lg:flex-row lg:items-center gap-5 lg:justify-between">
      <div class="flex flex-wrap items-center gap-x-5 gap-y-2 text-[11px] text-brand-gray">
        <span class="text-xs font-bold text-brand-dark dark:text-white">امنیت اتصال:</span>
        <span>✓ فقط با اجازهٔ شما و در همان جلسه</span>
        <span>✓ رمز یک‌بارمصرف جلسه</span>
        <span>✓ بدون کپی فایل بدون هماهنگی</span>
        <span>✓ قطع اتصال با یک کلیک، هر لحظه</span>
      </div>
      <div class="flex flex-wrap items-center gap-2 text-[10px] font-semibold text-brand-gray shrink-0">
        <span class="px-2.5 py-1 rounded-full bg-black/5 dark:bg-white/5">AnyDesk</span>
        <span class="px-2.5 py-1 rounded-full bg-black/5 dark:bg-white/5">RustDesk</span>
        <span class="px-2.5 py-1 rounded-full bg-black/5 dark:bg-white/5">درسان‌دسک</span>
        <span class="px-2.5 py-1 rounded-full bg-black/5 dark:bg-white/5">TeamViewer</span>
      </div>
    </div>
  </section>

'''
sub('  <!-- AI Diagnostic Hub -->', REMOTE_SECTION + '  <!-- AI Diagnostic Hub -->', "new remote section")

# ============================================================= R-04 modal ===
old_modal_start = s.index('  <div id="remoteModal"')
old_modal_end = s.index('  <!-- AI Custom API Key Settings Modal (aiSettingsModal) -->')
NEW_MODAL = '''  <div id="remoteModal" class="fixed inset-0 modal-glass-blur hidden z-50 place-items-center p-4 overflow-y-auto">
    <div class="bg-white dark:bg-[#1c1c1e] text-brand-dark dark:text-white rounded-[28px] max-w-lg w-full p-6 sm:p-8 shadow-2xl relative my-auto border border-black/[0.08] dark:border-white/[0.08]">

      <button onclick="closeRemoteModal()" aria-label="بستن" class="absolute left-6 top-6 w-8 h-8 rounded-full bg-black/5 dark:bg-white/10 flex items-center justify-center hover:opacity-75 transition">
        ✕
      </button>

      <!-- Request form -->
      <div id="remoteFormView">
        <span class="text-xs font-bold text-brand-blue uppercase tracking-wider">پشتیبانی ریموت شبانه‌روزی</span>
        <h3 class="text-xl font-bold mt-1 text-brand-dark dark:text-white">درخواست پشتیبانی از راه دور</h3>
        <p id="remoteModalPresence" class="mt-2 text-[11px] font-semibold text-emerald-600 dark:text-emerald-400">کارشناس آنلاین — هدف پاسخ‌گویی تا ۱۵ دقیقه</p>
        <p class="text-xs text-brand-gray mt-1 leading-relaxed">
          اتصال فقط با اجازهٔ شما و در همان جلسه برقرار می‌شود. برای عیب‌های سخت‌افزاری، پذیرش حضوری کارگاه (شنبه تا چهارشنبه ۹:۳۰ تا ۱۷:۰۰) در دسترس است.
        </p>

        <form onsubmit="handleRemoteSubmit(event)" class="mt-6 space-y-4">
          <div>
            <label for="remoteNameInput" class="block text-xs font-semibold text-neutral-800 dark:text-neutral-200 mb-1.5">نام و نام‌خانوادگی</label>
            <input type="text" id="remoteNameInput" required placeholder="مثال: سارا محمدی"
                   class="w-full bg-neutral-100 dark:bg-[#252528] border border-black/[0.08] dark:border-white/[0.08] rounded-xl px-4 py-2.5 text-xs text-brand-dark dark:text-white placeholder:text-neutral-400 dark:placeholder:text-neutral-500 focus:outline-none focus:border-brand-blue transition">
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label for="remotePhoneInput" class="block text-xs font-semibold text-neutral-800 dark:text-neutral-200 mb-1.5">شماره تماس</label>
              <input type="tel" id="remotePhoneInput" required placeholder="۰۹۱۲۳۴۵۶۷۸۹" dir="ltr"
                     class="w-full bg-neutral-100 dark:bg-[#252528] border border-black/[0.08] dark:border-white/[0.08] rounded-xl px-4 py-2.5 text-xs text-brand-dark dark:text-white text-right placeholder:text-neutral-400 dark:placeholder:text-neutral-500 focus:outline-none focus:border-brand-blue transition">
            </div>
            <div>
              <label for="remoteOsSelect" class="block text-xs font-semibold text-neutral-800 dark:text-neutral-200 mb-1.5">سیستم‌عامل</label>
              <select id="remoteOsSelect" class="w-full bg-neutral-100 dark:bg-[#252528] border border-black/[0.08] dark:border-white/[0.08] rounded-xl px-4 py-2.5 text-xs text-brand-dark dark:text-white font-medium focus:outline-none focus:border-brand-blue cursor-pointer transition">
                <option>ویندوز ۱۰ / ۱۱</option>
                <option>ویندوز ۷ / ۸</option>
                <option>مک (macOS)</option>
                <option>لینوکس</option>
                <option>سایر / نمی‌دانم</option>
              </select>
            </div>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label for="remoteCategorySelect" class="block text-xs font-semibold text-neutral-800 dark:text-neutral-200 mb-1.5">نوع مشکل</label>
              <select id="remoteCategorySelect" class="w-full bg-neutral-100 dark:bg-[#252528] border border-black/[0.08] dark:border-white/[0.08] rounded-xl px-4 py-2.5 text-xs text-brand-dark dark:text-white font-medium focus:outline-none focus:border-brand-blue cursor-pointer transition">
                <option>ویندوز و بوت</option>
                <option>شبکه، اینترنت و وای‌فای</option>
                <option>نرم‌افزار، آفیس و ایمیل</option>
                <option>ویروس، بدافزار و امنیت</option>
                <option>درایور و سخت‌افزار (تشخیص از راه دور)</option>
                <option>ریکاوری و بکاپ اطلاعات</option>
                <option>سایر</option>
              </select>
            </div>
            <div>
              <label for="remoteToolSelect" class="block text-xs font-semibold text-neutral-800 dark:text-neutral-200 mb-1.5">نرم‌افزار اتصال</label>
              <select id="remoteToolSelect" class="w-full bg-neutral-100 dark:bg-[#252528] border border-black/[0.08] dark:border-white/[0.08] rounded-xl px-4 py-2.5 text-xs text-brand-dark dark:text-white font-medium focus:outline-none focus:border-brand-blue cursor-pointer transition">
                <option>AnyDesk</option>
                <option>RustDesk</option>
                <option>درسان‌دسک (DorsanDesk)</option>
                <option>TeamViewer</option>
                <option>نمی‌دانم — کارشناس راهنمایی کند</option>
              </select>
            </div>
          </div>

          <div>
            <label for="remoteProblemInput" class="block text-xs font-semibold text-neutral-800 dark:text-neutral-200 mb-1.5">شرح کوتاه مشکل</label>
            <input type="text" id="remoteProblemInput" placeholder="مثال: بعد از آپدیت، ویندوز بالا نمی‌آید یا پرینتر در شبکه دیده نمی‌شود"
                   class="w-full bg-neutral-100 dark:bg-[#252528] border border-black/[0.08] dark:border-white/[0.08] rounded-xl px-4 py-2.5 text-xs text-brand-dark dark:text-white placeholder:text-neutral-400 dark:placeholder:text-neutral-500 focus:outline-none focus:border-brand-blue transition">
          </div>

          <div>
            <label for="remoteChannelSelect" class="block text-xs font-semibold text-neutral-800 dark:text-neutral-200 mb-1.5">راه تماس کارشناس با شما</label>
            <select id="remoteChannelSelect" class="w-full bg-neutral-100 dark:bg-[#252528] border border-black/[0.08] dark:border-white/[0.08] rounded-xl px-4 py-2.5 text-xs text-brand-dark dark:text-white font-medium focus:outline-none focus:border-brand-blue cursor-pointer transition">
              <option>تماس تلفنی</option>
              <option>واتساپ</option>
              <option>تلگرام</option>
              <option>بله / ایتا</option>
            </select>
          </div>

          <label class="flex items-start gap-2.5 p-3 rounded-xl bg-brand-lightGray dark:bg-white/5 border border-black/[0.06] dark:border-white/[0.08] cursor-pointer">
            <input type="checkbox" id="remoteConsentCheck" required class="mt-0.5 shrink-0"
                   onchange="this.closest('label').classList.toggle('opacity-60', !this.checked)">
            <span class="text-[11px] text-brand-gray leading-relaxed">
              اجازه می‌دهم کارشناس با ابزار ریموت — فقط در طول همین جلسه — به سیستم من متصل شود. می‌دانم که می‌توانم هر لحظه اتصال را قطع کنم.
            </span>
          </label>

          <button type="submit" class="w-full py-3 bg-brand-blue hover:bg-brand-blueHover text-white rounded-full text-xs font-bold transition shadow-sm">
            ثبت درخواست پشتیبانی ریموت
          </button>
        </form>
      </div>

      <!-- Success view -->
      <div id="remoteSuccessView" class="hidden text-center">
        <div class="w-12 h-12 rounded-full bg-emerald-500/10 text-emerald-500 flex items-center justify-center mx-auto text-xl font-bold">✓</div>
        <h3 class="text-lg font-bold mt-4 text-brand-dark dark:text-white">درخواست ریموت ثبت شد</h3>
        <p class="text-xs text-brand-gray mt-2">کد پیگیری</p>
        <b id="remoteSuccessCode" class="block mt-1 font-mono text-2xl font-black text-brand-blue" dir="ltr">RM-1405-000</b>
        <p id="remoteSuccessNext" class="text-[11px] text-brand-gray mt-4 leading-relaxed"></p>
        <div id="remoteSuccessHandoff" class="mt-4 flex flex-wrap gap-2 justify-center"></div>
        <div class="mt-6 flex flex-col sm:flex-row gap-2">
          <button onclick="closeRemoteModal()" class="flex-1 py-2.5 rounded-full bg-black/5 dark:bg-white/10 hover:bg-black/10 text-xs font-bold text-brand-dark dark:text-white transition">بستن</button>
          <button onclick="var c=document.getElementById('remoteSuccessCode').textContent; closeRemoteModal(); openTrackingModalWithCode(c);" class="flex-1 py-2.5 rounded-full bg-brand-blue hover:bg-brand-blueHover text-white text-xs font-bold transition">پیگیری این درخواست</button>
        </div>
      </div>

    </div>
  </div>

'''
s = s[:old_modal_start] + NEW_MODAL + s[old_modal_end:]
print("  ✓ remote modal rebuilt (real form + success view)")

# ========================================================== R-05 AI drawer ==
sub('''    <!-- Drawer Input Form -->''',
    '''    <!-- Remote handoff inside the assistant drawer -->
    <div class="px-4 py-3 border-t border-black/[0.08] dark:border-white/[0.08] bg-emerald-500/5 dark:bg-emerald-500/5">
      <button onclick="toggleAiDrawer(false); openRemoteModal();" class="w-full flex items-center justify-center gap-2 py-2.5 rounded-xl bg-brand-blue hover:bg-brand-blueHover text-white text-[11px] font-bold transition">
        <span class="w-1.5 h-1.5 rounded-full bg-white/90 animate-pulse"></span>
        <span>حل نشد؟ اتصال ریموت با کارشناس انسانی — <span id="drawerPresenceCount">آنلاین</span></span>
      </button>
    </div>

    <!-- Drawer Input Form -->''',
    "AI drawer remote handoff")

# ============================================================ R-05 launcher =
sub('''    <button onclick="toggleAiDrawer()" id="aiFloatingLauncherBtn" class="flex items-center gap-2 px-4 py-2.5 rounded-full bg-brand-dark dark:bg-white text-white dark:text-brand-dark shadow-2xl hover:scale-105 active:scale-95 transition-transform duration-200 border border-white/20 dark:border-black/20 ai-glow">
      <span class="w-2 h-2 rounded-full bg-purple-500 animate-pulse"></span>
      <span class="text-xs font-bold">مشاور فنی هوشمند</span>
      <span class="text-xs">✦</span>
    </button>''',
    '''    <button onclick="openRemoteModal()" id="aiFloatingLauncherBtn" class="flex items-center gap-2 px-4 py-2.5 rounded-full bg-brand-dark dark:bg-white text-white dark:text-brand-dark shadow-2xl hover:scale-105 active:scale-95 transition-transform duration-200 border border-white/20 dark:border-black/20 ai-glow">
      <span id="launcherPresenceDot" class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
      <span class="text-xs font-bold">پشتیبانی ریموت</span>
      <span id="launcherPresenceText" class="text-[10px] px-2 py-0.5 rounded-full bg-white/15 dark:bg-black/10">آنلاین</span>
    </button>''',
    "floating launcher → remote")

# =============================================================== R-05 plans ==
sub('<li class="flex items-center gap-2">✓ ۲ جلسه پشتیبانی ریموت فوری در ماه</li>',
    '<li class="flex items-center gap-2">✓ پوشش پشتیبانی ریموت شبانه‌روزی (شیفتی)</li>\n            <li class="flex items-center gap-2">✓ ۲ جلسه پشتیبانی ریموت فوری در ماه</li>',
    "plan 1 bullet")
sub('<li class="flex items-center gap-2">✓ پشتیبانی ریموت نامحدود بدون صف</li>',
    '<li class="flex items-center gap-2">✓ پشتیبانی ریموت نامحدود شبانه‌روزی بدون صف</li>',
    "plan 2 bullet")
sub('<li class="flex items-center gap-2">✓ اعزام کارشناس حضوری در تهران</li>',
    '<li class="flex items-center gap-2">✓ پوشش ریموت شبانه‌روزی برای همهٔ دستگاه‌های شبکه</li>\n            <li class="flex items-center gap-2">✓ اعزام کارشناس حضوری در تهران</li>',
    "plan 3 bullet")

# ================================================================= R-05 FAQ ==
sub('<p class="text-xs sm:text-sm text-brand-gray mt-2">هر آنچه پیش از تحویل سیستم یا درخواست تعمیرات لازم است بدانید.</p>',
    '<p class="text-xs sm:text-sm text-brand-gray mt-2">هر آنچه پیش از درخواست پشتیبانی ریموت یا تحویل دستگاه لازم است بدانید.</p>',
    "FAQ intro")

sub('''            کلیه قطعات سخت‌افزاری از قبیل ماژول‌های رم، پاور و حافظه‌های SSD با گارانتی ۱۲ الی ۲۴ ماهه شرکت‌های معتبر واردکننده و هولوگرام اصالت ارائه می‌شوند. علاوه بر گارانتی قطعه، اجرت خدمات فنی نیز دارای ۳۰ روز مهلت تست رسمی در فاکتور ممهور کارگاه می‌باشد.
          </div>
        </div>

      </div>''',
    '''            کلیه قطعات سخت‌افزاری از قبیل ماژول‌های رم، پاور و حافظه‌های SSD با گارانتی ۱۲ الی ۲۴ ماهه شرکت‌های معتبر واردکننده و هولوگرام اصالت ارائه می‌شوند. علاوه بر گارانتی قطعه، اجرت خدمات فنی نیز دارای ۳۰ روز مهلت تست رسمی در فاکتور ممهور کارگاه می‌باشد.
          </div>
        </div>

        <!-- FAQ Item 5 — remote policy -->
        <div class="bg-white dark:bg-brand-darkCard rounded-2xl border border-black/[0.08] dark:border-white/[0.08] overflow-hidden transition">
          <button onclick="toggleFaq(this)" class="w-full text-right p-6 flex items-center justify-between text-xs sm:text-sm font-bold text-brand-dark dark:text-white">
            <span>پشتیبانی ریموت شبانه‌روزی یعنی چه؟ اگر نیمه‌شب درخواست بدهم چه می‌شود؟</span>
            <span class="faq-icon text-brand-gray transform transition-transform duration-300">▼</span>
          </button>
          <div class="faq-answer px-6 pt-6 pb-6 text-xs text-brand-gray leading-8 hidden border-t border-black/[0.04] dark:border-white/[0.04]">
            پوشش پشتیبانی ریموت ۲۴ ساعته و شیفتی است: در تمام ساعات شبانه‌روز یک کارشناس در شیفت حضور دارد. وضعیت آنلاین بودن کارشناسان به‌صورت زنده در بالای همین صفحه و در بخش «پشتیبانی از راه دور» نمایش داده می‌شود. درخواست شما در هر ساعتی ثبت می‌شود و کد پیگیری می‌گیرد؛ اگر کارشناس آنلاین باشد همان لحظه وصل می‌شود و اگر در حال تعویض شیفت باشد، درخواست در صف می‌ماند و اولین کارشناس آزاد با شما تماس می‌گیرد. هدف پاسخ‌گویی ما تا ۱۵ دقیقه است.
          </div>
        </div>

        <!-- FAQ Item 6 — remote security -->
        <div class="bg-white dark:bg-brand-darkCard rounded-2xl border border-black/[0.08] dark:border-white/[0.08] overflow-hidden transition">
          <button onclick="toggleFaq(this)" class="w-full text-right p-6 flex items-center justify-between text-xs sm:text-sm font-bold text-brand-dark dark:text-white">
            <span>اتصال از راه دور امن است؟ کارشناس چه دسترسی‌ای به سیستم من دارد؟</span>
            <span class="faq-icon text-brand-gray transform transition-transform duration-300">▼</span>
          </button>
          <div class="faq-answer px-6 pt-6 pb-6 text-xs text-brand-gray leading-8 hidden border-t border-black/[0.04] dark:border-white/[0.04]">
            اتصال فقط با اجازهٔ شما و صرفاً در طول همان جلسه برقرار می‌شود. ابزارهای مورد استفاده AnyDesk، RustDesk یا درسان‌دسک هستند و هر جلسه رمز یک‌بارمصرف دارد. تمام کارهای کارشناس روی صفحهٔ شما دیده می‌شود و هر لحظه که بخواهید می‌توانید اتصال را قطع کنید. بدون هماهنگی قبلی هیچ فایلی از سیستم شما کپی یا حذف نمی‌شود و نشست‌های پشتیبانی برای مراجعات بعدی ثبت می‌گردد.
          </div>
        </div>

      </div>''',
    "FAQ items 5 & 6")

# ============================================================== R-05 footer =
sub('<span class="font-bold text-brand-dark dark:text-white">پشتیبان پی‌سی پایتخت</span>',
    '<span class="font-bold text-brand-dark dark:text-white">پشتیبان پی‌سی پایتخت — پشتیبانی ریموت شبانه‌روزی</span>',
    "footer tagline")
sub('<a href="#overview" class="hover:text-brand-dark dark:hover:text-white transition">نگاه کلی</a>',
    '<a href="#remote-support" class="hover:text-brand-dark dark:hover:text-white transition">پشتیبانی ریموت</a>',
    "footer links")

# ================================================================ R-01 JS ===
sub('''    function initShopHours() {''',
    '''    /* ================= پشتیبانی ریموت شبانه‌روزی — منبع حقیقت واحد =================
       الگوی پوشش: شیفت‌های چرخشی در همهٔ روزهای هفته.
       وضعیت «آنلاین» فقط از همین شیفت‌ها (یا قفل دستی پذیرش) محاسبه می‌شود و
       هیچ‌گاه به‌صورت ثابت نمایش داده نمی‌شود — چون فقط به همان تعداد کارشناسی
       که واقعاً در شیفت است پاسخ داده می‌شود. */
    const REMOTE_SUPPORT = {
      coverageLabel: 'پوشش شبانه‌روزی',
      responseTargetMin: 15,
      shifts: [
        { days: [0, 1, 2, 3, 4, 5, 6], from: 0,  to: 9,  role: 'کارشناس شیفت شب — ویندوز و شبکه' },
        { days: [0, 1, 2, 3, 4, 5, 6], from: 8,  to: 17, role: 'کارشناس ارشد نرم‌افزار و امنیت' },
        { days: [0, 1, 2, 3, 4, 5, 6], from: 16, to: 24, role: 'کارشناس ریکاوری داده و شبکه' }
      ],
      manualFallbackRole: 'کارشناس کشیک (آنلاین دستی)',
      manualOverride: null   // 'online' | 'offline' | null — پذیرش می‌تواند وضعیت را دستی قفل کند
    };

    /* کانال تحویل درخواست: چون سایت هنوز بک‌اند ندارد، این دو مقدار تنها مسیری هستند
       که درخواست ریموت را واقعاً به دست کارشناس می‌رسانند. پس از پر شدن، دکمهٔ
       پیام‌رسان در پیام موفقیت به‌طور خودکار ظاهر می‌شود.
       مثال: whatsapp: '989121234567' , telegram: 'poshtibanpc' */
    const SITE_CONTACT = { whatsapp: '', telegram: '' };

    function getTehranNow() {
      const n = new Date();
      const utc = n.getTime() + n.getTimezoneOffset() * 60000;
      return new Date(utc + 3.5 * 3600000);
    }
    function getTehranIndex(d) { return (d.getDay() + 1) % 7; }   // 0=شنبه … 6=جمعه
    function faNum(n) { return Number(n).toLocaleString('fa-IR'); }

    function getOnlineTechs(d = getTehranNow()) {
      if (REMOTE_SUPPORT.manualOverride === 'offline') return [];
      const h = d.getHours() + d.getMinutes() / 60;
      const day = getTehranIndex(d);
      let list = REMOTE_SUPPORT.shifts.filter(s => s.days.includes(day) && h >= s.from && h < s.to);
      if (!list.length && REMOTE_SUPPORT.manualOverride === 'online') {
        list = [{ role: REMOTE_SUPPORT.manualFallbackRole }];
      }
      return list;
    }

    function isIntakeOpenNow(d = getTehranNow()) {
      const h = d.getHours() + d.getMinutes() / 60;
      return SHOP_HOURS.weekdays.includes(getTehranIndex(d)) && h >= SHOP_HOURS.intake.from && h < SHOP_HOURS.intake.to;
    }

    /* یک تابع، همهٔ نقاط نمایش وضعیت را پر می‌کند */
    function renderPresence() {
      const d = getTehranNow();
      const techs = getOnlineTechs(d);
      const n = techs.length;
      const target = faNum(REMOTE_SUPPORT.responseTargetMin);
      const online = n > 0;

      const GREEN = "hidden xl:flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-medium bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20 shrink-0 whitespace-nowrap transition-colors";
      const AMBER = "hidden xl:flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-medium bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20 shrink-0 whitespace-nowrap transition-colors";

      const badge = document.getElementById('liveWorkStatusBadge');
      const badgeText = document.getElementById('shopHoursStatusText');
      const badgeDot = document.getElementById('shopHoursStatusDot');
      if (badge && badgeText && badgeDot) {
        if (online) {
          badgeText.textContent = `${faNum(n)} کارشناس آنلاین`;
          badge.className = GREEN;
          badgeDot.className = "w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse shrink-0";
        } else {
          badgeText.textContent = 'درخواست‌ها در صف — اولین کارشناس تماس می‌گیرد';
          badge.className = AMBER;
          badgeDot.className = "w-1.5 h-1.5 rounded-full bg-amber-500 shrink-0";
        }
      }

      const chip = document.getElementById('heroPresenceChip');
      if (chip) {
        chip.textContent = online ? `${faNum(n)} آنلاین` : 'صف درخواست';
        chip.className = online
          ? 'px-2 py-0.5 rounded-full bg-emerald-500 text-white text-[9px] font-bold'
          : 'px-2 py-0.5 rounded-full bg-amber-500 text-white text-[9px] font-bold';
      }

      const heroDot = document.getElementById('heroPresenceDot');
      const heroText = document.getElementById('heroPresenceText');
      if (heroDot && heroText) {
        if (online) {
          heroText.textContent = `${faNum(n)} کارشناس آنلاین — هدف پاسخ تا ${target} دقیقه`;
          heroDot.className = "w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse";
        } else {
          heroText.textContent = `همهٔ کارشناسان در تعویض شیفت‌اند — درخواست بگذار، اولین نفر تماس می‌گیرد`;
          heroDot.className = "w-1.5 h-1.5 rounded-full bg-amber-500";
        }
      }

      const secDot = document.getElementById('remoteSectionDot');
      const secCount = document.getElementById('remoteSectionCount');
      const secLabel = document.getElementById('remoteSectionCountLabel');
      const secRoles = document.getElementById('remoteSectionRoles');
      const secResp = document.getElementById('remoteSectionResponse');
      if (secCount && secLabel) {
        secCount.textContent = faNum(n);
        secCount.className = online ? 'text-3xl font-black text-emerald-500' : 'text-3xl font-black text-amber-500';
        secLabel.textContent = online ? 'کارشناس آنلاین' : 'کارشناس در شیفت';
      }
      if (secDot) secDot.className = online
        ? 'w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse shrink-0'
        : 'w-2.5 h-2.5 rounded-full bg-amber-500 shrink-0';
      if (secRoles) {
        secRoles.innerHTML = online
          ? techs.map(t => `<li class="flex items-start gap-2"><span class="text-emerald-500">●</span><span>${t.role}</span></li>`).join('')
          : `<li class="flex items-start gap-2"><span class="text-amber-500">●</span><span>در حال حاضر کارشناسی در شیفت نیست؛ درخواست شما در صف ثبت می‌شود.</span></li>`;
      }
      if (secResp) secResp.textContent = `هدف پاسخ‌گویی: تا ${target} دقیقه`;

      const launcherDot = document.getElementById('launcherPresenceDot');
      const launcherText = document.getElementById('launcherPresenceText');
      if (launcherDot && launcherText) {
        launcherText.textContent = online ? `${faNum(n)} آنلاین` : 'صف درخواست';
        launcherDot.className = online
          ? 'w-2 h-2 rounded-full bg-emerald-500 animate-pulse'
          : 'w-2 h-2 rounded-full bg-amber-500';
      }

      const drawerCount = document.getElementById('drawerPresenceCount');
      if (drawerCount) drawerCount.textContent = online ? `${faNum(n)} کارشناس آنلاین` : 'ثبت درخواست و تماس بعدی';

      const modalPresence = document.getElementById('remoteModalPresence');
      if (modalPresence) {
        modalPresence.textContent = online
          ? `${faNum(n)} کارشناس آنلاین است — هدف پاسخ‌گویی تا ${target} دقیقه`
          : 'کارشناسان در حال تعویض شیفت‌اند — درخواستت ثبت و اولین نفر آزاد تماس می‌گیرد';
        modalPresence.className = online
          ? 'mt-2 text-[11px] font-semibold text-emerald-600 dark:text-emerald-400'
          : 'mt-2 text-[11px] font-semibold text-amber-600 dark:text-amber-400';
      }

      return { count: n, online, responseTargetMin: REMOTE_SUPPORT.responseTargetMin };
    }

    function renderIntakeHours() {
      const text = document.getElementById('intakeHoursText');
      const dot = document.getElementById('intakeHoursDot');
      if (text) text.textContent = 'پذیرش حضوری: شنبه تا چهارشنبه ۹:۳۰ تا ۱۷:۰۰';
      if (dot) dot.className = isIntakeOpenNow()
        ? 'w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse'
        : 'w-1.5 h-1.5 rounded-full bg-neutral-400';
    }

    function initShopHours() {   // سازگاری با فراخوانی قبلی
      renderPresence();
      renderIntakeHours();
    }

    function unusedLegacyHoursPlaceholder() {''',
    "presence engine inserted")

# close the legacy function body (old initShopHours body now belongs to the placeholder)
sub('''    function unusedLegacyHoursPlaceholder() {
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
    }''',
    '''    function unusedLegacyHoursPlaceholder() { /* حذف شد — جای آن را renderPresence گرفته است */ }''',
    "legacy hours body removed")

# remote modal open/close/submit
sub('''    function openRemoteModal() {
      playHapticSound('click');
      const modal = document.getElementById("remoteModal");
      if (!modal) return;
      modal.classList.remove("hidden");
      modal.classList.add("grid");
      lockBodyScroll();
    }''',
    '''    function openRemoteModal() {
      playHapticSound('click');
      const modal = document.getElementById("remoteModal");
      if (!modal) return;
      const formView = document.getElementById("remoteFormView");
      const successView = document.getElementById("remoteSuccessView");
      if (formView) formView.classList.remove("hidden");
      if (successView) successView.classList.add("hidden");
      renderPresence();
      modal.classList.remove("hidden");
      modal.classList.add("grid");
      lockBodyScroll();
    }''',
    "openRemoteModal")

sub('''    function handleRemoteSubmit(e) {
      e.preventDefault();
      closeRemoteModal();
      showToast("درخواست ثبت شد. کارشناس کشیک تا ۵ دقیقه دیگر تماس می‌گیرد.");
    }''',
    '''    function normalizeFaDigits(str) {
      return (str || "")
        .replace(/[۰-۹]/g, d => "۰۱۲۳۴۵۶۷۸۹".indexOf(d))
        .replace(/[٠-٩]/g, d => "٠١٢٣٤٥٦٧٨٩".indexOf(d));
    }

    function handleRemoteSubmit(e) {
      e.preventDefault();

      const nameEl = document.getElementById("remoteNameInput");
      const phoneEl = document.getElementById("remotePhoneInput");
      const osEl = document.getElementById("remoteOsSelect");
      const catEl = document.getElementById("remoteCategorySelect");
      const toolEl = document.getElementById("remoteToolSelect");
      const problemEl = document.getElementById("remoteProblemInput");
      const channelEl = document.getElementById("remoteChannelSelect");
      const consentEl = document.getElementById("remoteConsentCheck");

      const clientName = (nameEl && nameEl.value.trim()) || "کاربر گرامی";
      const phone = normalizeFaDigits(phoneEl ? phoneEl.value.trim() : "");
      const osLabel = osEl ? osEl.value : "نامشخص";
      const category = catEl ? catEl.value : "سایر";
      const tool = toolEl ? toolEl.value : "نامشخص";
      const problem = (problemEl && problemEl.value.trim()) || "بدون شرح تکمیلی";
      const channel = channelEl ? channelEl.value : "تماس تلفنی";

      if (!/^09[0-9]{9}$/.test(phone)) {
        showToast("لطفاً شماره موبایل معتبر ۱۱ رقمی وارد فرمایید (مثال: ۰۹۱۲۳۴۵۶۷۸۹).");
        if (phoneEl) phoneEl.focus();
        return;
      }
      if (!consentEl || !consentEl.checked) {
        showToast("برای اتصال ریموت، تیک اجازهٔ اتصال لازم است.");
        return;
      }

      const code = "RM-1405-" + Math.floor(100 + Math.random() * 900);
      const presence = renderPresence();

      try {
        const tickets = JSON.parse(localStorage.getItem("poshtiban_tickets") || "{}");
        tickets[code] = {
          type: "remote",
          device: `${osLabel} — پشتیبانی ریموت`,
          client: clientName,
          phone: phone,
          services: ["remote"],
          tool: tool,
          category: category,
          channel: channel,
          problem: problem,
          status: presence.online ? "کارشناس آنلاین — در انتظار تماس" : "در صف انتظار شیفت بعدی",
          step: 1,
          notes: presence.online
            ? `درخواست ریموت (${category}) ثبت شد. کارشناس آنلاین از طریق ${channel} با شما تماس می‌گیرد و جلسه با ${tool} برگزار می‌شود.`
            : `درخواست ریموت (${category}) در صف ثبت شد. در حال حاضر کارشناسی در شیفت نیست؛ اولین کارشناس آزاد از طریق ${channel} تماس می‌گیرد.`
        };
        localStorage.setItem("poshtiban_tickets", JSON.stringify(tickets));
      } catch (err) {}

      const codeEl = document.getElementById("remoteSuccessCode");
      const nextEl = document.getElementById("remoteSuccessNext");
      const handoffEl = document.getElementById("remoteSuccessHandoff");
      if (codeEl) codeEl.textContent = code;

      if (nextEl) {
        nextEl.textContent = presence.online
          ? `الآن ${faNum(presence.count)} کارشناس آنلاین است. تماس با شمارهٔ ${phone} تا حدود ${faNum(presence.responseTargetMin)} دقیقه دیگر گرفته می‌شود. ابزار اتصال: ${tool}.`
          : `در حال حاضر کارشناس آنلاین نیست (پوشش شیفتی ۲۴ ساعته). درخواستت در صف ثبت شد و اولین کارشناس آزاد با شمارهٔ ${phone} تماس می‌گیرد. کد پیگیری را نگه دار.`;
      }

      if (handoffEl) {
        const summary = `درخواست پشتیبانی ریموت ${code}%0Aنام: ${encodeURIComponent(clientName)}%0Aموبایل: ${phone}%0Aسیستم: ${encodeURIComponent(osLabel)}%0Aمشکل: ${encodeURIComponent(category)} — ${encodeURIComponent(problem)}%0Aابزار: ${encodeURIComponent(tool)}`;
        let html = "";
        if (SITE_CONTACT.whatsapp) {
          html += `<a href="https://wa.me/${SITE_CONTACT.whatsapp}?text=${summary}" target="_blank" rel="noopener noreferrer" class="px-3.5 py-2 rounded-full bg-green-500/10 text-green-600 dark:text-green-400 text-[11px] font-bold hover:bg-green-500/20 transition">ارسال همین درخواست در واتساپ</a>`;
        }
        if (SITE_CONTACT.telegram) {
          html += `<a href="https://t.me/${SITE_CONTACT.telegram}" target="_blank" rel="noopener noreferrer" class="px-3.5 py-2 rounded-full bg-sky-500/10 text-sky-600 dark:text-sky-400 text-[11px] font-bold hover:bg-sky-500/20 transition">ادامه در تلگرام</a>`;
        }
        handoffEl.innerHTML = html;
      }

      const formView = document.getElementById("remoteFormView");
      const successView = document.getElementById("remoteSuccessView");
      if (formView) formView.classList.add("hidden");
      if (successView) successView.classList.remove("hidden");
      playHapticSound("success");
    }''',
    "handleRemoteSubmit")

sub('''      initShopHours();
      runBottleneckSimulation();''',
    '''      initShopHours();
      renderPresence();
      setInterval(renderPresence, 60000);   // وضعیت آنلاین هر دقیقه تازه می‌شود
      runBottleneckSimulation();''',
    "DOMContentLoaded presence init")

io.open(PATH, "w", encoding="utf-8").write(s)
print(f"\nDone — {len(s)} chars written to {PATH}")
