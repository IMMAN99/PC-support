"""Round 3 — the shop's second change list.

Run:  python3 tools/patches/patch_round3.py        (idempotent, marker: ROUND-3)

1. header: every previous item is back (nav «تست سرعت SSD», theme toggle on phones,
   «رزرو حضوری»), CTA renamed «درخواست ریموت», Night Mode moved to the end of the bar,
   and a «بیشتر ⋯» overflow keeps the remaining actions one click away on narrow desktops
   (nothing is deleted). Container widened to max-w-[1400px] so the full row fits ≥1200px.
2. all prices removed from the site except the Care plans (booking cards, booking totals,
   step-3 summary, service catalog, the AI cost answer, the hero «رایگان» claim).
4. AI: a new triage layer in front of the (untouched) knowledge engine — synonym expansion,
   weighted symptom scoring, a clarifying question with ready-made chips when the input is
   vague, short-answer memory, safety warnings, and zero pricing in any AI output.
5. in-person services made generic (brand name removed) + a fifth «سایر خدمات» option with
   a text field that flows into the ticket and the summary.
6. «intakeHoursDot» removed from the amber hero box.
"""
import io
import sys

P = "/home/user/پشتیبان_رایانه.html"
src = io.open(P, encoding="utf-8").read()

if "ROUND-3" in src:
    sys.exit("already applied — ROUND-3 marker found, nothing written")

ok = []


def sub(old, new, label):
    global src
    if old not in src:
        sys.exit(f"ANCHOR NOT FOUND [{label}]:\n{old[:420]}")
    src = src.replace(old, new, 1)
    ok.append(label)


# =============================================================== 1. HEADER
sub('<div class="max-w-6xl mx-auto px-2.5 sm:px-6 h-12 flex flex-nowrap items-center justify-between gap-1 sm:gap-2 lg:gap-3">',
    '<div class="max-w-[1400px] mx-auto px-3 sm:px-6 h-12 flex flex-nowrap items-center justify-between gap-1.5 sm:gap-2 xl:gap-3">',
    "1) header container widened to 1400px")

sub('        <a href="#remote-support" class="hover:text-brand-blue transition-colors whitespace-nowrap">پشتیبانی ریموت</a>\n',
    '        <a href="#remote-support" class="hover:text-brand-blue transition-colors whitespace-nowrap">پشتیبانی ریموت</a>\n'
    '        <a href="#speed-booster" class="hover:text-brand-blue transition-colors whitespace-nowrap">تست سرعت SSD</a>\n',
    "1) nav: «تست سرعت SSD» back in the bar")

sub('<button onclick="toggleAiDrawer(true)" class="hidden xl:flex items-center gap-1 px-2.5 py-1',
    '<button onclick="toggleAiDrawer(true)" class="hidden min-[1200px]:flex items-center gap-1 px-2.5 py-1',
    "1) AI action: inline from 1200px")
sub('<button onclick="openTrackingModal()" class="hidden sm:inline-flex text-[11px] font-semibold px-2.5 sm:px-3',
    '<button onclick="openTrackingModal()" class="hidden min-[1200px]:inline-flex text-[11px] font-semibold px-2.5 sm:px-3',
    "1) tracking stays in ⋯ below 1200px")
sub('<button onclick="openBookingModal()" class="hidden xl:inline-flex text-[11px] font-semibold px-3 py-1',
    '<button onclick="openBookingModal()" class="hidden min-[1200px]:inline-flex text-[11px] font-semibold px-3 py-1',
    "1) booking: inline from 1200px")

# CTA rename (header) — «درخواست پشتیبانی ریموت» → «درخواست ریموت»
sub('<button onclick="openRemoteModal()" class="inline-flex items-center gap-1.5 text-[11px] font-semibold px-2.5 sm:px-3.5 py-1 rounded-full bg-brand-blue hover:bg-brand-blueHover text-white shadow-sm transition shrink-0 whitespace-nowrap">\n'
    '          <span class="w-1.5 h-1.5 rounded-full bg-white/90 animate-pulse"></span>\n'
    '          <span>درخواست پشتیبانی ریموت</span>',
    '<button onclick="openRemoteModal()" class="inline-flex items-center gap-1.5 text-[11px] font-semibold px-2.5 sm:px-3.5 py-1 rounded-full bg-brand-blue hover:bg-brand-blueHover text-white shadow-sm transition shrink-0 whitespace-nowrap">\n'
    '          <span class="w-1.5 h-1.5 rounded-full bg-white/90 animate-pulse"></span>\n'
    '          <span>درخواست ریموت</span>',
    "1) header CTA renamed «درخواست ریموت»")

# theme toggle: out of its old slot …
sub('''        <!-- Theme Switcher -->
        <button id="themeToggleBtn" onclick="toggleTheme()" aria-label="تغییر تم" class="hidden sm:flex w-7 h-7 rounded-full flex items-center justify-center text-brand-dark/70 dark:text-white/70 hover:bg-black/5 dark:hover:bg-white/10 transition shrink-0">
          <span id="themeToggleIcon" class="text-xs">🌙</span>
        </button>

''', '', "1) theme toggle lifted out of the middle")

