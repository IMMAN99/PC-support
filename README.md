# پشتیبان پی‌سی · Poshtiban PC

Persian-language, right-to-left single-page front end for general PC guidance. The maintained app is static HTML with local styles, fonts, images, and build/QA tools. **There is no application server, shared database, payment processor, or remote-support backend in this workspace.**

## Source and generated files

- **`پشتیبان_رایانه.html`** — editable application source and source of truth.
- **`پیش‌نمایش_آفلاین.html`** — generated single-file offline-oriented build. It is intentionally ignored by Git and can be rebuilt at any time.
- **`assets/`** — frozen Tailwind CSS, embedded Vazirmatn font CSS, and image assets plus their PNG source files.
- **`tools/ops/assemble_offline.py`** — packages the source into the generated preview and checks Tailwind class coverage.
- **`tools/audit.py`** — optional Playwright/Chromium regression audit for the generated preview.

Do not edit the generated preview by hand. Update the source, rebuild, and run the checks instead.

## Run locally

Requires Python 3.10 or newer. The normal build uses only the Python standard library; Node.js is not required to run the site.

```bash
python3 tools/ops/assemble_offline.py
./run-preview.sh
```

Open `http://127.0.0.1:8899/`. Stop the server with `Ctrl+C`. The preview server defaults to loopback and serves only the generated page; it does not expose other workspace files. To use it behind a sandbox proxy, explicitly set `PREVIEW_HOST=0.0.0.0` and, optionally, `PORT=8899`.

The editable source HTML references the Tailwind CDN and Google Fonts. The offline build replaces those styling/font dependencies with the checked-in frozen Tailwind CSS and embedded Vazirmatn font data. Optional Gemini requests and user-initiated outbound platform links need a network connection.

## Development setup and checks

