"""Importa módulos de agentes sem colisão com content_agents/graph.py etc."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent  # scripts/

_SHADOW_MODULES = frozenset({
    "graph",
    "catalog",
    "status",
    "config",
    "apply_entry",
    "validators",
    "structure",
    "scrape",
    "fetch",
    "validate_program",
    "discover",
    "extract",
    "relate",
    "fetch_stage",
    "apply_entry",
})


def prepare_agent_package(agent_subdir: str) -> Path:
    """Coloca o pacote do agente na frente do sys.path e remove cache conflitante."""
    agent_dir = ROOT / agent_subdir
    if not agent_dir.is_dir():
        raise FileNotFoundError(f"Agent package not found: {agent_dir}")

    agent_dir_resolved = agent_dir.resolve()
    agent_path = str(agent_dir_resolved)
    agent_norm = agent_path.lower()
    scripts_root = ROOT.resolve()

    # Evict cached top-level helper modules (paths.py, status.py, workflow_runner.py,
    # …) that belong to a *sibling* agent package under scripts/<pkg>/. Each agent
    # package ships its own paths.py/status.py, so a stale cache from another package
    # would otherwise leak (e.g. nursing_knowledge_api/paths shadowing this package's).
    for name in list(sys.modules.keys()):
        if "." in name:
            continue
        mod = sys.modules.get(name)
        mod_file = getattr(mod, "__file__", None) if mod is not None else None
        if not mod_file:
            continue
        try:
            parent = Path(mod_file).resolve().parent
        except (OSError, ValueError):
            continue
        # Only evict modules that live directly in scripts/<pkg>/ (not scripts/*.py
        # root helpers like dataset_io, nor nested packages) and are not the target.
        if parent.parent == scripts_root and parent != agent_dir_resolved:
            del sys.modules[name]

    for p in (agent_path, str(ROOT / "apgar_agents"), str(ROOT)):
        while p in sys.path:
            sys.path.remove(p)
    sys.path.insert(0, str(ROOT))
    sys.path.insert(0, str(ROOT / "apgar_agents"))
    sys.path.insert(0, agent_path)

    return agent_dir
