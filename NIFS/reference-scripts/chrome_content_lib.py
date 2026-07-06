"""Load chrome navigation and shell copy from datasets/content/chrome/*.json."""

from __future__ import annotations

import json
from functools import lru_cache

from content_paths import content_path

NAV_PATH = content_path("chrome_navigation")
SHELL_PATH = content_path("chrome_shell")


@lru_cache(maxsize=1)
def get_navigation() -> dict:
    return json.loads(NAV_PATH.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def get_shell() -> dict:
    return json.loads(SHELL_PATH.read_text(encoding="utf-8"))


def reload_chrome_content() -> None:
    """Clear caches after JSON edits in long-running processes."""
    get_navigation.cache_clear()
    get_shell.cache_clear()
