# Rebuilding the frozen Tailwind CSS

`assets/tailwind-frozen.css` is what the offline bundle inlines. Regenerate it whenever a
**new Tailwind class** appears in `پشتیبان_رایانه.html` (otherwise `tools/ops/assemble_offline.py` exits 1
and lists the classes without a rule).

```bash
# 1) one-time: local generator (no network needed at runtime)
cd tools/ops/tailwind && npm init -y && npm i -D tailwindcss@3.4.17

# 2) collect every class token used by the page (including JS template strings)
python3 - <<'PY'
import io, re
h = io.open('/home/user/پشتیبان_رایانه.html', encoding='utf-8').read()
t = set()
for m in re.finditer(r'class="([^"]*)"', h): t.update(m.group(1).split())
for m in re.finditer(r"classList\.(?:add|remove|toggle|contains)\(\s*['\"]([^'\"]+)['\"]", h): t.update(m.group(1).split())
for m in re.finditer(r'\.className\s*=\s*[\'"`]([^\'"`]+)[\'"`]', h): t.update(m.group(1).split())
for m in re.finditer(r'const\s+\w*[Cc]lass\s*=\s*"([^"]*)"', h): t.update(m.group(1).split())
io.open('tokens.txt', 'w', encoding='utf-8').write("\n".join(sorted(x for x in t if x)))
PY

# 3) build + install
node node_modules/.bin/tailwindcss -c tailwind.config.js -i in.css -o out.css --minify
cp out.css /home/user/assets/tailwind-frozen.css

# 4) verify coverage
cd /home/user && python3 tools/ops/assemble_offline.py
```

`tailwind.config.js` here points `content` at the page + `tokens.txt` (written next to it, not committed).
