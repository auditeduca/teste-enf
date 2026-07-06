"""Status — Nursing Studio."""
from __future__ import annotations

from pathlib import Path

from paths import MD, OUT, editing_blocks, formats, load_json, templates


def collect_status() -> dict:
    agents = load_json("agents_registry.json").get("agents", [])
    imgs = list(OUT.glob("*.svg")) if OUT.exists() else []
    return {
        "program": "NKOS_STUDIO",
        "name": "Calculadoras de Enfermagem Studio",
        "formats": len(formats()),
        "editing_blocks": len(editing_blocks()),
        "templates_seed": len(templates()),
        "agents": len(agents),
        "generated_images": len(imgs),
        "output_dir": str(OUT),
        "master_data_path": str(MD),
        "graph_integrated": True,
    }
