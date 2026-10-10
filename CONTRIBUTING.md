# Contributing

Thanks for helping improve the Poshtiban PC front end.

## Working on the site

- Edit `پشتیبان_رایانه.html`; it is the source of truth.
- Treat `پیش‌نمایش_آفلاین.html` as generated output. Rebuild it with `python3 tools/ops/assemble_offline.py` instead of editing it directly.
- Preserve the Persian RTL identity, existing content and behavior, manual/automatic theme rules, reduced-motion support, and the established business rules unless a change is specifically intended and reviewed.
- For a new Tailwind utility, follow `tools/ops/tailwind/README.md`; inspect generated CSS before replacing the frozen stylesheet.

## Checks

Use Python 3.10 or newer. Install the pinned development dependencies in a virtual environment, install Chromium with Playwright, then run:

```bash
python3 tools/ops/assemble_offline.py
python3 -m compileall -q tools/audit.py tools/ops
python3 tools/audit.py
```

The browser audit is also run by GitHub Actions for pushes and pull requests.

## Security, data, and assets

- Never add API keys, passwords, customer records, or other private data to HTML, scripts, tests, screenshots, or documentation.
- Do not treat browser `localStorage` as a secure or authoritative database.
- Do not add or replace third-party assets without confirming redistribution rights and recording required attribution/license notices.
- Do not add a project license without the repository owner's decision. Third-party notices do not license the project's own source code.
