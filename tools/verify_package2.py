"""Package 2 — behavioural verification (run after tools/patches/patch_package2.py).

Covers what an aria-only audit cannot see:
  1. the delete button that now lives *inside* the <label> must not re-open the picker
  2. drag & drop really works (the placeholder promised it before; no code existed)
  3. the FAQ accordion animates open *and* closed, aria stays in sync
  4. the focus ring appears for keyboard users only, never for a real mouse click

Test 1/2 drive the *real* pipeline (FileReader -> decode -> canvas -> preview), so the
fixture must be a genuinely decodable image: a 64x48 PNG is built here at runtime.

Usage:  python3 tools/verify_package2.py
"""
import asyncio
import base64
import struct
import sys
import zlib

from playwright.async_api import async_playwright

BUNDLE = (
    "file:///home/user/"
    "%D9%BE%DB%8C%D8%B4%E2%80%8C%D9%86%D9%85%D8%A7%DB%8C%D8%B4_%D8%A2%D9%81%D9%84%D8%A7%DB%8C%D9%86.html"
)
FAILS = []


def tiny_png(w=64, h=48, rgb=(200, 40, 40)):
    """Minimal valid PNG so Chromium can actually decode it."""
    raw = b"".join(b"\x00" + bytes(rgb) * w for _ in range(h))

    def chunk(tag, data):
        body = tag + data
        return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF)

    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(raw, 9))
        + chunk(b"IEND", b"")
    )


def report(name, data, ok):
    print(f"  {'✓' if ok else '✗'} {name}\n      {data}")
    if not ok:
        FAILS.append(name)


