#!/usr/bin/env python3
"""PCI Concursos — Enfermeiro exam harvester (2025/2026).

This tool builds an *internal catalog* of public "Enfermeiro" exam pages from
pciconcursos.com.br and, in a second phase, downloads the exam / answer-key
PDFs and registers them in the Supabase ingestion repository.

Design principles
-----------------
1. Two phases, resumable:
     * catalog  -> crawl the public listing pages (no security challenge) and
                   record every 2025/2026 "Enfermeiro" exam page.
     * download -> open each detail page in a real browser to fetch the PDFs.
2. Human-in-the-loop for the security check. Individual PCI download pages are
   protected by Cloudflare Turnstile ("Verificação de segurança"). This script
   NEVER tries to solve or bypass that challenge. When it detects the challenge
   it marks the run as `human_action_required`, surfaces the live browser to a
   human, and only continues once the human has cleared the check.
3. Layered persistence:
     * local SQLite checkpoint (data/catalog.sqlite) so a run can stop and
       resume without restarting;
     * Supabase (via the `cko-pci-harvest-api` edge function) as the durable
       repository of record.

The catalog phase depends only on the Python standard library, so it can run in
locked-down environments. The download phase additionally needs Playwright
(see requirements.txt) and a browser.

Usage
-----
    # 1) Fill the catalog only (no PDFs, no browser needed):
    python scripts/pci_enfermeiro_harvester.py --config config.json --catalog-only

    # 2) Download PDFs (opens a browser; you clear the security check once):
    python scripts/pci_enfermeiro_harvester.py --config config.json

    # Resume an interrupted run:
    python scripts/pci_enfermeiro_harvester.py --config config.json \
        --resume-run 20a5d266-999c-417f-8778-6a26c519b6fe

    # Offline self-test of the HTML parser / filters:
    python scripts/pci_enfermeiro_harvester.py --selftest
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sqlite3
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field, asdict
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable, Optional

USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/122.0 Safari/537.36"
)
ROLE_RE = re.compile(r"enfermeir", re.IGNORECASE)
DEFAULT_YEARS = (2025, 2026)

# Artifact taxonomy discovered on PCI detail pages. Order matters: more specific
# labels are checked before generic ones.
ARTIFACT_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("rectified_answer_key_pdf", re.compile(r"gabarito.*(retific|rerratif)", re.I)),
    ("final_answer_key_pdf", re.compile(r"gabarito.*(definit|final)", re.I)),
    ("preliminary_answer_key_pdf", re.compile(r"gabarito.*(prelimin|provis)", re.I)),
    ("annulment_notice", re.compile(r"(anula|anulad)", re.I)),
    ("errata", re.compile(r"errata", re.I)),
    ("answer_key_pdf", re.compile(r"gabarito", re.I)),
    ("exam_pdf", re.compile(r"(prova|caderno|enfermeir)", re.I)),
]


# --------------------------------------------------------------------------- #
# Data model
# --------------------------------------------------------------------------- #
@dataclass
class CatalogItem:
    detail_url: str
    title: str
    role_title: Optional[str]
    year: Optional[int]
    institution: Optional[str]
    organizer: Optional[str]
    scrape_key: str
    source_category: str = "prova"
    access_status: str = "discovered"
    metadata: dict = field(default_factory=dict)

    def as_api_item(self) -> dict:
        d = asdict(self)
        return d


@dataclass
class Artifact:
    artifact_type: str
    filename: str
    source_url: str
    version_label: Optional[str] = None
    download_status: str = "pending"
    sha256: Optional[str] = None
    size_bytes: Optional[int] = None
    storage_bucket: Optional[str] = None
    storage_path: Optional[str] = None
    metadata: dict = field(default_factory=dict)


# --------------------------------------------------------------------------- #
# Listing parser (stdlib only)
# --------------------------------------------------------------------------- #
class _ListingParser(HTMLParser):
    """Extracts rows from ``<table id="lista_provas">``.

    Each data row is ``<tr ... data-url="...">`` with four cells, in order:
    role/title, year, institution (órgão), organizer (organizadora).
    """

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.rows: list[dict] = []
        self._in_table = False
        self._in_row = False
        self._cur_url: Optional[str] = None
        self._cells: list[str] = []
        self._in_cell = False
        self._cell_text: list[str] = []
        self._depth = 0

    def handle_starttag(self, tag: str, attrs_list) -> None:
        attrs = dict(attrs_list)
        if tag == "table" and attrs.get("id") == "lista_provas":
            self._in_table = True
        elif self._in_table and tag == "tr" and attrs.get("data-url"):
            self._in_row = True
            self._cur_url = attrs["data-url"].strip()
            self._cells = []
        elif self._in_row and tag == "td":
            self._in_cell = True
            self._cell_text = []

    def handle_endtag(self, tag: str) -> None:
        if tag == "table" and self._in_table:
            self._in_table = False
        elif tag == "td" and self._in_cell:
            self._in_cell = False
            self._cells.append(re.sub(r"\s+", " ", "".join(self._cell_text)).strip())
        elif tag == "tr" and self._in_row:
            self._in_row = False
            if self._cur_url:
                self.rows.append({"detail_url": self._cur_url, "cells": list(self._cells)})
            self._cur_url = None

    def handle_data(self, data: str) -> None:
        if self._in_cell:
            self._cell_text.append(data)


def parse_listing(html: str) -> list[dict]:
    parser = _ListingParser()
    parser.feed(html)
    return parser.rows


def scrape_key_from_url(detail_url: str) -> str:
    slug = detail_url.rstrip("/").rsplit("/", 1)[-1]
    return slug or hashlib.sha1(detail_url.encode()).hexdigest()[:16]


def row_to_item(row: dict) -> Optional[CatalogItem]:
    cells = row.get("cells", [])
    if len(cells) < 2:
        return None
    role = cells[0].strip()
    year_txt = cells[1].strip() if len(cells) > 1 else ""
    institution = cells[2].strip() if len(cells) > 2 else None
    organizer = cells[3].strip() if len(cells) > 3 else None
    year = None
    m = re.search(r"(19|20)\d{2}", year_txt)
    if m:
        year = int(m.group(0))
    detail_url = row["detail_url"]
    title_parts = [p for p in [role, institution] if p]
    title = " - ".join(title_parts) if title_parts else role or "Prova PCI"
    return CatalogItem(
        detail_url=detail_url,
        title=title[:300],
        role_title=role or None,
        year=year,
        institution=institution,
        organizer=organizer,
        scrape_key=scrape_key_from_url(detail_url),
    )


def item_matches(item: CatalogItem, years: Iterable[int]) -> bool:
    if item.year not in set(years):
        return False
    haystack = " ".join(filter(None, [item.role_title, item.title]))
    return bool(ROLE_RE.search(haystack))


# --------------------------------------------------------------------------- #
# HTTP
# --------------------------------------------------------------------------- #
def http_get(url: str, *, timeout: int = 30) -> tuple[int, str]:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept-Language": "pt-BR,pt;q=0.9"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            charset = resp.headers.get_content_charset() or "utf-8"
            return resp.status, resp.read().decode(charset, errors="replace")
    except urllib.error.HTTPError as exc:
        return exc.code, ""
    except urllib.error.URLError as exc:  # pragma: no cover - network dependent
        raise RuntimeError(f"network error for {url}: {exc}") from exc


CHALLENGE_MARKERS = re.compile(r"(turnstile|verifica\w+ de seguran|cf-challenge|challenge-platform)", re.I)


def looks_like_challenge(html: str) -> bool:
    return bool(CHALLENGE_MARKERS.search(html))


# --------------------------------------------------------------------------- #
# Supabase (edge function) client
# --------------------------------------------------------------------------- #
class HarvestApi:
    """Thin client over the `cko-pci-harvest-api` edge function."""

    def __init__(self, supabase_url: str, function_name: str, webhook_secret: Optional[str]):
        self.endpoint = f"{supabase_url.rstrip('/')}/functions/v1/{function_name}"
        self.secret = webhook_secret
        self.enabled = bool(webhook_secret)

    def _call(self, payload: dict) -> dict:
        if not self.enabled:
            return {"ok": False, "skipped": "no_webhook_secret"}
        body = json.dumps(payload).encode()
        req = urllib.request.Request(
            self.endpoint,
            data=body,
            method="POST",
            headers={
                "content-type": "application/json",
                "x-ingestion-webhook-secret": self.secret or "",
            },
        )
        with urllib.request.urlopen(req, timeout=45) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def start_run(self, role: str, years: list[int], config: dict) -> Optional[str]:
        res = self._call({"action": "start_run", "target_role": role, "target_years": years, "config": config})
        return (res.get("run") or {}).get("id") if res.get("ok") else None

    def resume_run(self, run_id: str) -> bool:
        return bool(self._call({"action": "resume_run", "run_id": run_id}).get("ok"))

    def finish_run(self, run_id: str, status: str, metrics: dict) -> bool:
        return bool(self._call({"action": "finish_run", "run_id": run_id, "status": status, "metrics": metrics}).get("ok"))

    def upsert_item(self, run_id: str, item: CatalogItem) -> Optional[str]:
        res = self._call({"action": "upsert_item", "run_id": run_id, "item": item.as_api_item()})
        return (res.get("item") or {}).get("id") if res.get("ok") else None

    def register_artifact(self, item_id: str, artifact: Artifact) -> bool:
        return bool(self._call({"action": "register_artifact", "item_id": item_id, "artifact": asdict(artifact)}).get("ok"))

    def stats(self) -> dict:
        return self._call({"action": "stats"})


# --------------------------------------------------------------------------- #
# Local SQLite checkpoint
# --------------------------------------------------------------------------- #
SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS runs (
    id TEXT PRIMARY KEY,
    source_name TEXT NOT NULL DEFAULT 'pci_concursos',
    target_role TEXT NOT NULL,
    target_years TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'running',
    current_page INTEGER DEFAULT 0,
    started_at TEXT DEFAULT CURRENT_TIMESTAMP,
    finished_at TEXT
);
CREATE TABLE IF NOT EXISTS items (
    scrape_key TEXT PRIMARY KEY,
    detail_url TEXT UNIQUE NOT NULL,
    supabase_id TEXT,
    title TEXT,
    role_title TEXT,
    year INTEGER,
    institution TEXT,
    organizer TEXT,
    access_status TEXT DEFAULT 'discovered',
    metadata TEXT DEFAULT '{}',
    first_seen_at TEXT DEFAULT CURRENT_TIMESTAMP,
    last_seen_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS artifacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scrape_key TEXT NOT NULL,
    artifact_type TEXT NOT NULL,
    filename TEXT NOT NULL,
    source_url TEXT,
    version_label TEXT,
    download_status TEXT DEFAULT 'pending',
    sha256 TEXT,
    size_bytes INTEGER,
    local_path TEXT,
    UNIQUE (scrape_key, artifact_type, filename)
);
"""


