"""Agentes de carreiras — empregos/cursos/trilhas por país, evidência Grau A + DeepSeek."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
CAREERS = ROOT / "datasets" / "master-data" / "careers"
GENERATED = ROOT / "datasets" / "generated" / "careers"
RUNS = CAREERS / "agent_runs"
PROMPTS = Path(__file__).resolve().parent / "prompts"

sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "apgar_agents"))
from agent_common.sanitize import sanitize_agent_result  # noqa: E402


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def validate_registry() -> dict:
    reg = json.loads((CAREERS / "country_registry.json").read_text(encoding="utf-8"))
    errors = []
    for item in reg.get("items", []):
        if item.get("evidence_grade_required") != "A":
            errors.append({"entity_code": item["entity_code"], "msg": "evidence != A"})
        if not item.get("entity_code", "").startswith("CAREER_"):
            errors.append({"entity_code": item.get("entity_code"), "msg": "bad code pattern"})
    return {"ok": not errors, "errors": errors, "total": reg.get("total_items", 0)}


def _scaffold_country(cc: str, items: list[dict]) -> dict:
    out_dir = GENERATED / cc.lower()
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "generated_at": _now(),
        "country_code": cc,
        "evidence_grade": "A",
        "status": "scaffold",
        "artifacts": [],
    }
    for item in items:
        manifest["artifacts"].append({
            "entity_code": item["entity_code"],
            "artifact_type": item["artifact_type"],
            "status": "scaffold",
            "licensing_hint": item.get("licensing_hint"),
        })
    path = out_dir / "manifest.json"
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"country_code": cc, "manifest_path": str(path.relative_to(ROOT)), "artifacts": len(manifest["artifacts"]), "ok": True}


def _generate_country_llm(cc: str, items: list[dict], *, api_key: str, model: str | None = None) -> dict:
    from apgar_agents.llm import chat_json, resolve_model  # noqa: E402

    country_name = items[0].get("country_name", cc) if items else cc
    licensing = items[0].get("licensing_hint", "") if items else ""
    system = (PROMPTS / "generate.md").read_text(encoding="utf-8")
    messages = [
        {"role": "system", "content": system},
        {
            "role": "user",
            "content": json.dumps(
                {
                    "country_code": cc,
                    "country_name": country_name,
                    "licensing_hint": licensing,
                    "who_region": items[0].get("who_region") if items else None,
                    "entity_codes": [i["entity_code"] for i in items],
                },
                ensure_ascii=False,
            ),
        },
    ]
    content = chat_json(messages, api_key=api_key, model=resolve_model(model), max_tokens=8192)
    out_dir = GENERATED / cc.lower()
    out_dir.mkdir(parents=True, exist_ok=True)
    content_path = out_dir / "content.json"
    doc = sanitize_agent_result(content if isinstance(content, dict) else {"raw": content})
    doc["generated_at"] = _now()
    doc["country_code"] = cc
    doc["evidence_grade"] = doc.get("evidence_grade", "A")
    doc["status"] = "awaiting_approval"
    content_path.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    manifest = _scaffold_country(cc, items)
    manifest["content_path"] = str(content_path.relative_to(ROOT))
    manifest["status"] = "llm_generated"
    manifest["llm"] = "deepseek"
    mpath = out_dir / "manifest.json"
    mdoc = json.loads(mpath.read_text(encoding="utf-8"))
    mdoc.update({k: manifest[k] for k in ("status", "llm", "content_path") if k in manifest})
    mpath.write_text(json.dumps(mdoc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def run_careers(
    *,
    countries: list[str] | None = None,
    limit: int = 10,
    api_key: str | None = None,
    use_llm: bool = False,
    model: str | None = None,
    rebuild: bool = True,
) -> dict:
    if rebuild:
        from build_registry import main as build_main  # noqa: E402

        build_main()

    if use_llm and not api_key:
        return sanitize_agent_result({
            "ok": False,
            "error": "DeepSeek API key obrigatória — defina DEEPSEEK_API_KEY ou use --api-key / plataforma NKP",
            "validation_ok": False,
        })

    val = validate_registry()
    reg = json.loads((CAREERS / "country_registry.json").read_text(encoding="utf-8"))
    by_cc: dict[str, list] = {}
    for item in reg.get("items", []):
        by_cc.setdefault(item["country_code"], []).append(item)

    target_ccs = countries or sorted(by_cc.keys())
    if not countries:
        target_ccs = target_ccs[:limit]

    country_results = []
    for cc in target_ccs:
        items = by_cc.get(cc, [])
        if not items:
            country_results.append({"country_code": cc, "ok": False, "error": "not in registry"})
            continue
        try:
            if use_llm and api_key:
                country_results.append(_generate_country_llm(cc, items, api_key=api_key, model=model))
            else:
                country_results.append(_scaffold_country(cc, items))
        except Exception as exc:
            country_results.append({"country_code": cc, "ok": False, "error": str(exc)})

    report = sanitize_agent_result({
        "generated_at": _now(),
        "validation_ok": val["ok"],
        "validation_errors": val["errors"],
        "countries_processed": len(country_results),
        "countries_ok": sum(1 for r in country_results if r.get("ok")),
        "use_llm": use_llm,
        "llm_provider": "deepseek" if use_llm else None,
        "results": country_results,
        "evidence_grade": "A",
        "ok": val["ok"] and all(r.get("ok") for r in country_results),
    })

    RUNS.mkdir(parents=True, exist_ok=True)
    run_path = RUNS / f"run_{_now().replace(':', '').replace('-', '')[:15]}.json"
    run_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report["run_path"] = str(run_path.relative_to(ROOT))
    return report
