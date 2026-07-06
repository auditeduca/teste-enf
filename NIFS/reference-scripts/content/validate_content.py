"""Validador CI — Master Data conteúdos pendentes."""
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
CONTENT_DIR = ROOT / "datasets" / "master-data" / "content-pending"

ENTITY_PATTERN = re.compile(r"^[A-Za-z0-9_-]+_(FLA|SIM|MMP|PRT|PKT|FAQ)_\d{3}$")


@dataclass
class ValidationReport:
    checks: int = 0
    passed: list[dict] = field(default_factory=list)
    warnings: list[dict] = field(default_factory=list)
    errors: list[dict] = field(default_factory=list)

    def ok(self, field_id: str, message: str) -> None:
        self.checks += 1
        self.passed.append({"field_id": field_id, "status": "pass", "message": message})

    def warn(self, field_id: str, message: str) -> None:
        self.checks += 1
        self.warnings.append({"field_id": field_id, "status": "warn", "message": message})

    def fail(self, field_id: str, message: str) -> None:
        self.checks += 1
        self.errors.append({"field_id": field_id, "status": "fail", "message": message})


def _load(name: str) -> dict:
    return json.loads((CONTENT_DIR / name).read_text(encoding="utf-8"))


def check_registry(rep: ValidationReport) -> None:
    for name in ("canonical.json", "content_types.json", "field_documentation.json", "modules.json", "pending_items.json"):
        path = CONTENT_DIR / name
        if not path.exists():
            rep.fail("CONTENT.registry.files", f"Arquivo ausente: {name}")
            return
        rep.ok("CONTENT.registry.files", f"{name} presente")

    pending = _load("pending_items.json")
    total = pending.get("total", 0)
    items = pending.get("items", [])
    if total != len(items):
        rep.fail("CONTENT.registry.pending_count", f"total={total} != len(items)={len(items)}")
    elif total < 1:
        rep.fail("CONTENT.registry.pending_count", "Fila vazia")
    else:
        rep.ok("CONTENT.registry.pending_count", f"{total} itens pendentes")

    types = {t["type_code"] for t in _load("content_types.json").get("content_types", [])}
    baseline = {"FLA", "SIM", "MMP", "PRT", "PKT", "FAQ"}
    if not baseline.issubset(types):
        rep.fail("CONTENT.registry.types", f"Tipos base ausentes: {baseline - types}")
    elif len(types) < 6:
        rep.fail("CONTENT.registry.types", f"Poucos tipos: {types}")
    else:
        rep.ok("CONTENT.registry.types", f"{len(types)} tipos de conteúdo ({', '.join(sorted(types))})")


def check_entity_codes(rep: ValidationReport) -> None:
    pending = _load("pending_items.json")
    for item in pending.get("items", []):
        ec = item.get("entity_code", "")
        fid = f"CONTENT.pending.{item.get('pending_id', ec)}"
        if not ENTITY_PATTERN.match(ec):
            rep.fail(fid, f"entity_code inválido: {ec}")
        else:
            rep.ok(fid, f"{ec} OK")


def check_field_docs(rep: ValidationReport) -> None:
    docs = _load("field_documentation.json")
    fields = docs.get("fields", [])
    modules_needed = {"registry", "flashcards", "simulados", "mapas_mentais", "protocolos", "guias_bolso", "faq"}
    found = {f.get("module") for f in fields}
    missing = modules_needed - found
    if missing:
        rep.fail("CONTENT.fields.modules", f"Módulos sem campos: {missing}")
    else:
        rep.ok("CONTENT.fields.modules", f"{len(fields)} campos documentados")

    for f in fields:
        roles = f.get("agent_roles") or []
        if "validate" not in roles:
            rep.warn(f["field_id"], "Sem agente validate")
        if f.get("module") != "registry" and "search" not in roles:
            rep.warn(f["field_id"], "Sem agente search")


