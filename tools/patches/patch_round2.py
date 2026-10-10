"""Round 2 — the shop's list from the annotated screenshots (image-1: hero/header, image-2: modal).

Run:  python3 tools/patches/patch_round2.py        (idempotent, marker: ROUND-2)

  1. hero H1: drop the «،» and the closing «.»
  2. remove the «آنلاین» chip in the hero kicker; the header pill now shows how many
     technicians are online («۳ آنلاین» / «در صف»)
  3. the two «پشتیبانی ریموت» labels are told apart: the nav one loses its green dot,
     the header action becomes «درخواست پشتیبانی ریموت»
  4. AI first in every aspect: nav order, hero CTA order + primary colour, floating
     launcher, mobile drawer, footer links, FAQ order, section order, header AI button,
     <title>/og/twitter/JSON-LD wording (an AI Service node goes in front of the remote one)
  5. the crossed line «۱ کارشناس آنلاین — هدف پاسخ تا ۱۵ دقیقه» is gone from the hero
     (its information now lives in the header pill)
  6. in-person intake starts at 10:00, not 09:30 — everywhere (engine, JSON-LD, copy, modal)
  7. the two remaining hero status lines become coloured boxes (amber = intake,
     emerald = remote hours) with an icon, a label and a value
  8. the remote form's native <select>s become the same custom dropdown component as the
     «تست گلوگاه و بازدهی قطعات» section (toggleModalDropdown/selectModalDropdownOption)
"""
import io
import re
import sys

P = "/home/user/پشتیبان_رایانه.html"
src = io.open(P, encoding="utf-8").read()

if "ROUND-2" in src:
    sys.exit("already applied — ROUND-2 marker found, nothing written")

ok = []


def sub(old, new, label, count=1):
    global src
    if old not in src:
        sys.exit(f"ANCHOR NOT FOUND [{label}]:\n{old[:400]}")
    src = src.replace(old, new, count)
    ok.append(label)


# ------------------------------------------------------------------ 1. H1 punctuation
sub('<span class="inline-block">هر ساعت شبانه‌روز،</span>',
    '<span class="inline-block">هر ساعت شبانه‌روز</span>',
    "1) H1: comma removed")
sub('        کارشناس آنلاین داری.\n',
    '        کارشناس آنلاین داری\n',
    "1) H1: full stop removed")

# ---------------------------------------------------- 2. kicker chip out, AI worded first
sub('''    <div class="inline-flex items-center gap-2 mb-6 p-1.5 pr-3.5 pl-2 rounded-full bg-brand-lightGray dark:bg-brand-darkCard border border-black/[0.08] dark:border-white/[0.08] shadow-sm">
      <span class="text-[11px] font-bold ai-gradient-text">پشتیبانی ریموت شبانه‌روزی + موتور هوش مصنوعی آنبرد</span>
      <span class="px-2 py-0.5 rounded-full bg-emerald-500 text-white text-[9px] font-bold" id="heroPresenceChip">آنلاین</span>
    </div>''',
    '''    <div class="inline-flex items-center gap-2 mb-6 px-3.5 py-1.5 rounded-full bg-brand-lightGray dark:bg-brand-darkCard border border-black/[0.08] dark:border-white/[0.08] shadow-sm">
      <span class="text-[11px] font-bold ai-gradient-text">موتور هوش مصنوعی آنبرد + پشتیبانی ریموت شبانه‌روزی</span>
    </div>''',
    "2) hero kicker: «آنلاین» chip removed, AI worded first")

# ------------------------------------------------------------- 3+4. header nav: AI first
sub('''        <a href="#remote-support" class="hover:text-brand-blue transition-colors whitespace-nowrap flex items-center gap-1.5">
          <span class="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span><span>پشتیبانی ریموت</span>
        </a>
        <a href="#ai-diagnostic" class="ai-gradient-text font-bold hover:opacity-80 transition-opacity flex items-center gap-1.5 whitespace-nowrap">
          <span>✦</span><span>عیب‌یاب هوشمند</span>
        </a>''',
    '''        <a href="#ai-diagnostic" class="ai-gradient-text font-bold hover:opacity-80 transition-opacity flex items-center gap-1.5 whitespace-nowrap">
          <span>✦</span><span>عیب‌یاب هوشمند</span>
        </a>
        <a href="#remote-support" class="hover:text-brand-blue transition-colors whitespace-nowrap">پشتیبانی ریموت</a>''',
    "3+4) nav: AI first, remote link loses its green dot")

