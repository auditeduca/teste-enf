"""Audit execution orchestrator — dependency graph, modes, per-domain live status.

Execution order (DAG):
  1. NKOS validators (validate_1_7, validate_8_12) — gate for data integrity
  2. Data & platform (dataset_completeness, ecosystem, platform_inventory, ci)
  3. Website artifacts — requires generated site
  4. Website deep audit (links/routes)
  5. Parallel UX domains (a11y, seo, sustainability) — require website/pt

Modes:
  full     — all stages respecting dependencies
  quick    — NKOS + website_artifacts + sample UX checks
  monitor  — a11y + seo + sustainability only (dashboard refresh)
  domain   — selected domains + required dependencies
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
DOMAINS_DIR = ROOT / "datasets" / "metadata" / "audit_domains"
NOW_ISO = lambda: datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

# stage_id → domain_id for live monitor tiles
STAGE_DOMAIN: dict[str, str] = {
    "validate_1_7": "nkos",
    "validate_8_12": "nkos",
    "dataset_completeness": "nkos",
    "ecosystem_coverage": "ecosystem",
    "platform_inventory": "platform",
    "website_artifacts": "website",
    "audit_website": "website",
    "audit_a11y": "a11y",
    "audit_seo": "seo",
    "audit_sustainability": "sustainability",
    "ci_report": "ci",
}

# Dependencies: stage cannot run until all deps completed successfully (or skipped)
STAGE_DEPENDS: dict[str, tuple[str, ...]] = {
    "validate_8_12": ("validate_1_7",),
    "dataset_completeness": ("validate_1_7", "validate_8_12"),
    "ecosystem_coverage": ("dataset_completeness",),
    "website_artifacts": ("validate_1_7",),
    "audit_website": ("website_artifacts",),
    "audit_a11y": ("website_artifacts",),
    "audit_seo": ("website_artifacts",),
    "audit_sustainability": ("website_artifacts",),
}

EXECUTION_MODES: dict[str, dict] = {
    "full": {
        "id": "full",
        "label": "Auditoria completa",
        "description": "Todos os estágios na ordem do DAG (NKOS → website → UX).",
        "domains": ("nkos", "ecosystem", "platform", "website", "a11y", "seo", "sustainability", "ci"),
    },
    "quick": {
        "id": "quick",
        "label": "Rápida",
        "description": "NKOS crítico + artefatos website + amostra UX.",
        "stage_filter": (
            "validate_1_7", "validate_8_12", "website_artifacts",
            "audit_a11y", "audit_seo", "audit_sustainability",
        ),
    },
    "monitor": {
        "id": "monitor",
        "label": "Monitor UX",
        "description": "Acessibilidade, SEO e sustentabilidade (dashboard tempo real).",
        "stage_filter": ("website_artifacts", "audit_a11y", "audit_seo", "audit_sustainability"),
    },
    "pre_deploy": {
        "id": "pre_deploy",
        "label": "Pré-deploy",
        "description": "Validadores NKOS + website + links + WCAG A.",
        "stage_filter": (
            "validate_1_7", "validate_8_12", "website_artifacts",
            "audit_website", "audit_a11y", "audit_seo",
        ),
    },
}

DOMAIN_META: dict[str, dict] = {
    "nkos": {"label": "NKOS / Dados", "icon": "database", "color": "#1990D0"},
    "ecosystem": {"label": "Ecossistema", "icon": "network", "color": "#6366f1"},
    "platform": {"label": "Plataforma", "icon": "layout", "color": "#8b5cf6"},
    "website": {"label": "Website", "icon": "globe", "color": "#0ea5e9"},
    "a11y": {"label": "Acessibilidade Digital", "icon": "accessibility", "color": "#16a34a"},
    "seo": {"label": "SEO", "icon": "search", "color": "#d97706"},
    "sustainability": {"label": "Sustentabilidade Digital", "icon": "leaf", "color": "#059669"},
    "ci": {"label": "CI / Pipeline", "icon": "pipeline", "color": "#64748b"},
}

# Free / optional external APIs (enhance precision when keys configured)
FREE_AUDIT_APIS: list[dict] = [
    {
        "id": "pagespeed",
        "name": "Google PageSpeed Insights",
        "env_key": "GOOGLE_PAGESPEED_API_KEY",
        "free_tier": "25.000 consultas/dia (grátis com Google Cloud)",
        "domains": ("seo", "sustainability"),
        "docs": "https://developers.google.com/speed/docs/insights/v5/get-started",
    },
    {
        "id": "mozilla_observatory",
        "name": "Mozilla HTTP Observatory",
        "env_key": None,
        "free_tier": "Sem chave — rate limit por IP",
        "domains": ("website",),
        "docs": "https://observatory.mozilla.org/",
    },
    {
        "id": "local_static",
        "name": "Validadores estáticos NKOS (local)",
        "env_key": None,
        "free_tier": "Sempre disponível — HTML/WCAG/SEO no repo",
        "domains": ("a11y", "seo", "sustainability", "nkos", "website"),
        "docs": "scripts/audit_*.py",
    },
    {
        "id": "deepseek",
        "name": "DeepSeek — sugestões IA",
        "env_key": "DEEPSEEK_API_KEY",
        "free_tier": "Pay-as-you-go / créditos — sugestões de correção",
        "domains": ("a11y", "seo", "sustainability", "nkos"),
        "docs": "POST /api/audit/suggest",
    },
]


def resolve_stages(
    all_stages: list[dict],
    *,
    mode: str = "full",
    domains: list[str] | None = None,
    skip_website: bool = False,
    skip_a11y: bool = False,
) -> list[dict]:
    """Return ordered stage list respecting mode, domain filter and dependencies."""
    by_id = {s["id"]: s for s in all_stages}
    mode_cfg = EXECUTION_MODES.get(mode, EXECUTION_MODES["full"])

    if mode_cfg.get("stage_filter"):
        wanted_ids = set(mode_cfg["stage_filter"])
    elif domains:
        wanted_ids = {sid for sid, dom in STAGE_DOMAIN.items() if dom in domains}
        for dep_id, deps in STAGE_DEPENDS.items():
            if dep_id in wanted_ids:
                wanted_ids.update(deps)
    else:
        wanted_ids = set(by_id)

    if skip_website:
        wanted_ids.discard("audit_website")
    if skip_a11y:
        wanted_ids.discard("audit_a11y")

    # Topological order preserving original AUDIT_STAGES order
    ordered: list[dict] = []
    seen: set[str] = set()

    def add_stage(sid: str) -> None:
        if sid in seen or sid not in wanted_ids or sid not in by_id:
            return
        for dep in STAGE_DEPENDS.get(sid, ()):
            add_stage(dep)
        if sid not in seen:
            seen.add(sid)
            ordered.append(by_id[sid])

    for st in all_stages:
        add_stage(st["id"])

    return ordered


def write_domain_status(
    domain_id: str,
    *,
    status: str,
    compliance_pct: float | None = None,
    running: bool = False,
    metrics: dict | None = None,
    detail: str = "",
    error: str = "",
) -> dict:
    DOMAINS_DIR.mkdir(parents=True, exist_ok=True)
    meta = DOMAIN_META.get(domain_id, {"label": domain_id})
    payload = {
        "domain": domain_id,
        "label": meta.get("label", domain_id),
        "status": status,
        "running": running,
        "compliance_pct": compliance_pct,
        "updated_at": NOW_ISO(),
        "detail": detail,
        "error": error,
        "metrics": metrics or {},
    }
    path = DOMAINS_DIR / f"{domain_id}.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload


def load_domain_status(domain_id: str) -> dict | None:
    path = DOMAINS_DIR / f"{domain_id}.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def load_all_domain_statuses() -> list[dict]:
    out: list[dict] = []
    for domain_id, meta in DOMAIN_META.items():
        data = load_domain_status(domain_id)
        if data:
            out.append(data)
        else:
            out.append({
                "domain": domain_id,
                "label": meta["label"],
                "status": "idle",
                "running": False,
                "compliance_pct": None,
                "updated_at": None,
                "detail": "Nunca executado",
                "metrics": {},
            })
    return out


def compliance_from_domain_report(domain_id: str, report_path: Path) -> tuple[float, dict]:
    """Extract compliance % and metrics from domain-specific JSON report."""
    if not report_path.exists():
        return 0.0, {}
    try:
        data = json.loads(report_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return 0.0, {}

    if domain_id == "a11y":
        levels = data.get("wcag_levels") or {}
        a = levels.get("A") or {}
        pct = float(a.get("pass_rate_percent") or 0)
        return pct, {
            "wcag_a": pct,
            "wcag_aa": (levels.get("AA") or {}).get("pass_rate_percent"),
            "total_errors": data.get("total_errors"),
            "pages": data.get("total_pages"),
        }
    if domain_id == "seo":
        pct = float(data.get("compliance_pct") or 0)
        return pct, {
            "pages_audited": data.get("pages_audited"),
            "issues": data.get("total_issues"),
            "avg_score": data.get("avg_page_score"),
        }
    if domain_id == "sustainability":
        pct = float(data.get("compliance_pct") or 0)
        return pct, {
            "avg_page_kb": data.get("avg_page_weight_kb"),
            "webp_ratio_pct": data.get("webp_ratio_pct"),
            "est_co2_g_per_view": data.get("est_co2_g_per_page_view"),
            "green_pages_pct": data.get("green_pages_pct"),
        }
    if domain_id == "website":
        err = data.get("links", {}).get("broken_count", 0)
        pct = 100.0 if err == 0 else max(0.0, 100 - err)
        return pct, {"broken_links": err}
    return 100.0 if data.get("passed") else 50.0, {}


def get_execution_plan(all_stages: list[dict], **kwargs) -> dict:
    resolved = resolve_stages(all_stages, **kwargs)
    return {
        "mode": kwargs.get("mode", "full"),
        "domains": kwargs.get("domains"),
        "stages": [{"id": s["id"], "label": s["label"], "domain": STAGE_DOMAIN.get(s["id"]), "depends_on": list(STAGE_DEPENDS.get(s["id"], ()))} for s in resolved],
        "stage_count": len(resolved),
        "free_apis": FREE_AUDIT_APIS,
    }


def build_monitor_snapshot(progress: dict | None, full_report: dict | None) -> dict:
    """Aggregate live monitor data for dashboard."""
    domains = load_all_domain_statuses()
    fw = (full_report or {}).get("framework") or {}
    fw_map = {f["id"]: f for f in fw.get("frameworks") or []}

    tiles = []
    for d in domains:
        did = d["domain"]
        fw_item = fw_map.get(did)
        pct = d.get("compliance_pct")
        if pct is None and fw_item:
            pct = fw_item.get("compliance_pct")
        tiles.append({
            **d,
            "compliance_pct": pct,
            "framework_status": fw_item.get("status") if fw_item else d.get("status"),
            "meta": DOMAIN_META.get(did, {}),
        })

    overall = fw.get("overall_compliance_pct")
    if overall is None:
        scored = [t["compliance_pct"] for t in tiles if t.get("compliance_pct") is not None]
        overall = round(sum(scored) / len(scored), 1) if scored else 0

    return {
        "updated_at": NOW_ISO(),
        "global_running": progress.get("status") == "running" if progress else False,
        "progress": progress,
        "overall_compliance_pct": overall,
        "domains": tiles,
        "free_apis": FREE_AUDIT_APIS,
    }
