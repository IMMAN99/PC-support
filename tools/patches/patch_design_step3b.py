#!/usr/bin/env python3
"""
DESIGN-STEP3B — «زنده‌شدن» صفحه، بخش ب: باندهای تصویری سکشن‌ها + شمارندهٔ تعامل‌محور.

  · باند پشتیبانی ریموت (جلسهٔ ریموت + پنل سه‌ردیفه)
  · باند ذخیره‌سازی داخل کارت تست سرعت (HDD/SATA/NVMe)
  · باند تست گلوگاه (رم و پردازنده)
  · باند باریک کارگاه در پرسش‌های متداول
  · شمارندهٔ عدد سکشن گلوگاه با هر تغییر انتخاب‌ها (بدون دست‌زدن به منطق شبیه‌ساز)

تصاویر در فایل پچ به‌صورت base64 تولید می‌شوند (صفر درخواست بیرونی).
اجرا:  python3 tools/patches/patch_design_step3b.py
"""
import base64, io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P = os.path.join(ROOT, 'پشتیبان_رایانه.html')
MARK = 'DESIGN-STEP3B'
s = io.open(P, encoding='utf-8').read()
if MARK in s:
    sys.exit('این پچ قبلاً اجرا شده است — دوباره اجرا نمی‌شود.')
assert 'DESIGN-STEP3A' in s, 'بخش الف باید اول اجرا شده باشد.'


def data_uri(name):
    path = os.path.join(ROOT, 'assets', 'img', name + '.webp')
    if not os.path.exists(path):
        sys.exit(f'تصویر نیست: {path}')
    raw = io.open(path, 'rb').read()
    print(f'  · {name}.webp  {len(raw)/1024:.0f} KB')
    return 'data:image/webp;base64,' + base64.b64encode(raw).decode()


REMOTE, DRIVES, RAM, WORKSHOP = (data_uri('remote-session'), data_uri('hardware-drives'),
                                 data_uri('ram-cpu'), data_uri('workshop-detail'))

done = []


def rep(old, new, label, count=1):
    global s
    n = s.count(old)
    assert n == count, f'✗ {label}: {n} مورد (انتظار {count})\n{old[:180]}'
    s = s.replace(old, new, count)
    done.append(label)


def ic(name, cls='al-ic'):
    return (f'<svg class="{cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">'
            f'<use href="#ic-{name}"/></svg>')


# ------------------------------------------------------------------ CSS
CSS = """
    /* --- DESIGN-STEP3B: باندهای تصویری سکشن‌ها --- */
    .al-band { position: relative; margin-bottom: 2rem; border-radius: 24px; overflow: hidden;
      background: #0b0b0c; border: 1px solid rgba(0,0,0,.08); box-shadow: 0 26px 60px -44px rgba(0,0,0,.5); }
    .dark .al-band { border-color: rgba(255,255,255,.10); }
    .al-band-shot { display: block; width: 100%; height: clamp(215px, 27vw, 360px); object-fit: cover; }
    .dark .al-band-shot { filter: brightness(.9) saturate(.96); }
    .al-band--thin .al-band-shot { height: clamp(150px, 15vw, 215px); }
    .al-band .al-scrim { background: linear-gradient(90deg, rgba(0,0,0,.64) 0%, rgba(0,0,0,.16) 56%, rgba(0,0,0,0) 100%); }
    .al-band--cap .al-scrim { background: linear-gradient(180deg, rgba(0,0,0,0) 42%, rgba(0,0,0,.62) 100%); }
    .al-panel { position: absolute; inset-block: 0; inset-inline-start: 0; width: min(48%, 440px);
      display: flex; flex-direction: column; justify-content: center; gap: 13px; padding: 22px 26px; color: #fff; }
    .al-row { display: flex; align-items: flex-start; gap: 10px; }
    .al-row .al-ic { color: #fff; opacity: .92; margin-top: 1px; }
    .al-row b { display: block; font-size: 12.5px; font-weight: 800; }
    .al-row span { display: block; font-size: 11px; color: rgba(255,255,255,.78); margin-top: 2px; line-height: 1.65; }
    @media (max-width: 767px) {
      .al-panel { position: static; width: auto; padding: 15px 16px 16px; }
      .al-band .al-scrim { background: linear-gradient(180deg, rgba(0,0,0,0) 30%, rgba(0,0,0,.62) 100%); }
    }
"""
rep("""    /* هاله در هاور کمی بازتر می‌شود؛ انتقالِ ترکیبی تا با لبهٔ D-03 تعارض نکند */""",
    CSS + """
    /* هاله در هاور کمی بازتر می‌شود؛ انتقالِ ترکیبی تا با لبهٔ D-03 تعارض نکند */""",
    'بلوک CSS بخش ب')

