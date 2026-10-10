#!/usr/bin/env python3
"""
DESIGN-STEP3A — «زنده‌شدن» صفحه، بخش الف (هیرو + ضربان زنده).

زمینه: کارفرما گفت «سایت هنوز مرده و خالی است» (۲۰۲۶-۱۰-۰۷). تصمیم‌های تأییدشده:
  · تصویر: همین حالا تصاویر ساخته‌شده (AI) جاسازی شوند (base64 — صفر درخواست بیرونی)
  · حرکت: «متوسط» — ساعت زنده، پنل وضعیت زنده، شمارندهٔ اعداد، عناصر فنی شناور (D-06)،
          پارالاکس ملایم ماوس (D-07)، تنفس گرادیان هیرو
  · چگالی: فقط پرکردن جاهای خالی با تصویر/پنل — هیچ آمار/نظر/عدد جعلی

این پچ:
  ۱) صحنهٔ تصویری هیرو (عکس میز کار) با پنل‌های شیشه‌ای زنده (وضعیت + ساعت تهران)
  ۲) عناصر فنی شناور (D-06) و پارالاکس ملایم (D-07) — فقط دسکتاپ، فقط حرکت مجاز
  ۳) شمارندهٔ اعداد سنجش (۷ / ۲.۴ / ۵٬۰۰۰) در اولین دیدن + با هر کلیک SSD/SATA/HDD
  ۴) تنفس آرام گرادیان محیطی هیرو (D-01 هیچ‌کدام از قیدهایش عوض نمی‌شود)
  ۵) پنل زنده از همان وضعیت واقعی حضور تغذیه می‌شود (renderPresence)

قواعد: صفر درخواست بیرونی · prefers-reduced-motion محترم · بدون تغییر متن/قیمت/قاعدهٔ کسب‌وکار
اجرا:  python3 tools/patches/patch_design_step3a.py     (یک‌بار — نشانگر محافظت می‌کند)
"""
import base64, io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P = os.path.join(ROOT, 'پشتیبان_رایانه.html')
MARK = 'DESIGN-STEP3A'
s = io.open(P, encoding='utf-8').read()
if MARK in s:
    sys.exit('این پچ قبلاً اجرا شده است — دوباره اجرا نمی‌شود.')
assert 'DESIGN-STEP2' in s, 'گام ۲ باید اول اجرا شده باشد.'


def data_uri(name):
    path = os.path.join(ROOT, 'assets', 'img', name + '.webp')
    if not os.path.exists(path):
        sys.exit(f'تصویر نیست: {path}  →  اول «python3 tools/ops/make_images.py» را اجرا کنید.')
    raw = io.open(path, 'rb').read()
    print(f'  · {name}.webp  {len(raw)/1024:.0f} KB  →  base64 {len(base64.b64encode(raw))/1024:.0f} KB')
    return 'data:image/webp;base64,' + base64.b64encode(raw).decode()


done = []


def rep(old, new, label, count=1):
    global s
    n = s.count(old)
    assert n == count, f'✗ {label}: {n} مورد پیدا شد (انتظار {count})\n{old[:200]}'
    s = s.replace(old, new, count)
    done.append(label)


HERO_IMG = data_uri('hero-bench')