There are no Python runtime dependencies. Browser QA and optional image generation use pinned development dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate              # Windows PowerShell: .\\.venv\\Scripts\\Activate.ps1
python -m pip install -r requirements-dev.txt
python -m playwright install chromium
python tools/ops/assemble_offline.py
python -m compileall -q tools/audit.py tools/ops
python tools/audit.py
```

If Chromium reports missing operating-system libraries, follow Playwright's installation instructions for your platform. `tools/ops/pw_setup.sh` installs Chromium for the already-active Python environment; it does not use `sudo` or install OS packages. GitHub Actions runs the build and browser audit on pushes and pull requests.

### Optional stylesheet rebuild

Only needed when adding or changing Tailwind utility classes. It uses Node.js 18+ and the nested, pinned Tailwind kit; see [`tools/ops/tailwind/README.md`](tools/ops/tailwind/README.md). It generates a reviewable `out.css` and does not replace the frozen stylesheet automatically.

### Optional image rebuild

`python tools/ops/make_images.py` converts `assets/img/src/*.png` to WebP using Pillow. This does **not** update the image data embedded in the HTML; review and update the source separately if replacing a site image.

## Application, privacy, and claim scope

See [`SECURITY.md`](SECURITY.md) for key-handling limitations and vulnerability-reporting guidance.

- Booking and remote-request forms only write local records to that browser's `localStorage`. Their selected dates are suggestions, not confirmed appointments; no request, call, payment, remote session, or external tracking lookup is performed by the form itself.
- Credit/wallet/session controls are local interface state only. They do not represent money, a payment balance, or a real support session. Do not rely on them for identity, payment, or service operations.
- The optional Gemini API key is entered by the user and stored in that browser's `localStorage`; it is not embedded in the source. A browser-side key cannot be kept secret from scripts running on the same origin. If Gemini is used, diagnostic text or image content is sent to Google's Generative Language API. Avoid sending sensitive or confidential information unless permitted.
- The source copy uses explicit “not confirmed/not announced” wording for unverified availability, location, prices, terms, warranties, credentials, service outcomes, and timing. Benchmark figures and the local simulator are labeled as illustrative; they are not device measurements or performance promises.
- The hard-coded `DEMO_TICKETS` entries are synthetic and remain in the source as requested. Their IDs, devices, names, and progress values are retained; displayed statuses/notes no longer assert that a repair, test, data transfer, warranty, or delivery occurred. No page-wide demo notice was added.
- JSON-LD is limited to neutral `WebSite` metadata. No business-service rating or `AggregateRating` markup is present; the visible page does not publish a star rating. Google also excludes business-controlled self-ratings on a business's own `LocalBusiness`/`Organization` page from review-snippet eligibility ([Google guidance](https://developers.google.com/search/docs/appearance/structured-data/review-snippet)).

## Publication checks and repository scope

- The existing Open Graph URL (`https://poshtibanpc.ir`) is retained from the source but has not been independently confirmed. Verify it before production publication. Open Graph/Twitter image metadata still uses a `placehold.co` placeholder.
- The visible platform links go to generic messaging-platform homepages, not verified business accounts. The optional `SITE_CONTACT` WhatsApp/Telegram values are empty; configure only approved account destinations if direct handoff links are intended.
- The Gemini model identifier contains `preview`; confirm current availability before relying on the optional integration.
- `.gitignore` keeps workspace-only material out of the proposed repository: original attachments under `uploads/`, internal documents under `docs/`, screenshots, reports, historical one-off patch scripts, and the generated offline HTML. These files remain in the working directory and are not needed to build the maintained application. `uploads/` has not been modified.
- The owner confirms that all bundled PNG/WebP images may be redistributed. Five of the six WebP assets match data embedded byte-for-byte in the source; `ai-diagnostic.webp` has no filename reference and no exact embedded match. It is retained because its purpose is uncertain and the image pipeline processes the full set. Preserve any attribution requirements that apply.
- The six embedded Vazirmatn WOFF2 faces report version 33.003, matching the upstream [v33.003 release](https://github.com/rastikerdar/vazirmatn/releases/tag/v33.003). Its OFL 1.1 notice and Tailwind CSS 3.4.17's MIT notice are recorded in [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md). The font files have not been byte-compared against the upstream archive.
- There is deliberately **no project-level `LICENSE`**. The owner must choose whether and under what terms to license the project's own code and content. Third-party notices do not license the application itself. This source is not configured for GitHub Pages deployment (`index.html` and a deployment workflow are not included).

## فارسی

این پروژه یک رابط تک‌صفحه‌ای فارسی و راست‌به‌چپ برای راهنمایی عمومی رایانه است. فایل اصلی و مرجع ویرایش `پشتیبان_رایانه.html` است؛ پیش‌نمایش تک‌فایلی با دستور `python3 tools/ops/assemble_offline.py` ساخته می‌شود و فایل تولیدی را نباید دستی ویرایش کرد.

برای اجرا، پیش‌نمایش را بسازید و سپس `./run-preview.sh` را اجرا کنید. فرم‌های درخواست، انتخاب زمان و اطلاعات اعتبار فقط در `localStorage` همان مرورگر ذخیره می‌شوند؛ ارسال درخواست، رزرو قطعی، تماس، اتصال از راه دور یا پرداخت انجام نمی‌شود. کلید اختیاری Gemini نیز در مرورگر ذخیره می‌شود و در صورت استفاده، متن یا تصویر عیب‌یابی به سرویس گوگل فرستاده می‌شود؛ اطلاعات حساس را ارسال نکنید.

اطلاعات تأییدنشده دربارهٔ نشانی، ساعات، قیمت، شرایط، ضمانت، مجوزها و نتیجهٔ خدمات در متن صفحه به‌عنوان اعلام‌نشده مشخص شده‌اند. رکوردهای `DEMO_TICKETS` ساختگی و حفظ شده‌اند؛ وضعیت و یادداشت آن‌ها وقوع تعمیر، آزمون، انتقال داده یا تحویل را تأیید نمی‌کند. هیچ اعلان سراسریِ نمایشی افزوده نشده است.

مالک تأیید کرده است که تصاویر PNG و WebP بسته‌شده قابل بازتوزیع‌اند؛ الزام انتساب احتمالی را حفظ کنید. پیوست‌ها، یادداشت‌های داخلی، گزارش‌ها و تصاویر آزمون با `.gitignore` از مخزن پیشنهادی کنار گذاشته شده‌اند اما از پوشهٔ کاری حذف نشده‌اند. پوشهٔ `uploads/` تغییر نکرده است. برای کد خود پروژه هیچ مجوزی انتخاب یا اضافه نشده؛ پیش از انتشار، مالک باید دربارهٔ مجوز تصمیم بگیرد.
