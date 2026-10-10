# پشتیبان پی‌سی — workspace

Persian (RTL) single-page demo site for a PC service shop: Tailwind + vanilla JS, no backend, no build step.
The original page is a **single self-contained HTML file**; everything else here exists to build, preview and QA it.

---

## Status — 2026-10-07

**بستهٔ ۱ · درست‌کارکرد** ✅ · **بستهٔ ۲ · دسترس‌پذیری** ✅ · **بستهٔ ۳ · موبایل و RTL** ✅ · **راند ۲ · بازخورد فروشگاه** ✅ · **راند ۳ · تغییرات جدید** ✅ · **سیستم اعتبار (قواعد نسخهٔ ۱ قفل‌شده + پنج تصمیم)** ✅ · **F-16 (آیکون‌ها)** ✅ · **پاک‌سازی ورک‌اسپیس** ✅ · **جلای طراحی — گام ۱ (پرتو محیطی · ورود نرم · بلندشدن کارت · درز گرادیانی)** ✅ · **جلای طراحی — گام ۲ (هالهٔ دو کارت · نوارهای سنجش · قاعدهٔ نقطه · زبان دکمه‌ها)** ✅ · **زنده‌شدن صفحه — گام ۳ (تصاویر جاسازی‌شده · ضربان زنده · پرکردن جاهای خالی)** ✅

وضعیت بررسی خودکار: **`PASS 102 · FAIL 0 · INFO 1`** — هیچ یافتهٔ بازی نمانده (جزئیات در «Known front-end issues» پایین همین سند). شواهد تصویری از ۱۳۰ به **۹۱ عکس** رسید و هر ارجاع تصویری در اسناد با فایل‌های موجود تطبیق داده شد.

### جلای طراحی — گام ۱ · ۲۰۲۶-۱۰-۰۷ (بر پایهٔ `docs/بازبینی_طراحی_سه_نمونه.md`)

از سه نمونهٔ قدیمی فقط «لایهٔ سینمایی» برداشته شد، با نسخهٔ سبک و دسترس‌پذیر خودمان: **D-01** پرتو محیطی هیرو (دو گرادیان نرم، بدون `filter`، بدون انیمیشن دائمی) · **D-02** ورود نرم اسکرولی (fade + ۱۲px، یک‌جهته، پله‌ای، یک‌بار اجرا) · **D-03** بلندشدن کارت‌ها ۴px با ویژگی مستقل `translate` (بدون تداخل با reveal) · **D-05** درز گرادیانی روی باندهای خاکستری (بیشترین اثر در تم تیره).

دو قاعدهٔ نانوشتهٔ پروژه رعایت شد: **صفر درخواست بیرونی** و **`prefers-reduced-motion`** (در حالت کاهش حرکت: بدون کلاس `js` هیچ محتوایی پنهان نمی‌شود). عکس سینمایی/`fixed attachment`/`scroll-scale`/ایموجی طبق سند عمداً کنار گذاشته شدند. پچ‌ها: `patch_design_step1.py` + `patch_design_step1b.py` · بررسی‌ها: `D-01…D-03` در گروه نگهبان‌ها · شواهد: `screenshots/states/d1-*.png` (۶ عکس).

### جلای طراحی — گام ۲ · ۲۰۲۶-۱۰-۰۷ (تأیید کارفرما: «start phase 2»)

**D-04** هالهٔ گوشه روی دقیقاً دو کارت — کارت عیب‌یاب (آبی، پایین‌راست) و کارت Care Pro (بنفش، بالا‌راست)؛ `background-image` رادیال زیر محتوا و در هاور ۱۱۲٪→۱۴۲٪ (بدون پرش). **D-08** نوارهای سنجش از صفر پر می‌شوند (`scaleX` از لبهٔ راست، طبق RTL) و تغییر SSD/SATA/HDD مثل قبل با پهنای نوار کار می‌کند. **D-09** قاعدهٔ نقطهٔ وضعیت تثبیت شد — سبزِ پالس‌دار = آنلاین، کهرباییِ **ثابت** = در صف/بسته؛ شکاف واقعیِ پیدا‌شده بسته شد: نقطهٔ ردیف «پشتیبانی ریموت» در منوی موبایل همیشه سبزِ پالس‌دار بود و به وضعیت حضور گره نخورده بود. **D-10** زبان واحد دکمه‌های اصلی — هاور ۱٫۰۲ و فشردن ۰٫۹۸ با **سلکتور ویژگی** (پس دکمه‌های ساختهٔ JS هم خودکار پوشش می‌گیرند)، فقط دسکتاپِ اشاره‌گر دقیق و حرکت روشن؛ لانچر شناور و دکمهٔ ارسال رزرو استثنا هستند.

در مسیر همین گام یک باگ واقعی پیدا و رفع شد: سلکتور D-10 به‌جای «مرکب» **فرزندی** نوشته شده بود (هر خط جدید در CSS ترکیب‌کنندهٔ فرزند است)، پس قاعده روی `<span>` داخل دکمه می‌نشست نه روی خود دکمه — `patch_design_step2b.py` آن را مرکب کرد و بررسی `D-10` هم بازنویسی شد تا شمارش پوشش را از **سلکتورِ واقعی استایل‌شیت** بگیرد (۲۰ دکمه/لینک، همه از نوع a/button).

پچ‌ها: `patch_design_step2.py` + `patch_design_step2b.py` · بررسی‌ها: `D-04` ×۲ · `D-08` · `D-09` ×۲ · `D-10` · شواهد: `screenshots/states/d2-*.png` (۱۲ عکس).

### زنده‌شدن صفحه — گام ۳ · ۲۰۲۶-۱۰-۰۷ (تأیید کارفرما: تصویر ساخته‌شده، حرکت متوسط، پرکردن جاهای خالی)

بازخورد کارفرما پس از گام‌های ۱ و ۲: «سایت هنوز مرده و خالی است.» ریشه در بازبینی پیدا شد: کل صفحه ۶٬۲۰۰px بود و هیچ تصویری نداشت؛ میان بخش‌ها ~۲۵۰px سفیدی خالی و در حالت سکون هیچ‌چیز زنده نبود. سه تصمیم تأیید‌شده و اجراشده:

