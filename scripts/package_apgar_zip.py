#!/usr/bin/env python3
"""Empacota a calculadora Apgar completa em ZIP portável para edição externa."""
from __future__ import annotations

import shutil
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DELIVERY = ROOT / "NIFS" / "DELIVERY"
STAGING = ROOT / "artifacts" / "apgar-export"
ZIP_OUT = Path("/opt/cursor/artifacts/apgar-completo.zip")

JS_FILES = [
    "global-scripts.js",
    "mega-menu.js",
    "i18n-loader.js",
    "lang-selector.js",
    "site-widgets.js",
    "nurse-palm.js",
    "cognitive-ui.js",
    "tool-cko-loader.js",
    "tool-profile-engine.js",
    "calc-engine-v2.js",
    "tool-medication-links.js",
    "partials-loader.js",
]

JS_DATA = [
    "modules/data/apgar-cko.json",
    "modules/data/apgar-edges.json",
    "modules/data/apgar-medications.json",
    "modules/schemas/cko-v1.schema.json",
]

PARTIALS = [
    "header.html",
    "footer.html",
    "accessibility-toolbar.html",
    "cookie-system.html",
]

SCRIPTS = [
    "build_apgar_cko.py",
    "patch_apgar_cko.py",
    "reorder_apgar_panels.py",
    "integrate_clinical_engine.py",
    "unify_clinical_engine.py",
    "fix_estudante_icons.py",
    "complete_preview_apgar.py",
    "fix_apgar_profiles.py",
    "package_apgar_zip.py",
    "integrate_relatorio_fiel.py",
    "sync_brand_assets.py",
]

REF_DATA = [
    "NIFS/reference-datasets/ontology/apgar_edges.json",
    "NIFS/reference-datasets/clinical/calculator_definitions.json",
]

I18N_FILES = ["pt-BR.json", "en.json", "es.json"]


def copy_file(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst, follow_symlinks=True)


def copy_tree_resolved(src: Path, dst: Path) -> None:
    if not src.exists():
        return
    if src.is_symlink():
        target = src.resolve()
        if target.is_dir():
            copy_tree_resolved(target, dst)
        else:
            copy_file(target, dst)
        return
    if src.is_file():
        copy_file(src, dst)
        return
    for item in src.iterdir():
        copy_tree_resolved(item, dst / item.name)


def write_readme(target: Path) -> None:
    built = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    text = f"""# Apgar — pacote completo para edição externa

Gerado em: {built}
Branch de origem: cursor/cko-profiles-pdf-c848

## Visualizar localmente

```bash
cd apgar-export
python3 -m http.server 8765
```

Abra no navegador:
- http://localhost:8765/preview_apgar.html  (entrada principal de desenvolvimento)
- http://localhost:8765/apgar.html
- http://localhost:8765/html/apgar.html     (caminho alternativo com base `../`)

## Estrutura

| Pasta/arquivo | Conteúdo |
|---------------|----------|
| `preview_apgar.html`, `apgar.html` | Página completa com perfis CKO, motor clínico e PDF |
| `html/apgar.html` | Cópia para rota `/html/` (symlinks resolvidos em `css/`, `js/`, `partials/`) |
| `css/` | `site-styles.css`, `print-template.css` |
| `js/` | Motor de cálculo, CKO, Nurse-PaLM, partials-loader |
| `js/modules/data/` | `apgar-cko.json`, `apgar-edges.json`, `apgar-medications.json` |
| `partials/` | Header, footer, acessibilidade, cookies |
| `scripts/` | Scripts Python de build e patch |
| `reference-datasets/` | Fontes para `build_apgar_cko.py` |
| `i18n/` | Dicionários básicos (pt-BR, en, es) |

## Perfis (ordem das abas)

Padrão → Urgência → Gestor → Estudante → Acadêmico

Conteúdo alimentado por `js/modules/data/apgar-cko.json` via `tool-cko-loader.js` e `tool-profile-engine.js`.

## Motor clínico

Após calcular, o fluxo único `#calcClinicalFlow` exibe:
NANDA·NIC·NOC → Nurse-PaLM → Plano/Monitoramento/Segurança/Medicamentos → Evidência & Pérolas → Recursos.

## Sincronizar CKO a partir dos datasets

```bash
python3 scripts/build_apgar_cko.py
```

## PDF / Relatório fiel

Template reutilizável: `partials/relatorio-fiel.html` + `css/print-template.css`

- Pré-visualização editável: `relatorio_fiel.html`
- Preenchimento automático via `calc-engine-v2.js` → `populatePrintReport()`
- Botão Imprimir gera `relatorio.pdf` (via `window.print()`)

Para integrar em outra ferramenta: use `<div id="printTemplateMount"></div>` e carregue via `partials-loader.js`.

## Notas

- Fontes e Font Awesome carregam de CDN (requer internet).
- Imagens do header (`images/logotipo_website.webp`) podem não estar incluídas; adicione em `images/` se necessário.
- `#tool-config` embutido no HTML contém a definição da calculadora; o CKO complementa com conteúdo por perfil.
"""
    target.write_text(text, encoding="utf-8")


