"""Federal legislation via Congresso Nacional APIs.

CKO path (not NIFS IDs, not Drive HTML, not invented UUIDs):

- Senado/Congresso `legis.senado.leg.br/dadosabertos/legislacao` is the enacted-norm source.
- Câmara `dadosabertos.camara.leg.br/api/v2` supplies proposition-type catalogs.
- Types without force of law are blocked (PL, PLP / projeto de lei complementar, REQ, parecer, …).
- Enacted Lei Complementar (LCP) has force of law (CF/88 art. 59, II) and is allowed.
- Revoked enacted norms are allowed as tool references, never as current applicability.

Drive/NIFS used only as discovery seeds. Supabase unread → EVIDENCE_PENDING.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from .paths import ROOT

FREQ_HOURS = 24
INBOX = ROOT / "cko_inbox" / "extracted"
CONGRESS_DIR = ROOT / "cko_inbox" / "congress"

CAMARA_TIPOS_URL = "https://dadosabertos.camara.leg.br/api/v2/referencias/proposicoes/siglaTipo"
CAMARA_PLP_SAMPLE_URL = "https://dadosabertos.camara.leg.br/api/v2/proposicoes?siglaTipo=PLP&itens=1&ordem=DESC&ordenarPor=id"
SENADO_OPENAPI_URL = "https://legis.senado.leg.br/dadosabertos/v3/api-docs"
SENADO_TIPOS_NORMA_URL = "https://legis.senado.leg.br/dadosabertos/legislacao/tiposNorma"
SENADO_LISTA_URL = "https://legis.senado.leg.br/dadosabertos/legislacao/lista"
SENADO_DETALHE_URL = "https://legis.senado.leg.br/dadosabertos/legislacao"
SENADO_PROCESSO_URL = "https://legis.senado.leg.br/dadosabertos/processo"

PROBE_CANDIDATES = (
    {
        "business_key": "API-CONGRESSO-SENADO-OPENAPI",
        "agency_key": "AGY-CONGRESSO",
        "agency": "Congresso Nacional / Senado Dados Abertos",
        "url": SENADO_OPENAPI_URL,
        "kind": "CONGRESSO_OPENAPI",
        "md_ref": "MD-API-CONGRESSO-SENADO",
        "reg_ref": "REG-API-CONGRESSO-SENADO",
        "base_host": "https://legis.senado.leg.br/dadosabertos/",
    },
    {
        "business_key": "API-CONGRESSO-SENADO-TIPOS-NORMA",
        "agency_key": "AGY-CONGRESSO",
        "agency": "Congresso Nacional / legislação federal",
        "url": SENADO_TIPOS_NORMA_URL,
        "kind": "LEGISLACAO_TIPOS_NORMA",
        "md_ref": "MD-API-CONGRESSO-LEGISLACAO",
        "reg_ref": "REG-API-CONGRESSO-LEGISLACAO",
        "base_host": "https://legis.senado.leg.br/dadosabertos/",
    },
    {
        "business_key": "API-CONGRESSO-CAMARA-TIPOS",
        "agency_key": "AGY-CONGRESSO",
        "agency": "Câmara dos Deputados Dados Abertos",
        "url": CAMARA_TIPOS_URL,
        "kind": "CAMARA_SIGLA_TIPO",
        "md_ref": "MD-API-CONGRESSO-CAMARA",
        "reg_ref": "REG-API-CONGRESSO-CAMARA",
        "base_host": "https://dadosabertos.camara.leg.br/api/v2/",
    },
)

# Enacted species with force of law (CF/88 art. 59 and Constituição itself).
ALLOW_SIGLAS = frozenset({
    "CON", "CON-v", "CON-nv", "ADCT",
    "EMC", "EMC-n", "EMC-sn", "EMR",
    "LEI", "LEI-n", "LEI-sn",
    "LCP",  # Lei Complementar ENACTED — has force of law. Not PLP.
    "LDL", "LCT",
    "MPV", "MPV-cs", "MPV-ss",
    "DLG", "DLN",
    "DPL", "DPL-n", "DPL-sn",
    "RCN",
    "DEL", "DEL-mpv",
    "AILEI", "AIEMC",
    "CDL", "CDL-n", "CDL-sn",
})

# Explicit denylist. User example "lei complementar" maps to PLP / projeto, not enacted LCP.
BLOCK_SIGLAS = frozenset({
    "PEC", "PECCD", "PLP", "PL", "PDC", "PRC", "PRN", "PLN",
    "REQ", "RIC", "INC", "MSC", "MSG", "MSV", "MSVP", "MSVT",
    "OFI", "OF", "OFN", "OFS", "PARN", "PRL", "PAR", "PET",
    "ACP",  # Ato Complementar — not Lei Complementar
    "INM", "EDT", "ALV", "MAN", "AVS", "RCA", "REP", "SUG",
})

BLOCK_NAME_FRAGMENTS = (
    "projeto de lei complementar",
    "projeto de lei ordinária",
    "projeto de lei de conversão",
    "projeto de lei",
    "projeto de decreto legislativo",
    "projeto de resolução",
    "proposta de emenda",
    "proposta de fiscalização",
    "requerimento",
    "parecer",
    "mensagem",
    "ofício",
    "indicação",
    "petição",
    "sugestão",
    "emenda na comissão",
    "emenda de plenário",
    "consulta",
    "discurso",
    "denúncia",
    "minuta de proposição",
)

# Discovery seeds (Drive lei8080-sus / NIFS instruments / CKO rights). CKO keys, not LEG.BR.*.
FEDERAL_SEEDS = (
    {
        "business_key": "INS-CF-1988",
        "tipo": "CON-v",
        "numero": None,
        "ano": 1988,
        "discovery": "Drive lei8080-sus + NIFS CF + CF/88 art. 196 saúde",
        "tool_slugs": ["simulado-tecnico"],
        "md_ref": "MD-INS-CF-1988",
        "reg_ref": "REG-INS-CF-1988",
    },
    {
        "business_key": "INS-LEI-8080-1990",
        "tipo": "LEI",
        "numero": 8080,
        "ano": 1990,
        "discovery": "Drive lei8080-sus.html (ads — not copied) + NIFS LOSUS",
        "tool_slugs": ["simulado-tecnico"],
        "md_ref": "MD-INS-LEI-8080-1990",
        "reg_ref": "REG-INS-LEI-8080-1990",
    },
    {
        "business_key": "INS-LEI-8142-1990",
        "tipo": "LEI",
        "numero": 8142,
        "ano": 1990,
        "discovery": "NIFS Lei 8.142 participação / transferências SUS",
        "tool_slugs": ["simulado-tecnico"],
        "md_ref": "MD-INS-LEI-8142-1990",
        "reg_ref": "REG-INS-LEI-8142-1990",
    },
    {
        "business_key": "INS-LEI-7498-1986",
        "tipo": "LEI",
        "numero": 7498,
        "ano": 1986,
        "discovery": "NIFS exercício da enfermagem; CKO-Regulatory-Delta ADR CURRENT-LEI7498",
        "tool_slugs": ["simulado-tecnico"],
        "md_ref": "MD-INS-LEI-7498-1986",
        "reg_ref": "REG-INS-LEI-7498-1986",
    },
    {
        "business_key": "INS-LEI-9610-1998",
        "tipo": "LEI",
        "numero": 9610,
        "ano": 1998,
        "discovery": "CKO rights profile already bound; Congress API re-identifies the same law",
        "tool_slugs": [],
        "md_ref": "MD-INS-LEI-9610-1998",
        "reg_ref": "REG-INS-LEI-9610-1998",
    },
    {
        "business_key": "INS-LEI-2312-1954",
        "tipo": "LEI",
        "numero": 2312,
        "ano": 1954,
        "discovery": "Congress API ediv of Lei 8080 — norma revogada, permitida como ferramenta",
        "tool_slugs": ["simulado-tecnico"],
        "md_ref": "MD-INS-LEI-2312-1954",
        "reg_ref": "REG-INS-LEI-2312-1954",
        "expect_revoked": True,
    },
)

GATE_NOTE = (
    "Instrumento sem força de lei é bloqueado. Exemplo do pedido: 'lei complementar' "
    "→ PLP / Projeto de Lei Complementar (não é lei). Lei Complementar promulgada (LCP) "
    "tem força de lei (CF/88 art. 59, II) e entra. Norma revogada entra só como "
    "ferramenta (REVOKED), nunca como aplicabilidade vigente."
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _dump(path: Path, payload: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def _load(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _as_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def classify_tipo(*, sigla: str | None, nome: str | None = None, source: str = "senado_tipos_norma") -> dict:
    """REG gate: force of law vs blocked. Deterministic. No HTTP."""
    raw_sigla = (sigla or "").strip()
    raw_nome = (nome or "").strip()
    sigla_key = raw_sigla
    nome_l = raw_nome.lower()
    decision = "HOLD"
    reason = "Tipo sem sigla classificável."
    if source.startswith("camara"):
        # Câmara catalogs proposições. CON ali é Consulta, não Constituição.
        if sigla_key == "PLP" or "lei complementar" in nome_l and "projeto" in nome_l:
            return {
                "sigla": sigla_key or None,
                "nome": raw_nome or None,
                "source": source,
                "decision": "BLOCK",
                "force_of_law": False,
                "reason": "PLP / Projeto de Lei Complementar não tem força de lei até transformação em LCP.",
                "uuid": None,
            }
        return {
            "sigla": sigla_key or None,
            "nome": raw_nome or None,
            "source": source,
            "decision": "BLOCK",
            "force_of_law": False,
            "reason": (
                "Proposicao da Câmara não entra como legislação federal. "
                "Norma com força de lei entra só via API legislacao/ do Congresso."
            ),
            "uuid": None,
        }
    if sigla_key in ALLOW_SIGLAS:
        decision = "ALLOW"
        reason = "Espécie com força de lei (CF/88 art. 59 / Constituição)."
        if sigla_key == "LCP":
            reason = (
                "Lei Complementar promulgada tem força de lei (CF/88 art. 59, II). "
                "Não confundir com PLP / projeto de lei complementar."
            )
        if sigla_key in {"CON-nv"}:
            reason = "Constituição anterior: força histórica. Ferramenta OK se REVOKED/SUPERSEDED. Não é vigente."
    elif sigla_key in BLOCK_SIGLAS:
        decision = "BLOCK"
        reason = "Tipo de instrumento legislativo sem força de lei."
        if sigla_key == "PLP":
            reason = "PLP = Projeto de Lei Complementar. Sem força de lei até transformação em LCP."
        if sigla_key == "ACP":
            reason = "Ato Complementar não é Lei Complementar e não tem força de lei ordinária/complementar."
    else:
        for frag in BLOCK_NAME_FRAGMENTS:
            if frag in nome_l:
                decision = "BLOCK"
                reason = f"Nome do tipo indica instrumento sem força de lei ({frag})."
                if "lei complementar" in frag:
                    reason = (
                        "Projeto de lei complementar / tipo sem força de lei. "
                        "LCP promulgada permanece ALLOW."
                    )
                break
        else:
            if not sigla_key:
                decision = "BLOCK"
                reason = "Tipo sem sigla na API — tratado como não-lei."
            else:
                decision = "BLOCK"
                reason = "Tipo fora da allowlist de força de lei. Default = BLOCK."
    return {
        "sigla": sigla_key or None,
        "nome": raw_nome or None,
        "source": source,
        "decision": decision,
        "force_of_law": decision == "ALLOW",
        "reason": reason,
        "uuid": None,
    }


def _revocation_from_detalhe(detalhe: dict) -> dict:
    docs = _as_list(((detalhe.get("DetalheDocumento") or {}).get("documentos") or {}).get("documento"))
    if not docs:
        return {"status": "UNKNOWN", "revoked": False, "evidence": None}
    doc = docs[0]
    tipo = ((doc.get("identificacao") or {}).get("tipo")) or ""
    if tipo == "CON-nv":
        return {
            "status": "SUPERSEDED",
            "revoked": True,
            "evidence": "tipo CON-nv = Constituição Federal Anterior",
            "tool_use_allowed": True,
        }
    vides = _as_list(((doc.get("vides") or {}).get("vide")))
    for vide in vides:
        comentario = (vide.get("comentario") or "").lower()
        posterior = vide.get("nomeNormaPosterior") or vide.get("codnormaposterior")
        if "revoga" in comentario and posterior:
            return {
                "status": "REVOKED",
                "revoked": True,
                "evidence": vide.get("comentario"),
                "revoked_by": vide.get("nomeNormaPosterior"),
                "tool_use_allowed": True,
            }
    return {"status": "CURRENT_OR_UNVERIFIED", "revoked": False, "evidence": None, "tool_use_allowed": True}


def _metadata_from_lista_item(item: dict) -> dict:
    return {
        "api_id": item.get("id"),
        "tipo": item.get("tipo"),
        "descricao": item.get("descricao"),
        "numero": item.get("numero"),
        "norma": item.get("norma"),
        "norma_nome": item.get("normaNome"),
        "ementa": item.get("ementa"),
        "data_assinatura": item.get("dataassinatura"),
        "ano_assinatura": item.get("anoassinatura"),
        "apelido": item.get("apelido"),
        "url_documento": item.get("urlDocumento"),
    }


def _metadata_from_detalhe(detalhe: dict) -> dict:
    docs = _as_list(((detalhe.get("DetalheDocumento") or {}).get("documentos") or {}).get("documento"))
    if not docs:
        return {}
    doc = docs[0]
    ident = doc.get("identificacao") or {}
    pubs = _as_list((doc.get("publicacoes") or {}).get("publicacao"))
    pub = pubs[0] if pubs else {}
    return {
        "api_id": doc.get("id"),
        "tipo": ident.get("tipo"),
        "descricao": ident.get("descricao"),
        "numero": ident.get("numero"),
        "norma": ident.get("norma"),
        "norma_nome": ident.get("normaNome"),
        "ementa": doc.get("ementa"),
        "data_assinatura": ident.get("dataassinatura"),
        "apelido": ident.get("apelido"),
        "url_documento": ident.get("urlDocumento"),
        "observacao": doc.get("observacao"),
        "classe": ((doc.get("classes") or {}).get("classe")),
        "publicacao_fonte": pub.get("fonte"),
        "publicacao_data": pub.get("data"),
        "clause_text": "NOT_COPIED_AS_PRODUCT_RULE",
        "dispositivos_copied": False,
    }


def _json_body(rec: dict) -> dict | list | None:
    body = rec.get("body") or b""
    if not body:
        return None
    try:
        return json.loads(body.decode("utf-8", errors="replace"))
    except json.JSONDecodeError:
        return None


def _congress_get(url: str, timeout: int = 30):
    from .agents import UA_BROWSER, _http_get
    return _http_get(
        url,
        timeout=timeout,
        user_agent=UA_BROWSER,
        accept="application/json, application/problem+json, */*;q=0.1",
    )


def probe_congress_apis(*, network: bool) -> dict:
    """AG-PROBE-CONGRESS-API — observe Câmara + Senado. base_url only on HTTP 200."""
    dest = INBOX / "congress_probe.json"
    adapters = []
    if network:
        for cand in PROBE_CANDIDATES:
            rec = _congress_get(cand["url"], timeout=30)
            body = rec.pop("body", b"") or b""
            ok = rec.get("http_status") == 200
            adapters.append({
                **{k: v for k, v in cand.items() if k != "base_host"},
                "uuid": None,
                "http_status": rec.get("http_status"),
                "bytes": rec.get("bytes") or len(body),
                "sha256": rec.get("sha256"),
                "error": rec.get("error"),
                "epistemic_status": "OBSERVED" if ok else "EVIDENCE_PENDING",
                "base_url": cand["base_host"] if ok else None,
                "online": bool(ok),
                "final_url": rec.get("final_url"),
                "note": "API do Congresso. base_url só se HTTP 200. Extração periódica 24h.",
                "probed_at": _now(),
            })
        _dump(dest, {
            "business_key": "IPE-CONGRESS-PROBE-001",
            "uuid": None,
            "status": "SOURCE_DERIVED",
            "probed_at": _now(),
            "frequency_hours": FREQ_HOURS,
            "adapters": adapters,
            "supabase_legislation": "EVIDENCE_PENDING",
            "supabase_note": "MCP execute_sql/list_tables: autenticação falhou. Não inventar schema.",
        })
    elif dest.exists():
        adapters = (_load(dest).get("adapters")) or []
    else:
        adapters = [{
            **{k: v for k, v in cand.items() if k != "base_host"},
            "uuid": None,
            "http_status": None,
            "bytes": None,
            "sha256": None,
            "error": "offline_no_inbox",
            "epistemic_status": "EVIDENCE_PENDING",
            "base_url": None,
            "online": False,
            "note": "Probe Congresso não executado.",
            "probed_at": None,
        } for cand in PROBE_CANDIDATES]
        _dump(dest, {
            "business_key": "IPE-CONGRESS-PROBE-001",
            "uuid": None,
            "status": "EVIDENCE_PENDING",
            "probed_at": None,
            "frequency_hours": FREQ_HOURS,
            "adapters": adapters,
        })

    # Merge congress adapters into the live API adapter registry without dropping CKAN.
    api_md_path = ROOT / "cko_md" / "api_adapter_registry.json"
    existing = _load(api_md_path)
    prior = [item for item in (existing.get("adapters") or []) if not str(item.get("business_key") or "").startswith("API-CONGRESSO-")]
    merged = prior + adapters
    _dump(api_md_path, {
        "business_key": existing.get("business_key") or "MD-API-ADAPTER-REG-001",
        "uuid": None,
        "status": "REGISTERED",
        "implemented": False,
        "production_api": False,
        "frequency_hours": FREQ_HOURS,
        "adapters": merged,
        "population": len(merged),
        "rule": "Resposta de API não vira verdade canônica sem snapshot, hash, MD, REG e validação.",
    })
    return {
        "agent_id": "AG-PROBE-CONGRESS-API",
        "class": "ACQUISITION",
        "role": "MAKER",
        "network": network,
        "adapters": adapters,
        "online_count": sum(1 for item in adapters if item.get("online")),
        "promotes_to_md": False,
        "status": "OBSERVED" if any(item.get("online") for item in adapters) else "EVIDENCE_PENDING",
    }


def _classify_senado_tipos(payload: dict) -> list[dict]:
    tipos = _as_list(
        (((payload.get("ListaTiposDocumento") or {}).get("TiposDocumento") or {}).get("TipoDocumento"))
    )
    classified = []
    for item in tipos:
        classified.append(classify_tipo(
            sigla=item.get("Sigla"),
            nome=item.get("Descricao"),
            source="senado_tipos_norma",
        ) | {
            "api_codigo": item.get("Codigo"),
            "instanciavel": item.get("Instanciavel"),
        })
    return classified


def _classify_camara_tipos(payload: dict) -> list[dict]:
    classified = []
    for item in payload.get("dados") or []:
        rec = classify_tipo(
            sigla=item.get("sigla"),
            nome=item.get("nome"),
            source="camara_siglaTipo",
        )
        rec["api_codigo"] = item.get("cod")
        classified.append(rec)
    return classified


def fetch_federal_legislation(*, network: bool) -> dict:
    """AG-FETCH-FEDERAL-LEGISLATION — enacted federal norms only. Gate before catalog."""
    from .vault import put_bytes

    CONGRESS_DIR.mkdir(parents=True, exist_ok=True)
    types_dest = INBOX / "congress_types.json"
    laws_dest = INBOX / "federal_legislation.json"
    blocked_sample_dest = INBOX / "congress_blocked_sample.json"

    senado_tipos: list[dict] = []
    camara_tipos: list[dict] = []
    instruments: list[dict] = []
    blocked_hits: list[dict] = []
    type_error = None

    if network:
        tipos_rec = _congress_get(SENADO_TIPOS_NORMA_URL, timeout=30)
        tipos_body = tipos_rec.get("body") or b""
        tipos_json = _json_body(tipos_rec)
        if tipos_rec.get("http_status") == 200 and tipos_json is not None:
            put_bytes(
                tipos_body,
                logical_id="SRC-CONGRESS-TIPOS-NORMA",
                source_url=SENADO_TIPOS_NORMA_URL,
                source_path="cko_inbox/congress/tipos_norma.json",
                media_type="application/json",
                mask_id="MASK-GOV-JSON",
                note="Congresso tiposNorma unaltered",
            )
            (CONGRESS_DIR / "tipos_norma.json").write_bytes(tipos_body)
            senado_tipos = _classify_senado_tipos(tipos_json)
        else:
            type_error = tipos_rec.get("error") or f"HTTP {tipos_rec.get('http_status')}"

        cam_rec = _congress_get(CAMARA_TIPOS_URL, timeout=30)
        cam_json = _json_body(cam_rec)
        if cam_rec.get("http_status") == 200 and isinstance(cam_json, dict):
            (CONGRESS_DIR / "camara_sigla_tipo.json").write_bytes(cam_rec.get("body") or b"")
            camara_tipos = _classify_camara_tipos(cam_json)

        plp_rec = _congress_get(CAMARA_PLP_SAMPLE_URL, timeout=25)
        plp_json = _json_body(plp_rec)
        plp_item = ((plp_json or {}).get("dados") or [None])[0] if isinstance(plp_json, dict) else None
        if plp_item:
            gate = classify_tipo(sigla=plp_item.get("siglaTipo"), nome="Projeto de Lei Complementar", source="camara_proposicao")
            blocked_hits.append({
                "business_key": "BLK-CAMARA-PLP-SAMPLE",
                "siglaTipo": plp_item.get("siglaTipo"),
                "numero": plp_item.get("numero"),
                "ano": plp_item.get("ano"),
                "ementa": (plp_item.get("ementa") or "")[:240],
                "uri": plp_item.get("uri"),
                "gate": gate,
                "cataloged_as_legislation": False,
                "note": "Amostra PLP bloqueada. Não vira instrumento MD.",
            })
        _dump(blocked_sample_dest, {
            "business_key": "IPE-CONGRESS-BLOCKED-001",
            "uuid": None,
            "status": "SOURCE_DERIVED",
            "hits": blocked_hits,
        })

        for seed in FEDERAL_SEEDS:
            seed_gate = classify_tipo(sigla=seed["tipo"], nome=None, source="seed")
            record = {
                **seed,
                "uuid": None,
                "gate": seed_gate,
                "http_status": None,
                "epistemic_status": "EVIDENCE_PENDING",
                "metadata": {},
                "revocation": {},
                "processo": None,
                "sha256": None,
                "inbox_path": None,
                "error": None,
            }
            if seed_gate["decision"] != "ALLOW":
                record["error"] = "SEED_TYPE_BLOCKED"
                record["status"] = "BLOCKED"
                instruments.append(record)
                continue
            if seed["numero"] is None:
                lista_url = f"{SENADO_LISTA_URL}?tipo={seed['tipo']}"
            else:
                lista_url = f"{SENADO_LISTA_URL}?tipo={seed['tipo']}&numero={seed['numero']}&ano={seed['ano']}"
            lista_rec = _congress_get(lista_url, timeout=30)
            lista_json = _json_body(lista_rec)
            record["http_status"] = lista_rec.get("http_status")
            docs = _as_list(
                (((lista_json or {}).get("ListaDocumento") or {}).get("documentos") or {}).get("documento")
            ) if isinstance(lista_json, dict) else []
            if lista_rec.get("http_status") != 200 or not docs:
                record["error"] = lista_rec.get("error") or "NOT_FOUND"
                record["status"] = "EVIDENCE_PENDING"
                instruments.append(record)
                continue
            item = docs[0]
            observed_tipo = item.get("tipo") or seed["tipo"]
            item_gate = classify_tipo(sigla=observed_tipo, nome=item.get("descricao"), source="senado_lista")
            record["gate"] = item_gate
            if item_gate["decision"] != "ALLOW":
                record["status"] = "BLOCKED"
                record["error"] = "OBSERVED_TYPE_BLOCKED"
                record["metadata"] = _metadata_from_lista_item(item)
                instruments.append(record)
                continue
            api_id = item.get("id")
            skip_detalhe = str(observed_tipo or "").startswith("CON")
            det_json = None
            det_body = b""
            det_rec = {"http_status": None, "sha256": None, "error": None}
            detalhe_url = f"{SENADO_DETALHE_URL}/{api_id}" if api_id else None
            if skip_detalhe:
                # Constituição detalhe includes full article tree and can IncompleteRead.
                meta = _metadata_from_lista_item(item)
                meta["lista_url"] = lista_url
                meta["detalhe_url"] = None
                meta["detalhe_skipped"] = "CONSTITUTION_TREE_TOO_LARGE"
                revocation = {"status": "CURRENT_OR_UNVERIFIED", "revoked": False, "tool_use_allowed": True} if observed_tipo == "CON-v" else {
                    "status": "SUPERSEDED", "revoked": True, "evidence": "tipo CON-nv", "tool_use_allowed": True,
                }
                lista_bytes = lista_rec.get("body") or b""
                if lista_bytes:
                    rel = CONGRESS_DIR / f"{seed['business_key']}.json"
                    rel.write_bytes(lista_bytes)
                    put_bytes(
                        lista_bytes,
                        logical_id=f"SRC-{seed['business_key']}",
                        source_url=lista_url,
                        source_path=str(rel.relative_to(ROOT)),
                        media_type="application/json",
                        mask_id="MASK-GOV-JSON",
                        note="Congress lista JSON. Constituição detalhe não baixado.",
                    )
                    record["inbox_path"] = str(rel.relative_to(ROOT))
                    record["sha256"] = lista_rec.get("sha256")
            else:
                det_rec = _congress_get(detalhe_url, timeout=35)
                det_body = det_rec.get("body") or b""
                det_json = _json_body(det_rec)
                meta = _metadata_from_detalhe(det_json) if isinstance(det_json, dict) else _metadata_from_lista_item(item)
                meta["lista_url"] = lista_url
                meta["detalhe_url"] = detalhe_url
                revocation = _revocation_from_detalhe(det_json) if isinstance(det_json, dict) else {}
                if det_body and det_rec.get("http_status") == 200:
                    rel = CONGRESS_DIR / f"{seed['business_key']}.json"
                    rel.write_bytes(det_body)
                    put_bytes(
                        det_body,
                        logical_id=f"SRC-{seed['business_key']}",
                        source_url=detalhe_url,
                        source_path=str(rel.relative_to(ROOT)),
                        media_type="application/json",
                        mask_id="MASK-GOV-JSON",
                        note="Congress legislation JSON unaltered. Clause text not promoted.",
                    )
                    record["inbox_path"] = str(rel.relative_to(ROOT))
                    record["sha256"] = det_rec.get("sha256")
            if not skip_detalhe and det_rec.get("http_status") != 200 and not meta.get("norma_nome") and not meta.get("normaNome"):
                record["error"] = det_rec.get("error") or "DETALHE_FAILED"
                record["metadata"] = meta
                record["status"] = "EVIDENCE_PENDING"
                instruments.append(record)
                continue
            proc = None
            if seed.get("numero") and seed.get("ano"):
                proc_url = f"{SENADO_PROCESSO_URL}?numeroNorma={seed['numero']}&anoNorma={seed['ano']}"
                proc_rec = _congress_get(proc_url, timeout=25)
                proc_json = _json_body(proc_rec)
                if isinstance(proc_json, list) and proc_json:
                    head = proc_json[0]
                    proc = {
                        "identificacao": head.get("identificacao"),
                        "tipoDocumento": head.get("tipoDocumento"),
                        "situacaoAtual": head.get("situacaoAtual"),
                        "normaGerada": head.get("normaGerada"),
                        "tramitando": head.get("tramitando"),
                        "note": "Processo originário (projeto) não é a norma. Só a norma gerada entra no catálogo.",
                    }
                    origin_gate = classify_tipo(
                        sigla=None,
                        nome=head.get("tipoDocumento"),
                        source="senado_processo_origin",
                    )
                    proc["origin_type_gate"] = origin_gate
            record.update({
                "metadata": meta,
                "revocation": revocation,
                "processo": proc,
                "epistemic_status": "OBSERVED",
                "status": "REVOKED" if revocation.get("revoked") else "REGISTERED",
                "applicability": "NOT_CURRENT" if revocation.get("revoked") else "APPLICABILITY_UNVERIFIED",
                "tool_use_if_revoked": True,
                "publication": "HOLD",
                "assured": False,
            })
            instruments.append(record)
        _dump(types_dest, {
            "business_key": "IPE-CONGRESS-TYPES-001",
            "uuid": None,
            "status": "SOURCE_DERIVED" if senado_tipos or camara_tipos else "EVIDENCE_PENDING",
            "gate_note": GATE_NOTE,
            "senado_tipos": senado_tipos,
            "camara_tipos": camara_tipos,
            "senado_allow": sum(1 for item in senado_tipos if item.get("decision") == "ALLOW"),
            "senado_block": sum(1 for item in senado_tipos if item.get("decision") == "BLOCK"),
            "camara_allow": sum(1 for item in camara_tipos if item.get("decision") == "ALLOW"),
            "camara_block": sum(1 for item in camara_tipos if item.get("decision") == "BLOCK"),
            "error": type_error,
            "classified_at": _now(),
        })
        _dump(laws_dest, {
            "business_key": "IPE-FED-LEG-001",
            "uuid": None,
            "status": "SOURCE_DERIVED",
            "captured_at": _now(),
            "frequency_hours": FREQ_HOURS,
            "discovery": {
                "drive": [
                    "lei8080-sus.html / lei8080-sus.webp — página de origem com ads. Não copiada.",
                    "CKO-Regulatory-Canonical-Delta ADR CURRENT-LEI7498 — referência, não golden MD.",
                ],
                "nifs": "NIFS/reference-datasets/regulatory/br/legislation_instruments.json — descoberta only.",
                "supabase": "EVIDENCE_PENDING — password authentication failed.",
            },
            "instruments": instruments,
            "blocked_hits": blocked_hits,
            "population": len(instruments),
            "rule": GATE_NOTE,
        })
    else:
        types_payload = _load(types_dest)
        laws_payload = _load(laws_dest)
        senado_tipos = types_payload.get("senado_tipos") or []
        camara_tipos = types_payload.get("camara_tipos") or []
        instruments = laws_payload.get("instruments") or []
        blocked_hits = (_load(blocked_sample_dest).get("hits")) or laws_payload.get("blocked_hits") or []
        if not types_payload:
            _dump(types_dest, {
                "business_key": "IPE-CONGRESS-TYPES-001",
                "uuid": None,
                "status": "EVIDENCE_PENDING",
                "gate_note": GATE_NOTE,
                "senado_tipos": [],
                "camara_tipos": [],
                "error": "offline_no_inbox",
            })
        if not laws_payload:
            instruments = [{
                **seed,
                "uuid": None,
                "gate": classify_tipo(sigla=seed["tipo"], source="seed"),
                "epistemic_status": "EVIDENCE_PENDING",
                "status": "EVIDENCE_PENDING",
                "error": "offline_no_inbox",
                "metadata": {},
                "revocation": {},
            } for seed in FEDERAL_SEEDS]
            _dump(laws_dest, {
                "business_key": "IPE-FED-LEG-001",
                "uuid": None,
                "status": "EVIDENCE_PENDING",
                "instruments": instruments,
                "population": len(instruments),
            })

    allowed = [item for item in instruments if item.get("gate", {}).get("decision") == "ALLOW" and item.get("epistemic_status") == "OBSERVED"]
    blocked = [item for item in instruments if item.get("status") == "BLOCKED"] + blocked_hits
    revoked_ok = [
        item for item in allowed
        if (item.get("revocation") or {}).get("revoked") and item.get("tool_use_if_revoked")
    ]

    md = {
        "business_key": "MD-LEG-INS-001",
        "uuid": None,
        "status": "REGISTERED",
        "identity_scheme": "CKO-BK-1",
        "jurisdiction": "JUR-BR",
        "source": "CONGRESSO_NACIONAL_API",
        "population": len(allowed),
        "instruments": [
            {
                "business_key": item["business_key"],
                "uuid": None,
                "md_ref": item.get("md_ref"),
                "reg_ref": item.get("reg_ref"),
                "tipo": (item.get("metadata") or {}).get("tipo") or item.get("tipo"),
                "numero": (item.get("metadata") or {}).get("numero") or item.get("numero"),
                "ano": item.get("ano"),
                "title": (item.get("metadata") or {}).get("norma_nome"),
                "ementa": (item.get("metadata") or {}).get("ementa"),
                "url": (item.get("metadata") or {}).get("url_documento"),
                "sha256": item.get("sha256"),
                "status": item.get("status"),
                "revoked": bool((item.get("revocation") or {}).get("revoked")),
                "tool_slugs": item.get("tool_slugs") or [],
                "clause_text": "NOT_COPIED_AS_PRODUCT_RULE",
                "publication": "HOLD",
                "assured": False,
            }
            for item in allowed
        ],
        "rule": "Identidade MD do instrumento precede REG e biblioteca. Texto de artigo não é regra de produto.",
    }
    _dump(ROOT / "cko_md" / "legislation_instrument_registry.json", md)

    links = []
    for item in allowed:
        for slug in item.get("tool_slugs") or []:
            links.append({
                "business_key": f"LNK-{item['business_key']}-{slug}",
                "uuid": None,
                "instrument_ref": item["business_key"],
                "md_ref": item.get("md_ref"),
                "reg_ref": item.get("reg_ref"),
                "tool_slug": slug,
                "link_type": "HISTORICAL_TOOL_REFERENCE" if (item.get("revocation") or {}).get("revoked") else "TOOL_REFERENCE",
                "current_applicability": not bool((item.get("revocation") or {}).get("revoked")),
                "publication": "HOLD",
            })
    _dump(ROOT / "cko_md" / "legislation_tool_links.json", {
        "business_key": "MD-LEG-TLK-001",
        "uuid": None,
        "status": "REGISTERED",
        "population": len(links),
        "links": links,
        "rule": "Vínculo ferramenta↔norma. Norma revogada pode vincular. Não cria fórmula.",
    })

    quals = []
    for item in instruments:
        gate = item.get("gate") or {}
        revoked = bool((item.get("revocation") or {}).get("revoked"))
        quals.append({
            "business_key": item.get("reg_ref") or f"REG-{item.get('business_key')}",
            "source_ref": item.get("business_key"),
            "md_ref": item.get("md_ref"),
            "reg_ref": item.get("reg_ref"),
            "agency_key": "AGY-CONGRESSO",
            "issuer": "Congresso Nacional",
            "jurisdiction": "JUR-BR",
            "instrument_class": "FEDERAL_LEGISLATION",
            "tipo": (item.get("metadata") or {}).get("tipo") or item.get("tipo"),
            "force_of_law": gate.get("force_of_law"),
            "gate_decision": gate.get("decision"),
            "gate_reason": gate.get("reason"),
            "rights": "GOVERNMENT_METADATA_ONLY",
            "clause_text": "NOT_COPIED_AS_PRODUCT_RULE",
            "applicability": "NOT_CURRENT" if revoked else "APPLICABILITY_UNVERIFIED",
            "revoked": revoked,
            "tool_use_if_revoked": True,
            "republication": "FORBIDDEN_FULL_TEXT",
            "status": item.get("status") or "DOCUMENTADO",
            "uuid": None,
        })
    for hit in blocked_hits:
        gate = hit.get("gate") or {}
        quals.append({
            "business_key": "REG-BLK-CAMARA-PLP-SAMPLE",
            "source_ref": hit.get("business_key"),
            "md_ref": "MD-BLK-CAMARA-PLP-SAMPLE",
            "reg_ref": "REG-BLK-CAMARA-PLP-SAMPLE",
            "agency_key": "AGY-CONGRESSO",
            "issuer": "Câmara dos Deputados",
            "jurisdiction": "JUR-BR",
            "instrument_class": "LEGISLATIVE_PROPOSITION_NO_FORCE",
            "tipo": hit.get("siglaTipo"),
            "force_of_law": False,
            "gate_decision": "BLOCK",
            "gate_reason": gate.get("reason"),
            "clause_text": "NOT_COPIED_AS_PRODUCT_RULE",
            "status": "BLOCKED",
            "uuid": None,
        })
    _dump(ROOT / "cko_reg" / "legislation_qualification.json", {
        "business_key": "REG-LEG-GATE-001",
        "uuid": None,
        "status": "DOCUMENTADO",
        "gate_note": GATE_NOTE,
        "allow_siglas": sorted(ALLOW_SIGLAS),
        "block_siglas": sorted(BLOCK_SIGLAS),
        "qualifications": quals,
        "population": len(quals),
        "rule": "REG qualifica força de lei. REG não cria identidade. PLP bloqueado. LCP promulgada permitida.",
    })

    return {
        "agent_id": "AG-FETCH-FEDERAL-LEGISLATION",
        "class": "ACQUISITION",
        "role": "MAKER",
        "network": network,
        "allowed": len(allowed),
        "blocked": len(blocked),
        "revoked_tool_ok": len(revoked_ok),
        "senado_allow_types": sum(1 for item in senado_tipos if item.get("decision") == "ALLOW"),
        "senado_block_types": sum(1 for item in senado_tipos if item.get("decision") == "BLOCK"),
        "camara_block_types": sum(1 for item in camara_tipos if item.get("decision") == "BLOCK"),
        "promotes_to_md": False,
        "publication": "HOLD",
        "status": "OBSERVED" if allowed else "EVIDENCE_PENDING",
        "gate_note": GATE_NOTE,
    }
