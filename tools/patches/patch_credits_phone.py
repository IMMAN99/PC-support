"""Credit system, decision #1 — the free hour is tied to the phone number (one per person).

Run:  python3 tools/patches/patch_credits_phone.py        (idempotent, marker: ROUND-3-CREDITS-PHONE)

Shop decision: «اولین ۶۰ دقیقهٔ اولین جلسه، برای هر شمارهٔ موبایل، یک بار.»
This patch re-cuts the wallet engine so the welcome hour is keyed to the phone number:
  * `CREDITS.freeScope = 'phone'` + `freeByPhone`/`grants` ledgers (migrated from the old global field)
  * the grant is created on the first remote request from a phone, never again for that phone
  * a session started from a ticket binds to that phone; its free minutes come from that phone's ledger
  * UI: the chip inside the remote modal follows what is typed in the phone field, the wallet lists the
    registered numbers (masked) with their remaining free minutes, and the tracking ticket records it
  * client-side limitation is stated in the UI copy; real «one per person» = SMS OTP on the backend
"""
import io
import sys

P = "/home/user/پشتیبان_رایانه.html"
src = io.open(P, encoding="utf-8").read()

if "ROUND-3-CREDITS-PHONE" in src:
    sys.exit("already applied — ROUND-3-CREDITS-PHONE marker found, nothing written")

ok = []


def sub(old, new, label):
    global src
    if old not in src:
        sys.exit(f"ANCHOR NOT FOUND [{label}]:\n{old[:420]}")
    src = src.replace(old, new, 1)
    ok.append(label)


# ---------------------------------------------------------------- 1. UI copy + placeholders
sub('جلسهٔ ریموت بر اساس مدت‌زمان کارشناس محاسبه می‌شود؛ <b>اولین ۶۰ دقیقهٔ اولین جلسهٔ شما رایگان است</b> و بعد از آن به‌ازای هر دقیقه اعتبار کم می‌شود.',
    'جلسهٔ ریموت بر اساس مدت‌زمان کارشناس محاسبه می‌شود؛ <b>اولین ۶۰ دقیقهٔ اولین جلسه برای هر شمارهٔ موبایل یک بار رایگان است</b> و بعد از آن به‌ازای هر دقیقه اعتبار کم می‌شود.',
    "copy: one welcome hour per phone number")

sub('''        <div class="text-left">
          <span class="text-[11px] text-brand-gray block">دورهٔ رایگان باقی‌مانده</span>
          <b id="walletFreeMinutes" class="text-lg font-bold text-emerald-600 dark:text-emerald-400">۶۰ دقیقه</b>
        </div>''',
    '''        <div class="text-left">
          <span class="text-[11px] text-brand-gray block">دورهٔ رایگان این شماره</span>
          <b id="walletFreeMinutes" class="text-lg font-bold text-emerald-600 dark:text-emerald-400">۶۰ دقیقه</b>
        </div>''',
    "wallet: per-phone free-hour label")

sub('''      <div class="mt-4">
        <span class="text-[11px] font-bold text-brand-dark dark:text-white block mb-2">شارژ اعتبار</span>''',
    '''      <div class="mt-4">
        <span class="text-[11px] font-bold text-brand-dark dark:text-white block mb-1.5">شماره‌های ثبت‌شده برای ساعت خوش‌آمد</span>
        <div id="walletFreeList" class="space-y-1.5 text-[11px] mb-1"></div>
        <p class="text-[10px] text-brand-gray leading-relaxed">ساعت اول رایگان به شمارهٔ موبایل گره خورده است: هر شماره یک بار. تأیید نهایی شماره با کد پیامکی، به‌محض فعال‌شدن پنل کاربری، انجام می‌شود.</p>
      </div>

      <div class="mt-4">
        <span class="text-[11px] font-bold text-brand-dark dark:text-white block mb-2">شارژ اعتبار</span>''',
    "wallet: registered-numbers block")

