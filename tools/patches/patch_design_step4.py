#!/usr/bin/env python3
"""
DESIGN-STEP4 — cohesive theme, lighting, separator, and glass pass.

Scope intentionally limited to the existing design system and theme controls:
  • automatic sunrise/sunset theme using device geolocation + local clock
    (no location persistence, no external requests; 07:00–19:00 local fallback)
  • saved Light / Dark / Automatic preference, plus accessible desktop/mobile controls
  • one low-intensity blue/violet ambient-light system behind all sections
  • remove neutral separator rules at section/card seams
  • use the header's translucent blur/reflection language on existing card surfaces
  • keep structure, copy, order, and business functionality unchanged

Run once from workspace root:
  python3 tools/patches/patch_design_step4.py
"""
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PAGE = os.path.join(ROOT, 'پشتیبان_رایانه.html')
MARK = 'DESIGN-STEP4'
source = io.open(PAGE, encoding='utf-8').read()
if MARK in source:
    sys.exit('DESIGN-STEP4 already exists; refusing to apply twice.')
assert 'DESIGN-STEP3B' in source and 'function toggleTheme()' in source, 'Expected current design/theme anchors not found.'
s = source
applied = []


def rep(old, new, label, count=1):
    global s
    actual = s.count(old)
    assert actual == count, f'{label}: expected {count} match(es), found {actual}\n{old[:180]}'
    s = s.replace(old, new, count)
    applied.append(label)


# 1) Theme bootstrap before paint: saved preference or local-time fallback.
rep('''  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0">''',
'''  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0">
  <!-- DESIGN-STEP4: جلوگیری از چشمک تم؛ پیش‌فرض خودکار با ساعت محلی (تا رسیدن نتیجهٔ مکان) -->
  <script id="designStep4ThemeBoot">
    (function () {
      var mode = 'auto';
      try {
        var saved = localStorage.getItem('poshtiban_theme');
        if (saved === 'light' || saved === 'dark' || saved === 'auto') mode = saved;
      } catch (_) {}
      var now = new Date(), minutes = now.getHours() * 60 + now.getMinutes();
      var dark = mode === 'dark' || (mode === 'auto' && (minutes < 420 || minutes >= 1140));
      document.documentElement.classList.toggle('dark', dark);
      window.__poshtibanThemeMode = mode;
      window.__poshtibanThemeDark = dark;
    })();
  </script>''', 'early local-time theme bootstrap')

# 2) Header control becomes a compact three-choice popup; header order/contents stay put.
old = '''        <!-- Night Mode — last control of the header (round 3, item 1) -->
        <button id="themeToggleBtn" onclick="toggleTheme()" aria-label="تغییر تم (حالت شب)" title="حالت شب / روز" class="flex w-7 h-7 rounded-full items-center justify-center text-brand-dark/70 dark:text-white/70 hover:bg-black/5 dark:hover:bg-white/10 transition shrink-0">
          <span id="themeToggleIcon" class="inline-flex" data-theme-icon="moon"><svg class="w-4 h-4 shrink-0" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><use href="#ic-moon"/></svg></span>
        </button>'''
