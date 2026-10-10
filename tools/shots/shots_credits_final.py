#!/usr/bin/env python3
"""
Screenshots for the five approved credit decisions:
expiry in the wallet, Care-plan monthly credits, low-balance alert,
workshop-drop phase, and the 48-hour dispute row.

usage:  python3 tools/shots/shots_credits_final.py
output: screenshots/states/r3-15…r3-19*.png
"""
import asyncio, os
from playwright.async_api import async_playwright

ROOT = "/home/user"
FILE = f"file://{ROOT}/%D9%BE%DB%8C%D8%B4%E2%80%8C%D9%86%D9%85%D8%A7%DB%8C%D8%B4_%D8%A2%D9%81%D9%84%D8%A7%DB%8C%D9%86.html"
S = os.path.join(ROOT, "screenshots", "states")


async def main():
    os.makedirs(S, exist_ok=True)
    async with async_playwright() as p:
        b = await p.chromium.launch()
        page = await b.new_page(viewport={"width": 1440, "height": 900}, reduced_motion="reduce")
        await page.goto(FILE, wait_until="load")
        await page.wait_for_timeout(800)

        async def shot(name):
            await page.wait_for_timeout(650)
            await page.screenshot(path=f"{S}/{name}.png")
            print("  saved", name)

        # --- wallet: expiry + Care monthly credits ---
        await page.evaluate("""() => {
            localStorage.clear(); resetCreditDemo(); topUpCredits('p2'); topUpCredits('p1');
            const t = document.getElementById('toast'); if (t) t.classList.add('hidden');
            openWalletModal();
        }""")
        await shot("r3-15-wallet-expiry")

        # --- Care plans: monthly credits ---
        await page.evaluate("""() => {
            closeWalletModal();
            document.getElementById('plans').scrollIntoView({ block: 'center' });
        }""")
        await shot("r3-16-plans-credits")

        # --- session bar: low-balance alert ---
        await page.evaluate("""() => {
            const phone = '09121110055';
            const st = creditState();
            st.grants[phone] = st.grants[phone] || new Date().toISOString();
            st.freeByPhone[phone] = 0; st.balance = 20; creditSave(st);
            openRemoteModal();
            document.getElementById('remoteNameInput').value = 'سمیرا ک.';
            document.getElementById('remotePhoneInput').value = phone;
            document.getElementById('remoteConsentCheck').checked = true;
            handleRemoteSubmit({ preventDefault(){} });
            startSessionFromSuccess();
            window.__creditNowOverride = creditSession.startedAt + 22 * 60000;
            tickChargeSession();
            const t = document.getElementById('toast'); if (t) t.classList.add('hidden');
        }""")
        await shot("r3-17-session-low-balance")

        # --- session bar: workshop drop ---
        await page.evaluate("""() => {
            toggleWorkshopDrop();
            window.__creditNowOverride = creditSession.startedAt + 27 * 60000;
            tickChargeSession();
            const t = document.getElementById('toast'); if (t) t.classList.add('hidden');
        }""")
        await shot("r3-18-session-drop")

        # --- tracking modal: 48h dispute ---
        await page.evaluate("""() => {
            topUpCredits('p1');                    // تا جلسه در آزمون تصویر با اعتبار صفر بسته نشود
            toggleWorkshopDrop();
            window.__creditNowOverride = creditSession.startedAt + 30 * 60000;
            tickChargeSession();
            const s = stopChargeSession('user');
            delete window.__creditNowOverride;
            const t = document.getElementById('toast'); if (t) t.classList.add('hidden');
            openTrackingModalWithCode(s.code);
            toggleDisputeForm();
            document.getElementById('trackDisputeReason').value =
              'اتصال برگشت ولی مشکل صدا هنوز هست و دستگاه ری‌استارت می‌شود.';
        }""")
        await page.evaluate("document.getElementById('trackingResultCard').scrollIntoView({ block: 'center' })")
        await shot("r3-19-dispute")

        await b.close()
    print("done")


asyncio.run(main())
