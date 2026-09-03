#!/usr/bin/env python3
"""Create every documented pendency from the PDF universe and the directory audit.

Does not write into Drive copies:
  cko-controlled/public/drive/**
  cko-controlled/control-plane/drive-html/**
Creating a pendency does not close B9 or assert production release.
"""
from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
PUB = ROOT / "public"
DATA = PUB / "data"
DRIVE_DIRS = (
    PUB / "drive",
    ROOT / "control-plane" / "drive-html",
)
REF = REPO / "reference-website"
WAVE2 = PUB / "institucional" / "CKO-PAGE-INSTITUTIONAL-WAVE2-v0.2.0"
WAVE2_PAGES = {
    "index.html",
    "missao.html",
    "objetivo.html",
    "ecossistema.html",
    "acessibilidade.html",
    "tecnologiaverde.html",
    "privacidade.html",
    "politica-editorial.html",
    "notificacoes-legais.html",
    "fale.html",
    "forum-enfermagem.html",
    "mapa-do-site.html",
}

SLUG_ALIASES = [
    ("escala-de-braden.html", "braden.html"),
    ("escala-de-glasgow.html", "glasgow.html"),
    ("escala-de-morse.html", "morse.html"),
]


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def assert_not_drive(path: Path) -> None:
    resolved = path.resolve()
    for drive in DRIVE_DIRS:
        try:
            resolved.relative_to(drive.resolve())
        except ValueError:
            continue
        raise SystemExit(f"refusing to write Drive copy: {path}")


def pendency(
    items: list[dict],
    *,
    pid: str,
    source: str,
    kind: str,
    status: str,
    summary: str,
    block: str | None = None,
    count: int | None = None,
    path: str | None = None,
    next_action: str | None = None,
    mutate_drive: bool = False,
) -> None:
    if mutate_drive:
        raise SystemExit("pendencies must not mutate Drive")
    item = {
        "id": pid,
        "source": source,
        "kind": kind,
        "status": status,
        "summary": summary,
        "block": block,
        "count": count,
        "path": path,
        "next_action": next_action or "KEEP_HOLD_FAIL_CLOSED",
        "release": "HOLD / NOT_RELEASED",
        "mutate_drive": False,
        "closes_b9": False,
    }
    items.append({k: v for k, v in item.items() if v is not None})


def freeze_drive() -> list[dict]:
    rows = []
    for root in DRIVE_DIRS:
        if not root.is_dir():
            continue
        for path in sorted(root.rglob("*")):
            if path.is_file():
                rows.append(
                    {
                        "path": str(path.relative_to(ROOT)).replace("\\", "/"),
                        "sha256": sha256_file(path),
                        "bytes": path.stat().st_size,
                    }
                )
    return rows


