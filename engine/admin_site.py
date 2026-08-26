"""Integrated Admin Studio surface. PRESENTATION_ONLY plus local control-plane buttons."""

from __future__ import annotations

import json
from pathlib import Path

from .html import attr, dumps_json, esc
from .paths import ADMIN_DIR, ASSETS_DIR, ROOT
from .chrome import ds_a11y_bar

MODULES = [
    ("dashboard", "Painel", "admin.html"),
    ("database", "Banco GitHub", "admin/database.html"),
    ("catalog", "Catálogo", "admin/catalog.html"),
    ("pipeline", "Pipeline", "admin/pipeline.html"),
    ("layers", "44 camadas", "admin/layers.html"),
    ("validations", "Validações", "admin/validations.html"),
    ("agents", "Agentes", "admin/agents.html"),
    ("monitoring", "Monitoramento", "admin/monitoring.html"),
    ("library", "Biblioteca", "admin/library.html"),
    ("apis", "APIs / órgãos", "admin/apis.html"),
    ("backlog", "Backlog", "admin/backlog.html"),
    ("design", "Design System", "admin/design-system.html"),
    ("locales", "Locales / Drive", "admin/locales.html"),
    ("mdm", "Master Data", "admin/mdm.html"),
    ("frameworks", "Frameworks", "admin/frameworks.html"),
    ("maturity", "Maturidade", "admin/maturity.html"),
    ("renderer", "Renderer", "admin/renderer.html"),
    ("deploy", "Deploy Git", "admin/deploy.html"),
]


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def studio_map() -> dict:
    return load_json(ADMIN_DIR / "studio_cms_map.v1.json")


def token_registry() -> dict:
    return load_json(ROOT / "cko_core" / "design_token_registry.json")


def inventory_tables() -> list[dict]:
    rows = []
    for folder, schema in (
        ("cko_core", "md_backbone"),
        ("cko_md", "master_data"),
        ("cko_reg", "regulatory"),
        ("cko_assurance", "assurance"),
        ("data/tools", "domain_candidate"),
        ("admin", "admin_contract"),
        ("cko_inbox/drive", "drive_inbox_quarantine"),
    ):
        directory = ROOT / folder
        if not directory.exists():
            continue
        for path in sorted(directory.glob("*.json")):
            rows.append({
                "schema": schema,
                "table": path.stem,
                "path": str(path.relative_to(ROOT)),
                "bytes": path.stat().st_size,
            })
    return rows


def _module_href(filename: str, nested: bool) -> str:
    if not nested:
        return filename
    if filename == "admin.html":
        return "../admin.html"
    return filename.split("/", 1)[1]


def admin_shell(
    *,
    title: str,
    description: str,
    current: str,
    inner: str,
    css_href: str,
    home_href: str,
    inline_css: bool,
    nested: bool,
    extra_head: str = "",
) -> str:
    from .generate import _shell

    items = []
    for key, label, filename in MODULES:
        href = _module_href(filename, nested)
        current_cls = ' aria-current="page"' if key == current else ""
        items.append(f'<a href="{attr(href)}"{current_cls}>{esc(label)}</a>')
    root_prefix = "../" if nested else ""
    script_src = f"{root_prefix}assets/admin-control.js"
    body = f"""{ds_a11y_bar()}
<div class="admin-app">
  <aside class="admin-side" aria-label="Módulos do Studio">
    <p class="admin-brand">CKO Studio</p>
    <p class="admin-brand-sub">Admin ↔ frontend · GitHub</p>
    <nav class="admin-nav">{"".join(items)}</nav>
    <p class="admin-side-note"><a href="{attr(home_href)}">Site público</a></p>
  </aside>
  <div class="admin-main">
    <header class="admin-top">
      <p class="eyebrow">{esc(title)}</p>
      <p class="admin-kicker">Não grava fórmula · uuid HOLD · NO_SENSITIVE_CAPTURE · chrome DS na barra de acessibilidade</p>
    </header>
    <main id="conteudo" class="admin-content">
      {inner}
    </main>
  </div>
</div>"""
    if inline_css:
        js = (ASSETS_DIR / "js" / "admin-control.js").read_text(encoding="utf-8")
        scripts = f'<script data-admin-root="{attr(root_prefix)}">\n{js}\n</script>'
    else:
        scripts = f'<script data-admin-root="{attr(root_prefix)}" src="{attr(script_src)}"></script>'
    return _shell(
        title,
        description,
        body,
        css_href=None if inline_css else css_href,
        css_inline="file" if inline_css else None,
        extra_head='<meta name="robots" content="noindex,nofollow">' + extra_head,
        scripts=scripts,
        home_href=home_href,
        social=False,
    )


def _table(headers: list[str], rows: list[list[str]]) -> str:
    th = "".join(f"<th>{esc(h)}</th>" for h in headers)
    body = []
    for row in rows:
        body.append("<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>")
    return (
        '<div class="table-wrap"><table class="inspect">'
        f"<thead><tr>{th}</tr></thead><tbody>{''.join(body)}</tbody></table></div>"
    )


def _status_chip(text: str) -> str:
    value = str(text or "UNKNOWN")
    cls = "chip"
    upper = value.upper()
    if any(token in upper for token in ("HOLD", "QUARANT", "CONFLICT", "PENDING", "UNKNOWN", "FORBIDDEN")):
        cls = "chip chip-hold"
    elif any(token in upper for token in ("PASS", "MATCH", "IMPLEMENTED", "OBSERVED", "RESTORED")):
        cls = "chip chip-ok"
    return f'<span class="{cls}">{esc(value)}</span>'


def page_dashboard(ctx: dict, *, css_href: str, home_href: str, inline_css: bool, nested: bool) -> str:
    tools = ctx["tools"]
    layers = ctx["layers"]
    completeness = ctx["completeness"]
    release = ctx["release"]
    studio = ctx["studio"]
    inner = f"""
    <header class="page-hero">
      <h1>Área administrativa integrada.</h1>
      <p class="lede">CKO-MD e CKO-REG são a espinha dorsal. Clinical Calculators e as demais camadas já existem no registry. Banco Day Zero = JSON no GitHub. Mapa Studio (Braden 98%, Ativo, Concluído) está em quarentena.</p>
      <p class="hold-banner">Release clínica: {esc(release.get("status"))} · Completude: {esc(completeness.get("status"))} · Layer Registry (44) · MD {esc(layers[0].get("md_profile_ref") if layers else "")} · REG {esc(layers[0].get("reg_profile_ref") if layers else "")} · SHARED_GITHUB_CONTRACTS · PRIV-NO-SENSITIVE-CAPTURE</p>
    </header>
    <section class="catalog admin-cards" aria-label="Módulos">
      <a class="tool-card" href="{attr(_module_href('admin/database.html', nested))}"><p class="eyebrow">MD/REG</p><h2>Banco GitHub</h2><p>Tabelas JSON versionadas. Sem Postgres live neste repo.</p></a>
      <a class="tool-card" href="{attr(_module_href('admin/catalog.html', nested))}"><p class="eyebrow">Domínio</p><h2>Catálogo</h2><p>5 candidatos piloto + itens Studio em QUARANTINED.</p></a>
      <a class="tool-card" href="{attr(_module_href('admin/renderer.html', nested))}"><p class="eyebrow">L400</p><h2>Renderer</h2><p>Botão local gera fetch + inline. PRESENTATION_ONLY.</p></a>
      <a class="tool-card" href="{attr(_module_href('admin/deploy.html', nested))}"><p class="eyebrow">Git</p><h2>Deploy</h2><p>Prepara changeset. git push é FORBIDDEN no botão.</p></a>
      <a class="tool-card" href="{attr(_module_href('admin/maturity.html', nested))}"><p class="eyebrow">M0–M7</p><h2>Maturidade</h2><p>Panorama observado de MD, REG, agentes, CAAT, IPE, Drive e DS.</p></a>
      <a class="tool-card" href="{attr(_module_href('admin/library.html', nested))}"><p class="eyebrow">L60</p><h2>Biblioteca</h2><p>Recursos ANVISA/MS/COFEN + currículo básico→avançado. Publicação HOLD.</p></a>
      <a class="tool-card" href="{attr(_module_href('admin/apis.html', nested))}"><p class="eyebrow">APIs</p><h2>Órgãos / APIs</h2><p>Portal ANVISA HTML ≠ JSON. CKAN + Congresso. base_url null até HTTP 200 JSON. PLP bloqueado. SQLite inbox.</p></a>
      <a class="tool-card" href="{attr(_module_href('admin/mdm.html', nested))}"><p class="eyebrow">L10</p><h2>Master Data</h2><p>Entity types e locale registry. Mockup MDM = linguagem de layout.</p></a>
      <a class="tool-card" href="{attr(_module_href('admin/frameworks.html', nested))}"><p class="eyebrow">COSO/COBIT/ISO</p><h2>Frameworks</h2><p>Registry only. CLAUSE_TEXT_UNAVAILABLE. ISO 8000 = perfil CKO, não certificação.</p></a>
    </section>
    <section class="panel">
      <h2>Mockups enviados nesta sessão</h2>
      <p>Studio CMS, Renderer, Validadores, MDM, Gestão de IAs, COSO, COBIT e Arquitetura de Dados são <strong>LAYOUT_LANGUAGE_ONLY</strong>. KPIs 98%/Produção/SHA dos murais = DOCUMENT_CLAIM. Mapa: <code>admin/mockup_reference_map.v1.json</code>.</p>
    </section>
    <section class="panel">
      <h2>Imagens do mapa Studio (lote anterior)</h2>
      <p>{esc((studio.get("images_in_conversation") or {}).get("note"))}</p>
    </section>
    """
    return admin_shell(
        title="Painel · CKO Studio",
        description="Painel administrativo integrado CKO.",
        current="dashboard",
        inner=inner,
        css_href=css_href,
        home_href=home_href,
        inline_css=inline_css,
        nested=nested,
        extra_head=f'<script type="application/json" id="admin-contract">{dumps_json(ctx.get("contract") or {})}</script>',
    )