sub('<input type="tel" id="remotePhoneInput" required placeholder="۰۹۱۲۳۴۵۶۷۸۹" dir="ltr"',
    '<input type="tel" id="remotePhoneInput" required placeholder="۰۹۱۲۳۴۵۶۷۸۹" dir="ltr" oninput="updateRemoteCreditChip()"',
    "remote form: chip follows the typed phone")

# ---------------------------------------------------------------- 2. grant on submit
sub('''      if (nextEl) {''',
    '''      // ROUND-3 (phone scope): ساعت خوش‌آمد برای این شماره یک بار ثبت می‌شود
      creditGrantFreeHour(phone);
      try { localStorage.setItem('poshtiban_last_phone', phone); } catch (e) {}

      if (nextEl) {''',
    "submit: grant the welcome hour to this phone")

# ---------------------------------------------------------------- 3. new engine
START = src.index('    /* ================= ROUND-3: سیستم اعتبار (کیف پول) ================= */')
END = src.index('    function openWalletModal() {')
old_engine = src[START:END]

NEW_ENGINE = r'''    /* ================= ROUND-3: سیستم اعتبار (کیف پول) =================
       تصمیم فروشگاه (بند ۱): «ساعت خوش‌آمد» به شمارهٔ موبایل گره خورده است — هر شماره، یک بار.
       در این نسخهٔ فرانت‌اند شماره از فرم درخواست ریموت گرفته می‌شود؛ تأیید واقعیِ «هر شخص»
       با کد پیامکی (OTP) و روی سرور انجام می‌شود (نگاه کنید به docs/credits-design.md). */
    const CREDITS = {
      ratePerMinute: 1,             // اعتبار مصرفی هر دقیقه پس از دورهٔ رایگان
      firstSessionFreeMinutes: 60,  // ساعت خوش‌آمد — یک بار برای هر شمارهٔ موبایل
      freeScope: 'phone',           // 'phone' = یک ساعت رایگان به‌ازای هر شماره
      demoMode: true,               // تا اتصال درگاه پرداختِ فروشگاه، شارژ «نمایشی» است
      packs: [
        { id: 'p1', credits: 60,  title: 'بستهٔ کوتاه',    hint: 'یک عیب‌یابی سریع' },
        { id: 'p2', credits: 300, title: 'بستهٔ استاندارد', hint: 'پرکاربردترین' },
        { id: 'p3', credits: 900, title: 'بستهٔ کارگاه',   hint: 'چند دستگاه / پروژه' }
      ]
    };

    function creditFa(n) { return Number(n || 0).toLocaleString('fa-IR'); }

    /* شمارهٔ موبایل: ارقام فارسی/عربی → انگلیسی، فقط رقم‌ها (۰۹۱… → 091…) */
    function creditNormalizePhone(raw) {
      return String(raw || '')
        .replace(/[۰-۹]/g, d => '۰۱۲۳۴۵۶۷۸۹'.indexOf(d))
        .replace(/[٠-٩]/g, d => '٠١٢٣٤٥٦٧٨٩'.indexOf(d))
        .replace(/[^0-9]/g, '');
    }
    function creditMaskPhone(phone) {
      const p = creditNormalizePhone(phone);
      return p ? `${p.slice(0, 4)}***${p.slice(-4)}` : 'بدون شماره';
    }

    function creditState() {
      let st = null;
      try { st = JSON.parse(localStorage.getItem('poshtiban_credits') || 'null'); } catch (e) {}
      if (!st || typeof st !== 'object') st = {};
      if (typeof st.balance !== 'number') st.balance = 0;
      if (!st.freeByPhone || typeof st.freeByPhone !== 'object') st.freeByPhone = {};
      if (!st.grants || typeof st.grants !== 'object') st.grants = {};
      // مهاجرت از نسخهٔ قبلی (دورهٔ رایگانِ سراسری) → به آخرین شمارهٔ شناخته‌شده نسبت داده می‌شود
      if (typeof st.freeMinutesLeft === 'number') {
        const last = creditNormalizePhone(st.lastPhone || '');
        if (last && !(last in st.freeByPhone)) {
          st.freeByPhone[last] = st.freeMinutesLeft;
          if (!st.grants[last]) st.grants[last] = new Date().toISOString();
        }
        delete st.freeMinutesLeft;
      }
      if (!Array.isArray(st.history)) st.history = [];
      if (typeof st.spentTotal !== 'number') st.spentTotal = 0;
      if (!st.sessions) st.sessions = [];
      return st;
    }
    function creditSave(st) {
      try { localStorage.setItem('poshtiban_credits', JSON.stringify(st)); } catch (e) {}
      renderCreditUI();
    }
    function creditLog(st, kind, amount, note) {
      st.history.unshift({ t: new Date().toISOString(), kind, amount, note });
      st.history = st.history.slice(0, 40);
    }

    /* موجودی ساعت خوش‌آمد برای یک شماره: ثبت‌نشده ⇒ ۶۰ دقیقه در انتظار، ثبت‌شده ⇒ ماندهٔ همان شماره */
    function creditFreeRemaining(phone) {
      const st = creditState();
      const p = creditNormalizePhone(phone);
      if (!p) return { phone: '', known: false, left: CREDITS.firstSessionFreeMinutes };
      const known = Object.prototype.hasOwnProperty.call(st.grants, p);
      return { phone: p, known, left: known ? Number(st.freeByPhone[p] || 0) : CREDITS.firstSessionFreeMinutes };
    }

    /* ثبت ساعت خوش‌آمد برای یک شماره — فقط یک بار در عمر آن شماره */
    function creditGrantFreeHour(phone) {
      const p = creditNormalizePhone(phone);
      if (!p) return false;
      const st = creditState();
      if (Object.prototype.hasOwnProperty.call(st.grants, p)) {
        st.lastPhone = p;
        creditSave(st);
        return false;
      }
      st.grants[p] = new Date().toISOString();
      st.freeByPhone[p] = CREDITS.firstSessionFreeMinutes;
      st.lastPhone = p;
      creditLog(st, 'welcome-hour', CREDITS.firstSessionFreeMinutes,
        `ساعت خوش‌آمد برای شمارهٔ ${creditMaskPhone(p)} فعال شد`);
      creditSave(st);
      return true;
    }

    /* محاسبهٔ خالص: چند دقیقه از دورهٔ رایگانِ این شماره، چند دقیقه پرداختی، چند اعتبار */
    function computeCharge(minutesElapsed, freeLeft, phone) {
      const mins = Math.max(0, Math.floor(minutesElapsed));
      const freeUsed = Math.min(mins, Math.max(0, Number(freeLeft) || 0));
      const chargeable = mins - freeUsed;
      return { minutes: mins, freeUsed, chargeable, freeLeftAfter: Math.max(0, (Number(freeLeft) || 0) - freeUsed),
               cost: chargeable * CREDITS.ratePerMinute, phone: creditNormalizePhone(phone) };
    }

    /* ساعت جلسه — در آزمون‌ها می‌توان با window.__creditNowOverride جابه‌جا کرد */
    function creditNow() { return typeof window.__creditNowOverride === 'number' ? window.__creditNowOverride : Date.now(); }
    let creditSession = null;     // { code, phone, startedAt, timer }

    function creditLastPhone() {
      let p = '';
      try { p = localStorage.getItem('poshtiban_last_phone') || ''; } catch (e) {}
      if (!p) p = (document.getElementById('remotePhoneInput') || {}).value || '';
      return creditNormalizePhone(p);
    }

    function startChargeSession(ticketCode, phone) {
      const p = creditNormalizePhone(phone) || creditLastPhone();
      // اگر شماره هنوز ساعت خوش‌آمد نگرفته، همین‌جا برایش ثبت می‌شود (بار اول)
      if (p) creditGrantFreeHour(p);
      const free = creditFreeRemaining(p);
      creditSession = { code: ticketCode || 'بدون کد', phone: p, freeLeft: free.left, startedAt: creditNow(), timer: null };
      const bar = document.getElementById('creditSessionBar');
      if (bar) bar.classList.remove('hidden');
      if (creditSession.timer) clearInterval(creditSession.timer);
      creditSession.timer = setInterval(tickChargeSession, 1000);
      tickChargeSession();
      showToast(p
        ? `جلسهٔ ریموت برای شمارهٔ ${creditMaskPhone(p)} آغاز شد — محاسبهٔ اعتبار شروع شد.`
        : 'جلسهٔ ریموت آغاز شد — محاسبهٔ اعتبار شروع شد.');
      return creditSession;
    }

    function tickChargeSession() {
      if (!creditSession) return;
      const st = creditState();
      const elapsedMs = creditNow() - creditSession.startedAt;
      const charge = computeCharge(elapsedMs / 60000, creditSession.freeLeft, creditSession.phone);

      const minutes = Math.floor(elapsedMs / 60000);
      const clock = document.getElementById('creditSessionClock');
      if (clock) clock.textContent = `${String(Math.floor(minutes / 60)).padStart(2, '۰')}:${String(minutes % 60).padStart(2, '۰')}`.replace(/[0-9]/g, d => '۰۱۲۳۴۵۶۷۸۹'[d]);
      const freeEl = document.getElementById('creditSessionFree');
      if (freeEl) freeEl.textContent = charge.freeLeftAfter > 0
        ? `رایگان: ${creditFa(charge.freeLeftAfter)} دقیقه`
        : 'دورهٔ رایگان این شماره تمام شد';
      const burnEl = document.getElementById('creditSessionBurn');
      if (burnEl) burnEl.textContent = `${creditFa(charge.cost)} اعتبار`;

      if (charge.cost > st.balance) {
        // اعتبار کافی نیست → جلسه با پیام روشن بسته می‌شود (نه بدهی)
        stopChargeSession('out-of-credit');
        showToast('اعتبار کافی نیست؛ جلسه بسته شد. برای ادامه کیف پول را شارژ کنید.');
      }
    }

    function stopChargeSession(reason) {
      if (!creditSession) return null;
      const st = creditState();
      const elapsedMs = creditNow() - creditSession.startedAt;
      const charge = computeCharge(elapsedMs / 60000, creditSession.freeLeft, creditSession.phone);
      const affordable = Math.min(charge.cost, st.balance);
      if (charge.phone) {
        st.freeByPhone[charge.phone] = charge.freeLeftAfter;   // ماندهٔ همین شماره به‌روز می‌شود
        st.lastPhone = charge.phone;
      }
      st.balance = Math.max(0, st.balance - affordable);
      st.spentTotal += affordable;
      const summary = {
        code: creditSession.code,
        phone: charge.phone,
        phoneMasked: creditMaskPhone(charge.phone),
        minutes: charge.minutes,
        freeMinutes: charge.freeUsed,
        chargedMinutes: charge.chargeable,
        cost: affordable,
        wanted: charge.cost,
        balanceAfter: st.balance,
        freeMinutesLeft: charge.freeLeftAfter,
        reason: reason || 'user',
        endedAt: new Date().toISOString()
      };
      st.sessions.unshift(summary);
      st.sessions = st.sessions.slice(0, 20);
      creditLog(st, 'session', -affordable,
        `جلسهٔ ${creditSession.code} (${summary.phoneMasked}): ${creditFa(charge.minutes)} دقیقه — ${creditFa(charge.freeUsed)} دقیقه رایگان`);
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
          t.credits = { minutes: summary.minutes, freeMinutes: summary.freeMinutes, cost: summary.cost,
                        phone: summary.phone, freeMinutesLeft: summary.freeMinutesLeft };
          t.creditsText = `${summary.phoneMasked} · رایگان: ${creditFa(summary.freeMinutes)} دقیقه · مصرف: ${creditFa(summary.cost)} اعتبار`;
          localStorage.setItem('poshtiban_tickets', JSON.stringify(tickets));
        }
      } catch (e) {}
      return summary;
    }

    function topUpCredits(packId) {
      const pack = CREDITS.packs.find(p => p.id === packId);
      if (!pack) return null;
      const st = creditState();
      st.balance += pack.credits;
      creditLog(st, CREDITS.demoMode ? 'demo-topup' : 'topup', pack.credits,
        CREDITS.demoMode ? `شارژ نمایشی «${pack.title}»` : `شارژ «${pack.title}»`);
      creditSave(st);
      showToast(`«${pack.title}» به کیف پول اضافه شد${CREDITS.demoMode ? ' (نمایشی)' : ''}.`);
      return st.balance;
    }

    function resetCreditDemo() {
      const st = creditState();
      st.balance = 0; st.freeByPhone = {}; st.grants = {}; st.lastPhone = '';
      st.history = []; st.spentTotal = 0; st.sessions = [];
      try { localStorage.removeItem('poshtiban_last_phone'); } catch (e) {}
      creditSave(st);
      showToast('کیف پول نمایشی بازنشانی شد.');
    }

    /* چیپ اعتبار داخل مودال ریموت — با هر کاراکتری که در فیلد شماره تایپ می‌شود به‌روز می‌شود */
    function updateRemoteCreditChip() {
      const st = creditState();
      const balanceEl = document.getElementById('remoteCreditBalance');
      if (balanceEl) balanceEl.textContent = creditFa(st.balance);
      const noteEl = document.getElementById('remoteCreditNote');
      if (!noteEl) return;
      const typed = creditNormalizePhone((document.getElementById('remotePhoneInput') || {}).value || '');
      if (typed.length !== 11) {
        noteEl.textContent = 'اولین ۶۰ دقیقهٔ اولین جلسه، برای هر شمارهٔ موبایل یک بار رایگان است';
        return;
      }
      const free = creditFreeRemaining(typed);
      noteEl.textContent = !free.known
        ? 'این شماره ساعت خوش‌آمد ۶۰ دقیقه‌ای دارد'
        : free.left > 0
          ? `برای این شماره ${creditFa(free.left)} دقیقه رایگان مانده`
          : 'دورهٔ رایگان این شماره استفاده شده — هر دقیقه ۱ اعتبار';
    }

    function renderCreditUI() {
      const st = creditState();
      const bal = document.getElementById('walletBalance');
      if (bal) bal.textContent = creditFa(st.balance);

      const freeList = Object.keys(st.grants).sort((a, b) => (st.freeByPhone[b] || 0) - (st.freeByPhone[a] || 0));
      const lastFree = creditFreeRemaining(st.lastPhone || '');
      const free = document.getElementById('walletFreeMinutes');
      if (free) free.textContent = lastFree.phone && lastFree.known
        ? `${creditFa(lastFree.left)} دقیقه`
        : `۶۰ دقیقه`;
      const listEl = document.getElementById('walletFreeList');
      if (listEl) {
        listEl.innerHTML = freeList.length
          ? freeList.map(p => `<div class="flex items-center justify-between gap-2 py-1 border-b border-black/[0.04] dark:border-white/[0.04]">
              <span class="text-brand-gray font-mono" dir="ltr">${creditMaskPhone(p)}</span>
              <b class="${(st.freeByPhone[p] || 0) > 0 ? 'text-emerald-600 dark:text-emerald-400' : 'text-brand-gray'} whitespace-nowrap">
                ${(st.freeByPhone[p] || 0) > 0 ? `${creditFa(st.freeByPhone[p])} دقیقه رایگان` : 'ساعت خوش‌آمد مصرف شد'}
              </b>
            </div>`).join('')
          : '<span class="text-brand-gray">هنوز شماره‌ای ثبت نشده — اولین درخواست ریموت، ساعت خوش‌آمد را برای آن شماره فعال می‌کند.</span>';
      }

      updateRemoteCreditChip();

      const packsEl = document.getElementById('walletPacks');
      if (packsEl && !packsEl.children.length) {
        packsEl.innerHTML = CREDITS.packs.map(p => `
          <button type="button" onclick="topUpCredits('${p.id}')" class="text-right p-3 rounded-2xl border border-black/[0.08] dark:border-white/[0.08] hover:border-brand-blue transition">
            <b class="block text-sm font-black text-brand-blue">${creditFa(p.credits)}</b>
            <span class="block text-[10px] text-brand-gray">اعتبار</span>
            <span class="block text-[10px] font-bold text-brand-dark dark:text-white mt-1">${p.title}</span>
            <span class="block text-[10px] text-brand-gray">${p.hint}</span>
          </button>`).join('');
      }
      const noteEl = document.getElementById('walletDemoNote');
      if (noteEl) noteEl.textContent = CREDITS.demoMode
        ? 'حالت نمایشی: تا اتصال درگاه پرداخت فروشگاه، شارژ فقط برای آزمایش است و مبلغی دریافت نمی‌شود.'
        : 'پرداخت از طریق درگاه امن فروشگاه انجام می‌شود.';
      const histEl = document.getElementById('walletHistory');
      if (histEl) {
        histEl.innerHTML = st.history.length
          ? st.history.map(h => `<div class="flex items-center justify-between gap-2 py-1 border-b border-black/[0.04] dark:border-white/[0.04]">
              <span class="text-brand-gray truncate">${h.note || h.kind}</span>
              <b class="${h.amount < 0 ? 'text-amber-600 dark:text-amber-400' : 'text-emerald-600 dark:text-emerald-400'} whitespace-nowrap">${h.amount > 0 ? '+' : ''}${creditFa(h.amount)}</b>
            </div>`).join('')
          : '<span class="text-brand-gray">هنوز گردشی ثبت نشده است.</span>';
      }
      const sumEl = document.getElementById('remoteSuccessCredit');
      if (sumEl) {
        if (creditSession) {
          sumEl.textContent = `جلسه در حال اجراست — شمارهٔ ${creditMaskPhone(creditSession.phone)} · رایگان: ${creditFa(creditSession.freeLeft)} دقیقه`;
        } else {
          const last = creditFreeRemaining(creditLastPhone());
          sumEl.textContent = !last.phone
            ? 'ساعت خوش‌آمد: ۶۰ دقیقه برای شمارهٔ شما'
            : last.known && last.left > 0
              ? `ساعت خوش‌آمد شمارهٔ ${creditMaskPhone(last.phone)}: ${creditFa(last.left)} دقیقه باقی مانده`
              : `شمارهٔ ${creditMaskPhone(last.phone)}: دورهٔ رایگان استفاده شده`;
        }
      }
    }

'''
src = src[:START] + NEW_ENGINE + src[END:]
ok.append("engine: per-phone welcome hour (grant / session bind / ledgers / UI)")

sub('<!-- ROUND-3-CREDITS: wallet + per-minute metering (first 60 minutes of the first session free),',
    '<!-- ROUND-3-CREDITS-PHONE: the welcome hour is tied to the phone number — 60 free minutes once per\n'
    '     mobile number (shop decision #1). Client-side grant + masking; real one-per-person = SMS OTP\n     on the backend. -->\n<!-- ROUND-3-CREDITS (wallet + per-minute metering),',
    "marker")

io.open(P, "w", encoding="utf-8").write(src)
for label in ok:
    print(f"  ✓ {label}")
print(f"\nDone — {len(src)} chars written.")