def from_pdf(universe: dict, items: list[dict]) -> None:
    counts = universe["residual_uncertainty"]["open_counts"]
    pendency(
        items,
        pid="PEND-PDF-HOLDS-BUCKET",
        source="pdf",
        kind="bucket",
        status="HOLD",
        summary="211 active holds documented in OV-CKO-GLOBAL-FINAL-AUD8L-1.0.0",
        count=counts["holds"],
        next_action="KEEP_SCOPED_HOLDS_EXPLICIT",
    )
    pendency(
        items,
        pid="PEND-PDF-FINDINGS-BUCKET",
        source="pdf",
        kind="bucket",
        status="OPEN",
        summary="313 open findings remain in the finding cycle",
        count=counts["findings_open"],
        next_action="CYCLE_FINDING_ROOTCAUSE_LEARNING_REPERF_RECERT",
    )
    pendency(
        items,
        pid="PEND-PDF-REPERF-BUCKET",
        source="pdf",
        kind="bucket",
        status="PENDING_REPERFORMANCE",
        summary="201 learning records in PENDING_REPERFORMANCE",
        block="B7",
        count=counts["pending_reperformance"],
        next_action="REPERFORMANCE_BY_OWNERSHIP",
    )
    pendency(
        items,
        pid="PEND-PDF-OUTBOX-BUCKET",
        source="pdf",
        kind="bucket",
        status="PENDING_NOT_ACK",
        summary="296 outbox events PENDING; PENDING is not ACK",
        count=counts["outbox_pending"],
        next_action="DO_NOT_TREAT_PENDING_AS_ACK",
    )
    pendency(
        items,
        pid="PEND-PDF-RIGHTS-BUCKET",
        source="pdf",
        kind="bucket",
        status="HOLD",
        summary="13 RIGHTS_PROVENANCE holds; do not publish without rights chain",
        count=counts["rights_holds"],
        next_action="CLOSE_RIGHTS_CHAIN_BEFORE_PUBLISH",
    )
    pendency(
        items,
        pid="PEND-PDF-UNRESOLVED-ID-BUCKET",
        source="pdf",
        kind="bucket",
        status="HOLD",
        summary="12 unresolved identities in B3",
        block="B3",
        count=counts["unresolved_identities"],
        next_action="SUCCESSOR_VERSION_WITHOUT_OVERWRITING_HISTORY",
    )
    for block in universe["blocks"]:
        pendency(
            items,
            pid=f"PEND-BLOCK-{block['id']}",
            source="pdf",
            kind="block-pending",
            status=block.get("release") or block.get("operational") or "HOLD",
            summary=block["pending"],
            block=block["id"],
        )
        for hold in block.get("holds") or []:
            hid = str(hold).replace(":", "-").replace("/", "-").replace(" ", "-")
            pendency(
                items,
                pid=f"PEND-HOLD-{block['id']}-{hid}",
                source="pdf",
                kind="hold",
                status="HOLD",
                summary=str(hold),
                block=block["id"],
            )
    for pr in universe["priorities"]:
        pendency(
            items,
            pid=f"PEND-{pr['id']}",
            source="pdf",
            kind="priority",
            status=pr["priority"],
            summary=f"{pr['domain']}: {pr['evidence']}",
            next_action=pr["effect"],
        )
    for unk in universe["unknown_universe"]:
        pendency(
            items,
            pid=f"PEND-{unk['id']}",
            source="pdf",
            kind="unknown",
            status="EXPLICIT_UNKNOWN",
            summary=unk["statement"],
            next_action="KEEP_UNKNOWN_EXPLICIT",
        )


def from_directory(audit: dict, items: list[dict], created: list[str]) -> None:
    html = audit["html_pendentes"]
    for name in html["links_quebrados_referenciados_no_index"]:
        exists = (PUB / name).is_file()
        pendency(
            items,
            pid=f"PEND-DIR-PAGE-{Path(name).stem}",
            source="directory",
            kind="site-page",
            status="CREATED_IN_RUNTIME_HOLD" if exists else "MISSING",
            summary=f"Index-referenced page {name}",
            path=name,
            next_action="KEEP_PAGE_IN_REPO_WITHOUT_DRIVE_MUTATION",
        )
    for row in html["links_com_alias_existente_corrigir_no_index"]:
        pendency(
            items,
            pid=f"PEND-DIR-ALIAS-{Path(row['link_index']).stem}",
            source="directory",
            kind="alias",
            status="CREATED_IN_RUNTIME_HOLD",
            summary=f"{row['link_index']} aliases {row['arquivo_existente']}",
            path=row["link_index"],
        )
    for row in audit["json_pendentes"]["criar_json_para_html"]:
        pendency(
            items,
            pid=f"PEND-DIR-SLUG-{row['slug_html']}",
            source="directory",
            kind="slug-alias",
            status="CREATED_IN_RUNTIME_HOLD",
            summary=f"{row['html']} slug vs {row['json_existente']}",
            path=f"escala-de-{row['slug_html']}.html" if row["slug_html"] != "braden" else "escala-de-braden.html",
        )
    for row in audit["json_pendentes"]["html_com_tool_config_json_invalido"]:
        pendency(
            items,
            pid="PEND-DIR-ASA-TOOL-CONFIG",
            source="directory",
            kind="parse-hold",
            status="HOLD",
            summary=row["erro"],
            path=row["html"],
            next_action="REGENERATE_FROM_data/tools/asa.json_WITHOUT_DRIVE",
        )
    for lang in audit["traducoes_pendentes"]["idiomas_planejados_sem_arquivo_json"]:
        exists = (PUB / "i18n" / f"{lang}.json").is_file()
        pendency(
            items,
            pid=f"PEND-DIR-I18N-{lang}",
            source="directory",
            kind="i18n",
            status="CREATED_IN_RUNTIME_HOLD" if exists else "HOLD_TRANSLATION_REQUIRED",
            summary=f"i18n/{lang}.json documented as planned",
            path=f"i18n/{lang}.json",
            next_action="DO_NOT_ACTIVATE_SELECTOR_BEFORE_HUMAN_REVIEW",
        )
    other = audit["outras_pendencias"]
    pendency(
        items,
        pid="PEND-DIR-SITEMAP",
        source="directory",
        kind="asset",
        status="CREATED_IN_RUNTIME_HOLD" if (PUB / "sitemap.xml").is_file() else "MISSING",
        summary="sitemap.xml",
        path="sitemap.xml",
    )
    for rel in other.get("fonts_woff2_ausentes") or []:
        pendency(
            items,
            pid=f"PEND-DIR-FONT-{rel.strip('/').replace('/', '-')}",
            source="directory",
            kind="asset",
            status="CREATED_IN_RUNTIME_HOLD",
            summary=rel,
            path=rel.lstrip("/"),
        )
    for rel in other.get("preload_css_404") or []:
        pendency(
            items,
            pid=f"PEND-DIR-CSS-{rel.strip('/').replace('/', '-')}",
            source="directory",
            kind="asset",
            status="CREATED_IN_RUNTIME_HOLD",
            summary=rel,
            path=rel.lstrip("/"),
        )
    pendency(
        items,
        pid="PEND-DIR-WEBMANIFEST",
        source="directory",
        kind="asset",
        status="CREATED_IN_RUNTIME_HOLD" if (PUB / "site.webmanifest").is_file() else "HOLD",
        summary="site.webmanifest",
        path="site.webmanifest",
    )
    _ = created