def page_database(ctx: dict, **kwargs) -> str:
    rows = []
    for item in inventory_tables():
        rows.append([
            esc(item["schema"]),
            esc(item["table"]),
            f"<code>{esc(item['path'])}</code>",
            str(item["bytes"]),
        ])
    types = (load_json(ROOT / "cko_md" / "entity_type_registry.json").get("types") or [])
    type_rows = [[esc(t.get("business_key")), esc(t.get("name"))] for t in types]
    supabase = load_json(ROOT / "cko_inbox" / "extracted" / "supabase_inventory.json")
    project_rows = [
        [
            esc(item.get("ref")),
            esc(item.get("name")),
            esc(item.get("status")),
            esc(item.get("region")),
        ]
        for item in (supabase.get("projects") or [])
    ] or [["—", "—", "EVIDENCE_PENDING", "—"]]
    fn_rows = [
        [esc(item.get("slug")), esc(item.get("status")), esc(item.get("source") or "NOT_FETCHED")]
        for item in (supabase.get("edge_functions") or [])
    ] or [["—", "—", "não observado"]]
    inner = f"""
    <header class="page-hero">
      <h1>Banco de dados Day Zero.</h1>
      <p class="lede">Store canônico deste lote: arquivos JSON no GitHub. Relato de Supabase 172 entities permanece EVIDENCE_PENDING (SQL/bytes/hash não estão neste tree).</p>
    </header>
    <section class="panel">
      <h2>Schemas / arquivos ({len(rows)})</h2>
      {_table(["schema", "objeto", "path", "bytes"], rows)}
    </section>
    <section class="panel">
      <h2>Entity types MD</h2>
      {_table(["business_key", "nome"], type_rows)}
    </section>
    <section class="panel">
      <h2>Supabase (descoberta, não canônico)</h2>
      <p class="hold-banner">Schema SQL: {esc(supabase.get("schema") or "EVIDENCE_PENDING")}. 28P01 em list_tables no ref aevqrmkdhffmursdtcmo. MCP get_project/list_tables no ref yskgekcjzndptzmnjfke = permission denied. Não inventar tabelas. LLM gateway HOLD. Fonte de Edge Function NÃO baixada. Chave publishable não está no GitHub.</p>
      <p>MCP Cursor (read_only): <code>https://mcp.supabase.com/mcp?project_ref=yskgekcjzndptzmnjfke&amp;read_only=true</code> em <code>.cursor/mcp.json</code> e <code>.mcp.json</code>. Skills: <code>.agents/skills/supabase</code>.</p>
      {_table(["ref", "nome", "status", "região"], project_rows)}
      <h3>Edge Functions (nome apenas)</h3>
      {_table(["slug", "status", "source"], fn_rows)}
    </section>
    <section class="panel">
      <h2>RLS / Postgres</h2>
      <p class="hold-banner">Nenhuma alteração de RLS. Banco relacional: NÃO ENCONTRADO neste repositório.</p>
    </section>
    """
    return admin_shell( title="Banco GitHub · CKO Studio", description="Inventário JSON Day Zero.", current="database", inner=inner, **kwargs)


def page_catalog(ctx: dict, **kwargs) -> str:
    tool_rows = []
    for tool in ctx["tools"]:
        overview = tool.get("overview") or {}
        prefix = "../" if kwargs["nested"] else ""
        tool_rows.append([
            f'<a href="{attr(prefix)}tools/{attr(tool["slug"])}.html">{esc(tool.get("slug"))}</a>',
            esc(overview.get("name")),
            _status_chip(tool.get("status")),
            esc(tool.get("kind")),
            esc("OBSERVED"),
        ])
    studio_rows = []
    for item in ctx["studio"].get("tabela_itens_logicos") or []:
        studio_rows.append([
            esc(item.get("business_key")),
            esc(item.get("id_logico")),
            esc(item.get("titulo")),
            _status_chip(item.get("studio_status")),
            _status_chip(item.get("cko_status")),
            esc("não" if not item.get("in_data_tools") else "sim"),
        ])
    inner = f"""
    <header class="page-hero">
      <h1>Catálogo prático.</h1>
      <p class="lede">Esquerda: objetos que existem em <code>data/tools</code>. Direita: mapa Studio em quarentena. Não mesclar.</p>
    </header>
    <section class="panel">
      <h2>Candidatos neste repositório ({len(ctx["tools"])})</h2>
      {_table(["slug", "nome", "status", "kind", "epistemic"], tool_rows)}
    </section>
    <section class="panel">
      <h2>Mapa Studio — itens lógicos (QUARANTINED)</h2>
      {_table(["business_key", "id lógico", "título", "claim Studio", "CKO", "em data/tools"], studio_rows)}
    </section>
    """
    return admin_shell( title="Catálogo · CKO Studio", description="Catálogo piloto e quarentena Studio.", current="catalog", inner=inner, **kwargs)


def page_pipeline(ctx: dict, **kwargs) -> str:
    rows = []
    for item in ctx["studio"].get("pipeline_status") or []:
        rows.append([
            esc(item.get("etapa")),
            _status_chip(item.get("studio_claim")),
            _status_chip(item.get("cko_status")),
            esc(item.get("epistemic_status")),
        ])
    inner = f"""
    <header class="page-hero">
      <h1>Pipeline de conteúdo.</h1>
      <p class="lede">O mural Studio marca tudo Concluído. Este repositório mede o lote piloto. DOCUMENTADO ≠ PUBLICADO.</p>
    </header>
    <section class="panel">
      {_table(["etapa", "claim Studio", "status CKO observado", "epistemic"], rows)}
    </section>
    """
    return admin_shell( title="Pipeline · CKO Studio", description="Pipeline Studio vs CKO.", current="pipeline", inner=inner, **kwargs)


def page_layers(ctx: dict, **kwargs) -> str:
    phase = load_json(ROOT / "cko_md" / "layer_md_reg_phase.json")
    rows = []
    for layer in (phase.get("layers") or ctx["layers"]):
        rows.append([
            esc(layer.get("layer_code") or layer.get("layer_code")),
            esc(layer.get("canonical_name")),
            esc(layer.get("phase") or layer.get("maturity")),
            _status_chip((layer.get("md") or {}).get("population") or layer.get("maturity")),
            _status_chip((layer.get("reg") or {}).get("population") or "M0"),
            esc((layer.get("md") or {}).get("populated")),
            esc(layer.get("gap") or ""),
        ])
    if not phase.get("layers"):
        rows = []
        for layer in ctx["layers"]:
            rows.append([
                esc(layer.get("layer_code")),
                esc(layer.get("canonical_name")),
                _status_chip(layer.get("maturity")),
                f"<code>{esc(layer.get('md_profile_ref'))}</code>",
                f"<code>{esc(layer.get('reg_profile_ref'))}</code>",
                "",
                "",
            ])
    phase_rows = [
        [esc(item.get("id")), esc(item.get("name")), esc(", ".join(item.get("layers") or [])), esc(item.get("md_populated")), esc(item.get("owner_secret"))]
        for item in (phase.get("phases") or [])
    ]
    counts = phase.get("counts") or {}
    inner = f"""
    <header class="page-hero">
      <h1>44 camadas — MD + REG faseados.</h1>
      <p class="lede">Envelope completo nas 44 ≠ população completa ≠ IMPLEMENTADO ≠ ASSURED. Registry permanece M0 EXISTS. Publicação HOLD.</p>
      <p class="hold-banner">MD populated={esc(counts.get("md_populated"))} · MD implemented={esc(counts.get("md_implemented"))} · REG populated={esc(counts.get("reg_populated"))} · assured={esc(counts.get("assured"))} · Braden em data/tools={esc(phase.get("braden_in_data_tools"))}.</p>
    </header>
    <section class="panel">
      <h2>Fases P0–P5 ({esc(phase.get("business_key") or "MD-LAYER-PHASE-001")})</h2>
      {_table(["fase", "nome", "camadas", "MD populated", "exige segredo"], phase_rows)}
    </section>
    <section class="panel">{_table(["code", "nome", "fase", "MD pop.", "REG pop.", "MD populated", "gap"], rows)}</section>
    """
    return admin_shell( title="Camadas · CKO Studio", description="Layer Registry 44 com envelopes MD+REG faseados.", current="layers", inner=inner, **kwargs)