new = '''        <!-- DESIGN-STEP4: سه حالت تم (روشن / تیره / خودکار با طلوع و غروب محلی) -->
        <div id="themeControl" class="theme-control">
          <button id="themeToggleBtn" type="button" onclick="toggleThemeMenu(event)" aria-label="تنظیم تم صفحه" title="تنظیم تم صفحه" aria-haspopup="true" aria-expanded="false" aria-controls="themeModeMenu" class="flex w-7 h-7 rounded-full items-center justify-center text-brand-dark/70 dark:text-white/70 hover:bg-black/5 dark:hover:bg-white/10 transition shrink-0">
            <span id="themeToggleIcon" class="inline-flex" data-theme-icon="moon"><svg class="w-4 h-4 shrink-0" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><use href="#ic-moon"/></svg></span>
          </button>
          <div id="themeModeMenu" class="theme-menu hidden" role="group" aria-label="انتخاب حالت تم">
            <span class="theme-menu-title">حالت نمایش</span>
            <div class="theme-mode-group">
              <button type="button" class="theme-mode-option" data-theme-mode="auto" aria-pressed="false" onclick="setThemeMode('auto')">خودکار · طلوع/غروب</button>
              <button type="button" class="theme-mode-option" data-theme-mode="light" aria-pressed="false" onclick="setThemeMode('light')">روشن</button>
              <button type="button" class="theme-mode-option" data-theme-mode="dark" aria-pressed="false" onclick="setThemeMode('dark')">تیره</button>
            </div>
            <span id="themeModeHint" class="theme-mode-hint">در حالت خودکار، برای محاسبهٔ طلوع و غروب مجوز مکان لازم است؛ در صورت رد، از ساعت محلی ۰۷ تا ۱۹ استفاده می‌شود.</span>
          </div>
        </div>'''
rep(old, new, 'desktop theme chooser')

# 3) The existing mobile theme row becomes a visible, accessible 3-choice control.
old = '''    <div class="flex items-center justify-between pb-3 border-b border-black/[0.06] dark:border-white/[0.08]">
      <span class="text-neutral-500 dark:text-neutral-400">حالت نمایش:</span>
      <button onclick="toggleTheme()" class="px-3 py-1 rounded-full bg-black/5 dark:bg-white/10 font-semibold text-xs">
        <span id="drawerThemeText">تغییر به تم تیره</span>
      </button>
    </div>'''
new = '''    <div id="mobileThemeControl" class="theme-mobile-control" role="group" aria-label="انتخاب حالت تم">
      <span class="theme-menu-title">حالت نمایش</span>
      <div class="theme-mode-group theme-mode-group-mobile">
        <button type="button" class="theme-mode-option" data-theme-mode="auto" aria-pressed="false" onclick="setThemeMode('auto')">خودکار</button>
        <button type="button" class="theme-mode-option" data-theme-mode="light" aria-pressed="false" onclick="setThemeMode('light')">روشن</button>
        <button type="button" class="theme-mode-option" data-theme-mode="dark" aria-pressed="false" onclick="setThemeMode('dark')">تیره</button>
      </div>
      <span id="mobileThemeHint" class="theme-mode-hint">خودکار با طلوع/غروب؛ در صورت رد مجوز مکان، ۰۷ تا ۱۹.</span>
    </div>'''
rep(old, new, 'mobile theme chooser')

