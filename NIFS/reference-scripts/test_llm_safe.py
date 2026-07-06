"""Teste seguro de LLM — nunca imprime chaves nem conteúdo do .env."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from agent_common.env_loader import env_status, load_project_env


def main() -> int:
    load_project_env()
    status = env_status()
    print("env_file_exists:", status["env_file_exists"])
    for key, ok in status["keys"].items():
        if key.endswith("_API_KEY"):
            print(f"{key}: {'configured' if ok else 'missing'}")

    try:
        from llm_router import llm_status, route_chat
    except ImportError as exc:
        print("llm_router: FAIL", exc)
        return 1

    print("any_configured:", llm_status().get("any_configured"))

    if not status["keys"].get("ANTHROPIC_API_KEY"):
        print("claude_test: SKIP (no key)")
        return 0

    try:
        result = route_chat(
            [{"role": "user", "content": "Responda apenas: OK"}],
            task="fast_check",
            provider="claude",
            max_tokens=16,
        )
        ok = "OK" in (result.get("content") or "").upper()
        print("claude_test:", "PASS" if ok else "UNEXPECTED", "| model:", result.get("model"))
        return 0 if ok else 2
    except Exception as exc:
        print("claude_test: FAIL |", str(exc)[:120])
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
