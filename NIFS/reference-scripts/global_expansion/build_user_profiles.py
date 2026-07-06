"""Gerador de perfis de usuário — 4 perfis × 5 módulos Grau A."""
from __future__ import annotations

import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from agent_common.json_io import load_json, save_json_atomic  # noqa: E402

EXP = ROOT / "datasets" / "master-data" / "global-expansion"
PROFILE_CONFIG = ROOT / "website" / "assets" / "data" / "user-profile-config.json"
MATRIX_PATH = EXP / "profile_content_matrix.json"
OUTPUT = EXP / "user_profiles_registry.json"

PROFILE_KEYS = ("estudante", "profissional", "gestor", "academico")

# module name → rota + dataset alvo para verificar prontidão
MODULE_BINDINGS: dict[str, dict] = {
    "simulados": {"route": "/simulados", "dataset": "datasets/education/simulated_exams.json", "min_records": 1},
    "flashcards": {"route": "/flashcards", "dataset": "datasets/education/flashcards.json", "min_records": 1},
    "trilhas": {"route": "/trilhas", "dataset": "datasets/content/editorial/template_pages.json", "min_records": 1},
    "quiz": {"route": "/quiz", "dataset": "datasets/content/editorial/template_pages.json", "min_records": 1},
    "calculadoras": {"route": "/calculadoras", "dataset": "datasets/clinical/clinical_tools_catalog.json", "min_records": 10},
    "carreiras": {"route": "/carreiras", "dataset": "datasets/master-data/careers/country_registry.json", "min_records": 100},
    "escalas": {"route": "/escalas", "dataset": "datasets/clinical/clinical_tools_catalog.json", "min_records": 10},
    "protocolos": {"route": "/protocolos", "dataset": "datasets/clinical/institutional_protocols.json", "min_records": 1},
    "medicamentos": {"route": "/medicamentos", "dataset": "datasets/clinical/drug_references.json", "min_records": 100},
    "ferramentas": {"route": "/ferramentas", "dataset": "datasets/clinical/clinical_tools_catalog.json", "min_records": 10},
    "empregos": {"route": "/empregos", "dataset": "datasets/master-data/careers/country_registry.json", "min_records": 100},
    "indicadores": {"route": "/gestao/indicadores", "dataset": "datasets/operations/nursing_indicators.json", "min_records": 50},
    "staffing": {"route": "/gestao/staffing", "dataset": "datasets/clinical/clinical_tools_catalog.json", "min_records": 10},
    "sae": {"route": "/sae", "dataset": "datasets/clinical/institutional_protocols.json", "min_records": 1},
    "sbar": {"route": "/sbar", "dataset": "datasets/content/site/user_profile_experience.json", "min_records": 0},
    "biblioteca": {"route": "/biblioteca", "dataset": "datasets/content/library/library_visual_assets.json", "min_records": 10},
    "artigos": {"route": "/artigos", "dataset": "datasets/content/editorial/articles.json", "min_records": 1},
    "nanda": {"route": "/nanda", "dataset": "datasets/clinical/taxonomy.json", "min_records": 50},
}


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _uid(seed: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"https://calenf.nkos/profile/{seed}"))


def _dataset_ready(rel: str, min_records: int) -> tuple[bool, int]:
    path = ROOT / rel.replace("/", "\\") if "\\" in str(ROOT) else ROOT / rel
    if not path.is_file():
        return False, 0
    try:
        doc = load_json(path)
    except (json.JSONDecodeError, OSError):
        return False, 0
    count = doc.get("count") or doc.get("total_items") or doc.get("total_count") or len(doc.get("records", []))
    if isinstance(doc.get("pages"), dict):
        count = max(count, len(doc["pages"]))
    if min_records <= 0:
        return True, count
    return count >= min_records, count