قاعدهٔ حاکم: **هیچ آمار، نظر، لوگو یا عدد جعلی ساخته نشد** — هر عدد سایت همان دادهٔ واقعی/تعاملی قبلی است (وضعیت حضور، سنجه‌های شبیه‌ساز، ساعات کارگاه).

**۱) تصویر (پنج تصویر، همه جاسازی‌شده):** خط تولید `tools/ops/make_images.py` تصاویر را به WebP فشرده و `patch_design_step3*.py` آن‌ها را **به‌صورت base64 داخل فایل** می‌گذارد — صفر درخواست بیرونی، همه با `alt`. صحنهٔ بزرگ هیرو (میز کار واقعی) + چهار باند تصویری: پشتیبانی ریموت (جلسهٔ کارشناس)، ذخیره‌سازی (HDD/SATA/NVMe)، تست گلوگاه (رم و پردازنده)، و باند باریک کارگاه در پرسش‌ها. اگر روزی عکس واقعی کارگاه رسید: همان اسکریپت + یک پچ جای‌گذاری، بدون دست‌زدن به ساختار.

**۲) ضربان زنده (حرکت متوسط):** ساعت تهرانِ زنده روی صحنهٔ هیرو، پنل وضعیت **از همان وضعیت واقعی حضور** تغذیه می‌شود (سبزِ پالس‌دار = آنلاین · کهرباییِ ثابت = در صف — دقیقاً هم‌قاعده با D-09)، شمارندهٔ اعداد سنجش (۷ ثانیه از صفر شمرده می‌شود؛ با هر کلیک SSD/SATA/HDD و با هر تغییر انتخاب‌های گلوگاه هم تکرار می‌شود)، تنفس آرام گرادیان هیرو، عناصر فنی شناور (**D-06**) و پارالاکس ملایم ماوس (**D-07** — ≤۱۰px، فقط دسکتاپِ اشاره‌گر دقیق). در `prefers-reduced-motion` همهٔ ضربان‌ها خاموش می‌شوند ولی تصویر و محتوا کامل دیده می‌شوند.

**۳) مسیر آزمون:** ۸ بررسی تازهٔ `S3-01…S3-08` (رمزگشایی واقعی تصویر، زنده‌بودن ساعت، تغذیهٔ پنل از وضعیت واقعی، مقدار میانی شمارنده، جاسازی‌بودن همهٔ تصاویر + `alt`، بی‌ضربان‌بودن در کاهش حرکت، دامنهٔ پارالاکس، و نگهبان «بدون جای‌گذار/تصویر بیرونی»). یک یافتهٔ واقعی هم پیدا شد: جای‌گذار `__HERO__` در پچ ۳A با base64 جایگزین نشده بود (کادر مشکی) → پچ اصلاحی `patch_design_step3a_img.py`. خوانایی RTL باندها هم با آینه‌کردن سایهٔ تصویر اصلاح شد (`patch_design_step3c.py`).

پچ‌ها: `patch_design_step3a.py` + `patch_design_step3a_img.py` + `patch_design_step3b.py` + `patch_design_step3c.py` · بررسی‌ها: `S3-01…S3-08` (چهار مورد `S3-02/03/05/08` در گروه نگهبان) · شواهد: `screenshots/states/d3-*.png` (۱۰ عکس).

### راند ۲ · بازخورد فروشگاه — ۱۳ مهر ۱۴۰۵ / ۲۰۲۶-۱۰-۰۵

دو اسکرین‌شات نشان‌دار شما (هیرو/هدر + مودال ریموت) ۸ تغییر خواسته بود. همه اعمال شد و هر کدام بررسی خودکار خودش را دارد (گروه «راند ۲» در `tools/audit.py`):

| # | بازخورد شما | چه کردیم | بررسی |
|---|---|---|---|
| ۱ | «،» و «.» اضافه در تیتر هیرو | تیتر: «هر ساعت شبانه‌روز کارشناس آنلاین داری» — بدون علائم انتهایی | `R2-01` |
| ۲ | کلمهٔ خالی «آنلاین» در هدر | پیل هدر = **تعداد زنده** («۱ آنلاین» / «در صف»، در xl جملهٔ کامل)؛ چیپ «آنلاین» هیرو حذف شد | `R2-02` |
| ۳ | دو کنترل هم‌نام «پشتیبانی ریموت» | لینک ناوبری بی‌نقطهٔ سبز ماند؛ دکمهٔ آبی هدر شد «درخواست پشتیبانی ریموت» | `R2-03` |
| ۴ | «عیب‌یاب/مشاور هوشمند همه‌جا اول» | AI-اول در ناوبری، دکمه‌های هیرو، هدر، دکمهٔ شناور، فوتر، پرسش‌ها و ترتیب سکشن‌ها (`#ai-diagnostic` قبل از `#remote-support`) | `R2-04` |
| ۵ | خط «هدف پاسخ تا ۱۵ دقیقه» در هیرو | حذف شد؛ همان اطلاعات در پیل هدر و پنل ریموت هست (متن مودال دست‌نخورده) | `R2-02` |
| ۶ | شروع پذیرش حضوری ۱۰:۰۰ (نه ۹:۳۰) | `SHOP_HOURS`، هیرو، مودال رزرو، مودال ریموت، تقویم و JSON-LD؛ اسکن کل صفحه: صفر «۹:۳۰» | `R2-06` |
| ۷ | رنگ/باکس برای خطوط وضعیت هیرو | دو باکس مستقل: کهربایی «پذیرش حضوری در کارگاه ۱۰:۰۰–۱۷:۰۰» و سبز «پاسخ‌گویی ریموت و تلفنی — شبانه‌روزی» | `R2-07` |
| ۸ | منوهای مودال ریموت مثل منوی «تست گلوگاه» | هر ۴ منو همان کامپوننت سفارشی بخش گلوگاه شد (منوی شیشه‌ای، تیک، بستن با بیرون‌کلیک)؛ صفر `<select>` بومی | `R2-08` |

پچ (idempotent): `tools/patches/patch_round2.py` — شواهد: `screenshots/states/r2-0*.png` (دسکتاپ/موبایل، روشن/تاریک، منوی باز)


### راند ۳ · تغییرات جدید — ۱۳ مهر ۱۴۰۵ / ۲۰۲۶-۱۰-۰۵

