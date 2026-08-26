"""Extraction agents: Fetch → Parse → Integrity → CAAT → IPE → Link.

MAKER (fetch/parse) ≠ CHECKER (CAAT/IPE) ≠ AUDITOR (human). Agents write to
cko_inbox / registries. They do not promote HTML to data/tools and do not
declare clinical PASS.
"""

from __future__ import annotations

import hashlib
import json
import re
import zipfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from http.client import IncompleteRead

from .paths import ROOT, TOOLS_DIR

UA = "CKO-FetchAgent/1.0 (origin recovery; calculadorasdeenfermagem)"
UA_BROWSER = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
ORIGIN = "https://www.calculadorasdeenfermagem.com.br/"
DRIVE_PAGES_FULL_ID = "1tJ-AEv3_KpEQxNa3lMuY7A80skFtw4IK"
PAGES_FULL_SHA256 = "0ca5fe5f1f689a5da96bd0453c3fa8f658123d0c5072c8c244f526e1c09a6136"
PAGES_FULL_BYTES = 9141800

ORIGIN_URLS = {
    "footer.html": ORIGIN + "footer.html",
    "menu-global.html": ORIGIN + "menu-global.html",
    "global-body-elements.html": ORIGIN + "global-body-elements.html",
    "img/icontopbar1-calculadoras-de-enfermagem.webp": ORIGIN + "img/icontopbar1-calculadoras-de-enfermagem.webp",
    "img/iconrodape1-80-calculadoras-de-enfermagem.webp": ORIGIN + "img/iconrodape1-80-calculadoras-de-enfermagem.webp",
    "sitemap.xml": ORIGIN + "sitemap.xml",
}

REGULATED_PAGES = [
    ("API-CAND-COFEN", "COFEN", "https://www.cofen.gov.br/"),
    ("API-CAND-ANVISA", "ANVISA", "https://www.gov.br/anvisa/pt-br"),
    ("API-CAND-MS", "Ministério da Saúde", "https://www.gov.br/saude/pt-br"),
]

CHROME_IDS = (
    "global-header-container",
    "language-selector-placeholder",
    "footer-placeholder",
    "barraAcessibilidade",
)

FORBIDDEN_IN_PROJECTION = (
    "adsbygoogle",
    "googleads",
    "doubleclick",
    'type="email"',
    "cdn.jsdelivr",
    "opendyslexic",
)

