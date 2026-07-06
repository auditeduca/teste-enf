"""Unified audit library for CALENF-NKD.

Aggregates validators, completeness scans, and website checks.
Ignores node_modules and other vendor/build noise when scanning the repo.

Writes:
  datasets/metadata/full_audit_report.json
  datasets/metadata/audit_progress.json  (live progress for UI)
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
DATASETS = ROOT / "datasets"
WEBSITE_PT = ROOT / "website" / "pt"
REPORT_PATH = DATASETS / "metadata" / "full_audit_report.json"
PROGRESS_PATH = DATASETS / "metadata" / "audit_progress.json"
NOW_ISO = lambda: datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

# Directories never scanned for inventory / completeness walks
IGNORE_DIR_NAMES = frozenset({
    "node_modules",
    ".git",
    "__pycache__",
    ".venv",
    "venv",
    ".cursor",
    "dist",
    ".vite",
    ".turbo",
    ".next",
    ".cache",
    "coverage",
})

# Keep platform/dist out; platform/src is scanned
IGNORE_PATH_PARTS = frozenset({
    "platform/node_modules",
    "platform/dist",
    "website/pt/en",
    "website/pt/es",
    "website/pt/fr",
    "website/pt/de",
    "website/pt/it",
    "website/pt/ja",
})


def should_ignore_path(path: Path) -> bool:
    rel = path.relative_to(ROOT).as_posix()
    for part in IGNORE_PATH_PARTS:
        if rel.startswith(part):
            return True
    for segment in path.parts:
        if segment in IGNORE_DIR_NAMES:
            return True
    return False


def iter_project_files(*, extensions: set[str] | None = None) -> list[Path]:
    out: list[Path] = []
    for p in ROOT.rglob("*"):
        if not p.is_file():
            continue
        if should_ignore_path(p):
            continue
        if extensions and p.suffix.lower() not in extensions:
            continue
        out.append(p)
    return out


def write_progress(data: dict) -> None:
    PROGRESS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(PROGRESS_PATH, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def run_subprocess_stage(script: str, extra_args: list[str] | None = None) -> dict:
    cmd = [sys.executable, str(SCRIPTS / script)] + (extra_args or [])
    start = time.monotonic()
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT))
    elapsed = round(time.monotonic() - start, 2)
    return {
        "exit_code": proc.returncode,
        "passed": proc.returncode == 0,
        "elapsed_s": elapsed,
        "stdout_tail": "\n".join((proc.stdout or "").strip().splitlines()[-8:]),
        "stderr_tail": "\n".join((proc.stderr or "").strip().splitlines()[-8:]),
    }


def load_json(rel: Path | str, default: Any = None) -> Any:
    p = Path(rel)
    if not p.is_absolute():
        p = ROOT / p
    if not p.exists():
        return default
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return default


def stage_dataset_completeness() -> dict:
    """Classify NKOS entities as complete (100%), partial, or gap."""
    status = load_json(DATASETS / "metadata" / "nkos_implementation_status.json", {}) or {}
    complete: list[dict] = []
    partial: list[dict] = []
    gaps: list[dict] = []

    def classify_entity(ent: dict, group: str) -> None:
        target = ent.get("target")
        actual = ent.get("actual")
        st = ent.get("status", "")
        pct = 100.0
        if target and actual is not None and target > 0:
            pct = round(min(100.0, actual / target * 100), 1)
        item = {
            "group": group,
            "entity": ent.get("entity", "?"),
            "file": ent.get("file", ""),
            "target": target,
            "actual": actual,
            "status": st,
            "pct": pct,
        }
        if st == "complete" or pct >= 100:
            complete.append(item)
        elif pct >= 50 or st in ("partial", "in_progress"):
            partial.append(item)
        else:
            gaps.append(item)

    for key, block in status.items():
        if not isinstance(block, dict):
            continue
        entities = block.get("entities")
        if isinstance(entities, list):
            for ent in entities:
                if isinstance(ent, dict) and ent.get("entity"):
                    classify_entity(ent, key)

    # Website / content gaps not in NKOS status
    content_checks = [
        ("articles", "datasets/content/editorial/articles.json", 50, "Artigos científicos"),
        ("drug_monographs", "datasets/clinical/drug_monographs.json", 500, "Monografias medicamentos"),
        ("assessment_results", "datasets/operations/assessment_results.json", 1, "Resultados avaliações"),
    ]
    for key, path, target, label in content_checks:
        try:
            from dataset_io import read_envelope
            recs = read_envelope(path.replace("datasets/", "")).get("records", [])
            actual = len(recs)
        except Exception:
            actual = 0
        pct = round(min(100.0, actual / target * 100), 1) if target else 0
        item = {"group": "content_gaps", "entity": label, "file": path, "target": target, "actual": actual, "pct": pct}
        if pct >= 100:
            complete.append(item)
        elif pct >= 20:
            partial.append(item)
        else:
            gaps.append(item)

    total = len(complete) + len(partial) + len(gaps)
    score = round(len(complete) / total * 100, 1) if total else 0
    return {
        "passed": True,
        "elapsed_s": 0,
        "score_pct": score,
        "complete_100": complete,
        "partial": partial,
        "gaps": gaps,
        "counts": {"complete": len(complete), "partial": len(partial), "gaps": len(gaps)},
    }


def stage_ecosystem_coverage() -> dict:
    """Hub ecosystem linkage audit (from audit_ecosystem_coverage logic)."""
    start = time.monotonic()

    def load_records(rel: str) -> list:
        try:
            from dataset_io import read_envelope
            return read_envelope(rel).get("records", [])
        except Exception:
            return []

    tools = load_records("clinical/clinical_tools_catalog.json")
    tool_codes = {t["tool_code"] for t in tools if t.get("tool_code")}
    nic = load_records("clinical/nursing_interventions.json")
    nanda = load_records("clinical/nursing_diagnoses.json")
    protos = load_records("clinical/institutional_protocols.json")
    articles = load_records("content/editorial/articles.json")
    mono = load_records("clinical/drug_monographs.json")
    refs = load_records("clinical/drug_references.json")

    idx_paths = [
        ROOT / "website" / "pt" / "assets" / "data" / "tool-concepts-index.json",
        ROOT / "website" / "assets" / "data" / "tool-concepts-index.json",
    ]
    concepts = []
    tools_with_eco = 0
    for idx_path in idx_paths:
        if idx_path.exists():
            idx = json.loads(idx_path.read_text(encoding="utf-8"))
            concepts = idx.get("concepts", [])
            tools_with_eco = sum(1 for c in concepts if (c.get("ecosystem") or c.get("resource_count", 0) > 0))
            break

    metrics = [
        {"label": "Ferramentas clínicas", "actual": len(tools), "target": 100, "linked": len(tools)},
        {"label": "Conceitos com ecossistema", "actual": tools_with_eco, "target": len(tools) or 100, "linked": tools_with_eco},
        {"label": "NIC com tool links", "actual": sum(1 for i in nic if i.get("related_tool_codes")), "target": len(nic), "linked": None},
        {"label": "NANDA com tool links", "actual": sum(1 for n in nanda if n.get("related_tool_codes")), "target": len(nanda), "linked": None},
        {"label": "Protocolos linkados", "actual": sum(1 for p in protos if p.get("related_tool_codes")), "target": len(protos), "linked": None},
        {"label": "Artigos", "actual": len(articles), "target": 50, "linked": sum(1 for a in articles if a.get("related_tools"))},
        {"label": "Monografias / refs fármacos", "actual": len(mono), "target": len(refs) or 500, "linked": len(mono)},
    ]

    complete = []
    partial = []
    gaps = []
    for m in metrics:
        tgt = m["target"] or 1
        pct = round(min(100.0, m["actual"] / tgt * 100), 1)
        row = {**m, "pct": pct}
        if pct >= 100:
            complete.append(row)
        elif pct >= 40:
            partial.append(row)
        else:
            gaps.append(row)

    elapsed = round(time.monotonic() - start, 2)
    return {
        "passed": True,
        "elapsed_s": elapsed,
        "metrics": metrics,
        "complete_100": complete,
        "partial": partial,
        "gaps": gaps,
        "concept_count": len(concepts),
        "tools_with_ecosystem": tools_with_eco,
    }


def stage_website_artifacts(*, require_build: bool = False) -> dict:
    start = time.monotonic()
    issues: list[str] = []
    manifest = load_json(WEBSITE_PT / "generation_manifest.json", {})
    build_report = load_json(ROOT / "website" / "build-report.json", {})
    audit_report = load_json(ROOT / "website" / "audit_pt_report.json", {})

    html_count = len(list(WEBSITE_PT.rglob("*.html"))) if WEBSITE_PT.exists() else 0
    if not WEBSITE_PT.exists():
        issues.append("website/pt missing")
    if html_count < 200:
        issues.append(f"low html count: {html_count}")
    if not (WEBSITE_PT / "sitemap.xml").exists():
        issues.append("sitemap.xml missing")
    if require_build and not build_report:
        issues.append("build-report.json missing")

    route_audit = audit_report.get("route_audit", {}) if isinstance(audit_report, dict) else {}
    links = audit_report.get("links", {}) if isinstance(audit_report, dict) else {}

    elapsed = round(time.monotonic() - start, 2)
    return {
        "passed": len(issues) == 0,
        "elapsed_s": elapsed,
        "issues": issues,
        "html_count": html_count,
        "manifest_pages": manifest.get("page_count"),
        "build_report_ok": bool(build_report.get("jsonld_validation", {}).get("passed")),
        "broken_links": links.get("broken_count", -1),
        "chrome_broken": links.get("chrome_broken_count", -1),
        "routes_ok": route_audit.get("missing_count", 0) == 0 if route_audit else None,
    }


def stage_platform_inventory() -> dict:
    """Scan platform source (excluding node_modules/dist)."""
    start = time.monotonic()
    src = ROOT / "platform" / "src"
    pages = list(src.glob("pages/*.jsx")) if src.exists() else []
    components = [p for p in src.rglob("*.jsx") if p.is_file() and "node_modules" not in p.parts]
    py_scripts = [p for p in SCRIPTS.glob("*.py") if p.is_file()]
    dataset_json = [
        p for p in DATASETS.rglob("*.json")
        if p.is_file() and not should_ignore_path(p)
    ]
    elapsed = round(time.monotonic() - start, 2)
    return {
        "passed": len(pages) >= 5,
        "elapsed_s": elapsed,
        "platform_pages": len(pages),
        "platform_components": len(components),
        "python_scripts": len(py_scripts),
        "dataset_files": len(dataset_json),
        "ignored_patterns": sorted(IGNORE_DIR_NAMES),
    }


def stage_validator_report(path: str) -> dict:
    """Load existing validator JSON report."""
    data = load_json(path, {})
    errors = data.get("errors", [])
    checks = data.get("checks", data.get("checks_run", 0))
    return {
        "passed": len(errors) == 0 and data.get("passed", len(errors) == 0),
        "checks": checks,
        "errors": errors[:20],
        "error_count": len(errors),
        "warnings": (data.get("warnings") or [])[:10],
        "validated_at": data.get("validated_at"),
    }


AUDIT_STAGES: list[dict] = [
    {"id": "validate_1_7", "label": "Integridade referencial (Fases 1–7)", "kind": "subprocess", "script": "validate_phases_1_7.py", "report": "datasets/metadata/validation_phases_1_7_report.json", "framework_id": "nkos"},
    {"id": "validate_8_12", "label": "Integridade referencial (Fases 8–12)", "kind": "subprocess", "script": "validate_phases_8_12.py", "report": "datasets/metadata/validation_phases_8_12_report.json", "framework_id": "nkos"},
    {"id": "dataset_completeness", "label": "Completude datasets NKOS", "kind": "inline", "fn": "dataset_completeness", "framework_id": "nkos"},
    {"id": "ecosystem_coverage", "label": "Cobertura ecossistema hub", "kind": "inline", "fn": "ecosystem_coverage", "framework_id": "ecosystem"},
    {"id": "platform_inventory", "label": "Inventário plataforma (sem node)", "kind": "inline", "fn": "platform_inventory", "framework_id": "platform"},
    {"id": "website_artifacts", "label": "Artefatos website pt-BR", "kind": "inline", "fn": "website_artifacts", "framework_id": "website"},
    {"id": "audit_website", "label": "Auditoria website (links, rotas, WCAG)", "kind": "subprocess", "script": "audit_website_pt.py", "optional": True, "framework_id": "website"},
    {"id": "audit_a11y", "label": "Auditoria acessibilidade WCAG", "kind": "subprocess", "script": "audit_website_a11y_pt.py", "optional": True, "framework_id": "a11y"},
    {"id": "audit_seo", "label": "Auditoria SEO", "kind": "subprocess", "script": "audit_seo_pt.py", "optional": True, "framework_id": "seo"},
    {"id": "audit_sustainability", "label": "Sustentabilidade digital", "kind": "subprocess", "script": "audit_sustainability_pt.py", "optional": True, "framework_id": "sustainability"},
    {"id": "ci_report", "label": "Relatório CI unificado", "kind": "inline", "fn": "ci_report", "framework_id": "ci"},
]


def stage_ci_report() -> dict:
    data = load_json(DATASETS / "metadata" / "ci_report.json", {})
    return {
        "passed": data.get("passed", False),
        "elapsed_s": 0,
        "ran_at": data.get("ran_at"),
        "steps": data.get("steps", {}),
    }


INLINE_FNS: dict[str, Callable[..., dict]] = {
    "dataset_completeness": stage_dataset_completeness,
    "ecosystem_coverage": stage_ecosystem_coverage,
    "platform_inventory": stage_platform_inventory,
    "website_artifacts": stage_website_artifacts,
    "ci_report": stage_ci_report,
}


CRITICAL_STAGES = frozenset({"validate_1_7", "validate_8_12"})


DOMAIN_REPORT_FILES: dict[str, Path] = {
    "a11y": ROOT / "website" / "audit_a11y_pt_report.json",
    "seo": ROOT / "website" / "audit_seo_pt_report.json",
    "sustainability": ROOT / "website" / "audit_sustainability_pt_report.json",
    "website": ROOT / "website" / "audit_pt_report.json",
}


def _update_domain_from_stage(stage_id: str, entry: dict) -> None:
    from audit_orchestrator import STAGE_DOMAIN, compliance_from_domain_report, write_domain_status

    domain_id = STAGE_DOMAIN.get(stage_id)
    if not domain_id:
        return
    report_path = DOMAIN_REPORT_FILES.get(domain_id)
    running = False
    if report_path:
        pct, metrics = compliance_from_domain_report(domain_id, report_path)
        status = "pass" if entry.get("passed", True) and pct >= 85 else "warn" if pct >= 70 else "fail"
        write_domain_status(domain_id, status=status, compliance_pct=pct, running=False, metrics=metrics, detail=entry.get("label", ""))
    else:
        passed = entry.get("passed", True)
        write_domain_status(
            domain_id,
            status="pass" if passed else "fail",
            compliance_pct=100.0 if passed else 0.0,
            running=False,
            detail=entry.get("label", ""),
        )


def run_full_audit(
    *,
    skip_website_audit: bool = False,
    skip_a11y: bool = False,
    mode: str = "full",
    domains: list[str] | None = None,
    progress_callback: Callable[[dict], None] | None = None,
) -> dict:
    """Run audit stages via orchestrator DAG; return aggregated report."""
    from audit_orchestrator import STAGE_DOMAIN, resolve_stages, write_domain_status

    started = NOW_ISO()
    stages_out: list[dict] = []
    all_complete: list[dict] = []
    all_partial: list[dict] = []
    all_gaps: list[dict] = []
    overall_ok = True

    active_stages = resolve_stages(
        AUDIT_STAGES,
        mode=mode,
        domains=domains,
        skip_website=skip_website_audit,
        skip_a11y=skip_a11y,
    )

    total = len(active_stages) or 1

    def emit_progress(idx: int, stage_id: str, status: str, detail: str = "") -> None:
        payload = {
            "status": status,
            "mode": mode,
            "started_at": started,
            "updated_at": NOW_ISO(),
            "current_stage": stage_id,
            "stage_index": idx,
            "stage_total": total,
            "progress_pct": round((idx / total) * 100, 1) if status == "running" else round(((idx + 1) / total) * 100, 1),
            "detail": detail,
        }
        write_progress(payload)
        if progress_callback:
            progress_callback(payload)

    emit_progress(0, active_stages[0]["id"] if active_stages else "", "starting", f"Modo {mode}")

    for i, st in enumerate(active_stages):
        domain_id = STAGE_DOMAIN.get(st["id"])
        if domain_id:
            write_domain_status(domain_id, status="running", running=True, detail=st["label"])

        emit_progress(i, st["id"], "running", st["label"])
        entry: dict = {
            "id": st["id"],
            "label": st["label"],
            "kind": st["kind"],
            "framework_id": st.get("framework_id", "nkos"),
        }

        if st["kind"] == "subprocess":
            res = run_subprocess_stage(st["script"])
            entry.update(res)
            if st.get("report"):
                vr = stage_validator_report(st["report"])
                entry["report_summary"] = vr
                if not vr["passed"]:
                    entry["passed"] = False
            if st["id"] in ("audit_a11y", "audit_seo", "audit_sustainability"):
                domain_report = DOMAIN_REPORT_FILES.get(st.get("framework_id", ""))
                if domain_report and domain_report.exists():
                    try:
                        dr = json.loads(domain_report.read_text(encoding="utf-8"))
                        entry["domain_report"] = {
                            "compliance_pct": dr.get("compliance_pct"),
                            "passed": dr.get("passed", res["passed"]),
                        }
                        entry["passed"] = dr.get("passed", res["passed"])
                    except json.JSONDecodeError:
                        pass
            if st["id"] == "audit_website" and res["passed"]:
                entry["website"] = stage_website_artifacts()
        elif st["kind"] == "inline":
            fn = INLINE_FNS[st["fn"]]
            res = fn() if st["fn"] != "website_artifacts" else fn(require_build=False)
            entry.update(res)

        if not entry.get("passed", True) and st["id"] in CRITICAL_STAGES:
            overall_ok = False
        elif st["kind"] == "subprocess" and st["id"] not in ("audit_website", "audit_a11y", "audit_seo", "audit_sustainability") and not entry.get("passed", True):
            overall_ok = False

        for key in ("complete_100", "partial", "gaps"):
            if key in entry:
                bucket = all_complete if key == "complete_100" else all_partial if key == "partial" else all_gaps
                for item in entry[key]:
                    item = dict(item)
                    item["stage"] = st["id"]
                    bucket.append(item)

        stages_out.append(entry)
        _update_domain_from_stage(st["id"], entry)

    finished = NOW_ISO()
    score_items = all_complete + all_partial + all_gaps
    completeness_score = round(len(all_complete) / len(score_items) * 100, 1) if score_items else 0

    report = {
        "started_at": started,
        "finished_at": finished,
        "passed": overall_ok,
        "summary": {
            "stages_total": total,
            "stages_passed": sum(1 for s in stages_out if s.get("passed", False)),
            "stages_failed": sum(1 for s in stages_out if not s.get("passed", True)),
            "complete_100_count": len(all_complete),
            "partial_count": len(all_partial),
            "gaps_count": len(all_gaps),
            "completeness_score_pct": completeness_score,
            "execution_mode": mode,
        },
        "stages": stages_out,
        "complete_100": all_complete,
        "partial": all_partial,
        "gaps": all_gaps,
        "ignore_rules": {
            "dirs": sorted(IGNORE_DIR_NAMES),
            "path_prefixes": sorted(IGNORE_PATH_PARTS),
        },
    }

    from audit_framework import enrich_audit_report

    report = enrich_audit_report(report)

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(REPORT_PATH, "w", encoding="utf-8", newline="\n") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
        f.write("\n")

    emit_progress(max(total - 1, 0), "", "done", f"Auditoria concluída — {'PASS' if overall_ok else 'FAIL'}")
    write_progress({
        "status": "done",
        "started_at": started,
        "finished_at": finished,
        "updated_at": finished,
        "progress_pct": 100,
        "passed": overall_ok,
        "report_path": str(REPORT_PATH.relative_to(ROOT)),
    })

    return report
