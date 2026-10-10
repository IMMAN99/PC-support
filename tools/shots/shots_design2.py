#!/usr/bin/env python3
"""
شواهد بصری DESIGN-STEP2 — گام ۲ جلای طراحی.

خروجی: screenshots/states/d2-*.png
  d2-halo-diag-light   هالهٔ گوشهٔ کارت عیب‌یاب (آبی، پایین‌راست) — تم روشن
  d2-halo-pro-light    هالهٔ گوشهٔ کارت Care Pro (بنفش، بالا‌راست) — تم روشن
  d2-halo-diag-dark    همان کارت عیب‌یاب در تم تیره
  d2-halo-pro-dark     همان کارت Care Pro در تم تیره
  d2-halo-hover        کارت Care Pro در هاور (هاله بازتر — نیازمند حرکتِ روشن)
  d2-bench-0           نوارهای سنجش در لحظهٔ ورود (تقریباً خالی — پر شدن از صفر)
  d2-bench-full        نوارهای سنجش پس از پر شدن کامل
  d2-bench-hdd         پس از کلیک «هارد دیسک» (پهنای نوارها عوض می‌شود — تعامل دست‌نخورده)
  d2-btn-hover         دکمهٔ اصلی هیرو در هاور (بزرگ‌نمایی ۱٫۰۲)
  d2-btn-press         همان دکمه در حال فشردن (۰٫۹۸)
  d2-dot-online        نقطهٔ ردیف «پشتیبانی ریموت» در منوی موبایل — آنلاین (سبز)
  d2-dot-offline       همان نقطه — آفلاین (کهرباییِ ثابت)

نکتهٔ شفافیت: برای ثبتِ پایدارِ «نوار تقریباً خالی» در d2-bench-0، شاتر کند می‌شود
(transition-duration این صفحهٔ عکس‌برداری ۶s می‌شود — فقط در همین روند عکس‌برداری،
نه در سایت). هندسه و منحنی دقیقاً همان است؛ در پایانِ اجرا مقدار scaleX چاپ می‌شود
تا خودِ عدد شاهد باشد. آزمون D-08 در audit.py جای این تصویر را می‌گیرد.

اجرا:  python3 tools/shots/shots_design2.py
"""
import asyncio, os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FILE = "file://" + os.path.join(ROOT, "پیش‌نمایش_آفلاین.html")
OUT = os.path.join(ROOT, "screenshots", "states")

DIAG = "#aiTextDiagnosticCard"
PRO = "#plans .grid > div:nth-child(2)"
BENCH = "#speed-booster .bench-card"
HERO_CTA = '#overview a[href="#ai-diagnostic"]'   # دکمهٔ اصلی هیرو (نه لینک ناوبری هدر)
DRAWER_ROW = '#mobileDrawer a[href="#remote-support"]'


