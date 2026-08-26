"""Loopback-only admin HTTP actions for the static fetch server."""

from __future__ import annotations

import json
from http.server import SimpleHTTPRequestHandler

from .control_plane import git_status, is_loopback, prepare_deploy, run_render


class AdminFetchHandler(SimpleHTTPRequestHandler):
    def _json(self, payload: dict, status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _forbidden(self) -> None:
        self._json({
            "status": "HOLD",
            "reason": "Control plane only on loopback. No remote admin mutation.",
        }, 403)

    def _allowed(self) -> bool:
        host = self.client_address[0] if self.client_address else ""
        return is_loopback(host)

    def do_GET(self) -> None:  # noqa: N802
        if self.path.startswith("/__admin/git-status"):
            if not self._allowed():
                return self._forbidden()
            return self._json(git_status())
        if self.path.startswith("/__admin/health"):
            return self._json({"status": "OBSERVED", "plane": "admin-control"})
        return super().do_GET()

    def do_POST(self) -> None:  # noqa: N802
        if not self.path.startswith("/__admin/"):
            self.send_error(405)
            return
        if not self._allowed():
            return self._forbidden()
        try:
            length = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            length = 0
        if length:
            self.rfile.read(length)
        if self.path.startswith("/__admin/render"):
            return self._json(run_render())
        if self.path.startswith("/__admin/deploy-prepare"):
            return self._json(prepare_deploy())
        self._json({"status": "UNKNOWN", "path": self.path}, 404)
