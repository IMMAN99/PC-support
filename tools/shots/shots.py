#!/usr/bin/env python3
"""
Section screenshots of the offline bundle + a quick layout audit.

usage:  python3 tools/shots/shots.py [--tag desktop] [--width 1440] [--height 900] [--dark]
output: screenshots/<tag>/*.png
"""
import argparse, asyncio, os
from playwright.async_api import async_playwright

ROOT = "/home/user"
FILE = f"file://{ROOT}/پیش‌نمایش_آفلاین.html"
SECTIONS = [
    ("01-hero", None), ("02-ai-diag", "#ai-diagnostic"), ("03-speed", "#speed-booster"),
    ("04-bottleneck", "#bottleneck"), ("05-plans", "#plans"), ("06-faq", "#faq"), ("07-footer", "footer"),
]


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="desktop")
    ap.add_argument("--width", type=int, default=1440)
    ap.add_argument("--height", type=int, default=900)
    ap.add_argument("--dark", action="store_true")
    args = ap.parse_args()
    outdir = os.path.join(ROOT, "screenshots", args.tag)
    os.makedirs(outdir, exist_ok=True)

    msgs, errors = [], []
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": args.width, "height": args.height}, reduced_motion="reduce")
        page.on("console", lambda m: msgs.append(f"[{m.type}] {m.text[:160]}") if m.type == "error" else None)
        page.on("pageerror", lambda e: errors.append(str(e)[:250]))
        await page.goto(FILE, wait_until="load")
        await page.wait_for_timeout(800)
        if args.dark:
            await page.evaluate("toggleTheme()")

        for name, sel in SECTIONS:
            if sel:
                el = await page.query_selector(sel)
                if not el:
                    print(f"   !! selector not found: {sel}")
                    continue
                await el.scroll_into_view_if_needed()
                await page.wait_for_timeout(400)
            else:
                await page.evaluate("window.scrollTo(0,0)")
                await page.wait_for_timeout(250)
            await page.screenshot(path=os.path.join(outdir, f"{name}.png"))

        audit = await page.evaluate("""() => {
          const t = [];
          document.querySelectorAll('button,a,[onclick]').forEach(el => {
            const r = el.getBoundingClientRect();
            if (r.width && r.height && r.height < 32) t.push(Math.round(r.height) + 'px ' +
              (el.innerText || el.getAttribute('aria-label') || el.id || el.tagName).trim().slice(0, 30));
          });
          return {fonts: document.fonts.status, pageH: document.body.scrollHeight,
                  overflow: document.documentElement.scrollWidth > window.innerWidth + 1,
                  smallTargets: t.length, sample: t.slice(0, 6)};
        }""")
        print(f"\n=== AUDIT ({args.tag}) ===")
        print(f"  fonts: {audit['fonts']} | height: {audit['pageH']}px | h-overflow: {audit['overflow']}")
        print(f"  tap targets under 32px: {audit['smallTargets']}  e.g. {audit['sample']}")
        if msgs:    print("  console errors:", *msgs[:8], sep="\n      ")
        if errors:  print("  JS ERRORS:", *errors[:8], sep="\n      ")
        print(f"  saved → {outdir}")
        await browser.close()

asyncio.run(main())
