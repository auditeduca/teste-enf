"""Bootstrap physical country partitions from global compliance dataset.

Creates datasets/by-country/{CC}/compliance_rules.json and content_requests.json
from the monolithic sources. Safe to re-run (idempotent).

Usage:
  python scripts/bootstrap_country_partitions.py
"""
from __future__ import annotations

import json
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

from dataset_io import write_envelope
from partition_lib import COUNTRY_ENTITY_FILES, COUNTRY_FRAMEWORKS, DATASETS, SUPPORTED_COUNTRIES

NOW = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _load_global(path: str) -> dict:
    with open(DATASETS / path, encoding="utf-8") as f:
        return json.load(f)


def _split_compliance(global_env: dict) -> dict[str, list]:
    by_country: dict[str, list] = {cc: [] for cc in SUPPORTED_COUNTRIES}
    for rec in global_env.get("records", []):
        fw = rec.get("framework", "")
        for cc, frameworks in COUNTRY_FRAMEWORKS.items():
            if fw in frameworks:
                row = deepcopy(rec)
                row.setdefault("country_code", cc)
                by_country[cc].append(row)
    return by_country


def _empty_content_envelope(template: dict, country: str) -> dict:
    env = {k: v for k, v in template.items() if k != "records"}
    env["country_code"] = country
    env["partition"] = "country"
    env["records"] = []
    env["count"] = 0
    env["generated_at"] = NOW
    env["note"] = f"Country partition {country} — ContentRequest runtime"
    return env


def main() -> None:
    compliance_global = _load_global("metadata/compliance_rules.json")
    content_template = _load_global("content/nkos/content_requests.json")
    split = _split_compliance(compliance_global)

    manifest = {
        "generated_at": NOW,
        "schema_version": "2026.1.0",
        "strategy": "physical_v2",
        "countries": {},
    }

    for cc in SUPPORTED_COUNTRIES:
        cc_dir = DATASETS / "by-country" / cc
        cc_dir.mkdir(parents=True, exist_ok=True)

        comp_env = {k: v for k, v in compliance_global.items() if k != "records"}
        comp_env["entity"] = "ComplianceRule"
        comp_env["country_code"] = cc
        comp_env["partition"] = "country"
        comp_env["source_global"] = "metadata/compliance_rules.json"
        comp_env["records"] = split[cc]
        comp_env["count"] = len(split[cc])
        comp_env["generated_at"] = NOW
        write_envelope(f"by-country/{cc}/compliance_rules.json", comp_env)

        content_env = _empty_content_envelope(content_template, cc)
        content_env["entity"] = "ContentRequest"
        write_envelope(f"by-country/{cc}/content_requests.json", content_env)

        manifest["countries"][cc] = {
            "compliance_rules": len(split[cc]),
            "content_requests": 0,
            "frameworks": COUNTRY_FRAMEWORKS[cc],
        }
        print(f"{cc}: {len(split[cc])} compliance rules")

    manifest_path = DATASETS / "by-country" / "manifest.json"
    with open(manifest_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print("Wrote", manifest_path)


if __name__ == "__main__":
    main()