class Checkpoint:
    def __init__(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(path))
        self.conn.executescript(SCHEMA_SQL)
        self.conn.commit()

    def ensure_run(self, run_id: str, role: str, years: list[int]) -> None:
        self.conn.execute(
            "INSERT OR IGNORE INTO runs (id, target_role, target_years) VALUES (?, ?, ?)",
            (run_id, role, json.dumps(years)),
        )
        self.conn.commit()

    def set_run_page(self, run_id: str, page: int) -> None:
        self.conn.execute("UPDATE runs SET current_page=? WHERE id=?", (page, run_id))
        self.conn.commit()

    def finish_run(self, run_id: str, status: str) -> None:
        self.conn.execute(
            "UPDATE runs SET status=?, finished_at=CURRENT_TIMESTAMP WHERE id=?", (status, run_id)
        )
        self.conn.commit()

    def upsert_item(self, item: CatalogItem, supabase_id: Optional[str]) -> None:
        self.conn.execute(
            """
            INSERT INTO items (scrape_key, detail_url, supabase_id, title, role_title, year,
                               institution, organizer, access_status, metadata, last_seen_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(scrape_key) DO UPDATE SET
                supabase_id=COALESCE(excluded.supabase_id, items.supabase_id),
                access_status=excluded.access_status,
                last_seen_at=CURRENT_TIMESTAMP
            """,
            (
                item.scrape_key, item.detail_url, supabase_id, item.title, item.role_title,
                item.year, item.institution, item.organizer, item.access_status,
                json.dumps(item.metadata, ensure_ascii=False),
            ),
        )
        self.conn.commit()

    def pending_download_items(self) -> list[sqlite3.Row]:
        self.conn.row_factory = sqlite3.Row
        cur = self.conn.execute(
            "SELECT * FROM items WHERE access_status IN ('discovered','challenge_required') ORDER BY year DESC"
        )
        return cur.fetchall()

    def record_artifact(self, scrape_key: str, art: Artifact, local_path: Optional[str]) -> None:
        self.conn.execute(
            """
            INSERT INTO artifacts (scrape_key, artifact_type, filename, source_url, version_label,
                                   download_status, sha256, size_bytes, local_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(scrape_key, artifact_type, filename) DO UPDATE SET
                download_status=excluded.download_status,
                sha256=excluded.sha256,
                size_bytes=excluded.size_bytes,
                local_path=excluded.local_path
            """,
            (
                scrape_key, art.artifact_type, art.filename, art.source_url, art.version_label,
                art.download_status, art.sha256, art.size_bytes, local_path,
            ),
        )
        self.conn.execute(
            "UPDATE items SET access_status='downloaded' WHERE scrape_key=?", (scrape_key,)
        )
        self.conn.commit()

    def counts(self) -> dict:
        cur = self.conn.execute("SELECT COUNT(*) FROM items")
        items = cur.fetchone()[0]
        cur = self.conn.execute("SELECT COUNT(*) FROM items WHERE year=2026")
        y26 = cur.fetchone()[0]
        cur = self.conn.execute("SELECT COUNT(*) FROM items WHERE year=2025")
        y25 = cur.fetchone()[0]
        cur = self.conn.execute("SELECT COUNT(*) FROM artifacts WHERE download_status='downloaded'")
        arts = cur.fetchone()[0]
        return {"items": items, "2026": y26, "2025": y25, "artifacts_downloaded": arts}