# 4) Replace the old binary click-toggle with preference, sunrise/sunset, and UI-sync logic.
start = s.index('    /* Modern Dark / Light Mode Switcher */')
end = s.index('    function toggleMobileMenu() {', start)
new_switcher = r'''    /* DESIGN-STEP4 — تم خودکارِ طلوع/غروب محلی + انتخاب دستیِ پایدار */
    let themeGeoCoords = null;          // مختصات فقط در حافظهٔ همین صفحه می‌ماند.
    let themeGeoState = 'pending';       // pending | ready | denied | unsupported
    let themeGeoRequested = false;
    let themeTransitionTimer = null;

    function getThemeMode() {
      try {
        const saved = localStorage.getItem('poshtiban_theme');
        return (saved === 'light' || saved === 'dark' || saved === 'auto') ? saved : 'auto';
      } catch (_) { return window.__poshtibanThemeMode || 'auto'; }
    }

    function normalizeDegrees(value) { return ((value % 360) + 360) % 360; }

    /* الگوریتم خورشیدی NOAA (زاویهٔ افق ۹۰٫۸۳۳°؛ تصحیح شکست نور).
       خروجی دقیقهٔ روزِ محلی دستگاه است؛ هیچ سرویس/درخواست بیرونی لازم نیست. */
    function solarEventLocalMinutes(now, latitude, longitude, sunrise) {
      const year = now.getFullYear(), month = now.getMonth(), day = now.getDate();
      const dayNumber = Math.floor((Date.UTC(year, month, day) - Date.UTC(year, 0, 0)) / 86400000);
      const longitudeHour = longitude / 15;
      const approximate = dayNumber + (((sunrise ? 6 : 18) - longitudeHour) / 24);
      const meanAnomaly = 0.9856 * approximate - 3.289;
      const trueLongitude = normalizeDegrees(meanAnomaly + 1.916 * Math.sin(meanAnomaly * Math.PI / 180)
        + 0.020 * Math.sin(2 * meanAnomaly * Math.PI / 180) + 282.634);
      let rightAscension = normalizeDegrees(Math.atan(0.91764 * Math.tan(trueLongitude * Math.PI / 180)) * 180 / Math.PI);
      rightAscension += Math.floor(trueLongitude / 90) * 90 - Math.floor(rightAscension / 90) * 90;
      rightAscension /= 15;
      const sinDeclination = 0.39782 * Math.sin(trueLongitude * Math.PI / 180);
      const cosDeclination = Math.cos(Math.asin(sinDeclination));
      const cosHourAngle = (Math.cos(90.833 * Math.PI / 180)
        - sinDeclination * Math.sin(latitude * Math.PI / 180))
        / (cosDeclination * Math.cos(latitude * Math.PI / 180));
      if (cosHourAngle > 1) return { polar: 'night', minutes: null };
      if (cosHourAngle < -1) return { polar: 'day', minutes: null };
      const angle = Math.acos(cosHourAngle) * 180 / Math.PI;
      const hour = (sunrise ? 360 - angle : angle) / 15;
      const localMean = hour + rightAscension - 0.06571 * approximate - 6.622;
      const utcHour = ((localMean - longitudeHour) % 24 + 24) % 24;
      const utcMidnightForLocalDate = Date.UTC(year, month, day);
      const event = new Date(utcMidnightForLocalDate + utcHour * 3600000);
      return { polar: null, minutes: event.getHours() * 60 + event.getMinutes() };
    }

    function isNightByThemeRule(mode = getThemeMode()) {
      if (mode === 'dark') return true;
      if (mode === 'light') return false;
      const now = new Date(), localMinutes = now.getHours() * 60 + now.getMinutes();
      if (themeGeoCoords) {
        const rise = solarEventLocalMinutes(now, themeGeoCoords.latitude, themeGeoCoords.longitude, true);
        const set = solarEventLocalMinutes(now, themeGeoCoords.latitude, themeGeoCoords.longitude, false);
        if (rise.polar === 'night' || set.polar === 'night') return true;
        if (rise.polar === 'day' || set.polar === 'day') return false;
        if (rise.minutes !== null && set.minutes !== null) return localMinutes < rise.minutes || localMinutes >= set.minutes;
      }
      // Privacy-preserving fallback if location is denied/unavailable: 07:00–18:59 local time = light.
      return localMinutes < 420 || localMinutes >= 1140;
    }

    function syncThemeControls() {
      const mode = getThemeMode();
      document.querySelectorAll('[data-theme-mode]').forEach(button => {
        const selected = button.getAttribute('data-theme-mode') === mode;
        button.setAttribute('aria-pressed', selected ? 'true' : 'false');
        button.classList.toggle('is-active', selected);
      });
      const hint = themeGeoState === 'ready'
        ? 'طلوع و غروب با موقعیت دستگاه و ساعت محلی محاسبه می‌شود؛ مختصات ذخیره یا ارسال نمی‌شود.'
        : themeGeoState === 'denied'
          ? 'مجوز مکان در دسترس نیست؛ خودکار از ساعت محلی ۰۷ تا ۱۹ استفاده می‌کند.'
          : themeGeoState === 'unsupported'
            ? 'مکان‌یابی در این مرورگر در دسترس نیست؛ خودکار از ساعت محلی ۰۷ تا ۱۹ استفاده می‌کند.'
            : 'در حالت خودکار، برای محاسبهٔ طلوع و غروب مجوز مکان لازم است؛ در صورت رد، از ساعت محلی ۰۷ تا ۱۹ استفاده می‌شود.';
      const desktopHint = document.getElementById('themeModeHint');
      const mobileHint = document.getElementById('mobileThemeHint');
      if (desktopHint) desktopHint.textContent = hint;
      if (mobileHint) mobileHint.textContent = hint;
    }

    function updateThemeUI(isDark) {
      const themeIcon = document.getElementById('themeToggleIcon');
      const themeButton = document.getElementById('themeToggleBtn');
      if (themeIcon) {
        themeIcon.innerHTML = poshIcon(isDark ? 'sun' : 'moon', 'w-4 h-4');
        themeIcon.setAttribute('data-theme-icon', isDark ? 'sun' : 'moon');
      }
      const mode = getThemeMode();
      const label = mode === 'auto' ? 'خودکار بر پایهٔ طلوع/غروب محلی' : (mode === 'dark' ? 'تیره' : 'روشن');
      if (themeButton) {
        themeButton.setAttribute('aria-label', 'تم فعلی: ' + label + '؛ بازکردن گزینه‌های تم');
        themeButton.title = 'تم فعلی: ' + label;
      }
      syncThemeControls();
    }

    function applyThemePreference(animate = true) {
      const root = document.documentElement;
      const dark = isNightByThemeRule();
      const changed = root.classList.contains('dark') !== dark;
      window.__poshtibanThemeDark = dark;
      const commit = () => {
        root.classList.toggle('dark', dark);
        updateThemeUI(dark);
      };
      if (changed && animate && !(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches)) {
        root.classList.add('theme-transitioning');
        requestAnimationFrame(() => requestAnimationFrame(commit));
        if (themeTransitionTimer) clearTimeout(themeTransitionTimer);
        themeTransitionTimer = setTimeout(() => root.classList.remove('theme-transitioning'), 650);
      } else {
        commit();
      }
    }

    function requestThemeLocation() {
      if (getThemeMode() !== 'auto' || themeGeoRequested) return;
      themeGeoRequested = true;
      if (!navigator.geolocation) {
        themeGeoState = 'unsupported';
        syncThemeControls();
        applyThemePreference(true);
        return;
      }
      navigator.geolocation.getCurrentPosition(position => {
        themeGeoCoords = { latitude: position.coords.latitude, longitude: position.coords.longitude };
        themeGeoState = 'ready';
        syncThemeControls();
        if (getThemeMode() === 'auto') applyThemePreference(true);
      }, () => {
        themeGeoState = 'denied';
        syncThemeControls();
        if (getThemeMode() === 'auto') applyThemePreference(true);
      }, { enableHighAccuracy: false, timeout: 10000, maximumAge: 86400000 });
    }

    function initializeTheme() {
      window.__poshtibanThemeMode = getThemeMode();
      applyThemePreference(false);
      syncThemeControls();
      if (getThemeMode() === 'auto') requestThemeLocation();
      window.setInterval(() => {
        if (!document.hidden && getThemeMode() === 'auto') applyThemePreference(true);
      }, 60000);
      document.addEventListener('visibilitychange', () => {
        if (!document.hidden && getThemeMode() === 'auto') applyThemePreference(true);
      });
      document.addEventListener('click', event => {
        if (!event.target.closest('#themeControl')) closeThemeMenu();
      });
      document.addEventListener('keydown', event => {
        if (event.key === 'Escape' && closeThemeMenu()) {
          document.getElementById('themeToggleBtn')?.focus();
        }
      });
    }

    function setThemeMode(mode) {
      if (!['auto', 'light', 'dark'].includes(mode)) return;
      try { localStorage.setItem('poshtiban_theme', mode); } catch (_) {}
      window.__poshtibanThemeMode = mode;
      applyThemePreference(true);
      if (mode === 'auto') requestThemeLocation();
      closeThemeMenu();
      if (typeof playHapticSound === 'function') playHapticSound('click');
      if (typeof showToast === 'function') {
        const title = mode === 'auto' ? 'حالت خودکارِ طلوع/غروب فعال شد.' : (mode === 'dark' ? 'حالت تیره فعال شد.' : 'حالت روشن فعال شد.');
        showToast(title);
      }
    }

    function toggleThemeMenu(event) {
      if (event) { event.preventDefault(); event.stopPropagation(); }
      const menu = document.getElementById('themeModeMenu');
      const button = document.getElementById('themeToggleBtn');
      if (!menu || !button) return;
      const open = menu.classList.contains('hidden');
      menu.classList.toggle('hidden', !open);
      button.setAttribute('aria-expanded', open ? 'true' : 'false');
      if (open) syncThemeControls();
    }

    function closeThemeMenu() {
      const menu = document.getElementById('themeModeMenu');
      const button = document.getElementById('themeToggleBtn');
      if (!menu || menu.classList.contains('hidden')) return false;
      menu.classList.add('hidden');
      if (button) button.setAttribute('aria-expanded', 'false');
      return true;
    }

'''
s = s[:start] + new_switcher + s[end:]
applied.append('sunrise/sunset theme engine + controls')

