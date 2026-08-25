"""First-party default Open Graph card. Does not copy Drive's 151 unpublished cards.

1200×630 PNG, navy brand tokens from Drive familias.json COMPARE (#1A3E74 → #122C53).
Pillow is not a dependency; the file is a solid two-band PNG via stdlib zlib.
"""

from __future__ import annotations

import struct
import zlib
from pathlib import Path

from .paths import ASSETS_DIR

OG_WIDTH = 1200
OG_HEIGHT = 630
NAVY = (0x1A, 0x3E, 0x74)
NAVY_DEEP = (0x12, 0x2C, 0x53)
BAND = 110


def _chunk(tag: bytes, data: bytes) -> bytes:
    return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)


def write_default_og_png(path: Path | None = None) -> Path:
    dest = path or (ASSETS_DIR / "img" / "og-default.png")
    dest.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    split = OG_HEIGHT - BAND
    for y in range(OG_HEIGHT):
        color = NAVY if y < split else NAVY_DEEP
        rows.append(b"\x00" + bytes(color) * OG_WIDTH)
    raw = b"".join(rows)
    ihdr = struct.pack(">IIBBBBB", OG_WIDTH, OG_HEIGHT, 8, 2, 0, 0, 0)
    dest.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        + _chunk(b"IHDR", ihdr)
        + _chunk(b"IDAT", zlib.compress(raw, 9))
        + _chunk(b"IEND", b"")
    )
    return dest
