"""HTTP fetch — dados abertos ANVISA (dados.anvisa.gov.br + dados.gov.br)."""
from __future__ import annotations

import hashlib
import json
import re
import ssl
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BASE_ANVISA = "https://dados.anvisa.gov.br"
PORTAL_DADOS_GOV = "https://dados.gov.br"
ORG_SLUG = "agencia-nacional-de-vigilancia-sanitaria-anvisa"
USER_AGENT = "CALENF-NKD-ANVISA/1.0 (+https://github.com/CALENF-NKD)"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def ssl_context(*, verify: bool = True) -> ssl.SSLContext:
    ctx = ssl.create_default_context()
    if not verify:
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
    return ctx


def content_hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fetch_bytes(url: str, *, timeout: float = 120.0, verify_ssl: bool = True) -> dict:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "*/*",
            "Accept-Language": "pt-BR,pt;q=0.9",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ssl_context(verify=verify_ssl)) as resp:
            raw = resp.read()
            return {
                "ok": True,
                "url": url,
                "status": resp.status,
                "last_modified": resp.headers.get("Last-Modified"),
                "etag": resp.headers.get("ETag"),
                "content_type": resp.headers.get("Content-Type"),
                "body": raw,
                "body_length": len(raw),
                "content_hash": content_hash(raw),
                "fetched_at": _now(),
            }
    except urllib.error.HTTPError as exc:
        return {"ok": False, "url": url, "error": f"HTTP {exc.code}", "status": exc.code}
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return {"ok": False, "url": url, "error": str(exc)}


def list_anvisa_csv_catalog(*, verify_ssl: bool = True) -> dict:
    """Lista CSVs em dados.anvisa.gov.br/dados/ (fonte oficial)."""
    url = f"{BASE_ANVISA}/dados/"
    fetched = fetch_bytes(url, timeout=30.0, verify_ssl=verify_ssl)
    if not fetched.get("ok"):
        return {"ok": False, "error": fetched.get("error"), "datasets": []}
    html = fetched["body"].decode("utf-8", errors="replace")
    seen: set[str] = set()
    datasets: list[dict] = []
    for m in re.finditer(r'href="(/dados/([^"]+\.csv))"[^>]*>([^<]*)', html, re.I):
        href, fname_raw, label = m.group(1), m.group(2), m.group(3)
        fname = urllib.parse.unquote(fname_raw.split("/")[-1])
        if fname.lower() in seen:
            continue
        seen.add(fname.lower())
        slug = re.sub(r"[^a-z0-9]+", "-", fname.lower().replace(".csv", ""))[:60].strip("-")
        datasets.append({
            "source_id": f"ANV.{slug.upper().replace('-', '_')[:40]}",
            "filename": fname,
            "url": f"{BASE_ANVISA}{href}",
            "title": (label or fname).strip(),
            "fetch_mode": "csv_direct",
            "organization": "ANVISA",
            "portal_url": f"{PORTAL_DADOS_GOV}/dados/organizacoes/visualizar/{ORG_SLUG}",
        })
    return {
        "ok": True,
        "catalog_url": url,
        "generated_at": _now(),
        "datasets_total": len(datasets),
        "datasets": datasets,
    }


def fetch_dados_gov_org_datasets(*, page: int = 1, page_size: int = 50, verify_ssl: bool = False) -> dict:
    """Tenta API pública dados.gov.br (pode retornar 401 — fallback para list_anvisa_csv_catalog)."""
    q = urllib.parse.urlencode({
        "organizacao": ORG_SLUG,
        "pagina": page,
        "itens": page_size,
    })
    url = f"{PORTAL_DADOS_GOV}/api/publico/conjuntos-dados?{q}"
    fetched = fetch_bytes(url, timeout=30.0, verify_ssl=verify_ssl)
    if not fetched.get("ok"):
        return {"ok": False, "error": fetched.get("error"), "datasets": []}
    try:
        doc = json.loads(fetched["body"].decode("utf-8"))
    except json.JSONDecodeError as exc:
        return {"ok": False, "error": str(exc), "datasets": []}
    items = []
    for ds in doc.get("conjuntosDados", []):
        ident = ds.get("identificador") or ds.get("id") or ""
        items.append({
            "source_id": f"ANV.DGOV.{re.sub(r'[^A-Z0-9]', '_', ident.upper())[:40]}",
            "identificador": ident,
            "title": ds.get("titulo") or ident,
            "url": f"{PORTAL_DADOS_GOV}/dados/conjuntos-dados/{ident}",
            "fetch_mode": "dados_gov_portal",
            "organization": "ANVISA",
            "portal_url": f"{PORTAL_DADOS_GOV}/dados/organizacoes/visualizar/{ORG_SLUG}",
        })
    return {
        "ok": True,
        "total": doc.get("total", len(items)),
        "generated_at": _now(),
        "datasets": items,
    }


def cache_csv_fetch(
    cache_dir: Path,
    source_id: str,
    url: str,
    *,
    max_bytes: int | None = None,
    verify_ssl: bool = True,
) -> dict:
    cache_dir.mkdir(parents=True, exist_ok=True)
    result = fetch_bytes(url, verify_ssl=verify_ssl)
    result["source_id"] = source_id
    if result.get("ok") and max_bytes and result.get("body_length", 0) > max_bytes:
        result["truncated"] = True
        result["body"] = result["body"][:max_bytes]
        result["body_length"] = len(result["body"])
        result["content_hash"] = content_hash(result["body"])
    meta = {k: v for k, v in result.items() if k != "body"}
    if result.get("ok"):
        raw_path = cache_dir / f"{source_id.replace('.', '_')}.csv"
        raw_path.write_bytes(result["body"])
        meta["raw_path"] = str(raw_path)
        meta["raw_bytes"] = result["body_length"]
    path = cache_dir / f"{source_id.replace('.', '_')}.json"
    path.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    meta["cache_path"] = str(path)
    return meta