def page_validations(ctx: dict, **kwargs) -> str:
    caat = ctx["layer_caat"]
    findings = ctx["completeness"].get("blockingFindings") or []
    finding_rows = [[esc(item.get("id")), esc(item.get("reason", item.get("id")))] for item in findings] or [["—", "Nenhum achado estrutural de schema."]]
    studio_rows = []
    for item in ctx["studio"].get("validacoes_clinicas") or []:
        studio_rows.append([
            esc(item.get("validacao")),
            esc(item.get("regra")),
            esc(item.get("severidade")),
            _status_chip(item.get("studio_status")),
            _status_chip(item.get("cko_status")),
        ])
    inner = f"""
    <header class="page-hero">
      <h1>Validações.</h1>
      <p class="lede">CAAT-LAYER-COUNT-44 testa a população do registry. Completude clínica do lote piloto permanece HOLD. Claims Studio de Aprovado não são reperformance.</p>
    </header>
    <section class="panel">
      <h2>CAAT Layer Registry</h2>
      <p>{_status_chip(caat.get("status"))} population={esc(caat.get("population"))} tested={esc(caat.get("tested"))} failed={esc(caat.get("failed"))}</p>
      <p>{esc(caat.get("note"))}</p>
    </section>
    <section class="panel">
      <h2>Completude clínica (lote piloto)</h2>
      {_table(["id", "reason"], finding_rows)}
    </section>
    <section class="panel">
      <h2>Validações do mapa Braden (quarentena)</h2>
      {_table(["validação", "regra", "severidade", "Studio", "CKO"], studio_rows)}
    </section>
    """
    return admin_shell( title="Validações · CKO Studio", description="CAAT, completude e quarentena.", current="validations", inner=inner, **kwargs)


def page_agents(ctx: dict, **kwargs) -> str:
    registry = load_json(ROOT / "cko_assurance" / "agent_registry.json")
    run = load_json(ROOT / "cko_inbox" / "agent_runs" / "latest.json")
    class_rows = []
    for item in registry.get("agents") or []:
        class_rows.append([
            esc(item.get("agent_id")),
            esc(item.get("class")),
            _status_chip("IMPLEMENTED" if item.get("implemented") else "REGISTERED"),
            esc(item.get("writes_to")),
            _status_chip("HOLD" if not item.get("promotes_to_md") else "PROMOTED"),
        ])
    studio_rows = []
    for item in ctx["studio"].get("agentes_tarefas") or []:
        studio_rows.append([
            esc(item.get("agente")),
            _status_chip(item.get("studio_status")),
            esc(item.get("data_hora")),
            _status_chip(item.get("cko_status")),
        ])
    steps = "".join(f"<li>{esc(step.get('agent_id'))} · {esc(step.get('status'))}</li>" for step in (run.get("steps") or []))
    fronts = load_json(ROOT / "cko_md" / "fronts_plan.json")
    unblock = load_json(ROOT / "cko_md" / "owner_unblock.json")
    front_rows = [
        [
            esc(item.get("id")),
            esc(item.get("name")),
            _status_chip(item.get("status")),
            esc(", ".join(item.get("agents") or [])),
            esc(item.get("gap")),
            esc((item.get("action") or "")[:160]),
        ]
        for item in (fronts.get("fronts") or [])
    ] or [["—", "—", "HOLD", "—", "—", "Plano ainda não gerado."]]
    unblock_rows = [
        [
            esc(item.get("id")),
            esc(item.get("frente")),
            _status_chip(item.get("status")),
            esc(item.get("title")),
            esc((item.get("how") or "")[:220]),
        ]
        for item in (unblock.get("actions") or [])
    ] or [["—", "—", "HOLD", "—", "Checklist ainda não gerado."]]
    drive = load_json(ROOT / "cko_inbox" / "extracted" / "drive_inventory.json")
    counts = drive.get("counts") or {}
    inner = f"""
    <header class="page-hero">
      <h1>Agentes.</h1>
      <p class="lede">Runner de extração IMPLEMENTADO (inbox). Publicação clínica HOLD. MAKER ≠ CHECKER ≠ AUDITOR. CLI: <code>python3 -m engine.cli extract</code>.</p>
      <p class="hold-banner">Último run: {esc(run.get("run_id") or "nenhum")} · status {esc(run.get("status") or "UNKNOWN")} · publicação {esc(run.get("publication") or "HOLD")} · IPE reliance={esc(run.get("ipe_reliance"))}.</p>
    </header>
    <section class="panel">
      <h2>Frentes do plano vivo ({esc(fronts.get("business_key") or "MD-FRONTS-PLAN-001")})</h2>
      <p>Método {esc(fronts.get("method") or "RECOVER → COMPARE → GAP ONLY")}. Publicação {esc(fronts.get("publication") or "HOLD")}. LLM autoridade={esc(fronts.get("llm_authority"))}.</p>
      {_table(["frente", "nome", "status", "agentes", "gap", "ação"], front_rows)}
    </section>
    <section class="panel">
      <h2>Como o dono desbloqueia agentes ({esc(unblock.get("business_key") or "MD-OWNER-UNBLOCK-001")})</h2>
      <p>Segredo, decisão de licença ou confirmação de evidência. Agente não inventa senha, 32 APIs nem texto NANDA/NIC/NOC.</p>
      {_table(["id", "frente", "status", "pedido", "como apoiar"], unblock_rows)}
    </section>
    <section class="panel">
      <h2>Inventário Drive classificado</h2>
      <p>População {esc(drive.get("population"))} · ALREADY_IN_CKO={esc(counts.get("ALREADY_IN_CKO"))} · QUARANTINE={esc(counts.get("DISCOVERY_QUARANTINE"))} · SKIP={esc(counts.get("SKIP_BINARY_DUMP"))} · GAP={esc(counts.get("CANDIDATE_GAP"))}. HTML de escalas não entra no header público.</p>
    </section>
    <section class="panel">
      <h2>Registry CKO ({esc(registry.get("population"))} agentes)</h2>
      {_table(["agent_id", "classe", "runtime", "escreve em", "MD"], class_rows)}
      <p>Publication implemented={esc(registry.get("publication_implemented"))}. Lista completa no JSON.</p>
    </section>
    <section class="panel">
      <h2>Pipeline do último run</h2>
      <ol>{steps or "<li>Nenhum run gravado.</li>"}</ol>
    </section>
    <section class="panel">
      <h2>Execução alegada no mapa Braden</h2>
      {_table(["agente", "Studio", "data", "CKO"], studio_rows)}
    </section>
    """
    return admin_shell( title="Agentes · CKO Studio", description="Agent registry e extração inbox.", current="agents", inner=inner, **kwargs)


def page_monitoring(ctx: dict, **kwargs) -> str:
    events_doc = load_json(ROOT / "cko_inbox" / "extracted" / "change_events.json")
    monitor = load_json(ROOT / "cko_assurance" / "monitoring_events.json")
    compare_src = load_json(ROOT / "cko_inbox" / "extracted" / "compare_source.json")
    compare_int = load_json(ROOT / "cko_inbox" / "extracted" / "compare_internal.json")
    events = [item for item in (events_doc.get("events") or []) if not str(item.get("logical_id") or "").startswith("TEST-")]
    event_rows = [
        [
            esc(item.get("kind")),
            esc(item.get("logical_id")),
            esc(item.get("detected_at")),
            esc((item.get("note") or "")[:180]),
        ]
        for item in events[-20:]
    ] or [["—", "—", "—", "Nenhum evento de drift gravado."]]
    cmp_rows = [
        [esc(item.get("logical_id")), _status_chip(item.get("status")), esc((item.get("observed_sha256") or item.get("first_sha256") or "")[:16])]
        for item in (compare_src.get("compared") or [])
    ]
    int_rows = [
        [esc(item.get("logical_id")), _status_chip(item.get("status")), esc(", ".join(item.get("internal_has_forbidden") or []) or "—")]
        for item in (compare_int.get("compared") or [])
    ]
    kpis = (ctx["studio"].get("monitoramento") or {}).get("kpis") or []
    claim_rows = [[esc(k.get("metrica")), esc(k.get("valor_claimed")), esc(k.get("variacao_claimed")), _status_chip("UNKNOWN")] for k in kpis]
    inner = f"""
    <header class="page-hero">
      <h1>Monitoramento.</h1>
      <p class="lede">Eventos reais vault vs fonte vs projeção. KPIs do mockup Studio permanecem UNKNOWN. Sem IPE não há reliance.</p>
      <p class="hold-banner">SOURCE_DRIFT={esc(monitor.get("open_source_drift"))} · INTERNAL_DRIFT={esc(monitor.get("open_internal_drift"))} · eventos={esc(monitor.get("population") or events_doc.get("population"))} · wired={esc(monitor.get("wired_to_frontend"))}</p>
    </header>
    <section class="panel">
      <h2>Eventos de alteração</h2>
      {_table(["tipo", "logical_id", "quando", "nota"], event_rows)}
    </section>
    <section class="panel">
      <h2>Fonte vs primeira cópia WORM</h2>
      {_table(["alvo", "status", "sha256"], cmp_rows)}
    </section>
    <section class="panel">
      <h2>Origem vs projeção interna</h2>
      <p>Hash diferente com ads/email removidos = EXPECTED_REWRITE.</p>
      {_table(["alvo", "status", "tokens proibidos na projeção"], int_rows)}
    </section>
    <section class="panel">
      <h2>KPIs claimed do Studio (não usar)</h2>
      {_table(["métrica", "valor claimed", "variação claimed", "CKO"], claim_rows)}
    </section>
    """
    return admin_shell( title="Monitoramento · CKO Studio", description="Drift vault vs fonte vs frontend.", current="monitoring", inner=inner, **kwargs)


