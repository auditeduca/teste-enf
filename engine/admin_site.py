"""Integrated Admin Studio surface. PRESENTATION_ONLY plus local control-plane buttons."""

from __future__ import annotations

import json
from pathlib import Path

from .html import attr, dumps_json, esc
from .paths import ADMIN_DIR, ASSETS_DIR, ROOT

MODULES = [
    ("dashboard", "Painel", "admin.html"),
    ("database", "Banco GitHub", "admin/database.html"),
    ("catalog", "Catálogo", "admin/catalog.html"),
    ("pipeline", "Pipeline", "admin/pipeline.html"),
    ("layers", "44 camadas", "admin/layers.html"),
    ("validations", "Validações", "admin/validations.html"),
    ("agents", "Agentes", "admin/agents.html"),
    ("monitoring", "Monitoramento", "admin/monitoring.html"),
    ("backlog", "Backlog", "admin/backlog.html"),
    ("design", "Design System", "admin/design-system.html"),
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
    body = f"""<div class="admin-app">
  <aside class="admin-side" aria-label="Módulos do Studio">
    <p class="admin-brand">CKO Studio</p>
    <p class="admin-brand-sub">Admin ↔ frontend · GitHub</p>
    <nav class="admin-nav">{"".join(items)}</nav>
    <p class="admin-side-note"><a href="{attr(home_href)}">Site público</a></p>
  </aside>
  <div class="admin-main">
    <header class="admin-top">
      <p class="eyebrow">{esc(title)}</p>
      <p class="admin-kicker">Não grava fórmula · uuid HOLD · NO_SENSITIVE_CAPTURE</p>
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
    elif any(token in upper for token in ("PASS", "MATCH", "IMPLEMENTED", "OBSERVED")):
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
    </section>
    <section class="panel">
      <h2>Imagens do mapa Studio</h2>
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
    class_rows = [[esc(name), _status_chip("REGISTERED"), esc("population 0")] for name in (registry.get("classes") or [])]
    studio_rows = []
    for item in ctx["studio"].get("agentes_tarefas") or []:
        studio_rows.append([
            esc(item.get("agente")),
            _status_chip(item.get("studio_status")),
            esc(item.get("data_hora")),
            _status_chip(item.get("cko_status")),
        ])
    inner = f"""
    <header class="page-hero">
      <h1>Agentes.</h1>
      <p class="lede">Classes registradas no Day Zero. Runtime agêntico: NÃO IMPLEMENTADO. MAKER ≠ CHECKER ≠ AUDITOR. O mapa Studio que marca Extração/Publicação como Concluído é DOCUMENT_CLAIM.</p>
    </header>
    <section class="panel">
      <h2>Registry CKO ({esc(registry.get("population"))} agentes)</h2>
      {_table(["classe", "status", "nota"], class_rows[:12])}
      <p>Total de classes: {len(registry.get("classes") or [])}. Lista completa no JSON.</p>
    </section>
    <section class="panel">
      <h2>Execução alegada no mapa Braden</h2>
      {_table(["agente", "Studio", "data", "CKO"], studio_rows)}
    </section>
    """
    return admin_shell( title="Agentes · CKO Studio", description="Agent registry e claims Studio.", current="agents", inner=inner, **kwargs)


def page_monitoring(ctx: dict, **kwargs) -> str:
    kpis = (ctx["studio"].get("monitoramento") or {}).get("kpis") or []
    rows = [[esc(k.get("metrica")), esc(k.get("valor_claimed")), esc(k.get("variacao_claimed")), _status_chip("UNKNOWN")] for k in kpis]
    inner = f"""
    <header class="page-hero">
      <h1>Monitoramento.</h1>
      <p class="lede">{esc((ctx["studio"].get("monitoramento") or {}).get("note"))} Sem IPE não há reliance.</p>
    </header>
    <section class="panel">{_table(["métrica", "valor claimed", "variação claimed", "CKO"], rows)}</section>
    """
    return admin_shell( title="Monitoramento · CKO Studio", description="KPIs unverified.", current="monitoring", inner=inner, **kwargs)


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
      <p class="hold-banner">Status oficial do DS: {esc(registry.get("official_ds_status"))}. Inter/Nunito: arquivos ausentes. Sem CDN.</p>
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
        "backlog.html": page_backlog,
        "design-system.html": page_design,
        "renderer.html": page_renderer,
        "deploy.html": page_deploy,
    }
    for name, fn in nested.items():
        pages[dest / "admin" / name] = fn(ctx, **common_nested)
    for path, html in pages.items():
        path.write_text(html, encoding="utf-8")
        written.append(path)
    for source in (
        ADMIN_DIR / "contract.json",
        ADMIN_DIR / "studio_cms_map.v1.json",
        ROOT / "cko_core" / "layer_registry.json",
        ROOT / "cko_core" / "design_token_registry.json",
    ):
        if source.exists():
            target = dest / "admin" / source.name
            target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
            written.append(target)
    return written
