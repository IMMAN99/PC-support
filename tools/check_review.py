#!/usr/bin/env python3
"""Render docs/بازبینی_رابط_کاربری.html headlessly to verify it still works
(filters, checkboxes, no JS errors, no external resources). Output goes to /tmp."""
import asyncio, os
from playwright.async_api import async_playwright

DOC = "file:///home/user/docs/بازبینی_رابط_کاربری.html"
OUT = "/tmp/review-check"
os.makedirs(OUT, exist_ok=True)


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={"width": 1180, "height": 1000})
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto(DOC, wait_until="load")
        await pg.wait_for_timeout(600)

        # NB: POS-01 sits outside #list on purpose (it is the repositioning card in the summary),
        # so count only the cards the filter actually owns.
        for f in ("high", "a11y", "all"):
            await pg.click(f'button[data-filter="{f}"]')
            await pg.wait_for_timeout(200)
            n = await pg.evaluate("()=>[...document.querySelectorAll('#list article.f')].filter(a=>a.style.display!=='none').length")
            print(f"  filter '{f}': {n} findings visible")

        ext = await pg.evaluate("()=>[...document.querySelectorAll('link,script,img')].filter(e=>(e.src||e.href||'').startsWith('http')).length")
        print("  external resources:", ext, "| JS errors:", errs or "none")
        await pg.screenshot(path=f"{OUT}/doc.png", full_page=False)
        await b.close()

asyncio.run(main())
