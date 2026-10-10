#!/usr/bin/env python3
"""
ROUND-3-CREDITS-FINAL — پیاده‌سازی پنج تصمیم تأییدشدهٔ شما روی قواعد اعتبار:
  ۱) انقضای اعتبار پس از ۱۲ ماه + نمایش تاریخ انقضا در کیف پول
  ۲) پنجرهٔ اعتراض ۴۸ ساعته به مصرف جلسه (ثبت در ماژول پیگیری)
  ۳) اعتبار ماهانه داخل طرح‌های Care
  ۴) اعلان کم‌موجودی («N دقیقه تا اتمام اعتبار» + شارژ سریع) روی نوار جلسه
  ۵) قطعی از سمت کارگاه: وقفه تا ۳ دقیقه (و بیشتر) بدون محاسبه + کنترل کارشناس

اجرا:  python3 tools/patches/patch_credits_final.py     (یک‌بار — با نشانگر محافظت می‌شود)
"""
import io, sys

P = '/home/user/پشتیبان_رایانه.html'
MARK = 'ROUND-3-CREDITS-FINAL'
s = io.open(P, encoding='utf-8').read()
if MARK in s:
    sys.exit('این پچ قبلاً اجرا شده است — دوباره اجرا نمی‌شود.')

done = []
def rep(old, new, label, count=1):
    global s
    n = s.count(old)
    assert n == count, f'✗ {label}: {n} مورد پیدا شد (انتظار {count})\n{old[:120]}'
    s = s.replace(old, new, 1)
    done.append(label)

# ---------------------------------------------------------------- ۱) تنظیمات
rep("""      sessionCaps: [60, 120, 300],  // گزینه‌های سقف مصرف برای انتخاب کاربر""",
"""      sessionCaps: [60, 120, 300],  // گزینه‌های سقف مصرف برای انتخاب کاربر
      expiryMonths: 12,             // اعتبار هر شارژ ۱۲ ماه اعتبار دارد (تصمیم ۱)
      disputeWindowHours: 48,       // پنجرهٔ اعتراض به مصرف جلسه (تصمیم ۲)
      careMonthlyCredits: [300, 900, 3000], // اعتبار ماهانهٔ طرح‌های Care (تصمیم ۳)
      lowBalanceMinutes: 5,         // اعلان «N دقیقه تا اتمام اعتبار» (تصمیم ۴)
      workshopDropGraceSeconds: 180,// قطعی سمت کارگاه: تا ۳ دقیقه وقفهٔ رایگان (تصمیم ۵)""",
    "CREDITS: کلیدهای پنج تصمیم تازه")

