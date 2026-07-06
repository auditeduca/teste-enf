"""DeepSeek documenta desvios — APENAS fatos detectados deterministicamente."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from guardrails import clamp_score, llm_payload_limits  # noqa: E402
from paths import MD  # noqa: E402


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _prompt_template() -> str:
    from paths import load_json  # noqa: E402
    for p in load_json("prompts_registry.json").get("prompts", []):
        if p.get("prompt_id") == "DEVIATION_DOCUMENTATION_SYSTEM":
            return p["template"]
    return (
        "Documente desvios APENAS dos itens listados em factual_findings. "
        "NUNCA invente entidades, códigos ou erros. JSON estrito."
    )


def _deterministic_deviation_doc(
    *,
    run_id: str,
    context: dict,
    validation: dict,
    review: dict,
    hallucination_flags: list[str],
) -> dict:
    errors = validation.get("errors") or context.get("validation_errors") or []
    warnings = validation.get("warnings") or context.get("validation_warnings") or []
    entities = context.get("entities_summary") or {}

    deviations = []
    for err in errors[:20]:
        deviations.append({
            "type": "error",
            "code": "VALIDATION_ERROR",
            "description": str(err)[:400],
            "severity": "critical",
            "source": "deterministic",
        })
    for warn in warnings[:15]:
        deviations.append({
            "type": "warning",
            "code": "VALIDATION_WARNING",
            "description": str(warn)[:400],
            "severity": "medium",
            "source": "deterministic",
        })
    for ek, info in entities.items():
        for issue in (info.get("issues") or [])[:3]:
            deviations.append({
                "type": "entity_issue",
                "code": ek,
                "description": str(issue)[:300],
                "severity": "high" if "duplicate" in str(issue) else "medium",
                "source": "deterministic",
            })
    for flag in hallucination_flags:
        deviations.append({
            "type": "guardrail",
            "code": flag,
            "description": f"Limitador anti-alucinação: {flag}",
            "severity": "info",
            "source": "guardrails",
        })

    return {
        "run_id": run_id,
        "documented_at": _now(),
        "mode": "deterministic",
        "deviation_count": len(deviations),
        "deviations": deviations,
        "summary_pt": f"{len(errors)} erros, {len(warnings)} avisos, {len(hallucination_flags)} flags guardrail",
        "standard_reference": "NKOS envelope + validate_phases_1_7 + ENTITY_TIERS",
    }


def document_deviations(
    *,
    run_id: str,
    context: dict,
    validation: dict,
    review: dict | None = None,
    plan: dict | None = None,
    use_llm: bool = True,
    api_key: str | None = None,
) -> dict:
    """Documenta desvios fora do padrão. LLM só redige texto — fatos vêm do código."""
    review = review or {}
    hallucination_flags = (review.get("guardrails") or {}).get("hallucination_risk", [])
    if plan and plan.get("guardrails"):
        hallucination_flags = list(dict.fromkeys(
            hallucination_flags + (plan.get("guardrails") or {}).get("dropped_actions", [])
        ))

    factual = {
        "errors": (validation.get("errors") or context.get("validation_errors") or [])[:20],
        "warnings": (validation.get("warnings") or context.get("validation_warnings") or [])[:15],
        "entities_with_issues": {
            k: v.get("issues", [])
            for k, v in (context.get("entities_summary") or {}).items()
            if v.get("issues")
        },
        "precision_score": validation.get("precision_score"),
        "validation_passed": validation.get("validation_passed"),
        "hallucination_flags": hallucination_flags,
        "review_decision": review.get("decision"),
    }

    baseline = _deterministic_deviation_doc(
        run_id=run_id,
        context=context,
        validation=validation,
        review=review,
        hallucination_flags=hallucination_flags,
    )

    if not use_llm or not api_key:
        baseline["llm_skipped"] = True
        return _persist_deviation_report(baseline)

    try:
        from llm_router import route_chat_json  # noqa: WPS433

        limits = llm_payload_limits()
        messages = [
            {"role": "system", "content": _prompt_template()},
            {
                "role": "user",
                "content": (
                    "Redija documentação dos desvios com base EXCLUSIVA em factual_findings.\n"
                    "PROIBIDO adicionar desvios não listados.\n\n"
                    f"```json\n{json.dumps({'factual_findings': factual, 'baseline_deviations': baseline['deviations'][:25]}, ensure_ascii=False)[:10000]}\n```\n\n"
                    "Retorne JSON: { summary_pt, deviations: [{type, code, description, severity, remediation_pt, standard_reference}], "
                    "compliance_gap_pct, narrative_pt }"
                ),
            },
        ]
        llm = route_chat_json(
            messages,
            task="database_validation",
            payload={"api_key": api_key, **limits},
        )
        parsed = llm.get("parsed") or {}
        if isinstance(parsed, str):
            parsed = json.loads(parsed)

        # Sanitizar: só aceitar desvios cujas descrições mapeiam a factual
        factual_blob = json.dumps(factual, ensure_ascii=False).lower()
        llm_devs = parsed.get("deviations") or []
        safe_devs = []
        for d in llm_devs:
            if not isinstance(d, dict):
                continue
            desc = str(d.get("description", "")).lower()
            code = str(d.get("code", "")).lower()
            # Deve referenciar algo factual ou ser remediação de item existente
            if any(token in factual_blob for token in desc.split()[:5] if len(token) > 4):
                safe_devs.append({
                    **d,
                    "source": "deepseek_documented",
                    "description": str(d.get("description", ""))[:500],
                    "remediation_pt": str(d.get("remediation_pt", ""))[:500],
                })
            elif code in factual_blob:
                safe_devs.append({**d, "source": "deepseek_documented"})

        merged = {
            **baseline,
            "mode": "deepseek_documented",
            "llm_model": llm.get("model"),
            "summary_pt": parsed.get("summary_pt") or baseline["summary_pt"],
            "narrative_pt": str(parsed.get("narrative_pt", ""))[:2000],
            "compliance_gap_pct": clamp_score(parsed.get("compliance_gap_pct", 100 - (validation.get("precision_score") or 0))),
            "deviations": baseline["deviations"] + safe_devs[:10],
            "deviation_count": len(baseline["deviations"]) + len(safe_devs[:10]),
            "guardrails": {"llm_deviations_accepted": len(safe_devs), "llm_deviations_rejected": max(0, len(llm_devs) - len(safe_devs))},
        }
        return _persist_deviation_report(merged)
    except Exception as exc:
        baseline["llm_error"] = str(exc)[:300]
        return _persist_deviation_report(baseline)


def _persist_deviation_report(doc: dict) -> dict:
    out_dir = MD / "deviation_reports"
    out_dir.mkdir(parents=True, exist_ok=True)
    run_id = doc.get("run_id", "UNKNOWN")
    path = out_dir / f"{run_id}_deviations.json"
    path.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    latest = MD / "last_deviation_report.json"
    latest.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    doc["report_path"] = str(path)
    return doc