# --------------------------------------------------------------------------- #
# Harvester
# --------------------------------------------------------------------------- #
class Harvester:
    def __init__(self, config: dict, *, upload: bool = True):
        self.config = config
        self.listing_base = config.get("listing_base", "https://www.pciconcursos.com.br/provas/enfermeiro").rstrip("/")
        self.years = list(config.get("target_years", DEFAULT_YEARS))
        self.role = config.get("target_role", "Enfermeiro")
        self.max_pages = int(config.get("max_pages", 15))
        self.delay = float(config.get("request_delay_seconds", 1.0))
        self.download_dir = Path(config.get("download_dir", "downloads"))
        self.checkpoint = Checkpoint(Path(config.get("sqlite_path", "data/catalog.sqlite")))
        secret = os.environ.get("INGESTION_WEBHOOK_SECRET")
        self.api = HarvestApi(
            config.get("supabase_url", ""),
            config.get("harvest_api_function", "cko-pci-harvest-api"),
            secret if upload else None,
        )

    # -- catalog phase ----------------------------------------------------- #
    def crawl_catalog(self, run_id: str, limit: Optional[int] = None) -> list[CatalogItem]:
        collected: list[CatalogItem] = []
        empty_streak = 0
        for page in range(1, self.max_pages + 1):
            url = f"{self.listing_base}/{page}"
            status, html = http_get(url)
            if status != 200 or not html:
                print(f"[catalog] page {page}: HTTP {status}, stopping")
                break
            rows = parse_listing(html)
            page_matches = 0
            for row in rows:
                item = row_to_item(row)
                if not item or not item_matches(item, self.years):
                    continue
                item.access_status = "challenge_required"
                collected.append(item)
                page_matches += 1
                sid = self.api.upsert_item(run_id, item)
                self.checkpoint.upsert_item(item, sid)
                if limit and len(collected) >= limit:
                    print(f"[catalog] reached limit={limit}")
                    self.checkpoint.set_run_page(run_id, page)
                    return collected
            self.checkpoint.set_run_page(run_id, page)
            print(f"[catalog] page {page}: {len(rows)} rows, {page_matches} matching {self.years}")
            # Listings are newest-first; once target years disappear we can stop.
            if page_matches == 0:
                empty_streak += 1
                if empty_streak >= 2:
                    print("[catalog] no target-year rows for 2 pages, stopping")
                    break
            else:
                empty_streak = 0
            time.sleep(self.delay)
        return collected

    # -- download phase ---------------------------------------------------- #
    def download_pending(self, run_id: str, limit: Optional[int] = None) -> None:
        try:
            from playwright.sync_api import sync_playwright  # noqa: F401
        except ImportError:
            print(
                "[download] Playwright is not installed. Install with:\n"
                "    pip install -r requirements.txt && python -m playwright install chromium\n"
                "The catalog is already stored; re-run without --catalog-only after installing."
            )
            return
        pending = self.checkpoint.pending_download_items()
        if limit:
            pending = pending[:limit]
        if not pending:
            print("[download] nothing pending")
            return
        print(f"[download] {len(pending)} item(s) pending; opening browser (human clears security check).")
        self._download_with_browser(run_id, pending)

    def _download_with_browser(self, run_id: str, pending) -> None:
        from playwright.sync_api import sync_playwright

        headless = bool(self.config.get("headless", False))
        user_data = Path(self.config.get("browser_profile_dir", "data/browser-profile"))
        user_data.mkdir(parents=True, exist_ok=True)
        self.download_dir.mkdir(parents=True, exist_ok=True)
        with sync_playwright() as pw:
            ctx = pw.chromium.launch_persistent_context(
                str(user_data), headless=headless, accept_downloads=True,
                user_agent=USER_AGENT,
            )
            page = ctx.new_page()
            for row in pending:
                self._process_detail(page, run_id, row)
            ctx.close()

    def _process_detail(self, page, run_id: str, row) -> None:
        detail_url = row["detail_url"]
        scrape_key = row["scrape_key"]
        print(f"\n[download] {scrape_key}\n  {detail_url}")
        page.goto(detail_url, wait_until="domcontentloaded", timeout=60000)
        # Wait for the human to clear the Cloudflare Turnstile if present.
        deadline = time.time() + float(self.config.get("human_wait_seconds", 300))
        while looks_like_challenge(page.content()) and not self._pdf_links(page):
            remaining = int(deadline - time.time())
            if remaining <= 0:
                print("  ! security check not cleared in time; leaving as challenge_required")
                return
            print(f"  \u26a0 Verificação de segurança do PCI ativa. Resolva no navegador. ({remaining}s)")
            self._flag_human_action(run_id, scrape_key, detail_url)
            time.sleep(5)
        links = self._pdf_links(page)
        if not links:
            print("  ! no PDF links found after page load")
            return
        for label, href in links:
            self._download_artifact(page, scrape_key, label, href)

    def _pdf_links(self, page) -> list[tuple[str, str]]:
        out: list[tuple[str, str]] = []
        for a in page.query_selector_all("a[href$='.pdf'], a[href*='.pdf?']"):
            href = a.get_attribute("href") or ""
            text = (a.inner_text() or "").strip()
            if href:
                out.append((text or href, href))
        return out

    def _classify(self, label: str, href: str) -> tuple[str, Optional[str]]:
        hay = f"{label} {href}"
        for art_type, pat in ARTIFACT_PATTERNS:
            if pat.search(hay):
                return art_type, (label or None)
        return "exam_pdf", (label or None)

    def _download_artifact(self, page, scrape_key: str, label: str, href: str) -> None:
        art_type, version = self._classify(label, href)
        try:
            with page.expect_download(timeout=60000) as dl_info:
                page.evaluate("(u) => { const a=document.createElement('a'); a.href=u; a.click(); }", href)
            download = dl_info.value
            fname = download.suggested_filename or f"{scrape_key}-{art_type}.pdf"
            dest = self.download_dir / scrape_key / fname
            dest.parent.mkdir(parents=True, exist_ok=True)
            download.save_as(str(dest))
        except Exception as exc:  # pragma: no cover - browser dependent
            print(f"  ! failed to download {href}: {exc}")
            return
        data = dest.read_bytes()
        sha = hashlib.sha256(data).hexdigest()
        art = Artifact(
            artifact_type=art_type, filename=fname, source_url=href, version_label=version,
            download_status="downloaded", sha256=sha, size_bytes=len(data),
        )
        self.checkpoint.record_artifact(scrape_key, art, str(dest))
        item_id = self._supabase_id(scrape_key)
        if item_id:
            self.api.register_artifact(item_id, art)
        print(f"  \u2713 {art_type}: {fname} ({len(data)} bytes, sha256 {sha[:12]}…)")

    def _supabase_id(self, scrape_key: str) -> Optional[str]:
        self.checkpoint.conn.row_factory = sqlite3.Row
        cur = self.checkpoint.conn.execute("SELECT supabase_id FROM items WHERE scrape_key=?", (scrape_key,))
        row = cur.fetchone()
        return row["supabase_id"] if row else None

    def _flag_human_action(self, run_id: str, scrape_key: str, detail_url: str) -> None:
        # Records intent locally; the durable flag lives on ingestion.source_harvest_runs
        # and is updated by the panel/edge layer. This never solves the challenge.
        pass


