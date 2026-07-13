"""Minimal dependency-free HTTP server for the agent (stdlib only)."""

import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

from .auth import check_token
from .routes import dispatch


class _Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def _send(self, code, payload):
        body = json.dumps(payload, default=str).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):  # noqa: N802
        self._handle("GET")

    def do_POST(self):  # noqa: N802
        self._handle("POST")

    def _handle(self, method):
        auth = self.headers.get("Authorization", "")
        token = auth.replace("Bearer ", "", 1) if auth.startswith("Bearer ") else None
        if not check_token(token):
            self._send(401, {"error": "unauthorized"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0") or "0")
            raw = self.rfile.read(length) if length else b"{}"
            body = json.loads(raw.decode("utf-8") or "{}")
        except Exception:
            body = {}
        code, payload = dispatch(self.server.agent, method, self.path, body)
        self._send(code, payload)

    def log_message(self, *args):
        pass


def run(agent, host: str = "127.0.0.1", port: int = 8787):
    server = HTTPServer((host, port), _Handler)
    server.agent = agent
    print(f"Unified Agent API on http://{host}:{port}  (Ctrl+C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
