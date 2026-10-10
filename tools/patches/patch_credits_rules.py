"""Frozen business rules v1 for the credit system — from the shop's review of docs/credits-design.md.

Run:  python3 tools/patches/patch_credits_rules.py        (idempotent, marker: ROUND-3-CREDITS-RULES)

Frozen rules
  1. NO inactivity auto-stop in v1. A session ends only when (a) credits reach the session cap,
     (b) the balance is exhausted, or (c) the operator/customer ends it manually.
  2. 2-minute setup grace period measured from the operator's «شروع جلسه» click; billing starts
     automatically after it (grace is never billed).
  3. The operator controls Start / Pause / End; pause time is not billed.
  4. Session spend cap (default 120 credits) chosen by the customer before the session starts.
  5. Packages read as time: 60 → up to 1 hour, 300 → up to 5 hours, 900 → up to 15 hours.
  6. Website wording is explicit: «اولین ۶۰ دقیقهٔ اولین جلسهٔ ریموت شما رایگان است.»
  7. No rial pricing outside the Care plans.
"""
import io
import sys

P = "/home/user/پشتیبان_رایانه.html"
src = io.open(P, encoding="utf-8").read()

if "ROUND-3-CREDITS-RULES" in src:
    sys.exit("already applied — ROUND-3-CREDITS-RULES marker found, nothing written")

ok = []


def sub(old, new, label):
    global src
    if old not in src:
        sys.exit(f"ANCHOR NOT FOUND [{label}]:\n{old[:420]}")
    src = src.replace(old, new, 1)
    ok.append(label)


def replace_func(name, new_code, label):
    """Swap a whole top-level (4-space indented) function."""
    global src
    start = src.index(f"    function {name}(")
    nxt = src.index("\n    function ", start + 10)
    src = src[:start] + new_code.rstrip("\n") + "\n" + src[nxt + 1:]
    ok.append(label)


# ------------------------------------------------------------------ 1. CREDITS config
sub('''    const CREDITS = {
      ratePerMinute: 1,             // اعتبار مصرفی هر دقیقه پس از دورهٔ رایگان
      firstSessionFreeMinutes: 60,  // ساعت خوش‌آمد — یک بار برای هر شمارهٔ موبایل
      freeScope: 'phone',           // 'phone' = یک ساعت رایگان به‌ازای هر شماره
      demoMode: true,               // تا اتصال درگاه پرداختِ فروشگاه، شارژ «نمایشی» است
      packs: [
        { id: 'p1', credits: 60,  title: 'بستهٔ کوتاه',    hint: 'یک عیب‌یابی سریع' },
        { id: 'p2', credits: 300, title: 'بستهٔ استاندارد', hint: 'پرکاربردترین' },
        { id: 'p3', credits: 900, title: 'بستهٔ کارگاه',   hint: 'چند دستگاه / پروژه' }
      ]
    };''',
    '''    const CREDITS = {
      ratePerMinute: 1,             // اعتبار مصرفی هر دقیقه پس از دورهٔ رایگان
      firstSessionFreeMinutes: 60,  // ساعت خوش‌آمد — یک بار برای هر شمارهٔ موبایل (تصمیم فروشگاه)
      freeScope: 'phone',           // 'phone' = یک ساعت رایگان به‌ازای هر شماره
      setupGraceSeconds: 120,       // مهلت راه‌اندازی: از کلیک «شروع جلسه» تا شروع محاسبه
      sessionCapDefault: 120,       // سقف مصرف پیش‌فرض هر جلسه (اعتبار) — کاربر تأیید می‌کند
      sessionCaps: [60, 120, 300],  // گزینه‌های سقف مصرف برای انتخاب کاربر
      // قواعد قفل‌شدهٔ نسخهٔ ۱: هیچ توقف خودکار بر پایهٔ بی‌فعالیتی وجود ندارد؛
      // جلسه فقط با پر شدن سقف، تمام شدن اعتبار، یا پایان دستی (کارشناس/کاربر) بسته می‌شود.
      demoMode: true,               // تا اتصال درگاه پرداختِ فروشگاه، شارژ «نمایشی» است
      packs: [
        { id: 'p1', credits: 60,  title: 'بستهٔ کوتاه',    hint: 'یک عیب‌یابی سریع',   span: 'تا ۱ ساعت' },
        { id: 'p2', credits: 300, title: 'بستهٔ استاندارد', hint: 'پرکاربردترین',        span: 'تا ۵ ساعت' },
        { id: 'p3', credits: 900, title: 'بستهٔ کارگاه',   hint: 'چند دستگاه / پروژه', span: 'تا ۱۵ ساعت' }
      ]
    };''',
    "CREDITS: grace 2m, session cap, time-labelled packs, no inactivity rule")