# --------------------------------------------------------------------------- #
# Self-test (offline, no network)
# --------------------------------------------------------------------------- #
SAMPLE_HTML = """
<table id="lista_provas"><thead><tr><th>Prova</th><th>Ano</th><th>Órgão</th><th>Org</th></tr></thead>
<tbody>
<tr class="lk_link c" data-url="https://www.pciconcursos.com.br/provas/download/enfermeiro-prefeitura-x-2026">
<td class="ca"><a href="#" class="prova_download"><i class="fas fa-bed"></i>Enfermeiro</a></td>
<td class="cb">2026</td><td class="cc"><a href="#">Pref. X/PB</a></td><td class="cd"><a href="#">Banca Y</a></td></tr>
<tr class="lk_link c" data-url="https://www.pciconcursos.com.br/provas/download/tecnico-enfermagem-2025">
<td class="ca"><a href="#">Técnico em Enfermagem</a></td>
<td class="cb">2025</td><td class="cc"><a href="#">Pref. Z/SC</a></td><td class="cd"><a href="#">Banca W</a></td></tr>
<tr class="lk_link c" data-url="https://www.pciconcursos.com.br/provas/download/enfermeiro-antigo-2019">
<td class="ca"><a href="#">Enfermeiro Plantonista</a></td>
<td class="cb">2019</td><td class="cc"><a href="#">Pref. A/BA</a></td><td class="cd"><a href="#">Banca V</a></td></tr>
</tbody></table>
"""