# ------------------------------------------------- ۲) تاریخ شمسی + انقضا + تخصیص FIFO
rep("""    function creditState() {""",
"""    /* ---------- تاریخ شمسی (بدون وابستگی به ICU) — برای نمایش انقضای اعتبار ---------- */
    const CREDIT_JMONTHS = ['فروردین','اردیبهشت','خرداد','تیر','مرداد','شهریور','مهر','آبان','آذر','دی','بهمن','اسفند'];
    function creditJalali(ms) {
      const d = new Date(ms);
      let gy = d.getFullYear(), gm = d.getMonth() + 1, gd = d.getDate();
      const gDays = [0,31,59,90,120,151,181,212,243,273,304,334];
      let jy = gy <= 1600 ? 0 : 979;
      gy -= gy <= 1600 ? 621 : 1600;
      const gy2 = gm > 2 ? gy + 1 : gy;
      let days = (365 * gy) + Math.floor((gy2 + 3) / 4) - Math.floor((gy2 + 99) / 100)
               + Math.floor((gy2 + 399) / 400) - 80 + gd + gDays[gm - 1];
      jy += 33 * Math.floor(days / 12053); days %= 12053;
      jy += 4 * Math.floor(days / 1461);   days %= 1461;
      if (days > 365) { jy += Math.floor((days - 1) / 365); days = (days - 1) % 365; }
      const jm = days < 186 ? 1 + Math.floor(days / 31) : 7 + Math.floor((days - 186) / 30);
      const jd = 1 + (days < 186 ? days % 31 : (days - 186) % 30);
      return { jy, jm, jd };
    }
    function creditJalaliLabel(ms) {
      const j = creditJalali(ms);
      return `${creditFa(j.jd)} ${CREDIT_JMONTHS[j.jm - 1]} ${creditFa(j.jy)}`;
    }
    /* انقضای هر بسته: همان روز، ۱۲ ماه بعد */
    function creditExpiryAt(atMs) {
      const d = new Date(atMs);
      const day = d.getDate();
      d.setFullYear(d.getFullYear() + (CREDITS.expiryMonths || 12));
      if (d.getDate() !== day) d.setDate(0);          // ۲۹ فوریه → آخرین روز ماه قبل
      return d.getTime();
    }
    function creditExpiryInfo() {
      const st = creditState();
      const lots = (st.lots || []).filter(l => (l.left || 0) > 0);
      if (!lots.length) return { hasLot: false, label: '', left: 0, at: null };
      lots.sort((a, b) => new Date(a.at) - new Date(b.at));
      const lot = lots[0];
      const at = new Date(lot.at).getTime();
      return { hasLot: true, left: lot.left, at, label: creditJalaliLabel(creditExpiryAt(at)), lot };
    }
    /* سوخت اعتبارِ منقضی‌شده — موجودی هیچ‌وقت منفی نمی‌شود */
    let creditSweeping = false;
    function creditSweepExpired(nowMs) {
      const now = typeof nowMs === 'number' ? nowMs : creditNow();
      const st = creditState();
      if (!Array.isArray(st.lots) || !st.lots.length) return 0;
      let expired = 0;
      st.lots.forEach(lot => {
        if ((lot.left || 0) > 0 && creditExpiryAt(new Date(lot.at).getTime()) <= now) {
          expired += lot.left;
          lot.left = 0;
        }
      });
      if (expired > 0 && !creditSweeping) {
        creditSweeping = true;
        st.balance = Math.max(0, st.balance - expired);
        creditLog(st, 'expiry', -expired,
          `انقضای اعتبار: ${creditFa(expired)} اعتبار پس از ${creditFa(CREDITS.expiryMonths)} ماه سوخت شد`);
        creditSave(st);
        creditSweeping = false;
      }
      return expired;
    }
    /* مصرف بسته‌ها به‌ترتیب قدیمی‌ترین (FIFO) — برای درست‌ماندن تاریخ انقضا */
    function creditConsumeLots(st, amount) {
      let left = Math.max(0, Number(amount) || 0);
      if (!Array.isArray(st.lots) || !left) return left;
      [...st.lots].sort((a, b) => new Date(a.at) - new Date(b.at)).forEach(lot => {
        if (left <= 0) return;
        const take = Math.min(lot.left || 0, left);
        lot.left = (lot.left || 0) - take;
        left -= take;
      });
      return left;
    }

    function creditState() {""",
    "موتور: تاریخ شمسی + انقضا + FIFO")

# ------------------------------------------- creditState: lots/disputes + مهاجرت
rep("""      if (!Array.isArray(st.history)) st.history = [];
      if (typeof st.spentTotal !== 'number') st.spentTotal = 0;
      if (!st.sessions) st.sessions = [];
      return st;""",
"""      if (!Array.isArray(st.history)) st.history = [];
      if (typeof st.spentTotal !== 'number') st.spentTotal = 0;
      if (!st.sessions) st.sessions = [];
      if (!Array.isArray(st.lots)) st.lots = [];
      if (!Array.isArray(st.disputes)) st.disputes = [];
      // مهاجرت: موجودیِ قدیمی که بستهٔ متناظر ندارد، یک بستهٔ فرضی می‌گیرد تا تاریخ انقضا نمایش داده شود
      if (!st.lots.length && st.balance > 0) {
        const lastTop = (st.history || []).find(h => (h.amount || 0) > 0);
        st.lots.push({ at: (lastTop && lastTop.t) || new Date().toISOString(),
                       credits: st.balance, left: st.balance, pack: 'شارژ پیشین' });
      }
      return st;""",
    "creditState: lots + disputes + مهاجرت")

# --------------------------------------------------- startChargeSession: sweep + فیلدها
rep("""    function startChargeSession(ticketCode, phone, sessionCap) {
      const p = creditNormalizePhone(phone) || creditLastPhone();""",
"""    function startChargeSession(ticketCode, phone, sessionCap) {
      creditSweepExpired();                     // تصمیم ۱: اعتبار منقضی پیش از جلسه سوخته می‌شود
      const p = creditNormalizePhone(phone) || creditLastPhone();""",
    "startChargeSession: sweep انقضا")

