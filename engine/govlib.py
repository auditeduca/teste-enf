"""Government sources, resource library, documentary curriculum, freshness alerts.

MD first, REG second. No invented REST base_url. No clinical text without a
bound tool/source. Licensed norms without a government alternative → HIGH pending.
"""

from __future__ import annotations

import hashlib
import json
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

from .paths import ROOT, TOOLS_DIR

FREQ_HOURS = 24
INBOX_DB = ROOT / "cko_inbox" / "cko_ops.sqlite"

GOV_HTML = (
    {
        "business_key": "SRC-GOV-ANVISA-PORTAL",
        "agency_key": "AGY-ANVISA",
        "agency": "ANVISA",
        "url": "https://www.gov.br/anvisa/pt-br",
        "kind": "REGULATED_HTML_PAGE",
        "frequency_hours": FREQ_HOURS,
        "md_ref": "MD-AGY-ANVISA",
        "reg_ref": "REG-SRC-ANVISA",
        "layer": "L60",
    },
    {
        "business_key": "SRC-GOV-MS-PORTAL",
        "agency_key": "AGY-MS",
        "agency": "Ministério da Saúde",
        "url": "https://www.gov.br/saude/pt-br",
        "kind": "REGULATED_HTML_PAGE",
        "frequency_hours": FREQ_HOURS,
        "md_ref": "MD-AGY-MS",
        "reg_ref": "REG-SRC-MS",
        "layer": "L110",
    },
    {
        "business_key": "SRC-GOV-BVSMS",
        "agency_key": "AGY-MS",
        "agency": "Ministério da Saúde / BVSMS",
        "url": "https://bvsms.saude.gov.br/",
        "kind": "REGULATED_HTML_PAGE",
        "frequency_hours": FREQ_HOURS,
        "md_ref": "MD-AGY-MS",
        "reg_ref": "REG-SRC-MS",
        "layer": "L140",
        "note": "Biblioteca Virtual em Saúde. Candidato de referência pública, não API REST.",
    },
    {
        "business_key": "SRC-GOV-COFEN-PORTAL",
        "agency_key": "AGY-COFEN",
        "agency": "COFEN",
        "url": "https://www.cofen.gov.br/",
        "kind": "REGULATED_HTML_PAGE",
        "frequency_hours": FREQ_HOURS,
        "md_ref": "MD-AGY-COFEN",
        "reg_ref": "REG-SRC-COFEN",
        "layer": "L110",
        "note": "Portal HTML. REST API não observada. Não inventar adapter COFEN.",
    },
    {
        "business_key": "SRC-GOV-COREN-SP-PORTAL",
        "agency_key": "AGY-COREN-SP",
        "agency": "COREN-SP",
        "url": "https://www.coren-sp.gov.br/",
        "kind": "REGULATED_HTML_PAGE",
        "frequency_hours": FREQ_HOURS,
        "md_ref": "MD-AGY-COREN-SP",
        "reg_ref": "REG-SRC-COREN-SP",
        "layer": "L110",
        "note": "Portal HTML estadual. REST API não observada. Não inventar adapter COREN.",
    },
    {
        "business_key": "SRC-GOV-PGDADOS-HUB",
        "agency_key": "AGY-SGD",
        "agency": "Secretaria de Governo Digital / MGI",
        "url": "https://www.gov.br/governodigital/pt-br/infraestrutura-nacional-de-dados/governancadedados",
        "kind": "REGULATED_HTML_PAGE",
        "frequency_hours": FREQ_HOURS,
        "md_ref": "MD-AGY-SGD",
        "reg_ref": "REG-SRC-PGDADOS-HUB",
        "layer": "L150",
        "note": "Hub PGDADOS / Trilha de Governança de Dados. Metadados; PDF integral não vira regra de produto.",
    },
    {
        "business_key": "SRC-GOV-PGDADOS-GUIA",
        "agency_key": "AGY-SGD",
        "agency": "Secretaria de Governo Digital / MGI",
        "url": "https://www.gov.br/governodigital/pt-br/infraestrutura-nacional-de-dados/governancadedados/pgdados",
        "kind": "REGULATED_HTML_PAGE",
        "frequency_hours": FREQ_HOURS,
        "md_ref": "MD-AGY-SGD",
        "reg_ref": "REG-SRC-PGDADOS-GUIA",
        "layer": "L150",
        "note": "Guia de Implementação PGDADOS. Parte 3 PDF só entra se href.gov.br for observado.",
    },
    {
        "business_key": "SRC-GOV-QUALIDADE-DIGIT",
        "agency_key": "AGY-SGD",
        "agency": "Secretaria de Governo Digital / MGI",
        "url": (
            "https://www.gov.br/governodigital/pt-br/estrategias-e-governanca-digital/"
            "transformacao-digital/central-de-qualidade/padroes-de-qualidade/"
            "padroes-de-qualidade-para-servicos-publicos-digitais"
        ),
        "kind": "REGULATED_HTML_PAGE",
        "frequency_hours": FREQ_HOURS,
        "md_ref": "MD-AGY-SGD",
        "reg_ref": "REG-SRC-QUALIDADE-DIGIT",
        "layer": "L150",
        "note": "Padrões de Qualidade (7 dimensões). Texto de atributo não copiado como regra CKO.",
    },
)

API_CANDIDATES = (
    {
        "business_key": "API-CKAN-DADOSGOV-STATUS",
        "agency_key": "AGY-DADOSGOV",
        "agency": "dados.gov.br",
        "url": "https://dados.gov.br/api/3/action/status_show",
        "kind": "CKAN_ACTION",
        "md_ref": "MD-API-DADOSGOV",
        "reg_ref": "REG-API-DADOSGOV",
    },
    {
        "business_key": "API-CKAN-DADOSGOV-ANVISA",
        "agency_key": "AGY-ANVISA",
        "agency": "ANVISA via dados.gov.br",
        "url": "https://dados.gov.br/api/3/action/package_search?q=anvisa&rows=5",
        "kind": "CKAN_ACTION",
        "md_ref": "MD-API-ANVISA-CKAN",
        "reg_ref": "REG-API-ANVISA",
    },
    {
        "business_key": "API-CKAN-OPENDATASUS-STATUS",
        "agency_key": "AGY-MS",
        "agency": "OpenDataSUS",
        "url": "https://opendatasus.saude.gov.br/api/3/action/status_show",
        "kind": "CKAN_ACTION",
        "md_ref": "MD-API-OPENDATASUS",
        "reg_ref": "REG-API-MS",
    },
    {
        "business_key": "API-CKAN-OPENDATASUS-VACINA",
        "agency_key": "AGY-MS",
        "agency": "OpenDataSUS busca vacina",
        "url": "https://opendatasus.saude.gov.br/api/3/action/package_search?q=vacina&rows=5",
        "kind": "CKAN_ACTION",
        "md_ref": "MD-API-OPENDATASUS-VACINA",
        "reg_ref": "REG-API-MS",
    },
    {
        "business_key": "API-CROSSREF-WORKS",
        "agency_key": "AGY-CROSSREF",
        "agency": "Crossref REST",
        "url": "https://api.crossref.org/works?query=enfermagem&rows=1",
        "kind": "BIBLIOGRAPHIC_SEARCH",
        "md_ref": "MD-API-CROSSREF",
        "reg_ref": "REG-API-CROSSREF",
    },
    {
        "business_key": "API-NCBI-EUTILS-ESEARCH",
        "agency_key": "AGY-NCBI",
        "agency": "NCBI E-utilities",
        "url": "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=nursing&retmax=1&retmode=json",
        "kind": "LITERATURE_SEARCH",
        "md_ref": "MD-API-NCBI-EUTILS",
        "reg_ref": "REG-API-NCBI",
    },
    {
        "business_key": "API-NLM-CLINICALTABLES-ICD10CM",
        "agency_key": "AGY-NLM",
        "agency": "NLM Clinical Tables ICD-10-CM",
        "url": "https://clinicaltables.nlm.nih.gov/api/icd10cm/v3/search?terms=sepsis&maxList=1",
        "kind": "TERMINOLOGY_SEARCH",
        "md_ref": "MD-API-NLM-ICD10CM",
        "reg_ref": "REG-API-NLM",
    },
    {
        "business_key": "API-OPENFDA-DRUGLABEL",
        "agency_key": "AGY-FDA",
        "agency": "openFDA (FDA / governo dos EUA)",
        "url": "https://api.fda.gov/drug/label.json?limit=1",
        "kind": "PRODUCT_LABEL_SEARCH",
        "md_ref": "MD-API-OPENFDA",
        "reg_ref": "REG-API-FDA",
        "note": "Fallback US gov quando CKAN dados.gov.br/ANVISA REST falha. Não substitui bula ANVISA.",
    },
    {
        "business_key": "API-WHO-GHO-INDICATOR",
        "agency_key": "AGY-WHO",
        "agency": "OMS GHO OData",
        "url": "https://ghoapi.azureedge.net/api/Indicator?$top=1",
        "kind": "INDICATOR_SEARCH",
        "md_ref": "MD-API-WHO-GHO",
        "reg_ref": "REG-API-WHO",
        "note": "Indicadores OMS. Não republica instrumento clínico.",
    },
    {
        "business_key": "API-RXNAV-VERSION",
        "agency_key": "AGY-NLM",
        "agency": "NLM RxNav",
        "url": "https://rxnav.nlm.nih.gov/REST/version.json",
        "kind": "TERMINOLOGY_VERSION",
        "md_ref": "MD-API-RXNAV",
        "reg_ref": "REG-API-NLM",
        "note": "Versão RxNorm. Sem dump de termos.",
    },
)

