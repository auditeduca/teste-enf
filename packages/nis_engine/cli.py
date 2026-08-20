"""Command-line interface: validate, build, serve."""

from __future__ import annotations

import argparse
import http.server
import os
import socketserver
import sys
from functools import partial

from .generate import build
from .paths import WEB_DIR
from .validate import validate_tools_dir


def cmd_validate(_: argparse.Namespace) -> int:
    failures = validate_tools_dir()
    if not failures:
        print("ok: all tools valid")
        return 0
    for name, errors in failures.items():
        print(f"FAIL {name}")
        for error in errors:
            print(f"  - {error}")
    return 1


def cmd_build(_: argparse.Namespace) -> int:
    status = cmd_validate(_)
    if status != 0:
        return status
    written = build()
    for path in written:
        try:
            print(f"wrote {path.relative_to(WEB_DIR.parent.parent)}")
        except ValueError:
            print(f"wrote {path}")
    print(f"built {len(written)} file(s)")
    return 0


def cmd_serve(args: argparse.Namespace) -> int:
    status = cmd_build(args)
    if status != 0:
        return status
    handler = partial(http.server.SimpleHTTPRequestHandler, directory=str(WEB_DIR))
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("0.0.0.0", args.port), handler) as httpd:
        print(f"serving {WEB_DIR} on http://127.0.0.1:{args.port}")
        httpd.serve_forever()
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="nis", description="NIS greenfield toolchain")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("validate").set_defaults(func=cmd_validate)
    sub.add_parser("build").set_defaults(func=cmd_build)
    serve = sub.add_parser("serve")
    serve.add_argument("--port", type=int, default=int(os.environ.get("PORT", "8081")))
    serve.set_defaults(func=cmd_serve)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
