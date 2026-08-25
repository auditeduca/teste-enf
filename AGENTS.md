# AGENTS.md

## Produto

CKO (Clinical Knowledge OS) — calculadoras e conteúdo clínico de enfermagem gerados a partir de JSON canônico.

Este repositório é autocontido. Documente e implemente apenas o que existe nesta árvore.

## Layout

- `schemas/` — contratos Draft-07
- `data/tools/` — fonte da verdade de cada objeto
- `engine/` — validate, score, generate, serve, audit
- `validators/` — completude clínica, paridade dual-render, release gate
- `assets/` — CSS/JS first-party
- `render/fetch` e `render/inline` — HTML gerado
- `docs/` — especificação desta aplicação

## Comandos

```bash
python3 -m pip install -e ".[dev]"
python3 -m pytest -q
python3 -m engine.cli validate
python3 -m engine.cli build
python3 -m engine.cli audit
python3 -m engine.cli serve --port 8081
```

## Regras

- Objetos novos entram em `data/tools/`. HTML gerado não é a fonte.
- Fórmula `expression` só pode conter dígitos e `+ - * / ( ) .`.
- SAE sem fonte canônica/licenciada permanece HOLD.
- Dimensionamento não emite número até a fórmula COFEN estar testada e aprovada.
- Sem CDN. Sem regeneração de conteúdo canônico por LLM.
- Português (pt-BR) é o idioma padrão da UI e da clínica.
- Conteúdo é apoio à decisão, não diagnóstico.

## Cursor Cloud

- Install: `python3 -m pip install -e ".[dev]"`
- Testes: `python3 -m pytest -q`
- Manual: `python3 -m engine.cli serve --port 8081`, abrir `/`, `/tools/gotejamento.html`, `/tools/meows.html`, `/inspector.html`