# … the «more» overflow keeps every action reachable on narrow desktops
sub('''        <!-- Mobile Drawer Toggle -->''',
    '''        <!-- Overflow: below 1200px the extra actions live here, so nothing disappears -->
        <div class="relative hidden min-[640px]:flex min-[1200px]:hidden shrink-0">
          <button type="button" onclick="toggleHeaderMore(event)" id="headerMoreBtn" aria-haspopup="menu" aria-expanded="false" aria-label="گزینه‌های بیشتر"
                  class="flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-semibold bg-black/5 dark:bg-white/10 hover:bg-brand-blue/10 hover:text-brand-blue text-brand-dark/80 dark:text-white/80 transition whitespace-nowrap">
            <span>بیشتر</span><span aria-hidden="true">⋯</span>
          </button>
          <div id="headerMoreMenu" role="menu" aria-label="گزینه‌های بیشتر"
               class="hidden absolute left-0 top-full mt-2 w-56 p-1.5 rounded-2xl bg-white/95 dark:bg-[#1c1c1e]/95 backdrop-blur-xl border border-black/[0.08] dark:border-white/[0.1] shadow-xl z-50 space-y-1">
            <button type="button" role="menuitem" onclick="toggleAiDrawer(true); closeHeaderMore();" class="w-full text-right px-3 py-2 rounded-xl text-[11px] font-semibold text-brand-dark dark:text-white hover:bg-brand-blue/10 hover:text-brand-blue transition">✦ مشاور هوشمند فنی</button>
            <button type="button" role="menuitem" onclick="openTrackingModal(); closeHeaderMore();" class="w-full text-right px-3 py-2 rounded-xl text-[11px] font-semibold text-brand-dark dark:text-white hover:bg-brand-blue/10 hover:text-brand-blue transition">پیگیری وضعیت دستگاه</button>
            <button type="button" role="menuitem" onclick="openBookingModal(); closeHeaderMore();" class="w-full text-right px-3 py-2 rounded-xl text-[11px] font-semibold text-brand-dark dark:text-white hover:bg-brand-blue/10 hover:text-brand-blue transition">رزرو نوبت حضوری (کارگاه)</button>
          </div>
        </div>

        <!-- Mobile Drawer Toggle -->''',
    "1) «بیشتر ⋯» overflow added")

# … and back in at the very end of the bar (Night Mode = last item)
sub('''        <!-- Mobile Drawer Toggle -->
        <button onclick="toggleMobileMenu()" aria-label="منوی موبایل" class="lg:hidden p-1.5 text-brand-dark dark:text-white shrink-0">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16m-7 6h7"></path>
          </svg>
        </button>''',
    '''        <!-- Mobile Drawer Toggle -->
        <button onclick="toggleMobileMenu()" aria-label="منوی موبایل" class="lg:hidden p-1.5 text-brand-dark dark:text-white shrink-0">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16m-7 6h7"></path>
          </svg>
        </button>

        <!-- Night Mode — last control of the header (round 3, item 1) -->
        <button id="themeToggleBtn" onclick="toggleTheme()" aria-label="تغییر تم (حالت شب)" title="حالت شب / روز" class="flex w-7 h-7 rounded-full items-center justify-center text-brand-dark/70 dark:text-white/70 hover:bg-black/5 dark:hover:bg-white/10 transition shrink-0">
          <span id="themeToggleIcon" class="text-xs">🌙</span>
        </button>''',
    "1) theme toggle at the end of the header")

# mobile drawer primary CTA (mobile twin of the header CTA)
sub('''      <button onclick="openRemoteModal(); toggleMobileMenu();" class="col-span-2 py-2 text-center rounded-xl bg-purple-500/10 text-purple-600 dark:text-purple-400 font-bold">
        درخواست پشتیبانی ریموت
      </button>''',
    '''      <button onclick="openRemoteModal(); toggleMobileMenu();" class="col-span-2 py-2 text-center rounded-xl bg-purple-500/10 text-purple-600 dark:text-purple-400 font-bold">
        درخواست ریموت
      </button>''',
    "1) drawer CTA renamed too")

# header-more behaviour
sub('    function sendQuickAiQuery(query) {',
    '''    function toggleHeaderMore(e) {
      if (e && e.stopPropagation) e.stopPropagation();
      const menu = document.getElementById('headerMoreMenu');
      const btn = document.getElementById('headerMoreBtn');
      if (!menu || !btn) return;
      const willOpen = menu.classList.contains('hidden');
      menu.classList.toggle('hidden', !willOpen);
      btn.setAttribute('aria-expanded', String(willOpen));
    }
    function closeHeaderMore() {
      const menu = document.getElementById('headerMoreMenu');
      const btn = document.getElementById('headerMoreBtn');
      if (menu) menu.classList.add('hidden');
      if (btn) btn.setAttribute('aria-expanded', 'false');
    }

    function sendQuickAiQuery(query) {''',
    "1) header-more JS")