# ------------------------------------------------------------------ ۱) باند پشتیبانی ریموت
rep("""    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 rise-stagger">""",
    f"""    <!-- DESIGN-STEP3B: باند تصویری پشتیبانی ریموت -->
    <div class="al-band rise" data-rise="1">
      <img class="al-band-shot" decoding="async" loading="lazy" width="1100" height="619"
           src="{REMOTE}"
           alt="جلسهٔ پشتیبانی ریموت: کارشناس پشت میز با هدست در حال رسیدگی به سیستم کاربر روی لپ‌تاپ">
      <span class="al-scrim" aria-hidden="true"></span>
      <div class="al-panel">
        <div class="al-row">{ic('lock')}
          <div><b>جلسهٔ امن از راه دور</b><span>دسترسی فقط با اجازهٔ شما و در همان جلسه؛ هر لحظه می‌توانید پایان دهید.</span></div>
        </div>
        <div class="al-row">{ic('chat')}
          <div><b>ابزار اتصال و راهنمای گام‌به‌گام</b><span>پیش از اتصال، لینک و راهنمای کوتاه برایتان ارسال می‌شود — بدون نصب پیچیده.</span></div>
        </div>
        <div class="al-row">{ic('shield')}
          <div><b>ویندوز، مک و لینوکس</b><span>بدون محدودیت برند و مدل سیستم؛ تنها چیزی که لازم است اینترنت است.</span></div>
        </div>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 rise-stagger">""",
    'باند پشتیبانی ریموت')

# ------------------------------------------------------------------ ۲) باند ذخیره‌سازی (داخل کارت تست سرعت)
rep("""    <div class="bg-white dark:bg-brand-darkCard rounded-[28px] p-6 sm:p-8 border border-black/[0.08] dark:border-white/[0.08] shadow-sm rise bench-card">
      <div class="flex justify-center mb-8">""",
    f"""    <div class="bg-white dark:bg-brand-darkCard rounded-[28px] p-6 sm:p-8 border border-black/[0.08] dark:border-white/[0.08] shadow-sm rise bench-card">
      <div class="al-band al-band--cap" style="margin-bottom:1.75rem">
        <img class="al-band-shot" decoding="async" loading="lazy" width="1100" height="619"
             src="{DRIVES}"
             alt="سه نوع حافظه در کنار هم: هارد مکانیکی، اس‌اس‌دی SATA و ماژول فوق‌سریع NVMe">
        <span class="al-scrim" aria-hidden="true"></span>
        <span class="al-cap">
          <span class="al-chip">از هارد مکانیکی تا NVMe Gen4 — همان تفاوتی که در اعداد زیر می‌بینید</span>
        </span>
      </div>
      <div class="flex justify-center mb-8">""",
    'باند ذخیره‌سازی')

