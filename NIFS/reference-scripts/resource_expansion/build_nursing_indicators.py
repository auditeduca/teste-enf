"""Gerador M21 — expande nursing_indicators.json até 100 registros."""
from __future__ import annotations

import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "resource_expansion"))

from agent_common.json_io import load_json, save_json_atomic  # noqa: E402
from indicator_catalog import INDICATOR_CATALOG, TARGET_COUNT  # noqa: E402

OUTPUT = ROOT / "datasets" / "operations" / "nursing_indicators.json"
EDITION = "2026"
SOURCE = "NKOS_CUSTOM"
BENCHMARK = "NDNQI / COFEN / JCI 2026"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _uid(seed: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"https://calenf.nkos/indicator/{seed}"))


def _category(code: str) -> str:
    prefix = code.replace("IND.", "").split(".")[0]
    domains = {
        "FALL": "seguranca_paciente",
        "PRESSURE": "pele_tegumentar",
        "MED": "medicamentos",
        "HAND": "ipc",
        "PAIN": "conforto",
        "SAE": "documentacao",
        "CVC": "ipc",
        "CAUTI": "ipc",
        "VAP": "ipc",
        "CLABSI": "ipc",
        "SSUR": "ipc",
        "PHLEBITIS": "ipc",
        "EXTUBATION": "respiratorio",
        "RESTRAINT": "saude_mental",
        "STAFF": "gestao_pessoas",
        "SKILL": "gestao_pessoas",
        "OVERTIME": "gestao_pessoas",
        "ABSENTEEISM": "gestao_pessoas",
        "TURNOVER": "gestao_pessoas",
        "READMISSION": "transicao_cuidados",
        "LOS": "eficiencia",
        "MORTALITY": "resultados_clinicos",
        "SEPSIS": "resultados_clinicos",
        "EARLY": "seguranca_paciente",
        "SATISFACTION": "experiencia",
        "DISCHARGE": "transicao_cuidados",
        "NUTRITION": "nutricao",
        "VTE": "resultados_clinicos",
        "OR": "cirurgico",
        "LABOR": "materno_infantil",
        "NEONATAL": "materno_infantil",
        "BREASTFEED": "materno_infantil",
        "KANGAROO": "materno_infantil",
        "APGAR": "materno_infantil",
        "ED": "urgencia",
        "ICU": "critico",
        "RRT": "critico",
        "CODE": "critico",
        "ONC": "oncologia",
        "CHEMO": "oncologia",
        "DIALYSIS": "renal",
        "TELEHEALTH": "digital",
        "EHR": "digital",
        "NCPD": "educacao",
        "COMPETENCY": "educacao",
        "MENTORSHIP": "educacao",
        "BURNOUT": "gestao_pessoas",
    }
    return domains.get(prefix, "qualidade_enfermagem")


def build_indicator_record(code: str, name: str, unit: str, direction: str, *, existing: dict | None = None) -> dict:
    if existing:
        return existing
    return {
        "uuid": _uid(code),
        "nursing_indicator_code": code,
        "name_pt": name,
        "unit_pt": unit,
        "direction": direction,
        "formula": "numerator / denominator * factor",
        "benchmark_source": BENCHMARK,
        "category": _category(code),
        "domain": "operations",
        "edition": EDITION,
        "content_source": SOURCE,
        "status": "active",
        "created_at": _now(),
        "updated_at": _now(),
    }


def generate(*, target: int = TARGET_COUNT) -> dict:
    existing_doc = load_json(OUTPUT) if OUTPUT.is_file() else {}
    by_code = {
        r["nursing_indicator_code"]: r
        for r in existing_doc.get("records", [])
        if r.get("nursing_indicator_code")
    }

    added = 0
    updated = 0
    records = []
    catalog_codes = set()

    for code, name, unit, direction in INDICATOR_CATALOG[:target]:
        catalog_codes.add(code)
        prev = by_code.get(code)
        rec = build_indicator_record(code, name, unit, direction, existing=prev)
        if prev:
            # Enriquecer registros antigos sem category
            if not prev.get("category") and rec.get("category"):
                prev = {**prev, "category": rec["category"], "updated_at": _now()}
                updated += 1
            records.append(prev)
        else:
            records.append(rec)
            added += 1

    # Preservar códigos extras já no dataset (não catalogados)
    for code, rec in by_code.items():
        if code not in catalog_codes:
            records.append(rec)

    env = {k: v for k, v in existing_doc.items() if k != "records"}
    env.setdefault("schema_version", "2026.2.10")
    env.setdefault("entity", "NursingIndicator")
    env.setdefault("nkos_phase", 10)
    env.setdefault("micro_phase", "10.7")
    env.setdefault("template_id", "T10.7")
    env.setdefault("edition", EDITION)
    env.setdefault("content_source", SOURCE)
    env.setdefault("reference_page", "/gestao/indicadores")
    env["records"] = records
    env["count"] = len(records)
    env["target"] = target
    env["generated_at"] = _now()
    env["generator"] = "scripts/resource_expansion/build_nursing_indicators.py"
    env["import_status"] = "complete" if len(records) >= target else "scaffold"

    save_json_atomic(OUTPUT, env)

    return {
        "ok": True,
        "path": str(OUTPUT.relative_to(ROOT)),
        "total": len(records),
        "added": added,
        "updated": updated,
        "target": target,
        "completion_pct": min(100, round(len(records) / target * 100)),
    }


def main() -> int:
    import argparse

    p = argparse.ArgumentParser(description="Gerador M21 — indicadores de enfermagem")
    p.add_argument("--target", type=int, default=TARGET_COUNT)
    args = p.parse_args()
    result = generate(target=args.target)
    print(
        f"M21 indicadores: {result['total']}/{result['target']} "
        f"({result['completion_pct']}%) — +{result['added']} novos, {result['updated']} enriquecidos"
    )
    return 0 if result["total"] >= min(args.target, len(INDICATOR_CATALOG)) else 1


if __name__ == "__main__":
    raise SystemExit(main())