sub('''        (typeof MODAL_DROPDOWNS !== 'undefined' ? MODAL_DROPDOWNS : []).forEach(key => {''',
    '''        const moreBtn = document.getElementById('headerMoreBtn');
        if (moreBtn && !moreBtn.parentElement.contains(e.target)) closeHeaderMore();
        (typeof MODAL_DROPDOWNS !== 'undefined' ? MODAL_DROPDOWNS : []).forEach(key => {''',
    "1) click-outside closes the ⋯ menu")
sub('''          ['cpu', 'ram', 'storage'].forEach(closeCustomDropdown);''',
    '''          ['cpu', 'ram', 'storage'].forEach(closeCustomDropdown);
          closeHeaderMore();''',
    "1) Esc closes the ⋯ menu")

# =============================================================== 2. NO PRICES
for amount, label in (("۲۵۰٬۰۰۰", "ssd"), ("۱۸۰٬۰۰۰", "thermal"), ("۱۲۰٬۰۰۰", "ram"), ("۳۰۰٬۰۰۰", "mobo")):
    sub(f'<span class="text-xs font-mono font-bold text-brand-blue">{amount} تومان</span>', '',
        f"2) price removed from the {label} card")

sub('<span class="text-brand-gray">جمع برآورد اجرت: <b id="bookSelectedTotalText" class="text-brand-dark dark:text-white font-mono font-bold">۲۵۰٬۰۰۰ تومان</b></span>',
    '<span class="text-brand-gray">اجرت و قطعات پس از عیب‌یابی و تأیید شما نهایی می‌شود.</span>',
    "2) step-1 total row → neutral note")
sub('<span class="text-brand-gray">جمع برآورد:</span>',
    '<span class="text-brand-gray">برآورد اجرت:</span>',
    "2) step-3 label")
sub('<span id="bookSummaryPriceText" class="font-mono font-bold text-brand-dark dark:text-white">۲۵۰٬۰۰۰ تومان</span>',
    '<span id="bookSummaryPriceText" class="font-bold text-brand-dark dark:text-white">پس از عیب‌یابی و تأیید شما</span>',
    "2) step-3 value → neutral note")

sub('ssd: { name: "ارتقای SSD + کلون سکتوری ویندوز", price: 250000, type: "اجرت تخصصی" },',
    'ssd: { name: "ارتقای حافظهٔ SSD (کلون کامل ویندوز)", type: "خدمات کارگاه" },', "2) catalog: ssd")
sub('thermal: { name: "سرویس دوره‌ای فن و تعویض خمیر سیلیکون", price: 180000, type: "سرویس فیزیکی" },',
    'thermal: { name: "سرویس دوره‌ای فن و تعویض خمیر سیلیکون", type: "سرویس فیزیکی" },', "2) catalog: thermal")
sub('ram: { name: "ارتقای ماژول حافظه رم (RAM)", price: 120000, type: "سخت‌افزار / اجرت" },',
    'ram: { name: "ارتقای ماژول حافظه رم (RAM)", type: "سخت‌افزار / اجرت" },', "2) catalog: ram")
sub('mobo: { name: "عیب‌یابی تخصصی مادربرد و مدار تغذیه", price: 300000, type: "آزمایشگاهی" }',
    'mobo: { name: "عیب‌یابی تخصصی مادربرد و مدار تغذیه", type: "آزمایشگاهی" },\n'
    'other: { name: "سایر خدمات (شرح مشتری)", type: "بر اساس شرح مشتری" }',
    "2+5) catalog: mobo + new «سایر خدمات»")

sub('let totalPrice = 0;', '', "2) JS: no price accumulation")
sub('totalPrice += SERVICES_CATALOG[id].price;', '', "2) JS: no price accumulation (2)")
sub('const totalText = document.getElementById("bookSelectedTotalText");', '', "2) JS: total element gone")
sub('if (totalText) totalText.textContent = `${totalPrice.toLocaleString("fa-IR")} تومان`;', '',
    "2) JS: no price write (step 1)")
sub('let sum = 0;', '', "2) JS: no sum")
sub('if (SERVICES_CATALOG[id]) sum += SERVICES_CATALOG[id].price;', '', "2) JS: no sum (2)")
sub('if (priceSummary) priceSummary.textContent = `${sum.toLocaleString("fa-IR")} تومان`;',
    'if (priceSummary) priceSummary.textContent = "پس از عیب‌یابی و تأیید شما";',
    "2) JS: neutral summary value")

sub('تعرفه‌ها و ضمانت خدمات کارگاه پشتیبان پی‌سی:',
    '### دربارهٔ اعلام هزینه و ضمانت خدمات',
    "2) AI cost answer: title")
