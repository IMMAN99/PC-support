#!/usr/bin/env python3
"""Tiny static server for the live preview: root serves the offline (self-contained)
build so the sandboxed no-network preview iframe renders the site fully styled."""
import http.server
import socketserver
import os
import urllib.parse

# the site files live at the workspace root; resolve it from this file so the
# server keeps working from any checkout location
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OFFLINE = os.path.join(ROOT, "پیش‌نمایش_آفلاین.html")
PORT = 8899


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=ROOT, **kw)

    def translate_path(self, path):
        # strip query, decode
        path = path.split("?", 1)[0].split("#", 1)[0]
        decoded = urllib.parse.unquote(path)
        if decoded in ("/", ""):
            return OFFLINE
        return super().translate_path(decoded)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        self.send_header("Access-Control-Allow-Origin", "*")
        super().end_headers()

    def log_message(self, fmt, *args):
        pass  # keep preview logs quiet


class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True

    def handle_error(self, request, client_address):
        # Ignore client disconnects/broken pipes gracefully
        pass


if __name__ == "__main__":
    with Server(("0.0.0.0", PORT), Handler) as httpd:
        print(f"preview serving on :{PORT} (root -> offline build)", flush=True)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
