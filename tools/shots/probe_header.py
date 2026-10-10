#!/usr/bin/env python3
"""Diagnose the header bar at many viewport widths: overflow + which items stick out."""
import asyncio
import sys
from playwright.async_api import async_playwright

FILE = "file:///home/user/%D9%BE%DB%8C%D8%B4%E2%80%8C%D9%86%D9%85%D8%A7%DB%8C%D8%B4_%D8%A2%D9%81%D9%84%D8%A7%DB%8C%D9%86.html"
WIDTHS = [int(x) for x in sys.argv[1:]] or [1920, 1600, 1536, 1440, 1366, 1280, 1180, 1100,
                                           1024, 960, 900, 834, 768, 700, 640, 430, 390, 360, 320]

PROBE = r"""() => {
  const bar = document.querySelector('header > div');
  const rect = e => { const r = e.getBoundingClientRect(); return {x: Math.round(r.x), r: Math.round(r.right), w: Math.round(r.width)}; };
  const items = [];
  for (const k of bar.children) {
    if (k.tagName === 'DIV' && !k.id) { for (const c of k.children) items.push({name: (c.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 18) || c.tagName, ...rect(c)}); }
    else items.push({name: (k.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 18) || k.tagName, ...rect(k)});
  }
  const vis = items.filter(i => i.w > 0);
  return { docOverflow: document.documentElement.scrollWidth - innerWidth,
           barOverflow: bar.scrollWidth - bar.clientWidth,
           clipped: vis.filter(i => i.x < -1 || i.r > innerWidth + 1).map(i => `${i.name} [${i.x}→${i.r}]`),
           count: vis.length, sum: vis.reduce((s, i) => s + i.w, 0) };
}"""


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={"width": 1440, "height": 900}, reduced_motion="reduce")
        await pg.goto(FILE, wait_until="load")
        await pg.wait_for_timeout(600)
        for w in WIDTHS:
            await pg.set_viewport_size({"width": w, "height": 900})
            await pg.wait_for_timeout(250)
            r = await pg.evaluate(PROBE)
            bad = "  ⚠ OVERFLOW" if (r["docOverflow"] > 1 or r["clipped"]) else ""
            print(f"{w:>5}px  doc+{r['docOverflow']:>4}  bar+{r['barOverflow']:>4}  visible={r['count']:>2}  sum={r['sum']:>4}{bad}")
            for c in r["clipped"]:
                print(f"          ↳ clipped: {c}")
        await b.close()


asyncio.run(main())
