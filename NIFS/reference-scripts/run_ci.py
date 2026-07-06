"""Unified CI pipeline for CALENF-NKD.

Runs the full quality gate in order and aggregates results:
  1. validate_phases_1_7.py   — referential integrity (phases 1-7)
  2. validate_phases_8_12.py  — referential integrity (phases 8-12)
  3. generate_website_pt.py   — static site build (pt-BR + locales)
  4. audit_website_pt.py      — broken links / WCAG / route coverage
  5. validate_build_report    — build-report.json, JSON-LD sample, deploy zip
  6. run_full_audit.py        — auditoria completa + relatório (com --full-audit)

Writes datasets/metadata/ci_report.json and exits non-zero if any step fails.

Usage:
  python scripts/run_ci.py                 # full pipeline
  python scripts/run_ci.py --no-build      # validators only (skip build+audit)
  python scripts/run_ci.py --pt-only       # build pt-BR only (faster dev gate)
  python scripts/run_ci.py --full-audit    # inclui auditoria completa NKOS + completude
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
ROOT = SCRIPTS.parent
REPORT = ROOT / "datasets" / "metadata" / "ci_report.json"
BUILD_REPORT = ROOT / "website" / "build-report.json"
DEPLOY_ZIP = ROOT / "website" / "nkos-site-build.zip"
NOW_ISO = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

# (id, script, ok_exit_codes, is_build_step, extra_args_fn)
STEPS = [
    ("validate_1_7", "validate_phases_1_7.py", {0}, False, lambda _: []),
    ("validate_8_12", "validate_phases_8_12.py", {0}, False, lambda _: []),
    ("build_site", "generate_website_pt.py", {0}, True, lambda args: ["--pt-only"] if "--pt-only" in args else []),
    ("audit_site", "audit_website_pt.py", {0}, True, lambda _: []),
]


def run_step(script: str, ok_codes: set[int], extra_args: list[str] | None = None) -> dict:
    cmd = [sys.executable, str(SCRIPTS / script)] + (extra_args or [])
    start = time.monotonic()
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT))
    elapsed = round(time.monotonic() - start, 2)
    tail = "\n".join((proc.stdout or "").strip().splitlines()[-6:])
    err_tail = "\n".join((proc.stderr or "").strip().splitlines()[-6:])
    return {
        "exit_code": proc.returncode,
        "passed": proc.returncode in ok_codes,
        "elapsed_s": elapsed,
        "stdout_tail": tail,
        "stderr_tail": err_tail,
    }


def validate_build_report(*, pt_only: bool) -> dict:
    """Check post-build artifacts written by generate_website_pt + build_lib."""
    start = time.monotonic()
    issues: list[str] = []

    if not BUILD_REPORT.exists():
        issues.append(f"Missing {BUILD_REPORT.relative_to(ROOT)}")
    else:
        try:
            report = json.loads(BUILD_REPORT.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            issues.append(f"Invalid JSON in build-report: {exc}")
            report = {}
        html_count = report.get("file_counts", {}).get("html", 0)
        if html_count < 200:
            issues.append(f"Unexpected HTML count: {html_count}")
        jsonld = report.get("jsonld_validation", {})
        if not jsonld.get("passed", False):
            issues.append(
                f"JSON-LD sample failed: invalid={jsonld.get('invalid_count', '?')} "
                f"missing={jsonld.get('missing_count', '?')}"
            )
        a11y = report.get("a11y_validation", {})
        if a11y and not a11y.get("passed", True):
            issues.append(f"A11y sample issues: {a11y.get('issues_count', '?')}")

    txt_report = ROOT / "website" / "build-report.txt"
    if not txt_report.exists():
        issues.append(f"Missing {txt_report.relative_to(ROOT)}")

    if not pt_only and not DEPLOY_ZIP.exists():
        issues.append(f"Missing deploy zip: {DEPLOY_ZIP.relative_to(ROOT)}")

    elapsed = round(time.monotonic() - start, 2)
    return {
        "passed": len(issues) == 0,
        "elapsed_s": elapsed,
        "issues": issues,
        "build_report": str(BUILD_REPORT.relative_to(ROOT)),
        "deploy_zip": str(DEPLOY_ZIP.relative_to(ROOT)) if not pt_only else None,
    }


def main() -> int:
    argv = sys.argv[1:]
    skip_build = "--no-build" in argv
    pt_only = "--pt-only" in argv
    results: dict[str, dict] = {}
    overall_ok = True

    print("=" * 56)
    print("CALENF-NKD — unified CI pipeline")
    if pt_only:
        print("  mode: --pt-only (locales + zip skipped in build)")
    print("=" * 56)

    for step_id, script, ok_codes, is_build, args_fn in STEPS:
        if skip_build and is_build:
            results[step_id] = {"skipped": True, "passed": True}
            print(f"[skip] {step_id} ({script})")
            continue
        extra = args_fn(argv)
        print(f"\n[run ] {step_id} ({script}) ...")
        res = run_step(script, ok_codes, extra)
        results[step_id] = res
        status = "PASS" if res["passed"] else "FAIL"
        print(f"[{status.lower():>4}] {step_id} exit={res['exit_code']} ({res['elapsed_s']}s)")
        if res["stdout_tail"]:
            for line in res["stdout_tail"].splitlines():
                print(f"        {line}")
        if not res["passed"]:
            overall_ok = False
            if res["stderr_tail"]:
                for line in res["stderr_tail"].splitlines():
                    print(f"        ! {line}")

    if not skip_build:
        print("\n[run ] validate_build_report ...")
        br = validate_build_report(pt_only=pt_only)
        results["validate_build_report"] = br
        status = "PASS" if br["passed"] else "FAIL"
        print(f"[{status.lower():>4}] validate_build_report ({br['elapsed_s']}s)")
        for issue in br.get("issues", []):
            print(f"        ! {issue}")
        if not br["passed"]:
            overall_ok = False

    if "--full-audit" in argv:
        print("\n[run ] full_audit (run_full_audit.py) ...")
        fa = run_step("run_full_audit.py", {0}, ["--skip-a11y"])
        results["full_audit"] = fa
        status = "PASS" if fa["passed"] else "FAIL"
        print(f"[{status.lower():>4}] full_audit exit={fa['exit_code']} ({fa['elapsed_s']}s)")
        if fa["stdout_tail"]:
            for line in fa["stdout_tail"].splitlines():
                print(f"        {line}")
        if not fa["passed"]:
            overall_ok = False

    report = {
        "ran_at": NOW_ISO,
        "pipeline": "validators_only" if skip_build else ("pt_only" if pt_only else "full"),
        "passed": overall_ok,
        "steps": results,
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    with open(REPORT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print("\n" + "=" * 56)
    print(f"CI result: {'PASS' if overall_ok else 'FAIL'}  ->  {REPORT}")
    print("=" * 56)
    return 0 if overall_ok else 1


if __name__ == "__main__":
    sys.exit(main())
