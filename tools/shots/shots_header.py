#!/usr/bin/env python3
"""Header crops at every breakpoint tier → screenshots/states/hdr-<width>.png"""
import asyncio
import os
from playwright.async_api import async_playwright

FILE = "file:///home/user/%D9%BE%DB%8C%D8%B4%E2%80%8C%D9%86%D9%85%D8%A7%DB%8C%D8%B4_%D8%A2%D9%81%D9%84%D8%A7%DB%8C%D9%86.html"
OUT = "/home/user/screenshots/states"
WIDTHS = [1920, 1440, 1280, 1024, 768, 430, 390, 360, 320]


async def main():
    os.makedirs(OUT, exist_ok=True)
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={"width": 1440, "height": 900}, reduced_motion="reduce", device_scale_factor=2)
        await pg.goto(FILE, wait_until="load")
        await pg.wait_for_timeout(700)
        for w in WIDTHS:
            await pg.set_viewport_size({"width": w, "height": 900})
            await pg.wait_for_timeout(350)
            await pg.screenshot(path=f"{OUT}/hdr-{w}.png", clip={"x": 0, "y": 0, "width": w, "height": 60})
            info = await pg.evaluate(r"""() => {
              const b = document.querySelector('header > div');
              const vis = el => { const r = el.getBoundingClientRect(); return r.width > 0 && r.height > 0; };
              return { items: [...b.querySelectorAll('a,button,nav')].filter(vis)
                        .map(e => (e.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 20)),
                       overflow: b.scrollWidth - b.clientWidth };
            }""")
            print(f"{w:>5}px  overflow={info['overflow']:>2}  " + " · ".join(info["items"]))
        await b.close()


asyncio.run(main())