sub('مطابق نرخ مصوبه اتحادیه و همراه با **ضمانت کتبی کارگاه** و ارائه قرارداد رسمی تحویل مشتری می‌گردد. برای استعلام هزینه دقیق قطعه انتخابی می‌توانید از طریق دکمه رزرو نوبت اقدام فرمایید.',
    'این دستیار هیچ قیمت، تعرفه یا برآورد هزینه‌ای اعلام نمی‌کند؛ مبلغ نهایی به قطعه، مدل دستگاه و نتیجهٔ عیب‌یابی بستگی دارد. کیفیت کار با **ضمانت کتبی کارگاه** و قرارداد رسمی تحویل تضمین می‌شود.\n'
    '**مسیر درست:** اول عیب‌یابی دقیق (همین چت یا سکشن «عیب‌یابی هوشمند»)، بعد انتخاب بین «درخواست ریموت» و «رزرو حضوری».',
    "2) AI cost answer: body without pricing")

sub('هر سؤالی درباره ارتقا، کندی سیستم، خطاهای ویندوز، قیمت خدمات یا انتخاب قطعات سازگار دارید بفرمایید تا راهنمایی‌تان کنم.',
    'هر سؤالی درباره ارتقا، کندی سیستم، خطاهای ویندوز یا انتخاب قطعات سازگار دارید بفرمایید تا راهنمایی‌تان کنم.',
    "2) AI greeting: no price topic")
sub('<span>عیب‌یابی رایگان سیستم</span>', '<span>شروع عیب‌یابی سیستم</span>',
    "2) hero CTA: «رایگان» claim removed")

# =============================================================== 4. SMARTER AI
sub('function runLocalIntelligentEngine(type, userQuery, notes = "") {',
    'function runLocalKnowledgeEngine(type, userQuery, notes = "") {',
    "4) knowledge engine renamed (body untouched)")