| # | خواستهٔ شما | چه شد | بررسی |
|---|---|---|---|
| ۱ | همهٔ آیتم‌های هدر بمانند؛ برچسب‌ها اصلاح شوند، «حالت شب» آخر هدر، «Support Request» → «Remote Request» | هیچ آیتمی حذف نشد: «تست سرعت SSD» به ناوبری برگشت و «🌙» روی موبایل هم دوباره دیده می‌شود (منتقل‌شده به **آخرین کنترل هدر**). CTA هدر و آیتم منوی موبایل شد **«درخواست ریموت»**. زیر ۱۲۰۰px سه اکشن (مشاور/پیگیری/رزرو) داخل منوی **«بیشتر ⋯»** می‌مانند تا نوار سرریز نکند؛ ظرف هدر به `max-w-[1400px]` باز شد | `R3-01` + `R2-09` |
| ۲ | حذف همهٔ قیمت‌ها به‌جز طرح‌های Care | کارت‌های خدمات رزرو، جمع برآورد مرحلهٔ ۱ و ۳، کاتالوگ `SERVICES_CATALOG` و پاسخ قیمتی هوش مصنوعی پاک شدند؛ «رایگان» از CTA هیرو برداشته شد. مقدار جای قیمت: «اجرت و قطعات پس از عیب‌یابی و تأیید شما نهایی می‌شود». تنها «تومان»های سایت داخل سکشن طرح‌های Care است | `R3-02` (+ سخت‌گیری در `F-04`) |
| ۳ | سیستم اعتبار (کیف پول) | کیف پول + ۳ بستهٔ شارژ + گردش اعتبار + زمان‌سنجی جلسه؛ **ساعت خوش‌آمد به شمارهٔ موبایل گره خورده است: هر شماره یک بار ۶۰ دقیقهٔ اول رایگان**، بعد ۱ اعتبار برای هر دقیقه. نوار زندهٔ جلسه، چیپ اعتبار در مودال ریموت (همراه با تایپ شماره)، خط اعتبار در ماژول پیگیری. درگاه پرداخت وصل **نیست** (`CREDITS.demoMode = true`) — سند کامل: `docs/credits-design.md` | `R3-07`, `R3-08` |
| ۳٫۲ | پنج تصمیم تأییدشدهٔ اعتبار — **اجرا شد** | **۱) انقضای ۱۲ ماههٔ اعتبار** + نمایش تاریخ انقضای شمسی در کیف پول و سوختن اعتبار منقضی در گردش. **۲) اعتراض ۴۸ ساعته:** ردیف «اعتراض به مصرف این جلسه» در ماژول پیگیری با شرح اجباری و ثبت در گردش. **۳) اعتبار ماهانهٔ طرح‌های Care:** ۳۰۰ / ۹۰۰ / ۳٬۰۰۰ اعتبار («نامحدود» از Pro برداشته شد تا تناقض نباشد). **۴) اعلان کم‌موجودی:** «N دقیقه تا اتمام اعتبار» + دکمهٔ «شارژ سریع» روی نوار جلسه. **۵) قطعی سمت کارگاه:** دکمهٔ کارشناس، وقفه بدون محاسبه، تا ۳ دقیقه خودکار رایگان و بعد هشدار «در انتظار تصمیم کارشناس» | `R3-11 الف…پ`, `R3-12 الف/ب`, `R3-13`, `R3-14`, `R3-15` |
| ۳٫۱ | قواعد نسخهٔ ۱ اعتبار — **قفل‌شده به‌تصویب شما** | **چرخهٔ صریح جلسه:** درخواست → پذیرش کارشناس → شروع → تایمر → کار → پایان → کسر اعتبار → گزارش. **کنترل دست کارشناس:** شروع / توقف موقت / پایان (زمان توقف محاسبه نمی‌شود) و سرور در نسخهٔ نهایی مرجع است. **توقف فقط سه راه دارد:** سقف مصرف جلسه، اعتبار صفر، پایان دستی — **توقف خودکار بر پایهٔ بی‌فعالیتی حذف شد.** **۲ دقیقه مهلت راه‌اندازی از کلیک «شروع جلسه»** و بعد محاسبه خودکار. **سقف مصرف جلسه با تأیید کاربر** (۶۰/۱۲۰ پیش‌فرض/۳۰۰). **بسته‌ها به زبان زمان:** ۶۰=تا ۱ ساعت، ۳۰۰=تا ۵ ساعت، ۹۰۰=تا ۱۵ ساعت. جملهٔ رسمی: «اولین ۶۰ دقیقهٔ اولین جلسهٔ ریموت شما رایگان است» | `R3-09 الف…ت`, `R3-10 الف…ث` |
| ۴ | هوش مصنوعی باهوش‌تر و بدون قیمت | لایهٔ تشخیص پیش از موتور دانش: مترادف‌های عامیانه، **امتیازدهی وزن‌دار** به‌جای اولین تطبیق، **پرسش روشنگر با گزینه‌های آماده** وقتی نشانه کافی نیست، حافظهٔ پاسخ کوتاه («بله»/«۲»)، هشدار ایمنی برای مایعات/دود/جرقه، اشاره به نشانهٔ دوم، و ممنوعیت مطلق اعلام قیمت (موتور دست‌نخورده ماند) | `R3-03`, `R3-04 الف…ج` |
| ۵ | خدمات حضوری عمومی + گزینهٔ «سایر خدمات» | نام تجاری از متن‌ها حذف شد (`Thermal Grizzly`، «ایسوس K513»، «لپ‌تاپ لنوو») و «ارتقای SSD + کلون سکتوری ویندوز» شد «ارتقای حافظهٔ SSD (کلون کامل ویندوز)». گزینهٔ پنجم **«سایر خدمات»** با فیلد توضیح: بدون شرح ثبت نمی‌شود، در خلاصهٔ نوبت و در تیکت ذخیره می‌شود | `R3-05 الف/ب` |
| ۶ | حذف `intakeHoursDot` از باکس کهربایی | نقطهٔ سمت چپ باکس حذف شد؛ متن ساعت پذیرش سر جایش است | `R3-06` |

پچ‌ها (idempotent): `tools/patches/patch_round3.py` (بندهای ۱، ۲، ۴، ۵، ۶) و `tools/patches/patch_credits.py` (بند ۳)
شواهد: `screenshots/states/r3-0*.png` · `hdr3-*.png`