rep("""      creditSession = {
        code: ticketCode || 'بدون کد',
        phone: p,
        freeLeft: free.left,
        cap: cap,
        startedAt: creditNow(),
        pausedTotalMs: 0,
        pauseStart: null,
        timer: null
      };""",
"""      creditSession = {
        code: ticketCode || 'بدون کد',
        phone: p,
        freeLeft: free.left,
        cap: cap,
        startedAt: creditNow(),
        pausedTotalMs: 0,
        pauseStart: null,
        dropTotalMs: 0,          // تصمیم ۵: مجموع وقفه‌های قطعیِ سمت کارگاه (بدون محاسبه)
        dropStart: null,
        warnedLow: false,        // تصمیم ۴: تا یک بار اعلان کم‌موجودی
        timer: null
      };""",
    "startChargeSession: فیلدهای drop/warnedLow")

# ------------------------------------------------------------ billable/phase
rep("""    function creditBillableMs(sess) {
      const now = creditNow();
      const graceMs = (CREDITS.setupGraceSeconds || 0) * 1000;
      const pausedNow = sess.pauseStart ? (now - sess.pauseStart) : 0;
      return Math.max(0, (now - sess.startedAt) - graceMs - sess.pausedTotalMs - pausedNow);
    }
    function creditPhase(sess) {
      if (sess.pauseStart) return 'paused';""",
"""    function creditBillableMs(sess) {
      const now = creditNow();
      const graceMs = (CREDITS.setupGraceSeconds || 0) * 1000;
      const pausedNow = sess.pauseStart ? (now - sess.pauseStart) : 0;
      const dropNow = sess.dropStart ? (now - sess.dropStart) : 0;      // تصمیم ۵
      return Math.max(0, (now - sess.startedAt) - graceMs - sess.pausedTotalMs - pausedNow
                          - (sess.dropTotalMs || 0) - dropNow);
    }
    function creditPhase(sess) {
      if (sess.dropStart) return 'drop';                               // تصمیم ۵: قطعی سمت کارگاه
      if (sess.pauseStart) return 'paused';""",
    "creditBillableMs/creditPhase: حالت drop")

# ------------------------------------------------------------------ tick
rep("""      const phaseEl = document.getElementById('creditSessionPhase');
      if (phaseEl) {
        phaseEl.textContent = phase === 'grace' ? 'مهلت راه‌اندازی — محاسبه شروع نشده'
          : phase === 'paused' ? 'توقف موقت — محاسبه متوقف است'
          : 'در حال محاسبه';
      }
      const pauseBtn = document.getElementById('creditSessionPauseBtn');
      if (pauseBtn) pauseBtn.textContent = phase === 'paused' ? 'ادامهٔ جلسه' : 'توقف موقت';""",
"""      const phaseEl = document.getElementById('creditSessionPhase');
      if (phaseEl) {
        phaseEl.textContent = phase === 'grace' ? 'مهلت راه‌اندازی — محاسبه شروع نشده'
          : phase === 'paused' ? 'توقف موقت — محاسبه متوقف است'
          : phase === 'drop' ? (dropMs > (CREDITS.workshopDropGraceSeconds || 180) * 1000
              ? `قطعی بیش از ${creditFa(Math.round((CREDITS.workshopDropGraceSeconds || 180) / 60))} دقیقه — در انتظار تصمیم کارشناس`
              : 'قطعی از سمت کارگاه — محاسبه متوقف (رایگان)')
          : 'در حال محاسبه';
      }
      const pauseBtn = document.getElementById('creditSessionPauseBtn');
      if (pauseBtn) pauseBtn.textContent = phase === 'paused' ? 'ادامهٔ جلسه' : 'توقف موقت';
      const dropBtn = document.getElementById('creditSessionDropBtn');
      if (dropBtn) {
        dropBtn.textContent = phase === 'drop' ? 'اتصال برگشت' : 'قطعی سمت کارگاه';
        dropBtn.setAttribute('aria-pressed', phase === 'drop' ? 'true' : 'false');
      }""",
    "tick: متن فاز قطعی + دکمهٔ کارشناس")

