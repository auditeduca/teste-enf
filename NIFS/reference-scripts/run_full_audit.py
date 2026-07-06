#!/usr/bin/env python3
"""Full project audit — validators, completeness, website (ignores node_modules).

Usage:
  python scripts/run_full_audit.py
  python scripts/run_full_audit.py --skip-website
  python scripts/run_full_audit.py --skip-a11y

Writes datasets/metadata/full_audit_report.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

from audit_lib import REPORT_PATH, run_full_audit  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description="CALENF-NKD full audit")
    ap.add_argument("--skip-website", action="store_true", help="Skip audit_website_pt.py")
    ap.add_argument("--skip-a11y", action="store_true", help="Skip audit_website_a11y_pt.py")
    args = ap.parse_args()

    print("=" * 60)
    print("CALENF-NKD — auditoria completa")
    print("  (ignora node_modules, dist, .git, locales duplicados)")
    print("=" * 60)

    report = run_full_audit(
        skip_website_audit=args.skip_website,
        skip_a11y=args.skip_a11y,
    )

    s = report["summary"]
    print(f"\nResultado: {'PASS' if report['passed'] else 'FAIL'}")
    print(f"  Estágios: {s['stages_passed']}/{s['stages_total']} OK")
    print(f"  100% completo: {s['complete_100_count']}")
    print(f"  Parcial:       {s['partial_count']}")
    print(f"  Lacunas:       {s['gaps_count']}")
    print(f"  Score:         {s['completeness_score_pct']}%")
    print(f"\nRelatório: {REPORT_PATH}")

    for st in report["stages"]:
        mark = "OK" if st.get("passed", False) else "FAIL"
        print(f"  [{mark}] {st['id']} ({st.get('elapsed_s', 0)}s)")

    if report["gaps"]:
        print("\n--- Lacunas (amostra) ---")
        for g in report["gaps"][:12]:
            label = g.get("entity") or g.get("label", "?")
            pct = g.get("pct", "?")
            print(f"  · {label}: {pct}%")

    return 0 if report["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
