"""Review scope limits and skip rules — avoids sending huge trees (e.g. node_modules)."""
from __future__ import annotations

from pathlib import Path

# Directories never traversed (segment match anywhere in path)
SKIP_DIR_NAMES: frozenset[str] = frozenset({
    "node_modules",
    "nodes",  # vendor / generated node trees
    ".git",
    "__pycache__",
    ".venv",
    "venv",
    ".shards",
    "dist",
    "build",
    "website",
    ".cursor",
    "archive",
    ".vite",
    "coverage",
    ".pytest_cache",
    "platform/node_modules",
})

# Relative path prefixes (POSIX) — large generated datasets
SKIP_PATH_PREFIXES: tuple[str, ...] = (
    "datasets/content/i18n/translations.shards/",
    "datasets/content/nkos/",
    "datasets/master/",
    "platform/node_modules/",
)

# Extensions eligible for full-text review (small files only)
REVIEW_EXTENSIONS: frozenset[str] = frozenset({
    ".py", ".js", ".jsx", ".ts", ".tsx", ".md", ".css", ".html",
})

# Hard limits
MAX_FILE_BYTES = 48_000
MAX_FILE_LINES = 800
MAX_FILES_TO_REVIEW = 30
MAX_BATCH_CHARS = 14_000
MAX_PATHS_DEFAULT = ("scripts", "platform/src", "docs")

# Default DeepSeek
DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"
DEFAULT_DEEPSEEK_MODEL = "deepseek-v4-flash"


def is_under_skip_prefix(rel_posix: str) -> str | None:
    for prefix in SKIP_PATH_PREFIXES:
        if rel_posix.startswith(prefix):
            return f"prefixo excluído: {prefix}"
    return None


def has_skip_dir_segment(rel: Path) -> str | None:
    for part in rel.parts:
        if part in SKIP_DIR_NAMES:
            return f"pasta excluída: {part}/"
    return None
