"""Package 3 — mobile fixes (F-11 launcher overlap, F-12 hours/access on phones, F-15 letter-spacing).

Run:  python3 tools/patches/patch_package3.py      (idempotent, marker: PACKAGE-3)

What it does
  F-11  floating launcher
        * slides out of the way while the page scrolls, and on narrow screens it only comes
          back when the visitor scrolls up, is near the top, or has keyboard focus on it
          (initLauncherAutoHide) — a 390px-wide column has no gutter, so a floating element
          that stays put can only ever sit on top of a text row
        * from 1420px up there *is* a real gutter next to the 1152px column: there the
          launcher stays put and collapses to a small chip so it never touches the text
        * the launcher's label and status no longer run together («پشتیبانی ریموت ۱ آنلاین»):
          the dot carries the count, the chip is one word, the full sentence lives in
          aria-label/title
        * the footer gets bottom room on phones, so the last lines can always scroll clear
  F-12  the header presence badge is no longer desktop-only: on phones it shows a compact
        «آنلاین / در صف» pill (full sentence in aria-label/title) and tapping it opens the
        remote-support request form
  F-15  tracking-tight removed from Persian text (logo, hero H1, the ۳۰٪ figure) — negative
        letter-spacing pulls Persian letter joins apart; Latin runs may still use it
"""
import io
import sys

P = "/home/user/پشتیبان_رایانه.html"
src = io.open(P, encoding="utf-8").read()

if "PACKAGE-3" in src:
    sys.exit("already applied — PACKAGE-3 marker found, nothing written")

ok = []


def sub(old, new, label, count=1):
    global src
    if old not in src:
        sys.exit(f"ANCHOR NOT FOUND [{label}]:\n{old[:400]}")
    src = src.replace(old, new, count)
    ok.append(label)


# ---------------------------------------------------------------- F-11: launcher markup
sub(
    '''  <!-- Floating AI Assistant Widget (Placed on RIGHT side) -->
  <div class="fixed bottom-6 right-6 z-40">
    <button onclick="openRemoteModal()" id="aiFloatingLauncherBtn" class="flex items-center gap-2 px-4 py-2.5 rounded-full bg-brand-dark dark:bg-white text-white dark:text-brand-dark shadow-2xl hover:scale-105 active:scale-95 transition-transform duration-200 border border-white/20 dark:border-black/20 ai-glow">
      <span id="launcherPresenceDot" class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
      <span class="text-xs font-bold">پشتیبانی ریموت</span>
      <span id="launcherPresenceText" class="text-[10px] px-2 py-0.5 rounded-full bg-white/15 dark:bg-black/10">آنلاین</span>
    </button>
  </div>''',
    '''  <!-- Floating remote-support launcher.
       ≥1420px: a real gutter exists beside the 1152px column, so it stays put there and shows
       only the status chip + icon at rest (the label slides out on hover/focus).
       Below that: it steps aside while the page scrolls and comes back when the visitor scrolls
       up / is near the top / focuses it — see initLauncherAutoHide(). -->
  <div id="aiFloatingLauncher" class="fixed bottom-5 right-4 sm:bottom-6 sm:right-6 z-40">
    <button onclick="openRemoteModal()" id="aiFloatingLauncherBtn" title="درخواست پشتیبانی ریموت" class="group flex items-center gap-2 p-2.5 rounded-full bg-brand-dark dark:bg-white text-white dark:text-brand-dark shadow-2xl hover:scale-105 active:scale-95 transition-all duration-200 border border-white/20 dark:border-black/20 ai-glow">
      <span id="launcherPresenceDot" class="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse shrink-0"></span>
      <svg class="w-4 h-4 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
        <path d="M3 15v-3a9 9 0 0 1 18 0v3"></path>
        <path d="M21 16.5a2.5 2.5 0 0 1-2.5 2.5H17v-5h1.5A2.5 2.5 0 0 1 21 16.5z"></path>
        <path d="M3 16.5A2.5 2.5 0 0 0 5.5 19H7v-5H5.5A2.5 2.5 0 0 0 3 16.5z"></path>
      </svg>
      <span class="text-[11px] sm:text-xs font-bold whitespace-nowrap launcher-wide-only">پشتیبانی ریموت</span>
      <span id="launcherPresenceText" class="text-[10px] px-2 py-0.5 rounded-full bg-white/15 dark:bg-black/10 shrink-0 whitespace-nowrap">آنلاین</span>
    </button>
  </div>''',
    "launcher rebuilt (gutter-aware, label + status separated)",
)

