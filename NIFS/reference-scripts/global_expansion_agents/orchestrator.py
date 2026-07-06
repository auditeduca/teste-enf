"""Agentes global expansion — Grau A, perfis, países."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "global_expansion_agents"))
sys.path.insert(0, str(ROOT / "scripts" / "content_agents"))
sys.path.insert(0, str(ROOT / "scripts" / "apgar_agents"))

from agent_common.sanitize import sanitize_agent_result  # noqa: E402
from global_expansion.validate_global import run_validation  # noqa: E402

EXP = ROOT / "datasets" / "master-data" / "global-expansion"
RUNS = EXP / "agent_runs"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def run_profile_module(profile_key: str, *, api_key: str | None, use_llm: bool) -> dict:
    matrix = json.loads((EXP / "profile_content_matrix.json").read_text(encoding="utf-8"))
    prof = matrix.get("profiles", {}).get(profile_key)
    if not prof:
        raise KeyError(profile_key)

    results = []
    artifact_to_field = {
        "SIM": "CONTENT.SIM.exam_structure",
        "FLA": "CONTENT.FLA.deck_structure",
        "PRT": "CONTENT.PRT.checklist_steps",
        "ART": "CONTENT.PKT.sections",
        "SCL": "CONTENT.FLA.linked_entity_code",
        "CAL": "CONTENT.SIM.exam_structure",
        "QIZ": "CONTENT.FAQ.questions",
        "CAR": "CONTENT.FAQ.questions",
        "EMP": "CONTENT.FAQ.questions",
    }

    ca = str(ROOT / "scripts" / "content_agents")
    aa = str(ROOT / "scripts" / "apgar_agents")
    for p in (ca, aa):
        if p in sys.path:
            sys.path.remove(p)
    sys.path.insert(0, aa)
    sys.path.insert(0, ca)
    import graph as content_graph  # noqa: E402

    for mod in prof.get("modules", []):
        field_id = artifact_to_field.get(mod["artifact"], "CONTENT.FAQ.questions")
        try:
            r = content_graph.run_field(field_id, api_key=api_key if use_llm else None, use_llm=use_llm)
            results.append({"module": mod["module"], "field_id": field_id, "ok": (r.get("validation") or {}).get("validation_passed")})
        except Exception as exc:
            results.append({"module": mod["module"], "error": str(exc), "ok": False})

    return sanitize_agent_result({
        "profile": profile_key,
        "evidence_grade": "A",
        "modules_run": results,
        "ok": all(x.get("ok") for x in results),
    })


def run_i18n_module(*, api_key: str | None, use_llm: bool, model: str | None = None, limit: int = 10) -> dict:
    i18n_path = EXP / "i18n_coverage_report.json"
    if not i18n_path.exists():
        return sanitize_agent_result({"module": "i18n_world", "ok": False, "error": "run build_registry.py first"})

    if use_llm and api_key:
        sys.path.insert(0, str(ROOT / "scripts" / "global_expansion"))
        from i18n_llm import run_i18n_batch  # noqa: E402

        batch = run_i18n_batch(api_key=api_key, model=model, limit=limit)
        cov = json.loads(i18n_path.read_text(encoding="utf-8"))
        reg = json.loads((EXP / "i18n_code_registry.json").read_text(encoding="utf-8"))
        return sanitize_agent_result({
            "module": "i18n_world",
            "llm_provider": "deepseek",
            "site_locales": cov.get("site_locales"),
            "i18n_items": reg.get("total_items"),
            "home_translated": batch.get("home_translated"),
            "batch": batch,
            "evidence_grade": "A",
            "ok": batch.get("ok") and cov.get("site_locales", 0) >= 30,
        })

    if use_llm and not api_key:
        return sanitize_agent_result({
            "module": "i18n_world",
            "ok": False,
            "error": "DeepSeek API key obrigatória para tradução i18n",
        })

    cov = json.loads(i18n_path.read_text(encoding="utf-8"))
    reg = json.loads((EXP / "i18n_code_registry.json").read_text(encoding="utf-8"))
    ok = cov.get("site_locales", 0) >= 30 and reg.get("total_items", 0) >= 300
    return sanitize_agent_result({
        "module": "i18n_world",
        "site_locales": cov.get("site_locales"),
        "i18n_items": reg.get("total_items"),
        "home_translated": cov.get("home_translated"),
        "evidence_grade": "A",
        "ok": ok,
    })


def run_careers_module(*, api_key: str | None, use_llm: bool, limit: int = 10, model: str | None = None) -> dict:
    import importlib.util

    path = ROOT / "scripts" / "career_agents" / "orchestrator.py"
    spec = importlib.util.spec_from_file_location("career_orchestrator", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    r = mod.run_careers(api_key=api_key, use_llm=use_llm, rebuild=False, limit=limit, model=model)
    return sanitize_agent_result({"module": "careers_global", **{k: r.get(k) for k in ("ok", "countries_ok", "countries_processed", "validation_ok", "run_path")}})


def run_global(*, profiles: list[str] | None = None, api_key: str | None = None, use_llm: bool = False, model: str | None = None, rebuild: bool = True, careers_limit: int = 10, i18n_limit: int = 10) -> dict:
    if use_llm and not api_key:
        return sanitize_agent_result({
            "ok": False,
            "error": "DeepSeek API key obrigatória — DEEPSEEK_API_KEY, --api-key ou chave na plataforma NKP",
            "validation_ok": False,
        })
    if rebuild:
        from global_expansion.build_registry import main as build_main  # noqa: E402

        build_main()
        try:
            from global_expansion.build_user_profiles import generate as build_profiles  # noqa: WPS433

            build_profiles()
        except Exception:
            pass

    rep = run_validation()
    profile_keys = profiles or ["estudante", "profissional", "gestor", "academico"]
    profile_results = [run_profile_module(k, api_key=api_key, use_llm=use_llm) for k in profile_keys]
    i18n_result = run_i18n_module(api_key=api_key, use_llm=use_llm, model=model, limit=i18n_limit)
    careers_result = run_careers_module(api_key=api_key, use_llm=use_llm, limit=careers_limit, model=model)

    i18n_cov = {}
    if (EXP / "i18n_coverage_report.json").exists():
        i18n_cov = json.loads((EXP / "i18n_coverage_report.json").read_text(encoding="utf-8"))

    report = sanitize_agent_result({
        "generated_at": _now(),
        "validation_ok": len(rep.errors) == 0,
        "validation_errors": rep.errors,
        "profiles": profile_results,
        "i18n": i18n_result,
        "careers": careers_result,
        "coverage": json.loads((EXP / "coverage_report.json").read_text(encoding="utf-8")) if (EXP / "coverage_report.json").exists() else {},
        "i18n_coverage": i18n_cov,
        "ok": (
            len(rep.errors) == 0
            and all(p.get("ok") for p in profile_results)
            and i18n_result.get("ok")
            and careers_result.get("ok")
        ),
    })

    RUNS.mkdir(parents=True, exist_ok=True)
    path = RUNS / f"run_{_now().replace(':', '').replace('-', '')[:15]}.json"
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report["run_path"] = str(path.relative_to(ROOT))

    from global_expansion.update_progress import persist_global_progress  # noqa: E402

    prog = persist_global_progress(last_run=report)
    report["overall_completion_pct"] = prog.get("overall_completion_pct", 0)
    report["progress_segments"] = prog.get("segments", {})
    return report