### اصلاح هدر — ۱۳ مهر ۱۴۰۵ (دنبالهٔ راند ۲)

پچ `tools/patches/patch_header.py` (marker `ROUND-2-HEADER`). سنجش با `tools/shots/probe_header.py` نشان داد نوار هدر (که `max-w-6xl` است و فقط ۱۱۰۴px ظرف دارد) از ۱۰۲۴px تا ۱۹۲۰px محتوایش ~۱۳۴۶px بود؛ یعنی «درخواست پشتیبانی ریموت» و «رزرو حضوری» بیرون از صفحه می‌افتادند و روی موبایل هم دکمهٔ منو ۷–۷۷px بیرون می‌زد.

| چه بود | چه شد |
|---|---|
| سرریز ۲۹۰px در عرض‌های ۱۰۲۴–۱۹۲۰px | ناوبری یک ناحیهٔ **flex-1** انعطاف‌پذیر شد و گروه اکشن‌ها shrink-proof؛ همهٔ ردیف‌ها حالا داخل ۱۱۰۴px جا می‌شوند |
| «۱ آنلاین» + تکرار جملهٔ کامل در xl (۲۲۴px) | پیل جمع‌وجور در همهٔ عرض‌ها؛ جملهٔ کامل در `title`/`aria-label` و پنل ریموت |
| سرریز ۷px@۳۹۰ · ۳۷px@۳۶۰ · ۷۷px@۳۲۰ | پدینگ/فاصلهٔ نوار باریک‌تر شد و کلمهٔ برند زیر ۳۸۰px فقط آیکون است |
| ۱۲ آیتم در ۱۱۰۴px (غیرممکن) | ردیف‌بندی: «مشاور هوشمند» ≥۱۲۸۰ · «رزرو حضوری» ≥۱۲۸۰ · تم و «پیگیری» ≥۶۴۰ (روی موبایل در منوی کشویی) · «تست سرعت SSD» از نوار حذف شد (در کارت‌های هیرو، منو و فوتر هست) |

شواهد: `screenshots/states/hdr3-1440.png` · `hdr3-1100-more-open.png` · `hdr-1920.png` (عرض بیشینه) · بررسی خودکار: `R2-09` (سوییپ ۱۶ عرض، از ۳۲۰ تا ۱۹۲۰px)
دو اصلاح جانبی همین گذر: تکرار متن پیل هدر در عرض‌های بزرگ (`xl:hidden`) و سخت‌گیرترشدن بررسی دکمهٔ شناور (بالای صفحه در ۳۹۰ و ۳۶۰px).

### بستهٔ ۳ · موبایل و RTL — ۲۰۲۶-۱۰-۰۵ / ۱۳ مهر ۱۴۰۵

| یافته | چه بود | چه شد |
|---|---|---|
| F-11 | دکمهٔ شناور در ۷ از ۸ موقعیت اسکرول روی متن می‌افتاد («پشتیبانی ریموت ۱ آنلاین» هم به‌هم چسبیده بود) | از **۱۴۲۰px** به بالا ستون گاتر واقعی دارد، پس دکمه همان‌جا می‌ماند و در حالت ثابت به «آیکون + چیپ وضعیت» جمع می‌شود؛ **زیر ۱۴۲۰px وقت خواندن کنار می‌رود** و با اسکرول به بالا/فوکوس کیبورد/بودن در بالای صفحه برمی‌گردد. برچسب و شمارنده جدا شدند (جملهٔ کامل در `aria-label`)، کف فوتر روی موبایل ۶rem جا باز کرد. سنجش: ۰ هم‌پوشانی در ۸ موقعیت، هم وسط اسکرول هم در سکون |
| F-12 | نشان «آنلاین» با `hidden xl:flex` و دکمهٔ عیب‌یاب با `hidden 2xl:flex` — یعنی روی موبایل هیچ‌کدام | نشان وضعیت حالا یک `<button>` همیشه‌روی‌صفحه است («آنلاین / در صف»، جملهٔ کامل در `aria-label`) و با یک ضربه فرم درخواست ریموت را باز می‌کند؛ روی xl متن کامل هم می‌آید |
| F-15 | فاصلهٔ حرفی منفی روی متن فارسی (تیتر −۱.۸px، لوگو، عدد ۳۰٪، ۱۱ کیکر با `tracking-wider`) | همه حذف شد؛ سنجش مرورگری: هیچ عنصر فارسی‌زبان فاصلهٔ حرفی غیرعادی ندارد |
| **F-17** | **یافتهٔ تازهٔ همین بسته:** `font-mono` روی ۲۱ عنصر (قیمت‌ها) اتصال حروف فارسی را می‌شکست چون فونت مونو گلیف فارسی ندارد | قاعدهٔ سراسری: `.font-mono` فونت فارسی + `tabular-nums` می‌گیرد — ارقام هم‌عرض می‌مانند، حروف درست می‌چسبند |

پچ (idempotent): `tools/patches/patch_package3.py` · شواهد: `screenshots/states/p3-01…p3-09` · سنجش حالت سکون: `python3 tools/measure_launcher_idle.py`
درس فنی بستهٔ ۳: صفحه `scroll-smooth` دارد، پس اسکرول‌های برنامه‌ای ~۷۰۰ms انیمیت می‌شوند؛ هر سنجش «وسط اسکرول» باید یا دو نمونه بگیرد یا تا سکون صبر کند. (`tools/measure_launcher_idle.py`)

### بستهٔ ۲ · دسترس‌پذیری — ۲۰۲۶-۱۰-۰۵ / ۱۳ مهر ۱۴۰۵