def from_wave2(items: list[dict]) -> None:
    vert = load_json(WAVE2 / "vertical_page_locale_matrix_360.json")
    horiz = load_json(WAVE2 / "horizontal_H00_H19_scope_matrix.json")
    for row in vert["rows"]:
        ready = row.get("publication_ready") is True
        pendency(
            items,
            pid=f"PEND-W2-{row['page_id']}-{row['locale']}",
            source="wave2",
            kind="locale-cell",
            status="PASS_STATIC_HOLD_RELEASE" if ready else row["status"],
            summary=f"{row['page_id']} {row['locale']} {row['status']}",
            path=row.get("target_route"),
            next_action=row.get("next_action"),
        )
    for row in horiz["rows"]:
        pendency(
            items,
            pid=f"PEND-W2-{row['h_id']}",
            source="wave2",
            kind="horizontal-layer",
            status=row["status"],
            summary=f"{row['h_id']} {row['layer']}: {row['evidence_summary']}",
        )
    pendency(
        items,
        pid="PEND-W2-A11Y-EMPIRICAL",
        source="wave2",
        kind="hold",
        status="HOLD",
        summary="Empirical AT/human accessibility validation remains HOLD",
        block="B6.3",
    )
    pendency(
        items,
        pid="PEND-W2-FORUM-CRITICAL",
        source="wave2",
        kind="hold",
        status="HOLD_CRITICAL_SECURITY_PRIVACY",
        summary="Forum production surface remains CRITICAL HOLD",
        path="forum-enfermagem.html",
    )


def from_drive_catalog(items: list[dict]) -> None:
    catalog = load_json(PUB / "drive" / "catalog.json")
    for row in catalog.get("items") or []:
        if row.get("deployed"):
            continue
        pendency(
            items,
            pid=f"PEND-DRIVE-KEEP-{row['id']}",
            source="drive-catalog",
            kind="drive-source-unaltered",
            status="HOLD_SOURCE_REMAINS_ON_DRIVE",
            summary=row.get("reason") or f"{row['name']} stays on Drive; do not mutate",
            path=row.get("path"),
            next_action="DO_NOT_ALTER_DRIVE_FILE",
        )


