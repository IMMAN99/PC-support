#!/usr/bin/env python3
"""
شواهد بصری DESIGN-STEP1 — گام ۱ جلای طراحی.

خروجی: screenshots/states/d1-*.png
  d1-hero-light      پرتو محیطی هیرو، تم روشن
  d1-hero-dark       پرتو محیطی هیرو، تم تیره
  d1-seam-dark       درز گرادیانی بالای باند خاکستری (تم تیره)
  d1-seam-light      همان درز در تم روشن
  d1-card-hover      بلندشدن کارت Care در هاور (نیازمند حرکتِ روشن)
  d1-mobile-hero     هیرو در ۳۹۰px

اجرا:  python3 tools/shots/shots_design1.py
"""
import asyncio, os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FILE = "file://" + os.path.join(ROOT, "پیش‌نمایش_آفلاین.html")
OUT = os.path.join(ROOT, "screenshots", "states")


async def main():
    os.makedirs(OUT, exist_ok=True)
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        b = await p.chromium.launch()

        # ---------- A) وضعیت پایدار (کاهش حرکت): پرتو، درزها ----------
        pg = await b.new_page(viewport={"width": 1440, "height": 900}, reduced_motion="reduce")
        await pg.goto(FILE, wait_until="load")
        await pg.wait_for_timeout(900)

        await pg.screenshot(path=f"{OUT}/d1-hero-light.png")
        print("  saved d1-hero-light.png")

        await pg.evaluate("document.getElementById('ai-diagnostic').scrollIntoView({block:'start'})")
        await pg.wait_for_timeout(500)
        await pg.screenshot(path=f"{OUT}/d1-seam-light.png")
        print("  saved d1-seam-light.png")

        await pg.evaluate("() => { window.scrollTo(0, 0); toggleTheme(); }")
        await pg.wait_for_timeout(700)
        await pg.screenshot(path=f"{OUT}/d1-hero-dark.png")
        print("  saved d1-hero-dark.png")

        await pg.evaluate("document.getElementById('ai-diagnostic').scrollIntoView({block:'start'})")
        await pg.wait_for_timeout(500)
        await pg.screenshot(path=f"{OUT}/d1-seam-dark.png")
        print("  saved d1-seam-dark.png")
        await pg.close()

        # ---------- B) حرکت روشن: هاور کارت + میانهٔ ورود نرم ----------
        mp = await b.new_page(viewport={"width": 1440, "height": 900})
        await mp.goto(FILE, wait_until="load")
        await mp.wait_for_timeout(400)

        # هاور: کل ردیف سه‌کارتی عکس می‌شود تا بلندشدنِ کارت وسط در کنار همسایه‌ها دیده شود
        grid = mp.locator("#plans .grid")
        await grid.scroll_into_view_if_needed()
        await mp.wait_for_timeout(1200)            # ورود نرم کامل شود
        await mp.locator("#plans .grid > div").first.hover()
        await mp.wait_for_timeout(500)
        await grid.screenshot(path=f"{OUT}/d1-card-hover.png")
        print("  saved d1-card-hover.png")

        # (ورود نرم با عکس ثابت قابل‌نمایش نیست؛ شاهدش را آزمون D-02/D-02ب می‌دهد:
        #  پنهانِ پیش از اسکرول → نمایانِ یک‌باره با اسکرول، و در «کاهش حرکت» همیشه نمایان.)
        await mp.close()

        # ---------- C) موبایل ----------
        m = await b.new_page(viewport={"width": 390, "height": 844}, reduced_motion="reduce",
                             device_scale_factor=3, is_mobile=True, has_touch=True)
        await m.goto(FILE, wait_until="load")
        await m.wait_for_timeout(900)
        await m.screenshot(path=f"{OUT}/d1-mobile-hero.png")
        print("  saved d1-mobile-hero.png")
        await m.close()

        await b.close()


asyncio.run(main())