| یافته | چه بود | چه شد |
|---|---|---|
| F-05 | پرش به محتوا نداشت | `<main id="main">` دور کل محتوا + لینک «پرش به محتوای اصلی» که فقط با Tab ظاهر می‌شود (بدون آنکه چیدمان را جابه‌جا کند) |
| F-06 | چهار کارت انتخاب خدمات و ناحیهٔ بارگذاری تصویر با `div[onclick]` کار می‌کردند (نه با کیبورد) | کارت‌ها `<button type="button" aria-pressed>` واقعی شدند (Enter/Space)؛ ناحیهٔ بارگذاری `<label for="aiImageFileInput" role="button" tabindex="0">` و در ضمن **drag & drop واقعاً وصل شد** (متنی که وعده می‌داد، قبلاً کدی نداشت) |
| F-07 | ۹ کنترل بدون برچسب | همه برچسب گرفتند (`for=`/`aria-labelledby`/`aria-label`) — ۵ مورد فقط `for=` کم داشتند |
| F-08 | دراور چت فوکوس را جابه‌جا نمی‌کرد، تاریخچه اعلام نمی‌شد، دکمهٔ ⚙️ بی‌نام بود | فوکوس خودکار روی فیلد ورودی (۳۲۰ms)، تاریخچه `role="log" aria-live="polite"`، `aria-label` برای تنظیمات |
| F-09 | هیچ حالت فوکوسی دیده نمی‌شد | قاعدهٔ سراسری `:focus-visible` (نوار آبی، `!important` + نسخهٔ تم تیره) — فقط برای کیبورد، کاربر ماوس چیزی نمی‌بیند |
| F-10 | کنتراست روزهای غیرفعال/تعطیل تقویم **۱.۴۷:۱ و ۱.۹۸:۱** | رسید به **۴.۵۸:۱ و ۵.۴۴:۱** (ترکیب‌شده روی پس‌زمینهٔ واقعی) + رنگ اختصاصی تم تیره |
| F-13 | آکاردئون FAQ بدون وضعیت و بدون انیمیشن | `aria-expanded`/`aria-controls` + باز/بسته شدن نرم ارتفاع، با احترام به `prefers-reduced-motion` |

پچ (idempotent، برای سابقه): `tools/patches/patch_package2.py` — شاهد: ۱۲ بررسی خودکار بستهٔ ۲ در `tools/audit.py` (فوکوس، لیبل‌ها، کنتراست، aria) که هر بار روی همین بیلد اجرا می‌شوند
بررسی‌های تازهٔ اضافه‌شده به audit برای این بسته: کیبورد روی کارت‌ها (Enter → `aria-pressed`)، نقش/`for` ناحیهٔ بارگذاری، و آکاردئون FAQ (۶ مورد).

---

**بستهٔ ۱ · درست‌کارکرد — انجام شد** ✅  (`python3 tools/audit.py` → بستهٔ ۱: all clear)

| یافته | چه بود | چه شد |
|---|---|---|
| F-01 | عیب‌یاب «صفحه آبی» را «نفوذ مایعات» تشخیص می‌داد (زیررشتهٔ «آب» داخل «آبی») | تطبیق روی مرز کلمه (`rxL`) + ترتیب اولویت: BSOD/کرش → مایعات → سوختگی → حرارت → دیسک → برق. ۹ سناریو تست شد، همه درست |
| F-03 | سه روایت متناقض از ساعت کاری | منبع حقیقت واحد `SHOP_HOURS` (پذیرش تا ۱۷:۰۰ · پشتیبانی تا ۲۰:۳۰ · شنبه–چهارشنبه). نشان هدر سه‌حالته شد؛ با ساعت شبیه‌سازی‌شدهٔ تهران تست می‌شود |
| F-04 | ارقام لاتین در شمارنده‌های رزرو + دو نوع جداکنندهٔ هزارگان | همهٔ شمارنده‌ها با `toLocaleString('fa-IR')`؛ جداکنندهٔ یکدست `٬`؛ حالت «بدون خدمت» برای صفر |
| F-14 | «شیفت عصر»، «۲ نوبت پشتیبانی» | «بعدازظهر»، «۲ جلسه پشتیبانی ریموت در ماه» |

Evidence: `screenshots/evidence/after-F01-bsod-report.png` · `after-F04-persian-digits.png`
Patch script (idempotent, for the record): `tools/patches/patch_package1.py`

**Progression: Package 1 `PASS 8 · FAIL 11` → Package 2 `PASS 30 · FAIL 2` → Package 3 `PASS 36 · FAIL 0` → Round 2 `PASS 43 · FAIL 0` → header fix `PASS 44 · FAIL 0` → Round 3 `PASS 61 · FAIL 0` → phone-scoped credits `PASS 65 · FAIL 0` → frozen credit rules v1 `PASS 72 · FAIL 0` → five approved credit decisions `PASS 80 · FAIL 0` → F-16 icons `PASS 83 · FAIL 0` → design step 1 `PASS 88 · FAIL 0` → design step 2 `PASS 94 · FAIL 0` → design step 3 (زنده‌شدن) `PASS 102 · FAIL 0`.**
Regression guards now cover: F-02 (calendar order — the retracted finding), F-01 edge cases, F-03 clock simulation.
F-11 note: a 390px column has no gutter, so *no* floating element can avoid text rows geometrically — the shipped guarantee is "out of the way while scrolling, and only back when the visitor scrolls up / is at the top / focuses it", plus a footer that always clears it. Round 2 added a top-of-page probe at 390 **and** 360 px: the launcher may sit over decorative chrome there, but never over reading text (h1–h4, p, li, b, strong, code). The probes now check both mid-scroll and idle, and they only count elements that are actually perceptible (opacity/visibility aware).

**قاعدهٔ کاری:** پس از هر تغییر در `پشتیبان_رایانه.html` ← `python3 tools/ops/assemble_offline.py` (تست پوشش CSS) ← `python3 tools/audit.py` (گزارش PASS/FAIL).

---

## Layout

