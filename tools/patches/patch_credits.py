"""Round 3, item 3 — credit-based remote-support billing (front-end implementation).

Run:  python3 tools/patches/patch_credits.py        (idempotent, marker: ROUND-3-CREDITS)

What it adds
  * a wallet (balance in «اعتبار», stored in localStorage next to the tickets) with top-up packs,
    a ledger and a demo-mode switch — real payment needs the shop's gateway (see docs/credits-design.md)
  * metering: when a remote session is active, elapsed minutes are counted; the first 60 minutes of
    the user's *first* session are free, after that credits are deducted per minute; if the balance
    runs out the session auto-stops
  * UI: a live session bar, a wallet modal, entries in the header ⋯ menu and the mobile drawer,
    a balance chip + free-hour note inside the remote modal, a demo «technician connected» button in
    the success view, and a credit line on the tracking ticket
  * no rial prices anywhere (round-3 item 2) — credits only
"""
import io
import sys

P = "/home/user/پشتیبان_رایانه.html"
src = io.open(P, encoding="utf-8").read()

if "ROUND-3-CREDITS" in src:
    sys.exit("already applied — ROUND-3-CREDITS marker found, nothing written")

ok = []


def sub(old, new, label):
    global src
    if old not in src:
        sys.exit(f"ANCHOR NOT FOUND [{label}]:\n{old[:420]}")
    src = src.replace(old, new, 1)
    ok.append(label)


