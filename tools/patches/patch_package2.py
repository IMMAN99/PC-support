#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Package 2 — accessibility patch for پشتیبان_رایانه.html

  F-05  <main id="main"> landmark + keyboard skip link
  F-06  no div[onclick] left: upload zone becomes a real <label> (with drag & drop),
        the four service cards become real <button aria-pressed>
  F-07  every form control has a programmatic label (for= / aria-label)
  F-08  chat drawer: autofocus on open, aria-live history, labelled input, labelled settings button
  F-09  one global :focus-visible ring (mouse users unaffected)
  F-10  calendar disabled/off contrast raised to ≥4.5:1 (light) and legible in dark
  F-13  FAQ accordion: aria-expanded/aria-controls + animated open/close (reduced-motion aware)

Idempotent: aborts if already applied.
"""
import io, re, sys

PATH = "/home/user/پشتیبان_رایانه.html"
s = io.open(PATH, encoding="utf-8").read()

if "PACKAGE-2" in s:
    print("Package 2 already applied — aborting.")
    sys.exit(0)

def sub(old, new, label, count=1):
    global s
    if old not in s:
        raise SystemExit(f"ANCHOR NOT FOUND [{label}]:\n{old[:200]}")
    s = s.replace(old, new, count)
    print(f"  ✓ {label}")

# ============================================================ F-05 landmark ==
sub('''<body class="bg-brand-canvas dark:bg-brand-darkCanvas text-brand-dark dark:text-white transition-colors duration-300 selection:bg-brand-blue selection:text-white min-h-screen pt-12">''',
    '''<body class="bg-brand-canvas dark:bg-brand-darkCanvas text-brand-dark dark:text-white transition-colors duration-300 selection:bg-brand-blue selection:text-white min-h-screen pt-12">

  <!-- F-05: keyboard skip link -->
  <a href="#main" class="sr-only focus:not-sr-only focus:fixed focus:top-3 focus:right-3 focus:z-[60] focus:px-4 focus:py-2 focus:rounded-full focus:bg-brand-blue focus:text-white focus:text-xs focus:font-bold focus:shadow-lg">پرش به محتوای اصلی</a>''',
    "skip link")

sub('  <!-- Hero Section -->', '  <!-- F-05: main landmark wraps all page content; modals/footer stay outside -->\n  <main id="main">\n\n  <!-- Hero Section -->',
    "<main> open")
sub('  <!-- Footer with Overflow-Safe Flex-Wrap -->', '  </main>\n\n  <!-- Footer with Overflow-Safe Flex-Wrap -->',
    "</main> close")

# ============================================================= F-09 focus ring
sub('''    .poshtiban-scrollbar {
      scrollbar-width: thin;
      scrollbar-color: rgba(140, 140, 145, 0.35) transparent;
    }
  </style>''',
    '''    .poshtiban-scrollbar {
      scrollbar-width: thin;
      scrollbar-color: rgba(140, 140, 145, 0.35) transparent;
    }

    /* --- F-09: یک حلقهٔ فوکوس سراسری برای کاربران کیبورد (کاربر ماوس چیزی نمی‌بیند) ---
       با !important تا بر focus:outline-none های موجود غلبه کند. */
    :is(a, button, input, textarea, select, [role="button"], [tabindex]):focus-visible {
      outline: 2px solid #0071e3 !important;
      outline-offset: 2px !important;
    }
    .dark :is(a, button, input, textarea, select, [role="button"], [tabindex]):focus-visible {
      outline-color: #4da3ff !important;
    }
    /* حلقهٔ فوکوس روی کارت‌های انتخاب خدمات کمی ضخیم‌تر، چون هدف بزرگ‌تری دارند */
    #bookingModal [id^="serviceCard_"]:focus-visible {
      outline-width: 3px !important;
      outline-offset: 3px !important;
    }
  </style>''',
    "global focus-visible ring")

# ========================================================== F-10 contrast ===
sub('''      color: rgba(134, 134, 139, 0.35) !important;
      cursor: not-allowed !important;''',
    '''      color: #75757a !important;            /* F-10: ≈4.6:1 روی کارت سفید (قبلاً 1.47:1) */
      cursor: not-allowed !important;''',
    "calendar disabled colour")

sub('''    .dark .cal-day-cell-off {
      color: rgba(248, 113, 113, 0.5) !important;''',
    '''    .dark .cal-day-cell-off {
      color: rgba(248, 113, 113, 0.92) !important;   /* F-10: خوانا روی پس‌زمینهٔ تیره */''',
    "calendar off colour (dark)")

sub('''      color: rgba(239, 68, 68, 0.5) !important;
      background-color: rgba(0, 0, 0, 0.02);
      text-decoration: line-through;
      text-decoration-color: rgba(239, 68, 68, 0.5);''',
    '''      color: #c0392b !important;           /* F-10: ≈5.4:1 (قبلاً 1.98:1) */
      background-color: rgba(0, 0, 0, 0.02);
      text-decoration: line-through;
      text-decoration-color: rgba(192, 57, 43, 0.55);''',
    "calendar off colour (light)")

# dark disabled (new rule appended next to the dark off one)
sub('''    .dark .cal-day-cell-off {
      color: rgba(248, 113, 113, 0.92) !important;   /* F-10: خوانا روی پس‌زمینهٔ تیره */''',
    '''    .dark .cal-day-cell-disabled {
      color: rgba(174, 174, 178, 0.85) !important;   /* F-10 */
    }
    .dark .cal-day-cell-off {
      color: rgba(248, 113, 113, 0.92) !important;   /* F-10: خوانا روی پس‌زمینهٔ تیره */''',
    "calendar disabled colour (dark)")

# ========================================================== F-06 upload zone =
sub('''        <div id="dropZoneArea" onclick="document.getElementById('aiImageFileInput').click()" class="border-2 border-dashed border-black/10 dark:border-white/10 hover:border-purple-500/50 rounded-2xl p-6 text-center cursor-pointer transition bg-brand-lightGray/50 dark:bg-[#1a1a1c]/50">
          <input type="file" id="aiImageFileInput" accept="image/*" class="hidden" onchange="handleImageSelected(event)">''',
    '''        <!-- F-06/F-07: label واقعی — با کیبورد (Enter/Space) و صفحه‌خوان قابل استفاده است -->
        <label for="aiImageFileInput" id="dropZoneArea" role="button" tabindex="0"
               aria-label="بارگذاری تصویر خطا یا صفحه آبی"
               onkeydown="if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); document.getElementById('aiImageFileInput').click(); }"
               class="block border-2 border-dashed border-black/10 dark:border-white/10 hover:border-purple-500/50 rounded-2xl p-6 text-center cursor-pointer transition bg-brand-lightGray/50 dark:bg-[#1a1a1c]/50">
          <input type="file" id="aiImageFileInput" accept="image/*" tabindex="-1" class="sr-only" onchange="handleImageSelected(event)">''',
    "upload zone → label[role=button]")

# closing tag of the label (the element that used to be the div).
# Note: the delete button already calls event.stopPropagation(), so it will NOT re-open the picker.
sub("""              ✕ حذف و انتخاب عکس دیگر
            </button>
          </div>
        </div>""",
    """              ✕ حذف و انتخاب عکس دیگر
            </button>
          </div>
        </label>""",
    "upload zone closing tag")

# drag & drop support (the copy promised "رها کردن" but nothing was wired)
sub('''    function handleImageSelected(event) {
      const file = event.target.files?.[0];
      if (!file) return;

      const fileNameText = document.getElementById("imageFileNameText");''',
    '''    /* F-06: مسیر مشترک پردازش تصویر — برای انتخاب فایل و رها کردن (drag & drop) */
    function processVisionFile(file) {
      if (!file) return;
      const fileNameText = document.getElementById("imageFileNameText");''',
    "processVisionFile extracted")

sub('''      reader.readAsDataURL(file);
    }

    function resetImageSelection() {''',
    '''      reader.readAsDataURL(file);
    }

    function handleImageSelected(event) {
      const file = event.target.files?.[0];
      if (!file) return;
      processVisionFile(file);
    }

    /* drag & drop روی ناحیهٔ بارگذاری */
    function initDropZone() {
      const zone = document.getElementById("dropZoneArea");
      if (!zone) return;
      const highlight = (on) => zone.classList.toggle("border-purple-500", on);
      ["dragenter", "dragover"].forEach(ev => zone.addEventListener(ev, e => {
        e.preventDefault(); highlight(true);
      }));
      ["dragleave", "dragend"].forEach(ev => zone.addEventListener(ev, () => highlight(false)));
      zone.addEventListener("drop", e => {
        e.preventDefault(); highlight(false);
        const file = e.dataTransfer?.files?.[0];
        if (file) processVisionFile(file);
      });
    }

    function resetImageSelection() {''',
    "handleImageSelected + initDropZone")

# ================================================== F-06 service cards ======
def convert_card(block: str) -> str:
    """Turn a service card div (and its nested divs) into a real button with spans."""
    first_end = block.index(">")
    open_tag = block[:first_end + 1]
    body = block[first_end + 1:]
    open_tag = open_tag.replace('<div id="serviceCard_', '<button type="button" id="serviceCard_', 1)
    open_tag = open_tag.replace('class="booking-service-card cursor-pointer ', 'aria-pressed="false" class="booking-service-card w-full text-right cursor-pointer ', 1)
    body = body.replace("<div", "<span").replace("</div>", "</span>")
    return open_tag + body

for sid in ("ssd", "thermal", "ram", "mobo"):
    start = s.index(f'<div id="serviceCard_{sid}"')
    # find the balanced closing </div> of this card
    depth = 0
    i = start
    end = None
    while i < len(s):
        if s.startswith("<div", i):
            depth += 1
        elif s.startswith("</div>", i):
            depth -= 1
            if depth == 0:
                end = i + len("</div>")
                break
        i += 1
    assert end, sid
    block = s[start:end]
    s = s[:start] + convert_card(block) + s[end:]
    print(f"  ✓ service card {sid} → <button aria-pressed>")

# keep aria-pressed in sync when the selection changes
sub('''        if (isSelected) {
          totalPrice += SERVICES_CATALOG[id].price;''',
    '''        if (card.tagName === "BUTTON") card.setAttribute("aria-pressed", String(isSelected));
        if (isSelected) {
          totalPrice += SERVICES_CATALOG[id].price;''',
    "service card aria-pressed sync")

# ======================================================== F-07 labels ========
sub('<label class="block text-xs font-medium text-brand-gray mb-1">نام و نام‌خانوادگی:</label>',
    '<label for="bookNameInput" class="block text-xs font-medium text-brand-gray mb-1">نام و نام‌خانوادگی:</label>', "label → bookNameInput")
sub('<label class="block text-xs font-medium text-brand-gray mb-1">شماره موبایل جهت پیامک کد پیگیری:</label>',
    '<label for="bookPhoneInput" class="block text-xs font-medium text-brand-gray mb-1">شماره موبایل جهت پیامک کد پیگیری:</label>', "label → bookPhoneInput")
sub('<label class="block text-xs font-medium text-brand-gray mb-1">مدل دستگاه یا شرح ایراد:</label>',
    '<label for="bookModelInput" class="block text-xs font-medium text-brand-gray mb-1">مدل دستگاه یا شرح ایراد:</label>', "label → bookModelInput")
sub('<label class="block text-xs font-medium text-brand-gray mb-1.5">توضیح تکمیلی درباره عکس (اختیاری):</label>',
    '<label for="aiVisionNotes" class="block text-xs font-medium text-brand-gray mb-1.5">توضیح تکمیلی درباره عکس (اختیاری):</label>', "label → aiVisionNotes")
sub('<label class="block text-xs font-semibold text-neutral-800 dark:text-neutral-200 mb-1">کلید Gemini API (اختیاری):</label>',
    '<label for="userCustomApiKeyInput" class="block text-xs font-semibold text-neutral-800 dark:text-neutral-200 mb-1">کلید Gemini API (اختیاری):</label>', "label → userCustomApiKeyInput")

sub('''          <h3 class="text-sm sm:text-base font-bold text-brand-dark dark:text-white">شرح اشکال به زبان ساده:</h3>''',
    '''          <h3 id="aiProblemHeading" class="text-sm sm:text-base font-bold text-brand-dark dark:text-white">شرح اشکال به زبان ساده:</h3>''',
    "diagnosis heading id")
sub('''<textarea id="aiProblemInput" rows="3" placeholder=''',
    '''<textarea id="aiProblemInput" aria-labelledby="aiProblemHeading" rows="3" placeholder=''',
    "aiProblemInput labelled")

sub('''        <input type="text" id="trackingSearchInput" value="PC-1405-912" placeholder="مثال: PC-1405-912"''',
    '''        <input type="text" id="trackingSearchInput" aria-label="کد پیگیری دستگاه" value="PC-1405-912" placeholder="مثال: PC-1405-912"''',
    "trackingSearchInput labelled")

sub('''        <input type="text" id="aiChatDrawerInput" placeholder="سؤال فنی خود را بنویسید..."''',
    '''        <input type="text" id="aiChatDrawerInput" aria-label="متن پیام به مشاور هوشمند" placeholder="سؤال فنی خود را بنویسید..."''',
    "chat input labelled")

# ========================================================= F-08 drawer ======
sub('''    <div id="aiChatHistoryContainer" class="flex-1 overflow-y-auto p-4 sm:p-5 space-y-3.5 text-xs poshtiban-scrollbar">''',
    '''    <div id="aiChatHistoryContainer" role="log" aria-live="polite" aria-atomic="false" aria-label="تاریخچهٔ گفتگو" class="flex-1 overflow-y-auto p-4 sm:p-5 space-y-3.5 text-xs poshtiban-scrollbar">''',
    "chat history aria-live")

sub('''      if (shouldOpen) {
        drawer.classList.remove("hidden");
        lockBodyScroll();
        setTimeout(() => drawer.classList.remove("translate-x-full"), 10);
      } else {''',
    '''      if (shouldOpen) {
        drawer.classList.remove("hidden");
        lockBodyScroll();
        setTimeout(() => {
          drawer.classList.remove("translate-x-full");
          // F-08: فوکوس داخل فیلد پیام تا کاربر کیبورد بتواند فوراً بنویسد
          const input = document.getElementById("aiChatDrawerInput");
          if (input) input.focus();
        }, 320);
      } else {''',
    "drawer autofocus")

sub('''        <button onclick="openAiSettingsModal()" title="تنظیمات کلید هوش مصنوعی" class="w-7 h-7 rounded-full bg-black/5 dark:bg-white/10 flex items-center justify-center text-xs hover:opacity-75 transition">''',
    '''        <button onclick="openAiSettingsModal()" title="تنظیمات کلید هوش مصنوعی" aria-label="تنظیمات کلید هوش مصنوعی" class="w-7 h-7 rounded-full bg-black/5 dark:bg-white/10 flex items-center justify-center text-xs hover:opacity-75 transition">''',
    "settings button aria-label")

# =========================================================== F-13 FAQ =======
faq_buttons = re.findall(r'<button onclick="toggleFaq\(this\)" class="w-full text-right p-6[^"]*">', s)
assert len(faq_buttons) == 6, len(faq_buttons)
for n, btn in enumerate(faq_buttons, start=1):
    s = s.replace(btn,
                  btn.replace('<button onclick="toggleFaq(this)"',
                              f'<button onclick="toggleFaq(this)" aria-expanded="false" aria-controls="faqAnswer{n}"'),
                  1)
    print(f"  ✓ FAQ button {n} → aria-expanded/aria-controls")

answers = re.findall(r'<div class="faq-answer px-6 pt-6 pb-6[^"]*">', s)
assert len(answers) == 6, len(answers)
for n, ans in enumerate(answers, start=1):
    s = s.replace(ans, ans.replace('<div class="faq-answer', f'<div id="faqAnswer{n}" class="faq-answer', 1), 1)
print("  ✓ FAQ answers got ids")

sub('''    function toggleFaq(btn) {
      playHapticSound('click');
      const answer = btn.nextElementSibling;
      const icon = btn.querySelector(".faq-icon");
      if (!answer) return;

      const isHidden = answer.classList.contains("hidden");
      if (isHidden) {
        answer.classList.remove("hidden");
        if (icon) icon.classList.add("rotate-180");
      } else {
        answer.classList.add("hidden");
        if (icon) icon.classList.remove("rotate-180");
      }
    }''',
    '''    /* F-13: آکاردئون پرسش‌های متداول — وضعیت اعلام‌شده به صفحه‌خوان + باز/بستهٔ نرم */
    function toggleFaq(btn) {
      playHapticSound('click');
      const answer = btn.nextElementSibling;
      const icon = btn.querySelector(".faq-icon");
      if (!answer) return;

      const isOpen = btn.getAttribute("aria-expanded") === "true";
      const reduceMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

      const setState = (open) => {
        btn.setAttribute("aria-expanded", String(open));
        if (icon) icon.classList.toggle("rotate-180", open);
      };

      if (!isOpen) {
        answer.classList.remove("hidden");
        if (reduceMotion || typeof answer.animate !== "function") { setState(true); return; }
        answer.style.overflow = "hidden";
        const target = answer.scrollHeight;
        const anim = answer.animate(
          [{ height: "0px" }, { height: target + "px" }],
          { duration: 220, easing: "ease-out" }
        );
        anim.onfinish = () => { answer.style.overflow = ""; answer.style.height = ""; };
        setState(true);
      } else {
        if (reduceMotion || typeof answer.animate !== "function") {
          answer.classList.add("hidden"); setState(false); return;
        }
        answer.style.overflow = "hidden";
        const current = answer.getBoundingClientRect().height;
        const anim = answer.animate(
          [{ height: current + "px" }, { height: "0px" }],
          { duration: 180, easing: "ease-in" }
        );
        anim.onfinish = () => {
          answer.classList.add("hidden");
          answer.style.overflow = ""; answer.style.height = "";
        };
        setState(false);
      }
    }''',
    "toggleFaq rewritten (aria + animation + reduced-motion)")

# init drop zone on load
sub('''      initShopHours();
      renderPresence();''',
    '''      initShopHours();
      renderPresence();
      initDropZone();          // F-06: drag & drop روی ناحیهٔ بارگذاری تصویر''',
    "initDropZone on load")

# marker
sub('    /* ================= پشتیبانی ریموت شبانه‌روزی',
    '    /* PACKAGE-2 (a11y) applied — see tools/patches/patch_package2.py */\n    /* ================= پشتیبانی ریموت شبانه‌روزی',
    "patch marker")

io.open(PATH, "w", encoding="utf-8").write(s)
print(f"\nDone — {len(s)} chars written.")