# ------------------------------------------------------------------ 2. session engine
replace_func("startChargeSession", r'''    function startChargeSession(ticketCode, phone, sessionCap) {
      const p = creditNormalizePhone(phone) || creditLastPhone();
      // اگر شماره هنوز ساعت خوش‌آمد نگرفته، همین‌جا برایش ثبت می‌شود (بار اول)
      if (p) creditGrantFreeHour(p);
      const free = creditFreeRemaining(p);
      const cap = Number(sessionCap) || Number(CREDITS.sessionCapDefault) || 0;
      creditSession = {
        code: ticketCode || 'بدون کد',
        phone: p,
        freeLeft: free.left,
        cap: cap,
        startedAt: creditNow(),
        pausedTotalMs: 0,
        pauseStart: null,
        timer: null
      };
      const bar = document.getElementById('creditSessionBar');
      if (bar) bar.classList.remove('hidden');
      if (creditSession.timer) clearInterval(creditSession.timer);
      creditSession.timer = setInterval(tickChargeSession, 1000);
      tickChargeSession();
      showToast(`جلسه آغاز شد — ${creditFa(Math.round(CREDITS.setupGraceSeconds / 60 * 10) / 10 || 2)} دقیقهٔ اول فقط راه‌اندازی است و محاسبه نمی‌شود.`);
      return creditSession;
    }''', "engine: startChargeSession (grace + cap)")

replace_func("tickChargeSession", r'''    /* زمان قابل محاسبه = کل زمان − مهلت راه‌اندازی − توقف‌های موقت */
    function creditBillableMs(sess) {
      const now = creditNow();
      const graceMs = (CREDITS.setupGraceSeconds || 0) * 1000;
      const pausedNow = sess.pauseStart ? (now - sess.pauseStart) : 0;
      return Math.max(0, (now - sess.startedAt) - graceMs - sess.pausedTotalMs - pausedNow);
    }
    function creditPhase(sess) {
      if (sess.pauseStart) return 'paused';
      if ((creditNow() - sess.startedAt) < (CREDITS.setupGraceSeconds || 0) * 1000) return 'grace';
      return 'billing';
    }

    function tickChargeSession() {
      if (!creditSession) return;
      const st = creditState();
      const phase = creditPhase(creditSession);
      const charge = computeCharge(creditBillableMs(creditSession) / 60000, creditSession.freeLeft, creditSession.phone);

      const totalMinutes = Math.floor((creditNow() - creditSession.startedAt) / 60000);
      const clock = document.getElementById('creditSessionClock');
      if (clock) clock.textContent = `${String(Math.floor(totalMinutes / 60)).padStart(2, '۰')}:${String(totalMinutes % 60).padStart(2, '۰')}`.replace(/[0-9]/g, d => '۰۱۲۳۴۵۶۷۸۹'[d]);

      const phaseEl = document.getElementById('creditSessionPhase');
      if (phaseEl) {
        phaseEl.textContent = phase === 'grace' ? 'مهلت راه‌اندازی — محاسبه شروع نشده'
          : phase === 'paused' ? 'توقف موقت — محاسبه متوقف است'
          : 'در حال محاسبه';
      }
      const pauseBtn = document.getElementById('creditSessionPauseBtn');
      if (pauseBtn) pauseBtn.textContent = phase === 'paused' ? 'ادامهٔ جلسه' : 'توقف موقت';

      const freeEl = document.getElementById('creditSessionFree');
      if (freeEl) freeEl.textContent = charge.freeLeftAfter > 0
        ? `رایگان: ${creditFa(charge.freeLeftAfter)} دقیقه`
        : 'دورهٔ رایگان این شماره تمام شد';
      const burnEl = document.getElementById('creditSessionBurn');
      if (burnEl) burnEl.textContent = `${creditFa(charge.cost)} / سقف ${creditFa(creditSession.cap)} اعتبار`;

      // سقف مصرف این جلسه (تصمیم نسخهٔ ۱: فقط سقف، اعتبار صفر، یا پایان دستی)
      if (creditSession.cap > 0 && charge.cost >= creditSession.cap) {
        stopChargeSession('cap');
        showToast('سقف مصرف این جلسه پر شد؛ برای ادامه جلسهٔ تازه با سقف بالاتر شروع کنید.');
        return;
      }
      if (charge.cost > st.balance) {
        stopChargeSession('out-of-credit');
        showToast('اعتبار کافی نیست؛ جلسه بسته شد. برای ادامه کیف پول را شارژ کنید.');
      }
    }''', "engine: tick with grace / pause / cap")