def redirect_html(target: str) -> str:
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8"/>
<meta name="robots" content="noindex, nofollow"/>
<meta http-equiv="refresh" content="0;url={target}"/>
<link rel="canonical" href="{target}"/>
<title>Redirect · HOLD / NOT_RELEASED</title>
</head>
<body>
<main>
<p>Alias documentado. Continuar para <a href="{target}">{target}</a>.</p>
<p>Estado: HOLD / NOT_RELEASED. Drive não foi alterado.</p>
</main>
</body>
</html>
"""


def materialize_directory(audit: dict) -> list[str]:
    created: list[str] = []
    if not REF.is_dir():
        return created

    def copy_from_ref(rel: str) -> None:
        src = REF / rel
        dest = PUB / rel
        if not src.exists():
            return
        assert_not_drive(dest)
        dest.parent.mkdir(parents=True, exist_ok=True)
        if src.is_dir():
            shutil.copytree(src, dest, dirs_exist_ok=True)
        else:
            shutil.copy2(src, dest)
        created.append(rel)

    for name in audit["html_pendentes"]["links_quebrados_referenciados_no_index"]:
        if name in WAVE2_PAGES:
            continue
        copy_from_ref(name)
        stem = Path(name).stem
        tool_json = REF / "data" / "tools" / f"{stem}.json"
        if tool_json.is_file():
            copy_from_ref(f"data/tools/{stem}.json")

    for row in audit["html_pendentes"]["links_com_alias_existente_corrigir_no_index"]:
        if name_exists := (PUB / row["arquivo_existente"]).is_file():
            _ = name_exists
        copy_from_ref(row["arquivo_existente"])
        dest = PUB / row["link_index"]
        if not dest.exists() and (PUB / row["arquivo_existente"]).is_file():
            assert_not_drive(dest)
            dest.write_text(redirect_html(row["arquivo_existente"]), encoding="utf-8")
            created.append(row["link_index"])

    for alias, target in SLUG_ALIASES:
        dest = PUB / alias
        if not dest.exists() and (PUB / target).is_file():
            assert_not_drive(dest)
            dest.write_text(redirect_html(target), encoding="utf-8")
            created.append(alias)

    copy_from_ref("sitemap.xml")
    if (REF / "i18n").is_dir():
        for src in (REF / "i18n").glob("*.json"):
            if src.name in {"validation_report.json", "manifest.json", "country-locale-map.json"}:
                copy_from_ref(f"i18n/{src.name}")
                continue
            copy_from_ref(f"i18n/{src.name}")

    if (REF / "biblioteca").is_dir():
        copy_from_ref("biblioteca")
    for rel in (
        "public/output.css",
        "global-styles.css",
        "css/fontawesome.min.css",
        "site.webmanifest",
        "js/calc-engine.js",
        "js/calc-engine-v2.js",
        "js/ce-calculadora-padrao.js",
        "js/modules/data/biblioteca.json",
        "js/modules/catalog-page.js",
        "aldrete.html",
        "imc.html",
        "gotejamento.html",
        "braden.html",
        "news.html",
        "gasometria.html",
        "biblioteca.html",
        "downloads.html",
        "biblioteca-provas.html",
        "biblioteca-cirurgica.html",
        "biblioteca-curativo.html",
        "biblioteca-seringa.html",
        "biblioteca-carinho-de-emergencia.html",
    ):
        copy_from_ref(rel)

    fonts_src = REF / "fonts"
    if fonts_src.is_dir():
        for font in ("inter/inter-regular.woff2", "inter/inter-600.woff2", "nunito/nunito-regular.woff2", "nunito/nunito-700.woff2"):
            copy_from_ref(f"fonts/{font}")

    manifest = PUB / "site.webmanifest"
    if not manifest.exists():
        assert_not_drive(manifest)
        manifest.write_text(
            json.dumps(
                {
                    "name": "Calculadoras de Enfermagem",
                    "short_name": "CalEnf",
                    "start_url": "/",
                    "display": "browser",
                    "background_color": "#F8FAFC",
                    "theme_color": "#1A3E74",
                    "release": "HOLD_NOT_RELEASED",
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        created.append("site.webmanifest")
    return created


def validate(items: list[dict], universe: dict, drive_rows: list[dict]) -> None:
    counts = universe["residual_uncertainty"]["open_counts"]
    by_id = {i["id"]: i for i in items}
    required = [
        "PEND-PDF-HOLDS-BUCKET",
        "PEND-PDF-FINDINGS-BUCKET",
        "PEND-PDF-REPERF-BUCKET",
        "PEND-PDF-OUTBOX-BUCKET",
        "PEND-PDF-RIGHTS-BUCKET",
        "PEND-BLOCK-B9",
        "PEND-BLOCK-B10",
        "PEND-W2-FORUM-CRITICAL",
        "PEND-DIR-SITEMAP",
    ]
    missing = [r for r in required if r not in by_id]
    if missing:
        raise SystemExit("missing required pendencies: " + ",".join(missing))
    if by_id["PEND-PDF-HOLDS-BUCKET"]["count"] != counts["holds"]:
        raise SystemExit("holds bucket mismatch")
    if by_id["PEND-PDF-FINDINGS-BUCKET"]["count"] != counts["findings_open"]:
        raise SystemExit("findings bucket mismatch")
    if by_id["PEND-PDF-REPERF-BUCKET"]["count"] != counts["pending_reperformance"]:
        raise SystemExit("reperf bucket mismatch")
    if by_id["PEND-PDF-OUTBOX-BUCKET"]["count"] != counts["outbox_pending"]:
        raise SystemExit("outbox bucket mismatch")
    if by_id["PEND-PDF-RIGHTS-BUCKET"]["count"] != counts["rights_holds"]:
        raise SystemExit("rights bucket mismatch")
    if any(i.get("mutate_drive") or i.get("closes_b9") for i in items):
        raise SystemExit("pendency illegally closes B9 or mutates Drive")
    if len(drive_rows) < 1:
        raise SystemExit("drive freeze empty")
    locale_n = sum(1 for i in items if i["kind"] == "locale-cell")
    if locale_n != 360:
        raise SystemExit(f"expected 360 locale cells, got {locale_n}")


def main() -> None:
    universe = load_json(DATA / "universe.json")
    audit = load_json(REF / "relatorio-pendencias.json")
    before = freeze_drive()
    created = materialize_directory(audit)
    after = freeze_drive()
    if before != after:
        raise SystemExit("Drive copies changed; aborting")

    items: list[dict] = []
    from_pdf(universe, items)
    from_directory(audit, items, created)
    from_wave2(items)
    from_drive_catalog(items)
    # stable unique ids
    uniq = {}
    for item in items:
        uniq[item["id"]] = item
    items = [uniq[k] for k in sorted(uniq)]
    validate(items, universe, after)

    payload = {
        "id": "CKO-PENDENCIES-1.0.0",
        "root": "policy-as-code",
        "release": "HOLD / NOT_RELEASED",
        "mutate_drive": False,
        "closes_b9": False,
        "rule": "coverage = 100% of documented pendencies; Drive files are immutable",
        "sources": [
            "CKO_Relatorio_Tecnico_Final_Controlado_v1.0.0",
            "reference-website/relatorio-pendencias.json",
            "CKO-PAGE-INSTITUTIONAL-WAVE2-v0.2.0",
            "public/drive/catalog.json (read-only)",
        ],
        "counts": {
            "items": len(items),
            "pdf": sum(1 for i in items if i["source"] == "pdf"),
            "directory": sum(1 for i in items if i["source"] == "directory"),
            "wave2": sum(1 for i in items if i["source"] == "wave2"),
            "drive_kept": sum(1 for i in items if i["source"] == "drive-catalog"),
            "created_files": len(created),
        },
        "kpis": universe["residual_uncertainty"]["open_counts"],
        "items": items,
    }
    assert_not_drive(DATA / "pendencies.json")
    write_json(DATA / "pendencies.json", payload)
    write_json(
        DATA / "drive-immutable.json",
        {
            "id": "CKO-DRIVE-IMMUTABLE-1.0.0",
            "rule": "DO_NOT_ALTER_DRIVE_FILE",
            "files": after,
        },
    )
    print(
        json.dumps(
            {
                "pendencies": payload["counts"],
                "drive_files_frozen": len(after),
                "created_files_n": len(created),
                "release": payload["release"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
