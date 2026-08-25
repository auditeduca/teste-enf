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
      <a class="tool-card" href="{attr(_module_href('admin/apis.html', nested))}"><p class="eyebrow">APIs</p><h2>Órgãos / APIs</h2><p>CKAN + Congresso. base_url null até HTTP 200. PLP bloqueado. SQLite inbox.</p></a>
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
    rows = []
    for layer in ctx["layers"]:
        rows.append([
            esc(layer.get("layer_code")),
            esc(layer.get("canonical_name")),
            _status_chip(layer.get("maturity")),
            f"<code>{esc(layer.get('md_profile_ref'))}</code>",
            f"<code>{esc(layer.get('reg_profile_ref'))}</code>",
        ])
    inner = f"""
    <header class="page-hero">
      <h1>44 camadas governadas.</h1>
      <p class="lede">EXISTS ≠ POPULATED ≠ IMPLEMENTADO ≠ ASSURED. Cada camada já nasceu com MD + REG.</p>
    </header>
    <section class="panel">{_table(["code", "nome", "maturidade", "MD", "REG"], rows)}</section>
    """
    return admin_shell( title="Camadas · CKO Studio", description="Layer Registry 44.", current="layers", inner=inner, **kwargs)


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
    inner = f"""
    <header class="page-hero">
      <h1>Agentes.</h1>
      <p class="lede">Runner de extração IMPLEMENTADO (inbox). Publicação clínica HOLD. MAKER ≠ CHECKER ≠ AUDITOR. CLI: <code>python3 -m engine.cli extract</code>.</p>
      <p class="hold-banner">Último run: {esc(run.get("run_id") or "nenhum")} · status {esc(run.get("status") or "UNKNOWN")} · publicação {esc(run.get("publication") or "HOLD")} · IPE reliance={esc(run.get("ipe_reliance"))}.</p>
    </header>
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
    inner = f"""
    <header class="page-hero">
      <h1>Biblioteca de recursos.</h1>
      <p class="lede">Catálogo MD + currículo documental + legislação federal do Congresso. Sem HTML integral. Sem LLM. Publicação HOLD. PLP bloqueado.</p>
      <p class="hold-banner">Recursos {esc(lib.get("population"))} · Unidades {esc(curr.get("population"))} · Leis {esc(laws.get("population"))} · Pendências ALTA {esc(curr.get("pending_high_count"))} · Alertas {esc(alerts.get("population"))}</p>
    </header>
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
      <p class="lede">ANVISA, MS, COFEN, COREN e Congresso Nacional. <code>base_url</code> só após HTTP 200. Legislação federal bloqueia tipo sem força de lei (ex.: PLP). Norma revogada pode ser ferramenta.</p>
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
      <h2>Gate de força de lei</h2>
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
    inner = f"""
    <header class="page-hero">
      <h1>Renderer.</h1>
      <p class="lede">O renderer já existe em <code>engine.generate.build</code>. Este módulo dispara a execução local. Dual-render é medido no <code>audit</code> depois das duas árvores existirem — o status não é embutido nesta página para não quebrar a paridade fetch/inline.</p>
    </header>
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
    drive_in = [[esc(a.get("title")), esc(a.get("action") or a.get("reason")), esc(a.get("id"))] for a in (drive.get("ingested") or [])]
    drive_out = [[esc(a.get("title")), esc(a.get("reason")), esc(a.get("id"))] for a in (drive.get("not_ingested") or [])]
    inner = f"""
    <header class="page-hero">
      <h1>Locales e Drive.</h1>
      <p class="lede">MD-LOCALE-REG-001 registra {esc(locales.get("population"))} códigos extraídos de locales.zip ({esc(locales.get("epistemic_status"))}). REG-I18N-001 mantém tradução em HOLD. Runtime permanece pt-BR.</p>
      <p class="hold-banner">Stems observados: cookies, footer. Sem strings de calculadora. Banner de cookies do zip NÃO implantado (NO_SENSITIVE_CAPTURE).</p>
    </header>
    <section class="panel">
      <h2>Registry MD ({esc(locales.get("file_count"))} arquivos)</h2>
      {_table(["business_key", "código zip", "stems", "frontend", "arquivos"], rows)}
    </section>
    <section class="panel">
      <h2>Perfil REG</h2>
      <p>Gate: {_status_chip(i18n.get("translation_gate"))} · revisão humana: {esc(i18n.get("human_review_required"))} · {esc(i18n.get("rule"))}</p>
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
    return admin_shell(title="Locales / Drive · CKO Studio", description="Locales Drive em quarentena.", current="locales", inner=inner, **kwargs)


def page_mdm(ctx: dict, **kwargs) -> str:
    types = (load_json(ROOT / "cko_md" / "entity_type_registry.json").get("types") or [])
    type_rows = [[esc(t.get("business_key")), esc(t.get("name")), _status_chip("M0_REGISTERED")] for t in types]
    locales = load_json(ROOT / "cko_md" / "locale_registry.json")
    fields = load_json(ROOT / "cko_md" / "field_dictionary.json")
    works = load_json(ROOT / "cko_md" / "work_registry.json")
    iso = load_json(ROOT / "cko_md" / "iso8000_profile.json")
    lineage = load_json(ROOT / "cko_md" / "lineage_registry.json")
    field_rows = [[esc(f.get("business_key")), esc(f.get("name")), esc(f.get("purpose"))] for f in (fields.get("fields") or [])]
    work_rows = [[esc(w.get("slug")), esc(w.get("work_class")), _status_chip(w.get("rights_status")), esc(w.get("cko_copyright_claim"))] for w in (works.get("works") or [])]
    iso_rows = [[esc(t.get("id")), _status_chip(t.get("status")), esc(t.get("principle"))] for t in (iso.get("tests") or [])]
    lin_rows = [[esc(item.get("slug")), _status_chip(item.get("status")), esc((item.get("md_vault_sha256") or "")[:12] or "—"), esc(item.get("frontend_href"))] for item in (lineage.get("links") or [])]
    inner = f"""
    <header class="page-hero">
      <h1>Master Data.</h1>
      <p class="lede">CKO-MD first. ISO 8000 no CKO é perfil de unicidade/proveniência/WORM/lineage — não certificação. Lei 9.610 vincula obras originais candidatas; escalas de terceiros HOLD.</p>
      <p class="hold-banner">ISO implemented={esc(iso.get("iso_implemented"))} · certified={esc(iso.get("certified"))} · clause={esc(iso.get("clause_text"))} · campos={esc(fields.get("population"))} · lineage completa={esc(lineage.get("complete_count"))}</p>
    </header>
    <section class="panel">
      <h2>Field dictionary ({esc(fields.get("population"))})</h2>
      {_table(["business_key", "campo", "propósito"], field_rows)}
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
      {_table(["teste", "status", "princípio"], iso_rows)}
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
      <p class="lede">{esc(registry.get("note"))} Mockups COSO/COBIT (88,7%, APO12.01, 184/214 objetivos) são DOCUMENT_CLAIM. ISO 8000 sem texto de cláusula. Não copiar norma licenciada.</p>
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
    ):
        if source.exists():
            target = dest / "admin" / source.name
            target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
            written.append(target)
    return written
