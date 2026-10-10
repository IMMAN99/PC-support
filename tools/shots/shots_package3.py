"""Package 3 evidence: mobile launcher states, phone-visible header pill, desktop gutter chip."""
import asyncio, os
from playwright.async_api import async_playwright

BUNDLE = ("file:///home/user/"
          "%D9%BE%DB%8C%D8%B4%E2%80%8C%D9%86%D9%85%D8%A7%DB%8C%D8%B4_%D8%A2%D9%81%D9%84%D8%A7%DB%8C%D9%86.html")
OUT = "/home/user/screenshots/states"


def rec_vis():
    return """() => { const el = document.getElementById('aiFloatingLauncherBtn');
        const w = document.getElementById('aiFloatingLauncher');
        const cs = getComputedStyle(w); const a = el.getBoundingClientRect();
        return {reading: w.className.includes('launcher-reading'), opacity: cs.opacity,
                onScreen: a.top < innerHeight && a.bottom > 0}; }"""


async def main():
    os.makedirs(OUT, exist_ok=True)
    async with async_playwright() as p:
        b = await p.chromium.launch()

        # ---------- mobile ----------
        m = await b.new_page(viewport={"width": 390, "height": 844}, reduced_motion="reduce", is_mobile=True, has_touch=True,
                             device_scale_factor=2)
        errs = []
        m.on("pageerror", lambda e: errs.append(str(e)))
        await m.goto(BUNDLE, wait_until="load")
        await m.wait_for_timeout(900)

        await m.screenshot(path=f"{OUT}/p3-01-mobile-top.png")          # header pill + launcher at rest (top)
        print("  top:", await m.evaluate(rec_vis()))

        await m.evaluate("document.querySelector('#plans').scrollIntoView({block:'center'})")
        await m.wait_for_timeout(1400)
        await m.screenshot(path=f"{OUT}/p3-02-mobile-reading.png")      # launcher away while reading
        print("  reading:", await m.evaluate(rec_vis()))

        await m.evaluate("window.scrollBy(0, -420)")                    # scroll up → it returns
        await m.wait_for_timeout(600)
        await m.screenshot(path=f"{OUT}/p3-03-mobile-scroll-up.png")
        print("  scrolled up:", await m.evaluate(rec_vis()))

        await m.evaluate("window.scrollTo(0, document.documentElement.scrollHeight)")
        await m.wait_for_timeout(1500)
        await m.screenshot(path=f"{OUT}/p3-04-mobile-footer.png")       # page end clears the launcher
        print("  page end:", await m.evaluate(rec_vis()))

        hdr = await m.query_selector("header")
        hb = await hdr.bounding_box()
        await m.evaluate("window.scrollTo(0,0)")
        await m.wait_for_timeout(400)
        await m.screenshot(path=f"{OUT}/p3-05-mobile-header.png",
                           clip={"x": 0, "y": 0, "width": 390, "height": 60})
        print("  JS errors (mobile):", errs or "none")
        await m.close()

        # ---------- desktop ----------
        pg = await b.new_page(viewport={"width": 1440, "height": 900}, reduced_motion="reduce", device_scale_factor=2)
        await pg.goto(BUNDLE, wait_until="load")
        await pg.wait_for_timeout(800)
        await pg.evaluate("document.querySelector('#bottleneck').scrollIntoView({block:'center'})")
        await pg.wait_for_timeout(1200)
        await pg.screenshot(path=f"{OUT}/p3-06-desktop-gutter.png",
                            clip={"x": 1040, "y": 620, "width": 400, "height": 280})
        await pg.hover("#aiFloatingLauncherBtn")
        await pg.wait_for_timeout(500)
        await pg.screenshot(path=f"{OUT}/p3-07-desktop-hover.png",
                            clip={"x": 1040, "y": 620, "width": 400, "height": 280})
        await pg.evaluate("window.scrollTo(0,0)")
        await pg.wait_for_timeout(600)
        await pg.screenshot(path=f"{OUT}/p3-08-desktop-hero.png",
                            clip={"x": 0, "y": 0, "width": 1440, "height": 620})
        print("  desktop shots saved")
        await b.close()

asyncio.run(main())