# header AI button: visible from md, moved to the front of the actions group
sub('''        <!-- AI Assistant Direct Trigger -->
        <button onclick="toggleAiDrawer(true)" class="hidden 2xl:flex items-center gap-1 px-3 py-1 rounded-full text-[11px] font-semibold bg-gradient-to-r from-purple-500/10 to-blue-500/10 text-purple-600 dark:text-purple-400 border border-purple-500/20 hover:border-purple-500/40 transition shrink-0 whitespace-nowrap">
          <span>✦ مشاور فنی</span>
        </button>

''', '', "4) header AI button lifted out of its old slot")
sub('''      <div class="flex items-center gap-1.5 sm:gap-2 shrink-0">
        <!-- Live remote-support presence (never faked — driven by REMOTE_SUPPORT shifts) -->''',
    '''      <div class="flex items-center gap-1.5 sm:gap-2 shrink-0">
        <!-- AI Assistant Direct Trigger — first action, and no longer desktop-only -->
        <button onclick="toggleAiDrawer(true)" class="hidden md:flex items-center gap-1 px-3 py-1 rounded-full text-[11px] font-semibold bg-gradient-to-r from-purple-500/10 to-blue-500/10 text-purple-600 dark:text-purple-400 border border-purple-500/20 hover:border-purple-500/40 transition shrink-0 whitespace-nowrap">
          <span>✦ مشاور هوشمند</span>
        </button>

        <!-- Live remote-support presence (never faked — driven by REMOTE_SUPPORT shifts) -->''',
    "4) header AI button now first in the actions row (md+)")

sub('''          <span class="w-1.5 h-1.5 rounded-full bg-white/90 animate-pulse"></span>
          <span>پشتیبانی ریموت</span>''',
    '''          <span class="w-1.5 h-1.5 rounded-full bg-white/90 animate-pulse"></span>
          <span>درخواست پشتیبانی ریموت</span>''',
    "3) header action renamed to «درخواست پشتیبانی ریموت»")

