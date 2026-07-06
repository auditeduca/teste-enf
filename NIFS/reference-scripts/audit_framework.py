"""Unified audit framework — compliance scoring, findings, styled exports.

Each audit stage maps to a framework (NKOS, Website, A11y, …).
Reports include compliance_pct per framework and structured findings.
"""
from __future__ import annotations

import base64
import html
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
LOGO_CANDIDATES = (
    ROOT / "website" / "assets" / "images" / "logotipo_website.webp",
    ROOT / "website" / "pt" / "assets" / "images" / "logotipo_website.webp",
)
FRAMEWORK_VERSION = "2026.1.0"
SITE_BRAND = "Calculadoras de Enfermagem — Nursing OS"
SITE_URL = "https://calculadorasdeenfermagem.com.br"

# ---------------------------------------------------------------------------
# Framework registry (one per audit format / domain)
# ---------------------------------------------------------------------------
AUDIT_FRAMEWORKS: dict[str, dict] = {
    "nkos": {
        "id": "nkos",
        "name": "NKOS — Integridade & Completude",
        "version": "2026.1",
        "weight": 25,
        "description": "Validação referencial fases 1–12, envelopes e completude de datasets.",
        "stage_ids": ("validate_1_7", "validate_8_12", "dataset_completeness"),
        "validators": ("validate_phases_1_7.py", "validate_phases_8_12.py", "dataset_completeness"),
    },
    "ecosystem": {
        "id": "ecosystem",
        "name": "Ecossistema Hub",
        "version": "2026.1",
        "weight": 15,
        "description": "Ligações ferramentas ↔ NIC/NANDA/protocolos/artigos/monografias.",
        "stage_ids": ("ecosystem_coverage",),
        "validators": ("ecosystem_coverage",),
    },
    "platform": {
        "id": "platform",
        "name": "Plataforma Admin",
        "version": "2026.1",
        "weight": 10,
        "description": "Inventário React/Vite e scripts Python (exclui node_modules).",
        "stage_ids": ("platform_inventory",),
        "validators": ("platform_inventory",),
    },
    "website": {
        "id": "website",
        "name": "Website pt-BR",
        "version": "2026.1",
        "weight": 20,
        "description": "Artefatos estáticos, links, rotas e integridade do build.",
        "stage_ids": ("website_artifacts", "audit_website"),
        "validators": ("website_artifacts", "audit_website_pt.py"),
    },
    "a11y": {
        "id": "a11y",
        "name": "WCAG / Acessibilidade Digital",
        "version": "2026.1",
        "weight": 12,
        "description": "Auditoria estática WCAG 2.2 (A/AA/AAA) + monitor tempo real.",
        "stage_ids": ("audit_a11y",),
        "validators": ("audit_website_a11y_pt.py",),
    },
    "seo": {
        "id": "seo",
        "name": "SEO",
        "version": "2026.1",
        "weight": 12,
        "description": "Title, meta, canonical, JSON-LD, headings e Open Graph.",
        "stage_ids": ("audit_seo",),
        "validators": ("audit_seo_pt.py",),
    },
    "sustainability": {
        "id": "sustainability",
        "name": "Sustentabilidade Digital",
        "version": "2026.1",
        "weight": 11,
        "description": "Peso de página, WebP, requests e estimativa de CO₂.",
        "stage_ids": ("audit_sustainability",),
        "validators": ("audit_sustainability_pt.py",),
    },
    "ci": {
        "id": "ci",
        "name": "Pipeline CI",
        "version": "2026.1",
        "weight": 5,
        "description": "Relatório unificado de steps CI persistido em metadata.",
        "stage_ids": ("ci_report",),
        "validators": ("ci_report",),
    },
}

