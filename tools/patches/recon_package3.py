"""Package 3 recon: measure the real geometry the mobile fixes must respect."""
import asyncio, json, sys
from playwright.async_api import async_playwright

BUNDLE = ("file:///home/user/"
          "%D9%BE%DB%8C%D8%B4%E2%80%8C%D9%86%D9%85%D8%A7%DB%8C%D8%B4_%D8%A2%D9%81%D9%84%D8%A7%DB%8C%D9%86.html")

PROBE = """() => {
  const r = el => { if (!el) return null; const b = el.getBoundingClientRect();
    return {x: Math.round(b.x), y: Math.round(b.y), w: Math.round(b.width), h: Math.round(b.height)}; };
  const cs = el => el ? getComputedStyle(el) : null;
  const launcher = document.getElementById('aiFloatingLauncherBtn');
  const wrap = launcher ? launcher.parentElement : null;
  // widest text column actually rendered in the viewport
  const cols = [...document.querySelectorAll('main > div, main section > div, footer > div')]
      .map(e => ({w: Math.round(e.getBoundingClientRect().width), cls: e.className.slice(0, 40)}))
      .filter(o => o.w > 200).sort((a, b) => b.w - a.w).slice(0, 4);
  return {
    viewport: {w: innerWidth, h: innerHeight},
    launcher: r(launcher), launcherWrap: r(wrap),
    launcherDisplay: cs(launcher)?.display,
    header: r(document.querySelector('header')),
    headerBadge: {rect: r(document.getElementById('liveWorkStatusBadge')),
                  display: cs(document.getElementById('liveWorkStatusBadge'))?.display},
    aiHeaderBtn: (() => { const b = [...document.querySelectorAll('button')].find(x => /toggleAiDrawer/.test(x.getAttribute('onclick')||'')); 
      return b ? {display: cs(b).display, cls: b.className.slice(0,60), rect: r(b)} : null; })(),
    gutters: {left: r(document.querySelector('#bottleneck')).x, right: innerWidth - (r(document.querySelector('#bottleneck')).x + r(document.querySelector('#bottleneck')).w)},
    widestColumns: cols,
    hamburger: (() => { const b = [...document.querySelectorAll('button')].find(x => /toggleMobileMenu|mobileMenu/i.test(x.getAttribute('onclick')||'')); 
      return b ? {cls: b.className.slice(0,80), rect: r(b)} : null; })(),
    drawerIds: [...document.querySelectorAll('[id*="obileMenu"], [id*="obile"]')].map(e => e.id).slice(0, 6),
    heroH1: {ls: cs(document.querySelector('h1'))?.letterSpacing, size: cs(document.querySelector('h1'))?.fontSize},
    trackingTight: [...document.querySelectorAll('.tracking-tight')].map(e => ({tag: e.tagName, cls: e.className.slice(0,44),
        ls: getComputedStyle(e).letterSpacing, txt: e.textContent.trim().slice(0, 24)})),
    emojiHits: ['📅','🌙','☀️','💬','📸'].map(ch => ({ch, n: (document.body.innerHTML.match(new RegExp(ch, 'g'))||[]).length})),
  };
}"""


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for w, h, mobile in ((1440, 900, False), (1280, 900, False), (390, 844, True)):
            pg = await b.new_page(viewport={"width": w, "height": h}, is_mobile=mobile, has_touch=mobile)
            await pg.goto(BUNDLE, wait_until="load")
            await pg.wait_for_timeout(700)
            data = await pg.evaluate(PROBE)
            print(f"\n=== {w}x{h} ===")
            print(json.dumps(data, ensure_ascii=False, indent=1)[:2600])
            await pg.close()
        await b.close()

asyncio.run(main())
