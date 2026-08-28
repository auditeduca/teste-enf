"""Caminhos candidatos para arquivos .env (workspace + legado Windows/WSL)."""
from __future__ import annotations

import os
from pathlib import Path

# Legado Windows e espelho WSL (/mnt/c/...)
LEGACY_ENV_PATHS: tuple[Path, ...] = (
    Path("C:/Github/CALENF-NKD/.env"),
    Path("C:/Users/leivi/Downloads/nkos-site-i18n-completo-v1/.env"),
    Path("/mnt/c/Users/leivi/Downloads/nkos-site-i18n-completo-v1/.env"),
)


def env_candidates(
    workspace: Path,
    *,
    nifs: Path | None = None,
    include_home: bool = True,
) -> list[Path]:
    """Lista ordenada de .env a tentar (CALENF_ENV_FILE tem prioridade)."""
    paths: list[Path] = []
    custom = os.environ.get("CALENF_ENV_FILE", "").strip()
    if custom:
        paths.append(Path(custom))
    paths.append(workspace / ".env")
    if nifs is not None:
        paths.append(nifs / ".env")
    paths.extend(LEGACY_ENV_PATHS)
    if include_home:
        paths.append(Path.home() / ".calenf" / ".env")
    return paths
