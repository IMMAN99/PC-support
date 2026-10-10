# Development tools

The maintained tools are portable and resolve project files relative to their own location. Run commands from the repository root unless a command says otherwise.

## Build and preview

```bash
python3 tools/ops/assemble_offline.py
python3 tools/ops/preview_server.py
```

The assembler creates the ignored, generated `پیش‌نمایش_آفلاین.html` from `پشتیبان_رایانه.html` and the frozen CSS/font assets. The preview server serves only that single file; it defaults to `127.0.0.1:8899` and does not expose the workspace directory. `./run-preview.sh` is a shortcut to start the server after building.

To expose the preview through a sandbox proxy, opt in explicitly:

```bash
PREVIEW_HOST=0.0.0.0 PORT=8899 python3 tools/ops/preview_server.py
```

## Automated browser audit

Install the pinned development requirements and Chromium as described in the root `README.md`, then run:

```bash
python3 tools/audit.py
```

The audit opens the generated offline page in Chromium. It is a regression check, not a production deployment or security certification.

## Asset and CSS maintenance

- `tools/ops/make_images.py` converts the PNG sources in `assets/img/src/` to WebP files. It requires Pillow. Updating the embedded images in the HTML remains a separate, reviewed step.
- `tools/ops/tailwind/` contains the optional Tailwind 3.4.17 generator. Its README explains how to build to a reviewable `out.css` without overwriting the committed frozen stylesheet automatically.

Historical one-off patches, screenshots, review boards, uploaded references, and test reports are local workspace material and are excluded from the proposed repository by `.gitignore`.