async def main():
    png_b64 = base64.b64encode(tiny_png()).decode()
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        # عمداً با حرکت کامل: آزمون ۳ باید انیمیشن آکاردئون را ببیند (در حالت «کاهش حرکت»
        # خود سایت انیمیشن را مطابق دسترس‌پذیری رد می‌کند، پس این آزمون آن حالت نیست).
        pg = await browser.new_page(viewport={"width": 1440, "height": 900})
        errors = []
        pg.on("pageerror", lambda e: errors.append(str(e)))
        await pg.goto(BUNDLE, wait_until="load")
        await pg.wait_for_timeout(700)
        await pg.evaluate("switchDiagMode('ai-vision')")
        await pg.wait_for_timeout(300)

        # 1 — a real image through the real pipeline, then the in-label delete button
        r1 = await pg.evaluate(
            """async (b64) => {
                const bytes = Uint8Array.from(atob(b64), c => c.charCodeAt(0));
                const file = new File([bytes], 'bsod-shot.png', {type: 'image/png'});
                const inp = document.getElementById('aiImageFileInput');
                const dt = new DataTransfer(); dt.items.add(file);
                Object.defineProperty(inp, 'files', {value: dt.files, configurable: true});
                handleImageSelected({target: inp});
                await new Promise(r => setTimeout(r, 400));
                const previewShown = !document.getElementById('dropZonePreview').classList.contains('hidden');
                const label = document.getElementById('imageFileNameText').textContent.trim();
                const del = [...document.querySelectorAll('#dropZonePreview button')].pop();
                del.click();                       // must NOT re-open the file picker
                await new Promise(r => setTimeout(r, 120));
                const resetBack = !document.getElementById('dropZonePlaceholder').classList.contains('hidden');
                return {previewShown, label, resetBack};
            }""",
            png_b64,
        )
        report("۱) تصویر واقعی → پیش‌نمایش، و دکمهٔ «حذف تصویر» داخل label بدون باز کردن پنجرهٔ فایل",
               r1, r1["previewShown"] and r1["resetBack"] and "KB" in r1["label"])

        # 2 — drag & drop through the same pipeline
        r2 = await pg.evaluate(
            """async (b64) => {
                const bytes = Uint8Array.from(atob(b64), c => c.charCodeAt(0));
                const dt = new DataTransfer();
                dt.items.add(new File([bytes], 'dropped.png', {type: 'image/png'}));
                const zone = document.getElementById('dropZoneArea');
                zone.dispatchEvent(new DragEvent('dragover', {bubbles: true, cancelable: true, dataTransfer: dt}));
                const hi = zone.classList.contains('border-purple-500');
                zone.dispatchEvent(new DragEvent('drop', {bubbles: true, cancelable: true, dataTransfer: dt}));
                await new Promise(r => setTimeout(r, 400));
                return {highlightedOnDrag: hi,
                        preview: !document.getElementById('dropZonePreview').classList.contains('hidden'),
                        name: document.getElementById('imageFileNameText').textContent.trim(),
                        highlightedAfter: zone.classList.contains('border-purple-500')};
            }""",
            png_b64,
        )
        report("۲) رها کردن فایل: هایلایت هنگام کشیدن + پردازش واقعی تصویر",
               r2, r2["highlightedOnDrag"] and r2["preview"] and "dropped.png" in r2["name"]
               and not r2["highlightedAfter"])
        await pg.evaluate("resetImageSelection()")

        # 3 — FAQ accordion
        r3 = await pg.evaluate(
            """async () => {
                const btn = document.querySelectorAll('#faq button[aria-expanded]')[1];
                const ans = document.getElementById(btn.getAttribute('aria-controls'));
                const closedH = ans.getBoundingClientRect().height;
                btn.click();
                await new Promise(r => setTimeout(r, 60));
                const midH = ans.getBoundingClientRect().height;
                await new Promise(r => setTimeout(r, 500));
                const openH = ans.getBoundingClientRect().height;
                btn.click();
                await new Promise(r => setTimeout(r, 700));
                const backH = ans.getBoundingClientRect().height;
                return {closedH, midH, openH, backH, aria: btn.getAttribute('aria-expanded'),
                        scrollH: ans.scrollHeight};
            }"""
        )
        report("۳) آکاردئون FAQ: انیمیشن ارتفاع در باز و بسته شدن + aria-expanded هم‌زمان",
               r3, r3["openH"] > r3["closedH"] and r3["midH"] < r3["openH"]
               and r3["backH"] <= r3["closedH"] + 2 and r3["aria"] == "false")

        # 4 — focus ring: real mouse click vs real Tab key.
        # NB: measure outlineStyle, not outlineWidth — outline-width computes to `medium`
        # (3px) even when outline-style is `none`, so width alone always looks like a hit.
        probe = """(sel) => { const el = document.querySelector(sel);
            return {style: getComputedStyle(el).outlineStyle,
                    width: getComputedStyle(el).outlineWidth,
                    matches: el.matches(':focus-visible'),
                    focused: document.activeElement === el}; }"""
        faq_btn = "#faq button[aria-expanded]"
        await pg.click(faq_btn)          # real mouse input, Playwright scrolls it into view itself
        await pg.wait_for_timeout(250)
        mouse = await pg.evaluate(probe, faq_btn)
        await pg.evaluate("document.querySelector('#faq button[aria-expanded]').click()")  # undo

        await pg.goto(BUNDLE, wait_until="load")
        await pg.wait_for_timeout(500)
        await pg.keyboard.press("Tab")
        await pg.wait_for_timeout(250)
        kbd = await pg.evaluate(probe, "a[href='#main']")
        report("۴) حلقهٔ فوکوس فقط برای کیبورد (ماوس: بدون حلقه)",
               {"mouse-click": mouse, "tab-key": kbd},
               mouse["focused"] and not mouse["matches"] and mouse["style"] == "none"
               and kbd["focused"] and kbd["matches"] and kbd["style"] == "solid")

        print("\n  JS errors:", errors or "none")
        if errors:
            FAILS.append("JS errors")
        await browser.close()

    print("\n" + ("  ALL CHECKS PASS ✓" if not FAILS else f"  FAILED: {FAILS}"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