STAGE_TO_FRAMEWORK: dict[str, str] = {}
for fw_id, fw in AUDIT_FRAMEWORKS.items():
    for sid in fw["stage_ids"]:
        STAGE_TO_FRAMEWORK[sid] = fw_id


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _stage_compliance(stage: dict) -> float:
    """0–100 compliance for a single stage."""
    if stage.get("score_pct") is not None:
        return float(stage["score_pct"])
    rs = stage.get("report_summary") or {}
    checks = rs.get("checks") or 0
    err_count = rs.get("error_count")
    if err_count is None:
        err_count = len(rs.get("errors") or [])
    if checks > 0:
        return round(max(0.0, (checks - err_count) / checks * 100), 1)
    if stage.get("passed") is True:
        return 100.0
    if stage.get("passed") is False:
        issues = len(stage.get("issues") or []) + len(stage.get("errors") or [])
        if issues == 0 and err_count:
            issues = err_count
        return 0.0 if issues else 50.0
    # completeness buckets
    c = len(stage.get("complete_100") or [])
    p = len(stage.get("partial") or [])
    g = len(stage.get("gaps") or [])
    total = c + p + g
    if total:
        return round((c * 100 + p * 50) / total, 1)
    return 100.0 if stage.get("passed", True) else 0.0


def compute_framework_compliance(stages: list[dict]) -> dict[str, Any]:
    """Per-framework and weighted overall compliance."""
    by_id: dict[str, list[float]] = {k: [] for k in AUDIT_FRAMEWORKS}
    stage_map = {s["id"]: s for s in stages if s.get("id")}

    for fw_id, fw in AUDIT_FRAMEWORKS.items():
        for sid in fw["stage_ids"]:
            st = stage_map.get(sid)
            if st:
                by_id[fw_id].append(_stage_compliance(st))

    frameworks_out: list[dict] = []
    weighted_sum = 0.0
    weight_total = 0.0

    for fw_id, fw in AUDIT_FRAMEWORKS.items():
        scores = by_id[fw_id]
        if not scores:
            pct = None
            status = "skipped"
        else:
            pct = round(sum(scores) / len(scores), 1)
            status = "pass" if pct >= 90 else "warn" if pct >= 70 else "fail"
            weighted_sum += pct * fw["weight"]
            weight_total += fw["weight"]
        frameworks_out.append({
            "id": fw_id,
            "name": fw["name"],
            "version": fw["version"],
            "weight": fw["weight"],
            "description": fw["description"],
            "validators": list(fw["validators"]),
            "stage_ids": list(fw["stage_ids"]),
            "compliance_pct": pct,
            "status": status,
            "stages_run": len(scores),
        })

    overall = round(weighted_sum / weight_total, 1) if weight_total else 0.0
    return {
        "framework_version": FRAMEWORK_VERSION,
        "overall_compliance_pct": overall,
        "overall_status": "pass" if overall >= 90 else "warn" if overall >= 70 else "fail",
        "frameworks": frameworks_out,
    }


def _finding(
    *,
    framework_id: str,
    stage_id: str,
    severity: str,
    message: str,
    code: str = "",
    file: str = "",
    suggestion: str = "",
) -> dict:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", message[:40]).strip("-").lower()
    return {
        "id": f"{stage_id}:{severity}:{code or slug}",
        "framework_id": framework_id,
        "stage_id": stage_id,
        "severity": severity,
        "code": code,
        "message": message,
        "file": file,
        "suggestion": suggestion,
        "timestamp": _now_iso(),
    }