AI_LAYER = r'''    /* ================= ROUND-3: لایهٔ هوشمند تشخیص =================
       موتور دانش (runLocalKnowledgeEngine) دست‌نخورده می‌ماند؛ این لایه پیش از آن اجرا می‌شود:
       ۱) نشانه‌های عامیانه/مترادف را به نشانه‌های استاندارد ترجمه می‌کند،
       ۲) نشانه‌ها را وزن‌دار امتیاز می‌دهد (به‌جای اولین تطبیق، قوی‌ترین تطبیق)،
       ۳) اگر نشانه کافی نباشد، به‌جای حدس زدن پرسش روشنگر با گزینه‌های آماده می‌پرسد،
       ۴) پاسخ کوتاه مرحلهٔ قبل («۱»، «بله»، نام گزینه) را به همان گفت‌وگو وصل می‌کند،
       ۵) برای نشانه‌های خطرناک، هشدار ایمنی به پاسخ اضافه می‌کند،
       ۶) هیچ قیمت/تعرفه‌ای تولید نمی‌کند. */
    const AI_INTENTS = [
      { id: 'bsod', crit: false, title: 'خطای صفحه آبی / ریستارت ناگهانی', canon: 'صفحه آبی کرش ریستارت',
        kws: [['صفحه آبی', 10], ['صفحه‌آبی', 10], ['بلو اسکرین', 10], ['بلواکرین', 10], ['blue screen', 10], ['bsod', 10],
              ['ارور آبی', 9], ['استاپ کد', 9], ['stop code', 9], ['critical_process', 10], ['memory_management', 10],
              ['مدیریت حافظه', 9], ['whea', 10], ['ریستارت می‌شه', 6], ['ریست میشه', 6], ['کرش', 6], ['crash', 6]] },
      { id: 'liquid', crit: true, title: 'نفوذ مایعات', canon: 'آب ریخت مایعات خیس',
        kws: [['آب ریخت', 12], ['آب خورد', 12], ['نفوذ آب', 12], ['آب روی', 10], ['ریختم', 9], ['ریخته', 9],
              ['مایعات', 10], ['مایع', 10], ['خیس', 9], ['چای', 9], ['قهوه', 9], ['نوشیدنی', 9], ['شربت', 9],
              ['کیبورد خیس', 10], ['صفحه خیس', 10]] },
      { id: 'burned', crit: true, title: 'بوی سوختگی / دود', canon: 'بوی سوختگی دود جرقه',
        kws: [['بوی سوختگی', 12], ['بو سوخت', 12], ['بوی سوخته', 12], ['سوخت', 9], ['دود', 10], ['جرقه', 10],
              ['آتش', 10], ['ماسفت', 8], ['سیم سوخته', 12]] },
      { id: 'thermal', crit: false, title: 'داغ شدن و فن', canon: 'داغ می‌کنه فن حرارت',
        kws: [['داغ', 9], ['حرارت', 9], ['گرم می‌کنه', 9], ['دما', 8], ['فن', 7], ['فنش', 7], ['صدای فن', 9],
              ['خاموش می‌شه', 7], ['خاموش می‌شود', 7], ['تهویه', 6], ['گوشت', 6], ['thermal', 8]] },
      { id: 'disk', crit: false, title: 'کندی دیسک / هارد', canon: 'هارد کند فریز درایو',
        kws: [['هارد', 9], ['دیسک', 9], ['درایو', 9], ['ssd', 9], ['اس اس دی', 9], ['کندی', 7], ['کند شده', 8],
              ['فریز', 8], ['هن', 7], ['بوت طول می‌کشه', 8], ['صد در صد دیسک', 10], ['۱۰۰ درصد دیسک', 10]] },
      { id: 'power', crit: false, title: 'روشن نشدن / تصویر نداشتن', canon: 'روشن نمی‌شه تصویر بوت بوق برق',
        kws: [['روشن نمی‌شه', 10], ['روشن نمیشه', 10], ['روشن نمی‌شود', 10], ['بالا نمیاد', 9], ['بالا نمی‌آید', 9],
              ['بوت نمی‌شه', 9], ['تصویر نمی‌ده', 10], ['تصویر نمی‌دهد', 10], ['صفحه سیاه', 10], ['بوق می‌زنه', 9],
              ['صدای بوق', 9], ['شارژ نمی‌شه', 9], ['برق', 6]] },
      { id: 'perf', crit: false, title: 'افت فریم و لگ بازی', canon: 'افت فریم لگ استاتر',
        kws: [['افت فریم', 10], ['فریم‌ریت', 8], ['فریم', 7], ['لگ', 9], ['fps', 9], ['استاتر', 9], ['لگ می‌زنه', 9],
              ['برای بازی', 6], ['گیمینگ', 6]] },
      { id: 'gpuart', crit: false, title: 'خط و آرتیفکت تصویر', canon: 'آرتیفکت خط روی صفحه شطرنجی',
        kws: [['آرتیفکت', 12], ['شطرنجی', 10], ['خط روی صفحه', 10], ['پرش تصویر', 9], ['بنفش', 8], ['گرافیک', 6]] },
      { id: 'noise', crit: false, title: 'صدای غیرعادی', canon: 'صدای غیرعادی صدا می‌ده',
        kws: [['صدای عجیب', 8], ['صدا می‌ده', 7], ['سوت می‌کشه', 8], ['تق تق', 7], ['وزوز', 7], ['صدای تق', 8]] }
    ];

    const AI_TRIAGE_CHIPS = [
      { label: 'روشن نمی‌شود / تصویر ندارد', q: 'دستگاه روشن نمی‌شود و تصویر نمی‌دهد' },
      { label: 'صفحه آبی / ریستارت می‌شود', q: 'صفحه آبی می‌دهد و ریستارت می‌شود' },
      { label: 'داغ می‌کند / صدای فن', q: 'دستگاه داغ می‌کند و صدای فن بلند شده' },
      { label: 'کند شده / فریز می‌کند', q: 'سیستم کند شده و فریز می‌کند (هارد)' },
      { label: 'مایعات یا بوی سوختگی', q: 'آب ریخت روی دستگاه و بوی سوختگی می‌دهد' },
      { label: 'مشکل ویندوز و نرم‌افزار', q: 'ویندوز بالا نمی‌آید و خطا می‌دهد' }
    ];

    let aiPendingTriage = null;      // گزینه‌های پرسش روشنگر
    let aiPendingGuess = null;       // نزدیک‌ترین احتمال، برای پاسخ «بله»
    let aiDefaultChipsHTML = null;

    function aiNormalize(t) {
      return String(t || '')
        .replace(/[‌‍]/g, ' ')             // نیم‌فاصله/اتصال‌گر → فاصله (برای تطبیق ساده‌تر)
        .replace(/[يى]/g, 'ی').replace(/ك/g, 'ک')
        .replace(/\s+/g, ' ').trim();
    }

    function aiScore(text) {
      const t = aiNormalize(text);
      const out = [];
      AI_INTENTS.forEach(intent => {
        let score = 0;
        intent.kws.forEach(([kw, w]) => { if (t.includes(aiNormalize(kw))) score += w; });
        if (score > 0) out.push({ id: intent.id, title: intent.title, canon: intent.canon, crit: intent.crit, score });
      });
      return out.sort((a, b) => b.score - a.score);
    }

    function aiExpandQuery(text) {
      const ranked = aiScore(text);
      const t = aiNormalize(text);
      const canon = ranked.slice(0, 2).map(r => r.canon).join(' ');
      return canon ? `${t} ${canon}` : t;
    }

    function faNum(n) { return Number(n).toLocaleString('fa-IR'); }

    function renderAiQuickChips(list) {
      const wrap = document.getElementById('aiQuickChips');
      if (!wrap) return;
      if (aiDefaultChipsHTML === null) aiDefaultChipsHTML = wrap.innerHTML;
      if (!list) { wrap.innerHTML = aiDefaultChipsHTML; return; }
      wrap.innerHTML = list.map(c =>
        `<button type="button" onclick="sendQuickAiQuery('${c.q.replace(/'/g, "\\'")}')" class="whitespace-nowrap px-2.5 py-1 rounded-full bg-purple-500/10 dark:bg-purple-500/15 hover:bg-purple-500/20 text-[10px] font-semibold text-purple-600 dark:text-purple-400 transition">${c.label}</button>`
      ).join('');
    }

    /* پاسخ کوتاه مرحلهٔ قبل را به گزینهٔ درست وصل می‌کند («۲»، «بله»، «آره») */
    function aiResolveShortAnswer(raw) {
      const t = aiNormalize(raw);
      const digits = { '۱': 0, '۲': 1, '۳': 2, '۴': 3, '۵': 4, '۶': 5 };
      if (digits[t] !== undefined) return digits[t];
      if (/^[1-6]$/.test(t)) return Number(t) - 1;
      if (/^(بله|آره|بلی|همینه|همین‌ه|درسته|بله همینه)/.test(t)) return 'GUESS';
      if (aiPendingTriage) {
        const idx = aiPendingTriage.findIndex(c => aiNormalize(c.label).includes(t) && t.length >= 4);
        if (idx >= 0) return idx;
      }
      return -1;
    }

    function aiTriageAnswer(guess, raw) {
      const lines = AI_TRIAGE_CHIPS.map((c, i) => `${faNum(i + 1)}. ${c.label}`);
      return `### برای تشخیص دقیق‌تر، یک نشانه بگو
برای اینکه اشتباه راهنمایی نکنم، به یک نشانهٔ بیشتر نیاز دارم. یکی از گزینه‌ها را بزن یا شماره‌اش را بنویس:

${lines.join('\n')}
${guess ? `\n**نزدیک‌ترین احتمال از توضیح تو:** «${guess.title}» — اگر همین است بنویس «بله».` : ''}
**نکته:** مدل دستگاه، صدای شنیده‌شده یا متن دقیق خطای ویندوز، تشخیص را دقیق‌تر می‌کند.`;
    }

    function runLocalIntelligentEngine(type, userQuery, notes = "") {
      if (type === 'vision') return runLocalKnowledgeEngine(type, userQuery, notes);

      let text = aiNormalize(userQuery);
      if (!text) return aiTriageAnswer(null, '');

      // حافظه: پاسخ کوتاه مرحلهٔ قبل
      if (aiPendingTriage) {
        const pick = aiResolveShortAnswer(text);
        if (pick === 'GUESS' && aiPendingGuess) {
          text = aiPendingGuess.canon;
        } else if (typeof pick === 'number' && aiPendingTriage[pick]) {
          text = aiPendingTriage[pick].q;
        } else {
          aiPendingTriage = null; aiPendingGuess = null; renderAiQuickChips(null);
        }
      }

      const ranked = aiScore(text);
      const top = ranked[0];

      // نشانهٔ کافی نیست → پرسش روشنگر (به‌جای حدس)
      if (!top || top.score < 6) {
        const guess = ranked.slice(0, 1)[0] || null;
        const chips = guess ? AI_TRIAGE_CHIPS.filter(c => aiScore(c.q).some(r => r.id === guess.id)).slice(0, 3) : [];
        const chipList = (chips.length ? chips : AI_TRIAGE_CHIPS).concat(AI_TRIAGE_CHIPS.filter(c => !(chips.length ? chips : AI_TRIAGE_CHIPS).includes(c))).slice(0, 6);
        aiPendingTriage = chipList;
        aiPendingGuess = guess;
        renderAiQuickChips(chipList);
        return aiTriageAnswer(guess, userQuery);
      }

      aiPendingTriage = null; aiPendingGuess = null; renderAiQuickChips(null);

      let answer = runLocalKnowledgeEngine('text', aiExpandQuery(text), notes);
      if (top.crit) {
        answer += '\n**اقدام فوری:** تا بررسی کارشناس، دستگاه را روشن نکنید و به برق یا شارژر وصل نکنید.';
      }
      if (ranked[1] && ranked[1].score >= 6) {
        answer += `\n**نشانهٔ دوم ثبت شد:** نشانه‌های مربوط به «${ranked[1].title}» هم دیده می‌شود؛ همان را جدا بنویس تا راهنمای همان را بگیری.`;
      }
      answer += '\n**قدم بعدی:** اگر می‌خواهی همین حالا کارشناس بررسی کند از «درخواست ریموت» استفاده کن؛ برای بررسی سخت‌افزاری، «رزرو حضوری» فعال است.';
      return answer;
    }

'''
sub('    function runLocalKnowledgeEngine(type, userQuery, notes = "") {',
    AI_LAYER + '    function runLocalKnowledgeEngine(type, userQuery, notes = "") {',
    "4) triage layer installed in front of the engine")