| Path | What it is | Edit it? |
|---|---|---|
| **`پشتیبان_رایانه.html`** | **Source of truth.** The live page (CDN Tailwind + Google Fonts). All front-end work happens here. | ✅ yes |
| `پیش‌نمایش_آفلاین.html` | Generated single-file bundle: Tailwind CSS + 6 Vazirmatn weights inlined, zero network requests. This is what the preview server serves. | ❌ never — regenerated |
| `tools/ops/assemble_offline.py` | Build script: source → offline bundle. Verifies every Tailwind class has a CSS rule and fails loudly if not. | ✅ yes |
| `tools/ops/preview_server.py` | Tiny static server on **:8899**; `/` maps to the offline bundle so the sandboxed no-network preview iframe renders the site fully. | ✅ yes |
| `run-preview.sh` | **لانچر یک‌خطی پیش‌نمایش:** `bash run-preview.sh` — اگر سرور از قبل روشن باشد همان را نشان می‌دهد، وگرنه بالا می‌آورد. | ✅ yes |
| `assets/vazirmatn-inlined.css` | Build input: Vazirmatn 400–900 as base64 woff2 (~271 KB). | ⚙️ rarely |
| `assets/tailwind-frozen.css` | Build input: complete frozen Tailwind 3.4.17 build for this page (+ the gap-fill patch at the tail of the file, marked with a comment). | ⚙️ see “Rebuilding the CSS” |
| `docs/بازبینی_رابط_کاربری.html` | **UI review board** — 16 findings + a Round-2 panel (8 shop-feedback rows), severity filters, progress checkboxes. | 📋 read |
| `docs/بازبینی_پروژه.md` | Pipeline / architecture review (build scripts, styling layer, product gaps). | 📋 read |
| `tools/audit.py` | **Regression audit** — renders the bundle and prints PASS/FAIL for every review finding. Run after each change. | ✅ yes |
| `tools/README.md` | **فهرست همهٔ ابزارها** و دستورهای روزمره — نقطهٔ شروع کار با `tools/`. | 📋 read |
| `tools/shots/shots.py` | Section screenshots + layout audit → `screenshots/<tag>/`. | ✅ yes |
| `tools/shots/states.py` | مودال‌ها، دراور، حالت شب و موبایل → `screenshots/{states,dark,mobile}/` (پوشه‌های `dark/` و `mobile/` در صورت نیاز خودشان ساخته می‌شوند). | ✅ yes |
| `tools/check_review.py` | Verifies the review board still renders (filters, no JS errors). | ✅ yes |
| `tools/shots/shots_package3.py` | Mobile + desktop evidence for Package 3 (launcher states, header pill, gutter chip). | ✅ yes |
| `tools/measure_launcher_idle.py` | Measures launcher↔text overlap **at rest** (waits out the smooth-scroll + reveal). | ✅ yes |
| `tools/patches/patch_round2.py` | Round-2 patch (H1 punctuation, header count, «پشتیبانی ریموت» naming, AI-first order, presence line, 10:00 intake, boxed hero status, custom modal dropdowns) — applied, idempotent. | 🗄️ record |
| `tools/patches/patch_header.py` | Header patch (width budget, flexible nav, compact status pill, tiered visibility) — applied, idempotent. | 🗄️ record |
| `tools/patches/patch_round3.py` | Round-3 patch (header restore + rename, prices removed, AI triage layer, generic services + «سایر خدمات», intakeHoursDot) — applied, idempotent. | 🗄️ record |
| `tools/patches/patch_credits.py` | Credit wallet + per-minute metering — applied, idempotent. | 🗄️ record |
| `tools/patches/patch_credits_phone.py` | Welcome hour tied to the phone number (one 60-min grant per number) — applied, idempotent. | 🗄️ record |
| `tools/patches/patch_credits_rules.py` | قواعد نسخهٔ ۱ اعتبار (حذف توقف بی‌فعالیتی، مهلت ۲ دقیقه‌ای، سقف جلسه، توقف موقت، برچسب زمانی بسته‌ها) — اعمال‌شده. | 🗄️ record |
| `tools/patches/patch_credits_final.py` | پنج تصمیم اعتبار (انقضای ۱۲ ماه، اعتراض ۴۸ ساعته، اعتبار ماهانهٔ Care، اعلان کم‌موجودی، قطعی سمت کارگاه) — اعمال‌شده. | 🗄️ record |
| `tools/patches/patch_f16.py` | آیکون‌های خطی SVG به‌جای ایموجی + الآن‌رپ قیمت طرح‌ها — اعمال‌شده. | 🗄️ record |
| `tools/patches/README.md` | **جدول زمانی همهٔ پچ‌ها** با نشانگر و ترتیب اجرا — برای بازسازی از صفر. | 📋 read |
| `docs/credits-design.md` | Credit-system design: decisions to make, edge cases, backend data model, roadmap, extra ideas. | 📋 read |
| `tools/shots/probe_header.py` | Measures the header bar at any list of widths: container overflow + which items stick out. Run after touching the header. | ✅ yes |
| `tools/shots/shots_header.py` | Header crops at every breakpoint tier → `screenshots/states/hdr-<width>.png`. | ✅ yes |
| `tools/ops/tailwind/` | Reproducible generator for `assets/tailwind-frozen.css` (config + in.css + instructions). `npm i -D tailwindcss@3.4.17` inside it, then follow its README. | ⚙️ build |
| `tools/verify_package2.py` | Behavioural a11y checks an aria-only audit can't see: real image → preview → in-`label` delete button, drag & drop, FAQ accordion animation, focus ring on keyboard only. | ✅ yes |
| `screenshots/` | **شواهد تصویری — ۹۱ عکس.** `states/` = شواهد راند ۲ و ۳، اعتبار، F-16، ریموت‌محوری، جلای طراحی (`d1-*` و `d2-*`) و «زنده‌شدن» (`d3-*`: صحنهٔ هیرو روشن/تیره، ساعت زنده، چهار باند تصویری، قاب میانی شمارنده، پارالاکس، موبایل) + گالری جریان‌های اصلی سایت (`booking-1…3`، `ai-settings`، `tracking`، `chat-*`، `diag-result`)؛ `desktop/` و `evidence/` = وضعیت اولیهٔ پروژه. پوشه‌های `dark/` و `mobile/` عمداً نگه داشته **نشده‌اند** — خروجی `tools/shots/states.py` هستند و با یک اجرا برمی‌گردند. | 📷 reference |
| `uploads/` | The four files exactly as received. **Untouched archive — do not edit.** | 🔒 no |

## Remote-first repositioning — 2026-10-05 (PM)

The site's story changed from «کارگاه سخت‌افزار» to «پشتیبانی ریموت شبانه‌روزی». Implemented in `tools/patches/patch_remote_first.py` (idempotent):