# footer: room at the bottom on phones so the last lines clear the launcher
sub(
    '''  <footer class="bg-white dark:bg-brand-darkCanvas border-t border-black/[0.08] dark:border-white/[0.08] py-10 px-4 sm:px-6 transition-colors">''',
    '''  <footer class="bg-white dark:bg-brand-darkCanvas border-t border-black/[0.08] dark:border-white/[0.08] pt-10 pb-24 lg:pb-10 px-4 sm:px-6 transition-colors">''',
    "footer bottom room on phones",
)

# ---------------------------------------------------------------- F-12: header badge
sub(
    '''        <div id="liveWorkStatusBadge" class="hidden xl:flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-medium bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20 shrink-0 whitespace-nowrap transition-colors">
          <span id="shopHoursStatusDot" class="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse shrink-0"></span>
          <span id="shopHoursStatusText" class="whitespace-nowrap">کارشناس آنلاین</span>
        </div>''',
    '''        <button type="button" onclick="openRemoteModal()" id="liveWorkStatusBadge" class="flex items-center gap-1.5 px-2 py-1 sm:px-2.5 rounded-full text-[10px] sm:text-[11px] font-medium bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20 shrink-0 whitespace-nowrap transition-colors">
          <span id="shopHoursStatusDot" class="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse shrink-0"></span>
          <span id="shopHoursStatusText" class="whitespace-nowrap">آنلاین</span>
          <span id="shopHoursStatusTextLong" class="hidden xl:inline whitespace-nowrap">کارشناس آنلاین</span>
        </button>''',
    "header presence badge visible on phones (compact text, long text on xl)",
)

# ---------------------------------------------------------------- F-11/F-12: JS
sub(
    '''      const GREEN = "hidden xl:flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-medium bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20 shrink-0 whitespace-nowrap transition-colors";
      const AMBER = "hidden xl:flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-medium bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20 shrink-0 whitespace-nowrap transition-colors";''',
    '''      // NB: these two strings must mirror the markup of #liveWorkStatusBadge (visibility included)
      const GREEN = "flex items-center gap-1.5 px-2 py-1 sm:px-2.5 rounded-full text-[10px] sm:text-[11px] font-medium bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20 shrink-0 whitespace-nowrap transition-colors";
      const AMBER = "flex items-center gap-1.5 px-2 py-1 sm:px-2.5 rounded-full text-[10px] sm:text-[11px] font-medium bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20 shrink-0 whitespace-nowrap transition-colors";''',
    "presence badge class strings synced with the new markup",
)

sub(
    '''      const badge = document.getElementById('liveWorkStatusBadge');
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
      }''',
    '''      const badge = document.getElementById('liveWorkStatusBadge');
      const badgeText = document.getElementById('shopHoursStatusText');
      const badgeLong = document.getElementById('shopHoursStatusTextLong');
      const badgeDot = document.getElementById('shopHoursStatusDot');
      if (badge && badgeText && badgeDot) {
        const longText = online
          ? `${faNum(n)} کارشناس آنلاین — هدف پاسخ تا ${target} دقیقه`
          : 'درخواست‌ها در صف — اولین کارشناس تماس می‌گیرد';
        badgeText.textContent = online ? 'آنلاین' : 'در صف';
        if (badgeLong) badgeLong.textContent = longText;
        // the pill is compact on phones, so the full sentence lives on the control itself
        badge.setAttribute('title', longText);
        badge.setAttribute('aria-label', `وضعیت پشتیبانی ریموت: ${longText} — برای ثبت درخواست بزنید`);
        badge.className = online ? GREEN : AMBER;
        badgeDot.className = online
          ? "w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse shrink-0"
          : "w-1.5 h-1.5 rounded-full bg-amber-500 shrink-0";
      }''',
    "presence badge: short/long text, title + aria-label, tappable",
)

