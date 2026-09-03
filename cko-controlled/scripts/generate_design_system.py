#!/usr/bin/env python3
"""Canonical LYR-DS-001 catalog for runtime render. HOLD / NOT_RELEASED."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cko_md_norm import MD_NORM_CHAIN

GATE = Path(__file__).resolve().parents[1]
SITE = GATE.parent / "reference-website"
CANON = Path(__file__).resolve().parent / "cko_44_layers.json"

COLORS = [
    ("navy-950", "--cko-navy-950", "#081527"),
    ("navy-900", "--cko-navy-900", "#1A3E74"),
    ("navy-800", "--cko-navy-800", "#163269"),
    ("navy-700", "--cko-navy-700", "#1E4D8C"),
    ("blue-700", "--cko-blue-700", "#1D4ED8"),
    ("blue-600", "--cko-blue-600", "#2563EB"),
    ("blue-100", "--cko-blue-100", "#DBEAFE"),
    ("ink", "--cko-ink", "#1F2937"),
    ("muted", "--cko-muted", "#475569"),
    ("bg", "--cko-bg", "#F8FAFC"),
    ("surface", "--cko-surface", "#FFFFFF"),
    ("hold", "--cko-hold", "#7C3AED"),
    ("warn", "--cko-warn", "#B45309"),
    ("success", "--cko-success", "#166534"),
    ("danger", "--cko-danger", "#991B1B"),
    ("focus", "--cko-focus", "#FFFF00"),
]

TYPE = [
    ("display", "Nunito Sans / 3xl", "cko-ds-title", "Calculadoras de Enfermagem"),
    ("title", "Nunito Sans / 2xl", None, "Camada de design"),
    ("body", "Inter / md", None, "Texto de leitura contínua, fail-closed, HOLD / NOT_RELEASED."),
    ("small", "Inter / sm", "cko-ds-help", "Metadado, breadcrumb, ajuda de campo."),
    ("mono", "ui-monospace", None, "LYR-DS-001 · ADR-DS-001"),
]

SPACES = [("1", "4px"), ("2", "8px"), ("3", "12px"), ("4", "16px"), ("5", "20px"), ("6", "24px"), ("8", "32px"), ("10", "40px"), ("12", "48px")]
RADII = [("sm", "0.4rem"), ("md", "0.75rem"), ("lg", "1rem"), ("xl", "1.4rem"), ("full", "999px")]
SHADOWS = [("sm", "var(--cko-shadow-sm)"), ("md", "var(--cko-shadow-md)"), ("lg", "var(--cko-shadow-lg)")]
MOTION = [("duration", "180ms"), ("ease", "cubic-bezier(0.2, 0.7, 0.2, 1)"), ("reduced", "0ms when prefers-reduced-motion")]

COMPONENTS = [
    ("btn-primary", "Botão primário", "button", '<button class="cko-ds-btn cko-ds-btn--primary" type="button">Acção primária</button>'),
    ("btn-secondary", "Botão secundário", "button", '<button class="cko-ds-btn cko-ds-btn--secondary" type="button">Acção secundária</button>'),
    ("btn-ghost", "Botão ghost", "button", '<button class="cko-ds-btn cko-ds-btn--ghost" type="button">Acção discreta</button>'),
    ("btn-danger", "Botão perigo", "button", '<button class="cko-ds-btn cko-ds-btn--danger" type="button">Remover</button>'),
    ("btn-disabled", "Botão desativado", "button", '<button class="cko-ds-btn cko-ds-btn--primary cko-ds-btn--disabled" type="button" disabled>Indisponível</button>'),
    ("btn-icon", "Botão ícone", "button", '<button class="cko-ds-btn cko-ds-btn--icon" type="button" aria-label="Abrir pesquisa">⌕</button>'),
    ("link", "Ligação", "link", '<a class="cko-ds-link" href="/camadas/">Ver camadas</a>'),
    ("badge", "Selo", "badge", '<span class="cko-ds-badge">Candidato</span>'),
    ("badge-hold", "Selo HOLD", "badge", '<span class="cko-ds-badge cko-ds-badge--hold">HOLD / NOT_RELEASED</span>'),
    ("badge-warn", "Selo aviso", "badge", '<span class="cko-ds-badge cko-ds-badge--warn">PENDING ≠ ACK</span>'),
    ("alert-info", "Alerta informação", "alert", '<div class="cko-ds-alert cko-ds-alert--info" role="status">Nurse-PaLM operacional: NOT_ASSERTED.</div>'),
    ("alert-warn", "Alerta aviso", "alert", '<div class="cko-ds-alert cko-ds-alert--warn" role="status">Direitos de marca e espaçamento ainda em hold.</div>'),
    ("alert-hold", "Alerta hold", "alert", '<div class="cko-ds-alert cko-ds-alert--hold" role="status">Sem homologação clínica. Sem publicação.</div>'),
    ("alert-ok", "Alerta confirmação", "alert", '<div class="cko-ds-alert cko-ds-alert--ok" role="status">Zip classificado verificado por SHA-256.</div>'),
    ("card", "Cartão", "card", '<article class="cko-ds-card"><h3>Cartão de conteúdo</h3><p>Superfície padrão do runtime.</p></article>'),
    ("card-hold", "Cartão hold", "card", '<article class="cko-ds-card cko-ds-card--hold"><h3>Governança</h3><p>Maker ≠ Checker ≠ Auditor.</p></article>'),
    ("input", "Campo de texto", "form", '<label class="cko-ds-field"><span class="cko-ds-label">Nome da escala</span><input class="cko-ds-input" type="text" value="Aldrete"></label>'),
    ("select", "Seleção", "form", '<label class="cko-ds-field"><span class="cko-ds-label">Tema</span><select class="cko-ds-select"><option>Institucional</option><option>Clínico</option></select></label>'),
    ("textarea", "Área de texto", "form", '<label class="cko-ds-field"><span class="cko-ds-label">Notas</span><textarea class="cko-ds-textarea">HOLD — não publicar conteúdo clínico.</textarea></label>'),
    ("checkbox", "Caixa de seleção", "form", '<label class="cko-ds-check"><input type="checkbox" checked> Concordo com o estado fail-closed</label>'),
    ("radio", "Rádio", "form", '<label class="cko-ds-radio"><input type="radio" name="ds-demo" checked> Candidato</label>'),
    ("switch", "Interruptor", "form", '<span class="cko-ds-switch" data-on="true" role="switch" aria-checked="true"></span>'),
    ("field-help", "Campo com ajuda", "form", '<label class="cko-ds-field"><span class="cko-ds-label">Escore</span><input class="cko-ds-input" type="number" value="9"><span class="cko-ds-help">Valor de demonstração. Não é cálculo clínico.</span></label>'),
    ("table", "Tabela", "data", '<div class="cko-ds-table-wrap"><table class="cko-ds-table"><thead><tr><th>id</th><th>release</th></tr></thead><tbody><tr><td>LYR-DS-001</td><td>HOLD</td></tr></tbody></table></div>'),
    ("breadcrumb", "Navegação", "nav", '<nav class="cko-ds-crumbs" aria-label="Breadcrumb"><a href="/">Início</a> › <a href="/camadas/">Camadas</a> › <span>LYR-DS-001</span></nav>'),
    ("skip", "Skip link", "nav", '<a class="cko-ds-skip" href="#main-content">Pular para o conteúdo principal</a>'),
    ("hero", "Hero", "layout", '<section class="cko-ds-hero"><span class="cko-ds-badge">Design system</span><h1>Tudo via render</h1><p>Catálogo canónico pintado a partir de JSON.</p></section>'),
    ("kpi", "Indicador", "data", '<p class="cko-ds-kpi">44/44</p>'),
    ("tile", "Azulejo de navegação", "nav", '<a class="cko-ds-tile" href="/camadas/LYR-UI-001/">UI Components<small>LYR-UI-001</small></a>'),
    ("empty", "Estado vazio", "feedback", '<div class="cko-ds-empty"><p>Nenhum objecto publicado.</p></div>'),
    ("modal", "Modal", "overlay", '<div class="cko-ds-modal"><h3>Confirmar</h3><p>Release continua HOLD / NOT_RELEASED.</p></div>'),
    ("toast", "Toast", "feedback", '<div class="cko-ds-toast" role="status">Evidência HOLD registada.</div>'),
    ("tabs", "Separadores", "nav", '<div class="cko-ds-tabs" role="tablist"><button class="cko-ds-tab" aria-selected="true" type="button">Tokens</button><button class="cko-ds-tab" aria-selected="false" type="button">Componentes</button></div>'),
    ("accordion", "Acordeão", "nav", '<details class="cko-ds-accordion" open><summary>Holds do DS</summary><p>ADR-DS-002 permanece proposta. Fidelity de runtime em hold.</p></details>'),
    ("pagination", "Paginação", "nav", '<nav class="cko-ds-pager" aria-label="Paginação"><a href="#p1">1</a><span aria-current="page">2</span><a href="#p3">3</a></nav>'),
    ("progress", "Progresso", "feedback", '<div class="cko-ds-progress" aria-valuemin="0" aria-valuemax="100" aria-valuenow="44" role="progressbar"><span></span></div>'),
    ("tooltip", "Dica", "overlay", '<span class="cko-ds-tooltip">SHA-256<div role="tooltip">59ecb1f46cbde8bd…</div></span>'),
]

TEMPLATES = [
    ("home", "Início", "Hero + grelha de ferramentas"),
    ("tool", "Calculadora clínica", "Formulário + resultado fail-closed"),
    ("scale", "Escala", "Itens + escore + referências"),
    ("library", "Biblioteca", "Listagem + filtros"),
    ("article", "Artigo", "Prosa + evidência HOLD"),
    ("flashcard", "Aprendizagem", "Cartão + SRS"),
    ("institutional", "Institucional", "Missão / objectivo / cluster"),
    ("legal", "Legal", "Privacidade / termos"),
    ("a11y", "Acessibilidade", "Contraste e atalhos"),
    ("ecosystem", "Ecossistema", "Mapa das 44 camadas"),
    ("layers", "Índice de camadas", "Grelha renderizada"),
    ("layer-detail", "Ficha de camada", "SHA + runtime + holds"),
    ("search", "Pesquisa", "Campo + resultados"),
    ("not-found", "404", "Estado vazio governado"),
    ("print", "Impressão", "Perfil de exportação"),
    ("quiz", "Simulado", "Pergunta + feedback"),
    ("protocol", "Protocolo", "Passos + norma"),
    ("medication", "Medicação", "Ficha + alerta"),
    ("exam", "Exame laboratorial", "Valores + contexto"),
    ("contest", "Concurso", "Trilha educacional"),
    ("profile", "Estado do utilizador", "Favoritos / coleções"),
]

# Catalog remains 21 templates. Implemented = HTML chrome exists; wireframe = moldura only.
TEMPLATE_RUNTIME = {
    "home": ("implemented", "templates/home.html"),
    "tool": ("implemented", "templates/calculator.html"),
    "scale": ("implemented", "templates/scale.html"),
    "library": ("implemented", "templates/library.html"),
    "article": ("implemented", "templates/content.html"),
    "institutional": ("implemented", "templates/institutional.html"),
    "legal": ("implemented", "templates/institutional.html"),
    "a11y": ("implemented", "templates/institutional.html"),
    "ecosystem": ("implemented", "templates/institutional.html"),
    "layers": ("implemented", "camadas/index.html"),
    "layer-detail": ("implemented", "camadas/LYR-DS-001/index.html"),
    "flashcard": ("wireframe", None),
    "search": ("wireframe", None),
    "not-found": ("wireframe", None),
    "print": ("wireframe", None),
    "quiz": ("wireframe", None),
    "protocol": ("wireframe", None),
    "medication": ("wireframe", None),
    "exam": ("wireframe", None),
    "contest": ("wireframe", None),
    "profile": ("wireframe", None),
}

SLOT_BEGIN = "/* CKO-SLOT-TOKENS:BEGIN */"
SLOT_END = "/* CKO-SLOT-TOKENS:END */"

THEMES = [
    ("institutional", "Institucional", "Paleta navy CALENF em fundo claro."),
    ("clinical", "Clínico", "Variação fria para ferramentas."),
    ("high-contrast", "Alto contraste", "Amarelo sobre preto, foco ciano."),
    ("dark", "Escuro", "Superfície navy invertida. Não é release."),
]

SLOT_HUES = [
    214, 222, 200, 188, 172, 160, 148, 132, 118, 204,
    230, 246, 262, 278, 294, 310, 326, 342, 12, 28,
    44, 58, 74, 88, 102, 196, 184, 168, 152, 136,
    248, 264, 280, 208, 192, 176, 160, 144, 128, 112,
    96, 80, 64, 48,
]


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def catalog() -> dict:
    layers = json.loads(CANON.read_text(encoding="utf-8"))
    if len(layers) != 44:
        raise SystemExit(f"canonical layers must be 44, got {len(layers)}")
    if len(COMPONENTS) != 37:
        raise SystemExit(f"components must be 37, got {len(COMPONENTS)}")
    if len(TEMPLATES) != 21:
        raise SystemExit(f"templates must be 21, got {len(TEMPLATES)}")
    if len(THEMES) != 4:
        raise SystemExit(f"themes must be 4, got {len(THEMES)}")
    slots = []
    for i, layer in enumerate(layers):
        hue = SLOT_HUES[i]
        slots.append(
            {
                "index": i + 1,
                "layer_id": layer["id"],
                "name": layer["name"],
                "seq": layer["seq"],
                "token": f"--cko-slot-{i + 1:02d}",
                "color": f"hsl({hue} 54% 32%)",
                "href": f"/camadas/{layer['id']}/",
            }
        )
    return {
        "id": "CKO-DS-RUNTIME-1.0.0",
        "kind": "design-system-catalog",
        "layer": "LYR-DS-001",
        "ui_layer": "LYR-UI-001",
        "artifact": "ART-DESIGN-SYSTEM-FINAL-CONTROLLED",
        "accepted_authority": "ADR-DS-001",
        "proposal_hold": "ADR-DS-002",
        "release": "HOLD / NOT_RELEASED",
        "operational": "NOT_ASSERTED",
        "published": False,
        "pending_is_not_ack": True,
        "render": "catalog",
        "root": "policy-as-code",
        "starts_at": "policy-as-code",
        "cascade": [
            "policy-as-code",
            "schemas",
            "graph-constraints",
            "CI-gates",
            "runtime-assertions",
            "automatic-evidence",
        ],
        "rule": "tudo inicia em policy-as-code; estágio seguinte só corre se o predecessor PASS",
        "release_allowed": False,
        "nursePalm": "NOT_ASSERTED",
        "master_data_to_frontend": MD_NORM_CHAIN,
        "inventory": {
            "components": 37,
            "templates": 21,
            "themes": 4,
            "theme_slots": 44,
        },
        "tokens": {
            "color": [{"id": i, "token": t, "value": v} for i, t, v in COLORS],
            "typography": [{"id": i, "spec": s, "sampleClass": c, "sample": txt} for i, s, c, txt in TYPE],
            "space": [{"id": i, "value": v} for i, v in SPACES],
            "radius": [{"id": i, "value": v} for i, v in RADII],
            "shadow": [{"id": i, "value": v} for i, v in SHADOWS],
            "motion": [{"id": i, "value": v} for i, v in MOTION],
        },
        "themes": [{"id": i, "name": n, "note": note} for i, n, note in THEMES],
        "theme_slots": slots,
        "components": [
            {"id": i, "name": n, "kind": k, "html": html} for i, n, k, html in COMPONENTS
        ],
        "templates": [
            {
                "id": i,
                "name": n,
                "note": note,
                "status": TEMPLATE_RUNTIME[i][0],
                "html": TEMPLATE_RUNTIME[i][1],
            }
            for i, n, note in TEMPLATES
        ],
        "templates_implemented_n": sum(1 for i, _, _ in TEMPLATES if TEMPLATE_RUNTIME[i][0] == "implemented"),
        "templates_wireframe_n": sum(1 for i, _, _ in TEMPLATES if TEMPLATE_RUNTIME[i][0] == "wireframe"),
        "refinement": "CKO-DS-RUNTIME-1.2.0-HOLD",
        "identity_manual": {
            "id": "CKO-DS-IDENTITY-V10",
            "version": "v10",
            "status": "INGESTED_HOLD",
            "html": "cko-identidade.html",
            "scale_specimen": "escala-padrao.html",
            "rule": "o manual v10 é linguagem visual; páginas e escalas usam cluster + tokens; HTML solto com <style> próprio fica fora do padrão",
            "release_allowed": False,
        },
        "holds": [
            "ADR-DS-002_PROPOSAL_PENDING_APPROVAL",
            "DS_RUNTIME_FIDELITY_AND_CONTROLLED_DEPLOYMENT",
            "BRAND_PROVENANCE_RIGHTS_VECTOR_MASTER_SPACING_SHADOW_GAPS",
            "INDEPENDENT_ACCESSIBILITY_USABILITY_AND_REMOTE_BROWSER_STAGING_QA",
        ],
        "css": ["/css/cko-ds-tokens.css", "/css/cko-ds.css"],
        "renderer": "/js/cko-ds-render.js",
    }


def write_slot_tokens(slots: list[dict]) -> None:
    """Materialize --cko-slot-01…44 and shell aliases into the token sheet."""
    path = SITE / "css" / "cko-ds-tokens.css"
    if not path.is_file():
        raise SystemExit("cko-ds-tokens.css missing")
    lines = [
        SLOT_BEGIN,
        ":root {",
        "  --cko-navy: var(--cko-navy-900);",
        "  --cko-navy-mid: var(--cko-navy-700);",
        "  --navy: var(--cko-navy-900);",
        "  --navy-light: var(--cko-navy-700);",
        "  --navy-dark: var(--cko-navy-800);",
        "  --cko-slate-500: var(--cko-muted-2);",
        "  --cko-slate-800: var(--cko-ink);",
        "  --cko-page-tint: var(--cko-bg);",
        "  --cko-tpl-navy: var(--cko-navy-900);",
        "  --cko-tpl-navy-mid: var(--cko-navy-700);",
        "  --cko-tpl-surface: var(--cko-surface);",
        "  --cko-tpl-tint: var(--cko-bg);",
        "  --cko-tpl-ink: var(--cko-ink);",
        "  --cko-tpl-muted: var(--cko-muted-2);",
    ]
    for slot in slots:
        lines.append(f"  {slot['token']}: {slot['color']};")
    lines.extend(["}", SLOT_END, ""])
    block = "\n".join(lines)
    text = path.read_text(encoding="utf-8")
    if SLOT_BEGIN in text and SLOT_END in text:
        text = re.sub(
            re.escape(SLOT_BEGIN) + r".*?" + re.escape(SLOT_END),
            block.strip(),
            text,
            count=1,
            flags=re.S,
        )
        if not text.endswith("\n"):
            text += "\n"
    else:
        text = text.rstrip() + "\n\n" + block
    path.write_text(text, encoding="utf-8")


def generate() -> dict:
    payload = catalog()
    if payload["templates_implemented_n"] + payload["templates_wireframe_n"] != 21:
        raise SystemExit("template status must cover 21 catalog templates")
    write_slot_tokens(payload["theme_slots"])
    write_json(SITE / "data" / "cko" / "design-system.json", payload)
    write_json(GATE / "public" / "data" / "design-system.json", payload)
    print(json.dumps({"id": payload["id"], "inventory": payload["inventory"], "templates_implemented_n": payload["templates_implemented_n"]}, ensure_ascii=False))
    return payload


if __name__ == "__main__":
    generate()