replace_func("stopChargeSession", r'''    function stopChargeSession(reason) {
      if (!creditSession) return null;
      const st = creditState();
      const totalMs = creditNow() - creditSession.startedAt;
      const charge = computeCharge(creditBillableMs(creditSession) / 60000, creditSession.freeLeft, creditSession.phone);
      const affordable = Math.min(charge.cost, st.balance);
      const charged = (reason === 'cap') ? Math.min(charge.cost, creditSession.cap) : affordable;
      if (charge.phone) {
        st.freeByPhone[charge.phone] = charge.freeLeftAfter;   // ماندهٔ همین شماره به‌روز می‌شود
        st.lastPhone = charge.phone;
      }
      st.balance = Math.max(0, st.balance - Math.min(charged, st.balance));
      st.spentTotal += Math.min(charged, st.balance + Math.min(charged, st.balance)) ? Math.min(charged, st.balance) : 0;
      const summary = {
        code: creditSession.code,
        phone: charge.phone,
        phoneMasked: creditMaskPhone(charge.phone),
        minutes: charge.minutes,                       // دقیقهٔ محاسبه‌شده (پس از راه‌اندازی و توقف‌ها)
        totalMinutes: Math.floor(totalMs / 60000),     // کل زمان جلسه
        graceMinutes: Math.round((CREDITS.setupGraceSeconds || 0) / 60),
        pausedMinutes: Math.floor(creditSession.pausedTotalMs / 60000),
        freeMinutes: charge.freeUsed,
        chargedMinutes: charge.chargeable,
        cost: Math.min(charged, st.balance + charged >= 0 ? charged : charged),
        wanted: charge.cost,
        cap: creditSession.cap,
        balanceAfter: st.balance,
        freeMinutesLeft: charge.freeLeftAfter,
        reason: reason || 'user',
        endedAt: new Date().toISOString()
      };
      summary.cost = charge.chargeable > 0 ? Math.max(0, Math.min(charged, charge.cost)) : 0;
      st.sessions.unshift(summary);
      st.sessions = st.sessions.slice(0, 20);
      creditLog(st, 'session', -summary.cost,
        `جلسهٔ ${creditSession.code} (${summary.phoneMasked}): ${creditFa(summary.minutes)} دقیقه محاسبه — ${creditFa(charge.freeUsed)} دقیقه رایگان${summary.cap ? ` · سقف ${creditFa(summary.cap)}` : ''}`);
      if (creditSession.timer) clearInterval(creditSession.timer);
      creditSession = null;
      creditSave(st);
      const bar = document.getElementById('creditSessionBar');
      if (bar) bar.classList.add('hidden');
      // جلسه در تیکت هم ثبت می‌شود تا در ماژول پیگیری دیده شود
      try {
        const tickets = JSON.parse(localStorage.getItem('poshtiban_tickets') || '{}');
        const t = tickets[summary.code];
        if (t) {
          t.credits = { minutes: summary.minutes, totalMinutes: summary.totalMinutes, freeMinutes: summary.freeMinutes,
                        cost: summary.cost, cap: summary.cap, phone: summary.phone, freeMinutesLeft: summary.freeMinutesLeft };
          t.creditsText = `${summary.phoneMasked} · ${creditFa(summary.totalMinutes)} دقیقه جلسه · رایگان: ${creditFa(summary.freeMinutes)} دقیقه · مصرف: ${creditFa(summary.cost)} اعتبار`;
          localStorage.setItem('poshtiban_tickets', JSON.stringify(tickets));
        }
      } catch (e) {}
      return summary;
    }

    /* کنترل‌های کارشناس: توقف موقت / ادامه — زمان توقف محاسبه نمی‌شود */
    function pauseChargeSession() {
      if (!creditSession) return null;
      if (creditSession.pauseStart) {                      // ادامه
        creditSession.pausedTotalMs += creditNow() - creditSession.pauseStart;
        creditSession.pauseStart = null;
        showToast('جلسه ادامه یافت — محاسبه از همین لحظه.');
      } else {                                             // توقف موقت
        creditSession.pauseStart = creditNow();
        showToast('جلسه موقتاً متوقف شد — زمان توقف محاسبه نمی‌شود.');
      }
      tickChargeSession();
      return creditSession;
    }
    function sessionCapChip(cap) { return creditFa(cap); }''', "engine: stop/pause with grace + cap accounting")