# ------------------------------------------------------------------ UI: session bar + wallet
sub('<!-- AI Custom API Key Settings Modal (aiSettingsModal) -->',
    '''<!-- ROUND-3: نوار جلسهٔ فعال ریموت (فقط وقتی جلسه‌ای در جریان است دیده می‌شود) -->
  <div id="creditSessionBar" class="hidden fixed top-14 left-1/2 -translate-x-1/2 z-40 w-[min(94vw,640px)]">
    <div class="flex flex-wrap items-center justify-between gap-2 px-3.5 py-2 rounded-2xl bg-brand-dark/95 dark:bg-white/95 text-white dark:text-brand-dark shadow-2xl border border-white/15 backdrop-blur">
      <div class="flex items-center gap-2 min-w-0">
        <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse shrink-0"></span>
        <b id="creditSessionTitle" class="text-[11px] font-bold whitespace-nowrap">جلسهٔ ریموت فعال</b>
        <span id="creditSessionClock" class="text-[11px] font-mono tabular-nums whitespace-nowrap">۰۰:۰۰</span>
      </div>
      <div class="flex items-center gap-2.5 text-[10px] font-semibold whitespace-nowrap">
        <span id="creditSessionFree" class="text-emerald-300 dark:text-emerald-600">رایگان</span>
        <span id="creditSessionBurn" class="text-amber-300 dark:text-amber-600">۰ اعتبار</span>
        <button onclick="stopChargeSession('user')" class="px-2.5 py-1 rounded-full bg-white/15 dark:bg-black/10 hover:bg-white/25 transition text-[10px] font-bold">پایان جلسه</button>
      </div>
    </div>
  </div>

  <!-- ROUND-3: کیف پول اعتبار -->
  <div id="walletModal" class="fixed inset-0 modal-glass-blur hidden z-50 place-items-center p-4 overflow-y-auto">
    <div class="bg-white dark:bg-[#1c1c1e] text-brand-dark dark:text-white rounded-[28px] max-w-lg w-full p-6 sm:p-8 shadow-2xl relative my-auto border border-black/[0.08] dark:border-white/[0.08]">
      <button onclick="closeWalletModal()" aria-label="بستن" class="absolute left-6 top-6 w-8 h-8 rounded-full bg-black/5 dark:bg-white/10 flex items-center justify-center hover:opacity-75 transition">✕</button>
      <span class="text-xs font-bold text-brand-blue uppercase">میز کاربری</span>
      <h3 class="text-xl font-bold mt-1 text-brand-dark dark:text-white">اعتبار پشتیبانی ریموت</h3>
      <p class="text-xs text-brand-gray mt-1 leading-relaxed">جلسهٔ ریموت بر اساس مدت‌زمان کا<b>ر</b>شناس محاسبه می‌شود؛ <b>اولین ۶۰ دقیقهٔ اولین جلسهٔ شما رایگان است</b> و بعد از آن به‌ازای هر دقیقه اعتبار کم می‌شود.</p>

      <div class="mt-5 p-4 rounded-2xl bg-brand-lightGray dark:bg-[#161617] border border-black/[0.06] dark:border-white/[0.06] flex items-end justify-between">
        <div>
          <span class="text-[11px] text-brand-gray block">اعتبار فعلی</span>
          <b id="walletBalance" class="text-2xl font-black text-brand-blue">۰</b>
          <span class="text-[11px] text-brand-gray">اعتبار</span>
        </div>
        <div class="text-left">
          <span class="text-[11px] text-brand-gray block">دورهٔ رایگان باقی‌مانده</span>
          <b id="walletFreeMinutes" class="text-lg font-bold text-emerald-600 dark:text-emerald-400">۶۰ دقیقه</b>
        </div>
      </div>

      <div class="mt-4">
        <span class="text-[11px] font-bold text-brand-dark dark:text-white block mb-2">شارژ اعتبار</span>
        <div id="walletPacks" class="grid grid-cols-1 sm:grid-cols-3 gap-2"></div>
        <p id="walletDemoNote" class="text-[10px] text-brand-gray mt-2 leading-relaxed"></p>
      </div>

      <div class="mt-4">
        <span class="text-[11px] font-bold text-brand-dark dark:text-white block mb-1.5">گردش اعتبار</span>
        <div id="walletHistory" class="max-h-40 overflow-y-auto poshtiban-scrollbar space-y-1.5 text-[11px]"></div>
      </div>

      <div class="mt-5 flex flex-col sm:flex-row gap-2">
        <button onclick="closeWalletModal()" class="flex-1 py-2.5 rounded-full bg-black/5 dark:bg-white/10 hover:bg-black/10 text-xs font-bold transition">بستن</button>
        <button onclick="resetCreditDemo()" class="flex-1 py-2.5 rounded-full border border-black/[0.08] dark:border-white/[0.08] hover:bg-black/5 dark:hover:bg-white/10 text-xs font-bold transition">بازنشانی (نمایشی)</button>
      </div>
    </div>
  </div>

  <!-- AI Custom API Key Settings Modal (aiSettingsModal) -->''',
    "UI: session bar + wallet modal")

# ------------------------------------------------------------------ entry points
sub('''            <button type="button" role="menuitem" onclick="openTrackingModal(); closeHeaderMore();" class="w-full text-right px-3 py-2 rounded-xl text-[11px] font-semibold text-brand-dark dark:text-white hover:bg-brand-blue/10 hover:text-brand-blue transition">پیگیری وضعیت دستگاه</button>''',
    '''            <button type="button" role="menuitem" onclick="openWalletModal(); closeHeaderMore();" class="w-full text-right px-3 py-2 rounded-xl text-[11px] font-semibold text-brand-dark dark:text-white hover:bg-brand-blue/10 hover:text-brand-blue transition">اعتبار و کیف پول</button>
            <button type="button" role="menuitem" onclick="openTrackingModal(); closeHeaderMore();" class="w-full text-right px-3 py-2 rounded-xl text-[11px] font-semibold text-brand-dark dark:text-white hover:bg-brand-blue/10 hover:text-brand-blue transition">پیگیری وضعیت دستگاه</button>''',
    "⋯ menu: wallet entry")
