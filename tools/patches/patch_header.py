"""Header fix — the bar was up to 290 px wider than its own container.

Run:  python3 tools/patches/patch_header.py        (idempotent, marker: ROUND-2-HEADER)

What was wrong (measured with tools/shots/probe_header.py):
  * the bar is `max-w-6xl` → only ~1104 px of content box, but the items summed to
    ~1346 px, so from 1024 px up to 1920 px «درخواست پشتیبانی ریموت» and «رزرو حضوری»
    were pushed outside the viewport (negative x) and the pill was cut in half;
  * on phones the bar overflowed by 7 px (390), 37 px (360), 77 px (320) — the menu
    button itself was the clipped item;
  * the status pill printed the count («۱ آنلاین») *and* the whole sentence at xl
    («۱ کارشناس آنلاین — هدف پاسخ تا ۱۵ دقیقه») — a 224 px duplicate.

The fix:
  1. one flexible middle (nav) + a shrink-proof action group, so the CTA can never be
     pushed off-screen again; every tier is sized against the 1104 px budget
  2. compact status pill everywhere (dot + «۱ آنلاین»); the full sentence lives in the
     control's title/aria-label (and in the remote panel)
  3. tiered visibility: AI action ≥1280 (nav carries it from 1024, drawer below that),
     theme toggle ≥640 (it is in the drawer on phones), tracking ≥640, booking ≥1280
  4. the desktop nav drops «تست سرعت SSD» (still in the hero cards, drawer and footer);
     brand wordmark goes icon-only under 380 px
"""
import io
import sys

P = "/home/user/پشتیبان_رایانه.html"
src = io.open(P, encoding="utf-8").read()

if "ROUND-2-HEADER" in src:
    sys.exit("already applied — ROUND-2-HEADER marker found, nothing written")

ok = []


def sub(old, new, label):
    global src
    if old not in src:
        sys.exit(f"ANCHOR NOT FOUND [{label}]:\n{old[:420]}")
    src = src.replace(old, new, 1)
    ok.append(label)


# ---------------------------------------------------------------- 1. bar shell
sub('<div class="max-w-6xl mx-auto px-3 sm:px-6 h-12 flex items-center justify-between gap-2 sm:gap-4">',
    '<div class="max-w-6xl mx-auto px-2.5 sm:px-6 h-12 flex flex-nowrap items-center justify-between gap-1 sm:gap-2 lg:gap-3">',
    "1) bar: nowrap + width budget (px-2.5 / gap-1 on phones)")

# brand wordmark: icon-only below 380 px, where the row cannot hold both it and the CTA
sub('<span class="font-bold text-xs sm:text-sm whitespace-nowrap">پشتیبان پی‌سی</span>',
    '<span class="font-bold text-xs sm:text-sm whitespace-nowrap hidden min-[380px]:inline">پشتیبان پی‌سی</span>',
    "2) brand: wordmark hidden under 380 px")

# ------------------------------------------------------------------- 2. the nav
sub('<nav class="hidden lg:flex items-center gap-6 xl:gap-8 text-[12px] text-brand-dark/80 dark:text-white/80 font-medium shrink-0">',
    '<nav class="hidden lg:flex flex-1 min-w-0 items-center justify-center gap-x-4 xl:gap-x-5 text-[12px] text-brand-dark/80 dark:text-white/80 font-medium overflow-hidden">',
    "3) nav: flexible middle zone that absorbs/absorbs-out overflow")
sub('        <a href="#speed-booster" class="hover:text-brand-blue transition-colors whitespace-nowrap">تست سرعت SSD</a>\n',
    '',
    "3) nav: «تست سرعت SSD» left the bar (kept in hero cards, drawer, footer)")

# --------------------------------------------------------------- 3. action group
sub('<div class="flex items-center gap-1.5 sm:gap-2 shrink-0">',
    '<div class="flex items-center gap-1 sm:gap-1.5 xl:gap-2 shrink-0">',
    "4) actions: tighter gaps, still shrink-proof")
sub('<button onclick="toggleAiDrawer(true)" class="hidden md:flex items-center gap-1 px-3 py-1 rounded-full text-[11px]',
    '<button onclick="toggleAiDrawer(true)" class="hidden xl:flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px]',
    "4) AI action: visible ≥1280 (nav carries AI-first from 1024, drawer below)")

# status pill: compact count, no duplicated sentence
sub('<span id="shopHoursStatusText" class="xl:hidden whitespace-nowrap">آنلاین</span>\n'
    '          <span id="shopHoursStatusTextLong" class="hidden xl:inline whitespace-nowrap">کارشناس آنلاین</span>',
    '<span id="shopHoursStatusText" class="whitespace-nowrap">آنلاین</span>',
    "5) status pill: single compact count (full sentence moves to title/aria-label)")
sub('<button type="button" onclick="openRemoteModal()" id="liveWorkStatusBadge" class="flex items-center gap-1.5 px-2 py-1 sm:px-2.5 rounded-full',
    '<button type="button" onclick="openRemoteModal()" id="liveWorkStatusBadge" class="flex items-center gap-1.5 px-1.5 py-1 sm:px-2.5 rounded-full',
    "5) status pill: narrower padding on phones")
sub('''      const badge = document.getElementById('liveWorkStatusBadge');
      const badgeText = document.getElementById('shopHoursStatusText');
      const badgeLong = document.getElementById('shopHoursStatusTextLong');
      const badgeDot = document.getElementById('shopHoursStatusDot');''',
    '''      const badge = document.getElementById('liveWorkStatusBadge');
      const badgeText = document.getElementById('shopHoursStatusText');
      const badgeDot = document.getElementById('shopHoursStatusDot');''',
    "5) JS: long-pill writer removed")
sub('''        badgeText.textContent = online ? `${faNum(n)} آنلاین` : 'در صف';
        if (badgeLong) badgeLong.textContent = longText;''',
    '''        badgeText.textContent = online ? `${faNum(n)} آنلاین` : 'در صف';''',
    "5) JS: pill writes only the count")

# theme toggle leaves the phone row (the drawer already has «تغییر به تم تیره»)
sub('<button id="themeToggleBtn" onclick="toggleTheme()" aria-label="تغییر تم" class="w-7 h-7 rounded-full',
    '<button id="themeToggleBtn" onclick="toggleTheme()" aria-label="تغییر تم" class="hidden sm:flex w-7 h-7 rounded-full',
    "6) theme toggle: ≥640 px (still in the mobile drawer)")
sub('<button onclick="openBookingModal()" class="hidden md:inline-flex text-[11px] font-semibold px-3 py-1 rounded-full',
    '<button onclick="openBookingModal()" class="hidden xl:inline-flex text-[11px] font-semibold px-3 py-1 rounded-full',
    "7) «رزرو حضوری»: ≥1280 px (hero box, drawer, remote section and AI drawer keep it)")

# ---------------------------------------------------------------- marker + note
sub('<!-- ROUND-2 (shop feedback:',
    '''<!-- ROUND-2-HEADER: bar re-cut to a 1104px budget — flexible nav + shrink-proof actions,
     compact count pill, tiered visibility (AI ≥1280, theme ≥640, tracking ≥640, booking ≥1280),
     brand wordmark icon-only under 380px. Verified by tools/shots/probe_header.py across 15 widths. -->
<!-- ROUND-2 (shop feedback:''',
    "marker")

io.open(P, "w", encoding="utf-8").write(src)
for label in ok:
    print(f"  ✓ {label}")
print(f"\nDone — {len(src)} chars written.")