# ------------------------------------------------------------------ 3. session bar UI
sub('''      <div class="flex items-center gap-2 min-w-0">
        <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse shrink-0"></span>
        <b id="creditSessionTitle" class="text-[11px] font-bold whitespace-nowrap">جلسهٔ ریموت فعال</b>
        <span id="creditSessionClock" class="text-[11px] font-mono tabular-nums whitespace-nowrap">۰۰:۰۰</span>
      </div>
      <div class="flex items-center gap-2.5 text-[10px] font-semibold whitespace-nowrap">
        <span id="creditSessionFree" class="text-emerald-300 dark:text-emerald-600">رایگان</span>
        <span id="creditSessionBurn" class="text-amber-300 dark:text-amber-600">۰ اعتبار</span>
        <button onclick="stopChargeSession('user')" class="px-2.5 py-1 rounded-full bg-white/15 dark:bg-black/10 hover:bg-white/25 transition text-[10px] font-bold">پایان جلسه</button>
      </div>''',
    '''      <div class="flex items-center gap-2 min-w-0">
        <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse shrink-0"></span>
        <b id="creditSessionTitle" class="text-[11px] font-bold whitespace-nowrap">جلسهٔ ریموت</b>
        <span id="creditSessionClock" class="text-[11px] font-mono tabular-nums whitespace-nowrap">۰۰:۰۰</span>
      </div>
      <div class="flex flex-wrap items-center justify-end gap-2 text-[10px] font-semibold">
        <span id="creditSessionPhase" class="text-white/80 dark:text-brand-dark/80 whitespace-nowrap">مهلت راه‌اندازی — محاسبه شروع نشده</span>
        <span id="creditSessionFree" class="text-emerald-300 dark:text-emerald-600 whitespace-nowrap">رایگان</span>
        <span id="creditSessionBurn" class="text-amber-300 dark:text-amber-600 whitespace-nowrap">۰ / سقف ۱۲۰ اعتبار</span>
        <button onclick="pauseChargeSession()" id="creditSessionPauseBtn" class="px-2.5 py-1 rounded-full bg-white/15 dark:bg-black/10 hover:bg-white/25 transition text-[10px] font-bold">توقف موقت</button>
        <button onclick="stopChargeSession('user')" class="px-2.5 py-1 rounded-full bg-white/15 dark:bg-black/10 hover:bg-white/25 transition text-[10px] font-bold">پایان جلسه</button>
      </div>''',
    "session bar: phase + pause control + cap")