# ------------------------------------------------------------------- 4+7. hero CTAs + strip
sub('''    <!-- Hero Action Buttons -->
    <div class="mt-8 sm:mt-10 flex flex-wrap items-center justify-center gap-3">
      <button onclick="openRemoteModal()" class="px-6 py-3 rounded-full bg-brand-blue hover:bg-brand-blueHover text-white text-xs sm:text-sm font-semibold shadow-lg shadow-brand-blue/20 transition transform active:scale-95 flex items-center gap-2">
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
    '''    <!-- Hero Action Buttons — AI first: diagnose, then decide between remote and in-person -->
    <div class="mt-8 sm:mt-10 flex flex-wrap items-center justify-center gap-3">
      <a href="#ai-diagnostic" class="px-6 py-3 rounded-full bg-brand-blue hover:bg-brand-blueHover text-white text-xs sm:text-sm font-semibold shadow-lg shadow-brand-blue/20 transition transform active:scale-95 flex items-center gap-2">
        <span class="text-sm leading-none" aria-hidden="true">✦</span>
        <span>عیب‌یابی رایگان سیستم</span>
      </a>
      <button onclick="toggleAiDrawer(true)" class="px-6 py-3 rounded-full bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white text-xs sm:text-sm font-semibold shadow-lg shadow-purple-500/20 transition transform active:scale-95 flex items-center gap-2">
        <span>مشاور هوشمند فنی</span>
        <span class="text-xs">✦</span>
      </button>
      <button onclick="openRemoteModal()" class="px-5 py-3 rounded-full bg-white dark:bg-brand-darkCard hover:bg-brand-blue/5 dark:hover:bg-white/5 text-brand-blue text-xs sm:text-sm font-semibold transition border border-brand-blue/25 dark:border-brand-blue/40 flex items-center gap-2">
        <span class="w-2 h-2 rounded-full bg-brand-blue/80 animate-pulse"></span>
        <span>درخواست پشتیبانی ریموت</span>
      </button>
    </div>

    <!-- Policy strip: intake hours (workshop) + remote coverage. The lived «how many are
         online right now» line moved to the header pill (item 2), so it is not repeated here. -->
    <div class="mt-8 flex flex-wrap items-stretch justify-center gap-3">
      <div class="inline-flex items-center gap-2.5 px-4 py-2.5 rounded-2xl bg-amber-500/10 border border-amber-500/25 shadow-sm">
        <svg class="w-4 h-4 shrink-0 text-amber-600 dark:text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <rect x="3" y="4.5" width="18" height="16" rx="2.5"></rect>
          <path d="M3 9.5h18M8 3v3M16 3v3"></path>
        </svg>
        <span class="text-right">
          <span class="block text-[10px] font-bold text-amber-700 dark:text-amber-300">پذیرش حضوری در کارگاه</span>
          <span class="block text-[11px] font-semibold text-amber-800/90 dark:text-amber-200/90" id="intakeHoursText">شنبه تا چهارشنبه، ۱۰:۰۰ تا ۱۷:۰۰</span>
        </span>
        <span id="intakeHoursDot" class="w-1.5 h-1.5 rounded-full bg-neutral-400 shrink-0"></span>
      </div>
      <div class="inline-flex items-center gap-2.5 px-4 py-2.5 rounded-2xl bg-emerald-500/10 border border-emerald-500/25 shadow-sm">
        <svg class="w-4 h-4 shrink-0 text-emerald-600 dark:text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <circle cx="12" cy="12" r="9"></circle>
          <path d="M12 7v5l3.5 2"></path>
        </svg>
        <span class="text-right">
          <span class="block text-[10px] font-bold text-emerald-700 dark:text-emerald-300">پاسخ‌گویی ریموت و تلفنی</span>
          <span class="block text-[11px] font-semibold text-emerald-800/90 dark:text-emerald-200/90">شبانه‌روزی، همهٔ روزهای هفته</span>
        </span>
      </div>
    </div>''',
    "4+5+7) hero CTAs AI-first; presence line deleted; intake+remote become coloured boxes")

# --------------------------------------------------------- 4. launcher: AI assistant again
sub('''    <button onclick="openRemoteModal()" id="aiFloatingLauncherBtn" title="درخواست پشتیبانی ریموت" class="group flex items-center gap-2 p-2.5 rounded-full bg-brand-dark dark:bg-white text-white dark:text-brand-dark shadow-2xl hover:scale-105 active:scale-95 transition-all duration-200 border border-white/20 dark:border-black/20 ai-glow">
      <span id="launcherPresenceDot" class="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse shrink-0"></span>
      <svg class="w-4 h-4 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
        <path d="M3 15v-3a9 9 0 0 1 18 0v3"></path>
        <path d="M21 16.5a2.5 2.5 0 0 1-2.5 2.5H17v-5h1.5A2.5 2.5 0 0 1 21 16.5z"></path>
        <path d="M3 16.5A2.5 2.5 0 0 0 5.5 19H7v-5H5.5A2.5 2.5 0 0 0 3 16.5z"></path>
      </svg>
      <span class="text-[11px] sm:text-xs font-bold whitespace-nowrap launcher-wide-only">پشتیبانی ریموت</span>
      <span id="launcherPresenceText" class="text-[10px] px-2 py-0.5 rounded-full bg-white/15 dark:bg-black/10 shrink-0 whitespace-nowrap">آنلاین</span>
    </button>''',
    '''    <button onclick="toggleAiDrawer(true)" id="aiFloatingLauncherBtn" title="مشاور هوشمند فنی" aria-label="مشاور هوشمند فنی پشتیبان پی‌سی" class="group flex items-center gap-2 p-2.5 rounded-full bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white shadow-2xl hover:scale-105 active:scale-95 transition-all duration-200 border border-white/20 ai-glow">
      <span class="text-base leading-none shrink-0" aria-hidden="true">✦</span>
      <span class="text-[11px] sm:text-xs font-bold whitespace-nowrap launcher-wide-only">مشاور هوشمند فنی</span>
      <span class="launcher-ai-chip text-[10px] px-2 py-0.5 rounded-full bg-white/15 shrink-0">AI</span>
    </button>''',
    "4) floating launcher is the AI assistant again")

sub('''  <!-- Floating remote-support launcher.''',
    '''  <!-- Floating AI-assistant launcher (item 4: the AI is the first thing to reach for).''',
    "4) launcher comment updated")

# ------------------------------------------------------------------- 4. mobile drawer order
sub('''    <a href="#remote-support" onclick="toggleMobileMenu()" class="flex items-center gap-2 py-1.5 font-bold text-emerald-600 dark:text-emerald-400">
      <span class="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span><span id="drawerPresenceLine">پشتیبانی ریموت شبانه‌روزی</span>
    </a>
    <a href="#ai-diagnostic" onclick="toggleMobileMenu()" class="block py-1.5 ai-gradient-text font-bold">✦ عیب‌یاب هوشمند سیستم</a>''',
    '''    <a href="#ai-diagnostic" onclick="toggleMobileMenu()" class="block py-1.5 ai-gradient-text font-bold">✦ عیب‌یاب هوشمند سیستم</a>
    <a href="#remote-support" onclick="toggleMobileMenu()" class="flex items-center gap-2 py-1.5 font-bold text-emerald-600 dark:text-emerald-400">
      <span class="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span><span id="drawerPresenceLine">پشتیبانی ریموت شبانه‌روزی</span>
    </a>''',
    "4) drawer: AI link first")

sub('''      <button onclick="openRemoteModal(); toggleMobileMenu();" class="col-span-2 py-2.5 text-center rounded-xl bg-brand-blue text-white font-bold">
        درخواست پشتیبانی ریموت
      </button>
      <button onclick="toggleAiDrawer(true); toggleMobileMenu();" class="py-2 text-center rounded-xl bg-purple-500/10 text-purple-600 dark:text-purple-400 font-bold">
        ✦ مشاور هوشمند
      </button>''',
    '''      <button onclick="toggleAiDrawer(true); toggleMobileMenu();" class="col-span-2 py-2.5 text-center rounded-xl bg-brand-blue text-white font-bold">
        ✦ مشاور هوشمند فنی
      </button>
      <button onclick="openRemoteModal(); toggleMobileMenu();" class="col-span-2 py-2 text-center rounded-xl bg-purple-500/10 text-purple-600 dark:text-purple-400 font-bold">
        درخواست پشتیبانی ریموت
      </button>''',
    "4) drawer: AI action is the primary button")

# --------------------------------------------------------------------- 4. footer link order
sub('''        <a href="#remote-support" class="hover:text-brand-dark dark:hover:text-white transition">پشتیبانی ریموت</a>
        <a href="#ai-diagnostic" class="hover:text-brand-dark dark:hover:text-white transition">عیب‌یاب هوشمند</a>''',
    '''        <a href="#ai-diagnostic" class="hover:text-brand-dark dark:hover:text-white transition">عیب‌یاب هوشمند</a>
        <a href="#remote-support" class="hover:text-brand-dark dark:hover:text-white transition">پشتیبانی ریموت</a>''',
    "4) footer: AI link first")

# ------------------------------------------------------------------------ 6. 09:30 → 10:00
sub('{ from: 9.5, to: 17 }', '{ from: 10, to: 17 }', "6) SHOP_HOURS.intake.from = 10")
sub('{ from: 9.5, to: 20.5 }', '{ from: 10, to: 20.5 }', "6) SHOP_HOURS.support.from = 10")
sub('''            "opens": "09:30",
            "closes": "17:00",''',
    '''            "opens": "10:00",
            "closes": "17:00",''',
    "6) JSON-LD opening hours")
sub('''      if (text) text.textContent = 'پذیرش حضوری: شنبه تا چهارشنبه ۹:۳۰ تا ۱۷:۰۰';''',
    '''      if (text) text.textContent = 'شنبه تا چهارشنبه، ۱۰:۰۰ تا ۱۷:۰۰';''',
    "6) renderIntakeHours text")
sub('''پذیرش حضوری کارگاه (شنبه تا چهارشنبه ۹:۳۰ تا ۱۷:۰۰) در دسترس است.''',
    '''پذیرش حضوری کارگاه (شنبه تا چهارشنبه ۱۰:۰۰ تا ۱۷:۰۰) در دسترس است.''',
    "6) remote-modal copy")

# --------------------------------------------------- 4. meta / JSON-LD: AI worded first
sub('''<title>پشتیبان پی‌سی | پشتیبانی ریموت شبانه‌روزی و عیب‌یابی هوشمند رایانه</title>''',
    '''<title>پشتیبان پی‌سی | عیب‌یابی هوشمند رایانه و پشتیبانی ریموت شبانه‌روزی</title>''',
    "4) <title> AI first")
sub('''content="پشتیبانی ریموت شبانه‌روزی برای ویندوز، مک و لینوکس؛ اتصال امن از راه دور، عیب‌یابی هوشمند با هوش مصنوعی، و کارگاه تخصصی سخت‌افزار در تهران"''',
    '''content="عیب‌یابی هوشمند رایانه با هوش مصنوعی، پشتیبانی ریموت شبانه‌روزی برای ویندوز، مک و لینوکس و کارگاه تخصصی سخت‌افزار در تهران"''',
    "4) og:description AI first")
sub('''content="پشتیبانی ریموت شبانه‌روزی، تحلیل هوشمند خطاهای صفحه آبی و ارتقای پرسرعت SSD"''',
    '''content="تحلیل هوشمند خطاهای صفحه آبی، پشتیبانی ریموت شبانه‌روزی و ارتقای پرسرعت SSD"''',
    "4) twitter:description AI first")
sub('''        "description": "پشتیبانی ریموت شبانه‌روزی (شیفتی) برای ویندوز، مک و لینوکس؛ عیب‌یابی هوشمند با هوش مصنوعی و کارگاه تخصصی تعمیر و ارتقای سخت‌افزار در تهران",''',
    '''        "description": "عیب‌یابی هوشمند با هوش مصنوعی؛ پشتیبانی ریموت شبانه‌روزی (شیفتی) برای ویندوز، مک و لینوکس و کارگاه تخصصی تعمیر و ارتقای سخت‌افزار در تهران",''',
    "4) JSON-LD store description AI first")
sub('''      {
        "@type": "Service",
        "@id": "https://poshtibanpc.ir/#remote-support",''',
    '''      {
        "@type": "Service",
        "@id": "https://poshtibanpc.ir/#ai-diagnostic",
        "name": "عیب‌یابی هوشمند رایانه با هوش مصنوعی",
        "description": "تحلیل متنی و تصویری خطاهای ویندوز و سخت‌افزار با موتور هوش مصنوعی آنبرد؛ تشخیص اولیهٔ عیب پیش از درخواست پشتیبانی ریموت یا تحویل دستگاه به کارگاه.",
        "serviceType": "AI diagnostics",
        "availableChannel": {
          "@type": "ServiceChannel",
          "serviceUrl": "https://poshtibanpc.ir/#ai-diagnostic",
          "availableLanguage": ["fa"]
        },
        "provider": { "@id": "https://poshtibanpc.ir/#store" }
      },
      {
        "@type": "Service",
        "@id": "https://poshtibanpc.ir/#remote-support",''',
    "4) JSON-LD: AI Service node before the remote one")

# ------------------------------------------------------- 2. header pill shows the count
sub('''        const longText = online
          ? `${faNum(n)} کارشناس آنلاین — هدف پاسخ تا ${target} دقیقه`
          : 'درخواست‌ها در صف — اولین کارشناس تماس می‌گیرد';
        badgeText.textContent = online ? 'آنلاین' : 'در صف';''',
    '''        const longText = online
          ? `${faNum(n)} کارشناس آنلاین — هدف پاسخ تا ${target} دقیقه`
          : 'درخواست‌ها در صف — اولین کارشناس تماس می‌گیرد';
        // item 2: the header pill carries how many technicians are online right now
        badgeText.textContent = online ? `${faNum(n)} آنلاین` : 'در صف';''',
    "2) header pill: online count")

# ------------------------------------- 2+5: drop the hero chip / presence-line JS writers
sub('''      const chip = document.getElementById('heroPresenceChip');
      if (chip) {
        chip.textContent = online ? `${faNum(n)} آنلاین` : 'صف درخواست';
        chip.className = online
          ? 'px-2 py-0.5 rounded-full bg-emerald-500 text-white text-[9px] font-bold'
          : 'px-2 py-0.5 rounded-full bg-amber-500 text-white text-[9px] font-bold';
      }

''', '', "2) hero kicker chip JS removed")
sub('''      const heroDot = document.getElementById('heroPresenceDot');
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

''', '', "5) hero presence line JS removed")
sub('''      const launcherDot = document.getElementById('launcherPresenceDot');
      const launcherText = document.getElementById('launcherPresenceText');
      const launcherBtn = document.getElementById('aiFloatingLauncherBtn');
      if (launcherDot && launcherText) {
        // the dot carries the count, the chip stays one short word (no more «ریموت ۱ آنلاین» jam)
        launcherText.textContent = online ? 'آنلاین' : 'در صف';
        launcherDot.className = online
          ? 'w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse shrink-0'
          : 'w-2.5 h-2.5 rounded-full bg-amber-500 shrink-0';
      }
      if (launcherBtn) {
        const summary = online
          ? `${faNum(n)} کارشناس آنلاین — هدف پاسخ تا ${target} دقیقه`
          : 'همهٔ کارشناسان در تعویض شیفت‌اند — درخواست بگذار، اولین نفر آزاد تماس می‌گیرد';
        launcherBtn.setAttribute('aria-label', `پشتیبانی ریموت شبانه‌روزی: ${summary}`);
        launcherBtn.setAttribute('title', `پشتیبانی ریموت — ${summary}`);
      }

''', '', "4) launcher presence writers removed (it is the AI button now)")

# --------------------------------------------------------------------- 4. FAQ: AI first
markers = [(int(mm.group(1)), mm.start()) for mm in re.finditer(r'<!-- FAQ Item (\d)[^>]*-->', src)]
markers.sort(key=lambda t: t[1])
assert len(markers) == 6, f"expected 6 FAQ items, found {len(markers)}"
faq_start = markers[0][1]
blocks = {}
for idx, (num, pos) in enumerate(markers):
    end = markers[idx + 1][1] if idx + 1 < len(markers) else None
    if end is not None:
        blocks[num] = src[pos:end]
    else:
        last = src[pos:]
        tail_marker = last.index('</div>\n      </div>')
        cut = tail_marker + len('</div>\n')
        blocks[num] = last[:cut]
        remainder = last[cut:]
assert set(blocks) == {1, 2, 3, 4, 5, 6}, f"FAQ items found: {sorted(blocks)}"

order = [3, 1, 2, 4, 5, 6]      # the AI question (was #3) goes first
new_list = ""
for new_i, old_i in zip(range(1, 7), order):
    b = blocks[old_i]
    b = b.replace(f'<!-- FAQ Item {old_i} -->', f'<!-- FAQ Item {new_i} -->')
    b = b.replace(f'faqAnswer{old_i}', f'faqAnswer{new_i}')
    new_list += b
src = src[:faq_start] + new_list + remainder
ok.append("4) FAQ: AI question moved first (ids follow DOM order)")

# ----------------------------------------------------------------- 4. section order swap
def section_block(sid):
    global src
    start = src.index(f'<section id="{sid}"')
    depth = 0
    i = start
    while True:
        nxt_open = src.find('<section', i + 1)
        nxt_close = src.find('</section>', i + 1)
        if nxt_close == -1:
            raise SystemExit(f"unbalanced <section> for {sid}")
        if nxt_open != -1 and nxt_open < nxt_close:
            depth += 1
            i = nxt_open
        else:
            if depth == 0:
                end = nxt_close + len('</section>')
                return src[start:end]
            depth -= 1
            i = nxt_close

remote_block = section_block("remote-support")
ai_block = section_block("ai-diagnostic")
# place the AI section first, then the remote one, keeping surrounding whitespace sane
src = src.replace(remote_block, "@@REMOTE_BLOCK@@", 1)
src = src.replace(ai_block, remote_block.rstrip() + "\n\n  ", 1)
src = src.replace("@@REMOTE_BLOCK@@", ai_block.rstrip(), 1)
ok.append("4) sections: #ai-diagnostic now comes before #remote-support")

# ---------------------------------------------------------- 8. modal custom dropdowns
def dropdown(key, label_text, options, default):
    opts = "\n".join(
        f'''                  <button type="button" role="option" aria-selected="{'true' if o == default else 'false'}" onclick="selectModalDropdownOption('{key}', '{o}', '{o}')" class="{key}-opt w-full text-right px-3 py-2 rounded-xl text-xs text-brand-dark dark:text-white transition flex items-center justify-between {'bg-brand-blue/10 text-brand-blue font-bold' if o == default else 'hover:bg-brand-blue/10 hover:text-brand-blue'}" data-value="{o}">
                    <span>{o}</span>
                    <span class="check-icon {'text-brand-blue font-bold' if o == default else 'hidden text-brand-blue font-bold'}">{'✓' if o == default else ''}</span>
                  </button>''' for o in options)
    return f'''            <div>
              <label for="{key}-trigger" class="block text-xs font-semibold text-neutral-800 dark:text-neutral-200 mb-1.5">{label_text}</label>
              <div class="relative" id="{key}Container">
                <input type="hidden" id="{key}" value="{default}">
                <button type="button" onclick="toggleModalDropdown('{key}')" id="{key}-trigger" aria-haspopup="listbox" aria-expanded="false" aria-controls="{key}-menu" class="w-full flex items-center justify-between bg-neutral-100 dark:bg-[#252528] hover:bg-black/[0.03] dark:hover:bg-white/[0.04] border border-black/[0.08] dark:border-white/[0.08] rounded-xl px-4 py-2.5 text-xs text-brand-dark dark:text-white font-medium transition focus:outline-none focus:border-brand-blue">
                  <span id="{key}-label">{default}</span>
                  <svg id="{key}-arrow" class="w-4 h-4 text-brand-gray transition-transform duration-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
                  </svg>
                </button>
                <div id="{key}-menu" role="listbox" class="hidden absolute left-0 right-0 top-full mt-1.5 z-40 bg-white/95 dark:bg-[#1c1c1e]/95 backdrop-blur-xl border border-black/[0.08] dark:border-white/[0.1] rounded-2xl shadow-xl p-1.5 space-y-1">
{opts}
                </div>
              </div>
            </div>'''


sub('''            <div>
              <label for="remoteOsSelect" class="block text-xs font-semibold text-neutral-800 dark:text-neutral-200 mb-1.5">سیستم‌عامل</label>
              <select id="remoteOsSelect" class="w-full bg-neutral-100 dark:bg-[#252528] border border-black/[0.08] dark:border-white/[0.08] rounded-xl px-4 py-2.5 text-xs text-brand-dark dark:text-white font-medium focus:outline-none focus:border-brand-blue cursor-pointer transition">
                <option>ویندوز ۱۰ / ۱۱</option>
                <option>ویندوز ۷ / ۸</option>
                <option>مک (macOS)</option>
                <option>لینوکس</option>
                <option>سایر / نمی‌دانم</option>
              </select>
            </div>''',
    dropdown("remoteOsSelect", "سیستم‌عامل",
             ["ویندوز ۱۰ / ۱۱", "ویندوز ۷ / ۸", "مک (macOS)", "لینوکس", "سایر / نمی‌دانم"],
             "ویندوز ۱۰ / ۱۱"),
    "8) OS select → custom dropdown")

sub('''            <div>
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
            </div>''',
    dropdown("remoteCategorySelect", "نوع مشکل",
             ["ویندوز و بوت", "شبکه، اینترنت و وای‌فای", "نرم‌افزار، آفیس و ایمیل",
              "ویروس، بدافزار و امنیت", "درایور و سخت‌افزار (تشخیص از راه دور)",
              "ریکاوری و بکاپ اطلاعات", "سایر"],
             "ویندوز و بوت"),
    "8) problem-type select → custom dropdown")

sub('''            <div>
              <label for="remoteToolSelect" class="block text-xs font-semibold text-neutral-800 dark:text-neutral-200 mb-1.5">نرم‌افزار اتصال</label>
              <select id="remoteToolSelect" class="w-full bg-neutral-100 dark:bg-[#252528] border border-black/[0.08] dark:border-white/[0.08] rounded-xl px-4 py-2.5 text-xs text-brand-dark dark:text-white font-medium focus:outline-none focus:border-brand-blue cursor-pointer transition">
                <option>AnyDesk</option>
                <option>RustDesk</option>
                <option>درسان‌دسک (DorsanDesk)</option>
                <option>TeamViewer</option>
                <option>نمی‌دانم — کارشناس راهنمایی کند</option>
              </select>
            </div>''',
    dropdown("remoteToolSelect", "نرم‌افزار اتصال",
             ["AnyDesk", "RustDesk", "درسان‌دسک (DorsanDesk)", "TeamViewer",
              "نمی‌دانم — کارشناس راهنمایی کند"],
             "AnyDesk"),
    "8) connection-tool select → custom dropdown")

sub('''          <div>
            <label for="remoteChannelSelect" class="block text-xs font-semibold text-neutral-800 dark:text-neutral-200 mb-1.5">راه تماس کارشناس با شما</label>
            <select id="remoteChannelSelect" class="w-full bg-neutral-100 dark:bg-[#252528] border border-black/[0.08] dark:border-white/[0.08] rounded-xl px-4 py-2.5 text-xs text-brand-dark dark:text-white font-medium focus:outline-none focus:border-brand-blue cursor-pointer transition">
              <option>تماس تلفنی</option>
              <option>واتساپ</option>
              <option>تلگرام</option>
              <option>بله / ایتا</option>
            </select>
          </div>''',
    dropdown("remoteChannelSelect", "راه تماس کارشناس با شما",
             ["تماس تلفنی", "واتساپ", "تلگرام", "بله / ایتا"],
             "تماس تلفنی"),
    "8) contact-channel select → custom dropdown")

# the modal dropdown engine + wiring
sub('''    function toggleCustomDropdown(type) {''',
    '''    /* ROUND-2: dropdown سفارشی مودال — همان رفتار «تست گلوگاه و بازدهی قطعات»
       (toggle / select / close) ولی بدون فراخوانی شبیه‌ساز گلوگاه. */
    const MODAL_DROPDOWNS = ['remoteOsSelect', 'remoteCategorySelect', 'remoteToolSelect', 'remoteChannelSelect'];

    function toggleModalDropdown(key) {
      playHapticSound('click');
      MODAL_DROPDOWNS.forEach(k => { if (k !== key) closeModalDropdown(k); });
      const menu = document.getElementById(key + '-menu');
      const trigger = document.getElementById(key + '-trigger');
      const arrow = document.getElementById(key + '-arrow');
      if (!menu) return;
      const willOpen = menu.classList.contains('hidden');
      menu.classList.toggle('hidden', !willOpen);
      if (arrow) arrow.classList.toggle('rotate-180', willOpen);
      if (trigger) trigger.setAttribute('aria-expanded', String(willOpen));
    }

    function closeModalDropdown(key) {
      const menu = document.getElementById(key + '-menu');
      const trigger = document.getElementById(key + '-trigger');
      const arrow = document.getElementById(key + '-arrow');
      if (menu) menu.classList.add('hidden');
      if (arrow) arrow.classList.remove('rotate-180');
      if (trigger) trigger.setAttribute('aria-expanded', 'false');
    }

    function selectModalDropdownOption(key, value, label) {
      playHapticSound('click');
      const input = document.getElementById(key);
      const labelEl = document.getElementById(key + '-label');
      if (input) input.value = value;
      if (labelEl) labelEl.textContent = label;

      document.querySelectorAll('.' + key + '-opt').forEach(opt => {
        const active = opt.getAttribute('data-value') === value;
        opt.className = key + '-opt w-full text-right px-3 py-2 rounded-xl text-xs text-brand-dark dark:text-white transition flex items-center justify-between '
          + (active ? 'bg-brand-blue/10 text-brand-blue font-bold' : 'hover:bg-brand-blue/10 hover:text-brand-blue');
        opt.setAttribute('aria-selected', String(active));
        const check = opt.querySelector('.check-icon');
        if (check) check.classList.toggle('hidden', !active);
      });

      closeModalDropdown(key);
    }

    function toggleCustomDropdown(type) {''',
    "8) modal dropdown engine added")

sub('''      // Click outside to close custom dropdowns
      document.addEventListener("click", (e) => {
        ['cpu', 'ram', 'storage'].forEach(t => {
          const cap = capitalize(t);
          const container = document.getElementById(`customDrop${cap}Container`);
          if (container && !container.contains(e.target)) {
            closeCustomDropdown(t);
          }
        });
      });''',
    '''      // Click outside to close custom dropdowns (bottleneck + remote modal)
      document.addEventListener("click", (e) => {
        ['cpu', 'ram', 'storage'].forEach(t => {
          const cap = capitalize(t);
          const container = document.getElementById(`customDrop${cap}Container`);
          if (container && !container.contains(e.target)) {
            closeCustomDropdown(t);
          }
        });
        (typeof MODAL_DROPDOWNS !== 'undefined' ? MODAL_DROPDOWNS : []).forEach(key => {
          const container = document.getElementById(key + 'Container');
          if (container && !container.contains(e.target)) closeModalDropdown(key);
        });
      });''',
    "8) click-outside also closes the modal dropdowns")

# launcher AI chip style
sub('''    .launcher-wide-only { display: inline-block; vertical-align: middle; }''',
    '''    .launcher-wide-only { display: inline-block; vertical-align: middle; }
    /* «AI» فقط جایی که برچسب جمع می‌شود (≥۱۴۲۰px) دیده می‌شود تا دکمه در گاتر جا شود */
    .launcher-ai-chip { display: none; }
    @media (min-width: 1420px) { .launcher-ai-chip { display: inline; } }''',
    "4) launcher AI chip style")

# --------------------------------------------------------------------------- marker
sub('''<!-- PACKAGE-3 (mobile: launcher overlap, phone-visible hours/access, Persian letter-spacing) -->''',
    '''<!-- PACKAGE-3 (mobile: launcher overlap, phone-visible hours/access, Persian letter-spacing) -->
<!-- ROUND-2 (shop feedback: H1 punctuation, header count, «پشتیبانی ریموت» naming, AI first,
     presence line removed, intake 10:00, boxed hero status, custom dropdowns in the remote form) -->''',
    "marker")

io.open(P, "w", encoding="utf-8").write(src)
for label in ok:
    print(f"  ✓ {label}")
print(f"\nDone — {len(src)} chars written.")
