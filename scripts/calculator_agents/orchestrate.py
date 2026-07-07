"""Orquestrador de segurança — DAG validate → scan → correct → re-scan."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from .correct import run_correction
from .env import env_status, llm_enabled, load_env
from .validate import DELIVERY_HTML, run_validation

REPORT_DIR = Path(__file__).resolve().parents[2] / "artifacts" / "security"

EXCLUDED_SLUGS = frozenset({
    "calculadora-template",
    "calculadora-template-v2",
    "calculadora-preview",
    "index",
    "mapa-do-site",
})

# Padrões de risco em HTML/JS (defesa em profundidade no conteúdo estático)
SECRET_PATTERNS = [
    (r"sk-[a-zA-Z0-9]{20,}", "openai_key_leak"),
    (r"AKIA[0-9A-Z]{16}", "aws_key_leak"),
    (r"DEEPSEEK_API_KEY\s*=\s*['\"][^'\"]+['\"]", "api_key_in_source"),
    (r"ANTHROPIC_API_KEY\s*=\s*['\"][^'\"]+['\"]", "api_key_in_source"),
    (r"password\s*[:=]\s*['\"][^'\"]{4,}['\"]", "hardcoded_password"),
    (r"Bearer\s+[a-zA-Z0-9._-]{20,}", "bearer_token_in_html"),
]

UNSAFE_JS_PATTERNS = [
    (r"\beval\s*\(", "eval_usage"),
    (r"new\s+Function\s*\(", "dynamic_function"),
    (r"document\.write\s*\(", "document_write"),
    (r"javascript:\s*void", "javascript_uri"),
]

A11Y_REQUIRED = [
    ('href="#main-content"', "missing_skip_link"),
    ('id="main-content"', "missing_main_landmark"),
    ('id="site-header"', "missing_header_placeholder"),
    ('id="site-a11y"', "missing_a11y_placeholder"),
]

STRUCTURE_BLOCKLIST = [
    "cip-section",
    "cog-section-wrapper",
    "cip-kg-links",
    "disclaimer-card",
]


@dataclass
class SecurityFinding:
    slug: str
    severity: str  # critical | high | medium | low
    code: str
    message: str


@dataclass
class SecurityScanReport:
    root: str
    pages_scanned: int = 0
    findings: list[SecurityFinding] = field(default_factory=list)

    def add(self, slug: str, severity: str, code: str, message: str) -> None:
        self.findings.append(SecurityFinding(slug, severity, code, message))

    def summary(self) -> dict:
        by_sev = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for f in self.findings:
            by_sev[f.severity] = by_sev.get(f.severity, 0) + 1
        return {
            "pages_scanned": self.pages_scanned,
            "total_findings": len(self.findings),
            "by_severity": by_sev,
        }

    def to_dict(self) -> dict:
        return {
            "root": self.root,
            **self.summary(),
            "findings": [
                {"slug": f.slug, "severity": f.severity, "code": f.code, "message": f.message}
                for f in self.findings
            ],
        }


def scan_page_security(html_path: Path, report: SecurityScanReport) -> None:
    slug = html_path.stem
    content = html_path.read_text(encoding="utf-8", errors="replace")
    report.pages_scanned += 1

    for pattern, code in SECRET_PATTERNS:
        if re.search(pattern, content, re.IGNORECASE):
            report.add(slug, "critical", code, f"Padrão sensível detectado: {code}")

    for pattern, code in UNSAFE_JS_PATTERNS:
        if re.search(pattern, content):
            report.add(slug, "high", code, f"Padrão JS inseguro: {code}")

    for marker, code in A11Y_REQUIRED:
        if marker not in content:
            report.add(slug, "medium", code, f"Requisito de acessibilidade ausente")

    for block in STRUCTURE_BLOCKLIST:
        if f'class="{block}"' in content:
            report.add(slug, "medium", "blocked_section", f"Seção bloqueada presente: {block}")

    if content.count("calc-engine-v2.js") > 1:
        report.add(slug, "low", "duplicate_script", "calc-engine-v2.js referenciado mais de uma vez")

    if 'type="application/json" id="tool-config"' not in content:
        if 'data-page=' in content or "calcForm" in content:
            report.add(slug, "high", "missing_tool_config", "Calculadora sem tool-config embutido")

    # Scripts externos sem crossorigin em CDNs (informativo)
    for m in re.finditer(r'<script[^>]+src="(https?://[^"]+)"[^>]*>', content):
        tag = m.group(0)
        if "cdn" in m.group(1).lower() and "crossorigin" not in tag:
            report.add(slug, "low", "cdn_no_crossorigin", f"Script CDN sem crossorigin: {m.group(1)[:60]}")


def run_security_scan(
    *,
    root: Path | None = None,
    slugs: list[str] | None = None,
) -> SecurityScanReport:
    root = root or DELIVERY_HTML
    report = SecurityScanReport(root=str(root))

    if slugs:
        paths = [root / f"{s}.html" for s in slugs if s not in EXCLUDED_SLUGS]
    else:
        paths = []
        for html_path in sorted(root.glob("*.html")):
            if html_path.stem in EXCLUDED_SLUGS:
                continue
            text = html_path.read_text(encoding="utf-8", errors="replace")
            if 'id="tool-config"' in text:
                paths.append(html_path)

    for html_path in paths:
        if html_path.is_file():
            scan_page_security(html_path, report)

    return report


@dataclass
class OrchestrationResult:
    started_at: str
    finished_at: str
    mode: str
    env: dict
    stages: dict
    gate_passed: bool
    corrections_applied: int
    report_path: str | None = None

    def to_dict(self) -> dict:
        d = {
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "mode": self.mode,
            "env": self.env,
            "stages": self.stages,
            "gate_passed": self.gate_passed,
            "corrections_applied": self.corrections_applied,
        }
        if self.report_path:
            d["report_path"] = self.report_path
        return d


def orchestrate(
    *,
    slugs: list[str] | None = None,
    mode: str = "pre_deploy",
    auto_correct: bool = True,
    use_llm: bool = False,
    write_report: bool = True,
) -> OrchestrationResult:
    """DAG de segurança: scan → validate → correct → re-scan → validate."""
    load_env()
    started = datetime.now(timezone.utc).isoformat()
    stages: dict = {}
    corrections = 0

    # Stage 1: security scan (baseline)
    scan_before = run_security_scan(slugs=slugs)
    stages["security_scan_before"] = scan_before.to_dict()

    # Stage 2: structural validation
    validation_before = run_validation(slugs=slugs)
    stages["validate_before"] = validation_before.to_dict()

    # Stage 3: safe corrections (no LLM unless explicitly enabled + keys present)
    correction_reports = []
    if auto_correct:
        target_slugs: list[str] = list(slugs) if slugs else []
        if not target_slugs:
            root = DELIVERY_HTML
            for p in root.glob("*.html"):
                if p.stem in EXCLUDED_SLUGS:
                    continue
                if 'id="tool-config"' in p.read_text(encoding="utf-8", errors="replace"):
                    target_slugs.append(p.stem)

        llm_on = use_llm and llm_enabled()
        for slug in target_slugs:
            rep = run_correction(slug, use_llm=llm_on, sync_json=True, normalize_footer=True)
            if rep.actions:
                corrections += 1
            correction_reports.append(rep.to_dict())
    stages["corrections"] = correction_reports

    # Stage 4: re-scan
    scan_after = run_security_scan(slugs=slugs)
    stages["security_scan_after"] = scan_after.to_dict()

    # Stage 5: final validation
    validation_after = run_validation(slugs=slugs)
    stages["validate_after"] = validation_after.to_dict()

    finished = datetime.now(timezone.utc).isoformat()

    critical_after = sum(1 for f in scan_after.findings if f.severity == "critical")
    high_after = sum(1 for f in scan_after.findings if f.severity == "high")
    val_errors = validation_after.to_dict()["errors"]

    gate_passed = critical_after == 0 and high_after == 0 and val_errors == 0

    result = OrchestrationResult(
        started_at=started,
        finished_at=finished,
        mode=mode,
        env=env_status(),
        stages=stages,
        gate_passed=gate_passed,
        corrections_applied=corrections,
    )

    if write_report:
        REPORT_DIR.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        out = REPORT_DIR / f"orchestration_{ts}.json"
        result.report_path = str(out)
        out.write_text(json.dumps(result.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")

    return result