# ------------------------------------------------------------------ 4. cap choice before start
sub('''<div class="mt-4 p-3 rounded-2xl bg-brand-lightGray dark:bg-[#161617] border border-black/[0.06] dark:border-white/[0.06] text-[11px] text-brand-gray leading-relaxed">
اعتبار جلسه: <b id="remoteSuccessCredit" class="text-brand-dark dark:text-white">۶۰ دقیقهٔ اول رایگان</b>
<div class="mt-2">
<button type="button" onclick="startChargeSession(document.getElementById('remoteSuccessCode').textContent.trim())" class="w-full py-2 rounded-full bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/25 text-[11px] font-bold hover:bg-emerald-500/20 transition">شبیه‌سازی اتصال کارشناس و شروع محاسبهٔ اعتبار</button>
</div>
</div>''',
    '''<div class="mt-4 p-3 rounded-2xl bg-brand-lightGray dark:bg-[#161617] border border-black/[0.06] dark:border-white/[0.06] text-[11px] text-brand-gray leading-relaxed">
اعتبار جلسه: <b id="remoteSuccessCredit" class="text-brand-dark dark:text-white">اولین ۶۰ دقیقهٔ اولین جلسهٔ ریموت شما رایگان است</b>
<div class="mt-3">
  <span class="block font-bold text-brand-dark dark:text-white mb-1.5">حداکثر مصرف این جلسه (تأیید شما):</span>
  <div id="sessionCapChoices" class="flex flex-wrap gap-1.5"></div>
  <p class="text-[10px] text-brand-gray mt-1.5">تا این سقف، جلسه بسته نمی‌شود؛ بعد از آن کارشناس متوقف می‌شود. ۲ دقیقهٔ اول فقط راه‌اندازی است و محاسبه نمی‌شود.</p>
  <button type="button" id="sessionStartBtn" onclick="startSessionFromSuccess()" class="mt-2 w-full py-2 rounded-full bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/25 text-[11px] font-bold hover:bg-emerald-500/20 transition">شروع جلسه (کارشناس متصل شد)</button>
</div>
</div>''',
    "success view: cap choice + operator start")

# ------------------------------------------------------------------ 5. JS for the two bits above
sub('    function openWalletModal() {',
    '''    /* انتخاب سقف مصرف جلسه — پیش از شروع، با تأیید کاربر (قاعدهٔ قفل‌شدهٔ نسخهٔ ۱) */
    let chosenSessionCap = null;
    function renderSessionCapChoices() {
      const wrap = document.getElementById('sessionCapChoices');
      if (!wrap) return;
      if (chosenSessionCap === null) chosenSessionCap = CREDITS.sessionCapDefault;
      wrap.innerHTML = CREDITS.sessionCaps.map(c => `
        <button type="button" onclick="chooseSessionCap(${c})" aria-pressed="${c === chosenSessionCap}"
                class="px-2.5 py-1 rounded-full text-[10px] font-bold border transition ${c === chosenSessionCap
                  ? 'bg-brand-blue text-white border-brand-blue'
                  : 'bg-white/60 dark:bg-white/5 text-brand-dark dark:text-white border-black/[0.08] dark:border-white/[0.08] hover:border-brand-blue'}">
          ${creditFa(c)} اعتبار
        </button>`).join('');
    }
    function chooseSessionCap(cap) {
      chosenSessionCap = Number(cap) || CREDITS.sessionCapDefault;
      renderSessionCapChoices();
    }
    function startSessionFromSuccess() {
      const code = (document.getElementById('remoteSuccessCode') || {}).textContent || '';
      const phone = (document.getElementById('remotePhoneInput') || {}).value || '';
      startChargeSession(code.trim(), phone, chosenSessionCap || CREDITS.sessionCapDefault);
    }

    function openWalletModal() {''',
    "JS: cap chooser + operator start")

sub('''      const sumEl = document.getElementById('remoteSuccessCredit');
      if (sumEl) {''',
    '''      renderSessionCapChoices();
      const sumEl = document.getElementById('remoteSuccessCredit');
      if (sumEl) {''',
    "render caps with the wallet")