def page_library(ctx: dict, **kwargs) -> str:
    lib = load_json(ROOT / "cko_md" / "resource_library.json")
    curr = load_json(ROOT / "cko_md" / "content_curriculum.json")
    libmap = load_json(ROOT / "cko_md" / "library_api_map.json")
    cmp32 = load_json(ROOT / "cko_md" / "library_32_compare.json")
    pgd = load_json(ROOT / "cko_md" / "pgdados_program.json")
    pgd_probe = load_json(ROOT / "cko_md" / "pgdados_pending_probe.json")
    pages_pend = load_json(ROOT / "cko_md" / "pages_full_reg_pendencies.json")
    clin = load_json(ROOT / "cko_md" / "clinical_dictionary_catalog.json")
    nnn_id = load_json(ROOT / "cko_md" / "nnn_identity_catalog.json")
    ucp = load_json(ROOT / "cko_md" / "ucp_v2_compare.json")
    l70 = load_json(ROOT / "cko_md" / "l70_anvisa_compare.json")
    alerts = load_json(ROOT / "cko_assurance" / "freshness_alerts.json")
    laws = load_json(ROOT / "cko_md" / "legislation_instrument_registry.json")
    res_rows = [
        [
            esc(item.get("business_key")),
            esc(item.get("title")),
            esc(item.get("status")),
            f"<code>{esc(item.get('md_ref'))}</code>",
            f"<code>{esc(item.get('reg_ref'))}</code>",
        ]
        for item in (lib.get("resources") or [])
    ]
    unit_rows = [
        [
            esc(item.get("tool_slug")),
            esc(item.get("level")),
            esc((item.get("body") or {}).get("status")),
            f"<code>{esc(item.get('tool_md_ref'))}</code>",
            f"<code>{esc(item.get('reg_ref'))}</code>",
        ]
        for item in (curr.get("units") or [])
    ]
    pend_rows = [
        [esc(item.get("business_key")), esc(item.get("severity")), esc(item.get("reason"))]
        for item in (curr.get("pending_high") or [])
    ]
    alert_rows = [
        [esc(item.get("severity")), esc(item.get("kind")), esc((item.get("message") or "")[:180])]
        for item in (alerts.get("alerts") or [])
    ]
    law_rows = [
        [
            esc(item.get("business_key")),
            esc(item.get("title")),
            esc(item.get("tipo")),
            esc("REVOKED" if item.get("revoked") else item.get("status")),
            f"<code>{esc(item.get('md_ref'))}</code>",
            f"<code>{esc(item.get('reg_ref'))}</code>",
        ]
        for item in (laws.get("instruments") or [])
    ]
    set_rows = [
        [
            esc(item.get("id")),
            esc(item.get("count")),
            esc(item.get("kind")),
            esc(item.get("official_api") or item.get("official_api_status") or "—"),
            esc((item.get("note") or "")[:180]),
        ]
        for item in (libmap.get("observed_sets") or [])
    ]
    layer_api_rows = [
        [
            esc(item.get("layer")),
            esc(item.get("adapter") or "null"),
            esc(item.get("http_status") if item.get("http_status") is not None else "null"),
            _status_chip(item.get("epistemic_status")),
            esc((item.get("note") or "")[:180]),
        ]
        for item in (libmap.get("api_where_possible") or [])
    ]
    page_pend_rows = [
        [esc(item.get("stem")), esc(item.get("gap")), esc(item.get("in_data_tools"))]
        for item in (pages_pend.get("third_party_scale_stems") or [])
    ]
    clin_code_rows = [
        [
            esc(item.get("slug")),
            esc(item.get("code")),
            esc(item.get("kind")),
            _status_chip(item.get("relation")),
            esc(", ".join(item.get("drive_name_hits") or []) or "—"),
        ]
        for item in (clin.get("pilot_codes") or [])
    ]
    clin_tool_rows = [[esc(name)] for name in (clin.get("new_tool_names") or [])[:20]]
    nnn_rows = [
        [
            esc(item.get("system")),
            esc(item.get("code")),
            esc(item.get("canonical_label") or "—"),
            esc(item.get("display_label")),
            f'<a href="{esc(item.get("deep_link"))}">{esc(item.get("deep_link"))}</a>' if item.get("deep_link") else "—",
            _status_chip(item.get("drive_file_status") or "QUARANTINE"),
        ]
        for item in (nnn_id.get("identities") or [])
    ]
    ucp_rows = [
        [
            esc(item.get("file")),
            esc(item.get("schema_id") or "—"),
            esc((item.get("draft") or "").replace("https://json-schema.org/", "").replace("http://json-schema.org/", "")),
            esc((item.get("sha256") or "")[:12] or "—"),
            esc(item.get("copied_into_schemas")),
        ]
        for item in (ucp.get("schemas") or [])
    ]
    ucp_missing_rows = [
        [esc(item.get("artifact_id")), esc(item.get("artifact_class")), esc(item.get("file"))]
        for item in (ucp.get("missing_from_register") or [])
    ]
    l70_api = (l70.get("official_api") or {})
    l70_portal = l70_api.get("portal") or {}
    l70_consultas = l70_api.get("consultas_medicamentos") or {}
    l70_zip = (l70.get("drive") or {}).get("zip") or {}
    l70_rows = [
        [
            esc(l70_portal.get("business_key") or "API-ANVISA-PORTAL"),
            esc(l70_portal.get("url") or "https://api.anvisa.gov.br/"),
            esc(l70_portal.get("http_status") if l70_portal.get("http_status") is not None else "—"),
            _status_chip(l70_portal.get("epistemic_status") or "EVIDENCE_PENDING"),
            esc("null" if not l70_portal.get("base_url") else l70_portal.get("base_url")),
            esc("não" if not l70_portal.get("rest_json") else "sim"),
        ],
        [
            esc(l70_consultas.get("business_key") or "API-ANVISA-CONSULTAS-MEDICAMENTOS"),
            esc(l70_consultas.get("url") or "https://consultas.anvisa.gov.br/api/consulta/medicamentos"),
            esc(l70_consultas.get("http_status") if l70_consultas.get("http_status") is not None else "—"),
            _status_chip(l70_consultas.get("epistemic_status") or "EVIDENCE_PENDING"),
            "null",
            "não",
        ],
    ]
    l70_gap_rows = [
        [esc(item.get("id")), _status_chip(item.get("status")), esc(item.get("reason"))]
        for item in (l70.get("gaps") or [])
    ]
    observed = cmp32.get("observed_counts") or {}
    sums = cmp32.get("observed_sums") or {}
    equals = cmp32.get("observed_sum_equals_32") or {}
    cmp_count_rows = [
        [esc(key), esc(value), "EVIDENCE_PENDING", "conjunto observado; não é as 32 APIs"]
        for key, value in observed.items()
    ]
    cmp_sum_rows = [
        [
            esc(key),
            esc(value),
            esc(equals.get(key)),
            "nenhuma soma observada equivale a 32" if not equals.get(key) else "FALHA: soma = 32",
        ]
        for key, value in sums.items()
    ]
    guia_parts = {item.get("part"): item for item in (pgd.get("guia_parts") or [])}
    cartilhas = {item.get("volume"): item for item in (pgd.get("cartilhas") or [])}
    last_probe = pgd.get("last_html_probe") or {}
    pgd_rows = [
        [
            "Guia Parte 3",
            esc((guia_parts.get(3) or {}).get("status") or "EVIDENCE_PENDING"),
            esc((guia_parts.get(3) or {}).get("url") or "null"),
            esc(last_probe.get("parte3_pdf_href") if last_probe else pgd_probe.get("parte3_pdf_href")),
            "rótulo ≠ href PDF gov.br",
        ],
        [
            "Cartilha vol. 4",
            esc((cartilhas.get(4) or {}).get("status") or "EVIDENCE_PENDING"),
            esc((cartilhas.get(4) or {}).get("url") or "null"),
            esc(last_probe.get("cartilha_v4_pdf_href") if last_probe else pgd_probe.get("cartilha_v4_pdf_href")),
            "mencionada no hub; sem href volume-4",
        ],
        [
            "Cartilha vol. 5",
            esc((cartilhas.get(5) or {}).get("status") or "EVIDENCE_PENDING"),
            esc((cartilhas.get(5) or {}).get("url") or "null"),
            esc(last_probe.get("cartilha_v5_pdf_href") if last_probe else pgd_probe.get("cartilha_v5_pdf_href")),
            "mencionada no hub; sem href volume-5",
        ],
    ]
    inner = f"""
    <header class="page-hero">
      <h1>Biblioteca de recursos.</h1>
      <p class="lede">Catálogo MD + currículo documental + legislação federal do Congresso + PGDADOS (SGD). Sem HTML/PDF integral. Sem LLM. Publicação HOLD. PLP bloqueado. COREN sem API REST.</p>
      <p class="hold-banner">Recursos {esc(lib.get("population"))} · Unidades {esc(curr.get("population"))} · Leis {esc(laws.get("population"))} · Pendências ALTA {esc(curr.get("pending_high_count"))} · Alertas {esc(alerts.get("population"))} · 32 bibliotecas={esc(libmap.get("claimed_32_libraries") or cmp32.get("claimed_32_libraries") or "EVIDENCE_PENDING")} · F10={esc(cmp32.get("owner_decision") or libmap.get("owner_decision") or "HOLD")}</p>
    </header>
    <section class="panel">
      <h2>32 APIs COMPARE ({esc(cmp32.get("business_key") or "MD-LIB-32-COMPARE-001")})</h2>
      <p>Dono UNBLOCK-32-LIST={esc(cmp32.get("owner_decision") or "COMPARE_ACCEPTED")}. Claimed 32={esc(cmp32.get("claimed_32_libraries") or "EVIDENCE_PENDING")}. Soma observada = 32? {esc(cmp32.get("claimed_32_equals_any_observed_sum"))}. Sem inventar adapters. Sem promover CAL-VAC, Braden ou NNN.</p>
      {_table(["conjunto", "n observado", "claimed 32", "nota"], cmp_count_rows or [["rode extract", "—", "EVIDENCE_PENDING", "—"]])}
      {_table(["soma heterogénea", "n", "equals 32", "nota"], cmp_sum_rows or [["—", "—", "false", "—"]])}
    </section>
    <section class="panel">
      <h2>PGDADOS Parte 3 / cartilhas 4–5 ({esc(pgd.get("business_key") or "MD-PGDADOS-001")})</h2>
      <p>Probe ao vivo hub HTTP {esc(pgd_probe.get("hub_http_status") or last_probe.get("hub_http_status") or "—")} · guia HTTP {esc(pgd_probe.get("guia_http_status") or last_probe.get("guia_http_status") or "—")} · probed_at {esc(pgd_probe.get("probed_at") or last_probe.get("live_probe_at") or "offline")}. Rótulo na página ≠ href PDF. Sem copiar corpo PDF. mwpt/ABNT ignorados.</p>
      {_table(["recurso", "status", "url", "href PDF", "nota"], pgd_rows)}
    </section>
    <section class="panel">
      <h2>Mapa L60 observado vs 32 reivindicadas ({esc(libmap.get("business_key") or "MD-LIB-API-MAP-001")})</h2>
      <p>Contagens COMPARE do Drive. 32 APIs permanecem EVIDENCE_PENDING. Sem promover CAL-VAC nem nanda-00046.json. Decisão dono={esc(libmap.get("owner_decision") or "COMPARE_ACCEPTED")}.</p>
      {_table(["conjunto", "n", "tipo", "API", "nota"], set_rows or [["—", "—", "—", "—", "mapa ainda não gerado"]])}
      {_table(["camada", "adapter", "HTTP", "estado", "nota"], layer_api_rows or [["—", "—", "—", "HOLD", "—"]])}
    </section>
    <section class="panel">
      <h2>Dicionário clínico Drive ({esc(clin.get("business_key") or "MD-CLIN-DICT-001")})</h2>
      <p>Zip {esc(clin.get("title"))} · dono {esc(clin.get("owner_sent_ref") or "UNBLOCK-DICT-SHEETS")} enviado={esc(clin.get("owner_sent"))} · sheets Content_Schemas/Meta_Schemas={esc(clin.get("sheets_content_meta") or "MISSING")} · FLD policy={esc(clin.get("runtime_fld_policy") or "ONLY_EXISTING_FLD")} · campos Foundation/Knowledge={esc(clin.get("dictionary_field_count"))} · nomes de ferramenta={esc(clin.get("new_tool_name_count"))} · publicação {_status_chip(clin.get("publication") or "HOLD")} · UUIDv4 adotado={esc((clin.get("identity_conflict") or {}).get("adopt_uuid_v4"))} · data/tools promovido={esc(clin.get("promoted_to_data_tools"))}.</p>
      <p class="hold-banner">COMPARE only. F21 RECEIVED no zip já observado. Sem dump de cláusula ABNT/ISO. Sem dump dos 163 Foundation para FLD-*. Escalas de terceiros (Braden/Norton/Glasgow) não entram em data/tools. Content_Schemas/Meta_Schemas reivindicados no índice e ausentes no xlsx.</p>
      {_table(["slug piloto", "código", "kind", "relação Drive", "nomes no zip"], clin_code_rows or [["rode extract", "—", "—", "HOLD", "—"]])}
      <p>Primeiros nomes da matriz de novas ferramentas:</p>
      {_table(["ferramenta (Drive)"], clin_tool_rows or [["—"]])}
    </section>
    <section class="panel">
      <h2>NANDA / NIC / NOC identidade OPT-B ({esc(nnn_id.get("business_key") or "MD-NNN-IDENTITY-001")})</h2>
      <p>Dono F12 = B. Códigos a partir dos nomes de ficheiro Drive. canonical_label=null. Deep-link ao titular. Sem texto licenciado. Publicação {_status_chip(nnn_id.get("publication") or "HOLD")}.</p>
      {_table(["sistema", "código", "label canônico", "exibição", "deep-link", "Drive"], nnn_rows or [["rode extract", "—", "—", "texto indisponível (licença)", "—", "QUARANTINE"]])}
    </section>
    <section class="panel">
      <h2>UCP v2.0 COMPARE ({esc(ucp.get("business_key") or "MD-UCP-V2-COMPARE-001")})</h2>
      <p>Política {esc(ucp.get("policy") or "POL-CKO-UCP-001-v2.0")} · schemas recebidos={esc(ucp.get("schema_count"))} · artefatos no registo={esc(ucp.get("register_artifact_count"))} · ausentes={esc(ucp.get("missing_register_count"))} · copiado para schemas/={esc(ucp.get("copied_into_schemas"))} · publicação {_status_chip(ucp.get("publication") or "HOLD")} · assured={esc(ucp.get("assured"))}.</p>
      <p class="hold-banner">COMPARE only. Draft 2020-12 ≠ draft-07 vigente. CONTROLLED_CANDIDATE não é ASSURED. authority_mode DERIVED_NOT_AUTHORITY alinhado. Sem substituir tool.schema.json. Sem inventar MODEL/PILOT ausentes.</p>
      {_table(["ficheiro", "$id", "draft", "sha256", "em schemas/"], ucp_rows or [["rode extract", "—", "—", "—", "false"]])}
      <p>Ausentes do lote (registo CSV):</p>
      {_table(["id", "classe", "ficheiro"], ucp_missing_rows or [["—", "—", "nenhum"]])}
    </section>
    <section class="panel">
      <h2>L70 Medicamentos — API ANVISA COMPARE ({esc(l70.get("business_key") or "MD-L70-ANVISA-001")})</h2>
      <p>Frente {esc(l70.get("frente") or "F24")} · product REST={esc(l70_api.get("product_rest") or "NOT_OBSERVED")} · unzip={esc(l70.get("unzipped"))} · data/tools={esc(l70.get("copied_into_data_tools"))} · claimed Drive={esc(l70.get("claimed_count_drive_description") or l70_zip.get("claimed_count_drive_description"))} · verified={esc(l70.get("verified_population") or "EVIDENCE_PENDING")} · publicação {_status_chip(l70.get("publication") or "HOLD")} · assured={esc(l70.get("assured"))}.</p>
      <p class="hold-banner">API oficial primeiro. Portal HTML 200 ≠ JSON de produto. Dump {esc(l70_zip.get("title") or "CKO_Medicamentos_ANVISA_Completo.zip")} = SKIP_BINARY_DUMP. 17231 é descrição Drive, não população hashed. openFDA não substitui bula ANVISA. Sem insulina.json.</p>
      {_table(["adapter", "URL", "HTTP", "estado", "base_url", "REST JSON"], l70_rows or [["rode extract", "https://api.anvisa.gov.br/", "—", "EVIDENCE_PENDING", "null", "não"]])}
      {_table(["gap", "estado", "razão"], l70_gap_rows or [["GAP-L70-ANVISA-REST-JSON", "EVIDENCE_PENDING", "rode extract"]])}
    </section>
    <section class="panel">
      <h2>Legislação federal</h2>
      {_table(["id", "norma", "tipo", "status", "MD", "REG"], law_rows or [["—", "rode extract", "—", "—", "—", "—"]])}
    </section>
    <section class="panel">
      <h2>Recursos</h2>
      {_table(["id", "título", "status", "MD", "REG"], res_rows or [["—", "rode extract", "—", "—", "—"]])}
    </section>
    <section class="panel">
      <h2>Currículo básico → avançado</h2>
      {_table(["ferramenta", "nível", "status", "MD", "REG"], unit_rows or [["—", "—", "—", "—", "—"]])}
    </section>
    <section class="panel">
      <h2>Pendências ALTA</h2>
      {_table(["id", "severidade", "razão"], pend_rows)}
    </section>
    <section class="panel">
      <h2>pages_full — catálogo de pendências REG ({esc(pages_pend.get("business_key") or "MD-PAGES-REG-PEND-001")})</h2>
      <p>{esc(pages_pend.get("owner_override") or "Inventário demonstra pendências REG.")} HTML={esc(pages_pend.get("html_count"))} · extração clínica em massa={esc(pages_pend.get("mass_clinical_extract") or "FORBIDDEN")}.</p>
      {_table(["stem", "gap", "em data/tools"], page_pend_rows or [["—", "rode extract", "false"]])}
    </section>
    <section class="panel">
      <h2>Alertas</h2>
      {_table(["severidade", "tipo", "mensagem"], alert_rows or [["—", "—", "sem alertas"]])}
      <p>Sem dispatch de e-mail (NO_SENSITIVE_CAPTURE). Frequência {esc(alerts.get("frequency_hours") or 24)}h.</p>
    </section>
    """
    return admin_shell(title="Biblioteca · CKO Studio", description="Biblioteca canônica e currículo.", current="library", inner=inner, **kwargs)


