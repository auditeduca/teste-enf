"""Status — Task Center."""
from __future__ import annotations

from paths import REGISTRY, MD


def collect_status() -> dict:
    import sys
    from pathlib import Path
    root = Path(__file__).resolve().parent.parent.parent
    scripts = str(root / "scripts" / "task_center")
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    from registry import list_tasks  # noqa: WPS433

    data = list_tasks(status="all", limit=500)
    return {
        "program_code": "TASK_CENTER",
        "name": "Centro de Tarefas NKOS",
        "registry_path": str(REGISTRY),
        "synced_at": data.get("synced_at"),
        "summary": data.get("summary"),
        "platform_route": "/tasks",
        "single_command": "python scripts/task_center/run_batch.py --run-all",
        "api_routes": [
            "GET /api/tasks/status",
            "GET /api/tasks/list",
            "POST /api/tasks/sync",
            "POST /api/tasks/run",
            "POST /api/tasks/run-batch",
        ],
    }