rep("""      const burnEl = document.getElementById('creditSessionBurn');
      if (burnEl) burnEl.textContent = `${creditFa(charge.cost)} / سقف ${creditFa(creditSession.cap)} اعتبار`;""",
"""      const burnEl = document.getElementById('creditSessionBurn');
      if (burnEl) burnEl.textContent = `${creditFa(charge.cost)} / سقف ${creditFa(creditSession.cap)} اعتبار`;

      // تصمیم ۴: اعلان کم‌موجودی — «N دقیقه تا اتمام اعتبار» + شارژ سریع
      const remainingMinutes = Math.max(0, charge.freeLeftAfter) + Math.max(0, st.balance - charge.cost);
      const low = (CREDITS.lowBalanceMinutes || 0) > 0 && remainingMinutes <= CREDITS.lowBalanceMinutes;
      const alertEl = document.getElementById('creditSessionAlert');
      const alertTextEl = document.getElementById('creditSessionAlertText');
      if (alertTextEl) alertTextEl.textContent = `${creditFa(remainingMinutes)} دقیقه تا اتمام اعتبار`;
      if (alertEl) { alertEl.classList.toggle('hidden', !low); alertEl.classList.toggle('flex', low); }
      if (low && !creditSession.warnedLow) {
        creditSession.warnedLow = true;
        showToast(`اعتبار شما تا ${creditFa(remainingMinutes)} دقیقهٔ دیگر تمام می‌شود — برای ادامه، کیف اعتبار را شارژ کنید.`);
      }
      if (!low) creditSession.warnedLow = false;""",
    "tick: اعلان کم‌موجودی")

rep("""      const totalMinutes = Math.floor((creditNow() - creditSession.startedAt) / 60000);""",
"""      const dropMs = (creditSession.dropTotalMs || 0)
        + (creditSession.dropStart ? (creditNow() - creditSession.dropStart) : 0);   // تصمیم ۵
      const totalMinutes = Math.floor((creditNow() - creditSession.startedAt) / 60000);""",
    "tick: محاسبهٔ مدت وقفه")

# ------------------------------------------------------------------ stop
rep("""      st.balance = st.balance - deducted;
      st.spentTotal += deducted;""",
"""      st.balance = st.balance - deducted;
      st.spentTotal += deducted;
      creditConsumeLots(st, deducted);          // تصمیم ۱: مصرف FIFO برای درست‌ماندن تاریخ انقضا""",
    "stop: مصرف FIFO بسته‌ها")

rep("""        pausedMinutes: Math.floor(creditSession.pausedTotalMs / 60000),""",
"""        pausedMinutes: Math.floor(creditSession.pausedTotalMs / 60000),
        dropMinutes: Math.floor(((creditSession.dropTotalMs || 0)
          + (creditSession.dropStart ? (creditNow() - creditSession.dropStart) : 0)) / 60000),""",
    "stop: ثبت دقیقهٔ قطعی در گزارش جلسه")

rep("""        `جلسهٔ ${creditSession.code} (${summary.phoneMasked}): ${creditFa(summary.minutes)} دقیقه محاسبه — ${creditFa(charge.freeUsed)} دقیقه رایگان${summary.cap ? ` · سقف ${creditFa(summary.cap)}` : ''}`);""",
"""        `جلسهٔ ${creditSession.code} (${summary.phoneMasked}): ${creditFa(summary.minutes)} دقیقه محاسبه — ${creditFa(charge.freeUsed)} دقیقه رایگان${summary.cap ? ` · سقف ${creditFa(summary.cap)}` : ''}${summary.dropMinutes ? ` · قطعی ${creditFa(summary.dropMinutes)} دقیقه (بدون محاسبه)` : ''}`);""",
    "stop: متن گردش با قطعی")

