# Rebuilding the frozen Tailwind stylesheet

`assets/tailwind-frozen.css` is the stylesheet inlined into the generated offline page. The editable source of truth is `پشتیبان_رایانه.html`; do not edit `پیش‌نمایش_آفلاین.html` by hand.

The optional generator is pinned to Tailwind CSS 3.4.17 in this directory's `package-lock.json`. It writes `out.css` for review and **does not replace** `assets/tailwind-frozen.css` automatically. A fresh output differs from the currently frozen stylesheet, so review the rule-level comparison and run the browser audit before accepting any replacement.

```bash
cd tools/ops/tailwind
npm ci
./build_css.sh

# Review rule-level changes before accepting them.
python3 compare_css.py

# If the diff is expected, copy it into the frozen asset:
cp out.css ../../../assets/tailwind-frozen.css
cd ../../..
python3 tools/ops/assemble_offline.py
python3 tools/audit.py
```

`collect_tokens.py` derives the temporary `tokens.txt` from literal class attributes and common `classList`/`className` assignments in the source, excluding inline CSS and HTML comments. Both `tokens.txt` and `out.css` are build artifacts and are ignored by Git. If the generated CSS differs, inspect the diff rather than assuming the current stylesheet should be replaced.

This nested npm package is a private build tool, not a separately licensed distributable. The generated Tailwind stylesheet carries Tailwind's upstream MIT notice; see `THIRD_PARTY_NOTICES.md`.