def check_flashcards(rep: ValidationReport) -> None:
    pending = _load("pending_items.json")
    fla = [i for i in pending.get("items", []) if i.get("artifact_type") == "FLA"]
    if len(fla) < 1:
        rep.fail("CONTENT.FLA.count", "Nenhum FLA na fila")
    else:
        rep.ok("CONTENT.FLA.count", f"{len(fla)} flashcards pendentes")
    without_parent = [i for i in fla if not i.get("parent_entity_code")]
    if without_parent:
        rep.fail("CONTENT.FLA.lineage", f"{len(without_parent)} FLA sem parent SCL")
    else:
        rep.ok("CONTENT.FLA.lineage", "Todos FLA com parent_entity_code")


def check_simulados(rep: ValidationReport) -> None:
    pending = _load("pending_items.json")
    sim = [i for i in pending.get("items", []) if i.get("artifact_type") == "SIM"]
    rep.ok("CONTENT.SIM.count", f"{len(sim)} simulados pendentes") if sim else rep.fail("CONTENT.SIM.count", "Nenhum SIM")


def check_mindmaps(rep: ValidationReport) -> None:
    path = ROOT / "datasets" / "content" / "editorial" / "mindmaps.json"
    pending = _load("pending_items.json")
    mmp = [i for i in pending.get("items", []) if i.get("artifact_type") == "MMP"]
    if not path.exists():
        rep.warn("CONTENT.MMP.dataset", "mindmaps.json ausente (esperado)")
    rep.ok("CONTENT.MMP.count", f"{len(mmp)} mapas mentais pendentes")


def check_protocolos(rep: ValidationReport) -> None:
    pending = _load("pending_items.json")
    prt = [i for i in pending.get("items", []) if i.get("artifact_type") == "PRT"]
    rep.ok("CONTENT.PRT.count", f"{len(prt)} protocolos pendentes") if prt else rep.fail("CONTENT.PRT.count", "Nenhum PRT")


def check_pocket_guides(rep: ValidationReport) -> None:
    path = ROOT / "datasets" / "content" / "editorial" / "pocket_guides.json"
    pending = _load("pending_items.json")
    pkt = [i for i in pending.get("items", []) if i.get("artifact_type") == "PKT"]
    if not path.exists():
        rep.warn("CONTENT.PKT.dataset", "pocket_guides.json ausente (esperado)")
    rep.ok("CONTENT.PKT.count", f"{len(pkt)} guias pendentes")


def check_faq(rep: ValidationReport) -> None:
    pending = _load("pending_items.json")
    faq = [i for i in pending.get("items", []) if i.get("artifact_type") == "FAQ"]
    rep.ok("CONTENT.FAQ.count", f"{len(faq)} FAQs pendentes") if faq else rep.fail("CONTENT.FAQ.count", "Nenhum FAQ")


def run_validation(*, write_report: bool = True) -> ValidationReport:
    rep = ValidationReport()
    check_registry(rep)
    check_entity_codes(rep)
    check_field_docs(rep)
    check_flashcards(rep)
    check_simulados(rep)
    check_mindmaps(rep)
    check_protocolos(rep)
    check_pocket_guides(rep)
    check_faq(rep)

    if write_report:
        report = {
            "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "schema_version": "2026.2.3-content-pending",
            "checks": rep.checks,
            "passed": len(rep.passed),
            "warnings": len(rep.warnings),
            "errors": rep.errors,
            "pass_rate": round(len(rep.passed) / rep.checks * 100, 1) if rep.checks else 0,
        }
        (CONTENT_DIR / "validation_report.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    return rep


def main() -> None:
    parser = argparse.ArgumentParser(description="Valida Master Data conteúdos pendentes")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    rep = run_validation()
    if args.json:
        print(json.dumps({"ok": len(rep.errors) == 0, "checks": rep.checks, "errors": rep.errors}, ensure_ascii=False))
    else:
        print(f"Checks: {rep.checks} | Pass: {len(rep.passed)} | Warn: {len(rep.warnings)} | Fail: {len(rep.errors)}")
        for e in rep.errors:
            print(f"  FAIL {e['field_id']}: {e['message']}")
    raise SystemExit(0 if not rep.errors else 1)


if __name__ == "__main__":
    main()