sub(
    '''      const launcherDot = document.getElementById('launcherPresenceDot');
      const launcherText = document.getElementById('launcherPresenceText');
      if (launcherDot && launcherText) {
        launcherText.textContent = online ? `${faNum(n)} آنلاین` : 'صف درخواست';
        launcherDot.className = online
          ? 'w-2 h-2 rounded-full bg-emerald-500 animate-pulse'
          : 'w-2 h-2 rounded-full bg-amber-500';
      }''',
    '''      const launcherDot = document.getElementById('launcherPresenceDot');
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
      }''',
    "launcher: short status chip + full sentence in aria-label",
)

# ---------------------------------------------------------------- F-11: auto-hide logic
AUTOHIDE_JS = '''    /* F-11: دکمهٔ شناور روی صفحه‌های باریک «وقت خواندن» کنار می‌رود.
       قاعده: از ۱۴۲۰px به بالا گاتر صفحه به‌قدر کافی هست و دکمه سرِ جایش می‌ماند؛
       زیر آن، دکمه فقط وقتی دیده می‌شود که کاربر به بالا اسکرول کند، در بالای صفحه باشد،
       یا با کیبورد روی آن فوکوس کرده باشد. هنگام اسکرول به پایین هم فوراً کنار می‌رود.
       اگر کاربر «کاهش انیمیشن» خواسته باشد، کل این رفتار غیرفعال است. */
    function initLauncherAutoHide() {
      const wrap = document.getElementById("aiFloatingLauncher");
      const btn = document.getElementById("aiFloatingLauncherBtn");
      if (!wrap || !btn) return;
      if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

      const hasGutter = () => window.innerWidth >= 1420;
      let pinned = false;          // keyboard focus keeps it put
      let lastY = window.scrollY;
      let upward = false;          // last movement was toward the top

      const show = () => wrap.classList.remove("launcher-reading");
      const elide = () => { if (!pinned && !hasGutter()) wrap.classList.add("launcher-reading"); };

      const apply = () => {
        if (pinned || hasGutter() || window.scrollY < 120 || upward) show();
        else elide();
      };

      window.addEventListener("scroll", () => {
        const y = window.scrollY;
        const dy = y - lastY;
        lastY = y;
        if (Math.abs(dy) > 1) upward = dy < 0;
        apply();
      }, { passive: true });

      window.addEventListener("resize", apply, { passive: true });
      btn.addEventListener("focus", () => { pinned = true; show(); });
      btn.addEventListener("blur", () => { pinned = false; apply(); });
      window.addEventListener("keydown", e => { if (e.key === "Tab") show(); });

      apply();
    }

'''
sub(
    '''    /* Initialization on Page Load */
    window.addEventListener("DOMContentLoaded", () => {''',
    AUTOHIDE_JS + '''    /* Initialization on Page Load */
    window.addEventListener("DOMContentLoaded", () => {''',
    "initLauncherAutoHide() added",
)

sub(
    '''      initShopHours();
      renderPresence();
      initDropZone();        ''',
    '''      initShopHours();
      renderPresence();
      initDropZone();
      initLauncherAutoHide();''',
    "auto-hide wired into DOMContentLoaded",
)