async def main():
    os.makedirs(OUT, exist_ok=True)
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        b = await p.chromium.launch()

        # ---------- A) هاله‌ها — وضعیت پایدار (کاهش حرکت)، تم روشن و تیره ----------
        pg = await b.new_page(viewport={"width": 1440, "height": 900}, reduced_motion="reduce")
        await pg.goto(FILE, wait_until="load")
        await pg.wait_for_timeout(900)

        diag = pg.locator(DIAG)
        await diag.scroll_into_view_if_needed(); await pg.wait_for_timeout(600)
        await diag.screenshot(path=f"{OUT}/d2-halo-diag-light.png")
        print("  saved d2-halo-diag-light.png")

        pro = pg.locator(PRO)
        await pro.scroll_into_view_if_needed(); await pg.wait_for_timeout(800)
        await pro.screenshot(path=f"{OUT}/d2-halo-pro-light.png")
        print("  saved d2-halo-pro-light.png")

        await pg.evaluate("() => { toggleTheme(); }")
        await pg.wait_for_timeout(700)
        await diag.scroll_into_view_if_needed(); await pg.wait_for_timeout(600)
        await diag.screenshot(path=f"{OUT}/d2-halo-diag-dark.png")
        print("  saved d2-halo-diag-dark.png")
        await pro.scroll_into_view_if_needed(); await pg.wait_for_timeout(800)
        await pro.screenshot(path=f"{OUT}/d2-halo-pro-dark.png")
        print("  saved d2-halo-pro-dark.png")
        await pg.close()

        # ---------- B) حرکتِ روشن: هاور هاله، نوارهای سنجش، دکمهٔ اصلی ----------
        mp = await b.new_page(viewport={"width": 1440, "height": 900})
        await mp.goto(FILE, wait_until="load")
        await mp.wait_for_timeout(400)

        # هاله در هاور (قاعده به no-preference + اشاره‌گر دقیق گره خورده)
        p2 = mp.locator(PRO)
        await p2.scroll_into_view_if_needed(); await mp.wait_for_timeout(1300)
        before = await p2.evaluate("el => getComputedStyle(el).backgroundSize")
        await p2.hover(); await mp.wait_for_timeout(700)
        after = await p2.evaluate("el => getComputedStyle(el).backgroundSize")
        await p2.screenshot(path=f"{OUT}/d2-halo-hover.png")
        print(f"  saved d2-halo-hover.png  ·  background-size {before} → {after}")

        # نوارهای سنجش — (۱) لحظهٔ ورود با شاترِ کند؛ (۲) پرِ کامل؛ (۳) پس از کلیک هارد دیسک
        await mp.evaluate("""() => { const st = document.createElement('style');
            st.id = 'shot-slow-shutter';
            st.textContent = 'html.js .bench-card .bench-bar { transition-duration: 6s !important; }';
            document.head.appendChild(st); }""")
        await mp.evaluate("document.getElementById('speed-booster').scrollIntoView({block:'center'})")
        await mp.wait_for_timeout(260)
        s0 = await mp.evaluate("() => new DOMMatrixReadOnly(getComputedStyle(document.getElementById('benchBootBar')).transform).a")
        await mp.locator(BENCH).screenshot(path=f"{OUT}/d2-bench-0.png")
        print(f"  saved d2-bench-0.png  ·  scaleX={s0:.3f} (شاتر کند‌شده برای ثبتِ این لحظه)")

        await mp.reload(wait_until="load"); await mp.wait_for_timeout(400)
        await mp.evaluate("document.getElementById('speed-booster').scrollIntoView({block:'center'})")
        await mp.wait_for_timeout(1800)
        widths = await mp.evaluate("""() => ['benchBootBar','benchAppBar','benchReadBar'].map(id => {
            const b = document.getElementById(id);
            return Math.round(100 * b.getBoundingClientRect().width / b.parentElement.getBoundingClientRect().width); })""")
        s1 = await mp.evaluate("() => new DOMMatrixReadOnly(getComputedStyle(document.getElementById('benchBootBar')).transform).a")
        await mp.locator(BENCH).screenshot(path=f"{OUT}/d2-bench-full.png")
        print(f"  saved d2-bench-full.png  ·  scaleX={s1:.3f} ·  پهنا={widths}٪")

        await mp.click("#benchBtnHdd"); await mp.wait_for_timeout(800)
        widths2 = await mp.evaluate("""() => ['benchBootBar','benchAppBar','benchReadBar'].map(id => {
            const b = document.getElementById(id);
            return Math.round(100 * b.getBoundingClientRect().width / b.parentElement.getBoundingClientRect().width); })""")
        await mp.locator(BENCH).screenshot(path=f"{OUT}/d2-bench-hdd.png")
        print(f"  saved d2-bench-hdd.png  ·  پهنا={widths2}٪")

        # دکمهٔ اصلی هیرو — هاور ۱٫۰۲ و فشردن ۰٫۹۸
        cta = mp.locator(HERO_CTA).first
        await mp.evaluate("window.scrollTo(0, 0)"); await mp.wait_for_timeout(600)
        await cta.hover(); await mp.wait_for_timeout(450)
        hs = await cta.evaluate("el => new DOMMatrixReadOnly(getComputedStyle(el).transform).a")
        await cta.screenshot(path=f"{OUT}/d2-btn-hover.png")
        print(f"  saved d2-btn-hover.png  ·  scale={hs:.3f}")

        await mp.mouse.down(); await mp.wait_for_timeout(400)
        ps = await cta.evaluate("el => new DOMMatrixReadOnly(getComputedStyle(el).transform).a")
        await cta.screenshot(path=f"{OUT}/d2-btn-press.png")
        await mp.mouse.up()
        print(f"  saved d2-btn-press.png  ·  scale={ps:.3f}")
        await mp.close()

        # ---------- C) موبایل: نقطهٔ حضور در منوی کشویی (آنلاین / آفلاین) ----------
        m = await b.new_page(viewport={"width": 390, "height": 844}, reduced_motion="reduce",
                             device_scale_factor=3, is_mobile=True, has_touch=True)
        await m.goto(FILE, wait_until="load")
        await m.wait_for_timeout(800)
        await m.evaluate("() => { REMOTE_SUPPORT.manualOverride = 'online'; renderPresence(); toggleMobileMenu(); }")
        await m.wait_for_timeout(700)
        row = m.locator(DRAWER_ROW).first
        await row.screenshot(path=f"{OUT}/d2-dot-online.png")
        cls_on = await m.evaluate("() => document.getElementById('drawerPresenceDot').className")
        print(f"  saved d2-dot-online.png  ·  {cls_on}")

        await m.evaluate("() => { REMOTE_SUPPORT.manualOverride = 'offline'; renderPresence(); }")
        await m.wait_for_timeout(600)
        await row.screenshot(path=f"{OUT}/d2-dot-offline.png")
        cls_off = await m.evaluate("() => document.getElementById('drawerPresenceDot').className")
        print(f"  saved d2-dot-offline.png  ·  {cls_off}")
        await m.close()

        await b.close()


asyncio.run(main())