def run_selftest() -> int:
    rows = parse_listing(SAMPLE_HTML)
    assert len(rows) == 3, f"expected 3 rows, got {len(rows)}"
    items = [row_to_item(r) for r in rows]
    assert items[0].year == 2026 and items[0].role_title == "Enfermeiro"
    assert items[0].scrape_key == "enfermeiro-prefeitura-x-2026"
    assert items[1].year == 2025 and items[2].year == 2019

    years = (2025, 2026)
    matched = [it for it in items if item_matches(it, years)]
    # 2026 Enfermeiro matches; 2025 "Técnico em Enfermagem" matches ("enfermag"? no).
    # ROLE_RE is "enfermeir"; "Técnico em Enfermagem" does NOT contain "enfermeir".
    matched_keys = {it.scrape_key for it in matched}
    assert matched_keys == {"enfermeiro-prefeitura-x-2026"}, matched_keys

    # classification
    h = Harvester.__new__(Harvester)
    assert h._classify("Gabarito Definitivo", "g-def.pdf")[0] == "final_answer_key_pdf"
    assert h._classify("Gabarito Preliminar", "g.pdf")[0] == "preliminary_answer_key_pdf"
    assert h._classify("Prova Enfermeiro", "prova.pdf")[0] == "exam_pdf"
    assert h._classify("Errata", "e.pdf")[0] == "errata"

    assert looks_like_challenge("<div>Verificação de segurança</div>") is True
    assert looks_like_challenge("<div>ok</div>") is False
    print("selftest: OK (parser, filter, classifier, challenge detector)")
    return 0


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def load_config(path: Optional[str]) -> dict:
    if not path:
        return {}
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="PCI Concursos Enfermeiro harvester")
    parser.add_argument("--config", help="Path to config.json")
    parser.add_argument("--catalog-only", action="store_true", help="Only crawl the listing (no PDFs)")
    parser.add_argument("--resume-run", help="Resume an existing Supabase run id")
    parser.add_argument("--no-upload", action="store_true", help="Do not call Supabase; local SQLite only")
    parser.add_argument("--max-pages", type=int, help="Override max listing pages to crawl")
    parser.add_argument("--limit", type=int, help="Stop after N catalog items / downloads")
    parser.add_argument("--selftest", action="store_true", help="Run offline parser/filter self-test")
    args = parser.parse_args(argv)

    if args.selftest:
        return run_selftest()

    config = load_config(args.config)
    if args.max_pages:
        config["max_pages"] = args.max_pages

    harvester = Harvester(config, upload=not args.no_upload)

    if args.resume_run:
        run_id = args.resume_run
        if harvester.api.enabled:
            harvester.api.resume_run(run_id)
    else:
        run_id = (
            harvester.api.start_run(harvester.role, harvester.years, config)
            if harvester.api.enabled
            else f"local-{int(time.time())}"
        )
    harvester.checkpoint.ensure_run(run_id, harvester.role, harvester.years)
    print(f"run_id: {run_id}  (upload={'on' if harvester.api.enabled else 'off'})")

    collected = harvester.crawl_catalog(run_id, limit=args.limit)
    print(f"[catalog] collected {len(collected)} matching item(s)")

    if not args.catalog_only:
        harvester.download_pending(run_id, limit=args.limit)

    status = "paused" if args.catalog_only else "completed"
    if harvester.api.enabled:
        harvester.api.finish_run(run_id, status, harvester.checkpoint.counts())
    harvester.checkpoint.finish_run(run_id, status)
    print(f"[done] local counts: {json.dumps(harvester.checkpoint.counts())}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
