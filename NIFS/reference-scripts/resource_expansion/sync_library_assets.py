"""Baixa assets visuais de calculadorasdeenfermagem.com.br → website/assets/."""
from __future__ import annotations

import json
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
MANIFEST = ROOT / "datasets" / "content" / "library" / "library_visual_assets.json"
SITE_URL = "https://calculadorasdeenfermagem.com.br"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _download(url: str, dest: Path, timeout: int = 8) -> bool:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.is_file() and dest.stat().st_size > 0:
        return True
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "CALENF-NKD-AssetSync/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read()
        if len(data) < 100:
            return False
        dest.write_bytes(data)
        return True
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError):
        return False


def sync(*, limit: int = 50, include_fallback: bool = False) -> dict:
    if not MANIFEST.is_file():
        from build_registry import main as build_main  # noqa: WPS433

        build_main()
    doc = json.loads(MANIFEST.read_text(encoding="utf-8"))
    ok, fail, skip = 0, 0, 0
    processed = 0
    # Prioridade: ícones SVG e logos conhecidos (paths reais no site)
    priority_urls = [
        ("website/assets/images/logotipo_website.webp", f"{SITE_URL}/assets/images/logotipo_website.webp"),
        ("website/assets/images/homepage-hero.webp", f"{SITE_URL}/assets/images/homepage-hero.webp"),
    ]
    for local, url in priority_urls:
        if processed >= limit:
            break
        dest = ROOT / local.replace("/", "\\") if "\\" in str(ROOT) else ROOT / local
        processed += 1
        if _download(url, dest):
            ok += 1
        else:
            fail += 1

    for rec in doc.get("records", []):
        if processed >= limit:
            break
        if rec.get("fallback") and not include_fallback:
            skip += 1
            continue
        url = rec.get("remote_url") or rec.get("thumbnail_remote")
        local = rec.get("local_path")
        if not url or not local:
            skip += 1
            continue
        processed += 1
        dest = ROOT / local.replace("/", "\\") if "\\" in str(ROOT) else ROOT / local
        if _download(url, dest):
            rec["status"] = "downloaded"
            rec["downloaded_at"] = _now()
            ok += 1
        else:
            rec["status"] = "download_failed"
            fail += 1

    doc["last_sync_at"] = _now()
    doc["sync_stats"] = {"ok": ok, "fail": fail, "skip": skip, "processed": processed}
    MANIFEST.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # Sync cópia pt/
    pt_manifest = ROOT / "website" / "pt" / "assets" / "data" / "library_visual_assets.json"
    pt_manifest.parent.mkdir(parents=True, exist_ok=True)
    pt_manifest.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"sync: {ok} ok, {fail} fail, {skip} skip")
    return doc["sync_stats"]


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("--limit", type=int, default=30)
    p.add_argument("--fallback", action="store_true")
    args = p.parse_args()
    sync(limit=args.limit, include_fallback=args.fallback)
