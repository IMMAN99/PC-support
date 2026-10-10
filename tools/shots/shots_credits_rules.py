#!/usr/bin/env python3
"""
Screenshot the frozen v1 credit rules UI:
cap chooser, time-labelled packs, session bar phases (grace / billing / paused).

usage:  python3 tools/shots/shots_credits_rules.py
output: screenshots/states/r3-10…r3-14*.png
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
        await page.wait_for_timeout(900)

        async def shot(name):
            await page.wait_for_timeout(700)
            await page.screenshot(path=f"{S}/{name}.png")
            print("  saved", name)

        # reset + top up so the wallet has movement
        await page.evaluate("""() => {
            localStorage.removeItem('poshtiban_credits');
            localStorage.removeItem('poshtiban_last_phone');
            resetCreditDemo();
            topUpCredits('p2');                 // ۳۰۰ اعتبار تا کیف خالی نباشد
            const t = document.getElementById('toast'); if (t) t.classList.add('hidden');
        }""")

        # --- packs read as time ---
        await page.evaluate("openWalletModal()")
        await shot("r3-10-packs-time.png")
        await page.evaluate("closeWalletModal()")

        # --- cap chooser on the remote success view ---
        await page.evaluate("""() => {
            openRemoteModal();
            document.getElementById('remoteNameInput').value = 'سارا محمدی';
            document.getElementById('remotePhoneInput').value = '09121110000';
            document.getElementById('remoteConsentCheck').checked = true;
            handleRemoteSubmit({ preventDefault(){} });
            const card = document.querySelector('#remoteModal > div');
            if (card) card.scrollIntoView({ block: 'start' });
        }""")
        await shot("r3-11-cap-chooser.png")

        # --- session bar: grace phase ---
        await page.evaluate("startSessionFromSuccess()")
        await shot("r3-12-session-grace.png")

        # --- session bar: billing phase, cap counter moving ---
        await page.evaluate("""() => {
            window.__creditNowOverride = creditSession.startedAt + 18 * 60000;
            tickChargeSession();
            document.getElementById('creditSessionBar').scrollIntoView({ block: 'center' });
        }""")
        await shot("r3-13-session-billing.png")

        # --- session bar: paused (not billed) ---
        await page.evaluate("pauseChargeSession()")
        await shot("r3-14-session-paused.png")

        await page.evaluate("""() => {
            pauseChargeSession();
            window.__creditNowOverride = creditSession.startedAt + 25 * 60000;
            tickChargeSession();
            const s = stopChargeSession('user');
            delete window.__creditNowOverride;
            closeRemoteModal();
        }""")
        await b.close()
    print("done")


asyncio.run(main())