# ------------------------------------------------------------------ ۱) CSS
CSS = """
    /* ===== DESIGN-STEP3A — «زنده‌شدن» صفحه: تصویر + پنل زنده + ساعت + شمارنده + پارالاکس ===== */
    /* صحنهٔ تصویری (هیرو): عکس تمام‌عرض کارت، با نوار تیرهٔ پایین برای خوانایی متن روی عکس */
    .al-stage { position: relative; margin-top: 2.5rem; border-radius: 28px; overflow: hidden;
      background: #0b0b0c; border: 1px solid rgba(0,0,0,.08); box-shadow: 0 34px 70px -46px rgba(0,0,0,.55); }
    .dark .al-stage { border-color: rgba(255,255,255,.10); }
    .al-shot { display: block; width: 100%; height: clamp(250px, 40vw, 520px); object-fit: cover; }
    .dark .al-shot { filter: brightness(.9) saturate(.96); }
    .al-scrim { position: absolute; inset: 0; pointer-events: none;
      background: linear-gradient(180deg, rgba(0,0,0,.20) 0%, rgba(0,0,0,0) 36%, rgba(0,0,0,.62) 100%); }
    .al-cap { position: absolute; inset-inline: 0; bottom: 0; display: flex; flex-wrap: wrap; align-items: center;
      gap: 8px; padding: 14px 16px; color: #fff; }
    .al-chip { display: inline-flex; align-items: center; gap: 6px; padding: 6px 11px; border-radius: 999px;
      font-size: 11px; font-weight: 700; background: rgba(255,255,255,.16); border: 1px solid rgba(255,255,255,.24);
      -webkit-backdrop-filter: blur(6px); backdrop-filter: blur(6px); }
    .al-chip svg { width: 14px; height: 14px; flex: 0 0 auto; }
    /* پنل‌های شیشه‌ای شناور روی عکس */
    .al-float { position: absolute; display: inline-flex; align-items: center; gap: 8px; padding: 9px 12px;
      border-radius: 16px; font-size: 11px; font-weight: 700; color: #1d1d1f;
      background: rgba(255,255,255,.92); border: 1px solid rgba(0,0,0,.08);
      box-shadow: 0 18px 44px -22px rgba(0,0,0,.5);
      -webkit-backdrop-filter: blur(10px); backdrop-filter: blur(10px); }
    .dark .al-float { color: #f5f5f7; background: rgba(22,22,23,.86); border-color: rgba(255,255,255,.14); }
    .al-float--start { top: 14px; inset-inline-start: 14px; }
    .al-float--end { bottom: 58px; inset-inline-end: 14px; }
    .al-dot { width: 8px; height: 8px; border-radius: 999px; flex: 0 0 auto; background: #10b981;
      box-shadow: 0 0 0 4px rgba(16,185,129,.18); }
    .al-dot[data-state="queue"] { background: #f59e0b; box-shadow: 0 0 0 4px rgba(245,158,11,.18); }
    .al-dot.pulse { animation: alDotPulse 2.2s cubic-bezier(.4,0,.6,1) infinite; }
    @keyframes alDotPulse { 0%, 100% { opacity: 1; } 50% { opacity: .45; } }
    .al-ic { width: 16px; height: 16px; flex: 0 0 auto; color: #0071e3; }
    .al-tl { display: flex; flex-direction: column; line-height: 1.3; }
    .al-t1 { font-size: 9px; font-weight: 700; color: #86868b; }
    .dark .al-t1 { color: #a1a1a6; }
    .al-t2 { font-size: 12px; font-weight: 800; font-variant-numeric: tabular-nums; }
    /* عناصر فنی شناور (D-06) — آرام، کم‌رنگ، فقط تزئینی */
    .al-drift { position: absolute; color: #fff; opacity: .5; pointer-events: none;
      filter: drop-shadow(0 2px 6px rgba(0,0,0,.35)); animation: alDrift 11s ease-in-out infinite alternate; }
    @keyframes alDrift { from { translate: 0 0; } to { translate: 0 -16px; } }
    @media (prefers-reduced-motion: reduce) {
      .al-drift, .al-dot.pulse { animation: none; }
    }
    /* موبایل: پنل‌های شناور و عناصر شناور پنهان می‌شوند (نه روی متن، نه زیر دکمهٔ شناور) */
    @media (max-width: 639px) { .al-float, .al-drift { display: none; } }
    /* D-01 — تنفس آرام پرتو محیطی هیرو (فقط حرکت مجاز؛ هیچ‌کدام از ویژگی‌های سنجیده‌شدهٔ D-01 عوض نمی‌شود) */
    @media (prefers-reduced-motion: no-preference) {
      #overview::before { animation: alAuroraA 28s ease-in-out infinite alternate; }
      #overview::after { animation: alAuroraB 34s ease-in-out infinite alternate; }
    }
    @keyframes alAuroraA { from { transform: translate3d(0, 0, 0) scale(1); } to { transform: translate3d(-3.5%, 2.5%, 0) scale(1.07); } }
    @keyframes alAuroraB { from { transform: translate3d(0, 0, 0) scale(1); } to { transform: translate3d(3%, -2%, 0) scale(1.05); } }
"""
rep("""    /* هاله در هاور کمی بازتر می‌شود؛ انتقالِ ترکیبی تا با لبهٔ D-03 تعارض نکند */""",
    CSS + """
    /* هاله در هاور کمی بازتر می‌شود؛ انتقالِ ترکیبی تا با لبهٔ D-03 تعارض نکند */""",
    'بلوک CSS گام ۳ الف')

