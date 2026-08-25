"""Local admin control plane. Render yes. Git push never. Canonical writes never."""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from .paths import ROOT

DEPLOY_DIR = ROOT / "cko_assurance" / "deploy_requests"


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def git_status() -> dict:
    def run(args: list[str]) -> str:
        result = subprocess.run(
            args,
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        return (result.stdout or result.stderr or "").strip()

    branch = run(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    head = run(["git", "rev-parse", "--short", "HEAD"])
    porcelain = run(["git", "status", "--porcelain"])
    lines = [line for line in porcelain.splitlines() if line.strip()]
    return {
        "business_key": "CTRL-GIT-STATUS",
        "branch": branch or "UNKNOWN",
        "head": head or "UNKNOWN",
        "dirty": bool(lines),
        "changed_count": len(lines),
        "porcelain": lines[:80],
        "push": "FORBIDDEN",
        "epistemic_status": "OBSERVED",
        "generated_at": _now(),
    }


def run_render() -> dict:
    from .generate import build

    written = build()
    return {
        "business_key": "CTRL-RENDER-RUN",
        "status": "IMPLEMENTED",
        "written": len(written),
        "generated_at": _now(),
        "note": "Renderer PRESENTATION_ONLY. Não grava fórmula nem identidade canônica.",
    }


def prepare_deploy() -> dict:
    """Write a deploy changeset. Does not git add, commit, or push."""
    DEPLOY_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    status = git_status()
    payload = {
        "business_key": f"CHG-DEPLOY-{stamp}",
        "uuid": None,
        "action": "DEPLOY_PREPARE",
        "store": "GitHub",
        "push": "FORBIDDEN",
        "commit": "HUMAN_OR_AGENT_REQUIRED",
        "git": status,
        "next": [
            "Rever porcelain",
            "Não incluir fórmula/dose/threshold",
            "git add seletivo",
            "git commit",
            "git push do branch de trabalho",
        ],
        "epistemic_status": "PROPOSED",
        "generated_at": _now(),
    }
    path = DEPLOY_DIR / f"{stamp}.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    payload["path"] = str(path.relative_to(ROOT))
    return payload


def is_loopback(host: str) -> bool:
    return host in {"127.0.0.1", "localhost", "::1", "0.0.0.0"}
