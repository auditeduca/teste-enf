"""HTTP fetch compartilhado — legislação (Planalto, BVS, LexML)."""
from __future__ import annotations

import json
import re
import urllib.error
import urllib.parse
import urllib.request
from html import unescape
from pathlib import Path


def strip_html(html: str) -> str:
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


def fetch_url(url: str, *, timeout: float = 25.0, accept: str = "text/html,application/xhtml+xml") -> dict:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "CALENF-NKD-Legislation/1.0",
            "Accept": accept,
            "Accept-Language": "pt-BR,pt;q=0.9",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
            charset = resp.headers.get_content_charset() or "utf-8"
            body = raw.decode(charset, errors="replace")
            last_mod = resp.headers.get("Last-Modified")
            etag = resp.headers.get("ETag")
            is_html = "html" in (resp.headers.get("Content-Type") or "").lower() or body.lstrip().startswith("<")
            return {
                "ok": True,
                "url": url,
                "status": resp.status,
                "last_modified": last_mod,
                "etag": etag,
                "body_length": len(body),
                "text": strip_html(body)[:150000] if is_html else body[:150000],
                "raw_excerpt": body[:2000] if not is_html else None,
            }
    except urllib.error.HTTPError as exc:
        return {"ok": False, "url": url, "error": f"HTTP {exc.code}", "status": exc.code}
    except (urllib.error.URLError, TimeoutError) as exc:
        return {"ok": False, "url": url, "error": str(exc)}


def cache_fetch(cache_dir: Path, source_id: str, url: str, *, timeout: float = 25.0) -> dict:
    cache_dir.mkdir(parents=True, exist_ok=True)
    result = fetch_url(url, timeout=timeout)
    result["source_id"] = source_id
    path = cache_dir / f"{source_id.replace('.', '_')}.json"
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    result["cache_path"] = str(path)
    return result


def lexml_search(keyword: str, *, max_results: int = 5) -> dict:
    """Busca LexML (HTML parse leve — API pública instável)."""
    q = urllib.parse.quote(keyword)
    url = f"https://www.lexml.gov.br/busca/search?keyword={q}&smode=simple"
    fetched = fetch_url(url, timeout=20.0)
    hits = []
    if fetched.get("ok") and fetched.get("text"):
        for m in re.finditer(r"(?i)(Lei|Decreto|Constituição)[^\n]{5,120}", fetched["text"]):
            hits.append(m.group(0).strip()[:120])
            if len(hits) >= max_results:
                break
    return {
        "ok": fetched.get("ok", False),
        "keyword": keyword,
        "url": url,
        "hits": hits,
        "error": fetched.get("error"),
    }