sub('''      <button onclick="openTrackingModal(); toggleMobileMenu();" class="col-span-2 py-2 text-center rounded-xl bg-black/5 dark:bg-white/10 font-bold">
        پیگیری وضعیت دستگاه
      </button>''',
    '''      <button onclick="openWalletModal(); toggleMobileMenu();" class="col-span-2 py-2 text-center rounded-xl bg-black/5 dark:bg-white/10 font-bold">
        اعتبار و کیف پول
      </button>
      <button onclick="openTrackingModal(); toggleMobileMenu();" class="col-span-2 py-2 text-center rounded-xl bg-black/5 dark:bg-white/10 font-bold">
        پیگیری وضعیت دستگاه
      </button>''',
    "drawer: wallet entry")

# remote modal: balance chip + free-hour note
sub('<form onsubmit="handleRemoteSubmit(event)" class="mt-6 space-y-4">',
    '''<!-- ROUND-3: وضعیت اعتبار پیش از ثبت درخواست -->
        <button type="button" onclick="openWalletModal()" id="remoteCreditChip" class="mt-4 w-full flex items-center justify-between gap-3 px-3.5 py-2.5 rounded-2xl bg-brand-blue/5 dark:bg-brand-blue/10 border border-brand-blue/20 hover:border-brand-blue/40 transition text-right">
          <span class="text-[11px] font-bold text-brand-blue">اعتبار شما: <b id="remoteCreditBalance">۰</b></span>
          <span id="remoteCreditNote" class="text-[10px] text-brand-gray">اولین ۶۰ دقیقهٔ اولین جلسه رایگان است</span>
        </button>

        <form onsubmit="handleRemoteSubmit(event)" class="mt-4 space-y-4">''',
    "remote modal: credit chip")
sub('<div id="remoteSuccessHandoff" class="mt-4 flex flex-wrap gap-2 justify-center"></div>',
    '''<div id="remoteSuccessHandoff" class="mt-4 flex flex-wrap gap-2 justify-center"></div>
<div class="mt-4 p-3 rounded-2xl bg-brand-lightGray dark:bg-[#161617] border border-black/[0.06] dark:border-white/[0.06] text-[11px] text-brand-gray leading-relaxed">
اعتبار جلسه: <b id="remoteSuccessCredit" class="text-brand-dark dark:text-white">۶۰ دقیقهٔ اول رایگان</b>
<div class="mt-2">
<button type="button" onclick="startChargeSession(document.getElementById('remoteSuccessCode').textContent.trim())" class="w-full py-2 rounded-full bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/25 text-[11px] font-bold hover:bg-emerald-500/20 transition">شبیه‌سازی اتصال کارشناس و شروع محاسبهٔ اعتبار</button>
</div>
</div>''',
    "success view: credit line + demo start")

# tracking modal: credit line on the ticket
sub('''<div id="trackingResultCard" class="mt-6 p-5 rounded-2xl bg-brand-lightGray dark:bg-[#161617] border border-black/[0.06] dark:border-white/[0.06] text-xs space-y-3.5">''',
    '''<div id="trackingResultCard" class="mt-6 p-5 rounded-2xl bg-brand-lightGray dark:bg-[#161617] border border-black/[0.06] dark:border-white/[0.06] text-xs space-y-3.5">
          <div id="trackCreditsRow" class="hidden flex items-center justify-between gap-3 pb-3 border-b border-black/[0.06] dark:border-white/[0.06]">
            <span class="text-brand-gray">محاسبهٔ اعتبار جلسه:</span>
            <b id="trackCreditsText" class="text-brand-dark dark:text-white">—</b>
          </div>''',
    "tracking: credit row")

