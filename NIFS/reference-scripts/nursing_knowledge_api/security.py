"""Security — API keys, rate limiting, identity context."""
from __future__ import annotations

import json
import time
from collections import defaultdict
from datetime import datetime, timezone
from functools import wraps
from pathlib import Path
from typing import Any, Callable

from flask import jsonify, request

from paths import LOGS, load_json

_RATE: dict[str, list[float]] = defaultdict(list)
VALID_DEV_KEYS = {
    "nkos_dev_internal": "internal",
    "nkos_dev_free": "free",
}


def _security() -> dict:
    return load_json("security.json")


def parse_identity() -> dict:
    raw = request.headers.get("X-Nursing-Identity")
    if raw:
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            pass
    body = request.get_json(silent=True) or {}
    if body.get("identity"):
        return body["identity"]
    return {
        "role": request.args.get("role", "student"),
        "country": request.args.get("country", "BR"),
        "level": request.args.get("level", "beginner"),
        "interest": request.args.get("interest"),
    }


def authenticate() -> tuple[dict | None, tuple[Any, int] | None]:
    sec = _security()
    keys_cfg = sec.get("auth", {}).get("api_keys", {})
    if not keys_cfg.get("enabled"):
        return {"tier": "internal", "key_id": "anonymous"}, None

    api_key = request.headers.get(keys_cfg.get("header", "X-API-Key"), "")
    dev_bypass = keys_cfg.get("dev_bypass", True)

    if not api_key and dev_bypass and request.remote_addr in ("127.0.0.1", "::1"):
        return {"tier": "internal", "key_id": "localhost"}, None

    tier = VALID_DEV_KEYS.get(api_key)
    if tier:
        return {"tier": tier, "key_id": api_key[:12]}, None

    if not api_key and dev_bypass:
        return {"tier": "free", "key_id": "open_dev"}, None

    return None, (jsonify({"ok": False, "error": "invalid_api_key", "hint": "Use X-API-Key header"}), 401)


def check_rate_limit(tier: str) -> tuple[bool, int]:
    sec = _security()
    if not sec.get("rate_limiting", {}).get("enabled"):
        return True, 9999
    limits = sec.get("auth", {}).get("api_keys", {}).get("tiers", {})
    rpm = limits.get(tier, limits.get("free", {})).get("rate_limit_per_minute", 30)
    key = f"{tier}:{request.remote_addr}"
    now = time.time()
    window = [t for t in _RATE[key] if now - t < 60]
    _RATE[key] = window
    if len(window) >= rpm:
        return False, 0
    _RATE[key].append(now)
    return True, rpm - len(window)


def log_request(endpoint: str, auth: dict, identity: dict, status: int) -> None:
    sec = _security()
    if not sec.get("logging", {}).get("enabled"):
        return
    LOGS.mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "endpoint": endpoint,
        "api_key_tier": auth.get("tier"),
        "identity": identity,
        "status": status,
    }
    log_file = LOGS / f"access_{datetime.now(timezone.utc).strftime('%Y%m%d')}.jsonl"
    with log_file.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def v1_protected(f: Callable) -> Callable:
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth, err = authenticate()
        if err:
            return err
        ok, remaining = check_rate_limit(auth["tier"])
        if not ok:
            return jsonify({"ok": False, "error": "rate_limit_exceeded"}), 429
        identity = parse_identity()
        resp = f(auth=auth, identity=identity, *args, **kwargs)
        if isinstance(resp, tuple):
            body, code = resp[0], resp[1]
        else:
            body, code = resp, 200
        log_request(request.path, auth, identity, code)
        if hasattr(body, "headers"):
            body.headers["X-RateLimit-Remaining"] = str(remaining)
            return body, code
        return body
    return wrapper