def stage() -> None:
    if STAGING.exists():
        shutil.rmtree(STAGING)
    STAGING.mkdir(parents=True)

    for name in ("preview_apgar.html", "apgar.html"):
        copy_file(DELIVERY / name, STAGING / name)

    root_preview = ROOT / "preview_apgar.html"
    if root_preview.is_file():
        copy_file(root_preview, STAGING / "preview_apgar_raiz.html")

    copy_file(DELIVERY / "html" / "apgar.html", STAGING / "html" / "apgar.html")

    for css in ("site-styles.css", "print-template.css"):
        copy_file(DELIVERY / "css" / css, STAGING / "css" / css)

    for rel in JS_FILES:
        copy_file(DELIVERY / "js" / rel, STAGING / "js" / rel)
    for rel in JS_DATA:
        copy_file(DELIVERY / "js" / rel, STAGING / "js" / rel)

    for name in PARTIALS:
        copy_file(DELIVERY / "partials" / name, STAGING / "partials" / name)
    copy_file(DELIVERY / "partials" / "relatorio-fiel.html", STAGING / "partials" / "relatorio-fiel.html")
    copy_file(DELIVERY / "relatorio_fiel.html", STAGING / "relatorio_fiel.html")

    for name in ("favicon-16x16.png", "favicon-32x32.png", "favicon.ico"):
        copy_file(DELIVERY / name, STAGING / name)
        copy_file(DELIVERY / name, STAGING / "html" / name)

    img_src = DELIVERY / "images"
    if img_src.is_dir():
        for item in img_src.iterdir():
            if item.is_file():
                copy_file(item, STAGING / "images" / item.name)
                copy_file(item, STAGING / "html" / "images" / item.name)

    html_sub = STAGING / "html"
    for sub in ("css", "js", "partials"):
        src = DELIVERY / "html" / sub
        dst = html_sub / sub
        if src.is_symlink():
            copy_tree_resolved(src.resolve(), dst)
        elif src.is_dir():
            copy_tree_resolved(src, dst)
        else:
            copy_tree_resolved(DELIVERY / sub, dst)

    for name in SCRIPTS:
        src = ROOT / "scripts" / name
        if src.is_file():
            copy_file(src, STAGING / "scripts" / name)

    for rel in REF_DATA:
        src = ROOT / rel
        if src.is_file():
            copy_file(src, STAGING / "reference-datasets" / Path(rel).name)

    i18n_src = ROOT / "reference-website" / "i18n"
    for name in I18N_FILES:
        src = i18n_src / name
        if src.is_file():
            copy_file(src, STAGING / "i18n" / name)

    backup = ROOT / ".apgar_original.html"
    if backup.is_file():
        copy_file(backup, STAGING / "backup" / ".apgar_original.html")

    write_readme(STAGING / "README.md")


def create_zip() -> Path:
    ZIP_OUT.parent.mkdir(parents=True, exist_ok=True)
    if ZIP_OUT.exists():
        ZIP_OUT.unlink()

    with zipfile.ZipFile(ZIP_OUT, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(STAGING.rglob("*")):
            if path.is_file():
                arc = Path("apgar-export") / path.relative_to(STAGING)
                zf.write(path, arcname=str(arc))

    return ZIP_OUT


def main() -> None:
    stage()
    out = create_zip()
    size_kb = out.stat().st_size / 1024
    print(f"Pacote: {STAGING}")
    print(f"ZIP: {out} ({size_kb:.1f} KB)")


if __name__ == "__main__":
    main()
