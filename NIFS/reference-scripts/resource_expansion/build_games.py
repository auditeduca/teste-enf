"""Gerador M25 — games registry + configs runtime para o site."""
from __future__ import annotations

import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "resource_expansion"))

from agent_common.json_io import load_json, save_json_atomic  # noqa: E402
from games_catalog import GAMES_CATALOG, TARGET_GAMES, TARGET_PHASES  # noqa: E402

RES = ROOT / "datasets" / "master-data" / "resource-expansion"
REGISTRY = RES / "games_registry.json"
SITE_GAMES = ROOT / "website" / "assets" / "data" / "games"
SITE_GAMES_PT = ROOT / "website" / "pt" / "assets" / "data" / "games"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _uid(seed: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"https://calenf.nkos/game/{seed}"))


def _dataset_stats(rel: str) -> tuple[bool, int]:
    path = ROOT / rel
    if not path.is_file():
        return False, 0
    try:
        doc = load_json(path)
    except (json.JSONDecodeError, OSError):
        return False, 0
    count = doc.get("count") or len(doc.get("records", []))
    if isinstance(doc.get("pages"), dict):
        count = max(count, len(doc["pages"]))
    return count > 0, count


def _sample_ids(records: list, key: str, limit: int = 5) -> list[str]:
    out = []
    for rec in records[:limit]:
        val = rec.get(key) or rec.get("entity_code") or rec.get("id")
        if val:
            out.append(str(val))
    return out


def _build_game_config(spec: dict) -> dict:
    datasets = spec.get("datasets", [])
    min_rec = spec.get("min_records", 1)
    sources = []
    all_ready = True
    total_records = 0

    for rel in datasets:
        ok, count = _dataset_stats(rel)
        sources.append({"path": rel, "record_count": count, "ready": ok and count >= min_rec})
        total_records += count
        if not ok or count < min_rec:
            all_ready = False

    sample_content: dict = {}
    if datasets:
        primary = ROOT / datasets[0]
        if primary.is_file():
            doc = load_json(primary)
            recs = doc.get("records", [])
            if spec["mechanic"] == "quiz_battle":
                sample_content["quiz_codes"] = _sample_ids(recs, "quiz_code", 8)
            elif spec["mechanic"] == "flashcard_streak":
                sample_content["deck_codes"] = list({r.get("deck_code") for r in recs[:50] if r.get("deck_code")})[:6]
            elif spec["mechanic"] == "clinical_case":
                sample_content["exam_codes"] = _sample_ids(recs, "exam_code", 5)
            elif spec["mechanic"] == "scale_speed":
                sample_content["scale_codes"] = _sample_ids(recs, "tool_code", 10) or _sample_ids(recs, "definition_code", 10)
            elif spec["mechanic"] == "path_xp":
                sample_content["path_codes"] = _sample_ids(recs, "path_code", 6)
            elif spec["mechanic"] == "indicator_boss":
                sample_content["indicator_codes"] = _sample_ids(recs, "nursing_indicator_code", 12)

    return {
        "uuid": _uid(spec["entity_code"]),
        "entity_code": spec["entity_code"],
        "slug": spec["slug"],
        "route": spec["route"],
        "phase": spec["phase"],
        "phase_label_pt": spec["phase_label_pt"],
        "mechanic": spec["mechanic"],
        "title_pt": spec["title_pt"],
        "description_pt": spec["description_pt"],
        "status": "ready" if all_ready else "pending",
        "evidence_grade": "A",
        "content_source": "NKOS_GAMES_AGENT",
        "sources": sources,
        "source_record_count": total_records,
        "sample_content": sample_content,
        "rules": {k: v for k, v in spec.items() if k not in (
            "entity_code", "slug", "route", "phase", "phase_label_pt", "mechanic",
            "title_pt", "description_pt", "datasets", "min_records",
        )},
        "updated_at": _now(),
    }


def generate() -> dict:
    games = [_build_game_config(spec) for spec in GAMES_CATALOG]
    ready = sum(1 for g in games if g["status"] == "ready")
    phases_ready = len({g["phase"] for g in games if g["status"] == "ready"})

    registry = {
        "schema_version": "2026.2.12-games-registry",
        "generated_at": _now(),
        "entity": "GameRegistry",
        "status": "complete" if ready == TARGET_GAMES else "scaffold",
        "evidence_grade_required": "A",
        "games": games,
        "summary": {
            "games_total": len(games),
            "games_ready": ready,
            "games_completion_pct": round(ready / max(TARGET_GAMES, 1) * 100, 1),
            "phases_total": TARGET_PHASES,
            "phases_ready": phases_ready,
            "phases_completion_pct": round(phases_ready / TARGET_PHASES * 100, 1),
            "completion_pct": round((ready / max(TARGET_GAMES, 1) * 0.7 + phases_ready / TARGET_PHASES * 0.3) * 100, 1),
        },
        "generator": "scripts/resource_expansion/build_games.py",
    }

    save_json_atomic(REGISTRY, registry)

    index = {
        "schema_version": "2026.2.12",
        "generated_at": _now(),
        "hub_route": "/games",
        "title_pt": "Games — Calculadoras de Enfermagem",
        "subtitle_pt": "Quiz battle, flash streak, casos clínicos e desafios de gestão.",
        "games": [
            {
                "entity_code": g["entity_code"],
                "slug": g["slug"],
                "route": g["route"],
                "title_pt": g["title_pt"],
                "phase": g["phase"],
                "status": g["status"],
                "mechanic": g["mechanic"],
            }
            for g in games
        ],
    }

    for target_dir in (SITE_GAMES, SITE_GAMES_PT):
        target_dir.mkdir(parents=True, exist_ok=True)
        save_json_atomic(target_dir / "index.json", index)
        for g in games:
            save_json_atomic(target_dir / f"{g['slug']}.json", g)

    # Atualiza roadmap status
    roadmap_path = RES / "games_roadmap.json"
    if roadmap_path.is_file():
        roadmap = load_json(roadmap_path)
        roadmap["status"] = "complete" if ready == TARGET_GAMES else "in_progress"
        roadmap["games_ready"] = ready
        roadmap["generated_at"] = _now()
        save_json_atomic(roadmap_path, roadmap)

    return {
        "ok": ready == TARGET_GAMES,
        "path": str(REGISTRY.relative_to(ROOT)),
        "games_ready": ready,
        "games_total": len(games),
        "completion_pct": registry["summary"]["completion_pct"],
        "site_assets": str(SITE_GAMES.relative_to(ROOT)),
    }


def main() -> int:
    result = generate()
    print(
        f"M25 games: {result['games_ready']}/{result['games_total']} "
        f"({result['completion_pct']}%) -> {result['site_assets']}"
    )
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