# ------------------------------------------- کنترل کارشناس: قطعی + اعتراض ۴۸ ساعته
rep("""      tickChargeSession();
      return creditSession;
    }
    function sessionCapChip(cap) { return creditFa(cap); }""",
"""      tickChargeSession();
      return creditSession;
    }

    /* تصمیم ۵: قطعی از سمت کارگاه — وقفهٔ اتصال محاسبه نمی‌شود (تا ۳ دقیقه رایگان و بیشتر از آن هم بدون محاسبه
       و در انتظار تصمیم کارشناس؛ قاعدهٔ «بدون توقف خودکار» نسخهٔ ۱ دست‌نخورده می‌ماند) */
    function toggleWorkshopDrop() {
      if (!creditSession) return null;
      if (creditSession.dropStart) {
        creditSession.dropTotalMs = (creditSession.dropTotalMs || 0) + (creditNow() - creditSession.dropStart);
        creditSession.dropStart = null;
        showToast('اتصال برگشت — محاسبه از همین لحظه ادامه دارد.');
      } else {
        if (creditSession.pauseStart) pauseChargeSession();          // توقف موقت و قطعی هم‌زمان معنا ندارد
        creditSession.dropStart = creditNow();
        showToast(`قطعی از سمت کارگاه ثبت شد — وقفهٔ اتصال محاسبه نمی‌شود (تا ${creditFa(Math.round((CREDITS.workshopDropGraceSeconds || 180) / 60))} دقیقه رایگان).`);
      }
      tickChargeSession();
      return creditSession;
    }

    /* تصمیم ۲: پنجرهٔ ۴۸ ساعتهٔ اعتراض به مصرف جلسه */
    function creditDisputeState(code) {
      const st = creditState();
      const c = String(code || '').trim().toUpperCase();
      const session = (st.sessions || []).find(x => String(x.code).toUpperCase() === c) || null;
      const dispute = (st.disputes || []).find(d => String(d.code).toUpperCase() === c) || null;
      const endedAt = session && session.endedAt ? new Date(session.endedAt).getTime() : null;
      const now = creditNow();
      const withinWindow = !!(endedAt && !dispute && now <= endedAt + (CREDITS.disputeWindowHours || 48) * 3600000);
      return { code: c, session, dispute, endedAt, withinWindow, windowHours: CREDITS.disputeWindowHours || 48 };
    }
    function toggleDisputeForm() {
      const form = document.getElementById('trackDisputeForm');
      if (!form) return;
      form.classList.toggle('hidden');
      if (!form.classList.contains('hidden')) {
        const ta = document.getElementById('trackDisputeReason');
        if (ta) ta.focus();
      }
    }
    function submitCreditDispute() {
      const ta = document.getElementById('trackDisputeReason');
      const reason = (ta && ta.value || '').trim();
      const code = ((document.getElementById('trackingSearchInput') || {}).value || '').trim().toUpperCase();
      if (reason.length < 3) { showToast('لطفاً در یک جمله بنویسید چه چیزی حل نشد.'); return null; }
      const st = creditState();
      const d = creditDisputeState(code);
      if (!d.session) { showToast('برای این کد جلسهٔ محاسبه‌شده‌ای ثبت نشده است.'); return null; }
      if (d.dispute) { showToast('اعتراض این جلسه قبلاً ثبت شده است.'); return d.dispute; }
      if (!d.withinWindow) { showToast(`پنجرهٔ ${creditFa(d.windowHours)} ساعتهٔ اعتراض برای این جلسه گذشته است.`); return null; }
      const rec = { code: d.code, at: new Date().toISOString(), reason, status: 'open',
                    phoneMasked: d.session.phoneMasked, cost: d.session.cost };
      st.disputes.unshift(rec);
      st.disputes = st.disputes.slice(0, 20);
      creditLog(st, 'dispute', 0, `اعتراض به مصرف جلسهٔ ${d.code}: بررسی تا ${creditFa(d.windowHours)} ساعت`);
      creditSave(st);
      if (ta) ta.value = '';
      renderTrackDispute(d.code);
      showToast(`اعتراض شما ثبت شد — تا ${creditFa(d.windowHours)} ساعت بررسی می‌شود و در صورت تأیید، مصرف جلسه صفر می‌شود.`);
      return rec;
    }
    function renderTrackDispute(code) {
      const row = document.getElementById('trackDisputeRow');
      const btn = document.getElementById('trackDisputeBtn');
      const form = document.getElementById('trackDisputeForm');
      const statusEl = document.getElementById('trackDisputeStatus');
      if (!row) return;
      const d = creditDisputeState(code);
      if (!d.session) { row.classList.add('hidden'); row.classList.remove('flex'); return; }
      row.classList.remove('hidden');
      row.classList.add('flex');
      if (form) { form.classList.add('hidden'); }
      if (d.dispute) {
        if (statusEl) statusEl.textContent = `اعتراض ثبت شد (${creditJalaliLabel(new Date(d.dispute.at).getTime())}) — بررسی تا ${creditFa(d.windowHours)} ساعت`;
        if (btn) { btn.classList.add('hidden'); btn.classList.remove('inline-block'); }
        return;
      }
      if (d.withinWindow) {
        if (statusEl) statusEl.textContent = `اگر مشکل این جلسه حل نشد، تا ${creditFa(d.windowHours)} ساعت می‌توانید اعتراض ثبت کنید.`;
        if (btn) { btn.classList.remove('hidden'); btn.classList.add('inline-block'); btn.textContent = `ثبت اعتراض (تا ${creditFa(d.windowHours)} ساعت)`; }
        return;
      }
      if (statusEl) statusEl.textContent = `پنجرهٔ ${creditFa(d.windowHours)} ساعتهٔ اعتراض این جلسه گذشته است.`;
      if (btn) { btn.classList.add('hidden'); btn.classList.remove('inline-block'); }
    }
    function sessionCapChip(cap) { return creditFa(cap); }""",
    "کنترل کارشناس: قطعی سمت کارگاه + اعتراض ۴۸ ساعته")