# chips container gets an id so the triage layer can rewrite it
sub('<div class="px-4 py-2 flex gap-1.5 overflow-x-auto hide-scrollbar border-t border-black/[0.04] dark:border-white/[0.04]">',
    '<div id="aiQuickChips" class="px-4 py-2 flex gap-1.5 overflow-x-auto hide-scrollbar border-t border-black/[0.04] dark:border-white/[0.04]">',
    "4) quick-chips container addressable")

# live-model prompt: same rules (no pricing, ask when data is thin, safety first)
sub('''**خدمت پیشنهادی کارگاه:** [نام یکی از این خدمات دقیق: "ارتقای SSD + کلون سکتوری ویندوز" یا "سرویس دوره‌ای فن و تعویض خمیر سیلیکون" یا "ارتقای ماژول حافظه رم (RAM)" یا "عیب‌یابی تخصصی مادربرد و مدار تغذیه"]`;''',
    '''**خدمت پیشنهادی کارگاه:** [نام یکی از این خدمات دقیق: "ارتقای حافظهٔ SSD (کلون کامل ویندوز)" یا "سرویس دوره‌ای فن و تعویض خمیر سیلیکون" یا "ارتقای ماژول حافظه رم (RAM)" یا "عیب‌یابی تخصصی مادربرد و مدار تغذیه"]

قواعد الزامی:
۱) هیچ قیمت، تعرفه، مبلغ یا تخمین هزینه‌ای اعلام نکن؛ اگر کاربر پرسید، بگو مبلغ پس از عیب‌یابی و تأیید خودش نهایی می‌شود و او را به «درخواست ریموت» یا «رزرو حضوری» راهنمایی کن.
۲) اگر نشانه‌های ارسالی برای تشخیص کافی نیست، اول حداکثر دو پرسش کوتاه و دقیق بپرس و بعد تحلیل بده.
۳) اگر نشانه خطرناک است (مایعات، دود، بوی سوختگی، جرقه)، در ابتدای پاسخ یک هشدار ایمنی بده: دستگاه را روشن نکن و به برق/شارژر وصل نکن.
۴) از نام تجاری خاص برای قطعات استفاده نکن؛ مشخصات فنی کافی است.`;''',
    "4) live-model prompt: no pricing + triage rules")

