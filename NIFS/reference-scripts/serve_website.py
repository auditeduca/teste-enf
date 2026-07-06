#!/usr/bin/env python3
"""Serve the generated pt-BR site locally (website/pt).

Default: http://127.0.0.1:8765/ — dedicated dev port to avoid clashing with
other http.server instances on 8080 (repo root, Vite, etc.).
"""
from __future__ import annotations

import argparse
import http.server
import socket
import subprocess
import sys
import webbrowser
from functools import partial
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "website" / "pt"
DEFAULT_PORT = 8765


def pick_port(start: int, host: str = "127.0.0.1") -> int:
    for port in range(start, start + 20):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                sock.bind((host, port))
                return port
            except OSError:
                continue
    raise OSError(f"Nenhuma porta livre entre {start} e {start + 19}")


def open_browser(url: str) -> None:
    """Open local URL in a new browser context (Windows-friendly)."""
    if sys.platform == "win32":
        try:
            subprocess.Popen(
                ["cmd", "/c", "start", "", url],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return
        except OSError:
            pass
    webbrowser.open(url, new=1, autoraise=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Servidor local do site estático (website/pt)")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help=f"Porta (default: {DEFAULT_PORT})")
    parser.add_argument("--no-open", action="store_true", help="Não abrir o navegador automaticamente")
    parser.add_argument("--open", action="store_true", help="Abrir o navegador (default)")
    args = parser.parse_args()

    if not SITE.is_dir():
        print(f"ERROR: {SITE} not found. Run: python scripts/generate_website_pt.py")
        return 1
    if not (SITE / "index.html").is_file():
        print(f"ERROR: {SITE / 'index.html'} missing. Run: python scripts/generate_website_pt.py")
        return 1

    host = "127.0.0.1"
    try:
        port = pick_port(args.port, host)
    except OSError as exc:
        print(f"ERROR: {exc}")
        return 1

    handler = partial(http.server.SimpleHTTPRequestHandler, directory=str(SITE))
    httpd = http.server.ThreadingHTTPServer((host, port), handler)

    url = f"http://{host}:{port}/"
    print(f"Serving {SITE}")
    print(f"Local: {url}")
    print("Press Ctrl+C to stop.")
    print("")
    print("  ATENÇÃO: use esta URL — NÃO abra calculadorasdeenfermagem.com.br para testar o build local.")

    should_open = not args.no_open
    if should_open:
        open_browser(url)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        httpd.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
