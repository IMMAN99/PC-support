# -*- coding: utf-8 -*-
"""
Assemble the single-file offline preview bundle from پشتیبان_رایانه.html,
inlining the frozen Tailwind CSS stylesheet and local Vazirmatn fonts.

Inputs :  پشتیبان_رایانه.html          (source of truth, edit this one; workspace root)
          assets/vazirmatn-inlined.css (6 × woff2, base64)
          assets/tailwind-frozen.css   (complete frozen Tailwind 3.4.17 build + gap-fill patch)
Output :  پیش‌نمایش_آفلاین.html          (generated — never edit by hand)
"""
import os
import re

# workspace root = two levels up from tools/ops/  (the bundle lives at the root,
# next to the source of truth, so both stay easy to find)
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MAIN_HTML_PATH = os.path.join(ROOT, "پشتیبان_رایانه.html")
OFFLINE_HTML_PATH = os.path.join(ROOT, "پیش‌نمایش_آفلاین.html")
FONTS_CSS_PATH = os.path.join(ROOT, "assets/vazirmatn-inlined.css")
FROZEN_CSS_PATH = os.path.join(ROOT, "assets/tailwind-frozen.css")

with open(MAIN_HTML_PATH, "r", encoding="utf-8") as f:
    main_html = f.read()

with open(FONTS_CSS_PATH, "r", encoding="utf-8") as f:
    fonts_css = f.read()

with open(FROZEN_CSS_PATH, "r", encoding="utf-8") as f:
    frozen_css = f.read()

s_cdn = main_html.find("<!-- Tailwind CSS CDN -->")
e_cdn = main_html.find("  <!-- Brand Styling, iOS Auto-Zoom Fix")
if s_cdn == -1 or e_cdn == -1:
    raise ValueError("Could not locate CDN or styling boundary markers in main HTML.")

offline_font_block = f"""<!-- ===== OFFLINE PREVIEW BUILD: all CDN assets inlined ===== -->
  <style>
{fonts_css}
  </style>
  """

offline_html = main_html[:s_cdn] + offline_font_block + main_html[e_cdn:]
# retitle for the offline build (regex: the source title may change as positioning evolves)
offline_html, n_titles = re.subn(
    r"<title>.*?</title>",
    "<title>پیش‌نمایش آفلاین | پشتیبان پی‌سی (نسخه تک‌فایلی بدون اینترنت)</title>",
    offline_html, count=1)
if n_titles != 1:
    raise ValueError("Could not retitle the offline build (no <title> found).")

head_close = offline_html.find("</head>")
if head_close == -1:
    raise ValueError("Could not locate </head> in HTML.")

offline_html = (
    offline_html[:head_close]
    + f"\n  <style id=\"frozen-tailwind\">\n{frozen_css}\n  </style>\n"
    + offline_html[head_close:]
)

with open(OFFLINE_HTML_PATH, "w", encoding="utf-8") as f:
    f.write(offline_html)

# ---- verification: every class the page uses must have a rule in the inlined CSS ----
import re

def css_unescape(s: str) -> str:
    return re.sub(r'\\(?:([0-9a-fA-F]{1,6})[ \t\n]?|(.))',
                  lambda m: chr(int(m.group(1), 16)) if m.group(1) else m.group(2), s)

inline_css = css_unescape(frozen_css)

# classes the page defines for itself (its own <style> blocks) need no Tailwind rule
custom_css = css_unescape("".join(re.findall(r'<style[^>]*>(.*?)</style>', main_html, re.S)))
own = set(re.findall(r'\.([A-Za-z][\w-]*)', custom_css))

# JS-only hook classes that intentionally carry no CSS (behavioural selectors)
HOOKS = {
    "book-time-btn", "booking-service-card", "check-box", "check-icon",
    "faq-answer", "faq-icon", "simCpu-opt", "simRam-opt", "simStorage-opt",
    "cal-day-cell", "cal-day-cell-off", "cal-day-cell-disabled", "selected",
}

tokens = set()
# 1) every class="…" attribute — includes the ones inside JS template strings
for m in re.finditer(r'class="([^"]*)"', main_html):
    tokens.update(m.group(1).split())
# 2) classList / className assignments
for m in re.finditer(r'classList\.(?:add|remove|toggle|contains)\(\s*[\'"]([^\'"]+)[\'"]', main_html):
    tokens.update(m.group(1).split())
for m in re.finditer(r'\.className\s*=\s*[\'"`]([^\'"`]+)[\'"`]', main_html):
    tokens.update(m.group(1).split())
# 3) two multi-class constants declared as bare strings in JS
for m in re.finditer(r'const\s+\w*[Cc]lass\s*=\s*"([^"]*)"', main_html):
    tokens.update(m.group(1).split())

utility = re.compile(r'^(?:(?:sm|md|lg|xl|2xl|dark|hover|focus|focus-visible|active|disabled|group-hover|print|rtl|ltr):)*'
                     r'[a-z][a-z0-9]*(?:[-\[][a-z0-9\[\]#./%(),_-]*)?$')

missing = sorted(t for t in tokens
                 if t not in own and t not in HOOKS and utility.match(t)
                 and ('.' + t) not in inline_css)

print(f"Packaged پیش‌نمایش_آفلاین.html successfully! ({len(offline_html)} chars, {os.path.getsize(OFFLINE_HTML_PATH)} bytes)")
if missing:
    print(f"⚠️  {len(missing)} class(es) used by the page have no CSS rule: {missing[:20]}")
    raise SystemExit(1)
print("✓ CSS coverage check passed — every class used by the page has a rule in the bundle.")