def extract_findings(stages: list[dict]) -> list[dict]:
    """Normalize errors/issues into framework-tagged findings."""
    findings: list[dict] = []
    idx = 0

    for stage in stages:
        sid = stage.get("id", "?")
        fw = STAGE_TO_FRAMEWORK.get(sid, "nkos")

        rs = stage.get("report_summary") or {}
        for err in rs.get("errors") or []:
            msg = err if isinstance(err, str) else json.dumps(err, ensure_ascii=False)
            idx += 1
            f = _finding(
                framework_id=fw, stage_id=sid, severity="error", message=msg,
                code="VALIDATION_ERROR",
            )
            f["id"] = f"{sid}:error:{idx}"
            findings.append(f)

        for warn in rs.get("warnings") or []:
            msg = warn if isinstance(warn, str) else json.dumps(warn, ensure_ascii=False)
            findings.append(_finding(
                framework_id=fw, stage_id=sid, severity="warning", message=msg,
                code="VALIDATION_WARN",
            ))

        for issue in stage.get("issues") or []:
            findings.append(_finding(
                framework_id=fw, stage_id=sid, severity="error", message=str(issue),
                code="STAGE_ISSUE",
            ))

        for err in stage.get("errors") or []:
            if isinstance(err, str):
                findings.append(_finding(
                    framework_id=fw, stage_id=sid, severity="error", message=err,
                    code="STAGE_ERROR",
                ))

        for gap in stage.get("gaps") or []:
            label = gap.get("entity") or gap.get("label") or "?"
            pct = gap.get("pct", 0)
            findings.append(_finding(
                framework_id=fw,
                stage_id=sid,
                severity="error" if pct < 40 else "warning",
                message=f"{label}: {gap.get('actual', '?')}/{gap.get('target', '?')} ({pct}%)",
                code="COMPLETENESS_GAP",
                file=gap.get("file", ""),
            ))

        if stage.get("stderr_tail"):
            tail = stage["stderr_tail"].strip()
            if tail and stage.get("passed") is False:
                findings.append(_finding(
                    framework_id=fw, stage_id=sid, severity="error",
                    message=tail.splitlines()[-1][:500],
                    code="SUBPROCESS_STDERR",
                ))

    return findings


def enrich_audit_report(report: dict) -> dict:
    """Add framework compliance + findings to raw audit report."""
    report = dict(report)
    stages = report.get("stages") or []
    enriched_stages = []
    for stage in stages:
        st = dict(stage)
        st["compliance_pct"] = _stage_compliance(st)
        enriched_stages.append(st)
    report["stages"] = enriched_stages

    fw = compute_framework_compliance(enriched_stages)
    findings = extract_findings(enriched_stages)
    report["framework"] = fw
    report["findings"] = findings
    report["finding_counts"] = {
        "error": sum(1 for f in findings if f["severity"] == "error"),
        "warning": sum(1 for f in findings if f["severity"] == "warning"),
        "info": sum(1 for f in findings if f["severity"] == "info"),
    }
    if report.get("summary"):
        report["summary"] = dict(report["summary"])
        report["summary"]["overall_compliance_pct"] = fw["overall_compliance_pct"]
        report["summary"]["framework_version"] = FRAMEWORK_VERSION
    return report


def list_frameworks() -> list[dict]:
    return [
        {
            "id": fw["id"],
            "name": fw["name"],
            "version": fw["version"],
            "weight": fw["weight"],
            "description": fw["description"],
            "validators": list(fw["validators"]),
            "stage_ids": list(fw["stage_ids"]),
        }
        for fw in AUDIT_FRAMEWORKS.values()
    ]


def _logo_data_uri() -> str:
    for p in LOGO_CANDIDATES:
        if p.exists():
            b64 = base64.standard_b64encode(p.read_bytes()).decode("ascii")
            return f"data:image/webp;base64,{b64}"
    return f"{SITE_URL}/assets/images/logotipo_website.webp"


def _severity_badge(sev: str) -> str:
    colors = {"error": "#dc2626", "warning": "#d97706", "info": "#1990D0"}
    return f'<span class="badge badge-{sev}">{html.escape(sev.upper())}</span>'


def render_markdown(report: dict) -> str:
    fw = report.get("framework") or {}
    summary = report.get("summary") or {}
    lines = [
        f"# Relatório de Auditoria — {SITE_BRAND}",
        "",
        f"- **Gerado:** {report.get('finished_at') or report.get('started_at') or '—'}",
        f"- **Framework:** v{FRAMEWORK_VERSION}",
        f"- **Compliance geral:** {fw.get('overall_compliance_pct', summary.get('completeness_score_pct', 0))}%",
        f"- **Resultado:** {'PASS' if report.get('passed') else 'FAIL'}",
        "",
        "## Compliance por framework",
        "",
        "| Framework | Compliance | Status | Validadores |",
        "|-----------|------------|--------|-------------|",
    ]
    for f in fw.get("frameworks") or []:
        pct = f"{f['compliance_pct']}%" if f.get("compliance_pct") is not None else "N/A"
        vals = ", ".join(f.get("validators") or [])
        lines.append(f"| {f['name']} | {pct} | {f.get('status', '—')} | {vals} |")

    lines.extend(["", "## Achados", ""])
    for finding in report.get("findings") or []:
        lines.append(f"### [{finding['severity'].upper()}] {finding['framework_id']} / {finding['stage_id']}")
        lines.append(f"- **Código:** `{finding.get('code') or '—'}`")
        lines.append(f"- **Mensagem:** {finding['message']}")
        if finding.get("file"):
            lines.append(f"- **Arquivo:** `{finding['file']}`")
        if finding.get("suggestion"):
            lines.append(f"- **Sugestão IA:** {finding['suggestion']}")
        lines.append("")

    lines.extend(["", "## Estágios", ""])
    for st in report.get("stages") or []:
        ok = "OK" if st.get("passed", True) else "FAIL"
        pct = _stage_compliance(st)
        lines.append(f"- **{st.get('label', st.get('id'))}** — {ok} ({pct}% compliance, {st.get('elapsed_s', 0)}s)")

    return "\n".join(lines)


