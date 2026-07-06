"""Optional free external APIs to enhance audit precision."""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from review.ssl_utils import urlopen_request


def pagespeed_available() -> bool:
    return bool(os.environ.get("GOOGLE_PAGESPEED_API_KEY", "").strip())


def fetch_pagespeed(url: str, *, strategy: str = "mobile") -> dict[str, Any]:
    """Google PageSpeed Insights v5 — free tier with API key."""
    key = os.environ.get("GOOGLE_PAGESPEED_API_KEY", "").strip()
    if not key:
        return {"available": False, "error": "GOOGLE_PAGESPEED_API_KEY não configurada"}

    params = urllib.parse.urlencode({
        "url": url,
        "strategy": strategy,
        "category": "performance",
        "category": "accessibility",
        "category": "seo",
        "key": key,
    })
    # urllib urlencode duplicates keys — build manually
    qs = f"url={urllib.parse.quote(url)}&strategy={strategy}&category=performance&category=accessibility&category=seo&key={urllib.parse.quote(key)}"
    req = urllib.request.Request(f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?{qs}")

    try:
        with urlopen_request(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return {"available": True, "error": f"HTTP {exc.code}", "body": exc.read()[:500].decode(errors="replace")}
    except Exception as exc:
        return {"available": True, "error": str(exc)}

    cats = (data.get("lighthouseResult") or {}).get("categories") or {}
    scores = {}
    for name in ("performance", "accessibility", "seo", "best-practices"):
        block = cats.get(name) or {}
        if block.get("score") is not None:
            scores[name] = round(float(block["score"]) * 100, 1)

    return {
        "available": True,
        "url": url,
        "strategy": strategy,
        "scores": scores,
        "overall_pct": round(sum(scores.values()) / len(scores), 1) if scores else None,
    }


def enhance_domain_with_external(domain_id: str, site_url: str) -> dict[str, Any]:
    """Call external APIs when configured; never blocks local audit."""
    out: dict[str, Any] = {"domain": domain_id, "external": []}
    if domain_id in ("seo", "sustainability", "a11y") and pagespeed_available():
        ps = fetch_pagespeed(site_url)
        out["external"].append({"provider": "pagespeed", **ps})
        if ps.get("scores"):
            out["pagespeed_scores"] = ps["scores"]
    return out