def generate() -> dict:
    matrix = load_json(MATRIX_PATH)
    config = load_json(PROFILE_CONFIG) if PROFILE_CONFIG.is_file() else {}
    locale_matrix = load_json(EXP / "locale_profile_matrix.json") if (EXP / "locale_profile_matrix.json").is_file() else {}

    profiles_out = []
    total_modules = 0
    ready_modules = 0

    for key in PROFILE_KEYS:
        prof_matrix = matrix.get("profiles", {}).get(key, {})
        prof_ui = config.get("profiles", {}).get(key, {})
        if not prof_matrix:
            continue

        modules = []
        for mod in prof_matrix.get("modules", []):
            name = mod.get("module", "")
            binding = MODULE_BINDINGS.get(name, {"route": f"/{name}", "dataset": "", "min_records": 0})
            rel = binding.get("dataset", "")
            min_rec = binding.get("min_records", 0)
            ready, rec_count = _dataset_ready(rel, min_rec) if rel else (True, 0)
            total_modules += 1
            if ready:
                ready_modules += 1

            modules.append({
                "module": name,
                "artifact": mod.get("artifact"),
                "priority": mod.get("priority"),
                "evidence_grade": mod.get("evidence_grade", "A"),
                "route": binding.get("route", f"/{name}"),
                "target_dataset": rel or None,
                "record_count": rec_count,
                "status": "ready" if ready else "pending",
            })

        profiles_out.append({
            "profile_key": key,
            "entity_code": prof_ui.get("profile_code") or f"PROFILE.{key.upper()}",
            "label_pt": prof_ui.get("label") or key,
            "description_pt": prof_ui.get("description", ""),
            "icon": prof_ui.get("icon"),
            "quick_links": prof_ui.get("quick_links", []),
            "priority_modules": prof_ui.get("priority_modules", []),
            "modules": modules,
            "modules_ready": sum(1 for m in modules if m["status"] == "ready"),
            "modules_total": len(modules),
            "completion_pct": round(sum(1 for m in modules if m["status"] == "ready") / max(len(modules), 1) * 100),
        })

    locales_count = len(locale_matrix.get("locales", {}))
    locale_target = 30
    config_profiles = len(config.get("profiles", {}))

    env = {
        "schema_version": "2026.2.11-user-profiles",
        "generated_at": _now(),
        "entity": "UserProfileRegistry",
        "profiles": profiles_out,
        "summary": {
            "profile_count": len(profiles_out),
            "modules_total": total_modules,
            "modules_ready": ready_modules,
            "modules_completion_pct": round(ready_modules / max(total_modules, 1) * 100, 1),
            "locale_matrix_locales": locales_count,
            "locale_matrix_pct": min(100, round(locales_count / locale_target * 100)),
            "ui_config_profiles": config_profiles,
        },
        "generator": "scripts/global_expansion/build_user_profiles.py",
    }

    mod_pct = env["summary"]["modules_completion_pct"]
    loc_pct = env["summary"]["locale_matrix_pct"]
    ui_pct = 100 if config_profiles >= 4 else round(config_profiles / 4 * 100)
    overall = round(mod_pct * 0.5 + loc_pct * 0.3 + ui_pct * 0.2, 1)
    env["summary"]["overall_profiles_pct"] = overall

    save_json_atomic(OUTPUT, env)

    return {
        "ok": overall >= 100,
        "path": str(OUTPUT.relative_to(ROOT)),
        "profiles": len(profiles_out),
        "modules_ready": ready_modules,
        "modules_total": total_modules,
        "modules_completion_pct": mod_pct,
        "locale_matrix_pct": loc_pct,
        "overall_profiles_pct": overall,
    }


def main() -> int:
    result = generate()
    print(
        f"Perfis: {result['profiles']} | módulos {result['modules_ready']}/{result['modules_total']} "
        f"({result['modules_completion_pct']}%) | overall {result['overall_profiles_pct']}%"
    )
    return 0 if result["overall_profiles_pct"] >= 100 else 1


if __name__ == "__main__":
    raise SystemExit(main())