# ------------------------------------------------------------------ engine
sub('    function toggleHeaderMore(e) {',
    r'''    /* ================= ROUND-3: سیستم اعتبار (کیف پول) ================= */
    const CREDITS = {
      ratePerMinute: 1,             // اعتبار مصرفی هر دقیقه پس از دورهٔ رایگان
      firstSessionFreeMinutes: 60,  // اولین ساعتِ اولین جلسهٔ هر کاربر رایگان
      demoMode: true,               // تا اتصال درگاه پرداختِ فروشگاه، شارژ «نمایشی» است
      packs: [
        { id: 'p1', credits: 60,  title: 'بستهٔ کوتاه',    hint: 'یک عیب‌یابی سریع' },
        { id: 'p2', credits: 300, title: 'بستهٔ استاندارد', hint: 'پرکاربردترین' },
        { id: 'p3', credits: 900, title: 'بستهٔ کارگاه',   hint: 'چند دستگاه / پروژه' }
      ]
    };

    function creditFa(n) { return Number(n || 0).toLocaleString('fa-IR'); }

    function creditState() {
      let st = null;
      try { st = JSON.parse(localStorage.getItem('poshtiban_credits') || 'null'); } catch (e) {}
      if (!st || typeof st !== 'object') st = {};
      if (typeof st.balance !== 'number') st.balance = 0;
      if (typeof st.freeMinutesLeft !== 'number') st.freeMinutesLeft = CREDITS.firstSessionFreeMinutes;
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

    /* محاسبهٔ خالص: چند دقیقه از دورهٔ رایگان، چند دقیقه پرداختی، چند اعتبار */
    function computeCharge(minutesElapsed, st) {
      const mins = Math.max(0, Math.floor(minutesElapsed));
      const freeUsed = Math.min(mins, st.freeMinutesLeft);
      const chargeable = mins - freeUsed;
      return { minutes: mins, freeUsed, chargeable, cost: chargeable * CREDITS.ratePerMinute };
    }

    /* ساعت جلسه — در آزمون‌ها می‌توان با window.__creditNowOverride جابه‌جا کرد */
    function creditNow() { return typeof window.__creditNowOverride === 'number' ? window.__creditNowOverride : Date.now(); }
    let creditSession = null;     // { code, startedAt, timer }

    function startChargeSession(ticketCode) {
      const st = creditState();
      creditSession = { code: ticketCode || 'بدون کد', startedAt: creditNow(), timer: null };
      const bar = document.getElementById('creditSessionBar');
      if (bar) bar.classList.remove('hidden');
      if (creditSession.timer) clearInterval(creditSession.timer);
      creditSession.timer = setInterval(tickChargeSession, 1000);
      tickChargeSession();
      showToast('جلسهٔ ریموت آغاز شد — محاسبهٔ اعتبار شروع شد.');
      return creditSession;
    }

    function tickChargeSession() {
      if (!creditSession) return;
      const st = creditState();
      const elapsedMs = creditNow() - creditSession.startedAt;
      const charge = computeCharge(elapsedMs / 60000, st);

      // دورهٔ رایگان به‌صورت پیش‌رونده مصرف می‌شود تا اگر کاربر وسط جلسه قطع کرد، درست حساب شود
      const remainingFree = Math.max(0, st.freeMinutesLeft - charge.freeUsed);
      const minutes = Math.floor(elapsedMs / 60000);
      const clock = document.getElementById('creditSessionClock');
      if (clock) clock.textContent = `${String(Math.floor(minutes / 60)).padStart(2, '۰')}:${String(minutes % 60).padStart(2, '۰')}`.replace(/[0-9]/g, d => '۰۱۲۳۴۵۶۷۸۹'[d]);
      const freeEl = document.getElementById('creditSessionFree');
      if (freeEl) freeEl.textContent = remainingFree > 0 ? `رایگان: ${creditFa(remainingFree)} دقیقه` : 'دورهٔ رایگان تمام شد';
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
      const charge = computeCharge(elapsedMs / 60000, st);
      const freeRemaining = Math.max(0, st.freeMinutesLeft - charge.freeUsed);
      const affordable = Math.min(charge.cost, st.balance);
      st.freeMinutesLeft = freeRemaining;
      st.balance = Math.max(0, st.balance - affordable);
      st.spentTotal += affordable;
      const summary = {
        code: creditSession.code,
        minutes: charge.minutes,
        freeMinutes: charge.freeUsed,
        chargedMinutes: charge.chargeable,
        cost: affordable,
        wanted: charge.cost,
        balanceAfter: st.balance,
        freeMinutesLeft: freeRemaining,
        reason: reason || 'user',
        endedAt: new Date().toISOString()
      };
      st.sessions.unshift(summary);
      st.sessions = st.sessions.slice(0, 20);
      creditLog(st, 'session', -affordable,
        `جلسهٔ ${creditSession.code}: ${creditFa(charge.minutes)} دقیقه (${creditFa(charge.freeUsed)} دقیقه رایگان)`);
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
          t.credits = { minutes: summary.minutes, freeMinutes: summary.freeMinutes, cost: summary.cost };
          t.creditsText = `دورهٔ رایگان: ${creditFa(summary.freeMinutes)} دقیقه · مصرف: ${creditFa(summary.cost)} اعتبار`;
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
      st.balance = 0; st.freeMinutesLeft = CREDITS.firstSessionFreeMinutes;
      st.history = []; st.spentTotal = 0; st.sessions = [];
      creditSave(st);
      showToast('کیف پول نمایشی بازنشانی شد.');
    }

    function renderCreditUI() {
      const st = creditState();
      const bal = document.getElementById('walletBalance');
      if (bal) bal.textContent = creditFa(st.balance);
      const free = document.getElementById('walletFreeMinutes');
      if (free) free.textContent = `${creditFa(st.freeMinutesLeft)} دقیقه`;
      const chipBal = document.getElementById('remoteCreditBalance');
      if (chipBal) chipBal.textContent = creditFa(st.balance);
      const chipNote = document.getElementById('remoteCreditNote');
      if (chipNote) chipNote.textContent = st.freeMinutesLeft > 0
        ? `اولین ${creditFa(st.freeMinutesLeft)} دقیقه رایگان است`
        : `هر دقیقه ${creditFa(CREDITS.ratePerMinute)} اعتبار`;
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
      if (sumEl && creditSession) {
        sumEl.textContent = `جلسه در حال اجراست — دورهٔ رایگان: ${creditFa(st.freeMinutesLeft)} دقیقه`;
      }
    }

    function openWalletModal() {
      playHapticSound('click');
      const modal = document.getElementById('walletModal');
      if (!modal) return;
      renderCreditUI();
      modal.classList.remove('hidden');
      modal.classList.add('grid');
      lockBodyScroll();
    }
    function closeWalletModal() {
      const modal = document.getElementById('walletModal');
      if (modal) { modal.classList.add('hidden'); modal.classList.remove('grid'); }
      unlockBodyScroll();
    }

    function toggleHeaderMore(e) {''',
    "credits engine")

# Esc + load wiring
sub('''          closeHeaderMore();''',
    '''          closeHeaderMore();
          closeWalletModal();''',
    "Esc closes the wallet")
sub('''      initLauncherAutoHide();''',
    '''      initLauncherAutoHide();
      renderCreditUI();          // ROUND-3: نمایش اعتبار در پنل کاربری''',
    "renderCreditUI on load")

# ------------------------------------------------------------------ marker + docs
sub('<!-- ROUND-3 (round-2-header follow-up)',
    '''<!-- ROUND-3-CREDITS: wallet + per-minute metering (first 60 minutes of the first session free),
     session bar, wallet modal, balance chip in the remote modal, credit line on the tracking ticket.
     Payment gateway is NOT connected yet — CREDITS.demoMode keeps top-ups labelled as demo.
     Design + open questions: docs/credits-design.md -->
<!-- ROUND-3 (round-2-header follow-up)''',
    "marker")

io.open(P, "w", encoding="utf-8").write(src)
for label in ok:
    print(f"  ✓ {label}")
print(f"\nDone — {len(src)} chars written.")