def page_apis(ctx: dict, **kwargs) -> str:
    adapters = load_json(ROOT / "cko_md" / "api_adapter_registry.json")
    gov = load_json(ROOT / "cko_inbox" / "extracted" / "gov_pages.json")
    agencies = load_json(ROOT / "cko_md" / "agency_registry.json")
    types = load_json(ROOT / "cko_inbox" / "extracted" / "congress_types.json")
    laws = load_json(ROOT / "cko_md" / "legislation_instrument_registry.json")
    gate = load_json(ROOT / "cko_reg" / "legislation_qualification.json")
    db_path = ROOT / "cko_inbox" / "cko_ops.sqlite"
    api_rows = [
        [
            esc(item.get("business_key")),
            esc(item.get("agency")),
            esc(item.get("http_status")),
            esc(item.get("base_url") or "null"),
            _status_chip(item.get("epistemic_status")),
            f"<code>{esc(item.get('md_ref'))}</code>",
            f"<code>{esc(item.get('reg_ref'))}</code>",
        ]
        for item in (adapters.get("adapters") or [])
    ]
    gov_rows = [
        [
            esc(item.get("agency")),
            esc(item.get("http_status")),
            _status_chip(item.get("epistemic_status")),
            f"<code>{esc((item.get('sha256') or '')[:16])}</code>",
        ]
        for item in (gov.get("pages") or [])
    ]
    ag_rows = [[esc(item.get("business_key")), esc(item.get("name")), _status_chip(item.get("status"))] for item in (agencies.get("agencies") or [])]
    gate_rows = [
        [
            esc(item.get("source_ref")),
            esc(item.get("tipo")),
            esc(item.get("gate_decision")),
            esc("sim" if item.get("revoked") else "não"),
            esc((item.get("gate_reason") or "")[:160]),
        ]
        for item in (gate.get("qualifications") or [])
    ]
    inner = f"""
    <header class="page-hero">
      <h1>APIs e órgãos.</h1>
      <p class="lede">ANVISA (Portal de APIs + gov.br), MS, COFEN, COREN-SP (HTML; sem REST), SGD/PGDADOS e Congresso Nacional. <code>base_url</code> só após HTTP 200 JSON. HTML SPA ≠ adapter REST. Catálogo federal bloqueia proposição sem efeito jurídico (ex.: PLP). Decreto numerado entra como regulamentar. Norma revogada pode ser ferramenta.</p>
      <p class="hold-banner">Adapters {esc(adapters.get("population"))} · produção API={esc(adapters.get("production_api"))} · tipos Senado ALLOW {esc(types.get("senado_allow"))} / BLOCK {esc(types.get("senado_block"))} · leis {esc(laws.get("population"))} · SQLite inbox {esc("presente" if db_path.exists() else "ausente")} · Postgres produção=NÃO · RLS inalterado</p>
    </header>
    <section class="panel">
      <h2>Agências MD</h2>
      {_table(["business_key", "nome", "status"], ag_rows)}
    </section>
    <section class="panel">
      <h2>Probe de API</h2>
      {_table(["adapter", "órgão", "HTTP", "base_url", "estado", "MD", "REG"], api_rows or [["—", "rode extract --network", "—", "null", "EVIDENCE_PENDING", "—", "—"]])}
    </section>
    <section class="panel">
      <h2>Gate de legislação federal</h2>
      <p>{esc(gate.get("gate_note") or "REG-LEG-GATE-001")}</p>
      {_table(["instrumento", "tipo", "decisão", "revogada", "razão"], gate_rows or [["—", "—", "EVIDENCE_PENDING", "—", "rode extract"]])}
    </section>
    <section class="panel">
      <h2>Portais HTML oficiais</h2>
      {_table(["órgão", "HTTP", "estado", "sha256"], gov_rows)}
    </section>
    <section class="panel">
      <h2>Banco operacional</h2>
      <p>Espelho SQLite <code>cko_inbox/cko_ops.sqlite</code> (inbox). Store canônico continua JSON no GitHub. Nenhuma alteração de RLS. Sem captura de e-mail para alerta.</p>
    </section>
    """
    return admin_shell(title="APIs / órgãos · CKO Studio", description="Adapters ANVISA/MS/COFEN/Congresso observados.", current="apis", inner=inner, **kwargs)


