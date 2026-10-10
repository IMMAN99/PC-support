#!/usr/bin/env python3
"""
Screenshots for F-16 (emoji → line SVG icons, plan price nowrap).

usage:  python3 tools/shots/shots_f16.py
output: screenshots/states/f16-*.png
"""
import asyncio, os
from playwright.async_api import async_playwright

ROOT = "/home/user"
FILE = f"file://{ROOT}/%D9%BE%DB%8C%D8%B4%E2%80%8C%D9%86%D9%85%D8%A7%DB%8C%D8%B4_%D8%A2%D9%81%D9%84%D8%A7%DB%8C%D9%86.html"
S = os.path.join(ROOT, "screenshots", "states")

TRUST_JS = """() => {
    const b = document.querySelector('a[href^="https://t.me"]');
    if (b) b.closest('section').scrollIntoView({ block: 'center' });
}"""


async def main():
    os.makedirs(S, exist_ok=True)
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={"width": 1440, "height": 900}, reduced_motion="reduce")
        await pg.goto(FILE, wait_until="load")
        await pg.wait_for_timeout(800)

        async def shot(name, wait=500):
            await pg.wait_for_timeout(wait)
            await pg.screenshot(path=f"{S}/{name}.png")
            print("  saved", name)

        await shot("f16-header-light")
        await pg.evaluate("toggleTheme()")
        await shot("f16-header-dark")
        await pg.evaluate("toggleTheme()")

        await pg.evaluate("openBookingModal(); goToBookingStep(2)")
        await pg.evaluate("document.getElementById('calSelectedDateBadge').scrollIntoView({block:'center'})")
        await shot("f16-calendar-shifts")
        await pg.evaluate("closeBookingModal()")

        await pg.evaluate("document.getElementById('aiTabVisionBtn').click()")
        await pg.evaluate("document.getElementById('dropZonePlaceholder').scrollIntoView({block:'center'})")
        await shot("f16-ai-vision-tab")

        # عناصر را مستقیم عکس می‌گیریم تا اسکرول به هدف بخورد
        handle = await pg.evaluate_handle("""() => {
            const b = [...document.querySelectorAll('b')].find(x => x.textContent.includes('عضو اتحادیه فناوران'));
            return b.closest('section').querySelectorAll('div.grid')[0];
        }""")
        await handle.as_element().screenshot(path=f"{S}/f16-trust-badges.png")
        print("  saved f16-trust-badges")
        box = await pg.evaluate("() => { const a=document.querySelector('a[href^=\"https://t.me\"]'); const r=a.getBoundingClientRect(); const p=a.parentElement.getBoundingClientRect(); return {x:Math.max(0,p.x-8), y:Math.max(0,p.y-8), width:p.width+16, height:p.height+16}; }")
        await pg.evaluate("() => { const a=document.querySelector('a[href^=\"https://t.me\"]'); a.parentElement.scrollIntoView({block:'center'}); }")
        await pg.wait_for_timeout(400)
        box = await pg.evaluate("() => { const a=document.querySelector('a[href^=\"https://t.me\"]'); const r=a.parentElement.getBoundingClientRect(); return {x:Math.max(0,r.x-10), y:Math.max(0,r.y-10), width:Math.min(r.width+20, innerWidth), height:r.height+20}; }")
        await pg.screenshot(path=f"{S}/f16-messengers.png", clip=box)
        print("  saved f16-messengers")

        await pg.evaluate("""() => {
            localStorage.clear(); resetCreditDemo(); topUpCredits('p1');
            const t = document.getElementById('toast'); if (t) t.classList.add('hidden');
            openWalletModal();
        }""")
        await shot("f16-wallet-expiry-icon")
        await b.close()

    async with async_playwright() as p:
        b = await p.chromium.launch()
        mp = await b.new_page(viewport={"width": 390, "height": 844}, reduced_motion="reduce", is_mobile=True, has_touch=True)
        await mp.goto(FILE, wait_until="load")
        await mp.wait_for_timeout(700)
        h = await mp.evaluate_handle("() => document.getElementById('plans').querySelectorAll('div.grid')[0]")
        await mp.evaluate("() => document.getElementById('plans').scrollIntoView({block:'start'})")
        await mp.wait_for_timeout(500)
        await h.as_element().screenshot(path=f"{S}/f16-plans-390.png")
        print("  saved f16-plans-390")
        await b.close()
    print("done")


asyncio.run(main())
