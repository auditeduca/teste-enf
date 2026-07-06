"""HTTP fetch — legislação MS, DOU, SES estaduais."""
from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from html import unescape
from pathlib import Path

from config import SCRAPE_CACHE


def _strip_html(html: str) -> str:
    text = re.sub(r"(?is)<script[^>]*>.*?</script>", " ", html)
    text = re.sub(r"(?is)<style[^>]*>.*?</style>", " ", text)
    text = re.sub(r"(?is)<br\s*/?>", "\n", text)
    text = re.sub(r"(?is)</p>", "\n", text)
    text = re.sub(r"(?is)</tr>", "\n", text)
    text = re.sub(r"(?is)</td>", " | ", text)
    text = re.sub(r"(?is)<[^>]+>", " ", text)
    text = unescape(text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def fetch_url(url: str, *, timeout: float = 20.0) -> dict:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "CALENF-NKD-CompulsoryNotification/1.0 (+https://github.com/CALENF-NKD)",
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "pt-BR,pt;q=0.9",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
            charset = resp.headers.get_content_charset() or "utf-8"
            html = raw.decode(charset, errors="replace")
            return {
                "ok": True,
                "url": url,
                "status": resp.status,
                "html_length": len(html),
                "text": _strip_html(html)[:120000],
            }
    except urllib.error.HTTPError as exc:
        return {"ok": False, "url": url, "error": f"HTTP {exc.code}", "status": exc.code}
    except (urllib.error.URLError, TimeoutError) as exc:
        return {"ok": False, "url": url, "error": str(exc)}


def cache_fetch(source_id: str, url: str) -> dict:
    SCRAPE_CACHE.mkdir(parents=True, exist_ok=True)
    result = fetch_url(url)
    result["source_id"] = source_id
    path = SCRAPE_CACHE / f"{source_id.replace('.', '_')}.json"
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    result["cache_path"] = str(path)
    return result