def page_backlog(ctx: dict, **kwargs) -> str:
    rows = []
    for item in ctx["studio"].get("backlog_revisao") or []:
        rows.append([
            _status_chip(item.get("severidade")),
            esc(item.get("item")),
            esc(item.get("descricao")),
            esc(item.get("data")),
        ])
    inner = f"""
    <header class="page-hero">
      <h1>Backlog humano.</h1>
      <p class="lede">Itens SOURCE_DERIVED do mapa. Interpretação Braden 9-12 em CONFLICT com o claim de validação Aprovado.</p>
    </header>
    <section class="panel">{_table(["severidade", "item", "ação", "data"], rows)}</section>
    """
    return admin_shell( title="Backlog · CKO Studio", description="Backlog de revisão humana.", current="backlog", inner=inner, **kwargs)


def page_design(ctx: dict, **kwargs) -> str:
    registry = ctx["tokens"]
    rows = []
    for token in registry.get("tokens") or []:
        rows.append([
            esc(token.get("business_key")),
            f"<code>{esc(token.get('css_var'))}</code>",
            esc(token.get("annex_value")),
            esc(token.get("runtime_value")),
            _status_chip(token.get("compare")),
            esc(token.get("epistemic_status")),
        ])
    inner = f"""
    <header class="page-hero">
      <h1>Design System — recuperação.</h1>
      <p class="lede">{esc(registry.get("note"))}</p>
      <p class="hold-banner">Status oficial do DS: {esc(registry.get("official_ds_status"))}. Inter/Nunito woff2 first-party RESTORED. OpenDyslexic EVIDENCE_PENDING (fallback Arial, sem CDN).</p>
    </header>
    <section class="panel">
      <div class="ds-swatches" aria-label="Swatches navy">
        <span class="swatch" style="background:#1A3E74"></span>
        <span class="swatch" style="background:#1E4D8C"></span>
        <span class="swatch" style="background:#163269"></span>
        <span class="swatch" style="background:#4A90E2"></span>
        <span class="swatch" style="background:#122C54"></span>
        <span class="swatch" style="background:#003366"></span>
      </div>
      {_table(["token", "css", "anexo", "runtime", "compare", "epistemic"], rows)}
    </section>
    """
    return admin_shell( title="Design System · CKO Studio", description="Comparação anexo vs runtime.", current="design", inner=inner, **kwargs)


def page_renderer(ctx: dict, **kwargs) -> str:
    concept = load_json(ROOT / "cko_md" / "concept_renderer.json")
    proj_rows = [
        [
            esc(item.get("id")),
            esc(item.get("layer")),
            esc((item.get("source") or "")[:220]),
        ]
        for item in (concept.get("projections") or [])
    ]
    inner = f"""
    <header class="page-hero">
      <h1>Renderer.</h1>
      <p class="lede">O renderer já existe em <code>engine.generate.build</code>. Este módulo dispara a execução local. Dual-render é medido no <code>audit</code> depois das duas árvores existirem — o status não é embutido nesta página para não quebrar a paridade fetch/inline.</p>
    </header>
    <section class="panel">
      <h2>Guia por conceito único ({esc(concept.get("business_key") or "MD-CONCEPT-RENDER-001")})</h2>
      <p>{esc(concept.get("rule") or "Um conceito → uma identidade → projeções.")} LLM canónico={esc((concept.get("renderer") or {}).get("llm_canonical") or "FORBIDDEN")}. Publicação {esc(concept.get("publication") or "HOLD")}.</p>
      {_table(["projeção", "camada", "fonte"], proj_rows or [["—", "—", "arquitectura ainda não gerada"]])}
    </section>
    <section class="panel">
      <h2>Ação prática</h2>
      <p>Gera <code>render/fetch</code> e <code>render/inline</code> a partir dos JSON. Não publica. Não altera fórmula.</p>
      <p class="actions">
        <button type="button" class="btn-primary" data-admin-action="render">Renderizar agora</button>
      </p>
      <pre id="admin-action-out" class="admin-out" hidden></pre>
    </section>
    """
    return admin_shell( title="Renderer · CKO Studio", description="Renderer local CKO.", current="renderer", inner=inner, **kwargs)


def page_deploy(ctx: dict, **kwargs) -> str:
    inner = f"""
    <header class="page-hero">
      <h1>Deploy via Git.</h1>
      <p class="lede">O botão prepara um changeset versionado. <strong>git push é FORBIDDEN</strong> a partir do browser. Publicação clínica permanece HOLD.</p>
    </header>
    <section class="panel">
      <h2>Ações</h2>
      <p class="actions">
        <button type="button" class="btn-secondary" data-admin-action="git-status">Ver git status</button>
        <button type="button" class="btn-primary" data-admin-action="render">Renderizar</button>
        <button type="button" class="btn-primary" data-admin-action="deploy-prepare">Preparar changeset Git</button>
      </p>
      <pre id="admin-action-out" class="admin-out" hidden></pre>
      <ol>
        <li>Renderizar projeções</li>
        <li>Preparar changeset em <code>cko_assurance/deploy_requests/</code></li>
        <li>Revisão humana ou agente</li>
        <li><code>git add</code> seletivo · <code>git commit</code> · <code>git push</code> do branch</li>
      </ol>
    </section>
    """
    return admin_shell( title="Deploy Git · CKO Studio", description="Preparar deploy Git. Sem push automático.", current="deploy", inner=inner, **kwargs)


