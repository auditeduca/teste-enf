"""Validador resource expansion."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
RES = ROOT / "datasets" / "master-data" / "resource-expansion"


@dataclass
class Report:
    checks: int = 0
    errors: list[dict] = field(default_factory=list)
    passed: list[dict] = field(default_factory=list)

    def ok(self, fid: str, msg: str) -> None:
        self.checks += 1
        self.passed.append({"field_id": fid, "message": msg})

    def fail(self, fid: str, msg: str) -> None:
        self.checks += 1
        self.errors.append({"field_id": fid, "message": msg})


def run_validation() -> Report:
    rep = Report()
    for name in ("canonical.json", "modules_registry.json", "slides_registry.json", "games_roadmap.json", "coverage_report.json"):
        if not (RES / name).exists():
            rep.fail(f"RES.files.{name}", "ausente")
        else:
            rep.ok(f"RES.files.{name}", "presente")

    lib = ROOT / "datasets" / "content" / "library" / "library_visual_assets.json"
    if not lib.is_file():
        rep.fail("RES.library_assets", "manifest ausente")
    else:
        doc = json.loads(lib.read_text(encoding="utf-8"))
        rep.ok("RES.library_assets", f"{doc.get('total_assets', 0)} assets")

    slides = json.loads((RES / "slides_registry.json").read_text(encoding="utf-8")) if (RES / "slides_registry.json").is_file() else {}
    if slides.get("total_decks", 0) < 50:
        rep.fail("RES.slides", f"{slides.get('total_decks', 0)} < 50 decks")
    else:
        rep.ok("RES.slides", f"{slides['total_decks']} decks")

    mods = json.loads((RES / "modules_registry.json").read_text(encoding="utf-8")) if (RES / "modules_registry.json").is_file() else {}
    required = {"M19_cv_generator", "M20_scales_generator", "M21_indicators_generator", "M22_dictionary", "M23_library_assets", "M24_tool_slides", "M25_games"}
    found = {m["module_id"] for m in mods.get("modules", [])}
    missing = required - found
    if missing:
        rep.fail("RES.modules", f"ausentes: {missing}")
    else:
        rep.ok("RES.modules", f"{len(found)} módulos M19–M25")

    games = json.loads((RES / "games_roadmap.json").read_text(encoding="utf-8")) if (RES / "games_roadmap.json").is_file() else {}
    if len(games.get("phases", [])) < 3:
        rep.fail("RES.games", "roadmap incompleto")
    else:
        rep.ok("RES.games", f"{len(games['phases'])} fases")

    return rep


if __name__ == "__main__":
    import sys

    r = run_validation()
    print(f"Checks: {r.checks} | Pass: {len(r.passed)} | Fail: {len(r.errors)}")
    for e in r.errors:
        print(f"  FAIL {e['field_id']}: {e['message']}")
    sys.exit(1 if r.errors else 0)