# ====================================================== 5. GENERIC IN-PERSON SERVICES
sub('<b class="text-xs block text-brand-dark dark:text-white">ارتقای SSD + کلون سکتوری ویندوز</b>',
    '<b class="text-xs block text-brand-dark dark:text-white">ارتقای حافظهٔ SSD (کلون کامل ویندوز)</b>',
    "5) service card 1 made generic")
sub('استفاده از خمیر کربنی مرغوب Thermal Grizzly',
    'خمیر کربنی مرغوب، تمیزکاری کامل فن و هیت‌سینک',
    "5) brand name removed from card 2")
sub('placeholder="مثال: لپ‌تاپ ایسوس K513 یا کیس گیمینگ"',
    'placeholder="مثال: لپ‌تاپ ۱۵ اینچی، اولترابوک یا کیس گیمینگ"',
    "5) brand removed from the device placeholder")
sub('placeholder="مثال: لپ‌تاپ لنوو دارم که بعد از ۱۰ دقیقه بازی فن با صدای زیاد کار میکنه و صفحه خاموش میشه یا ویندوز خطای CR',
    'placeholder="مثال: لپ‌تاپم بعد از ۱۰ دقیقه بازی فن با صدای زیاد کار میکنه و صفحه خاموش میشه یا ویندوز خطای CR',
    "5) brand removed from the AI placeholder")

sub('''          </span>

        </div>

        <!-- Live Selection Counter -->''',
    '''          </span>

          <!-- Round 3, item 5: free-text option for anything not listed above -->
          <button type="button" id="serviceCard_other" onclick="toggleBookingService('other')" aria-pressed="false" class="booking-service-card w-full text-right cursor-pointer p-3.5 rounded-2xl border border-black/[0.08] dark:border-white/[0.08] flex items-center justify-between hover:border-brand-blue transition">
            <span class="flex items-center gap-3">
              <span class="check-box w-5 h-5 rounded-lg border border-black/20 dark:border-white/20 flex items-center justify-center text-xs font-bold transition-all"></span>
              <span>
                <b class="text-xs block text-brand-dark dark:text-white">سایر خدمات</b>
                <span class="text-[11px] text-brand-gray">هر خدمتی که در فهرست نیست؛ کافی است خودتان توضیح دهید</span>
              </span>
            </span>
            <span class="text-[11px] font-bold text-brand-blue whitespace-nowrap">توضیح می‌دهم</span>
          </button>
        </div>

        <!-- Free-text detail for «سایر خدمات» -->
        <div id="bookOtherServiceWrap" class="hidden mt-3">
          <label for="bookOtherServiceInput" class="block text-xs font-semibold text-brand-dark dark:text-white mb-1.5">شرح خدمت مورد نیاز شما</label>
          <textarea id="bookOtherServiceInput" rows="3" placeholder="مثال: تعویض کیبورد لپ‌تاپ، نصب ویندوز و نرم‌افزارهای کاری، راه‌اندازی پرینتر شبکه…"
                    class="w-full bg-brand-lightGray dark:bg-[#161617] border border-black/[0.08] dark:border-white/[0.08] rounded-xl px-3.5 py-2.5 text-xs text-brand-dark dark:text-white placeholder:text-neutral-400 dark:placeholder:text-neutral-500 focus:outline-none focus:border-brand-blue transition"></textarea>
          <p class="text-[10px] text-brand-gray mt-1">نیازی به دانستن نام فنی قطعه نیست؛ هر توضیحی که کمک کند سریع‌تر آماده شویم کافی است.</p>
        </div>

        <!-- Live Selection Counter -->''',
    "5) «سایر خدمات» card + free-text field")

