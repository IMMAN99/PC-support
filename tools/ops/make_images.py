#!/usr/bin/env python3
"""
ساخت دارایی‌های تصویری سایت — از PNG‌های خام تا WebP سبک برای جاسازی base64.

ورودی:  assets/img/src/*.png   (تصاویر ساخته‌شده/واقعی)
خروجی:  assets/img/*.webp      (برش ۱۶:۹، عرض هدف، کیفیت هدف)

تصاویر بعداً مستقیم به‌صورت data:image/webp;base64 داخل فایل سایت جاسازی می‌شوند
(صفر درخواست بیرونی). اگر بعداً عکس واقعی گذاشتید، فقط همین اسکریپت را دوباره
اجرا کنید و بعد پچ جای‌گذاری تصویر را تازه بسازید.

اجرا:  python3 tools/ops/make_images.py
"""
import io, os, sys

try:
    from PIL import Image
except ImportError:
    sys.exit("Pillow لازم است:  pip install pillow")

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(ROOT, "assets", "img", "src")
OUT = os.path.join(ROOT, "assets", "img")

# name → (عرض هدف, کیفیت WebP, نسبت تصویر w/h)
JOBS = {
    "hero-bench":       (1280, 70, (16, 9)),   # نوار هیرو
    "remote-session":   (1100, 68, (16, 9)),   # باند پشتیبانی ریموت
    "ai-diagnostic":    (1100, 68, (16, 9)),   # باند عیب‌یاب هوشمند
    "hardware-drives":  (1100, 68, (16, 9)),   # باند تست سرعت
    "ram-cpu":          (1100, 68, (16, 9)),   # باند تست گلوگاه
    "workshop-detail":  (900,  68, (16, 9)),   # باند باریک (فوتر/پرسش‌ها)
}


def crop_ratio(im, ratio):
    """برش مرکزی به نسبت دلخواه."""
    tw, th = ratio
    w, h = im.size
    target = tw / th
    if w / h > target:                 # عریض‌تر از هدف → از دو طرف ببر
        nw = int(h * target)
        x = (w - nw) // 2
        return im.crop((x, 0, x + nw, h))
    nh = int(w / target)               # بلندتر از هدف → از بالا/پایین ببر
    y = (h - nh) // 2
    return im.crop((0, y, w, y + nh))


def main():
    os.makedirs(OUT, exist_ok=True)
    total = 0
    for name, (width, quality, ratio) in JOBS.items():
        src = os.path.join(SRC, name + ".png")
        if not os.path.exists(src):
            print(f"  ⚠️  نیست: {src}")
            continue
        im = Image.open(src).convert("RGB")
        im = crop_ratio(im, ratio)
        h = round(width * ratio[1] / ratio[0])
        im = im.resize((width, h), Image.LANCZOS)
        dst = os.path.join(OUT, name + ".webp")
        im.save(dst, "WEBP", quality=quality, method=6)
        size = os.path.getsize(dst)
        total += size
        print(f"  ✓ {name}.webp  {width}×{h}  q{quality}  {size/1024:.0f} KB")
    print(f"\n  مجموع: {total/1024:.0f} KB  ({total} بایت)")


if __name__ == "__main__":
    main()
