#!/usr/bin/env python3
"""Monitor consolidado — avanço dos programas master-data.

  python scripts/monitor_progress.py
  python scripts/monitor_progress.py --json
  python scripts/monitor_progress.py --refresh   # recalcula resource-expansion
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "datasets" / "metadata" / "progress_monitor.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load(rel: str) -> dict:
    p = ROOT / rel
    if not p.is_file():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        obj, _ = json.JSONDecoder().raw_decode(p.read_text(encoding="utf-8"))
        return obj if isinstance(obj, dict) else {}


def _delta(prev: dict | None, key: str, current: float) -> float | None:
    if not prev:
        return None
    old = prev.get(key)
    if old is None:
        return None
    try:
        return round(float(current) - float(old), 1)
    except (TypeError, ValueError):
        return None


def collect(*, refresh_resource: bool = False) -> dict:
    if refresh_resource:
        sys.path.insert(0, str(ROOT / "scripts" / "resource_expansion"))
        from update_progress import persist_progress  # noqa: WPS433

        persist_progress()

    prev = _load("datasets/metadata/progress_monitor.json") if OUT.is_file() else {}
    prev_snap = prev.get("snapshot") if isinstance(prev, dict) else None

    # Content pending
    cp = _load("datasets/master-data/content-pending/pending_items.json")
    cp_items = cp.get("items", [])
    cp_counts = dict(Counter(i.get("status") for i in cp_items))
    cp_applied = cp_counts.get("applied", 0)
    cp_total = len(cp_items) or cp.get("total", 0)
    cp_pct = round(cp_applied / cp_total * 100, 1) if cp_total else 0

    # Resource expansion
    cov = _load("datasets/master-data/resource-expansion/coverage_report.json")
    re_pct = cov.get("overall_completion_pct", 0)
    re_mods = cov.get("module_progress", {})

    # Global expansion
    ge = _load("datasets/master-data/global-expansion/coverage_report.json")
    ge_pct = ge.get("overall_completion_pct", 0)
    ge_seg = ge.get("progress_segments", {})

    # Doc 14
    p14 = _load("datasets/metadata/master_code_sequence_proposal.json")

    # APGAR
    apgar = _load("datasets/master-data/apgar/modules.json")

    # Library + dictionary (blockers)
    lib = _load("datasets/content/library/library_visual_assets.json")
    lib_total = lib.get("total_assets", len(lib.get("records", [])))
    lib_dl = sum(1 for r in lib.get("records", []) if r.get("status") == "downloaded")

    nd = _load("datasets/master/nursing_dictionary.json")
    nd_records = nd.get("records", [])
    nd_defs = sum(1 for r in nd_records if r.get("definition_pt") or r.get("definition"))

    med = _load("datasets/clinical/medication_dictionary.json")
    med_records = med.get("records", [])
    med_defs = sum(1 for r in med_records if r.get("definition_pt") or r.get("definition"))
    drug_refs = _load("datasets/clinical/drug_references.json")
    drug_total = len(drug_refs.get("records", []))
    med_pct = round(med_defs / drug_total * 100, 1) if drug_total else 0

    ind = _load("datasets/operations/nursing_indicators.json")
    ind_n = len(ind.get("records", []))

    # Workflows content-pending awaiting
    wf_idx = _load("datasets/master-data/content-pending/workflow/index.json")
    wf_counts = dict(Counter(w.get("status") for w in wf_idx.get("workflows", [])))

    snapshot = {
        "generated_at": _now(),
        "programs": {
            "content_pending": {
                "status": cp.get("status", "unknown"),
                "completion_pct": cp_pct,
                "applied": cp_applied,
                "total": cp_total,
                "pending": cp_counts.get("pending", 0),
                "workflows": wf_counts,
            },
            "resource_expansion": {
                "completion_pct": re_pct,
                "modules": re_mods,
                "blockers": {
                    "M22_dictionary": f"{nd_defs}/{len(nd_records)} definições",
                    "M23_library_assets": f"{lib_dl}/{lib_total} assets baixados",
                    "M21_indicators": f"{ind_n}/100 indicadores",
                },
            },
            "global_expansion": {
                "completion_pct": ge_pct,
                "segments": ge_seg,
            },
            "doc14_entity_codes": {
                "status": p14.get("status"),
                "approved_by": p14.get("approved_by"),
            },
            "apgar_pilot": {
                "completion_pct": apgar.get("overall_completion_pct"),
                "status": apgar.get("status"),
            },
            "medication_dictionary": {
                "linked": len(med_records),
                "with_definition": med_defs,
                "total_drug_references": drug_total,
                "pending": max(drug_total - len(med_records), 0),
                "completion_pct": med_pct,
                "parent_entity_type": "DrugReference",
                "code_pattern": "{CONCEPT}_DICT_{NNN}",
            },
        },
        "deltas_since_last": {
            "content_pending_pct": _delta(prev_snap, "content_pending_pct", cp_pct),
            "resource_expansion_pct": _delta(
                {"resource_expansion_pct": (prev_snap or {}).get("programs", {}).get("resource_expansion", {}).get("completion_pct")},
                "resource_expansion_pct",
                re_pct,
            ),
            "global_expansion_pct": _delta(
                {"global_expansion_pct": (prev_snap or {}).get("programs", {}).get("global_expansion", {}).get("completion_pct")},
                "global_expansion_pct",
                ge_pct,
            ),
        },
    }

    # Flat keys for simple delta
    snapshot["content_pending_pct"] = cp_pct
    snapshot["resource_expansion_pct"] = re_pct
    snapshot["global_expansion_pct"] = ge_pct

    doc = {"schema_version": "2026.2.9-progress-monitor", "snapshot": snapshot, "history": prev.get("history", [])[-19:]}
    if prev_snap:
        doc["history"].append({"at": prev_snap.get("generated_at"), "snapshot": prev_snap})
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    return snapshot


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--json", action="store_true")
    p.add_argument("--refresh", action="store_true", help="Recalcula resource-expansion antes do snapshot")
    args = p.parse_args()

    snap = collect(refresh_resource=args.refresh)

    if args.json:
        print(json.dumps(snap, ensure_ascii=False, indent=2))
    else:
        print(f"=== Progress monitor @ {snap['generated_at']} ===")
        cp = snap["programs"]["content_pending"]
        re = snap["programs"]["resource_expansion"]
        ge = snap["programs"]["global_expansion"]
        print(f"Content pending:  {cp['completion_pct']}% ({cp['applied']}/{cp['total']} applied) [{cp['status']}]")
        print(f"Resource exp.:    {re['completion_pct']}%  blockers: {re['blockers']}")
        print(f"Global exp.:      {ge['completion_pct']}%  {ge['segments']}")
        print(f"Doc 14:           {snap['programs']['doc14_entity_codes']['status']}")
        print(f"APGAR:            {snap['programs']['apgar_pilot']['completion_pct']}%")
        md = snap["programs"]["medication_dictionary"]
        print(f"Med. dictionary:  {md['completion_pct']}% ({md['with_definition']}/{md['total_drug_references']} DICT->DrugReference)")
        d = snap["deltas_since_last"]
        changed = [f"{k} {v:+.1f}" for k, v in d.items() if v is not None and v != 0]
        if changed:
            print(f"Delta vs último:  {', '.join(changed)}")
        print(f"Artefato: datasets/metadata/progress_monitor.json")

    return 0


if __name__ == "__main__":
    sys.exit(main())