# --------------------------------------------------------------- topUp: بسته/انقضا
rep("""      st.balance += pack.credits;
      creditLog(st, CREDITS.demoMode ? 'demo-topup' : 'topup', pack.credits,
        CREDITS.demoMode ? `شارژ نمایشی «${pack.title}»` : `شارژ «${pack.title}»`);""",
"""      st.balance += pack.credits;
      if (!Array.isArray(st.lots)) st.lots = [];
      st.lots.push({ at: new Date().toISOString(), credits: pack.credits, left: pack.credits, pack: pack.title });
      creditLog(st, CREDITS.demoMode ? 'demo-topup' : 'topup', pack.credits,
        `${CREDITS.demoMode ? `شارژ نمایشی «${pack.title}»` : `شارژ «${pack.title}»`} · ${creditFa(CREDITS.expiryMonths)} ماه اعتبار`);""",
    "topUpCredits: ثبت بسته + انقضا")

rep("""      st.history = []; st.spentTotal = 0; st.sessions = [];""",
"""      st.history = []; st.spentTotal = 0; st.sessions = []; st.lots = []; st.disputes = [];""",
    "resetCreditDemo: پاک‌کردن بسته‌ها و اعتراض‌ها")

# --------------------------------------------------- renderCreditUI: یادداشت انقضا
rep("""    function renderCreditUI() {
      const st = creditState();
      const bal = document.getElementById('walletBalance');
      if (bal) bal.textContent = creditFa(st.balance);""",
"""    function renderCreditUI() {
      const st = creditState();
      const bal = document.getElementById('walletBalance');
      if (bal) bal.textContent = creditFa(st.balance);

      // تصمیم ۱: تاریخ انقضای اعتبار + تصمیم ۳: اعتبار ماهانهٔ طرح‌های Care
      const expEl = document.getElementById('walletExpiryNote');
      if (expEl) {
        const info = creditExpiryInfo();
        expEl.textContent = info.hasLot
          ? `اعتبار فعلی تا ${info.label} اعتبار دارد (${creditFa(CREDITS.expiryMonths)} ماه از تاریخ شارژ).`
          : `هر شارژ ${creditFa(CREDITS.expiryMonths)} ماه اعتبار دارد.`;
      }
      const careEl = document.getElementById('walletCareNote');
      if (careEl) {
        careEl.textContent = `طرح‌های Care اعتبار ماهانه دارند (${creditFa(CREDITS.careMonthlyCredits[0])}، ${creditFa(CREDITS.careMonthlyCredits[1])} و ${creditFa(CREDITS.careMonthlyCredits[2])} اعتبار) که خودکار به همین کیف اضافه می‌شود.`;
      }""",
    "renderCreditUI: یادداشت انقضا + Care")

