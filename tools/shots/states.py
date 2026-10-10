#!/usr/bin/env python3
"""
Capture the interactive states of the offline bundle:
modal wizard steps, tracking, chat drawer, AI settings, diagnosis result,
dark-mode sections and the mobile layout.

usage:  python3 tools/shots/states.py
output: screenshots/states/*.png  +  screenshots/dark/*.png  +  screenshots/mobile/*.png
"""
import asyncio, os
from playwright.async_api import async_playwright

ROOT = "/home/user"
FILE = f"file://{ROOT}/پیش‌نمایش_آفلاین.html"
S = os.path.join(ROOT, "screenshots", "states")
D = os.path.join(ROOT, "screenshots", "dark")
M = os.path.join(ROOT, "screenshots", "mobile")


async def main():
    for d in (S, D, M):
        os.makedirs(d, exist_ok=True)

    async with async_playwright() as p:
        b = await p.chromium.launch()

        # ---------- desktop: modals, drawers, results ----------
        page = await b.new_page(viewport={"width": 1440, "height": 900}, reduced_motion="reduce")
        await page.goto(FILE, wait_until="load")
        await page.wait_for_timeout(800)

        async def shot(path):
            await page.wait_for_timeout(600)
            await page.screenshot(path=path)
            print("  saved", os.path.basename(path))

        await page.evaluate("openBookingModal()")
        await shot(f"{S}/booking-1-services.png")
        await page.evaluate("goToBookingStep(2)"); await shot(f"{S}/booking-2-calendar.png")
        await page.evaluate("goToBookingStep(3)"); await shot(f"{S}/booking-3-details.png")
        await page.evaluate("closeBookingModal()")

        await page.evaluate("openAiSettingsModal()");   await shot(f"{S}/ai-settings.png")
        await page.evaluate("closeAiSettingsModal()")
        await page.evaluate("openTrackingModal()")
        await page.evaluate("setTrackingDemo('PC-1405-728')"); await shot(f"{S}/tracking.png")
        await page.evaluate("closeTrackingModal()")

        await page.evaluate("toggleAiDrawer(true)");    await shot(f"{S}/chat-drawer.png")
        await page.evaluate("handleAiChatSubmit({preventDefault(){}})") ; await shot(f"{S}/chat-answer.png")
        await page.evaluate("toggleAiDrawer(false)")

        await page.evaluate("""() => {
            document.getElementById('aiProblemInput').value =
              'لپ‌تاپم بعد از ۱۰ دقیقه بازی فنش بلند می‌شه و صفحه آبی می‌ده';
            runAiTextDiagnosis(); }""")
        await page.wait_for_timeout(1500)
        await page.evaluate("document.getElementById('diagReportCard').scrollIntoView({block:'center'})")
        await shot(f"{S}/diag-result.png")

        # ---------- dark mode ----------
        await page.evaluate("toggleTheme()")
        for name, sel in [("hero", "#overview"), ("bottleneck", "#bottleneck"), ("plans", "#plans")]:
            await page.evaluate(f"document.querySelector('{sel}').scrollIntoView({{block:'start'}})")
            await shot(f"{D}/{name}.png")

        # ---------- mobile ----------
        m = await b.new_page(viewport={"width": 390, "height": 844}, reduced_motion="reduce", device_scale_factor=3,
                             is_mobile=True, has_touch=True)
        await m.goto(FILE, wait_until="load"); await m.wait_for_timeout(900)
        await m.screenshot(path=f"{M}/01-hero.png"); print("  saved 01-hero.png")
        for name, sel in [("02-ai", "#ai-diagnostic"), ("03-speed", "#speed-booster"),
                          ("04-bottleneck", "#bottleneck"), ("05-plans", "#plans")]:
            await m.evaluate(f"document.querySelector('{sel}').scrollIntoView({{block:'start'}})")
            await m.wait_for_timeout(450)
            await m.screenshot(path=f"{M}/{name}.png"); print(f"  saved {name}.png")
        await m.evaluate("toggleMobileMenu()"); await m.wait_for_timeout(600)
        await m.screenshot(path=f"{M}/06-drawer.png"); print("  saved 06-drawer.png")
        await m.evaluate("toggleMobileMenu()")
        await m.evaluate("openBookingModal()"); await m.wait_for_timeout(700)
        await m.screenshot(path=f"{M}/07-booking.png"); print("  saved 07-booking.png")

        audit = await m.evaluate("""() => ({
            overflow: document.documentElement.scrollWidth > window.innerWidth + 1,
            sw: document.documentElement.scrollWidth, w: window.innerWidth })""")
        print(f"\n  MOBILE overflow: {audit['overflow']} ({audit['sw']} vs {audit['w']})")
        await b.close()

asyncio.run(main())