# ------------------------------------------------------------------ ۳) باند تست گلوگاه
rep("""      <div class="bg-white dark:bg-brand-darkCard rounded-[28px] p-6 sm:p-8 border border-black/[0.08] dark:border-white/[0.08] shadow-sm rise">
        
        <!-- Selectors: Modern Frosted Glass Custom Dropdowns -->""",
    f"""      <!-- DESIGN-STEP3B: باند تصویری تست گلوگاه -->
      <div class="al-band rise" data-rise="1">
        <img class="al-band-shot" decoding="async" loading="lazy" width="1100" height="619"
             src="{RAM}"
             alt="نمای نزدیک رم و پردازندهٔ نصب‌شده روی مادربورد">
        <span class="al-scrim" aria-hidden="true"></span>
        <div class="al-panel">
          <div class="al-row">{ic('sliders')}
            <div><b>تست گلوگاه، بدون حدس</b><span>مشخصات کنونی را انتخاب کنید و نتیجه را همان لحظه ببینید.</span></div>
          </div>
          <div class="al-row">{ic('alert')}
            <div><b>گلوگاه = کُندکنندهٔ کل سیستم</b><span>قطعهٔ گلوگاه مشخص می‌شود تا ارتقا با هزینهٔ هدفمند انجام شود.</span></div>
          </div>
        </div>
      </div>

      <div class="bg-white dark:bg-brand-darkCard rounded-[28px] p-6 sm:p-8 border border-black/[0.08] dark:border-white/[0.08] shadow-sm rise">
        
        <!-- Selectors: Modern Frosted Glass Custom Dropdowns -->""",
    'باند تست گلوگاه')

# ------------------------------------------------------------------ ۴) باند باریک کارگاه در پرسش‌ها
rep("""      <div class="space-y-4 rise-stagger">""",
    f"""      <!-- DESIGN-STEP3B: باند باریک کارگاه -->
      <div class="al-band al-band--thin al-band--cap rise">
        <img class="al-band-shot" decoding="async" loading="lazy" width="900" height="506"
             src="{WORKSHOP}"
             alt="کار کارگاه با ابزار دقیق روی برد لپ‌تاپ">
        <span class="al-scrim" aria-hidden="true"></span>
        <span class="al-cap">
          <span class="al-chip">کارگاه تخصصی — کار با ابزار دقیق، فرش ضدالکتریسیته و قطعات اصل</span>
        </span>
      </div>

      <div class="space-y-4 rise-stagger">""",
    'باند کارگاه در پرسش‌ها')

# ------------------------------------------------------------------ ۵) شمارندهٔ سکشن گلوگاه (بدون تغییر منطق شبیه‌ساز)
rep("""    const AL_NUMS = ['benchBootTime', 'benchAppTime', 'benchReadSpeed'];
    const alCountAll = () => AL_NUMS.forEach(id => alCount(document.getElementById(id)));""",
    """    const AL_NUMS = ['benchBootTime', 'benchAppTime', 'benchReadSpeed'];
    const alCountAll = () => AL_NUMS.forEach(id => alCount(document.getElementById(id)));

    /* DESIGN-STEP3B: عدد گلوگاه با هر تغییرِ انتخاب‌ها از صفر شمرده می‌شود.
       با شنوندهٔ سطح سکشن کار می‌کند، پس منطق خودِ شبیه‌ساز دست‌نخورده می‌ماند. */
    const bottSec = document.getElementById('bottleneck');
    if (bottSec) {
      const alSim = () => alCount(document.getElementById('simScoreVal'), 650);
      bottSec.addEventListener('input', alSim);
      bottSec.addEventListener('click', e => { if (e.target.closest('button')) alSim(); });
    }""",
    'شمارندهٔ سکشن گلوگاه')

# ------------------------------------------------------------------ نشانگر
rep("""    /* --- DESIGN-STEP3B: باندهای تصویری سکشن‌ها --- */""",
    """    /* --- DESIGN-STEP3B: باندهای تصویری سکشن‌ها ---  [DESIGN-STEP3B] */""",
    'نشانگر DESIGN-STEP3B')

io.open(P, 'w', encoding='utf-8').write(s)
print('\n'.join(f'  ✓ {d}' for d in done))
print(f'\nDone — {len(s)} chars  ({len(s.encode("utf-8"))} bytes)')
print(f"  · باندها: {s.count('al-band ')} · نشانگر: {s.count(MARK)}")
