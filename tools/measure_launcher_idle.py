"""Measure the launcher's overlap *at rest* (what a reader actually sees) — mobile + desktop.

The audit's F-11 probe samples 250 ms after a scroll, i.e. mid-animation (the page turns on
`scroll-smooth`, so programmatic scrolls animate for ~700 ms). This script waits for the
scroll to settle (1200 ms) so it measures the idle state: launcher visible again.
"""
import asyncio
from playwright.async_api import async_playwright

BUNDLE = ("file:///home/user/"
          "%D9%BE%DB%8C%D8%B4%E2%80%8C%D9%86%D9%85%D8%A7%DB%8C%D8%B4_%D8%A2%D9%81%D9%84%D8%A7%DB%8C%D9%86.html")

PROBE = """() => {
  const vis = el => { const cs = getComputedStyle(el);
    return cs.display !== 'none' && cs.visibility !== 'hidden' && parseFloat(cs.opacity) > 0.05; };
  const el = document.getElementById('aiFloatingLauncherBtn');
  if (!el || !vis(el)) return {launcherVisible: false, rect: null, hits: []};
  const a = el.getBoundingClientRect();
  if (a.bottom <= 0 || a.top >= innerHeight) return {launcherVisible: false, rect: a, hits: []};
  const hits = [...document.querySelectorAll('h2, h3, p, li, span, b, code')].filter(e => {
    if (!vis(e)) return false;
    const r = e.getBoundingClientRect();
    if (!r.width || !r.height || r.height > 200) return false;
    if (el.contains(e) || !(r.top < innerHeight && r.bottom > 0)) return false;
    return a.left < r.right && a.right > r.left && a.top < r.bottom && a.bottom > r.top;
  }).map(e => e.textContent.trim().slice(0, 26));
  return {launcherVisible: true, rect: {l: Math.round(a.left), t: Math.round(a.top),
          r: Math.round(a.right), b: Math.round(a.bottom)}, hits: hits.slice(0, 3)};
}"""


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for w, h, mobile in ((390, 844, True), (1440, 900, False)):
            pg = await b.new_page(viewport={"width": w, "height": h}, is_mobile=mobile, has_touch=mobile)
            await pg.goto(BUNDLE, wait_until="load")
            await pg.wait_for_timeout(800)
            print(f"\n=== {w}x{h} (idle, after the scroll animation settles) ===")
            total = 0
            for sel in ("#speed-booster", "#bottleneck", "#plans", "footer"):
                for block in ("start", "center"):
                    await pg.evaluate(f"document.querySelector('{sel}').scrollIntoView({{block:'{block}'}})")
                    await pg.wait_for_timeout(1300)          # smooth scroll + 450 ms reveal
                    d = await pg.evaluate(PROBE)
                    flag = "✗" if d["hits"] else "✓"
                    total += len(d["hits"])
                    print(f"  {flag} {sel}[{block}] launcher={d['launcherVisible']} rect={d['rect']} hits={d['hits']}")
            print(f"  → total overlapping text nodes at rest: {total}")
            await pg.close()
        await b.close()

asyncio.run(main())
