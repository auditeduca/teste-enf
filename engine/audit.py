"""Write audit trail, 360 audit and release manifest for this application."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from .paths import AUDIT_DIR, REPORTS_DIR, ROOT, TOOLS_DIR
from .validate import iter_tool_files, load_tool

from validators.clinical_completeness import evaluate_catalog
from validators.dual_render import check_parity
from validators.release_gate import evaluate_release


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def write_audit_artifacts() -> list[Path]:
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    objects = []
    for path in iter_tool_files(TOOLS_DIR):
        tool = load_tool(path)
        objects.append({
            "slug": tool.get("slug"),
            "kind": tool.get("kind"),
            "status": tool.get("status"),
            "version": tool.get("version"),
            "path": str(path.relative_to(ROOT)),
            "sha256": _sha256(path),
        })

    completeness = evaluate_catalog()
    parity = check_parity()
    release = evaluate_release(completeness, parity)

    trail = {
        "schemaVersion": "1.0.0",
        "artifact": "audit-trail.v1",
        "generatedAt": _now(),
        "application": "cko",
        "objects": objects,
        "hashChain": [item["sha256"] for item in objects],
    }
    audit_360 = {
        "schemaVersion": "1.0.0",
        "artifact": "final-360-audit.v1",
        "generatedAt": _now(),
        "perspectives": {
            "direct": {"status": "PARTIAL", "note": "Fonte JSON → HTML gerado está materializado para os pilotos."},
            "inverse": {"status": "PARTIAL", "note": "HTML aponta para slug/versão/hash do objeto; thread regulatório completo ainda não está materializado."},
            "complementary": {"status": "PARTIAL", "note": "Pilotos se complementam sem fusão indevida."},
            "transversal": {"status": "HOLD", "note": "Relações entre Regulatory Core, bibliotecas e provas ainda não estão no grafo consultável."},
            "diagonal": {"status": "HOLD", "note": "Caminhos multi-hop norma → tópico → questão → simulado ainda não estão materializados."},
        },
        "clinicalCompleteness": completeness,
        "dualRenderParity": {"status": parity["status"], "findings": parity.get("findings", [])},
        "conclusion": release["status"],
    }
    manifest = {
        "schemaVersion": "1.0.0",
        "artifact": "release-manifest.v1",
        "generatedAt": _now(),
        "releaseId": "cko-v0.1.0-pilot",
        "status": release["status"],
        "gates": release["gates"],
        "objects": objects,
        "promotionAllowed": release["status"] == "PASS",
    }

    written = []
    for name, payload in (
        ("audit-trail.v1.json", trail),
        ("final-360-audit.v1.json", audit_360),
        ("release-manifest.v1.json", manifest),
    ):
        dest = AUDIT_DIR / name
        dest.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        written.append(dest)

    report = REPORTS_DIR / "ESTADO-ATUAL.md"
    report.write_text(_estado_atual(completeness, parity, release, objects), encoding="utf-8")
    written.append(report)
    return written


def _estado_atual(completeness, parity, release, objects) -> str:
    rows = "\n".join(
        f"| `{item['slug']}` | {item['kind']} | {item['status']} | `{item['sha256'][:12]}` |"
        for item in objects
    )
    return f"""# Estado atual desta aplicação

Gerado automaticamente por `cko audit`. Este relatório descreve **somente** o que existe neste repositório.

## Conclusão de release

**{release['status']}** — promoção para produção clínica completa **não** está autorizada.

## Objetos

| Slug | Tipo | Status | SHA-256 |
|---|---|---|---|
{rows}

## Gates

- Completude clínica: **{completeness['status']}**
- Paridade dual-render: **{parity['status']}**
- Release: **{release['status']}**

## Leitura permitida

> Esta aplicação possui motor canônico, contratos, validadores e um lote piloto renderizável. A aderência 360° e a publicação clínica completa ainda não foram demonstradas.
"""
