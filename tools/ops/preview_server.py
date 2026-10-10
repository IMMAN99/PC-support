#!/usr/bin/env python3
"""Serve only the generated, self-contained offline preview.

The server defaults to loopback and deliberately does not expose the workspace
filesystem or enable cross-origin requests. Set PREVIEW_HOST=0.0.0.0 only when
a sandbox/reverse proxy explicitly needs to reach this preview.
"""
from http.server import BaseHTTPRequestHandler
import os
from pathlib import Path
import socketserver
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[2]
OFFLINE = ROOT / "پیش‌نمایش_آفلاین.html"
HOST = os.environ.get("PREVIEW_HOST", "127.0.0.1")
PORT = int(os.environ.get("PORT", "8899"))
ALLOWED_PATHS = {"", "/", "/index.html", "/پیش‌نمایش_آفلاین.html"}


class PreviewHandler(BaseHTTPRequestHandler):
    """Expose the single generated page, never arbitrary workspace files."""

    def _respond(self, status: int, body: bytes, content_type: str, head_only: bool) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        self.send_header("Referrer-Policy", "no-referrer")
        self.end_headers()
        if not head_only:
            self.wfile.write(body)

    def _serve(self, head_only: bool) -> None:
        path = unquote(urlsplit(self.path).path)
        if path not in ALLOWED_PATHS:
            self._respond(404, b"Not found\n", "text/plain; charset=utf-8", head_only)
            return

        try:
            body = OFFLINE.read_bytes()
        except FileNotFoundError:
            self._respond(
                503,
                b"Offline preview is not built. Run tools/ops/assemble_offline.py first.\n",
                "text/plain; charset=utf-8",
                head_only,
            )
            return

        self._respond(200, body, "text/html; charset=utf-8", head_only)

    def do_GET(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
        self._serve(head_only=False)

    def do_HEAD(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
        self._serve(head_only=True)

    def log_message(self, fmt: str, *args: object) -> None:
        # Keep local preview output readable; the handler serves no user data.
        return


class ThreadingServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


if __name__ == "__main__":
    if not 1 <= PORT <= 65535:
        raise SystemExit("PORT must be between 1 and 65535")
    with ThreadingServer((HOST, PORT), PreviewHandler) as server:
        print(f"Offline preview listening on {HOST}:{PORT}", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
