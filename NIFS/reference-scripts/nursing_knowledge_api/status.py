"""Status — Nursing Knowledge API."""
from __future__ import annotations

from paths import MD, load_json, tools_catalog


def collect_status() -> dict:
    canon = load_json("canonical.json")
    services = load_json("services_registry.json").get("services", {})
    sec = load_json("security.json")
    phase1 = canon.get("phases", {}).get("phase1", {}).get("services", [])

    by_phase = {"phase1": 0, "phase2": 0, "phase3": 0}
    mvp = 0
    for s in services.values():
        ph = s.get("phase", 1)
        by_phase[f"phase{ph}"] = by_phase.get(f"phase{ph}", 0) + 1
        if s.get("status") == "mvp":
            mvp += 1

    return {
        "program": canon.get("program_code", "NKA"),
        "name": canon.get("name"),
        "gateway": canon.get("gateway"),
        "services_total": len(services),
        "services_mvp": mvp,
        "phase1_services": phase1,
        "by_phase": by_phase,
        "tools_in_catalog": len(tools_catalog()),
        "auth": {
            "api_keys": sec.get("auth", {}).get("api_keys", {}).get("enabled"),
            "oauth2": sec.get("auth", {}).get("oauth2", {}).get("enabled"),
            "rate_limiting": sec.get("rate_limiting", {}).get("enabled"),
        },
        "platform_route": canon.get("platform_route"),
    }