def page_locales(ctx: dict, **kwargs) -> str:
    locales = load_json(ROOT / "cko_md" / "locale_registry.json")
    i18n = load_json(ROOT / "cko_reg" / "i18n_profile.json")
    who = load_json(ROOT / "cko_md" / "who_i18n_modulation.json")
    drive = load_json(ROOT / "cko_inbox" / "drive" / "INVENTORY.json")
    rows = []
    for item in locales.get("locales") or []:
        rows.append([
            esc(item.get("business_key")),
            esc(item.get("bcp47")),
            esc(", ".join(item.get("stems_observed") or [])),
            _status_chip("HOLD" if not item.get("wired_to_frontend") else "WIRED"),
            str(len(item.get("files") or [])),
        ])
    who_rows = [
        [esc(item.get("bcp47")), esc(item.get("label_observed")), _status_chip("DRIVE" if item.get("in_drive_zip") else "WHO_ONLY")]
        for item in (who.get("who_official_languages") or [])
    ]
    drive_in = [[esc(a.get("title")), esc(a.get("action") or a.get("reason")), esc(a.get("id"))] for a in (drive.get("ingested") or [])]
    drive_out = [[esc(a.get("title")), esc(a.get("reason")), esc(a.get("id"))] for a in (drive.get("not_ingested") or [])]
    inner = f"""
    <header class="page-hero">
      <h1>Locales e Drive.</h1>
      <p class="lede">MD-LOCALE-REG-001 registra {esc(locales.get("population"))} códigos extraídos de locales.zip ({esc(locales.get("epistemic_status"))}). REG-I18N-001 mantém tradução em HOLD. Runtime {esc(who.get("runtime_who_local_key") or "who.en+local.pt-BR")}. Dono APPROVED a chave composta; OMS/WHO HQ (6 oficiais) + locale local BCP47; não liga o seletor.</p>
      <p class="hold-banner">Dono i18n={esc(who.get("owner_decision") or i18n.get("owner_decision") or "HOLD")} · gate {esc(who.get("translation_gate") or "HOLD")} · wired={esc(who.get("wired_to_frontend"))}. Stems observados: cookies, footer. Sem strings de calculadora. Banner de cookies do zip NÃO implantado (NO_SENSITIVE_CAPTURE). Dump ICD/ICNP/GHO FORBIDDEN. pt ≠ pt-BR ≠ pt-PT ≠ pt-AO. CLDR default pt→pt-BR NÃO adotado.</p>
    </header>
    <section class="panel">
      <h2>Modulação WHO/OMS ({esc(who.get("business_key"))})</h2>
      <p>Seletor who.int observado: {esc(", ".join(item.get("bcp47") or "" for item in (who.get("who_official_languages") or [])))}. Interseção Drive ∩ WHO: {esc(", ".join(who.get("drive_intersection") or []))}. Drive-only: {esc(", ".join(who.get("drive_only") or []))}. Gate: {_status_chip(who.get("translation_gate") or i18n.get("translation_gate"))} · wired={esc(who.get("wired_to_frontend"))} · chave runtime={esc(who.get("runtime_who_local_key"))} · who.int/pt raiz=404.</p>
      {_table(["BCP47", "rótulo observado", "Drive zip"], who_rows)}
    </section>
    <section class="panel">
      <h2>Chave WHO + local (variantes lusófonas)</h2>
      <p>XLIFF srcLang/trgLang. RFC 5646 BCP47. RFC 4647 sem fallback irmão. PAHO Content-Language pt-br. Zip design/imagens SKIP_BINARY.</p>
      {_table(["BCP47", "país", "região WHO", "chave who+local", "estado", "runtime"], [
        [esc(item.get("bcp47")), esc(item.get("label")), esc(item.get("who_region")), esc(item.get("who_local_key")), _status_chip(item.get("epistemic_status")), esc(item.get("runtime"))]
        for item in (who.get("lusophone_variants") or [])
      ])}
    </section>
    <section class="panel">
      <h2>Registry MD ({esc(locales.get("file_count"))} arquivos)</h2>
      {_table(["business_key", "código zip", "stems", "frontend", "arquivos"], rows)}
    </section>
    <section class="panel">
      <h2>Perfil REG</h2>
      <p>Gate: {_status_chip(i18n.get("translation_gate"))} · revisão humana: {esc(i18n.get("human_review_required"))} · who_ref: {esc(i18n.get("who_ref"))} · {esc(i18n.get("rule"))}</p>
    </section>
    <section class="panel">
      <h2>Drive ingerido neste ciclo</h2>
      {_table(["artefato", "ação", "fileId"], drive_in)}
    </section>
    <section class="panel">
      <h2>Drive observado e não promovido</h2>
      {_table(["artefato", "motivo", "fileId"], drive_out)}
    </section>
    """
    return admin_shell(title="Locales / Drive · CKO Studio", description="Locales Drive em quarentena. Overlay WHO HOLD.", current="locales", inner=inner, **kwargs)


def page_mdm(ctx: dict, **kwargs) -> str:
    types = (load_json(ROOT / "cko_md" / "entity_type_registry.json").get("types") or [])
    type_rows = [[esc(t.get("business_key")), esc(t.get("name")), _status_chip("M0_REGISTERED")] for t in types]
    locales = load_json(ROOT / "cko_md" / "locale_registry.json")
    fields = load_json(ROOT / "cko_md" / "field_dictionary.json")
    works = load_json(ROOT / "cko_md" / "work_registry.json")
    iso = load_json(ROOT / "cko_md" / "iso8000_profile.json")
    binding = load_json(ROOT / "cko_md" / "iso8000_pgdados_binding.json")
    lineage = load_json(ROOT / "cko_md" / "lineage_registry.json")
    field_rows = [
        [
            esc(f.get("business_key")),
            esc(f.get("name")),
            esc(f.get("iso_test_id")),
            esc(f.get("pgdados_term")),
            esc(f.get("pgdados_instrument")),
        ]
        for f in (fields.get("fields") or [])
    ]
    work_rows = [[esc(w.get("slug")), esc(w.get("work_class")), _status_chip(w.get("rights_status")), esc(w.get("cko_copyright_claim"))] for w in (works.get("works") or [])]
    iso_rows = [[esc(t.get("id")), _status_chip(t.get("status")), esc(t.get("principle")), esc(t.get("pgdados_term"))] for t in (iso.get("tests") or [])]
    bind_rows = [
        [esc(item.get("field_ref")), esc(item.get("iso_test_id")), esc(item.get("pgdados_term")), esc(item.get("pgdados_instrument"))]
        for item in (binding.get("links") or [])
    ]
    dim_rows = [[esc(d.get("name")), esc(d.get("source")), _status_chip(d.get("clause_text"))] for d in (binding.get("data_quality_dimensions") or [])]
    instr_rows = [[esc(i.get("business_key")), esc(i.get("name")), esc(i.get("guia_ref"))] for i in (binding.get("instruments") or [])]
    lin_rows = [[esc(item.get("slug")), _status_chip(item.get("status")), esc((item.get("md_vault_sha256") or "")[:12] or "—"), esc(item.get("frontend_href"))] for item in (lineage.get("links") or [])]
    inner = f"""
    <header class="page-hero">
      <h1>Master Data.</h1>
      <p class="lede">CKO-MD first. ISO 8000 no CKO é perfil de unicidade/proveniência/WORM/lineage — não certificação. Cada campo do perfil aponta a um termo ou instrumento PGDADOS. Referência operacional BR: <a href="https://www.gov.br/governodigital/pt-br/infraestrutura-nacional-de-dados/governancadedados/pgdados">PGDADOS /pgdados</a> e <a href="https://www.gov.br/governodigital/pt-br/infraestrutura-nacional-de-dados/governancadedados/glossario-de-termos-de-dados">glossário</a>. Lei 9.610 vincula obras originais candidatas; escalas de terceiros HOLD.</p>
      <p class="hold-banner">ISO implemented={esc(iso.get("iso_implemented"))} · certified={esc(iso.get("certified"))} · clause={esc(iso.get("clause_text"))} · bindings={esc(binding.get("population"))} · campos={esc(fields.get("population"))} · lineage completa={esc(lineage.get("complete_count"))}</p>
    </header>
    <section class="panel">
      <h2>Field dictionary ({esc(fields.get("population"))})</h2>
      {_table(["business_key", "campo", "teste ISO CKO", "termo PGDADOS", "instrumento"], field_rows)}
    </section>
    <section class="panel">
      <h2>Vínculo ISO 8000 CKO → PGDADOS</h2>
      <p>Todo campo do dicionário ISO 8000 CKO tem termo/instrumento PGDADOS. Texto de cláusula ISO = CLAUSE_TEXT_UNAVAILABLE. PGDADOS não substitui a norma licenciada.</p>
      {_table(["campo", "teste ISO CKO", "termo PGDADOS", "instrumento"], bind_rows)}
      <h3>Instrumentos PGDADOS</h3>
      {_table(["id", "nome", "guia"], instr_rows)}
      <h3>Dimensões de qualidade (glossário)</h3>
      {_table(["dimensão", "fonte", "cláusula"], dim_rows)}
    </section>
    <section class="panel">
      <h2>Obras e direitos</h2>
      {_table(["slug", "classe", "direitos", "claim CKO"], work_rows)}
    </section>
    <section class="panel">
      <h2>Lineage vault → frontend</h2>
      {_table(["slug", "status", "vault MD", "href"], lin_rows)}
    </section>
    <section class="panel">
      <h2>Perfil ISO 8000 CKO</h2>
      <p>Catálogo ISO: <code>{esc(iso.get("official_catalog_url"))}</code>. Referência BR: <a href="{attr(iso.get("pgdados_hub_url") or "https://www.gov.br/governodigital/pt-br/infraestrutura-nacional-de-dados/governancadedados/pgdados")}">{esc(iso.get("pgdados_hub_url") or "PGDADOS /pgdados")}</a>. {esc(iso.get("government_reference") or "")}</p>
      {_table(["teste", "status", "princípio", "termo PGDADOS"], iso_rows)}
    </section>
    <section class="panel">
      <h2>Entity types ({len(types)})</h2>
      {_table(["business_key", "nome", "maturidade"], type_rows)}
    </section>
    <section class="panel">
      <h2>Linha MD → consumo</h2>
      <p>Fonte Drive/GitHub → vault WORM → MD registry → REG profile → renderer → frontend. Locales: {esc(locales.get("population"))} códigos SOURCE_DERIVED, wired={esc(False)}.</p>
    </section>
    """
    return admin_shell(title="Master Data · CKO Studio", description="MDM, ISO 8000 profile e lineage.", current="mdm", inner=inner, **kwargs)