# ---------------------------------------------------------------- F-11: launcher styles
sub(
    '''    .poshtiban-scrollbar {''',
    '''    /* --- F-11: حالت‌های دکمهٔ شناور (منطق در initLauncherAutoHide) ---
       روی ستون تمام‌عرض موبایل هیچ عنصر شناوری نمی‌تواند از روی ردیف‌های متن رد نشود؛
       پس آن‌جا دکمه وقت خواندن کنار می‌رود. از ۱۴۲۰px به بالا گاتر واقعی وجود دارد. --- */
    #aiFloatingLauncher {
      transition: opacity .25s ease, transform .25s ease;
    }
    @media (max-width: 1419.9px) {
      #aiFloatingLauncher.launcher-reading {
        /* کنار رفتن سریع‌تر از بازگشت است تا لحظهٔ شروع اسکرول هم پوششی روی متن نماند */
        transition-duration: .12s;
        opacity: 0;
        /* کاملاً زیر لبهٔ دید تا دکمهٔ نامرئی هم جعبه‌ای روی متن نگذارد */
        transform: translateY(calc(100% + 1.5rem));
        pointer-events: none;
      }
    }
    @media (prefers-reduced-motion: reduce) {
      #aiFloatingLauncher { transition: none; }
    }
    /* برچسب «پشتیبانی ریموت»: جایی که گاتر واقعی هست (≥۱۴۲۰px) در حالت ثابت جمع می‌شود
       تا دکمه در گاتر جا شود و با هاور/فوکوس باز می‌شود. زیر ۱۴۲۰px که دکمه فقط
       لحظه‌ای ظاهر می‌شود، برچسب روشن می‌ماند تا معنی‌اش روشن باشد. */
    .launcher-wide-only { display: inline-block; vertical-align: middle; }
    @media (min-width: 1420px) {
      .launcher-wide-only {
        max-width: 0; opacity: 0; overflow: hidden; white-space: nowrap;
        transition: max-width .3s ease, opacity .3s ease;
      }
      #aiFloatingLauncherBtn:hover .launcher-wide-only,
      #aiFloatingLauncherBtn:focus-visible .launcher-wide-only { max-width: 9rem; opacity: 1; }
    }

    .poshtiban-scrollbar {''',
    "launcher-reading style",
)

# ---------------------------------------------------------------- F-15: letter-spacing
sub(
    '''<span class="font-bold text-xs sm:text-sm tracking-tight''',
    '''<span class="font-bold text-xs sm:text-sm''',
    "F-15 logo: tracking-tight removed",
)
sub(
    '''class="hero-headline text-4xl sm:text-6xl md:text-7xl font-extrabold tracking-tight text-brand-dark''',
    '''class="hero-headline text-4xl sm:text-6xl md:text-7xl font-extrabold text-brand-dark''',
    "F-15 hero H1: tracking-tight removed (it sat late in the class list)",
)
sub(
    '''uppercase tracking-wider''',
    '''uppercase''',
    "F-15 section kickers: tracking-wider removed (Persian letter joins)",
    count=11,
)
sub(
    '''class="text-3xl sm:text-4xl font-black tracking-tight''',
    '''class="text-3xl sm:text-4xl font-black''',
    "F-15 ۳۰٪ figure: tracking-tight removed",
)

# ---------------------------------------------------------------- F-17: mono font on Persian
sub(
    '''    .poshtiban-scrollbar {''',
    '''    /* --- F-17: فونت مونو گلیف فارسی ندارد و اتصال حروف را می‌شکند («تومان» → «ت وم ا ن»)؛
       ارقام و متن فارسی با همان فونت متن ولی با ارقام هم‌عرض (tabular) نمایش داده می‌شوند. --- */
    .font-mono {
      font-family: 'Vazirmatn', system-ui, BlinkMacSystemFont, sans-serif !important;
      font-variant-numeric: tabular-nums;
    }

    .poshtiban-scrollbar {''',
    "F-17 .font-mono no longer breaks Persian letter joining",
)

# ---------------------------------------------------------------- marker
sub(
    '''</body>''',
    '''<!-- PACKAGE-3 (mobile: launcher overlap, phone-visible hours/access, Persian letter-spacing) -->
</body>''',
    "patch marker",
)

io.open(P, "w", encoding="utf-8").write(src)
for label in ok:
    print(f"  ✓ {label}")
print(f"\nDone — {len(src)} chars written.")
