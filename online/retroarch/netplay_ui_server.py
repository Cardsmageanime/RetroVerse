#!/usr/bin/env python3
"""Loopback-only HTTP controller for native RetroArch netplay.

Serves the RetroVerse HTML interface and accepts validated preview/launch
requests. Not a public API. No wildcard CORS and no remote listening.
"""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import argparse
import json
import secrets
import subprocess
from urllib.parse import urlsplit
from netplay_bridge import build_command

ROOT = Path(__file__).resolve().parents[2]
NEON = ROOT / "interface" / "neon-showcase" / "index.html"
NETPLAY = Path(__file__).with_name("netplay.html")
MAX_REQUEST = 4096

def prepare(data):
    if not isinstance(data, dict):
        raise ValueError("JSON object required")
    allowed = {"mode", "retroarch", "core", "content", "peer", "port", "nick"}
    if set(data) - allowed:
        raise ValueError("Unexpected request fields")
    return build_command(data.get("mode"), data.get("retroarch", "retroarch"),
                         data.get("core", ""), data.get("content", ""),
                         data.get("peer"), data.get("port", 55435), data.get("nick"))

def handler_factory(token, port):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt, *args):
            # Avoid logging user-supplied paths, game names and identifiers.
            pass

        def _send(self, code, raw, content_type):
            self.send_response(code)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(raw)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Security-Policy", "default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; connect-src 'self'")
            self.end_headers()
            self.wfile.write(raw)

        def _json(self, status, obj):
            self._send(status, json.dumps(obj).encode(), "application/json; charset=utf-8")

        def do_GET(self):
            # Reject DNS-rebinding hosts before serving the session-bearing page.
            if self.headers.get("Host") != f"127.0.0.1:{port}":
                self._json(403, {"ok": False, "error": "host_rejected"})
                return
            path = urlsplit(self.path).path
            if path == "/":
                page = NEON
            elif path == "/netplay":
                page = NETPLAY
            else:
                self._json(404, {"ok": False, "error": "not_found"})
                return
            text = page.read_text(encoding="utf-8")
            if path == "/netplay":
                # Session token only readable by local browser page.
                text = text.replace("<script>\n(()=>", "<script>window.RETROVERSE_SESSION_TOKEN=" + json.dumps(token) + ";</script><script>\n(()=>", 1)
            self._send(200, text.encode(), "text/html; charset=utf-8")

        def do_POST(self):
            if self.path not in ("/api/netplay/preview", "/api/netplay/launch"):
                self._json(404, {"ok": False, "error": "not_found"})
                return
            # Defend against cross-site browser writes and DNS rebinding.
            if self.headers.get("Host") != f"127.0.0.1:{port}" or self.headers.get("Origin") not in (None, f"http://127.0.0.1:{port}"):
                self._json(403, {"ok": False, "error": "origin_rejected"})
                return
            if not secrets.compare_digest(self.headers.get("X-RetroVerse-Token", ""), token):
                self._json(403, {"ok": False, "error": "session_rejected"})
                return
            if self.headers.get("Content-Type", "").split(";")[0] != "application/json":
                self._json(415, {"ok": False, "error": "json_required"})
                return
            try:
                size = int(self.headers.get("Content-Length", "-1"))
                if not 1 <= size <= MAX_REQUEST:
                    raise ValueError("invalid payload size")
                data = json.loads(self.rfile.read(size).decode("utf-8"))
                cmd = prepare(data)
                if self.path.endswith("/preview"):
                    self._json(200, {"ok": True, "command": cmd})
                    return
                # Start a local process only after explicit browser confirmation.
                proc = subprocess.Popen(cmd, stdin=subprocess.DEVNULL,
                                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                self._json(200, {"ok": True, "pid": proc.pid})
            except (ValueError, TypeError, UnicodeError, OSError) as exc:
                self._json(400, {"ok": False, "error": str(exc)[:180]})

    return Handler

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--port", type=int, default=8768)
    args = p.parse_args()
    if not 1024 <= args.port <= 65535:
        p.error("Port must be between 1024 and 65535")
    token = secrets.token_urlsafe(32)
    server = ThreadingHTTPServer(("127.0.0.1", args.port), handler_factory(token, args.port))
    print(f"RetroVerse local Netplay UI: http://127.0.0.1:{args.port}/netplay", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()

if __name__ == "__main__":
    main()