sub('''          const last = creditFreeRemaining(creditLastPhone());
          sumEl.textContent = !last.phone
            ? 'ساعت خوش‌آمد: ۶۰ دقیقه برای شمارهٔ شما'
            : last.known && last.left > 0
              ? `ساعت خوش‌آمد شمارهٔ ${creditMaskPhone(last.phone)}: ${creditFa(last.left)} دقیقه باقی مانده`
              : `شمارهٔ ${creditMaskPhone(last.phone)}: دورهٔ رایگان استفاده شده`;''',
    '''          const last = creditFreeRemaining(creditLastPhone());
          sumEl.textContent = !last.phone
            ? 'اولین ۶۰ دقیقهٔ اولین جلسهٔ ریموت شما رایگان است'
            : last.known && last.left > 0
              ? `اولین جلسهٔ شمارهٔ ${creditMaskPhone(last.phone)}: ${creditFa(last.left)} دقیقه رایگان باقی است`
              : `شمارهٔ ${creditMaskPhone(last.phone)}: اولین جلسهٔ رایگان مصرف شده — هر دقیقه ${creditFa(CREDITS.ratePerMinute)} اعتبار`;''',
    "success line: explicit welcome-hour wording")

# ------------------------------------------------------------------ 6. explicit wording + pack spans
sub('جلسهٔ ریموت بر اساس مدت‌زمان کارشناس محاسبه می‌شود؛ <b>اولین ۶۰ دقیقهٔ اولین جلسه برای هر شمارهٔ موبایل یک بار رایگان است</b> و بعد از آن به‌ازای هر دقیقه اعتبار کم می‌شود.',
    '<b>اولین ۶۰ دقیقهٔ اولین جلسهٔ ریموت شما رایگان است</b> — این ساعت خوش‌آمد یک بار به شمارهٔ موبایل شما تعلق می‌گیرد و بعد از آن هر دقیقه یک اعتبار کم می‌شود. ۲ دقیقهٔ اول هر جلسه هم فقط راه‌اندازی است و محاسبه نمی‌شود.',
    "wallet copy: explicit welcome hour + grace")

sub('''        noteEl.textContent = 'اولین ۶۰ دقیقهٔ اولین جلسه، برای هر شمارهٔ موبایل یک بار رایگان است';
        return;''',
    '''        noteEl.textContent = 'اولین ۶۰ دقیقهٔ اولین جلسهٔ ریموت شما رایگان است';
        return;''',
    "chip copy: explicit welcome hour")

sub('''            <b class="block text-sm font-black text-brand-blue">${creditFa(p.credits)}</b>
            <span class="block text-[10px] text-brand-gray">اعتبار</span>
            <span class="block text-[10px] font-bold text-brand-dark dark:text-white mt-1">${p.title}</span>
            <span class="block text-[10px] text-brand-gray">${p.hint}</span>''',
    '''            <b class="block text-sm font-black text-brand-blue">${creditFa(p.credits)}</b>
            <span class="block text-[10px] text-brand-gray">اعتبار — ${p.span}</span>
            <span class="block text-[10px] font-bold text-brand-dark dark:text-white mt-1">${p.title}</span>
            <span class="block text-[10px] text-brand-gray">${p.hint}</span>''',
    "wallet packs: credits + «تا …»")

# ------------------------------------------------------------------ marker
sub('<!-- ROUND-3-CREDITS-PHONE:',
    '''<!-- ROUND-3-CREDITS-RULES: business rules frozen for v1 — 2-minute setup grace from the operator's
     «شروع جلسه» click, operator-controlled start/pause/end, customer-confirmed session spend cap,
     NO inactivity auto-stop (only cap / zero balance / manual end), packages labelled as time,
     explicit «اولین ۶۰ دقیقهٔ اولین جلسهٔ ریموت شما رایگان است» wording. -->
<!-- ROUND-3-CREDITS-PHONE:''',
    "marker")

io.open(P, "w", encoding="utf-8").write(src)
for label in ok:
    print(f"  ✓ {label}")
print(f"\nDone — {len(src)} chars written.")