# ------------------------------------------------------------------ ۲) صحنهٔ زندهٔ هیرو
STAGE = """    <!-- DESIGN-STEP3A: صحنهٔ زندهٔ کارگاه — تصویر + پنل‌های زنده -->
    <div class="al-stage rise" data-rise="5" id="alHeroStage">
      <img class="al-shot" data-al-depth="6" width="1280" height="720" decoding="async"
           src="__HERO__"
           alt="میز کار کارگاه پشتیبان پی‌سی: لپ‌تاپ باز روی فرش کار آبی، پیچ‌گوشتی‌های دقیق، جعبهٔ قطعات و ابزار سنجش">

      <span class="al-scrim" aria-hidden="true"></span>

      <!-- عناصر فنی شناور (D-06) -->
      <svg class="al-drift" style="top:15%;inset-inline-start:5%;width:30px;height:30px" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><use href="#ic-sliders"/></svg>
      <svg class="al-drift" style="top:64%;inset-inline-start:9%;width:24px;height:24px;animation-delay:-4s" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><use href="#ic-shield"/></svg>
      <svg class="al-drift" style="top:20%;inset-inline-end:7%;width:26px;height:26px;animation-delay:-7s" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><use href="#ic-lock"/></svg>

      <!-- پنل زنده: از همان وضعیت واقعی حضور تغذیه می‌شود (renderPresence) -->
      <span class="al-float al-float--start" data-al-depth="14" role="status" aria-live="polite">
        <span class="al-dot pulse" id="alLiveDot" data-state="online" aria-hidden="true"></span>
        <span id="alLiveText">پشتیبانی ریموت شبانه‌روزی — کارشناس آمادهٔ اتصال</span>
      </span>

      <!-- ساعت تهران (زنده) -->
      <span class="al-float al-float--end" data-al-depth="12" aria-hidden="true">
        <svg class="al-ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><use href="#ic-clock"/></svg>
        <span class="al-tl">
          <span class="al-t1">هم‌اکنون — ساعت تهران</span>
          <span class="al-t2" id="alClock">—</span>
        </span>
      </span>

      <span class="al-cap">
        <span class="al-chip">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><use href="#ic-building"/></svg>
          کارگاه تخصصی — میرداماد، مجتمع کامپیوتر پایتخت، واحد ۲۰۴
        </span>
        <span class="al-chip">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><use href="#ic-calendar"/></svg>
          پذیرش حضوری: شنبه تا چهارشنبه، ۱۰:۰۰ تا ۱۷:۰۰
        </span>
      </span>
    </div>

    <!-- Bento Grid Showcase -->"""
STAGE = STAGE.replace('__HERO__', HERO_IMG)      # جاسازی base64 تصویر هیرو
rep("""    <!-- Bento Grid Showcase -->""", STAGE, 'صحنهٔ زندهٔ هیرو')