def render_html(report: dict, *, for_print: bool = False) -> str:
    fw = report.get("framework") or {}
    summary = report.get("summary") or {}
    overall = fw.get("overall_compliance_pct", summary.get("completeness_score_pct", 0))
    status = "PASS" if report.get("passed") else "FAIL"
    status_color = "#16a34a" if report.get("passed") else "#dc2626"
    logo = _logo_data_uri()
    finished = html.escape(report.get("finished_at") or report.get("started_at") or _now_iso())

    fw_rows = ""
    for f in fw.get("frameworks") or []:
        pct = f.get("compliance_pct")
        pct_str = f"{pct}%" if pct is not None else "—"
        bar_w = pct if pct is not None else 0
        bar_color = "#16a34a" if (pct or 0) >= 90 else "#d97706" if (pct or 0) >= 70 else "#dc2626"
        fw_rows += f"""
        <tr>
          <td><strong>{html.escape(f['name'])}</strong><br><small>{html.escape(f.get('description',''))}</small></td>
          <td class="num">{pct_str}</td>
          <td><div class="bar"><div class="bar-fill" style="width:{bar_w}%;background:{bar_color}"></div></div></td>
          <td><code>{html.escape(', '.join(f.get('validators') or []))}</code></td>
        </tr>"""

    finding_rows = ""
    for finding in (report.get("findings") or [])[:200]:
        sug = finding.get("suggestion") or "—"
        finding_rows += f"""
        <tr class="sev-{html.escape(finding['severity'])}">
          <td>{_severity_badge(finding['severity'])}</td>
          <td><code>{html.escape(finding.get('framework_id',''))}</code></td>
          <td><code>{html.escape(finding.get('code') or '—')}</code></td>
          <td>{html.escape(finding['message'])}</td>
          <td><small>{html.escape(finding.get('file') or '—')}</small></td>
          <td class="suggestion">{html.escape(sug)}</td>
        </tr>"""

    print_css = """
    @media print { .no-print { display: none; } body { background: #fff; } }
    """ if for_print else ""

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8"/>
  <title>Auditoria — {html.escape(SITE_BRAND)}</title>
  <style>
    :root {{ --navy: #0f172a; --primary: #1990D0; --muted: #64748b; --border: #e2e8f0; }}
    * {{ box-sizing: border-box; }}
    body {{ font-family: system-ui, -apple-system, 'Segoe UI', sans-serif; margin: 0; background: #f8fafc; color: var(--navy); line-height: 1.5; }}
    .wrap {{ max-width: 960px; margin: 0 auto; padding: 2rem 1.5rem; }}
    header {{ display: flex; align-items: center; gap: 1.25rem; padding: 1.5rem; background: #fff; border-radius: 12px; border: 1px solid var(--border); margin-bottom: 1.5rem; }}
    header img {{ height: 48px; width: auto; }}
    h1 {{ margin: 0; font-size: 1.35rem; }}
    .meta {{ color: var(--muted); font-size: 0.85rem; margin-top: 0.25rem; }}
    .score {{ margin-left: auto; text-align: right; }}
    .score .pct {{ font-size: 2.5rem; font-weight: 800; color: var(--primary); }}
    .score .status {{ font-weight: 700; color: {status_color}; }}
    section {{ background: #fff; border: 1px solid var(--border); border-radius: 12px; padding: 1.25rem; margin-bottom: 1rem; }}
    h2 {{ margin: 0 0 1rem; font-size: 1rem; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 0.85rem; }}
    th, td {{ padding: 0.5rem 0.65rem; border-bottom: 1px solid var(--border); text-align: left; vertical-align: top; }}
    th {{ background: #f1f5f9; font-weight: 600; }}
    .num {{ font-weight: 700; white-space: nowrap; }}
    .bar {{ height: 8px; background: #e2e8f0; border-radius: 4px; overflow: hidden; min-width: 80px; }}
    .bar-fill {{ height: 100%; border-radius: 4px; }}
    .badge {{ display: inline-block; padding: 0.15rem 0.45rem; border-radius: 4px; font-size: 0.65rem; font-weight: 700; }}
    .badge-error {{ background: #fef2f2; color: #dc2626; }}
    .badge-warning {{ background: #fffbeb; color: #d97706; }}
    .badge-info {{ background: #eff6ff; color: #1990D0; }}
    tr.sev-error {{ background: #fef2f2; }}
    tr.sev-warning {{ background: #fffbeb; }}
    .suggestion {{ color: var(--muted); font-size: 0.8rem; max-width: 220px; }}
    footer {{ text-align: center; color: var(--muted); font-size: 0.75rem; padding: 2rem 0; }}
    {print_css}
  </style>
</head>
<body>
  <div class="wrap">
    <header>
      <img src="{logo}" alt="Logo"/>
      <div>
        <h1>Relatório de Auditoria Completa</h1>
        <p class="meta">{html.escape(SITE_BRAND)} · Framework v{FRAMEWORK_VERSION}<br/>Timestamp: {finished}</p>
      </div>
      <div class="score">
        <div class="pct">{overall}%</div>
        <div class="status">{status}</div>
        <small>compliance</small>
      </div>
    </header>

    <section>
      <h2>Compliance por framework</h2>
      <table>
        <thead><tr><th>Framework</th><th>%</th><th>Barra</th><th>Validadores</th></tr></thead>
        <tbody>{fw_rows}</tbody>
      </table>
    </section>

    <section>
      <h2>Achados ({len(report.get('findings') or [])}) — erros detalhados</h2>
      <table>
        <thead><tr><th>Severidade</th><th>Framework</th><th>Código</th><th>Mensagem</th><th>Arquivo</th><th>Sugestão IA</th></tr></thead>
        <tbody>{finding_rows or '<tr><td colspan="6">Nenhum achado registrado.</td></tr>'}</tbody>
      </table>
    </section>

    <footer>Gerado por Nursing OS Audit Framework · {finished}</footer>
  </div>
</body>
</html>"""


def render_docx_html(report: dict) -> str:
    """Word-compatible HTML (opens in Microsoft Word)."""
    body = render_html(report)
    return body.replace("<!DOCTYPE html>", '<!DOCTYPE html>\n<!--[if gte mso 9]><xml><w:WordDocument><w:View>Print</w:View></w:WordDocument></xml><![endif]-->')


def export_report(report: dict, fmt: str) -> tuple[str, str, str]:
    """Return (content, mime_type, filename_ext)."""
    stamp = (report.get("finished_at") or _now_iso())[:19].replace(":", "-").replace("T", "_")
    base = f"audit-report-{stamp}"

    fmt = (fmt or "md").lower()
    if fmt in ("md", "markdown"):
        return render_markdown(report), "text/markdown; charset=utf-8", f"{base}.md"
    if fmt in ("html", "htm"):
        return render_html(report), "text/html; charset=utf-8", f"{base}.html"
    if fmt in ("pdf",):
        return render_html(report, for_print=True), "text/html; charset=utf-8", f"{base}-print.html"
    if fmt in ("docx", "doc", "word"):
        return render_docx_html(report), "application/msword; charset=utf-8", f"{base}.doc"
    raise ValueError(f"Formato não suportado: {fmt}")
