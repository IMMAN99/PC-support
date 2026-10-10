#!/usr/bin/env python3
"""
شواهد بصری DESIGN-STEP3 — «زنده‌شدن» صفحه.

خروجی: screenshots/states/d3-*.png
  d3-hero-light     صحنهٔ هیرو کامل (تصویر + پنل زنده + چیپ‌ها) — تم روشن، در حالت «کاهش حرکت»
  d3-hero-dark      همان صحنه در تم تیره
  d3-clock          پنل ساعت تهران (زنده) و پنل وضعیت — بزرگ‌نمایی
  d3-band-remote    باند تصویری پشتیبانی ریموت
  d3-band-bench     باند ذخیره‌سازی داخل کارت تست سرعت
  d3-band-bottleneck باند تصویری تست گلوگاه
  d3-band-faq       باند باریک کارگاه در پرسش‌های متداول
  d3-count-mid      شمارندهٔ اعداد وسط شمارش (شاهد مقدار میانی)
  d3-parallax       پارالاکس هیرو با ماوس در گوشهٔ صحنه
  d3-mobile-hero    صحنه و باند در ۳۹۰px

اجرا:  bash tools/ops/pw_setup.sh && python3 tools/shots/shots_design3.py
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

        # ---------- A) وضعیت پایدار (کاهش حرکت) ----------
        pg = await b.new_page(viewport={"width": 1440, "height": 950}, reduced_motion="reduce")
        await pg.goto(FILE, wait_until="load")
        await pg.wait_for_timeout(1000)
        # همین قاب در حالت «کاهش حرکت» گرفته می‌شود → شاهد S3-06 هم هست
        await pg.screenshot(path=f"{OUT}/d3-hero-light.png")
        print("  saved d3-hero-light.png")

        await pg.evaluate("() => toggleTheme()")
        await pg.wait_for_timeout(700)
        await pg.screenshot(path=f"{OUT}/d3-hero-dark.png")
        print("  saved d3-hero-dark.png")
        await pg.evaluate("() => toggleTheme()")
        await pg.wait_for_timeout(500)

        # پنل‌های زنده (برش بزرگ‌نما)
        stage = pg.locator("#alHeroStage")
        await stage.scroll_into_view_if_needed(); await pg.wait_for_timeout(500)
        await stage.screenshot(path=f"{OUT}/d3-clock.png")
        print("  saved d3-clock.png")

        for name, sel in (("d3-band-remote", "#remote-support .al-band"),
                          ("d3-band-bench", "#speed-booster .al-band"),
                          ("d3-band-bottleneck", "#bottleneck .al-band"),
                          ("d3-band-faq", "#faq .al-band")):
            loc = pg.locator(sel).first
            await loc.scroll_into_view_if_needed(); await pg.wait_for_timeout(500)
            await loc.screenshot(path=f"{OUT}/{name}.png")
            print(f"  saved {name}.png")
        await pg.close()

        # ---------- B) حرکت روشن: شمارنده + پارالاکس ----------
        mp = await b.new_page(viewport={"width": 1440, "height": 950})
        await mp.goto(FILE, wait_until="load")
        await mp.wait_for_timeout(200)
        await mp.evaluate("document.getElementById('speed-booster').scrollIntoView({block:'center'})")
        card = mp.locator("#speed-booster .bench-card")
        # چند نمونهٔ سریع می‌گیریم و اولین قابی را نگه می‌داریم که عددِ میانی (نه نهایی) را نشان دهد
        mid = ""
        for _ in range(6):
            await mp.wait_for_timeout(120)
            txt = await mp.evaluate("() => document.getElementById('benchBootTime').textContent.trim()")
            if txt not in ("۷ ثانیه", ""):
                await card.screenshot(path=f"{OUT}/d3-count-mid.png")
                mid = txt
                break
        await mp.wait_for_timeout(1500)
        end = await mp.evaluate("() => document.getElementById('benchBootTime').textContent.trim()")
        if not mid:      # قاب میانی به دست نیامد → همان قاب نهایی را ذخیره کن (آزمون S3-04 مرجع است)
            await card.screenshot(path=f"{OUT}/d3-count-mid.png")
        print(f"  saved d3-count-mid.png  ·  میانی «{mid or '—'}» → نهایی «{end}»")

        stage2 = mp.locator("#alHeroStage")
        await stage2.scroll_into_view_if_needed(); await mp.wait_for_timeout(700)
        box = await stage2.bounding_box()
        await mp.mouse.move(box["x"] + box["width"] * .18, box["y"] + box["height"] * .26)
        await mp.wait_for_timeout(350)
        await stage2.screenshot(path=f"{OUT}/d3-parallax.png")
        tr = await mp.evaluate("() => [...document.querySelectorAll('#alHeroStage [data-al-depth]')].map(e => e.style.translate)")
        print(f"  saved d3-parallax.png  ·  translate={tr}")
        await mp.close()

        # ---------- C) موبایل ----------
        m = await b.new_page(viewport={"width": 390, "height": 844}, reduced_motion="reduce",
                             device_scale_factor=3, is_mobile=True, has_touch=True)
        await m.goto(FILE, wait_until="load")
        await m.wait_for_timeout(900)
        await m.screenshot(path=f"{OUT}/d3-mobile-hero.png")
        print("  saved d3-mobile-hero.png")
        await m.close()

        await b.close()


asyncio.run(main())