* **New section `#remote-support`** right after the hero: live technician panel, 3-step how-it-works, «از راه دور حل می‌شود» vs «مسیر کارگاه», security/tools strip.
* **Live presence engine `REMOTE_SUPPORT`** (3 rotating shifts covering all 24h / 7 days — the site says «شبانه‌روزی», never «۲۴/۷») + `renderPresence()` driving header badge, hero chip, hero status strip, remote section, floating launcher, chat drawer and the request modal — all from one source, refreshed every 60 s. `manualOverride` lets reception lock «online/offline» manually. **Online is never faked**: no shift → every indicator switches to «درخواست‌ها در صف».
* **Real remote request form** (`#remoteModal` rebuilt): 8 fields, Persian/Arabic digit normalisation, consent checkbox, code `RM-1405-xxx`, ticket saved into the existing `poshtiban_tickets` store, success view with «پیگیری این درخواست» → opens the existing tracking modal.
* **In-person intake** stays the hardware escalation path (Sat–Wed, now **10:00**–17:00 after Round 2) — calendar, copy and JSON-LD store hours all match.
* **Hero / nav / header CTAs / mobile drawer / footer / Care plans / FAQ (2 new items) / meta / JSON-LD (Service node for the all-day remote desk)** all aligned.

**One switch left to make requests actually reach a human (no backend needed):** fill `SITE_CONTACT = { whatsapp: '98912…', telegram: '…' }` in the page's script — the success view then shows a messenger hand-off button carrying the full request summary.

Audit (snapshot of that step): new group «ریموت‌محوری» — 8 checks (all-day coverage, six clock probes, honesty check with `manualOverride='offline'`, form completeness, ticket persistence, invalid-phone rejection, tracking integration, remote-first narrative). Totals at that moment: **PASS 16 · FAIL 11** (remaining then = Package 2 a11y + Package 3 mobile; see the Status block for the current totals).

---

## Everyday commands

```bash
# rebuild the offline bundle (always run after editing پشتیبان_رایانه.html)
python3 tools/ops/assemble_offline.py

# live preview  →  port 8899   (یا ساده‌تر، از ریشه: bash run-preview.sh)
python3 tools/ops/preview_server.py

# regression check (content, a11y, mobile, contrast, focus …)  →  PASS/FAIL report
python3 tools/audit.py

# accessibility behaviour (bundle must be rebuilt first)  →  ALL CHECKS PASS
python3 tools/verify_package2.py

# fresh screenshots
python3 tools/shots/shots.py --tag desktop          # light, 1440×900
python3 tools/shots/shots.py --tag desktop-dark --dark
python3 tools/shots/states.py                       # modals + mobile + dark
python3 tools/shots/shots_credits_final.py          # انقضا، اعتراض، کم‌موجودی، قطعی سمت کارگاه
python3 tools/shots/shots_design1.py                 # شواهد جلای گام ۱ (پرتو، درز، هاور، موبایل)
python3 tools/shots/shots_design2.py                 # شواهد جلای گام ۲ (هاله، نوارهای سنجش، دکمه‌ها، نقطهٔ حضور)
python3 tools/ops/make_images.py                     # فشرده‌سازی تصاویر (PNG خام → WebP) پیش از پچ‌های تصویر
python3 tools/shots/shots_design3.py                 # شواهد «زنده‌شدن» (صحنه، باندها، ساعت، شمارنده، پارالاکس)
python3 tools/shots/shots_f16.py                    # آیکون‌های SVG و الآن‌رپ قیمت طرح‌ها
```

First-time setup in a new sandbox (the browser download is not part of the workspace snapshot):

```bash
pip install playwright && python3 -m playwright install --with-deps chromium
```

## Rebuilding the frozen Tailwind CSS

هر وقت در `پشتیبان_رایانه.html` **کلاس تازه‌ای** اضافه شد، CSS منجمد باید بازسازی شود — وگرنه
`tools/ops/assemble_offline.py` با خطا بیرون می‌آید و فهرست کلاس‌های بی‌قاعده را می‌دهد.
کیت کامل (کانفیگ + `in.css` + فهرست توکن‌ها + اسکریپت استخراج) داخل ریپو است:

```bash
cd tools/ops/tailwind
npm i -D tailwindcss@3.4.17            # فقط بار اول در هر سندباکس
# توکن‌ها را از صفحه جمع کن (اسکریپت آماده در README همین پوشه)، بعد:
node node_modules/.bin/tailwindcss -c tailwind.config.js -i in.css -o out.css --minify
cp out.css /home/user/assets/tailwind-frozen.css
python3 /home/user/tools/ops/assemble_offline.py     # تست پوشش CSS
```

جزئیات: **`tools/ops/tailwind/README.md`**

---

## Cleanup log — 2026-10-05

Reorganised from a flat root + hidden `.qa/` scratch folder into the structure above.
Everything removed was **superseded, duplicated or regenerable**; nothing unique was lost, and the received originals are still in `uploads/`.

**Removed**

| Removed | Why |
|---|---|
| `assemble_offline_patched.py` | superseded — the CSS patch is now canonical, one build script is enough |
| `پیش‌نمایش_آفلاین_اصلاح‌شده.html` | superseded proposal build (the patched CSS is now in the main bundle) |
| `.qa/uploaded-offline-reference.html` | byte-identical duplicate of `uploads/Offline_Preview.html` |
| `.qa/tailwind-frozen-updated.ORIGINAL.css` | pre-patch copy — original is preserved in `uploads/` |
| `.qa/gap-fill.css` | merged into `assets/tailwind-frozen.css` (marked section at the end) |
| `.qa/tailwind-frozen-v2.css` | alternative full rebuild — regenerable with the commands above |
| `.qa/audit_dom.py`, `audit2.py`, `audit3.py`, `audit4.py` | four one-off probes merged into `tools/audit.py` |
| `screenshots/sheet-*.jpg`, `screenshots/review-*.png`, 4 redundant crops | my own working montages/scratch, duplicated by the individual shots (تاریخی — این فایل‌ها دیگر وجود ندارند) |
| `.sudo_as_admin_successful` | sudo marker file |

**Renamed / moved**

`پشتیبان_رایانه.html` stays at root (source) · `.qa/fonts_inlined.css` → `assets/vazirmatn-inlined.css` ·
`.qa/tailwind-frozen-updated.css` → `assets/tailwind-frozen.css` · audits/tools → `tools/` · reviews → `docs/` ·
screenshots sorted into per-context folders.

**Status of the build after cleanup:** `tools/ops/assemble_offline.py` re-run — bundle regenerated, CSS coverage check passed
(every class used by the page has a rule), preview server serving the patched build.

