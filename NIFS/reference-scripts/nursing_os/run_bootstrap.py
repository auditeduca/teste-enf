#!/usr/bin/env python3
"""Nursing OS bootstrap — validate domains, regenerate OG pilot, status."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from status import collect_status  # noqa: E402


def main() -> int:
    p = argparse.ArgumentParser(description="Nursing OS Global")
    p.add_argument("--status", action="store_true")
    p.add_argument("--bootstrap", action="store_true", help="Regenera OG piloto + valida domínios")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    result = {}
    if args.bootstrap:
        veip = ROOT / "scripts" / "visual_intelligence_agents"
        sys.path.insert(0, str(veip))
        from og_generator import generate_all  # noqa: WPS433

        og = generate_all(locale="pt-BR")
        result["og_bootstrap"] = og
        result["status"] = collect_status()
    else:
        result = collect_status()

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        st = result.get("status", result)
        m = st.get("metrics", {})
        print(f"Nursing OS: {st.get('name')} · {len(st.get('domains', []))} domínios")
        print(f"  OG: {m.get('og_manifest_entries')}/{m.get('og_templates')} · Artigos: {m.get('clinical_articles')} · Agentes: {m.get('ai_agents_registered')}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