LEVELS = (
    ("BASICO", "O que é, indicação e limites"),
    ("FUNDAMENTOS", "Variáveis, unidades e população"),
    ("PROCEDIMENTO", "Passo a passo do cálculo ou protocolo"),
    ("INTERPRETACAO", "Leitura do resultado e ações"),
    ("AVANCADO", "SAE, exceções e o que permanece HOLD"),
)

LIBRARY_TOPICS = (
    ("LIB-L60-DISPOSITIVOS", "L60", "Dispositivos e materiais", "AGY-ANVISA", "PENDENCIA_ALTA"),
    ("LIB-L70-MEDICAMENTOS", "L70", "Medicamentos e soluções", "AGY-ANVISA", "PENDENCIA_ALTA"),
    ("LIB-L80-EXAMES", "L80", "Exames laboratoriais", "AGY-MS", "PENDENCIA_ALTA"),
    ("LIB-L110-PROTOCOLOS", "L110", "Procedimentos e protocolos", "AGY-COFEN", "PENDENCIA_ALTA"),
    ("LIB-L130-CONCURSO", "L130", "Educação / concurso", "AGY-MS", "PENDENCIA_ALTA"),
    ("LIB-L140-LEGISLACAO-FEDERAL", "L140", "Legislação federal (Congresso)", "AGY-CONGRESSO", "PENDENCIA_ALTA"),
    ("LIB-L150-GUIAS", "L150", "Artigos / guias / resumos", "AGY-MS", "PENDENCIA_ALTA"),
    ("LIB-L150-PGDADOS", "L150", "PGDADOS / governança de dados (SGD)", "AGY-SGD", "PENDENCIA_ALTA"),
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _dump(path: Path, payload: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def _title(body: bytes) -> str | None:
    if not body:
        return None
    match = re.search(r"<title[^>]*>(.*?)</title>", body.decode("utf-8", errors="replace"), re.I | re.S)
    if not match:
        return None
    return re.sub(r"\s+", " ", match.group(1)).strip()[:200]


def _official_gov_pdf_links(html: str, page_url: str) -> list[dict]:
    """href .pdf on gov.br only. Ignore third-party chrome (ABNT/mwpt)."""
    from urllib.parse import urljoin

    found = []
    seen = set()
    for href, label in re.findall(r'href=["\']([^"\']+)["\'][^>]*>([^<]{0,200})', html, flags=re.I):
        full = urljoin(page_url, href).split("#")[0]
        if ".pdf" not in full.lower():
            continue
        host = urlparse(full).netloc.lower()
        if host.endswith("mwpt.com.br") or "abnt-nbr" in full.lower():
            continue
        if not host.endswith("gov.br"):
            continue
        if full in seen:
            continue
        seen.add(full)
        found.append({
            "url": full,
            "label": re.sub(r"\s+", " ", label).strip()[:180] or None,
        })
    return found


def _quality_dimension_names(html: str) -> list[dict]:
    text = re.sub(r"<script[\s\S]*?</script>", " ", html, flags=re.I)
    text = re.sub(r"<style[\s\S]*?</style>", " ", text, flags=re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    names = []
    seen = set()
    dim_re = re.compile(
        r"DIMENS[AÃ]O\s+(\d+)\s+(Facilidade|Comunica[cç][aã]o|Atendimento|Experi[eê]ncia Unificada|"
        r"Acessibilidade|Privacidade e Seguran[cç]a|Escuta Ativa)",
        flags=re.I,
    )
    for match in dim_re.finditer(text):
        n = int(match.group(1))
        name = match.group(2).strip()
        if n in seen or not name:
            continue
        seen.add(n)
        names.append({"n": n, "name": name, "clause_text": "NOT_COPIED_AS_PRODUCT_RULE"})
    return names


def catalog_pgdados(pages: list[dict]) -> dict:
    """MD catalog of observed PGDADOS/quality pages and official PDF hrefs. No PDF body as product rule."""
    gov_dir = ROOT / "cko_inbox" / "gov"
    guia_parts = []
    cartilhas = []
    quality_dims = []
    ignored_third_party = 0
    for src in GOV_HTML:
        key = src["business_key"]
        html_path = gov_dir / f"{key}.html"
        page = next((item for item in pages if item.get("business_key") == key), {})
        html = html_path.read_text(encoding="utf-8", errors="replace") if html_path.exists() else ""
        pdfs = _official_gov_pdf_links(html, src["url"]) if html else []
        ignored_third_party += html.lower().count("mwpt.com.br") if html else 0
        if key == "SRC-GOV-PGDADOS-GUIA":
            for pdf in pdfs:
                label = (pdf.get("label") or pdf["url"]).lower()
                part = None
                if "parte-1" in pdf["url"] or "parte 1" in label:
                    part = 1
                elif "parte-2" in pdf["url"] or "parte 2" in label:
                    part = 2
                elif "parte-3" in pdf["url"] or "parte 3" in label:
                    part = 3
                guia_parts.append({
                    "business_key": f"RES-PGDADOS-GUIA-P{part}" if part else f"RES-PGDADOS-GUIA-{len(guia_parts)+1}",
                    "uuid": None,
                    "part": part,
                    "title": pdf.get("label") or f"Guia PGDADOS parte {part}",
                    "url": pdf["url"],
                    "source_ref": key,
                    "md_ref": src["md_ref"],
                    "reg_ref": src["reg_ref"],
                    "status": "SOURCE_DERIVED" if page.get("http_status") == 200 else "EVIDENCE_PENDING",
                    "clause_text": "NOT_COPIED_AS_PRODUCT_RULE",
                    "republication": "METADATA_ONLY",
                })
            if not any(item.get("part") == 3 for item in guia_parts):
                guia_parts.append({
                    "business_key": "RES-PGDADOS-GUIA-P3",
                    "uuid": None,
                    "part": 3,
                    "title": "Parte 3 — PDF gov.br não observado",
                    "url": None,
                    "source_ref": key,
                    "md_ref": src["md_ref"],
                    "reg_ref": src["reg_ref"],
                    "status": "EVIDENCE_PENDING",
                    "note": "Estrutura citada na página. PDF gov.br não observado neste lote.",
                    "clause_text": "NOT_COPIED_AS_PRODUCT_RULE",
                    "republication": "METADATA_ONLY",
                })
        if key == "SRC-GOV-PGDADOS-HUB":
            for pdf in pdfs:
                vol = None
                m = re.search(r"volume-(\d+)", pdf["url"], flags=re.I)
                if m:
                    vol = int(m.group(1))
                cartilhas.append({
                    "business_key": f"RES-PGDADOS-CARTILHA-V{vol}" if vol else f"RES-PGDADOS-CARTILHA-{len(cartilhas)+1}",
                    "uuid": None,
                    "volume": vol,
                    "title": pdf.get("label") or f"Cartilha volume {vol}",
                    "url": pdf["url"],
                    "source_ref": key,
                    "md_ref": src["md_ref"],
                    "reg_ref": src["reg_ref"],
                    "status": "SOURCE_DERIVED" if page.get("http_status") == 200 else "EVIDENCE_PENDING",
                    "clause_text": "NOT_COPIED_AS_PRODUCT_RULE",
                    "republication": "METADATA_ONLY",
                })
            html_l = html.lower()
            for vol in (4, 5):
                if any(item.get("volume") == vol for item in cartilhas):
                    continue
                mentioned = f"volume {vol}" in html_l or f"volume-{vol}" in html_l
                cartilhas.append({
                    "business_key": f"RES-PGDADOS-CARTILHA-V{vol}",
                    "uuid": None,
                    "volume": vol,
                    "title": f"Volume {vol} — PDF gov.br não observado",
                    "url": None,
                    "source_ref": key,
                    "md_ref": src["md_ref"],
                    "reg_ref": src["reg_ref"],
                    "status": "EVIDENCE_PENDING",
                    "label_mentioned_on_page": mentioned,
                    "note": "Volume previsto na trilha. Sem href PDF gov.br neste lote.",
                    "clause_text": "NOT_COPIED_AS_PRODUCT_RULE",
                    "republication": "METADATA_ONLY",
                })
        if key == "SRC-GOV-QUALIDADE-DIGIT" and html:
            quality_dims = _quality_dimension_names(html)
    payload = {
        "business_key": "MD-PGDADOS-001",
        "uuid": None,
        "status": "REGISTERED",
        "publication": "HOLD",
        "assured": False,
        "issuer": "Secretaria de Governo Digital / MGI",
        "agency_key": "AGY-SGD",
        "parent_agency": "AGY-MGI",
        "drive": "NOT_FOUND",
        "nifs": "NOT_FOUND",
        "supabase": "EVIDENCE_PENDING",
        "guia_parts": guia_parts,
        "cartilhas": cartilhas,
        "quality_dimensions": quality_dims,
        "quality_dimension_count": len(quality_dims),
        "glossary_url": (
            "https://www.gov.br/governodigital/pt-br/infraestrutura-nacional-de-dados/"
            "governancadedados/glossario-de-termos-de-dados"
        ),
        "data_quality_dimensions": [
            {
                "name": name,
                "source_url": (
                    "https://www.gov.br/governodigital/pt-br/infraestrutura-nacional-de-dados/"
                    "governancadedados/glossario-de-termos-de-dados"
                ),
                "source": "Cartilha Governança de Dados Volume I (nome no glossário)",
                "clause_text": "NOT_COPIED_AS_PRODUCT_RULE",
            }
            for name in (
                "integridade",
                "padronização",
                "precisão",
                "acurácia",
                "atualização",
                "acessibilidade",
                "confiabilidade",
            )
        ],
        "implementation_instruments": [
            "Política Interna de Governança de Dados",
            "Estratégia de Dados",
            "Plano de Implementação do Programa de Governança de Dados",
        ],
        "third_party_pdf_ignored": ignored_third_party > 0,
        "third_party_note": "PDF ABNT/mwpt no chrome do portal não entra no catálogo CKO.",
        "clause_text": "NOT_COPIED_AS_PRODUCT_RULE",
        "rule": "Catálogo de metadados oficiais. PDF não é regra de produto. LLM não autorou o conteúdo.",
    }
    _dump(ROOT / "cko_md" / "pgdados_program.json", payload)
    _dump(ROOT / "cko_inbox" / "extracted" / "pgdados_program.json", payload)
    return payload


def write_agency_md() -> dict:
    agencies = [
        {"business_key": "AGY-ANVISA", "name": "ANVISA", "jurisdiction": "JUR-BR", "uuid": None, "status": "REGISTERED"},
        {"business_key": "AGY-MS", "name": "Ministério da Saúde", "jurisdiction": "JUR-BR", "uuid": None, "status": "REGISTERED"},
        {"business_key": "AGY-COFEN", "name": "COFEN", "jurisdiction": "JUR-BR", "uuid": None, "status": "REGISTERED", "rest_api": "NOT_OBSERVED", "note": "Portal HTML. Sem REST HTTP 200 neste lote. Não inventar base_url."},
        {"business_key": "AGY-COREN-SP", "name": "COREN-SP", "jurisdiction": "JUR-BR", "uuid": None, "status": "REGISTERED", "rest_api": "NOT_OBSERVED", "note": "Sem API REST. Portal HTML estadual apenas. Demais CORENs não observados."},
        {"business_key": "AGY-MGI", "name": "Ministério da Gestão e da Inovação em Serviços Públicos", "jurisdiction": "JUR-BR", "uuid": None, "status": "REGISTERED", "rest_api": "NOT_OBSERVED"},
        {"business_key": "AGY-SGD", "name": "Secretaria de Governo Digital", "jurisdiction": "JUR-BR", "uuid": None, "status": "REGISTERED", "parent_agency": "AGY-MGI", "rest_api": "NOT_OBSERVED", "note": "Portal Gov.br / Governo Digital. PGDADOS e Padrões de Qualidade."},
        {"business_key": "AGY-DADOSGOV", "name": "dados.gov.br", "jurisdiction": "JUR-BR", "uuid": None, "status": "REGISTERED"},
        {"business_key": "AGY-CONGRESSO", "name": "Congresso Nacional", "jurisdiction": "JUR-BR", "uuid": None, "status": "REGISTERED", "note": "Legislação federal via Dados Abertos Senado/Câmara. Não é NIFS."},
        {"business_key": "AGY-CROSSREF", "name": "Crossref", "jurisdiction": "JUR-INTL", "uuid": None, "status": "REGISTERED", "note": "API bibliográfica. Não é autoridade clínica."},
        {"business_key": "AGY-NCBI", "name": "NCBI / NLM", "jurisdiction": "JUR-US", "uuid": None, "status": "REGISTERED", "note": "E-utilities. Busca, não full-text canônico."},
        {"business_key": "AGY-NLM", "name": "U.S. National Library of Medicine", "jurisdiction": "JUR-US", "uuid": None, "status": "REGISTERED", "note": "Clinical Tables = busca. Não dump de classificação."},
        {"business_key": "AGY-FDA", "name": "U.S. Food and Drug Administration", "jurisdiction": "JUR-US", "uuid": None, "status": "REGISTERED", "note": "openFDA = busca de rótulo. Fallback se API ANVISA/CKAN BR falhar."},
        {"business_key": "AGY-WHO", "name": "Organização Mundial da Saúde", "jurisdiction": "JUR-INTL", "uuid": None, "status": "REGISTERED", "note": "GHO OData observado. IRIS é HTML. Não republica escala."},
    ]
    payload = {
        "business_key": "MD-AGENCY-REG-001",
        "uuid": None,
        "status": "REGISTERED",
        "identity_scheme": "CKO-BK-1",
        "agencies": agencies,
        "population": len(agencies),
        "rule": "Identidade MD da agência precede adapter de API e conteúdo.",
    }
    _dump(ROOT / "cko_md" / "agency_registry.json", payload)
    api_path = ROOT / "cko_assurance" / "api_registry.json"
    try:
        api_payload = json.loads(api_path.read_text(encoding="utf-8")) if api_path.exists() else {}
    except json.JSONDecodeError:
        api_payload = {}
    apis = [item for item in (api_payload.get("apis") or []) if item.get("business_key") not in {"API-CAND-COFEN", "API-CAND-COREN"}]
    apis = [
        {
            "business_key": "API-CAND-COFEN",
            "name": "COFEN",
            "base_url": None,
            "html_page": "https://www.cofen.gov.br/",
            "kind": "REGULATED_HTML_PAGE",
            "rest_api": "NOT_OBSERVED",
            "status": "SOURCE_DERIVED",
            "note": "Portal HTML. Sem REST HTTP 200. Não inventar base_url.",
        },
        {
            "business_key": "API-CAND-COREN",
            "name": "COREN",
            "base_url": None,
            "html_page": "https://www.coren-sp.gov.br/",
            "kind": "NO_REST_API",
            "rest_api": "NOT_OBSERVED",
            "status": "SOURCE_DERIVED",
            "note": "COREN não possui API REST observada. Apenas portal HTML estadual.",
        },
    ] + apis
    _dump(api_path, {
        "business_key": api_payload.get("business_key") or "REG-API-001",
        "status": "REGISTERED",
        "implemented": False,
        "note": "API REST base_url permanece null até HTTP 200. COREN/COFEN sem REST observada.",
        "apis": apis,
    })
    return payload


def write_source_reg() -> dict:
    items = []
    for src in GOV_HTML:
        items.append({
            "business_key": src["reg_ref"],
            "source_ref": src["business_key"],
            "md_ref": src["md_ref"],
            "reg_ref": src["reg_ref"],
            "agency_key": src["agency_key"],
            "issuer": src["agency"],
            "jurisdiction": "JUR-BR",
            "instrument_class": "PUBLIC_ADMINISTRATIVE_PAGE",
            "rights": "GOVERNMENT_PAGE_METADATA_ONLY",
            "clause_text": "NOT_COPIED_AS_PRODUCT_RULE",
            "applicability": "APPLICABILITY_UNVERIFIED",
            "republication": "FORBIDDEN_FULL_HTML",
            "status": "DOCUMENTADO",
            "uuid": None,
            "rest_api": "NOT_OBSERVED" if src["agency_key"] in {"AGY-COFEN", "AGY-COREN-SP"} else None,
        })
    for api in API_CANDIDATES:
        items.append({
            "business_key": api["reg_ref"],
            "source_ref": api["business_key"],
            "md_ref": api["md_ref"],
            "reg_ref": api["reg_ref"],
            "agency_key": api["agency_key"],
            "issuer": api["agency"],
            "jurisdiction": "JUR-INTL" if api["agency_key"] in {"AGY-CROSSREF", "AGY-NCBI", "AGY-NLM"} else "JUR-BR",
            "instrument_class": "OPEN_DATA_API_CANDIDATE",
            "rights": "OPEN_DATA_IF_OBSERVED",
            "clause_text": "NOT_COPIED_AS_PRODUCT_RULE",
            "applicability": "APPLICABILITY_UNVERIFIED",
            "status": "DOCUMENTADO",
            "uuid": None,
        })
    payload = {
        "business_key": "REG-GOV-SRC-001",
        "uuid": None,
        "status": "DOCUMENTADO",
        "qualifications": items,
        "population": len(items),
        "rule": "REG qualifica. REG não cria identidade. Texto de norma licenciada = CLAUSE_TEXT_UNAVAILABLE.",
    }
    _dump(ROOT / "cko_reg" / "source_qualification.json", payload)
    return payload


def fetch_gov_sources(*, network: bool) -> dict:
    """AG-FETCH-GOV-SOURCES — official HTML. Replay inbox when offline."""
    from .agents import UA_BROWSER, _http_get
    from .vault import put_bytes

    dest = ROOT / "cko_inbox" / "extracted" / "gov_pages.json"
    gov_dir = ROOT / "cko_inbox" / "gov"
    gov_dir.mkdir(parents=True, exist_ok=True)
    write_agency_md()
    write_source_reg()
    pages = []
    if network:
        for src in GOV_HTML:
            rec = _http_get(src["url"], user_agent=UA_BROWSER)
            body = rec.pop("body", b"") or b""
            path = gov_dir / f"{src['business_key']}.html"
            if body:
                path.write_bytes(body)
                put_bytes(
                    body,
                    logical_id=src["business_key"],
                    source_url=src["url"],
                    source_path=str(path.relative_to(ROOT)),
                    media_type="text/html",
                    mask_id="MASK-REGULATED-HTML",
                    note="Government HTML unaltered",
                )
            pages.append({
                **src,
                "http_status": rec.get("http_status"),
                "bytes": rec.get("bytes") or len(body),
                "sha256": rec.get("sha256") or (_sha256_bytes(body) if body else None),
                "title": _title(body),
                "error": rec.get("error"),
                "epistemic_status": rec.get("epistemic_status") or "EVIDENCE_PENDING",
                "captured_at": _now(),
                "api_base_url": None,
                "inbox_path": str(path.relative_to(ROOT)) if path.exists() else None,
            })
        _dump(dest, {
            "business_key": "IPE-GOV-PAGES-001",
            "uuid": None,
            "status": "SOURCE_DERIVED",
            "captured_at": _now(),
            "frequency_hours": FREQ_HOURS,
            "pages": pages,
        })
    elif dest.exists():
        pages = json.loads(dest.read_text(encoding="utf-8")).get("pages") or []
    else:
        pages = [{
            **src,
            "http_status": None,
            "bytes": None,
            "sha256": None,
            "title": None,
            "error": "offline_no_inbox",
            "epistemic_status": "EVIDENCE_PENDING",
            "captured_at": None,
            "api_base_url": None,
            "inbox_path": None,
        } for src in GOV_HTML]
        _dump(dest, {
            "business_key": "IPE-GOV-PAGES-001",
            "uuid": None,
            "status": "EVIDENCE_PENDING",
            "captured_at": _now(),
            "frequency_hours": FREQ_HOURS,
            "pages": pages,
        })
    catalog_pgdados(pages)
    return {
        "agent_id": "AG-FETCH-GOV-SOURCES",
        "class": "ACQUISITION",
        "role": "MAKER",
        "network": network,
        "pages": pages,
        "api_base_url_set": False,
        "promotes_to_md": False,
        "status": "OBSERVED" if pages else "EVIDENCE_PENDING",
    }


def write_scale_search_probe(*, network: bool) -> dict:
    """Bibliographic search for third-party scales. Search ≠ instrument dump."""
    dest = ROOT / "cko_inbox" / "extracted" / "scale_search_probe.json"
    if dest.exists() and not network:
        return json.loads(dest.read_text(encoding="utf-8"))
    from .agents import UA_BROWSER, _http_get

    queries = (
        {
            "id": "SCALE-BRADEN",
            "term": "Braden scale pressure ulcer",
            "url": "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=Braden+scale+pressure+ulcer&retmax=0&retmode=json",
        },
        {
            "id": "SCALE-NORTON",
            "term": "Norton scale pressure ulcer",
            "url": "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=Norton+scale+pressure+ulcer&retmax=0&retmode=json",
        },
        {
            "id": "SCALE-GLASGOW",
            "term": "Glasgow Coma Scale",
            "url": "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=Glasgow+Coma+Scale&retmax=0&retmode=json",
        },
    )
    pubmed = []
    if network:
        for item in queries:
            rec = _http_get(item["url"], timeout=25, user_agent=UA_BROWSER)
            body = rec.get("body") or b""
            count = None
            try:
                payload = json.loads(body.decode("utf-8", errors="replace"))
                count = (payload.get("esearchresult") or {}).get("count")
            except (json.JSONDecodeError, UnicodeDecodeError, AttributeError):
                count = None
            pubmed.append({
                **item,
                "http_status": rec.get("http_status"),
                "count": count,
                "kind": "LITERATURE_SEARCH",
                "republication": "FORBIDDEN",
            })
        scielo = _http_get("https://search.scielo.org/?q=braden&lang=pt&format=json", timeout=20, user_agent=UA_BROWSER)
        cofen = _http_get("https://www.cofen.gov.br/?s=braden", timeout=20, user_agent=UA_BROWSER)
        anvisa = _http_get("https://www.gov.br/anvisa/pt-br/search?SearchableText=braden", timeout=20, user_agent=UA_BROWSER)
        who_iris = _http_get("https://iris.who.int/discover?query=glasgow+coma+scale", timeout=20, user_agent=UA_BROWSER)
        payload = {
            "business_key": "IPE-SCALE-SEARCH-001",
            "uuid": None,
            "status": "SOURCE_DERIVED",
            "rule": "Busca bibliográfica ≠ republicação do instrumento. Sem copiar itens Braden/Norton/Glasgow.",
            "pubmed": pubmed,
            "scielo": {
                "url": "https://search.scielo.org/?q=braden&lang=pt&format=json",
                "http_status": scielo.get("http_status"),
                "epistemic_status": "OBSERVED" if scielo.get("http_status") == 200 else "EVIDENCE_PENDING",
            },
            "cofen_html": {
                "url": "https://www.cofen.gov.br/?s=braden",
                "http_status": cofen.get("http_status"),
                "kind": "HTML_SEARCH",
                "rest_api": "NOT_OBSERVED",
            },
            "anvisa_html": {
                "url": "https://www.gov.br/anvisa/pt-br/search?SearchableText=braden",
                "http_status": anvisa.get("http_status"),
                "kind": "HTML_SEARCH",
                "rest_api": "NOT_OBSERVED",
            },
            "who_iris_html": {
                "url": "https://iris.who.int/discover?query=glasgow+coma+scale",
                "http_status": who_iris.get("http_status"),
                "kind": "HTML_SEARCH",
            },
            "probed_at": _now(),
        }
        _dump(dest, payload)
        return payload
    payload = {
        "business_key": "IPE-SCALE-SEARCH-001",
        "uuid": None,
        "status": "EVIDENCE_PENDING",
        "rule": "Busca bibliográfica ≠ republicação do instrumento.",
        "pubmed": [],
        "probed_at": None,
    }
    _dump(dest, payload)
    return payload


def probe_apis(*, network: bool) -> dict:
    """AG-API-PROBE — observe candidate REST. Never invent HTTP 200 or base_url."""
    from .agents import UA_BROWSER, _http_get

    dest = ROOT / "cko_inbox" / "extracted" / "api_probe.json"
    persisted = {}
    if dest.exists():
        persisted = {
            item.get("business_key"): item
            for item in (json.loads(dest.read_text(encoding="utf-8")).get("adapters") or [])
            if item.get("business_key")
        }
    adapters = []
    if network:
        for cand in API_CANDIDATES:
            rec = _http_get(cand["url"], timeout=25, user_agent=UA_BROWSER)
            body = rec.pop("body", b"") or b""
            observed_ok = rec.get("http_status") == 200
            host = urlparse(cand["url"]).netloc
            adapters.append({
                **cand,
                "uuid": None,
                "http_status": rec.get("http_status"),
                "bytes": rec.get("bytes") or len(body),
                "sha256": rec.get("sha256"),
                "error": rec.get("error"),
                "epistemic_status": "OBSERVED" if observed_ok else "EVIDENCE_PENDING",
                "base_url": f"https://{host}/" if observed_ok else None,
                "online": bool(observed_ok),
                "note": cand.get("note") or "API observada só se HTTP 200. Sem 200, base_url permanece null. API pode ficar offline; extração é periódica.",
                "probed_at": _now(),
            })
        _dump(dest, {
            "business_key": "IPE-API-PROBE-001",
            "uuid": None,
            "status": "SOURCE_DERIVED",
            "probed_at": _now(),
            "frequency_hours": FREQ_HOURS,
            "adapters": adapters,
        })
    else:
        for cand in API_CANDIDATES:
            prev = persisted.get(cand["business_key"]) or {}
            if prev:
                adapters.append({**cand, **prev, "business_key": cand["business_key"], "url": cand["url"]})
            else:
                adapters.append({
                    **cand,
                    "uuid": None,
                    "http_status": None,
                    "bytes": None,
                    "sha256": None,
                    "error": "offline_no_inbox",
                    "epistemic_status": "EVIDENCE_PENDING",
                    "base_url": None,
                    "online": False,
                    "note": cand.get("note") or "Probe não executado. base_url null até HTTP 200 observado.",
                    "probed_at": None,
                })
        _dump(dest, {
            "business_key": "IPE-API-PROBE-001",
            "uuid": None,
            "status": "SOURCE_DERIVED" if any(item.get("http_status") is not None for item in adapters) else "EVIDENCE_PENDING",
            "probed_at": _now() if any(item.get("http_status") is not None for item in adapters) else None,
            "frequency_hours": FREQ_HOURS,
            "adapters": adapters,
        })
    write_scale_search_probe(network=network)
    md = {
        "business_key": "MD-API-ADAPTER-REG-001",
        "uuid": None,
        "status": "REGISTERED",
        "implemented": False,
        "production_api": False,
        "frequency_hours": FREQ_HOURS,
        "adapters": adapters,
        "population": len(adapters),
        "rule": "Resposta de API não vira verdade canônica sem snapshot, hash, MD, REG e validação.",
    }
    _dump(ROOT / "cko_md" / "api_adapter_registry.json", md)
    return {
        "agent_id": "AG-API-PROBE",
        "class": "ACQUISITION",
        "role": "MAKER",
        "network": network,
        "adapters": adapters,
        "online_count": sum(1 for item in adapters if item.get("online")),
        "promotes_to_md": False,
        "status": "OBSERVED" if adapters else "EVIDENCE_PENDING",
    }


def catalog_library() -> dict:
    """AG-LIBRARY-CATALOG — catalog observed gov pages as library resources. No full HTML republish."""
    gov = json.loads((ROOT / "cko_inbox" / "extracted" / "gov_pages.json").read_text(encoding="utf-8")) if (ROOT / "cko_inbox" / "extracted" / "gov_pages.json").exists() else {}
    probe = json.loads((ROOT / "cko_inbox" / "extracted" / "api_probe.json").read_text(encoding="utf-8")) if (ROOT / "cko_inbox" / "extracted" / "api_probe.json").exists() else {}
    laws = json.loads((ROOT / "cko_md" / "legislation_instrument_registry.json").read_text(encoding="utf-8")) if (ROOT / "cko_md" / "legislation_instrument_registry.json").exists() else {}
    resources = []
    for page in gov.get("pages") or []:
        observed = page.get("epistemic_status") == "OBSERVED" and page.get("http_status") == 200
        resources.append({
            "business_key": f"RES-{page['business_key']}",
            "uuid": None,
            "entity_type": "ETYPE-RESOURCE",
            "title": page.get("title") or page.get("agency"),
            "agency_key": page.get("agency_key"),
            "source_ref": page["business_key"],
            "md_ref": page.get("md_ref"),
            "reg_ref": page.get("reg_ref"),
            "layer": page.get("layer"),
            "url": page.get("url"),
            "sha256": page.get("sha256"),
            "kind": "GOVERNMENT_PORTAL_SNAPSHOT",
            "republication": "METADATA_ONLY",
            "status": "SOURCE_DERIVED" if observed else "EVIDENCE_PENDING",
            "assured": False,
            "publication": "HOLD",
        })
    for item in laws.get("instruments") or []:
        resources.append({
            "business_key": f"RES-{item['business_key']}",
            "uuid": None,
            "entity_type": "ETYPE-RESOURCE",
            "title": item.get("title") or item.get("business_key"),
            "agency_key": "AGY-CONGRESSO",
            "source_ref": item.get("business_key"),
            "md_ref": item.get("md_ref"),
            "reg_ref": item.get("reg_ref"),
            "layer": "L140",
            "url": item.get("url"),
            "sha256": item.get("sha256"),
            "kind": "FEDERAL_REGULATORY_DECREE_METADATA" if str(item.get("tipo") or "").startswith("DEC") else "FEDERAL_LEGISLATION_METADATA",
            "republication": "METADATA_ONLY",
            "status": "REVOKED_TOOL_OK" if item.get("revoked") else "SOURCE_DERIVED",
            "revoked": bool(item.get("revoked")),
            "assured": False,
            "publication": "HOLD",
            "note": (
                "Decreto regulamentar: órgão emite; corpus federal no Congresso/normas.leg.br. Texto integral não republicado."
                if str(item.get("tipo") or "").startswith("DEC")
                else "Norma revogada permitida como ferramenta. Texto integral não republicado."
            ),
        })
    pgd = json.loads((ROOT / "cko_md" / "pgdados_program.json").read_text(encoding="utf-8")) if (ROOT / "cko_md" / "pgdados_program.json").exists() else {}
    for item in (pgd.get("guia_parts") or []) + (pgd.get("cartilhas") or []):
        resources.append({
            "business_key": item["business_key"],
            "uuid": None,
            "entity_type": "ETYPE-RESOURCE",
            "title": item.get("title") or item["business_key"],
            "agency_key": "AGY-SGD",
            "source_ref": item.get("source_ref"),
            "md_ref": item.get("md_ref") or "MD-AGY-SGD",
            "reg_ref": item.get("reg_ref") or "REG-SRC-PGDADOS-HUB",
            "layer": "L150",
            "url": item.get("url"),
            "sha256": None,
            "kind": "GOVERNMENT_PDF_METADATA",
            "republication": "METADATA_ONLY",
            "status": item.get("status") or "EVIDENCE_PENDING",
            "assured": False,
            "publication": "HOLD",
            "note": item.get("note") or "PDF oficial catalogado por href. Texto não copiado.",
        })
    if pgd.get("quality_dimensions"):
        resources.append({
            "business_key": "RES-QUALIDADE-DIGIT-DIM",
            "uuid": None,
            "entity_type": "ETYPE-RESOURCE",
            "title": "Padrões de Qualidade — 7 dimensões (SGD)",
            "agency_key": "AGY-SGD",
            "source_ref": "SRC-GOV-QUALIDADE-DIGIT",
            "md_ref": "MD-AGY-SGD",
            "reg_ref": "REG-SRC-QUALIDADE-DIGIT",
            "layer": "L150",
            "url": next((src["url"] for src in GOV_HTML if src["business_key"] == "SRC-GOV-QUALIDADE-DIGIT"), None),
            "kind": "GOVERNMENT_QUALITY_DIMENSIONS",
            "republication": "METADATA_ONLY",
            "status": "SOURCE_DERIVED",
            "dimension_count": pgd.get("quality_dimension_count"),
            "assured": False,
            "publication": "HOLD",
            "clause_text": "NOT_COPIED_AS_PRODUCT_RULE",
            "note": "Nomes das dimensões observados na página. Atributos não copiados.",
        })
    for topic_key, layer, title, agency, pending in LIBRARY_TOPICS:
        has_source = any(
            item.get("agency_key") == agency and item.get("status") in {"SOURCE_DERIVED", "REVOKED_TOOL_OK"}
            for item in resources
        )
        resources.append({
            "business_key": topic_key,
            "uuid": None,
            "entity_type": "ETYPE-RESOURCE",
            "title": title,
            "agency_key": agency,
            "source_ref": None,
            "md_ref": f"MD-{topic_key}",
            "reg_ref": f"REG-{topic_key}",
            "layer": layer,
            "url": None,
            "sha256": None,
            "kind": "LIBRARY_TOPIC_PLAN",
            "republication": "NOT_APPLICABLE",
            "status": "DOCUMENTADO" if has_source else pending,
            "assured": False,
            "publication": "HOLD",
            "note": "Tópico planejado básico→avançado. Sem objeto de domínio até evidência + REG.",
        })
    payload = {
        "business_key": "MD-LIB-RES-001",
        "uuid": None,
        "status": "REGISTERED",
        "layer": "L60",
        "resources": resources,
        "population": len(resources),
        "api_adapters_observed": sum(1 for item in (probe.get("adapters") or []) if item.get("online")),
        "publication": "HOLD",
        "rule": "Biblioteca cataloga metadados e hashes. Não republica HTML integral. Não cria fórmula.",
    }
    _dump(ROOT / "cko_md" / "resource_library.json", payload)
    return {
        "agent_id": "AG-LIBRARY-CATALOG",
        "class": "CONTENT",
        "role": "MAKER",
        "population": len(resources),
        "promotes_to_md": False,
        "status": "DOCUMENTADO",
        "publication": "HOLD",
    }


def _unit_body(tool: dict, level: str) -> dict:
    overview = tool.get("overview") or {}
    calc = tool.get("calculator") or {}
    formula = calc.get("formula") or {}
    interpretation = tool.get("interpretation") or {}
    sae = tool.get("sae") or {}
    hold = tool.get("status") == "HOLD" or tool.get("slug") == "dimensionamento"
    if hold and level in {"PROCEDIMENTO", "INTERPRETACAO", "AVANCADO"}:
        return {
            "text": "HOLD_OBJECT: fórmula/interpretação não projetadas. Sem evidência canônica neste lote.",
            "fields_used": ["status"],
            "status": "HOLD",
        }
    if level == "BASICO":
        return {
            "text": " ".join(part for part in (overview.get("objective"), overview.get("indication")) if part),
            "fields_used": ["overview.objective", "overview.indication"],
            "status": "DOCUMENTADO",
        }
    if level == "FUNDAMENTOS":
        inputs = calc.get("inputs") or []
        labels = [f"{item.get('label')} ({item.get('unit') or 'sem unidade'})" for item in inputs]
        pop = overview.get("targetPopulation") or ""
        return {
            "text": ("; ".join(labels) + (". " + pop if pop else "")).strip(),
            "fields_used": ["calculator.inputs", "overview.targetPopulation"],
            "status": "DOCUMENTADO" if labels or pop else "HOLD",
        }
    if level == "PROCEDIMENTO":
        expr = formula.get("expression")
        return {
            "text": f"Expressão canônica: {expr}" if expr else "Sem expressão neste objeto.",
            "fields_used": ["calculator.formula.expression"],
            "status": "DOCUMENTADO" if expr else "HOLD",
        }
    if level == "INTERPRETACAO":
        chunks = [interpretation.get("resultLabel"), interpretation.get("note")]
        if isinstance(interpretation.get("bands"), list):
            chunks.extend(str(band.get("label") or band) for band in interpretation["bands"][:6])
        text = " ".join(str(item) for item in chunks if item)
        return {
            "text": text or "Interpretação não preenchida no objeto MD.",
            "fields_used": ["interpretation"],
            "status": "DOCUMENTADO" if text else "HOLD",
        }
    sae_status = sae.get("status") or "UNKNOWN"
    return {
        "text": f"SAE status={sae_status}. Avançado permanece HOLD até fonte SAE licenciada.",
        "fields_used": ["sae.status"],
        "status": "HOLD" if sae_status == "HOLD" else "DOCUMENTADO",
    }


def content_curriculum() -> dict:
    """AG-CONTENT-CURRICULUM — documentary básico→avançado from existing tool MD only."""
    units = []
    for path in sorted(TOOLS_DIR.glob("*.json")):
        tool = json.loads(path.read_text(encoding="utf-8"))
        slug = tool.get("slug")
        work_ref = f"MD-TOOL-{slug}"
        rights_ref = "REG-RIGHTS-LEI-9610"
        for order, (level, label) in enumerate(LEVELS, start=1):
            body = _unit_body(tool, level)
            blob = json.dumps(body, ensure_ascii=False, sort_keys=True).encode("utf-8")
            units.append({
                "business_key": f"CNT-{slug}-{level}",
                "uuid": None,
                "entity_type": "ETYPE-CONTENT_OBJECT",
                "tool_slug": slug,
                "tool_md_ref": work_ref,
                "reg_ref": rights_ref,
                "level": level,
                "order": order,
                "label": label,
                "body": body,
                "sha256": _sha256_bytes(blob),
                "assured": False,
                "publication": "HOLD",
                "generated_by": "AG-CONTENT-CURRICULUM",
                "llm_authored": False,
            })
    pending = [
        {
            "business_key": "PEND-COREN-DEMAIS-UFS",
            "severity": "ALTA",
            "reason": "Apenas COREN-SP tem portal HTML candidato. REST API de COREN não observada. Não inventar adapter. Demais Conselhos Regionais não observados.",
            "government_alternative_sought": True,
            "alternative": "Portal COFEN nacional (também HTML; REST não observada).",
            "status": "PENDENCIA_ALTA",
        },
        {
            "business_key": "PEND-COFEN-REST-NOT-OBSERVED",
            "severity": "ALTA",
            "reason": "COFEN: portal HTML observado. REST/dados abertos sem HTTP 200 neste lote. Não inventar base_url.",
            "government_alternative_sought": True,
            "alternative": "https://www.cofen.gov.br/ — HTML. Plano de dados abertos = EVIDENCE_PENDING.",
            "status": "PENDENCIA_ALTA",
        },
        {
            "business_key": "PEND-ISO-CLAUSE-TEXT",
            "severity": "ALTA",
            "reason": "Texto de cláusula ISO licenciada indisponível. Government alternative NÃO substitui ISO 8000 clause text.",
            "government_alternative_sought": True,
            "alternative": (
                "https://www.gov.br/governodigital/pt-br/infraestrutura-nacional-de-dados/"
                "governancadedados/pgdados — referência operacional BR (PGDADOS). "
                "Não substitui texto de cláusula ISO licenciada."
            ),
            "status": "PENDENCIA_ALTA",
        },
        {
            "business_key": "PEND-THIRD-PARTY-SCALES",
            "severity": "ALTA",
            "reason": (
                "Braden/Norton/Glasgow: obra de terceiros. Busca bibliográfica permitida "
                "(PubMed/COFEN/ANVISA HTML/OMS). Republicar o instrumento continua FORBIDDEN."
            ),
            "government_alternative_sought": True,
            "alternative": (
                "PubMed E-utilities HTTP 200 (contagens). COFEN/ANVISA HTML 200. OMS GHO JSON 200. "
                "SciELO JSON 403 = EVIDENCE_PENDING. Nenhum equivalente autoriza republicar itens da escala."
            ),
            "status": "PENDENCIA_ALTA",
        },
        {
            "business_key": "PEND-PAGES-FULL-1516",
            "severity": "ALTA",
            "reason": (
                "1516 HTML = catálogo de pendências REG (1 stem → 1 gap MD+REG+rights). "
                "Inventário demonstra as pendências. Extração em massa de fórmula clínica para data/tools permanece FORBIDDEN."
            ),
            "government_alternative_sought": False,
            "reg_pendency_catalog": True,
            "catalog_ref": "MD-PAGES-REG-PEND-001",
            "status": "PENDENCIA_ALTA",
        },
        {
            "business_key": "PEND-ANVISA-REST-PRODUCT",
            "severity": "ALTA",
            "reason": "API de produtos ANVISA autenticada/consulta não observada como REST pública estável neste ambiente.",
            "government_alternative_sought": True,
            "alternative": (
                "CKAN dados.gov.br package_search q=anvisa = HTTP 401 neste lote. "
                "Fallback US gov: API-OPENFDA-DRUGLABEL (HTTP 200 JSON). Não substitui bula ANVISA."
            ),
            "status": "PENDENCIA_ALTA",
        },
        {
            "business_key": "PEND-SUPABASE-LEGISLATION",
            "severity": "ALTA",
            "reason": "Supabase legislation/tables: autenticação MCP falhou. Nada inventado. Extração federal usa API do Congresso.",
            "government_alternative_sought": True,
            "alternative": "https://legis.senado.leg.br/dadosabertos/legislacao",
            "status": "PENDENCIA_ALTA",
        },
    ]
    payload = {
        "business_key": "MD-CONTENT-CURR-001",
        "uuid": None,
        "status": "DOCUMENTADO",
        "logic": "BASICO → FUNDAMENTOS → PROCEDIMENTO → INTERPRETACAO → AVANCADO",
        "llm_authored": False,
        "units": units,
        "population": len(units),
        "pending_high": pending,
        "pending_high_count": len(pending),
        "publication": "HOLD",
        "rule": "Envelope de conteúdo referencia MD/REG. Não inventa dose, fórmula nem cláusula.",
    }
    _dump(ROOT / "cko_md" / "content_curriculum.json", payload)
    return {
        "agent_id": "AG-CONTENT-CURRICULUM",
        "class": "CONTENT",
        "role": "MAKER",
        "population": len(units),
        "pending_high_count": len(pending),
        "llm_used": False,
        "promotes_to_md": False,
        "status": "DOCUMENTADO",
        "publication": "HOLD",
    }


def sync_ops_db() -> dict:
    """AG-OPS-DB-SYNC — SQLite inbox mirror. Not production Postgres. No RLS change."""
    INBOX_DB.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(INBOX_DB)
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS sources (
            business_key TEXT PRIMARY KEY,
            agency_key TEXT,
            url TEXT,
            kind TEXT,
            md_ref TEXT NOT NULL,
            reg_ref TEXT NOT NULL,
            frequency_hours INTEGER,
            http_status INTEGER,
            sha256 TEXT,
            epistemic_status TEXT
        );
        CREATE TABLE IF NOT EXISTS resources (
            business_key TEXT PRIMARY KEY,
            title TEXT,
            source_ref TEXT,
            md_ref TEXT NOT NULL,
            reg_ref TEXT NOT NULL,
            status TEXT,
            layer TEXT
        );
        CREATE TABLE IF NOT EXISTS content_units (
            business_key TEXT PRIMARY KEY,
            tool_slug TEXT,
            level TEXT,
            md_ref TEXT NOT NULL,
            reg_ref TEXT NOT NULL,
            status TEXT,
            sha256 TEXT
        );
        CREATE TABLE IF NOT EXISTS alerts (
            business_key TEXT PRIMARY KEY,
            severity TEXT,
            kind TEXT,
            message TEXT,
            source_ref TEXT,
            status TEXT,
            created_at TEXT
        );
        CREATE TABLE IF NOT EXISTS legislation (
            business_key TEXT PRIMARY KEY,
            tipo TEXT,
            numero TEXT,
            ano INTEGER,
            md_ref TEXT NOT NULL,
            reg_ref TEXT NOT NULL,
            status TEXT,
            revoked INTEGER,
            sha256 TEXT
        );
        """
    )
    gov = json.loads((ROOT / "cko_inbox" / "extracted" / "gov_pages.json").read_text(encoding="utf-8")) if (ROOT / "cko_inbox" / "extracted" / "gov_pages.json").exists() else {}
    lib = json.loads((ROOT / "cko_md" / "resource_library.json").read_text(encoding="utf-8")) if (ROOT / "cko_md" / "resource_library.json").exists() else {}
    curr = json.loads((ROOT / "cko_md" / "content_curriculum.json").read_text(encoding="utf-8")) if (ROOT / "cko_md" / "content_curriculum.json").exists() else {}
    alerts = json.loads((ROOT / "cko_assurance" / "freshness_alerts.json").read_text(encoding="utf-8")) if (ROOT / "cko_assurance" / "freshness_alerts.json").exists() else {}
    laws = json.loads((ROOT / "cko_md" / "legislation_instrument_registry.json").read_text(encoding="utf-8")) if (ROOT / "cko_md" / "legislation_instrument_registry.json").exists() else {}
    conn.execute("DELETE FROM sources")
    conn.execute("DELETE FROM resources")
    conn.execute("DELETE FROM content_units")
    conn.execute("DELETE FROM alerts")
    conn.execute("DELETE FROM legislation")
    for page in gov.get("pages") or []:
        conn.execute(
            "INSERT INTO sources VALUES (?,?,?,?,?,?,?,?,?,?)",
            (
                page.get("business_key"), page.get("agency_key"), page.get("url"), page.get("kind"),
                page.get("md_ref") or "UNKNOWN", page.get("reg_ref") or "UNKNOWN",
                page.get("frequency_hours") or FREQ_HOURS, page.get("http_status"),
                page.get("sha256"), page.get("epistemic_status"),
            ),
        )
    for item in lib.get("resources") or []:
        conn.execute(
            "INSERT INTO resources VALUES (?,?,?,?,?,?,?)",
            (
                item.get("business_key"), item.get("title"), item.get("source_ref"),
                item.get("md_ref") or "UNKNOWN", item.get("reg_ref") or "UNKNOWN",
                item.get("status"), item.get("layer"),
            ),
        )
    for unit in curr.get("units") or []:
        conn.execute(
            "INSERT INTO content_units VALUES (?,?,?,?,?,?,?)",
            (
                unit.get("business_key"), unit.get("tool_slug"), unit.get("level"),
                unit.get("tool_md_ref") or "UNKNOWN", unit.get("reg_ref") or "UNKNOWN",
                (unit.get("body") or {}).get("status"), unit.get("sha256"),
            ),
        )
    for item in laws.get("instruments") or []:
        conn.execute(
            "INSERT INTO legislation VALUES (?,?,?,?,?,?,?,?,?)",
            (
                item.get("business_key"), item.get("tipo"), str(item.get("numero") or ""),
                item.get("ano"), item.get("md_ref") or "UNKNOWN", item.get("reg_ref") or "UNKNOWN",
                item.get("status"), 1 if item.get("revoked") else 0, item.get("sha256"),
            ),
        )
    for alert in alerts.get("alerts") or []:
        conn.execute(
            "INSERT INTO alerts VALUES (?,?,?,?,?,?,?)",
            (
                alert.get("business_key"), alert.get("severity"), alert.get("kind"),
                alert.get("message"), alert.get("source_ref"), alert.get("status"),
                alert.get("created_at"),
            ),
        )
    conn.commit()
    counts = {
        "sources": conn.execute("SELECT COUNT(*) FROM sources").fetchone()[0],
        "resources": conn.execute("SELECT COUNT(*) FROM resources").fetchone()[0],
        "content_units": conn.execute("SELECT COUNT(*) FROM content_units").fetchone()[0],
        "alerts": conn.execute("SELECT COUNT(*) FROM alerts").fetchone()[0],
        "legislation": conn.execute("SELECT COUNT(*) FROM legislation").fetchone()[0],
    }
    missing = conn.execute(
        "SELECT COUNT(*) FROM resources WHERE md_ref IS NULL OR md_ref='' OR reg_ref IS NULL OR reg_ref=''"
    ).fetchone()[0]
    missing_leg = conn.execute(
        "SELECT COUNT(*) FROM legislation WHERE md_ref IS NULL OR md_ref='' OR reg_ref IS NULL OR reg_ref=''"
    ).fetchone()[0]
    conn.close()
    return {
        "agent_id": "AG-OPS-DB-SYNC",
        "class": "MD",
        "role": "MAKER",
        "path": str(INBOX_DB.relative_to(ROOT)),
        "counts": counts,
        "rows_missing_md_or_reg": missing + missing_leg,
        "production_postgres": False,
        "rls_changed": False,
        "promotes_to_md": False,
        "status": "IMPLEMENTED_INBOX_ONLY",
    }


def alert_freshness() -> dict:
    """AG-ALERT-FRESHNESS — periodic extraction expectation + HIGH copyright/source gaps."""
    gov = json.loads((ROOT / "cko_inbox" / "extracted" / "gov_pages.json").read_text(encoding="utf-8")) if (ROOT / "cko_inbox" / "extracted" / "gov_pages.json").exists() else {}
    probe = json.loads((ROOT / "cko_inbox" / "extracted" / "api_probe.json").read_text(encoding="utf-8")) if (ROOT / "cko_inbox" / "extracted" / "api_probe.json").exists() else {}
    congress = json.loads((ROOT / "cko_inbox" / "extracted" / "congress_probe.json").read_text(encoding="utf-8")) if (ROOT / "cko_inbox" / "extracted" / "congress_probe.json").exists() else {}
    curr = json.loads((ROOT / "cko_md" / "content_curriculum.json").read_text(encoding="utf-8")) if (ROOT / "cko_md" / "content_curriculum.json").exists() else {}
    alerts = []
    for page in gov.get("pages") or []:
        if page.get("http_status") != 200:
            alerts.append({
                "business_key": f"ALRT-OFFLINE-{page['business_key']}",
                "severity": "ALTA" if page.get("agency_key") in {"AGY-ANVISA", "AGY-MS", "AGY-COFEN"} else "MEDIA",
                "kind": "SOURCE_OFFLINE",
                "message": f"{page.get('agency')} HTTP {page.get('http_status')} — extração periódica {FREQ_HOURS}h. API/portal pode estar offline.",
                "source_ref": page.get("business_key"),
                "status": "OPEN",
                "created_at": _now(),
            })
    for adapter in (probe.get("adapters") or []) + (congress.get("adapters") or []):
        if not adapter.get("online"):
            alerts.append({
                "business_key": f"ALRT-API-{adapter['business_key']}",
                "severity": "ALTA",
                "kind": "API_OFFLINE",
                "message": f"{adapter.get('agency')} não observou HTTP 200. base_url null. Reprobe a cada {FREQ_HOURS}h.",
                "source_ref": adapter.get("business_key"),
                "status": "OPEN",
                "created_at": _now(),
            })
    for pending in curr.get("pending_high") or []:
        alerts.append({
            "business_key": f"ALRT-{pending['business_key']}",
            "severity": "ALTA",
            "kind": "COPYRIGHT_OR_EVIDENCE",
            "message": pending.get("reason"),
            "source_ref": pending.get("business_key"),
            "status": "OPEN",
            "created_at": _now(),
        })
    payload = {
        "business_key": "ASU-FRESHNESS-001",
        "uuid": None,
        "frequency_hours": FREQ_HOURS,
        "status": "HOLD" if alerts else "OBSERVED",
        "alerts": alerts,
        "population": len(alerts),
        "alta_count": sum(1 for item in alerts if item.get("severity") == "ALTA"),
        "wired_to_admin": True,
        "email_dispatch": False,
        "note": "Alerta é registro JSON + Admin. Sem e-mail (NO_SENSITIVE_CAPTURE).",
    }
    _dump(ROOT / "cko_assurance" / "freshness_alerts.json", payload)
    return {
        "agent_id": "AG-ALERT-FRESHNESS",
        "class": "MONITORING",
        "role": "CHECKER",
        "population": len(alerts),
        "alta_count": payload["alta_count"],
        "email_dispatch": False,
        "promotes_to_md": False,
        "wired_to_frontend": True,
        "status": payload["status"],
    }