# ----------------------------------------------------- markup: کیف پول (انقضا/Care)
rep("""      <div class="mt-4">
        <span class="text-[11px] font-bold text-brand-dark dark:text-white block mb-1.5">شماره‌های ثبت‌شده برای ساعت خوش‌آمد</span>""",
"""      <div class="mt-3 flex items-start gap-2 p-3 rounded-2xl bg-emerald-500/[0.07] border border-emerald-500/20">
        <span class="text-xs">⏳</span>
        <p class="text-[10px] text-brand-gray leading-relaxed mb-0">
          <b class="text-brand-dark dark:text-white">مهلت اعتبار:</b>
          <span id="walletExpiryNote"></span>
          <span id="walletCareNote" class="block mt-1"></span>
        </p>
      </div>

      <div class="mt-4">
        <span class="text-[11px] font-bold text-brand-dark dark:text-white block mb-1.5">شماره‌های ثبت‌شده برای ساعت خوش‌آمد</span>""",
    "markup کیف پول: جعبهٔ انقضا + Care")

# ------------------------------------------------- markup: طرح‌های Care (اعتبار ماهانه)
rep("""            <li class="flex items-center gap-2">✓ ۲ جلسه پشتیبانی ریموت فوری در ماه</li>""",
"""            <li class="flex items-center gap-2">✓ <b class="text-brand-dark dark:text-white">۳۰۰ اعتبار پشتیبانی ریموت در ماه (تا ۵ ساعت)</b></li>""",
    "Care شخصی: ۳۰۰ اعتبار ماهانه")

rep("""            <li class="flex items-center gap-2">✓ پشتیبانی ریموت نامحدود شبانه‌روزی بدون صف</li>""",
"""            <li class="flex items-center gap-2">✓ <b class="text-brand-dark dark:text-white">۹۰۰ اعتبار پشتیبانی ریموت در ماه (تا ۱۵ ساعت)</b> — نوبت‌دهی بدون صف</li>""",
    "Care Pro: ۹۰۰ اعتبار ماهانه (جای «نامحدود» تا تناقض نباشد)")

rep("""            <li class="flex items-center gap-2">✓ پوشش ریموت شبانه‌روزی برای همهٔ دستگاه‌های شبکه</li>""",
"""            <li class="flex items-center gap-2">✓ <b class="text-brand-dark dark:text-white">۳٬۰۰۰ اعتبار ریموت تیمی در ماه</b></li>
            <li class="flex items-center gap-2">✓ پوشش ریموت شبانه‌روزی برای همهٔ دستگاه‌های شبکه</li>""",
    "Care Business: ۳٬۰۰۰ اعتبار ماهانه")

rep("""    </div>
  </section>

  <!-- FAQ Section with Generous Padding -->""",
"""    </div>

    <p class="text-[11px] text-brand-gray text-center mt-6 leading-relaxed">
      اعتبار ماهانهٔ هر طرح به کیف اعتبار شما واریز می‌شود و مثل اعتبار خریداری‌شده <b class="text-brand-dark dark:text-white">۱۲ ماه</b> اعتبار دارد.
      مصرف جلسه‌های ریموت از همین اعتبار کم می‌شود —
      <a href="#" onclick="openWalletModal();return false;" class="text-brand-blue font-bold hover:underline">دیدن کیف اعتبار</a>
    </p>
  </section>

  <!-- FAQ Section with Generous Padding -->""",
    "markup طرح‌ها: پانویس اعتبار ماهانه")

# --------------------------------------------------------- markup: نوار جلسه (alert + drop)
rep("""        <button onclick="pauseChargeSession()" id="creditSessionPauseBtn" class="px-2.5 py-1 rounded-full bg-white/15 dark:bg-black/10 hover:bg-white/25 transition text-[10px] font-bold">توقف موقت</button>""",
"""        <span id="creditSessionAlert" class="hidden items-center gap-1.5 px-2 py-0.5 rounded-full bg-rose-500/30 font-bold whitespace-nowrap">
          <span id="creditSessionAlertText">۵ دقیقه تا اتمام اعتبار</span>
          <button onclick="openWalletModal()" class="underline hover:no-underline">شارژ سریع</button>
        </span>
        <button onclick="toggleWorkshopDrop()" id="creditSessionDropBtn" aria-pressed="false" class="px-2.5 py-1 rounded-full bg-amber-400/25 hover:bg-amber-400/40 transition text-[10px] font-bold">قطعی سمت کارگاه</button>
        <button onclick="pauseChargeSession()" id="creditSessionPauseBtn" class="px-2.5 py-1 rounded-full bg-white/15 dark:bg-black/10 hover:bg-white/25 transition text-[10px] font-bold">توقف موقت</button>""",
    "نوار جلسه: اعلان کم‌موجودی + دکمهٔ قطعی")

