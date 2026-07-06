#!/usr/bin/env python3
"""Reconstrói os blocos hreflang de todo o site com base nos arquivos que existem no disco.

Problema que corrige (ver PENDENCIAS_I18N.md — "Achado técnico adicional"):
  1. Páginas raiz (pt-BR) declaravam só 3 alternates (pt-BR/es-419/x-default) —
     reciprocidade quebrada com os demais idiomas gerados.
  2. Páginas de artigo tinham o bloco fantasma antigo (~19 idiomas, sem x-default,
     incluindo idiomas cujas pastas não existem).
  3. Códigos inconsistentes entre páginas do mesmo cluster (es vs es-419).

Estratégia: para cada página que possui ao menos uma versão de idioma gerada,
remove TODAS as tags <link rel="alternate" hreflang=...> (raiz e subpastas) e
injeta um bloco único e idêntico em todo o cluster: pt-BR + idiomas existentes
no disco + x-default. Re-executável: rode de novo após restaurar idiomas ausentes.

Uso:  python fix_hreflang.py [--dry-run]
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "reference-website"
BASE = "https://www.calculadorasdeenfermagem.com.br"

# dir -> código hreflang (lista autoritativa: site_locales.py do NKOS)
LANG_CODES = {
    "en": "en", "es": "es-419", "fr": "fr", "de": "de", "it": "it",
    "zh": "zh-CN", "ja": "ja", "ar": "ar", "hi": "hi-IN", "ru": "ru-RU",
    "ko": "ko-KR", "tr": "tr-TR", "pl": "pl-PL", "nl": "nl-NL", "sv": "sv-SE",
    "no": "no-NO", "da": "da-DK", "fi": "fi-FI", "cs": "cs-CZ", "hu": "hu-HU",
    "ro": "ro-RO", "bg": "bg-BG", "hr": "hr-HR", "sr": "sr-RS", "sl": "sl-SI",
    "uk": "uk-UA", "vi": "vi-VN", "th": "th-TH", "id": "id-ID",
}

HREFLANG_TAG = re.compile(
    r'[ \t]*<link\b(?=[^>]*rel=["\']alternate["\'])(?=[^>]*hreflang=)[^>]*/?>[ \t]*\r?\n?',
    re.I,
)
CANONICAL_TAG = re.compile(
    r'[ \t]*<link\b(?=[^>]*rel=["\']canonical["\'])[^>]*/?>[ \t]*\r?\n?', re.I
)
HEAD_CLOSE = re.compile(r"</head>", re.I)


def build_block(page_name: str, lang_dirs: list[str]) -> str:
    lines = [f'<link rel="alternate" hreflang="pt-BR" href="{BASE}/{page_name}" />']
    for d in lang_dirs:
        lines.append(
            f'<link rel="alternate" hreflang="{LANG_CODES[d]}" href="{BASE}/{d}/{page_name}" />'
        )
    lines.append(f'<link rel="alternate" hreflang="x-default" href="{BASE}/{page_name}" />')
    return "\n".join(lines) + "\n"


def rewrite(path: Path, block: str, dry: bool) -> tuple[int, str]:
    """Retorna (tags removidas, modo de inserção)."""
    html = path.read_text(encoding="utf-8")
    html_wo, removed = HREFLANG_TAG.subn("", html)

    m = CANONICAL_TAG.search(html_wo)
    if m:
        pos = m.end()
        mode = "canonical"
    else:
        m = HEAD_CLOSE.search(html_wo)
        if not m:
            return removed, "SEM_HEAD"
        pos = m.start()
        mode = "head"

    new_html = html_wo[:pos] + block + html_wo[pos:]
    if new_html != html and not dry:
        path.write_text(new_html, encoding="utf-8", newline="")
    return removed, mode


def main() -> None:
    dry = "--dry-run" in sys.argv
    lang_dirs = sorted(d.name for d in ROOT.iterdir() if d.is_dir() and d.name in LANG_CODES)
    print(f"Idiomas encontrados no disco ({len(lang_dirs)}): {', '.join(lang_dirs)}")
    missing = sorted(set(LANG_CODES) - set(lang_dirs))
    if missing:
        print(f"AVISO — idiomas da lista autoritativa sem pasta (ignorados): {', '.join(missing)}")

    stats = {"pages": 0, "files": 0, "tags_removed": 0, "no_canonical": [], "skipped_root": []}

    for root_page in sorted(ROOT.glob("*.html")):
        name = root_page.name
        present = [d for d in lang_dirs if (ROOT / d / name).is_file()]
        if not present:  # templates/partials/admin — sem versões de idioma
            stats["skipped_root"].append(name)
            continue

        block = build_block(name, present)
        stats["pages"] += 1
        for f in [root_page] + [ROOT / d / name for d in present]:
            removed, mode = rewrite(f, block, dry)
            stats["files"] += 1
            stats["tags_removed"] += removed
            if mode != "canonical":
                stats["no_canonical"].append(f"{f.relative_to(ROOT)} ({mode})")

    print(f"\n{'[DRY-RUN] ' if dry else ''}Páginas (clusters): {stats['pages']}")
    print(f"Arquivos reescritos: {stats['files']}")
    print(f"Tags hreflang antigas removidas: {stats['tags_removed']}")
    print(f"Ignorados na raiz (sem versões de idioma): {len(stats['skipped_root'])} -> "
          f"{', '.join(stats['skipped_root'])}")
    if stats["no_canonical"]:
        print(f"\nSem canonical (bloco inserido antes de </head>): {len(stats['no_canonical'])}")
        for x in stats["no_canonical"][:20]:
            print(f"  - {x}")


if __name__ == "__main__":
    main()