PILOT_SLUGS = {"gotejamento", "meows", "cinco-ts-pcr", "simulado-tecnico", "dimensionamento"}


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _dump(path: Path, payload: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def _http_get(url: str, timeout: int = 20, *, user_agent: str | None = None, accept: str | None = None) -> dict:
    rec: dict = {"url": url}
    agents = [user_agent] if user_agent else [UA]
    gov_hosts = (
        "planalto.gov.br", "iso.org", "gov.br", "cofen.gov.br", "coren-sp.gov.br",
        "dados.gov.br", "opendatasus.saude.gov.br", "bvsms.saude.gov.br",
        "camara.leg.br", "senado.leg.br", "congressonacional.leg.br", "normas.leg.br",
    )
    if any(host in url for host in gov_hosts) and not user_agent:
        agents = [UA_BROWSER, UA]
    last_error = None
    accept_header = accept or "text/html,application/xhtml+xml,application/json,*/*"
    for agent in agents:
        try:
            req = Request(url, headers={"User-Agent": agent, "Accept": accept_header})
            with urlopen(req, timeout=timeout) as resp:
                body = resp.read()
                rec.update({
                    "http_status": getattr(resp, "status", None) or resp.getcode(),
                    "bytes": len(body),
                    "sha256": _sha256_bytes(body),
                    "final_url": resp.geturl(),
                    "body": body,
                    "epistemic_status": "OBSERVED",
                    "user_agent": agent,
                })
                return rec
        except HTTPError as err:
            last_error = err
            rec.update({
                "http_status": err.code,
                "error": f"HTTPError {err.code}",
                "epistemic_status": "EVIDENCE_PENDING",
            })
            if err.code == 403:
                continue
            break
        except IncompleteRead as err:
            last_error = err
            rec.update({
                "http_status": None,
                "error": f"IncompleteRead: {str(err)[:180]}",
                "epistemic_status": "EVIDENCE_PENDING",
            })
            continue
        except (URLError, TimeoutError, OSError) as err:
            last_error = err
            rec.update({
                "http_status": None,
                "error": f"{type(err).__name__}: {str(err)[:180]}",
                "epistemic_status": "EVIDENCE_PENDING",
            })
            continue
    if last_error and "error" not in rec:
        rec["error"] = str(last_error)[:180]
    return rec


def fetch_origin(*, network: bool) -> dict:
    """AG-FETCH-ORIGIN — snapshot chrome from own production origin."""
    inbox = ROOT / "cko_inbox" / "origin"
    files = []
    if network:
        for rel, url in ORIGIN_URLS.items():
            if rel == "sitemap.xml":
                continue
            rec = _http_get(url)
            rec.pop("body", None)
            rec["rel"] = rel
            files.append(rec)
    manifest_path = inbox / "MANIFEST.json"
    observed = []
    if manifest_path.exists():
        observed = json.loads(manifest_path.read_text(encoding="utf-8")).get("files") or []
    return {
        "agent_id": "AG-FETCH-ORIGIN",
        "class": "ACQUISITION",
        "role": "MAKER",
        "network": network,
        "origin": ORIGIN,
        "live_fetches": files,
        "inbox_manifest_files": len(observed),
        "promotes_to_md": False,
        "status": "OBSERVED" if observed or files else "EVIDENCE_PENDING",
    }


def fetch_regulated_pages(*, network: bool) -> dict:
    """AG-FETCH-REGULATED — official HTML pages, not invented REST APIs."""
    dest = ROOT / "cko_inbox" / "extracted" / "regulated_pages.json"
    pages = []
    if network:
        for key, name, url in REGULATED_PAGES:
            rec = _http_get(url)
            body = rec.pop("body", b"")
            title = None
            if body:
                match = re.search(r"<title[^>]*>(.*?)</title>", body.decode("utf-8", errors="replace"), re.I | re.S)
                if match:
                    title = re.sub(r"\s+", " ", match.group(1)).strip()[:200]
            pages.append({
                "business_key": key,
                "name": name,
                "url": url,
                "kind": "REGULATED_HTML_PAGE",
                "api_base_url": None,
                "http_status": rec.get("http_status"),
                "bytes": rec.get("bytes"),
                "sha256": rec.get("sha256"),
                "title": title,
                "error": rec.get("error"),
                "epistemic_status": rec.get("epistemic_status"),
                "note": "Página HTML pública observada. Não é API REST. base_url de API permanece null.",
            })
        _dump(dest, {
            "business_key": "IPE-REGULATED-PAGES-001",
            "uuid": None,
            "status": "SOURCE_DERIVED",
            "captured_at": _now(),
            "pages": pages,
        })
    elif dest.exists():
        pages = json.loads(dest.read_text(encoding="utf-8")).get("pages") or []
    return {
        "agent_id": "AG-FETCH-REGULATED",
        "class": "ACQUISITION",
        "role": "MAKER",
        "network": network,
        "pages": [{k: v for k, v in p.items() if k != "body"} for p in pages],
        "api_base_url_set": False,
        "promotes_to_md": False,
        "status": "OBSERVED" if pages else "EVIDENCE_PENDING",
    }


def _zip_candidates() -> list[Path]:
    return [
        Path("/tmp/pages_full.zip"),
        ROOT / "cko_inbox" / "drive" / "pages_full.zip",
    ]


def write_pages_full_reg_pendencies(inventory: dict | None = None) -> dict:
    """Owner override: pages_full inventory demonstrates REG pendencies. No mass clinical extract."""
    dest_inv = ROOT / "cko_inbox" / "drive" / "pages_full" / "INVENTORY.json"
    inventory = inventory or (json.loads(dest_inv.read_text(encoding="utf-8")) if dest_inv.exists() else {})
    pages = inventory.get("pages") or []
    stems = {item.get("stem") for item in pages if item.get("stem")}
    pilots = sorted(stems & {"gotejamento", "meows", "cinco-ts-pcr", "simulado-tecnico", "dimensionamento"})
    scales = []
    for stem in ("braden", "norton", "glasgow"):
        if stem in stems:
            scales.append({
                "stem": stem,
                "gap": "PEND-THIRD-PARTY-SCALES",
                "in_data_tools": False,
                "role": "pendency_evidence",
            })
    institutional = [stem for stem in ("index", "missao", "politica", "termos") if stem in stems]
    catalog = {
        "business_key": "MD-PAGES-REG-PEND-001",
        "uuid": None,
        "status": "SOURCE_DERIVED",
        "inventory_ref": "MD-PAGE-INV-001",
        "drive_file_id": inventory.get("drive_file_id") or "1tJ-AEv3_KpEQxNa3lMuY7A80skFtw4IK",
        "html_count": inventory.get("html_count") or len(pages),
        "unique_stems": inventory.get("unique_stems") or len(stems),
        "buckets": inventory.get("buckets") or {},
        "reg_pendency_catalog": True,
        "promoted_to_data_tools": False,
        "mass_clinical_extract": "FORBIDDEN",
        "owner_override": (
            "Inventário demonstra pendências REG do projeto. "
            "Extração em massa de fórmula clínica para data/tools permanece FORBIDDEN."
        ),
        "gap_rule": "1 stem → 1 identidade MD+REG+rights pendente até COMPARE fechar",
        "pilot_stems_in_inventory": pilots,
        "pilot_stems_missing_from_inventory": sorted(
            {"gotejamento", "meows", "cinco-ts-pcr", "simulado-tecnico", "dimensionamento"} - set(pilots)
        ),
        "third_party_scale_stems": scales,
        "institutional_stems": institutional,
        "publication": "HOLD",
        "assured": False,
    }
    _dump(ROOT / "cko_md" / "pages_full_reg_pendencies.json", catalog)
    md_dest = ROOT / "cko_md" / "page_inventory.json"
    if dest_inv.exists():
        md_payload = {k: v for k, v in inventory.items() if k != "pages"}
        md_payload["reg_pendency_catalog"] = True
        md_payload["catalog_ref"] = "MD-PAGES-REG-PEND-001"
        md_payload["inventory_path"] = str(dest_inv.relative_to(ROOT))
        md_payload["related_to"] = "data/catalog.json"
        md_payload["relation_type"] = "RELATED_TAXONOMY"
        md_payload["not"] = "1:1 replace of the five pilots"
        _dump(md_dest, md_payload)
    return catalog


def parse_pages_full_zip(zip_path: Path | None = None) -> dict:
    """AG-PARSE-PAGES-FULL — inventory HTML stems. Does not copy pages to data/tools."""
    dest = ROOT / "cko_inbox" / "drive" / "pages_full" / "INVENTORY.json"
    md_dest = ROOT / "cko_md" / "page_inventory.json"
    zip_path = zip_path or next((p for p in _zip_candidates() if p.exists()), None)
    if zip_path is None:
        if dest.exists():
            payload = json.loads(dest.read_text(encoding="utf-8"))
            catalog = write_pages_full_reg_pendencies(payload)
            return {
                "agent_id": "AG-PARSE-PAGES-FULL",
                "class": "EXTRACTION",
                "role": "MAKER",
                "status": "SOURCE_DERIVED",
                "replay": True,
                "html_count": payload.get("html_count"),
                "unique_stems": payload.get("unique_stems"),
                "reg_pendency_catalog": catalog.get("business_key"),
                "path": str(dest.relative_to(ROOT)),
            }
        return {
            "agent_id": "AG-PARSE-PAGES-FULL",
            "class": "EXTRACTION",
            "role": "MAKER",
            "status": "EVIDENCE_PENDING",
            "reason": "pages_full.zip ausente; inventário ainda não gravado.",
        }

    blob = zip_path.read_bytes()
    digest = _sha256_bytes(blob)
    with zipfile.ZipFile(zip_path) as zf:
        names = [n for n in zf.namelist() if n.endswith(".html")]
        buckets: Counter[str] = Counter()
        stems: Counter[str] = Counter()
        pages = []
        chrome_hits = {key: 0 for key in CHROME_IDS}
        ads_hits = 0
        for name in names:
            parts = Path(name).parts
            bucket = parts[1] if len(parts) > 1 else "unknown"
            buckets[bucket] += 1
            stem = Path(name).stem
            stems[stem] += 1
            info = zf.getinfo(name)
            pages.append({
                "path": name,
                "stem": stem,
                "bucket": bucket,
                "bytes": info.file_size,
            })
            if bucket == "root" and stem in {"index", "gotejamento", "braden", "imc"}:
                html = zf.read(name).decode("utf-8", errors="replace")
                for key in CHROME_IDS:
                    if f'id="{key}"' in html or f"id='{key}'" in html:
                        chrome_hits[key] += 1
                if "adsbygoogle" in html:
                    ads_hits += 1

    duplicate_stems = sorted(stem for stem, count in stems.items() if count > 1)
    payload = {
        "business_key": "MD-PAGE-INV-001",
        "uuid": None,
        "status": "SOURCE_DERIVED",
        "maturity": "M0_REGISTERED",
        "epistemic_status": "SOURCE_DERIVED",
        "quarantine": True,
        "drive_file_id": DRIVE_PAGES_FULL_ID,
        "title": "pages_full.zip",
        "zip_bytes": len(blob),
        "zip_sha256": digest,
        "expected_sha256": PAGES_FULL_SHA256,
        "hash_match": digest == PAGES_FULL_SHA256,
        "html_count": len(names),
        "unique_stems": len(stems),
        "duplicate_stems": duplicate_stems,
        "buckets": dict(sorted(buckets.items())),
        "chrome_ids_in_sample": chrome_hits,
        "ads_in_sample": ads_hits,
        "rule": (
            "Inventário SOURCE_DERIVED usado como catálogo de pendências REG "
            "(1 stem → 1 gap MD+REG+rights). Extração em massa de fórmula clínica para data/tools permanece FORBIDDEN."
        ),
        "reg_pendency_catalog": True,
        "catalog_ref": "MD-PAGES-REG-PEND-001",
        "promoted_to_data_tools": False,
        "extracted_at": _now(),
        "pages": pages,
    }
    _dump(dest, payload)
    md_payload = {k: v for k, v in payload.items() if k != "pages"}
    md_payload["inventory_path"] = str(dest.relative_to(ROOT))
    md_payload["related_to"] = "data/catalog.json"
    md_payload["relation_type"] = "RELATED_TAXONOMY"
    md_payload["not"] = "1:1 replace of the five pilots"
    _dump(md_dest, md_payload)
    write_pages_full_reg_pendencies(payload)
    return {
        "agent_id": "AG-PARSE-PAGES-FULL",
        "class": "EXTRACTION",
        "role": "MAKER",
        "status": "SOURCE_DERIVED",
        "replay": False,
        "html_count": len(names),
        "unique_stems": len(stems),
        "duplicate_stems": duplicate_stems,
        "hash_match": digest == PAGES_FULL_SHA256,
        "path": str(dest.relative_to(ROOT)),
        "promotes_to_md": False,
    }


def parse_sitemap(xml_path: Path | None = None, *, network: bool = False) -> dict:
    """AG-PARSE-SITEMAP — loc stems from production sitemap."""
    dest = ROOT / "cko_inbox" / "extracted" / "sitemap_slugs.json"
    xml_path = xml_path or Path("/tmp/cko-fetch/sitemap.xml")
    xml_bytes = b""
    source = None
    if network:
        rec = _http_get(ORIGIN + "sitemap.xml", timeout=30)
        xml_bytes = rec.pop("body", b"") or b""
        source = {"url": ORIGIN + "sitemap.xml", "http_status": rec.get("http_status"), "sha256": rec.get("sha256")}
    elif xml_path.exists():
        xml_bytes = xml_path.read_bytes()
        source = {"path": str(xml_path), "sha256": _sha256_bytes(xml_bytes), "bytes": len(xml_bytes)}
    elif dest.exists():
        payload = json.loads(dest.read_text(encoding="utf-8"))
        return {
            "agent_id": "AG-PARSE-SITEMAP",
            "class": "EXTRACTION",
            "role": "MAKER",
            "status": "SOURCE_DERIVED",
            "replay": True,
            "loc_count": payload.get("loc_count"),
        }
    if not xml_bytes:
        return {"agent_id": "AG-PARSE-SITEMAP", "class": "EXTRACTION", "role": "MAKER", "status": "EVIDENCE_PENDING"}
    locs = re.findall(r"<loc>(.*?)</loc>", xml_bytes.decode("utf-8", errors="replace"))
    slugs = []
    for loc in locs:
        name = loc.rstrip("/").rsplit("/", 1)[-1]
        if name.endswith(".html"):
            slugs.append(name[:-5])
        elif name:
            slugs.append(name)
    unique = sorted(set(slugs))
    payload = {
        "business_key": "SRC-SITEMAP-001",
        "uuid": None,
        "status": "SOURCE_DERIVED",
        "origin": ORIGIN,
        "source": source,
        "loc_count": len(locs),
        "unique_slugs": len(unique),
        "slugs": unique,
        "extracted_at": _now(),
        "rule": "Sitemap é evidência de URL observada. Não publica ferramenta.",
    }
    _dump(dest, payload)
    return {
        "agent_id": "AG-PARSE-SITEMAP",
        "class": "EXTRACTION",
        "role": "MAKER",
        "status": "SOURCE_DERIVED",
        "loc_count": len(locs),
        "unique_slugs": len(unique),
        "promotes_to_md": False,
    }


def parse_chrome_contract() -> dict:
    """AG-PARSE-CHROME — production chrome IDs vs CKO projection rules."""
    origin = ROOT / "cko_inbox" / "origin"
    hits = {}
    for name in ("footer.html", "menu-global.html", "global-body-elements.html"):
        path = origin / name
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        hits[name] = {
            "exists": path.exists(),
            "bytes": path.stat().st_size if path.exists() else 0,
            "barraAcessibilidade": "barraAcessibilidade" in text,
            "footer_tag": "<footer" in text.lower(),
            "icontopbar": "icontopbar1-calculadoras-de-enfermagem" in text,
            "email_input": 'type="email"' in text.lower(),
            "adsbygoogle": "adsbygoogle" in text,
            "cookie_modal": "cookie-modal" in text,
        }
    contract = {
        "business_key": "SRC-CHROME-CONTRACT-001",
        "uuid": None,
        "status": "SOURCE_DERIVED",
        "production_placeholders": {
            "global-header-container": {"min_height_desktop": "96px", "min_height_mobile": "60px"},
            "language-selector-placeholder": {"min_height": "46px"},
            "footer-placeholder": {"min_height_mobile": "520px", "min_height_desktop": "277px"},
            "barraAcessibilidade": {"height": "36px", "background": "#1A3E74"},
        },
        "theme_color": "#1A3E74",
        "header_icon": "icontopbar1-calculadoras-de-enfermagem.webp",
        "footer_icon": "iconrodape1-80-calculadoras-de-enfermagem.webp",
        "fonts": ["Inter 400/600/700/900", "Nunito Sans 400/700/900"],
        "do_not_copy": ["adsbygoogle", "googleads dns-prefetch", "type=email", "cookie modal", "OpenDyslexic CDN"],
        "origin_files": hits,
        "extracted_at": _now(),
    }
    _dump(ROOT / "cko_inbox" / "extracted" / "chrome_contract.json", contract)
    return {
        "agent_id": "AG-PARSE-CHROME",
        "class": "EXTRACTION",
        "role": "MAKER",
        "status": "SOURCE_DERIVED",
        "contract_path": "cko_inbox/extracted/chrome_contract.json",
        "promotes_to_md": False,
    }


def integrity_hashes() -> dict:
    """AG-INTEGRITY — hash chain over inbox artifacts."""
    paths = [
        ROOT / "cko_inbox" / "origin" / "MANIFEST.json",
        ROOT / "cko_inbox" / "drive" / "pages_full" / "INVENTORY.json",
        ROOT / "cko_inbox" / "drive" / "site-shell-calculadoras-enfermagem.zip",
        ROOT / "cko_inbox" / "extracted" / "chrome_contract.json",
        ROOT / "cko_inbox" / "extracted" / "regulated_pages.json",
        ROOT / "cko_inbox" / "official" / "lei-9610.html",
        ROOT / "cko_inbox" / "vault" / "MANIFEST.json",
        ROOT / "assets" / "img" / "icontopbar1-calculadoras-de-enfermagem.webp",
        ROOT / "assets" / "fonts" / "inter" / "inter-regular.woff2",
    ]
    items = []
    for path in paths:
        if not path.exists():
            items.append({"path": str(path), "status": "MISSING"})
            continue
        data = path.read_bytes()
        items.append({
            "path": str(path.relative_to(ROOT)),
            "bytes": len(data),
            "sha256": _sha256_bytes(data),
            "status": "OBSERVED",
        })
    payload = {
        "business_key": "IPE-HASH-CHAIN-001",
        "uuid": None,
        "status": "OBSERVED",
        "captured_at": _now(),
        "items": items,
    }
    _dump(ROOT / "cko_inbox" / "extracted" / "hash_chain.json", payload)
    return {
        "agent_id": "AG-INTEGRITY",
        "class": "EVIDENCE",
        "role": "CHECKER",
        "status": "OBSERVED",
        "items": len(items),
        "missing": sum(1 for item in items if item["status"] == "MISSING"),
    }


def caat_extracted_population() -> dict:
    """AG-CAAT — uniqueness on extracted stems. Not clinical PASS."""
    inv_path = ROOT / "cko_inbox" / "drive" / "pages_full" / "INVENTORY.json"
    sitemap_path = ROOT / "cko_inbox" / "extracted" / "sitemap_slugs.json"
    findings = []
    html_count = 0
    unique_stems = 0
    duplicate_stems: list[str] = []
    if inv_path.exists():
        inv = json.loads(inv_path.read_text(encoding="utf-8"))
        html_count = inv.get("html_count") or 0
        unique_stems = inv.get("unique_stems") or 0
        duplicate_stems = inv.get("duplicate_stems") or []
        if duplicate_stems:
            findings.append({
                "id": "CAAT-STEM-COLLISION",
                "status": "FINDING",
                "detail": duplicate_stems,
                "note": "Stems repetidos entre buckets. Não auto-merge.",
            })
        if html_count and unique_stems:
            findings.append({
                "id": "CAAT-PAGE-POPULATION",
                "status": "PASS",
                "tested": html_count,
                "unique": unique_stems,
                "note": "População do zip. Não é PASS clínico.",
            })
    else:
        findings.append({"id": "CAAT-PAGE-POPULATION", "status": "HOLD", "reason": "Inventário ausente."})

    if sitemap_path.exists():
        sm = json.loads(sitemap_path.read_text(encoding="utf-8"))
        findings.append({
            "id": "CAAT-SITEMAP-POPULATION",
            "status": "PASS",
            "loc_count": sm.get("loc_count"),
            "unique_slugs": sm.get("unique_slugs"),
            "note": "População do sitemap. Não é PASS clínico.",
        })

    tools = {path.stem for path in TOOLS_DIR.glob("*.json")}
    if tools != PILOT_SLUGS:
        findings.append({
            "id": "CAAT-PILOT-SET",
            "status": "FAIL",
            "observed": sorted(tools),
            "expected": sorted(PILOT_SLUGS),
        })
    else:
        findings.append({
            "id": "CAAT-PILOT-SET",
            "status": "PASS",
            "tested": 5,
            "note": "Cinco pilotos inalterados. Braden fora de data/tools.",
        })
    if (TOOLS_DIR / "braden.json").exists():
        findings.append({"id": "CAAT-BRADEN-NOT-PROMOTED", "status": "FAIL"})
    else:
        findings.append({"id": "CAAT-BRADEN-NOT-PROMOTED", "status": "PASS", "note": "braden.html permanece quarentena."})

    statuses = {item["status"] for item in findings}
    overall = "HOLD"
    if "FAIL" in statuses:
        overall = "FAIL"
    elif findings and all(item["status"] in {"PASS", "FINDING"} for item in findings):
        overall = "PASS_WITH_FINDINGS"
    payload = {
        "business_key": "CAAT-EXTRACT-001",
        "uuid": None,
        "status": overall,
        "implemented": True,
        "scope": "extracted_population_plus_pilot_set",
        "not": "PASS clínico / release",
        "findings": findings,
        "tested_at": _now(),
    }
    _dump(ROOT / "cko_inbox" / "extracted" / "caat_extract.json", payload)
    return {
        "agent_id": "AG-CAAT-EXTRACT",
        "class": "CAAT",
        "role": "CHECKER",
        "status": overall,
        "findings": findings,
        "html_count": html_count,
        "unique_stems": unique_stems,
    }


def ipe_carr() -> dict:
    """AG-IPE — CARR over extraction reports. No reliance."""
    reports = {
        "COMPLETE": (ROOT / "cko_inbox" / "drive" / "pages_full" / "INVENTORY.json").exists(),
        "ACCURATE": False,
        "RELEVANT": True,
        "RELIABLE": False,
        "REPRODUCIBLE": (ROOT / "cko_inbox" / "extracted" / "hash_chain.json").exists(),
    }
    payload = {
        "business_key": "IPE-EXTRACT-001",
        "uuid": None,
        "status": "HOLD",
        "implemented": True,
        "reliance": False,
        "carr": {
            "COMPLETE": "PASS" if reports["COMPLETE"] else "HOLD",
            "ACCURATE": "UNKNOWN",
            "RELEVANT": "PASS",
            "RELIABLE": "FAIL",
            "REPRODUCIBLE": "PASS" if reports["REPRODUCIBLE"] else "HOLD",
        },
        "notes": {
            "ACCURATE": "Comparação WORM existe para chrome/site-shell/pilotos/Lei 9.610. Não houve comparação página-a-página live vs zip para cada um dos 1516 HTML.",
            "RELIABLE": "Relatório interno de extração não autoriza publicação clínica.",
        },
        "tested_at": _now(),
        "rule": "Relatório interno não é evidência sem avaliação IPE. SEM EVIDÊNCIA → HOLD.",
    }
    _dump(ROOT / "cko_inbox" / "extracted" / "ipe_extract.json", payload)
    return {
        "agent_id": "AG-IPE-EXTRACT",
        "class": "IPE",
        "role": "CHECKER",
        "status": "HOLD",
        "reliance": False,
        "carr": payload["carr"],
    }


def link_to_md() -> dict:
    """AG-LINK-MD — bind extracted stems to existing pilots only."""
    inv_path = ROOT / "cko_inbox" / "drive" / "pages_full" / "INVENTORY.json"
    stems: set[str] = set()
    if inv_path.exists():
        inv = json.loads(inv_path.read_text(encoding="utf-8"))
        stems = {item.get("stem") for item in inv.get("pages") or []}
    tools = {path.stem for path in TOOLS_DIR.glob("*.json")}
    bound = sorted(stems & tools)
    quarantined_examples = sorted(stems & {"braden", "norton", "glasgow", "insulina", "imc", "gasometria"})
    payload = {
        "business_key": "REG-EXTRACT-LINK-001",
        "uuid": None,
        "status": "HOLD",
        "bound_pilots": bound,
        "quarantined_examples": quarantined_examples,
        "unbound_stems": max(0, len(stems) - len(bound)),
        "rule": "Ligação MD só para identidade já existente. Extração não cria UUID nem golden record.",
        "linked_at": _now(),
    }
    rights = {}
    rights_path = ROOT / "cko_reg" / "rights_profile.json"
    if rights_path.exists():
        rights = json.loads(rights_path.read_text(encoding="utf-8"))
    _dump(ROOT / "cko_inbox" / "extracted" / "md_link.json", payload)
    _dump(ROOT / "cko_reg" / "extraction_profile.json", {
        "business_key": "REG-EXTRACT-001",
        "uuid": None,
        "status": "HOLD",
        "translation_gate": "HOLD",
        "publication_gate": "HOLD",
        "rights_gate": rights.get("gate") or "HOLD",
        "rights_ref": "REG-RIGHTS-001",
        "instrument_ref": "INS-LEI-9610-1998",
        "note": "Conteúdo extraído de pages_full/sitemap/origin/site-shell é SOURCE_DERIVED. REG não cria identidade. Lei 9.610 documentada; escalas de terceiros HOLD.",
        "bound_pilots": bound,
    })
    return {
        "agent_id": "AG-LINK-MD",
        "class": "ENTITY_RESOLUTION",
        "role": "CHECKER",
        "status": "HOLD",
        "bound_pilots": bound,
        "quarantined_examples": quarantined_examples,
        "promotes_to_md": False,
    }


def apply_norm_masks() -> dict:
    """AG-MASK-APPLY — simple deterministic execution of robust-AI-authored masks."""
    from .masks import apply_all
    from .vault import first_copy

    law = first_copy("SRC-LEI-9610-1998")
    law_text = (law or {}).get("bytes_payload", b"").decode("latin-1", errors="replace") if law else ""
    fetch_index = ROOT / "render" / "fetch" / "index.html"
    internal_text = fetch_index.read_text(encoding="utf-8") if fetch_index.exists() else ""
    rights = {}
    rights_path = ROOT / "cko_reg" / "rights_profile.json"
    if rights_path.exists():
        rights = json.loads(rights_path.read_text(encoding="utf-8"))
    iso = {}
    iso_path = ROOT / "cko_md" / "iso8000_profile.json"
    if iso_path.exists():
        iso = json.loads(iso_path.read_text(encoding="utf-8"))
    lineage = {}
    lineage_path = ROOT / "cko_md" / "lineage_registry.json"
    if lineage_path.exists():
        lineage = json.loads(lineage_path.read_text(encoding="utf-8"))
    complete_slugs = {item.get("slug") for item in (lineage.get("links") or []) if item.get("complete")}
    contexts = [
        {
            "mask_id": "MASK-LAW-BR",
            "logical_id": "SRC-LEI-9610-1998",
            "text": law_text,
            "inbox_present": bool(law),
            "clause_text": "NOT_COPIED_AS_PRODUCT_RULE",
        },
        {
            "mask_id": "MASK-TECH-STD",
            "clause_text": iso.get("clause_text") or "CLAUSE_TEXT_UNAVAILABLE",
            "licensed_body": False,
            "certified": False,
            "media_type": "text/html",
        },
        {
            "mask_id": "MASK-ORIGIN-HTML",
            "logical_id": "SRC-SITE-SHELL",
            "internal_text": internal_text,
        },
        {
            "mask_id": "MASK-REGULATED-HTML",
            "api_base_url": None,
            "invented_rest": False,
        },
    ]
    for slug in ("gotejamento", "meows", "cinco-ts-pcr", "simulado-tecnico"):
        contexts.append({
            "mask_id": "MASK-TOOL-WORK",
            "slug": slug,
            "lineage_complete": slug in complete_slugs,
            "rights_status": rights.get("status") or "HOLD",
        })
    for slug in ("braden", "norton", "glasgow"):
        contexts.append({
            "mask_id": "MASK-SCALE-THIRD-PARTY",
            "slug": slug,
            "quarantined": True,
        })
    dim_path = TOOLS_DIR / "dimensionamento.json"
    dim = json.loads(dim_path.read_text(encoding="utf-8")) if dim_path.exists() else {}
    contexts.append({
        "mask_id": "MASK-HOLD-WORK",
        "slug": "dimensionamento",
        "status": dim.get("status"),
        "has_formula": "calculator" in dim,
    })
    payload = apply_all(contexts)
    _dump(ROOT / "cko_inbox" / "extracted" / "mask_run.json", payload)
    statuses = {item.get("status") for item in payload.get("results") or []}
    overall = "HOLD"
    if payload.get("results") and all(item.get("status") == "PASS" for item in payload["results"]):
        overall = "PASS"
    elif "FAIL" in statuses:
        overall = "FAIL"
    return {
        "agent_id": "AG-MASK-APPLY",
        "class": "REGULATORY",
        "role": "CHECKER",
        "status": overall,
        "population": payload.get("population"),
        "llm_used": False,
        "execution_policy": payload.get("execution_policy"),
        "promotes_to_md": False,
    }


def agent_records() -> list[dict]:
    return [
        {
            "agent_id": "AG-ORCHESTRATOR",
            "class": "ORCHESTRATOR",
            "implemented": True,
            "writes_to": "cko_inbox/agent_runs",
            "promotes_to_md": False,
            "note": "Orquestra MAKER then CHECKER. Não publica.",
        },
        {
            "agent_id": "AG-FETCH-ORIGIN",
            "class": "ACQUISITION",
            "implemented": True,
            "writes_to": "cko_inbox/origin",
            "promotes_to_md": False,
        },
        {
            "agent_id": "AG-FETCH-REGULATED",
            "class": "ACQUISITION",
            "implemented": True,
            "writes_to": "cko_inbox/extracted/regulated_pages.json",
            "promotes_to_md": False,
            "note": "HTML oficial. API REST base_url null.",
        },
        {
            "agent_id": "AG-PARSE-PAGES-FULL",
            "class": "EXTRACTION",
            "implemented": True,
            "writes_to": "cko_inbox/drive/pages_full/INVENTORY.json",
            "promotes_to_md": False,
        },
        {
            "agent_id": "AG-PARSE-SITEMAP",
            "class": "EXTRACTION",
            "implemented": True,
            "writes_to": "cko_inbox/extracted/sitemap_slugs.json",
            "promotes_to_md": False,
        },
        {
            "agent_id": "AG-PARSE-CHROME",
            "class": "A11Y",
            "implemented": True,
            "writes_to": "cko_inbox/extracted/chrome_contract.json",
            "promotes_to_md": False,
        },
        {
            "agent_id": "AG-INTEGRITY",
            "class": "EVIDENCE",
            "implemented": True,
            "writes_to": "cko_inbox/extracted/hash_chain.json",
            "promotes_to_md": False,
        },
        {
            "agent_id": "AG-CAAT-EXTRACT",
            "class": "CAAT",
            "implemented": True,
            "writes_to": "cko_inbox/extracted/caat_extract.json",
            "promotes_to_md": False,
        },
        {
            "agent_id": "AG-IPE-EXTRACT",
            "class": "IPE",
            "implemented": True,
            "writes_to": "cko_inbox/extracted/ipe_extract.json",
            "promotes_to_md": False,
            "reliance": False,
        },
        {
            "agent_id": "AG-LINK-MD",
            "class": "ENTITY_RESOLUTION",
            "implemented": True,
            "writes_to": "cko_reg/extraction_profile.json",
            "promotes_to_md": False,
        },
        {
            "agent_id": "AG-PARSE-SITE-SHELL",
            "class": "EXTRACTION",
            "implemented": True,
            "writes_to": "cko_inbox/drive/site_shell/INVENTORY.json",
            "promotes_to_md": False,
            "note": "Drive site-shell zip. Ads/CDN não copiados para o renderer.",
        },
        {
            "agent_id": "AG-VAULT-PUT",
            "class": "EVIDENCE",
            "implemented": True,
            "writes_to": "cko_inbox/vault",
            "promotes_to_md": False,
            "note": "WORM: primeira cópia inalterada. Hash novo = objeto novo + evento.",
        },
        {
            "agent_id": "AG-RIGHTS-BIND",
            "class": "REGULATORY",
            "implemented": True,
            "writes_to": "cko_reg/rights_profile.json",
            "promotes_to_md": False,
            "note": "Lei 9.610 como instrumento. Escalas de terceiros HOLD.",
        },
        {
            "agent_id": "AG-LINEAGE-BIND",
            "class": "ENTITY_RESOLUTION",
            "implemented": True,
            "writes_to": "cko_md/lineage_registry.json",
            "promotes_to_md": False,
            "wired_to_frontend": True,
        },
        {
            "agent_id": "AG-ISO8000-PROFILE",
            "class": "MD",
            "implemented": True,
            "writes_to": "cko_md/iso8000_profile.json",
            "promotes_to_md": False,
            "note": "Perfil CKO. clause_text CLAUSE_TEXT_UNAVAILABLE. certified=false.",
        },
        {
            "agent_id": "AG-WHO-I18N",
            "class": "MD",
            "implemented": True,
            "writes_to": "cko_md/who_i18n_modulation.json",
            "promotes_to_md": False,
            "wired_to_frontend": False,
            "note": "OMS who.int seletor (en ar zh fr ru es). Chave who.en+local.pt-BR. Variantes lusófonas HOLD. Sem dump ICD/ICNP/GHO.",
        },
        {
            "agent_id": "AG-LAYER-PHASE",
            "class": "MD",
            "implemented": True,
            "writes_to": "cko_md/layer_md_reg_phase.json",
            "promotes_to_md": False,
            "wired_to_frontend": False,
            "note": "Envelope MD+REG das 44 camadas faseado P0–P5. Envelope completo ≠ assured. publication HOLD.",
        },
        {
            "agent_id": "AG-CLIN-DICT",
            "class": "MD",
            "implemented": True,
            "writes_to": "cko_md/clinical_dictionary_catalog.json",
            "promotes_to_md": False,
            "wired_to_frontend": False,
            "note": "Dicionario clinico.zip COMPARE. Códigos piloto CALC-/SCALE-/GUIDE-/EXAM-*. Sem Braden em data/tools. UUIDv4 não adotado.",
        },
        {
            "agent_id": "AG-MASK-APPLY",
            "class": "REGULATORY",
            "implemented": True,
            "writes_to": "cko_inbox/extracted/mask_run.json",
            "promotes_to_md": False,
            "note": "Máscaras desenhadas (IA robusta). Execução determinística simples. LLM checker FORBIDDEN.",
        },
        {
            "agent_id": "AG-COMPARE-SOURCE",
            "class": "MONITORING",
            "implemented": True,
            "writes_to": "cko_inbox/extracted/compare_source.json",
            "promotes_to_md": False,
        },
        {
            "agent_id": "AG-COMPARE-INTERNAL",
            "class": "MONITORING",
            "implemented": True,
            "writes_to": "cko_inbox/extracted/compare_internal.json",
            "promotes_to_md": False,
        },
        {
            "agent_id": "AG-MONITOR-DRIFT",
            "class": "MONITORING",
            "implemented": True,
            "writes_to": "cko_assurance/monitoring_events.json",
            "promotes_to_md": False,
            "wired_to_frontend": True,
        },
        {
            "agent_id": "AG-FETCH-GOV-SOURCES",
            "class": "ACQUISITION",
            "implemented": True,
            "writes_to": "cko_inbox/extracted/gov_pages.json",
            "promotes_to_md": False,
            "note": "ANVISA, MS, COFEN, COREN-SP HTML, SGD PGDADOS. Sem inventar API REST.",
        },
        {
            "agent_id": "AG-API-PROBE",
            "class": "ACQUISITION",
            "implemented": True,
            "writes_to": "cko_md/api_adapter_registry.json",
            "promotes_to_md": False,
            "note": "CKAN dados.gov.br / OpenDataSUS / Portal APIs ANVISA. base_url só se HTTP 200 JSON. HTML SPA ≠ REST.",
        },
        {
            "agent_id": "AG-PROBE-CONGRESS-API",
            "class": "ACQUISITION",
            "implemented": True,
            "writes_to": "cko_inbox/extracted/congress_probe.json",
            "promotes_to_md": False,
            "note": "Câmara + Senado/Congresso. base_url só se HTTP 200.",
        },
        {
            "agent_id": "AG-FETCH-FEDERAL-LEGISLATION",
            "class": "ACQUISITION",
            "implemented": True,
            "writes_to": "cko_md/legislation_instrument_registry.json",
            "promotes_to_md": False,
            "note": "Catálogo federal: LCP/lei ALLOW; PLP BLOCK; decreto numerado REGULATORY; norma revogada para ferramenta.",
        },
        {
            "agent_id": "AG-LIBRARY-CATALOG",
            "class": "CONTENT",
            "implemented": True,
            "writes_to": "cko_md/resource_library.json",
            "promotes_to_md": False,
            "note": "Catálogo de metadados. Não republica HTML integral.",
        },
        {
            "agent_id": "AG-INVENTORY-DRIVE",
            "class": "DISCOVERY",
            "implemented": True,
            "writes_to": "cko_inbox/extracted/drive_inventory.json",
            "promotes_to_md": False,
            "note": "Replay do listing Drive persistido. Não unzip mega-zip nem promove HTML.",
        },
        {
            "agent_id": "AG-INVENTORY-SUPABASE",
            "class": "DISCOVERY",
            "implemented": True,
            "writes_to": "cko_inbox/extracted/supabase_inventory.json",
            "promotes_to_md": False,
            "note": "Projetos e slugs de Edge Function observados. MCP Cursor JSON read_only DOCUMENTADO. Schema SQL EVIDENCE_PENDING (28P01 / MCP -32600).",
        },
        {
            "agent_id": "AG-COMPARE-STORES",
            "class": "MONITORING",
            "implemented": True,
            "writes_to": "cko_inbox/extracted/compare_stores.json",
            "promotes_to_md": False,
            "note": "CHECKER: Drive/Supabase vs GitHub MD/REG. Só gaps.",
        },
        {
            "agent_id": "AG-PLAN-FRONTS",
            "class": "ORCHESTRATOR",
            "implemented": True,
            "writes_to": "cko_md/fronts_plan.json",
            "promotes_to_md": False,
            "note": "Plano vivo F1–F24. layer_intent + NNN rights-safe + owner unblock + L70 ANVISA. Não é waterfall. LLM não é autoridade.",
        },
        {
            "agent_id": "AG-UCP-V2-COMPARE",
            "class": "MONITORING",
            "implemented": True,
            "writes_to": "cko_md/ucp_v2_compare.json",
            "promotes_to_md": False,
            "note": "COMPARE contratos UCP v2.0. Não copiar para schemas/. CONTROLLED_CANDIDATE ≠ ASSURED.",
        },
        {
            "agent_id": "AG-L70-ANVISA-COMPARE",
            "class": "MONITORING",
            "implemented": True,
            "writes_to": "cko_md/l70_anvisa_compare.json",
            "promotes_to_md": False,
            "note": "L70: Portal APIs ANVISA + listing Drive. Sem unzip dump. Sem inventar dose. openFDA ≠ bula.",
        },
        {
            "agent_id": "AG-CONTENT-CURRICULUM",
            "class": "CONTENT",
            "implemented": True,
            "writes_to": "cko_md/content_curriculum.json",
            "promotes_to_md": False,
            "note": "Básico→avançado a partir do MD da ferramenta. LLM FORBIDDEN.",
        },
        {
            "agent_id": "AG-OPS-DB-SYNC",
            "class": "MD",
            "implemented": True,
            "writes_to": "cko_inbox/cko_ops.sqlite",
            "promotes_to_md": False,
            "note": "Espelho SQLite inbox. Não é Postgres de produção. Sem RLS.",
        },
        {
            "agent_id": "AG-ALERT-FRESHNESS",
            "class": "MONITORING",
            "implemented": True,
            "writes_to": "cko_assurance/freshness_alerts.json",
            "promotes_to_md": False,
            "wired_to_frontend": True,
            "note": "Alerta JSON/Admin. Sem e-mail. Pendência ALTA se norma indisponível.",
        },
    ]


def write_agent_registry(run: dict | None = None) -> None:
    agents = agent_records()
    payload = {
        "business_key": "REG-AGENT-001",
        "status": "IMPLEMENTED_INBOX_ONLY",
        "implemented": True,
        "publication_implemented": False,
        "rule": "Agente executa processo. Agente não cria autoridade. MAKER ≠ CHECKER ≠ AUDITOR.",
        "classes": [
            "ORCHESTRATOR", "DISCOVERY", "ACQUISITION", "EXTRACTION", "NORMALIZATION",
            "ENTITY_RESOLUTION", "MD", "REGULATORY", "KNOWLEDGE", "EVIDENCE", "CONTENT",
            "SEO", "A11Y", "PRIVACY", "SECURITY", "SUSTAINABILITY", "RENDERER",
            "PUBLICATION", "VALIDATION", "CAAT", "IPE", "RISK", "AUDIT", "SEARCH",
            "SAE", "MONITORING",
        ],
        "agents": agents,
        "population": len(agents),
        "last_run": (run or {}).get("run_id"),
        "last_run_status": (run or {}).get("status"),
    }
    _dump(ROOT / "cko_assurance" / "agent_registry.json", payload)


def run_extraction(*, network: bool = True) -> dict:
    """AG-ORCHESTRATOR — ordered pipeline. Never auto-PASS publication."""
    from .congress import fetch_federal_legislation, probe_congress_apis
    from .govlib import (
        alert_freshness,
        catalog_library,
        content_curriculum,
        fetch_gov_sources,
        probe_apis,
        sync_ops_db,
    )
    from .clinical_dict import evaluate_clinical_dict
    from .iso8000 import evaluate_profile
    from .lineage import bind_lineage
    from .layer_phase import evaluate_layer_md_reg
    from .who_i18n import evaluate_who_i18n
    from .monitor import compare_internal, compare_source, monitor_drift
    from .rights import bind_rights
    from .site_shell import parse_site_shell
    from .store_inventory import compare_stores, inventory_drive, inventory_supabase, plan_fronts
    from .ucp_v2 import compare_ucp_v2
    from .l70_anvisa import compare_l70_anvisa
    from .vault import put_known_sources

    run_id = "RUN-EXTRACT-" + _now().replace(":", "").replace("-", "")
    steps = [
        fetch_origin(network=network),
        fetch_regulated_pages(network=network),
        fetch_gov_sources(network=network),
        probe_apis(network=network),
        probe_congress_apis(network=network),
        fetch_federal_legislation(network=network),
        parse_pages_full_zip(),
        parse_sitemap(network=network),
        parse_chrome_contract(),
        parse_site_shell(),
        integrity_hashes(),
        put_known_sources(network=network, fetch_fn=_http_get),
        bind_rights(),
        bind_lineage(),
        evaluate_clinical_dict(),
        evaluate_profile(),
        evaluate_who_i18n(),
        evaluate_layer_md_reg(),
        apply_norm_masks(),
        caat_extracted_population(),
        ipe_carr(),
        link_to_md(),
        catalog_library(),
        inventory_drive(),
        inventory_supabase(),
        compare_stores(),
        compare_ucp_v2(),
        compare_l70_anvisa(),
        plan_fronts(),
        content_curriculum(),
        compare_source(network=network, fetch_fn=_http_get),
        compare_internal(),
        monitor_drift(),
        alert_freshness(),
        sync_ops_db(),
    ]
    caat = next(step for step in steps if step.get("agent_id") == "AG-CAAT-EXTRACT")
    ipe = next(step for step in steps if step.get("agent_id") == "AG-IPE-EXTRACT")
    status = "HOLD"
    if caat.get("status") == "FAIL":
        status = "FAIL"
    run = {
        "business_key": "IPE-AGENT-RUN-001",
        "run_id": run_id,
        "uuid": None,
        "status": status,
        "network": network,
        "started_at": _now(),
        "chain": "vault → CKO-MD → CKO-REG → projection → renderer → frontend",
        "rule": "DOCUMENTADO ≠ IMPLEMENTADO ≠ VALIDADO ≠ ASSURED ≠ PUBLICADO. Extração ≠ promoção. LLM não é checker.",
        "publication": "HOLD",
        "ipe_reliance": False,
        "caat_status": caat.get("status"),
        "ipe_status": ipe.get("status"),
        "llm_used": False,
        "steps": steps,
        "forbidden_copied": list(FORBIDDEN_IN_PROJECTION),
    }
    _dump(ROOT / "cko_inbox" / "agent_runs" / "latest.json", run)
    write_agent_registry(run)
    return run