# ------------------------------------------------------------------ ۳) پنل زنده از وضعیت واقعی
rep("""      const drawerDot = document.getElementById('drawerPresenceDot');
      if (drawerDot) drawerDot.className = online
        ? 'w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse'
        : 'w-1.5 h-1.5 rounded-full bg-amber-500';""",
    """      const drawerDot = document.getElementById('drawerPresenceDot');
      if (drawerDot) drawerDot.className = online
        ? 'w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse'
        : 'w-1.5 h-1.5 rounded-full bg-amber-500';

      /* DESIGN-STEP3A: پنل زندهٔ صحنهٔ هیرو هم از همین وضعیت واقعی تغذیه می‌شود */
      if (window.alRenderLive) alRenderLive(online, n);""",
    'اتصال پنل زنده به renderPresence')

# ------------------------------------------------------------------ ۴) اسکریپت زنده
SCRIPT = """
  <!-- DESIGN-STEP3A — ضربان زندهٔ صفحه: ساعت تهران، پنل وضعیت، شمارندهٔ اعداد، پارالاکس ملایم -->
  <script>
  (function () {
    const reduced = () => matchMedia('(prefers-reduced-motion: reduce)').matches;
    const AL_FA = '۰۱۲۳۴۵۶۷۸۹';
    const alFa = str => String(str).replace(/\\d/g, d => AL_FA[+d]);

    /* ---------- ساعت تهران (زنده، بدون منبع بیرونی) ---------- */
    let alTimeFmt = null;
    try {
      alTimeFmt = new Intl.DateTimeFormat('fa-IR', { timeZone: 'Asia/Tehran', hour: '2-digit', minute: '2-digit', second: '2-digit' });
    } catch (e) { alTimeFmt = null; }
    function alTick() {
      const el = document.getElementById('alClock');
      if (!el || document.hidden) return;
      try { el.textContent = alTimeFmt ? alTimeFmt.format(new Date()) : ''; } catch (e) { /* بی‌صدا */ }
    }
    alTick();
    setInterval(alTick, 1000);
    document.addEventListener('visibilitychange', alTick);

    /* ---------- پنل زندهٔ وضعیت — آینهٔ همان وضعیت واقعی هدر ---------- */
    window.alRenderLive = function (online, n) {
      const dot = document.getElementById('alLiveDot');
      const txt = document.getElementById('alLiveText');
      if (!dot || !txt) return;
      if (typeof online !== 'boolean') {          // حالت اطمینان: از DOM بخوان
        const bd = document.getElementById('shopHoursStatusDot');
        online = !!bd && /emerald/.test(bd.className);
        const bt = (document.getElementById('shopHoursStatusText') || {}).textContent || '';
        const digits = bt.replace(/[^\\u06F0-\\u06F9\\d]/g, '').replace(/[\\u06F0-\\u06F9]/g, d => String(d.charCodeAt(0) - 0x06F0));
        n = parseInt(digits, 10) || 0;
      }
      dot.dataset.state = online ? 'online' : 'queue';
      dot.className = online ? 'al-dot pulse' : 'al-dot';
      txt.textContent = online
        ? ((n > 0 ? alFa(n) + ' کارشناس آنلاین — ' : 'کارشناس آنلاین — ') + 'اتصال همین حالا ممکن است')
        : 'درخواست‌ها در صف — اولین کارشناس تماس می‌گیرد';
    };

    /* ---------- شمارندهٔ اعداد (فقط حرکت مجاز) ---------- */
    function alFmt(n, dec) {
      const str = dec ? n.toFixed(dec).replace('.', '٫')
                      : Math.round(n).toLocaleString('en-US').replace(/,/g, '٬');
      return alFa(str);
    }
    function alCount(el, dur) {
      if (!el) return;
      const m = el.textContent.trim().match(/^([\\d\\u06F0-\\u06F9,٬٫.]+)\\s*(.*)$/);
      if (!m) return;
      const target = parseFloat(m[1]
        .replace(/[\\u06F0-\\u06F9]/g, d => String(d.charCodeAt(0) - 0x06F0))
        .replace(/[٬,]/g, '').replace('٫', '.'));
      if (!isFinite(target) || target <= 0) return;
      const unit = m[2] ? ' ' + m[2].trim() : '';
      const dec = /[٫.]/.test(m[1]) ? 1 : 0;
      if (reduced()) { el.textContent = alFmt(target, dec) + unit; return; }
      const t0 = performance.now();
      const total = dur || 900;
      (function step(now) {
        const p = Math.min(1, (now - t0) / total);
        const e = 1 - Math.pow(1 - p, 3);
        el.textContent = alFmt(target * e, dec) + unit;
        if (p < 1) requestAnimationFrame(step);
      })(t0);
    }
    const AL_NUMS = ['benchBootTime', 'benchAppTime', 'benchReadSpeed'];
    const alCountAll = () => AL_NUMS.forEach(id => alCount(document.getElementById(id)));

    /* با هر کلیک SSD/SATA/HDD اعداد از صفر شمرده می‌شوند (تعامل قبلی دست‌نخورده می‌ماند) */
    if (typeof setStorageBenchmark === 'function') {
      const alOrigBench = setStorageBenchmark;
      window.setStorageBenchmark = function (t) { alOrigBench(t); alCountAll(); };
    }
    /* اولین باری که سکشن تست سرعت دیده می‌شود */
    const benchSec = document.getElementById('speed-booster');
    if (benchSec && 'IntersectionObserver' in window) {
      const io = new IntersectionObserver(es => {
        es.forEach(e => { if (e.isIntersecting) { alCountAll(); io.disconnect(); } });
      }, { threshold: .25 });
      io.observe(benchSec);
    }

    /* ---------- پارالاکس ملایم محیطی (D-07) — فقط دسکتاپِ اشاره‌گر دقیق و حرکت مجاز ---------- */
    const stage = document.getElementById('alHeroStage');
    if (stage && !reduced() && matchMedia('(hover: hover) and (pointer: fine)').matches) {
      const layers = [...stage.querySelectorAll('[data-al-depth]')];
      stage.addEventListener('mousemove', e => {
        const r = stage.getBoundingClientRect();
        const x = (e.clientX - r.left) / r.width - .5;
        const y = (e.clientY - r.top) / r.height - .5;
        layers.forEach(l => {
          const d = parseFloat(l.dataset.alDepth) || 4;
          l.style.translate = (-x * d).toFixed(1) + 'px ' + (-y * d).toFixed(1) + 'px';
        });
      });
      stage.addEventListener('mouseleave', () => layers.forEach(l => { l.style.translate = ''; }));
    }

    /* ---------- آینه‌کاری وضعیت هر چند ثانیه (اگر renderPresence دیرتر اجرا شود) ---------- */
    setInterval(() => { if (!document.hidden) window.alRenderLive(); }, 7000);
    window.alRenderLive();
  })();
  </script>

"""
rep("</body>", SCRIPT + "</body>", 'اسکریپت زندهٔ صفحه')

# ------------------------------------------------------------------ نشانگر
rep("""    /* ===== DESIGN-STEP3A — «زنده‌شدن» صفحه: تصویر + پنل زنده + ساعت + شمارنده + پارالاکس ===== */""",
    """    /* ===== DESIGN-STEP3A — «زنده‌شدن» صفحه: تصویر + پنل زنده + ساعت + شمارنده + پارالاکس =====  [DESIGN-STEP3A] */""",
    'نشانگر DESIGN-STEP3A')

io.open(P, 'w', encoding='utf-8').write(s)
print('\n'.join(f'  ✓ {d}' for d in done))
print(f'\nDone — {len(s)} chars  ({len(s.encode("utf-8"))} bytes)')
print(f"  · نشانگر: {s.count(MARK)} · صحنه: {s.count('al-stage')} · پنل زنده: {s.count('alLiveText')}")