## Cleanup log — 2026-10-06

**ساختار تازه** (ریشه تمیز شد؛ دارایی‌ها و ابزارها دسته‌بندی شدند):

```
/home/user
├── پشتیبان_رایانه.html        منبع اصلی — همهٔ ویرایش‌ها این‌جا
├── پیش‌نمایش_آفلاین.html       بیلد تک‌فایلی (ساخته‌شده — دست نزنید)
├── README.md                   همین سند: وضعیت، نقشه، دستورها، سابقهٔ پاک‌سازی
├── docs/                       سند طراحی اعتبار + تختهٔ بازبینی + بازبینی اولیهٔ پروژه
├── assets/                     ورودی‌های بیلد: CSS منجمد Tailwind + فونت وزیرمتن
├── screenshots/                شواهد تصویری (۹۱ عکس)
├── tools/                      ابزارها → tools/README.md
│   ├── audit.py · verify_package2.py · check_review.py · measure_launcher_idle.py
│   ├── ops/                    ساخت و اجرا (assemble_offline.py، preview_server.py، کیت Tailwind)
│   ├── shots/                  ۸ اسکریپت عکس‌برداری و سنجش
│   └── patches/                ۲۰ پچ اجراشده (فقط سابقه) + README جدول زمانی
└── uploads/                    فایل‌های اولیهٔ شما — دست‌نخورده
```

| جابه‌جا شد | از | به |
|---|---|---|
| اسکریپت‌های ساخت و سرور | ریشهٔ ورک‌اسپیس | `tools/ops/` (مسیر ریشه از محل فایل حل می‌شود، پس از هر جایی اجرا می‌شوند) |
| کیت Tailwind | `tools/tailwind/` | `tools/ops/tailwind/` |
| اسکریپت‌های عکس‌برداری و سنجش | `tools/` (کنار audit) | `tools/shots/` |
| ۲۰ پچ یک‌بارمصرف + ابزار کاوش | `tools/patch_*.py` | `tools/patches/` + README با جدول زمانی |

| حذف شد | چرا |
|---|---|
| **۶۷ عکس** تکراری/قدیمی (از ۱۳۰ به ۶۳) | هر عکس مانده یا در سندی ارجاع دارد، یا شاهد یک تصمیم است، یا یکی از جریان‌های اصلی سایت را نشان می‌دهد؛ بقیه نسخهٔ قدیمیِ همان نماها بودند که با یک دستور بازساخته می‌شوند (~۹ مگابایت آزاد شد) |
| `screenshots/dark/` و `screenshots/mobile/` (پوشهٔ کامل) | خروجی `tools/shots/states.py` — با یک اجرا برمی‌گردند |
| پوشهٔ `screenshots/evidence/crop-*.png` (۸ برش) | برش‌های لحظه‌ای اندازه‌گیری F-15/F-17 — حذف شدند؛ عدد و نتیجه‌شان در تختهٔ بازبینی مانده |
| `tools/ops/tailwind/out.css` | خروجی خام ژنراتور؛ نسخهٔ رسمی `assets/tailwind-frozen.css` است |
| `.sudo_as_admin_successful` | فایل نشانگر sudo (۰ بایت) |

**بازبینی پس از پاک‌سازی:** ارجاع‌های تصویریِ همهٔ اسناد با فایل‌های موجود تطبیق داده شد (صفر ارجاع شکسته) و
پس از جابه‌جایی‌ها همهٔ زنجیره دوباره اجرا شد: `tools/ops/assemble_offline.py` ✓ (پوشش CSS) ·
`tools/audit.py` → **PASS 102 · FAIL 0** · `tools/verify_package2.py` → ALL CHECKS PASS · `tools/check_review.py` → صفر منبع بیرونی، صفر خطای JS · پیش‌نمایش :8899 → HTTP 200.

---

## Known front-end issues

**هیچ یافتهٔ بازی نمانده.** هر ۱۷ یافتهٔ اولین بازبینی (`F-01`…`F-17`) بسته شده‌اند — به‌جز `F-02` که خودم پس گرفتم
(مشکل، واقعی نبود). تختهٔ بازبینی (`docs/بازبینی_رابط_کاربری.html`) وضعیت کامل با فیلتر شدت را نشان می‌دهد.

`python3 tools/audit.py` → **`PASS 102 · FAIL 0 · INFO 1`** (۱۰۲ بررسی در گروه‌های بستهٔ ۱، بستهٔ ۲، بستهٔ ۳، ریموت‌محوری، راند ۲، راند ۳ و نگهبان‌ها).

**دو ورودی که فقط شما می‌توانید بدهید (کار را متوقف نکرده‌اند):**

* **`REMOTE_04` — تحویل درخواست به پیام‌رسان.** فرم ریموت کد `RM-…` می‌سازد و تیکت را ذخیره می‌کند؛ دکمهٔ واتساپ/تلگرام در نمای موفقیت فقط وقتی ظاهر می‌شود که `SITE_CONTACT` مقدار بگیرد. **منتظر آی‌دی/شمارهٔ شما.**
* **جدول واقعی شیفت‌ها.** چرخش فعلی `REMOTE_SUPPORT` جایگزین است (شب ۰۰–۰۹ / روز ۰۸–۱۷ / عصر ۱۶–۲۴، هدف پاسخ ۱۵ دقیقه) و همهٔ نشانگرهای «آنلاین» از همین یک منبع تغذیه می‌شوند. با جدول واقعی شما، فقط همان آرایه عوض می‌شود.

**واژگان:** «شبانه‌روزی» به‌جای «۲۴/۷» در متن، متا، JSON-LD، طرح‌های Care و پرسش‌ها — و `LANG-01` در `tools/audit.py` جلوی برگشتنش را می‌گیرد (خط واقعی «تست پایداری ۲۴ ساعته» مستثناست).

**کارهای بک‌اند که از سمت فرانت آماده‌اند:** OTP برای تأیید شمارهٔ ساعت خوش‌آمد · درگاه پرداخت (فعلاً `CREDITS.demoMode = true`) · واریز خودکار اعتبار ماهانهٔ طرح‌های Care · پنل ادمین برای تأیید اعتراض ۴۸ ساعته و صفرکردن مصرف. مدل دادهٔ پیشنهادی در `docs/credits-design.md` بند ۵.

---