# --------------------------------------------------------- markup: ردیف اعتراض در پیگیری
rep("""          <div id="trackCreditsRow" class="hidden flex items-center justify-between gap-3 pb-3 border-b border-black/[0.06] dark:border-white/[0.06]">
            <span class="text-brand-gray">محاسبهٔ اعتبار جلسه:</span>
            <b id="trackCreditsText" class="text-brand-dark dark:text-white">—</b>
          </div>""",
"""          <div id="trackCreditsRow" class="hidden flex items-center justify-between gap-3 pb-3 border-b border-black/[0.06] dark:border-white/[0.06]">
            <span class="text-brand-gray">محاسبهٔ اعتبار جلسه:</span>
            <b id="trackCreditsText" class="text-brand-dark dark:text-white">—</b>
          </div>
          <div id="trackDisputeRow" class="hidden flex items-start justify-between gap-3 pb-3 border-b border-black/[0.06] dark:border-white/[0.06]">
            <span class="text-brand-gray">اعتراض به مصرف این جلسه:</span>
            <div class="text-left grow">
              <b id="trackDisputeStatus" class="text-amber-600 dark:text-amber-400 block text-[11px] font-bold"></b>
              <button id="trackDisputeBtn" onclick="toggleDisputeForm()" class="hidden mt-1.5 px-2.5 py-1 rounded-full border border-black/[0.08] dark:border-white/[0.08] hover:bg-black/5 dark:hover:bg-white/10 text-[10px] font-bold transition"></button>
              <div id="trackDisputeForm" class="hidden mt-2">
                <textarea id="trackDisputeReason" rows="2" placeholder="در یک جمله بنویسید چه چیزی حل نشد…" class="w-full text-[11px] p-2 rounded-xl bg-white dark:bg-black/20 border border-black/[0.08] dark:border-white/[0.08] outline-none focus:border-brand-blue"></textarea>
                <button onclick="submitCreditDispute()" class="mt-1.5 px-3 py-1 rounded-full bg-brand-blue hover:bg-brand-blueHover text-white text-[10px] font-bold transition">ثبت اعتراض</button>
              </div>
            </div>
          </div>""",
    "ماژول پیگیری: ردیف اعتراض ۴۸ ساعته")

rep("""      const creditRow = document.getElementById("trackCreditsRow");
      const creditText = document.getElementById("trackCreditsText");
      if (creditRow && creditText) {
        if (ticket && ticket.creditsText) { creditText.textContent = ticket.creditsText; creditRow.classList.remove("hidden"); }
        else { creditRow.classList.add("hidden"); }
      }""",
"""      const creditRow = document.getElementById("trackCreditsRow");
      const creditText = document.getElementById("trackCreditsText");
      if (creditRow && creditText) {
        if (ticket && ticket.creditsText) { creditText.textContent = ticket.creditsText; creditRow.classList.remove("hidden"); }
        else { creditRow.classList.add("hidden"); }
      }
      // تصمیم ۲: پنجرهٔ ۴۸ ساعتهٔ اعتراض به مصرف همین جلسه
      renderTrackDispute(val);""",
    "searchTrackingTicket: نمایش ردیف اعتراض")

# ------------------------------------------------------------- init: sweep در بارگذاری
rep("""      renderCreditUI();          // ROUND-3: نمایش اعتبار در پنل کاربری""",
"""      creditSweepExpired();      // ROUND-3 تصمیم ۱: اعتبار منقضی همان لحظهٔ ورود سوخته می‌شود
      renderCreditUI();          // ROUND-3: نمایش اعتبار در پنل کاربری""",
    "DOMContentLoaded: sweep انقضا")

# ---------------------------------------------------------------------- نشانگر
rep("""const CREDITS = {""",
"""/* ROUND-3-CREDITS-FINAL — تصمیم‌های ۱…۵ اعتبار (انقضا، اعتراض ۴۸ ساعته، اعتبار Care، اعلان کم‌موجودی، قطعی سمت کارگاه) */
    const CREDITS = {""",
    "نشانگر پچ")

io.open(P, 'w', encoding='utf-8').write(s)
print('\n'.join(f'  ✓ {d}' for d in done))
print(f'\nDone — {len(s)} chars written.')