# 5) Replace DOMContentLoaded's old OS preference / binary localStorage logic.
old_theme_init = '''      // Theme detection
      const savedTheme = localStorage.getItem("poshtiban_theme");
      const prefersDark = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
      if (savedTheme === "dark" || (!savedTheme && prefersDark)) {
        document.documentElement.classList.add("dark");
        updateThemeUI(true);
      } else {
        document.documentElement.classList.remove("dark");
        updateThemeUI(false);
      }
'''
rep(old_theme_init, '''      // DESIGN-STEP4: حالت ذخیره‌شده یا خودکارِ طلوع/غروب محلی
      initializeTheme();
''', 'theme initialization / old OS-dark logic removed')

# 6) Cohesive ambient light, non-grey section transitions, and glass surfaces.
CSS = r'''

    /* ===== DESIGN-STEP4 — یک محیط نوری + شیشهٔ مشترک در سراسر سایت ===== */
    :root { color-scheme: light; --surface-glass-light: rgba(255,255,255,.62); --surface-glass-dark: rgba(19,20,25,.68); }
    :root.dark { color-scheme: dark; }
    html { background-color: #fbfbfd; }
    html.dark { background-color: #07080c; }
    body { position: relative; isolation: isolate; background-color: transparent !important; background-image: none !important; }
    /* دو لایه با هندسهٔ ثابت: طیف آبی-بنفش آرامِ هدر، امتدادیافته زیر کل صفحه. */
    body::before, body::after { content: ""; position: fixed; inset: 0; z-index: -1; pointer-events: none;
      transition: opacity .55s cubic-bezier(.2,.7,.2,1); }
    body::before { opacity: 1; background:
      radial-gradient(780px 560px at 91% 0%, rgba(0,113,227,.080), transparent 72%),
      radial-gradient(740px 560px at 7% 9%, rgba(168,85,247,.055), transparent 72%),
      radial-gradient(920px 620px at 76% 96%, rgba(0,113,227,.026), transparent 75%); }
    body::after { opacity: 0; background:
      radial-gradient(780px 560px at 91% 0%, rgba(0,113,227,.145), transparent 72%),
      radial-gradient(740px 560px at 7% 9%, rgba(168,85,247,.105), transparent 72%),
      radial-gradient(920px 620px at 76% 96%, rgba(0,113,227,.050), transparent 75%); }
    html.dark body::before { opacity: 0; }
    html.dark body::after { opacity: 1; }

    /* هدر، مرجع شیشه: لایهٔ نیمه‌شفاف آبی/بنفش، blur و بازتاب بالایی؛ بدون خط خاکستری زیرین. */
    .frosted-glass { background: linear-gradient(120deg, rgba(255,255,255,.86), rgba(249,250,255,.72) 58%, rgba(249,247,255,.70));
      backdrop-filter: blur(24px) saturate(155%); -webkit-backdrop-filter: blur(24px) saturate(155%);
      box-shadow: inset 0 1px 0 rgba(255,255,255,.78); }
    .dark .frosted-glass { background: linear-gradient(120deg, rgba(24,25,31,.82), rgba(13,14,19,.76) 58%, rgba(20,16,27,.72));
      backdrop-filter: blur(24px) saturate(145%); -webkit-backdrop-filter: blur(24px) saturate(145%);
      box-shadow: inset 0 1px 0 rgba(255,255,255,.10); }
    #mainHeader { border-bottom: 0 !important; box-shadow: 0 10px 34px -28px rgba(17,24,39,.30), inset 0 1px 0 rgba(255,255,255,.76); }
    .dark #mainHeader { box-shadow: 0 12px 36px -24px rgba(0,0,0,.72), inset 0 1px 0 rgba(255,255,255,.10); }
    .frosted-glass-scrolled { box-shadow: 0 12px 34px -22px rgba(17,24,39,.25), inset 0 1px 0 rgba(255,255,255,.70); }
    .dark .frosted-glass-scrolled { box-shadow: 0 16px 38px -23px rgba(0,0,0,.76), inset 0 1px 0 rgba(255,255,255,.10); }
    #mobileDrawer { border-top: 0 !important; }
    #mobileDrawer [class*="border-t"], #mobileDrawer [class*="border-b"] { border-color: transparent !important; }
    #aiChatDrawer { border-left: 0 !important; }

    /* بخش‌های خاکستری، لایهٔ شفافِ محیطی‌اند نه سطوح مات؛ پس‌زمینهٔ مشترک از زیرشان دیده می‌شود. */
    #main > section[class*="bg-brand-lightGray"] { background-color: rgba(240,243,249,.48) !important; }
    html.dark #main > section[class*="bg-brand-lightGray"] { background-color: rgba(12,13,18,.50) !important; }
    footer { border-top: 0 !important; background-color: rgba(255,255,255,.42) !important;
      backdrop-filter: blur(14px) saturate(135%); -webkit-backdrop-filter: blur(14px) saturate(135%); }
    html.dark footer { background-color: rgba(9,10,14,.54) !important; }

    /* مرزهای تمام‌عرض سکشن‌ها حذف می‌شوند؛ تفاوت زمینه، فاصله و عمق، تفکیک را بر عهده دارد. */
    #main > section { border-block-start: 0 !important; border-block-end: 0 !important; }
    body [class*="border-t"][class*="border-black/"],
    body [class*="border-b"][class*="border-black/"] { border-color: transparent !important; }
    body [class*="dark:border-white/"][class*="border-t"],
    body [class*="dark:border-white/"][class*="border-b"] { border-color: transparent !important; }

    /* D-05 به‌جای درز خاکستری: محوشدگیِ آبی/بنفش بسیار ملایم در همان جهتِ نور محیط. */
    section[class*="bg-brand-lightGray"]::before { background: linear-gradient(to bottom, rgba(0,113,227,.035) 0%, rgba(0,113,227,0) 100%); }
    #ai-diagnostic::after, #bottleneck::after { background: linear-gradient(to top, rgba(168,85,247,.025) 0%, rgba(168,85,247,0) 100%); }
    html.dark section[class*="bg-brand-lightGray"]::before { background: linear-gradient(to bottom, rgba(0,113,227,.055) 0%, rgba(0,113,227,0) 100%); }
    html.dark #ai-diagnostic::after, html.dark #bottleneck::after { background: linear-gradient(to top, rgba(168,85,247,.040) 0%, rgba(168,85,247,0) 100%); }

    /* شیشهٔ ملایم روی کارت‌های موجود (نه بازطراحی/تغییر چیدمان): عبور نور + blur + بازتاب داخلی. */
    body div[class*="rounded-[28px]"][class*="bg-white"],
    body div[class*="rounded-3xl"][class*="bg-white"],
    body div[class*="rounded-2xl"][class*="bg-white"][class*="border-black"],
    body div[class*="rounded-2xl"][class*="bg-brand-lightGray"][class*="border-black"]:not([class*="border-dashed"]) {
      background-color: var(--surface-glass-light) !important;
      -webkit-backdrop-filter: blur(18px) saturate(150%); backdrop-filter: blur(18px) saturate(150%);
      box-shadow: 0 14px 38px -28px rgba(21,35,61,.26), inset 0 1px 0 rgba(255,255,255,.74);
    }
    html.dark body div[class*="rounded-[28px]"][class*="bg-white"],
    html.dark body div[class*="rounded-3xl"][class*="bg-white"],
    html.dark body div[class*="rounded-2xl"][class*="bg-white"][class*="border-black"],
    html.dark body div[class*="rounded-2xl"][class*="bg-brand-lightGray"][class*="border-black"]:not([class*="border-dashed"]) {
      background-color: var(--surface-glass-dark) !important;
      -webkit-backdrop-filter: blur(18px) saturate(140%); backdrop-filter: blur(18px) saturate(140%);
      box-shadow: 0 18px 42px -30px rgba(0,0,0,.78), inset 0 1px 0 rgba(255,255,255,.075);
    }
    /* حذف لبهٔ خاکستریِ کارت‌های بزرگ؛ مرز فعال/برند و فوکوس تعاملی دست‌نخورده می‌مانند. */
    body div[class*="rounded-[28px]"][class*="border-black"],
    body div[class*="rounded-3xl"][class*="border-black"],
    body div[class*="rounded-2xl"][class*="bg-white"][class*="border-black"],
    body div[class*="rounded-2xl"][class*="bg-brand-lightGray"][class*="border-black"]:not([class*="border-dashed"]) { border-color: transparent !important; }
    @media (hover: hover) and (pointer: fine) and (prefers-reduced-motion: no-preference) {
      body div[class*="rounded-[28px]"][class*="bg-white"]:hover,
      body div[class*="rounded-3xl"][class*="bg-white"]:hover,
      body div[class*="rounded-2xl"][class*="bg-white"][class*="border-black"]:hover,
      body div[class*="rounded-2xl"][class*="bg-brand-lightGray"][class*="border-black"]:not([class*="border-dashed"]):hover {
        box-shadow: 0 20px 44px -26px rgba(21,35,61,.30), inset 0 1px 0 rgba(255,255,255,.76);
      }
      html.dark body div[class*="rounded-[28px]"][class*="bg-white"]:hover,
      html.dark body div[class*="rounded-3xl"][class*="bg-white"]:hover,
      html.dark body div[class*="rounded-2xl"][class*="bg-white"][class*="border-black"]:hover,
      html.dark body div[class*="rounded-2xl"][class*="bg-brand-lightGray"][class*="border-black"]:not([class*="border-dashed"]):hover {
        box-shadow: 0 22px 48px -26px rgba(0,0,0,.82), inset 0 1px 0 rgba(255,255,255,.085);
      }
    }

    /* تم‌گزین مشترک: پنل هدر و سه‌گزینهٔ منوی موبایل از همان شیشهٔ هدر استفاده می‌کنند. */
    .theme-control { position: relative; display: flex; flex: 0 0 auto; }
    .theme-menu { position: absolute; z-index: 60; top: calc(100% + 10px); inset-inline-end: 0; width: 238px;
      padding: 13px; border-radius: 18px; color: #1d1d1f;
      background: linear-gradient(130deg, rgba(255,255,255,.88), rgba(248,250,255,.76) 60%, rgba(248,245,255,.74));
      -webkit-backdrop-filter: blur(24px) saturate(155%); backdrop-filter: blur(24px) saturate(155%);
      box-shadow: 0 20px 55px -30px rgba(18,28,48,.34), inset 0 1px 0 rgba(255,255,255,.82);
      outline: 1px solid rgba(255,255,255,.34); }
    .dark .theme-menu { color: #f5f5f7; background: linear-gradient(130deg, rgba(25,26,32,.92), rgba(12,13,18,.86) 60%, rgba(20,16,27,.84));
      box-shadow: 0 22px 56px -30px rgba(0,0,0,.78), inset 0 1px 0 rgba(255,255,255,.10); outline-color: rgba(255,255,255,.08); }
    .theme-menu-title { display: block; font-size: 11px; font-weight: 800; margin: 0 0 8px; color: #62626a; }
    .dark .theme-menu-title { color: #c0c0c5; }
    .theme-mode-group { display: grid; gap: 4px; }
    .theme-mode-option { display: flex; align-items: center; justify-content: flex-start; width: 100%; min-height: 34px;
      padding: 7px 10px; border: 0; border-radius: 11px; background: transparent; color: inherit;
      font: inherit; font-size: 11px; font-weight: 650; text-align: right; cursor: pointer;
      transition: background-color .18s ease, color .18s ease, box-shadow .18s ease; }
    .theme-mode-option:hover { background: rgba(0,113,227,.075); }
    .theme-mode-option.is-active { color: #0066cc; background: rgba(0,113,227,.105); box-shadow: inset 0 1px 0 rgba(255,255,255,.48); }
    .dark .theme-mode-option.is-active { color: #79baff; background: rgba(0,113,227,.20); box-shadow: inset 0 1px 0 rgba(255,255,255,.075); }
    .theme-mode-hint { display: block; margin-top: 9px; font-size: 9px; line-height: 1.7; color: #77777e; }
    .dark .theme-mode-hint { color: #a1a1a6; }
    .theme-mobile-control { display: grid; gap: 7px; padding: 0 0 12px; }
    .theme-mode-group-mobile { grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 5px; }
    .theme-mode-group-mobile .theme-mode-option { justify-content: center; min-width: 0; padding-inline: 5px; font-size: 10px; }
    .theme-mobile-control .theme-mode-hint { margin-top: 0; }

    /* یک گذار فقط برای رنگ/سطح/عمق؛ هرگز حرکت یا چیدمان را override نمی‌کند. */
    html.theme-transitioning, html.theme-transitioning *, html.theme-transitioning *::before, html.theme-transitioning *::after {
      transition-property: color, background-color, border-color, box-shadow, fill, stroke, opacity !important;
      transition-duration: .48s !important; transition-timing-function: cubic-bezier(.2,.7,.2,1) !important;
    }
    @media (prefers-reduced-motion: reduce) {
      body::before, body::after { transition: none; }
      html.theme-transitioning, html.theme-transitioning *, html.theme-transitioning *::before, html.theme-transitioning *::after { transition: none !important; }
    }
    /* ===== END DESIGN-STEP4 ===== */
'''
# Add at the actual end of the page's sole authored style element.
assert s.count('</style>') == 1, 'Expected a single authored style block.'
s = s.replace('</style>', CSS + '\n  </style>', 1)
applied.append('coherent ambient-light + glass + separator CSS')

# Marker also appears in the CSS, serving as a visible, idempotent source anchor.
assert s.count(MARK) >= 4, 'Missing Step-4 markers.'
io.open(PAGE, 'w', encoding='utf-8').write(s)
print('\n'.join('  ✓ ' + x for x in applied))
print(f'\nDone — {len(s):,} chars / {len(s.encode("utf-8")):,} bytes')