# keep the textarea in sync with the selection, and expose it to the summary
sub('''      updateBookingServiceCardsUI();
    }''',
    '''      syncOtherServiceField();
      updateBookingServiceCardsUI();
    }

    /* ROUND-3: گزینهٔ «سایر خدمات» فیلد توضیح را باز/بسته می‌کند */
    function syncOtherServiceField() {
      const wrap = document.getElementById('bookOtherServiceWrap');
      if (!wrap) return;
      const on = selectedBookingServiceIds.has('other');
      wrap.classList.toggle('hidden', !on);
      if (on) {
        const ta = document.getElementById('bookOtherServiceInput');
        if (ta && !ta.value) ta.focus();
      }
    }''',
    "5) «سایر خدمات» toggle behaviour")

sub('        const priceSummary = document.getElementById("bookSummaryPriceText");',
    '''        const priceSummary = document.getElementById("bookSummaryPriceText");
        const otherRow = document.getElementById('bookSummaryOtherRow');
        const otherText = document.getElementById('bookSummaryOtherText');
        const otherVal = ((document.getElementById('bookOtherServiceInput') || {}).value || '').trim();
        if (otherRow) otherRow.classList.toggle('hidden', !selectedBookingServiceIds.has('other'));
        if (otherText) otherText.textContent = otherVal || 'بدون توضیح';''',
    "5) summary shows the free-text service")

# summary row for the free-text service
sub('''            </div>
          </div>

          <!-- Pre-Intake Workshop Protocol''',
    '''            </div>
            <div id="bookSummaryOtherRow" class="hidden flex justify-between gap-3">
              <span class="text-brand-gray shrink-0">شرح خدمت دلخواه:</span>
              <span id="bookSummaryOtherText" class="font-bold text-brand-dark dark:text-white text-left">—</span>
            </div>
          </div>

          <!-- Pre-Intake Workshop Protocol''',
    "5) summary row for the free text")

# validation + ticket content
sub('''      playHapticSound('success');
      const nameInput = document.getElementById("bookNameInput");''',
    '''      if (selectedBookingServiceIds.has('other')) {
        const otherVal = (document.getElementById('bookOtherServiceInput') || {}).value || '';
        if (otherVal.trim().length < 4) {
          showToast("برای گزینهٔ «سایر خدمات»، لطفاً خدمت مورد نیازتان را در کادر توضیح بنویسید.");
          const ta = document.getElementById('bookOtherServiceInput');
          if (ta) ta.focus();
          return;
        }
      }
      playHapticSound('success');
      const nameInput = document.getElementById("bookNameInput");''',
    "5) validation for the free-text service")

sub('''        services: Array.from(selectedBookingServiceIds),''',
    '''        services: Array.from(selectedBookingServiceIds),
        otherService: ((document.getElementById('bookOtherServiceInput') || {}).value || '').trim(),''',
    "5) ticket carries the free text")

# =============================================================== 6. DOT REMOVED
sub('\n        <span id="intakeHoursDot" class="w-1.5 h-1.5 rounded-full bg-neutral-400 shrink-0"></span>', '',
    "6) intakeHoursDot removed from the amber box")

# ------------------------------------------------------------------- marker
sub('<!-- ROUND-2-HEADER:',
    '''<!-- ROUND-3 (round-2-header follow-up): every header item restored (nav «تست سرعت SSD», theme on phones,
     booking, tracking, AI action), CTA renamed «درخواست ریموت», Night Mode last, «بیشتر ⋯» overflow below
     1200px, container max-w-[1400px]. Prices removed site-wide except Care plans. AI triage layer added.
     In-person services made generic + «سایر خدمات» free-text option. intakeHoursDot removed. -->
<!-- ROUND-2-HEADER:''',
    "marker")

io.open(P, "w", encoding="utf-8").write(src)
for label in ok:
    print(f"  ✓ {label}")
print(f"\nDone — {len(src)} chars written.")