def page_frameworks(ctx: dict, **kwargs) -> str:
    registry = load_json(ROOT / "cko_core" / "framework_registry.json")
    mockups = load_json(ADMIN_DIR / "mockup_reference_map.v1.json")
    rows = []
    for item in registry.get("frameworks") or []:
        rows.append([
            esc(item.get("business_key")),
            esc(item.get("name")),
            esc(item.get("role")),
            _status_chip(item.get("clause_text")),
            _status_chip(item.get("epistemic_status")),
        ])
    mock_rows = [[esc(r.get("id")), esc(r.get("title")), esc(r.get("maps_to"))] for r in (mockups.get("references") or [])]
    inner = f"""
    <header class="page-hero">
      <h1>Frameworks de controle.</h1>
      <p class="lede">{esc(registry.get("note"))} Mockups COSO/COBIT (88,7%, APO12.01, 184/214 objetivos) são DOCUMENT_CLAIM. ISO 8000 sem texto de cláusula. Referência BR explícita: PGDADOS /pgdados. Não copiar norma licenciada.</p>
    </header>
    <section class="panel">
      {_table(["business_key", "nome", "papel", "cláusula", "epistemic"], rows)}
    </section>
    <section class="panel">
      <h2>Mockups mapeados (quarentena)</h2>
      {_table(["id", "título", "módulo CKO"], mock_rows)}
    </section>
    """
    return admin_shell(title="Frameworks · CKO Studio", description="Framework registry only.", current="frameworks", inner=inner, **kwargs)


def page_maturity(ctx: dict, **kwargs) -> str:
    from .maturity import evaluate_maturity

    panorama = evaluate_maturity()
    layers = panorama.get("layers") or {}
    by_m = layers.get("by_maturity") or {}
    mat_rows = [[esc(k), str(v)] for k, v in sorted(by_m.items())]
    agents = panorama.get("agents") or {}
    caat = panorama.get("caat") or {}
    layer_caat = caat.get("layer_count_44") or {}
    ipe = panorama.get("ipe") or {}
    locales = panorama.get("locales") or {}
    ds = panorama.get("design_system") or {}
    nxt = "".join(f"<li>{esc(item)}</li>" for item in (panorama.get("next_gate") or []))
    inner = f"""
    <header class="page-hero">
      <h1>Panorama de maturidade.</h1>
      <p class="lede">Gerado dos registries (MD → REG → assurance → projeção). {esc(panorama.get("rule"))}</p>
      <p class="hold-banner">Release: {esc(panorama.get("release"))} · Cadeia: {esc(panorama.get("chain"))} · IPE dashboard: candidato, sem reliance.</p>
    </header>
    <section class="catalog admin-cards" aria-label="KPIs observados">
      <article class="tool-card"><p class="eyebrow">Camadas</p><h2>{esc(layers.get("population"))}</h2><p>44 no registry. Nenhuma ASSURED.</p></article>
      <article class="tool-card"><p class="eyebrow">Pilotos</p><h2>{esc((panorama.get("domain_candidates") or {}).get("tools"))}</h2><p>HOLD internos: {esc((panorama.get("domain_candidates") or {}).get("hold"))}. Braden em data/tools: {esc((panorama.get("domain_candidates") or {}).get("braden_in_data_tools"))}.</p></article>
      <article class="tool-card"><p class="eyebrow">Agentes</p><h2>{esc(agents.get("population"))}</h2><p>Classes {esc(agents.get("classes"))}. Runtime extração: {_status_chip("IMPLEMENTED_INBOX_ONLY" if agents.get("implemented") else "NOT_IMPLEMENTED")}. Publicação HOLD.</p></article>
      <article class="tool-card"><p class="eyebrow">CAAT 44</p><h2>{esc(layer_caat.get("status"))}</h2><p>Só a população do Layer Registry. Não é PASS do projeto.</p></article>
      <article class="tool-card"><p class="eyebrow">Locales Drive</p><h2>{esc(locales.get("population"))}</h2><p>Stems {esc(", ".join(locales.get("stems_only") or []))} · wired={esc(locales.get("wired_to_frontend"))}.</p></article>
      <article class="tool-card"><p class="eyebrow">DS header</p><h2>{esc(ds.get("header_compare"))}</h2><p>{esc(ds.get("fonts"))}</p></article>
    </section>
    <section class="panel">
      <h2>Camadas por código de maturidade</h2>
      {_table(["maturidade", "n"], mat_rows)}
    </section>
    <section class="panel">
      <h2>CAAT / IPE</h2>
      <p>CAATs registrados: {esc(caat.get("registered_caats"))} · registry implemented={esc(caat.get("registry_implemented"))}.</p>
      <p>IPEs registrados: {esc(ipe.get("ipes"))} · implemented={esc(ipe.get("registry_implemented"))}. {esc(ipe.get("rule"))}</p>
      <p>CARR: {esc(", ".join(ipe.get("carr") or []))}.</p>
    </section>
    <section class="panel">
      <h2>Próximo gate</h2>
      <ol>{nxt}</ol>
    </section>
    """
    return admin_shell(title="Maturidade · CKO Studio", description="Panorama observado M0–M7.", current="maturity", inner=inner, **kwargs)


def emit_admin_pages(dest: Path, ctx: dict, *, css_href: str, home_href: str, inline_css: bool) -> list[Path]:
    written: list[Path] = []
    (dest / "admin").mkdir(parents=True, exist_ok=True)
    common_root = dict(css_href=css_href, home_href=home_href, inline_css=inline_css, nested=False)
    pages = {
        dest / "admin.html": page_dashboard(ctx, **common_root),
    }
    nested_css = "../assets/app.css" if not inline_css else css_href
    nested_home = "../index.html"
    common_nested = dict(css_href=nested_css, home_href=nested_home, inline_css=inline_css, nested=True)
    nested = {
        "database.html": page_database,
        "catalog.html": page_catalog,
        "pipeline.html": page_pipeline,
        "layers.html": page_layers,
        "validations.html": page_validations,
        "agents.html": page_agents,
        "monitoring.html": page_monitoring,
        "library.html": page_library,
        "apis.html": page_apis,
        "backlog.html": page_backlog,
        "design-system.html": page_design,
        "renderer.html": page_renderer,
        "deploy.html": page_deploy,
        "locales.html": page_locales,
        "mdm.html": page_mdm,
        "frameworks.html": page_frameworks,
        "maturity.html": page_maturity,
    }
    for name, fn in nested.items():
        pages[dest / "admin" / name] = fn(ctx, **common_nested)
    for path, html in pages.items():
        path.write_text(html, encoding="utf-8")
        written.append(path)
    for source in (
        ADMIN_DIR / "contract.json",
        ADMIN_DIR / "studio_cms_map.v1.json",
        ADMIN_DIR / "mockup_reference_map.v1.json",
        ROOT / "cko_core" / "layer_registry.json",
        ROOT / "cko_core" / "design_token_registry.json",
        ROOT / "cko_md" / "locale_registry.json",
        ROOT / "cko_md" / "who_i18n_modulation.json",
        ROOT / "cko_md" / "translation_envelopes.json",
        ROOT / "cko_md" / "nnn_identity_catalog.json",
        ROOT / "cko_md" / "ucp_v2_compare.json",
        ROOT / "cko_md" / "l70_anvisa_compare.json",
        ROOT / "cko_md" / "library_32_compare.json",
        ROOT / "cko_md" / "pgdados_pending_probe.json",
        ROOT / "cko_md" / "layer_md_reg_phase.json",
    ):
        if source.exists():
            target = dest / "admin" / source.name
            target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
            written.append(target)
    return written
